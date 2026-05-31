from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from app.schemas import CandidateAnswer, InterviewSession, InterviewTurn


class SessionRepository:
    def __init__(self) -> None:
        self._sessions: dict[str, InterviewSession] = {}
        self._turns: dict[str, list[InterviewTurn]] = defaultdict(list)

    async def create_session(self, session: InterviewSession) -> InterviewSession:
        self._sessions[session.id] = session
        return session

    async def get_session(self, session_id: str) -> InterviewSession | None:
        return self._sessions.get(session_id)

    async def update_session(self, session: InterviewSession) -> InterviewSession:
        self._sessions[session.id] = session
        return session

    async def list_turns(self, session_id: str) -> list[InterviewTurn]:
        return list(self._turns.get(session_id, []))

    async def append_turn(self, turn: InterviewTurn) -> InterviewTurn:
        self._turns[turn.session_id].append(turn)
        return turn

    async def save_answer(
        self,
        session_id: str,
        turn_id: str,
        answer: CandidateAnswer,
        answered_at: datetime | None = None,
    ) -> InterviewTurn | None:
        turns = self._turns.get(session_id, [])
        for index, turn in enumerate(turns):
            if turn.id == turn_id:
                updated = turn.model_copy(update={"answer": answer, "answered_at": answered_at})
                turns[index] = updated
                return updated
        return None
