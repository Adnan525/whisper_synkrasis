# ================================================================================================================
# NOTE: https://docs.python.org/3/library/wave.html
# Can't use sd.rec since it does not support indefinite recording
# NOTE: https://python-sounddevice.readthedocs.io/en/0.5.1/api/convenience-functions.html#sounddevice.rec
# Using sd.InputStream instead
# NOTE: https://python-sounddevice.readthedocs.io/en/0.5.1/api/streams.html#sounddevice.InputStream
# ================================================================================================================

import sounddevice as sd
import numpy as np
import wave
import threading
import psutil

def record_audio_indefinitely(filename: str, 
                              samplerate: int = 44100, 
                              channels: int = 1):
    print("Recording... Press Enter to stop.")
    
    frames = []
    is_recording = True

    def monitor_cpu():
        """Monitor CPU usage while recording."""
        nonlocal is_recording
        while is_recording:
            print(f"CPU Usage: {psutil.cpu_percent(interval=0.5)}%")
    

    def callback(indata, frame_count, time_info, status):
        frames.append(indata.copy())


    def stop_recording():
        nonlocal is_recording
        input()
        is_recording = False

    # Starting a separate thread to listen for enter key
    stop_thread = threading.Thread(target=stop_recording)
    # monitor_thread = threading.Thread(target=monitor_cpu, daemon=True) # to exit automatically when main thread exits
    stop_thread.start()
    # monitor_thread.start()

    with sd.InputStream(samplerate=samplerate, channels=channels, dtype='int16', callback=callback):
        while is_recording:
            # keep extending the recording
            # without sleep, the CPU usage will be high (tested on hcc4)
            sd.sleep(100)
            # continue

    stop_thread.join()
    print("Recording stopped. Saving to file...")

    # Save recorded audio to WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16-bit audio
        wf.setframerate(samplerate)
        wf.writeframes(b''.join(frame.tobytes() for frame in frames))

    print(f"Recording saved as {filename}")


if __name__ == "__main__":
    record_audio_indefinitely("recordings/output_sd.wav", channels=2)