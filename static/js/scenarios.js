/**
 * EventCraft AI - Scenario Loader
 * Pre-configured event profiles for instant demonstration.
 */

import { SCENARIOS } from "./state.js";
import { updateNotesCounter, updatePerGuestCalculation, updatePrioritiesState } from "./form.js";
import { announceStatus } from "./utils.js";

/**
 * Load a pre-configured sample scenario into the form and submit.
 * @param {string} scenarioKey - Identifier matching a pre-defined scenario key.
 * @returns {void}
 */
export function loadScenario(scenarioKey) {
  const sc = SCENARIOS[scenarioKey];
  if (!sc) return;

  const radio = /** @type {HTMLInputElement|null} */ (
    document.querySelector(`input[name="event_type"][value="${sc.event_type}"]`)
  );
  if (radio) radio.checked = true;
  const typeSelect = /** @type {HTMLSelectElement|null} */ (document.getElementById("event_type"));
  if (typeSelect) typeSelect.value = sc.event_type;

  const dateInput = /** @type {HTMLInputElement|null} */ (document.getElementById("event_date"));
  if (dateInput) {
    const future = new Date();
    future.setDate(future.getDate() + sc.event_date_offset_days);
    dateInput.value = future.toISOString().split("T")[0];
    dateInput.setAttribute("aria-invalid", "false");
    const errDate = document.getElementById("error-date");
    if (errDate) errDate.setAttribute("hidden", "");
  }

  const guestInput = /** @type {HTMLInputElement|null} */ (document.getElementById("guest_count"));
  if (guestInput) {
    guestInput.value = String(sc.guest_count);
    guestInput.setAttribute("aria-invalid", "false");
    const errGuests = document.getElementById("error-guests");
    if (errGuests) errGuests.setAttribute("hidden", "");
  }

  const budgetInput = /** @type {HTMLInputElement|null} */ (document.getElementById("total_budget"));
  if (budgetInput) {
    budgetInput.value = String(sc.total_budget);
    budgetInput.setAttribute("aria-invalid", "false");
    const errBudget = document.getElementById("error-budget");
    if (errBudget) errBudget.setAttribute("hidden", "");
  }

  const vibeInput = /** @type {HTMLInputElement|null} */ (document.getElementById("vibe"));
  if (vibeInput) vibeInput.value = sc.vibe;
  const cityInput = /** @type {HTMLInputElement|null} */ (document.getElementById("city"));
  if (cityInput) cityInput.value = sc.city;

  const prioChips = /** @type {NodeListOf<HTMLInputElement>} */ (
    document.querySelectorAll('input[name="priorities_chip"]')
  );
  prioChips.forEach((chip) => {
    chip.checked = sc.priorities.includes(chip.value);
  });
  updatePrioritiesState();

  const dietaryChips = /** @type {NodeListOf<HTMLInputElement>} */ (
    document.querySelectorAll('input[name="dietary"]')
  );
  dietaryChips.forEach((chip) => {
    chip.checked = sc.dietary.includes(chip.value);
  });

  const notesArea = /** @type {HTMLTextAreaElement|null} */ (document.getElementById("custom_notes"));
  if (notesArea) {
    notesArea.value = sc.notes;
    updateNotesCounter();
  }

  updatePerGuestCalculation();
  announceStatus(`Loaded ${scenarioKey.replace("-", " ")} scenario. Generating plan.`);
  const form = document.getElementById("event-plan-form");
  if (form) form.dispatchEvent(new Event("submit"));
}

/**
 * Bind listeners to sample scenario buttons.
 * @returns {void}
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
