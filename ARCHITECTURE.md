# EventCraft AI - System Architecture

> **"Let Python do the math. Let AI do the vibe."**

EventCraft AI is an enterprise-grade, accessible event planning platform that pairs **deterministic Python calculation engines** with **generative AI (Google Gemini 2.5 Flash)**. By strictly decoupling financial math and scheduling logic from LLM generation, EventCraft AI completely eliminates hallucinated budgets, impossible deadlines, and erratic timeline calculations.

---

## 1. High-Level Architecture Overview

EventCraft AI follows a layered, decoupled service architecture:

```mermaid
graph TD
    Client["Client Browser<br/>(WCAG 2.1 AA, ES Modules &lt; 200 lines)"]
    
    subgraph FastAPI Application
        SecMid["SecurityHeadersMiddleware<br/>&amp; Rate Limiter"]
        Router["FastAPI Router<br/>(/api/plan, /api/chat, /api/export/ics)"]
        
        subgraph Deterministic Engines
            BudgetEng["Budget Engine<br/>(Penny Balancing &amp; Priority Boost)"]
            TimeEng["Timeline Engine<br/>(Backward-Scheduling &amp; Rush Compression)"]
            VendorEng["Vendor Engine<br/>(Lead-Times &amp; Interview Prompts)"]
            ICSEng["iCalendar (.ics) Generator"]
        end
        
        subgraph GenAI Creative Layer
            GeminiClient["Gemini Client Wrapper<br/>(gemini-2.5-flash)"]
            LRUCache["In-Memory LRU Cache<br/>(SHA-256 Request Hash)"]
            FallbackBlueprints["Deterministic Fallback<br/>(Instant Local Blueprints)"]
        end
    end

    Client -->|HTTPS POST| SecMid
    SecMid --> Router
    Router --> BudgetEng
    Router --> TimeEng
    Router --> VendorEng
    Router --> GeminiClient
    Router --> ICSEng
    GeminiClient <--> LRUCache
    GeminiClient -->|API Error / Missing Key| FallbackBlueprints
```

---

## 2. Layered Component Architecture

### Layer 1: Frontend Client Presentation (`/static`)
- **Zero Build Step**: Native ECMAScript Modules (`<script type="module" src="/static/app.js">`) executable in all modern browsers without Webpack, Vite, or Babel.
- **Strict Modularity**: Each module is focused and strictly kept **under 200 lines**:
  - `static/app.js`: Application coordinator, tab roving tabindex, accessibility controls.
  - `static/js/planner.js`: Plan generation submission, skeleton loading, and render delegation.
  - `static/js/budget.js`: Accessible SVG donut chart, color legend, itemized allocation table.
  - `static/js/timeline.js`: Phase-grouped vertical timeline, critical task filter toggle.
  - `static/js/vendors.js`: Interactive vendor cards, budget caps, booking deadlines, localStorage progress persistence.
  - `static/js/ideas.js`: Creative themes, culinary concepts, and decor suggestions with AI vs Template badges.
  - `static/js/chat.js`: Interactive planning assistant query handler with suggested question chips.
  - `static/js/export.js`: Native iCalendar (.ics) export and plain-text clipboard copy.
  - `static/js/form.js`: Inline validation, real-time per-guest cost calculator, and character counters.
  - `static/js/scenarios.js`: Instant sample scenario loaders (Wedding, Birthday, Community).
  - `static/js/state.js`: Centralized application state and scenario definitions.
  - `static/js/utils.js`: Safe DOM creation (`createEl`, `createSvgIcon`), currency formatting (`Intl.NumberFormat`), screen-reader announcements (`aria-live`).
- **XSS Immunity**: Absolute ban on `.innerHTML` and `insertAdjacentHTML`. All user data and API responses are bound exclusively via `document.createTextNode` and `element.textContent`.
- **WCAG 2.1 AA Accessibility**:
  - Skip-to-content links (`#main-content`).
  - Full keyboard accessibility for tabs (`ArrowLeft`, `ArrowRight`, `Home`, `End`).
  - High-contrast color tokens exceeding 4.5:1 ratio.
  - Screen reader live regions (`role="status"`, `aria-live="polite"`).
  - Explicit form fieldsets, legends, and inline error summaries linked via anchor IDs.

---

### Layer 2: Security & Sanitization Layer (`app/security.py`, `app/sanitizer.py`)
- **Security Headers Middleware**: Injects strict OWASP-compliant security headers on all responses:
  - `Content-Security-Policy`: Restricts scripts, styles, and fonts to origin and trusted CDNs.
  - `X-Frame-Options: DENY`: Prevents clickjacking.
  - `X-Content-Type-Options: nosniff`: Prevents MIME-sniffing attacks.
  - `Referrer-Policy: strict-origin-when-cross-origin`: Minimizes referrer leakage.
  - `Permissions-Policy`: Disables geolocation, camera, and microphone.
- **In-Memory Rate Limiting**: Sliding 60-second window tracking client IP addresses to mitigate denial-of-service and brute-force attacks.
- **Input Sanitization & Secret Masking**:
  - Strips invisible Unicode and dangerous control characters (`[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]`).
  - Redacts sensitive personal information (emails, phone numbers) before passing context to LLM prompts.
  - Masks internal exception traces using generic RFC 7807 problem details in production.

---

### Layer 3: Centralized Constants & Domain Models (`app/constants.py`, `app/models.py`)
- **Centralized Constants (`app/constants.py`)**:
  - Zero circular imports between engine profiles, AI client, and Pydantic schemas.
  - Named limits: `MIN_GUEST_COUNT` (1), `MAX_GUEST_COUNT` (2000), `MAX_NOTES_LENGTH` (500), `DEFAULT_CACHE_MAX_SIZE` (128), `DEFAULT_RETRY_ATTEMPTS` (3).
- **Strong Typing with Pydantic v2**:
  - Domain models: `EventRequest`, `BudgetResponse`, `TimelineResponse`, `PlanResponse`, `HealthResponse`.
  - Type-safe data structures (`NamedTuple`): `ProfileCategory`, `TaskTemplate`, `VendorSpec`, `FeasibilityResult`, `BudgetBuildResult`.
  - Full PEP 561 compliance via `app/py.typed`.

---

### Layer 4: Deterministic Computation Engines (`app/engine/`)
1. **Budget Engine (`app/engine/budget.py`)**:
   - Shifts category percentages according to user priorities using a deterministic multiplier (`1.25x`).
   - Normalizes non-contingency categories to ensure the contingency reserve (`5% - 20%`) is strictly protected.
   - Applies penny balancing algorithm (`_balance_penny_discrepancy`) ensuring exact zero-discrepancy equality with total budget down to the rupee.
   - Evaluates per-guest minimum thresholds and generates structured feasibility recommendations when underfunded.
2. **Timeline Engine (`app/engine/timeline.py`)**:
   - Computes backward-scheduled milestone dates from target event date using standard lead times.
   - Automatically detects compressed planning windows (`lead_time_days < standard_lead_time_days`).
   - Applies non-linear task compression with priority preservation and emits rush timeline warnings.
3. **Vendor Engine (`app/engine/vendors.py`)**:
   - Computes category-specific booking deadlines and matches budget allocations.
   - Provides structured interview vetting questions for each vendor category.
4. **iCalendar Engine (`app/engine/ics.py`)**:
   - Generates RFC 5545 compliant `.ics` calendar files for one-click import into Google Calendar, Apple Calendar, and Outlook.

---

### Layer 5: GenAI Creative Layer (`app/ai/`)
- **Google GenAI SDK**: Powered by `google-genai` and `gemini-2.5-flash`.
- **Structured Schema Enforcement**: Uses `IdeasResponse` Pydantic model directly as `response_schema` to enforce deterministic JSON structures from the generative model.
- **LRU In-Memory Cache**: Computes deterministic SHA-256 hashes of input payloads to instantly serve repeat requests with 0ms network latency and zero API cost.
- **Deterministic Offline Fallbacks (`app/ai/fallback.py`)**: Curated event planning blueprints ensure 100% application functionality even during network outages or missing API keys.

---

## 3. Request-Response Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Screen Reader
    participant Frontend as Frontend ES Modules
    participant API as FastAPI Router
    participant Engine as Deterministic Engines
    participant Gemini as Google Gemini AI

    User->>Frontend: Enters event details & selects priorities
    Frontend->>Frontend: Client-side validation & live per-guest calc
    Frontend->>API: POST /api/plan
    API->>API: SecurityHeaders & Rate Limiting check
    API->>Engine: allocate_event_budget(EventRequest)
    Engine-->>API: BudgetResponse (penny-balanced)
    API->>Engine: create_backward_timeline(EventRequest)
    Engine-->>API: TimelineResponse (compressed milestones)
    API->>Engine: build_vendor_checklist(EventRequest, BudgetResponse)
    Engine-->>API: list[VendorChecklistItem]
    API->>Gemini: generate_event_ideas(IdeasRequest)
    alt Cache Hit
        Gemini-->>API: Cached IdeasResponse (0ms)
    else Live Gemini Call
        Gemini-->>API: Structured IdeasResponse
    else Fallback on Failure
        Gemini-->>API: Curated Blueprint IdeasResponse
    end
    API-->>Frontend: PlanResponse (Unified JSON)
    Frontend->>Frontend: Render KPI cards, Donut chart, Timeline, Vendors
    Frontend-->>User: Visual UI update & screen-reader status announcement
```

---

## 4. Quality, Testing & CI Standards

- **Static Type Checking**: `mypy --strict app` with 100% typed functions, zero `Any` leakage, and strict optional checking across all 29 source files.
- **Linter & Complexity**: `ruff check .` with McCabe cyclomatic complexity limit (`max-complexity = 5`, `C901`) enforced in CI.
- **Code Quality**: `pylint app` maintaining a perfect **10.00 / 10.00** rating.
- **Radon Cyclomatic Complexity**: 100% Grade A cyclomatic complexity (`radon cc app -n B` returns 0 violations) and 100% Grade A maintainability index (`radon mi app -n B` returns 0 violations).
- **Test Suite**:
  - **56 Python automated tests** (`pytest --cov=app`) with **97.19% total code coverage** (failing under 90% threshold) executing in < 5 seconds.
  - **9 Node.js unit tests** (`node --test tests/js/*.test.js`) verifying pure JavaScript formatters and validation helpers.
  - Architectural AST inspection tests guaranteeing that `app.engine` never imports from `app.api`, `app.services`, or `app.ai`.
  - Frontend asset accessibility (skip links, single h1, fieldsets, ARIA roles, zero innerHTML).

---

## 5. Architectural Layers & Dependency Rule

EventCraft AI strictly enforces a unidirectional four-layer dependency hierarchy:

```
[ app.api (routes_plan, routes_chat, routes_export) ]
                       │
                       ▼
[ app.services (plan_service) ]
          │                   │
          ▼                   ▼
[ app.engine (pure math) ]  [ app.ai (creative layer) ]
          │                            │
          ▼                            ▼
[ app.engine.data ]          [ app.ai.data ]
```

1. **`app.api`**: Thin routing layer declaring endpoint signatures, parameter constraints, and response schemas. Routes invoke domain services and do not run business logic directly.
2. **`app.services`**: Orchestration layer coordinating deterministic calculations with creative AI generation.
3. **`app.engine`**: Pure deterministic calculation modules (budget, timeline, vendors, ICS export). Zero external I/O and zero dependencies on higher layers (`app.api`, `app.services`, `app.ai`), verified via automated AST inspection tests.
4. **`app.ai`**: GenAI client and resilient deterministic fallbacks.
5. **Data vs Logic Split**: Task templates, vendor interview specifications, and canned conversation dispatch rules reside exclusively in `app.engine.data` and `app.ai.data` as typed constants.

---

## 6. Code Quality Suppressions & Justifications

To preserve strict type safety and code health, blanket `noqa`, wildcard `type: ignore`, and broad disables are forbidden. Every remaining linter suppression is isolated and explicitly justified:

| File | Suppression | One-Line Justification |
| :--- | :--- | :--- |
| `app/security.py:37` | `# pylint: disable=too-few-public-methods` | Starlette `BaseHTTPMiddleware` contract specifically requires implementing only the single `dispatch` method. |
| `app/ai/gemini_client.py:73` | `# pylint: disable=broad-exception-caught` | Required for resilience to ensure external network or Gemini API failures gracefully fall back without crashing the plan generation. |
| `app/ai/gemini_client.py:101` | `# pylint: disable=broad-exception-caught` | Catches unexpected upstream SDK parsing errors to ensure guaranteed return of valid fallback event ideas. |
| `app/ai/gemini_client.py:116` | `# pylint: disable=broad-exception-caught` | Fallback resilience to ensure chat assistant never returns HTTP 500 when external LLM endpoint fails. |
| `app/ai/gemini_client.py:147` | `# pylint: disable=broad-exception-caught` | Catches SDK exceptions during conversational stream/response parsing to return canned planning advice. |
| `pyproject.toml` | `ignore = ["B008"]` | FastAPI's standard dependency injection and parameter defaults (`Query(...)`, `Depends(...)`) require function calls in default arguments. |
| `pyproject.toml` | `ignore = ["ANN401"]` | Necessary for generic in-memory caching wrappers that accept arbitrary JSON-serializable argument types (`Any`). |
| `pyproject.toml` | `ignore = ["D104"]` | Package `__init__.py` marker files do not require redundant multi-line docstrings. |
| `pyproject.toml` | `ignore = ["D203", "D213"]` | Mutually conflicting docstring summary line formatting rules in Google vs NumPy styles. |
| `tests/*` | `ignore = ["S101", "ANN", "D"]` | Pytest test functions rely on standard `assert` statements and do not require production API docstrings or return type annotations. |
