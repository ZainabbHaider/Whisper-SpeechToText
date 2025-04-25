import os
import queue
import pyaudio
import threading
import time
from google.cloud import speech
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk, messagebox
from content_filter import is_toxic_urdu

# Set Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "central-kit-457708-g7-51870db1a771.json"

# Audio parameters
RATE = 16000
CHUNK = int(RATE / 10)
audio_queue = queue.Queue()
stop_flag = False
final_transcript = ""

def show_intro_popup():
    popup = tk.Tk()
    popup.title("Welcome")
    popup.geometry("800x600")  # Adjusted height to fit design
    popup.configure(bg="#f8f9fa")

    intro_text = (
        """
        Welcome to our Real-Time Urdu Transcription Tool!

        We use an advanced AI model called Whisper to convert spoken Urdu into written text in real time.

        To evaluate this tool, we used:

        • Common Voice Urdu Dataset (Kaggle: 20,000 audio clips)
        • Urdu TTS Dataset (by Muhammad Saad Gondal on Hugging Face)

        To improve real-time performance in noisy environments, we’ve added noise reduction using RNNoise which you can find: .
        You can check our full implementation here: git.com/zainab

        Your privacy matters: None of your audio is recorded or stored.

        If you believe the transcription is incorrect or inappropriate, please report it to: hijabfatima87@gmail.com


        خوش آمدید! یہ ہے ہمارا ریئل ٹائم اردو ٹرانسکرپشن ٹول۔

        Whisper AI: استعمال کیا ہے جو آپ کی بولی گئی اردو کو فوری طور پر تحریر میں تبدیل کرتا ہے ہم نے ایک جدید 

        اس ماڈل کی جانچ کے لیے ہم نے درج ذیل ڈیٹا سیٹس استعمال کیے:

        • Common Voice Urdu Dataset (Kaggle: 20,000 آڈیو کلپس)
        • Urdu TTS Dataset (محمد سعد گوندل – Hugging Face)
        • RNNoise : شور والے ماحول میں بہتر کارکردگی کے لیے استعمال کرتے ہوئے آواز صاف کرنے کا فیچر شامل کیا ہے 

        مکمل کوڈ دیکھنے کے لیے یہ لنک ملاحظہ کریں: git.com/zainab

        آپ کی پرائیویسی ہمارے لیے اہم ہے: آپ کی کوئی آڈیو ریکارڈ یا محفوظ نہیں کی جاتی۔

        اگر آپ محسوس کریں کہ کوئی ٹرانسکرپشن نامناسب یا غلط ہے، تو براہ کرم ہمیں اس ای میل پر اطلاع دیں: hijabfatima87@gmail.com
        """
    )

    # Create a scrollable text area
    text_area = ScrolledText(popup, wrap=tk.WORD, font=("Segoe UI", 12), bg="#f8f9fa", borderwidth=0)
    text_area.insert(tk.END, intro_text)
    text_area.configure(state="disabled")
    text_area.pack(padx=20, pady=20, fill="both", expand=True)

    # Buttons at the bottom
    button_frame = tk.Frame(popup, bg="#f8f9fa")
    button_frame.pack(pady=10)

    def proceed():
        popup.destroy()
        launch_transcription_gui()

    def cancel():
        popup.destroy()
        exit()

    ttk.Button(button_frame, text="Proceed", command=proceed).pack(side="left", padx=10)
    ttk.Button(button_frame, text="Cancel", command=cancel).pack(side="left", padx=10)

    popup.mainloop()

def launch_transcription_gui():
    global root, text_display, stop_button, status_label

    # GUI setup
    root = tk.Tk()
    root.title("Urdu Live Transcription")
    root.geometry("900x600")
    root.configure(bg="#f8f9fa")

    style = ttk.Style()
    style.configure("TButton", font=("Segoe UI", 12), padding=6)

    header = tk.Label(root, text="🎤 Whisper Urdu Live Transcription", font=("Segoe UI", 18, "bold"), bg="#f8f9fa", fg="#343a40")
    header.pack(pady=(20, 10))

    text_frame = tk.Frame(root, bg="#f8f9fa")
    text_frame.pack(padx=20, pady=10, fill="both", expand=True)

    text_display = ScrolledText(text_frame, font=("Segoe UI", 14), wrap=tk.WORD, undo=True, padx=10, pady=10)
    text_display.pack(expand=True, fill="both")
    text_display.tag_configure("right", justify="right")
    text_display.configure(state="disabled")

    bottom_frame = tk.Frame(root, bg="#f8f9fa")
    bottom_frame.pack(fill="x", padx=20, pady=(0, 20))

    status_label = tk.Label(bottom_frame, text="Listening... Press 'Stop' to end.", font=("Segoe UI", 12), bg="#f8f9fa", fg="#495057")
    status_label.pack(side="left")

    def stop_transcription():
        global stop_flag
        stop_flag = True
        stop_button.config(state=tk.DISABLED)
        status_label.config(text="Stopping transcription...")

    stop_button = ttk.Button(bottom_frame, text="Stop", command=stop_transcription)
    stop_button.pack(side="right")

    # Start transcription in background
    threading.Thread(target=run_transcription, daemon=True).start()
    root.mainloop()

def update_gui(text_lines):
    text_display.configure(state="normal")
    text_display.delete("1.0", tk.END)
    for line in text_lines:
        text_display.insert(tk.END, line + "\n", "right")
    text_display.configure(state="disabled")

def audio_callback(in_data, frame_count, time_info, status):
    if stop_flag:
        return (None, pyaudio.paComplete)
    audio_queue.put(in_data)
    return (None, pyaudio.paContinue)

def generate_audio_stream():
    while not stop_flag:
        chunk = audio_queue.get()
        if chunk is None:
            break
        yield speech.StreamingRecognizeRequest(audio_content=chunk)
    yield speech.StreamingRecognizeRequest(audio_content=b"\0" * 4000)
    time.sleep(1)

def listen_print_loop(responses):
    global final_transcript
    phrase_time = None
    phrase_timeout = 2.0
    transcription = [""]
    last_written_line = ""

    with open("transcription_output.txt", "w", encoding="utf-8") as file:
        try:
            for response in responses:
                if stop_flag:
                    break

                now = time.time()
                if phrase_time and (now - phrase_time) > phrase_timeout:
                    current_line = transcription[-1].strip()
                    if current_line and current_line != last_written_line and current_line not in final_transcript:
                        final_transcript += " " + current_line
                        file.write(current_line + "\n")
                        file.flush()
                        last_written_line = current_line
                    transcription.append("")

                phrase_time = now

                for result in response.results:
                    transcript = result.alternatives[0].transcript.strip()
                    if result.is_final:
                        if transcript and transcript != last_written_line:
                            if not is_toxic_urdu(transcript):
                                transcription[-1] = transcript
                                final_transcript += " " + transcript
                                file.write(transcript + "\n")
                                file.flush()
                                last_written_line = transcript
                            else:
                                print(f"[⚠️ Filtered Toxic Line]: {transcript}")
                        transcription.append("")
                    else:
                        if not is_toxic_urdu(transcript):
                            transcription[-1] = transcript
                        else:
                            transcription[-1] = ""


                root.after(0, update_gui, transcription)

        except Exception as e:
            print("Error:", e)

def run_transcription():
    client = speech.SpeechClient()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="ur-PK",
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,
        single_utterance=False
    )

    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        stream_callback=audio_callback)

    responses = client.streaming_recognize(streaming_config, generate_audio_stream())
    listen_print_loop(responses)

    stream.stop_stream()
    stream.close()
    audio.terminate()

# 🔰 Launch the popup screen
show_intro_popup()
