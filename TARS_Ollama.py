import requests
import json

class TARS_Ollama:
    def __init__(self):
        # URL for the Ollama API
        self.url = "http://10.0.0.39:11434/api/chat"  # Replace with the correct IP
        self.messages = None

    # Function to ask a question and get a response
    def ask_question(self, question):
        data = {
            "model": "llama3.2",  # Using the specified model
            "messages": self.messages + 
            [{
                "role": "user",
                "content": question
            }],
            "max_tokens": 100,  # Adjust the number of tokens as needed
        }

        response = requests.post(self.url, json=data)

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

            ret = complete_response.strip() # Clean up the response
            self.messages += [
                {'role': 'user', 'content': question},
                {'role': 'assistant', 'content': ret},
            ]
            return ret 

        else:
            print(f"Error: {response.status_code}")
            return None

# Main function to interact with the user
def main():
    TARS = TARS_Ollama()
    question = "Could you tell me about TARS, from the movie Interstellar?"  # Predefined question
    answer = TARS.ask_question(question)
    if answer:
        print(answer)

if __name__ == "__main__":
    main()
