import sys
import time
import random
import queue
import threading
import tkinter as tk
import os
import math

try:
    import pygame
except ImportError:
    print("\n[!] Pygame library is missing. Run: pip install pygame\n")
    sys.exit(1)


TITLE = "jealous ni ikee"
WIDTH, HEIGHT = 950, 480  


BG_MAIN = "#000411"      
BG_CARD = "#000822"     
TXT_WHITE = "#00FFFF"   
TXT_MUTED = "#002266"   
ACCENT = "#0055ff"       
AUDIO_FILE = "C:/Users/HP/jealous1.mp3"

LYRICS_MATRIX = [
   
    (0.0, "I turn my cheer music up, and I'm puffing my chest", 0.10),
    (4.5, "I'm gettin' red in the face, you can call me obsessed", 0.09),
    (9.0, "It's not your fault that they hover, I mean no disrespect", 0.09),  
    (13.5, "It's my right to be hellish, I still get jealous", 0.09),
    
    
    (18.5, "Cause you're too sexy beautiful and everybody wants a taste", 0.09),
    (22.8, "That's why (that's why) I still get jealous", 0.10),
    
    
    (27.5, "You're too sexy beautiful and everybody wants a taste", 0.09),
    (31.2, "That's why (that's why) I still get jealous", 0.10),
]

class TimingEngine(threading.Thread):
    def __init__(self, msg_queue, audio_active, time_offset_ref):
        super().__init__(daemon=True)
        self.queue = msg_queue
        self.audio_active = audio_active
        self.time_offset_ref = time_offset_ref  
        self.is_running = True

    def run(self):
        while self.audio_active and not pygame.mixer.music.get_busy() and self.is_running:
            time.sleep(0.01)
            
        start_time = time.time()
        
        for schedule, sentence, char_speed in LYRICS_MATRIX:
            if not self.is_running:
                break
            
            while self.is_running:
                current_offset = self.time_offset_ref["offset"]
                
                if self.audio_active and pygame.mixer.music.get_busy():
                    current_elapsed = (pygame.mixer.music.get_pos() / 1000.0) + current_offset
                else:
                    current_elapsed = (time.time() - start_time) + current_offset
                    
                if current_elapsed >= schedule:
                    break
                time.sleep(0.002) 

            if not self.is_running:
                break

            running_text = ""
            for char in sentence:
                if not self.is_running:
                    break
                running_text += char
                self.queue.put(("UPDATE_TEXT", running_text))
                time.sleep(char_speed)
                
            time.sleep(0.4) 


class LyricsApp:
    def __init__(self, window):
        self.window = window
        self.ui_queue = queue.Queue()
        self.bioparticles = []
        self.cat_pixel_blocks = []
        self.cat_frame_toggle = 0
        self.audio_active = False
        self.time_tracker = {"offset": 0.0}
        
        if os.path.exists(AUDIO_FILE):
            try:
                pygame.mixer.pre_init(44100, -16, 2, 512)
                pygame.mixer.init()
                pygame.mixer.music.load(AUDIO_FILE)
                pygame.mixer.music.set_volume(1.0)
                pygame.mixer.music.play()
                self.audio_active = True
            except Exception as e:
                print(f"Audio interface error: {e}")
        else:
            print(f"\n[Warning] File missing at: {AUDIO_FILE}. Running silent mode.\n")
        
        self.window.title(TITLE)
        self.window.configure(bg=BG_MAIN)
        scr_w, scr_h = self.window.winfo_screenwidth(), self.window.winfo_screenheight()
        self.window.geometry(f"{WIDTH}x{HEIGHT}+{int((scr_w-WIDTH)/2)}+{int((scr_h-HEIGHT)/2)}")
        self.window.resizable(False, False)
        
        # Sleek Luminous Blue Borders
        border_outer = tk.Frame(self.window, bg="#001144", padx=2, pady=2)
        border_outer.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        border_inner = tk.Frame(border_outer, bg="#0033aa", padx=2, pady=2)
        border_inner.pack(fill=tk.BOTH, expand=True)
        
        card_panel = tk.Frame(border_inner, bg=BG_CARD)
        card_panel.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(card_panel, bg=BG_CARD, highlightthickness=0, bd=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Note: Background grid generator removed to keep the view space completely clean.
        
        self.label_lyrics = tk.Label(
            card_panel, text="", bg=BG_CARD, fg=TXT_WHITE,
            font=("Courier New", 26, "bold"), wraplength=WIDTH-250, justify=tk.CENTER
        )
        self.label_lyrics.place(relx=0.45, rely=0.50, anchor=tk.CENTER)
        
        self.window.bind("<Left>", self.shift_time_backward)
        self.window.bind("<Right>", self.shift_time_forward)
        
        self.engine = TimingEngine(self.ui_queue, self.audio_active, self.time_tracker)
        self.engine.start()
        
        self.window.protocol("WM_DELETE_WINDOW", self.safely_exit)
        self.window.after(30, self.check_queue_messages)
        
     
        self.init_realistic_bioparticles()
        self.render_bioparticle_physics()
        self.render_sad_cat()

    def shift_time_backward(self, event):
        self.time_tracker["offset"] += 0.1
        self.update_status_readout("Micro-Adjusted: +0.1s Earlier")

    def shift_time_forward(self, event):
        self.time_tracker["offset"] -= 0.1
        self.update_status_readout("Micro-Adjusted: -0.1s Later")

    def update_status_readout(self, alert_msg):
        current_offset = self.time_tracker["offset"]
        print(f"[Sync Adjustment] {alert_msg} (Total Bias: {current_offset:+.1f}s)")

    def check_queue_messages(self):
        try:
            while True:
                msg_type, data = self.ui_queue.get_nowait()
                if msg_type == "UPDATE_TEXT":
                    self.label_lyrics.config(text=data)
                    # Trigger physical wave surge in floating particles upon lyric state changes
                    for p in self.bioparticles:
                        p["speed_y"] -= random.uniform(0.5, 1.2)
                        p["glow_phase"] = random.uniform(0, math.pi)
                self.ui_queue.task_done()
        except queue.Empty:
            pass
        self.window.after(20, self.check_queue_messages)

   
    def init_realistic_bioparticles(self):
        for _ in range(50):
            x = random.uniform(0, WIDTH - 180)
            y = random.uniform(0, HEIGHT)
            speed_y = random.uniform(-0.3, -0.8)   # Natural upward drift buoyancy
            speed_x = random.uniform(-0.2, 0.2)    # Fluid cross-drift sway
            size = random.choice([2, 3, 4])
            glow_phase = random.uniform(0, 2 * math.pi)
            
            # Shifting oceanic bioluminescent spectrum palettes
            base_color = random.choice(["#00ffff", "#00bfff", "#3388ff", "#00f5ff"])
            
            pt_id = self.canvas.create_rectangle(x, y, x + size, y + size, fill=base_color, outline="")
            self.bioparticles.append({
                "id": pt_id, "x": x, "y": y, 
                "speed_x": speed_x, "speed_y": speed_y, 
                "size": size, "glow_phase": glow_phase, "base_color": base_color
            })

    def render_bioparticle_physics(self):
        for f in self.bioparticles:
         
            f["glow_phase"] += 0.04
            fluid_sway = math.sin(f["glow_phase"]) * 0.25
            
            f["x"] += f["speed_x"] + fluid_sway
            f["y"] += f["speed_y"]
            
           
            if f["speed_y"] < -1.0:
                f["speed_y"] *= 0.96

            # Wrap coordinates around container floor smoothly
            if f["y"] < -10:
                f["y"] = HEIGHT + 10
                f["x"] = random.uniform(0, WIDTH - 180)
            if f["x"] < -10 or f["x"] > WIDTH:
                f["x"] = random.uniform(0, WIDTH - 180)
                
           
            intensity = (math.sin(f["glow_phase"]) + 1) / 2.0
            if intensity < 0.25:
                curr_color = "#000a26"  
            elif intensity < 0.6:
                curr_color = "#0033aa"  
            else:
                curr_color = f["base_color"] 
                
            self.canvas.coords(f["id"], f["x"], f["y"], f["x"] + f["size"], f["y"] + f["size"])
            self.canvas.itemconfig(f["id"], fill=curr_color)
            
        self.window.after(25, self.render_bioparticle_physics)

    
    def render_sad_cat(self):
        """Draws a high-fidelity 64x64 detailed pixel art layout of a sad cat"""
        for item in self.cat_pixel_blocks:
            self.canvas.delete(item)
        self.cat_pixel_blocks.clear()

        
        start_x, start_y = WIDTH - 160, HEIGHT - 150
        pixel_size = 2  

        self.cat_frame_toggle = (self.cat_frame_toggle + 1) % 40
        breathing_offset = 1 if self.cat_frame_toggle > 20 else 0
        is_blinking = 36 <= self.cat_frame_toggle <= 39

        
        C_BODY = "#1e3a8a"  
        C_EAR  = "#172554"  
        C_EYE  = "#00FFFF"  
        C_TEAR = "#38bdf8"  

        
        cat_grid = [
            [0]*64, [0]*64, [0]*64, [0]*64, [0]*64, [0]*64, [0]*64, [0]*64,
            [0]*16 + [1]*6  + [0]*20 + [1]*6  + [0]*16,
            [0]*15 + [1]*2  + [2]*4  + [1]*2  + [0]*16 + [1]*2  + [2]*4  + [1]*2  + [0]*15,
            [0]*14 + [1]*2  + [2]*6  + [1]*2  + [0]*14 + [1]*2  + [2]*6  + [1]*2  + [0]*14,
            [0]*13 + [1]*2  + [2]*8  + [1]*2  + [0]*12 + [1]*2  + [2]*8  + [1]*2  + [0]*13,
            [0]*12 + [1]*2  + [2]*10 + [1]*2  + [0]*10 + [1]*2  + [2]*10 + [1]*2  + [0]*12,
            [0]*11 + [1]*2  + [1]*12 + [1]*2  + [0]*8  + [1]*2  + [1]*12 + [1]*2  + [0]*11,
            [0]*10 + [1]*2  + [1]*14 + [1]*1  + [0]*8  + [1]*1  + [1]*14 + [1]*2  + [0]*10,
            [0]*9  + [1]*2  + [1]*16 + [1]*1  + [0]*6  + [1]*1  + [1]*16 + [1]*2  + [0]*9,
            [0]*8  + [1]*2  + [1]*18 + [1]*27 + [1]*18 + [1]*2  + [0]*8,
            [0]*7  + [1]*2  + [1]*48 + [1]*2  + [0]*7,
            [0]*6  + [1]*2  + [1]*12 + [3]*2  + [1]*22 + [3]*2  + [1]*12 + [1]*2  + [0]*6,
            [0]*6  + [1]*2  + [1]*10 + [3]*4  + [1]*22 + [3]*4  + [1]*10 + [1]*2  + [0]*6,
            [0]*6  + [1]*2  + [1]*8  + [3]*2  + [4]*4  + [3]*2  + [1]*18 + [3]*2  + [4]*4  + [3]*2  + [1]*8 + [1]*2 + [0]*6,
            [0]*6  + [1]*2  + [1]*8  + [3]*2  + [0]*4  + [3]*2  + [1]*18 + [3]*2  + [0]*4  + [3]*2  + [1]*8 + [1]*2 + [0]*6,
            [0]*7  + [1]*2  + [1]*6  + [1]*4  + [0]*2  + [1]*2  + [1]*18 + [1]*2  + [0]*2  + [1]*4  + [1]*6 + [1]*2 + [0]*7,
            [0]*8  + [1]*2  + [1]*4  + [1]*4  + [0]*2  + [1]*2  + [1]*18 + [1]*2  + [0]*2  + [1]*4  + [1]*4 + [1]*2 + [0]*8,
            [0]*9  + [1]*2  + [1]*2  + [1]*4  + [0]*2  + [1]*32 + [1]*2  + [1]*4  + [1]*2  + [1]*2 + [0]*9,
            [0]*10 + [1]*44 + [0]*10,
            [0]*11 + [1]*42 + [0]*11,
            [0]*12 + [1]*40 + [0]*12,
            [0]*13 + [1]*38 + [0]*13,
            [0]*14 + [1]*12 + [0]*12 + [1]*12 + [0]*14,
            [0]*15 + [1]*10 + [0]*14 + [1]*10 + [0]*15,
            [0]*16 + [1]*8  + [0]*16 + [1]*8  + [0]*16,
            [0]*17 + [1]*6  + [0]*18 + [1]*6  + [0]*17,
            [0]*18 + [1]*4  + [0]*20 + [1]*4  + [0]*18,
            [0]*19 + [1]*2  + [0]*22 + [1]*2  + [0]*19,
            [0]*64, [0]*64, [0]*64, [0]*64, [0]*64, [0]*64
        ]

        for r_idx, row in enumerate(cat_grid):
            for c_idx, val in enumerate(row):
                if val == 0:
                    continue

                curr_y = start_y + (r_idx * pixel_size)
                curr_x = start_x + (c_idx * pixel_size)

                
                if r_idx < 22:
                    curr_y += breathing_offset

                color = C_BODY
                if val == 2:
                    color = C_EAR
                elif val == 3:
                    color = BG_CARD if is_blinking else C_EYE
                elif val == 4:
                    color = C_TEAR if not is_blinking else C_BODY
                    curr_y += (self.cat_frame_toggle % 6)  # Fluid linear tear slider offset execution

                p_id = self.canvas.create_rectangle(
                    curr_x, curr_y, curr_x + pixel_size, curr_y + pixel_size,
                    fill=color, outline=""
                )
                self.cat_pixel_blocks.append(p_id)

        self.window.after(100, self.render_sad_cat)

    def safely_exit(self):
        self.engine.is_running = False
        try:
            if self.audio_active:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except Exception:
            pass
        self.window.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = LyricsApp(root)
    root.mainloop()