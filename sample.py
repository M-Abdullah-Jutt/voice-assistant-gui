import pyaudio
import wave
import whisper
import requests
import datetime
import pyttsx3 
# from database import setup_database, store_interaction

# Load Whisper model
model = whisper.load_model("base")

# DeepSeek API configuration
DEEPSEEK_API_KEY = "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"  # Use environment variables in production
url = "https://openrouter.ai/api/v1/chat/completions"

def get_deepseek_response(prompt: str):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def extract_simple_response(response_json):
    return response_json['choices'][0]['message']['content']

def transcribe_audio(file_path):
    result = model.transcribe(file_path)
    return result["text"]

def record_audio():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    frames = []
    while True:
        data = stream.read(CHUNK)
        frames.append(data)

        if len(frames) > 10000:  # Example condition to stop recording
            break

    stream.stop_stream()
    stream.close()
    audio.terminate()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"output_{timestamp}.wav"

    with wave.open(output_filename, 'wb') as wavefile:
        wavefile.setnchannels(CHANNELS)
        wavefile.setsampwidth(audio.get_sample_size(FORMAT))
        wavefile.setframerate(RATE)
        wavefile.writeframes(b''.join(frames))

    return output_filename

def speak_text(text, rate=160, volume=1.0, voice_gender="male"):
    engine = pyttsx3.init()

    # Set rate
    engine.setProperty('rate', rate)
    
    # Set volume (0.0 to 1.0)
    engine.setProperty('volume', volume)

    # Set voice by gender
    voices = engine.getProperty('voices')
    for voice in voices:
        if voice_gender.lower() in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

    engine.say(text)
    engine.runAndWait()