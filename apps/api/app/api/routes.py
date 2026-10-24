from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import Response
from jira_client import JiraClient, JiraError
from timesheet_core import excel_renderer
from timesheet_core.preview import build_draft
from timesheet_core.progress import ProgressError, split_progress, total_progress
from timesheet_core.sample_data import sample_month
from timesheet_core.schemas import (
    FormulaSimulateRequest,
    FormulaSimulateResponse,
    GenerateRequest,
    JiraConnectRequest,
    JiraStatus,
    PreviewRequest,
    SignatureStatus,
    TemplateSpec,
    TimesheetDraft,
)
from timesheet_core.templates import delete_template, get_template, list_templates, save_template

from app.config import Settings, get_settings

router = APIRouter(prefix="/api")

MAX_SIGNATURE_BYTES = 1_000_000
SIGNATURE_ROLES = {"employee", "team_lead"}


def _template(template_id: str) -> TemplateSpec:
    try:
        return get_template(template_id)
    except KeyError:
        raise HTTPException(404, f"Template '{template_id}' tidak ditemukan") from None


@router.get("/templates", response_model=list[TemplateSpec])
def templates() -> list[TemplateSpec]:
    return list_templates()


@router.get("/templates/{template_id}", response_model=TemplateSpec)
def get_single_template(template_id: str) -> TemplateSpec:
    return _template(template_id)


@router.post("/templates", response_model=TemplateSpec, status_code=201)
def create_template(template: TemplateSpec) -> TemplateSpec:
    return save_template(template)


@router.put("/templates/{template_id}", response_model=TemplateSpec)
def update_template(template_id: str, template: TemplateSpec) -> TemplateSpec:
    if template.id != template_id:
        raise HTTPException(400, "ID template pada URL dan isi tidak cocok")
    return save_template(template)


@router.delete("/templates/{template_id}", status_code=204)
def remove_template(template_id: str) -> None:
    try:
        delete_template(template_id)
    except KeyError:
        raise HTTPException(404, f"Template '{template_id}' tidak ditemukan") from None


@router.post("/timesheet/preview", response_model=TimesheetDraft)
async def preview(req: PreviewRequest, settings: Settings = Depends(get_settings)) -> TimesheetDraft:
    template = _template(req.template_id)
    if settings.jira_mock:
        data = sample_month(req.year, req.month)
    else:
        client = JiraClient(
            settings.jira_base_url,
            settings.jira_email,
            settings.jira_api_token,
            story_points_field=settings.jira_story_points_field,
            timezone=template.timezone,
            hours_per_manday=template.formula.hours_per_manday,
        )
        try:
            data = await client.fetch_month(req.year, req.month)
        except JiraError as exc:
            raise HTTPException(502, str(exc)) from exc
        finally:
            await client.aclose()
    try:
        return build_draft(
            year=req.year,
            month=req.month,
            template=template,
            data=data,
            leave_dates=set(req.leave_dates),
            manual_percent=req.manual_percent,
            story_state=req.story_state,
            reroll_seed=req.reroll_seed,
            show_all_days=req.show_all_days,
            non_ticket_entries=req.non_ticket_entries,
            manual_estimates=req.manual_estimates,
            manual_epics=req.manual_epics,
            custom_hours=req.custom_hours,
        )
    except ProgressError as exc:
        raise HTTPException(422, str(exc)) from exc


def _signature_path(settings: Settings, role: str) -> Path | None:
    for ext in ("png", "jpg"):
        p = settings.storage_dir / "signatures" / f"{role}.{ext}"
        if p.exists():
            return p
    return None


@router.post("/timesheet/generate")
def generate(req: GenerateRequest, settings: Settings = Depends(get_settings)) -> Response:
    template = _template(req.draft.template_id)
    content = excel_renderer.render_timesheet(
        req.draft,
        template,
        employee_signature=_signature_path(settings, "employee"),
        team_lead_signature=_signature_path(settings, "team_lead"),
    )
    name = excel_renderer.file_name(template, req.draft.year)
    return Response(
        content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )


@router.get("/signatures", response_model=SignatureStatus)
def signature_status(settings: Settings = Depends(get_settings)) -> SignatureStatus:
    return SignatureStatus(
        employee=_signature_path(settings, "employee") is not None,
        team_lead=_signature_path(settings, "team_lead") is not None,
    )


@router.delete("/signatures/{role}", status_code=204)
def delete_signature(role: str, settings: Settings = Depends(get_settings)) -> None:
    if role not in SIGNATURE_ROLES:
        raise HTTPException(404, "Role tidak dikenal")
    folder = settings.storage_dir / "signatures"
    deleted = False
    for old in folder.glob(f"{role}.*"):
        old.unlink()
        deleted = True
    if not deleted:
        raise HTTPException(404, f"Tanda tangan '{role}' tidak ditemukan")


@router.get("/jira/status", response_model=JiraStatus)
def jira_status(settings: Settings = Depends(get_settings)) -> JiraStatus:
    if settings.jira_mock:
        return JiraStatus(
            connected=True,
            site_url="mock://jira.local",
            email="developer@example.com",
            message="Menggunakan data simulasi Jira (Mock Mode)",
        )
    if settings.jira_base_url and settings.jira_email and settings.jira_api_token:
        return JiraStatus(
            connected=True,
            site_url=settings.jira_base_url,
            email=settings.jira_email,
            message="Terkoneksi ke Jira Cloud",
        )
    return JiraStatus(
        connected=False,
        message="Belum terhubung ke Jira Cloud. Silakan hubungkan token atau aktifkan mode mock.",
    )


@router.post("/jira/connect", response_model=JiraStatus)
async def jira_connect(req: JiraConnectRequest) -> JiraStatus:
    client = JiraClient(req.site_url, req.email, req.api_token)
    try:
        # Verifikasi kredensial Jira
        res = await client._client.get("/rest/api/3/myself")
        if res.status_code == 200:
            user_info = res.json()
            return JiraStatus(
                connected=True,
                site_url=req.site_url,
                email=user_info.get("emailAddress", req.email),
                message=f"Berhasil terhubung sebagai {user_info.get('displayName', req.email)}",
            )
        raise HTTPException(res.status_code, f"Koneksi Jira gagal ({res.status_code})")
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(400, f"Gagal menghubungi Jira: {exc}") from exc
    finally:
        await client.aclose()


@router.post("/formula/simulate", response_model=FormulaSimulateResponse)
def simulate_formula(req: FormulaSimulateRequest) -> FormulaSimulateResponse:
    tot = total_progress(
        done=req.done,
        prior_active_days=0,
        active_days=req.active_days,
        estimate=req.estimate_mandays,
        previous_percent=req.start_percent,
        cfg=req.formula,
    )
    if tot is None or req.active_days <= 0:
        return FormulaSimulateResponse(total_progress=tot, daily_percentages=[])
    splits = split_progress(
        start=req.start_percent,
        end=tot,
        days=req.active_days,
        cfg=req.formula,
        seed=req.seed,
    )
    return FormulaSimulateResponse(total_progress=tot, daily_percentages=splits)


@router.post("/signatures/{role}", status_code=204)
async def upload_signature(role: str, file: UploadFile, settings: Settings = Depends(get_settings)) -> None:
    """Employee diunggah karyawan; Team Lead diunggah Team Lead sendiri (TODO: cek peran)."""
    if role not in SIGNATURE_ROLES:
        raise HTTPException(404, "Role tidak dikenal")
    ext = {"image/png": "png", "image/jpeg": "jpg"}.get(file.content_type or "")
    if not ext:
        raise HTTPException(415, "Format harus PNG atau JPG")
    content = await file.read()
    if len(content) > MAX_SIGNATURE_BYTES:
        raise HTTPException(413, "Ukuran maksimum 1 MB")
    folder = settings.storage_dir / "signatures"
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob(f"{role}.*"):
        old.unlink()
    (folder / f"{role}.{ext}").write_bytes(content)


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "today": date.today().isoformat()}
