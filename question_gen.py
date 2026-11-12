import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-flash-lite-latest")

def generate_questions(resume_text, target_role="Software Developer", num_questions=8):
    prompt = f"""
You are an experienced technical interviewer.

Candidate's resume text:
{resume_text}

Target role: {target_role}

Generate {num_questions} interview questions for this candidate, personalized to their
actual skills and projects mentioned above. Include a mix of technical questions,
project-specific questions, and 1-2 general HR questions.

Return ONLY a numbered list of questions, nothing else.
"""

    response = model.generate_content(prompt)
    raw_text = response.text

    questions = [line.strip() for line in raw_text.split("\n") if line.strip()]
    return questions