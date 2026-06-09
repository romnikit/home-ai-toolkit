#!/bin/bash

# Download given Youtube video. Based on `yt-dlp` tool.
# brew install yt-dlp
# All parameters go transparently, the only required parameter is a YouTube URL.

yt-dlp $*
