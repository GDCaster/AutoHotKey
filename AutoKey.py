import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
import json
import os
from pynput import keyboard, mouse
from pynput.keyboard import Key, Listener as KeyboardListener
from pynput.mouse import Button, Listener as MouseListener
import queue

class KeyRemapperApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Key Remapper & Simulator")
        self.root.geometry("900x750")
        self.root.resizable(True, True)

        # ตั้งค่าไอคอนของหน้าต่าง
        try:
            self.root.iconbitmap('app_icon.ico')
        except Exception as e:
            print(f"ไม่สามารถโหลดไอคอนได้: {e}")
        
        # ตัวแปรสถานะ
        self.enabled = True
        self.key_configs = []
        self.active_holds = {}  # เก็บสถานะปุ่มที่กำลังกดค้าง
        self.active_repeats = {}  # เก็บสถานะปุ่มที่กำลังกดซ้ำ
        self.keyboard_controller = keyboard.Controller()
        self.mouse_controller = mouse.Controller()
        self.listener = None
        self.config_file = "key_configs.json"
        self.last_activity_time = 0  # เก็บเวลาการใช้งานล่าสุด
        self.activity_indicator = None  # ตัวแสดงสถานะการใช้งาน
        self.is_remapping_active = False  # เก็บสถานะว่ากำลังทำงาน remapping หรือไม่
        
        # Queue สำหรับ thread communication
        self.action_queue = queue.Queue()
        
        # สร้าง GUI
        self.create_gui()
        self.load_config()
        self.start_listener()
        
        # สร้างหน้าต่าง overlay สำหรับข้อความพร้อมใช้งาน
        self.create_ready_overlay()
        
        # เริ่ม thread สำหรับประมวลผล actions
        self.action_thread = threading.Thread(target=self.process_actions, daemon=True)
        self.action_thread.start()
        
        # เริ่ม thread สำหรับอัปเดตสถานะการใช้งาน
        self.activity_thread = threading.Thread(target=self.update_activity_indicator, daemon=True)
        self.activity_thread.start()
        
        # ตั้งค่าการปิดแอป
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # ตั้งค่าให้แอปอยู่บนสุดเสมอ
        self.root.attributes("-topmost", True)
    
    def create_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Title with activity indicator
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        title_label = ttk.Label(title_frame, text="Key Remapper & Simulator", 
                               font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Activity indicator
        self.activity_indicator = ttk.Label(title_frame, text="● ใช้งานแล้ว", 
                                          foreground="green", font=("Arial", 10, "bold"))
        self.activity_indicator.pack(side=tk.RIGHT)
        
        # Always on top toggle
        topmost_frame = ttk.Frame(main_frame)
        topmost_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.topmost_var = tk.BooleanVar(value=True)
        topmost_check = ttk.Checkbutton(topmost_frame, text="อยู่บนสุดเสมอ", 
                                       variable=self.topmost_var, 
                                       command=self.toggle_topmost)
        topmost_check.pack(side=tk.LEFT)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="สถานะ", padding="10")
        status_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="เปิดใช้งาน", 
                                     foreground="green", font=("Arial", 12, "bold"))
        self.status_label.pack(side=tk.LEFT)
        
        self.toggle_button = ttk.Button(status_frame, text="ปิดใช้งาน", 
                                       command=self.toggle_enabled)
        self.toggle_button.pack(side=tk.RIGHT)
        
        # Key configurations frame
        config_frame = ttk.LabelFrame(main_frame, text="การตั้งค่าปุ่ม", padding="10")
        config_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(3, weight=1)
        
        # Treeview for key configs
        columns = ("ชื่อ", "ปุ่มกด", "การทำงาน", "ปุ่มเป้าหมาย", "พารามิเตอร์", "สถานะ")
        self.tree = ttk.Treeview(config_frame, columns=columns, show="tree headings", height=12)
        
        # กำหนดขนาดคอลัมน์
        self.tree.column("#0", width=50)
        for col in columns:
            self.tree.column(col, width=130)
            self.tree.heading(col, text=col)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(config_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        config_frame.columnconfigure(0, weight=1)
        config_frame.rowconfigure(0, weight=1)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(button_frame, text="เพิ่มการตั้งค่า", 
                  command=self.add_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="แก้ไข", 
                  command=self.edit_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="ลบ", 
                  command=self.delete_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="บันทึกการตั้งค่า", 
                  command=self.save_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="โหลดการตั้งค่า", 
                  command=self.load_config).pack(side=tk.LEFT, padx=(0, 5))
        
        # Info frame
        info_frame = ttk.LabelFrame(main_frame, text="คำแนะนำการใช้งาน", padding="10")
        info_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        info_text = """ประเภทการทำงาน:
• รีแมปปุ่ม (Key Remap): กดปุ่ม X = กดปุ่ม Y (เช่น กด a = กด b)
• กดค้าง (Hold Toggle): กดปุ่มเพื่อเริ่ม/หยุดกดค้าง (สามารถใช้ปุ่มเดียวกันได้)
• กดหลายครั้ง (Multi Press): กดปุ่ม 1 ครั้ง = กดปุ่มเป้าหมายหลายครั้งตามที่กำหนด
• กดซ้ำอัตโนมัติ (Auto Repeat): กดปุ่มเพื่อเริ่ม/หยุดการกดซ้ำอัตโนมัติ

⚡ คุณสมบัติใหม่: สามารถใช้ปุ่มเดียวกันเป็นทั้งปุ่มสั่งการและปุ่มเป้าหมายได้!
   เช่น กด Shift เพื่อเริ่มกดค้าง Shift และกดอีกครั้งเพื่อหยุด

ปุ่มที่รองรับ: a-z, 0-9, space, enter, shift, ctrl, alt, tab, esc, f1-f12
เมาส์: left_click, right_click, middle_click, scroll_up, scroll_down"""
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)
    
    def toggle_topmost(self):
        """สลับสถานะอยู่บนสุด"""
        self.root.attributes("-topmost", self.topmost_var.get())
    
    def update_activity_indicator(self):
        """อัปเดตตัวบ่งชี้การใช้งาน"""
        while True:
            # ตรวจสอบว่ามีการทำงาน remapping อยู่หรือไม่
            has_active_actions = (
                any(hold.get('holding', False) for hold in self.active_holds.values()) or
                any(repeat.get('repeating', False) for repeat in self.active_repeats.values()) or
                self.is_remapping_active
            )

            if has_active_actions:
                self.activity_indicator.config(text="● กำลังใช้งาน", foreground="red")
                self.update_ready_overlay("● กำลังใช้งาน", "red")
            else:
                self.activity_indicator.config(text="○ พร้อมใช้งาน", foreground="green")
                self.update_ready_overlay("○ พร้อมใช้งาน", "green")

            time.sleep(0.1)
    
    def toggle_enabled(self):
        self.enabled = not self.enabled
        if self.enabled:
            self.status_label.config(text="เปิดใช้งาน", foreground="green")
            self.toggle_button.config(text="ปิดใช้งาน")
        else:
            self.status_label.config(text="ปิดใช้งาน", foreground="red")
            self.toggle_button.config(text="เปิดใช้งาน")
            # หยุดการทำงานทั้งหมด
            self.stop_all_activities()
    
    def stop_all_activities(self):
        # หยุดการกดค้าง
        for config_id in list(self.active_holds.keys()):
            if self.active_holds[config_id].get('holding'):
                self.stop_hold(config_id)
        
        # หยุดการกดซ้ำ
        for config_id in list(self.active_repeats.keys()):
            if self.active_repeats[config_id].get('repeating'):
                self.stop_repeat(config_id)
    
    def add_config(self):
        self.show_config_dialog()
    
    def edit_config(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกรายการที่ต้องการแก้ไข")
            return
        
        item_id = selection[0]
        config_index = int(item_id) - 1
        if 0 <= config_index < len(self.key_configs):
            self.show_config_dialog(self.key_configs[config_index], config_index)
    
    def delete_config(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกรายการที่ต้องการลบ")
            return
        
        if messagebox.askyesno("ยืนยัน", "ต้องการลบการตั้งค่านี้หรือไม่?"):
            item_id = selection[0]
            config_index = int(item_id) - 1
            if 0 <= config_index < len(self.key_configs):
                config_id = self.key_configs[config_index].get('id')
                
                # หยุดการทำงานถ้ากำลังทำงานอยู่
                if config_id in self.active_holds:
                    self.stop_hold(config_id)
                if config_id in self.active_repeats:
                    self.stop_repeat(config_id)
                
                del self.key_configs[config_index]
                self.refresh_tree()
    
    def show_config_dialog(self, config=None, index=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("ตั้งค่าปุ่ม")
        dialog.geometry("600x750")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # ชื่อการตั้งค่า
        ttk.Label(frame, text="ชื่อการตั้งค่า:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar(value=config.get('name', '') if config else '')
        name_entry = ttk.Entry(frame, textvariable=name_var, width=35)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # ปุ่มกด (ปุ่มต้นทาง)
        ttk.Label(frame, text="ปุ่มกด (ปุ่มต้นทาง):").grid(row=1, column=0, sticky=tk.W, pady=5)
        source_var = tk.StringVar(value=config.get('source_key', '') if config else '')
        source_entry = ttk.Entry(frame, textvariable=source_var, width=35)
        source_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # การทำงาน
        ttk.Label(frame, text="การทำงาน:").grid(row=2, column=0, sticky=tk.W, pady=5)
        action_var = tk.StringVar(value=config.get('action_type', 'remap') if config else 'remap')
        action_combo = ttk.Combobox(frame, textvariable=action_var, 
                                   values=['remap', 'hold_toggle', 'multi_press', 'auto_repeat'], 
                                   state='readonly', width=32)
        action_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # ปุ่มเป้าหมาย
        ttk.Label(frame, text="ปุ่มเป้าหมาย:").grid(row=3, column=0, sticky=tk.W, pady=5)
        target_var = tk.StringVar(value=config.get('target_key', '') if config else '')
        target_entry = ttk.Entry(frame, textvariable=target_var, width=35)
        target_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # ปุ่ม Quick Fill (สำหรับใช้ปุ่มเดียวกัน)
        def quick_fill_same_key():
            if source_var.get().strip():
                target_var.set(source_var.get().strip())
        
        quick_fill_btn = ttk.Button(frame, text="ใช้ปุ่มเดียวกัน", command=quick_fill_same_key)
        quick_fill_btn.grid(row=3, column=2, padx=(10, 0), pady=5)
        
        # จำนวนครั้ง (สำหรับ multi_press)
        ttk.Label(frame, text="จำนวนครั้งที่กด:").grid(row=4, column=0, sticky=tk.W, pady=5)
        press_count_var = tk.IntVar(value=config.get('press_count', 1) if config else 1)
        press_count_spin = ttk.Spinbox(frame, from_=1, to=50, textvariable=press_count_var, width=33)
        press_count_spin.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # ช่วงเวลาระหว่างการกด (สำหรับ multi_press)
        ttk.Label(frame, text="ช่วงเวลาระหว่างการกด (วินาที):").grid(row=5, column=0, sticky=tk.W, pady=5)
        press_delay_var = tk.DoubleVar(value=config.get('press_delay', 0.05) if config else 0.05)
        press_delay_spin = ttk.Spinbox(frame, from_=0.01, to=5.0, increment=0.01, 
                                     textvariable=press_delay_var, width=33)
        press_delay_spin.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # ช่วงเวลาการกดซ้ำ (สำหรับ auto_repeat)
        ttk.Label(frame, text="ช่วงเวลาการกดซ้ำ (วินาที):").grid(row=6, column=0, sticky=tk.W, pady=5)
        repeat_interval_var = tk.DoubleVar(value=config.get('repeat_interval', 0.1) if config else 0.1)
        repeat_interval_spin = ttk.Spinbox(frame, from_=0.01, to=10.0, increment=0.01, 
                                         textvariable=repeat_interval_var, width=33)
        repeat_interval_spin.grid(row=6, column=1, sticky=tk.W, pady=5)
        
        # คำอธิบายการทำงาน
        info_frame = ttk.LabelFrame(frame, text="คำอธิบายการทำงาน", padding="10")
        info_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)
        
        def update_info(*args):
            action_type = action_var.get()
            if action_type == 'remap':
                info_text = "รีแมปปุ่ม: กดปุ่มต้นทาง = กดปุ่มเป้าหมาย 1 ครั้ง\nเช่น กด 'a' = กด 'b'"
            elif action_type == 'hold_toggle':
                info_text = """กดค้างแบบสลับ: กดครั้งแรกเริ่มกดค้าง กดอีกครั้งหยุดกดค้าง
เช่น กด 'q' เพื่อเริ่ม/หยุดกดค้าง 'shift'
⚡ สามารถใช้ปุ่มเดียวกันได้: เช่น กด 'shift' เพื่อเริ่ม/หยุดกดค้าง 'shift'"""
            elif action_type == 'multi_press':
                info_text = "กดหลายครั้ง: กดปุ่มต้นทาง 1 ครั้ง = กดปุ่มเป้าหมายหลายครั้ง\nเช่น กด 'z' = กด 'space' 5 ครั้ง"
            elif action_type == 'auto_repeat':
                info_text = "กดซ้ำอัตโนมัติ: กดเพื่อเริ่ม/หยุดการกดซ้ำอัตโนมัติ\nเช่น กด 'r' เพื่อเริ่ม/หยุดกดซ้ำ 'e' ทุก 0.1 วินาที"
            
            info_label.config(text=info_text)
        
        action_var.trace('w', update_info)
        
        info_label = ttk.Label(info_frame, text="", justify=tk.LEFT, wraplength=540)
        info_label.pack(anchor=tk.W)
        update_info()  # แสดงข้อมูลเริ่มต้น
        
        # ตัวอย่างปุ่ม
        example_frame = ttk.LabelFrame(frame, text="ตัวอย่างปุ่ม", padding="10")
        example_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        example_text = """ปุ่มทั่วไป: a, b, c, 1, 2, 3
ปุ่มพิเศษ: space, enter, shift, ctrl, alt, tab, esc
ปุ่มฟังก์ชัน: f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12
ปุ่มลูกศร: up, down, left, right
เมาส์: left_click, right_click, middle_click"""
        
        ttk.Label(example_frame, text=example_text, justify=tk.LEFT).pack(anchor=tk.W)
        
        # คำเตือนสำหรับการใช้ปุ่มเดียวกัน
        warning_frame = ttk.LabelFrame(frame, text="คำแนะนำ", padding="10")
        warning_frame.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        warning_text = """⚡ การใช้ปุ่มเดียวกัน: เหมาะสำหรับ Hold Toggle และ Auto Repeat
   เช่น กด Shift เพื่อเริ่มกดค้าง Shift และกดอีกครั้งเพื่อหยุด
   
⚠️  หลีกเลี่ยงการใช้ปุ่มเดียวกันกับ Key Remap เพราะจะเกิดการวนซ้ำ"""
        
        warning_label = ttk.Label(warning_frame, text=warning_text, justify=tk.LEFT, foreground="blue")
        warning_label.pack(anchor=tk.W)
        
        # ปุ่ม
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=10, column=0, columnspan=3, pady=20)
        
        def save_config():
            name = name_var.get().strip()
            source = source_var.get().strip()
            action = action_var.get()
            target = target_var.get().strip()
            press_count = press_count_var.get()
            press_delay = press_delay_var.get()
            repeat_interval = repeat_interval_var.get()
            
            if not all([name, source, target]):
                messagebox.showerror("ข้อผิดพลาด", "กรุณากรอกข้อมูลให้ครบถ้วน")
                return
            
            # เตือนเมื่อใช้ปุ่มเดียวกันกับ remap
            if action == 'remap' and source.lower() == target.lower():
                if not messagebox.askyesno("คำเตือน", 
                    "การใช้ปุ่มเดียวกันกับ Key Remap อาจทำให้เกิดการวนซ้ำ\nต้องการดำเนินการต่อหรือไม่?"):
                    return
            
            new_config = {
                'id': config.get('id') if config else len(self.key_configs) + 1,
                'name': name,
                'source_key': source.lower(),
                'action_type': action,
                'target_key': target.lower(),
                'press_count': press_count,
                'press_delay': press_delay,
                'repeat_interval': repeat_interval,
                'enabled': config.get('enabled', True) if config else True
            }
            
            if index is not None:
                self.key_configs[index] = new_config
            else:
                self.key_configs.append(new_config)
            
            self.refresh_tree()
            dialog.destroy()
        
        ttk.Button(button_frame, text="บันทึก", command=save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="ยกเลิก", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Focus on name entry
        name_entry.focus()
    
    def refresh_tree(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add configs
        for i, config in enumerate(self.key_configs):
            status = "เปิดใช้งาน" if config.get('enabled', True) else "ปิดใช้งาน"
            
            action_type = config['action_type']
            if action_type == 'remap':
                action_desc = "รีแมปปุ่ม"
                param_desc = "ทันที"
            elif action_type == 'hold_toggle':
                action_desc = "กดค้างสลับ"
                param_desc = "สลับเปิด/ปิด"
            elif action_type == 'multi_press':
                action_desc = "กดหลายครั้ง"
                param_desc = f"{config.get('press_count', 1)} ครั้ง (ห่าง {config.get('press_delay', 0.05)} วิ)"
            elif action_type == 'auto_repeat':
                action_desc = "กดซ้ำอัตโนมัติ"
                param_desc = f"ทุก {config.get('repeat_interval', 0.1)} วินาที"
            else:
                action_desc = action_type
                param_desc = "-"
            
            self.tree.insert('', 'end', iid=str(i+1),
                           values=(config['name'], 
                                  config['source_key'],
                                  action_desc,
                                  config['target_key'],
                                  param_desc,
                                  status))
    
    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.key_configs, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("สำเร็จ", "บันทึกการตั้งค่าเรียบร้อย")
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถบันทึกไฟล์ได้: {str(e)}")
    
    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.key_configs = json.load(f)
                self.refresh_tree()
                messagebox.showinfo("สำเร็จ", "โหลดการตั้งค่าเรียบร้อย")
            else:
                self.key_configs = []
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถโหลดไฟล์ได้: {str(e)}")
            self.key_configs = []
    
    def start_listener(self):
        def on_press(key):
            if not self.enabled:
                return

            # อัปเดตเวลาการใช้งาน
            self.last_activity_time = time.time()

            # ป้องกันการเรียกซ้ำ
            if hasattr(self, '_processing_key') and self._processing_key:
                return

            try:
                key_char = key.char.lower() if hasattr(key, 'char') and key.char else str(key).replace('Key.', '')
            except:
                key_char = str(key).replace('Key.', '')

            # ใส่ action ลง queue
            self.action_queue.put(('key_press', key_char))

        self.listener = KeyboardListener(on_press=on_press, suppress=False)
        self.listener.start()
    
    def process_actions(self):
        while True:
            try:
                action_type, key_char = self.action_queue.get(timeout=1)
                if action_type == 'key_press':
                    self.handle_key_press(key_char)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing action: {e}")
    
    def handle_key_press(self, key_char):
        self._processing_key = True
        
        try:
            for config in self.key_configs:
                if not config.get('enabled', True):
                    continue
                    
                if config['source_key'] == key_char:
                    action_type = config['action_type']
                    
                    # สำหรับการใช้ปุ่มเดียวกัน ต้องตรวจสอบสถานะก่อน
                    if config['source_key'] == config['target_key']:
                        if action_type in ['hold_toggle', 'auto_repeat']:
                            # ปุ่มเดียวกันใช้ได้กับ hold_toggle และ auto_repeat
                            pass
                        elif action_type == 'remap':
                            # หลีกเลี่ยงการวนซ้ำของ remap
                            continue
                    
                    if action_type == 'remap':
                        self.handle_remap(config)
                    elif action_type == 'hold_toggle':
                        self.handle_hold_toggle(config)
                    elif action_type == 'multi_press':
                        self.handle_multi_press(config)
                    elif action_type == 'auto_repeat':
                        self.handle_auto_repeat(config)
        finally:
            time.sleep(0.01)  # หน่วงเล็กน้อยเพื่อป้องกันการเรียกซ้ำ
            self._processing_key = False
    
    def handle_remap(self, config):
        """รีแมปปุ่ม: กด A = กด B"""
        self.is_remapping_active = True
        target_key = config['target_key']
        self.press_key(target_key)
        self.is_remapping_active = False
        print(f"รีแมป: {config['source_key']} → {target_key}")
    
    def handle_hold_toggle(self, config):
        """กดค้างแบบสลับ"""
        config_id = config['id']
        target_key = config['target_key']

        if config_id not in self.active_holds:
            self.active_holds[config_id] = {'holding': False}

        if self.active_holds[config_id]['holding']:
            self.stop_hold(config_id)
            print(f"หยุดกดค้าง: {target_key}")
        else:
            # ดีเลย์ 0.5 วินาทีก่อนเริ่มกดค้าง
            def delayed_start():
                time.sleep(0.1)
                if self.enabled and config_id in self.active_holds and not self.active_holds[config_id]['holding']:
                    self.start_hold(config)
                    print(f"เริ่มกดค้าง: {target_key}")

            thread = threading.Thread(target=delayed_start, daemon=True)
            thread.start()
            print(f"กำลังเริ่มกดค้างใน 0.1 วินาที: {target_key}")
    
    def handle_multi_press(self, config):
        """กดหลายครั้ง"""
        target_key = config['target_key']
        press_count = config.get('press_count', 1)
        press_delay = config.get('press_delay', 0.05)

        def press_multiple():
            self.is_remapping_active = True
            try:
                for i in range(press_count):
                    if not self.enabled:
                        break
                    self.press_key(target_key)
                    if i < press_count - 1:  # ไม่หน่วงหลังการกดครั้งสุดท้าย
                        time.sleep(press_delay)
            finally:
                self.is_remapping_active = False

        thread = threading.Thread(target=press_multiple, daemon=True)
        thread.start()
        print(f"กดหลายครั้ง: {target_key} จำนวน {press_count} ครั้ง")
    
    def handle_auto_repeat(self, config):
        """กดซ้ำอัตโนมัติ"""
        config_id = config['id']
        
        if config_id not in self.active_repeats:
            self.active_repeats[config_id] = {'repeating': False, 'thread': None}
        
        if self.active_repeats[config_id]['repeating']:
            self.stop_repeat(config_id)
            print(f"หยุดกดซ้ำ: {config['target_key']}")
        else:
            self.start_repeat(config)
            print(f"เริ่มกดซ้ำ: {config['target_key']} ทุก {config.get('repeat_interval', 0.1)} วินาที")
    
    def start_hold(self, config):
        config_id = config['id']
        target_key = config['target_key']
        
        self.press_key_down(target_key)
        self.active_holds[config_id]['holding'] = True
    
    def stop_hold(self, config_id):
        if config_id in self.active_holds and self.active_holds[config_id]['holding']:
            # หาปุ่มเป้าหมายจาก config
            target_key = None
            for config in self.key_configs:
                if config['id'] == config_id:
                    target_key = config['target_key']
                    break
            
            if target_key:
                self.press_key_up(target_key)
                self.active_holds[config_id]['holding'] = False
    
    def start_repeat(self, config):
        config_id = config['id']
        target_key = config['target_key']
        repeat_interval = config.get('repeat_interval', 0.1)
        
        def repeat_task():
            self.active_repeats[config_id]['repeating'] = True
            while self.active_repeats[config_id]['repeating'] and self.enabled:
                self.press_key(target_key)
                time.sleep(repeat_interval)
        
        thread = threading.Thread(target=repeat_task, daemon=True)
        self.active_repeats[config_id]['thread'] = thread
        thread.start()
    
    def stop_repeat(self, config_id):
        if config_id in self.active_repeats:
            self.active_repeats[config_id]['repeating'] = False
    
    def press_key(self, key):
        """กดปุ่ม (กดแล้วปล่อย)"""
        try:
            if key in ['left_click', 'right_click', 'middle_click']:
                if key == 'left_click':
                    self.mouse_controller.click(Button.left)
                elif key == 'right_click':
                    self.mouse_controller.click(Button.right)
                elif key == 'middle_click':
                    self.mouse_controller.click(Button.middle)
            elif key in ['scroll_up', 'scroll_down']:
                if key == 'scroll_up':
                    self.mouse_controller.scroll(0, 1)
                elif key == 'scroll_down':
                    self.mouse_controller.scroll(0, -1)
            else:
                key_obj = self.get_key_object(key)
                if key_obj:
                    self.keyboard_controller.press(key_obj)
                    self.keyboard_controller.release(key_obj)
        except Exception as e:
            print(f"Error pressing key {key}: {e}")
    
    def press_key_down(self, key):
        """กดปุ่มค้าง (กดไม่ปล่อย)"""
        try:
            if key in ['left_click', 'right_click', 'middle_click']:
                if key == 'left_click':
                    self.mouse_controller.press(Button.left)
                elif key == 'right_click':
                    self.mouse_controller.press(Button.right)
                elif key == 'middle_click':
                    self.mouse_controller.press(Button.middle)
            else:
                key_obj = self.get_key_object(key)
                if key_obj:
                    self.keyboard_controller.press(key_obj)
        except Exception as e:
            print(f"Error pressing key down {key}: {e}")
    
    def press_key_up(self, key):
        """ปล่อยปุ่ม"""
        try:
            if key in ['left_click', 'right_click', 'middle_click']:
                if key == 'left_click':
                    self.mouse_controller.release(Button.left)
                elif key == 'right_click':
                    self.mouse_controller.release(Button.right)
                elif key == 'middle_click':
                    self.mouse_controller.release(Button.middle)
            else:
                key_obj = self.get_key_object(key)
                if key_obj:
                    self.keyboard_controller.release(key_obj)
        except Exception as e:
            print(f"Error releasing key {key}: {e}")
    
    def get_key_object(self, key_str):
        """แปลงชื่อปุ่มเป็น object ของ pynput"""
        key_mapping = {
            'space': Key.space,
            'enter': Key.enter,
            'tab': Key.tab,
            'esc': Key.esc,
            'escape': Key.esc,
            'shift': Key.shift,
            'ctrl': Key.ctrl,
            'alt': Key.alt,
            'cmd': Key.cmd,
            'backspace': Key.backspace,
            'delete': Key.delete,
            'up': Key.up,
            'down': Key.down,
            'left': Key.left,
            'right': Key.right,
            'home': Key.home,
            'end': Key.end,
            'page_up': Key.page_up,
            'page_down': Key.page_down,
            'insert': Key.insert,
            'caps_lock': Key.caps_lock,
            'num_lock': Key.num_lock,
            'scroll_lock': Key.scroll_lock,
            'print_screen': Key.print_screen,
            'pause': Key.pause,
            'menu': Key.menu,
            'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4,
            'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7, 'f8': Key.f8,
            'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12
        }
        
        if key_str in key_mapping:
            return key_mapping[key_str]
        elif len(key_str) == 1:
            return key_str
        else:
            return None
    
    def on_closing(self):
        """ปิดแอปพลิเคชัน"""
        # หยุดการทำงานทั้งหมด
        self.enabled = False
        self.stop_all_activities()
        
        # หยุด listener
        if self.listener:
            self.listener.stop()
        
        # ปิดหน้าต่าง overlay
        if hasattr(self, 'ready_overlay') and self.ready_overlay:
            self.ready_overlay.destroy()
        
        # ปิดแอป
        self.root.destroy()
    
    def run(self):
        """เริ่มต้นแอปพลิเคชัน"""
        self.root.mainloop()
    
    def create_ready_overlay(self):
        """สร้างหน้าต่าง overlay สำหรับข้อความพร้อมใช้งาน"""
        self.ready_overlay = tk.Toplevel(self.root)
        self.ready_overlay.overrideredirect(True)  # เอา border ออก
        self.ready_overlay.attributes("-topmost", True)  # อยู่บนสุดเสมอ
        self.ready_overlay.attributes("-alpha", 0.85)  # ความโปร่งใสเล็กน้อย
        
        # สร้าง label แสดงข้อความ
        self.ready_label = ttk.Label(self.ready_overlay, text="○ พร้อมใช้งาน", 
                                     font=("Arial", 12, "bold"), foreground="green",
                                     background="white")
        self.ready_label.pack(ipadx=10, ipady=5)
        
        # ตั้งตำแหน่งที่มุมบนขวาของหน้าจอ
        self.position_ready_overlay()
        
        # อัปเดตตำแหน่งเมื่อหน้าต่างหลักเคลื่อนที่หรือเปลี่ยนขนาด
        self.root.bind("<Configure>", lambda e: self.position_ready_overlay())
    
    def position_ready_overlay(self):
        """ตั้งตำแหน่ง overlay ที่มุมบนขวาของหน้าจอ"""
        self.ready_overlay.update_idletasks()
        screen_width = self.ready_overlay.winfo_screenwidth()
        x = screen_width - self.ready_overlay.winfo_width() - 10  # เว้นระยะ 10 px จากขอบขวา
        y = 10  # เว้นระยะ 10 px จากขอบบน
        self.ready_overlay.geometry(f"+{x}+{y}")
    
    def update_ready_overlay(self, text, color):
        """อัปเดตข้อความและสีของ overlay"""
        if hasattr(self, 'ready_label') and self.ready_label:
            self.ready_label.config(text=text, foreground=color)

# ฟังก์ชันสำหรับสร้างไฟล์ตัวอย่าง
def create_sample_config():
    sample_configs = [
        {
            "id": 1,
            "name": "รีแมป A เป็น B",
            "source_key": "a",
            "action_type": "remap",
            "target_key": "b",
            "press_count": 1,
            "press_delay": 0.05,
            "repeat_interval": 0.1,
            "enabled": True
        },
        {
            "id": 2,
            "name": "กดค้าง Shift ด้วย Shift (ปุ่มเดียวกัน)",
            "source_key": "shift",
            "action_type": "hold_toggle",
            "target_key": "shift",
            "press_count": 1,
            "press_delay": 0.05,
            "repeat_interval": 0.1,
            "enabled": True
        },
        {
            "id": 3,
            "name": "กด Space 5 ครั้งด้วย Z",
            "source_key": "z",
            "action_type": "multi_press",
            "target_key": "space",
            "press_count": 5,
            "press_delay": 0.1,
            "repeat_interval": 0.1,
            "enabled": True
        },
        {
            "id": 4,
            "name": "กดซ้ำ E อัตโนมัติด้วย E (ปุ่มเดียวกัน)",
            "source_key": "e",
            "action_type": "auto_repeat",
            "target_key": "e",
            "press_count": 1,
            "press_delay": 0.05,
            "repeat_interval": 0.1,
            "enabled": True
        },
        {
            "id": 5,
            "name": "กดค้าง Ctrl ด้วย Q",
            "source_key": "q",
            "action_type": "hold_toggle",
            "target_key": "ctrl",
            "press_count": 1,
            "press_delay": 0.05,
            "repeat_interval": 0.1,
            "enabled": True
        }
    ]
    
    with open("sample_configs.json", 'w', encoding='utf-8') as f:
        json.dump(sample_configs, f, ensure_ascii=False, indent=2)
    
    print("สร้างไฟล์ตัวอย่าง sample_configs.json เรียบร้อย")

if __name__ == "__main__":
    # ตรวจสอบและติดตั้ง dependencies
    try:
        import pynput
    except ImportError:
        print("กรุณาติดตั้ง pynput ด้วยคำสั่ง: pip install pynput")
        print("หรือ: python -m pip install pynput")
        input("กด Enter เพื่อออก...")
        exit(1)
    
    # สร้างไฟล์ตัวอย่าง
    # if not os.path.exists("sample_configs.json"):
    #     create_sample_config()
    
    # เริ่มแอป
    print("เริ่มต้น Key Remapper & Simulator (Enhanced)...")
    print("คุณสมบัติใหม่:")
    print("- ข้อความแจ้งเตือนการใช้งานแบบเรียลไทม์")
    print("- รองรับการใช้ปุ่มเดียวกันสำหรับ Hold Toggle และ Auto Repeat")
    print("- แอปอยู่บนสุดเสมอ (สามารถเปิด/ปิดได้)")
    print("- ป้องกันการวนซ้ำอัตโนมัติ")
    print("หมายเหตุ: แอปจะทำงานในพื้นหลัง หากต้องการปิด ให้ปิดหน้าต่าง GUI")
    
    app = KeyRemapperApp()
    app.run()