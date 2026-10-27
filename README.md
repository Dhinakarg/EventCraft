# EventCraft AI 🎪✨

[![CI](https://github.com/Dhinakarg/EventCraft/actions/workflows/ci.yml/badge.svg)](https://github.com/Dhinakarg/EventCraft/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type Check: Mypy Strict](https://img.shields.io/badge/mypy-strict-blue.svg)](https://mypy-lang.org/)
[![Pylint: 10/10](https://img.shields.io/badge/pylint-10.00%2F10-brightgreen.svg)](https://pylint.pycqa.org/)
[![WCAG 2.1 AA](https://img.shields.io/badge/accessibility-WCAG%202.1%20AA-success.svg)](docs/ACCESSIBILITY.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **"Let Python do the math. Let AI do the vibe."**

EventCraft AI is an accessible, deterministic event planning engine for **weddings**, **birthdays**, and **community festivals**. It pairs deterministic Python rules with **Google Gemini 2.5 Flash** for bespoke themes, decor, and chat assistance — with zero hallucinated arithmetic and complete offline resilience.

---

## ⚡ Highlights

- 💰 **Exact Arithmetic**: Budget allocations balanced down to the rupee/cent with a protected 5%–10% contingency buffer.
- ⏱️ **Backward Timeline Scheduling**: Generates milestone due dates from the event date backward, with automated rush detection.
- 📋 **Vendor Checklists**: Pre-negotiation interview questions and category budget caps.
- 🎨 **Creative Ideas Layer**: Gemini 2.5 Flash generates bespoke themes, color palettes, and menus with 100% offline fallback support.
- ♿ **WCAG 2.1 AA Compliant**: High-contrast dark/light mode, full keyboard navigation, screen-reader live regions, and zero `innerHTML`.
- 🛡️ **Hardened Security**: Strict CSP, rate-limiting, input sanitization, and PII masking.

---

## 🏛️ Architecture at a Glance

EventCraft AI uses a clean, unidirectional 4-layer architecture:

```
[ Frontend: Vanilla ES Modules (Zero Build Step) ]
                       │
                       ▼
[ API Layer: FastAPI Routers (/api/plan, /api/chat, /api/export/ics) ]
                       │
                       ▼
[ Service Layer: Domain Orchestration (plan_service.py) ]
          │                                  │
          ▼                                  ▼
[ Deterministic Engine ]            [ Creative AI Engine ]
  • budget.py (exact math)            • Gemini 2.5 Flash
  • timeline.py (scheduling)          • LRU in-memory cache
  • vendors.py (checklists)           • Context-aware fallbacks
  • ics.py (RFC 5545 export)          • Prompt injection guard
          │                                  │
          ▼                                  ▼
[ engine/data/ (typed specs) ]      [ ai/data/ (canned content) ]
```

*For complete technical details, see [ARCHITECTURE.md](ARCHITECTURE.md).*

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/Dhinakarg/EventCraft.git
cd EventCraft
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
```bash
cp .env.example .env
# Add your GEMINI_API_KEY (if omitted, high-quality curated fallbacks run automatically)
```

### 3. Run Application
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## 🧪 Testing & Quality Gates

EventCraft AI maintains strict quality standards across all modules:

```bash
# Run 56 Python tests with whole-app coverage enforcement (>=90%)
pytest --cov=app --cov-report=term-missing --cov-fail-under=90

# Run 9 pure JavaScript unit tests
npm test

# Run full linter and static typecheck pipeline
ruff check .
mypy --strict app
pylint app
radon cc app -n B  # 100% Grade A cyclomatic complexity

# Or run everything with one command:
make verify
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/plan` | Generates complete event plan with budget, timeline, vendors, and creative ideas. |
| `POST` | `/api/chat` | Conversational assistant for plan refinement (constrained strictly to event planning). |
| `GET` | `/api/export/ics` | Exports timeline tasks as an RFC 5545 standard `.ics` calendar file. |
| `GET` | `/health` | Service health check and model readiness probe. |

---

## ♿ Accessibility & Standards

EventCraft AI is built to be accessible to all users out of the box:
- **WCAG 2.1 Level AA**: Meets all contrast, zoom (200%), and 320px reflow criteria.
- **Screen Reader Ready**: Full ARIA tab patterns, announcements via `#status-announcer`, and proper form field grouping.
- **Zero Third-Party CDNs**: Local assets only with system font fallbacks and lightweight SVG sprites.

*Detailed audit reports are documented in [docs/ACCESSIBILITY.md](docs/ACCESSIBILITY.md).*

---

## 📄 License

MIT License. Designed and built with deterministic reliability and modern accessibility.
