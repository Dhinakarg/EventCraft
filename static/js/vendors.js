/**
 * EventCraft AI - Vendor Checklist Tab Renderer
 * Interactive booking statuses, progress tracking, budget caps, and interview prompts.
 */

import { state } from "./state.js";
import { announceStatus, createEl, createSvgIcon, formatCurrency, formatFriendlyDate } from "./utils.js";

/**
 * Render Vendor Tab with progress bar, status select (To do/Contacted/Booked), urgency badge,
 * interview questions in collapsible <details>, and localStorage persistence.
 * @param {Array} vendors 
 * @param {HTMLElement} container 
 */
export function renderVendorsTab(vendors, container) {
  if (!container || !vendors) return;
  container.replaceChildren();

  const planDate = state.currentPlan ? state.currentPlan.event_date : "default";
  const planType = state.currentPlan ? state.currentPlan.event_type : "type";
  const storageKey = `eventcraft_vendor_status_${planDate}_${planType}`;
  let savedStatuses = {};
  try {
    savedStatuses = JSON.parse(localStorage.getItem(storageKey) || "{}");
  } catch {
    savedStatuses = {};
  }

  // Progress Bar Wrapper
  const progressWrapper = createEl("div", {
    className: "vendor-progress-wrapper",
    role: "region",
    aria: { label: "Vendor booking checklist progress" },
  });
  const progressHeader = createEl("div", { className: "vendor-progress-header" });
  const progressTitle = createEl("span", {}, ["Vendor Booking Progress:"]);
  const progressText = createEl("span", { id: "vendor-progress-label" });
  progressHeader.appendChild(progressTitle);
  progressHeader.appendChild(progressText);
  progressWrapper.appendChild(progressHeader);

  const track = createEl("div", { className: "progress-bar-track" });
  const bar = createEl("div", {
    id: "vendor-progress-fill",
    className: "progress-bar-fill",
    role: "progressbar",
    aria: { valuemin: "0", valuemax: "100" },
  });
  track.appendChild(bar);
  progressWrapper.appendChild(track);
  container.appendChild(progressWrapper);

  const updateProgress = () => {
    const total = vendors.length;
    let booked = 0;
    for (const v of vendors) {
      if (savedStatuses[v.category] === "booked") booked++;
    }
    const pct = total > 0 ? Math.round((booked / total) * 100) : 0;
    progressText.textContent = `${booked} of ${total} Booked (${pct}%)`;
    bar.style.width = `${pct}%`;
    bar.setAttribute("aria-valuenow", String(pct));
  };
  updateProgress();

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // Render cards for each vendor
  for (const v of vendors) {
    const card = createEl("div", { className: "vendor-card" });

    // Header: Category, Budget Cap, Status Select
    const cardHeader = createEl("div", { className: "vendor-card-header" });
    const infoCol = createEl("div", {}, [
      createEl("div", { className: "vendor-category-title" }, [v.category]),
      createEl("div", { className: "vendor-cap-text" }, [
        `Budget Cap: ${formatCurrency(v.budget_cap, state.currentPlan?.budget?.currency || "INR")}`,
      ]),
    ]);

    const select = createEl("select", {
      className: "vendor-status-select",
      aria: { label: `Booking status for ${v.category}` },
    });
    select.appendChild(createEl("option", { value: "todo" }, ["To do"]));
    select.appendChild(createEl("option", { value: "contacted" }, ["Contacted"]));
    select.appendChild(createEl("option", { value: "booked" }, ["Booked"]));

    select.value = savedStatuses[v.category] || "todo";

    select.addEventListener("change", () => {
      savedStatuses[v.category] = select.value;
      try {
        localStorage.setItem(storageKey, JSON.stringify(savedStatuses));
      } catch {
        // storage disabled or quota
      }
      updateProgress();
      announceStatus(`${v.category} marked as ${select.options[select.selectedIndex].text}.`);
    });

    cardHeader.appendChild(infoCol);
    cardHeader.appendChild(select);
    card.appendChild(cardHeader);

    // Deadline & Urgency row
    const deadlineDate = new Date(v.booking_deadline + "T00:00:00");
    const diffDays = Math.ceil((deadlineDate - today) / (1000 * 60 * 60 * 24));
    let urgencyClass = "urgency-ontrack";
    let urgencyText = "On track";
    let urgencyIcon = "check";

    if (diffDays < 0) {
      urgencyClass = "urgency-overdue";
      urgencyText = "Overdue";
      urgencyIcon = "warning";
    } else if (diffDays <= 7) {
      urgencyClass = "urgency-thisweek";
      urgencyText = "This week";
      urgencyIcon = "timeline";
    }

    const urgencyBadge = createEl("span", { className: `urgency-badge ${urgencyClass}` }, [
      createSvgIcon(urgencyIcon),
      ` ${urgencyText}`,
    ]);

    const deadlineRow = createEl("div", { className: "vendor-deadline-row" }, [
      createEl("span", {}, [`Book by ${formatFriendlyDate(v.booking_deadline)}`]),
      urgencyBadge,
    ]);
    card.appendChild(deadlineRow);

    // Collapsible Interview Questions
    const details = createEl("details", { className: "vendor-questions-details" });
    const summary = createEl("summary", { className: "vendor-questions-summary" }, [
      `Interview Questions (${(v.questions_to_ask || []).length})`,
    ]);
    details.appendChild(summary);

    const qList = createEl("ul", { className: "vendor-questions-list" });
    for (const q of v.questions_to_ask || []) {
      qList.appendChild(createEl("li", {}, [q]));
    }
    details.appendChild(qList);
    card.appendChild(details);

    container.appendChild(card);
  }
}
