import os
import time

# Function to clear the terminal screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Function to read ASCII art from a file
def load_ascii_art(file_path):
    with open(file_path, 'r') as file:
        # Read the content of the file and split it by the 'break' delimiter
        art_data = file.read().split('break')
        # Strip each piece of art to remove unnecessary newlines or spaces
        return [art.strip() for art in art_data]

# Load ASCII art from the text file
ascii_art_list = load_ascii_art('TARS_ASCII_ART.txt')

# Main loop to cycle through the ASCII art
while True:
    for art in ascii_art_list:
        clear_screen()
        print(art)
        time.sleep(1)  # Wait for 1 second before showing the next piece of art
