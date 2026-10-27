# EventCraft AI 🎪✨

**EventCraft AI** is a GenAI planning assistant for **weddings**, **birthdays**, and **community events**.

It pairs a **pure deterministic mathematical engine** (for budget allocation, timeline run-of-show, vendor breakdowns, and milestone checklists) with the **Google GenAI SDK** for creative spark generation (themes, decor, vows/speeches, signature moments) and conversational plan refinement.

---

## 🏛️ Architecture & Non-Negotiables

| Principle | Implementation |
|---|---|
| **Deterministic Logic (`app/engine`)** | Pure functions with **zero network calls** for budget distribution, 5% contingency reserve, minute-by-minute day schedules, vendor lead times, and phased checklists. |
| **GenAI SDK (`app/services`)** | Official `google-genai` SDK (`from google import genai`) used solely for creative ideas and conversational refinement, with resilient offline/fallback support. |
| **Untrusted Input Sanitization** | All user strings are length-limited, stripped of control characters, and sanitized via `app/sanitizer.py`. Zero PII or secrets are logged. |
| **Frontend (Vanilla HTML/CSS/JS)** | Zero build step. Meets **WCAG 2.1 AA** standards (accessible form labels, ARIA tabs, keyboard navigation, skip-to-content link, high contrast). **Never uses `innerHTML` with user or AI data**. |
| **Code Quality** | Strict type hints and short docstrings on every function. **No function exceeds 40 lines**. |
| **Testing & Compact Footprint** | Complete `pytest` test suite covering engines, sanitization, and API endpoints. Repository size is kept under 5 MB on a single `main` branch. |

---

## 🚀 Quick Start

### 1. Setup Virtual Environment
```bash
py -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment (Optional for Gemini API)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Provide your `GEMINI_API_KEY` (if omitted, high-quality deterministic creative fallbacks ensure 100% offline functionality).

### 3. Run Development Server
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Access the application at: **http://127.0.0.1:8000**

---

## 🧪 Running Pytest Tests

Run the full automated test suite:
```bash
.\.venv\Scripts\pytest -v
```

Verify compliance with function length (`<= 40 lines`) and docstrings:
```bash
.\.venv\Scripts\python -c "
import ast, glob, sys
violations = []
for p in glob.glob('app/**/*.py', recursive=True) + glob.glob('tests/**/*.py', recursive=True):
    tree = ast.parse(open(p, encoding='utf-8').read())
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            lines = (n.end_lineno - n.lineno) + 1
            if not ast.get_docstring(n): violations.append(f'{p}:{n.name} missing docstring')
            if lines > 40: violations.append(f'{p}:{n.name} {lines} lines (> 40)')
if violations: sys.exit('\n'.join(violations))
print('PASS: All functions comply with docstrings and <= 40 lines')
"
```

---

## 📂 Directory Structure

```
├── app/
│   ├── __init__.py
│   ├── config.py              # Pydantic Settings from env (no hardcoded secrets)
│   ├── sanitizer.py           # Untrusted input sanitization & PII redactor
│   ├── schemas.py             # Pydantic v2 validation models
│   ├── engine/                # Pure deterministic functions (no network calls)
│   │   ├── __init__.py
│   │   ├── budget.py          # Category allocation & 5% contingency
│   │   ├── timeline.py        # Day-of schedule & countdown milestones
│   │   ├── vendors.py         # Lead times, deliverables, interview questions
│   │   └── checklist.py       # Phased task generation
│   ├── services/
│   │   ├── __init__.py
│   │   └── ai_service.py      # google-genai integration with fallback
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── planner.py         # Deterministic REST endpoints
│   │   ├── ai_ideas.py        # GenAI creative studio endpoint
│   │   └── chat.py            # Conversational refinement endpoint
│   └── main.py                # FastAPI app initialization
├── static/
│   ├── index.html             # Semantic, WCAG 2.1 AA compliant UI
│   ├── css/
│   │   └── style.css          # Design system, accessible focus rings & dark/light modes
│   └── js/
│       ├── api.js             # Asynchronous API layer
│       ├── dom.js             # Safe DOM builder (strictly NO innerHTML with data)
│       └── app.js             # Client state, tab controller & interaction logic
├── tests/                     # 27 comprehensive pytest test cases
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```
