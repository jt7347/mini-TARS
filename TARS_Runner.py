from TARS_Servo_Abstractor import TARS_Servo_Abstractor
from TARS_Speech import TARS_Speech

# take keyboard inputs instead of bluetooth controller through SSH?

class TARS_Runner:
    def __init__(self):
        self.abstractor = TARS_Servo_Abstractor()
        self.controller = self.abstractor.controller # TARS_Servo_Abstractor already has a controller attribute
        self.speech = TARS_Speech()

        # Reset drive and center lift servos
        # self.controller.pwm.set_pwm(0, 0, self.controller.<VAL_HERE>) # VAL = ___
        # self.controller.pwm.set_pwm(1, 1, self.controller.<VAL_HERE>) # VAL = ___
        # self.controller.pwm.set_pwm(2, 2, self.controller.<VAL_HERE>) # VAL = ___
        
        # initialize current action
        self.queue = None

    def handle_action(self, prompt):
        # handle action here
        if prompt == "step forward":
            tts = "Roger. Taking a step forward."
            self.speech.tts_piper(tts)
            self.abstractor.stepForward()
        elif prompt == "turn left":
            tts = "Roger. Turning left."
            self.speech.tts_piper(tts)
            self.abstractor.turnLeft()
        elif prompt == "turn right":
            tts = "Roger. Turning right."
            self.speech.tts_piper(tts)
            self.abstractor.turnRight()
        else:
            tts = "Didn't quite get that. Come again?" # default if no command is recognized
            # tts = prompt
            # pass tts into ollama pipeline
            # get return
            # pass return into piper for speech synthesis
            # need to find a way to speed up speech synthesis...
            # or thread synthesis with chat streaming
            self.speech.tts_piper(tts)

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
