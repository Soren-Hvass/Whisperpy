import tkinter as tk
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import threading
import requests
import json
import openai  # Added the import for openai
import keyboard
import pyperclip  # Added the import for pyperclip
import os  # Added the import for os

class GlobalListener:
    def __init__(self, callback):
        self.hotkey = 'ctrl+shift+a'
        self.callback = callback

    def start_listening(self):
        keyboard.add_hotkey(self.hotkey, self.callback)

    def change_hotkey(self, new_hotkey):
        keyboard.remove_hotkey(self.hotkey)
        self.hotkey = new_hotkey
        keyboard.add_hotkey(self.hotkey, self.callback)

class Recorder:
    def __init__(self):
        self.recording = False
        self.fs = 44100  # Sample rate
        self.audio = []

    def callback(self, indata, frames, time, status):
        if self.recording:
            self.audio.append(indata.copy())

    def start_recording(self):
        self.recording = True
        self.audio = []
        self.stream = sd.InputStream(callback=self.callback, channels=2, samplerate=self.fs)
        self.stream.start()

    def stop_recording(self):
        self.recording = False
        self.stream.stop()
        self.stream.close()
        if self.audio:  # Check if self.audio is not empty
            self.audio = np.concatenate(self.audio, axis=0)
            wav.write('output.wav', self.fs, self.audio)  # Save as WAV file

class WhisperAPI: 
    def __init__(self):
        try:
            with open('config.json') as config_file:
                data = json.load(config_file)
            openai.api_key = data['api_key']
        except FileNotFoundError:
            openai.api_key = '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'  # Replace 'your_static_key_here' with your static key

    def transcribe(self, audio_file):
        audio_file= open(audio_file, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript
recorder = Recorder()
whisper = WhisperAPI()

def on_button_press(event):
    threading.Thread(target=recorder.start_recording).start()

def on_button_release(event):
    recorder.stop_recording()

def on_button2_click(event):
    threading.Thread(target=transcribe_and_insert).start()

def transcribe_and_insert():
    transcription = whisper.transcribe('output.wav')
    transcription_text = transcription.text  # Extract the transcription text
    text_output.delete('1.0', tk.END)  # Clear the text output field
    text_output.insert(tk.END, "'" + transcription_text + "' - copied to clipboard\n ")
    pyperclip.copy(transcription_text)  # Copy the transcription text to the clipboardd the line to copy the transcription to the clipboard

def save_api_key():
    # Here you can write the code to save the API key
    api_key = api_key_input.get()
    print(f"API Key: {api_key}")  # This is just an example, replace with your own logic
def on_hotkey_press():
    print('Hotkey pressed!')
listener = GlobalListener(on_hotkey_press)
listener.start_listening()
root = tk.Tk()
root.title("WhisperWriter")  # Set a fitting title
frame = tk.Frame(root)
frame.grid()
button1 = tk.Button(frame, text='Record', width=40, height=12, padx=15, pady=15)
button1.grid(row=0, column=0)
button1.bind('<ButtonPress-1>', on_button_press)
button1.bind('<ButtonRelease-1>', on_button_release)

button2 = tk.Button(frame, text='Send to AI translator', width=40, height=12, padx=15, pady=15)
button2.grid(row=0, column=1)
button2.bind('<Button-1>', on_button2_click)

main_frame = tk.Frame(root)
main_frame.grid()

output_frame = tk.LabelFrame(main_frame, text="Output file", padx=5, pady=5)
output_frame.grid(row=0, column=0)

transcribe_frame = tk.LabelFrame(main_frame, text="Transcribe KeyBind", padx=5, pady=5)
transcribe_frame.grid(row=0, column=1)

api_key_frame = tk.LabelFrame(main_frame, text="API KEY", padx=5, pady=5)
api_key_frame.grid(row=0, column=2)

output_filename = tk.StringVar()
output_filename.set('output.wav')
output_label = tk.Label(output_frame, textvariable=output_filename, state='disabled')
output_label.grid()

transcribe_button_field = tk.StringVar()
transcribe_button_field.set("No hotkey selected")
transcribe_button_label = tk.Label(transcribe_frame, textvariable=transcribe_button_field, state='disabled')
transcribe_button_label.grid()

api_key_input = tk.Entry(api_key_frame)
api_key_input.grid()

save_button = tk.Button(api_key_frame, text='Save', command=save_api_key)
save_button.grid()

# New text output field
text_output = tk.Text(root, height=16)
text_output.grid()
text_output.insert(tk.END, "Press and hold the record button to record for transcription")

root.lift()  # Added the line to make the program window focused on launch
root.attributes('-topmost',True)  # Added the line to keep the program window always on top
root.after_idle(root.attributes,'-topmost',False)  # Added the line to remove the always on top attribute after the window is launched

root.mainloop() # YOLO SLAGGING