/**
 * EventCraft AI - Timeline Tab Renderer
 * Backward-scheduled milestone timeline grouped by phase with critical filter toggle.
 */

import { state } from "./state.js";
import { announceStatus, createEl, createSvgIcon, formatFriendlyDate } from "./utils.js";

/**
 * Render Vertical Timeline grouped by phase with friendly dates and critical filter toggle.
 * @param {Object} timeline 
 * @param {HTMLElement} container 
 */
export function renderTimelineTab(timeline, container) {
  if (!container || !timeline) return;
  container.replaceChildren();

  const isCriticalOnly = Boolean(state.timelineCriticalOnly);

  // Filter toolbar
  const controls = createEl("div", { className: "timeline-controls" });
  const filterBtn = createEl("button", {
    type: "button",
    id: "timeline-filter-critical",
    className: `btn btn-sm ${isCriticalOnly ? "btn-primary" : "btn-outline"}`,
    aria: { pressed: isCriticalOnly ? "true" : "false" },
  }, [
    createSvgIcon("filter"),
    isCriticalOnly ? " Showing critical only" : " Show only critical",
  ]);

  filterBtn.addEventListener("click", () => {
    state.timelineCriticalOnly = !state.timelineCriticalOnly;
    renderTimelineTab(timeline, container);
    announceStatus(state.timelineCriticalOnly ? "Filtered to show only critical tasks." : "Showing all timeline tasks.");
  });
  controls.appendChild(filterBtn);

  const allTasks = timeline.tasks || [];
  const filteredTasks = isCriticalOnly
    ? allTasks.filter((t) => t.is_critical || (t.priority && t.priority.toLowerCase() === "critical"))
    : allTasks;

  const countBadge = createEl("span", { className: "timeline-count-badge" }, [
    `Showing ${filteredTasks.length} of ${allTasks.length} tasks`,
  ]);
  controls.appendChild(countBadge);
  container.appendChild(controls);

  // Group by phase
  const phases = {};
  for (const t of filteredTasks) {
    const phaseKey = t.phase || "Milestones";
    if (!phases[phaseKey]) phases[phaseKey] = [];
    phases[phaseKey].push(t);
  }

  const phaseKeys = Object.keys(phases);
  if (phaseKeys.length === 0) {
    container.appendChild(createEl("p", { style: "padding: 20px; text-align: center; color: var(--text-muted);" }, [
      "No critical tasks found for this timeline.",
    ]));
    return;
  }

  for (const phase of phaseKeys) {
    const phaseGroup = createEl("div", { className: "timeline-phase-group" });
    const phaseHeading = createEl("h4", { className: "phase-heading" }, [
      createSvgIcon("timeline"),
      phase,
    ]);
    phaseGroup.appendChild(phaseHeading);

    const taskList = createEl("div", { role: "list" });
    for (const task of phases[phase]) {
      const friendlyDate = formatFriendlyDate(task.due_date);
      const isCritical = task.is_critical || (task.priority && task.priority.toLowerCase() === "critical");
      const isDeferred = task.is_deferred || (task.tags && task.tags.includes("deferred"));

      const badgeGroup = createEl("div", { className: "timeline-badge-group" }, [
        createEl("span", { className: "badge" }, [task.priority || "Standard"]),
        isCritical ? createEl("span", { className: "badge badge-critical" }, ["Critical"]) : null,
        isDeferred ? createEl("span", { className: "badge badge-deferred" }, ["Deferred"]) : null,
      ].filter(Boolean));

      const item = createEl("div", { className: "timeline-item", role: "listitem" }, [
        createEl("div", { className: "timeline-meta" }, [
          `Due: ${friendlyDate} (${task.days_before_event} days before event)`,
        ]),
        createEl("div", { className: "timeline-title" }, [task.title]),
        badgeGroup,
      ]);
      taskList.appendChild(item);
    }
    phaseGroup.appendChild(taskList);
    container.appendChild(phaseGroup);
  }
}
