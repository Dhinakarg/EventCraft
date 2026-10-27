/**
 * EventCraft AI - API Client
 * Clean asynchronous HTTP layer for backend communication.
 */

const BASE_URL = "";

/**
 * Handle API responses safely.
 * @param {Response} res 
 * @returns {Promise<any>}
 */
async function handleResponse(res) {
  if (!res.ok) {
    let errMessage = `Server returned ${res.status}`;
    try {
      const errorData = await res.json();
      if (errorData.detail) {
        errMessage = typeof errorData.detail === "string" 
          ? errorData.detail 
          : JSON.stringify(errorData.detail);
      }
    } catch {
      // fallback to status text
    }
    throw new Error(errMessage);
  }
  return res.json();
}

/**
 * Generate full event plan.
 * @param {Object} planRequest 
 * @returns {Promise<Object>}
 */
export async function generateMasterPlan(planRequest) {
  const res = await fetch(`${BASE_URL}/api/plan/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(planRequest),
  });
  return handleResponse(res);
}

/**
 * Recalculate budget only.
 * @param {Object} planRequest 
 * @returns {Promise<Object>}
 */
export async function fetchBudget(planRequest) {
  const res = await fetch(`${BASE_URL}/api/plan/budget`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(planRequest),
  });
  return handleResponse(res);
}

/**
 * Fetch creative ideas from LLM / fallback.
 * @param {Object} ideaRequest 
 * @returns {Promise<Object>}
 */
export async function fetchCreativeIdeas(ideaRequest) {
  const res = await fetch(`${BASE_URL}/api/ai/ideas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(ideaRequest),
  });
  return handleResponse(res);
}

/**
 * Send chat message to conversational copilot.
 * @param {string} planContext 
 * @param {string} question 
 * @returns {Promise<Object>}
 */
export async function sendChatMessage(planContext, question) {
  const res = await fetch(`${BASE_URL}/api/ai/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ plan_context: planContext, question: question }),
  });
  return handleResponse(res);
}

/**
 * Check backend health status.
 * @returns {Promise<Object>}
 */
export async function checkHealth() {
  const res = await fetch(`${BASE_URL}/health`);
  return handleResponse(res);
}
