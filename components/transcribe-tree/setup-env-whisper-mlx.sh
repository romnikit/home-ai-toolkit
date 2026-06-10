#!/bin/bash

# Needed Homebrew packages.
brew install pyenv ffmpeg xz

# Whisper-mps actually require Python >= 3.10.
PYTHON_VERSION="3.14.5"
PYTHON_PATH="$HOME/.pyenv/envs/env-whisper-mlx-$PYTHON_VERSION"
pyenv install -s $PYTHON_VERSION
pyenv shell $PYTHON_VERSION
python3 -m venv $PYTHON_PATH
source "$PYTHON_PATH/bin/activate"

# MLX whisper, Ollama for post-processing.
pip install -U pip mlx-whisper
pip install -U ollama
