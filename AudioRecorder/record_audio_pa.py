# ==========================================================================================================
# DO NOT USE THIS, HAD BUFFER OVERFLOW ISSUES
# Can record but large chunks will be missing
# Reduce chunk size and test with exception_on_overflow=False
# ==========================================================================================================

import pyaudio
import wave
import psutil
import threading
import time
import numpy as np

recording = True

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
# NOTE: https://stackoverflow.com/questions/10733903/pyaudio-input-overflowed/13774711
# NOTE: https://stackoverflow.com/questions/35970282/what-are-chunks-samples-and-frames-when-using-pyaudio
CHUNK = 16384  # Buffer size


def record_audio(filename: str):
    """Record audio indefinitely until Enter is pressed."""
    global recording

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, 
                    channels=CHANNELS,
                    rate=RATE, 
                    input=True, 
                    frames_per_buffer=CHUNK*16)

    print("Recording... Press Enter to stop.")

    # Thread to stop recording on Enter key press
    def stop():
        global recording
        input()
        recording = False

    threading.Thread(target=stop, daemon=True).start()

    frames = []
    
    while recording:
        data = stream.read(CHUNK, 
                           exception_on_overflow=False)
        frames.append(data)
        # time.sleep(0.1)

    print("Recording stopped.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recording to a WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"Recording saved as {filename}")

if __name__ == "__main__":
    record_audio("recordings/output_pa.wav")
