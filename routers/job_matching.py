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

class JobMatchingRequest(BaseModel):
    jobDescription: str = Field(..., min_length=10)
    resumeText: str = Field(..., min_length=10)
    collegeTier: str = Field(default="Tier 2/3")
    characterProfileKey: str = Field(default="Explorer")
    skills: list[str] = Field(default_factory=list)

router = APIRouter(
    prefix="/api/job-matching",
    tags=["Job Matching"]
)

model = genai.GenerativeModel("gemini-2.5-flash")

@router.post("/analyze")
async def analyze_job_match(request: JobMatchingRequest):
    try:
        prompt = f"""
You are an expert career coach and recruiter specializing in helping students from {request.collegeTier} colleges land jobs at top companies. Your analysis must be constructive, encouraging, and highly actionable. Analyze the resume and job description for compatibility, skill gaps, and improvement suggestions. Provide feedback in simple markdown format.

Student profile: College tier {request.collegeTier}, character profile {request.characterProfileKey}, skills: {', '.join(request.skills) if request.skills else 'Not specified'}.

Job Description:
---
{request.jobDescription}
---

Resume Text:
---
{request.resumeText}
---

Provide an analysis with the following structure:
### Overall Match Score: [Give a score out of 10, e.g., 7.5/10]
(Briefly explain the score based on skills, experience, and qualifications match. Mention any standout strengths or major gaps.)

### Key Matching Skills & Experiences (Bulleted List - Max 5 items)
- Point 1 (e.g., "Strong Python experience matches the job's requirements for data analysis tools")
- Point 2
- Point 3

### Skill Gaps & Recommendations (Bulleted List - Max 5 items, Actionable Suggestions Only)
- Point 1 (e.g., "Consider gaining experience with cloud platforms like AWS or Azure to align with job requirements")
- Point 2
- Point 3

### Suggested Improvements to Resume (Bulleted List - Max 5 items, Specific to this Job Application Only)
- Point 1 (e.g., "Add a 'Projects' section highlighting relevant coursework or personal projects that demonstrate required skills")
- Point 2
- Point 3

### Next Steps (Bulleted List - Max 3 items, Prioritized by Impact and Feasibility for a Student from {request.collegeTier} College)
- Point 1 (e.g., "Apply for internships in related fields to build practical experience quickly")
- Point 2
- Point 3
"""

        response = model.generate_content(prompt)
        generated_text = response.text.strip()

        if not generated_text:
            raise HTTPException(status_code=500, detail="Model returned empty response")

        return {"analysis": generated_text}

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Failed to analyze job match")
