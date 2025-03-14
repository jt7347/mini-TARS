import subprocess
import base64

def capture_and_convert(output_image="image.jpg", output_text="image_base64.txt"):
    # Run the libcamera-still command to capture an image
    try:
        subprocess.run(["libcamera-still", "-o", output_image, "--timeout", "1000"], check=True)
        print(f"✅ Image captured and saved as {output_image}")
    except subprocess.CalledProcessError:
        print("❌ Error: Failed to capture image.")
        return

    # Convert the image to Base64
    try:
        with open(output_image, "rb") as img_file:
            base64_string = base64.b64encode(img_file.read()).decode('utf-8')

        # Save Base64 string to a text file
        with open(output_text, "w") as txt_file:
            txt_file.write(base64_string)

        print(f"✅ Base64 string saved to {output_text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    capture_and_convert()
