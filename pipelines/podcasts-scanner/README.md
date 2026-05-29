# Podcasts scanner.

The approach is:

- Setup Python virtual environment under ~/.pyenv/envs/...
- Download selected podcasts (scan only last year, tune if re-scan is needed).
- Transcribe relevant media files (into .json).
- Extract text information into .txt files with the same names.

Expected results:
- .txt files on the podcasts volume ready to be searched by any indexing engine 'right now'.
- .json files containing more information in accordance to Whisperer approach.

Further embedding / query / agentic interface is outside of this regular pipeline.
