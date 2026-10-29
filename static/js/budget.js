/**
 * EventCraft AI - Budget Tab Renderer
 * SVG Donut Chart, visual legend, accessible table, and responsive wrapper.
 */

import { createEl, createSvgIcon, formatCurrency } from "./utils.js";

const CHART_COLORS = [
  "#2563eb",
  "#059669",
  "#d97706",
  "#7c3aed",
  "#db2777",
  "#0891b2",
  "#ea580c",
  "#4f46e5",
];

/**
 * Render Budget Tab with SVG Donut Chart, visual legend, hidden chart summary, and itemized table.
 * @param {Object} budget - Budget response data object.
 * @param {HTMLElement} container - DOM container element.
 * @returns {void}
 */
export function renderBudgetTab(budget, container) {
  if (!container || !budget) return;
  container.replaceChildren();

  // Visually hidden summary of chart for screen readers
  const srSummary = createEl("div", { className: "sr-status" }, [
    `Budget breakdown donut chart summary: Total ${formatCurrency(budget.total_budget, budget.currency)}. ${budget.items.map((i) => `${i.category}: ${i.percentage}% (${formatCurrency(i.allocated_amount, budget.currency)})`).join(", ")}.`,
  ]);
  container.appendChild(srSummary);

  // Donut chart container
  const donutCard = createEl("div", {
    className: "donut-container",
    role: "region",
    aria: { label: "Budget allocation donut chart and category legend" },
  });

  // SVG Donut
  const svgWrapper = createEl("div", { className: "donut-svg-wrapper" });
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 240 240");
  svg.setAttribute("class", "donut-svg");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-hidden", "true");

  const trackCircle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  trackCircle.setAttribute("cx", "120");
  trackCircle.setAttribute("cy", "120");
  trackCircle.setAttribute("r", "80");
  trackCircle.setAttribute("fill", "transparent");
  trackCircle.setAttribute("stroke", "var(--border)");
  trackCircle.setAttribute("stroke-width", "26");
  svg.appendChild(trackCircle);

  const C = 2 * Math.PI * 80; // ~502.65
  let accumulatedPct = 0;

  budget.items.forEach((item, idx) => {
    const color = CHART_COLORS[idx % CHART_COLORS.length];
    const sliceCircle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    sliceCircle.setAttribute("cx", "120");
    sliceCircle.setAttribute("cy", "120");
    sliceCircle.setAttribute("r", "80");
    sliceCircle.setAttribute("fill", "transparent");
    sliceCircle.setAttribute("stroke", color);
    sliceCircle.setAttribute("stroke-width", "26");

    const dashLen = Math.max(1, (item.percentage / 100) * C);
    const offset = - (accumulatedPct / 100) * C;
    sliceCircle.setAttribute("stroke-dasharray", `${dashLen} ${C}`);
    sliceCircle.setAttribute("stroke-dashoffset", String(offset));
    sliceCircle.setAttribute("transform", "rotate(-90 120 120)");
    svg.appendChild(sliceCircle);

    accumulatedPct += item.percentage;
  });

  // Central total in donut
  const centerTextGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
  const labelText = document.createElementNS("http://www.w3.org/2000/svg", "text");
  labelText.setAttribute("x", "120");
  labelText.setAttribute("y", "112");
  labelText.setAttribute("text-anchor", "middle");
  labelText.setAttribute("font-size", "11");
  labelText.setAttribute("fill", "var(--text-muted)");
  labelText.setAttribute("font-weight", "600");
  labelText.textContent = "TOTAL BUDGET";
  centerTextGroup.appendChild(labelText);

  const amountText = document.createElementNS("http://www.w3.org/2000/svg", "text");
  amountText.setAttribute("x", "120");
  amountText.setAttribute("y", "134");
  amountText.setAttribute("text-anchor", "middle");
  amountText.setAttribute("font-size", "17");
  amountText.setAttribute("font-weight", "800");
  amountText.setAttribute("fill", "var(--text)");
  amountText.textContent = formatCurrency(budget.total_budget, budget.currency);
  centerTextGroup.appendChild(amountText);
  svg.appendChild(centerTextGroup);

  svgWrapper.appendChild(svg);
  donutCard.appendChild(svgWrapper);

  // Donut legend
  const legend = createEl("div", { className: "donut-legend" });
  budget.items.forEach((item, idx) => {
    const color = CHART_COLORS[idx % CHART_COLORS.length];
    const legendItem = createEl("div", { className: "donut-legend-item" }, [
      createEl("div", { className: "donut-legend-label" }, [
        createEl("span", { className: "donut-color-dot", style: `background-color: ${color};` }),
        createEl("span", {}, [item.category]),
      ]),
      createEl("div", { style: "font-weight: 700;" }, [
        `${formatCurrency(item.allocated_amount, budget.currency)} (${item.percentage}%)`,
      ]),
    ]);
    legend.appendChild(legendItem);
  });
  donutCard.appendChild(legend);
  container.appendChild(donutCard);

  // Itemized Table
  const tableTitle = createEl("h3", { className: "section-subtitle" }, [
    createSvgIcon("chart"),
    " Itemized Budget Breakdown",
  ]);
  container.appendChild(tableTitle);

  const table = createEl("table", { className: "budget-table", aria: { label: "Budget allocations by category" } });
  const thead = createEl("thead", {}, [
    createEl("tr", {}, [
      createEl("th", { scope: "col" }, ["Category"]),
      createEl("th", { scope: "col" }, ["Allocated Amount"]),
      createEl("th", { scope: "col" }, ["Share"]),
      createEl("th", { scope: "col" }, ["Priority"]),
    ]),
  ]);
  table.appendChild(thead);

  const tbody = createEl("tbody");
  for (const item of budget.items) {
    const isPriority = item.priority && item.priority.toLowerCase() === "high";
    const priorityCell = createEl("td", {}, [
      isPriority ? createEl("span", { className: "badge-priority" }, ["Priority"]) : (item.priority || "Standard"),
    ]);

    const tr = createEl("tr", {}, [
      createEl("td", { style: "font-weight: 600;" }, [item.category]),
      createEl("td", {}, [formatCurrency(item.allocated_amount, budget.currency)]),
      createEl("td", {}, [`${item.percentage}%`]),
      priorityCell,
    ]);
    tbody.appendChild(tr);
  }
  table.appendChild(tbody);

  const tableWrapper = createEl("div", {
    className: "table-responsive",
    tabIndex: 0,
    role: "region",
    aria: { label: "Itemized Budget Breakdown Table" },
  }, [table]);
  container.appendChild(tableWrapper);
}
