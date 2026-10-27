"""Curated context-aware deterministic fallback generators for ideas and chat."""


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
            f"Interactive street taco bar with carnitas, jackfruit, and cilantro lime rice ({labels})",
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
    return IdeasResponse(
        themes=[
            f"{vibe.capitalize()} Garden Romance with ambient taper candles",
            f"Timeless {vibe.capitalize()} Minimalism with architectural floral installations",
            f"{vibe.capitalize()} Starlight Soirée with suspended twinkling fairy lights",
        ],
        menu_ideas=_build_dietary_menu("wedding", req.dietary),
        activities=[
            "Vintage audio guestbook telephone for voice message recordings",
            "Golden hour couple portrait session during the cocktail hour",
            "Interactive late-night acoustic sing-along around fire pits",
        ],
        decor_tips=[
            "Hanging cascading floral cloud above the head table",
            "Warm amber perimeter uplighting and soft chiffon drapery",
            "Calligraphy etched acrylic welcome easel with gold leaf accents",
        ],
        personal_touches=[
            "Hand-bound vows booklets crafted on artisanal cotton paper",
            "Locally sourced artisanal honey or olive oil favor bottles",
        ],
        source="fallback",
    )


def _build_birthday_fallback(req: IdeasRequest) -> IdeasResponse:
    """Generate curated birthday celebration fallback."""
    vibe = req.vibe or "Festive"
    return IdeasResponse(
        themes=[
            f"{vibe.capitalize()} Rooftop Glow with neon script signs",
            "Retro Velvet Lounge with throwback vinyl DJ set",
            "Chic Celestial Midnight with metallic accents and mood lighting",
        ],
        menu_ideas=_build_dietary_menu("birthday", req.dietary),
        activities=[
            "Speed-trivia game highlighting funny moments from the honoree's life",
            "Instant Polaroid photo wall where guests peg photos with personal notes",
            "Cake cutting countdown with indoor cold-spark fountain effects",
        ],
        decor_tips=[
            "Organic cascading balloon garland with eucalyptus sprigs",
            "Mirror photo station with customized dry-erase milestone stats",
            "Color-coordinated illuminated marquee numbers celebrating the age",
        ],
        personal_touches=[
            "Custom signature cocktail named after the honoree's favorite memory",
            "Personalized soundtrack playlist curated collaboratively with guests",
        ],
        source="fallback",
    )


def _build_community_fallback(req: IdeasRequest) -> IdeasResponse:
    """Generate curated community festival fallback."""
    vibe = req.vibe or "Vibrant"
    return IdeasResponse(
        themes=[
            f"{vibe.capitalize()} Community Heritage & Craft Fair",
            "Green Horizons Eco-Festival with solar stage and maker workshops",
            "Neighborhood Arts & Flavors Bazaar highlighting grassroots creators",
        ],
        menu_ideas=_build_dietary_menu("community", req.dietary),
        activities=[
            "Community collaborative paint-by-numbers outdoor mural",
            "Live acoustic stage spotlighting youth musicians and spoken word",
            "DIY seed-bomb and pollinator planting workshop for all ages",
        ],
        decor_tips=[
            "Weather-resistant upcycled fabric pennant flags strung between trees",
            "Stenciled wooden directional signs with clear universal symbols",
            "Chalk art hopscotch and greeting pathways leading to entry gates",
        ],
        personal_touches=[
            "Community time capsule box to be opened at next year's anniversary",
            "Commemorative commemorative badge or seed packet for each visitor",
        ],
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
    off_topic = any(k in q_lower for k in ("python", "code", "hack", "math", "stock", "president"))
    if off_topic:
        reply = (
            "I specialize exclusively in event planning! I can assist with your budget, "
            "timelines, catering accommodations, vendor vetting, and design ideas. "
            "What event details would you like to review?"
        )
    elif any(k in q_lower for k in ("budget", "cost", "save", "cheap", "price")):
        reply = (
            "To trim costs without hurting the guest experience, shift 10% from floral decor "
            "to catering, choose in-season local produce, and ask your venue about off-peak hours."
        )
    elif any(k in q_lower for k in ("timeline", "time", "hour", "schedule", "buffer")):
        reply = (
            "Always include a 30-minute buffer before key moments like grand entrances or "
            "speeches. Photographers typically need 45 minutes for formal group portraits."
        )
    else:
        reply = (
            f"For your event plan ({plan_context[:80]}...), focus on booking high-lead vendors "
            "early and locking your core headcount before ordering custom rentals or menu tastings."
        )
    return ChatRefineResponse(reply=reply, source="fallback")
