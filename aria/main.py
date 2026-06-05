import tkinter as tk
import threading
import queue
import time
import subprocess
import sys
import os
import webbrowser
import datetime
import random
import glob

missing = []
try:
    import pyttsx3
except ImportError:
    missing.append("pyttsx3")

try:
    import speech_recognition as sr
except ImportError:
    missing.append("SpeechRecognition")

if missing:
    print(f"Run: pip install {' '.join(missing)}")
    sys.exit(1)


BG       = "#1a1a2e"
BG2      = "#16213e"
BG3      = "#0f3460"
RED      = "#e94560"
WHITE    = "#ffffff"
GRAY     = "#a0a0b0"
DARKGRAY = "#2a2a4a"


APPS = {
    "notepad":        "notepad.exe",
    "calculator":     "calc.exe",
    "paint":          "mspaint.exe",
    "explorer":       "explorer.exe",
    "file explorer":  "explorer.exe",
    "task manager":   "taskmgr.exe",
    "cmd":            "cmd.exe",
    "terminal":       "cmd.exe",
    "vs code":        "code",
    "chrome":         r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "brave":          r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    "firefox":        r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "edge":           r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "spotify":        r"C:\Users\maste\AppData\Roaming\Spotify\Spotify.exe",
    "vlc":            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
}

SITES = {
    "youtube":   "https://www.youtube.com",
    "gmail":     "https://mail.google.com",
    "whatsapp":  "https://web.whatsapp.com",
    "chatgpt":   "https://chat.openai.com",
    "chat gpt":  "https://chat.openai.com",
    "google":    "https://www.google.com",
    "github":    "https://www.github.com",
    "instagram": "https://www.instagram.com",
    "twitter":   "https://www.twitter.com",
    "facebook":  "https://www.facebook.com",
}

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why was the JavaScript developer sad? He didn't Node how to Express himself.",
    "There are 10 types of people: those who understand binary and those who don't.",
    "I told my computer I needed a break. Now it won't stop sending me Kit Kat ads.",
    "Why do Java developers wear glasses? Because they don't C sharp!",
]


class Speaker:
    def __init__(self):
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty("voices")
        for v in voices:
            if "zira" in v.name.lower() or "female" in v.name.lower():
                self.engine.setProperty("voice", v.id)
                break
        self.engine.setProperty("rate", 170)
        self.engine.setProperty("volume", 1.0)

    def say(self, text):
        def run():
            self.engine.say(text)
            self.engine.runAndWait()
        threading.Thread(target=run, daemon=True).start()


class Listener:
    def __init__(self):
        self.r = sr.Recognizer()
        self.r.pause_threshold = 0.8
        self.r.dynamic_energy_threshold = True
        self.mic_index = self.find_mic()

    def find_mic(self):
        # By returning None, speech_recognition will use the system's default microphone.
        # This prevents the app from trying to use disconnected Bluetooth headsets.
        return None

    def listen(self):
        old = sys.stderr
        devnull = open(os.devnull, "w")
        sys.stderr = devnull
        try:
            kwargs = {}
            if self.mic_index is not None:
                kwargs["device_index"] = self.mic_index
            sys.stderr = old
            with sr.Microphone(**kwargs) as source:
                self.r.adjust_for_ambient_noise(source, duration=0.4)
                audio = self.r.listen(source, timeout=8, phrase_time_limit=12)
            return self.r.recognize_google(audio)
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return "[NO_INTERNET]"
        except:
            self.mic_index = self.find_mic()
            return "[NO_MIC]"
        finally:
            sys.stderr = old
            try:
                devnull.close()
            except:
                pass


def handle(text):
    t = text.lower().strip()

    if any(w in t for w in ["hello", "hi", "hey"]):
        h = datetime.datetime.now().hour
        g = "Good morning" if h < 12 else "Good afternoon" if h < 18 else "Good evening"
        return f"{g}! I am ready. How can I help you?"

    if "time" in t:
        return "The time is " + datetime.datetime.now().strftime("%I:%M %p")

    if "date" in t:
        return "Today is " + datetime.datetime.now().strftime("%A, %B %d %Y")

    if "joke" in t:
        return random.choice(JOKES)

    if "weather" in t:
        city = ""
        for w in t.split():
            if len(w) > 3 and w not in ["weather", "what", "like", "today", "show", "tell"]:
                city = w
                break
        webbrowser.open(f"https://wttr.in/{city}")
        return "Opening weather forecast."

    if "open" in t or "launch" in t:
        for name, url in SITES.items():
            if name in t:
                webbrowser.open(url)
                return f"Opening {name}."
        for name, path in APPS.items():
            if name in t:
                return launch_app(name, path)
        app_name = t.replace("open", "").replace("launch", "").strip()
        if app_name:
            return smart_find(app_name)

    if any(w in t for w in ["search", "google", "look up", "what is", "who is"]):
        for prefix in ["search for", "search", "google", "look up", "what is", "who is"]:
            if t.startswith(prefix):
                q = t[len(prefix):].strip()
                if q:
                    webbrowser.open(f"https://www.google.com/search?q={q.replace(' ', '+')}")
                    return f"Searching for {q}."
        webbrowser.open(f"https://www.google.com/search?q={t.replace(' ', '+')}")
        return f"Searching for {t}."

    if any(w in t for w in ["bye", "goodbye", "exit", "quit", "stop"]):
        return "GOODBYE"

    if len(t.split()) > 2:
        webbrowser.open(f"https://www.google.com/search?q={t.replace(' ', '+')}")
        return f"Searching for: {t}"

    return "I didn't get that. Please try again."


def launch_app(name, path):
    if os.path.exists(path):
        try:
            subprocess.Popen([path])
            return f"Opening {name}."
        except:
            pass
    try:
        subprocess.Popen(f'start "" "{path}"', shell=True)
        return f"Opening {name}."
    except:
        return f"Could not open {name}."


def smart_find(name):
    folders = [
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs"),
    ]
    for folder in folders:
        for lnk in glob.glob(os.path.join(folder, "**", "*.lnk"), recursive=True):
            lnk_name = os.path.splitext(os.path.basename(lnk))[0].lower()
            if name in lnk_name or lnk_name in name:
                try:
                    subprocess.Popen(f'start "" "{lnk}"', shell=True)
                    return f"Opening {name}."
                except:
                    pass
    for folder in [r"C:\Program Files", r"C:\Program Files (x86)"]:
        for exe in glob.glob(os.path.join(folder, "**", "*.exe"), recursive=True):
            exe_name = os.path.splitext(os.path.basename(exe))[0].lower()
            if name in exe_name or exe_name in name:
                try:
                    subprocess.Popen([exe])
                    return f"Opening {name}."
                except:
                    pass
    return f"Could not find {name}."


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Voice Assistant")
        self.geometry("360x580")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.listening = False
        self.q = queue.Queue()
        self.speaker = Speaker()
        self.listener = Listener()
        self.last_command = tk.StringVar(value="None")
        self.last_result = tk.StringVar(value="None")

        self.build()
        self.check_queue()
        threading.Thread(target=self.greet, daemon=True).start()

    def build(self):
        tk.Frame(self, bg=BG, height=24).pack()

        tk.Label(self, text="AI Voice Assistant", bg=BG, fg=WHITE,
                 font=("Segoe UI", 16, "bold")).pack()

        tk.Frame(self, bg=BG, height=24).pack()

        self.mic_canvas = tk.Canvas(self, width=110, height=110,
                                    bg=BG, highlightthickness=0)
        self.mic_canvas.pack()
        self.draw_mic()

        tk.Frame(self, bg=BG, height=8).pack()

        self.status_var = tk.StringVar(value="Click mic to speak")
        tk.Label(self, textvariable=self.status_var, bg=BG, fg=RED,
                 font=("Segoe UI", 11, "bold")).pack()

        tk.Frame(self, bg=BG, height=20).pack()

        info = tk.Frame(self, bg=BG2, padx=16, pady=14)
        info.pack(fill="x", padx=24)

        tk.Label(info, text="Last Command", bg=BG2, fg=GRAY,
                 font=("Segoe UI", 8)).grid(row=0, column=0, sticky="w")
        tk.Label(info, textvariable=self.last_command, bg=BG2, fg=WHITE,
                 font=("Segoe UI", 10, "bold"), wraplength=290,
                 justify="left").grid(row=1, column=0, sticky="w", pady=(2, 10))

        tk.Label(info, text="Active Result", bg=BG2, fg=GRAY,
                 font=("Segoe UI", 8)).grid(row=2, column=0, sticky="w")
        tk.Label(info, textvariable=self.last_result, bg=BG2, fg=WHITE,
                 font=("Segoe UI", 10, "bold"), wraplength=290,
                 justify="left").grid(row=3, column=0, sticky="w", pady=(2, 0))

        tk.Frame(self, bg=BG, height=16).pack()

        log_outer = tk.Frame(self, bg=BG2)
        log_outer.pack(fill="both", expand=True, padx=24, pady=(0, 0))

        tk.Label(log_outer, text="  Activity Log", bg=BG3, fg=WHITE,
                 font=("Segoe UI", 9), anchor="w").pack(fill="x")

        self.log = tk.Text(log_outer, bg=BG2, fg=GRAY,
                           font=("Segoe UI", 9), bd=0,
                           state="disabled", wrap="word",
                           height=7, padx=8, pady=6)
        self.log.pack(fill="both", expand=True)

        self.log.tag_configure("user",   foreground=WHITE)
        self.log.tag_configure("aria",   foreground=RED)
        self.log.tag_configure("system", foreground=GRAY)

        tk.Frame(self, bg=BG, height=10).pack()

        bottom = tk.Frame(self, bg=BG2)
        bottom.pack(fill="x", padx=24, pady=(0, 20))

        self.text_box = tk.Entry(bottom, bg=DARKGRAY, fg=GRAY,
                                 insertbackground=WHITE,
                                 font=("Segoe UI", 10), bd=0, relief="flat")
        self.text_box.pack(side="left", fill="x", expand=True, padx=(8, 0), pady=8)
        self.text_box.insert(0, "Type command here...")
        self.text_box.bind("<FocusIn>",  self.clear_hint)
        self.text_box.bind("<FocusOut>", self.restore_hint)
        self.text_box.bind("<Return>",   self.send_text)

        go = tk.Label(bottom, text="  GO  ", bg=RED, fg=WHITE,
                      font=("Segoe UI", 9, "bold"), cursor="hand2", pady=8)
        go.pack(side="right", padx=(4, 8))
        go.bind("<Button-1>", self.send_text)

    def draw_mic(self, listening=False, speaking=False):
        self.mic_canvas.delete("all")
        if listening:
            color = RED
        elif speaking:
            color = "#4CAF50"
        else:
            color = BG3
        self.mic_canvas.create_oval(5, 5, 105, 105, fill=color, outline="")
        self.mic_canvas.create_text(55, 55, text="🎙",
                                    font=("Segoe UI Emoji", 30))
        self.mic_canvas.bind("<Button-1>", lambda e: self.toggle_mic())

    def toggle_mic(self):
        if self.listening:
            return
        self.listening = True
        self.draw_mic(listening=True)
        self.status_var.set("Listening...")
        self.add_log("System: Listening...", "system")
        threading.Thread(target=self.do_listen, daemon=True).start()

    def do_listen(self):
        result = self.listener.listen()
        self.q.put(result)

    def check_queue(self):
        try:
            while True:
                text = self.q.get_nowait()
                if text != "BOOT":
                    self.process(text)
        except queue.Empty:
            pass
        self.after(100, self.check_queue)

    def process(self, text):
        self.listening = False
        self.draw_mic()
        self.status_var.set("Click mic to speak")

        if text == "[NO_MIC]":
            self.add_log("System: No microphone detected.", "system")
            return
        if text == "[NO_INTERNET]":
            self.add_log("System: No internet connection.", "system")
            return
        if not text:
            self.add_log("System: Didn't catch that.", "system")
            return

        self.last_command.set(text)
        self.add_log(f"You: {text}", "user")

        response = handle(text)

        if response == "GOODBYE":
            self.add_log("Assistant: Goodbye! See you soon.", "aria")
            self.speaker.say("Goodbye! See you soon.")
            self.after(2000, self.destroy)
            return

        self.last_result.set(response)
        self.add_log(f"Assistant: {response}", "aria")
        self.draw_mic(speaking=True)
        self.status_var.set("Speaking...")
        self.speaker.say(response)
        self.after(2500, lambda: [self.draw_mic(), self.status_var.set("Click mic to speak")])

    def add_log(self, text, tag):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n", tag)
        self.log.configure(state="disabled")
        self.log.see("end")

    def send_text(self, *args):
        text = self.text_box.get().strip()
        if not text or text == "Type command here...":
            return
        self.text_box.delete(0, "end")
        self.process(text)

    def clear_hint(self, e):
        if self.text_box.get() == "Type command here...":
            self.text_box.delete(0, "end")
            self.text_box.configure(fg=WHITE)

    def restore_hint(self, e):
        if not self.text_box.get():
            self.text_box.insert(0, "Type command here...")
            self.text_box.configure(fg=GRAY)

    def greet(self):
        time.sleep(0.8)
        h = datetime.datetime.now().hour
        g = "Good morning" if h < 12 else "Good afternoon" if h < 18 else "Good evening"
        msg = f"{g}! Say Hey Assistant to wake me up."
        self.q.put("BOOT")
        self.after(0, lambda: self.add_log("Assistant: System initialized. I am ready to help.", "aria"))
        self.after(0, lambda: self.last_result.set("System initialized. I am ready to help."))
        self.speaker.say(msg)


if __name__ == "__main__":
    App().mainloop()
