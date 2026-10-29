/**
 * EventCraft AI - Form Interactions & Event Listeners
 * Live calculations, character counters, priority constraints, and responsive collapse.
 */

import {
  calculatePerGuest,
  isValidBudget,
  isValidFutureDate,
  isValidGuestCount,
  validateField,
} from "./form_validation.js";
import { formatCurrency } from "./utils.js";

export {
  calculatePerGuest,
  isValidBudget,
  isValidFutureDate,
  isValidGuestCount,
  validateField,
};

/**
 * Update live "= ₹312 per guest" estimate under guests and budget fields.
 * @returns {void}
 */
export function updatePerGuestCalculation() {
  const guestInput = /** @type {HTMLInputElement|null} */ (document.getElementById("guest_count"));
  const budgetInput = /** @type {HTMLInputElement|null} */ (document.getElementById("total_budget"));
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
 * @returns {void}
 */
export function updateNotesCounter() {
  const notesArea = /** @type {HTMLTextAreaElement|null} */ (document.getElementById("custom_notes"));
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
 * @returns {void}
 */
export function updatePrioritiesState() {
  const chips = /** @type {NodeListOf<HTMLInputElement>} */ (
    document.querySelectorAll('input[name="priorities_chip"]')
  );
  const counter = document.getElementById("priority-counter");
  const legacySelect = /** @type {HTMLSelectElement|null} */ (document.getElementById("priorities"));

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
 * Bind form interactive listeners: calculation, counters, chips, blur validation, and number input wheel lock.
 * @returns {void}
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
  const legacyTypeSelect = /** @type {HTMLSelectElement|null} */ (document.getElementById("event_type"));
  typeRadios.forEach((radio) => {
    radio.addEventListener("change", () => {
      const radioInput = /** @type {HTMLInputElement} */ (radio);
      if (radioInput.checked && legacyTypeSelect) legacyTypeSelect.value = radioInput.value;
    });
  });

  const dateInput = document.getElementById("event_date");
  if (dateInput) {
    dateInput.addEventListener("blur", () => validateField("event_date"));
    dateInput.addEventListener("input", () => {
      if (dateInput.getAttribute("aria-invalid") === "true") validateField("event_date");
    });
  }

  // Prevent mouse wheel from inadvertently changing values in number inputs
  const numberInputs = document.querySelectorAll('input[type="number"]');
  numberInputs.forEach((input) => {
    input.addEventListener("wheel", (e) => {
      e.preventDefault();
      const el = /** @type {HTMLInputElement} */ (input);
      el.blur();
    }, { passive: false });
  });

  document.addEventListener("wheel", () => {
    const active = /** @type {HTMLInputElement|null} */ (document.activeElement);
    if (active && active.type === "number") {
      active.blur();
    }
  }, { passive: true });
}

/**
 * Collapse form into a summary bar on tablet/mobile screens after plan generation.
 * @param {{ event_type: string, total_budget: number, currency: string, guest_count: number, event_date: string }} plan - Generated event plan object.
 * @returns {void}
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
