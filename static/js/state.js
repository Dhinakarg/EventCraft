/**
 * EventCraft AI - Shared Application State & Scenarios
 */

export const state = {
  currentPlan: null,
  chatMessages: [
    {
      role: "bot",
      text: "Hello! I am your EventCraft AI planner. How can I help refine your event details today?",
    },
  ],
};

export const SCENARIOS = {
  "tight-wedding": {
    event_type: "wedding",
    event_date_offset_days: 180,
    guest_count: 60,
    total_budget: 400000,
    vibe: "Rustic",
    city: "Jaipur",
    priorities: ["venue", "food", "photography"],
    dietary: ["Vegetarian", "Gluten-free"],
    notes: "Daytime garden celebration with buffet dining, acoustic music, and natural lighting.",
  },
  "milestone-birthday": {
    event_type: "birthday",
    event_date_offset_days: 90,
    guest_count: 40,
    total_budget: 150000,
    vibe: "Modern Minimalist",
    city: "Bengaluru",
    priorities: ["food", "entertainment", "decor"],
    dietary: ["Nut allergy"],
    notes: "Rooftop lounge gathering with craft cocktails, finger foods, and DJ.",
  },
  "community-fest": {
    event_type: "community",
    event_date_offset_days: 150,
    guest_count: 350,
    total_budget: 600000,
    vibe: "Garden Party",
    city: "Mumbai",
    priorities: ["venue", "entertainment", "other"],
    dietary: ["Vegan", "Halal"],
    notes: "Outdoor park festival with community art booths, food trucks, and acoustic stages.",
  },
};
