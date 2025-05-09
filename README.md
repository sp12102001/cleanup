# CleanUp

[![GitHub Actions][gh-actions-shield]][gh-actions-link]
[![PyPI][pypi-shield]][pypi-link]
[![License][license-shield]][license-link]

A powerful command line utility that organises files in a directory into subdirectories based on customizable rules, including file extensions, patterns, sizes, and dates.

## Usage

![Usage](https://i.imgur.com/iATfu3Y.png)

When run without any option, it organises the files in the specified directory into subdirectories based on the files' extensions.

### Options

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

## Configuration

You can customize CleanUp behavior using a configuration file (YAML or JSON). Here's an example:

```yaml
rules:
  - type: extension
    description: Default extension-based categorization

  - type: pattern
    patterns:
      "*.txt": text
      "*.log": logs
      "backup*": backups

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

  - type: date
    date_ranges:
      - start: "2020-01-01"
        end: "2020-12-31"
        folder: 2020_files
      - start: "2021-01-01"
        end: "2021-12-31"
        folder: 2021_files

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
