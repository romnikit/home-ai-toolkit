#!/usr/bin/env python3

import gc
import json
import mlx_whisper
import mlx.core as mx
import os
from collections import deque
from pathlib import Path

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

# Choose your marker. Your current script uses .json as "already processed".
MARKER_EXT = ".json"

# Can be defined as "en","nl","ru" and many others (see 'mlx_whisper' output).
LANGUAGE = None

def should_consider(path: Path) -> bool:
    name = path.name
    if "." not in name:
        return False
    ext = name.rsplit(".", 1)[1].lower()
    if ext in EXCLUDE:
        return False
    return ext in INCLUDE

def already_processed(path: Path) -> bool:
    return (path.with_suffix(MARKER_EXT)).exists()

def run_whisper(path: Path) -> None:
    out = path.with_suffix(".json")
    try:

        # 1. Receive transcribation as variable.
        result = mlx_whisper.transcribe(
            str(path),
            path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
            #path_or_hf_repo="mlx-community/whisper-large-v3-mlx",
            initial_prompt = (
                "Keep sentences as short as possible. Use clean punctuation."
            ),
            condition_on_previous_text=False,
            temperature=(0.0, 0.2, 0.4, 0.6),
            compression_ratio_threshold=2.4,
            logprob_threshold=-1.0,
            no_speech_threshold=0.6,
            word_timestamps=True,
            hallucination_silence_threshold=2.0,
            language=LANGUAGE,
            verbose=False
        )

        # 2. Save directly to the target file (handling spaces & dots flawlessly)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False)
            #, indent=2)

    except Exception as e:
        print(f"ERROR transcribing {path.name}: {e}")
        # raise

    finally:
        # Unified Memory cleanup.
        mx.clear_cache()
        gc.collect()

def walk(root: Path):
    """Fast scandir-based recursion, yields file Paths."""
    stack = [root]
    queue = deque([root])
    while queue:
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
