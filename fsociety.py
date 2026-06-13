"""
FSOCIETY PRANK — theatrical simulation, inspired by Mr. Robot
EXIT: CTRL+SHIFT+Q or wait 90 sec. Nothing is damaged.
"""
import tkinter as tk
import random
import threading
import time
import winsound

# ── colours ────────────────────────────────────────────────────────────────
BG     = "#000000"
GREEN  = "#00FF41"
MGREEN = "#00BB30"
DGREEN = "#003B00"
RED    = "#FF0000"
DRED   = "#880000"
WHITE  = "#FFFFFF"
GREY   = "#1A1A1A"
CYAN   = "#00FFFF"

GLITCH = "!@#$%^&*<>[]{}|\\/?~`ΩЖЦЧЩабвгдёжзий▓▒░█▄▀01"

# ── ASCII art ──────────────────────────────────────────────────────────────

# Large Unicode-block skull for the lockscreen
SKULL_BIG = """\
  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
 ░░██████████████████████████████████░░
░░████░░░░░░░░░░░░░░░░░░░░░░░░░░░░████░░
░░███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░███░░
░░███░░░░██████░░░░░░░░░██████░░░░░███░░
░░███░░░░██████░░░░░░░░░██████░░░░░███░░
░░███░░░░██████░░░░░░░░░██████░░░░░███░░
░░███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░███░░
░░███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░███░░
░░███░░░░░░██████████████░░░░░░░░░███░░
░░███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░███░░
░░████░░░░░░░░░░░░░░░░░░░░░░░░░░████░░
 ░░████████████████████████████████░░
   ░░████░░░░░░████████░░░░░░████░░
   ░░███████████████████████████░░
    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░"""

# Petya ransomware-style skull for popups
SKULL_PETYA = """\
  uu$$$$$$$$$$uu
 u$$$$$$$$$$$$$$u
u$$$$$$$$$$$$$$$$u
u$$$$"  "$$$"  "$$u
 "$$"    u$u    "$$"
  $$u    u$u    u$$
  $$u   u$$$u   u$$
  "$$$$uu$$ $$uu$$$$"
   "$$$$$" "$$$$$"
    u$$$$$$$$$u
    u$"$"$"$"$u
uuu $$u$ $ $u$$ uuu
u$$  $$$$$$$$$  $$u
 $$$$  $$$$$  $$$$
  "$$$$$$$$$$$$$"
    "$$$$$$$$$" """

# Compact skull for small popups
SKULL_MINI = """\
  ,--./,-.
 / #      \\
|          |
 \\  ~~~~  /
  `._,._,'
   |||||
   |||||"""

FSOCIETY_LOGO = """\
 ███████╗███████╗ ██████╗  ██████╗██╗███████╗████████╗██╗   ██╗
 ██╔════╝██╔════╝██╔═══██╗██╔════╝██║██╔════╝╚══██╔══╝╚██╗ ██╔╝
 █████╗  ███████╗██║   ██║██║     ██║█████╗     ██║    ╚████╔╝
 ██╔══╝  ╚════██║██║   ██║██║     ██║██╔══╝     ██║     ╚██╔╝
 ██║     ███████║╚██████╔╝╚██████╗██║███████╗   ██║      ██║
 ╚═╝     ╚══════╝ ╚═════╝  ╚═════╝╚═╝╚══════╝   ╚═╝      ╚═╝  """

POPUP_MSGS = [
    "SYSTEM COMPROMISED",   "FIREWALL BYPASSED",
    "ROOT ACCESS GRANTED",  "KERNEL INJECTED",
    "WE ARE FSOCIETY",      "HELLO, FRIEND",
    "TRUST NO ONE",         "DELETING LOGS...",
    "DATA EXFIL: 78%",      "BACKDOOR INSTALLED",
    "COVERING TRACKS...",   "LSASS DUMPED",
    "C2 CHANNEL OPEN",      "MBR OVERWRITTEN",
    "YOU HAVE BEEN CHOSEN", "WE DO NOT FORGIVE",
]

STATUS_MSGS = [
    "Scanning network topology...",
    "Bypassing IDS signatures...",
    "Injecting shellcode into svchost.exe...",
    "Extracting NTLM hashes...",
    "Establishing reverse C2 tunnel...",
    "Corrupting MBR sectors 0-63...",
    "Pivoting through 10.0.0.0/8...",
    "Exfiltrating SAM database...",
    "Patching watchdog timer...",
    "Disabling Windows Defender real-time...",
    "Dumping LSASS process memory...",
    "Lateral movement via SMB relay...",
    "Deploying ransomware payload...",
    "Wiping event logs...",
]

# ── globals ────────────────────────────────────────────────────────────────
running     = True
popups      = []
plock       = threading.Lock()
flash_event = threading.Event()


def glitch(s: str, intensity: float = 0.07) -> str:
    return "".join(
        random.choice(GLITCH) if c not in (" ", "\n") and random.random() < intensity else c
        for c in s
    )


def _play_seq(seq):
    try:
        for freq, dur in seq:
            winsound.Beep(freq, dur)
    except Exception:
        pass


def beep():
    """Scary burst used on popup spawn."""
    patterns = [
        # descending alarm
        [(1200, 70), (950, 70), (700, 70), (450, 100)],
        # rapid high glitch
        [(1500, 35), (1650, 35), (1400, 35), (1700, 35), (1200, 60)],
        # low horror rumble + spike
        [(100, 180), (150, 120), (1800, 50), (100, 130)],
        # critical error sweep down
        [(900, 55), (800, 55), (700, 55), (600, 55), (500, 55), (400, 80)],
        # Windows "death" stutter
        [(200, 40), (200, 40), (200, 40), (150, 80), (100, 120)],
    ]
    threading.Thread(target=_play_seq, args=(random.choice(patterns),), daemon=True).start()


def flash_beep():
    """Scarier sound specifically for screen flashes."""
    flash_event.set()
    threading.Timer(0.15, flash_event.clear).start()
    patterns = [
        # industrial alarm: fast descending
        [(1800, 50), (1600, 50), (1400, 50), (1200, 50), (1000, 50), (800, 80)],
        # sub-bass boom + screech
        [(80, 250), (90, 200), (2000, 60), (1900, 60), (1800, 80)],
        # horror drone: rising pulse
        [(120, 100), (140, 80), (160, 80), (180, 80), (200, 80), (2000, 100)],
        # glitch burst: random spikes
        [(1700, 30), (200, 30), (1900, 30), (150, 30), (2000, 30), (100, 100)],
        # nuclear alarm
        [(960, 80), (960, 80), (960, 80), (720, 200), (960, 80), (960, 80), (720, 300)],
    ]
    threading.Thread(target=_play_seq, args=(random.choice(patterns),), daemon=True).start()


# ── popup window ───────────────────────────────────────────────────────────
def spawn_popup():
    if not running:
        return
    win = tk.Toplevel()
    win.overrideredirect(True)
    win.configure(bg=BG)
    win.attributes("-topmost", True)
    win.attributes("-alpha", 0.94)

    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    size = random.choice(["mini", "mid", "large"])
    if size == "mini":
        w, h, skull, sfont = 200, 190, SKULL_MINI,  ("Courier", 9)
    elif size == "mid":
        w, h, skull, sfont = 290, 250, SKULL_PETYA, ("Courier", 7)
    else:
        w, h, skull, sfont = 370, 300, SKULL_PETYA, ("Courier", 8)

    x = random.randint(0, max(0, sw - w))
    y = random.randint(0, max(0, sh - h))
    win.geometry(f"{w}x{h}+{x}+{y}")

    border_col = random.choice([RED, "#FF4400", "#CC0055", "#FF6600"])
    tk.Frame(win, bg=border_col).place(x=0, y=0, relwidth=1, relheight=1)
    inner = tk.Frame(win, bg=BG)
    inner.place(x=1, y=1, width=w-2, height=h-2)

    # fake title bar
    tbar = tk.Frame(inner, bg=DRED, height=18)
    tbar.pack(fill="x")
    tk.Label(tbar, text="■ FSOCIETY BREACH v3.1  [kernel32.dll hooked]",
             font=("Courier", 7, "bold"), bg=DRED, fg=WHITE).pack(side="left", padx=3)

    skull_lbl = tk.Label(inner, text=skull, font=sfont, bg=BG, fg=RED, justify="center")
    skull_lbl.pack(pady=(3, 0))

    msg = random.choice(POPUP_MSGS)
    tk.Label(inner, text=f"[!] {msg}", font=("Courier", 8, "bold"),
             bg=BG, fg=GREEN).pack()

    prog_var = tk.StringVar(value="[░░░░░░░░░░░░░░░░░░░░] 0%")
    tk.Label(inner, textvariable=prog_var, font=("Courier", 7),
             bg=BG, fg=DGREEN).pack()

    with plock:
        popups.append(win)

    def animate():
        pct = 0
        try:
            while running and pct <= 100:
                skull_lbl.config(text=glitch(skull, 0.06 + random.random() * 0.1))
                bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
                prog_var.set(f"[{bar}] {pct}%")
                pct += random.randint(1, 5)
                time.sleep(random.uniform(0.04, 0.14))
        except Exception:
            pass

    threading.Thread(target=animate, daemon=True).start()

    def shake():
        try:
            for _ in range(10):
                dx, dy = random.randint(-14, 14), random.randint(-14, 14)
                win.geometry(f"{w}x{h}+{x+dx}+{y+dy}")
                time.sleep(0.025)
            win.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

    def flash_shake_loop():
        """Shake in sync with every screen flash."""
        while running:
            fired = flash_event.wait(timeout=3)
            if not running:
                break
            if fired:
                try:
                    for _ in range(12):
                        dx = random.randint(-20, 20)
                        dy = random.randint(-20, 20)
                        win.geometry(f"{w}x{h}+{x+dx}+{y+dy}")
                        time.sleep(0.018)
                    win.geometry(f"{w}x{h}+{x}+{y}")
                except Exception:
                    break

    threading.Thread(target=shake, daemon=True).start()
    threading.Thread(target=flash_shake_loop, daemon=True).start()
    threading.Thread(target=beep, daemon=True).start()


def kill_popups():
    with plock:
        for w in popups:
            try: w.destroy()
            except Exception: pass
        popups.clear()


# ── lockscreen ─────────────────────────────────────────────────────────────
class Lockscreen:
    COUNTDOWN = 90

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FSOCIETY")
        self.root.configure(bg=BG)
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        # block escape routes
        for k in ("<Escape>", "<Alt-F4>"):
            self.root.bind(k, lambda e: None)
        self.root.bind("<Control-Shift-Q>", lambda e: self._exit())
        self.root.bind("<Control-Shift-q>", lambda e: self._exit())

        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()
        self._build()
        self._start()

    # ── UI ──────────────────────────────────────────────────────────────
    def _build(self):
        self.canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        self.canvas.place(x=0, y=0, width=self.sw, height=self.sh)

        # matrix rain columns
        cw = 14
        self.mat = []
        for i in range(self.sw // cw):
            x   = i * cw + cw // 2
            y   = random.randint(-self.sh, 0)
            spd = random.randint(4, 18)
            lng = random.randint(5, 22)
            col = []
            for j in range(lng):
                fill = GREEN if j == 0 else (MGREEN if j < 3 else DGREEN)
                item = self.canvas.create_text(
                    x, y + j * cw,
                    text=random.choice("01ABCDEF░▒▓"),
                    font=("Courier", 10, "bold"),
                    fill=fill, anchor="center"
                )
                col.append(item)
            self.mat.append({"x": x, "y": y, "spd": spd, "items": col, "lng": lng})

        # subtle scanlines
        for i in range(0, self.sh, 5):
            self.canvas.create_line(0, i, self.sw, i, fill="#001200", width=1)

        # centre frame
        frm = tk.Frame(self.root, bg=BG)
        frm.place(relx=0.5, rely=0.5, anchor="center")

        self.logo_lbl = tk.Label(frm, text=FSOCIETY_LOGO,
                                  font=("Courier", 12, "bold"),
                                  bg=BG, fg=GREEN, justify="center")
        self.logo_lbl.pack(pady=(0, 4))

        self.skull_lbl = tk.Label(frm, text=SKULL_BIG,
                                   font=("Courier", 10),
                                   bg=BG, fg=RED, justify="center")
        self.skull_lbl.pack()

        self.main_var = tk.StringVar(value="")
        tk.Label(frm, textvariable=self.main_var,
                 font=("Courier", 15, "bold"),
                 bg=BG, fg=RED, justify="center").pack(pady=(10, 3))

        self.timer_var = tk.StringVar()
        tk.Label(frm, textvariable=self.timer_var,
                 font=("Courier", 30, "bold"),
                 bg=BG, fg=GREEN).pack()

        self.prog_var = tk.StringVar()
        tk.Label(frm, textvariable=self.prog_var,
                 font=("Courier", 10),
                 bg=BG, fg=DGREEN).pack(pady=(4, 0))

        self.status_var = tk.StringVar(value="")
        tk.Label(frm, textvariable=self.status_var,
                 font=("Courier", 9),
                 bg=BG, fg="#005500").pack(pady=(2, 0))

        # barely-visible hint
        tk.Label(frm, text="[ CTRL+SHIFT+Q — exit prank ]",
                 font=("Courier", 7), bg=BG, fg="#111111").pack(pady=(18, 0))

    # ── animations ──────────────────────────────────────────────────────
    def _start(self):
        self._matrix_tick()
        self._glitch_tick()
        self._type_msg("  YOUR SYSTEM HAS BEEN COMPROMISED\n    WE ARE FSOCIETY  —  HELLO, FRIEND")
        self._timer_tick(self.COUNTDOWN)
        self._prog_tick(0)
        self._status_tick()
        self._flash_tick()
        self._popup_wave()

    def _matrix_tick(self):
        if not running: return
        for col in self.mat:
            col["y"] += col["spd"]
            if col["y"] > self.sh + 60:
                col["y"] = random.randint(-200, -20)
                col["spd"] = random.randint(4, 18)
            for j, item in enumerate(col["items"]):
                self.canvas.coords(item, col["x"], col["y"] + j * 14)
                if random.random() < 0.08:
                    self.canvas.itemconfig(item, text=random.choice("01ABCDEF░▒▓█"))
                    self.canvas.itemconfig(item, fill=GREEN if j == 0 else (MGREEN if j < 3 else DGREEN))
        self.root.after(35, self._matrix_tick)

    def _glitch_tick(self):
        if not running: return
        intensity = 0.03 + random.random() * 0.13
        self.logo_lbl.config(text=glitch(FSOCIETY_LOGO, intensity))
        self.skull_lbl.config(text=glitch(SKULL_BIG, intensity * 0.4))
        self.root.after(random.randint(50, 220), self._glitch_tick)

    def _type_msg(self, msg: str, idx: int = 0):
        if not running: return
        self.main_var.set(msg[:idx] + ("▌" if idx < len(msg) else ""))
        if idx < len(msg):
            self.root.after(random.randint(25, 70),
                            lambda: self._type_msg(msg, idx + 1))

    def _timer_tick(self, val: int):
        if not running: return
        mm, ss = divmod(max(0, val), 60)
        self.timer_var.set(f"◈  {mm:02d}:{ss:02d}  ◈")
        if val > 0:
            self.root.after(1000, lambda: self._timer_tick(val - 1))
        else:
            self._exit()

    def _prog_tick(self, pct: int):
        if not running: return
        done = pct // 3
        bar  = "█" * done + "▓" + "░" * max(0, 33 - done - 1)
        self.prog_var.set(f"UPLOADING TO F-SOCIETY SERVER  [{bar}]  {pct}%")
        if pct < 100:
            self.root.after(random.randint(55, 170),
                            lambda: self._prog_tick(min(100, pct + random.randint(1, 3))))

    def _status_tick(self):
        if not running: return
        self.status_var.set(f" ▶  {random.choice(STATUS_MSGS)}")
        self.root.after(random.randint(700, 2200), self._status_tick)

    def _flash_tick(self):
        if not running: return
        if random.random() < 0.07:
            col = random.choice([RED, "#FF4400", WHITE, "#FF0055"])
            self.root.configure(bg=col)
            self.root.after(55, lambda: self.root.configure(bg=BG))
            flash_beep()
        self.root.after(random.randint(150, 900), self._flash_tick)

    def _popup_wave(self):
        def loop():
            for _ in range(18):
                if not running: break
                self.root.after(0, spawn_popup)
                time.sleep(random.uniform(0.4, 1.3))
        threading.Thread(target=loop, daemon=True).start()

    def _exit(self):
        global running
        running = False
        kill_popups()
        try: self.root.destroy()
        except Exception: pass

    def run(self):
        self.root.mainloop()


# ── phase 1: popup wave before lockscreen ─────────────────────────────────
def phase1():
    root = tk.Tk()
    root.withdraw()

    def wave():
        for _ in range(14):
            if not running: break
            root.after(0, spawn_popup)
            threading.Thread(target=beep, daemon=True).start()
            time.sleep(random.uniform(0.1, 0.45))
        time.sleep(1.8)
        root.after(0, lambda: (kill_popups(), root.quit()))

    threading.Thread(target=wave, daemon=True).start()
    root.mainloop()


if __name__ == "__main__":
    phase1()
    if running:
        Lockscreen().run()
