/**
 * EventCraft AI - Form Validation Utilities
 * Pure validation rules and DOM validation helper.
 */

/**
 * Pure validation helper for future date.
 * @param {string} dateStr - Date string in YYYY-MM-DD format.
 * @param {Date} [today] - Optional reference date (defaults to current date).
 * @returns {boolean} True if date is valid and strictly in the future.
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
 * @param {number|string} guests - Number of invited guests.
 * @returns {boolean} True if guest count is an integer between 1 and 2,000.
 */
export function isValidGuestCount(guests) {
  const num = parseInt(String(guests), 10);
  return !isNaN(num) && num >= 1 && num <= 2000;
}

/**
 * Pure validation helper for total budget (> 0).
 * @param {number|string} budget - Event total budget amount.
 * @returns {boolean} True if budget is a positive number.
 */
export function isValidBudget(budget) {
  const num = parseFloat(String(budget));
  return !isNaN(num) && num > 0;
}

/**
 * Pure calculation helper for per-guest cost.
 * @param {number|string} budget - Total budget amount.
 * @param {number|string} guests - Number of guests.
 * @returns {number|null} Rounded per-guest cost or null if inputs are invalid.
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
 * Validate a form input inline against business constraints.
 * @param {string} fieldId - ID of the field to validate.
 * @returns {{ field: HTMLElement, id: string, message: string } | null} Error object if invalid, or null if valid.
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
