#!/usr/bin/env python3
"""
CleanUp Demo Script
This script creates a test directory with various file types
and demonstrates how CleanUp organizes them.
"""

import os
import sys
import shutil
import tempfile
import subprocess
import random
import time
from datetime import datetime, timedelta

# Create a temporary directory for the demo
DEMO_DIR = os.path.join(tempfile.gettempdir(), "cleanup_demo")

# List of sample file extensions to create
FILE_TYPES = {
    "txt": ["sample", "notes", "readme", "document", "data"],
    "pdf": ["report", "manual", "invoice", "book"],
    "jpg": ["photo", "screenshot", "wallpaper", "image"],
    "mp3": ["song", "recording", "audio"],
    "mp4": ["video", "recording", "clip"],
    "docx": ["letter", "resume", "contract"],
    "xlsx": ["budget", "data", "sheet"],
    "zip": ["archive", "backup"],
    "py": ["script", "test", "example"],
    "json": ["config", "data", "settings"],
    "html": ["webpage", "template", "index"],
    "css": ["style", "theme"],
    "js": ["script", "module"]
}

def create_sample_files():
    """Create sample files of various types in the demo directory"""
    print(f"Creating sample files in {DEMO_DIR}...")

    # Create the demo directory if it doesn't exist
    if os.path.exists(DEMO_DIR):
        shutil.rmtree(DEMO_DIR)
    os.makedirs(DEMO_DIR)

    # Create files with different dates
    now = datetime.now()
    dates = [
        now,
        now - timedelta(days=30),  # 1 month ago
        now - timedelta(days=90),  # 3 months ago
        now - timedelta(days=180), # 6 months ago
        now - timedelta(days=365), # 1 year ago
    ]

    # Create files with different sizes
    sizes = [
        100,      # Tiny files (100 bytes)
        10240,    # Small files (10 KB)
        102400,   # Medium files (100 KB)
        1048576,  # Large files (1 MB)
    ]

    file_count = 0
    # Create files of each type
    for ext, prefixes in FILE_TYPES.items():
        for prefix in prefixes:
            # Create files with different dates and sizes
            for i, date in enumerate(dates):
                for j, size in enumerate(sizes):
                    # Create filename
                    filename = f"{prefix}_{i}_{j}.{ext}"
                    filepath = os.path.join(DEMO_DIR, filename)

                    # Create file with specific size
                    with open(filepath, 'wb') as f:
                        f.write(b'0' * size)

                    # Set file modification time
                    mod_time = time.mktime(date.timetuple())
                    os.utime(filepath, (mod_time, mod_time))

                    file_count += 1

    # Create some special pattern files
    special_files = [
        "README.md",
        "backup_important.zip",
        "data_analysis.csv",
        "profile_photo.jpg",
        "screenshot_20230101.png",
        ".hidden_file.txt",
        "temp.tmp",
        "~temporary.txt"
    ]

    for filename in special_files:
        filepath = os.path.join(DEMO_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(b'0' * random.choice(sizes))
        file_count += 1

    print(f"Created {file_count} sample files!")

def list_directory(directory):
    """List the contents of a directory"""
    print(f"\nContents of {directory}:")
    print("-" * 50)

    items = os.listdir(directory)
    items.sort()

    for item in items:
        path = os.path.join(directory, item)
        if os.path.isdir(path):
            print(f"📁 {item}/")
        else:
            size = os.path.getsize(path)
            if size < 1024:
                size_str = f"{size} bytes"
            elif size < 1024 * 1024:
                size_str = f"{size/1024:.1f} KB"
            else:
                size_str = f"{size/(1024*1024):.1f} MB"

            print(f"📄 {item} ({size_str})")

def run_cleanup(options=""):
    """Run cleanup with the given options"""
    cmd = f"cleanup {options} {DEMO_DIR}"
    print(f"\nRunning: {cmd}")
    print("-" * 50)

    try:
        result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running cleanup: {e}")
        print(e.stdout)
        print(e.stderr)

def interactive_demo():
    """Run an interactive demo"""
    while True:
        print("\nCleanUp Demo Options:")
        print("1. Create sample files")
        print("2. List files in demo directory")
        print("3. Run basic cleanup")
        print("4. Run cleanup with dry-run")
        print("5. Run cleanup with pattern filter (*.pdf,*.docx)")
        print("6. Run cleanup with size-based organization (using example_config.yaml)")
        print("7. Revert the last cleanup")
        print("8. Exit")

        choice = input("\nEnter your choice (1-8): ")

        if choice == '1':
            create_sample_files()
            list_directory(DEMO_DIR)
        elif choice == '2':
            list_directory(DEMO_DIR)
        elif choice == '3':
            run_cleanup("")
            list_directory(DEMO_DIR)
        elif choice == '4':
            run_cleanup("-d")
        elif choice == '5':
            run_cleanup("-p '*.pdf,*.docx'")
            list_directory(DEMO_DIR)
        elif choice == '6':
            config_path = os.path.abspath("example_config.yaml")
            if os.path.exists(config_path):
                run_cleanup(f"-c {config_path}")
                list_directory(DEMO_DIR)
            else:
                print(f"Error: Config file not found at {config_path}")
        elif choice == '7':
            run_cleanup("-r")
            list_directory(DEMO_DIR)
        elif choice == '8':
            print("Exiting demo...")
            break
        else:
            print("Invalid choice, please try again.")

def main():
    print("=" * 50)
    print("CleanUp Demonstration Script")
    print("=" * 50)

    # Check if cleanup is installed
    try:
        subprocess.run(["cleanup", "-h"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: CleanUp is not installed or not in PATH.")
        print("Please install it first with: pip install .")
        sys.exit(1)

    # Run interactive demo
    interactive_demo()

    # Cleanup the demo directory when done
    if os.path.exists(DEMO_DIR):
        print(f"\nCleaning up demo directory: {DEMO_DIR}")
        try:
            shutil.rmtree(DEMO_DIR)
            print("Demo directory removed.")
        except Exception as e:
            print(f"Error removing demo directory: {e}")

if __name__ == "__main__":
    main()