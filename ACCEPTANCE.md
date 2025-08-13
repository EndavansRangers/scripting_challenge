# Criterios de Aceptación

- PRs que modifiquen `config/queries.yml` → producen artefactos PDF/JSON y resumen del run. 
- El job programado/manual envía emails; fallos → **exit code ≠ 0** y logs claros. 
- Artefactos retenidos 14–30 días; outputs reproducibles por commit. 
- Considerar backoff y límite de tiempo global (`MAX_RUNTIME`). 
- Seguridad: sin impresión de secretos, secretos en Actions, least privilege. 
- Observabilidad: logs estructurados, job summary, mensajes de fallo claros. 
