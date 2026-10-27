"""GenAI integration service using google-genai SDK with safe fallbacks."""

import json
from typing import Any, Dict, List, Optional
from google import genai
from google.genai import types
from app.config import get_settings
from app.sanitizer import mask_sensitive_info, sanitize_raw_text
from app.schemas import (
    ChatMessage,
    ChatResponse,
    CreativeIdeaResponse,
    CreativePromptRequest,
    EventType,
)


def _get_client() -> Optional[genai.Client]:
    """Instantiate Google GenAI client if API key is present."""
    settings = get_settings()
    if not settings.gemini_api_key or not settings.gemini_api_key.strip():
        return None
    return genai.Client(api_key=settings.gemini_api_key.strip())


def _wedding_fallback(name: str, style: str, topic: str) -> CreativeIdeaResponse:
    """Return fallback wedding creative ideas."""
    return CreativeIdeaResponse(
        topic=topic,
        title=f"{style.capitalize()} Enchantment for {name}",
        ideas=[
            f"Curated {style.lower()} palette: Warm champagne, muted sage, and brushed gold.",
            "Customized vows booklet with hand-pressed botanical paper and calligraphy.",
            "Interactive audio guestbook phone booth where friends leave voicemail memories.",
            "Late-night artisan snack cart featuring warm sliders and cookie shots.",
        ],
        decor_suggestions=[
            "Hanging suspended floral cloud over the sweetheart head table.",
            "Warm amber uplighting with textured drapery and glowing taper candles.",
            "Personalized acrylic welcome signage with gold foil calligraphy accents.",
        ],
        signature_touch="A departure gift box featuring local artisanal treats.",
        source="deterministic-fallback",
    )


def _birthday_fallback(name: str, style: str, topic: str) -> CreativeIdeaResponse:
    """Return fallback birthday creative ideas."""
    return CreativeIdeaResponse(
        topic=topic,
        title=f"Spectacular {style.capitalize()} Celebration for {name}",
        ideas=[
            f"Theme Concept: '{style.capitalize()} Retro Glow' or 'Chic Celestial Evening'.",
            "Personalized trivia contest about the honoree with lighthearted prizes.",
            "Photo station with customizable polaroids and metallic marker guest board.",
            "Signature mocktail/cocktail tailored to the honoree's favorite flavors.",
        ],
        decor_suggestions=[
            "Organic tiered balloon installation with neon script typography sign.",
            "Glittering table runners with ambient fairy light mason jars.",
            "Customized photo timeline banner celebrating memorable milestone moments.",
        ],
        signature_touch="Confetti cannon blast during the chorus of the birthday song.",
        source="deterministic-fallback",
    )


def _community_fallback(name: str, style: str, topic: str) -> CreativeIdeaResponse:
    """Return fallback community creative ideas."""
    return CreativeIdeaResponse(
        topic=topic,
        title=f"Vibrant Community Gathering for {name}",
        ideas=[
            "Collaborative community art mural where attendees paint a commemorative canvas.",
            "Local culinary passport: sample bites from 5 neighborhood grassroots food vendors.",
            "Maker station featuring do-it-yourself seedling planting or craft exchange.",
            "Acoustic showcase highlighting emerging youth talent from nearby schools.",
        ],
        decor_suggestions=[
            "Weather-resistant colorful pennant bunting across trees and pathways.",
            "Recycled wood signage guiding visitors to hydration, workshops, and rest areas.",
            "Chalk art hopscotch and greeting pathways leading to the entry gate.",
        ],
        signature_touch="A community time capsule box sealed at closing ceremony for next year.",
        source="deterministic-fallback",
    )


def _build_fallback_ideas(req: CreativePromptRequest) -> CreativeIdeaResponse:
    """Generate high-quality curated creative suggestions deterministically."""
    style = req.style_preference or "Modern"
    name = req.event_name or "Event"
    if req.event_type == EventType.WEDDING:
        return _wedding_fallback(name, style, req.topic)
    if req.event_type == EventType.BIRTHDAY:
        return _birthday_fallback(name, style, req.topic)
    return _community_fallback(name, style, req.topic)


def _build_fallback_chat(
    messages: List[ChatMessage], current_plan: Optional[Dict[str, Any]]
) -> ChatResponse:
    """Provide rule-based conversational refinement when LLM is unavailable."""
    last_msg = messages[-1].content.lower() if messages else ""
    if any(k in last_msg for k in ("budget", "cost", "cheap", "money")):
        reply = (
            "To optimize your budget, shift 5-10% from decor into catering, "
            "or host on a Friday/Sunday for lower venue rental fees."
        )
    elif any(k in last_msg for k in ("time", "schedule", "timeline")):
        reply = (
            "For a smoother timeline, ensure a 30-minute buffer before the grand entrance. "
            "Check the Timeline tab to see your minute-by-minute schedule!"
        )
    elif any(k in last_msg for k in ("vendor", "photo", "dj", "band")):
        reply = (
            "When interviewing vendors, always ask about backup gear and overage rates. "
            "Review our Vendor Guide tab for interview questions and deliverables!"
        )
    else:
        reply = (
            "I'm here to refine your event! You can ask for themes, speech points, "
            "cost-saving tips, or timeline advice. What would you like to explore?"
        )
    return ChatResponse(reply=reply, plan_adjustments=None)


def generate_creative_ideas(req: CreativePromptRequest) -> CreativeIdeaResponse:
    """Generate creative ideas via Gemini or fallback."""
    client = _get_client()
    if client is None:
        return _build_fallback_ideas(req)

    settings = get_settings()
    prompt = (
        f"You are EventCraft AI. Create ideas for a {req.event_type.value} named '{req.event_name}' "
        f"with {req.guest_count} guests in {req.style_preference} style. "
        f"Topic: {req.topic}. Details: {req.additional_context}. "
        "Output JSON with keys: topic, title, ideas (list of 4 strings), "
        "decor_suggestions (list of 3 strings), signature_touch (string)."
    )
    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        data = json.loads(response.text)
        return CreativeIdeaResponse(
            topic=sanitize_raw_text(data.get("topic", req.topic), 50),
            title=sanitize_raw_text(data.get("title", f"Ideas for {req.event_name}"), 100),
            ideas=[sanitize_raw_text(i, 200) for i in data.get("ideas", [])[:5]],
            decor_suggestions=[sanitize_raw_text(d, 200) for d in data.get("decor_suggestions", [])[:4]],
            signature_touch=sanitize_raw_text(data.get("signature_touch", ""), 250),
            source="gemini-ai",
        )
    except Exception:
        return _build_fallback_ideas(req)


def refine_plan_with_chat(
    messages: List[ChatMessage], current_plan: Optional[Dict[str, Any]]
) -> ChatResponse:
    """Refine event plan conversationally via Gemini or fallback."""
    client = _get_client()
    if client is None:
        return _build_fallback_chat(messages, current_plan)

    settings = get_settings()
    history = [f"{m.role.upper()}: {mask_sensitive_info(m.content)}" for m in messages[-6:]]
    plan_ctx = f"Event: {current_plan.get('event_name', 'Event')}" if current_plan else "None"

    prompt = (
        "You are EventCraft AI. Assist with event planning. "
        f"Plan Context: {plan_ctx}. "
        "Conversation:\n" + "\n".join(history) + "\n\n"
        "Provide an encouraging, actionable response under 100 words."
    )
    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
        )
        cleaned_reply = sanitize_raw_text(response.text or "", 1000)
        return ChatResponse(reply=cleaned_reply, plan_adjustments=None)
    except Exception:
        return _build_fallback_chat(messages, current_plan)
