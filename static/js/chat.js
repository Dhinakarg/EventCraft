/**
 * EventCraft AI - Interactive Chat Assistant
 * Safe message appending, topic refinement, and suggested question chips.
 */

import { state } from "./state.js";
import { announceStatus, createEl, createSvgIcon } from "./utils.js";

/**
 * Append chat message to log safely using textContent.
 * @param {string} role - Message sender role ('user' or 'bot').
 * @param {string} text - Chat message body content.
 * @returns {void}
 */
export function appendChatMessage(role, text) {
  const log = document.getElementById("chat-conversation");
  if (!log) return;

  const msg = createEl("div", {
    className: `chat-msg ${role === "user" ? "chat-msg-user" : "chat-msg-bot"}`,
    role: "article",
    aria: { label: role === "user" ? "You" : "Planner" },
  }, [text]);
  log.appendChild(msg);
  log.scrollTop = log.scrollHeight;
}

/**
 * Send chat question to POST /api/chat with disabled state while sending.
 * @param {Event} e - Form submission event.
 * @returns {Promise<void>}
 */
export async function onChatSubmit(e) {
  e.preventDefault();
  const input = /** @type {HTMLInputElement|null} */ (document.getElementById("chat-input"));
  const sendBtn = /** @type {HTMLButtonElement|null} */ (document.getElementById("chat-send-btn"));
  if (!input) return;
  const query = input.value.trim();
  if (!query) return;

  appendChatMessage("user", query);
  input.value = "";
  input.disabled = true;
  if (sendBtn) {
    sendBtn.disabled = true;
    sendBtn.replaceChildren(createSvgIcon("spinner", "icon-spin"), " Sending...");
  }
  announceStatus("Sending question to event planner.");

  const p = state.currentPlan;
  const ctx = p
    ? `${p.event_type} for ${p.guest_count} guests with ${p.currency} ${p.total_budget} budget in ${p.city}`
    : "General event planning";

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ plan_context: ctx, question: query }),
    });

    if (!res.ok) throw new Error("Chat request failed");
    const data = await res.json();
    appendChatMessage("bot", data.reply);
    announceStatus(`Planner replied: ${data.reply}`);
  } catch {
    appendChatMessage("bot", "I am having trouble answering right now. Please try again.");
  } finally {
    input.disabled = false;
    if (sendBtn) {
      sendBtn.disabled = false;
      sendBtn.replaceChildren(createSvgIcon("chat"), " Send");
    }
    input.focus();
  }
}

/**
 * Bind listeners to chat suggested question chips.
 * @returns {void}
 */
export function initChatChips() {
  const chips = document.querySelectorAll(".chat-chip");
  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const input = /** @type {HTMLInputElement|null} */ (document.getElementById("chat-input"));
      const form = document.getElementById("chat-query-form");
      if (input && form && chip.textContent) {
        input.value = chip.textContent.trim();
        form.dispatchEvent(new Event("submit"));
      }
    });
  });
}
