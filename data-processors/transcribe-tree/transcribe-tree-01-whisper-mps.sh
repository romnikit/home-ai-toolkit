#!/bin/bash

# This script is expected to scout through the folderes tree
# and for each file supported by Whisper (.mo3, .mp4...) if it was not already processed
# (has no generated .txt/.srt with the same name) it tries to generate the transcribation.
# Note, that only .txt and .srt transcribation resutls are preserved, other 3 (.vtt, .json, .tsv) are deleted.


# List of extensions to include (only known to be supported media types).
INCLUDE_EXTENSIONS="mp3 mp4 ogg ts"

# List of extensions that are not to be processed 100%.
EXCLUDE_EXTENSIONS="pdf json txt sh doc docx lnk DS_Store"

# Function to check if a .txt AND .srt files exist with the same name.
# This signals that we already processed the file with Whisper.
check_already_processed() {
  local file="$1"
  local base_name="${file%.*}" # Remove extension

  if [[ ! -f "${base_name}.json" ]]; then
    return 1 # .txt OR .srt does not exist.
  else
    return 0 # .txt AND .srt exists.
  fi

  # if [[ ! -f "${base_name}.txt" || ! -f "${base_name}.srt" ]]; then
  #    return 1 # .txt OR .srt does not exist.
  # else
  #    return 0 # .txt AND .srt exists.
  # fi
}

# Function to call whisper
call_whisper() {
  local file="$1"
  local file_dir="$(dirname "$file")"
  local base_name="${file%.*}" # Remove extension

  whisper-mps \
    --file-name "${file}" \
    --model-name large-v3-turbo \
    --output-file-name "${base_name}.json"
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

# Folder processing cycle (every foldeer is considered a tree).
process_tree() {
  # Iterate over files recursively from the current directory
  find "$1" -type f -print0 | while IFS= read -r -d '' file; do
    # Get the file extension
    extension="${file##*.}"

    # Check if the extension is in the ignore list
    ignore=true
    for include_ext in $INCLUDE_EXTENSIONS; do
      if [[ "$extension" == "$include_ext" ]]; then
        ignore=false
        break
      fi
    done

    if [[ "$ignore" == "false" ]]; then
      # Check if a .txt file with the same name exists
      if check_already_processed "$file"; then
        echo "Skipping '$file': is already processed"
      else
        echo "Processing '$file' with Whisper..."
        call_whisper "$file"
        #clean_generated_files "$file" # Clean up after whisper
      fi
      # One-time.
      # clean_generated_files "$file" # Clean up after whisper
    else
      ignore_silently=false
      for no_log_ext in $EXCLUDE_EXTENSIONS; do
        if [ "$extension" = "$no_log_ext" ]; then
          ignore_silently=true
          break
        fi
      done
      if [ "$ignore_silently" = "false" ]; then
        echo "Ignoring $file (extension: $extension)"
      fi
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
