'''Package for loading screens, animations, and console related functionalities'''
import os
import time
from dummy_class import DummyClass
from threading import Thread

# global variables
status = None

class Console:
    def __init__(self):
        self.fps = 2

    # Function to clear the terminal screen
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    # Function to read ASCII art from a file
    def load_ascii_art(self, file_path):
        with open(file_path, 'r') as file:
            # Read the content of the file and split it by the 'break' delimiter
            art_data = file.read().split('break')
            # Strip each piece of art to remove unnecessary newlines or spaces
            return [art.strip() for art in art_data]
    
    def bootup_animation(self):
        # Load ASCII art from the text file
        ascii_art_list = self.load_ascii_art('TARS_ASCII_ART.txt')

        # Main loop to cycle through the ASCII art
        while status is None:
            for art in ascii_art_list:
                self.clear_screen()
                print(art)
                time.sleep(1 / self.fps)  # Wait for 1/fps seconds

# Example usage:
if __name__ == "__main__":
    console = Console()
    # console.bootup_animation()
    thread = Thread(target=console.bootup_animation)
    thread.start()
    dummy = DummyClass()
    status = dummy.val
    thread.join()
    console.clear_screen()