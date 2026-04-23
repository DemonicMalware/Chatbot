# Chatbot de WhatsApp para IOMA (Área Personal)

Proyecto base de **chatbot completo** para atención por WhatsApp usando la API oficial de Meta (WhatsApp Cloud API).

Permite:
- conectar un número de WhatsApp Business,
- recibir mensajes de afiliadxs,
- pedir datos clave (nombre, DNI, nro de afiliado),
- clasificar el trámite,
- generar un número de gestión y dejar la conversación lista para seguimiento humano.

> ⚠️ Este proyecto es una base técnica. Para producción en un organismo público, se recomienda agregar autenticación de operadores, persistencia en base de datos, auditoría, y cumplimiento legal de protección de datos personales.

## Flujo conversacional incluido

1. Saludo inicial.
2. Nombre y apellido.
3. DNI.
4. Número de afiliado/a.
5. Tipo de trámite:
   - Consulta de cobertura
   - Autorización de práctica
   - Alta/actualización de datos
   - Estado de trámite
   - Otro
6. Detalle del caso.
7. Emisión de ticket automático (`IOMA-XXXXXXXX`).

## Requisitos

- Python 3.11+
- App de Meta Developers con WhatsApp Cloud API habilitada
- Número de teléfono configurado en WhatsApp Business Platform
- URL pública HTTPS para webhook (por ejemplo con ngrok, Cloudflare Tunnel, o despliegue en servidor)

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
```

Editar `.env` con tus credenciales reales.

## Variables de entorno

- `VERIFY_TOKEN`: token que usará Meta para verificar el webhook.
- `WHATSAPP_ACCESS_TOKEN`: token de acceso permanente o de larga duración.
- `WHATSAPP_PHONE_NUMBER_ID`: ID del número de WhatsApp en Meta.
- `GRAPH_API_VERSION`: versión de Graph API (por defecto `v22.0`).

## Ejecución local

```bash
uvicorn app.main:app --reload --port 8000
```

Endpoints:
- `GET /health`
- `GET /webhook` (verificación Meta)
- `POST /webhook` (recepción de mensajes)

## Configurar webhook en Meta

En tu app de Meta, en WhatsApp > Configuration:

- **Callback URL**: `https://TU_DOMINIO/webhook`
- **Verify token**: el mismo valor que `VERIFY_TOKEN`

Suscribí al menos el evento `messages`.

## Pruebas

```bash
pytest
```

## Próximos pasos recomendados para IOMA

1. Persistir chats y tickets en PostgreSQL.
2. Integrar con sistema interno de gestión de trámites.
3. Añadir panel para operadores (tomar conversación, responder, cerrar caso).
4. Implementar consentimiento de uso de datos personales antes de capturar DNI.
5. Configurar métricas (tiempo de primera respuesta, casos por tipo, SLA).

## Corregir alertas de Pylance (`reportMissingImports`)

Si VS Code marca `fastapi` o `fastapi.responses` como no resueltos:

1. Crear y activar el entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. En VS Code, seleccionar el intérprete `.venv` (Command Palette → `Python: Select Interpreter`).

Este repo incluye `pyrightconfig.json` apuntando a `.venv`, por lo que esas dos alertas desaparecen al usar ese entorno.
