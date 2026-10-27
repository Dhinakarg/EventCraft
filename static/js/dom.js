/**
 * EventCraft AI - Safe DOM Manipulation Utility
 * Strictly enforces WCAG 2.1 AA compliance and zero innerHTML with user/AI data.
 */

/**
 * Create a DOM element safely with attributes and children.
 * @param {string} tag 
 * @param {Object} attrs 
 * @param {Array<HTMLElement|string>} children 
 * @returns {HTMLElement}
 */
export function el(tag, attrs = {}, children = []) {
  const element = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === "className") {
      element.className = value;
    } else if (key.startsWith("on") && typeof value === "function") {
      element.addEventListener(key.slice(2).toLowerCase(), value);
    } else if (key === "aria" && typeof value === "object") {
      for (const [aKey, aVal] of Object.entries(value)) {
        element.setAttribute(`aria-${aKey}`, aVal);
      }
    } else {
      element.setAttribute(key, value);
    }
  }

  for (const child of children) {
    if (typeof child === "string" || typeof child === "number") {
      element.appendChild(document.createTextNode(String(child)));
    } else if (child instanceof HTMLElement || child instanceof DocumentFragment) {
      element.appendChild(child);
    }
  }
  return element;
}

/**
 * Format currency amount safely.
 * @param {number} amount 
 * @returns {string}
 */
export function formatCurrency(amount) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(amount || 0);
}

/**
 * Render budget breakdown cards.
 * @param {Object} budget 
 * @param {HTMLElement} container 
 */
export function renderBudget(budget, container) {
  container.replaceChildren();

  const metricsRow = el("div", { className: "metrics-row" }, [
    el("div", { className: "metric-card" }, [
      el("div", { className: "metric-label" }, ["Total Budget"]),
      el("div", { className: "metric-value" }, [formatCurrency(budget.total_budget)]),
      el("div", { className: "metric-sub" }, ["100% Accounted"]),
    ]),
    el("div", { className: "metric-card" }, [
      el("div", { className: "metric-label" }, ["Per Guest Spend"]),
      el("div", { className: "metric-value" }, [formatCurrency(budget.per_guest_cost)]),
      el("div", { className: "metric-sub" }, ["Optimized Allocation"]),
    ]),
    el("div", { className: "metric-card" }, [
      el("div", { className: "metric-label" }, ["Contingency Buffer (5%)"]),
      el("div", { className: "metric-value" }, [formatCurrency(budget.contingency_fund)]),
      el("div", { className: "metric-sub" }, ["Emergency Reserve"]),
    ]),
  ]);

  const listContainer = el("div", { className: "budget-list" });

  for (const item of budget.items) {
    const card = el("div", { className: "budget-card-item" }, [
      el("div", { className: "item-top" }, [
        el("span", { className: "item-name" }, [item.category]),
        el("span", { className: "item-amount" }, [
          `${formatCurrency(item.allocated_amount)} (${item.percentage}%)`,
        ]),
      ]),
      el("div", { className: "item-bar-bg" }, [
        el("div", {
          className: "item-bar-fill",
          style: `width: ${Math.min(item.percentage * 2, 100)}%;`,
        }),
      ]),
      el("p", { className: "item-desc" }, [item.description]),
      el("div", { className: "metric-sub", style: "margin-top: 6px;" }, [item.tips]),
    ]);
    listContainer.appendChild(card);
  }

  container.appendChild(metricsRow);
  container.appendChild(listContainer);
}

/**
 * Render timeline run of show and advance milestones.
 * @param {Object} timeline 
 * @param {HTMLElement} container 
 */
export function renderTimeline(timeline, container) {
  container.replaceChildren();

  const hSchedule = el("h3", { className: "card-title" }, ["📅 Day-Of Event Schedule"]);
  const scheduleList = el("div", { className: "timeline-list" });

  for (const item of timeline.day_schedule) {
    const entry = el("div", { className: "timeline-entry" }, [
      el("div", { className: "time-stamp" }, [item.time]),
      el("h4", { className: "timeline-title" }, [item.title]),
      el("p", { className: "item-desc" }, [item.description]),
      el("span", { className: "responsible-badge" }, [`Lead: ${item.responsible}`]),
    ]);
    scheduleList.appendChild(entry);
  }

  const hMilestones = el("h3", { className: "card-title", style: "margin-top: 36px;" }, [
    "🚩 Planning Countdown Milestones",
  ]);
  const milestonesGrid = el("div", { className: "vendor-grid" });

  for (const ms of timeline.milestones) {
    const ul = el("ul", { className: "vendor-ul" });
    for (const act of ms.action_items) {
      ul.appendChild(el("li", {}, [act]));
    }

    const card = el("div", { className: "vendor-card" }, [
      el("div", {}, [
        el("div", { className: "lead-time" }, [`${ms.timeframe} (${ms.days_before} days)`]),
        el("h4", { className: "vendor-cat" }, [ms.title]),
      ]),
      ul,
    ]);
    milestonesGrid.appendChild(card);
  }

  container.appendChild(hSchedule);
  container.appendChild(scheduleList);
  container.appendChild(hMilestones);
  container.appendChild(milestonesGrid);
}

/**
 * Render vendor guide and interview questions.
 * @param {Array} vendors 
 * @param {HTMLElement} container 
 */
export function renderVendors(vendors, container) {
  container.replaceChildren();

  const grid = el("div", { className: "vendor-grid" });

  for (const v of vendors) {
    const qList = el("ul", { className: "vendor-ul" });
    for (const q of v.questions_to_ask) {
      qList.appendChild(el("li", {}, [q]));
    }

    const dList = el("ul", { className: "vendor-ul" });
    for (const d of v.key_deliverables) {
      dList.appendChild(el("li", {}, [d]));
    }

    const card = el("div", { className: "vendor-card" }, [
      el("div", {}, [
        el("div", { className: "vendor-head" }, [
          el("span", { className: "vendor-cat" }, [v.category]),
          el("span", { className: "vendor-cost" }, [formatCurrency(v.allocated_budget)]),
        ]),
        el("div", { className: "lead-time" }, [
          `Target Window: ${v.estimated_cost_range} | Book ~${v.booking_lead_time_weeks} wks out`,
        ]),
        el("div", { className: "vendor-subhead" }, ["Key Deliverables:"]),
        dList,
        el("div", { className: "vendor-subhead" }, ["Essential Interview Questions:"]),
        qList,
      ]),
    ]);
    grid.appendChild(card);
  }

  container.appendChild(grid);
}

/**
 * Render interactive checklist with completion updates.
 * @param {Array} tasks 
 * @param {HTMLElement} container 
 * @param {Function} onToggle 
 */
export function renderChecklist(tasks, container, onToggle) {
  container.replaceChildren();

  const phases = {};
  for (const t of tasks) {
    if (!phases[t.phase]) phases[t.phase] = [];
    phases[t.phase].push(t);
  }

  const completedCount = tasks.filter((t) => t.completed).length;
  const progressHeader = el("div", { className: "metric-card", style: "margin-bottom: 20px;" }, [
    el("div", { className: "metric-label" }, ["Checklist Progress"]),
    el("div", { className: "metric-value" }, [
      `${completedCount} of ${tasks.length} Completed`,
    ]),
    el("div", { className: "item-bar-bg", style: "margin-top: 8px;" }, [
      el("div", {
        className: "item-bar-fill",
        style: `width: ${tasks.length ? (completedCount / tasks.length) * 100 : 0}%;`,
      }),
    ]),
  ]);

  container.appendChild(progressHeader);

  const groupsContainer = el("div", { className: "checklist-container" });

  for (const [phase, phaseTasks] of Object.entries(phases)) {
    const groupCard = el("div", { className: "phase-group" });
    const header = el("div", { className: "phase-title" }, [
      el("span", {}, [phase]),
      el("span", { className: "char-count" }, [`${phaseTasks.length} tasks`]),
    ]);
    groupCard.appendChild(header);

    for (const t of phaseTasks) {
      const checkbox = el("input", {
        type: "checkbox",
        id: `chk-${t.id}`,
        className: "task-check",
        ...(t.completed ? { checked: "checked" } : {}),
      });

      checkbox.addEventListener("change", () => {
        t.completed = checkbox.checked;
        if (onToggle) onToggle();
      });

      const priorityClass =
        t.priority.toLowerCase() === "high"
          ? "priority-high"
          : t.priority.toLowerCase() === "medium"
          ? "priority-medium"
          : "priority-low";

      const itemRow = el("div", { className: "task-item" }, [
        checkbox,
        el("label", { htmlFor: `chk-${t.id}`, className: "task-label" }, [
          el("div", { style: "font-weight: 600;" }, [t.task]),
          el("div", { className: "char-count" }, [`Deadline: ${t.deadline_description}`]),
        ]),
        el("span", { className: `badge-priority ${priorityClass}` }, [t.priority]),
      ]);

      groupCard.appendChild(itemRow);
    }
    groupsContainer.appendChild(groupCard);
  }

  container.appendChild(groupsContainer);
}

/**
 * Render creative ideas in a styled results card safely without innerHTML.
 * @param {Object} data 
 * @param {HTMLElement} container 
 */
export function renderCreativeIdeas(data, container) {
  container.replaceChildren();

  const resultsCard = el("div", { className: "ai-results-card" });

  const headerTag = el("div", { className: "ai-header-tag" }, [
    `✨ Creative Sparks: ${data.topic.toUpperCase()} (${data.source})`,
  ]);
  const title = el("h3", { className: "card-title" }, [data.title]);

  const ideasList = el("ul", { className: "vendor-ul" });
  for (const idea of data.ideas) {
    ideasList.appendChild(el("li", {}, [idea]));
  }

  const decorList = el("ul", { className: "vendor-ul" });
  for (const decor of data.decor_suggestions) {
    decorList.appendChild(el("li", {}, [decor]));
  }

  const sigBox = el("div", { className: "signature-box" }, [
    el("div", { style: "font-weight: 700; color: #a5b4fc; font-size: 0.85rem;" }, [
      "SIGNATURE WOW MOMENT:",
    ]),
    el("div", { style: "margin-top: 4px; font-weight: 600;" }, [data.signature_touch]),
  ]);

  resultsCard.appendChild(headerTag);
  resultsCard.appendChild(title);
  resultsCard.appendChild(el("div", { className: "vendor-subhead" }, ["Core Creative Concepts:"]));
  resultsCard.appendChild(ideasList);
  resultsCard.appendChild(el("div", { className: "vendor-subhead" }, ["Decor & Atmosphere Highlights:"]));
  resultsCard.appendChild(decorList);
  resultsCard.appendChild(sigBox);

  container.appendChild(resultsCard);
}

/**
 * Append chat message bubble safely.
 * @param {string} role 
 * @param {string} text 
 * @param {HTMLElement} messagesContainer 
 */
export function appendChatMessage(role, text, messagesContainer) {
  const isUser = role === "user";
  const bubble = el(
    "div",
    {
      className: `chat-bubble ${isUser ? "bubble-user" : "bubble-assistant"}`,
      role: "article",
      aria: { label: `${isUser ? "You" : "EventCraft AI"}` },
    },
    [text]
  );
  messagesContainer.appendChild(bubble);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
