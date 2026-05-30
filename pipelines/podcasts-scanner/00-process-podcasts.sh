#!/bin/bash

source ./00-tools/setup-whisper-env.sh
./00-tools/download-podcasts.sh
./00-tools/transcribe-tree-01-whisper-mps.py
./00-tools/transcribe-tree-02-extract-txt.py
