# Civilization VI Gemini AI Advisor 🧠🏛️

**Civ6 Gemini Advisor** is an intelligent, real-time strategy assistant for *Sid Meier's Civilization VI*, powered by Google's Gemini AI. It analyzes your game state directly from the logs and provides actionable advice on economy, research, military, and diplomacy via a non-intrusive overlay.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Lua](https://img.shields.io/badge/Lua-5.2-000080) ![Gemini API](https://img.shields.io/badge/AI-Gemini%20Pro-8E44AD)

## 🌟 Features

*   **Real-time Analysis:** Tracks your science, culture, gold, faith, and city status every turn.
*   **AI-Powered Strategy:** Uses Google Gemini Pro to generate context-aware advice based on your current civilization and situation.
*   **In-Game Overlay:** Displays advice in a transparent, "Always-on-Top" window that floats over the game.
*   **Safe & Non-Cheating:** Reads data from `Lua.log` (exported by a custom mod) and does not modify game memory or save files.

## 📂 Project Structure

*   `Civ6Mod/`: The Lua mod that exports game data to `Lua.log`.
*   `Advisor/`: The Python application that reads the log, queries Gemini AI, and displays the overlay.

## 🚀 Installation

### Prerequisites

1.  **Civilization VI** (Steam/Epic)
2.  **Python 3.10** or higher
3.  **Google Gemini API Key** ([Get it here](https://aistudio.google.com/app/apikey))

### Step 1: Install the Mod

Copy the `Civ6Mod` folder to your game's Mods directory:

*   **Windows:** `C:\Users\[YourName]\Documents\My Games\Sid Meier's Civilization VI\Mods`

### Step 2: Enable Logging

1.  Navigate to `C:\Users\[YourName]\AppData\Local\Firaxis Games\Sid Meier's Civilization VI\AppOptions.txt`.
2.  Open it and ensure `EnableLuaLogger 1` is set under the `[Debug]` section.

### Step 3: Setup the Advisor

1.  Clone this repository:
    ```bash
    git clone https://github.com/ChiwooSong/Civ6-AI-Advisor.git
    cd Civ6-AI-Advisor/Advisor
    ```
2.  Create a virtual environment and install dependencies:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  Create a `.env` file in the `Advisor` folder:
    ```env
    GEMINI_API_KEY=your_api_key_here
    CIV6_LOG_PATH=C:/Users/[YourName]/AppData/Local/Firaxis Games/Sid Meier's Civilization VI/Logs/Lua.log
    ```

## 🎮 Usage

1.  Run the advisor:
    ```bash
    cd Advisor
    .\venv\Scripts\python main.py
    ```
2.  Launch **Civilization VI**.
3.  Enable the mod **"Civ6 Gemini Strategist"** in "Additional Content".
4.  Start a game. The advisor window will update automatically each turn!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License
