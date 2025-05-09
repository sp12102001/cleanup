"""
Configuration management for CleanUp.
"""

import os
import json
import yaml

# Default configuration
DEFAULT_CONFIG = {
    "rules": [
        {
            "type": "extension",
            "description": "Default extension-based categorization"
        }
    ],
    "quarantine": False,
    "recursive": False,
    "threads": 1,
    "include_patterns": [],
    "exclude_patterns": []
}

def load_config(config_path):
    """
    Load configuration from a YAML or JSON file.

    Args:
        config_path (str): Path to the configuration file

    Returns:
        dict: Configuration dictionary or None if failed
    """
    if not os.path.exists(config_path):
        return None

    try:
        _, ext = os.path.splitext(config_path)
        with open(config_path, 'r') as f:
            if ext.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            elif ext.lower() == '.json':
                return json.load(f)
            else:
                # Try JSON as default
                return json.load(f)
    except Exception:
        return None

def save_config(config_path, config):
    """
    Save configuration to a YAML or JSON file.

    Args:
        config_path (str): Path to the configuration file
        config (dict): Configuration dictionary

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        _, ext = os.path.splitext(config_path)
        with open(config_path, 'w') as f:
            if ext.lower() in ['.yaml', '.yml']:
                yaml.dump(config, f, default_flow_style=False)
            else:
                # Use JSON as default
                json.dump(config, f, indent=2)
        return True
    except Exception:
        return False

def get_user_config_path():
    """
    Returns the path to the user configuration file.

    Returns:
        str: Path to the user configuration file
    """
    home_dir = os.path.expanduser("~")
    config_dirs = [
        os.path.join(home_dir, '.config', 'cleanup'),
        os.path.join(home_dir, '.cleanup')
    ]

    for config_dir in config_dirs:
        if os.path.exists(config_dir):
            for filename in ['config.yaml', 'config.yml', 'config.json', '.cleanup.yaml', '.cleanup.json']:
                config_path = os.path.join(config_dir, filename)
                if os.path.exists(config_path):
                    return config_path

    # Default location
    default_dir = os.path.join(home_dir, '.config', 'cleanup')
    os.makedirs(default_dir, exist_ok=True)
    return os.path.join(default_dir, 'config.yaml')

def create_example_config(config_path=None):
    """
    Create an example configuration file.

    Args:
        config_path (str, optional): Path to save the configuration file.
                                     If None, uses the default user config path.

    Returns:
        str: Path to the created configuration file
    """
    if config_path is None:
        config_path = get_user_config_path()

    example_config = {
        "rules": [
            {
                "type": "extension",
                "description": "Default extension-based categorization"
            },
            {
                "type": "pattern",
                "patterns": {
                    "*.txt": "text",
                    "*.log": "logs",
                    "backup*": "backups"
                }
            },
            {
                "type": "size",
                "size_ranges": [
                    {
                        "min": 0,
                        "max": 1024 * 1024,  # 1MB
                        "folder": "small_files"
                    },
                    {
                        "min": 1024 * 1024,
                        "max": 100 * 1024 * 1024,  # 100MB
                        "folder": "medium_files"
                    },
                    {
                        "min": 100 * 1024 * 1024,
                        "folder": "large_files"
                    }
                ]
            },
            {
                "type": "date",
                "date_ranges": [
                    {
                        "start": "2020-01-01",
                        "end": "2020-12-31",
                        "folder": "2020_files"
                    },
                    {
                        "start": "2021-01-01",
                        "end": "2021-12-31",
                        "folder": "2021_files"
                    }
                ]
            }
        ],
        "quarantine": False,
        "recursive": False,
        "threads": 4,
        "include_patterns": ["*.txt", "*.pdf", "*.jpg"],
        "exclude_patterns": ["*.tmp", "~*"]
    }

    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    save_config(config_path, example_config)
    return config_path