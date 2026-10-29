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
 * @param {string} tabKey - Unique key of the tab to activate.
 * @returns {void}
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
 * @param {KeyboardEvent} e - Keyboard event triggered on tab button.
 * @returns {void}
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
 * Persist and apply selected color theme.
 * @param {string} theme
 */
function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  try {
    localStorage.setItem("eventcraft_theme", theme);
  } catch { /* storage disabled */ }
  const isDark = theme === "dark";
  const btn = document.getElementById("theme-btn");
  const text = document.getElementById("theme-text");
  if (btn) btn.setAttribute("aria-pressed", isDark ? "true" : "false");
  if (text) text.textContent = isDark ? "Light Mode" : "Dark Mode";
}

/**
 * Persist and apply root text display size.
 * @param {string} size
 */
function applyFontSize(size) {
  document.documentElement.setAttribute("data-font-size", size);
  try {
    localStorage.setItem("eventcraft_font_size", size);
  } catch { /* storage disabled */ }
  document.querySelectorAll(".btn-size").forEach((btn) => {
    const active = btn.getAttribute("data-size") === size;
    btn.classList.toggle("active", active);
    btn.setAttribute("aria-pressed", active ? "true" : "false");
  });
  const sel = document.getElementById("font-size-select");
  if (sel) sel.value = size;
}

/**
 * Initialize theme, font size, and responsive collapse controls.
 */
function initAccessibilityControls() {
  let initialTheme = "light";
  try {
    const saved = localStorage.getItem("eventcraft_theme");
    const sysDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    initialTheme = saved === "light" || saved === "dark" ? saved : (sysDark ? "dark" : "light");
  } catch { /* fallback */ }
  applyTheme(initialTheme);

  let initialSize = "normal";
  try {
    const saved = localStorage.getItem("eventcraft_font_size");
    if (saved === "normal" || saved === "large" || saved === "xl") initialSize = saved;
  } catch { /* fallback */ }
  applyFontSize(initialSize);

  document.querySelectorAll(".btn-size").forEach((btn) => {
    btn.addEventListener("click", () => {
      const size = btn.getAttribute("data-size") || "normal";
      applyFontSize(size);
      announceStatus(`Text size set to ${btn.getAttribute("aria-label") || size}.`);
    });
  });

  const fontSelect = document.getElementById("font-size-select");
  if (fontSelect) fontSelect.addEventListener("change", (e) => applyFontSize(e.target.value));

  const themeBtn = document.getElementById("theme-btn");
  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      const cur = document.documentElement.getAttribute("data-theme") || "light";
      const next = cur === "dark" ? "light" : "dark";
      applyTheme(next);
      announceStatus(`Theme switched to ${next} mode.`);
    });
  }

  const btnEdit = document.getElementById("btn-edit-details");
  if (btnEdit) {
    btnEdit.addEventListener("click", () => {
      const bar = document.getElementById("form-summary-bar");
      const form = document.getElementById("event-plan-form");
      if (bar) bar.setAttribute("hidden", "");
      if (form) {
        form.removeAttribute("hidden");
        form.scrollIntoView({ behavior: "smooth", block: "start" });
      }
      const first = document.getElementById("event_type");
      if (first) first.focus();
      announceStatus("Form opened. You can now edit your event details.");
    });
  }
}

/**
 * Set minimum selectable event date to tomorrow.
 */
function initDefaults() {
  const dateInput = document.getElementById("event_date");
  if (dateInput) {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    dateInput.min = tomorrow.toISOString().split("T")[0];
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
