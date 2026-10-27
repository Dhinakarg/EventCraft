/**
 * EventCraft AI - Form Interactions & Validation
 * Inline validation, live per-guest calculations, character limits, and responsive collapse.
 */

import { formatCurrency } from "./utils.js";

/**
 * Pure validation helper for future date.
 * @param {string} dateStr
 * @param {Date} [today]
 * @returns {boolean}
 */
export function isValidFutureDate(dateStr, today = new Date()) {
  if (!dateStr) return false;
  const selectedDate = new Date(dateStr);
  if (isNaN(selectedDate.getTime())) return false;
  const startOfToday = new Date(today);
  startOfToday.setHours(0, 0, 0, 0);
  return selectedDate > startOfToday;
}

/**
 * Pure validation helper for guest count (1 - 2,000).
 * @param {number|string} guests
 * @returns {boolean}
 */
export function isValidGuestCount(guests) {
  const num = parseInt(String(guests), 10);
  return !isNaN(num) && num >= 1 && num <= 2000;
}

/**
 * Pure validation helper for total budget (> 0).
 * @param {number|string} budget
 * @returns {boolean}
 */
export function isValidBudget(budget) {
  const num = parseFloat(String(budget));
  return !isNaN(num) && num > 0;
}

/**
 * Pure calculation helper for per-guest cost.
 * @param {number|string} budget
 * @param {number|string} guests
 * @returns {number|null}
 */
export function calculatePerGuest(budget, guests) {
  const b = parseFloat(String(budget));
  const g = parseInt(String(guests), 10);
  if (!isNaN(b) && b > 0 && !isNaN(g) && g > 0) {
    return Math.round(b / g);
  }
  return null;
}

/**
 * Validate a form input inline.
 * Returns { field, id, message } on error, or null if valid.
 * @param {string} fieldId
 * @returns {Object|null}
 */
export function validateField(fieldId) {
  if (fieldId === "event_date") {
    const input = document.getElementById("event_date");
    const err = document.getElementById("error-date");
    if (!input || !err) return null;

    if (!isValidFutureDate(input.value)) {
      err.removeAttribute("hidden");
      input.setAttribute("aria-invalid", "true");
      return { field: input, id: "event_date", message: "Event date must be a valid future date." };
    }
    err.setAttribute("hidden", "");
    input.setAttribute("aria-invalid", "false");
    return null;
  }

  if (fieldId === "guest_count") {
    const input = document.getElementById("guest_count");
    const err = document.getElementById("error-guests");
    if (!input || !err) return null;

    if (!isValidGuestCount(input.value)) {
      err.removeAttribute("hidden");
      input.setAttribute("aria-invalid", "true");
      return { field: input, id: "guest_count", message: "Guest count must be between 1 and 2,000." };
    }
    err.setAttribute("hidden", "");
    input.setAttribute("aria-invalid", "false");
    return null;
  }

  if (fieldId === "total_budget") {
    const input = document.getElementById("total_budget");
    const err = document.getElementById("error-budget");
    if (!input || !err) return null;

    if (!isValidBudget(input.value)) {
      err.removeAttribute("hidden");
      input.setAttribute("aria-invalid", "true");
      return { field: input, id: "total_budget", message: "Total budget must be greater than zero." };
    }
    err.setAttribute("hidden", "");
    input.setAttribute("aria-invalid", "false");
    return null;
  }

  return null;
}

/**
 * Update live "= ₹312 per guest" estimate under guests and budget.
 */
export function updatePerGuestCalculation() {
  const guestInput = document.getElementById("guest_count");
  const budgetInput = document.getElementById("total_budget");
  const calcAmount = document.getElementById("per-guest-amount");
  if (!guestInput || !budgetInput || !calcAmount) return;

  const perGuest = calculatePerGuest(budgetInput.value, guestInput.value);
  if (perGuest !== null) {
    calcAmount.textContent = `= ${formatCurrency(perGuest, "INR")} per guest`;
  } else {
    calcAmount.textContent = "= -- per guest";
  }
}

/**
 * Update live character counter for notes textarea (500 max).
 */
export function updateNotesCounter() {
  const notesArea = document.getElementById("custom_notes");
  const counter = document.getElementById("notes-counter");
  if (!notesArea || !counter) return;

  const max = 500;
  const len = notesArea.value.length;
  const remaining = Math.max(0, max - len);
  counter.textContent = `${remaining} characters left`;
  counter.classList.toggle("limit-near", remaining <= 50);
}

/**
 * Enforce max 3 priority chips, update live counter in aria-live region, and sync legacy select.
 */
export function updatePrioritiesState() {
  const chips = document.querySelectorAll('input[name="priorities_chip"]');
  const counter = document.getElementById("priority-counter");
  const legacySelect = document.getElementById("priorities");

  const checkedChips = Array.from(chips).filter((c) => c.checked);
  const count = checkedChips.length;

  if (counter) counter.textContent = `${count} of 3 selected`;

  chips.forEach((chip) => {
    const itemLabel = chip.closest(".chip-item");
    if (!chip.checked && count >= 3) {
      chip.disabled = true;
      if (itemLabel) itemLabel.classList.add("disabled");
    } else {
      chip.disabled = false;
      if (itemLabel) itemLabel.classList.remove("disabled");
    }
  });

  if (legacySelect) {
    const checkedValues = new Set(checkedChips.map((c) => c.value));
    Array.from(legacySelect.options).forEach((opt) => {
      opt.selected = checkedValues.has(opt.value);
    });
  }
}

/**
 * Bind form interactive listeners: calculation, counters, chips, blur validation, radio sync.
 */
export function initFormInteractions() {
  const guestInput = document.getElementById("guest_count");
  const budgetInput = document.getElementById("total_budget");
  if (guestInput) {
    guestInput.addEventListener("input", updatePerGuestCalculation);
    guestInput.addEventListener("change", updatePerGuestCalculation);
    guestInput.addEventListener("blur", () => validateField("guest_count"));
  }
  if (budgetInput) {
    budgetInput.addEventListener("input", updatePerGuestCalculation);
    budgetInput.addEventListener("change", updatePerGuestCalculation);
    budgetInput.addEventListener("blur", () => validateField("total_budget"));
  }
  updatePerGuestCalculation();

  const notesArea = document.getElementById("custom_notes");
  if (notesArea) {
    notesArea.addEventListener("input", updateNotesCounter);
    updateNotesCounter();
  }

  const prioChips = document.querySelectorAll('input[name="priorities_chip"]');
  prioChips.forEach((chip) => chip.addEventListener("change", updatePrioritiesState));
  updatePrioritiesState();

  const typeRadios = document.querySelectorAll('input[name="event_type"]');
  const legacyTypeSelect = document.getElementById("event_type");
  typeRadios.forEach((radio) => {
    radio.addEventListener("change", () => {
      if (radio.checked && legacyTypeSelect) legacyTypeSelect.value = radio.value;
    });
  });

  const dateInput = document.getElementById("event_date");
  if (dateInput) {
    dateInput.addEventListener("blur", () => validateField("event_date"));
    dateInput.addEventListener("input", () => {
      if (dateInput.getAttribute("aria-invalid") === "true") validateField("event_date");
    });
  }
}

/**
 * Collapse form into a summary bar on tablet/mobile screens after plan generation.
 * @param {Object} plan 
 */
export function updateMobileFormCollapse(plan) {
  const summaryBar = document.getElementById("form-summary-bar");
  const form = document.getElementById("event-plan-form");
  const summaryText = document.getElementById("summary-text");
  if (!summaryBar || !form || !summaryText) return;

  const formattedType = plan.event_type.charAt(0).toUpperCase() + plan.event_type.slice(1);
  const formattedCost = formatCurrency(plan.total_budget, plan.currency);
  summaryText.textContent = `${formattedType} · ${plan.guest_count} guests · ${formattedCost} · ${plan.event_date}`;

  if (window.innerWidth < 1024) {
    summaryBar.removeAttribute("hidden");
    form.setAttribute("hidden", "");
    const heading = document.getElementById("results-heading");
    if (heading) {
      heading.setAttribute("tabindex", "-1");
      heading.focus();
    }
  }
}
