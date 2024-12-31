from TARS_Servo_Abstractor import TARS_Servo_Abstractor
from TARS_Speech import TARS_Speech

# take keyboard inputs instead of bluetooth controller through SSH?

class TARS_Runner:
    def __init__(self):
        self.abstractor = TARS_Servo_Abstractor()
        self.controller = self.abstractor.controller # TARS_Servo_Abstractor already has a controller attribute
        self.speech = TARS_Speech()

        # port
        self.controller.pwm.set_pwm(3, 3, self.controller.portMain) # portMain = 610
        self.controller.pwm.set_pwm(4, 4, self.controller.portForearm) # portForearm = 570
        # self.controller.pwm.set_pwm(5, 5, self.controller.portHand) # portHand = 570, for hand extendor?
        
        # starboard
        self.controller.pwm.set_pwm(6, 6, self.controller.starMain) # starMain = 200
        self.controller.pwm.set_pwm(7, 7, self.controller.starForearm) # starForearm = 200
        # self.controller.pwm.set_pwm(8, 8, self.controller.starHand) # starHand = 240, for hand extendor?

        # self.toggle = True
        # self.pose = False
        
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
