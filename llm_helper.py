from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

def llm(messages):
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY")
    )

    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"},
    )

    return chat_completion.choices[0].message.content

if __name__ == "__main__":
    load_dotenv()   

    messages=[
        {
            "role": "user",
            "content": "What is the weather in New York? Respond in JSON format."
        }
    ]

    response = llm(messages)
    print(response)