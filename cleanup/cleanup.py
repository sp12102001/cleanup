#! /usr/bin/env python3

'''
Organise files in a directory into subdirectories based on their extensions or custom rules.

Usage:
  cleanup [-d | -s] [-r [<timestamp>]] [-i] [-q] [-c CONFIG] [-l LOG] [-p PATTERN] [-x EXCLUDE] [--recursive] [--threads NUM] <dir>
  cleanup -h

Options:
  -d, --dry-run       Just display the changes that would be made, without actually doing anything.
  -i, --interactive   Interactive mode: approve or reject each move.
  -s, --silent        Do not display information while performing operations.
  -r, --revert        Revert previous cleanup of the directory.
                      Optionally specify a timestamp to revert to a specific cleanup.
  -c, --config        Specify a configuration file (YAML or JSON).
  -l, --log           Specify a log file to record operations.
  -p, --pattern       File patterns to include (comma-separated), e.g., "*.txt,*.pdf".
  -x, --exclude       File patterns to exclude (comma-separated), e.g., "*.exe,*.dll".
  --recursive         Process subdirectories recursively.
  --threads NUM       Number of threads to use for processing [default: 1].
  -q, --quarantine    Move files to a temporary location before finalizing.
  -h, --help          Display this help text.
'''

import io
import json
import os
import sys
import glob
import shutil
import time
import threading
import concurrent.futures
import fnmatch
from datetime import datetime

from docopt import docopt
from huepy import bold, lightblue, yellow, lightgreen, lightred
import yaml
import colorama
from tqdm import tqdm

from .file_types import FILE_TYPES
from .config import load_config, save_config, DEFAULT_CONFIG
from .logger import setup_logger, log_action

# Initialize colorama for cross-platform color support
colorama.init()

# Constants
REVERT_INFO_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'revert_info')
DEFAULT_REVERT_INFO_FILE = os.path.join(REVERT_INFO_DIR, 'revert_info.json')

# Ensure revert_info directory exists
if not os.path.exists(REVERT_INFO_DIR):
    os.makedirs(REVERT_INFO_DIR)

def get_longest_extension(filename):
    '''
    Returns the longest known extension from the given filename
    '''
    parts = filename.split('.')
    if len(parts) > 3:
        # possible triple extension (.pkg.tar.xz)
        extension = '.'.join(parts[-3:]).upper()
        if FILE_TYPES.get(extension):
            return extension
    if len(parts) > 2:
        # possible double extension (.tar.gz)
        extension = '.'.join(parts[-2:]).upper()
        if FILE_TYPES.get(extension):
            return extension
    if len(parts) > 1:
        # possible single extension (.zip)
        extension = parts[-1].upper()
        if FILE_TYPES.get(extension):
            return extension
    return None

def get_revert_info_file(abs_path, timestamp=None):
    """
    Get the revert info file path for a specific directory and optional timestamp
    """
    dir_hash = abs_path.replace(os.path.sep, '_').replace(':', '_')
    if timestamp:
        return os.path.join(REVERT_INFO_DIR, f"{dir_hash}_{timestamp}.json")
    else:
        # Get the most recent revert info file
        pattern = os.path.join(REVERT_INFO_DIR, f"{dir_hash}_*.json")
        revert_files = sorted(glob.glob(pattern), reverse=True)
        if revert_files:
            return revert_files[0]
        else:
            # Fall back to default for backward compatibility
            return DEFAULT_REVERT_INFO_FILE

def save_revert_info(abs_path, revert_info):
    """
    Save revert information with timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    dir_hash = abs_path.replace(os.path.sep, '_').replace(':', '_')
    revert_info_file = os.path.join(REVERT_INFO_DIR, f"{dir_hash}_{timestamp}.json")

    with io.open(revert_info_file, 'w', encoding='utf8') as file:
        file.write(json.dumps(revert_info, ensure_ascii=False, sort_keys=True,
                          indent=4, separators=(',', ': ')))
    return timestamp

def read_revert_info(revert_info_file):
    """
    Read revert information from file
    """
    try:
        with io.open(revert_info_file) as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def list_available_reverts(abs_path):
    """
    List all available revert points for a directory
    """
    dir_hash = abs_path.replace(os.path.sep, '_').replace(':', '_')
    pattern = os.path.join(REVERT_INFO_DIR, f"{dir_hash}_*.json")
    revert_files = sorted(glob.glob(pattern))

    reverts = []
    for file in revert_files:
        timestamp = file.split('_')[-1].replace('.json', '')
        date_formatted = datetime.strptime(timestamp, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
        reverts.append((timestamp, date_formatted))

    return reverts

def print_cleaning(action, dir):
    print(action + ' ' + bold(lightblue(dir)) + ':')

def print_move(move_action, file, file_type, revert=False, dry_run=False):
    if revert:
        preposition = 'from'
    else:
        preposition = 'under'
    if dry_run:
        move_action = yellow(move_action)
    else:
        move_action = lightgreen(move_action)
    print(move_action + ' ' + bold(file) + ' ' + preposition + ' '
          + bold(file_type))

def print_file_error(error, file, file_type, dry_run=False):
    if dry_run:
        preposition = 'from'
    else:
        preposition = 'under'
    print(lightred(error) + ' ' + bold(file) + ' ' + preposition + ' '
          + bold(file_type))

def print_dir_error(error, dir):
    print(lightred(error) + ': ' + bold(lightblue(dir)))

def print_complete(operation, stats=None):
    if stats:
        print(operation + ' ' + lightgreen('complete') + '! ' +
              f"({stats['success']} files moved, {stats['skipped']} skipped, {stats['error']} errors)")
    else:
        print(operation + ' ' + lightgreen('complete') + '!')

def ask_confirmation(message, default="y"):
    """Ask for user confirmation"""
    valid = {"yes": True, "y": True, "no": False, "n": False}
    if default == "y":
        prompt = " [Y/n] "
    elif default == "n":
        prompt = " [y/N] "
    else:
        prompt = " [y/n] "

    while True:
        print(message + prompt, end='')
        choice = input().lower()
        if choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes' or 'no' (or 'y' or 'n').")

def process_file(file_info, abs_path, config, dry_run, interactive, quarantine, silent, logger):
    """Process a single file according to rules"""
    file = file_info['name']
    original_path = file_info['path']
    file_type = file_info['type']

    # Apply user-configured rules to determine file_type if applicable
    if config.get('rules'):
        for rule in config['rules']:
            if rule['type'] == 'extension' and rule.get('extensions'):
                # Already handled by get_longest_extension
                pass
            elif rule['type'] == 'pattern' and rule.get('patterns'):
                for pattern, folder in rule['patterns'].items():
                    if fnmatch.fnmatch(file.lower(), pattern.lower()):
                        file_type = folder
                        break
            elif rule['type'] == 'size' and rule.get('size_ranges'):
                file_size = os.path.getsize(original_path)
                for size_range in rule['size_ranges']:
                    min_size = size_range.get('min', 0)
                    max_size = size_range.get('max', float('inf'))
                    if min_size <= file_size <= max_size and size_range.get('folder'):
                        file_type = size_range['folder']
                        break
            elif rule['type'] == 'date' and rule.get('date_ranges'):
                mod_time = os.path.getmtime(original_path)
                file_date = datetime.fromtimestamp(mod_time)
                for date_range in rule['date_ranges']:
                    start_date = datetime.strptime(date_range.get('start', '1970-01-01'), '%Y-%m-%d')
                    end_date = datetime.strptime(date_range.get('end', '2999-12-31'), '%Y-%m-%d')
                    if start_date <= file_date <= end_date and date_range.get('folder'):
                        file_type = date_range['folder']
                        break

    # Prepare paths
    target_dir = os.path.join(abs_path, file_type)
    new_path = os.path.join(target_dir, file)

    # Handle quarantine
    if quarantine and not dry_run:
        quarantine_dir = os.path.join(abs_path, '.cleanup_quarantine')
        if not os.path.exists(quarantine_dir):
            os.makedirs(quarantine_dir)
        quarantine_path = os.path.join(quarantine_dir, file)

    # Handle interactive mode
    if interactive and not dry_run:
        action_msg = f"Move '{file}' to '{file_type}' directory?"
        if not ask_confirmation(action_msg):
            return {'status': 'skipped', 'file': file, 'type': file_type}

    # Prepare target directory
    if not os.path.exists(target_dir) and not dry_run:
        os.makedirs(target_dir)

    try:
        if dry_run:
            print_move('Will move', file, file_type, dry_run=True)
            return {'status': 'would_move', 'file': file, 'type': file_type}
        else:
            if quarantine:
                # First move to quarantine
                shutil.move(original_path, quarantine_path)
                # Then to final destination
                shutil.move(quarantine_path, new_path)
            else:
                # Direct move
                shutil.move(original_path, new_path)

            if not silent:
                print_move('Moved', file, file_type)

            if logger:
                logger.info(f"Moved {file} to {file_type} directory")

            return {'status': 'success', 'file': file, 'type': file_type}
    except Exception as e:
        error_msg = f"Error moving {file}: {str(e)}"
        print_file_error('Failed to move', file, file_type)

        if logger:
            logger.error(error_msg)

        return {'status': 'error', 'file': file, 'type': file_type, 'error': str(e)}

def revert(abs_path, timestamp=None, dry_run=False, silent=False, logger=None):
    '''
    Given the absolute path to a directory, it reverts the cleanup operation
    performed on it and moves back files to their original location, deleting
    empty folders that remain after files have been moved from them.
    '''
    revert_info_file = get_revert_info_file(abs_path, timestamp)
    revert_info = read_revert_info(revert_info_file)

    if not revert_info:
        available_reverts = list_available_reverts(abs_path)
        if available_reverts:
            print("Available revert points:")
            for i, (ts, date_formatted) in enumerate(available_reverts, 1):
                print(f"{i}. {date_formatted}")
            print("\nSpecify the timestamp with -r option: cleanup -r TIMESTAMP <dir>")
        else:
            print('Nothing to do. No revert information found.')
        return

    if dry_run:
        print_cleaning('When reverting cleanup of', abs_path)
    elif not silent:
        print_cleaning('Reverting cleanup of', abs_path)

    # Statistics
    stats = {'success': 0, 'error': 0, 'skipped': 0}

    # Progress bar if not silent
    file_info_list = revert_info.get(abs_path, [])
    progress_bar = None if silent else tqdm(total=len(file_info_list), desc="Reverting", unit="file")

    for file_info in file_info_list:
        file_type = file_info['type']
        file = file_info['name']
        prev_path = os.path.join(abs_path, file_type, file)
        new_path = os.path.join(abs_path, file)

        try:
            if dry_run:
                if os.path.exists(prev_path):
                    print_move('Will move back', file, file_type, revert=True, dry_run=True)
                    stats['success'] += 1
                else:
                    print_file_error('Will fail to move back', file, file_type, dry_run=True)
                    stats['error'] += 1
            else:
                if os.path.exists(prev_path):
                    os.renames(prev_path, new_path)
                    if not silent:
                        print_move('Moved back', file, file_type, revert=True)
                    stats['success'] += 1
                    if logger:
                        logger.info(f"Reverted {file} from {file_type} directory")
                else:
                    print_file_error('Could not find', file, file_type)
                    stats['error'] += 1
                    if logger:
                        logger.error(f"Could not find {file} in {file_type} directory during revert")
        except Exception as e:
            print_file_error('Failed to move back', file, file_type)
            stats['error'] += 1
            if logger:
                logger.error(f"Error reverting {file}: {str(e)}")

        if progress_bar:
            progress_bar.update(1)

    if progress_bar:
        progress_bar.close()

    # Clean up empty directories
    if not dry_run:
        for root, dirs, files in os.walk(abs_path, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if not os.listdir(dir_path) and dir_path != abs_path:
                    os.rmdir(dir_path)
                    if logger:
                        logger.info(f"Removed empty directory: {dir_path}")

    if not dry_run:
        if not silent:
            print_complete('Revert', stats)

    return stats

def scan_directory(directory, recursive=False, include_patterns=None, exclude_patterns=None):
    """
    Scan a directory for files, optionally recursively and with pattern filtering
    """
    files_info = []

    # Convert pattern strings to lists
    include_patterns = include_patterns.split(',') if include_patterns else None
    exclude_patterns = exclude_patterns.split(',') if exclude_patterns else None

    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, directory)

                # Skip files not matching include patterns
                if include_patterns and not any(fnmatch.fnmatch(file, pattern) for pattern in include_patterns):
                    continue

                # Skip files matching exclude patterns
                if exclude_patterns and any(fnmatch.fnmatch(file, pattern) for pattern in exclude_patterns):
                    continue

                extension = get_longest_extension(file)
                if extension:
                    files_info.append({
                        'name': rel_path,
                        'path': file_path,
                        'type': FILE_TYPES[extension]
                    })
    else:
        # Non-recursive scan
        _, _, files = next(os.walk(directory), (None, [], []))
        for file in files:
            file_path = os.path.join(directory, file)

            # Skip files not matching include patterns
            if include_patterns and not any(fnmatch.fnmatch(file, pattern) for pattern in include_patterns):
                continue

            # Skip files matching exclude patterns
            if exclude_patterns and any(fnmatch.fnmatch(file, pattern) for pattern in exclude_patterns):
                continue

            extension = get_longest_extension(file)
            if extension:
                files_info.append({
                    'name': file,
                    'path': file_path,
                    'type': FILE_TYPES[extension]
                })

    return files_info

def cleanup(abs_path, config=None, dry_run=False, silent=False, interactive=False,
            quarantine=False, recursive=False, include_patterns=None, exclude_patterns=None,
            threads=1, logger=None):
    '''
    Given the absolute path to a directory, it organises files in that directory
    into subdirectories based on the files' extensions or custom rules.
    '''
    if not os.path.isdir(abs_path):
        print_dir_error('The specified directory does not exist', abs_path)
        return

    # Scan directory for files to process
    files_info = scan_directory(abs_path, recursive, include_patterns, exclude_patterns)

    if not files_info:
        print('Nothing to do. No matching files found.')
        return

    if dry_run:
        print_cleaning('When cleaning up', abs_path)
    elif not silent:
        print_cleaning('Cleaning up', abs_path)

    # Statistics
    stats = {'success': 0, 'error': 0, 'skipped': 0}

    # Progress bar if not silent
    progress_bar = None if silent else tqdm(total=len(files_info), desc="Processing", unit="file")

    # Process files with multithreading if requested
    revert_list = []

    if threads > 1 and not dry_run and not interactive:
        # Use thread pool for parallel processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            for file_info in files_info:
                future = executor.submit(
                    process_file, file_info, abs_path, config or {},
                    dry_run, interactive, quarantine, True, logger
                )
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result['status'] == 'success':
                    stats['success'] += 1
                    revert_list.append({
                        'name': result['file'],
                        'type': result['type']
                    })
                    if not silent:
                        print_move('Moved', result['file'], result['type'])
                elif result['status'] == 'error':
                    stats['error'] += 1
                elif result['status'] == 'skipped':
                    stats['skipped'] += 1

                if progress_bar:
                    progress_bar.update(1)
    else:
        # Process files sequentially
        for file_info in files_info:
            result = process_file(
                file_info, abs_path, config or {},
                dry_run, interactive, quarantine, silent, logger
            )

            if result['status'] == 'success':
                stats['success'] += 1
                revert_list.append({
                    'name': result['file'],
                    'type': result['type']
                })
            elif result['status'] == 'would_move':
                stats['success'] += 1  # Count dry-run as success
            elif result['status'] == 'error':
                stats['error'] += 1
            elif result['status'] == 'skipped':
                stats['skipped'] += 1

            if progress_bar:
                progress_bar.update(1)

    if progress_bar:
        progress_bar.close()

    if not dry_run:
        if not silent:
            print_complete('Cleanup', stats)

        # Save revert information
        revert_info = {abs_path: revert_list}
        timestamp = save_revert_info(abs_path, revert_info)

        if logger:
            logger.info(f"Cleanup completed. Revert timestamp: {timestamp}")

    return stats

def main():
    arguments = docopt(__doc__)
    dir_path = arguments['<dir>']   # path to the directory to be cleaned
    silent = arguments['--silent']
    dry_run = arguments['--dry-run']
    to_revert = arguments['--revert']
    revert_timestamp = arguments['<timestamp>'] if to_revert else None
    interactive = arguments['--interactive']
    config_file = arguments['--config']
    log_file = arguments['--log']
    include_patterns = arguments['--pattern']
    exclude_patterns = arguments['--exclude']
    recursive = arguments['--recursive']
    threads = int(arguments['--threads']) if arguments['--threads'] else 1
    quarantine = arguments['--quarantine']

    # Set up logging if requested
    logger = setup_logger(log_file) if log_file else None

    # Load configuration if specified
    config = None
    if config_file:
        config = load_config(config_file)
        if not config and not silent:
            print(f"Warning: Could not load config file {config_file}. Using default settings.")

    # Convert dir_path to absolute path
    abs_path = os.path.abspath(dir_path)

    try:
        if to_revert:
            result = revert(abs_path, revert_timestamp, dry_run, silent, logger)
        else:
            result = cleanup(abs_path, config, dry_run, silent, interactive,
                     quarantine, recursive, include_patterns, exclude_patterns,
                     threads, logger)

        # Generate summary report if logging is enabled
        if logger and result:
            logger.info(f"Operation Summary: {result['success']} succeeded, "
                       f"{result['skipped']} skipped, {result['error']} failed")

    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
        if logger:
            logger.warning("Operation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        if logger:
            logger.error(f"Unhandled exception: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
