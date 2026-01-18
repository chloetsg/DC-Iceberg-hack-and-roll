#Requires AutoHotkey v2.0
#SingleInstance Force

; Configuration
global isActive := true  ; Auto-start enabled
global boundaryRestrictionEnabled := false  ; OFF by default for tkinter compatibility
global minInterval :=  5000    ; Minimum time between teleports (ms)
global maxInterval := 8000   ; Maximum time between teleports (ms)

; Canvas bounds (loaded from config file)
canvasLeft := 0
canvasTop := 0
canvasRight := 0
canvasBottom := 0

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

; Shift+B to toggle boundary restriction (changed from Shift+T to avoid conflict)
+b:: {
    global boundaryRestrictionEnabled
    boundaryRestrictionEnabled := !boundaryRestrictionEnabled

    if (boundaryRestrictionEnabled) {
        ToolTip("Boundary Restriction ON")
    } else {
        ToolTip("Boundary Restriction OFF")
    }

    SetTimer(RemoveTooltip, -1500)
}

; Auto-start the teleporting effect
StartTeleporting() {
    global isActive
    if (isActive) {
        ; Load canvas bounds when enabling effect (optional for tkinter)
        LoadCanvasBounds()
        SetTimer(TeleportCursor, RandomInterval())
    }
}

; Shift+T to toggle teleporting effect
+t:: {
    global isActive
    isActive := !isActive

    if (isActive) {
        ; Load canvas bounds when enabling effect
        if (LoadCanvasBounds()) {
            ToolTip("TP: ON (Bounds loaded)")
        } else {
            ToolTip("TP: ON (No bounds)")
        }
        SetTimer(RemoveTooltip, -1500)
        SetTimer(TeleportCursor, RandomInterval())
    } else {
        ToolTip("TP: OFF")
        SetTimer(RemoveTooltip, -1500)
        SetTimer(TeleportCursor, 0)  ; Disable timer
    }
}

; Start on launch
StartTeleporting()

TeleportCursor() {
    global isActive, canvasLeft, canvasTop, canvasRight, canvasBottom, boundaryRestrictionEnabled

    if (!isActive)
        return

    MouseGetPos(&currentX, &currentY)

    ; Only teleport if cursor is within canvas bounds (or boundary restriction is off)
    if (!IsWithinCanvas(currentX, currentY)) {
        ; Cursor is outside canvas, don't teleport
        SetTimer(TeleportCursor, RandomInterval())
        return
    }

    ; Teleport within canvas bounds
    if (boundaryRestrictionEnabled && canvasRight > canvasLeft && canvasBottom > canvasTop) {
        ; Use canvas dimensions for teleport
        randomX := Random(canvasLeft, canvasRight)
        randomY := Random(canvasTop, canvasBottom)
    } else {
        ; Use screen dimensions if no bounds or restriction disabled
        screenWidth := A_ScreenWidth
        screenHeight := A_ScreenHeight
        randomX := Random(0, screenWidth - 1)
        randomY := Random(0, screenHeight - 1)
    }

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
