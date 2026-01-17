; Jittery Momentum Cursor Script
; Press Shift+J to toggle the effect on/off
; Press Shift+T to toggle canvas boundary restriction (ON by default)
; Adds jitter that biases toward movement direction, proportional to speed
; Difficult to write legibly, but not impossible

#Requires AutoHotkey v2.0
#SingleInstance Force

; Global variables
effectEnabled := false
boundaryRestrictionEnabled := true  ; ON by default

; Cursor tracking variables
lastX := 0
lastY := 0

; Canvas bounds (loaded from config file)
canvasLeft := 0
canvasTop := 0
canvasRight := 0
canvasBottom := 0

; Tuning parameters - adjust these to change difficulty
baseJitter := 0          ; Random jitter amount (pixels)
speedMultiplier := 10   ; How much speed amplifies the throw distance
directionBias := 1     ; How much jitter biases toward movement direction (0-1)
                         ; 0 = pure random, 1 = always in movement direction
perpendicularBias := 1  ; How much to add perpendicular drift (makes writing hard)

; Load canvas bounds from JSON file
LoadCanvasBounds() {
    global canvasLeft, canvasTop, canvasRight, canvasBottom

    configFile := A_ScriptDir . "\..\canvas_bounds.json"

    if !FileExist(configFile) {
        return false
    }

    try {
        jsonContent := FileRead(configFile)
        bounds := Jxon_Load(&jsonContent)

        canvasLeft := bounds["left"]
        canvasTop := bounds["top"]
        canvasRight := bounds["right"]
        canvasBottom := bounds["bottom"]

        return true
    } catch {
        return false
    }
}

; Check if cursor is within canvas bounds
IsWithinCanvas(x, y) {
    global canvasLeft, canvasTop, canvasRight, canvasBottom, boundaryRestrictionEnabled

    ; If boundary restriction is disabled, act like cursor is always within canvas
    if (!boundaryRestrictionEnabled) {
        return true
    }

    return (x >= canvasLeft && x <= canvasRight && y >= canvasTop && y <= canvasBottom)
}

; Simple JSON parser for our needs
Jxon_Load(&src) {
    ; Remove whitespace
    src := RegExReplace(src, "[\s\r\n]", "")

    obj := Map()

    ; Extract key-value pairs
    Loop Parse src, "," {
        if (InStr(A_LoopField, ":")) {
            pair := StrSplit(A_LoopField, ":")
            key := RegExReplace(pair[1], '["{}\[\]]', "")
            value := RegExReplace(pair[2], '["{}\[\]]', "")
            obj[key] := Integer(value)
        }
    }

    return obj
}

; Shift+T to toggle boundary restriction
+t:: {
    global boundaryRestrictionEnabled
    boundaryRestrictionEnabled := !boundaryRestrictionEnabled

    if (boundaryRestrictionEnabled) {
        ToolTip("Boundary Restriction ON")
    } else {
        ToolTip("Boundary Restriction OFF")
    }

    SetTimer(RemoveToolTip, -1000)
}

; Shift+J to toggle effect
+j:: {
    global effectEnabled, lastX, lastY
    effectEnabled := !effectEnabled

    if (effectEnabled) {
        ; Load canvas bounds when enabling effect
        if (LoadCanvasBounds()) {
            ToolTip("Jitter ON (Bounds loaded)")
        } else {
            ToolTip("Jitter ON (No bounds)")
        }
        MouseGetPos(&lastX, &lastY)
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

    ; Only apply jitter if cursor is within canvas bounds
    if (!IsWithinCanvas(x, y)) {
        lastX := x
        lastY := y
        SetTimer(JitterCursor, Random(8, 20))
        return  ; Skip jitter, cursor behaves normally
    }

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
