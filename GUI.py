import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import os
import datetime
import wave
from playsound import playsound
import pyaudio
import pyttsx3
import warnings
from sample import transcribe_audio, get_deepseek_response, speak_text
from database import setup_database, store_interaction
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")


# Global variables
is_recording = False
frames = []
stream = None
audio = None
output_filename = ""

def record_audio_thread():
    global is_recording, frames, stream, audio

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    frames.clear()
    while is_recording:
        try:
            data = stream.read(CHUNK)
            frames.append(data)
        except Exception as e:
            print(f"Recording error: {e}")
            break

def start_recording():
    global is_recording
    is_recording = True
    status_label.config(text="Recording...")
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    transcript_textbox.delete(1.0, tk.END)
    response_textbox.delete(1.0, tk.END)
    threading.Thread(target=record_audio_thread, daemon=True).start()

def stop_recording():
    global is_recording, stream, audio, output_filename
    is_recording = False
    stop_button.config(state=tk.DISABLED)
    status_label.config(text="Processing...")

    # Close audio
    try:
        stream.stop_stream()
        stream.close()
        audio.terminate()
    except Exception as e:
        print(f"Audio termination error: {e}")

    # Save audio file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"output_{timestamp}.wav"

    try:
        with wave.open(output_filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(frames))
    except Exception as e:
        messagebox.showerror("Error", f"Error saving audio: {e}")
        return

    # Process audio in separate thread
    threading.Thread(target=process_audio, args=(output_filename,), daemon=True).start()

def process_audio(file_path):
    try:
        # Transcribe
        transcript = transcribe_audio(file_path)
        transcript_textbox.insert(tk.END, transcript)

        response_textbox.insert(tk.END, "Assistant is thinking...\n")
        response_textbox.update()

        # Get response
        response_json = get_deepseek_response(transcript)
        reply = response_json['choices'][0]['message']['content'].split('---')[0].strip()

        response_textbox.insert(tk.END, reply)
        # Save to database
        store_interaction(transcript, reply)

        speak_text(reply)

    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        status_label.config(text="Idle")
        start_button.config(state=tk.NORMAL)

  # optional, if you want to display or log it


def build_gui():
    global transcript_textbox, response_textbox, status_label, start_button, stop_button

    window = tk.Tk()
    window.title("Voice Assistant")
    window.geometry("600x500")

    tk.Label(window, text="🎤 Voice Assistant", font=("Arial", 18, "bold")).pack(pady=10)

    start_button = tk.Button(window, text="Start Recording", bg="green", fg="white", font=("Arial", 12), command=start_recording)
    start_button.pack(pady=5)

    stop_button = tk.Button(window, text="Stop Recording", bg="red", fg="white", font=("Arial", 12), command=stop_recording)
    stop_button.pack(pady=5)
    stop_button.config(state=tk.DISABLED)

    status_label = tk.Label(window, text="Idle", font=("Arial", 12), fg="blue")
    status_label.pack()

    tk.Label(window, text="Transcription:", font=("Arial", 12, "bold")).pack(pady=(10, 0))
    transcript_textbox = scrolledtext.ScrolledText(window, height=5, width=70, wrap=tk.WORD)
    transcript_textbox.pack(padx=10)

    tk.Label(window, text="Assistant Response:", font=("Arial", 12, "bold")).pack(pady=(10, 0))
    response_textbox = scrolledtext.ScrolledText(window, height=7, width=70, wrap=tk.WORD)
    response_textbox.pack(padx=10)

    tk.Button(window, text="Exit", command=window.quit, bg="black", fg="white", font=("Arial", 12)).pack(pady=10)

    setup_database()
    window.mainloop()

if __name__ == "__main__":
    build_gui()
