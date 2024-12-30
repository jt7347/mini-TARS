import speech_recognition as sr
import pyaudio
import time
import numpy as np

# Structure ~ essentially, always listening for an 'activation_keyword,' in this case maybe just "TARS"?
class TARS_Speech:
    def __init__(self):
        self.timeout = 1  # time to wait before no phrase registered
        self.duration = 30  # max phrase duration recognition length
        self.recognizer = sr.Recognizer()  # init recognizer
        self.calibrated = False
        self.rate = 44100
        self.chunk = 1024
        self.channels = 1
        self.noise_threshold = None # test value

    def calibrate_microphone(self):
        # calibrate for ambient noise
        sample_num = 20 # check max amplitude 20 times then average and adjust noise threshold
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
            total += max_amplitude

        stream.stop_stream()
        stream.close()
        p.terminate()

        noise_threshold = total / sample_num

        self.noise_threshold = noise_threshold
        print(noise_threshold)

    
    def phonetic_match(self, text):
        # use this function to map any phonetically similar words, or unrecognized words (e.g. taurus -> TARS)
        if "taurus" in text:
            text = text.replace("taurus", "TARS")
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
            return command  # default to returning original value
        
    def record_audio(self):
        max_duration = self.duration
        timeout = self.timeout
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

            # Stop recording if no sound has been detected for 'timeout' seconds
            if time.time() - last_sound_time > timeout:
                break
            # Stop recording if max_duration is reached
            if time.time() - start_time > max_duration:
                break

        stream.stop_stream()
        stream.close()
        p.terminate()

        audio_data = b''.join(frames)
        audio = sr.AudioData(audio_data, self.rate, 2)

        return audio


    def listen_for_command(self):
        # Use the microphone for input
        print("Listening for command...")
        while True:
            # Record audio using the record_audio method
            audio = self.record_audio()

            # Recognize the speech from the recorded audio
            try:
                command = self.phonetic_match(self.recognizer.recognize_google(audio).lower())
                print(command)
                if "TARS" in command:
                    action = self.command_reference(command)
                    return action  # action can be nonetype

            except sr.UnknownValueError:
                # print("Sorry, didn't quite catch that. Come again?")
                continue
            except sr.RequestError as e:
                print(f"Error with the speech recognition service: {e}")
                continue
    
    def run_speech_module(self):
        if not self.calibrated:
            self.calibrate_microphone()
            self.calibrated = True
        prompt = self.listen_for_command()
        return prompt

def main():
    TARS = TARS_Speech()
    out = TARS.run_speech_module()
    print(out)

if __name__ == "__main__":
    main()
