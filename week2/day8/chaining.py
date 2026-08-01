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

# JD create 

JD = """
We are hiring a Backend Python Developer.

Requirements:
- Strong Python
- FastAPI or Django
- PostgreSQL
- Docker
- AWS
- REST APIs
- 2+ years of experience
"""

# Resume create

RESUME = """
Name: Sonu sharma 
Experience:
3 years as a Software Developer.
Skills:
Python, FastAPI, MySQL, Docker, REST APIs, Git
Projects:
Built a food delivery backend using
FastAPI and MySQL.
Deployed applications using Docker.
"""

# function to call llm

def ask_llm(system_prompt,user_prompt,):
    system_msg ={
        "role":"system",
        "content":system_prompt
    }
    user_msg = {
        "role":"user",
        "content":user_prompt
    }
    messages = [system_msg,user_msg]
    response = client.chat.completions.create(model=model,messages=messages)
    answer= response.choices[0].message.content
    return answer

# step 1 

def resume_extract(RESUME):
    print("STEP 1")
    system_prompt="""
    You are a professional HR assistant. Extract the skills from the candidates resume provided.
    Only return the skills no other information. Do not invent any skillsby yourself.
    Output Format:
    Skills should be separated by commas. Just return comma separated skills do not return any other filler information
    """ 
    user_prompt=f"""
    Extract the skills from this resume
    {RESUME}
    """
    return ask_llm(system_prompt, user_prompt)

# step 2 

def jd_extract(JD):
    print("STEP 2")
    system_prompt="""
    You are a professional HR assistant. Extract the skills from the Job description  provided.
    Only return the skills no other information. Do not invent any skills by yourself.
    Output Format:
    Skills should be separated by commas. Just return comma separated skills do not return any other filler information
    """
    user_prompt=f"""
    Extract the skills from this JD
    {JD}
    """
    return ask_llm(system_prompt, user_prompt)

# step 3

def matching(candidate,jd):
    print("STEP 3")
    system_prompt="""
    You are a professional HR assistant. compare the skills of candidate and the skills required in the JD and produce a final score between
    1 and 100. also produce a short verdict whther the candidate is a good fit for the role.
    """
    user_prompt=f"""
    Compare and match the skills
    JD:
    {jd}
    Candidate:
    {candidate}
    """
    return ask_llm(system_prompt, user_prompt)

candidate = resume_extract(RESUME)
print(candidate)
sleep(1)
jd = jd_extract(JD)  
print(jd)
sleep(2)
score = matching(candidate,jd)
print(score)