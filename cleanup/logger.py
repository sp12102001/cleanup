"""
Logging functionality for CleanUp.
"""

import os
import logging
from datetime import datetime

def setup_logger(log_file=None):
    """
    Set up and configure the logger.

    Args:
        log_file (str, optional): Path to the log file. If None, uses default location.

    Returns:
        logging.Logger: Configured logger
    """
    if log_file is None:
        # Use default log file in user's home directory
        log_dir = os.path.join(os.path.expanduser("~"), '.cleanup', 'logs')
        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"cleanup_{timestamp}.log")

    # Create directory for log file if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # Configure logger
    logger = logging.getLogger('cleanup')
    logger.setLevel(logging.DEBUG)

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # Format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(file_handler)

    # Log start of session
    logger.info("CleanUp session started")
    logger.info(f"Log file: {log_file}")

    return logger

def log_action(logger, action, file_path, destination=None, status="success", error=None):
    """
    Log a file action.

    Args:
        logger (logging.Logger): The logger to use
        action (str): The action performed (e.g., 'move', 'revert')
        file_path (str): Path to the file
        destination (str, optional): Destination path or category
        status (str): Status of the action ('success', 'error', 'skipped')
        error (str, optional): Error message if status is 'error'
    """
    if not logger:
        return

    message = f"{action.capitalize()}: {file_path}"
    if destination:
        message += f" -> {destination}"

    if status == "success":
        logger.info(message)
    elif status == "error":
        error_msg = f"{message} - FAILED: {error}"
        logger.error(error_msg)
    elif status == "skipped":
        logger.info(f"{message} - SKIPPED")

def get_log_summary(log_file):
    """
    Generate a summary of actions from a log file.

    Args:
        log_file (str): Path to the log file

    Returns:
        dict: Summary statistics
    """
    if not os.path.exists(log_file):
        return None

    summary = {
        'total_actions': 0,
        'successful': 0,
        'failed': 0,
        'skipped': 0,
        'start_time': None,
        'end_time': None
    }

    try:
        with open(log_file, 'r') as f:
            for line in f:
                if 'CleanUp session started' in line:
                    timestamp = line.split(' - ')[0].strip()
                    summary['start_time'] = timestamp

                if 'Move' in line or 'Revert' in line:
                    summary['total_actions'] += 1
                    if 'FAILED' in line:
                        summary['failed'] += 1
                    elif 'SKIPPED' in line:
                        summary['skipped'] += 1
                    else:
                        summary['successful'] += 1

                timestamp = line.split(' - ')[0].strip()
                summary['end_time'] = timestamp
    except Exception:
        pass

    return summary