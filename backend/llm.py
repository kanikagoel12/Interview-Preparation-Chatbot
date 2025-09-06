import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# Mock question generator
def generate_questions(role, domain, mode, n):
    return [
        {
            "id": i+1,
            "question": f"Sample question {i+1} for {role} ({domain}, {mode})",
            "type": "Technical" if "Technical" in mode else "Behavioral",
            "difficulty": "Medium"
        }
        for i in range(n)
    ]

# Mock evaluator
def evaluate_answer(question, answer, mode):
    return {
        "score": 7.5,
        "strengths": ["Clear explanation", "Good structure"],
        "weaknesses": ["Add real-world example", "Minor inaccuracies"],
        "feedback": f"Your answer for '{question}' is decent but could improve.",
        "suggested_improvement": "Provide examples and be more precise.",
        "resources": [
            "https://www.interviewbit.com/technical-interview-questions/",
            "https://www.geeksforgeeks.org/hr-interview-questions-and-answers/"
        ]
    }
