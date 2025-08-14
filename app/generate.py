# app/generate.py
from datetime import datetime

def synthetic_items(fields, max_items):
    # Genera filas sintéticas con las columnas pedidas
    items = []
    for i in range(max_items):
        row = {}
        for col in fields:
            if col == "id":
                row[col] = i + 1
            elif col == "date_display":
                row[col] = datetime.utcnow().date().isoformat()
            else:
                row[col] = f"{col}-{i+1}"
        items.append(row)
    return items

def render_html_placeholder(report_name, search, fields, items, generated_at, max_items):
    # Plantilla inline simple (mañana cambiamos a cargar templates/report.html)
    header = f"<h1>{report_name}</h1><div>generated_at={generated_at} | search='{search}' | max_items={max_items}</div>"
    table_head = "<tr>" + "".join(f"<th>{c}</th>" for c in fields) + "</tr>"
    table_rows = ""
    for it in items:
        table_rows += "<tr>" + "".join(f"<td>{it.get(c,'')}</td>" for c in fields) + "</tr>"
    table = f"<table border='1'>{table_head}{table_rows}</table>"
    return f"<!doctype html><html><body>{header}{table}</body></html>"
