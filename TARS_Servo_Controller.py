import time
import Adafruit_PCA9685
from threading import Thread

class TARS_Servo_Controller:
    def __init__(self):
        self.pwm = Adafruit_PCA9685.PCA9685(busnum=1)

        # Set frequency to 60hz, good for servos.
        self.pwm.set_pwm_freq(60)

        # Center Lift Servo (0) Values
        self.upHeight = 205
        self.neutralHeight = 275
        self.downHeight = 450

        # Port Drive Servo (1) Values
        self.forwardPort = 440
        self.neutralPort = 375
        self.backPort = 330

        # Starboard Drive Servo (2) Values
        self.forwardStarboard = 292
        self.neutralStarboard = 357
        self.backStarboard = 402

    # moves the torso from a neutral position upwards, allowing the torso to pivot forwards or backwards
    def height_neutral_to_up(self):
        height = self.neutralHeight
        print('setting center servo (0) Neutral --> Up position')
        while (height > self.upHeight):
            height = height - 1
            self.pwm.set_pwm(0, 0, height)
            time.sleep(0.001)
        print('center servo (0) set to: Up position\n ')

    # rotates the torso outwards, enough so that when TARS pivots and lands, the bottom of the torso is 
    # flush with the ground. Making the torso flush with the ground is an intentional improvement from
    # previous programs, where TARS would land and then slide a little on smooth surfaces, which while
    # allowing for a simple walking program, inhibited TARS' ability to walk on surfaces with different 
    # coefficients of friction
    def torso_neutral_to_forwards(self):
        port = self.neutralPort
        starboard = self.neutralStarboard
        print('setting port and starboard servos (1)(2) Neutral --> Forward')
        while (port < self.forwardPort):
            port = port + 1
            starboard = starboard - 1
            self.pwm.set_pwm(1, 1, port)
            self.pwm.set_pwm(2, 2, starboard)
            time.sleep(0.0001)
        print('port and starboard servos (1)(2) set to: Forward position\n ')

    def torso_neutral_to_backwards(self):
        port = self.neutralPort
        starboard = self.neutralStarboard
        print('setting port and starboard servos (1)(2) Neutral --> Forward')
        while (port > self.backPort):
            port = port - 1
            starboard = starboard + 1
            self.pwm.set_pwm(1, 1, port)
            self.pwm.set_pwm(2, 2, starboard)
            time.sleep(0.0001)
        print('port and starboard servos (1)(2) set to: Forward position\n ')

    # rapidly shifts the torso height from UP --> DOWN and then returns --> UP, which should cause TARS 
    # to pivot and land on it's torso
    def torso_bump(self):
        height = self.upHeight
        print('performing a torso bump\nsetting center servo (0) Up --> Down position FAST')
        while (height < self.downHeight):
            height = height + 2
            self.pwm.set_pwm(0, 0, height)
            time.sleep(0.000001)
        print('setting center servo (0) Down --> Up position FAST')
        while (height > self.upHeight):
            height = height - 1
            self.pwm.set_pwm(0, 0, height)
            time.sleep(0.0001)
        print('center servo (0) returned to Up position\n')
        
    # returns the torso's vertical height and rotation to centered values from up height and forward 
    # rotation. Activates two external functions so movement in both axes can occur in parallel.
    def torso_return(self):
        t1 = Thread(target = self.torso_return_rotation)
        t2 = Thread(target = self.torso_return_vertical)
        
        t1.start()
        t2.start()

    # returns torso's rotation to neutral from forward
    def torso_return_rotation(self):
        port = self.forwardPort
        starboard = self.forwardStarboard
        print('setting port and starboard servos (1)(2) Forward --> Neutral position')
        while (port > self.neutralPort):
            port = port - 1
            starboard = starboard + 1
            self.pwm.set_pwm(1, 1, port)
            self.pwm.set_pwm(2, 2, starboard)
            time.sleep(0.005)
        print('port and starboard servos (1)(2) set to: Neutral position\n ')

    # returns torso's vertical to neutral from up	
    def torso_return_vertical(self):
        height = self.upHeight
        print('setting center servo (0) Up --> Down position')
        # moving the torso down to create clearance for the rotation of the legs
        while (height < self.downHeight):
            height = height + 1
            self.pwm.set_pwm(0, 0, height)
            time.sleep(0.00005)
        # moving the torso up from down to neutral
        #time.sleep(.2)
        while (height > self.neutralHeight):
            height = height - 1
            self.pwm.set_pwm(0, 0, height)
            time.sleep(0.00001)
        print('center servo (0) set to: Neutral position\n ')

    def torso_return2(self):
        t1 = Thread(target = self.torso_return_rotation2)
        t2 = Thread(target = self.torso_return_vertical2)
        
        t1.start()
        t2.start()

    # returns torso's rotation to neutral from forward
    def torso_return_rotation2(self):
        port = self.backPort
        starboard = self.backStarboard
        print('setting port and starboard servos (1)(2) Forward --> Neutral position')
        while (port < self.neutralPort):
            port = port + 1
            starboard = starboard - 1
            self.pwm.set_pwm(1, 1, port)
            self.pwm.set_pwm(2, 2, starboard)
            time.sleep(0.01)
        print('port and starboard servos (1)(2) set to: Neutral position\n ')

    # returns torso's vertical to neutral from up	
    def torso_return_vertical2(self):
        height = self.upHeight
        print('setting center servo (0) Up --> Down position')
        # moving the torso down to create clearance for the rotation of the legs
        while (height < self.downHeight):
            height = height + 1
            self.pwm.set_pwm(0, 0, height)
            time.sleep(0.001)
        # moving the torso up from down to neutral
        time.sleep(.25)
        while (height > self.neutralHeight):
            height = height - 1
            self.pwm.set_pwm(0, 0, height)
            time.sleep(0.001)
        print('center servo (0) set to: Neutral position\n ')


    # moves the torso from neutral position to down
    def neutral_to_down(self):
        height = self.neutralHeight
        print('setting center servo (0) Neutral --> Down position')
        while (height < self.downHeight):
            height = height + 1
            self.pwm.set_pwm(0, 0, height)
            time.sleep(0.001)
            
    def down_to_up(self):
        height = self.downHeight
        print('setting center servo (0) Down --> Neutral position')
        while (height > self.upHeight):
            height = height - 1
            self.pwm.set_pwm(0, 0, height)
            time.sleep(0.001)

    def down_to_neutral(self):
        height = self.downHeight
        print('setting center servo (0) Down --> Neutral position')
        while (height > self.neutralHeight):
            height = height - 1
            self.pwm.set_pwm(0, 0, height)
            time.sleep(0.001)

    def neutral_to_down(self):
        height = self.neutralHeight
        print('setting center servo (0) Down --> Neutral position')
        while (height < self.downHeight):
            height = height + 1
            self.pwm.set_pwm(0, 0, height)
            time.sleep(0.001)


    def turn_right(self):
        port = self.neutralPort
        starboard = self.neutralStarboard
        while (port < self.forwardPort):
            port = port + 1
            starboard = starboard + 1
            self.pwm.set_pwm(1, 1, port)
            self.pwm.set_pwm(2, 2, starboard)
            time.sleep(0.001)
            
    def turn_left(self):
        port = self.neutralPort
        starboard = self.neutralStarboard
        while (port > self.backPort):
            port = port - 1
            starboard = starboard - 1
            self.pwm.set_pwm(1, 1, port)
            self.pwm.set_pwm(2, 2, starboard)
            time.sleep(0.001)
            
    def neutral_from_right(self):
        port = self.forwardPort
        starboard = self.backStarboard
        while (port > self.neutralPort):
            port = port - 1
            starboard = starboard - 1
            self.pwm.set_pwm(1, 1, port)
            self.pwm.set_pwm(2, 2, starboard)
            time.sleep(0.005)
        self.pwm.set_pwm(1, 1, self.neutralPort)
        self.pwm.set_pwm(2, 2, self.neutralStarboard)
            
    def neutral_from_left(self):
        port = self.backPort
        starboard = self.forwardStarboard
        while (port < self.neutralPort):
            port = port + 1
            starboard = starboard + 1
            self.pwm.set_pwm(1, 1, port)
            self.pwm.set_pwm(2, 2, starboard)
            time.sleep(0.005)
        self.pwm.set_pwm(1, 1, self.neutralPort)
        self.pwm.set_pwm(2, 2, self.neutralStarboard)