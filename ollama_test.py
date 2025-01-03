import requests
import json

# URL for the Ollama API
url = "http://10.0.0.39:11434/api/generate"  # Replace with the correct IP

# Function to ask a question and get a response
def ask_question(question):
    data = {
        "model": "llama3.2",  # Using the specified model
        "prompt": question,
        "max_tokens": 100,  # Adjust the number of tokens as needed
        "keep_alive": 5
    }

    response = requests.post(url, json=data)

    if response.status_code == 200:
        # print("Raw Response Text:")
        # print(response.text)  # Print raw response

        # Initialize a variable to store the complete response
        complete_response = ""

        # Split the raw response text into separate JSON objects
        response_parts = response.text.splitlines()

        # Parse each JSON object and append the 'response' field
        for part in response_parts:
            try:
                chunk = json.loads(part)
                complete_response += chunk['response']
                if chunk['done']:  # If done is True, the response is complete
                    break
            except json.JSONDecodeError:
                continue

        return complete_response.strip()  # Clean up the response

    else:
        print(f"Error: {response.status_code}")
        return None

# Main function to interact with the user
def main():
    question = "Could you tell me about TARS, from the movie Interstellar?"  # Predefined question
    answer = ask_question(question)
    if answer:
        print(answer)

if __name__ == "__main__":
    main()
