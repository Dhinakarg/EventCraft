/**
 * Unit tests for static/js/utils.js pure formatters using node:test.
 */
import test from "node:test";
import assert from "node:assert/strict";
import { formatCurrency, formatFriendlyDate } from "../../static/js/utils.js";

test("formatCurrency formats INR by default without fraction digits", () => {
  const result = formatCurrency(50000);
  assert.ok(result.includes("50,000"));
});

test("formatCurrency handles zero and falsy numbers gracefully", () => {
  const zero = formatCurrency(0);
  assert.ok(zero.includes("0"));
  const nanVal = formatCurrency(null);
  assert.ok(nanVal.includes("0"));
});

test("formatCurrency formats other currency codes", () => {
  const usd = formatCurrency(1200, "USD");
  assert.ok(usd.includes("1,200"));
});

test("formatFriendlyDate parses YYYY-MM-DD into readable English format", () => {
  const formatted = formatFriendlyDate("2027-06-15");
  assert.strictEqual(formatted, "Jun 15, 2027");
});

test("formatFriendlyDate handles empty or invalid date strings", () => {
  assert.strictEqual(formatFriendlyDate(""), "");
  assert.strictEqual(formatFriendlyDate(null), "");
  assert.strictEqual(formatFriendlyDate("not-a-date"), "not-a-date");
});
