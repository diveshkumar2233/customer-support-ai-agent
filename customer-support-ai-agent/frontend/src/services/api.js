/**
 * API service layer — the only place that knows the backend's URL shape.
 * WHY: keeps components free of fetch() boilerplate and makes it trivial
 * to swap the base URL (e.g. via an env var) for different environments.
 */
const API_BASE = "/api/v1";

export async function sendChatMessage(sessionId, customerId, message) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, customer_id: customerId, message }),
  });
  if (!res.ok) throw new Error(`Chat request failed: ${res.status}`);
  return res.json();
}

export async function fetchOrderStatus(orderId) {
  const res = await fetch(`${API_BASE}/orders/${orderId}`);
  if (!res.ok) throw new Error(`Order lookup failed: ${res.status}`);
  return res.json();
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}
