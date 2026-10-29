/**
 * EventCraft AI - Plan Generation Coordinator
 * Handles form submission, API call, skeleton toggling, and delegating tab rendering.
 */

import { renderBudgetTab } from "./budget.js";
import { updateMobileFormCollapse, validateField } from "./form.js";
import { renderIdeasTab } from "./ideas.js";
import { renderKpiCards } from "./kpis.js";
import { state } from "./state.js";
import { renderTimelineTab } from "./timeline.js";
import { announceStatus, createSvgIcon } from "./utils.js";
import { renderVendorsTab } from "./vendors.js";
import { renderWarnings } from "./warnings.js";

/**
 * Submit plan form to POST /api/plan with skeleton loading, error summary, and full render.
 * @param {Event} e - Form submit event.
 * @param {Function} [onPlanSuccess] - Optional callback executed on successful plan creation.
 * @returns {Promise<void>}
 */
export async function onPlanSubmit(e, onPlanSuccess) {
  e.preventDefault();

  const errors = [
    validateField("event_date"),
    validateField("guest_count"),
    validateField("total_budget"),
  ].filter(Boolean);

  const summaryBox = document.getElementById("form-error-summary");
  const summaryList = document.getElementById("error-summary-list");

  if (errors.length > 0) {
    if (summaryList) {
      summaryList.replaceChildren();
      errors.forEach((err) => {
        const li = document.createElement("li");
        const a = document.createElement("a");
        a.href = `#${err.id}`;
        a.textContent = err.message;
        a.addEventListener("click", (evt) => {
          evt.preventDefault();
          err.field.focus();
        });
        li.appendChild(a);
        summaryList.appendChild(li);
      });
    }
    if (summaryBox) {
      summaryBox.removeAttribute("hidden");
      summaryBox.focus();
    }
    announceStatus(`Form submission error: ${errors.length} issue${errors.length > 1 ? "s" : ""} need correction.`);
    return;
  }

  if (summaryBox) {
    summaryBox.setAttribute("hidden", "");
    if (summaryList) summaryList.replaceChildren();
  }

  const btn = document.getElementById("btn-submit-plan");
  btn.replaceChildren(createSvgIcon("spinner", "icon-spin"), " Crafting your plan…");
  btn.disabled = true;
  announceStatus("Crafting your plan. Please wait.");

  const emptyState = document.getElementById("results-empty-state");
  const resultsContent = document.getElementById("results-content");
  const skeleton = document.getElementById("results-skeleton");

  if (emptyState) emptyState.setAttribute("hidden", "");
  if (resultsContent) resultsContent.setAttribute("hidden", "");
  if (skeleton) skeleton.removeAttribute("hidden");

  let priorities = [];
  const checkedChips = document.querySelectorAll('input[name="priorities_chip"]:checked');
  if (checkedChips.length > 0) {
    priorities = Array.from(checkedChips).map((c) => c.value).slice(0, 3);
  } else {
    const pSelect = document.getElementById("priorities");
    if (pSelect) {
      for (const opt of pSelect.selectedOptions) {
        if (opt.value && priorities.length < 3) priorities.push(opt.value);
      }
    }
  }

  const dietaryChips = document.querySelectorAll('input[name="dietary"]:checked');
  const dietary = Array.from(dietaryChips).map((c) => c.value);

  const checkedType = document.querySelector('input[name="event_type"]:checked');
  const eventType = checkedType ? checkedType.value : (document.getElementById("event_type")?.value || "wedding");

  const payload = {
    event_type: eventType,
    event_date: document.getElementById("event_date").value,
    guest_count: parseInt(document.getElementById("guest_count").value, 10),
    total_budget: parseFloat(document.getElementById("total_budget").value),
    currency: "INR",
    vibe: document.getElementById("vibe")?.value.trim() || "Modern",
    city: document.getElementById("city")?.value.trim() || "",
    priorities: priorities,
    dietary: dietary,
    notes: document.getElementById("custom_notes")?.value.trim() || "",
  };

  try {
    const res = await fetch("/api/plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Server returned ${res.status}`);
    }

    const plan = await res.json();
    state.currentPlan = plan;

    if (skeleton) skeleton.setAttribute("hidden", "");
    if (resultsContent) resultsContent.removeAttribute("hidden");

    renderKpiCards(plan);
    renderWarnings(plan.warnings, plan.timeline?.rush_warning, document.getElementById("warnings-container"));
    renderBudgetTab(plan.budget, document.getElementById("budget-output"));
    renderTimelineTab(plan.timeline, document.getElementById("timeline-output"));
    renderVendorsTab(plan.vendors, document.getElementById("vendors-output"));
    renderIdeasTab(plan.ideas, document.getElementById("ideas-output"));

    if (typeof onPlanSuccess === "function") {
      onPlanSuccess("budget");
    }
    updateMobileFormCollapse(plan);
    announceStatus("Event plan generated successfully! Displaying budget breakdown.");
  } catch (err) {
    if (skeleton) skeleton.setAttribute("hidden", "");
    if (!state.currentPlan && emptyState) emptyState.removeAttribute("hidden");
    alert(`Could not generate plan: ${err.message}`);
    announceStatus(`Error generating plan: ${err.message}`);
  } finally {
    btn.replaceChildren(createSvgIcon("bolt"), " Generate Plan");
    btn.disabled = false;
  }
}
