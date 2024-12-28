import speech_recognition as sr

# Structure ~ essentially, always listening for an 'activation_keyword,' in this case maybe just "TARS"?
class TARS_Speech:
    def __init__(self):
        self.timeout = 1 # time to wait before no phrase registered
        self.phrase_max = 5 # max phrase duration recognition length
        self.recognizer = sr.Recognizer() # init recognizer

    def calibrate_microphone(self):
        # calibrate for ambient noise
        with sr.Microphone() as source:
            print("Calibrating microphone... Please wait.")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)  # Optional: Adjust for ambient noise
            print("Done.")
    
    def phonetic_match(self, text):
        # use this function to map any phonetically similar words, or unrecognized words
        if "TAURUS" in text:
            text = text.replace("TAURUS", "TARS")
        
        return text

    def listen_for_command(self):
        # Use the microphone for input
        with sr.Microphone() as source:
            print("Listening for the activation keyword...")
            while True:
                try:
                    audio = self.recognizer.listen(source, 1, 5)
                    # Recognize the speech using Google Speech Recognition
                    command = self.phonetic_match(self.recognizer.recognize_google(audio).upper())
                    print(f"Recognized command: {command}")
                    if "TARS" in command: # check for "TARS," if yes then go to another fxn
                        print("TARS here, what can I do for you?")
                        # go to another function call
                        break

                    # Command needs to be fed into llm, and then converted to actual command

                except sr.WaitTimeoutError:
                    # # Timeout occurred, continue listening
                    # print("Listening timed out, waiting for new input...")
                    continue
                except sr.UnknownValueError:
                    # print("Could not understand the audio")
                    continue
                except sr.RequestError as e:
                    # print(f"Error with the speech recognition service: {e}")
                    continue

def main():
    speech_module = TARS_Speech()
    speech_module.calibrate_microphone()
    speech_module.listen_for_command()

if __name__ == "__main__":
    main()