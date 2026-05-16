# Hammerspoon keyboard switcher / hotkeys helper script

## Why

Hammerspoon is an outstanding tool if you need some universal handler for system events in MacOS.

## What

This configuration specifically handles 2 problems:

1. One-key switching between keyboard layouts. The script uses Control+Command+[number] keys for US, Ukrainian and Russian layouts avoiding more specific and heavy tooling.
2. Screen sharing hotkeys helper. The script provides temporary switching to the 'U.S.' keyboard layout while Control key is pressed in Screen Sharing sessions. This allows using keys like Control-U on remote desktop terminals while using non-English layout. Otherwise having local keyboard layouts management under Screen Sharing blocks such hotkeys so you will need constantly to return to US keyboard for any of Control+[key] combinations.

## How

Hammerspoon installation:

````
brew install --cask hammerspoon
````

And then place provided `init.lua` script under `~/.hammerspoon/`. After the next reboot or just 'load script' menu command switcher will be installed. Chances are you will need a different layouts set but I am pretty sure that it will be useful in remote setups with MacOS devices.
