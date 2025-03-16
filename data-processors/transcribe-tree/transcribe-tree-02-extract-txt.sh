#!/bin/bash

# This script is expected to scout through the folderes tree
# and extract .txt transcription for each .json file being result of
# appropriate Whisper processing jobs (checks for supported media file and appropriate .json file).
# The expected result is a tree with .txt files (re-)placed.

# List of extensions to include (only known to be supported media types).
INCLUDE_EXTENSIONS=" 'mp3' 'ogg' 'wav' 'm4a' 'm4b' 'aac' 'mkv' 'ts' 'mp4' 'mov' "

# List of extensions that are not to be processed 100%.
EXCLUDE_EXTENSIONS=" 'pdf' 'json' 'txt' 'sh' 'doc' 'docx' 'xlsx' 'lnk' 'ds_store' 'css' 'html' \
    'js' 'png' 'jpg' 'epub' 'fb3' 'zip' 'db' 'без названия' 'prc' 'webm' 'tgs' "


# Function to check if a .json file exists for the provided media file.
check_already_processed() {
  local file="$1"
  local base_name="${file%.*}" # Remove extension

  if [[ ! -f "${base_name}.json" ]]; then
    return 1
  else
    return 0
  fi
}

# Extract .txt file.
extract_txt() {
  local file="$1"
  local file_dir="$(dirname "$file")"
  local base_name="${file%.*}" # Remove extension
  python -m json.tool --no-ensure-ascii <"${base_name}.json" | jq -r '.text' >"${base_name}.txt"
  ### --- just for test --- rm "${base_name}.txt"
}

# Function to clean generated files (except .txt and .srt)
clean_generated_files() {
  # local fn="${1}"
  # echo "Performing cleanup for '$fn'..."
  local base_name="${1%.*}" # Remove extension
  local files_to_clean=$(ls "$base_name".*)
  echo "$files_to_clean" | while IFS= read -r file; do
    local extension="${file##*.}"
    if [[ "$extension" == "vtt" || "$extension" == "tsv" || "$extension" == "srt"  || "$extension" == "txt" ]]; then
      echo "Removing generated file: $file"
      rm "$file"
    fi
  done
}

process_tree() {
  # Iterate over files recursively from the current directory
  find "$1" -type f -print0 | while IFS= read -r -d '' file; do

    filename="${file##*/}"
    if [[ "$filename" == "$file" || "$filename" == *.* ]]; then
      extension="${filename##*.}"
    else
      # No extension.
      continue
    fi

    if echo "$EXCLUDE_EXTENSIONS" | grep -q -w -i " '$extension' "; then
      continue  # Skip processing if found in exclusion list
    fi

    # Check if the extension is in the include list
    ignore=true
    if echo "$INCLUDE_EXTENSIONS" | grep -q -w -i " '$extension' "; then
        ignore=false
    fi

    if [[ "$ignore" == "false" ]]; then
      # Check if a .txt file with the same name exists
      if check_already_processed "$file"; then
        echo "DO : Extract .txt for '$file' ..."
        extract_txt "$file"
      else
        echo ".. : media without .json result."
      fi
    else
        echo "Ignoring $file (extension: $extension)"
    fi
  done
}

### ===============================================================
### Main logic (actually pretty simple).
### ===============================================================

# Default to '.' if no arguments are given
if [ "$#" -eq 0 ]; then
    set -- "."
fi

# Iterate over each argument
for item in "$@"; do
    echo "PROCESSING: $item"
    process_tree "$item"
done
