#!/bin/bash

# This script is expected to scout through the folderes tree
# and extract .txt transcription for each .json file being result of
# appropriate Whisper processing jobs (checks for supported media file and appropriate .json file).
# The expected result is a tree with .txt files (re-)placed.

# List of the extensions to include (only known to be supported media types).
INCLUDE_EXTENSIONS=" 'mp3' 'ogg' 'wav' 'm4a' 'm4b' 'aac' 'mkv' 'ts' 'mp4' 'mov' 'flv' 'avi' 'wmv' "

# List of the extensions that are not to be processed 100%.
EXCLUDE_EXTENSIONS=" 'pdf' 'json' 'txt' 'sh' 'doc' 'docx' 'xlsx' 'lnk' 'ds_store' 'css' 'html' \
    'js' 'png' 'jpg' 'jpeg' 'bmp' 'epub' 'fb2' 'fb3' 'zip' 'db' 'без названия' 'prc' 'webm' 'tgs' 'url' \
    'image' 'webp' 'mhml' "


# Function to check if a .json file exists for the provided media file.
check_has_json() {
  local base_name="$1"
  if [[ ! -f "${base_name}.json" ]]; then
    return 1
  else
    return 0
  fi
}

# Function to check if a .txt file exists for the provided media file.
check_has_txt() {
  local base_name="$1"
  if [[ ! -f "${base_name}.txt" ]]; then
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
  do_new_line=false
  find "$1" -type f -print0 | while IFS= read -r -d '' file; do

    file_name="${file##*/}" # File name without extension
    if [[ "$file_name" == "$file" || "$file_name" == *.* ]]; then
      extension="${file_name##*.}"
    else
      # No extension.
      echo -n "."
      do_new_line=true
      continue
    fi

    base_name="${file%.*}" # Path + file name but not extension.

    if echo "$EXCLUDE_EXTENSIONS" | grep -q -w -i " '$extension' "; then
      echo -n "."
      do_new_line=true
      continue  # Skip processing if found in exclusion list
    fi

    # Check if the extension is in the include list
    if echo "$INCLUDE_EXTENSIONS" | grep -q -w -i " '$extension' "; then

      # Check if a .txt file with the same name exists
      if check_has_json "$base_name"; then
        if check_has_txt "$base_name"; then
          echo -n "+" # Already has .txt.
          do_new_line=true
        else
          if $do_new_line; then
            echo
            do_new_line=false
          fi
          echo "DO : Extract .txt for '$file' ..."
          extract_txt "$file"
        fi
      else
        echo -n "x" # Media but no .json.
        do_new_line=true
      fi
    fi
  done
  echo
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
