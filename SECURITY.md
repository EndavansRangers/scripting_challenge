# Security & Secrets

## Secretos requeridos (para el job real del Día 2)
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `FROM_EMAIL`.
Almacenados en **Actions secrets** o **Environment secrets**. **Nunca** imprimir en logs. 

## Opcional (recomendado)
- **OIDC + secret manager** (cloud) para evitar credenciales de larga vida. :contentReference[oaicite:19]{index=19}

## Parámetros no sensibles
- Definir vía `env`/inputs: `MAX_RUNTIME`, `RATE_LIMIT`, `API_BASE`. 
