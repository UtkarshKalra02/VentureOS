import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-3-flash-preview")

def call_gemini(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text