# 🎮 Key Remapper App

**TH / EN inside one file** · Windows-ready EXE · No Python required

[⬇️ ดาวน์โหลดสำหรับ Windows (.exe)](https://github.com/GDCaster/AutoHotKey/blob/main/AutoKey.exe)


---

แอปสำหรับ **รีแมพปุ่มคีย์บอร์ดและเมาส์** พร้อมโหมดช่วยกด:

* กดค้างสลับ (Hold Toggle)
* กดหลายครั้ง (Multi-Press)
* กดซ้ำอัตโนมัติ (Auto-Repeat)

พัฒนาโดยใช้ **Python + Tkinter + pynput**

---

## 🚀 วิธีติดตั้ง (Windows EXE)

> **แนะนำ:** ใช้ไฟล์ .exe สำเร็จรูป ไม่ต้องติดตั้ง Python หรือไลบรารีใด ๆ

1. ไปที่หน้า **Releases**:
   [https://github.com/your-username/your-repo/releases/latest](https://github.com/GDCaster/AutoHotKey/)
2. ดาวน์โหลดไฟล์ `KeyRemapperApp.exe` (หรือชื่อที่คุณตั้งไว้)
3. ดับเบิลคลิกเพื่อใช้งานได้ทันที

### ⚠️ หมายเหตุ SmartScreen (ครั้งแรกที่เปิด)

* หากมีแจ้งเตือน **Windows protected your PC** ให้กด **More info** → **Run anyway**
* แอปไม่ต้องการสิทธิ์แอดมิน (ยกเว้นบางกรณีที่ระบบตั้งค่าความปลอดภัยไว้สูงมาก)

---

## 🖥️ วิธีใช้งาน (Usage)

* แถบด้านบนมีตัวบอกสถานะ:
  **● กำลังใช้งาน** = แอปกำลังส่งคีย์/คลิก,  **○ พร้อมใช้งาน** = Idle
* ปุ่ม **อยู่บนสุดเสมอ** ช่วยให้หน้าต่างไม่ถูกบัง (ปิด/เปิดได้)
* ปุ่ม **ปิดใช้งาน/เปิดใช้งาน** ใช้หยุดทุกกิจกรรมทันที (หยุด Hold/Repeat ทั้งหมด)

### สร้าง/แก้ไขกฎ (Key Config)

1. กด **เพิ่มการตั้งค่า** → ตั้งชื่อ, ปุ่มต้นทาง (`source_key`), เลือกประเภทการทำงาน, ปุ่มเป้าหมาย (`target_key`)
2. สำหรับ **Multi-Press** ตั้ง `จำนวนครั้ง` และ `ช่วงเวลาระหว่างการกด (วินาที)`
3. สำหรับ **Auto-Repeat** ตั้ง `ช่วงเวลาการกดซ้ำ (วินาที)`
4. กด **บันทึกการตั้งค่า** เพื่อเซฟลงไฟล์ `key_configs.json`

### ประเภทการทำงาน

* **Remap:** กดปุ่ม X = ส่งปุ่ม Y 1 ครั้ง (เช่น `a → b`)
* **Hold Toggle:** กดครั้งแรกเริ่มค้าง, กดอีกครั้งยกเลิก (รองรับการใช้ปุ่มเดียวกัน เช่น `shift → shift`)
* **Multi-Press:** กดปุ่มครั้งเดียว แต่ส่งปุ่มเป้าหมายหลายครั้งต่อเนื่อง
* **Auto-Repeat:** กดเพื่อสลับเปิด/ปิดการยิงปุ่มเป้าหมายซ้ำ ๆ ตามรอบเวลา

### ปุ่มที่รองรับ (ตัวอย่าง)

ตัวอักษร/ตัวเลขทั่วไป (`a-z`, `0-9`), `space`, `enter`, `shift`, `ctrl`, `alt`, `tab`, `esc`, `f1-f12`,
ปุ่มลูกศร `up/down/left/right`, เมาส์: `left_click`, `right_click`, `middle_click`, สกรอลล์: `scroll_up`, `scroll_down`

### เคล็ดลับสำคัญ

* การใช้ปุ่มเดียวกันกับ **Hold Toggle** และ **Auto-Repeat** ทำได้ (เช่น `e → e`)
* หลีกเลี่ยงการใช้ปุ่มเดียวกันกับ **Remap** (อาจทำให้วนซ้ำ)

---

## 🗂️ ไฟล์คอนฟิก

* แอปบันทึก/โหลดกฎจาก `key_configs.json` ในโฟลเดอร์เดียวกับ .exe
* มีตัวอย่างไฟล์ `sample_configs.json` สำหรับอ้างอิง

---

## 🧰 ติดตั้งจากซอร์ส (ไม่จำเป็นสำหรับผู้ใช้ทั่วไป)

> เฉพาะกรณีต้องการรันจากซอร์สโค้ด

1. ติดตั้ง **Python 3.9+**
2. ติดตั้งไลบรารี:

   ```bash
   pip install pynput
   ```
3. รันโปรแกรม:

   ```bash
   python main.py
   ```

---

## 🔒 ความเป็นส่วนตัว

แอปทำงานภายในเครื่อง ไม่ส่งข้อมูลออกอินเทอร์เน็ต
การรีแมพปุ่ม/คลิกใช้ผ่านไลบรารี `pynput` เท่านั้น

---

# 🎮 Key Remapper App (English)

**Windows-ready EXE** · No Python required
[⬇️ Download for Windows (.exe)](https://github.com/GDCaster/AutoHotKey/blob/main/AutoKey.exe)

An app for **keyboard/mouse remapping** with helper modes:

* **Hold Toggle** (press once to hold, press again to release)
* **Multi-Press** (press once → send multiple times)
* **Auto-Repeat** (toggle repeating at a fixed interval)

Built with **Python + Tkinter + pynput**

---

## 🚀 Installation (Windows EXE)

1. Visit **Releases**:
   [https://github.com/your-username/your-repo/releases/latest](https://github.com/GDCaster/AutoHotKey/)
2. Download `KeyRemapperApp.exe`
3. Double-click to run

### SmartScreen note (first launch)

If Windows shows **"Windows protected your PC"**, click **More info** → **Run anyway**.
The app does **not** require admin rights under normal settings.

---

## 🖥️ Usage

* Top bar shows activity: **● Active** when sending keys/clicks, **○ Ready** when idle
* **Always on top** toggle keeps the window above others
* **Enable/Disable** instantly stops all holds/repeats

### Create/Edit rules (Key Config)

1. Click **Add** → set name, `source_key`, action type, `target_key`
2. For **Multi-Press**, set `press_count` and `press_delay` (seconds)
3. For **Auto-Repeat**, set `repeat_interval` (seconds)
4. Click **Save** to persist in `key_configs.json`

### Action types

* **Remap:** press X → send Y once (e.g., `a → b`)
* **Hold Toggle:** press to start holding, press again to release (supports same-key like `shift → shift`)
* **Multi-Press:** press once → send target key multiple times
* **Auto-Repeat:** toggle repeating at a fixed interval

### Supported keys (examples)

Letters/numbers (`a-z`, `0-9`), `space`, `enter`, `shift`, `ctrl`, `alt`, `tab`, `esc`, `f1-f12`,
arrows `up/down/left/right`, mouse: `left_click`, `right_click`, `middle_click`, scroll: `scroll_up`, `scroll_down`

---

## 🗂️ Config file

* Rules are saved/loaded from `key_configs.json` next to the .exe
* See `sample_configs.json` for examples

---

## 🧰 Run from source (optional)

1. Install **Python 3.9+**
2. Install deps:

   ```bash
   pip install pynput
   ```
3. Run:

   ```bash
   python main.py
   ```

---

## 📦 Building the EXE (for maintainers)

If you need to rebuild the EXE yourself:

```bash
pip install pyinstaller
pyinstaller -F -w -i app_icon.ico main.py
```

* `-F` single-file, `-w` no console window, `-i` icon file (optional)

---

## 📝 License

Specify your license here (e.g., MIT).
You may also add usage terms if needed.




