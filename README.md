# CleanUp

[![GitHub Actions][gh-actions-shield]][gh-actions-link]
[![PyPI][pypi-shield]][pypi-link]
[![License][license-shield]][license-link]

A powerful command line utility that organises files in a directory into subdirectories based on customizable rules, including file extensions, patterns, sizes, and dates.

## Features

- **Customizable Organization Rules** - Sort files by extension, pattern, size, date, and more
- **Interactive Mode** - Approve or reject each move operation individually
- **Safe Operations** - Quarantine mode to prevent accidental data loss
- **Detailed Logging** - Comprehensive logs of all operations
- **Multiple Revert Points** - Revert to any previous cleanup operation
- **Advanced Filtering** - Include/exclude files based on patterns
- **Recursive Processing** - Organize files in subdirectories
- **Multi-threading** - Speed up processing of large directories
- **Cross-Platform** - Works on Windows, macOS, and Linux

## Usage

![Usage](https://i.imgur.com/iATfu3Y.png)

When run without any options, CleanUp organizes the files in the specified directory into subdirectories based on the files' extensions.

### Basic Examples

```bash
# Basic cleanup of a directory
cleanup ~/Downloads

# Preview what would happen (dry run)
cleanup -d ~/Documents

# Interactively approve each move operation
cleanup -i ~/Pictures

# Process a directory and all its subdirectories
cleanup --recursive ~/Music

# Only organize PDF and image files
cleanup -p "*.pdf,*.jpg,*.png" ~/Documents

# Exclude executable files
cleanup -x "*.exe,*.dll,*.sh" ~/Downloads

# Use 4 threads for faster processing
cleanup --threads 4 ~/Videos
```

### Command-Line Options

* #### `-d`, `--dry-run`

  Just displays the changes that would be made, without actually doing anything.

  ```bash
  cleanup -d path/to/dir        # dry run the cleanup
  cleanup -dr path/to/dir       # dry run the reverting a cleanup
  ```

* #### `-s`, `--silent`

  Prevents displaying any information while performing operations. Errors, however, are displayed irrespective of whether this option is enabled or not.

  ```bash
  cleanup -s path/to/dir        # silently cleanup
  cleanup -sr path/to/dir       # silently revert a cleanup
  ```

* #### `-r`, `--revert`

  Reverts the cleanup of a directory. You can specify a timestamp to revert to a specific cleanup.

  ```bash
  cleanup -r path/to/dir                 # revert the most recent cleanup
  cleanup -r 20220415123045 path/to/dir  # revert to a specific cleanup by timestamp
  ```

* #### `-i`, `--interactive`

  Enable interactive mode to approve or reject each move operation.

  ```bash
  cleanup -i path/to/dir        # interactively clean up a directory
  ```

* #### `-q`, `--quarantine`

  Move files to a temporary location before finalizing the move, preventing accidental data loss.

  ```bash
  cleanup -q path/to/dir        # use quarantine for safer moves
  ```

* #### `-c`, `--config`

  Specify a configuration file (YAML or JSON) to customize cleanup behavior.

  ```bash
  cleanup -c config.yaml path/to/dir  # use custom configuration
  ```

* #### `-l`, `--log`

  Specify a log file to record all operations.

  ```bash
  cleanup -l cleanup.log path/to/dir  # log all operations to a file
  ```

* #### `-p`, `--pattern`

  Specify file patterns to include (comma-separated).

  ```bash
  cleanup -p "*.txt,*.pdf" path/to/dir  # only process text and PDF files
  ```

* #### `-x`, `--exclude`

  Specify file patterns to exclude (comma-separated).

  ```bash
  cleanup -x "*.exe,*.dll" path/to/dir  # exclude executable and DLL files
  ```

* #### `--recursive`

  Process subdirectories recursively.

  ```bash
  cleanup --recursive path/to/dir  # process all subdirectories
  ```

* #### `--threads`

  Number of threads to use for processing (default: 1).

  ```bash
  cleanup --threads 4 path/to/dir  # use 4 threads for faster processing
  ```

* #### `-h`, `--help`

  Displays the help text.

  ```bash
  cleanup -h
  ```

## Configuration File

You can customize CleanUp behavior using a configuration file (YAML or JSON). This allows for powerful organization rules beyond simple file extensions.

### Configuration Example

```yaml
rules:
  # Default rule: organize by file extension
  - type: extension
    description: Default extension-based categorization

  # Pattern-based rules
  - type: pattern
    patterns:
      "*.txt": text
      "*.log": logs
      "backup*": backups
      "report*.pdf": reports

  # Size-based rules
  - type: size
    size_ranges:
      - min: 0
        max: 1048576  # 1MB
        folder: small_files
      - min: 1048576
        max: 104857600  # 100MB
        folder: medium_files
      - min: 104857600
        folder: large_files

  # Date-based rules (using file modification time)
  - type: date
    date_ranges:
      - start: "2020-01-01"
        end: "2020-12-31"
        folder: 2020_files
      - start: "2021-01-01"
        end: "2021-12-31"
        folder: 2021_files
      - start: "2022-01-01"
        end: "2022-12-31"
        folder: 2022_files

# Global settings
quarantine: false
recursive: false
threads: 4
include_patterns:
  - "*.txt"
  - "*.pdf"
  - "*.jpg"
exclude_patterns:
  - "*.tmp"
  - "~*"
```

### Rule Precedence

When multiple rules could apply to a file, the rules are evaluated in the following order:
1. Pattern-based rules
2. Size-based rules
3. Date-based rules
4. Extension-based rules (default fallback)

## Advanced Usage Examples

### Creating a Log Report

```bash
# Run cleanup with logging enabled
cleanup -l cleanup.log ~/Downloads

# The log file contains detailed information about all operations
cat cleanup.log
```

### Using Quarantine Mode for Safety

```bash
# First move files to a temporary location before final destination
cleanup -q ~/Important_Files
```

### Multi-threaded Processing for Large Directories

```bash
# Use 8 threads for faster processing of large directories
cleanup --threads 8 ~/Videos
```

### Managing Multiple Revert Points

```bash
# When reverting without a timestamp, it shows available revert points
cleanup -r ~/Documents

# Reverting to a specific cleanup operation
cleanup -r 20230524135721 ~/Documents
```

## Development

### Setup

1. Clone the repo and `cd` into it.

2. Set up a Python 3 virtual environment using [pipenv](https://docs.pipenv.org):
   ```bash
   pipenv --three         # create Python 3 virtual environment
   pipenv install --dev   # install all dependencies
   pipenv shell           # activate virtual environment shell
   ```

3. The cleanup script can now be run from the root directory of the project:
   ```bash
   python3 -m cleanup.cleanup -h
   ```

### Test

Make sure you're in the root directory of the project. You can then run the test using:
```bash
python3 -m tests.test
```

## License

This project is licensed under the terms of the [MIT license][license-link].


[gh-actions-shield]: https://img.shields.io/github/actions/workflow/status/faheel/cleanup/ci.yml?style=for-the-badge&logo=github
[gh-actions-link]: https://github.com/faheel/cleanup/actions/workflows/ci.yml
[pypi-shield]: https://img.shields.io/pypi/v/cleanup.svg?style=for-the-badge
[pypi-link]: https://pypi.org/project/cleanup
[license-shield]: https://img.shields.io/github/license/faheel/cleanup.svg?style=for-the-badge
[license-link]: https://github.com/faheel/cleanup/blob/master/LICENSE
