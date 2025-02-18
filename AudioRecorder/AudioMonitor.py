# ===================================================================================================
# SoundDevice implementation
# Reference: https://python-sounddevice.readthedocs.io/en/0.5.1/api/streams.html#sounddevice.Stream
# Monitors audio input only.
# sd.query_devices() to get device info - 
# > 0 HDA Intel PCH: ALC3204 Analog (hw:0,0), ALSA (2 in, 0 out)
# < 1 HDA Intel PCH: DELL U2719D (hw:0,3), ALSA (0 in, 2 out)
#   2 HDA Intel PCH: DELL U2724D (hw:0,7), ALSA (0 in, 2 out)
#   3 HDA Intel PCH: HDMI 2 (hw:0,8), ALSA (0 in, 8 out)
#   4 HDA Intel PCH: HDMI 3 (hw:0,9), ALSA (0 in, 8 out)
#   5 WD19 Dock: USB Audio (hw:1,0), ALSA (2 in, 2 out)
#   6 WD19 Dock: USB Audio #1 (hw:1,1), ALSA (0 in, 2 out)
#   7 sysdefault, ALSA (128 in, 0 out)
#   8 hdmi, ALSA (0 in, 2 out)
# ===================================================================================================

import sounddevice as sd
import numpy as np
import time

class AudioMonitor:
    def __init__(self, 
                 chunk_threshold: int = 10,
                 silence_volume_threshold: int = 2,
                 silence_time_threshold: int = 2,
                 device: int = 0):
        self.recording_start = time.time()
        self.start_time = None
        self.silence_start_time = None
        self.silence_volume_threshold = silence_volume_threshold
        self.silence_time_threshold = silence_time_threshold
        self.chunk_threshold = chunk_threshold
        self.has_chunk_duration_threshold = False
        self.has_silence_threshold = False
        self.device = device
        self.samplerate = 44100 # No compression


    def monitor_audio(self, duration: int) -> None:
        print("Starting audio monitoring...")
        with sd.InputStream(callback=self.callback,
                      channels=2,
                      device=self.device,
                      samplerate=self.samplerate):
            sd.sleep(duration * 1000)


    def callback(self, 
                 indata: np.ndarray, 
                #  outdata: np.ndarray,
                 frames: int, 
                 time_info, 
                 status) -> None:
        """
        Callback function to monitor audio levels
        NOTE: https://python-sounddevice.readthedocs.io/en/0.5.1/api/streams.html#sounddevice.Stream
        NOTE: https://python-sounddevice.readthedocs.io/en/0.5.1/api/streams.html#sounddevice.InputStream
        """
        if self.start_time is None:
            self.start_time = time.time()
        
        print(f"Elapsed time: {time.time() - self.recording_start:.2f}s")
        
        volume_norm = np.linalg.norm(indata) * 10
        print(f"Volume: {'|' * int(volume_norm)}")

        # Chunk the audio if we can
        self._do_chunk()

        # Check for silence
        self._set_silence_threshold_flag(volume_norm)

        # Check if we can chunk the audio
        self._set_if_chunkable_flag()

        print("="*50)
            

    def _set_silence_threshold_flag(self, volume_norm: float) -> None:
        """
        Check if there has been continuous silence for the threshold duration
        """
        is_silence = volume_norm <= self.silence_volume_threshold # will be checked for each frame
        print(f"Volume value: {volume_norm} | Silence: {is_silence}")
        current_time = time.time()
        
        if is_silence:
            # Start tracking silence if we weren't already
            if self.silence_start_time is None:
                self.silence_start_time = current_time
            # Check if we've reached the silence duration threshold
            elif (current_time - self.silence_start_time) >= self.silence_time_threshold:
                print(f"Silence duration: {current_time - self.silence_start_time:.2f}s")
                self.has_silence_threshold = True
                print("Silence threshold reached!")
            else:
                print(f"Silence duration: {current_time - self.silence_start_time:.2f}s")
        else:
            # Reset silence tracking if we detect sound
            self.silence_start_time = None
    

    def _set_if_chunkable_flag(self) -> bool:
        """
        Check if the current duration is greater than the chunk threshold
        """
        # if self.start_time is None:
        #     self.start_time = time.time()
        current_duration = time.time() - self.start_time
        print(f"Duration: {current_duration:.2f}s")
        # Update chunkable status based on duration
        self.has_chunk_duration_threshold = current_duration >= self.chunk_threshold
        if self.has_chunk_duration_threshold:
            print("Recording is now chunkable!")

        
    def _do_chunk(self) -> None:
        """
        Simulate chunking the audio and reset the timers
        """
        print(f"SILENCE: {self.has_silence_threshold}")
        print(f"CHUNK: {self.has_chunk_duration_threshold}")
        print(f"Chunking flag: {self.has_chunk_duration_threshold and self.has_silence_threshold}")
        if self.has_chunk_duration_threshold and self.has_silence_threshold:
            print()
            print("#"*50)
            print("Chunking audio...")
            print("#"*50)
            print()
            self.start_time = time.time()
            self.has_silence_threshold = False
            self.has_chunk_duration_threshold = False


if __name__ == "__main__":
    monitor = AudioMonitor(silence_volume_threshold = 3)
    monitor.monitor_audio(22)