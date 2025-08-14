#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import time
from typing import Any, Dict, List
import requests
import yaml

AIC_BASE = "https://api.artic.edu/api/v1"
SEARCH_ENDPOINT = f"{AIC_BASE}/artworks/search"


def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    if "reports" not in cfg or not isinstance(cfg["reports"], list):
        raise ValueError("El YAML debe contener 'reports: [...]'")
    return cfg


def fetch_artworks(search: str, fields: List[str], max_items: int,
                   timeout: int = 30, max_retries: int = 3) -> List[Dict[str, Any]]:
    """
    Llama a /artworks/search paginando hasta reunir 'max_items'.
    Devuelve solo los campos solicitados (faltantes -> None).
    """
    collected: List[Dict[str, Any]] = []
    page = 1

    while len(collected) < max_items:
        remaining = max_items - len(collected)
        limit = min(remaining, 100)  # la API soporta hasta 100

        params = {
            "q": search,
            "fields": ",".join(fields),
            "limit": limit,
            "page": page,
        }

        attempt = 0
        while True:
            try:
                r = requests.get(SEARCH_ENDPOINT, params=params, timeout=timeout)
                r.raise_for_status()
                payload = r.json()
                break
            except requests.RequestException as e:
                attempt += 1
                if attempt > max_retries:
                    raise RuntimeError(f"Error consultando AIC: {e}") from e
                time.sleep(1.5 ** attempt)  # backoff suave

        data = payload.get("data", []) or []
        if not data:
            break  # no hay más resultados

        for it in data:
            collected.append({k: it.get(k) for k in fields})
            if len(collected) >= max_items:
                break

        if len(data) < limit:
            break  # se agotaron los resultados

        page += 1

    return collected


def print_report(name: str, search: str, fields: List[str], items: List[Dict[str, Any]]) -> None:
    print(f"\n=== Reporte: {name} | q='{search}' | items={len(items)} ===")
    # Imprime filas con los fields en orden
    header = " | ".join(fields)
    print(header)
    print("-" * len(header))
    for it in items:
        row = " | ".join(str(it.get(f, "")) if it.get(f) is not None else "" for f in fields)
        print(row)


def main() -> int:
    p = argparse.ArgumentParser(description="Lee config/queries.yml, consulta la API AIC y muestra resultados en terminal")
    p.add_argument("--config", default="config/queries.yml", help="Ruta a config/queries.yml")
    args = p.parse_args()

    try:
        cfg = load_config(args.config)
    except Exception as e:
        print(f"[error] Cargando YAML: {e}", file=sys.stderr)
        return 1

    reports: List[Dict[str, Any]] = cfg["reports"]

    for r in reports:
        # Validaciones mínimas
        for k in ("name", "search", "fields", "max_items"):
            if k not in r:
                print(f"[warn] Reporte inválido, falta '{k}': {r}", file=sys.stderr)
                continue

        name = r["name"]
        search = r["search"]
        fields = r["fields"]
        max_items = r["max_items"]

        try:
            items = fetch_artworks(search=search, fields=fields, max_items=max_items)
            print_report(name=name, search=search, fields=fields, items=items)
        except Exception as e:
            print(f"[error] Reporte '{name}': {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
