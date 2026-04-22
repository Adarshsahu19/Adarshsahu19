# AI Voice Assistant (Full-Stack)

A full-scale starter project for an **AI Voice Assistant** with:
- **Frontend**: React + Vite, text and voice input using browser speech recognition.
- **Backend**: FastAPI, chat endpoints, session lifecycle, and websocket voice channel.
- **AI layer**: OpenAI Chat Completions (with graceful fallback when API key is missing).

## Project Structure

```text
backend/
  app/
    api/routes.py
    core/config.py
    models/schemas.py
    services/assistant.py
  requirements.txt
frontend/
  src/
    components/VoiceAssistant.jsx
    App.jsx
    api.js
    main.jsx
    styles.css
  package.json
docker-compose.yml
.env.example
```

## Quick Start

### Option 1: Docker Compose (recommended)

1. Copy env file:
   ```bash
   cp .env.example .env
   ```
2. Add your key in `.env` (optional but recommended):
   ```env
   OPENAI_API_KEY=your_key_here
   OPENAI_MODEL=gpt-4o-mini
   ```
3. Run:
   ```bash
   docker compose up
   ```
4. Open app: http://localhost:5173
5. Backend API docs: http://localhost:8000/docs

### Option 2: Manual setup

#### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

- `GET /api/health` → basic service health.
- `POST /api/sessions` → create a new assistant session.
- `POST /api/chat` → send a text message to assistant.
- `WS /api/ws/voice/{session_id}` → streaming voice transcript channel.

## Notes

- Browser voice input uses `SpeechRecognition`/`webkitSpeechRecognition` where supported.
- If `OPENAI_API_KEY` is absent, backend returns deterministic fallback responses.
