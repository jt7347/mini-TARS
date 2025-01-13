from TARS_Servo_Abstractor import TARS_Servo_Abstractor
from TARS_Speech import TARS_Speech
from console_module import Console
from threading import Thread

class TARS_Runner:
    def __init__(self):
        self.abstractor = TARS_Servo_Abstractor()
        self.controller = self.abstractor.controller # TARS_Servo_Abstractor already has a controller attribute
        self.speech = TARS_Speech()
        self.console_module = Console()

        # Reset drive and center lift servos
        # self.controller.pwm.set_pwm(0, 0, self.controller.<VAL_HERE>) # VAL = ___
        # self.controller.pwm.set_pwm(1, 1, self.controller.<VAL_HERE>) # VAL = ___
        # self.controller.pwm.set_pwm(2, 2, self.controller.<VAL_HERE>) # VAL = ___
        
        # initialize current action
        self.queue = None

    def handle_action(self, content):
        # handle action here
        if content == "step forward":
            tts = "Taking a step forward."
            console = tts
            audio_thread = Thread(target=self.speech.tts_piper, args=(tts.lower(), ))
            text_thread = Thread(target=self.console_module.print, args=(("TARS: ", console), ))
            # Start both threads
            audio_thread.start()
            text_thread.start()
            # Control action
            self.abstractor.stepForward()
        elif content == "turn left":
            tts = "Turning left."
            console = tts
            audio_thread = Thread(target=self.speech.tts_piper, args=(tts.lower(), ))
            text_thread = Thread(target=self.console_module.print, args=(("TARS: ", console), ))
            # Start both threads
            audio_thread.start()
            text_thread.start()
            # Control action
            self.abstractor.turnLeft()
        elif content == "turn right":
            tts = "Turning right."
            console = tts
            audio_thread = Thread(target=self.speech.tts_piper, args=(tts.lower(), ))
            text_thread = Thread(target=self.console_module.print, args=(("TARS: ", console), ))
            # Start both threads
            audio_thread.start()
            text_thread.start()
            # Control action
            self.abstractor.turnRight()
        else:
            tts = content # default if no command is recognized
            tts = self.speech.remove_linebreak(tts)
            console = tts
            tts = self.speech.format(tts)
            audio_thread = Thread(target=self.speech.tts_piper, args=(tts, ))
            text_thread = Thread(target=self.console_module.print, args=(("TARS: ", console), ))
            # Start both threads
            audio_thread.start()
            text_thread.start()

    def start(self):
        while True:
            self.queue = self.speech.run_speech_module()
            if self.queue is not None:
                self.handle_action(self.queue)

def main():
    TARS = TARS_Runner()
    TARS.start()

if __name__ == "__main__":
    main()
