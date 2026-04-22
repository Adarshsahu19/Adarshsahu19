import { useMemo, useRef, useState } from 'react'

function browserSpeechRecognition() {
  return window.SpeechRecognition || window.webkitSpeechRecognition
}

export default function VoiceAssistant({ onTranscript }) {
  const [isListening, setIsListening] = useState(false)
  const recognitionRef = useRef(null)

  const isSupported = useMemo(() => Boolean(browserSpeechRecognition()), [])

  const startListening = () => {
    const SpeechRecognition = browserSpeechRecognition()
    if (!SpeechRecognition) return

    const recognition = new SpeechRecognition()
    recognition.lang = 'en-US'
    recognition.interimResults = false
    recognition.maxAlternatives = 1

    recognition.onstart = () => setIsListening(true)
    recognition.onend = () => setIsListening(false)
    recognition.onerror = () => setIsListening(false)

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      onTranscript(transcript)
    }

    recognitionRef.current = recognition
    recognition.start()
  }

  const stopListening = () => {
    recognitionRef.current?.stop()
    setIsListening(false)
  }

  if (!isSupported) {
    return <p className="support-warning">Voice input is not supported in this browser.</p>
  }

  return (
    <div className="voice-controls">
      {!isListening ? (
        <button onClick={startListening}>🎙️ Start Voice Input</button>
      ) : (
        <button className="danger" onClick={stopListening}>⏹ Stop Listening</button>
      )}
    </div>
  )
}
