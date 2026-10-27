/**
 * EventCraft AI - Core Application Logic
 * Accessible interaction handling, state management, and tab switching.
 */

import {
  fetchCreativeIdeas,
  generateMasterPlan,
  sendChatMessage,
} from "./api.js";
import {
  appendChatMessage,
  el,
  renderBudget,
  renderCreativeIdeas,
  renderTimeline,
  renderVendors,
  renderWarnings,
} from "./dom.js";

// Application State
const state = {
  currentPlan: null,
  chatHistory: [
    {
      role: "assistant",
      content:
        "Welcome to EventCraft AI! Ask me about timeline buffers, vendor vetting, or budget optimization.",
    },
  ],
  isSubmitting: false,
};

// Preset configurations for instant exploration with future dates
const PRESETS = {
  wedding: {
    event_type: "wedding",
    event_name: "Eleanor & James Coastal Wedding",
    guest_count: 85,
    total_budget: 28000,
    event_date: "2027-06-18",
    vibe: "Coastal Elegance",
    city: "Carmel-by-the-Sea",
    dietary: ["Vegetarian", "Gluten-Free"],
    priorities: ["venue", "food"],
    notes: "Sunset oceanfront ceremony followed by terrace reception with local seafood.",
  },
  birthday: {
    event_type: "birthday",
    event_name: "Maya's 30th Rooftop Glow Party",
    guest_count: 45,
    total_budget: 4500,
    event_date: "2026-12-05",
    vibe: "Retro Neon",
    city: "Austin",
    dietary: ["Nut-Free"],
    priorities: ["entertainment", "decor"],
    notes: "Signature cocktails, live vinyl DJ, and illuminated polaroid photobooth.",
  },
  community: {
    event_type: "community",
    event_name: "Oakridge Neighborhood Harvest Festival",
    guest_count: 400,
    total_budget: 12000,
    event_date: "2027-10-09",
    vibe: "Rustic Eco-Friendly",
    city: "Portland",
    dietary: ["Vegan", "Halal"],
    priorities: ["venue", "entertainment"],
    notes: "Community craft booths, artisan food trucks, youth music stage.",
  },
};

/**
 * Populate form inputs with specific preset data.
 * @param {Object} data 
 */
function applyPreset(data) {
  document.getElementById("event_type").value = data.event_type;
  document.getElementById("event_name").value = data.event_name;
  document.getElementById("guest_count").value = data.guest_count;
  document.getElementById("budget_total").value = data.total_budget;
  document.getElementById("budget_range").value = data.total_budget;
  document.getElementById("event_date").value = data.event_date;
  document.getElementById("vibe").value = data.vibe;
  document.getElementById("city").value = data.city || "";
  document.getElementById("custom_notes").value = data.notes;

  updateCharCounts();
  updateBudgetPreviews();
}

/**
 * Update live character counters for validated text inputs.
 */
function updateCharCounts() {
  const nameInput = document.getElementById("event_name");
  const notesInput = document.getElementById("custom_notes");
  document.getElementById("name_count").textContent = `${nameInput.value.length}/120`;
  document.getElementById("notes_count").textContent = `${notesInput.value.length}/500`;
}

/**
 * Sync budget slider, number input, and per-guest estimate preview.
 */
function updateBudgetPreviews() {
  const total = parseFloat(document.getElementById("budget_total").value) || 0;
  const guests = parseInt(document.getElementById("guest_count").value, 10) || 1;
  const perGuest = Math.round(total / Math.max(guests, 1));
  document.getElementById("per_guest_preview").textContent = `~₹${perGuest.toLocaleString("en-IN")}/guest`;
}

/**
 * Activate a tab panel by ID and handle aria states.
 * @param {string} targetTabId 
 */
function activateTab(targetTabId) {
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");

  tabButtons.forEach((btn) => {
    const isTarget = btn.getAttribute("data-tab") === targetTabId;
    btn.setAttribute("aria-selected", isTarget ? "true" : "false");
    btn.tabIndex = isTarget ? 0 : -1;
  });

  tabPanels.forEach((panel) => {
    const isTarget = panel.id === `panel-${targetTabId}`;
    if (isTarget) {
      panel.classList.add("active");
    } else {
      panel.classList.remove("active");
    }
  });
}

/**
 * Handle Tab Keyboard Navigation (WCAG 2.1 AA Tablist Pattern).
 * @param {KeyboardEvent} e 
 */
function handleTabKeydown(e) {
  const tabButtons = Array.from(document.querySelectorAll(".tab-btn"));
  const currentIndex = tabButtons.indexOf(document.activeElement);
  if (currentIndex === -1) return;

  let nextIndex = null;
  if (e.key === "ArrowRight") {
    nextIndex = (currentIndex + 1) % tabButtons.length;
  } else if (e.key === "ArrowLeft") {
    nextIndex = (currentIndex - 1 + tabButtons.length) % tabButtons.length;
  } else if (e.key === "Home") {
    nextIndex = 0;
  } else if (e.key === "End") {
    nextIndex = tabButtons.length - 1;
  }

  if (nextIndex !== null) {
    e.preventDefault();
    tabButtons[nextIndex].focus();
    activateTab(tabButtons[nextIndex].getAttribute("data-tab"));
  }
}

/**
 * Gather form values into an untrusted request payload.
 * @returns {Object}
 */
function getFormData() {
  const selectedPriorities = [];
  const prioritySelect = document.getElementById("priorities");
  if (prioritySelect) {
    for (const opt of prioritySelect.selectedOptions) {
      if (opt.value && selectedPriorities.length < 3) {
        selectedPriorities.push(opt.value);
      }
    }
  }

  return {
    event_type: document.getElementById("event_type").value,
    event_date: document.getElementById("event_date").value,
    guest_count: parseInt(document.getElementById("guest_count").value, 10),
    total_budget: parseFloat(document.getElementById("budget_total").value),
    currency: "INR",
    city: document.getElementById("city") ? document.getElementById("city").value.trim() : "",
    vibe: document.getElementById("vibe") ? document.getElementById("vibe").value.trim() : "Modern",
    dietary: ["Vegetarian"],
    priorities: selectedPriorities.length ? selectedPriorities : ["venue", "food"],
    notes: document.getElementById("custom_notes").value.trim(),
  };
}

/**
 * Submit form and generate full plan deterministically.
 * @param {Event} e 
 */
async function onPlanSubmit(e) {
  e.preventDefault();
  if (state.isSubmitting) return;

  const btn = document.getElementById("btn-generate-plan");
  const originalText = btn.textContent;
  state.isSubmitting = true;
  btn.replaceChildren(el("span", { className: "spinner" }), " Generating Plan...");
  btn.disabled = true;

  try {
    const payload = getFormData();
    const plan = await generateMasterPlan(payload);
    state.currentPlan = plan;

    // Render into each tab container
    renderBudget(plan.budget, document.getElementById("budget-container"));
    renderWarnings(plan.warnings, document.getElementById("budget-container"));
    renderTimeline(plan.timeline, document.getElementById("timeline-container"));
    renderVendors(plan.vendors, document.getElementById("vendors-container"));

    // Update active plan banner
    const planSummary = document.getElementById("plan-summary-badge");
    if (planSummary) {
      planSummary.textContent = `${plan.vibe} ${plan.event_type} • ${plan.guest_count} Guests • ₹${plan.total_budget.toLocaleString("en-IN")}`;
    }

    activateTab("budget");
  } catch (err) {
    alert(`Could not generate plan: ${err.message}`);
  } finally {
    state.isSubmitting = false;
    btn.textContent = originalText;
    btn.disabled = false;
  }
}

/**
 * Request creative ideas for selected topic.
 */
async function onGenerateIdeas() {
  const btn = document.getElementById("btn-generate-ideas");
  const container = document.getElementById("ideas-output");

  const originalText = btn.textContent;
  btn.replaceChildren(el("span", { className: "spinner" }), " Crafting Ideas...");
  btn.disabled = true;

  try {
    const formData = getFormData();
    const req = {
      event_type: formData.event_type,
      vibe: formData.vibe || "Modern",
      dietary: formData.dietary || [],
      guest_count: formData.guest_count || 50,
      city: formData.city || "",
      notes: formData.notes || "",
    };

    const result = await fetchCreativeIdeas(req);
    renderCreativeIdeas(result, container);
  } catch (err) {
    container.replaceChildren(
      el("div", { className: "metric-card", style: "color: #f87171;" }, [
        `Error generating ideas: ${err.message}`,
      ])
    );
  } finally {
    btn.textContent = originalText;
    btn.disabled = false;
  }
}

/**
 * Send user message to chat co-planner.
 * @param {string} text 
 */
async function onSendChat(text) {
  if (!text || !text.trim()) return;

  const chatInput = document.getElementById("chat-input");
  const messagesContainer = document.getElementById("chat-messages");

  state.chatHistory.push({ role: "user", content: text.trim() });
  appendChatMessage("user", text.trim(), messagesContainer);
  chatInput.value = "";

  const typingIndicator = el(
    "div",
    { className: "chat-bubble bubble-assistant", id: "typing-indicator" },
    ["Thinking..."]
  );
  messagesContainer.appendChild(typingIndicator);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;

  const ctx = state.currentPlan
    ? `${state.currentPlan.event_type} for ${state.currentPlan.guest_count} guests with ₹${state.currentPlan.total_budget.toLocaleString("en-IN")} budget`
    : "General event planning";

  try {
    const response = await sendChatMessage(ctx, text.trim());
    typingIndicator.remove();
    state.chatHistory.push({ role: "assistant", content: response.reply });
    appendChatMessage("assistant", response.reply, messagesContainer);
  } catch (err) {
    typingIndicator.remove();
    appendChatMessage("assistant", `Sorry, I encountered an issue: ${err.message}`, messagesContainer);
  }
}

/**
 * Initialize theme toggle (dark/light) with local preference persistence.
 */
function initThemeToggle() {
  const toggleBtn = document.getElementById("theme-toggle");
  const currentTheme = localStorage.getItem("eventcraft-theme") || "dark";
  document.documentElement.setAttribute("data-theme", currentTheme);
  toggleBtn.textContent = currentTheme === "dark" ? "☀️ Light" : "🌙 Dark";

  toggleBtn.addEventListener("click", () => {
    const active = document.documentElement.getAttribute("data-theme");
    const next = active === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("eventcraft-theme", next);
    toggleBtn.textContent = next === "dark" ? "☀️ Light" : "🌙 Dark";
  });
}

/**
 * Setup default event listeners on DOMContentLoaded.
 */
document.addEventListener("DOMContentLoaded", () => {
  initThemeToggle();

  // Character counters
  const nameInput = document.getElementById("event_name");
  const notesInput = document.getElementById("custom_notes");
  if (nameInput) nameInput.addEventListener("input", updateCharCounts);
  if (notesInput) notesInput.addEventListener("input", updateCharCounts);

  // Budget slider sync
  const budgetInput = document.getElementById("budget_total");
  const budgetRange = document.getElementById("budget_range");
  const guestInput = document.getElementById("guest_count");

  budgetRange.addEventListener("input", () => {
    budgetInput.value = budgetRange.value;
    updateBudgetPreviews();
  });
  budgetInput.addEventListener("input", () => {
    budgetRange.value = budgetInput.value;
    updateBudgetPreviews();
  });
  guestInput.addEventListener("input", updateBudgetPreviews);

  // Preset buttons
  document.querySelectorAll(".pill-preset").forEach((btn) => {
    btn.addEventListener("click", () => {
      const presetKey = btn.getAttribute("data-preset");
      if (PRESETS[presetKey]) {
        applyPreset(PRESETS[presetKey]);
      }
    });
  });

  // Tab navigation
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => activateTab(btn.getAttribute("data-tab")));
  });
  const tabList = document.querySelector(".tabs-nav");
  if (tabList) tabList.addEventListener("keydown", handleTabKeydown);

  // Form submit
  document.getElementById("planner-form").addEventListener("submit", onPlanSubmit);

  // Creative Studio button
  document.getElementById("btn-generate-ideas").addEventListener("click", onGenerateIdeas);

  // Chat send & quick suggestions
  document.getElementById("btn-send-chat").addEventListener("click", () => {
    const input = document.getElementById("chat-input");
    onSendChat(input.value);
  });
  document.getElementById("chat-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      onSendChat(e.target.value);
    }
  });
  document.querySelectorAll(".btn-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      onSendChat(chip.textContent);
    });
  });

  // Load default wedding preset on start
  applyPreset(PRESETS.wedding);

  // Trigger initial plan generation so dashboard is immediately active and visually rich
  document.getElementById("planner-form").dispatchEvent(new Event("submit"));
});
