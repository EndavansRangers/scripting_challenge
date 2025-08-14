# PR Preview - Definición Funcional

## Triggers
- `pull_request` (cambios en `config/queries.yml`).
- `workflow_dispatch` (ejecución manual para pruebas).

## Pasos del job
1) Checkout del repo → set up toolchain → instalar dependencias.
2) Ejecutar el CLI con `--dry-run` (genera solo artefactos; **no envía emails**). 
3) Subir `out/**` (PDF, JSON, logs) como artefacto **reports**. 
4) (Opcional recomendado) Publicar **resumen** con: ítems por reporte, tamaños, warnings. 


## Retención de artefactos
Definir entre **14–30 días** en Actions. 
