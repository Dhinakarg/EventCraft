"""Google GenAI client wrapper with response schema, retry, timeout, and LRU cache."""

import hashlib
import json
from collections import OrderedDict

from google import genai
from google.genai import types

from app.ai.fallback import get_fallback_chat, get_fallback_ideas
from app.ai.prompts import build_chat_prompt, build_ideas_prompt
from app.ai.schemas import ChatRefineResponse, IdeasRequest, IdeasResponse
from app.config import get_settings
from app.sanitizer import sanitize_raw_text

# In-memory thread-safe LRU cache for ideas and chat queries
_CACHE: OrderedDict[str, object] = OrderedDict()
_CACHE_MAX_SIZE = 128


def _get_cache(key: str) -> object | None:
    """Retrieve entry from LRU cache and update access order."""
    if key in _CACHE:
        _CACHE.move_to_end(key)
        return _CACHE[key]
    return None


def _set_cache(key: str, value: object) -> None:
    """Store entry in LRU cache, evicting oldest if capacity reached."""
    _CACHE[key] = value
    _CACHE.move_to_end(key)
    if len(_CACHE) > _CACHE_MAX_SIZE:
        _CACHE.popitem(last=False)


def clear_cache() -> None:
    """Clear all items in the in-memory LRU cache."""
    _CACHE.clear()


def compute_request_hash(data: dict) -> str:
    """Compute deterministic SHA-256 hash for request payload."""
    serialized = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _get_client() -> genai.Client | None:
    """Return configured GenAI client or None if API key missing."""
    settings = get_settings()
    if not settings.gemini_api_key or not settings.gemini_api_key.strip():
        return None
    return genai.Client(api_key=settings.gemini_api_key.strip())


def _call_gemini_ideas_with_retry(client: genai.Client, prompt: str) -> IdeasResponse:
    """Execute Gemini request with response schema and 1 retry on failure."""
    settings = get_settings()
    cfg = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=IdeasResponse,
    )
    last_err: Exception | None = None
    for _ in range(2):
        try:
            response = client.models.generate_content(model=settings.gemini_model, contents=prompt, config=cfg)
            parsed = json.loads(response.text)
            parsed["source"] = "ai"
            return IdeasResponse.model_validate(parsed)
        except Exception as err:
            last_err = err
    raise last_err or RuntimeError("Gemini ideas generation failed")


def generate_event_ideas(req: IdeasRequest) -> IdeasResponse:
    """Generate structured creative ideas using Gemini AI or fallback with caching."""
    cache_key = f"ideas:{compute_request_hash(req.model_dump())}"
    cached = _get_cache(cache_key)
    if isinstance(cached, IdeasResponse):
        return cached

    client = _get_client()
    if client is None:
        result = get_fallback_ideas(req)
        _set_cache(cache_key, result)
        return result

    prompt = build_ideas_prompt(req)
    try:
        result = _call_gemini_ideas_with_retry(client, prompt)
    except Exception:
        result = get_fallback_ideas(req)

    _set_cache(cache_key, result)
    return result


def _call_gemini_chat_with_retry(client: genai.Client, prompt: str) -> str:
    """Execute conversational query with 1 retry on failure."""
    settings = get_settings()
    last_err: Exception | None = None
    for _ in range(2):
        try:
            response = client.models.generate_content(model=settings.gemini_model, contents=prompt)
            return sanitize_raw_text(response.text or "", 600)
        except Exception as err:
            last_err = err
    raise last_err or RuntimeError("Gemini chat failed")


def refine_plan_chat(plan_context: str, question: str) -> ChatRefineResponse:
    """Refine event plan conversationally with length limits and 1 retry."""
    clean_q = sanitize_raw_text(question, max_length=300)
    cache_key = f"chat:{compute_request_hash({'ctx': plan_context, 'q': clean_q})}"
    cached = _get_cache(cache_key)
    if isinstance(cached, ChatRefineResponse):
        return cached

    client = _get_client()
    if client is None:
        result = get_fallback_chat(plan_context, clean_q)
        _set_cache(cache_key, result)
        return result

    prompt = build_chat_prompt(plan_context, clean_q)
    try:
        reply_text = _call_gemini_chat_with_retry(client, prompt)
        result = ChatRefineResponse(reply=reply_text, source="ai")
    except Exception:
        result = get_fallback_chat(plan_context, clean_q)

    _set_cache(cache_key, result)
    return result
