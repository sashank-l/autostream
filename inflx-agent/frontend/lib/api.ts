const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function sendMessage(
  sessionId: string | null,
  message: string
): Promise<{ session_id: string }> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message }),
  });
  if (!res.ok) throw new Error(`Chat failed: ${res.status}`);
  return res.json();
}

export async function getLeads(): Promise<{ leads: Array<{
  id: number;
  name: string;
  email: string;
  platform: string;
  captured_at: string;
}> }> {
  const res = await fetch(`${API_BASE}/api/leads`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Leads fetch failed: ${res.status}`);
  return res.json();
}
