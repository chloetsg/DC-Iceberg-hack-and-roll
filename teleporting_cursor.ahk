#Requires AutoHotkey v2.0
#SingleInstance Force

; Configuration
global isActive := false
global minInterval := 1000    ; Minimum time between teleports (ms)
global maxInterval := 2000   ; Maximum time between teleports (ms)

; Shift+T to toggle
+t:: {
    global isActive
    isActive := !isActive
    
    if (isActive) {
        ToolTip("Random Cursor: ON")
        SetTimer(RemoveTooltip, -1500)
        SetTimer(TeleportCursor, RandomInterval())
    } else {
        ToolTip("Random Cursor: OFF")
        SetTimer(RemoveTooltip, -1500)
        SetTimer(TeleportCursor, 0)  ; Disable timer
    }
}

TeleportCursor() {
    global isActive
    
    if (!isActive)
        return
    
    ; Get screen dimensions
    screenWidth := A_ScreenWidth
    screenHeight := A_ScreenHeight
    
    ; Generate random coordinates
    randomX := Random(0, screenWidth - 1)
    randomY := Random(0, screenHeight - 1)
    
    ; Move cursor
    MouseMove(randomX, randomY)
    
    ; Set next teleport with random interval
    SetTimer(TeleportCursor, RandomInterval())
}

RandomInterval() {
    global minInterval, maxInterval
    return Random(minInterval, maxInterval)
}

RemoveTooltip() {
    ToolTip()
}
