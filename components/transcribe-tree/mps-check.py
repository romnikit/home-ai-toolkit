#!/usr/bin/env python3

# How to check actual GPU usage:
# sudo powermetrics --samplers gpu_power -i 1000

import torch

if torch.backends.mps.is_available():
    mps_device = torch.device("mps")
    x = torch.ones(1, device=mps_device)
    print(x)
else:
    print("MPS device not found.")

print('-------------------------------------------')
mps = torch.device("mps")
print(f"torch.device[mps]: {mps}")
print(f"torch.device: {torch.device}")
print(f'mps.is.available: {torch.backends.mps.is_available()}') # Should return True
print(f'torch.mps.is_build: {torch.backends.mps.is_built()}')   # Should return True
print(f'torch.cuda.is_available: {torch.cuda.is_available()}')  # Should return False (since Mac uses Metal, not CUDA)
