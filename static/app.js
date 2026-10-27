/**
 * EventCraft AI - Client Application Entrypoint (ES Module)
 * Strict WCAG 2.1 AA, proper ARIA tabs pattern, and zero innerHTML.
 */

import { appendChatMessage, initChatChips, onChatSubmit } from "./js/chat.js";
import { copyPlanAsText, downloadIcs } from "./js/export.js";
import { initFormInteractions } from "./js/form.js";
import { onPlanSubmit } from "./js/planner.js";
import { initScenarioButtons } from "./js/scenarios.js";
import { state } from "./js/state.js";
import { announceStatus } from "./js/utils.js";

/**
 * Handle Tab Activation and proper ARIA states.
 * @param {string} tabKey 
 */
export function activateTab(tabKey) {
  const tabs = document.querySelectorAll(".tab-btn");
  const panels = document.querySelectorAll(".tab-content");

  tabs.forEach((t) => {
    const isTarget = t.getAttribute("data-tab") === tabKey;
    t.setAttribute("aria-selected", isTarget ? "true" : "false");
    t.tabIndex = isTarget ? 0 : -1;
  });

  panels.forEach((p) => {
    const isTarget = p.id === `panel-${tabKey}`;
    if (isTarget) {
      p.classList.add("active");
      p.removeAttribute("hidden");
    } else {
      p.classList.remove("active");
      p.setAttribute("hidden", "");
    }
  });
}

/**
 * ARIA Tabs Keyboard Navigation (Left, Right, Up, Down, Home, End).
 * @param {KeyboardEvent} e 
 */
export function onTabKeydown(e) {
  const tabs = Array.from(document.querySelectorAll(".tab-btn"));
  const curr = tabs.indexOf(document.activeElement);
  if (curr === -1) return;

  let nextIdx = null;
  if (e.key === "ArrowRight" || e.key === "ArrowDown") {
    nextIdx = (curr + 1) % tabs.length;
  } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
    nextIdx = (curr - 1 + tabs.length) % tabs.length;
  } else if (e.key === "Home") {
    nextIdx = 0;
  } else if (e.key === "End") {
    nextIdx = tabs.length - 1;
  }

  if (nextIdx !== null) {
    e.preventDefault();
    tabs[nextIdx].focus();
    activateTab(tabs[nextIdx].getAttribute("data-tab"));
  }
}

/**
 * Initialize theme, font size, and responsive collapse controls.
 */
function initAccessibilityControls() {
  const sizeBtns = document.querySelectorAll(".btn-size");
  sizeBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const size = btn.getAttribute("data-size");
      document.documentElement.setAttribute("data-font-size", size);
      sizeBtns.forEach((b) => {
        const isActive = b === btn;
        b.classList.toggle("active", isActive);
        b.setAttribute("aria-pressed", isActive ? "true" : "false");
      });
      announceStatus(`Text size set to ${btn.getAttribute("aria-label") || size}.`);
    });
  });

  const fontSelect = document.getElementById("font-size-select");
  if (fontSelect) {
    fontSelect.addEventListener("change", (e) => {
      document.documentElement.setAttribute("data-font-size", e.target.value);
    });
  }

  const themeBtn = document.getElementById("theme-btn");
  const themeText = document.getElementById("theme-text");
  if (themeBtn) {
    const isDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    themeBtn.setAttribute("aria-pressed", isDark ? "true" : "false");
    if (themeText) themeText.textContent = isDark ? "Light Mode" : "Dark Mode";

    themeBtn.addEventListener("click", () => {
      const cur = document.documentElement.getAttribute("data-theme");
      const next = cur === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      const isNowDark = next === "dark";
      themeBtn.setAttribute("aria-pressed", isNowDark ? "true" : "false");
      if (themeText) themeText.textContent = isNowDark ? "Light Mode" : "Dark Mode";
      announceStatus(`Theme switched to ${next} mode.`);
    });
  }

  const btnEdit = document.getElementById("btn-edit-details");
  if (btnEdit) {
    btnEdit.addEventListener("click", () => {
      const summaryBar = document.getElementById("form-summary-bar");
      const form = document.getElementById("event-plan-form");
      if (summaryBar) summaryBar.setAttribute("hidden", "");
      if (form) form.removeAttribute("hidden");
      const firstInput = document.getElementById("event_type");
      if (firstInput) firstInput.focus();
    });
  }
}

/**
 * Set default event date in future.
 */
function initDefaults() {
  const dateInput = document.getElementById("event_date");
  if (dateInput && !dateInput.value) {
    const future = new Date();
    future.setDate(future.getDate() + 180);
    dateInput.value = future.toISOString().split("T")[0];
  }
}

// Setup Event Listeners on DOMContentLoaded
document.addEventListener("DOMContentLoaded", () => {
  initAccessibilityControls();
  initDefaults();
  initFormInteractions();
  initScenarioButtons();
  initChatChips();

  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => activateTab(btn.getAttribute("data-tab")));
  });
  const tablist = document.querySelector(".tabs-list");
  if (tablist) tablist.addEventListener("keydown", onTabKeydown);

  document.getElementById("event-plan-form").addEventListener("submit", (e) => {
    onPlanSubmit(e, activateTab);
  });
  document.getElementById("chat-query-form").addEventListener("submit", onChatSubmit);

  document.getElementById("btn-export-ics").addEventListener("click", downloadIcs);
  document.getElementById("btn-print-plan").addEventListener("click", () => {
    window.print();
  });
  document.getElementById("btn-copy-text").addEventListener("click", copyPlanAsText);

  appendChatMessage("bot", state.chatMessages[0].text);
});
