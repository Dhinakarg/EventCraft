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
 * Format currency amount safely.
 * @param {number} amount 
 * @param {string} currency 
 * @returns {string}
 */
function formatCurrency(amount, currency = "USD") {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: currency || "USD",
    maximumFractionDigits: 0,
  }).format(amount || 0);
}

/**
 * Create DOM element safely with textContent or children.
 * @param {string} tag 
 * @param {Object} attrs 
 * @param {Array<HTMLElement|string>} children 
 * @returns {HTMLElement}
 */
function createEl(tag, attrs = {}, children = []) {
  const elem = document.createElement(tag);
  for (const [key, val] of Object.entries(attrs)) {
    if (key === "className") {
      elem.className = val;
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
    } else if (child instanceof HTMLElement) {
      elem.appendChild(child);
    }
  }
  return elem;
}

/**
 * Render warnings banner if warnings exist.
 * @param {Array<string>} warnings 
 * @param {HTMLElement} container 
 */
function renderWarnings(warnings, container) {
  container.replaceChildren();
  if (!warnings || warnings.length === 0) return;

  const box = createEl("div", { className: "alert-box", role: "alert" });
  box.appendChild(createEl("div", { className: "alert-title" }, ["⚠️ Planning Alerts & Recommendations:"]));
  const ul = createEl("ul", { style: "padding-left: 20px;" });
  for (const w of warnings) {
    ul.appendChild(createEl("li", {}, [w]));
  }
  box.appendChild(ul);
  container.appendChild(box);
}

/**
 * Render Budget Table and Accessible Bar Chart with visible text values.
 * @param {Object} budget 
 * @param {HTMLElement} container 
 */
function renderBudgetTab(budget, container) {
  container.replaceChildren();

  // Metrics summary
  const summaryBox = createEl("div", { style: "display: flex; gap: 16px; margin-bottom: 20px; flex-wrap: wrap;" }, [
    createEl("div", { className: "alert-box", style: "flex: 1; min-width: 180px; margin-bottom: 0; background: var(--bg-surface-alt); color: var(--text-main);" }, [
      createEl("div", { style: "font-size: 0.85rem; color: var(--text-muted);" }, ["Total Budget"]),
      createEl("div", { style: "font-size: 1.3rem; font-weight: 800;" }, [formatCurrency(budget.total_budget, budget.currency)]),
    ]),
    createEl("div", { className: "alert-box", style: "flex: 1; min-width: 180px; margin-bottom: 0; background: var(--bg-surface-alt); color: var(--text-main);" }, [
      createEl("div", { style: "font-size: 0.85rem; color: var(--text-muted);" }, ["Per Guest Spend"]),
      createEl("div", { style: "font-size: 1.3rem; font-weight: 800;" }, [formatCurrency(budget.per_guest_cost, budget.currency)]),
    ]),
    createEl("div", { className: "alert-box", style: "flex: 1; min-width: 180px; margin-bottom: 0; background: var(--bg-surface-alt); color: var(--text-main);" }, [
      createEl("div", { style: "font-size: 0.85rem; color: var(--text-muted);" }, [`Contingency Buffer (${budget.contingency_percentage}%)`]),
      createEl("div", { style: "font-size: 1.3rem; font-weight: 800;" }, [formatCurrency(budget.contingency_fund, budget.currency)]),
    ]),
  ]);
  container.appendChild(summaryBox);

  // Accessible HTML Table
  const table = createEl("table", { className: "budget-table", aria: { label: "Budget allocations by category" } });
  const caption = createEl("caption", { className: "sr-status" }, ["Itemized Budget Breakdown Table"]);
  table.appendChild(caption);

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
    const tr = createEl("tr", {}, [
      createEl("td", { style: "font-weight: 600;" }, [item.category]),
      createEl("td", {}, [formatCurrency(item.allocated_amount, budget.currency)]),
      createEl("td", {}, [`${item.percentage}%`]),
      createEl("td", {}, [item.priority]),
    ]);
    tbody.appendChild(tr);
  }
  table.appendChild(tbody);
  container.appendChild(table);

  // Accessible Bar Chart (with text values, not relying on color alone)
  const chartHeading = createEl("h3", { style: "font-size: 1.1rem; margin-top: 24px; margin-bottom: 12px;" }, [
    "📊 Category Allocation Chart (with text values)",
  ]);
  const chartWrapper = createEl("div", { className: "chart-wrapper", role: "region", aria: { label: "Visual allocation bar chart" } });

  for (const item of budget.items) {
    const row = createEl("div", { className: "chart-row" }, [
      createEl("div", { className: "chart-labels" }, [
        createEl("span", {}, [item.category]),
        createEl("span", {}, [`${formatCurrency(item.allocated_amount, budget.currency)} (${item.percentage}%)`]),
      ]),
      createEl("div", { className: "chart-bar-outer" }, [
        createEl("div", {
          className: "chart-bar-inner",
          style: `width: ${Math.max(10, Math.min(item.percentage * 2.2, 100))}%;`,
          role: "progressbar",
          aria: { valuenow: String(item.percentage), valuemin: "0", valuemax: "100", label: `${item.category}: ${item.percentage}%` },
        }, [`${item.percentage}%`]),
      ]),
    ]);
    chartWrapper.appendChild(row);
  }

  container.appendChild(chartHeading);
  container.appendChild(chartWrapper);
}

/**
 * Render Timeline Tasks.
 * @param {Object} timeline 
 * @param {HTMLElement} container 
 */
function renderTimelineTab(timeline, container) {
  container.replaceChildren();

  if (timeline.rush_warning) {
    const rushAlert = createEl("div", { className: "alert-box", style: "border-left: 4px solid var(--danger);", role: "alert" }, [
      createEl("div", { className: "alert-title" }, ["🚨 Rush Timeline Notice"]),
      createEl("p", {}, [timeline.rush_warning]),
    ]);
    container.appendChild(rushAlert);
  }

  const h = createEl("h3", { style: "font-size: 1.1rem; margin-bottom: 16px;" }, [
    `📅 Scheduled Tasks (${timeline.lead_time_days} Days Lead Time)`,
  ]);
  container.appendChild(h);

  const list = createEl("div", { role: "list" });
  for (const task of timeline.tasks || []) {
    const item = createEl("div", { className: "timeline-item", role: "listitem" }, [
      createEl("div", { className: "timeline-meta" }, [
        `Due: ${task.due_date} (${task.days_before_event} days before event) • Phase: ${task.phase}`,
      ]),
      createEl("div", { className: "timeline-title" }, [task.title]),
      createEl("span", {
        className: "badge",
        style: task.is_critical ? "background: var(--warning-bg); color: var(--warning-text);" : "background: var(--bg-surface-alt);",
      }, [task.priority]),
    ]);
    list.appendChild(item);
  }
  container.appendChild(list);
}

/**
 * Render Vendor Checklist with progress and localStorage persistence.
 * @param {Array} vendors 
 * @param {HTMLElement} container 
 */
function renderVendorsTab(vendors, container) {
  container.replaceChildren();

  // Load saved checklist states from localStorage
  const storageKey = `eventcraft_vendors_${state.currentPlan ? state.currentPlan.event_date : "default"}`;
  let savedStates = {};
  try {
    savedStates = JSON.parse(localStorage.getItem(storageKey) || "{}");
  } catch {
    savedStates = {};
  }

  const progressHeader = createEl("div", {
    className: "alert-box",
    style: "background: var(--bg-surface-alt); color: var(--text-main); margin-bottom: 20px;",
  });
  const updateProgress = () => {
    const total = vendors.length;
    let completed = 0;
    for (const v of vendors) {
      if (savedStates[v.category]) completed++;
    }
    progressHeader.replaceChildren(
      createEl("div", { style: "font-weight: 700;" }, [`Vendor Checklist Progress: ${completed} of ${total} Booked`])
    );
  };
  updateProgress();
  container.appendChild(progressHeader);

  for (const v of vendors) {
    const isChecked = Boolean(savedStates[v.category]);
    const checkbox = createEl("input", {
      type: "checkbox",
      className: "check-box",
      id: `chk-${v.category.replace(/[^a-zA-Z0-9]/g, "_")}`,
    });
    checkbox.checked = isChecked;

    checkbox.addEventListener("change", () => {
      savedStates[v.category] = checkbox.checked;
      try {
        localStorage.setItem(storageKey, JSON.stringify(savedStates));
      } catch {
        // quota exceeded or disabled
      }
      updateProgress();
      announceStatus(`${v.category} marked as ${checkbox.checked ? "booked" : "pending"}.`);
    });

    const qList = createEl("ul", { style: "padding-left: 20px; font-size: 0.9rem; margin-top: 6px; color: var(--text-muted);" });
    for (const q of v.questions_to_ask || []) {
      qList.appendChild(createEl("li", {}, [q]));
    }

    const group = createEl("div", { className: "checklist-group" }, [
      createEl("div", { className: "check-item" }, [
        checkbox,
        createEl("label", { htmlFor: checkbox.id, className: "check-label" }, [
          createEl("div", { style: "font-weight: 700; font-size: 1.05rem;" }, [v.category]),
          createEl("div", { style: "font-size: 0.85rem; color: var(--text-muted);" }, [
            `Cap: ${formatCurrency(v.budget_cap)} • Deadline: ${v.booking_deadline} (${v.lead_time_days} days out)`,
          ]),
        ]),
      ]),
      createEl("div", { style: "margin-top: 8px; font-weight: 600; font-size: 0.85rem;" }, ["Interview Questions:"]),
      qList,
    ]);
    container.appendChild(group);
  }
}

/**
 * Render Creative Ideas with AI vs Template badge.
 * @param {Object} ideas 
 * @param {HTMLElement} container 
 */
function renderIdeasTab(ideas, container) {
  container.replaceChildren();
  if (!ideas) {
    container.appendChild(createEl("p", {}, ["No ideas generated yet."]));
    return;
  }

  const isAi = ideas.source === "ai";
  const badge = createEl("span", {
    className: `badge ${isAi ? "badge-ai" : "badge-tmpl"}`,
  }, [isAi ? "✨ AI-generated" : "📋 Template ideas"]);
  container.appendChild(badge);

  // Themes
  const themesBlock = createEl("div", { style: "margin-bottom: 20px;" }, [
    createEl("h3", { style: "font-size: 1.1rem; margin-bottom: 8px;" }, ["🎨 Bespoke Theme Concepts"]),
  ]);
  const themesUl = createEl("ul", { style: "padding-left: 20px;" });
  for (const t of ideas.themes || []) {
    themesUl.appendChild(createEl("li", { style: "margin-bottom: 4px; font-weight: 600;" }, [t]));
  }
  themesBlock.appendChild(themesUl);
  container.appendChild(themesBlock);

  // Menu ideas
  if (ideas.menu_ideas && ideas.menu_ideas.length) {
    const menuBlock = createEl("div", { style: "margin-bottom: 20px;" }, [
      createEl("h4", { style: "font-size: 1rem; margin-bottom: 6px;" }, ["🍽️ Menu & Culinary Ideas"]),
    ]);
    const menuUl = createEl("ul", { style: "padding-left: 20px; font-size: 0.95rem;" });
    for (const m of ideas.menu_ideas) menuUl.appendChild(createEl("li", {}, [m]));
    menuBlock.appendChild(menuUl);
    container.appendChild(menuBlock);
  }

  // Activities
  if (ideas.activities && ideas.activities.length) {
    const actBlock = createEl("div", { style: "margin-bottom: 20px;" }, [
      createEl("h4", { style: "font-size: 1rem; margin-bottom: 6px;" }, ["🎲 Interactive Activities"]),
    ]);
    const actUl = createEl("ul", { style: "padding-left: 20px; font-size: 0.95rem;" });
    for (const a of ideas.activities) actUl.appendChild(createEl("li", {}, [a]));
    actBlock.appendChild(actUl);
    container.appendChild(actBlock);
  }

  // Decor & Personal Touches
  if (ideas.decor_tips && ideas.decor_tips.length) {
    const decorBlock = createEl("div", { style: "margin-bottom: 20px;" }, [
      createEl("h4", { style: "font-size: 1rem; margin-bottom: 6px;" }, ["💐 Ambient Decor Suggestions"]),
    ]);
    const decorUl = createEl("ul", { style: "padding-left: 20px; font-size: 0.95rem;" });
    for (const d of ideas.decor_tips) decorUl.appendChild(createEl("li", {}, [d]));
    decorBlock.appendChild(decorUl);
    container.appendChild(decorBlock);
  }

  if (ideas.personal_touches && ideas.personal_touches.length) {
    const touchBlock = createEl("div", { className: "alert-box", style: "background: var(--bg-surface-alt); color: var(--text-main);" }, [
      createEl("div", { style: "font-weight: 700; margin-bottom: 6px;" }, ["Signature Personal Touches:"]),
    ]);
    const touchUl = createEl("ul", { style: "padding-left: 20px;" });
    for (const pt of ideas.personal_touches) touchUl.appendChild(createEl("li", {}, [pt]));
    touchBlock.appendChild(touchUl);
    container.appendChild(touchBlock);
  }
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
    if (p.id === `panel-${tabKey}`) {
      p.classList.add("active");
    } else {
      p.classList.remove("active");
    }
  });
}

/**
 * ARIA Tabs Keyboard Navigation (Left, Right, Home, End).
 * @param {KeyboardEvent} e 
 */
function onTabKeydown(e) {
  const tabs = Array.from(document.querySelectorAll(".tab-btn"));
  const curr = tabs.indexOf(document.activeElement);
  if (curr === -1) return;

  let nextIdx = null;
  if (e.key === "ArrowRight") {
    nextIdx = (curr + 1) % tabs.length;
  } else if (e.key === "ArrowLeft") {
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
 * Submit plan form to POST /api/plan.
 * @param {Event} e 
 */
async function onPlanSubmit(e) {
  e.preventDefault();

  const btn = document.getElementById("btn-submit-plan");
  const origText = btn.textContent;
  btn.textContent = "⏳ Calculating Master Plan...";
  btn.disabled = true;
  announceStatus("Calculating event master plan. Please wait.");

  const priorities = [];
  const pSelect = document.getElementById("priorities");
  for (const opt of pSelect.selectedOptions) {
    if (opt.value && priorities.length < 3) priorities.push(opt.value);
  }

  const payload = {
    event_type: document.getElementById("event_type").value,
    event_date: document.getElementById("event_date").value,
    guest_count: parseInt(document.getElementById("guest_count").value, 10),
    total_budget: parseFloat(document.getElementById("total_budget").value),
    currency: "USD",
    vibe: document.getElementById("vibe").value.trim() || "Modern",
    city: document.getElementById("city").value.trim() || "",
    priorities: priorities,
    notes: document.getElementById("custom_notes").value.trim(),
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

    renderWarnings(plan.warnings, document.getElementById("warnings-container"));
    renderBudgetTab(plan.budget, document.getElementById("budget-output"));
    renderTimelineTab(plan.timeline, document.getElementById("timeline-output"));
    renderVendorsTab(plan.vendors, document.getElementById("vendors-output"));
    renderIdeasTab(plan.ideas, document.getElementById("ideas-output"));

    activateTab("budget");
    announceStatus("Event plan generated successfully! Displaying budget breakdown.");
  } catch (err) {
    alert(`Could not generate plan: ${err.message}`);
    announceStatus(`Error generating plan: ${err.message}`);
  } finally {
    btn.textContent = origText;
    btn.disabled = false;
  }
}

/**
 * Send chat question to POST /api/chat.
 * @param {Event} e 
 */
async function onChatSubmit(e) {
  e.preventDefault();
  const input = document.getElementById("chat-input");
  const query = input.value.trim();
  if (!query) return;

  appendChatMessage("user", query);
  input.value = "";
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
 * Copy plain text summary of plan to clipboard.
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

  navigator.clipboard.writeText(text).then(() => {
    alert("Plan summary copied to clipboard!");
    announceStatus("Plan summary copied to clipboard.");
  }).catch(() => {
    alert("Could not access clipboard.");
  });
}

/**
 * Initialize theme and font size selectors.
 */
function initAccessibilityControls() {
  const fontSelect = document.getElementById("font-size-select");
  fontSelect.addEventListener("change", (e) => {
    document.documentElement.setAttribute("data-font-size", e.target.value);
    announceStatus(`Text size set to ${e.target.value}.`);
  });

  const themeBtn = document.getElementById("theme-btn");
  themeBtn.addEventListener("click", () => {
    const cur = document.documentElement.getAttribute("data-theme");
    const next = cur === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    announceStatus(`Theme switched to ${next} mode.`);
  });
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

  // Generate initial plan automatically
  document.getElementById("event-plan-form").dispatchEvent(new Event("submit"));
});
