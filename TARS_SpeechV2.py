import speech_recognition as sr
import pyaudio
import time
import numpy as np
import subprocess
from TARS_Ollama import TARS_Ollama
import re
import json

class TARS_Speech:
    def __init__(self):
        self.timeout = 2  # time to wait before no phrase registered
        self.max_duration = 30  # max phrase duration recognition length
        self.recognizer = sr.Recognizer()  # init recognizer
        self.calibrated = False
        self.rate = 44100
        self.chunk = 1024
        self.channels = 1
        self.noise_threshold = None
        self.noise_buffer = 1500
        self.ollama = TARS_Ollama()
        self.active = True
        self.wakeword = "TARS"
        self.last_active = time.time() - 20
        self.sleep_time = 20
        self.pre_compute = json.load(open("character/pre_compute.json"))
        
        # Preload Piper process for faster TTS
        self.piper_process = subprocess.Popen(
            ["piper", "--model", "voice_models/TARS.onnx", "--output-raw"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )

    def calibrate_microphone(self):
        sample_num = 100
        total = 0
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk)
        for _ in range(sample_num):
            data = stream.read(self.chunk)
            test_audio = np.frombuffer(data, dtype=np.int16)
            total += float(np.max(np.abs(test_audio)))

        stream.stop_stream()
        stream.close()
        p.terminate()
        self.noise_threshold = total / sample_num + self.noise_buffer

    def phonetic_match(self, text):
        if "taurus" in text:
            text = text.replace("taurus", "TARS")
        elif text == "cars":
            text = text.replace("cars", "TARS")
        return text

    def command_reference(self, command):
        if "step forward" in command:
            return "step forward"
        elif "turn left" in command:
            return "turn left"
        elif "turn right" in command:
            return "turn right"
        else:
            return self.ollama.ask_question(command)

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
            if np.max(np.abs(test_audio)) > self.noise_threshold:
                last_sound_time = time.time()
            if time.time() - last_sound_time > self.timeout or time.time() - start_time > self.max_duration:
                break

        stream.stop_stream()
        stream.close()
        p.terminate()

        audio_data = b''.join(frames)
        return sr.AudioData(audio_data, self.rate, 2)

    def listen_for_command(self):
        if self.active and time.time() - self.last_active > self.sleep_time:
            print("TARS: (Standby mode...)")
            self.active = False

        audio = self.record_audio()

        try:
            prompt = self.phonetic_match(self.recognizer.recognize_google(audio).lower())
            if self.active:
                print("Input: ", prompt.upper())
                action = self.command_reference(prompt)
                self.last_active = time.time()
                return action
            else:
                if prompt == self.wakeword:
                    print("TARS: (Listening...)")
                    self.active = True
                    self.last_active = time.time()
                return
        except sr.UnknownValueError:
            return
        except sr.RequestError as e:
            print(f"Error with the speech recognition service: {e}")
            return

    def run_speech_module(self):
        if not self.calibrated:
            self.calibrate_microphone()
            self.calibrated = True
        return self.listen_for_command()

    def tts_piper(self, tts):
        print("TARS: (Generating audio...)")

        # Check for pre-computed audio
        if tts in self.pre_compute:
            subprocess.run(["aplay", "-r", "22050", "-f", "S16_LE", self.pre_compute[tts]])
            self.last_active = time.time()
            return

        try:

            # Write text to the preloaded Piper process
            self.piper_process.stdin.write((tts + '\n').encode())
            self.piper_process.stdin.flush()

            # Continuously stream Piper's audio output to aplay
            aplay_process = subprocess.Popen(
                ["aplay", "-r", "22050", "-f", "S16_LE", "-t", "raw"],
                stdin=subprocess.PIPE
            )

            while True:
                # Read from Piper's output
                data = self.piper_process.stdout.read(1024)  # Read in chunks
                if data:
                    # Write to aplay's stdin
                    aplay_process.stdin.write(data)
                    aplay_process.stdin.flush()
                else:
                    # If no data, break (this could be replaced with a signal check)
                    break
            
            # Close aplay's input to signal EOF
            print("done with reading")
            aplay_process.stdin.close()
                    
            aplay_process.wait()
            print("done")

            # Reset last_active to account for speech synthesis time
            self.last_active = time.time()

        except Exception as e:
            print(f"Error during TTS generation: {e}")

    
    def remove_linebreak(self, tts):
        tts = tts.replace("\n", " ")
        # Replace multiple spaces with a single space
        tts = " ".join(tts.split())
        return tts.strip()

    def format(self, tts):
        # format for piper processing
        tts = re.sub(r'([.!?])\s*', r'\1\n', tts)
        tts = tts.strip().lower()
        return tts

def main():
    TARS = TARS_Speech()
    while True:
        out = TARS.run_speech_module()
        if out is not None:
            out = TARS.remove_linebreak(out)
            print(out)

if __name__ == "__main__":
    main()
