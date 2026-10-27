/**
 * EventCraft AI - JSDoc Type Definitions for API Responses & Domain Models
 */

/**
 * @typedef {Object} BudgetItem
 * @property {string} category - Budget line item category name.
 * @property {number} percentage - Percentage share of total budget.
 * @property {number} allocated_amount - Exact monetary allocation in target currency.
 * @property {string} description - Description of vendor items covered.
 * @property {string} priority - Priority level (High, Medium, Standard).
 * @property {string} tips - Practical spending recommendation.
 */

/**
 * @typedef {Object} BudgetResponse
 * @property {number} total_budget - Total budget amount.
 * @property {number} per_guest_cost - Average allocation per invited guest.
 * @property {string} currency - 3-letter ISO currency code (e.g. INR).
 * @property {number} contingency_fund - Emergency contingency amount.
 * @property {number} contingency_percentage - Emergency buffer percentage.
 * @property {boolean} is_feasible - Financial feasibility determination.
 * @property {Array<string>} feasibility_notes - Optimization suggestions and advisories.
 * @property {Array<BudgetItem>} items - Itemized allocation list.
 */

/**
 * @typedef {Object} TimelineTask
 * @property {string} id - Unique milestone task identifier.
 * @property {string} title - Actionable task summary.
 * @property {string} phase - Planning phase milestone group.
 * @property {string} due_date - ISO date string (YYYY-MM-DD).
 * @property {number} days_before_event - Number of days prior to event.
 * @property {string} priority - Urgency indicator (Urgent Critical, Standard).
 * @property {boolean} is_critical - True if task is critical path.
 * @property {string} status - Completion status (todo, in_progress, done).
 */

/**
 * @typedef {Object} TimelineResponse
 * @property {number} lead_time_days - Available days between today and event.
 * @property {number} standard_lead_time_days - Recommended planning lead time.
 * @property {boolean} is_compressed - True if timeframe is rushed.
 * @property {Array<TimelineTask>} tasks - Chronologically sorted milestone tasks.
 * @property {string|null} rush_warning - Warning text if timeline is compressed.
 */

/**
 * @typedef {Object} VendorChecklistItem
 * @property {string} category - Vendor service category.
 * @property {number} budget_cap - Target budget cap for vendor contract.
 * @property {string} booking_deadline - Final date to execute contract (YYYY-MM-DD).
 * @property {number} lead_time_days - Days before event when booking must occur.
 * @property {Array<string>} questions_to_ask - Recommended interview vetting questions.
 * @property {string} status - Workflow status (todo, contacted, booked).
 */

/**
 * @typedef {Object} CreativeIdeas
 * @property {Array<string>} themes - Bespoke creative theme titles.
 * @property {Array<string>} menu_ideas - Catering and dietary suggestions.
 * @property {Array<string>} activities - Guest engagement and entertainment ideas.
 * @property {Array<string>} decor_tips - Ambient visual design recommendations.
 * @property {Array<string>} personal_touches - Personalized signature guest details.
 * @property {"ai"|"fallback"} source - Provenance tag indicating AI or curated template origin.
 */

/**
 * @typedef {Object} PlanResponse
 * @property {string} event_type - Event category (wedding, birthday, community).
 * @property {string} event_date - Target date (YYYY-MM-DD).
 * @property {number} guest_count - Number of confirmed/projected attendees.
 * @property {number} total_budget - Total budget amount.
 * @property {string} currency - Target currency symbol or code.
 * @property {string} city - Host city or location.
 * @property {string} vibe - Aesthetic vibe keyword.
 * @property {BudgetResponse} budget - Balanced budget breakdown.
 * @property {TimelineResponse} timeline - Backward-scheduled milestone timeline.
 * @property {Array<VendorChecklistItem>} vendors - Vendor booking checklist.
 * @property {Array<string>} warnings - Consolidated budget and timeline alerts.
 * @property {CreativeIdeas|null} ideas - Creative themes, decor, and culinary concepts.
 */

/**
 * @typedef {Object} ChatRefineResponse
 * @property {string} reply - Assistant guidance response.
 * @property {"ai"|"fallback"} source - Origin of answer.
 */

/**
 * @typedef {Object} AppState
 * @property {PlanResponse|null} currentPlan - Active event plan response.
 * @property {boolean} timelineCriticalOnly - Filter flag for critical milestone tasks.
 * @property {Array<{role: string, text: string}>} chatMessages - Conversation history log.
 */

export {};
