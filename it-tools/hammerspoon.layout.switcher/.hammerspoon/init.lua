
--[[
    Keyboard layouts switcher for Hammerspoon (3 layouts).
    Also allows to properly translate towards remote desktops simple Ctrl+[key] hotkeys
    due to the temporary switch to 'U.S.' layout under pressed Control.

    Hammerspoon installation:

        brew install --cask hammerspoon

]]

-- We track layout changes and Control key states.
activeLayout = nil
controlDown = false

-- Switch the layout. As it appears under Control we need to remember it as 'prior'.
function switchToLayout(name)
    local success = hs.keycodes.setLayout(name)
    if success then
        -- print("Switch to: " .. name)
        hs.alert.show(name)
        activeLayout = name
    end
end

-- Local layouts binding. Here we use Control+Command+[digit] to switch between U.S., Ukrainian and Russian layouts.
hs.hotkey.bind({"ctrl", "cmd"}, "1", function() switchToLayout("U.S.") end)
hs.hotkey.bind({"ctrl", "cmd"}, "2", function() switchToLayout("Ukrainian") end)
hs.hotkey.bind({"ctrl", "cmd"}, "3", function() switchToLayout("Russian") end)

-- The Control-Key Layout Magic Tap on 'flag changed' events.
controlLayoutTap = hs.eventtap.new({hs.eventtap.event.types.flagsChanged}, function(event)
    local frontApp = hs.application.frontmostApplication()

    local lastControlDown = controlDown

    local flags = event:getFlags()
    controlDown = flags.ctrl

    -- Simple event debug.
    --[[
    if frontApp then
        print("EVENT:" .. frontApp:name())
    else
        print("EVENT WITHOUR APPLICATION")        
    end
    ]]

    -- Only if control was changed and we are under screen sharing or NoMachine session.
    if controlDown ~= lastControlDown and frontApp and (
        frontApp:name() == "Screen Sharing" or frontApp:name() == "NoMachine" ) then

        -- If Control is pressed
        if controlDown then
            activeLayout = hs.keycodes.currentLayout()
            --[[
            if activeLayout then
                print("Control ON: " .. activeLayout)
            else
                print("Control ON")
            end
            ]]
            hs.keycodes.setLayout("U.S.")

        -- If Control is released
        else
            if activeLayout then
                -- print("Control OFF: " .. activeLayout)
                hs.keycodes.setLayout(activeLayout)
            --[[
            else
                print("Control OFF")
            ]]
            end
        end
    end
    return false -- Always pass the event through so the remote Mac gets the Control flag
end)
controlLayoutTap:start()
