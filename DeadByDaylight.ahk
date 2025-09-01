; Dead by Daylight - Custom Hold Key Toggle
; กดปุ่มที่เลือก 1 ครั้ง = เริ่มกดค้าง, กดอีกครั้ง = หยุดกดค้าง
; กด F1 เพื่อเปิด/ปิดการใช้งาน

#NoEnv
#SingleInstance Force
#Persistent
#InstallKeybdHook
#UseHook

SendMode Input
SetWorkingDir %A_ScriptDir%

; ======== การตั้งค่าที่ปรับได้ ========
KeyName := "Shift"      ; ปุ่มที่ต้องการให้กดค้าง (เช่น Shift, Space, Ctrl, Alt, X, F เป็นต้น)
ToggleKey := "F1"       ; ปุ่มสลับเปิด/ปิดการทำงาน
EmergencyKey := "Esc"   ; ปุ่มหยุดฉุกเฉิน
; =====================================

; ตัวแปรสถานะ
ToggleEnabled := true
KeyHeld := false
KeyPressed := false

; แสดง tooltip เมื่อเริ่มต้น
ShowMainToolTip("เปิดใช้งาน")
SetTimer, RemoveToolTip, 3000

; Hotkey แบบไดนามิกสำหรับปุ่มหลัก
Hotkey, IfWinNotActive
Hotkey, % "~" . KeyName, HandleKeyPress
Hotkey, % "~" . EmergencyKey, HandleEmergency

; ปุ่มเปิด/ปิดการทำงาน
Hotkey, %ToggleKey%, ToggleFunction

return

; ======== ฟังก์ชันหลัก ========
HandleKeyPress:
    if (!ToggleEnabled || KeyPressed)
        return
        
    KeyPressed := true
    SetTimer, WaitKeyRelease, -10
return

WaitKeyRelease:
    ; รอจนกว่าปุ่มจะถูกปล่อย
    KeyWait, %KeyName%
    KeyPressed := false
    
    if (!ToggleEnabled)
        return
    
    if (KeyHeld) {
        ; หยุดกดค้าง
        Send, {%KeyName% up}
        KeyHeld := false
        ShowStatusToolTip("หยุดกดค้างแล้วXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    } else {
        ; เริ่มกดค้าง
        Send, {%KeyName% down}
        KeyHeld := true
        ShowStatusToolTip("กำลังกดค้าง🟢🟢🟢OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
    }
return

HandleEmergency:
    if (KeyHeld) {
        Send, {%KeyName% up}
        KeyHeld := false
        ShowEmergencyToolTip("หยุดการกดค้างฉุกเฉิน!")
    }
return

ToggleFunction:
    ToggleEnabled := !ToggleEnabled
    
    ; ยกเลิกการกดค้างเมื่อปิดการทำงาน
    if (!ToggleEnabled && KeyHeld) {
        Send, {%KeyName% up}
        KeyHeld := false
    }
    
    ShowMainToolTip(ToggleEnabled ? "เปิดใช้งาน" : "ปิดใช้งาน")
    SetTimer, RemoveToolTip, 2000
return

; ======== ฟังก์ชันแสดง Tooltip ========
ShowMainToolTip(status) {
    ToolTip, Dead by Daylight [%KeyName% Toggle]`n%ToggleKey%: เปิด/ปิดการใช้งาน`n%KeyName%: กดค้าง/หยุดกดค้าง`nสถานะ: %status%, 10, 10, 1
}

ShowStatusToolTip(message) {
    ToolTip, %message%, 10, 50, 2
    SetTimer, RemoveToolTip2, 1000
}

ShowEmergencyToolTip(message) {
    ToolTip, %message%, 10, 90, 3
    SetTimer, RemoveToolTip3, 1500
}

; ======== ฟังก์ชันลบ Tooltip ========
RemoveToolTip:
    ToolTip, , , , 1
return

RemoveToolTip2:
    ToolTip, , , , 2
return

RemoveToolTip3:
    ToolTip, , , , 3
return

; ======== ฟังก์ชันจัดการการปิด ========
ExitApp:
    if (KeyHeld) {
        Send, {%KeyName% up}
    }
ExitApp

; ======== เมนู System Tray ========
Menu, Tray, NoStandard
Menu, Tray, Add, เปิด/ปิดการใช้งาน (%ToggleKey%), ToggleFunction
Menu, Tray, Add
Menu, Tray, Add, ตั้งค่าปุ่ม, OpenSettings
Menu, Tray, Add, ออกจากโปรแกรม, ExitFunction
Menu, Tray, Default, เปิด/ปิดการใช้งาน (%ToggleKey%)
Menu, Tray, Click, 1
return

OpenSettings:
    MsgBox, 64, การตั้งค่า, ปุ่มปัจจุบัน:`n- ปุ่มหลัก: %KeyName%`n- ปุ่มสลับ: %ToggleKey%`n- ปุ่มหยุดฉุกเฉิน: %EmergencyKey%`n`nแก้ไขโดยเปิดสคริปต์ใน Notepad, 5
return

ExitFunction:
    if (KeyHeld) {
        Send, {%KeyName% up}
    }
    ExitApp
return