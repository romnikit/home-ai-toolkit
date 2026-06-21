#!/usr/bin/env python3

import os
import sys
import json
from collections import deque
from pathlib import Path
from typing import Iterator

import ollama

import re
import unicodedata
from dataclasses import dataclass

# Please bear in mind, Ollama must be installed to do this.
#
# brew install ollama
#

# Gemma 4 (4b network) is considered the best for now.
MODEL_NAME = 'gemma4:e4b'

# --- CONFIGURATION ---
#MODEL_NAME = "qwen2.5:1.5b"
#MODEL_NAME = 'qwen2.5:7b'
#MODEL_NAME = 'llama3.2:3b'
#MODEL_NAME = 'llama3.1:8b'
#MODEL_NAME = 'gemma3:4b'
#MODEL_NAME = 'gemma4:e4b'
#MODEL_NAME = 'gemma:7b'
#MODEL_NAME = 'mistral:7b'
#MODEL_NAME = 'mistral-nemo:12b'
#MODEL_NAME = 'phi3:14b'


# Translation of transcribe-tree-02-extract-txt.sh (phase 2)
# Uses a fast scandir-based walk() generator, but keeps output semantics:
#   '.' = ignored/no extension/excluded
#   '+' = has txt already
#   'x' = media file but missing json
#   "DO : Extract .txt for '...' ..." = extraction action

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

# Target word count per LLM invocation. This is not a hard limit as if we have no paragraphs detected in buffer
# and still have segments, we just need a bigger buffer.
BUFFER_WORD_LIMIT = 500

def check_has_json(base_name: str) -> bool:
    # Equivalent to: [[ -f "${base_name}.json" ]]
    return os.path.isfile(f"{base_name}.json")

def check_has_txt(base_name: str) -> bool:
    # Equivalent to: [[ -f "${base_name}.txt" ]]
    return os.path.isfile(f"{base_name}.txt")

# Call this at the start of your automated pipeline execution loop
def start_ollama():
    ensure_model(MODEL_NAME)


def ensure_model(model_name: str):
    """
    Checks if a model is installed locally. If not, pulls it from the Ollama registry.
    """
    try:
        # Get the list of locally pulled models
        local_models = ollama.list()
        #print(local_models)

        installed_names = [m.model for m in getattr(local_models, 'models', [])]
        #print('---------------------------------')
        #print(installed_names)

        # Handle tag normalization (e.g., 'llama3.1' vs 'llama3.1:latest')
        is_installed = any(
            name == model_name or name.startswith(f"{model_name}:") 
            for name in installed_names
        )
        #print(f"INSTALLED: {is_installed}")

        if not is_installed:
            print(f"📦 Model '{model_name}' not found. Downloading via Ollama...")
            # This will stream the download progress to your console
            ollama.pull(model_name)
            print(f"✅ Success: '{model_name}' is ready to use.")
        else:
            print(f"⚡ Model '{model_name}' is already verified local.")

    except Exception as e:
        print(f"❌ Failed to verify or pull model: {e}")

# ------------------------------------------------
#

default_system_prompt_debug = """
Find paragraph breaks in numbered transcript lines.

Output only numbers from the provided list.
Each number means: this line is the last line of the paragraph.
Output one paragraph break per line with the following line format:

<number>: <short reason>

If there are no paragraph breaks, output nothing.
"""

default_system_prompt = """
Find paragraph breaks in numbered transcript lines.

Output only numbers from the provided list.
Each number means: this line is the last line of the paragraph.
Output one paragraph break per line.

If there are no paragraph breaks, output nothing.
"""

def ask_llm_for_breaks(raw_input: str, system_prompt=default_system_prompt) -> str:
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f"Raw Transcript:\n\n{raw_input}"}
        ],
        options={
            'temperature': 0.0,      # Absolute determinism (prevents creative writing)
        },
        stream=False
    )
    # think=False
    return response['message']['content']
    #return json.loads(response['message']['content'])

# Capitalize first letter of the string.
def capitalize_first(s: str) -> str:
    s = s.strip()
    return s[:1].upper() + s[1:] if s else s

def format_paragraph(phrase_list):

    """Joins phrases, handles capitalization, and ensures a clean sentence end."""
    full_text = ""
    if phrase_list:
        # Strip whitespace from individual pieces
        cleaned_phrases = [p.strip() for p in phrase_list if p.strip()]
        if cleaned_phrases:

            full_text = " ".join(cleaned_phrases)
            # Safely capitalize the start of the paragraph
            full_text = capitalize_first(full_text)

            # Add a period if it doesn't end with sentence-ending punctuation
            if not full_text.endswith(('.', '!', '?')):
                full_text += "."
            full_text += "\n\n"

    return full_text

def process_transcript(raw_segments: list):

    final_output = ""
    current_buffer = []

    segments = raw_segments

    print(f"Processing {len(segments)} sentences...")

    idx = 0
    while idx < len(segments) or current_buffer:

        # 1. Top up buffer from the remaining ASR segments
        have_new_segments = False
        while idx < len(segments):

            # We add at least one segment each time when we need it.
            current_buffer.append(segments[idx])
            have_new_segments = True
            idx += 1

            # Simple heuristic: stop filling if buffer exceeds target word count
            buffer_word_count = sum(len(s.split()) for s in current_buffer)
            if buffer_word_count >= BUFFER_WORD_LIMIT:
                break

        # 2. If we have processed everything (no buffer), stop.
        if not current_buffer:
            break

        valid_breaks = []
        if have_new_segments:

            # 3. Build the numbered prompt block (1-indexed for the LLM)
            prompt_lines = []
            for i, seg in enumerate(current_buffer, start=1):
                text_chunk = seg.strip()
                prompt_lines.append(f"{i}: {text_chunk}")
            numbered_phrases_text = "\n".join(prompt_lines)

            # 4. Call LLM to get paragraph break indices
            print(f"Processing window of {len(current_buffer)} sentence(s)...")
            print(f"<- REQUEST:\n{numbered_phrases_text}\n--------\n")
            model_output = ask_llm_for_breaks(numbered_phrases_text)
            print(f"-> RESPONSE:\n{model_output}\n--------\n")

            # 5. Filter and validate indices returned by LLM
            valid_breaks = sorted([int(num) for num in re.findall(r"^(\d+)", model_output, re.MULTILINE)])

            valid_breaks = sorted(
                int(num)
                for num in re.findall(r"^(\d+)", model_output, re.MULTILINE)
                if int(num) < len(prompt_lines)
            )
            print(f"DETECTED BREAKS: {valid_breaks}")
        else:
            # If we did not get anything new, write out the rest.
            valid_breaks = [len(current_buffer)]
            print(f"LAST TEXT PARAGRAPH: {valid_breaks}")

        # 6. Slice the buffer into paragraphs based on the indices
        start_seg_idx = 0
        last_break_processed = 0
        for b in valid_breaks:
            # Slice segments up to this break index
            paragraph_segments = current_buffer[start_seg_idx:b]
            paragraph_texts = [s for s in paragraph_segments]
            # print(f"-> SELECTED: {start_seg_idx}:{b}\n{paragraph_texts}", end="")
            formatted_paragraph = format_paragraph(paragraph_texts)
            print(f"-> PARAGRAPH: {start_seg_idx}:{b}\n{formatted_paragraph}", end="")
            final_output += formatted_paragraph

            start_seg_idx = b
            last_break_processed = b

        # 7. We drop from current_buffer everything that was processed.
        #   Worst case this will not change it and later will append at least one phrase.
        current_buffer = current_buffer[last_break_processed:]

    return final_output


@dataclass
class FormatValidation:
    ok: bool
    text_equivalent: bool
    layout_clean: bool
    reason: str
    cleaned_output: str


def clean_output_spacing(text: str) -> str:
    """
    Normalizes formatting that is allowed anyway:
    - CRLF -> LF
    - tabs / multiple spaces -> one space
    - trim each line
    - no more than one blank line between paragraphs
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u00a0", " ")

    lines = []
    for line in text.split("\n"):
        line = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(line)

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def canonical_for_text_identity(text: str) -> str:
    """
    Keeps only letters/digits and normalized spaces.
    Removes punctuation, symbols, capitalization, and line-break differences.

    Works for English and Russian because str.isalnum() is Unicode-aware.
    ё and е remain different, which is good: changing ё -> е is a letter change.
    """
    text = unicodedata.normalize("NFKC", text).casefold()

    out = []
    last_was_space = False

    for ch in text:
        if ch.isspace():
            if not last_was_space:
                out.append(" ")
                last_was_space = True
        elif ch.isalnum():
            out.append(ch)
            last_was_space = False
        else:
            # punctuation / symbols removed
            pass

    return "".join(out).strip()

def find_layout_problem(text: str) -> str | None:
    if "\r" in text:
        return "Output contains CR line endings."

    for i, line in enumerate(text.split("\n"), start=1):
        if line != line.strip():
            return f"Line {i} has leading or trailing spaces."
        if "\t" in line:
            return f"Line {i} contains a tab."
        if re.search(r" {2,}", line):
            return f"Line {i} contains multiple consecutive spaces."

    if re.search(r"\n{3,}", text):
        return "Output contains more than one blank line between paragraphs."

    return None

def validate_formatting_only(original: str, formatted: str) -> FormatValidation:
    cleaned = clean_output_spacing(formatted)

    original_canon = canonical_for_text_identity(original)
    formatted_canon = canonical_for_text_identity(cleaned)

    text_equivalent = original_canon == formatted_canon
    layout_problem = find_layout_problem(cleaned)
    layout_clean = layout_problem is None

    result = None
    #print(f"ORIGINAL  : {original_canon}")
    #print(f"FORMATTED : {formatted_canon}")

    if not text_equivalent:
        result = FormatValidation(
            ok=False,
            text_equivalent=False,
            layout_clean=layout_clean,
            reason="Output changed letters/words after removing punctuation/case/spacing.",
            cleaned_output=cleaned,
        )
    elif not layout_clean:
        result = FormatValidation(
            ok=False,
            text_equivalent=True,
            layout_clean=False,
            reason=layout_problem or "Output layout is not clean.",
            cleaned_output=cleaned,
        )
    else:
        result = FormatValidation(
            ok=True,
            text_equivalent=True,
            layout_clean=True,
            reason="OK",
            cleaned_output=cleaned,
        )

    return result

from typing import Iterable

_DOT = "<DOT>"

ABBREVIATIONS = {
    # English
    "mr.", "mrs.", "ms.", "dr.", "prof.", "sr.", "jr.",
    "e.g.", "i.e.", "etc.", "vs.", "approx.", "fig.",
    # Dutch-ish
    "dhr.", "mevr.", "mw.", "m.a.w.", "bijv.", "enz.",
    # Russian-ish
    "т.е.", "т.д.", "т.п.", "т.к.", "н.к.", "г.", "ул.",
}


def protect_dots(text: str) -> str:
    # URLs / domains
    text = re.sub(
        r"\b(?:https?://)?(?:www\.)?[\w.-]+\.[a-zA-Z]{2,}(?:/\S*)?",
        lambda m: m.group(0).replace(".", _DOT),
        text,
    )

    # Decimal numbers: 3.14
    text = re.sub(
        r"(?<=\d)\.(?=\d)",
        _DOT,
        text,
    )

    # Initials: J. R. R. Tolkien
    text = re.sub(
        r"\b(?:[A-ZА-ЯЁ]\.){1,}",
        lambda m: m.group(0).replace(".", _DOT),
        text,
    )

    # Known abbreviations
    for abbr in sorted(ABBREVIATIONS, key=len, reverse=False):
        pattern = re.compile(re.escape(abbr), re.IGNORECASE)
        text = pattern.sub(lambda m: m.group(0).replace(".", _DOT), text)

    return text


def split_sentences(text: str) -> list[str]:
    """
    Split Whisper .text into sentence-like units.
    """
    text = text.strip()
    if not text:
        return []

    # Normalize whitespace.
    text = re.sub(r"\s+", " ", text)

    # Protect some specific dot-containing patterns replacing dots there with the special token.
    protected = protect_dots(text)

    # Capture sentence-ending punctuation plus optional closing quote/bracket.
    # But for now we use more practical and transcribation-friendlier regexp.
    pattern = re.compile(
        r'([.!?…]+["\'”’)\]]*)\s+(?=\S)'
        # r'([.!?…]+["\'”’)\]]*)\s+(?=[A-ZА-ЯЁ0-9"\'“‘(\[])'
    )

    parts = []
    start = 0

    # print(f"[+] TEXT WITH PROTECTED DOTS:\n{protected}")
    for match in pattern.finditer(protected):
        end = match.end(1)  # keep punctuation/quote/bracket in sentence
        sentence = protected[start:end]
        # print(f"[+] SENTENCE: {sentence}")
        parts.append(sentence)
        start = match.end()  # skip whitespace

    sentence = protected[start:]
    # print(f"[+] SENTENCE: {sentence}")
    parts.append(sentence)
    # print("---------------------------------------")

    # Recover protected dots.
    sentences = [
        capitalize_first(part.replace(_DOT, ".").strip())
        for part in parts
        if part.strip()
    ]

    return sentences


def extract_txt(file_path: str) -> None:
    # Equivalent target: python -m json.tool --no-ensure-ascii < base.json | jq -r '.text' > base.txt
    base_name = file_path.rsplit(".", 1)[0]
    json_path = f"{base_name}.json"
    txt_path = f"{base_name}.txt"

    # Parse json and extract `.text`
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Execute processing pipeline
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Original text is in .text (used for validation) but we process .segments.
    input_text = data.get("text", "")
    sentences = split_sentences(input_text)
    formatted_result = process_transcript(sentences)

    print("--- FINAL OUTPUT ---------------------------------")
    print(formatted_result, end="")
    print("--------------------------------------------------")
    validation = validate_formatting_only(input_text, formatted_result)

    if not validation.ok:
        print("❌ Model formatting failed: ", result.reason)
        # Probably retry with stricter prompt / smaller chunk / different model
    else:
        with open(txt_path, "w", encoding="utf-8") as out:
            out.write(formatted_result)

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

    start_ollama()

    for item in argv:
        print(f"PROCESSING: {item}")
        process_tree(item)
    return 0

if __name__ == "__main__":
    import sys
    roots = sys.argv[1:] or ["."]
    main(roots)
