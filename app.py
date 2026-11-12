from flask import Flask, render_template, request, redirect, jsonify
import os
import json
import hashlib
import pdfplumber
from question_gen import generate_questions
from evaluator import evaluate_all
from problems import PROBLEMS
from code_runner import run_tests
from code_feedback import build_feedback
from history import init_db, add_session, list_sessions


app = Flask(__name__)
init_db()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

QUESTIONS_FILE = "latest_questions.json"


def save_questions(questions):
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f)


def load_questions():
    if os.path.exists(QUESTIONS_FILE):
        try:
            with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []
    return []


latest_questions = load_questions()
question_cache = {}  # resume_hash -> list of questions


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    global latest_questions
    if request.method == "POST":
        resume = request.files.get("resume")
        if resume:
            filepath = os.path.join(UPLOAD_FOLDER, resume.filename)
            resume.save(filepath)
            resume_text = extract_text_from_pdf(filepath)

            resume_hash = hashlib.md5(resume_text.encode("utf-8")).hexdigest()

            if resume_hash in question_cache:
                latest_questions = question_cache[resume_hash]
            else:
                raw_questions = generate_questions(resume_text)
                latest_questions = clean_questions(raw_questions)
                question_cache[resume_hash] = latest_questions

            save_questions(latest_questions)
            return render_template("questions.html", questions=latest_questions)

    return render_template("upload.html", extracted=None)


@app.route("/interview")
def interview():
    if not latest_questions:
        return redirect("/upload")
    return render_template("interview.html", questions=latest_questions)


@app.route("/evaluate", methods=["POST"])
def evaluate():
    data = request.get_json(silent=True) or {}
    qa_pairs = data.get("answers", [])

    evaluated = evaluate_all(qa_pairs)

    results = []
    scored = []
    for pair, ev in zip(qa_pairs, evaluated):
        results.append({
            "question": pair.get("question", ""),
            "answer": pair.get("answer", ""),
            "score": ev["score"],
            "feedback": ev["feedback"],
        })
        if not ev["error"]:          # failed API calls don't drag the average down
            scored.append(ev["score"])

    average_score = round(sum(scored) / len(scored), 1) if scored else 0

    # save to history (only when at least one answer was really scored)
    if scored:
        try:
            add_session("interview", "Voice interview", average_score * 10)
        except Exception as e:
            print("Could not save history:", e)

    return {"results": results, "average_score": average_score}


# ---------------- coding round ----------------
@app.route("/coding")
def coding():
    problem_id = request.args.get("problem", "two-sum")
    if problem_id not in PROBLEMS:
        problem_id = "two-sum"
    p = PROBLEMS[problem_id]
    listing = [{"id": k, "title": v["title"], "difficulty": v["difficulty"]} for k, v in PROBLEMS.items()]
    return render_template(
        "coding.html", problems=listing, pid=problem_id, title=p["title"], difficulty=p["difficulty"],
        statement=p["statement"], example=p["example"], starter=p["starter"], hint_count=len(p["hints"]),
    )


@app.route("/run", methods=["POST"])
def run_code():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    if len(code) > 20000:
        return jsonify({"status": "error", "message": "Code is too long.", "passed": 0, "total": 0, "tests": []})
    return jsonify(run_tests(data.get("problem", ""), code))


@app.route("/hint")
def hint():
    p = PROBLEMS.get(request.args.get("problem", ""))
    level = request.args.get("level", "1")
    if p is None or not level.isdigit() or not (1 <= int(level) <= len(p["hints"])):
        return jsonify({"hint": "No more hints for this problem."})
    return jsonify({"hint": p["hints"][int(level) - 1]})


@app.route("/code-feedback", methods=["POST"])
def code_feedback():
    data = request.get_json(silent=True) or {}
    result = build_feedback(data)
    try:
        problem = PROBLEMS.get(data.get("problem", ""))
        if problem:   # ignore malformed requests
            add_session("coding", "Coding: " + problem["title"], result["score"], result["verdict"])
    except Exception as e:
        print("Could not save history:", e)
    return jsonify(result)


@app.route("/history")
def history():
    return render_template("history.html", sessions=list_sessions())


def clean_questions(raw_questions):
    cleaned = []
    for q in raw_questions:
        q = q.strip()
        if not q:
            continue
        parts = q.split(". ", 1)
        if len(parts) == 2 and parts[0].strip().rstrip(".").isdigit():
            q = parts[1]
        cleaned.append(q.strip())
    return cleaned


def extract_text_from_pdf(filepath):
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


if __name__ == "__main__":
    app.run(debug=True)