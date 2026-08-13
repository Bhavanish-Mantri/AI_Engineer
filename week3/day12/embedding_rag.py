import os
import dotenv
from groq import Groq
import numpy as np
from sentence_transformers import SentenceTransformer

def cosine_similarity(a,b):
    return np.dot(a,b) / (np.linalg.norm(a) * np.linalg.norm(b))   

model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions

# text = "Hello, how are you?"

# embedding = model.encode(text)

# print(embedding.shape)
# print(embedding[:10])

t1 = "There are 24 leaves"
t2 = "My name is Bhavanish"

e1 = model.encode(t1)
e2 = model.encode(t2)

print(cosine_similarity(e1, e2))
