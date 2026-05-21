from fastapi import APIRouter
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Load API key
GEMINI_API_KEY = os.getenv("VITE_GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY is missing in .env")

genai.configure(api_key=GEMINI_API_KEY)

class ChatRequest(BaseModel):
    message: str

router = APIRouter(
    prefix="/api/ai/chat",
    tags=["ChatBot"]
)

model = genai.GenerativeModel("gemini-2.5-flash")  # or gemini-2.0, etc.

@router.post("/")
async def chat_with_bot(data: ChatRequest):
    try:
        prompt = f"""
You are a career assistant.
Only answer questions related to careers, jobs, job market, and skills.
If the question is outside this scope, politely decline.

User question: {data.message}
"""

        response = model.generate_content(prompt)

        return {
            "response": response.text
        }

    except Exception as e:
        print("Error:", e)
        return {"error": "Failed to get response from Google AI."}
