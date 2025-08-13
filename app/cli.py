# app/cli.py
import argparse
import json
import os
from datetime import datetime
from .generate import synthetic_items, render_html_placeholder

def main():
    p = argparse.ArgumentParser(description="Reports-as-code CLI (stub)")
    p.add_argument("--config", required=True, help="Path to config/queries.yml")
    p.add_argument("--out", required=True, help="Output directory")
    p.add_argument("--dry-run", action="store_true", help="Do not send emails; produce artifacts only")
    args = p.parse_args()

    # En el stub, no parseamos YAML real: usamos una lista fija equivalente al config de ejemplo.
    # Mañana: cargar y validar YAML.
    reports = [
        {
            "name": "war-art",
            "search": "war",
            "fields": ["id", "title", "artist_title", "date_display"],
            "max_items": 25,
        },
        {
            "name": "impressionism-sample",
            "search": "impressionism",
            "fields": ["id", "title", "artist_title", "date_display"],
            "max_items": 10,
        },
    ]

    os.makedirs(args.out, exist_ok=True)
    summary = []

    for r in reports:
        items = synthetic_items(r["fields"], r["max_items"])
        # JSON “raw”
        json_path = os.path.join(args.out, f"{r['name']}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

        # HTML placeholder (simula render de plantilla)
        html = render_html_placeholder(
            report_name=r["name"],
            search=r["search"],
            fields=r["fields"],
            items=items,
            generated_at=datetime.utcnow().isoformat() + "Z",
            max_items=r["max_items"],
        )
        html_path = os.path.join(args.out, f"{r['name']}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)

        # “PDF” placeholder: archivo .pdf mínimo para artefacto (se reemplazará por render real)
        pdf_path = os.path.join(args.out, f"{r['name']}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n% placeholder preview\n%%EOF\n")

        summary.append({"report": r["name"], "count": len(items)})

    # Guardar un pequeño resumen para el job summary
    with open(os.path.join(args.out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    if args.dry_run:
        print("[stub] Dry-run complete. Artifacts written to:", args.out)
