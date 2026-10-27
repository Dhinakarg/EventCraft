"""Typed fallback blueprint data and canned conversational responses."""

WEDDING_FALLBACK_ACTIVITIES: tuple[str, ...] = (
    "Vintage audio guestbook telephone for voice message recordings",
    "Golden hour couple portrait session during the cocktail hour",
    "Interactive late-night acoustic sing-along around fire pits",
)

WEDDING_FALLBACK_DECOR: tuple[str, ...] = (
    "Hanging cascading floral cloud above the head table",
    "Warm amber perimeter uplighting and soft chiffon drapery",
    "Calligraphy etched acrylic welcome easel with gold leaf accents",
)

WEDDING_FALLBACK_PERSONAL_TOUCHES: tuple[str, ...] = (
    "Hand-bound vows booklets crafted on artisanal cotton paper",
    "Locally sourced artisanal honey or olive oil favor bottles",
)

BIRTHDAY_FALLBACK_THEMES: tuple[str, ...] = (
    "Retro Velvet Lounge with throwback vinyl DJ set",
    "Chic Celestial Midnight with metallic accents and mood lighting",
)

BIRTHDAY_FALLBACK_ACTIVITIES: tuple[str, ...] = (
    "Speed-trivia game highlighting funny moments from the honoree's life",
    "Instant Polaroid photo wall where guests peg photos with personal notes",
    "Cake cutting countdown with indoor cold-spark fountain effects",
)

BIRTHDAY_FALLBACK_DECOR: tuple[str, ...] = (
    "Organic cascading balloon garland with eucalyptus sprigs",
    "Mirror photo station with customized dry-erase milestone stats",
    "Color-coordinated illuminated marquee numbers celebrating the age",
)

BIRTHDAY_FALLBACK_PERSONAL_TOUCHES: tuple[str, ...] = (
    "Custom signature cocktail named after the honoree's favorite memory",
    "Personalized soundtrack playlist curated collaboratively with guests",
)

COMMUNITY_FALLBACK_THEMES: tuple[str, ...] = (
    "Green Horizons Eco-Festival with solar stage and maker workshops",
    "Neighborhood Arts & Flavors Bazaar highlighting grassroots creators",
)

COMMUNITY_FALLBACK_ACTIVITIES: tuple[str, ...] = (
    "Community collaborative paint-by-numbers outdoor mural",
    "Live acoustic stage spotlighting youth musicians and spoken word",
    "DIY seed-bomb and pollinator planting workshop for all ages",
)

COMMUNITY_FALLBACK_DECOR: tuple[str, ...] = (
    "Weather-resistant upcycled fabric pennant flags strung between trees",
    "Stenciled wooden directional signs with clear universal symbols",
    "Chalk art hopscotch and greeting pathways leading to entry gates",
)

COMMUNITY_FALLBACK_PERSONAL_TOUCHES: tuple[str, ...] = (
    "Community time capsule box to be opened at next year's anniversary",
    "Commemorative commemorative badge or seed packet for each visitor",
)

OFF_TOPIC_REPLY: str = (
    "I specialize exclusively in event planning! I can assist with your budget, "
    "timelines, catering accommodations, vendor vetting, and design ideas. "
    "What event details would you like to review?"
)

BUDGET_REPLY: str = (
    "To trim costs without hurting the guest experience, shift 10% from floral decor "
    "to catering, choose in-season local produce, and ask your venue about off-peak hours."
)

TIMELINE_REPLY: str = (
    "Always include a 30-minute buffer before key moments like grand entrances or "
    "speeches. Photographers typically need 45 minutes for formal group portraits."
)

OFF_TOPIC_KEYWORDS: tuple[str, ...] = ("python", "code", "hack", "math", "stock", "president")
BUDGET_KEYWORDS: tuple[str, ...] = ("budget", "cost", "save", "cheap", "price")
TIMELINE_KEYWORDS: tuple[str, ...] = ("timeline", "time", "hour", "schedule", "buffer")

CHAT_DISPATCH_RULES: tuple[tuple[tuple[str, ...], str], ...] = (
    (OFF_TOPIC_KEYWORDS, OFF_TOPIC_REPLY),
    (BUDGET_KEYWORDS, BUDGET_REPLY),
    (TIMELINE_KEYWORDS, TIMELINE_REPLY),
)
