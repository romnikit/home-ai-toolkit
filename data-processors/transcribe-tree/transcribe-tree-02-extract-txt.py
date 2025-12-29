#!/usr/bin/env python3

import os
import sys
import json
from pathlib import Path
from typing import Iterator

# Translation of transcribe-tree-02-extract-txt.sh (phase 2)
# Uses a fast scandir-based walk() generator, but keeps output semantics:
#   '.' = ignored/no extension/excluded
#   '+' = has txt already
#   'x' = media file but missing json
#   "DO : Extract .txt for '...' ..." = extraction action

# List of the extensions to include (only known to be supported media types).
INCLUDE = {
    "mp3", "ogg", "wav", "m4a", "m4b", "aac",
    "mkv", "m4v", "ts", "mp4", "mov", "flv", "avi", "wmv",
}

# List of the extensions that are not to be processed 100%.
EXCLUDE = {
    "pdf", "json", "txt", "sh", "doc", "docx", "xlsx", "lnk", "ds_store", "css", "html",
    "js", "png", "jpg", "jpeg", "jfif", "bmp", "epub", "fb2", "fb3", "zip", "db",
    "без названия", "prc", "webm", "tgs", "url", "image", "webp", "mhtml", "rar",
}

def check_has_json(base_name: str) -> bool:
    # Equivalent to: [[ -f "${base_name}.json" ]]
    return os.path.isfile(f"{base_name}.json")

def check_has_txt(base_name: str) -> bool:
    # Equivalent to: [[ -f "${base_name}.txt" ]]
    return os.path.isfile(f"{base_name}.txt")

def extract_txt(file_path: str) -> None:
    # Equivalent target: python -m json.tool --no-ensure-ascii < base.json | jq -r '.text' > base.txt
    base_name = file_path.rsplit(".", 1)[0]
    json_path = f"{base_name}.json"
    txt_path = f"{base_name}.txt"

    # Parse json and extract `.text`
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    text = data.get("text", "")
    # jq -r would print raw text (and "null" becomes empty); we emulate by defaulting to "".
    if text is None:
        text = ""

    with open(txt_path, "w", encoding="utf-8") as out:
        out.write(text)

def walk(root: Path):
    """Fast scandir-based recursion, yields file Paths."""
    stack = [root]
    while stack:
        d = stack.pop()
        try:
            with os.scandir(d) as it:
                for entry in it:
                    if entry.is_dir(follow_symlinks=False):
                        stack.append(Path(entry.path))
                    elif entry.is_file(follow_symlinks=False):
                        yield Path(entry.path)
        except PermissionError:
            continue
        except FileNotFoundError:
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
            sys.stdout.write(".")
            sys.stdout.flush()
            do_new_line = True
            continue

        base_name = file_str.rsplit(".", 1)[0]

        # Exclude list check (case-insensitive)
        if extension.lower() in EXCLUDE:
            sys.stdout.write(".")
            sys.stdout.flush()
            do_new_line = True
            continue

        # Include list check (case-insensitive)
        if extension.lower() in INCLUDE:
            # Media candidate: now check json/txt state
            if check_has_json(base_name):
                if check_has_txt(base_name):
                    sys.stdout.write("+")  # Already has .txt
                    sys.stdout.flush()
                    do_new_line = True
                else:
                    if do_new_line:
                        print()
                        do_new_line = False
                    print(f"DO : Extract .txt for '{file_str}' ...")
                    extract_txt(file_str)
            else:
                sys.stdout.write("x")  # Media but no .json
                sys.stdout.flush()
                do_new_line = True
        else:
            # In bash: for non-included and non-excluded, it prints nothing (just silently skips).
            # We keep that behavior.
            continue

    print()  # final newline like the bash script

def main(argv: list[str]) -> int:
    if not argv:
        argv = ["."]
    for item in argv:
        print(f"PROCESSING: {item}")
        process_tree(item)
    return 0

if __name__ == "__main__":
    import sys
    roots = sys.argv[1:] or ["."]
    main(roots)
