#!/bin/bash

pyenv local 3.11.11
python3 -m venv whisper-env-3-11
source whisper-env-3-11/bin/activate

pip install -U pip torch torchvision torchaudio

#pip install -U openai-whisper
pip install -U whisper-mps
