from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Load API key from environment variables
GEMINI_API_KEY = os.getenv("VITE_GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY is missing in .env file. Please add it.")

# Configure Google Generative AI with the API key
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model (using the latest available model name, adjust if needed)
model = genai.GenerativeModel("gemini-2.5-flash")

# --- Pydantic Models ---
class SkillJobMatchingRequest(BaseModel):
    skills: list[str] = Field(..., description="List of user skills.")
    collegeTier: str = Field(..., description="College tier (e.g., 'Tier 2/3').")
    characterProfileKey: str = Field(..., description="Character profile key (e.g., 'Explorer').")

class Job(BaseModel):
    title: str
    company: str
    location: str
    description: str
    salaryRange: str
    matchScore: int

class SkillAnalysis(BaseModel):
    skillLevel: str

class SkillJobMatchingResponse(BaseModel):
    skillAnalysis: SkillAnalysis
    suggestedJobs: list[Job]

# --- Router ---
router = APIRouter(
    prefix="/api/skill-job-matching",
    tags=["Skill Job Matching"]
)

# --- Endpoint ---
@router.post("/analyze")
async def analyze_skills_for_jobs(request: SkillJobMatchingRequest):
    print(f"Received skill job matching request for skills: {request.skills}, collegeTier: {request.collegeTier}, characterProfileKey: {request.characterProfileKey}")

    try:
        # System instruction for the AI model
        system_instruction = """You are an expert career coach specializing in helping students from Tier 2/3 colleges find suitable jobs. Analyze the provided skills, college tier, and character profile to suggest matching jobs. Respond ONLY with valid JSON in this exact format:

{
  "skillAnalysis": {
    "skillLevel": "string (e.g., Beginner, Intermediate, Advanced)"
  },
  "suggestedJobs": [
    {
      "title": "string",
      "company": "string",
      "location": "string",
      "description": "string",
      "salaryRange": "string",
      "matchScore": number (0-100)
    }
  ]
}

Rules:
- Return ONLY JSON.
- Suggest 3-5 jobs.
- Match scores should be realistic based on skills.
- Salary ranges should be appropriate for the role and location.
"""

        # Prompt for the AI model
        prompt = f"""Analyze the following skills for a student from {request.collegeTier} college with character profile '{request.characterProfileKey}'.

Skills: {', '.join(request.skills)}

Provide job suggestions that match these skills."""

        # Generate content using the AI model
        response = model.generate_content(
            contents=[
                {"parts": [{"text": system_instruction}]},
                {"parts": [{"text": prompt}]}
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

        import json
        result = json.loads(cleaned_text)

        # Validate the structure
        if "skillAnalysis" not in result or "suggestedJobs" not in result:
            raise HTTPException(status_code=500, detail="Invalid response structure from AI model.")

        print("Skill job matching completed successfully.")
        return result

    except json.JSONDecodeError:
        print("❌ JSON decoding failed.")
        raise HTTPException(status_code=500, detail="Failed to parse the JSON from AI response.")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
