import os
import queue
import pyaudio
import threading
import keyboard  # Install via: pip install keyboard
import time
from google.cloud import speech

# Set up Google credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "luminous-byway-448406-n6-79b7ef905ed7.json"

# Audio parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms chunks

# Queue for audio streaming
audio_queue = queue.Queue()
stop_flag = False  # Flag to stop transcription
final_transcript = ""

def audio_callback(in_data, frame_count, time_info, status):
    """Capture live audio and put it into the queue."""
    if stop_flag:
        return (None, pyaudio.paComplete)  # Stop recording
    audio_queue.put(in_data)
    return (None, pyaudio.paContinue)

def generate_audio_stream():
    """Yields audio data from the queue for streaming."""
    while not stop_flag:
        chunk = audio_queue.get()
        if chunk is None:
            break
        yield speech.StreamingRecognizeRequest(audio_content=chunk)

    # **Force final processing by sending silence**
    yield speech.StreamingRecognizeRequest(audio_content=b"\0" * 4000)
    time.sleep(1)  # Give time to finalize

def listen_print_loop(responses):
    """Processes streaming responses and ensures last sentences are saved."""
    global final_transcript
    last_transcript = ""

    with open("test.txt", "w", encoding="utf-8") as file:
        try:
            for response in responses:
                if stop_flag:  # Stop if "Q" is pressed
                    break
                for result in response.results:
                    transcript = result.alternatives[0].transcript.strip()

                    if result.is_final:
                        if not final_transcript.endswith(transcript):
                            print(transcript)
                            file.write(transcript + "\n")
                            final_transcript += " " + transcript
                        last_transcript = ""  # Clear interim buffer
                    else:
                        last_transcript = transcript  # Store interim text

        except Exception as e:
            print("Error:", e)
        finally:
            # **Ensure last pending transcript is saved**
            if last_transcript and last_transcript not in final_transcript:
                print("\n[Saving last part] ->", last_transcript)
                file.write(last_transcript + "\n")
                final_transcript += " " + last_transcript

def listen_for_quit():
    """Waits for user to press 'Q' to stop transcription."""
    global stop_flag
    keyboard.wait("q")  # Blocks execution until "Q" is pressed
    stop_flag = True
    print("\n🛑 Stopping transcription... ")
    time.sleep(2)  # Wait for final words to process

def main():
    global stop_flag
    client = speech.SpeechClient()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="ur-PK",
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,  # Allow partial text saving
        single_utterance=False
    )

    # Start background thread to listen for "Q"
    quit_thread = threading.Thread(target=listen_for_quit, daemon=True)
    quit_thread.start()

    # Initialize PyAudio for real-time input
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        stream_callback=audio_callback)

    print("🎤 Listening... Press 'Q' to stop.")

    # Start streaming recognition
    responses = client.streaming_recognize(streaming_config, generate_audio_stream())
    listen_print_loop(responses)

    # Cleanup
    stream.stop_stream()
    stream.close()
    audio.terminate()

if __name__ == "__main__":
    main()
