"""Google GenAI client wrapper with response schema, retry, timeout, and LRU cache."""

import hashlib
import json
from collections import OrderedDict

from fastapi import Request
from google import genai
from google.genai import types

from app.ai.fallback import get_fallback_chat, get_fallback_ideas
from app.ai.prompts import build_chat_prompt, build_ideas_prompt
from app.ai.schemas import ChatRefineResponse, IdeasRequest, IdeasResponse
from app.config import get_settings
from app.constants import DEFAULT_CACHE_MAX_SIZE, DEFAULT_RETRY_ATTEMPTS, DEFAULT_TIMEOUT_MS
from app.sanitizer import sanitize_raw_text


class LruCache:
    """Thread-safe LRU cache with capacity limit."""

    def __init__(self, max_size: int = DEFAULT_CACHE_MAX_SIZE) -> None:
        """Initialize LRU cache with maximum allowed entries."""
        self.max_size = max_size
        self._store: OrderedDict[str, object] = OrderedDict()

    def get(self, key: str) -> object | None:
        """Retrieve entry from LRU cache and update access order."""
        if key in self._store:
            self._store.move_to_end(key)
            return self._store[key]
        return None

    def set(self, key: str, value: object) -> None:
        """Store entry in LRU cache, evicting oldest if capacity reached."""
        self._store[key] = value
        self._store.move_to_end(key)
        if len(self._store) > self.max_size:
            self._store.popitem(last=False)

    def clear(self) -> None:
        """Clear all items in the LRU cache."""
        self._store.clear()

    def __len__(self) -> int:
        """Return the number of stored cache entries."""
        return len(self._store)

    def __contains__(self, key: str) -> bool:
        """Check if key exists in cache."""
        return key in self._store


def get_lru_cache(request: Request) -> LruCache:
    """FastAPI dependency injecting the LruCache stored on app.state."""
    cache: LruCache | None = getattr(request.app.state, "cache", None)
    if cache is None:
        cache = LruCache()
        request.app.state.cache = cache
    return cache


def compute_request_hash(data: dict[str, object]) -> str:
    """Compute deterministic SHA-256 hash for request payload."""
    serialized = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _get_client() -> genai.Client | None:
    """Return configured GenAI client or None if API key missing."""
    settings = get_settings()
    if not settings.gemini_api_key or not settings.gemini_api_key.strip():
        return None
    http_opts = types.HttpOptions(timeout=DEFAULT_TIMEOUT_MS)
    return genai.Client(api_key=settings.gemini_api_key.strip(), http_options=http_opts)


def _call_gemini_ideas_with_retry(client: genai.Client, prompt: str) -> IdeasResponse:
    """Execute Gemini request with response schema and retries on failure."""
    settings = get_settings()
    cfg = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=IdeasResponse,
    )
    last_err: Exception | None = None
    for _ in range(DEFAULT_RETRY_ATTEMPTS):
        try:
            response = client.models.generate_content(model=settings.gemini_model, contents=prompt, config=cfg)
            raw_text = response.text or "{}"
            parsed = json.loads(raw_text)
            parsed["source"] = "ai"
            return IdeasResponse.model_validate(parsed)
        except Exception as err:  # pylint: disable=broad-exception-caught
            last_err = err
    raise last_err or RuntimeError("Gemini ideas generation failed")


def _fetch_ideas_with_fallback(client: genai.Client | None, req: IdeasRequest) -> IdeasResponse:
    """Fetch ideas from Gemini client with graceful fallback."""
    if client is None:
        return get_fallback_ideas(req)
    prompt = build_ideas_prompt(req)
    try:
        return _call_gemini_ideas_with_retry(client, prompt)
    except Exception:  # pylint: disable=broad-exception-caught
        return get_fallback_ideas(req)


def generate_event_ideas(req: IdeasRequest, cache: LruCache | None = None) -> IdeasResponse:
    """Generate structured creative ideas using Gemini AI or fallback with caching.

    Args:
        req: Validated ideas request containing event type, vibe, city, and dietary needs.
        cache: Optional LruCache instance to check and populate.

    Returns:
        IdeasResponse with themes, decor suggestions, menu ideas, and activities.
    """
    cache_key = f"ideas:{compute_request_hash(req.model_dump())}"
    if cache is not None:
        cached = cache.get(cache_key)
        if isinstance(cached, IdeasResponse):
            return cached

    result = _fetch_ideas_with_fallback(_get_client(), req)
    if cache is not None:
        cache.set(cache_key, result)
    return result


def _call_gemini_chat_with_retry(client: genai.Client, prompt: str) -> str:
    """Execute conversational query with 1 retry on failure."""
    settings = get_settings()
    last_err: Exception | None = None
    for _ in range(2):
        try:
            response = client.models.generate_content(model=settings.gemini_model, contents=prompt)
            return sanitize_raw_text(response.text or "", 600)
        except Exception as err:  # pylint: disable=broad-exception-caught
            last_err = err
    raise last_err or RuntimeError("Gemini chat failed")


def _fetch_chat_with_fallback(client: genai.Client | None, plan_context: str, clean_q: str) -> ChatRefineResponse:
    """Fetch chat reply from Gemini client with graceful fallback."""
    if client is None:
        return get_fallback_chat(plan_context, clean_q)
    prompt = build_chat_prompt(plan_context, clean_q)
    try:
        reply_text = _call_gemini_chat_with_retry(client, prompt)
        return ChatRefineResponse(reply=reply_text, source="ai")
    except Exception:  # pylint: disable=broad-exception-caught
        return get_fallback_chat(plan_context, clean_q)


def refine_plan_chat(plan_context: str, question: str, cache: LruCache | None = None) -> ChatRefineResponse:
    """Refine event plan conversationally with length limits and 1 retry.

    Args:
        plan_context: Summary string describing current event parameters and budget.
        question: User query or prompt for plan refinement.
        cache: Optional LruCache instance to check and populate.

    Returns:
        ChatRefineResponse containing sanitized assistant reply and source tag.
    """
    clean_q = sanitize_raw_text(question, max_length=300)
    cache_key = f"chat:{compute_request_hash({'ctx': plan_context, 'q': clean_q})}"
    if cache is not None:
        cached = cache.get(cache_key)
        if isinstance(cached, ChatRefineResponse):
            return cached

    result = _fetch_chat_with_fallback(_get_client(), plan_context, clean_q)
    if cache is not None:
        cache.set(cache_key, result)
    return result
