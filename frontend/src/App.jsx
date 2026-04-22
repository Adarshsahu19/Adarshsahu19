import { useEffect, useMemo, useState } from 'react'
import VoiceAssistant from './components/VoiceAssistant'
import { createSession, sendMessage } from './api'

export default function App() {
  const [sessionId, setSessionId] = useState('')
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [messages, setMessages] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    async function bootstrapSession() {
      try {
        const session = await createSession()
        setSessionId(session.session_id)
      } catch {
        setError('Unable to create assistant session.')
      }
    }
    bootstrapSession()
  }, [])

  const canSend = useMemo(() => input.trim().length > 0 && !loading && Boolean(sessionId), [input, loading, sessionId])

  const askAssistant = async (message) => {
    if (!sessionId || !message.trim()) return
    setLoading(true)
    setError('')

    const userMessage = { role: 'user', text: message }
    setMessages((prev) => [...prev, userMessage])

    try {
      const response = await sendMessage(sessionId, message)
      setMessages((prev) => [...prev, { role: 'assistant', text: response.reply }])
      setInput('')
    } catch {
      setError('Assistant response failed. Make sure backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const onSubmit = async (event) => {
    event.preventDefault()
    await askAssistant(input)
  }

  return (
    <main className="container">
      <header>
        <h1>AI Voice Assistant</h1>
        <p>Production-ready starter with speech-to-text input and AI backend APIs.</p>
        <small>Session: {sessionId || 'creating...'}</small>
      </header>

      <VoiceAssistant onTranscript={askAssistant} />

      <section className="messages">
        {messages.map((message, index) => (
          <div key={`${message.role}-${index}`} className={`bubble ${message.role}`}>
            <strong>{message.role === 'user' ? 'You' : 'Assistant'}:</strong> {message.text}
          </div>
        ))}
      </section>

      <form onSubmit={onSubmit} className="composer">
        <input
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button disabled={!canSend}>{loading ? 'Thinking...' : 'Send'}</button>
      </form>

      {error && <p className="error">{error}</p>}
    </main>
  )
}
