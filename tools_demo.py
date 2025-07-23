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
        self.instructions = '''These are a set of instructions for calling methods. If you decide to invoke these methods depending on the context of the user input - if and only if a method is required to answer the question - it should be wrapped with ```tool_code```. The python methods described below are imported and available, you can only use defined methods. Do not try to invoke methods that are not specified. The generated code should be readable and efficient. The response to a method will be wrapped in ```tool_output``` use it to call more tools or generate a helpful, friendly response. The user (myself) will feed you ```tool_output``` wrapped text, to which you will generate said helpful, friendly response based on the context of the inputted text. An example workflow for tool calling would be: if deemed appropriate (for example, if an available method is to return the date, asking for the date would return ```tool_code``` that corresponds to calling the date() function. After the code handles your outputted ```tool_code```, I will feed you back a ```tool_output``` snippet, to which you will generate a response to make sense of the actual output. It is important to note that you DO NOT always have to invoke a method, when it does not make sense to do so (i.e. calling the date() function when I asked for a joke would not make sense within the context).

        The following Python methods are available to be invoked:

        ```python
        def date(when: str) -> str:
            """Return the date yesterday, today, or tomorrow depending on the string argument

            Args:
            when: A string chosen from "today", "yesterday", or "tomorrow"
            """
        ```

        End of defined methods.

        Example of correct function workflow:

        User: What is today's date?
    
        TARS:
        ```tool_code
        date(when='today')
        ```

        User:
        ```tool_output
        2025-07-06
        ```

        TARS: Today is July 6th, 2025.


        Examples of inappropiate function invoking:

        User: Tell me a joke.

        TARS:
        ```tool_code
        date(when='today')
        ```

        The above example is inappropiate because the user's prompt does not require invoking the 'date' function to answer. A general guideline to follow, is that if the user's prompt does not have any words that match the existing functions or their descriptions (in this case, the user asks "tell me a joke", a prompt which does not contain the words 'date', 'today', 'yesterday', or 'tomorrow', using the 'date' function is completely irrelevant).

        '''
        # self.available_tools = ["date"]

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
    _ = TARS.ask_question(TARS.instructions, attachment=image)

    while True:
        question = input("Input: ")
        image = "" # base64 string here
        answer = TARS.ask_question(question, attachment=image)
        print(answer)
        # tool_call = TARS.extract_tool_call(answer)
        # # print(tool_call)
        # if tool_call:
        #     print("Tool called.")
        #     # print(tool_call)
        #     answer2 = TARS.ask_question(tool_call, attachment=image)
        #     if answer2:
        #         # print("---Tool---Answer---")
        #         print(answer2)
        #         # print("---Tool---Answer---")
        # else:
        #     # print("---Reg---Answer---")
        #     print(answer)
        #     # print("---Reg---Answer---")

if __name__ == "__main__":
    main()
    