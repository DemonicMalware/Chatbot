from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import re
import uuid


class Step(str, Enum):
    START = "start"
    ASK_FIRST_NAME = "ask_first_name"
    ASK_LAST_NAME = "ask_last_name"
    ASK_DNI = "ask_dni"
    ASK_MEMBER_ID = "ask_member_id"
    ASK_PROCEDURE = "ask_procedure"
    ASK_DETAILS = "ask_details"
    DONE = "done"


@dataclass
class ConversationState:
    user_id: str
    step: Step = Step.START
    first_name: str | None = None
    last_name: str | None = None
    dni: str | None = None
    member_id: str | None = None
    procedure: str | None = None
    details: str | None = None
    ticket_id: str | None = None
    completed_at: datetime | None = None
    persisted: bool = False
    messages: list[str] = field(default_factory=list)


PROCEDURES = {
    "1": "Consulta de cobertura",
    "2": "Autorización de práctica",
    "3": "Alta o actualización de datos",
    "4": "Estado de trámite",
    "5": "Otro",
}


def normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def valid_dni(text: str) -> str | None:
    digits = re.sub(r"\D", "", text)
    if 7 <= len(digits) <= 8:
        return digits
    return None


def next_messages(state: ConversationState, incoming_text: str) -> list[str]:
    msg = incoming_text.strip()
    state.messages.append(msg)

    if state.step == Step.START:
        state.step = Step.ASK_FIRST_NAME
        return [
            "¡Hola! 👋 Soy el asistente virtual de IOMA (área personal).",
            "Esta conversación registra datos para gestionar trámites de manera segura.",
            "¿Cuál es tu nombre?",
        ]

    if state.step == Step.ASK_FIRST_NAME:
        if len(msg) < 2:
            return ["Por favor, escribí tu nombre para continuar."]
        state.first_name = msg
        state.step = Step.ASK_LAST_NAME
        return ["Gracias. ¿Cuál es tu apellido?"]

    if state.step == Step.ASK_LAST_NAME:
        if len(msg) < 2:
            return ["Por favor, escribí tu apellido para continuar."]
        state.last_name = msg
        state.step = Step.ASK_DNI
        return ["Perfecto. Ahora indicame tu DNI (solo números)."]

    if state.step == Step.ASK_DNI:
        dni = valid_dni(msg)
        if not dni:
            return ["El DNI no parece válido. Ejemplo: 30111222"]
        state.dni = dni
        state.step = Step.ASK_MEMBER_ID
        return ["¿Cuál es tu número de afiliado/a de IOMA?"]

    if state.step == Step.ASK_MEMBER_ID:
        if len(msg) < 4:
            return ["Necesito un número de afiliado/a válido para continuar."]
        state.member_id = re.sub(r"\s+", "", msg)
        state.step = Step.ASK_PROCEDURE
        options = "\n".join([f"{k}. {v}" for k, v in PROCEDURES.items()])
        return ["¿Qué necesitás hacer hoy? Respondé con el número de opción:\n" + options]

    if state.step == Step.ASK_PROCEDURE:
        key = normalize(msg)
        if key not in PROCEDURES:
            return ["No entendí la opción. Respondé con 1, 2, 3, 4 o 5."]
        state.procedure = PROCEDURES[key]
        state.step = Step.ASK_DETAILS
        return [f"Seleccionaste: {state.procedure}. Contame más detalles del trámite."]

    if state.step == Step.ASK_DETAILS:
        if len(msg) < 8:
            return ["Necesito un poco más de detalle para poder ayudarte mejor."]
        state.details = msg
        state.ticket_id = f"IOMA-{uuid.uuid4().hex[:8].upper()}"
        state.completed_at = datetime.now(timezone.utc)
        state.step = Step.DONE
        state.persisted = False
        return [
            "✅ ¡Listo! Registré tu solicitud.",
            f"Tu número de trámite es: *{state.ticket_id}*",
            "Un/a operador/a autorizado/a del área personal te va a responder por este medio.",
        ]

    if normalize(msg) in {"menu", "inicio", "empezar", "nuevo"}:
        state.step = Step.ASK_FIRST_NAME
        state.first_name = None
        state.last_name = None
        state.dni = None
        state.member_id = None
        state.procedure = None
        state.details = None
        state.ticket_id = None
        state.completed_at = None
        state.persisted = False
        return ["Perfecto, empezamos de nuevo. ¿Cuál es tu nombre?"]

    return ["Ya tengo tu solicitud registrada. Si querés iniciar una nueva, escribí *MENU*."]
