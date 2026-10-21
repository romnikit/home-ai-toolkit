#!/bin/bash

# Download given Youtube video. Based on `yt-dlp` tool.
# brew install yt-dlp
# All parameters go transparently, the only required parameter is a YouTube URL.
#
# How to get available formats:
#       yt-dlp -F <URL>
# Example of merged download with 2 stream IDs (Audio+Video):
#       yt-dlp -f 135+140 --merge-output-format mp4 <URL>

yt-dlp $*
