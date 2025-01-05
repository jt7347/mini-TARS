from TARS_Servo_Abstractor import TARS_Servo_Abstractor
from TARS_Speech import TARS_Speech

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

    def handle_action(self, content):
        # handle action here
        if content == "step forward":
            tts = "Taking a step forward."
            print("TARS: ", tts)
            self.speech.tts_piper(tts)
            self.abstractor.stepForward()
        elif content == "turn left":
            tts = "Turning left."
            print("TARS: ", tts)
            self.speech.tts_piper(tts)
            self.abstractor.turnLeft()
        elif content == "turn right":
            tts = "Turning right."
            print("TARS: ", tts)
            self.speech.tts_piper(tts)
            self.abstractor.turnRight()
        else:
            tts = content # default if no command is recognized
            print("TARS: ", tts)
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
