"""Render timesheet ke .xlsx dengan layout identik file referensi (Bagian 5 PRD)."""

from __future__ import annotations

import io
import math
from datetime import time
from pathlib import Path

from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from PIL import Image as PILImage

from timesheet_core import i18n
from timesheet_core.preview import default_working_hours
from timesheet_core.schemas import DayRow, TemplateSpec, TimesheetDraft

FONT = "Arial"
RED = "FFFF0000"
BLACK = "FF000000"
THIN = Side(style="thin")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT_WRAP = Alignment(horizontal="left", vertical="center", wrap_text=True)

COL_WIDTHS = {"A": 6.86, "B": 13.71, "C": 12.0, "D": 14.43, "E": 14.0, "F": 95.0}
HEADER_ROW_INFO = 11
HEADER_ROW_TABLE = 14
FIRST_DATA_ROW = 15
SIGNATURE_MAX_PX = (160, 70)
ASSETS_DIR = Path(__file__).resolve().parent / "templates" / "assets"


def _t(value: str) -> time:
    h, m = value.split(":")
    return time(int(h), int(m))


def info_text(row: DayRow) -> str:
    """`[Label] KEY: Judul (xx%) - aktivitas`, tiap task ke-2 dst. dipisah baris baru (\n)."""
    blocks: list[str] = []
    for s in row.stories:
        head = f"{s.key}: {s.title}"
        if s.epic:
            head = f"[{s.epic}] {head}"
        if s.percent is not None:
            head += f" ({s.percent}%)"
        blocks.append(head + "".join(f" - {a}" for a in s.activities))
    if row.free_text:
        blocks.append(row.free_text)
    return "\n".join(blocks)


def _style(cell, *, bold=False, color=None, fill=None, align=CENTER, border=True):
    cell.font = Font(name=FONT, size=11, bold=bold, color=color)
    cell.alignment = align
    if fill:
        cell.fill = PatternFill("solid", fgColor=fill)
    if border:
        cell.border = BORDER


def _add_signature(ws, path: Path | None, anchor: str) -> None:
    if not path or not path.exists():
        return
    with PILImage.open(path) as im:
        w, h = im.size
    scale = min(SIGNATURE_MAX_PX[0] / w, SIGNATURE_MAX_PX[1] / h, 1)
    img = XLImage(str(path))
    img.width, img.height = int(w * scale), int(h * scale)
    ws.add_image(img, anchor)


def render_timesheet(
    draft: TimesheetDraft,
    template: TemplateSpec,
    *,
    employee_signature: Path | None = None,
    team_lead_signature: Path | None = None,
) -> bytes:
    lang = template.language
    wb = Workbook()
    ws = wb.active
    ws.title = i18n.month_name(lang, draft.month)
    ws.sheet_view.showGridLines = True
    for col, width in COL_WIDTHS.items():
        ws.column_dimensions[col].width = width

    # Baris 1-7: area logo template referensi (kolom B:D)
    company_logo_name = template.company_logo or (
        "pasti_logo.png" if "PASTI" in template.company_name.upper() else None
    )
    if company_logo_name:
        logo_path = ASSETS_DIR / company_logo_name
        if logo_path.exists():
            img0 = XLImage(str(logo_path))
            img0.width, img0.height = 138, 135
            ws.add_image(img0, "B1")

    client_logo_name = template.client_logo or (
        "siloam_logo.png" if "SILOAM" in template.client.upper() else None
    )
    if client_logo_name:
        client_logo_path = ASSETS_DIR / client_logo_name
        if client_logo_path.exists():
            img1 = XLImage(str(client_logo_path))
            img1.width, img1.height = 465, 126
            ws.add_image(img1, "D1")

    ws["A9"] = template.company_name
    ws["A9"].font = Font(name=FONT, size=12, bold=True)
    # Header info (baris 11-12)
    ws.merge_cells("A11:B11")
    ws.merge_cells("A12:B12")
    last_day = max(r.date for r in draft.rows) if draft.rows else None
    month_label = i18n.month_name(lang, draft.month)
    period = f"1 {month_label} {draft.year} - {(last_day.day if last_day else 31)} {month_label} {draft.year}"
    headers = {
        "A11": "Title",
        "C11": "Name",
        "D11": "Company",
        "E11": "Dept",
        "F11": i18n.label(lang, "period"),
    }
    values = {
        "A12": template.title,
        "C12": template.employee_name,
        "D12": template.client,
        "E12": template.department,
        "F12": period,
    }
    for col in "ABCDEF":
        _style(ws[f"{col}11"], bold=True, color="FFFFFFFF", fill=BLACK)
        _style(ws[f"{col}12"])
    for ref, text in headers.items():
        ws[ref] = text
    for ref, text in values.items():
        ws[ref] = text

    # Header tabel (baris 14)
    for i, name in enumerate(
        ["Id", "Date", "Time In", "Time Out", "Working Hour", "Information Activity"], start=1
    ):
        cell = ws.cell(HEADER_ROW_TABLE, i, name)
        _style(cell, bold=True, color="FFFFFFFF", fill=BLACK)

    # Baris data
    r = FIRST_DATA_ROW
    for idx, row in enumerate(draft.rows, start=1):
        for col in range(1, 7):
            _style(ws.cell(r, col), align=LEFT_WRAP if col == 6 else CENTER)
        ws.cell(r, 1, idx)
        ws.cell(r, 2, row.date).number_format = "d mmm yyyy"

        if row.kind == "leave":
            ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=6)
            ws.cell(r, 3, i18n.label(lang, "leave"))
            _style(ws.cell(r, 3), bold=True, color="FFFFFFFF", fill=RED)
        elif row.kind in ("weekend", "holiday"):
            for col in range(3, 7):
                _style(
                    ws.cell(r, col),
                    bold=True,
                    color="FFFFFFFF",
                    fill=RED,
                    align=LEFT_WRAP if col == 6 else CENTER,
                )
        else:
            if row.time_in and row.time_out:
                ws.cell(r, 3, _t(row.time_in)).number_format = "hh:mm"
                ws.cell(r, 4, _t(row.time_out)).number_format = "hh:mm"
                hours = row.working_hours
                if hours is None:
                    hours = default_working_hours(row.time_in, row.time_out, template.break_minutes)
                # Ditulis sebagai angka (bukan rumus): openpyxl tidak menghitung nilai rumus.
                ws.cell(r, 5, hours).number_format = "0.##"
            text = info_text(row)
            ws.cell(r, 6, text)
            line_count = sum(max(1, math.ceil(len(line) / 95)) for line in text.split("\n")) if text else 1
            ws.row_dimensions[r].height = max(18, 15 * line_count)
        r += 1

    # Footer: tanda tangan
    last_row = r - 1
    label_row = last_row + 2
    ws.cell(label_row, 2, i18n.label(lang, "employee"))
    ws.cell(label_row, 6, i18n.label(lang, "team_lead"))
    for col in (2, 6):
        ws.cell(label_row, col).font = Font(name=FONT, size=11, bold=True)
        ws.cell(label_row, col).alignment = Alignment(horizontal="center" if col == 2 else "left")
    sig_row = label_row + 1
    for rr in range(sig_row, sig_row + 4):
        ws.row_dimensions[rr].height = 20
    _add_signature(ws, employee_signature, f"B{sig_row}")
    _add_signature(ws, team_lead_signature, f"F{sig_row}")
    name_row = sig_row + 4
    ws.cell(name_row, 2, template.employee_name).font = Font(name=FONT, size=11)
    ws.cell(name_row, 6, template.team_lead_name).font = Font(name=FONT, size=11)
    ws.cell(name_row, 6).alignment = Alignment(horizontal="left")

    ws.freeze_panes = f"A{FIRST_DATA_ROW}"
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def file_name(template: TemplateSpec, year: int) -> str:
    safe = template.employee_name.strip().replace(" ", "_")
    return template.file_name_pattern.format(name=safe, year=year)
