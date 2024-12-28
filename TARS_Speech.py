import speech_recognition as sr

# Structure ~ essentially, always listening for an 'activation_keyword,' in this case maybe just "TARS"?
class TARS_Speech:
    def __init__(self):
        self.timeout = 5 # time to wait before no phrase registered
        self.duration = 30 # max phrase duration recognition length
        self.recognizer = sr.Recognizer() # init recognizer
        self.calibrated = False

    def calibrate_microphone(self):
        # calibrate for ambient noise
        with sr.Microphone() as source:
            print("Calibrating microphone... Please wait.")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)  # Optional: Adjust for ambient noise
            print("Done.")
    
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
            print("TARS here. You called?")

    def listen_for_command(self):
        # Use the microphone for input
        with sr.Microphone() as source:
            print("Listening for command...")
            while True:
                try:
                    audio = self.recognizer.listen(source, self.timeout, self.duration)
                    # Recognize the speech using Google Speech Recognition
                    command = self.phonetic_match(self.recognizer.recognize_google(audio).lower())
                    if "TARS" in command:
                        action = self.command_reference(command)
                        return action # action can be nonetype

                except sr.WaitTimeoutError:
                    # Add a timeout catch
                    continue
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