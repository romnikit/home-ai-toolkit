#!/bin/bash

pyenv local 3.11.11
python3 -m venv whisper-env-3-11
source whisper-env-3-11/bin/activate

# At some point I need to free from the moviepy and move whisper-mps to use 2.x.
pip install -U pip torch torchvision torchaudio moviepy==1.0.3

#pip install -U openai-whisper
#pip install -U whisper-mps
pip install git+https://github.com/romnikit/whisper-mps.git
