/**
 * EventCraft AI - KPI Cards Renderer
 */

import { formatCurrency, formatFriendlyDate } from "./utils.js";

/**
 * Render the 4 KPI cards at the top of results.
 * @param {Object} plan 
 */
export function renderKpiCards(plan) {
  const b = plan.budget;
  const budgetVal = document.getElementById("kpi-val-budget");
  const budgetSub = document.getElementById("kpi-sub-budget");
  if (budgetVal) budgetVal.textContent = formatCurrency(b.total_budget, b.currency);
  if (budgetSub) budgetSub.textContent = `${b.currency || "INR"} Allocation`;

  const guestVal = document.getElementById("kpi-val-guest");
  const guestSub = document.getElementById("kpi-sub-guest");
  if (guestVal) guestVal.textContent = `${formatCurrency(b.per_guest_cost, b.currency)} / guest`;
  if (guestSub) guestSub.textContent = `${plan.guest_count} guests planned`;

  const contVal = document.getElementById("kpi-val-contingency");
  const contSub = document.getElementById("kpi-sub-contingency");
  if (contVal) contVal.textContent = formatCurrency(b.contingency_fund, b.currency);
  if (contSub) contSub.textContent = `${b.contingency_percentage}% reserved buffer`;

  const daysVal = document.getElementById("kpi-val-days");
  const daysSub = document.getElementById("kpi-sub-date");
  if (daysVal && plan.event_date) {
    const eventTime = new Date(plan.event_date + "T00:00:00").getTime();
    const nowTime = new Date().getTime();
    const days = Math.max(0, Math.ceil((eventTime - nowTime) / (1000 * 60 * 60 * 24)));
    daysVal.textContent = `${days} Days`;
    if (daysSub) daysSub.textContent = formatFriendlyDate(plan.event_date);
  }
}
