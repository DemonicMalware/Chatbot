from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.chatbot import next_messages
from app.config import get_settings
from app.storage import store
from app.whatsapp_client import send_text_message

app = FastAPI(title="IOMA WhatsApp Bot")


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
async def receive_message(request: Request) -> dict[str, bool]:
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
                for reply in replies:
                    await send_text_message(from_phone, reply)

    return {"ok": True}
