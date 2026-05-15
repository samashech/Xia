import os
import asyncio
import base64
import subprocess
import speech_recognition as sr
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import edge_tts
import ollama

app = FastAPI()

# Define characters (Persona + Voice)
CHARACTERS = {
    "1": {
        "name": "Freaky Goth",
        "voice": "en-US-AriaNeural",
        "persona": "You are a chaotic, sarcastic, and slightly freaky AI companion. Keep answers brief, punchy, and highly conversational. No markdown."
    },
    "2": {
        "name": "Sweet Helper",
        "voice": "en-US-JennyNeural",
        "persona": "You are a sweet, overly polite, and incredibly helpful AI assistant. You love to assist and are always cheerful. Keep answers brief and conversational. No markdown."
    },
    "3": {
        "name": "Posh British",
        "voice": "en-GB-SoniaNeural",
        "persona": "You are a posh, slightly condescending, but elegant British lady AI. You find humans amusing but assist them anyway. Keep answers brief. No markdown."
    },
    "4": {
        "name": "Freaky Gamer",
        "voice": "en-US-AriaNeural",
        "persona": "You are a highly chaotic, freaky, and completely unhinged AI gaming companion watching my screen. You constantly make weird, slightly inappropriate, or sarcastic comments. Keep responses under 2 sentences. Be funny and disruptive. Talk directly to me. No markdown."
    }
}

# Use a conversational text model
MODEL_NAME = "llama3.1"

# Initialize speech recognizer
recognizer = sr.Recognizer()

class ChatRequest(BaseModel):
    character_id: str
    text: str

@app.get("/api/characters")
def get_characters():
    return CHARACTERS

@app.post("/api/chat")
async def chat(request: ChatRequest):
    return await process_chat(request.character_id, request.text)

@app.post("/api/chat_audio")
async def chat_audio(character_id: str = Form(...), audio: UploadFile = File(...)):
    char = CHARACTERS.get(character_id)
    if not char:
        raise HTTPException(status_code=400, detail="Invalid character ID")
        
    input_file = f"temp_in_{id(audio)}.webm"
    wav_file = f"temp_out_{id(audio)}.wav"
    
    try:
        # Save uploaded file
        with open(input_file, "wb") as f:
            content = await audio.read()
            f.write(content)
            
        # Convert to WAV using ffmpeg
        subprocess.run(["ffmpeg", "-y", "-i", input_file, "-ar", "16000", "-ac", "1", wav_file], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                       
        # Transcribe
        with sr.AudioFile(wav_file) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            
    except sr.UnknownValueError:
        raise HTTPException(status_code=400, detail="Could not understand the audio. Please speak clearer.")
    except Exception as e:
        print(f"Transcription Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process audio.")
    finally:
        # Cleanup
        if os.path.exists(input_file): os.remove(input_file)
        if os.path.exists(wav_file): os.remove(wav_file)
        
    # Process the text as usual
    return await process_chat(character_id, text)

async def process_chat(character_id: str, text: str):
    char = CHARACTERS.get(character_id)
    if not char:
        raise HTTPException(status_code=400, detail="Invalid character ID")
        
    # 1. Think with Ollama
    messages = [
        {'role': 'system', 'content': char["persona"]},
        {'role': 'user', 'content': text}
    ]
    try:
        response = ollama.chat(model=MODEL_NAME, messages=messages)
        ai_reply = response['message']['content']
    except Exception as e:
        print(f"Ollama Error: {e}")
        raise HTTPException(status_code=500, detail=f"Ollama Error: Make sure {MODEL_NAME} is pulled and running.")
        
    # 2. Generate Audio with edge-tts
    audio_file = f"response_{id(text)}.mp3"
    try:
        communicate = edge_tts.Communicate(ai_reply, char["voice"])
        await communicate.save(audio_file)
        
        with open(audio_file, "rb") as f:
            audio_bytes = f.read()
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
    except Exception as e:
        print(f"TTS Error: {e}")
        raise HTTPException(status_code=500, detail="Text-to-speech generation failed.")
    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)
            
    return {"text": ai_reply, "audio_b64": audio_b64, "user_text": text}

# Mount static directory for the frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", "r") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    print("Starting AI Companion Web Server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)