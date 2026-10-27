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
 * @param {string} currency 
 * @returns {string}
 */
export function formatCurrency(amount, currency = "INR") {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: currency || "INR",
    maximumFractionDigits: 0,
  }).format(amount || 0);
}

/**
 * Render warnings banner if any exist.
 * @param {Array<string>} warnings 
 * @param {HTMLElement} container 
 */
export function renderWarnings(warnings, container) {
  if (!warnings || warnings.length === 0) return;
  const banner = el("div", {
    className: "metric-card",
    style: "border-left: 4px solid var(--accent-amber); margin-bottom: 20px;",
    role: "alert",
  });
  banner.appendChild(
    el("div", { style: "font-weight: 700; color: var(--accent-amber); margin-bottom: 4px;" }, [
      "⚠️ Planning Alerts & Concrete Recommendations:",
    ])
  );
  const ul = el("ul", { className: "vendor-ul", style: "margin-bottom: 0;" });
  for (const w of warnings) {
    ul.appendChild(el("li", {}, [w]));
  }
  banner.appendChild(ul);
  container.prepend(banner);
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
      el("div", { className: "metric-value" }, [
        formatCurrency(budget.total_budget, budget.currency),
      ]),
      el("div", { className: "metric-sub" }, ["100% Accounted Exactly"]),
    ]),
    el("div", { className: "metric-card" }, [
      el("div", { className: "metric-label" }, ["Per Guest Spend"]),
      el("div", { className: "metric-value" }, [
        formatCurrency(budget.per_guest_cost, budget.currency),
      ]),
      el("div", { className: "metric-sub" }, [
        budget.is_feasible ? "Feasible Allocation" : "Below Minimum Threshold",
      ]),
    ]),
    el("div", { className: "metric-card" }, [
      el("div", { className: "metric-label" }, [
        `Contingency Buffer (${budget.contingency_percentage}%)`,
      ]),
      el("div", { className: "metric-value" }, [
        formatCurrency(budget.contingency_fund, budget.currency),
      ]),
      el("div", { className: "metric-sub" }, ["Protected Emergency Reserve"]),
    ]),
  ]);

  const listContainer = el("div", { className: "budget-list" });

  for (const item of budget.items) {
    const card = el("div", { className: "budget-card-item" }, [
      el("div", { className: "item-top" }, [
        el("span", { className: "item-name" }, [item.category]),
        el("span", { className: "item-amount" }, [
          `${formatCurrency(item.allocated_amount, budget.currency)} (${item.percentage}%)`,
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
 * Render backward-scheduled timeline tasks and rush alerts.
 * @param {Object} timeline 
 * @param {HTMLElement} container 
 */
export function renderTimeline(timeline, container) {
  container.replaceChildren();

  if (timeline.rush_warning) {
    const rushAlert = el("div", {
      className: "metric-card",
      style: "border-left: 4px solid var(--accent-rose); margin-bottom: 20px;",
      role: "alert",
    }, [
      el("div", { style: "font-weight: 700; color: #fda4af; margin-bottom: 4px;" }, [
        "🚨 Rush Timeline Plan:",
      ]),
      el("p", { className: "item-desc" }, [timeline.rush_warning]),
    ]);
    container.appendChild(rushAlert);
  }

  const hSchedule = el("h3", { className: "card-title" }, [
    `📅 Backward-Scheduled Tasks (${timeline.lead_time_days} Days Lead Time)`,
  ]);
  const scheduleList = el("div", { className: "timeline-list" });

  const tasks = timeline.tasks || [];
  for (const item of tasks) {
    const pClass = item.is_critical ? "priority-high" : "priority-low";
    const entry = el("div", { className: "timeline-entry" }, [
      el("div", { className: "time-stamp" }, [
        `Due: ${item.due_date} (${item.days_before_event}d out)`,
      ]),
      el("h4", { className: "timeline-title" }, [item.title]),
      el("div", { style: "display: flex; gap: 8px; margin-top: 6px;" }, [
        el("span", { className: "responsible-badge" }, [item.phase]),
        el("span", { className: `badge-priority ${pClass}` }, [item.priority]),
      ]),
    ]);
    scheduleList.appendChild(entry);
  }

  container.appendChild(hSchedule);
  container.appendChild(scheduleList);
}

/**
 * Render vendor guide and checklist.
 * @param {Array} vendors 
 * @param {HTMLElement} container 
 */
export function renderVendors(vendors, container) {
  container.replaceChildren();

  const grid = el("div", { className: "vendor-grid" });

  for (const v of vendors) {
    const qList = el("ul", { className: "vendor-ul" });
    for (const q of v.questions_to_ask || []) {
      qList.appendChild(el("li", {}, [q]));
    }

    const card = el("div", { className: "vendor-card" }, [
      el("div", {}, [
        el("div", { className: "vendor-head" }, [
          el("span", { className: "vendor-cat" }, [v.category]),
          el("span", { className: "vendor-cost" }, [formatCurrency(v.budget_cap)]),
        ]),
        el("div", { className: "lead-time" }, [
          `Book by ${v.booking_deadline} (${v.lead_time_days} days lead) • Status: ${v.status}`,
        ]),
        el("div", { className: "vendor-subhead" }, ["Essential Interview Questions:"]),
        qList,
      ]),
    ]);
    grid.appendChild(card);
  }

  container.appendChild(grid);
}

/**
 * Render structured creative ideas (themes, menu, activities, decor, touches).
 * @param {Object} data 
 * @param {HTMLElement} container 
 */
export function renderCreativeIdeas(data, container) {
  container.replaceChildren();

  const resultsCard = el("div", { className: "ai-results-card" });

  const headerTag = el("div", { className: "ai-header-tag" }, [
    `✨ Creative Sparks (Source: ${data.source.toUpperCase()})`,
  ]);
  resultsCard.appendChild(headerTag);

  // 3 Themes
  const themesBlock = el("div", {}, [
    el("h4", { className: "card-title", style: "font-size: 1.1rem; margin-top: 10px;" }, [
      "🎨 3 Bespoke Theme Concepts",
    ]),
  ]);
  const themesList = el("ul", { className: "vendor-ul" });
  for (const t of data.themes || []) {
    themesList.appendChild(el("li", { style: "font-weight: 600;" }, [t]));
  }
  themesBlock.appendChild(themesList);
  resultsCard.appendChild(themesBlock);

  // Menu Ideas
  if (data.menu_ideas && data.menu_ideas.length > 0) {
    resultsCard.appendChild(el("div", { className: "vendor-subhead" }, ["🍽️ Culinary & Beverage Pairings:"]));
    const menuList = el("ul", { className: "vendor-ul" });
    for (const m of data.menu_ideas) menuList.appendChild(el("li", {}, [m]));
    resultsCard.appendChild(menuList);
  }

  // Activities
  if (data.activities && data.activities.length > 0) {
    resultsCard.appendChild(el("div", { className: "vendor-subhead" }, ["🎲 Interactive Activities & Flow:"]));
    const actList = el("ul", { className: "vendor-ul" });
    for (const a of data.activities) actList.appendChild(el("li", {}, [a]));
    resultsCard.appendChild(actList);
  }

  // Decor Tips
  if (data.decor_tips && data.decor_tips.length > 0) {
    resultsCard.appendChild(el("div", { className: "vendor-subhead" }, ["💐 Ambient Decor & Lighting:"]));
    const decorList = el("ul", { className: "vendor-ul" });
    for (const d of data.decor_tips) decorList.appendChild(el("li", {}, [d]));
    resultsCard.appendChild(decorList);
  }

  // Personal Touches
  if (data.personal_touches && data.personal_touches.length > 0) {
    const touchesBox = el("div", { className: "signature-box" });
    touchesBox.appendChild(
      el("div", { style: "font-weight: 700; color: #a5b4fc; font-size: 0.85rem;" }, [
        "MEMORABLE PERSONAL TOUCHES:",
      ])
    );
    for (const pt of data.personal_touches) {
      touchesBox.appendChild(el("div", { style: "margin-top: 4px;" }, [`• ${pt}`]));
    }
    resultsCard.appendChild(touchesBox);
  }

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
