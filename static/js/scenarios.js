/**
 * EventCraft AI - Scenario Loader
 * Pre-configured event profiles for instant demonstration.
 */

import { SCENARIOS } from "./state.js";
import { updateNotesCounter, updatePerGuestCalculation, updatePrioritiesState } from "./form.js";
import { announceStatus } from "./utils.js";

/**
 * Load a pre-configured sample scenario into the form and submit.
 * @param {string} scenarioKey 
 */
export function loadScenario(scenarioKey) {
  const sc = SCENARIOS[scenarioKey];
  if (!sc) return;

  const radio = document.querySelector(`input[name="event_type"][value="${sc.event_type}"]`);
  if (radio) {
    radio.checked = true;
    const legacySelect = document.getElementById("event_type");
    if (legacySelect) legacySelect.value = sc.event_type;
  }

  const dateInput = document.getElementById("event_date");
  if (dateInput) {
    const future = new Date();
    future.setDate(future.getDate() + sc.event_date_offset_days);
    dateInput.value = future.toISOString().split("T")[0];
    dateInput.setAttribute("aria-invalid", "false");
    const errDate = document.getElementById("error-date");
    if (errDate) errDate.setAttribute("hidden", "");
  }

  const guestInput = document.getElementById("guest_count");
  if (guestInput) {
    guestInput.value = String(sc.guest_count);
    guestInput.setAttribute("aria-invalid", "false");
    const errGuests = document.getElementById("error-guests");
    if (errGuests) errGuests.setAttribute("hidden", "");
  }

  const budgetInput = document.getElementById("total_budget");
  if (budgetInput) {
    budgetInput.value = String(sc.total_budget);
    budgetInput.setAttribute("aria-invalid", "false");
    const errBudget = document.getElementById("error-budget");
    if (errBudget) errBudget.setAttribute("hidden", "");
  }

  const vibeInput = document.getElementById("vibe");
  if (vibeInput) vibeInput.value = sc.vibe;
  const cityInput = document.getElementById("city");
  if (cityInput) cityInput.value = sc.city;

  const prioChips = document.querySelectorAll('input[name="priorities_chip"]');
  prioChips.forEach((chip) => {
    chip.checked = sc.priorities.includes(chip.value);
  });
  updatePrioritiesState();

  const dietaryChips = document.querySelectorAll('input[name="dietary"]');
  dietaryChips.forEach((chip) => {
    chip.checked = sc.dietary.includes(chip.value);
  });

  const notesArea = document.getElementById("custom_notes");
  if (notesArea) {
    notesArea.value = sc.notes;
    updateNotesCounter();
  }

  updatePerGuestCalculation();
  announceStatus(`Loaded ${scenarioKey.replace("-", " ")} scenario. Generating plan.`);
  document.getElementById("event-plan-form").dispatchEvent(new Event("submit"));
}

/**
 * Bind listeners to sample scenario buttons.
 */
export function initScenarioButtons() {
  const scenarioBtns = document.querySelectorAll(".scenario-btn");
  scenarioBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const key = btn.getAttribute("data-scenario");
      if (key) loadScenario(key);
    });
  });
}
