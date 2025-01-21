from TARS_Servo_Abstractor import TARS_Servo_Abstractor
from TARS_Speech import TARS_Speech
from threading import Thread
import console

# # global definitions
# load_stat = False

# def clear_screen():
#     os.system('cls' if os.name == 'nt' else 'clear')

# def bootup_animation():
#     with open('TARS_ASCII_ART.txt', 'r') as file:
#         # Read the content of the file and split it by the 'break' delimiter
#         art_data = file.read().split('break')
#         # Strip each piece of art to remove unnecessary newlines or spaces
#         ascii_art_list = [art.strip() for art in art_data]

#         # Main loop to cycle through the ASCII art
#         while not load_stat:
#             for art in ascii_art_list:
#                 clear_screen()
#                 print(art, end="")
#                 time.sleep(1 / 2.5)  # FPS = 2.5
#         clear_screen()
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
            console = tts
            self.speech.tts_piper(tts.lower())
            print("TARS: ", console)
            self.abstractor.stepForward()
        elif content == "turn left":
            tts = "Turning left."
            console = tts
            self.speech.tts_piper(tts.lower())
            print("TARS: ", console)
            self.abstractor.turnLeft()
        elif content == "turn right":
            tts = "Turning right."
            console = tts
            self.speech.tts_piper(tts.lower())
            print("TARS: ", console)
            self.abstractor.turnRight()
        else:
            tts = content # default if no command is recognized
            tts = self.speech.remove_linebreak(tts)
            console = tts
            tts = self.speech.format(tts)
            self.speech.tts_piper(tts)
            print("TARS: ", console)

    def start(self):
        while True:
            self.queue = self.speech.run_speech_module()
            if self.queue is not None:
                self.handle_action(self.queue)

def main():
    global load_stat
    main_console = console.Console()
    thread = Thread(target=main_console.bootup_animation)
    thread.start()
    TARS = TARS_Runner()
    load_stat = True
    thread.join()
    main_console.clear_screen()
    TARS.start()

if __name__ == "__main__":
    main()
