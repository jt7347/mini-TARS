import speech_recognition as sr
import pyaudio
import time
import numpy as np
import subprocess
from TARS_Ollama import TARS_Ollama
import re

# Structure ~ essentially, always listening for an 'activation_keyword,' in this case maybe just "TARS"?
class TARS_Speech:
    def __init__(self):
        self.timeout = 2  # time to wait before no phrase registered
        self.max_duration = 30  # max phrase duration recognition length
        self.recognizer = sr.Recognizer()  # init recognizer
        self.calibrated = False
        self.rate = 44100
        self.chunk = 1024
        self.channels = 1
        self.noise_threshold = None # test value
        self.noise_buffer = 1500 # pad on top of average ambient threshold
        self.ollama = TARS_Ollama()
        # wakeword attributes
        self.active = True
        self.wakeword = "TARS"
        self.last_active = time.time() - 20 # last active time, initialize to boot time - 10 seconds to force standby
        self.sleep_time = 20 # seconds

    def calibrate_microphone(self):
        # calibrate for ambient noise
        sample_num = 100 # check max amplitude 100 times then average and adjust noise threshold
        total = 0
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk)
        frames = []
        for i in range(sample_num):
            data = stream.read(self.chunk)
            frames.append(data)  
            # Convert raw data to numpy array for amplitude check
            test_audio = np.frombuffer(data, dtype=np.int16)
            max_amplitude = np.max(np.abs(test_audio))  # Find maximum amplitude in the chunk
            total += float(max_amplitude)

        stream.stop_stream()
        stream.close()
        p.terminate()

        noise_threshold = total / sample_num
        # print("Noise Threshold: ", noise_threshold)

        self.noise_threshold = noise_threshold + self.noise_buffer

    
    def phonetic_match(self, text):
        # use this function to map any phonetically similar words, or unrecognized words (e.g. taurus -> TARS)
        if "taurus" in text:
            text = text.replace("taurus", "TARS")
        elif text == "cars":
            text = text.replace("cars", "TARS") # very niche case...hopefully it doesn't bite me in the ass
        return text
    
    def command_reference(self, command):
        # Command needs to be fed into llm, and then converted to text
        if "step forward" in command:
            return "step forward"
        elif "turn left" in command:
            return "turn left"
        elif "turn right" in command:
            return "turn right"
        else:
            answer = self.ollama.ask_question(command)
            return answer
        
    def record_audio(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk)
        frames = []
        start_time = time.time()  # Track the start time to enforce max_duration
        last_sound_time = time.time()  # Track the last time sound was detected
        while True:
            data = stream.read(self.chunk)
            frames.append(data)
            
            # Convert raw data to numpy array for amplitude check
            test_audio = np.frombuffer(data, dtype=np.int16)
            max_amplitude = np.max(np.abs(test_audio))  # Find maximum amplitude in the chunk
            # Check if the maximum amplitude exceeds the noise threshold
            if max_amplitude > self.noise_threshold:
                last_sound_time = time.time()  # Reset the timer when sound is detected
                # print("recording")

            # Stop recording if no sound has been detected for 'timeout' seconds
            if time.time() - last_sound_time > self.timeout:
                # print("No (more) audio detected")
                break
            # Stop recording if max_duration is reached
            if time.time() - start_time > self.max_duration:
                # print("Max prompt duration reached")
                break

        stream.stop_stream()
        stream.close()
        p.terminate()

        audio_data = b''.join(frames)
        audio = sr.AudioData(audio_data, self.rate, 2)

        return audio


    def listen_for_command(self):
        # add sleep timeout
        if self.active and ((time.time() - self.last_active) > self.sleep_time):
            print("TARS: (Standby mode...)")
            self.active = False

        # Record audio using the record_audio method
        audio = self.record_audio() # has a timeout of 2 seconds, duration of 30

        # Recognize the speech from the recorded audio
        try:
            prompt = self.phonetic_match(self.recognizer.recognize_google(audio).lower())
            if self.active:
                console = prompt.upper()
                print("Input: ", console)
                action = self.command_reference(prompt)
                self.last_active = time.time() # update active timer
                return action  # action can be nonetype also
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
        prompt = self.listen_for_command()
        return prompt
    
    def tts_piper(self, tts):
        # First process: echo 'text here'
        print("TARS: (Generating audio...)")
        
        echo_process = subprocess.Popen(
            ["echo", tts], stdout=subprocess.PIPE
        )

        # Second process: piper
        piper_process = subprocess.Popen(
            ["piper", "--model", "voice_models/TARS.onnx", "--output-raw"],
            stdin=echo_process.stdout,
            stdout=subprocess.PIPE
        )

        # Third process: aplay
        aplay_process = subprocess.Popen(
            ["aplay", "-r", "22050", "-f", "S16_LE", "-t", "raw", "-"],
            stdin=piper_process.stdout
        )

        # Wait for all processes to finish
        echo_process.stdout.close()
        piper_process.stdout.close()
        aplay_process.wait()
    
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
