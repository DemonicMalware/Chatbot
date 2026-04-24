from __future__ import annotations

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import AuthError, authenticate
from app.chatbot import Step, next_messages
from app.config import get_settings
from app.database import get_session, init_db
from app.repository import get_case_by_ticket, log_access, save_case_from_state, security_review
from app.storage import store
from app.whatsapp_client import send_text_message

app = FastAPI(title="IOMA WhatsApp Bot")


@app.on_event("startup")
async def startup() -> None:
    await init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/webhook", response_class=PlainTextResponse)
def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
) -> str:
    settings = get_settings()
    if hub_mode == "subscribe" and hub_verify_token == settings.verify_token:
        return hub_challenge
    raise HTTPException(status_code=403, detail="Token de verificación inválido")


@app.post("/webhook")
async def receive_message(request: Request, session: AsyncSession = Depends(get_session)) -> dict[str, bool]:
    body = await request.json()

    entries = body.get("entry", [])
    for entry in entries:
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages", [])
            for message in messages:
                from_phone = message.get("from")
                text = message.get("text", {}).get("body")
                if not from_phone or not text:
                    continue

                state = store.get(from_phone)
                replies = next_messages(state, text)
                if state.step == Step.DONE and state.ticket_id and not state.persisted:
                    await save_case_from_state(session, state, from_phone)
                    state.persisted = True

                for reply in replies:
                    await send_text_message(from_phone, reply)

    return {"ok": True}


@app.get("/admin/cases/{ticket_id}")
async def admin_get_case(
    ticket_id: str,
    request: Request,
    reason: str = Query(..., min_length=8, description="Motivo de acceso"),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    x_device_id: str = Header(default="unknown", alias="X-Device-ID"),
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    try:
        actor = authenticate(x_api_key)
    except AuthError as err:
        await log_access(
            session,
            actor_id="unknown",
            action="get_case",
            reason=reason,
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown"),
            device_id=x_device_id,
            outcome="denied",
        )
        raise HTTPException(status_code=401, detail=str(err)) from err

    data = await get_case_by_ticket(session, ticket_id)
    outcome = "success" if data else "not_found"
    await log_access(
        session,
        actor_id=actor.actor_id,
        action="get_case",
        reason=reason,
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "unknown"),
        device_id=x_device_id,
        outcome=outcome,
        role=actor.role,
    )

    if not data:
        raise HTTPException(status_code=404, detail="Trámite no encontrado")
    return data


@app.get("/admin/security/review")
async def admin_security_review(
    request: Request,
    reason: str = Query(..., min_length=8, description="Motivo de acceso"),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    x_device_id: str = Header(default="unknown", alias="X-Device-ID"),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    try:
        actor = authenticate(x_api_key)
    except AuthError as err:
        await log_access(
            session,
            actor_id="unknown",
            action="security_review",
            reason=reason,
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown"),
            device_id=x_device_id,
            outcome="denied",
        )
        raise HTTPException(status_code=401, detail=str(err)) from err

    report = await security_review(session)
    await log_access(
        session,
        actor_id=actor.actor_id,
        action="security_review",
        reason=reason,
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "unknown"),
        device_id=x_device_id,
        outcome="success",
        role=actor.role,
    )
    return report
