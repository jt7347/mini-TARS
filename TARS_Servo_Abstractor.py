from TARS_Servo_Controller import TARS_Servo_Controller
import time

class TARS_Servo_Abstractor:
	def __init__(self):
		self.controller = TARS_Servo_Controller()

	def stepForward(self):
		self.controller.height_neutral_to_up()
		self.controller.torso_neutral_to_forwards()
		self.controller.torso_bump()
		self.controller.torso_return()

	def turnLeft(self):
		self.controller.neutral_to_down()
		self.controller.turn_left()
		self.controller.down_to_neutral()
		self.controller.neutral_from_left()

	def turnRight(self):
		self.controller.neutral_to_down()
		self.controller.turn_right()
		self.controller.down_to_neutral()
		self.controller.neutral_from_right()

def main():
	TARS = TARS_Servo_Abstractor()
	TARS.stepForward()
	time.sleep(1)
	TARS.turnLeft()
	time.sleep(1)
	TARS.turnRight
	time.sleep(1)

if __name__ == "__main__":
	main()
    