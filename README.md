# Chatbot de WhatsApp para IOMA (Área Personal) con base segura

Backend de chatbot por WhatsApp (Meta Cloud API) con **persistencia cifrada de datos sensibles**, **control de acceso para personal autorizado** y **auditoría de accesos**.

## Qué guarda el sistema

Cuando se completa un trámite, se persiste en una base aislada:
- nombre,
- apellido,
- DNI,
- número de afiliado,
- número de trámite (`ticket_id`),
- día/mes/año/hora del evento,
- detalle y tipo de gestión.

## Controles de seguridad implementados

1. **Cifrado de datos sensibles en reposo** (`cryptography/Fernet`).
2. **Hash de campos críticos** (DNI/teléfono) para correlación sin exponer texto plano.
3. **Base de datos separada del estado en memoria** (SQLAlchemy + URL dedicada).
4. **Control de acceso por API key para endpoints administrativos**.
5. **Motivo de acceso obligatorio** (`reason`) para consultar casos.
6. **Auditoría de accesos**: actor, dispositivo, IP, horario, acción, resultado.
7. **Revisión de seguridad** de eventos sospechosos (accesos fuera de horario y cambio de dispositivo).

> Importante: esto es una base técnica robusta. No equivale por sí sola a certificación ISO. Para cumplimiento formal se requiere proceso organizacional, auditorías y controles documentados.

## Arquitectura

- `POST /webhook`: recibe mensajes de WhatsApp y avanza flujo.
- `GET /webhook`: verificación de Meta.
- `GET /admin/cases/{ticket_id}`: consulta de expediente (solo personal autorizado).
- `GET /admin/security/review`: revisión de seguridad y accesos sospechosos.

## Requisitos

- Python 3.11+
- WhatsApp Cloud API (Meta)
- URL pública HTTPS para webhook

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Variables de entorno

- `VERIFY_TOKEN`
- `WHATSAPP_ACCESS_TOKEN`
- `WHATSAPP_PHONE_NUMBER_ID`
- `GRAPH_API_VERSION`
- `DATABASE_URL` (recomendado PostgreSQL aislado en producción)
- `ENCRYPTION_KEY` (Fernet, idealmente desde KMS/HSM)
- `ADMIN_API_KEYS` (`actor:key,actor2:key2`)

## Ejecución

```bash
uvicorn app.main:app --reload --port 8000
```

## Seguridad de acceso administrativo

Ejemplo para consultar un trámite:

```bash
curl "http://localhost:8000/admin/cases/IOMA-12345678?reason=auditoria%20de%20tramite" \
  -H "X-API-Key: cambiar-api-key-segura" \
  -H "X-Device-ID: equipo-rh-01"
```

Cada acceso queda auditado con usuario, dispositivo, IP, horario y resultado.

## Lineamientos ISO (orientativos)

Esta base ayuda a alinear controles técnicos de:
- **ISO/IEC 27001** (control de acceso, gestión de registros, criptografía),
- **ISO/IEC 27701** (privacidad sobre datos personales),
- **ISO 27002** (buenas prácticas operativas).

Para cumplimiento real: definir políticas, segregación de funciones, recertificación de accesos, gestión de incidentes y auditoría externa.

## Pruebas

```bash
pytest
```
