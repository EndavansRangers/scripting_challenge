# app/pdf.py
from pathlib import Path
from typing import Optional
from playwright.sync_api import sync_playwright

def html_to_pdf(html: str, pdf_path: str, base_dir: Optional[str] = None) -> None:
    """
    Renderiza HTML a PDF con Chromium (Playwright).
    - html: HTML completo (<!doctype html>...).
    - pdf_path: ruta de salida .pdf
    - base_dir: carpeta base para resolver rutas relativas (css/img).
    """
    pdf_file = Path(pdf_path)
    pdf_file.parent.mkdir(parents=True, exist_ok=True)

    # Si se especifica base_dir, lo convertimos a file://... para usarlo como base_url del contexto
    base_url = None
    if base_dir:
        base_url = Path(base_dir).resolve().as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        # IMPORTANTE: base_url va en el CONTEXTO, no en set_content
        if base_url:
            context = browser.new_context(base_url=base_url)
        else:
            context = browser.new_context()

        page = context.new_page()
        page.set_content(html, wait_until="load")

        page.pdf(
            path=str(pdf_file),
            format="A4",
            print_background=True,
            margin={"top": "12mm", "right": "12mm", "bottom": "12mm", "left": "12mm"},
            display_header_footer=False,
        )

        context.close()
        browser.close()
