import subprocess
import base64

class TARS_Camera:
    def __init__(self):
        self.timeout = 1000

    def take_photo(output_image="image.jpg"):
        # Run the libcamera-still command to capture an image
        try:
            subprocess.run(["libcamera-still", "-o", output_image, "--timeout", "1000"], check=True)
            with open(output_image, "rb") as img_file:
                base64_string = base64.b64encode(img_file.read()).decode('utf-8')
                return base64_string
        except subprocess.CalledProcessError:
            print("Error: Failed to capture image.")
            return
