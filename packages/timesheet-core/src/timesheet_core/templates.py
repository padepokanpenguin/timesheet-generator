"""Penyimpanan template (JSON di folder). Hanya admin yang boleh mengubah (TODO: peran)."""

from __future__ import annotations

from pathlib import Path

from timesheet_core.schemas import TemplateSpec

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


def list_templates() -> list[TemplateSpec]:
    return [
        TemplateSpec.model_validate_json(p.read_text(encoding="utf-8"))
        for p in sorted(TEMPLATE_DIR.glob("*.json"))
    ]


def get_template(template_id: str) -> TemplateSpec:
    for t in list_templates():
        if t.id == template_id:
            return t
    raise KeyError(template_id)


def save_template(template: TemplateSpec) -> TemplateSpec:
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    target = TEMPLATE_DIR / f"{template.id}.json"
    target.write_text(template.model_dump_json(indent=2), encoding="utf-8")
    return template


def delete_template(template_id: str) -> None:
    target = TEMPLATE_DIR / f"{template_id}.json"
    if not target.exists():
        raise KeyError(template_id)
    target.unlink()
