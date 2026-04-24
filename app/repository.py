from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Select, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.chatbot import ConversationState
from app.models import AccessAuditLog, UserCase
from app.security import decrypt_value, encrypt_value, hash_value


async def save_case_from_state(session: AsyncSession, state: ConversationState, phone: str) -> None:
    if not all([state.ticket_id, state.first_name, state.last_name, state.dni, state.member_id, state.procedure, state.details]):
        return

    event_dt = state.completed_at or datetime.now(timezone.utc)
    case = UserCase(
        ticket_id=state.ticket_id,
        phone_encrypted=encrypt_value(phone),
        phone_hash=hash_value(phone),
        first_name_encrypted=encrypt_value(state.first_name),
        last_name_encrypted=encrypt_value(state.last_name),
        dni_encrypted=encrypt_value(state.dni),
        dni_hash=hash_value(state.dni),
        member_id_encrypted=encrypt_value(state.member_id),
        procedure=state.procedure,
        details_encrypted=encrypt_value(state.details),
        event_day=event_dt.day,
        event_month=event_dt.month,
        event_year=event_dt.year,
        event_hour=event_dt.hour,
    )
    session.add(case)
    await session.commit()


async def log_access(
    session: AsyncSession,
    *,
    actor_id: str,
    action: str,
    reason: str,
    ip_address: str,
    user_agent: str,
    device_id: str,
    outcome: str,
    role: str = "authorized_staff",
) -> None:
    row = AccessAuditLog(
        actor_id=actor_id,
        role=role,
        action=action,
        reason=reason,
        ip_address=ip_address,
        user_agent=user_agent,
        device_id=device_id,
        outcome=outcome,
    )
    session.add(row)
    await session.commit()


async def get_case_by_ticket(session: AsyncSession, ticket_id: str) -> dict[str, str] | None:
    stmt: Select[tuple[UserCase]] = select(UserCase).where(UserCase.ticket_id == ticket_id)
    row = (await session.execute(stmt)).scalar_one_or_none()
    if not row:
        return None

    return {
        "ticket_id": row.ticket_id,
        "phone": decrypt_value(row.phone_encrypted),
        "first_name": decrypt_value(row.first_name_encrypted),
        "last_name": decrypt_value(row.last_name_encrypted),
        "dni": decrypt_value(row.dni_encrypted),
        "member_id": decrypt_value(row.member_id_encrypted),
        "procedure": row.procedure,
        "details": decrypt_value(row.details_encrypted),
        "day": str(row.event_day),
        "month": str(row.event_month),
        "year": str(row.event_year),
        "hour": str(row.event_hour),
    }


async def security_review(session: AsyncSession) -> dict[str, object]:
    last_logs = (
        await session.execute(
            select(AccessAuditLog).order_by(desc(AccessAuditLog.timestamp)).limit(100)
        )
    ).scalars().all()

    suspicious: list[dict[str, str]] = []
    known_device_per_actor: dict[str, set[str]] = {}

    for log in reversed(last_logs):
        known = known_device_per_actor.setdefault(log.actor_id, set())
        if known and log.device_id not in known:
            suspicious.append(
                {
                    "type": "new_device",
                    "actor_id": log.actor_id,
                    "device_id": log.device_id,
                    "timestamp": str(log.timestamp),
                }
            )
        known.add(log.device_id)

        if log.timestamp and (log.timestamp.hour < 7 or log.timestamp.hour > 20):
            suspicious.append(
                {
                    "type": "out_of_hours_access",
                    "actor_id": log.actor_id,
                    "timestamp": str(log.timestamp),
                }
            )

    failed_count = (
        await session.execute(
            select(func.count(AccessAuditLog.id)).where(AccessAuditLog.outcome == "denied")
        )
    ).scalar_one()

    return {
        "total_logs_analyzed": len(last_logs),
        "failed_access_total": failed_count,
        "suspicious_events": suspicious,
    }
