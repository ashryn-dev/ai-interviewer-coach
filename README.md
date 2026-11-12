# AI Interviewer Coach

**Developed by:** Ashish Sharma
**Course:** BCA (AI/DS)

A web app that turns your resume into a personalised mock interview. 
Upload a PDF resume, 
answer the generated questions out loud,
 and get a score and 
 written feedback for every answer.

## Features

- **Resume-based questions:** reads a PDF resume and generates 8 tailored interview questions using Google Gemini.
- **Voice interview:** questions are spoken aloud by the browser, and answers are captured with speech recognition. A "Type instead" option is available if the microphone fails.
- **Choice of interviewer voice:** pick any installed English voice and preview it before you start.
- **Scored feedback:** each answer gets a score out of 10 and 2-3 sentences of constructive feedback, plus an overall average.
- **Reliable evaluation:** all answers are scored in a single API call, with an automatic fallback to a second model if the first one is rate-limited.
- **Polished interface:** dark theme with gold accents, animated landing page, progress dots, and colour-coded score badges.

## Tech stack

| Part | Technology |
|---|---|
| Backend | Python, Flask |
| AI | Google Gemini (`google-generativeai`) |
| PDF parsing | pdfplumber |
| Frontend | HTML, CSS, vanilla JavaScript |
| Voice | Web Speech API (speech synthesis and speech recognition) |

## Project structure

```
AI INTERVIEWER COACH/
├── app.py                  # Flask routes
├── question_gen.py         # Gemini question generation
├── evaluator.py            # Gemini answer scoring
├── .env                    # GEMINI_API_KEY (not committed)
├── static/
│   └── style.css
├── templates/
│   ├── index.html          # Landing page
│   ├── upload.html         # Resume upload
│   ├── questions.html      # Generated questions
│   └── interview.html      # Voice interview and feedback
└── uploads/                # Uploaded resumes (not committed)
```

## Setup

1. **Open a terminal** in the project folder.

2. **Create and activate a virtual environment**

```
   python -m venv venv
   venv\Scripts\activate
```

3. **Install dependencies**

```
   pip install flask pdfplumber python-dotenv google-generativeai
```

4. **Add your Gemini API key.** Create a file named `.env` in the project folder:

```
   GEMINI_API_KEY=your_key_here
```

   You can get a free key from Google AI Studio.

5. **Run the app**

```
   python app.py
```

6. Open **http://127.0.0.1:5000/** in **Chrome or Edge**.

## How to use

1. Click **Get started** on the landing page.
2. Upload your resume as a PDF and wait a few seconds for the questions.
3. Click **Start voice interview**, then **Start Interview**.
4. For each question, click **Record Answer** and speak (or use **Type instead**), then click **Next Question**.
5. After the last question, read your scores and feedback.

## Notes

- Use **Chrome or Edge**. Speech recognition is not supported in Firefox.
- Allow microphone access when the browser asks.
- Always open the app at `127.0.0.1` or `localhost`.
- The free Gemini tier has daily limits. If scoring fails, wait and try again, or use a different API key.
- The most recent questions are saved to `latest_questions.json`, so the interview page still works after the server restarts.

## Limitations

- PDF resumes only.
- Scores come from an AI model and are guidance, not a guarantee of interview results.
- Speech recognition accuracy depends on the browser and microphone.

## Possible future improvements

- Support for DOCX resumes.
- Saving interview history and progress over time.
- Choosing the job role or difficulty level.
- Migrating to the newer `google-genai` package.