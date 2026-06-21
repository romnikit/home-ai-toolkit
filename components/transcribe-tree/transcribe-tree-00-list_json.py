#!/usr/bin/env python3

import os
import sys
import json
from collections import deque
from pathlib import Path
from typing import Iterator

# This scanner iterates over media files and outputs only ready JSON files.
# This allows any validations or processing over transcribation results.
# Note that files are sorted and subfolders are processed only after all files on the upper level are processed.

# List of the extensions to include (only known to be supported media types).
INCLUDE = {
    "mp3", "ogg", "wav", "m4a", "m4b", "aac",
    "mkv", "m4v", "ts", "mp4", "mov", "flv", "avi", "wmv", "webm",
}

# List of the extensions that are not to be processed 100%.
EXCLUDE = {
    "pdf", "json", "txt", "sh", "doc", "docx", "xlsx", "lnk", "ds_store", "css", "html",
    "js", "png", "jpg", "jpeg", "jfif", "bmp", "epub", "fb2", "fb3", "zip", "db",
    "без названия", "prc", "tgs", "url", "image", "webp", "mhtml", "rar",
}

def check_has_json(base_name: str) -> bool:
    # Equivalent to: [[ -f "${base_name}.json" ]]
    return os.path.isfile(f"{base_name}.json")

def check_has_txt(base_name: str) -> bool:
    # Equivalent to: [[ -f "${base_name}.txt" ]]
    return os.path.isfile(f"{base_name}.txt")

def process_file(file_path: str) -> None:
    # Given media file path (file_path) check if we have appropriate JSON
    # and if so, output its name.
    base_name = file_path.rsplit(".", 1)[0]
    if check_has_json(base_name):
        json_path = f"{base_name}.json"
        sys.stdout.write(f"{json_path}\n")

def report_file_skip():
    # sys.stdout.write(".")
    # sys.stdout.flush()
    do_new_line = True
    pass

def report_root_start(item: str):
    # print(f"PROCESSING: {item}")
    pass

def walk(root: Path):
    """Fast scandir-based recursion, yields file Paths."""
    stack = [root]
    queue = deque([root])
    while stack:
        d = queue.popleft()
        try:
            with os.scandir(d) as it:
                entries = sorted(it, key=lambda e: e.name, reverse=False)

            for entry in entries:
                if entry.is_dir(follow_symlinks=False):
                    queue.append(Path(entry.path))
                elif entry.is_file(follow_symlinks=False):
                    yield Path(entry.path)

        except (PermissionError, FileNotFoundError):
            continue

def process_tree(root: str) -> None:
    do_new_line = False
    # seen = 0
    for file_path in walk(Path(root)):
        # seen += 1
        # if seen % 1000 == 0:
        #     print(f"Scanned {seen} files...", end="\r")

        file_str = str(file_path)
        file_name = file_path.name  # basename

        # Bash extension logic:
        # if [[ "$file_name" == "$file" || "$file_name" == *.* ]]; then extension="${file_name##*.}" else no ext
        # Effective result: treat "no dot" as no extension.
        if "." in file_name:
            extension = file_name.rsplit(".", 1)[1]
        else:
            report_file_skip()
            continue

        base_name = file_str.rsplit(".", 1)[0]

        if extension.lower() in EXCLUDE:
            # Explicit exclude list check (case-insensitive).
            report_file_skip()
        elif extension.lower() in INCLUDE:
            # Include list check (case-insensitive)
            process_file(file_str)

    # print()  # final newline like the bash script

def main(argv: list[str]) -> int:
    if not argv:
        argv = ["."]
    for item in argv:
        report_root_start(item)
        process_tree(item)
    return 0

if __name__ == "__main__":
    import sys
    roots = sys.argv[1:] or ["."]
    main(roots)
