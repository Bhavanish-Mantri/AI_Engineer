import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API key kaha hai yr")

client  = Groq(api_key = my_api_key)

model = "llama-3.3-70b-versatile"
role = "user"
# prompt = "I love you so much"
prompt = "Suggest name for my new clothing company"

# SYSTEM 

# message_system = {
#     "role": "system",
#     "content": "you are my sweet and lovely girlfriend"
# }

# message_system ={
#     "role": "system",
#     "content": " you are my strict office Manager"
# }

message_system ={
    "role": "system",
    "content": " you are a Brand Manager , suggest me some names for my new clothing comapny . name should be in one word , siggest one name only"
}

# message me role and content pass karna hai

message = {
    "role": role,
    "content": prompt
}

# as the system message change, the way of answer is also change, so we can use system message to change the way of answer
# messages = [message_system, message]
 
messages = [message_system, message]

# By default Temperature is 0 , groq range is [0-2]
response = client.chat.completions.create(model = model , messages = messages, temperature = 2)

print("###########################################################")

answer = response.choices[0].message.content
print(answer)