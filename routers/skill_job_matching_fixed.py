from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Load API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("VITE_GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY is missing in .env")

genai.configure(api_key=GEMINI_API_KEY)

class SkillJobMatchingRequest(BaseModel):
    skills: list[str] = Field(..., min_items=1)
    collegeTier: str = Field(default="Tier 2/3")
    characterProfileKey: str = Field(default="Explorer")

router = APIRouter(
    prefix="/api/skill-job-matching",
    tags=["Skill Job Matching"]
)

model = genai.GenerativeModel("gemini-2.5-flash")

@router.post("/analyze")
async def analyze_skills(request: SkillJobMatchingRequest):
    try:
        prompt = f"""
You are an expert career coach specializing in helping students from {request.collegeTier} colleges find suitable jobs based on their skills.

Student profile: College tier {request.collegeTier}, character profile {request.characterProfileKey}.

Skills provided: {', '.join(request.skills)}

Provide a response in the following JSON format only:
{{
  "skillAnalysis": {{
    "skillLevel": "Beginner/Intermediate/Advanced",
    "keyStrengths": ["strength1", "strength2"],
    "suggestedCareers": ["career1", "career2"]
  }},
  "suggestedJobs": [
    {{
      "title": "Job Title",
      "company": "Company Name",
      "location": "Location",
      "description": "Brief description",
      "matchScore": 85,
      "salaryRange": "$50,000 - $70,000"
    }},
    {{
      "title": "Another Job Title",
      "company": "Another Company",
      "location": "Another Location",
      "description": "Another brief description",
      "matchScore": 75,
      "salaryRange": "$45,000 - $65,000"
    }}
  ]
}}

Suggest 3-5 relevant jobs based on the skills. Focus on entry-level positions suitable for {request.collegeTier} college graduates.
"""

        response = model.generate_content(prompt)
        generated_text = response.text.strip()

        # Try to parse as JSON
        import json
        try:
            result = json.loads(generated_text)
            return result
        except json.JSONDecodeError:
            # If not JSON, wrap in a basic structure
            return {
                "skillAnalysis": {
                    "skillLevel": "Intermediate",
                    "keyStrengths": request.skills[:3],
                    "suggestedCareers": ["Software Developer", "Data Analyst"]
                },
                "suggestedJobs": [
                    {
                        "title": "Junior Developer",
                        "company": "Tech Corp",
                        "location": "Remote",
                        "description": "Entry-level development role",
                        "matchScore": 80,
                        "salaryRange": "$50,000 - $70,000"
                    }
                ]
            }

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Failed to analyze skills")
