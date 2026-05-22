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
async def generate_career_path(job_title: str) -> str:
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

async def generate_interview_question(job_title: str, experience_level: str) -> str:
    prompt = f"""
    You are an expert FAANG interviewer.
    Generate ONE interview question for a candidate applying for a '{job_title}' position at a '{experience_level}' level.
    Respond with ONLY the question itself. No introductory text or conversational filler.
    """
    try:
        response = litellm.completion(
            model=litellm.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("AI Error generating single interview question:", e)
        return f"Could you describe a challenging project you worked on recently as a {job_title}?"


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


async def process_interview_answer(question: str, user_answer: str, job_title: str, experience_level: str) -> tuple[str, str]:
    """
    Process an interview answer and generate feedback + next question.
    Returns: (feedback_text, next_question_text)
    """
    feedback_prompt = f"""
    You are an expert FAANG interviewer evaluating a candidate for a {job_title} position ({experience_level} level).

    Question: {question}
    Candidate's Answer: {user_answer}

    Provide detailed, constructive feedback in Markdown format. Include:
    1. Overall Impression
    2. Strengths of the answer
    3. Areas for Improvement
    4. A model answer example
    """

    next_question_prompt = f"""
    You are an expert interviewer for a {job_title} position ({experience_level} level).
    Based on the previous question and answer, generate ONE follow-up interview question.
    The question should naturally build on the conversation.

    Previous Question: {question}
    Candidate's Answer Summary: {user_answer[:200]}

    Respond with ONLY the interview question, no extra text.
    """

    try:
        feedback_response = litellm.completion(
            model=litellm.model,
            messages=[{"role": "user", "content": feedback_prompt}]
        )
        feedback_text = feedback_response.choices[0].message.content

        next_q_response = litellm.completion(
            model=litellm.model,
            messages=[{"role": "user", "content": next_question_prompt}]
        )
        next_question_text = next_q_response.choices[0].message.content

        return feedback_text, next_question_text
    except Exception as e:
        print("AI Error in process_interview_answer:", e)
        return (
            "Sorry, there was an issue generating feedback. Please try again.",
            "Could you tell me more about your experience with this topic?"
        )
