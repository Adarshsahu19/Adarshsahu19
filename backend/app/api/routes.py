from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.models.schemas import ChatRequest, ChatResponse, HealthResponse, SessionResponse
from app.services.assistant import AssistantService

router = APIRouter(prefix='/api', tags=['assistant'])
assistant_service = AssistantService()


@router.get('/health', response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@router.post('/sessions', response_model=SessionResponse)
def create_session() -> SessionResponse:
    return SessionResponse(session_id=str(uuid4()), created_at=datetime.utcnow())


@router.post('/chat', response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    reply, created_at = assistant_service.generate_reply(payload.session_id, payload.message)
    return ChatResponse(session_id=payload.session_id, reply=reply, created_at=created_at)


@router.websocket('/ws/voice/{session_id}')
async def voice_socket(websocket: WebSocket, session_id: str) -> None:
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            transcript = data.get('transcript', '')
            if not transcript:
                await websocket.send_json({'error': 'No transcript provided'})
                continue

            reply, created_at = assistant_service.generate_reply(session_id, transcript)
            await websocket.send_json(
                {
                    'session_id': session_id,
                    'transcript': transcript,
                    'reply': reply,
                    'created_at': created_at.isoformat(),
                }
            )
    except WebSocketDisconnect:
        return
