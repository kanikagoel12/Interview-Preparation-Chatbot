# main.py (Streamlit frontend) — fixed to avoid out-of-bounds errors
import requests
import streamlit as st
import random, json, io, datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# ----------------- Helper data (local question bank) -----------------
QUESTION_BANK = {
    "Software Engineer": {
        "General": [
            {"id": 1, "question":"Explain the difference between process and thread.", "type":"concept", "difficulty":"easy", "hint":"Consider memory and scheduling."},
            {"id": 2, "question":"How would you find a cycle in a directed graph? Give approach and complexity.", "type":"algorithm","difficulty":"medium", "hint":"Think DFS and colors/stack."},
            {"id": 3, "question":"Design a URL shortener service. Outline components and trade-offs.", "type":"system-design","difficulty":"hard", "hint":"Consider database, hashing, collision handling."}
        ],
        "Backend": [
            {"id": 4, "question":"How does database indexing speed up queries? Types of indexes?", "type":"concept","difficulty":"medium","hint":"B-trees, hash indexes"},
            {"id": 5, "question":"Explain ACID properties in databases.", "type":"concept","difficulty":"easy","hint":""}
        ],
        "Frontend": [
            {"id": 6, "question":"How does the browser render a webpage (critical rendering path)?", "type":"concept","difficulty":"medium","hint":"HTML, CSS, JS parsing & layout."},
            {"id": 7, "question":"Explain virtual DOM and its benefits.", "type":"concept","difficulty":"easy","hint":""}
        ],
        "Machine Learning": [
            {"id": 8, "question":"How would you evaluate and compare two models with different class imbalance?", "type":"ml","difficulty":"medium","hint":"Precision/recall, ROC, PR curves."}
        ],
        "System Design": [
        {"id": 6, "question": "Design a URL shortener (like bit.ly).", "type": "technical", "difficulty": "hard", "hint": "Think database, hashing, scalability."},
        {"id": 7, "question": "How would you design a scalable chat system?", "type": "technical", "difficulty": "hard", "hint": "Message queues, storage, real-time updates."},
        ],
        "Full Stack Development": [
            {"id": 8, "question": "What is the role of middleware in Express.js?", "type": "technical", "difficulty": "medium", "hint": "Request/response lifecycle."},
            {"id": 9, "question": "How do you secure a full-stack web application?", "type": "technical", "difficulty": "hard", "hint": "Authentication, authorization, input validation."},
        ]


    },
    "Product Manager": {
        "General": [
            {"id": 11, "question":"Describe a time you prioritized features under tight deadline (STAR).", "type":"behavioral","difficulty":"medium","hint":"Be specific about trade-offs."},
            {"id": 12, "question":"How do you define success metrics for a new feature?", "type":"behavioral","difficulty":"easy","hint":"Think quantitative + qualitative metrics."}
        ]
    },
    "Data Analyst": {
        "General":[
            {"id": 21, "question":"How would you clean a dataset with many missing values?", "type":"concept","difficulty":"medium","hint":"Imputation, dropping, modeling missingness."},
            {"id": 22, "question":"Which chart would you use to compare distribution of a continuous variable across groups?", "type":"concept","difficulty":"easy","hint":"Box plot, violin plot."}
        ]
    }
}

# ----------------- Utility functions -----------------
def generate_questions(role, domain, mode, n=3):
    """Pick n questions from the local QUESTION_BANK according to role/domain."""
    bank = QUESTION_BANK.get(role, {})
    # if domain not available, use 'General'
    q_list = bank.get(domain) or bank.get("General") or []
    if not q_list:
        return []
    if n >= len(q_list):
        return q_list.copy()
    return random.sample(q_list, n)

def mock_evaluate_answer(question_text, answer_text, mode):
    score = 4.0
    words = answer_text.strip().split()
    if len(words) > 15: score += 2.0
    if len(words) > 60: score += 2.0
    key_terms = ["complexity","time","space","edge case","scalable","tests","trade-off","STAR","impact"]
    matches = sum(1 for k in key_terms if k in answer_text.lower())
    score += min(matches, 2)
    score = max(0, min(10, score))
    strengths = ["Good detail and explanation"] if len(words) > 15 else []
    weaknesses = ["Answer too short — add more specifics"] if len(words) <= 15 else []
    strengths += ["Used relevant keywords"] if matches else []
    weaknesses += ["Missing technical keywords or trade-offs"] if not matches else []
    feedback = "Nice attempt. " + ("Expand with edge-cases and complexity analysis." if "complexity" not in answer_text.lower() else "Good complexity analysis.")
    suggested = "Mention time/space complexity and give one edge-case or test example."
    resources = ["Cracking the Coding Interview (book)", "System Design Primer (GitHub)"]
    return {
        "score": round(score,1),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "feedback": feedback,
        "suggested_improvement": suggested,
        "resources": resources
    }

def make_pdf_bytes(session_meta, qa_list):
    """Generate a simple PDF summary using reportlab and return bytes."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    w, h = letter
    margin = 40
    y = h - margin
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, f"Interview Summary — {session_meta['role']} ({session_meta['mode']})")
    y -= 28
    c.setFont("Helvetica", 11)
    c.drawString(margin, y, f"Domain: {session_meta['domain']}   Questions: {len(qa_list)}   Avg score: {session_meta.get('avg_score','-')}")
    y -= 20
    for i, item in enumerate(qa_list, start=1):
        if y < 120:
            c.showPage()
            y = h - margin
        c.setFont("Helvetica-Bold", 12)
        qline = f"Q{i}: {item['question'][:100]}"
        c.drawString(margin, y, qline)
        y -= 14
        c.setFont("Helvetica", 10)
        a = item.get('answer','(skipped)') or '(skipped)'
        c.drawString(margin, y, "Answer: " + (a[:180].replace('\n',' ')))
        y -= 14
        evals = item.get('eval',{})
        c.drawString(margin, y, f"Score: {evals.get('score','-')}  Feedback: {evals.get('feedback','')[:200]}")
        y -= 20
    c.save()
    buf.seek(0)
    return buf.getvalue()

# ----------------- Streamlit UI -----------------
st.set_page_config(page_title="LLM Interview Simulator", layout="wide")
st.title("🤖 LLM Interview Simulator")

# Sidebar controls
with st.sidebar:
    st.subheader("Interview setup")
    role = st.selectbox("Role", list(QUESTION_BANK.keys()))
    # gather domains for selected role
    domains = list(QUESTION_BANK.get(role, {}).keys())
    domain = st.selectbox("Domain", domains)
    mode = st.radio("Mode", ["Technical", "Behavioral"])
    n_q = st.slider("Number of questions", 1, 5, 3)
    mock_mode = st.checkbox("Mock Mode ", value=True)
    st.markdown("---")
# Session state initialization
if "questions" not in st.session_state: 
    st.session_state.questions = []
if "current" not in st.session_state: 
    st.session_state.current = 0
if "answers" not in st.session_state: 
    st.session_state.answers = []
if "evals" not in st.session_state: 
    st.session_state.evals = []
if "started" not in st.session_state: 
    st.session_state.started = False

# Start / Restart
if st.sidebar.button("Start / Restart Interview"):
    st.session_state.questions = generate_questions(role, domain, mode, n_q)
    st.session_state.current = 0
    st.session_state.answers = []
    st.session_state.evals = []
    st.session_state.started = True

# Stop if not started or no questions
if not st.session_state.started or not st.session_state.questions:
    st.info("Configure the interview in the sidebar and click **Start / Restart Interview**.")
    st.stop()

# Layout: left (main question & input) and right (history/feedback)
left, right = st.columns([2,1])

# Ensure questions is not empty before accessing
if st.session_state.questions:
    st.session_state.current = max(0, min(st.session_state.current, len(st.session_state.questions) - 1))
    q_index = st.session_state.current
    question_obj = st.session_state.questions[q_index]
else:
    # Just in case, fallback safe stop
    st.info("No questions available, please start the interview.")
    st.stop()


# Ensure current index is within bounds
st.session_state.current = min(st.session_state.current, len(st.session_state.questions)-1)
q_index = st.session_state.current
question_obj = st.session_state.questions[q_index]

# ----- Question & Answer UI -----

progress_pct = int((q_index / len(st.session_state.questions)) * 100)
with left:
    st.subheader(f"Question {q_index+1} / {len(st.session_state.questions)}")
    st.progress(progress_pct)
    st.markdown(f"**{question_obj.get('question')}**")
    if question_obj.get('hint'):
        with st.expander("Hint"):
            st.write(question_obj.get('hint'))

    st.write("")  # spacing
    answer_key = f"answer_{q_index}"
    if answer_key not in st.session_state:
        st.session_state[answer_key] = ""
    st.session_state[answer_key] = st.text_area("Your answer", value=st.session_state[answer_key], height=220)

    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button("Submit Answer"):
            answer_text = st.session_state[answer_key].strip()
            if not answer_text:
                st.warning("Please write an answer before submitting.")
            else:
                if mock_mode:
                    # Use your existing mock evaluator
                    eval_result = mock_evaluate_answer(question_obj.get('question'), answer_text, mode)
                else:
                    # Call backend API
                    import requests
                    backend_url = "http://127.0.0.1:8000/evaluate"  # your backend endpoint
                    payload = {
                        "question": question_obj.get("question"),
                        "answer": answer_text,
                        "mode": mode
                    }
                    try:
                        resp = requests.post(backend_url, json=payload)
                        resp.raise_for_status()
                        eval_result = resp.json().get("eval", {"score":0, "feedback":"No feedback", "strengths":[], "weaknesses":[], "suggested_improvement":"", "resources":[]})
                    except Exception as e:
                        eval_result = {"score":0, "feedback": f"Backend call failed: {e}", "strengths":[], "weaknesses":[], "suggested_improvement":"", "resources":[]}

                # Ensure answers/evals lists have correct length
                if len(st.session_state.answers) > q_index:
                    st.session_state.answers[q_index] = answer_text
                else:
                    st.session_state.answers.append(answer_text)

                if len(st.session_state.evals) > q_index:
                    st.session_state.evals[q_index] = eval_result
                else:
                    st.session_state.evals.append(eval_result)

                # Move to next question
                if st.session_state.current < len(st.session_state.questions)-1:
                    st.session_state.current += 1

                st.session_state.update()  # refresh page to show feedback

    with c2:
        if st.button("Skip"):
            while len(st.session_state.answers) <= q_index:
                st.session_state.answers.append("")

            while len(st.session_state.evals) <= q_index:
                st.session_state.evals.append({"score": 0, "feedback":"", "strengths":[], "weaknesses":[]})

            st.session_state.evals[q_index] = {"score": 0, "feedback":"Skipped", "strengths":[], "weaknesses":[]}

            if q_index < len(st.session_state.questions)-1:
                st.session_state.current += 1
            st.session_state.update()
    with c3:
        if st.button("Retry (clear)"):
            st.session_state[answer_key] = ""
            st.session_state.update()

with right:
    st.subheader("Live Feedback")
    if q_index < len(st.session_state.evals):
        ev = st.session_state.evals[q_index]
    else:
        ev = {}

    # show last evaluation if available
    last_idx = len(st.session_state.evals) - 1
    if last_idx >= 0 and last_idx >= q_index:
        ev = st.session_state.evals[q_index]
        st.metric("Score", f"{ev.get('score','-')} / 10")
        st.markdown("**Feedback**")
        st.write(ev.get('feedback',''))
        if ev.get('strengths'):
            st.markdown("**Strengths**")
            for s in ev.get('strengths'):
                st.write("• " + s)
        if ev.get('weaknesses'):
            st.markdown("**Weaknesses**")
            for w in ev.get('weaknesses'):
                st.write("• " + w)
        if ev.get('suggested_improvement'):
            with st.expander("Suggested improvement / model answer"):
                st.write(ev.get('suggested_improvement'))
        if ev.get('resources'):
            with st.expander("Resources"):
                for r in ev.get('resources'):
                    st.write("• " + r)
        if st.button("Next Question"):
            if st.session_state.current < len(st.session_state.questions)-1:
                st.session_state.current += 1
                st.rerun()
    else:
        st.info("Submit an answer to see feedback here.")

# Final summary when all questions have been answered
if len(st.session_state.evals) >= len(st.session_state.questions):
    st.markdown("---")
    st.header("Final Summary")
    scores = [e.get('score',0) for e in st.session_state.evals]
    avg = sum(scores)/len(scores) if scores else 0
    st.metric("Average score", f"{avg:.2f} / 10")
    # aggregate strengths/weaknesses
    strengths = []
    weaknesses = []
    for ev in st.session_state.evals:
        strengths += ev.get('strengths', [])
        weaknesses += ev.get('weaknesses', [])
    st.subheader("Top strengths")
    for s in set(strengths) or ["(none)"]:
        st.write("• " + s)
    st.subheader("Top weaknesses")
    for w in set(weaknesses) or ["(none)"]:
        st.write("• " + w)

    # full Q/A list
    st.subheader("All Q/A")
    for i, q in enumerate(st.session_state.questions):
        st.markdown(f"**Q{i+1}:** {q.get('question')}")
        st.write("**A:** " + (st.session_state.answers[i] or "(skipped)"))
        st.write("**Score:** " + str(st.session_state.evals[i].get('score', '-')))
        st.write("---")

    # Download JSON
    if st.button("Prepare session downloads"):
        session_meta = {"role": role, "domain": domain, "mode": mode, "avg_score": f"{avg:.2f}", "created_at": datetime.datetime.utcnow().isoformat()}
        qa_items = []
        for i,q in enumerate(st.session_state.questions):
            qa_items.append({"question": q.get('question'), "answer": st.session_state.answers[i], "eval": st.session_state.evals[i]})
        st.session_state._download_json = json.dumps({"meta": session_meta, "qa": qa_items}, indent=2)
        st.session_state._download_pdf = make_pdf_bytes(session_meta, qa_items)
        st.success("Prepared downloads!")

    if st.session_state.get("_download_json"):
        st.download_button("Download JSON", data=st.session_state._download_json, file_name="interview_session.json", mime="application/json")
    if st.session_state.get("_download_pdf"):
        st.download_button("Download PDF summary", data=st.session_state._download_pdf, file_name="interview_summary.pdf", mime="application/pdf")
