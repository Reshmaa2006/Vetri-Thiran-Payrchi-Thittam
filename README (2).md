# FitBuddy – AI Fitness Plan Generator

FitBuddy is a FastAPI + Jinja2 + SQLite application based on the supplied documentation. It generates personalized 7-day workout plans, nutrition/recovery tips, and feedback-based revisions using Google's Gemini API.

## Features
- User form: name, user ID, age, weight, goal, intensity
- AI 7-day workout generation
- AI nutrition/recovery tip
- Feedback-based plan revision
- SQLite + SQLAlchemy persistence
- Admin dashboard with original/updated plans
- REST API and FastAPI Swagger docs
- Local demo fallback when no Gemini key is configured

## Structure
```text
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── services.py
│   ├── routes.py
│   ├── gemini_generator.py
│   ├── gemini_flash_generator.py
│   ├── updated_plan.py
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── result.html
│       ├── all_users.html
│       └── error.html
├── static/css/style.css
├── static/js/app.js
├── tests/test_app.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## VS Code setup
1. Install Python 3.11+.
2. Open this folder in VS Code.
3. Open Terminal.
4. Create and activate a virtual environment.

Windows PowerShell:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
Windows CMD:
```cmd
python -m venv .venv
.venv\Scripts\activate
```
macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install packages:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Gemini configuration
Copy `.env.example` to `.env` and put your Gemini key in `GEMINI_API_KEY`.

The project uses the current `google-genai` SDK. If the key is empty, FitBuddy uses a local deterministic demo response so you can test the UI and database without an API call.

## Run
```bash
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000
API docs: http://127.0.0.1:8000/docs
Admin: http://127.0.0.1:8000/view-all-users
Health: http://127.0.0.1:8000/health

If `ADMIN_KEY` is set, use `/view-all-users?admin_key=YOUR_KEY`.

## Test
```bash
pytest -q
```
Tests use local demo mode and do not require a Gemini key.

## API
POST `/api/workout` accepts name, user_id, age, weight, goal and intensity.
POST `/api/feedback` accepts user_id and feedback.
GET `/api/nutrition-tip?goal=weight%20loss`

## Health note
This is a wellness/education demo, not medical advice. Users should seek qualified professional guidance for injuries, medical conditions, pregnancy, eating disorders, or other special circumstances.
