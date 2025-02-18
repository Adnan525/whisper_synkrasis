import sounddevice as sd

def print_audio_devices():
    """
    Print all audio devices with their IDs
    """
    devices = sd.query_devices()
    print("\nAvailable Audio Devices:")
    for i, device in enumerate(devices):
        print(f"[{i}] {device['name']}")
        print(f"    Max Input Channels: {device['max_input_channels']}")
        print(f"    Max Output Channels: {device['max_output_channels']}")
        print(f"    Default Sample Rate: {device['default_samplerate']}")
        # print(device)
        print()

if __name__ == "__main__":
    print_audio_devices()
    print("\nDefault input device:", sd.default.device[0])
    print("Default output device:", sd.default.device[1])