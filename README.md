# CodeMate AI — AI Coding Assistant

A lightweight college mini project built with Python Flask, HTML, CSS, JavaScript, SQLite and the Gemini API.

## Features
- AI code generation
- Code explanation
- Debugging suggestions
- Code optimization
- Programming language conversion
- Programming Q&A chat
- SQLite request history

## Requirements
- Python 3.10+
- Internet access for Gemini API calls
- A Gemini API key

## Setup (Windows)

1. Open this folder in VS Code.
2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env`.
5. Add your API key to `.env`:

   ```env
   GEMINI_API_KEY=your_actual_key
   GEMINI_MODEL=gemini-2.5-flash
   ```

   Keep `.env` private. Do not upload it to GitHub or share screenshots containing your key.

6. Start the app:

   ```bash
   python app.py
   ```

7. Open http://127.0.0.1:5000 in your browser.

## Setup (macOS/Linux)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your API key
python app.py
```

## Project structure

```text
AI_Coding_Assistant/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── backend/
│   ├── __init__.py
│   ├── ai_engine.py
│   └── database.py
├── frontend/
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── script.js
└── database/
    └── (history.db is created automatically)
```

## Notes
- The app does not execute user-submitted or AI-generated code. It provides AI-assisted suggestions only.
- The SQLite database and its table are created automatically on first launch.
- API usage may be subject to provider quotas, pricing, and rate limits.
- Review AI-generated code before using it in real systems.
