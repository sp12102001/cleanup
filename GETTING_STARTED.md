# Getting Started with CleanUp

This guide will help you quickly start using CleanUp to organize your files.

## Installation

### Using pip

```bash
pip install cleanup
```

### From Source

```bash
git clone https://github.com/faheel/cleanup.git
cd cleanup
pip install -e .
```

## Basic Usage

CleanUp organizes files into folders based on their extensions by default:

```bash
cleanup ~/Downloads
```

This will move all files in your Downloads directory into subdirectories named after their types.

## Common Use Cases

### 1. Organizing a Messy Directory

To clean up a directory with lots of mixed files:

```bash
cleanup ~/Desktop
```

### 2. Safely Preview Before Organizing

To see what changes would be made without actually moving anything:

```bash
cleanup -d ~/Documents
```

### 3. Organizing with User Input

To approve each move operation:

```bash
cleanup -i ~/Pictures
```

### 4. Working with Large Directories

For faster processing of large directories:

```bash
cleanup --threads 8 ~/Videos
```

### 5. Organizing Only Specific File Types

To organize only certain file types:

```bash
cleanup -p "*.pdf,*.docx,*.xlsx" ~/Documents
```

### 6. Reverting a Previous Cleanup

If you want to undo a cleanup operation:

```bash
cleanup -r ~/Documents
```

## Using Configuration Files

For more advanced organization, create a configuration file:

1. Create a file named `config.yaml` with your desired rules (see `example_config.yaml`)
2. Run CleanUp with the config file:

```bash
cleanup -c config.yaml ~/Documents
```

You can also place a config file at `~/.config/cleanup/config.yaml` and it will be used automatically.

## Logging

To keep a log of all operations:

```bash
cleanup -l cleanup.log ~/Downloads
```

## Tips & Tricks

1. **Always use `-d` (dry run) first** when organizing important directories
2. **Use `-q` (quarantine)** when dealing with critical files
3. **Combine options** for more control:
   ```bash
   cleanup -di -p "*.mp3,*.flac" --threads 4 ~/Music
   ```
4. **Create custom configs** for different directories with specific organization needs
5. **Use recursive mode with care** as it can process a large number of files

## Getting Help

To see all available options:

```bash
cleanup -h
```

For more detailed information, refer to the [README.md](README.md) file.