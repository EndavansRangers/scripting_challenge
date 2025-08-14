
import argparse
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader, select_autoescape
from .script import load_config, fetch_artworks
from .pdf import html_to_pdf
from .emailer import send_email


from .script import load_config, fetch_artworks

def render_html(template_dir: str, template_name: str, context: Dict[str, Any]) -> str:
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(enabled_extensions=("html",))
    )
    tpl = env.get_template(template_name)
    return tpl.render(**context)

def run_reports(config_path: str, out_dir: str, dry_run: bool, strict: bool) -> int:
    print(f"[cli] config={config_path} | out={out_dir} | dry_run={dry_run} | strict={strict}")
    os.makedirs(out_dir, exist_ok=True)

    try:
        cfg = load_config(config_path)
    except Exception as e:
        print(f"[error] Cargando YAML: {e}", file=sys.stderr)
        return 1

    reports: List[Dict[str, Any]] = cfg.get("reports", [])
    if not reports:
        print("[warn] No hay reports en el YAML", file=sys.stderr)
        return 0

    summary = []
    error_count = 0

    for r in reports:
        # Validación mínima
        for k in ("name", "search", "fields", "max_items"):
            if k not in r:
                print(f"[warn] Reporte inválido, falta '{k}': {r}", file=sys.stderr)
                error_count += 1
                break
        else:
            name: str = r["name"]
            search: str = r["search"]
            fields: List[str] = r["fields"]
            max_items: int = int(r["max_items"])
            recipients: List[str] = r.get("recipients", []) or []

            print(f"[cli] fetching: name={name} q='{search}' fields={fields} max_items={max_items}")
            try:
                items = fetch_artworks(search=search, fields=fields, max_items=max_items)
            except Exception as e:
                print(f"[error] Reporte '{name}': {e}", file=sys.stderr)
                error_count += 1
                continue

            # JSON real
            json_path = os.path.join(out_dir, f"{name}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
            print(f"[cli] wrote {json_path}")

            # HTML real (Jinja2)
            env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape(("html",)))
            tpl = env.get_template("report.html")
            context = {
                "report_name": name,
                "search": search,
                "fields": fields,
                "items": items,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "max_items": max_items,
            }
            html = tpl.render(**context)
            html_path = os.path.join(out_dir, f"{name}.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"[cli] wrote {html_path}")

            # PDF real (Playwright)
            pdf_path = os.path.join(out_dir, f"{name}.pdf")
            try:
                html_to_pdf(html=html, pdf_path=pdf_path, base_dir="templates")
                print(f"[cli] wrote {pdf_path} (via Chromium)")
            except Exception as e:
                with open(pdf_path, "wb") as f:
                    f.write(b"%PDF-1.4\n% fallback placeholder\n%%EOF\n")
                print(f"[cli][warn] PDF renderer failed, wrote placeholder instead: {e}")

            summary.append({"report": name, "count": len(items)})

            # === ENVÍO DE EMAIL (solo si NO es dry-run) ===
            if not dry_run:
                try:
                    subject = f"[Reports] {name} — {len(items)} items"
                    body = (
                        f"Reporte: {name}\n"
                        f"Query: '{search}'\n"
                        f"Items: {len(items)}\n"
                        f"Generado: {context['generated_at']}\n\n"
                        f"Se adjuntan PDF, HTML y JSON.\n"
                    )
                    attachments = [
                        (f"{name}.pdf", pdf_path),
                        (f"{name}.html", html_path),
                        (f"{name}.json", json_path),
                    ]
                    send_email(subject=subject, body=body, to=recipients, attachments=attachments)
                    print(f"[cli] email sent to: {', '.join(recipients) if recipients else '(sin destinatarios)'}")
                except Exception as e:
                    print(f"[error] Email '{name}': {e}", file=sys.stderr)
                    error_count += 1

    # Resumen global para el Job Summary
    summary_path = os.path.join(out_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"[cli] wrote {summary_path}")

    # Política de salida:
    # - preview (dry-run): no falles el build salvo errores “duros” (carga YAML).
    # - nightly strict: si strict=True y hubo errores de reportes, sal con código != 0
    if strict and error_count > 0:
        print(f"[cli] strict mode: {error_count} errores (consulta/render/email)", file=sys.stderr)
        return 2

    return 0

def main():
    p = argparse.ArgumentParser(description="Reports-as-code CLI (API real + HTML con Jinja2)")
    # Soporta: python -m app --config ... --out ... [--dry-run] [--strict]
    #          python -m app run --config ... --out ... [--dry-run] [--strict]
    sub = p.add_subparsers(dest="cmd")

    # flags comunes
    p.add_argument("--config", default="config/queries.yml", help="Ruta a config/queries.yml")
    p.add_argument("--out", default="out", help="Directorio de salida")
    p.add_argument("--dry-run", action="store_true", help="No envía correos; solo genera artefactos")
    p.add_argument("--strict", action="store_true", help="Falla si algún reporte falla (recomendado en nightly)")

    run_p = sub.add_parser("run", help="Ejecuta los reportes")
    run_p.add_argument("--config", default="config/queries.yml")
    run_p.add_argument("--out", default="out")
    run_p.add_argument("--dry-run", action="store_true")
    run_p.add_argument("--strict", action="store_true")

    args = p.parse_args()

    # Normaliza según si vino por raíz o subcomando
    cfg = getattr(args, "config", "config/queries.yml")
    out_dir = getattr(args, "out", "out")
    dry = getattr(args, "dry_run", False)
    strict = getattr(args, "strict", False)

    code = run_reports(cfg, out_dir, dry, strict)
    sys.exit(code)

if __name__ == "__main__":
    main()
