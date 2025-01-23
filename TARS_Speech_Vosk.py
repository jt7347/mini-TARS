import vosk
import pyaudio
import json
import time
import numpy as np
import subprocess
import re
from piper.voice import PiperVoice
from TARS_Ollama import TARS_Ollama
import sounddevice as sd

# Structure ~ essentially, always listening for an 'activation_keyword,' in this case maybe just "TARS"?
class TARS_Speech_Vosk:
    def __init__(self):
        self.timeout = 2  # time to wait before no phrase registered
        self.max_duration = 30  # max phrase duration recognition length
        self.calibrated = False
        self.rate = 16000
        self.chunk = 1024
        self.channels = 1
        self.noise_threshold = None # test value
        self.noise_buffer = 1500 # pad on top of average ambient threshold
        self.ollama = TARS_Ollama()
        # wakeword attributes
        self.active = True
        self.wakeword = ["TARS", "hey TARS"]
        self.last_active = time.time() - 20 # last active time, initialize to boot time - 10 seconds to force standby
        self.sleep_time = 20 # seconds
        self.pre_compute = json.load(open("character/pre_compute.json"))
        # Preload Piper process for faster TTS
        self.piper = PiperVoice.load("voice_models/TARS.onnx")
        
        # Initialize Vosk recognizer
        self.model = vosk.Model("vosk-model-small-en-us-0.15")
        self.recognizer = vosk.KaldiRecognizer(self.model, self.rate)

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
        # example (this is used to change lower case recognition to upper, but structure is the same)
        if "tars" in text:
            text = text.replace("tars", "TARS") # final case where Kaldi recognizes tars
        return text
    
    def command_reference(self, command):
        # Command needs to be fed into llm, and then converted to text
        if "step forward" in command:
            return "step forward"
        elif "turn left" in command:
            return "turn left"
        elif "turn right" in command:
            return "turn right"
        elif command == "play secret":
            return "(Playing secret)"
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
        return audio_data


    def listen_for_command(self):
        # add sleep timeout
        if self.active and ((time.time() - self.last_active) > self.sleep_time):
            print("TARS: (Standby mode...)")
            self.play_beep(400, 0.1, 44100, 0.6)
            # Dynamic recognizer --> (if in sleep mode, focus on discerning wakeword phrases)
            self.recognizer = vosk.KaldiRecognizer(self.model, self.rate, json.dumps([phrase.lower() for phrase in self.wakeword]))
            self.active = False

        # Record audio using the record_audio method
        audio_data = self.record_audio() # has a timeout of 2 seconds, duration of 30

        # Recognize the speech from the recorded audio
        try:
            if self.recognizer.AcceptWaveform(audio_data):
                result = json.loads(self.recognizer.Result())
                prompt = self.phonetic_match(result.get("text", "").lower())
                # return None if result is empty
                if prompt == "":
                    return
                # print(prompt)
                if self.active:
                    console = prompt.upper()
                    print("Input: ", console)
                    action = self.command_reference(prompt)
                    self.last_active = time.time() # update active timer
                    return action  # action can be nonetype also
                else:
                    if prompt in self.wakeword:
                        print("TARS: (Listening...)")
                        self.play_beep(1200, 0.1, 44100, 0.8)
                        self.tts_piper("listening...")
                        self.active = True
                        # Dynamic recognizer --> (when active, go back to full vocabulary)
                        self.recognizer = vosk.KaldiRecognizer(self.model, self.rate)
                        self.last_active = time.time()
                    return

        except Exception as e:
            print(f"Error with the speech recognition service: {e}")
            return
    
    def run_speech_module(self):
        if not self.calibrated:
            self.calibrate_microphone()
            self.calibrated = True
        prompt = self.listen_for_command()
        return prompt
    
    def tts_piper(self, tts):
        # print("TARS: (Generating audio...)")

        # Check for pre-computed audio
        if tts in self.pre_compute:
            subprocess.run(["aplay", "-r", "22050", "-f", "S16_LE", self.pre_compute[tts]])
            # reset last_active to account for speech synthesis time
            self.last_active = time.time()
            return

        # Simplified subprocess pipeline
        try:
            # Generate piper raw stream
            audio_stream = self.piper.synthesize_stream_raw(tts)
            
            # Create aplay subprocess
            aplay_process = subprocess.Popen(
                ["aplay", "-r", "22050", "-f", "S16_LE", "-t", "raw", "-"],
                stdin=subprocess.PIPE
            )

            # Feed audio stream into aplay process
            for chunk in audio_stream:
                aplay_process.stdin.write(chunk)
            # close stdin to signal input completion
            aplay_process.stdin.close()

            # Wait for aplay to finish
            aplay_process.wait()

            # reset last_active to account for speech synthesis time
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
    
    def play_beep(self, frequency, duration, sample_rate, volume):
        """
        Play a system beep sound.
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

def main():
    TARS = TARS_Speech_Vosk()
    while True:
        out = TARS.run_speech_module()
        # if out is not None:
        #     print(out)

if __name__ == "__main__":
    main()
