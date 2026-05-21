
import json
import google.generativeai as genai
import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("VITE_GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY is missing in .env")

# Configure Google Generative AI
genai.configure(api_key=GEMINI_API_KEY)

# Initialize model
model = genai.GenerativeModel("gemini-2.5-flash")

# --- Pydantic Model ---
class MarketInsightsRequest(BaseModel):
    jobTitle: str = Field(..., min_length=2)

# --- Router ---
router = APIRouter(
    prefix="/api/market",
    tags=["Market Insights"]
)

# --- Endpoint ---
@router.post("/market-insights")
async def get_market_insights(request: MarketInsightsRequest):
    print(f"Received market insights request for: {request.jobTitle}")

    try:
        system_instruction = """
You are a job market analyst.
Provide key insights for a specific job title.
Respond ONLY with valid JSON in this exact format:

{
  "averageSalary": "string",
  "demand": "string",
  "topSkills": [
    { "name": "string", "importance": number }
  ]
}

Rules:
- Return ONLY JSON.
- No explanation.
- 5–10 skills.
"""

        prompt = f'Provide job market insights for "{request.jobTitle}".'

        # --- FIXED Gemini Request Format ---
        response = model.generate_content(
            contents=[
                {
                    "parts": [
                        {"text": system_instruction},
                        {"text": prompt}
                    ]
                }
            ]
        )

        result_text = response.text

        if not result_text or not result_text.strip():
            raise HTTPException(status_code=500, detail="Model returned an empty response.")

        # Remove ```json fences if any
        cleaned_text = (
            result_text.replace("```json", "")
                       .replace("```", "")
                       .strip()
        )

        insights_data = json.loads(cleaned_text)

        print("Market insights generated successfully.")
        return insights_data

    except json.JSONDecodeError:
        print("❌ JSON decoding failed.")
        raise HTTPException(status_code=500, detail="Failed to parse the JSON from AI response.")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
