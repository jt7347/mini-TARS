import subprocess
import base64

class TARS_Camera:
    def __init__(self):
        self.timeout = 1000
        self.filename = "image.jpg"

    def take_photo(self):
        # Run the libcamera-still command to capture an image
        try:
            subprocess.run(["libcamera-still", "-o", self.filename, "--timeout", "1000"], check=True)
            ret = self.encode_image(self.filename)
            return ret
        except subprocess.CalledProcessError:
            print("Error: Failed to capture image.")
            # None return
            return
    
    def encode_image(self, filename):
        '''Separate the take photo and encode image to allow
        usage of encoding function w/o needing to take a photo.'''
        with open(filename, "rb") as img_file:
            base64_string = base64.b64encode(img_file.read()).decode('utf-8')
            return base64_string

# Main function to interact with the user
def main():
    TARS = TARS_Camera()
    ret = TARS.take_photo()

if __name__ == "__main__":
    main()
