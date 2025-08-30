import os
import json
import subprocess
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

def execute_command(command):
    result = subprocess.run(command, shell=True, executable='/bin/zsh', 
                          capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Error executing command: {result.stderr}")
    return f"stdout: {result.stdout}\nstderr: {result.stderr}"

def write_to_file(file_path, content):
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"File written successfully to {file_path}"

def add_two_numbers(a, b):
    return a + b

def get_weather_info(city):
    weather_data = {
        "New York": "25 degrees Celsius with clear skies",
        "Los Angeles": "30 degrees Celsius with sunny weather",
        "Chicago": "20 degrees Celsius with cloudy skies",
    }
    return weather_data.get(city, "Weather information not available for this city.")

TOOLS_MAP = {
    "addTwoNumbers": add_two_numbers,
    "getWeatherInfo": get_weather_info,
    "exectuteCommand": execute_command,
    "writeToFile": write_to_file,
}

SYSTEM_PROMPT = """
You are a helpful AI assistant designed to resolve and code user queries.
You work on START, THINK, ACTION, OBSERVE and OUTPUT cycle.

In the START phase, you will receive a user query.
In the THINK phase, you will analyze the query and determine if you can resolve it with your built-in functions or if you need to call an external tool. Do the think thing for as long as it is necessary.
If there is a need to call an external tool, you will use the ACTION phase to call the tool with input parameters.
If there is an action call, wait for the OBSERVE that is the output of the tool.
Based on the OBSERVE from the previous step, you will either OUTPUT or repeat the cycle.

Available tools:
- addTwoNumbers(a: number, b: number): number - Adds two numbers together.
- getWeatherInfo(city: string): string - Returns the current weather information for a given city.
- exectuteCommand(command: string): string - Executes a shell command on the user's machine and returns the STDOUT and STDIN.
- writeToFile(filePath: string, content: string): string - Writes content to a file at the specified path.

Always build a new folder for any new application that the user wants to have which is already not there in the workspace.

Example:
START: What is the weather in New York?
THINK: The user is asking for the weather in New York
THINK: From the available tools, I can use getWeatherInfo to get the weather information.
ACTION: Call tool getWeatherInfo("New York")
OBSERVE: 25 degrees Celsius
THINK: The output for getWeatherInfo for "New York" is 25 degrees Celsius.
OUTPUT: The current weather in New York is 25 degrees Celsius with clear skies.

Rules:
- Always wait for the next step.
- Always output a single step and wait for the next step.
- The output must be stricly JSON format.
- Only call tool action from available tools.
- If you are dealing with code generation, make sure the formatting is correct and the next line is indented properly.

Output format:
{
  "step": "string",
  "tool": "string",
  "input": "string",
  "content": "string",
}

Output example:
{
  "role": "user",
  "content": "What is the weather in New York?",
}
{
  "step": "think",
  "content": "The user is asking for the weather in New York."
}
{
  "step": "think",
  "content": "From the available tools, I can use getWeatherInfo to get the weather information."
}
{
  "step": "action",
  "tool": "getWeatherInfo",
  "input": {
    "city": "New York"
  }
}
{
  "step": "observe",
  "content": "25 degrees Celsius"
}
{
  "step": "think",
  "content": "The output for getWeatherInfo for 'New York' is 25 degrees Celsius."
}
{
  "step": "output",
  "content": "The current weather in New York is 25 degrees Celsius with clear skies."
}   
"""

def main():
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
    ]

    # user_query = 'Make a separte folder and inside it make a complete chess website for me. Only the homepage using html css and js. The application should be end to end.'

    user_query = input("Enter the next big thing to build")

    messages.append({
        "role": "user",
        "content": user_query,
    })

    while True:
        response = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
        )

        messages.append({"role": "assistant", "content": response.choices[0].message.content})

        parsed_response = json.loads(response.choices[0].message.content)
        
        if parsed_response.get("step") == "think":
            print(f"🧠: {parsed_response['content']}")
            continue

        if parsed_response.get("step") == "output":
            print(f"💬: {parsed_response['content']}")
            break

        if parsed_response.get("step") == "action":
            print(f"🔧: Calling tool {parsed_response['tool']} with input {json.dumps(parsed_response['input'])}")
            
            tool = parsed_response["tool"]
            input_params = parsed_response["input"]

            value = TOOLS_MAP[tool](*input_params.values())
            print(f"🧐: Tool result: {value}")

            messages.append({
                "role": "assistant",
                "content": json.dumps({
                    "step": "observe",
                    "content": value,
                }),
            })

            continue

if __name__ == "__main__":
    main()
