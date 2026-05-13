# Xia - AI Voice & Vision Companion

Xia is a local AI companion script that listens to your voice, takes a screenshot of your screen to understand your context, and speaks back to you with different selectable personas. It runs completely locally using Ollama for inference and Microsoft Edge TTS for fast voice generation.

## Features

*   **Voice Interactions:** Listens to you through your microphone using `SpeechRecognition`.
*   **Vision Capabilities:** Takes a screenshot using `Pillow` right after you speak, allowing the AI to see what you are doing.
*   **Local AI:** Uses `Ollama` with the `llama3.2-vision` model for completely private, local processing.
*   **Multiple Personas:** Choose between different characters with unique personalities and voices (e.g., Freaky Goth, Sweet Helper, Posh British, Freaky Gamer).
*   **Fast TTS:** Uses `edge-tts` for high-quality, fast text-to-speech.

## Prerequisites

Before running the companion, ensure you have the following installed on your system:

1.  **Python 3.8+**
2.  **Ollama:** [Download and install Ollama](https://ollama.com/)
    *   Once installed, you must pull the vision model:
        ```bash
        ollama pull llama3.2-vision
        ```
3.  **FFmpeg:** Required to play the generated audio (the script uses `ffplay`).
    *   **Ubuntu/Debian:** `sudo apt install ffmpeg`
    *   **macOS:** `brew install ffmpeg`
    *   **Windows:** Download from the [official site](https://ffmpeg.org/download.html) or use `winget install ffmpeg`.

## Installation

1.  Clone or download this repository.
2.  Navigate to the project directory:
    ```bash
    cd ai-companion
    ```
3.  (Optional but recommended) Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```
4.  Install the required Python packages:
    ```bash
    pip install -r requirements_free.txt
    ```
    *(Note: You may need to install system dependencies for `pyaudio` first, e.g., `sudo apt-get install portaudio19-dev` on Debian/Ubuntu).*

## Usage

1.  Make sure the **Ollama app is running** in the background.
2.  Run the main script:
    ```bash
    python main.py
    ```
3.  When prompted, enter a number to select your desired AI persona.
4.  The application will start listening. Speak into your microphone. 
5.  After you stop speaking, it will take a screenshot, process your voice and screen through Ollama, and reply back to you with voice!
6.  Press `Ctrl+C` in the terminal to exit.

## Architecture

*   **`main.py`**: The core script. Handles microphone input, screen capture, Ollama API calls, and TTS playback.
*   **`requirements_free.txt`**: Python dependencies required to run the project.

## Note on Privacy
Everything runs locally on your machine. Screen captures and voice data are sent only to your local Ollama instance and are not uploaded to the cloud (TTS does use Edge TTS which requires internet, but the core LLM reasoning is local).