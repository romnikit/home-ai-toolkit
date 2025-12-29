#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path

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

# Choose your marker. Your current script uses .json as "already processed".
MARKER_EXT = ".json"

def should_consider(path: Path) -> bool:
    name = path.name
    if "." not in name:
        return False
    ext = name.rsplit(".", 1)[1].lower()
    if ext in EXCLUDE:
        return False
    return ext in INCLUDE

def already_processed(path: Path) -> bool:
    base = path.with_suffix("")  # removes only last suffix
    return (base.with_suffix(MARKER_EXT)).exists()

def run_whisper(path: Path) -> None:
    base = path.with_suffix("")
    out = base.with_suffix(".json")
    subprocess.run(
        ["whisper-mps",
         "--file-name", str(path),
         "--model-name", "large-v3-turbo",
         "--output-file-name", str(out)],
        check=True
    )

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
    seen = 0
    for file_path in walk(Path(root)):
        seen += 1
        if seen % 1000 == 0:
            print(f"Scanned {seen} files...", end="\r")

        if not should_consider(file_path):
            continue
        if already_processed(file_path):
            continue

        print(f"Processing '{file_path}' with Whisper...")
        run_whisper(file_path)
        print()  # end the \r line

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
