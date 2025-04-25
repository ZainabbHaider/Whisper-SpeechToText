import os
import numpy as np
import speech_recognition as sr
import whisper
import torch
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
from datetime import datetime, timedelta
from queue import Queue
from time import sleep
from sys import platform
import rnnoise_wrapper

class SpeechToTextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech-to-Text Transcriber with RNNoise")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        self.recording = False
        self.data_queue = Queue()
        self.transcription = ['']
        self.audio_model = None
        self.recorder = sr.Recognizer()
        self.source = None
        self.thread = None
        self.phrase_time = None
        self.rnnoise = rnnoise_wrapper.RNNoise()

        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.pack(fill=tk.X, pady=5)

        ttk.Label(control_frame, text="Model:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.model_var = tk.StringVar(value="medium")
        model_combo = ttk.Combobox(control_frame, textvariable=self.model_var, values=["tiny", "base", "small", "medium", "large"])
        model_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        self.english_var = tk.BooleanVar(value=True)
        english_check = ttk.Checkbutton(control_frame, text="Use English model", variable=self.english_var)
        english_check.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)

        ttk.Label(control_frame, text="Energy Threshold:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.energy_var = tk.IntVar(value=1000)
        energy_entry = ttk.Spinbox(control_frame, from_=0, to=5000, increment=100, textvariable=self.energy_var, width=10)
        energy_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(control_frame, text="Record Timeout (s):").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.rec_timeout_var = tk.DoubleVar(value=2.0)
        rec_timeout_entry = ttk.Spinbox(control_frame, from_=0.5, to=10.0, increment=0.5, textvariable=self.rec_timeout_var, width=5)
        rec_timeout_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)

        ttk.Label(control_frame, text="Phrase Timeout (s):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.phrase_timeout_var = tk.DoubleVar(value=3.0)
        phrase_timeout_entry = ttk.Spinbox(control_frame, from_=0.5, to=10.0, increment=0.5, textvariable=self.phrase_timeout_var, width=5)
        phrase_timeout_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(control_frame, text="Language Code:").grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        self.language_var = tk.StringVar(value="en")
        language_entry = ttk.Entry(control_frame, textvariable=self.language_var, width=5)
        language_entry.grid(row=2, column=3, sticky=tk.W, padx=5, pady=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)

        self.load_button = ttk.Button(button_frame, text="Load Model", command=self.load_model)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.start_button = ttk.Button(button_frame, text="Start Recording", command=self.toggle_recording, state=tk.DISABLED)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.save_button = ttk.Button(button_frame, text="Save Transcription", command=self.save_transcription, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_transcription)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.status_var = tk.StringVar(value="Ready to load model")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_label.pack(fill=tk.X, pady=5)

        ttk.Label(main_frame, text="Transcription:").pack(anchor=tk.W, pady=(10, 0))
        self.transcription_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=15)
        self.transcription_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def load_model(self):
        try:
            self.status_var.set("Loading model... Please wait.")
            self.root.update()
            model = self.model_var.get()
            if model != "large" and self.english_var.get():
                model += ".en"
            thread = threading.Thread(target=self._load_model_thread, args=(model,))
            thread.daemon = True
            thread.start()
        except Exception as e:
            self.status_var.set(f"Error loading model: {str(e)}")
            messagebox.showerror("Error", f"Failed to load model: {str(e)}")

    def _load_model_thread(self, model):
        try:
            self.audio_model = whisper.load_model(model)
            self.root.after(0, self._model_loaded)
        except Exception as e:
            self.root.after(0, lambda: self._model_load_error(str(e)))

    def _model_loaded(self):
        self.status_var.set(f"Model {self.model_var.get()} loaded successfully")
        self.start_button.config(state=tk.NORMAL)

    def _model_load_error(self, error_msg):
        self.status_var.set(f"Error loading model: {error_msg}")
        messagebox.showerror("Error", f"Failed to load model: {error_msg}")

    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        try:
            self.recorder.energy_threshold = self.energy_var.get()
            self.recorder.dynamic_energy_threshold = False
            self.source = sr.Microphone(sample_rate=16000)
            with self.source:
                self.recorder.adjust_for_ambient_noise(self.source)
            self.recorder.listen_in_background(self.source, self.record_callback,
                                               phrase_time_limit=self.rec_timeout_var.get())
            self.recording = True
            self.data_queue = Queue()
            self.phrase_time = None
            self.thread = threading.Thread(target=self.process_audio)
            self.thread.daemon = True
            self.thread.start()
            self.start_button.config(text="Stop Recording")
            self.load_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.NORMAL)
            self.status_var.set("Recording... Speak now")
        except Exception as e:
            self.status_var.set(f"Error starting recording: {str(e)}")
            messagebox.showerror("Error", f"Failed to start recording: {str(e)}")

    def record_callback(self, _, audio: sr.AudioData) -> None:
        data = audio.get_raw_data()
        self.data_queue.put(data)

    def process_audio(self):
        try:
            while self.recording:
                now = datetime.utcnow()
                if not self.data_queue.empty():
                    phrase_complete = False
                    if self.phrase_time and now - self.phrase_time > timedelta(seconds=self.phrase_timeout_var.get()):
                        phrase_complete = True
                    self.phrase_time = now

                    audio_data = b''.join(list(self.data_queue.queue))
                    self.data_queue.queue.clear()

                    # Convert to numpy and normalize
                    audio_np = np.frombuffer(audio_data, dtype=np.int16)

                    # Apply RNNoise denoising
                    denoised = np.array([self.rnnoise.filter(sample) for sample in audio_np], dtype=np.float32) / 32768.0

                    language = None if self.english_var.get() else self.language_var.get()
                    result = self.audio_model.transcribe(denoised, fp16=torch.cuda.is_available(), language=language)
                    text = result['text'].strip()

                    if phrase_complete:
                        self.transcription.append(text)
                    else:
                        self.transcription[-1] = text

                    self.root.after(0, self.update_transcription_text)
                else:
                    sleep(0.25)
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error in processing: {str(e)}"))

    def update_transcription_text(self):
        self.transcription_text.delete(1.0, tk.END)
        for line in self.transcription:
            if line:
                self.transcription_text.insert(tk.END, line + "\n\n")

    def stop_recording(self):
        self.recording = False
        if self.thread:
            self.thread.join(1.0)
        self.start_button.config(text="Start Recording")
        self.load_button.config(state=tk.NORMAL)
        self.status_var.set("Recording stopped")

    def save_transcription(self):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                     filetypes=[("Text files", ".txt"), ("All files", ".*")],
                                                     title="Save Transcription")
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    for line in self.transcription:
                        if line:
                            f.write(line + "\n")
                self.status_var.set(f"Transcription saved to {file_path}")
        except Exception as e:
            self.status_var.set(f"Error saving file: {str(e)}")
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def clear_transcription(self):
        self.transcription = ['']
        self.transcription_text.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechToTextApp(root)
    root.mainloop()
