#!/bin/bash

source ./00-tools/setup-env-whisper.sh
./00-tools/download-podcasts.sh
./00-tools/transcribe-tree-01-whisper-mlx.py
./00-tools/transcribe-tree-02-extract-txt.py
