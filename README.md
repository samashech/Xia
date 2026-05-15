# Xia - AI Web Companion

Xia is a local AI companion application that runs a modern web interface. It listens to your voice through your browser, processes your conversation locally using Ollama, and speaks back to you via fast Microsoft Edge TTS.

## Features

*   **Web Dashboard:** A clean, dark-themed HTML/JS frontend you can access in your browser.
*   **Browser Voice Recognition:** Uses the native Web Speech API (Chrome/Edge recommended) for instant, push-to-talk transcription.
*   **Local AI:** Uses `Ollama` with the `llama3.1` model for completely private, local processing.
*   **Multiple Personas:** Choose between different characters with unique personalities and voices (e.g., Freaky Goth, Sweet Helper, Posh British, Freaky Gamer).
*   **Fast TTS:** Uses `edge-tts` to stream audio responses back to the browser.

## Prerequisites

Before running the companion, ensure you have the following installed on your system:

1.  **Python 3.8+**
2.  **Ollama:** [Download and install Ollama](https://ollama.com/)
    *   Once installed, pull the conversational model:
        ```bash
        ollama pull llama3.1
        ```

## Installation process

1.  Clone or download this repository.
2.  Navigate to the project directory:
    ```bash
    cd ai-companion
    ```
3.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```
4.  Install the required Python packages:
    ```bash
    pip install -r requirements_free.txt
    ```

## Usage

1.  Make sure the **Ollama app is running** in the background.
2.  Start the FastAPI backend server:
    ```bash
    python main.py
    ```
    *(Alternatively: `uvicorn main:app --host 0.0.0.0 --port 8000`)*
3.  Open your web browser (Chrome or Edge recommended for microphone support) and navigate to:
    **http://localhost:8000**
4.  Select a character from the grid.
5.  Click and hold the **🎙️ Hold to Talk** button, speak your message, and release.
6.  The AI will process your message and speak back to you!

## Architecture

*   **`main.py`**: The FastAPI backend. Exposes API endpoints for characters and chat generation, and serves the static frontend.
*   **`static/`**: Contains the frontend SPA (Single Page Application):
    *   `index.html`: Layout and structure.
    *   `style.css`: Dark-themed modern styling.
    *   `app.js`: Client-side logic for microphone handling, UI state, and API requests.
*   **`requirements_free.txt`**: Python dependencies (FastAPI, Uvicorn, Ollama, Edge-TTS).

## Note on Privacy
All text processing and audio transcription run entirely locally on your machine. The text-to-speech generation uses Edge TTS, which requires an internet connection, but your raw voice recordings and the LLM's reasoning never leave your local environment.
