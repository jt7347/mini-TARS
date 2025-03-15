import requests
import base64

# Function to encode image to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Path to your image
image_path = "burn_out_image.jpg"

# Get base64 encoded image
base64_image = encode_image(image_path)

# API endpoint
url = "http://localhost:10000/api/generate"

# Payload
payload = {
    "model": "llama3.2-vision",
    "prompt": "What is in this picture?",
    "stream": False,
    "images": [base64_image],
}

# Make the POST request
response = requests.post(url, json=payload)

# Parse and display the "response" field
response_json = response.json()
print(response_json.get("response", "No response found"))