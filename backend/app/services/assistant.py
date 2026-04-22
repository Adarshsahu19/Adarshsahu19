from collections import defaultdict
from datetime import datetime
from openai import OpenAI

from app.core.config import get_settings


class AssistantService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.histories: dict[str, list[dict[str, str]]] = defaultdict(list)
        self.client = OpenAI(api_key=self.settings.openai_api_key) if self.settings.openai_api_key else None

    def _fallback_reply(self, message: str) -> str:
        return (
            "I heard you say: "
            f"'{message}'. This is a fallback assistant response because OPENAI_API_KEY is not configured."
        )

    def generate_reply(self, session_id: str, message: str) -> tuple[str, datetime]:
        self.histories[session_id].append({'role': 'user', 'content': message})

        if not self.client:
            reply = self._fallback_reply(message)
        else:
            completion = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {
                        'role': 'system',
                        'content': (
                            'You are a production-grade AI voice assistant. '
                            'Provide concise, helpful conversational responses.'
                        ),
                    },
                    *self.histories[session_id],
                ],
                temperature=0.5,
            )
            reply = completion.choices[0].message.content or "I couldn't generate a response."

        self.histories[session_id].append({'role': 'assistant', 'content': reply})
        return reply, datetime.utcnow()
