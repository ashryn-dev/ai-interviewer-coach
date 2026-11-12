import os
import json
import re
import time
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Tried in order. Separate models have separate quota pools.
MODEL_NAMES = ["gemini-flash-lite-latest", "gemini-flash-latest"]
MODELS = [genai.GenerativeModel(name) for name in MODEL_NAMES]

GEN_CONFIG = {"response_mime_type": "application/json", "temperature": 0.3}


def _call_model(prompt):
    """Try each model (2 attempts each). Return the reply text or raise."""
    last_error = None
    for model in MODELS:
        for attempt in range(2):
            try:
                response = model.generate_content(prompt, generation_config=GEN_CONFIG)
                return response.text
            except Exception as e:
                last_error = e
                print(f"Gemini call failed ({model.model_name}, attempt {attempt + 1}):", e)
                time.sleep(1.5)
    raise RuntimeError(f"All models failed: {last_error}")


def _parse_json_list(raw_text):
    """Parse a JSON array from the reply, tolerating extra text or code fences."""
    raw_text = raw_text.strip()
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", raw_text, re.DOTALL)
        if not match:
            raise ValueError("No JSON array found in response")
        data = json.loads(match.group(0))
    if isinstance(data, dict):          # sometimes wrapped as {"results": [...]}
        data = next((v for v in data.values() if isinstance(v, list)), [])
    return data


def _clean_score(value):
    try:
        return max(0, min(10, round(float(value))))
    except (TypeError, ValueError):
        return 0


def evaluate_all(qa_pairs):
    """
    Score every answer in ONE API call.
    Returns a list (same order as qa_pairs) of dicts:
        {"score": int, "feedback": str, "error": bool}
    """
    results = [None] * len(qa_pairs)
    to_score = []   # (index, question, answer)

    for i, pair in enumerate(qa_pairs):
        answer = (pair.get("answer") or "").strip()
        if not answer:
            results[i] = {"score": 0, "feedback": "No answer was recorded for this question.", "error": False}
        else:
            to_score.append((i, pair.get("question", ""), answer))

    if to_score:
        items = "\n\n".join(
            f"[{n}] Question: {q}\nCandidate's answer: {a}"
            for n, (_, q, a) in enumerate(to_score, start=1)
        )
        prompt = f"""
You are an expert interview coach evaluating a candidate's spoken answers.

For EACH numbered item below, rate the answer from 1 to 10 for relevance,
completeness and clarity, and give 2-3 sentences of constructive feedback.

{items}

Respond ONLY with a JSON array, one object per item, in this exact format:
[{{"id": 1, "score": <number 1-10>, "feedback": "<feedback text>"}}]
"""
        try:
            parsed = _parse_json_list(_call_model(prompt))
            by_id = {}
            for entry in parsed:
                if isinstance(entry, dict) and "id" in entry:
                    by_id[int(entry["id"])] = entry

            for n, (i, _, _) in enumerate(to_score, start=1):
                entry = by_id.get(n)
                if entry:
                    results[i] = {
                        "score": _clean_score(entry.get("score")),
                        "feedback": entry.get("feedback", "No feedback available."),
                        "error": False,
                    }
        except Exception as e:
            print("Evaluation error:", e)

    # anything still missing failed to score
    for i, r in enumerate(results):
        if r is None:
            results[i] = {
                "score": 0,
                "feedback": "Could not evaluate this answer right now (API limit or error). Please try again.",
                "error": True,
            }
    return results


def evaluate_answer(question, answer):
    """Single-answer helper kept for compatibility."""
    r = evaluate_all([{"question": question, "answer": answer}])[0]
    return r["score"], r["feedback"]