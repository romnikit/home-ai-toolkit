#!/bin/bash

# Needed Homebrew packages.
# brew install xz

# Whisper-mps actually require Python >= 3.10.
PYTHON_VERSION="3.14.5"
PYTHON_PATH="$HOME/.pyenv/envs/env-whisper-$PYTHON_VERSION"
pyenv install -s $PYTHON_VERSION
pyenv shell $PYTHON_VERSION
python3 -m venv $PYTHON_PATH
source "$PYTHON_PATH/bin/activate"

# At some point I need to free from the moviepy and move whisper-mps to use 2.x.
pip install -U pip torch torchvision torchaudio
# moviepy==1.0.3

#pip install -U openai-whisper
pip install -U whisper-mps
#pip install git+https://github.com/romnikit/whisper-mps.git
