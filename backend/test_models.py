import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure the API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# List available models
for m in genai.list_models():
    print(f"Model name: {m.name}")
    print(f"Display name: {m.display_name}")
    print(f"Description: {m.description}")
    print("---") 