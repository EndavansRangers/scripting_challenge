# scripting_challenge
# Reports-as-Code (GitHub Actions)

## Objetivo
Convertir la generación de reportes en un flujo versionado y revisable (“reports-as-code”).
- Cada PR que cambie `config/queries.yml` ejecuta un **preview** y adjunta **PDF/JSON** como artefactos (sin emails).
- Un **job nocturno** (y **manual**) ejecuta el build real y **envía emails**. Todos los outputs se retienen como artefactos. 

## Estructura
- `config/queries.yml`: definiciones editables por negocio.
- `templates/report.html`: plantilla HTML renderizada a PDF.
- `app/`: CLI de reportes con soporte `--dry-run`.
- `requirements.txt`: versiones fijadas; opcional `Dockerfile` para reproducibilidad. :contentReference[oaicite:9]{index=9}
