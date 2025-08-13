# PR Preview - Definición Funcional

## Triggers
- `pull_request` (cambios en `config/queries.yml`).
- `workflow_dispatch` (ejecución manual para pruebas). :contentReference[oaicite:11]{index=11}

## Pasos del job
1) Checkout del repo → set up toolchain → instalar dependencias. :contentReference[oaicite:12]{index=12}
2) Ejecutar el CLI con `--dry-run` (genera solo artefactos; **no envía emails**). :contentReference[oaicite:13]{index=13}
3) Subir `out/**` (PDF, JSON, logs) como artefacto **reports**. :contentReference[oaicite:14]{index=14}
4) (Opcional recomendado) Publicar **resumen** con: ítems por reporte, tamaños, warnings. :contentReference[oaicite:15]{index=15}

## Retención de artefactos
Definir entre **14–30 días** en Actions. 
