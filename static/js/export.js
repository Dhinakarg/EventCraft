/**
 * EventCraft AI - Plan Export Utilities
 * iCalendar (.ics) download and clipboard plain text copying.
 */

import { state } from "./state.js";
import { announceStatus } from "./utils.js";

/**
 * Download .ics timeline calendar file.
 * @returns {void}
 */
export function downloadIcs() {
  if (!state.currentPlan) {
    announceStatus("Please generate an event plan first before downloading.");
    return;
  }
  const p = state.currentPlan;
  const url = `/api/export/ics?event_date=${p.event_date}&event_type=${p.event_type}&guest_count=${p.guest_count}&total_budget=${p.total_budget}&vibe=${encodeURIComponent(p.vibe)}`;
  window.location.href = url;
  announceStatus("Downloading iCalendar .ics timeline.");
}

/**
 * Copy plain text summary of plan to clipboard with "Copied!" confirmation.
 * @returns {void}
 */
export function copyPlanAsText() {
  if (!state.currentPlan) {
    announceStatus("Please generate an event plan first before copying.");
    return;
  }
  const p = state.currentPlan;
  let text = `EVENT PLAN SUMMARY\n--------------------\n`;
  text += `Type: ${p.event_type}\nDate: ${p.event_date}\nGuests: ${p.guest_count}\nBudget: ${p.currency} ${p.total_budget}\nCity: ${p.city}\nVibe: ${p.vibe}\n\n`;
  text += `BUDGET BREAKDOWN:\n`;
  for (const item of p.budget.items) {
    text += `- ${item.category}: ${p.currency} ${item.allocated_amount} (${item.percentage}%)\n`;
  }
  text += `Contingency Fund: ${p.currency} ${p.budget.contingency_fund}\n\n`;
  text += `TIMELINE TASKS:\n`;
  for (const t of p.timeline.tasks) {
    text += `- ${t.due_date}: ${t.title} [${t.priority}]\n`;
  }

  const btn = document.getElementById("btn-copy-text");
  const btnText = document.getElementById("copy-btn-text");
  const copyIcon = document.getElementById("copy-icon");

  navigator.clipboard.writeText(text).then(() => {
    if (btnText && copyIcon) {
      btnText.textContent = "Copied!";
      if (btn) btn.classList.add("btn-copied");
      copyIcon.querySelector("use")?.setAttribute("href", "#icon-check");
      setTimeout(() => {
        btnText.textContent = "Copy as text";
        if (btn) btn.classList.remove("btn-copied");
        copyIcon.querySelector("use")?.setAttribute("href", "#icon-copy");
      }, 2000);
    }
    announceStatus("Plan summary copied to clipboard!");
  }).catch(() => {
    announceStatus("Clipboard access denied. Please copy manually.");
  });
}
