import numpy as np
import sounddevice as sd

def play_beep(frequency, duration, sample_rate, volume):
    """
    Play a beep sound to indicate the system is listening.
    Parameters:
    - frequency (int): Frequency of the beep in Hz (e.g., 1000 for 1kHz).
    - duration (float): Duration of the beep in seconds.
    - sample_rate (int): Sample rate in Hz (default: 44100).
    - volume (float): Volume of the beep (0.0 to 1.0).
    """
    # Generate a sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = volume * np.sin(2 * np.pi * frequency * t)

    # Play the sine wave
    sd.play(wave, samplerate=sample_rate)
    sd.wait()  # Wait until the sound finishes playing


play_beep(400, 0.1, 44100, 0.6)
