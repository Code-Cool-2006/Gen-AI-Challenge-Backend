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
class ResumeReviewRequest(BaseModel):
    resume_text: str = Field(..., min_length=10, description="The full text of the resume to review. Must be at least 10 characters long.")

# --- Router ---
router = APIRouter(
    prefix="/api/resume",
    tags=["Resume Review"]  # Updated tag for clarity
)

# --- Endpoint ---
@router.post("/review")
async def review_resume(request: ResumeReviewRequest):
    print(f"Received resume review request. Resume length: {len(request.resume_text)} characters.")

    try:
        # System instruction for the AI model to act as a career coach and recruiter
        system_instruction = """You are an expert career coach and recruiter specializing in helping students from Tier 2/3 colleges land jobs at top companies. Your feedback must be constructive, encouraging, and highly actionable. Analyze the resume for ATS compatibility, impact metrics, action verbs, and clarity. Based on the resume, suggest the most suitable career path and specific job titles. Provide feedback in simple markdown format."""

        # Prompt for the AI model with the resume text
        prompt = f"""Please review the following resume for a student from a Tier 2/3 college. Provide a review with the following structure: ### Overall Impression (A brief, encouraging summary) ### ATS Compatibility Score: [Give a score out of 10] (Briefly explain why, mentioning keywords and formatting) ### Actionable Feedback (Bulleted List) - Point 1 - Point 2 - Point 3 ### Suggested Career & Jobs - **Suggested Career Path:** [e.g., Software Engineer, Data Analyst, Product Manager] - **Confidence Score:** [e.g., 85%] - **Top 3 Job Titles:** - [Job Title 1] - [Job Title 2] - [Job Title 3] Resume Text: --- {request.resume_text} ---"""

        # Generate content using the AI model with system instruction and prompt
        response = model.generate_content([system_instruction, prompt])

        # Extract the generated text from the response
        generated_text = response.text

        # Check if the generated text is valid and not empty
        if not generated_text or not generated_text.strip():
            raise HTTPException(status_code=500, detail="Model returned an empty response. Please try again.")

        # Return the generated review text as a JSON response with a key "review"
        return {"review": generated_text.strip()}

    except Exception as e:
        # Log the error for debugging purposes
        print(f"❌ Error in resume review: {e}")

        # Raise an HTTP exception with a 500 status code and a detailed error message
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
