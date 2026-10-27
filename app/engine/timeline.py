"""Pure deterministic timeline generation engine."""

from datetime import date, datetime, timedelta

from app.schemas import EventTimeline, EventType, MilestoneItem, TimelineScheduleItem


def format_clock_time(base_dt: datetime, offset_hours: float) -> str:
    """Format time string after adding fractional offset hours."""
    target = base_dt + timedelta(hours=offset_hours)
    return target.strftime("%I:%M %p")


def _wedding_early_items(base_dt: datetime) -> list[TimelineScheduleItem]:
    """Generate early ceremony and arrival blocks for wedding."""
    return [
        TimelineScheduleItem(
            time=format_clock_time(base_dt, -2.0),
            title="Vendor Arrival & Venue Setup",
            description="Florals, catering prep, sound check, lighting inspection",
            responsible="Coordinator & Vendors",
        ),
        TimelineScheduleItem(
            time=format_clock_time(base_dt, 0.0),
            title="Guest Arrival & Welcome Refreshments",
            description="Background acoustic music, welcome drinks, usher seating",
            responsible="Ushers / Host",
        ),
        TimelineScheduleItem(
            time=format_clock_time(base_dt, 0.5),
            title="Ceremony",
            description="Processional, vows, ring exchange, and recessional",
            responsible="Officiant & Couple",
        ),
    ]


def _wedding_reception_items(base_dt: datetime, dur: float) -> list[TimelineScheduleItem]:
    """Generate reception and evening blocks for wedding."""
    return [
        TimelineScheduleItem(
            time=format_clock_time(base_dt, 1.2),
            title="Cocktail Hour & Photos",
            description="Passed hors d'oeuvres, signature cocktails, family portraits",
            responsible="Photographer & Catering",
        ),
        TimelineScheduleItem(
            time=format_clock_time(base_dt, 2.2),
            title="Dinner & Toasts",
            description="Grand entrance, dinner service, emotional speeches",
            responsible="Emcee & Catering",
        ),
        TimelineScheduleItem(
            time=format_clock_time(base_dt, 3.5),
            title="First Dance & Open Dance Floor",
            description="Special dances followed by party music",
            responsible="DJ / Band",
        ),
        TimelineScheduleItem(
            time=format_clock_time(base_dt, dur),
            title="Grand Send-off & Pack Down",
            description="Sparkler / bubble send-off, rental load-out",
            responsible="Coordinator & Tear-down Team",
        ),
    ]


def _get_wedding_schedule(base_dt: datetime, dur: float) -> list[TimelineScheduleItem]:
    """Generate day-of schedule blocks for weddings."""
    return _wedding_early_items(base_dt) + _wedding_reception_items(base_dt, dur)


def _get_birthday_schedule(base_dt: datetime, dur: float) -> list[TimelineScheduleItem]:
    """Generate day-of schedule blocks for birthdays."""
    return [
        TimelineScheduleItem(
            time=format_clock_time(base_dt, -1.0),
            title="Venue Access & Decor Setup",
            description="Balloons, banner placement, photobooth prep, cake delivery",
            responsible="Host & Decorator",
        ),
        TimelineScheduleItem(
            time=format_clock_time(base_dt, 0.0),
            title="Guest Arrival & Welcome Mixer",
            description="Welcome drinks, playlist running, photo station open",
            responsible="Host",
        ),
        TimelineScheduleItem(
            time=format_clock_time(base_dt, 0.8),
            title="Food Service & Refreshments",
            description="Main buffet / food stations open",
            responsible="Catering / Host",
        ),
        TimelineScheduleItem(
            time=format_clock_time(base_dt, 2.0),
            title="Games & Main Entertainment",
            description="Trivia, party games, or live performance",
            responsible="Party Host / Entertainer",
        ),
        TimelineScheduleItem(
            time=format_clock_time(base_dt, 3.0),
            title="Cake Cutting & Toasts",
            description="Birthday song, birthday wish, cake serving",
            responsible="Host & Guests",
        ),
        TimelineScheduleItem(
            time=format_clock_time(base_dt, dur),
            title="Wrap Up & Favor Distribution",
            description="Gift collection, farewell to guests, venue clearing",
            responsible="Host & Family",
        ),
    ]


def _get_community_schedule(base_dt: datetime, dur: float) -> list[TimelineScheduleItem]:
    """Generate day-of schedule blocks for community events."""
    return [
        TimelineScheduleItem(
            time=format_clock_time(base_dt, -2.0),
            title="Site Staging & Volunteer Briefing",
            description="PA check, booth setups, safety walk-through, volunteer vests",
            responsible="Organizers & Volunteer Leads",
        ),
        TimelineScheduleItem(
            time=format_clock_time(base_dt, 0.0),
            title="Gates Open & Registration",
            description="Info booth open, welcome announcements, maps distribution",
            responsible="Welcome Volunteers",
        ),
        TimelineScheduleItem(
            time=format_clock_time(base_dt, 0.5),
            title="Opening Ceremony & Keynote",
            description="Community leader welcome remarks, sponsor acknowledgment",
            responsible="Lead Emcee",
        ),
        TimelineScheduleItem(
            time=format_clock_time(base_dt, 1.5),
            title="Workshops, Booths & Food Trucks",
            description="Interactive booths, local food vendors, games",
            responsible="Activity Coordinators",
        ),
        TimelineScheduleItem(
            time=format_clock_time(base_dt, dur - 0.5),
            title="Closing Remarks & Community Thanks",
            description="Raffle winners, awards, closing ceremony",
            responsible="Event Director",
        ),
        TimelineScheduleItem(
            time=format_clock_time(base_dt, dur),
            title="Tear Down & Litter Sweep",
            description="Tear down tents, pack sound gear, leave-no-trace sweep",
            responsible="Clean-up Crew",
        ),
    ]


def build_day_schedule(
    start_time_str: str, duration_hours: float, event_type: EventType
) -> list[TimelineScheduleItem]:
    """Build day-of event schedule based on event type and start time."""
    try:
        parsed_time = datetime.strptime(start_time_str, "%H:%M")
    except ValueError:
        parsed_time = datetime.strptime("16:00", "%H:%M")

    base_dt = datetime(2026, 1, 1, parsed_time.hour, parsed_time.minute)
    if event_type == EventType.WEDDING:
        return _get_wedding_schedule(base_dt, duration_hours)
    if event_type == EventType.BIRTHDAY:
        return _get_birthday_schedule(base_dt, duration_hours)
    return _get_community_schedule(base_dt, duration_hours)


def _early_milestones() -> list[MilestoneItem]:
    """Generate milestones for 3 to 12 months out."""
    return [
        MilestoneItem(
            timeframe="12-6 Months Out",
            days_before=180,
            title="Vision, Venue & Core Budget",
            action_items=[
                "Finalize overall budget and primary guest estimate",
                "Tour and book venue with deposit",
                "Reserve priority vendors (caterer, lead entertainment)",
            ],
        ),
        MilestoneItem(
            timeframe="3-4 Months Out",
            days_before=90,
            title="Design, Details & Invitations",
            action_items=[
                "Send formal invitations and track RSVPs",
                "Confirm menu tasting and dietary accommodations",
                "Finalize visual theme, decor rentals, and lighting",
            ],
        ),
    ]


def _final_milestones() -> list[MilestoneItem]:
    """Generate countdown milestones for the final month."""
    return [
        MilestoneItem(
            timeframe="1 Month Out",
            days_before=30,
            title="Logistics & Confirmations",
            action_items=[
                "Confirm headcounts with catering and venue",
                "Finalize day-of run of show with all vendors",
                "Create seating charts and print signage/programs",
            ],
        ),
        MilestoneItem(
            timeframe="1 Week Out",
            days_before=7,
            title="Final Countdown & Packs",
            action_items=[
                "Prepare vendor final balance payments and tips",
                "Assemble emergency kit (tape, sewing kit, chargers, meds)",
                "Conduct final run-through rehearsal",
            ],
        ),
    ]


def build_milestones(target_date: date) -> list[MilestoneItem]:
    """Generate countdown planning milestones leading up to the event."""
    return _early_milestones() + _final_milestones()


def create_event_timeline(
    event_date: date, start_time: str, duration_hours: float, event_type: EventType
) -> EventTimeline:
    """Create complete timeline object with day schedule and milestones."""
    return EventTimeline(
        day_schedule=build_day_schedule(start_time, duration_hours, event_type),
        milestones=build_milestones(event_date),
    )
