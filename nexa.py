"""
================================================================================
PROJECT: NEXA / NEXA ULTIMATE TERMINAL INTERFACE
ENVIRONMENT: Windows Terminal (100% Offline Local AI, Voice & Automation)
CORE AI: Llama 3.2 1B via Ollama (Auto-managed background server)
================================================================================
"""

import os
import sys
import platform
import subprocess
import webbrowser
import datetime
import time
import urllib.request
import threading
import queue
import psutil
import ollama
import pyttsx3
import speech_recognition as sr
import numpy as np
# PyCaw Audio Imports
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import ctypes

# ==============================================================================
# 0. TERMINAL STYLING & ANSI COLORS
# ==============================================================================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033'
    BOLD = '\033[1m'


# ==============================================================================
# 1. THREAD-SAFE VOICE ENGINE (NON-BLOCKING SPEECH QUEUE)
# ==============================================================================

speech_queue = queue.Queue()

def voice_worker():
    """Single background worker loop to safely handle speech without thread crashes."""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 175)    # Speed of speech
        engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
    except Exception as e:
        print(f"{Colors.FAIL}[TTS Init Error]: {e}{Colors.ENDC}")
        return

    while True:
        text = speech_queue.get()
        if text is None:
            break
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"\n{Colors.FAIL}[Speech Processing Error]: {e}{Colors.ENDC}")
        finally:
            speech_queue.task_done()

# Launch background speech worker thread once globally
speech_thread = threading.Thread(target=voice_worker, daemon=True)
speech_thread.start()

def speak_text(text):
    """Adds speech tasks safely to the speech queue."""
    if text:
        speech_queue.put(text)

        import speech_recognition as sr

# ==============================================================================
# MICROPHONE STATE & BACKGROUND VOICE LISTENER
# ==============================================================================
mic_enabled = False  # Microphone starts OFF by default

import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav

def listen_in_background():
    """Background listener using sounddevice (no C++ build tools required)."""
    global mic_enabled
    recognizer = sr.Recognizer()
    
    fs = 44100  # Sample rate
    seconds = 5  # Duration of each voice chunk

    while True:
        if mic_enabled:
            try:
                print(f"\n{Colors.GREEN}[🎙️ MIC ACTIVE - Speak now...]{Colors.ENDC}")
                
                # Record audio using sounddevice
                audio_data = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
                sd.wait()  # Wait until the recording is finished
                
                # Save temporarily to a wav file
                temp_file = "temp_voice.wav"
                wav.write(temp_file, fs, audio_data)
                
                # Recognize speech from the wav file
                with sr.AudioFile(temp_file) as source:
                    audio = recognizer.record(source)
                    voice_text = recognizer.recognize_google(audio).strip()
                    
                    if voice_text:
                        print(f"\n{Colors.WARNING}You (Voice): {voice_text}{Colors.ENDC}")
                        process_command(voice_text)
                        
            except sr.UnknownValueError:
                # Spoken words weren't clear enough; loop silently
                pass
            except Exception as e:
                # Catch audio device timeout/busy states gracefully
                time.sleep(0.5)
        else:
            time.sleep(0.5)

# Start background microphone thread once globally
mic_thread = threading.Thread(target=listen_in_background, daemon=True)
mic_thread.start()


# ==============================================================================
# 2. OLLAMA AUTO-START SERVER ENGINE
# ==============================================================================

def ensure_ollama_running():
    """Checks if Ollama background server is responding; launches automatically if offline."""
    try:
        urllib.request.urlopen("http://localhost:11434", timeout=1)
    except Exception:
        print(f"{Colors.WARNING}[NEXA System]: Ollama server not detected. Booting up in background...{Colors.ENDC}")
        try:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            time.sleep(3)
            print(f"{Colors.GREEN}[NEXA System]: Ollama background server online!{Colors.ENDC}\n")
        except Exception as e:
            print(f"{Colors.FAIL}[NEXA Error]: Failed to launch Ollama. Run 'ollama serve' manually. Details: {e}{Colors.ENDC}")

def print_banner():
    print(f"{Colors.CYAN}{Colors.BOLD}" + "="*60)
    print("      NEXA ULTIMATE TERMINAL INTERFACE")
    print("      [⚡] System & App Automation = 0.01s (Instant)")
    print("      [🔍] Smart Web Search = Chrome & YouTube")
    print("      [⚡] Power Controls = Shutdown / Restart / Sleep")
    print("      [🧠] Conversational AI = Llama 3.2 1B (Streaming)")
    print("      (Press Ctrl + C anytime to exit)")
    print("="*60 + f"{Colors.ENDC}\n")


# ==============================================================================
# 3. INSTANT SYSTEM AUTOMATION & UTILITIES ENGINE
# ==============================================================================

def control_power(user_lower):
    """Executes safe power state controls for shutdown, restart, and sleep."""
    try:
        # Shutdown commands
        if "shutdown" in user_lower:
            os.system("shutdown /s /t 10")
            return "Initiating system shutdown sequence in 7 seconds. Goodbye, sir."
        
        # Restart commands
        elif "restart" in user_lower:
            os.system("shutdown /r /t 10")
            return "Initiating system reboot sequence in 7 seconds, sir."
        
        # Sleep commands
        elif "sleep" in user_lower:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "Putting your system into sleep mode, sir."
            
        return None
    except Exception as e:
        return f"Power command failure: {e}"

        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import ctypes

def control_volume(user_lower):
    """Controls Windows master system volume (up, down, mute, unmute)."""
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
        
        # Get current volume level (-65.0 to 0.0 dB)
        current_scalar = volume.GetMasterVolumeLevelScalar() # 0.0 to 1.0
        
        if "volume up" in user_lower or "increase volume" in user_lower:
            new_scalar = min(1.0, current_scalar + 0.15)
            volume.SetMasterVolumeLevelScalar(new_scalar, None)
            return "Increasing volume, sir."
            
        elif "volume down" in user_lower or "decrease volum"in user_lower:
            new_scalar = max(0.0, current_scalar - 0.15)
            volume.SetMasterVolumeLevelScalar(new_scalar, None)
            return "Decreasing volume, sir."
            
        elif "mute" in user_lower:
            volume.SetMute(1, None)
            return "Muting audio, sir."
            
        elif "unmute" in user_lower:
            volume.SetMute(0, None)
            return "Unmuting audio, sir."
            
        return None
    except Exception as e:
        return f"Volume control failure: {e}"

def control_clock(user_lower):
    """Opens the Windows default Clock app to specific tabs using URI protocols."""
    try:
        if "alarm" in user_lower:
            os.system("start ms-clock:alarm")
            return "Opening Windows Alarms, sir."
        elif "timer" in user_lower:
            os.system("start ms-clock:timer")
            return "Opening Windows Timer, sir."
        elif "focus" in user_lower or "focus session" in user_lower:
            os.system("start ms-clock:focus")
            return "Opening Windows Focus Sessions, sir."
        elif "stopwatch" in user_lower:
            os.system("start ms-clock:stopwatch")
            return "Opening Windows Stopwatch, sir."
        else:
            os.system("start ms-clock:")
            return "Opening the Windows Clock app, sir."
    except Exception as e:
        return f"Failed to open Clock app: {e}"
    
def close_application(user_lower):
    """Terminates running applications or closes specific target programs."""
    try:
        # Extract target app name if phrase matches "close [app]" or "kill [app]"
        target = ""
        if "close" in user_lower:
            target = user_lower.split("close")[-1].strip()
        elif "kill" in user_lower:
            target = user_lower.split("kill")[-1].strip()
            
        if not target:
            return "Please specify which application you would like to close, sir."
            
        closed_any = False
        # Iterate through running system processes
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                proc_name = proc.info['name'].lower()
                if target in proc_name or target.replace(" ", "") in proc_name.replace(" ", ""):
                    proc.terminate()
                    closed_any = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
        if closed_any:
            return f"Successfully closed {target}, sir."
        else:
            return f"Could not find any running process matching '{target}', sir."
            
    except Exception as e:
        return f"Failed to close application: {e}"

def get_system_stats():
    """Gathers live CPU, RAM, and disk stats instantly."""
    try:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('C:')
        
        stats_msg = (
            f"System Status: CPU usage is at {cpu} percent, "
            f"RAM usage is at {mem.percent} percent, "
            f"and C Drive has {disk.free // (1024**3)} gigabytes free."
        )
        return stats_msg
    except Exception as e:
        return f"Failed to retrieve system telemetry: {e}"

def open_folder(user_lower):
    """Opens core Windows directories instantly in File Explorer."""
    try:
        user_profile = os.environ.get("USERPROFILE", "C:\\")
        
        if "download" in user_lower:
            path = os.path.join(user_profile, "Downloads")
            os.startfile(path)
            return "Opening your Downloads directory, sir."
        elif "document" in user_lower:
            path = os.path.join(user_profile, "Documents")
            os.startfile(path)
            return "Opening your Documents directory, sir."
        elif "desktop" in user_lower:
            path = os.path.join(user_profile, "Desktop")
            os.startfile(path)
            return "Opening your Desktop directory, sir."
        elif "picture" in user_lower or "photo folder" in user_lower:
            path = os.path.join(user_profile, "Pictures")
            os.startfile(path)
            return "Opening your Pictures directory, sir."
        elif "project" in user_lower or "workspace" in user_lower:
            path = r"D:\SUBODH\projects"
            os.startfile(path)
            return "Opening your Projects workspace directory, sir."
        else:
            subprocess.Popen("explorer")
            return "Opening File Explorer, sir."
    except Exception as e:
        return f"Failed to access folder path: {e}"

def open_application(user_lower, full_input=""):
    """Launches local desktop software, web links, and automated searches error-free."""
    system_name = platform.system()
    
    try:
        # ==========================================
        # 1. AUTOMATED WEB SEARCHES (CHROME & YOUTUBE)
        # ==========================================
        if "chrome" in user_lower and "search" in user_lower:
            if "search for" in user_lower:
                query = full_input.lower().split("search for")[-1].strip()
            else:
                query = full_input.lower().split("search")[-1].strip()
                
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return f"Opening Google Chrome and searching for '{query}', sir."

        elif "youtube" in user_lower and "search" in user_lower:
            if "search for" in user_lower:
                query = full_input.lower().split("search for")[-1].strip()
            else:
                query = full_input.lower().split("search")[-1].strip()
                
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return f"Searching YouTube for '{query}', sir."

        # ==========================================
        # 2. WEBSITES & WEB SERVICES
        # ==========================================
        elif "l mail" in user_lower:
            webbrowser.open("https://mail.google.com")
            return "Launching Gmail, sir."
        elif "l gemini" in user_lower:
            webbrowser.open("https://gemini.google.com")
            return "Launching Google Gemini, sir."
        elif "l deepseek" in user_lower:
            webbrowser.open("https://chat.deepseek.com")
            return "Launching DeepSeek AI, sir."
        elif "l map" in user_lower or "google map" in user_lower:
            webbrowser.open("https://www.google.com/maps")
            return "Launching Google Maps, sir."
        elif "l youtube" in user_lower:
            webbrowser.open("https://www.youtube.com")
            return "Launching YouTube, sir."
        elif "l whatsapp" in user_lower:
            webbrowser.open("https://web.whatsapp.com/")
            return "Launching whatsapp, sir."
        elif "l reddit" in user_lower:
                    webbrowser.open("https://www.reddit.com")
                    return "Launching reddit, sir."       
        elif "l google" in user_lower:
            webbrowser.open("https://www.google.com")
            return "Launching Google, sir."
        elif "l github" in user_lower:
            webbrowser.open("https://github.com")
            return "Launching GitHub, sir."
        elif "l chatgpt" in user_lower:
            webbrowser.open("https://chatgpt.com")
            return "Launching ChatGPT, sir."

        # ==========================================
        # 3. WINDOWS APPS & SYSTEM UTILITIES
        # ==========================================
        elif "x terminal" in user_lower or "cmd" in user_lower or "command prompt" in user_lower:
            subprocess.Popen("wt", shell=True)
            return "Spawning new Windows Terminal instance, sir."
        elif "x ms store" in user_lower:
            subprocess.Popen("start mswindows-store:", shell=True)
            return "Opening Microsoft Store, sir."
        elif "x photo" in user_lower:
            subprocess.Popen("start ms-photos:", shell=True)
            return "Opening Photos, sir."
        elif "x media player" in user_lower:
            subprocess.Popen("start mswindowsmusic:", shell=True)
            return "Opening Media Player, sir."
        elif "x sn" in user_lower:
            subprocess.Popen("start ms-stickynotes:", shell=True)
            return "Opening Sticky Notes, sir."
        elif "x camera" in user_lower:
            subprocess.Popen("start microsoft.windows.camera:", shell=True)
            return "Opening Camera, sir."
        elif "x task manager" in user_lower:
            subprocess.Popen("taskmgr.exe")
            return "Opening Task Manager, sir."
        elif "x gb" in user_lower:
            subprocess.Popen("start xboxgamebar:", shell=True)
            return "Launching Xbox Game Bar, sir."

        # ==========================================
        # 4. GAMES & DESKTOP SOFTWARE
        # ==========================================
        elif "o roblox studio" in user_lower:
            subprocess.Popen('explorer.exe shell:AppsFolder\\ROBLOXCORPORATION.ROBLOXSTUDIO_55nm523wkazg6!Studio', shell=True)
            return "Launching Roblox Studio, sir."
        elif "o antigravity" in user_lower:
            project_path = r"D:\SUBODH\projects"
            if os.path.exists(project_path):
                os.startfile(project_path)
            return "Antigravity workspace opened, sir."
        elif "o chrome" in user_lower or "google chrome" in user_lower:
            subprocess.Popen("start chrome", shell=True)
            return "Opening Google Chrome, sir."
        elif "o spotify" in user_lower:
            os.startfile("spotify:") if system_name == "Windows" else subprocess.Popen(["spotify"])
            return "Initializing Spotify, sir."
        elif "o vs code" in user_lower:
            subprocess.Popen("code", shell=True)
            return "Launching Visual Studio Code workspace, sir."
        elif "o notepad" in user_lower:
            subprocess.Popen("notepad.exe")
            return "Opening Notepad utility, sir."
        elif "o calc" in user_lower or "calculator" in user_lower:
            subprocess.Popen("calc.exe")
            return "Opening Calculator, sir."
            
        return None
    except Exception as e:
        return f"Failed to launch application: {e}"


# ==============================================================================
# 4. STREAMING AI CORE ROUTER (Llama 3.2 1B)
# ==============================================================================

import json

def load_user_profile():
    """Loads user personal information dynamically from user_profile.json."""
    profile_path = "user_profile.json"
    if os.path.exists(profile_path):
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return (
                    f"You are NEXA, an elite personal AI assistant for {data.get('name', 'sir')}. "
                    f"User profile details: Main project is {data.get('main_project')}, "
                    f"workspace path is {data.get('projects_folder')}. "
                    f"Custom preferences: {', '.join(data.get('custom_notes', []))}."
                )
        except Exception:
            pass
    return "You are NEXA, an elite, direct, and highly intelligent local AI assistant."

conversation_history = [
    {
        'role': 'system',
        'content': load_user_profile()
    }
]

def log_interaction(user_query, nexa_reply):
    """Logs session history locally to a text file."""
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("NEXA_session_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] User: {user_query}\n")
            f.write(f"[{timestamp}] NEXA: {nexa_reply}\n")
            f.write("-" * 50 + "\n")
    except Exception:
        pass

def process_command(user_input):
    global mic_enabled       # <-- ADD THIS LINE
    user_lower = user_input.lower()

    # ==========================================
    # MIC TOGGLE COMMANDS ("ON MIC" / "OFF MIC")
    # ==========================================
    if "on mic" in user_lower or "enable mic" in user_lower or "turn on mic" in user_lower:
        mic_enabled = True
        reply = "Microphone activated, sir. I am listening to your voice."
        print(f"\n{Colors.GREEN}[⚡ INSTANT SYSTEM COMMAND]{Colors.ENDC}\nNEXA: {reply}\n")
        speak_text(reply)
        return

    elif "off mic" in user_lower or "disable mic" in user_lower or "turn off mic" in user_lower:
        mic_enabled = False
        reply = "Microphone muted, sir. Switched to manual terminal input."
        print(f"\n{Colors.GREEN}[⚡ INSTANT SYSTEM COMMAND]{Colors.ENDC}\nNEXA: {reply}\n")
        speak_text(reply)
        return
    
    # ==========================================
    # WINDOWS CLOCK COMMANDS (Alarm, Timer, Focus)
    # ==========================================
    if any(c in user_lower for c in ["alarm", "timer", "focus session", "stopwatch", "clock app"]):
        reply = control_clock(user_lower)
        print(f"\n{Colors.GREEN}[⚡ INSTANT SYSTEM COMMAND]{Colors.ENDC}\nNEXA: {reply}\n")
        speak_text(reply)
        log_interaction(user_input, reply)
        return
    
    if any(v in user_lower for v in ["volume", "louder", "quieter", "mute", "unmute", "increase volume", "decrease volume"]):
        reply = control_volume(user_lower)
        if reply:
            print(f"\n{Colors.GREEN}[⚡ INSTANT SYSTEM COMMAND]{Colors.ENDC}\nNEXA: {reply}\n")
            speak_text(reply)
            log_interaction(user_input, reply)
            return

    if "close " in user_lower or "kill " in user_lower:
        reply = close_application(user_lower)
        print(f"\n{Colors.GREEN}[⚡ INSTANT SYSTEM COMMAND]{Colors.ENDC}\nNEXA: {reply}\n")
        speak_text(reply)
        log_interaction(user_input, reply)
        return

    # Priority 1: Power Management (Shutdown, Restart, Sleep)
    power_reply = control_power(user_lower)
    if power_reply:
        print(f"\n{Colors.GREEN}[⚡ INSTANT SYSTEM COMMAND (0.01s)]{Colors.ENDC}")
        print(f"NEXA: {power_reply}\n")
        speak_text(power_reply)
        log_interaction(user_input, power_reply)
        return

    # Priority 2: System Telemetry / Hardware Status
    if any(k in user_lower for k in ["status", "stats", "cpu", "ram", "telemetry"]):
        reply = get_system_stats()
        print(f"\n{Colors.GREEN}[⚡ INSTANT SYSTEM COMMAND (0.01s)]{Colors.ENDC}")
        print(f"NEXA: {reply}\n")
        speak_text(reply)
        log_interaction(user_input, reply)
        return

    # Priority 3: Folders & Directory Navigation
    if "folder" in user_lower or any(f in user_lower for f in ["downloads", "documents", "desktop", "pictures", "workspace", "project"]):
        reply = open_folder(user_lower)
        print(f"\n{Colors.GREEN}[⚡ INSTANT SYSTEM COMMAND (0.01s)]{Colors.ENDC}")
        print(f"NEXA: {reply}\n")
        speak_text(reply)
        log_interaction(user_input, reply)
        return

    # Priority 4: Application, Search & Browser Launcher
    app_reply = open_application(user_lower, full_input=user_input)
    if app_reply:
        print(f"\n{Colors.GREEN}[⚡ INSTANT SYSTEM COMMAND (0.01s)]{Colors.ENDC}")
        print(f"NEXA: {app_reply}\n")
        speak_text(app_reply)
        log_interaction(user_input, app_reply)
        return

    # Priority 5: Conversational AI Engine (Llama 3.2 1B Streaming)
    print(f"\n{Colors.BLUE}[🧠 AI MODEL (Llama 3.2 1B - Active Stream)]{Colors.ENDC}")
    print(f"{Colors.BOLD}NEXA:{Colors.ENDC} ", end="", flush=True)
    
    try:
        conversation_history.append({'role': 'user', 'content': user_input})
        
        response = ollama.chat(
            model='llama3.2:1b',
            messages=conversation_history,
            stream=True,
            options={
                'num_predict': 200,
                'temperature': 0.4
            },
            keep_alive=-1
        )
        
        full_reply = ""
        for chunk in response:
            token = chunk['message']['content']
            print(token, end="", flush=True)
            full_reply += token
            
        print("\n")
        conversation_history.append({'role': 'assistant', 'content': full_reply})
        speak_text(full_reply)
        log_interaction(user_input, full_reply)
        
    except Exception as e:
        error_msg = f"Neural core connection error. Details: {e}"
        print(f"\n{Colors.FAIL}[AI Error]: {error_msg}{Colors.ENDC}\n")
        speak_text("Neural core connection error, sir.")


# ==============================================================================
# 5. MAIN TERMINAL EVENT LOOP
# ==============================================================================

if __name__ == "__main__":
    ensure_ollama_running()
    print_banner()

    startup_greeting = "All systems online and fully operational, sir."
    print(f"{Colors.CYAN}NEXA: {startup_greeting}{Colors.ENDC}\n")
    speak_text(startup_greeting)

    try:
        while True:
            try:
                user_text = input(f"{Colors.WARNING}You: {Colors.ENDC}").strip()

                if not user_text:
                    continue

                if user_text.lower() in ['exit', 'quit', 'bye', 'shutdown jarvis']:
                    exit_msg = "Terminating terminal session. Goodbye, sir."
                    print(f"\n{Colors.CYAN}NEXA: {exit_msg}{Colors.ENDC}")
                    speak_text(exit_msg)
                    time.sleep(1.5)
                    break

                process_command(user_text)

            except KeyboardInterrupt:
                print(f"\n\n{Colors.CYAN}NEXA: Emergency interrupt detected. Shutting down cleanly. Goodbye, sir!{Colors.ENDC}")
                sys.exit(0)

    except SystemExit:
        sys.exit(0)