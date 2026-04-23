from __future__ import annotations

import httpx

from app.config import get_settings


async def send_text_message(to_phone: str, body: str) -> None:
    settings = get_settings()
    if not settings.whatsapp_access_token or not settings.whatsapp_phone_number_id:
        # modo desarrollo: sin token, no falla silenciosamente en webhook
        return

    url = (
        f"https://graph.facebook.com/{settings.graph_api_version}/"
        f"{settings.whatsapp_phone_number_id}/messages"
    )
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"preview_url": False, "body": body},
    }
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_access_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        await client.post(url, json=payload, headers=headers)
