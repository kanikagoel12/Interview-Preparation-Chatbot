import os
from pathlib import Path
from dotenv import load_dotenv
import json
from openai import OpenAI
# Load environment variables
dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

client = OpenAI(api_key=OPENAI_API_KEY)
# Hardcoded demo questions
DEMO_QUESTIONS = [
    {"id": 1, "question":"Explain the difference between process and thread.", "type":"concept","difficulty":"easy","hint":"Consider memory and scheduling."},
    {"id": 2, "question":"How would you find a cycle in a directed graph? Give approach and complexity.", "type":"algorithm","difficulty":"medium","hint":"Think DFS and colors/stack."},
    {"id": 3, "question":"Design a URL shortener service. Outline components and trade-offs.", "type":"system-design","difficulty":"hard","hint":"Consider database, hashing, collision handling."},
    {"id": 4, "question":"Explain the difference between process and thread.", "type":"concept","difficulty":"easy","hint":"Consider memory and scheduling."},
    {"id": 5, "question":"How would you find a cycle in a directed graph? Give approach and complexity.", "type":"algorithm","difficulty":"medium","hint":"Think DFS and colors/stack."},
    
]

def generate_questions(role, domain, mode, n):
    # just return first n questions from DEMO_QUESTIONS
    return DEMO_QUESTIONS[:n]

def evaluate_answer(question, answer, mode):
    # your LLM feedback logic here
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




# ----------------- LLM-powered answer evaluator -----------------
def evaluate_answer(question, answer, mode):
    """
    Sends candidate answer to OpenAI LLM for evaluation.
    Returns JSON with score, strengths, weaknesses, feedback, suggested improvement, resources.
    Works with any question passed in (demo, future LLM-generated, or hardcoded).
    """
    prompt = f"""
You are an interview evaluator.
Question: {question}
Candidate Answer: {answer}
Mode: {mode} (Technical or Behavioral)
Evaluate the answer and return strictly JSON in this format:
{{
  "score": 0-10 float,
  "strengths": ["..."],
  "weaknesses": ["..."],
  "feedback": "...",
  "suggested_improvement": "...",
  "resources": ["...","..."]
}}
"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful interviewer and evaluator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        text = response.choices[0].message.content
        # parse JSON safely
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("Response not dict")
        return data
    except Exception as e:
        # fallback if LLM fails
        return {
            "score": 5,
            "strengths": [],
            "weaknesses": [],
            "feedback": f"Could not evaluate using AI. Reason: {str(e)}",
            "suggested_improvement": "",
            "resources": []
        }
