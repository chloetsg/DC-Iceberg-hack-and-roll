; Jittery Momentum Cursor Script
; Press Shift+J to toggle the effect on/off
; Adds jitter that biases toward movement direction, proportional to speed
; Difficult to write legibly, but not impossible

#Requires AutoHotkey v2.0
#SingleInstance Force

; Global variables
effectEnabled := false

; Cursor tracking variables
lastX := 0
lastY := 0

; Tuning parameters - adjust these to change difficulty
baseJitter := 0          ; Random jitter amount (pixels)
speedMultiplier := 10   ; How much speed amplifies the throw distance
directionBias := 1     ; How much jitter biases toward movement direction (0-1)
                         ; 0 = pure random, 1 = always in movement direction
perpendicularBias := 1  ; How much to add perpendicular drift (makes writing hard)

; Shift+J to toggle effect
+j:: {
    global effectEnabled, lastX, lastY
    effectEnabled := !effectEnabled
    
    if (effectEnabled) {
        MouseGetPos(&lastX, &lastY)
        ToolTip("Jitter ON")
        SetTimer(JitterCursor, 5)
    } else {
        ToolTip("Jitter OFF")
        SetTimer(JitterCursor, 0)
    }
    
    SetTimer(RemoveToolTip, -1000)
}

JitterCursor() {
    global lastX, lastY, baseJitter, speedMultiplier, directionBias, perpendicularBias

    MouseGetPos(&x, &y)

    ; Calculate velocity and speed
    velocityX := x - lastX
    velocityY := y - lastY
    speed := Sqrt(velocityX**2 + velocityY**2)

    lastX := x
    lastY := y

    ; Generate random jitter (constant amount)
    randomX := Random(-baseJitter, baseJitter)
    randomY := Random(-baseJitter, baseJitter)

    if (speed < 1) {
        ; Stationary: jitter in place then snap back
        MouseMove(x + randomX, y + randomY)
        Sleep(5)
        MouseMove(x, y)
    } else {
        ; Moving: blend random jitter with directional bias
        dirScale := baseJitter / speed
        dirX := velocityX * dirScale
        dirY := velocityY * dirScale

        ; Add perpendicular drift (90 degrees to movement direction)
        perpX := -dirY * perpendicularBias  ; Perpendicular vector
        perpY := dirX * perpendicularBias

        ; Combine: random jitter + directional bias + perpendicular drift, then amplify by speed
        offsetX := (randomX * (1 - directionBias) + dirX * directionBias + perpX) * (1 + speed * speedMultiplier)
        offsetY := (randomY * (1 - directionBias) + dirY * directionBias + perpY) * (1 + speed * speedMultiplier)
        MouseMove(x + offsetX, y + offsetY)
    }

    SetTimer(JitterCursor, Random(8, 20))
}

RemoveToolTip() {
    ToolTip()
}
