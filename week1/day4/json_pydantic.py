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
# now structuring it 
from pydantic import BaseModel
class Ticket(BaseModel):
    name : str
    email : str
    Issue : str

# Schema create karege 
schema = Ticket.model_json_schema()

# response type banayege
response_format = {
    "type" : "json_object"
} 

# system prompt to tell LLM to behave like this 
system_prompt = f'''extract the personal info from the following ticket strictly based on this schemaand give me in  and give in json format output {schema}'''

# message 
message_system = {
    "role" : "system",
    "content" : system_prompt
}
# user input
text = "Hello My name is Bhavanish Mantri .I have a phone which is not working that i have bought from your shop. I live in Delhi, nad my email is abc@gmail.com and contach no. is 9876543210"
prompt = f''' this is a customer info from this {text} ''' 


# message me role and content pass karna hai

message = {
    "role": role,
    "content": prompt
}

messages = [message_system,message]

response = client.chat.completions.create(model = model , messages = messages,response_format = response_format)

answer = response.choices[0].message.content
print(answer)



# isko padhte kaise hai
import json
raw_json = answer
data_file = json.loads(raw_json)
ticket = Ticket(**data_file)

# isko pass karege aage ke program me!
print(ticket.name)
print(ticket.email)
print(ticket.Issue) 