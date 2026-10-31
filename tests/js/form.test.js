/**
 * Unit tests for static/js/form.js pure validation functions using node:test.
 */
import test from "node:test";
import assert from "node:assert/strict";
import {
  isValidFutureDate,
  isValidGuestCount,
  isValidBudget,
  calculatePerGuest,
} from "../../static/js/form.js";

test("isValidFutureDate accepts future date and rejects past or invalid dates", () => {
  const referenceToday = new Date("2026-10-28T00:00:00Z");
  assert.strictEqual(isValidFutureDate("2027-01-01", referenceToday), true);
  assert.strictEqual(isValidFutureDate("2025-01-01", referenceToday), false);
  assert.strictEqual(isValidFutureDate("invalid-date", referenceToday), false);
  assert.strictEqual(isValidFutureDate("", referenceToday), false);
});

test("isValidGuestCount validates boundary of 1 to 2000 guests", () => {
  assert.strictEqual(isValidGuestCount(1), true);
  assert.strictEqual(isValidGuestCount(2000), true);
  assert.strictEqual(isValidGuestCount(150), true);
  assert.strictEqual(isValidGuestCount(0), false);
  assert.strictEqual(isValidGuestCount(2001), false);
  assert.strictEqual(isValidGuestCount(-5), false);
  assert.strictEqual(isValidGuestCount("abc"), false);
});

test("isValidBudget validates positive numbers", () => {
  assert.strictEqual(isValidBudget(50000), true);
  assert.strictEqual(isValidBudget("100000"), true);
  assert.strictEqual(isValidBudget(0), false);
  assert.strictEqual(isValidBudget(-100), false);
  assert.strictEqual(isValidBudget("not-a-number"), false);
});

test("calculatePerGuest computes rounded cost per attendee and safeguards negative counts with Math.max", () => {
  assert.strictEqual(calculatePerGuest(100000, 100), 1000);
  assert.strictEqual(calculatePerGuest(100000, 3), 33333);
  assert.strictEqual(calculatePerGuest(100000, -5), 100000);
  assert.strictEqual(calculatePerGuest(50000, 0), 50000);
  assert.strictEqual(calculatePerGuest(0, 100), null);
  assert.strictEqual(calculatePerGuest(-500, 10), null);
  assert.strictEqual(calculatePerGuest("invalid", 50), null);
});
