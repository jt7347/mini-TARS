import sys, time

class Console:
    def __init__(self):
        self.text_speed = 0.03
        self.frame_rate = 0.1

    def print(self, string):
        for char in string:
            # these two lines prevent python from including a new line after every >    
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.03)
        sys.stdout.write('\n')

# animation = "|/-\\"
# idx = 0
# while True:
#     print(animation[idx % len(animation)], end="\r")
#     idx += 1
#     time.sleep(0.1)