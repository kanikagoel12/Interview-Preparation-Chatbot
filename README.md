# Interview-Preparation-Chatbot

# LLM Interview Simulator

A Streamlit-based app for practicing interviews with AI feedback.  
Includes a FastAPI backend for evaluation using OpenAI's GPT API.

---

## Features

- Mock or AI-based question evaluation  
- Supports multiple roles and domains (Software Engineer, Product Manager, Data Analyst, etc.)  
- Tracks answers, scores, feedback, strengths, and weaknesses  
- Export interview sessions as JSON or PDF  

---

## Prerequisites

- Python 3.10+  
- OpenAI API key (for AI evaluation)  

---

## Setup Instructions

1. Clone the repository
   ```bash
   git clone <your_repo_url>
   cd <repo_folder>

2. Create a virtual environment
   ```bash
   python -m venv venv

3. Activate the environment
   ```bash
   Windows:
   venv\Scripts\activate
   Linux / Mac:
   source venv/bin/activate
   
5. Install dependencies
   ```bash
   pip install -r requirements.txt

5. Set up environment variables

   Copy .env.example to .env inside the backend folder:

   copy backend\.env.example backend\.env  # Windows
   cp backend/.env.example backend/.env    # Linux / Mac

   Add your OpenAI API key in backend/.env:

   OPENAI_API_KEY=your_openai_api_key_here

---

## Running the App

1. Start the backend
   ```bash
   cd backend
   uvicorn main:app --reload

2. Start the frontend  
Open another terminal in the project root:
   ```bash
   streamlit run main.py

3. Open the app in your browser  
   Streamlit usually opens automatically at http://localhost:8501.

---

## Mock Mode

Mock Mode allows running the app without an OpenAI API key.  
In the Streamlit sidebar, check Mock Mode before starting the interview.  
Scores and feedback are generated using a local evaluator instead of AI.

---

## Notes

.env files should never be committed to the repository.  
Use the sidebar to select role, domain, mode, and number of questions.  
Final session results can be exported as JSON or PDF.


