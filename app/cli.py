# app/cli.py
import argparse
import json
import os
import sys
from datetime import datetime
from .generate import synthetic_items, render_html_placeholder

def _do_run(config_path: str, out_dir: str, dry_run: bool) -> int:
    # Diagnóstico básico
    print(f"[cli] cwd={os.getcwd()}")
    print(f"[cli] config={config_path} | out={out_dir} | dry_run={dry_run}")

    # En el stub aún no leemos YAML real; usamos 2 reportes fijos.
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

    # Crear carpeta de salida
    os.makedirs(out_dir, exist_ok=True)

    summary = []
    for r in reports:
        items = synthetic_items(r["fields"], r["max_items"])

        # JSON “raw”
        json_path = os.path.join(out_dir, f"{r['name']}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        print(f"[cli] wrote {json_path}")

        # HTML placeholder (simula render con plantilla)
        html = render_html_placeholder(
            report_name=r["name"],
            search=r["search"],
            fields=r["fields"],
            items=items,
            generated_at=datetime.utcnow().isoformat() + "Z",
            max_items=r["max_items"],
        )
        html_path = os.path.join(out_dir, f"{r['name']}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[cli] wrote {html_path}")

        # “PDF” placeholder (mínimo para existir como artefacto)
        pdf_path = os.path.join(out_dir, f"{r['name']}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n% placeholder preview\n%%EOF\n")
        print(f"[cli] wrote {pdf_path}")

        summary.append({"report": r["name"], "count": len(items)})

    # Guardar pequeño resumen
    summary_path = os.path.join(out_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"[cli] wrote {summary_path}")

    if dry_run:
        print("[cli] Dry-run complete. Artifacts are ready.")
    return 0

def main():
    # Soporta:
    #   python -m app --config ... --out ... --dry-run
    #   python -m app run --config ... --out ... --dry-run
    parser = argparse.ArgumentParser(prog="app", description="Reports-as-code CLI (stub)")
    subparsers = parser.add_subparsers(dest="command")

    # Parser raíz (sin subcomando)
    parser.add_argument("--config", help="Path to config/queries.yml")
    parser.add_argument("--out", help="Output directory")
    parser.add_argument("--dry-run", action="store_true", help="Produce artifacts only (no emails)")

    # Subcomando 'run'
    run_p = subparsers.add_parser("run", help="Run reports")
    run_p.add_argument("--config", required=False, help="Path to config/queries.yml")
    run_p.add_argument("--out", required=False, help="Output directory")
    run_p.add_argument("--dry-run", action="store_true", help="Produce artifacts only (no emails)")

    args, unknown = parser.parse_known_args()
    if unknown:
        print(f"[cli][warn] unrecognized args: {unknown}", file=sys.stderr)

    # Normaliza parámetros si viene por raíz o por 'run'
    cmd = args.command or "root"
    cfg = getattr(args, "config", None)
    out_dir = getattr(args, "out", None)
    dry = getattr(args, "dry_run", False)

    # Defaults razonables si faltan (para que no falle silenciosamente)
    if not cfg:
        cfg = "config/queries.yml"
    if not out_dir:
        out_dir = "out"

    try:
        code = _do_run(cfg, out_dir, dry)
    except Exception as e:
        print(f"[cli][error] {e}", file=sys.stderr)
        code = 1
    sys.exit(code)
