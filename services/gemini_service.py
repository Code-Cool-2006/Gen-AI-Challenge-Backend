import os
import re
import litellm
from dotenv import load_dotenv

load_dotenv()

# ---- LiteLLM Config ----
litellm.model = os.getenv("LITELLM_MODEL", "openai/gpt-4o")

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", "")

litellm.fallbacks = [
    {"openai/gpt-4o": ["openai/gpt-4o-mini"]},
    {"gemini/gemini-2.5-flash": ["openai/gpt-4o"]},
]


# ---- AI SERVICE FUNCTIONS ----
def generate_career_path(job_title: str) -> str:
    prompt = f"""
    Act as an expert career coach. A user wants to become a '{job_title}'.
    Provide a clear, structured Markdown roadmap with these exact sections:

    ### 🚀 Potential Career Path
    ### 🔧 Key Skills to Master
    ### 🤔 Sample Interview Questions
    """

    try:
        response = litellm.completion(
            model=litellm.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("AI Error:", e)
        return "Sorry, there was an issue generating the career path. Please try again later."


def generate_interview_questions(role: str) -> list[str]:
    prompt = f"""
    Generate 8 professional interview questions for a {role}.
    Number them 1-8, each on a new line. No extra text.
    """

    try:
        response = litellm.completion(
            model=litellm.model,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.choices[0].message.content
        questions = [q.strip() for q in text.split("\n") if q.strip()]
        questions = [re.sub(r"^\d+\.\s*", "", q) for q in questions]
        return questions[:8]
    except Exception as e:
        print("AI Error:", e)
        return []


def generate_interview_feedback(question: str, user_answer: str) -> str:
    prompt = f"""
    You are a FAANG interviewer.
    Provide Markdown feedback for the candidate's answer.

    **Question:** {question}
    **Answer:** {user_answer}

    Include:
    1. Overall Impression
    2. Strengths
    3. Areas for Improvement
    """

    try:
        response = litellm.completion(
            model=litellm.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("AI Error:", e)
        return "Sorry, there was an issue generating feedback."
