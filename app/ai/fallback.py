"""Curated context-aware deterministic fallback generators for ideas and chat."""

from app.ai.data.fallback_content import (
    BIRTHDAY_FALLBACK_ACTIVITIES,
    BIRTHDAY_FALLBACK_DECOR,
    BIRTHDAY_FALLBACK_PERSONAL_TOUCHES,
    BIRTHDAY_FALLBACK_THEMES,
    CHAT_DISPATCH_RULES,
    COMMUNITY_FALLBACK_ACTIVITIES,
    COMMUNITY_FALLBACK_DECOR,
    COMMUNITY_FALLBACK_PERSONAL_TOUCHES,
    COMMUNITY_FALLBACK_THEMES,
    WEDDING_FALLBACK_ACTIVITIES,
    WEDDING_FALLBACK_DECOR,
    WEDDING_FALLBACK_PERSONAL_TOUCHES,
)
from app.ai.schemas import ChatRefineResponse, IdeasRequest, IdeasResponse


def _build_dietary_menu(event_type: str, dietary: list[str]) -> list[str]:
    """Generate context-aware menu ideas incorporating specified dietary needs."""
    labels = ", ".join(dietary) if dietary else "Omnivore & Vegetarian"
    if "wedding" in event_type.lower():
        return [
            f"Plated Pan-Seared Bass or Herb Risotto ({labels} adapted)",
            "Artisanal salad with edible blossoms, toasted hazelnuts, and citrus vinaigrette",
            f"Passed hors d'oeuvres: Wild mushroom crostini and smoked duck breast ({labels})",
            "Late-night slider bar with gourmet truffle fries and vegan sliders",
        ]
    if "birthday" in event_type.lower():
        return [
            f"Interactive taco bar with carnitas, jackfruit, and cilantro rice ({labels})",
            f"Custom milestone birthday cake crafted with {labels} options",
            "Signature sparkling mocktail station with cold-pressed berries and fresh mint",
        ]
    return [
        f"Local artisan food truck lineup offering verified {labels} certified meals",
        "Grab-and-go Mediterranean mezze boxes with hummus, pita, and grilled vegetables",
        "Hydration oasis with infused cucumber-mint and strawberry-basil water urns",
    ]


def _build_wedding_fallback(req: IdeasRequest) -> IdeasResponse:
    """Generate curated wedding ideas fallback."""
    vibe = req.vibe or "Romantic"
    cap_vibe = vibe.capitalize()
    return IdeasResponse(
        themes=[
            f"{cap_vibe} Garden Romance with ambient taper candles",
            f"Timeless {cap_vibe} Minimalism with architectural floral installations",
            f"{cap_vibe} Starlight Soirée with suspended twinkling fairy lights",
        ],
        menu_ideas=_build_dietary_menu("wedding", req.dietary),
        activities=list(WEDDING_FALLBACK_ACTIVITIES),
        decor_tips=list(WEDDING_FALLBACK_DECOR),
        personal_touches=list(WEDDING_FALLBACK_PERSONAL_TOUCHES),
        source="fallback",
    )


def _build_birthday_fallback(req: IdeasRequest) -> IdeasResponse:
    """Generate curated birthday celebration fallback."""
    vibe = req.vibe or "Festive"
    cap_vibe = vibe.capitalize()
    themes = [f"{cap_vibe} Rooftop Glow with neon script signs", *BIRTHDAY_FALLBACK_THEMES]
    return IdeasResponse(
        themes=themes,
        menu_ideas=_build_dietary_menu("birthday", req.dietary),
        activities=list(BIRTHDAY_FALLBACK_ACTIVITIES),
        decor_tips=list(BIRTHDAY_FALLBACK_DECOR),
        personal_touches=list(BIRTHDAY_FALLBACK_PERSONAL_TOUCHES),
        source="fallback",
    )


def _build_community_fallback(req: IdeasRequest) -> IdeasResponse:
    """Generate curated community festival fallback."""
    vibe = req.vibe or "Vibrant"
    cap_vibe = vibe.capitalize()
    themes = [f"{cap_vibe} Community Heritage & Craft Fair", *COMMUNITY_FALLBACK_THEMES]
    return IdeasResponse(
        themes=themes,
        menu_ideas=_build_dietary_menu("community", req.dietary),
        activities=list(COMMUNITY_FALLBACK_ACTIVITIES),
        decor_tips=list(COMMUNITY_FALLBACK_DECOR),
        personal_touches=list(COMMUNITY_FALLBACK_PERSONAL_TOUCHES),
        source="fallback",
    )


def get_fallback_ideas(req: IdeasRequest) -> IdeasResponse:
    """Return context-aware ideas fallback by event type, vibe, and dietary."""
    e_type = req.event_type.lower()
    if "wedding" in e_type:
        return _build_wedding_fallback(req)
    if "birthday" in e_type:
        return _build_birthday_fallback(req)
    return _build_community_fallback(req)


def get_fallback_chat(plan_context: str, question: str) -> ChatRefineResponse:
    """Return fallback conversational response constrained to event planning."""
    q_lower = question.lower()
    for keywords, response_text in CHAT_DISPATCH_RULES:
        if any(k in q_lower for k in keywords):
            return ChatRefineResponse(reply=response_text, source="fallback")

    default_reply = (
        f"For your event plan ({plan_context[:80]}...), focus on booking high-lead vendors "
        "early and locking your core headcount before ordering custom rentals or menu tastings."
    )
    return ChatRefineResponse(reply=default_reply, source="fallback")
