from __future__ import annotations

from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserCase(Base):
    __tablename__ = "user_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)

    phone_encrypted: Mapped[str] = mapped_column(Text)
    phone_hash: Mapped[str] = mapped_column(String(120), index=True)

    first_name_encrypted: Mapped[str] = mapped_column(Text)
    last_name_encrypted: Mapped[str] = mapped_column(Text)
    dni_encrypted: Mapped[str] = mapped_column(Text)
    dni_hash: Mapped[str] = mapped_column(String(120), index=True)
    member_id_encrypted: Mapped[str] = mapped_column(Text)

    procedure: Mapped[str] = mapped_column(String(120))
    details_encrypted: Mapped[str] = mapped_column(Text)

    event_day: Mapped[int] = mapped_column(Integer)
    event_month: Mapped[int] = mapped_column(Integer)
    event_year: Mapped[int] = mapped_column(Integer)
    event_hour: Mapped[int] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AccessAuditLog(Base):
    __tablename__ = "access_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    actor_id: Mapped[str] = mapped_column(String(100), index=True)
    role: Mapped[str] = mapped_column(String(60), default="authorized_staff")
    action: Mapped[str] = mapped_column(String(120))
    reason: Mapped[str] = mapped_column(String(255))

    ip_address: Mapped[str] = mapped_column(String(60))
    user_agent: Mapped[str] = mapped_column(String(255))
    device_id: Mapped[str] = mapped_column(String(120))
    outcome: Mapped[str] = mapped_column(String(30), index=True)
