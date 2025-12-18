#!/bin/bash

# Whisper-mps actually require Python >= 3.10.
PYTHON_VERSION="3.11.14"
pyenv install -s $PYTHON_VERSION
pyenv shell $PYTHON_VERSION
python3 -m venv "whisper-env-$PYTHON_VERSION"
source "whisper-env-$PYTHON_VERSION/bin/activate"

# At some point I need to free from the moviepy and move whisper-mps to use 2.x.
pip install -U pip torch torchvision torchaudio moviepy<3.0.0,>=2.0.0

#pip install -U openai-whisper
#pip install -U whisper-mps
pip install -U git+https://github.com/romnikit/whisper-mps.git
