/**
 * EventCraft AI - Warnings & Advisories Renderer
 */

import { announceStatus, createEl, createSvgIcon } from "./utils.js";

/**
 * Render dismissible alert region with severity levels (info, warning, critical).
 * Rush timeline notice receives "critical" style and plain-language explanation.
 * @param {Array<string>} warnings 
 * @param {string|null} rushWarning 
 * @param {HTMLElement} container 
 */
export function renderWarnings(warnings, rushWarning, container) {
  if (!container) return;
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
