# copy ollama vision and add tools
import requests
import json
import time
import re

class TARS_Ollama:
    def __init__(self):
        # URL for the Ollama API
        self.url = "http://127.0.0.1:11434/api/chat"  # Replace with the correct IP
        self.messages = json.load(open("character/tars.json"))
        self.SYSTEM_MESSAGE = """
            As TARS, you are also able to perform functionalized actions when appropiate.
            Answer questions directly when possible, and use function calling when necessary.

            ### Add new function descriptions below as necessary ###
            DECISION PROCESS:
            1. When asking for the date today, yesterday, or tomorrow:
            → Use the 'date' function.

            2. Placeholder:
            → Placeholder decision.

            IMPORTANT RULES:
            - When calling a function, respond ONLY with the JSON object, no additional text, no backticks.
            - When answering directly from memory, respond ONLY in clean natural language text, NOT in JSON.

            FUNCTION CALL FORMAT (Strict):
            Example for Date. If asked for the date today, respond with:

            ```json
            {
                "name": "date",
                "parameters": {
                    "when": "today"
                }
            }
            ```

            DATE FUNCTION (more information on the function types and their required arguments):
            {
                "name": "date",
                "description": "call the python time API to determine the date today, yesterday, or tomorrow.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "when": {
                            "type": "string",
                            "description": "a string chosen from 'today', 'yesterday', or 'tomorrow'"
                        }
                    },
                    "required": ["when"]
                }
            }

            RESPONSE GUIDELINES:
            - Only call functions if the context requires to do so (e.g. if the user asks for a joke, do not use the 'date' function)
            - If not calling a function, respond naturally without any JSON.
            - If you think you should call a function, but the function is not defined above, just respond naturally, like a chatbot would. Use context from knowledge of who you are.

            VERY IMPORTANT:
            - Do NOT try to call functions (i.e. return a json response) if the user prompt does not call for usage of the explicitly defined functions above.
            - If you are answering from memory (no function call needed), respond ONLY in natural human-readable text, NOT JSON structure.
            - Do NOT format memory answers as JSON.
            - JSON format must be used only for function calls.

        """

    # Function to ask a question and get a response
    def ask_question(self, question, attachment=""):
        data = {
            "model": "gemma3",  # Using the specified model -> gemma3 has vlm capabilities
            "messages": self.messages + 
            [{
                "role": "user",
                "content": question
            }],
            "max_tokens": 1000,  # Adjust the number of tokens as needed
        }
        # conditional attachment
        if attachment:
            data["messages"][-1]["images"] = [attachment]

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
                    complete_response += chunk['message']['content']
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
        
    # extract the tool call from the response
    def extract_tool_call(self, text):
        import io
        from contextlib import redirect_stdout

        pattern = r"```tool_code\s*(.*?)\s*```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            code = 'self.' + match.group(1).strip() # remove 'self.' + 
            # print(code)
            # Capture stdout in a string buffer
            f = io.StringIO()
            with redirect_stdout(f):
                result = eval(code, {"self": self}) # result = eval(code)
            output = f.getvalue()
            r = result if output == '' else output
            return f'```tool_output\n{str(r).strip()}\n```'''
        return None

    # def extract_func_name(self, func_str):
    #     match = re.match(r'^\s*([a-zA-Z_][\w]*)\s*\(', func_str)
    #     if match:
    #         return match.group(1)
    #     return None

    def date(self, when):
        # Get current local time
        now = time.localtime()

        # Convert current time to seconds since epoch
        current_timestamp = time.mktime(now)

        # One day in seconds
        one_day = 86400

        if when.lower() == 'yesterday':
            target_timestamp = current_timestamp - one_day
        elif when.lower() == 'today':
            target_timestamp = current_timestamp
        elif when.lower() == 'tomorrow':
            target_timestamp = current_timestamp + one_day
        else:
            return "Invalid input. Use 'yesterday', 'today', or 'tomorrow'."

        # Convert timestamp to struct_time
        target_time = time.localtime(target_timestamp)

        # Format as a calendar date (e.g., "2025-07-01")
        return time.strftime("%Y-%m-%d", target_time)


# Unit Testing
def main():
    TARS = TARS_Ollama()
    
    image = "" # base64 string here
    _ = TARS.ask_question(TARS.SYSTEM_MESSAGE, attachment=image)

    while True:
        question = input("Input: ")
        image = "" # base64 string here
        answer = TARS.ask_question(question, attachment=image)
        print(answer)
        # tool_call = TARS.extract_tool_call(answer)
        # # print(tool_call)
        # if tool_call:
        #     print("Tool called.")
        #     print(tool_call)
        #     answer2 = TARS.ask_question(tool_call, attachment=image)
        #     if answer2:
        #         print("---Tool---Answer---")
        #         print(answer2)
        #         print("---Tool---Answer---")
        # else:
        #     print("---Reg---Answer---")
        #     print(answer)
        #     print("---Reg---Answer---")

if __name__ == "__main__":
    main()
    