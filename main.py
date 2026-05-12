import os
import time
import asyncio
import pyaudio
import speech_recognition as sr
import edge_tts
import ollama
import subprocess
import base64
import io
from PIL import ImageGrab

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
        "name": "Freaky Gamer (Like the Video)",
        "voice": "en-US-AriaNeural",
        "persona": "You are a highly chaotic, freaky, and completely unhinged AI gaming companion watching my screen. You constantly make weird, slightly inappropriate, or sarcastic comments about my gameplay and what you see. You are a biohazard yourself. Keep responses under 2 sentences. Be funny and disruptive. Talk directly to me. No markdown."
    }
}

# Use a vision model for screen context
MODEL_NAME = "llama3.2-vision"

# Global variables for selected character
CURRENT_PERSONA = ""
CURRENT_VOICE = ""

def capture_screen():
    print("Taking screenshot...")
    try:
        screen = ImageGrab.grab()
        buffered = io.BytesIO()
        # Compress the image a bit so the local vision model can process it faster
        screen.convert("RGB").save(buffered, format="JPEG", quality=50)
        img_bytes = buffered.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')
    except Exception as e:
        print(f"[Screen Capture Error]: {e}")
        return None

def listen_audio(recognizer, microphone):
    print("Listening...")
    with microphone as source:
        # Adjust for background noise quickly
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            text = recognizer.recognize_google(audio)
            print(f"\n[You]: {text}")
            return text
        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"\n[Error]: Speech Recognition API Error: {e}")
        except Exception as e:
            print(f"\n[Error]: {e}")
    return None

def generate_response(prompt, image_b64=None):
    print("Thinking...")
    messages = [
        {
            'role': 'system',
            'content': CURRENT_PERSONA,
        }
    ]
    
    user_message = {
        'role': 'user',
        'content': prompt,
    }
    
    if image_b64:
        user_message['images'] = [image_b64]
        
    messages.append(user_message)
    
    try:
        response = ollama.chat(model=MODEL_NAME, messages=messages)
        reply = response['message']['content']
        print(f"[AI]: {reply}")
        return reply
    except Exception as e:
        print(f"\n[Ollama Error]: Make sure Ollama is running and you have pulled '{MODEL_NAME}'. Run 'ollama run {MODEL_NAME}'. Error: {e}")
        return None

async def speak_text(text):
    print("Speaking...")
    try:
        # Generate audio file
        audio_file = "response.mp3"
        communicate = edge_tts.Communicate(text, CURRENT_VOICE)
        await communicate.save(audio_file)
        
        # Play the audio file using ffplay
        subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", audio_file])
        
        # Clean up
        os.remove(audio_file)
    except Exception as e:
        print(f"\n[TTS Error]: {e}")

def main():
    global CURRENT_PERSONA, CURRENT_VOICE
    
    print("=== AI Companion Setup ===")
    print("Choose your character:")
    for key, char in CHARACTERS.items():
        print(f"{key}. {char['name']}")
    
    choice = input("\nEnter number (1-4): ").strip()
    if choice not in CHARACTERS:
        print("Invalid choice, defaulting to 4 (Freaky Gamer).")
        choice = "4"
        
    selected_char = CHARACTERS[choice]
    CURRENT_PERSONA = selected_char["persona"]
    CURRENT_VOICE = selected_char["voice"]
    
    print(f"\nInitializing {selected_char['name']}...")
    
    # Initialize speech recognition
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print(f"\nSetup Complete! Ensure Ollama is running.")
    print(f"Make sure you run: ollama run {MODEL_NAME}")
    print("Ready to talk. Press Ctrl+C to exit.\n")

    try:
        while True:
            # 1. Listen
            user_text = listen_audio(recognizer, microphone)
            
            if user_text:
                # 2. See (Capture screen right after user speaks to see what they are talking about)
                image_b64 = capture_screen()
                
                # 3. Think
                ai_reply = generate_response(user_text, image_b64)
                
                if ai_reply:
                    # 4. Speak
                    asyncio.run(speak_text(ai_reply))
                    
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nExiting AI Companion.")

if __name__ == "__main__":
    main()