# Runbook

## Local (hoy en modo documentación)
- Crear virtualenv e instalar `requirements.txt`.
- Ejecutar: `python -m app run --config config/queries.yml --out out --dry-run`.
- Verifica `out/` para PDFs/JSON (cuando el CLI esté implementado mañana). 

## Variables para ejecución real (Día 2)
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `FROM_EMAIL`.

## Troubleshooting (borrador)
- API/rate limit → backoff y ajustar `max_items`.
- PDF renderer y fuentes instaladas.
- SMTP: credenciales/puertos TLS/SSL y políticas del remitente. 
