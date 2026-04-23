from __future__ import annotations

from threading import Lock
from app.chatbot import ConversationState


class InMemoryStateStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._states: dict[str, ConversationState] = {}

    def get(self, user_id: str) -> ConversationState:
        with self._lock:
            if user_id not in self._states:
                self._states[user_id] = ConversationState(user_id=user_id)
            return self._states[user_id]


store = InMemoryStateStore()
