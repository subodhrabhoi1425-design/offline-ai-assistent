[nexa_github_readme.md](https://github.com/user-attachments/files/34753180/nexa_github_readme.md)
# NEXA ⚡ Offline AI Assistant & Windows Terminal Interface

**NEXA** is an elite, blazingly fast, 100% offline local Python assistant and system automation terminal built for Windows. It combines instant low-level hardware control (0.01s execution) with a local streaming Llama 3.2 1B neural core via Ollama, featuring an intuitive structured prefix routing system.

Repository: [subodhrabhoi1425-design/offline-ai-assistent](https://github.com/subodhrabhoi1425-design/offline-ai-assistent)

## 🚀 Key Features

* **⚡ Instant System Automation (0.01s):** Direct Python-based execution for volume control, process termination, power management, and folder navigation without cloud latency.

* **📂 Structured Prefix Routing:** Clean, lightning-fast shortcuts categorized by prefixes:
  * `l` — Web Links & Web Services
  * `x` — Windows Native Utilities & System Apps
  * `o` — Desktop Software & Custom Workspaces

* **🎙️ Hands-Free Voice Pipeline:** Dual-threaded audio architecture utilizing `sounddevice` for background listening and a thread-safe `pyttsx3` speech queue to prevent UI freezing.

* **🧠 Local AI Fallback Core:** Auto-manages Ollama background servers, streaming responses from `llama3.2:1b` with dynamic profile context (`user_profile.json`).

* **📊 Telemetry & Session Logging:** Live CPU/RAM monitoring and local interaction logging to `NEXA_session_log.txt`.

## 🛠️ Command Prefix Reference

### 1. `l` — Web Links & Web Services
| Command | Action / Destination |
| :--- | :--- |
| `l mail` | Opens Google Gmail |
| `l gemini` | Opens Google Gemini AI |
| `l deepseek` | Opens DeepSeek AI Portal |
| `l map` | Opens Google Maps |
| `l youtube` | Opens YouTube |
| `l reddit` | Opens Reddit |
| `l google` | Opens Google Search Engine |
| `l github` | Opens GitHub Developer Portal |
| `l chatgpt` | Opens OpenAI ChatGPT |

### 2. `x` — Windows System Utilities
| Command | Action / Utility |
| :--- | :--- |
| `x terminal` | Spawns Windows Terminal (`wt`) |
| `x ms store` | Opens Microsoft Store |
| `x photo` | Opens Windows Photos App |
| `x media player` | Opens Windows Media Player |
| `x sn` | Opens Sticky Notes |
| `x camera` | Opens Windows Camera |
| `x task manager` | Opens Task Manager (`taskmgr.exe`) |
| `x gb` | Launches Xbox Game Bar |

### 3. `o` — Desktop Software & Games
| Command | Action / Application |
| :--- | :--- |
| `o roblox studio` | Launches Roblox Studio IDE |
| `o antigravity` | Opens Projects Workspace directory |
| `o chrome` | Opens Google Chrome Browser |
| `o spotify` | Initializes Spotify Music Player |
| `o vs code` | Launches Visual Studio Code workspace |
| `o notepad` | Opens Notepad utility |
| `o calc` | Opens Windows Calculator |

## 🧠 Ollama & Llama 3.2 1B Setup Guide

NEXA relies on **Ollama** to run Meta's lightweight `llama3.2:1b` model completely offline on your machine. Follow these steps before running NEXA for the first time:

1. **Download & Install Ollama:**
   * Visit [ollama.com](https://ollama.com/download) and download the **Windows Installer** (`OllamaSetup.exe`).
   * Run the installer. Once installed, Ollama runs quietly in your Windows System Tray.

2. **Pull the `llama3.2:1b` Model:**
   * Open **Windows Terminal**, **PowerShell**, or **Command Prompt** (`cmd`).
   * Run the command to download the 1-billion parameter model (~1.3 GB):
     ```bash
     ollama pull llama3.2:1b
     ```

3. **Verify Model Installation:**
   * Confirm that the model is ready by listing local models:
     ```bash
     ollama list
     ```
   * *(Note: NEXA automatically starts the background server at `http://localhost:11434` on launch!)*

## 📋 Python Dependencies

Ensure you have **Python 3.10+** installed on Windows, then install all required dependencies:

```bash
pip install psutil pycaw comtypes sounddevice scipy pyttsx3 ollama SpeechRecognition numpy
```

## ⚙️ Installation & Running NEXA

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/subodhrabhoi1425-design/offline-ai-assistent.git
   cd offline-ai-assistent
   ```

2. **Configure User Profile (Optional):**
   Create a `user_profile.json` file in the root directory to personalize NEXA's system memory:
   ```json
   {
       "name": [Your name],
       "main_project": "NEXA Terminal Assistant",
       "projects_folder": [your workspace location],
       "custom_notes": ["Prefers concise technical feedback", "Fast execution"]
   }
   ```

3. **Launch NEXA:**
   ```bash
   python nexa.py
   ```

## 📄 License

Distributed under the **MIT License**. Feel free to fork, modify, and build upon NEXA!

*Built with passion by Subodh.*
