/**
 * EventCraft AI - DOM & Formatting Utilities
 * Pure textContent/createElement with zero innerHTML usage.
 */

/**
 * Announce messages to screen readers via aria-live region.
 * @param {string} msg 
 */
export function announceStatus(msg) {
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
export function formatCurrency(amount, currency = "INR") {
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
export function createSvgIcon(name, extraClass = "") {
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
export function createEl(tag, attrs = {}, children = []) {
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
export function formatFriendlyDate(dateStr) {
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
