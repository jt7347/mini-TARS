from vosk import Model, KaldiRecognizer
import pyaudio
import time
import numpy as np
import subprocess
import json

class TARS_Speech:
    def __init__(self):
        self.timeout = 2  # Time to wait before no phrase is registered
        self.max_duration = 30  # Max phrase duration recognition length
        self.rate = 16000  # Vosk model requires 16kHz audio
        self.chunk = 1024
        self.channels = 1
        self.noise_threshold = None
        self.noise_buffer = 1500
        self.active = True
        self.wakeword = "TARS"
        self.last_active = time.time() - 20
        self.sleep_time = 20
        self.pre_compute = json.load(open("character/pre_compute.json"))
        self.model = Model("vosk-model-small-en-us-0.15")  # Ensure you download a Vosk model and specify its path
        self.recognizer = KaldiRecognizer(self.model, self.rate)

    def calibrate_microphone(self):
        sample_num = 100
        total = 0
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk)
        for _ in range(sample_num):
            data = stream.read(self.chunk)
            test_audio = np.frombuffer(data, dtype=np.int16)
            max_amplitude = np.max(np.abs(test_audio))
            total += float(max_amplitude)

        stream.stop_stream()
        stream.close()
        p.terminate()

        self.noise_threshold = total / sample_num + self.noise_buffer

    def phonetic_match(self, text):
        if "taurus" in text:
            text = text.replace("taurus", "TARS")
        elif "cars" in text:
            text = text.replace("cars", "TARS")
        return text

    def record_audio(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk)
        frames = []
        start_time = time.time()
        last_sound_time = time.time()

        while True:
            data = stream.read(self.chunk)
            frames.append(data)
            test_audio = np.frombuffer(data, dtype=np.int16)
            max_amplitude = np.max(np.abs(test_audio))

            if max_amplitude > self.noise_threshold:
                print("recording")
                last_sound_time = time.time()

            if time.time() - last_sound_time > self.timeout or time.time() - start_time > self.max_duration:
                print("no more audio heard")
                break

        stream.stop_stream()
        stream.close()
        p.terminate()
        return b"".join(frames)

    def listen_for_command(self):
        if self.active and (time.time() - self.last_active > self.sleep_time):
            print("TARS: (Standby mode...)")
            self.active = False

        audio_data = self.record_audio()

        if self.recognizer.AcceptWaveform(audio_data):
            result = json.loads(self.recognizer.Result())
            text = result.get("text", "").lower()
            text = self.phonetic_match(text)

            if True:
                print("Input:", text.upper())
                self.last_active = time.time()
                return text
            elif text == self.wakeword:
                print("TARS: (Listening...)")
                self.active = True
                self.last_active = time.time()
                return None

    def run_speech_module(self):
        if not self.noise_threshold:
            self.calibrate_microphone()
        return self.listen_for_command()

def main():
    TARS = TARS_Speech()
    while True:
        out = TARS.run_speech_module()
        if out is not None:
            print("Recognized Command:", out)

if __name__ == "__main__":
    main()
