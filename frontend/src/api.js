const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function createSession() {
  const response = await fetch(`${API_BASE}/api/sessions`, { method: 'POST' })
  if (!response.ok) throw new Error('Failed to create session')
  return response.json()
}

export async function sendMessage(sessionId, message) {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message })
  })
  if (!response.ok) throw new Error('Failed to get assistant response')
  return response.json()
}
