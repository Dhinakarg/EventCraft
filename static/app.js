/**
 * EventCraft AI - Accessible Client Application
 * Strict WCAG 2.1 AA, proper ARIA tabs pattern, and zero innerHTML with data.
 */

// Application State
const state = {
  currentPlan: null,
  chatMessages: [
    {
      role: "bot",
      text: "Hello! I am your EventCraft AI planner. How can I help refine your event details today?",
    },
  ],
};

/**
 * Announce messages to screen readers via aria-live region.
 * @param {string} msg 
 */
function announceStatus(msg) {
  const el = document.getElementById("status-announcer");
  if (el) {
    el.textContent = "";
    setTimeout(() => {
      el.textContent = msg;
    }, 50);
  }
}

/**
 * Format currency amount safely using Indian Rupee (INR) / en-IN by default.
 * @param {number} amount 
 * @param {string} currency 
 * @returns {string}
 */
function formatCurrency(amount, currency = "INR") {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: currency || "INR",
    maximumFractionDigits: 0,
  }).format(amount || 0);
}

/**
 * Create inline SVG referencing the symbol sprite (aria-hidden by default).
 * @param {string} name 
 * @param {string} extraClass 
 * @returns {SVGElement}
 */
function createSvgIcon(name, extraClass = "") {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", `icon ${extraClass}`.trim());
  svg.setAttribute("aria-hidden", "true");
  const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
  use.setAttribute("href", `#icon-${name}`);
  svg.appendChild(use);
  return svg;
}

/**
 * Create DOM element safely with textContent or children.
 * @param {string} tag 
 * @param {Object} attrs 
 * @param {Array<Element|string|number>} children 
 * @returns {HTMLElement}
 */
function createEl(tag, attrs = {}, children = []) {
  const elem = document.createElement(tag);
  for (const [key, val] of Object.entries(attrs)) {
    if (key === "className") {
      elem.className = val;
    } else if (key === "htmlFor" || key === "for") {
      elem.setAttribute("for", val);
      elem.htmlFor = val;
    } else if (key.startsWith("on") && typeof val === "function") {
      elem.addEventListener(key.slice(2).toLowerCase(), val);
    } else if (key === "aria" && typeof val === "object") {
      for (const [aKey, aVal] of Object.entries(val)) {
        elem.setAttribute(`aria-${aKey}`, aVal);
      }
    } else {
      elem.setAttribute(key, val);
    }
  }
  for (const child of children) {
    if (typeof child === "string" || typeof child === "number") {
      elem.appendChild(document.createTextNode(String(child)));
    } else if (child instanceof Element) {
      elem.appendChild(child);
    }
  }
  return elem;
}

/**
 * Format date string into friendly readable format (e.g. "Mar 3, 2027").
 * @param {string} dateStr 
 * @returns {string}
 */
function formatFriendlyDate(dateStr) {
  if (!dateStr) return "";
  try {
    const d = new Date(dateStr + "T00:00:00");
    if (isNaN(d.getTime())) return dateStr;
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    }).format(d);
  } catch {
    return dateStr;
  }
}

/**
 * Render the 4 KPI cards at the top of results.
 * @param {Object} plan 
 */
function renderKpiCards(plan) {
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

/**
 * Render dismissible alert region with severity levels (info, warning, critical).
 * Rush timeline notice receives "critical" style and plain-language explanation.
 * @param {Array<string>} warnings 
 * @param {string|null} rushWarning 
 * @param {HTMLElement} container 
 */
function renderWarnings(warnings, rushWarning, container) {
  container.replaceChildren();
  const alertList = [];

  if (rushWarning) {
    alertList.push({
      severity: "critical",
      title: "Rush Timeline Notice",
      icon: "warning",
      text: `${rushWarning} Standard recommended lead times were compressed. Core vendors (such as venue, catering, and photography) should be secured immediately; some vendors may charge rush fees or have limited availability.`,
    });
  }

  for (const w of warnings || []) {
    const isCritical = w.toLowerCase().includes("budget exceed") || w.toLowerCase().includes("critical");
    const isInfo = w.toLowerCase().includes("recommendation") || w.toLowerCase().includes("note");
    alertList.push({
      severity: isCritical ? "critical" : isInfo ? "info" : "warning",
      title: isCritical ? "Allocation Warning" : isInfo ? "Planning Advisory" : "Budget & Timeline Notice",
      icon: isCritical ? "warning" : isInfo ? "info" : "warning",
      text: w,
    });
  }

  if (alertList.length === 0) return;

  for (const item of alertList) {
    const box = createEl("div", {
      className: `alert-box alert-${item.severity}`,
      role: "alert",
    });

    const header = createEl("div", { className: "alert-header" });
    const headerMain = createEl("div", { className: "alert-header-main" }, [
      createSvgIcon(item.icon),
      createEl("span", { className: "alert-severity-badge" }, [item.severity]),
      createEl("span", {}, [item.title]),
    ]);

    const dismissBtn = createEl("button", {
      type: "button",
      className: "alert-dismiss-btn",
      aria: { label: `Dismiss notice: ${item.title}` },
    }, [createSvgIcon("close")]);

    dismissBtn.addEventListener("click", () => {
      box.remove();
      announceStatus(`${item.title} dismissed.`);
    });

    header.appendChild(headerMain);
    header.appendChild(dismissBtn);
    box.appendChild(header);

    const desc = createEl("p", { className: "alert-desc" }, [item.text]);
    box.appendChild(desc);

    container.appendChild(box);
  }
}

/**
 * Render Budget Tab with SVG Donut Chart, visual legend, hidden chart summary, and itemized table.
 * @param {Object} budget 
 * @param {HTMLElement} container 
 */
function renderBudgetTab(budget, container) {
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
  const colors = ["#2563eb", "#059669", "#d97706", "#7c3aed", "#db2777", "#0891b2", "#ea580c", "#4f46e5"];
  let accumulatedPct = 0;

  budget.items.forEach((item, idx) => {
    const color = colors[idx % colors.length];
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
    const color = colors[idx % colors.length];
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

// Timeline critical filter state
let timelineCriticalOnly = false;

/**
 * Render Vertical Timeline grouped by phase with friendly dates and critical filter toggle.
 * @param {Object} timeline 
 * @param {HTMLElement} container 
 */
function renderTimelineTab(timeline, container) {
  container.replaceChildren();

  // Filter toolbar
  const controls = createEl("div", { className: "timeline-controls" });
  const filterBtn = createEl("button", {
    type: "button",
    id: "timeline-filter-critical",
    className: `btn btn-sm ${timelineCriticalOnly ? "btn-primary" : "btn-outline"}`,
    aria: { pressed: timelineCriticalOnly ? "true" : "false" },
  }, [
    createSvgIcon("filter"),
    timelineCriticalOnly ? " Showing critical only" : " Show only critical",
  ]);

  filterBtn.addEventListener("click", () => {
    timelineCriticalOnly = !timelineCriticalOnly;
    renderTimelineTab(timeline, container);
    announceStatus(timelineCriticalOnly ? "Filtered to show only critical tasks." : "Showing all timeline tasks.");
  });
  controls.appendChild(filterBtn);

  const allTasks = timeline.tasks || [];
  const filteredTasks = timelineCriticalOnly
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

/**
 * Render Vendor Tab with progress bar, status select (To do/Contacted/Booked), urgency badge,
 * interview questions in collapsible <details>, and localStorage persistence.
 * @param {Array} vendors 
 * @param {HTMLElement} container 
 */
function renderVendorsTab(vendors, container) {
  container.replaceChildren();

  const storageKey = `eventcraft_vendor_status_${state.currentPlan ? state.currentPlan.event_date : "default"}_${state.currentPlan ? state.currentPlan.event_type : "type"}`;
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
    const optTodo = createEl("option", { value: "todo" }, ["To do"]);
    const optContacted = createEl("option", { value: "contacted" }, ["Contacted"]);
    const optBooked = createEl("option", { value: "booked" }, ["Booked"]);
    select.appendChild(optTodo);
    select.appendChild(optContacted);
    select.appendChild(optBooked);

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

/**
 * Render Ideas Tab with card grid and AI-generated vs Template ideas badge with text explanation.
 * @param {Object} ideas 
 * @param {HTMLElement} container 
 */
function renderIdeasTab(ideas, container) {
  container.replaceChildren();
  if (!ideas) {
    container.appendChild(createEl("p", {}, ["No ideas available."]));
    return;
  }

  const isAi = ideas.source === "ai";

  // Source Banner with tooltip-free plain text explanation
  const banner = createEl("div", { className: "ideas-source-banner" }, [
    createEl("span", { className: `badge ${isAi ? "badge-ai" : "badge-tmpl"}` }, [
      createSvgIcon(isAi ? "sparkle" : "copy"),
      isAi ? " AI-generated" : " Template ideas",
    ]),
    createEl("span", { className: "ideas-source-desc" }, [
      isAi
        ? "Custom-generated by Gemini based on your unique event parameters, dietary requirements, and aesthetic vibe."
        : "Curated event planning blueprint calibrated to your event size, category, and budget tier.",
    ]),
  ]);
  container.appendChild(banner);

  // Card Grid for themes, menu, activities, decor, personal touches
  const grid = createEl("div", { className: "ideas-card-grid" });

  if (ideas.themes && ideas.themes.length) {
    const cardThemes = createEl("div", { className: "ideas-card" }, [
      createEl("div", { className: "ideas-card-header" }, [
        createSvgIcon("palette"),
        createEl("span", {}, ["Bespoke Themes"]),
      ]),
      createEl("ul", { className: "ideas-card-list" }, ideas.themes.map((t) => createEl("li", {}, [t]))),
    ]);
    grid.appendChild(cardThemes);
  }

  if (ideas.menu_ideas && ideas.menu_ideas.length) {
    const cardMenu = createEl("div", { className: "ideas-card" }, [
      createEl("div", { className: "ideas-card-header" }, [
        createSvgIcon("utensils"),
        createEl("span", {}, ["Menu & Culinary Ideas"]),
      ]),
      createEl("ul", { className: "ideas-card-list" }, ideas.menu_ideas.map((m) => createEl("li", {}, [m]))),
    ]);
    grid.appendChild(cardMenu);
  }

  if (ideas.activities && ideas.activities.length) {
    const cardAct = createEl("div", { className: "ideas-card" }, [
      createEl("div", { className: "ideas-card-header" }, [
        createSvgIcon("activities"),
        createEl("span", {}, ["Interactive Activities"]),
      ]),
      createEl("ul", { className: "ideas-card-list" }, ideas.activities.map((a) => createEl("li", {}, [a]))),
    ]);
    grid.appendChild(cardAct);
  }

  if (ideas.decor_tips && ideas.decor_tips.length) {
    const cardDecor = createEl("div", { className: "ideas-card" }, [
      createEl("div", { className: "ideas-card-header" }, [
        createSvgIcon("decor"),
        createEl("span", {}, ["Ambient Decor Concepts"]),
      ]),
      createEl("ul", { className: "ideas-card-list" }, ideas.decor_tips.map((d) => createEl("li", {}, [d]))),
    ]);
    grid.appendChild(cardDecor);
  }

  if (ideas.personal_touches && ideas.personal_touches.length) {
    const cardTouches = createEl("div", { className: "ideas-card" }, [
      createEl("div", { className: "ideas-card-header" }, [
        createSvgIcon("sparkle"),
        createEl("span", {}, ["Signature Personal Touches"]),
      ]),
      createEl("ul", { className: "ideas-card-list" }, ideas.personal_touches.map((pt) => createEl("li", {}, [pt]))),
    ]);
    grid.appendChild(cardTouches);
  }

  container.appendChild(grid);
}

/**
 * Append chat message to log safely using textContent.
 * @param {string} role 
 * @param {string} text 
 */
function appendChatMessage(role, text) {
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
 * Handle Tab Activation and proper ARIA states.
 * @param {string} tabKey 
 */
function activateTab(tabKey) {
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
function onTabKeydown(e) {
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
 * Collapse form into a summary bar on tablet/mobile screens after plan generation.
 * @param {Object} plan 
 */
function updateMobileFormCollapse(plan) {
  const summaryBar = document.getElementById("form-summary-bar");
  const form = document.getElementById("event-plan-form");
  const summaryText = document.getElementById("summary-text");
  if (!summaryBar || !form || !summaryText) return;

  const formattedType = plan.event_type.charAt(0).toUpperCase() + plan.event_type.slice(1);
  const formattedCost = formatCurrency(plan.total_budget, plan.currency);
  summaryText.textContent = `${formattedType} · ${plan.guest_count} guests · ${formattedCost} · ${plan.event_date}`;

  if (window.innerWidth < 1024) {
    summaryBar.removeAttribute("hidden");
    form.setAttribute("hidden", "");
    const heading = document.getElementById("results-heading");
    if (heading) {
      heading.setAttribute("tabindex", "-1");
      heading.focus();
    }
  }
}

/**
 * Validate a form input inline.
 * Returns { field, id, message } on error, or null if valid.
 * @param {string} fieldId
 * @returns {Object|null}
 */
function validateField(fieldId) {
  if (fieldId === "event_date") {
    const input = document.getElementById("event_date");
    const err = document.getElementById("error-date");
    if (!input || !err) return null;
    const selectedDate = new Date(input.value);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (!input.value || isNaN(selectedDate.getTime()) || selectedDate <= today) {
      err.removeAttribute("hidden");
      input.setAttribute("aria-invalid", "true");
      return { field: input, id: "event_date", message: "Event date must be a valid future date." };
    } else {
      err.setAttribute("hidden", "");
      input.setAttribute("aria-invalid", "false");
      return null;
    }
  }

  if (fieldId === "guest_count") {
    const input = document.getElementById("guest_count");
    const err = document.getElementById("error-guests");
    if (!input || !err) return null;
    const guests = parseInt(input.value, 10);

    if (isNaN(guests) || guests < 1 || guests > 2000) {
      err.removeAttribute("hidden");
      input.setAttribute("aria-invalid", "true");
      return { field: input, id: "guest_count", message: "Guest count must be between 1 and 2,000." };
    } else {
      err.setAttribute("hidden", "");
      input.setAttribute("aria-invalid", "false");
      return null;
    }
  }

  if (fieldId === "total_budget") {
    const input = document.getElementById("total_budget");
    const err = document.getElementById("error-budget");
    if (!input || !err) return null;
    const budget = parseFloat(input.value);

    if (isNaN(budget) || budget <= 0) {
      err.removeAttribute("hidden");
      input.setAttribute("aria-invalid", "true");
      return { field: input, id: "total_budget", message: "Total budget must be greater than zero." };
    } else {
      err.setAttribute("hidden", "");
      input.setAttribute("aria-invalid", "false");
      return null;
    }
  }

  return null;
}

/**
 * Update live "= $312 per guest" estimate under guests and budget.
 */
function updatePerGuestCalculation() {
  const guestInput = document.getElementById("guest_count");
  const budgetInput = document.getElementById("total_budget");
  const calcAmount = document.getElementById("per-guest-amount");
  if (!guestInput || !budgetInput || !calcAmount) return;

  const guests = parseInt(guestInput.value, 10);
  const budget = parseFloat(budgetInput.value);

  if (!isNaN(guests) && guests > 0 && !isNaN(budget) && budget > 0) {
    const perGuest = Math.round(budget / guests);
    calcAmount.textContent = `= ${formatCurrency(perGuest, "INR")} per guest`;
  } else {
    calcAmount.textContent = "= -- per guest";
  }
}

/**
 * Update live character counter for notes textarea (500 max).
 */
function updateNotesCounter() {
  const notesArea = document.getElementById("custom_notes");
  const counter = document.getElementById("notes-counter");
  if (!notesArea || !counter) return;

  const max = 500;
  const len = notesArea.value.length;
  const remaining = Math.max(0, max - len);
  counter.textContent = `${remaining} characters left`;
  counter.classList.toggle("limit-near", remaining <= 50);
}

/**
 * Enforce max 3 priority chips, update live counter in aria-live region, and sync legacy select.
 */
function updatePrioritiesState() {
  const chips = document.querySelectorAll('input[name="priorities_chip"]');
  const counter = document.getElementById("priority-counter");
  const legacySelect = document.getElementById("priorities");

  const checkedChips = Array.from(chips).filter((c) => c.checked);
  const count = checkedChips.length;

  if (counter) {
    counter.textContent = `${count} of 3 selected`;
  }

  chips.forEach((chip) => {
    const itemLabel = chip.closest(".chip-item");
    if (!chip.checked && count >= 3) {
      chip.disabled = true;
      if (itemLabel) itemLabel.classList.add("disabled");
    } else {
      chip.disabled = false;
      if (itemLabel) itemLabel.classList.remove("disabled");
    }
  });

  if (legacySelect) {
    const checkedValues = new Set(checkedChips.map((c) => c.value));
    Array.from(legacySelect.options).forEach((opt) => {
      opt.selected = checkedValues.has(opt.value);
    });
  }
}

/**
 * Bind form interactive listeners: calculation, counters, chips, blur validation, radio sync.
 */
function initFormInteractions() {
  // Live calculation
  const guestInput = document.getElementById("guest_count");
  const budgetInput = document.getElementById("total_budget");
  if (guestInput) {
    guestInput.addEventListener("input", updatePerGuestCalculation);
    guestInput.addEventListener("change", updatePerGuestCalculation);
    guestInput.addEventListener("blur", () => validateField("guest_count"));
  }
  if (budgetInput) {
    budgetInput.addEventListener("input", updatePerGuestCalculation);
    budgetInput.addEventListener("change", updatePerGuestCalculation);
    budgetInput.addEventListener("blur", () => validateField("total_budget"));
  }
  updatePerGuestCalculation();

  // Notes counter
  const notesArea = document.getElementById("custom_notes");
  if (notesArea) {
    notesArea.addEventListener("input", updateNotesCounter);
    updateNotesCounter();
  }

  // Priority chips
  const prioChips = document.querySelectorAll('input[name="priorities_chip"]');
  prioChips.forEach((chip) => {
    chip.addEventListener("change", updatePrioritiesState);
  });
  updatePrioritiesState();

  // Event type radios -> sync to hidden select
  const typeRadios = document.querySelectorAll('input[name="event_type"]');
  const legacyTypeSelect = document.getElementById("event_type");
  typeRadios.forEach((radio) => {
    radio.addEventListener("change", () => {
      if (radio.checked && legacyTypeSelect) {
        legacyTypeSelect.value = radio.value;
      }
    });
  });

  // Date blur validation
  const dateInput = document.getElementById("event_date");
  if (dateInput) {
    dateInput.addEventListener("blur", () => validateField("event_date"));
    dateInput.addEventListener("input", () => {
      if (dateInput.getAttribute("aria-invalid") === "true") {
        validateField("event_date");
      }
    });
  }
}

// Preset sample scenarios for instant exploration
const SCENARIOS = {
  "tight-wedding": {
    event_type: "wedding",
    event_date_offset_days: 180,
    guest_count: 60,
    total_budget: 400000,
    vibe: "Rustic",
    city: "Jaipur",
    priorities: ["venue", "food", "photography"],
    dietary: ["Vegetarian", "Gluten-free"],
    notes: "Daytime garden celebration with buffet dining, acoustic music, and natural lighting.",
  },
  "milestone-birthday": {
    event_type: "birthday",
    event_date_offset_days: 90,
    guest_count: 40,
    total_budget: 150000,
    vibe: "Modern Minimalist",
    city: "Bengaluru",
    priorities: ["food", "entertainment", "decor"],
    dietary: ["Nut allergy"],
    notes: "Rooftop lounge gathering with craft cocktails, finger foods, and DJ.",
  },
  "community-fest": {
    event_type: "community",
    event_date_offset_days: 150,
    guest_count: 350,
    total_budget: 600000,
    vibe: "Garden Party",
    city: "Mumbai",
    priorities: ["venue", "entertainment", "other"],
    dietary: ["Vegan", "Halal"],
    notes: "Outdoor park festival with community art booths, food trucks, and acoustic stages.",
  },
};

/**
 * Load a pre-configured sample scenario into the form and submit.
 * @param {string} scenarioKey 
 */
function loadScenario(scenarioKey) {
  const sc = SCENARIOS[scenarioKey];
  if (!sc) return;

  // 1. Radio Card & Select
  const radio = document.querySelector(`input[name="event_type"][value="${sc.event_type}"]`);
  if (radio) {
    radio.checked = true;
    const legacySelect = document.getElementById("event_type");
    if (legacySelect) legacySelect.value = sc.event_type;
  }

  // 2. Event Date
  const dateInput = document.getElementById("event_date");
  if (dateInput) {
    const future = new Date();
    future.setDate(future.getDate() + sc.event_date_offset_days);
    dateInput.value = future.toISOString().split("T")[0];
    dateInput.setAttribute("aria-invalid", "false");
    const errDate = document.getElementById("error-date");
    if (errDate) errDate.setAttribute("hidden", "");
  }

  // 3. Guests
  const guestInput = document.getElementById("guest_count");
  if (guestInput) {
    guestInput.value = String(sc.guest_count);
    guestInput.setAttribute("aria-invalid", "false");
    const errGuests = document.getElementById("error-guests");
    if (errGuests) errGuests.setAttribute("hidden", "");
  }

  // 4. Budget
  const budgetInput = document.getElementById("total_budget");
  if (budgetInput) {
    budgetInput.value = String(sc.total_budget);
    budgetInput.setAttribute("aria-invalid", "false");
    const errBudget = document.getElementById("error-budget");
    if (errBudget) errBudget.setAttribute("hidden", "");
  }

  // 5. Vibe & City
  const vibeInput = document.getElementById("vibe");
  if (vibeInput) vibeInput.value = sc.vibe;
  const cityInput = document.getElementById("city");
  if (cityInput) cityInput.value = sc.city;

  // 6. Priorities Chips
  const prioChips = document.querySelectorAll('input[name="priorities_chip"]');
  prioChips.forEach((chip) => {
    chip.checked = sc.priorities.includes(chip.value);
  });
  updatePrioritiesState();

  // 7. Dietary Chips
  const dietaryChips = document.querySelectorAll('input[name="dietary"]');
  dietaryChips.forEach((chip) => {
    chip.checked = sc.dietary.includes(chip.value);
  });

  // 8. Notes
  const notesArea = document.getElementById("custom_notes");
  if (notesArea) {
    notesArea.value = sc.notes;
    updateNotesCounter();
  }

  updatePerGuestCalculation();

  announceStatus(`Loaded ${scenarioKey.replace("-", " ")} scenario. Generating plan.`);
  document.getElementById("event-plan-form").dispatchEvent(new Event("submit"));
}

/**
 * Bind listeners to sample scenario buttons.
 */
function initScenarioButtons() {
  const scenarioBtns = document.querySelectorAll(".scenario-btn");
  scenarioBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const key = btn.getAttribute("data-scenario");
      if (key) loadScenario(key);
    });
  });
}

/**
 * Bind listeners to chat suggested question chips.
 */
function initChatChips() {
  const chips = document.querySelectorAll(".chat-chip");
  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const input = document.getElementById("chat-input");
      if (input) {
        input.value = chip.textContent.trim();
        document.getElementById("chat-query-form").dispatchEvent(new Event("submit"));
      }
    });
  });
}

/**
 * Submit plan form to POST /api/plan with skeleton loading, error summary, and full render.
 * @param {Event} e 
 */
async function onPlanSubmit(e) {
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

  // Toggle skeleton loading in results area
  const emptyState = document.getElementById("results-empty-state");
  const resultsContent = document.getElementById("results-content");
  const skeleton = document.getElementById("results-skeleton");

  if (emptyState) emptyState.setAttribute("hidden", "");
  if (resultsContent) resultsContent.setAttribute("hidden", "");
  if (skeleton) skeleton.removeAttribute("hidden");

  // Gather priorities from checked chips
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

  // Gather dietary restrictions from checked dietary chips
  const dietaryChips = document.querySelectorAll('input[name="dietary"]:checked');
  const dietary = Array.from(dietaryChips).map((c) => c.value);

  // Gather event type from checked radio
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

    activateTab("budget");
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

/**
 * Send chat question to POST /api/chat with disabled state while sending.
 * @param {Event} e 
 */
async function onChatSubmit(e) {
  e.preventDefault();
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("chat-send-btn");
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

  const ctx = state.currentPlan
    ? `${state.currentPlan.event_type} for ${state.currentPlan.guest_count} guests with $${state.currentPlan.total_budget} budget in ${state.currentPlan.city}`
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
  } catch (err) {
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
 * Download .ics timeline calendar file.
 */
function downloadIcs() {
  if (!state.currentPlan) {
    alert("Please generate a plan first.");
    return;
  }
  const p = state.currentPlan;
  const url = `/api/export/ics?event_date=${p.event_date}&event_type=${p.event_type}&guest_count=${p.guest_count}&total_budget=${p.total_budget}&vibe=${encodeURIComponent(p.vibe)}`;
  window.location.href = url;
  announceStatus("Downloading iCalendar .ics timeline.");
}

/**
 * Copy plain text summary of plan to clipboard with "Copied!" confirmation.
 */
function copyPlanAsText() {
  if (!state.currentPlan) {
    alert("Please generate a plan first.");
    return;
  }
  const p = state.currentPlan;
  let text = `EVENT PLAN SUMMARY\n--------------------\n`;
  text += `Type: ${p.event_type}\nDate: ${p.event_date}\nGuests: ${p.guest_count}\nBudget: $${p.total_budget}\nCity: ${p.city}\nVibe: ${p.vibe}\n\n`;
  text += `BUDGET BREAKDOWN:\n`;
  for (const item of p.budget.items) {
    text += `- ${item.category}: $${item.allocated_amount} (${item.percentage}%)\n`;
  }
  text += `Contingency Fund: $${p.budget.contingency_fund}\n\n`;
  text += `TIMELINE TASKS:\n`;
  for (const t of p.timeline.tasks) {
    text += `- ${t.due_date}: ${t.title} [${t.priority}]\n`;
  }

  const btn = document.getElementById("btn-copy-text");
  const btnText = document.getElementById("copy-btn-text");
  const copyIcon = document.getElementById("copy-icon");

  navigator.clipboard.writeText(text).then(() => {
    if (btnText && copyIcon) {
      btnText.textContent = "Copied!";
      btn.classList.add("btn-copied");
      copyIcon.querySelector("use")?.setAttribute("href", "#icon-check");
      setTimeout(() => {
        btnText.textContent = "Copy as text";
        btn.classList.remove("btn-copied");
        copyIcon.querySelector("use")?.setAttribute("href", "#icon-copy");
      }, 2000);
    }
    announceStatus("Plan summary copied to clipboard!");
  }).catch(() => {
    alert("Could not access clipboard.");
  });
}

/**
 * Initialize theme and font size controls.
 */
function initAccessibilityControls() {
  // 3-Button Font Size Control
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

  // Legacy select if present
  const fontSelect = document.getElementById("font-size-select");
  if (fontSelect) {
    fontSelect.addEventListener("change", (e) => {
      document.documentElement.setAttribute("data-font-size", e.target.value);
    });
  }

  // Theme toggle with aria-pressed and text label
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

  // Mobile "Edit details" button
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

  // Tabs
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => activateTab(btn.getAttribute("data-tab")));
  });
  const tablist = document.querySelector(".tabs-list");
  if (tablist) tablist.addEventListener("keydown", onTabKeydown);

  // Forms
  document.getElementById("event-plan-form").addEventListener("submit", onPlanSubmit);
  document.getElementById("chat-query-form").addEventListener("submit", onChatSubmit);

  // Action Buttons
  document.getElementById("btn-export-ics").addEventListener("click", downloadIcs);
  document.getElementById("btn-print-plan").addEventListener("click", () => {
    window.print();
  });
  document.getElementById("btn-copy-text").addEventListener("click", copyPlanAsText);

  // Initial chat greeting
  appendChatMessage("bot", state.chatMessages[0].text);
});
