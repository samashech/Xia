import os
import time
import asyncio
import pyaudio
import pygame
import speech_recognition as sr
import edge_tts
import ollama

# Configure your AI Companion persona here
PERSONA = "You are a chaotic, funny, and slightly freaky AI companion. Keep your answers brief, punchy, and highly conversational. Do not use markdown or emojis, just plain text suitable for speech."
# The local Ollama model you want to use
MODEL_NAME = "llama3" 
# Edge-TTS voice (en-US-ChristopherNeural is a good standard male voice, en-US-AriaNeural for female)
VOICE = "en-US-ChristopherNeural"

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

def generate_response(prompt):
    print("Thinking...")
    try:
        response = ollama.chat(model=MODEL_NAME, messages=[
            {
                'role': 'system',
                'content': PERSONA,
            },
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        reply = response['message']['content']
        print(f"[AI]: {reply}")
        return reply
    except Exception as e:
        print(f"\n[Ollama Error]: Make sure Ollama is running locally and you have pulled the '{MODEL_NAME}' model. Error: {e}")
        return None

async def speak_text(text):
    print("Speaking...")
    try:
        # Generate audio file
        audio_file = "response.mp3"
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(audio_file)
        
        # Play the audio file using pygame
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        
        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
        # Clean up
        pygame.mixer.quit()
        os.remove(audio_file)
    except Exception as e:
        print(f"\n[TTS Error]: {e}")

def main():
    print("Initializing AI Companion (Free Stack)...")
    
    # Initialize speech recognition
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    # Pre-configure pygame mixer to reduce startup latency later
    pygame.mixer.init()

    print(f"\nSetup Complete! Ensure Ollama is running in the background.")
    print("Ready to talk. Press Ctrl+C to exit.\n")

    try:
        while True:
            # 1. Listen
            user_text = listen_audio(recognizer, microphone)
            
            if user_text:
                # 2. Think
                ai_reply = generate_response(user_text)
                
                if ai_reply:
                    # 3. Speak (Run the async function synchronously)
                    asyncio.run(speak_text(ai_reply))
                    
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nExiting AI Companion.")

if __name__ == "__main__":
    main()