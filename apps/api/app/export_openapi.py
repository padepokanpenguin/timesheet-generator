"""Cetak skema OpenAPI ke stdout: `uv run python -m app.export_openapi > openapi.json`."""

import json

from app.main import app

print(json.dumps(app.openapi(), indent=2, ensure_ascii=False))
