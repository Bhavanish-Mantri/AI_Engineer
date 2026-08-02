import os
from pathlib import Path
from time import sleep
from dotenv import load_dotenv
from groq import Groq
from time import sleep

load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API key kaha hai bhai")

client=Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"

prompt = "Explain how internet works in very simple and easy manner"

messages = {
    "role" : "user",
    "content" : prompt
}

messages = [messages]

# # without streaming
# print("---without streaming---")
# response = client.chat.completions.create(model=model,messages=messages)   # no need to write 'stream=false' as it is default behaviour of LLM
# answer = response.choices[0].message.content
# print(answer)


# with streaming
print("---with streaming---")
response = client.chat.completions.create(model = model, messages = messages, stream = True)

for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end = "", flush = True)
