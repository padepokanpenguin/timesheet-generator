import secrets
from datetime import date
from pathlib import Path
from typing import NamedTuple

from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile
from fastapi.responses import Response
from jira_client import JiraClient, JiraError
from timesheet_core import excel_renderer
from timesheet_core.preview import build_draft
from timesheet_core.progress import ProgressError, split_progress, total_progress
from timesheet_core.sample_data import sample_month
from timesheet_core.schemas import (
    AuthResponse,
    FormulaSimulateRequest,
    FormulaSimulateResponse,
    GenerateRequest,
    JiraConnectRequest,
    JiraStatus,
    LoginRequest,
    PreviewRequest,
    SignatureStatus,
    TemplateSpec,
    TimesheetDraft,
    UserAccountCreate,
    UserAccountUpdate,
    UserPublic,
)
from timesheet_core.templates import delete_template, get_template, list_templates, save_template

from app.config import Settings, get_settings
from app.users import (
    authenticate_user,
    create_user_account,
    delete_user_account,
    get_user_by_id,
    load_all_users,
    update_user_account,
)

router = APIRouter(prefix="/api")

MAX_SIGNATURE_BYTES = 1_000_000
SIGNATURE_ROLES = {"employee", "team_lead"}


class UserSession(NamedTuple):
    token: str
    user_id: str
    username: str
    email: str
    api_token: str
    site_url: str
    display_name: str
    role: str
    template_id: str
    account_id: str = ""

SESSIONS: dict[str, UserSession] = {}


def _extract_token(auth_header: str | None) -> str | None:
    if not auth_header:
        return None
    if auth_header.startswith("Bearer "):
        return auth_header[7:].strip()
    return auth_header.strip()


def get_current_user(
    authorization: str | None = Header(None, alias="Authorization"),
    settings: Settings = Depends(get_settings),
) -> UserSession | None:
    token = _extract_token(authorization)
    if token and token in SESSIONS:
        return SESSIONS[token]
    if settings.jira_base_url and settings.jira_email and settings.jira_api_token:
        return UserSession(
            token="default-env-token",
            user_id="aria.jamal",
            username="aria.jamal",
            email=settings.jira_email,
            api_token=settings.jira_api_token,
            site_url=settings.jira_base_url,
            display_name="Aria Nur Jamal",
            role="developer",
            template_id="default-id",
            account_id="default-user",
        )
    return None


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
async def preview(
    req: PreviewRequest,
    authorization: str | None = Header(None, alias="Authorization"),
    settings: Settings = Depends(get_settings),
) -> TimesheetDraft:
    template = _template(req.template_id)
    user = get_current_user(authorization, settings)

    if user and user.api_token and not settings.jira_mock:
        client = JiraClient(
            user.site_url,
            user.email,
            user.api_token,
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
    elif settings.jira_mock:
        data = sample_month(req.year, req.month)
    elif settings.jira_base_url and settings.jira_email and settings.jira_api_token:
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
    else:
        raise HTTPException(401, "Silakan hubungkan akun Jira Anda terlebih dahulu.")

    effective_template = template.model_copy()
    if user and user.display_name:
        effective_template.employee_name = user.display_name

    try:
        return build_draft(
            year=req.year,
            month=req.month,
            template=effective_template,
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


def _signature_path(settings: Settings, role: str, user_id: str = "default") -> Path | None:
    if user_id != "default":
        user_folder = settings.storage_dir / "signatures" / user_id
        if user_folder.exists():
            for ext in ("png", "jpg"):
                p = user_folder / f"{role}.{ext}"
                if p.exists():
                    return p
        return None
    for ext in ("png", "jpg"):
        p = settings.storage_dir / "signatures" / f"{role}.{ext}"
        if p.exists():
            return p
    return None


@router.post("/timesheet/generate")
def generate(
    req: GenerateRequest,
    authorization: str | None = Header(None, alias="Authorization"),
    settings: Settings = Depends(get_settings),
) -> Response:
    template = _template(req.draft.template_id)
    user = get_current_user(authorization, settings)
    effective_template = template.model_copy()
    if user and user.display_name:
        effective_template.employee_name = user.display_name

    user_id = user.account_id.replace(":", "_") if user else "default"
    content = excel_renderer.render_timesheet(
        req.draft,
        effective_template,
        employee_signature=_signature_path(settings, "employee", user_id),
        team_lead_signature=_signature_path(settings, "team_lead", user_id),
    )
    name = excel_renderer.file_name(effective_template, req.draft.year)
    return Response(
        content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )


@router.get("/signatures", response_model=SignatureStatus)
def signature_status(
    authorization: str | None = Header(None, alias="Authorization"),
    settings: Settings = Depends(get_settings),
) -> SignatureStatus:
    user = get_current_user(authorization, settings)
    user_id = user.account_id.replace(":", "_") if user else "default"
    return SignatureStatus(
        employee=_signature_path(settings, "employee", user_id) is not None,
        team_lead=_signature_path(settings, "team_lead", user_id) is not None,
    )


@router.delete("/signatures/{role}", status_code=204)
def delete_signature(
    role: str,
    authorization: str | None = Header(None, alias="Authorization"),
    settings: Settings = Depends(get_settings),
) -> None:
    if role not in SIGNATURE_ROLES:
        raise HTTPException(404, "Role tidak dikenal")
    user = get_current_user(authorization, settings)
    user_id = user.account_id.replace(":", "_") if user else "default"
    folder = settings.storage_dir / "signatures" / user_id
    deleted = False
    if folder.exists():
        for old in folder.glob(f"{role}.*"):
            old.unlink()
            deleted = True
    for old in (settings.storage_dir / "signatures").glob(f"{role}.*"):
        old.unlink()
        deleted = True
    if not deleted:
        raise HTTPException(404, f"Tanda tangan '{role}' tidak ditemukan")


@router.get("/jira/status", response_model=JiraStatus)
def jira_status(
    authorization: str | None = Header(None, alias="Authorization"),
    settings: Settings = Depends(get_settings),
) -> JiraStatus:
    user = get_current_user(authorization, settings)
    if user:
        return JiraStatus(
            connected=True,
            site_url=user.site_url,
            email=user.email,
            display_name=user.display_name,
            account_id=user.account_id,
            token=user.token,
            message=f"Terkoneksi sebagai {user.display_name} ({user.email})",
        )
    if settings.jira_mock:
        return JiraStatus(
            connected=True,
            site_url="mock://jira.local",
            email="developer@example.com",
            display_name="Developer Mock",
            account_id="mock-user",
            token="mock-token",
            message="Menggunakan data simulasi Jira (Mock Mode)",
        )
    if settings.jira_base_url and settings.jira_email and settings.jira_api_token:
        return JiraStatus(
            connected=True,
            site_url=settings.jira_base_url,
            email=settings.jira_email,
            display_name="Aria Nur Jamal",
            account_id="default-user",
            token="default-env-token",
            message=f"Terkoneksi ke Jira Cloud ({settings.jira_email})",
        )
    return JiraStatus(
        connected=False,
        message="Belum terhubung ke Jira Cloud. Silakan hubungkan token akun Anda.",
    )


@router.post("/auth/logout", status_code=204)
def auth_logout(
    authorization: str | None = Header(None, alias="Authorization"),
) -> None:
    token = _extract_token(authorization)
    if token and token in SESSIONS:
        del SESSIONS[token]


@router.post("/auth/login", response_model=AuthResponse)
def auth_login(req: LoginRequest, settings: Settings = Depends(get_settings)) -> AuthResponse:
    acc = authenticate_user(settings.storage_dir, req.username_or_email, req.password)
    if not acc:
        raise HTTPException(401, "Username/Email atau Password salah. Akun dibuat dan dikelola oleh Admin.")
    token = secrets.token_urlsafe(32)
    sess = UserSession(
        token=token,
        user_id=acc.id,
        username=acc.username,
        email=acc.email,
        api_token=acc.jira_api_token,
        site_url=acc.jira_site_url,
        display_name=acc.display_name,
        role=acc.role,
        template_id=acc.template_id,
    )
    SESSIONS[token] = sess
    return AuthResponse(token=token, user=acc.to_public(), message="Login berhasil")


@router.get("/auth/me", response_model=UserPublic)
def auth_me(
    authorization: str | None = Header(None, alias="Authorization"),
    settings: Settings = Depends(get_settings),
) -> UserPublic:
    user = get_current_user(authorization, settings)
    if not user:
        raise HTTPException(401, "Sesi tidak valid atau belum login")
    acc = get_user_by_id(settings.storage_dir, user.user_id)
    if not acc:
        # Jika default env user
        return UserPublic(
            id=user.user_id,
            username=user.username,
            email=user.email,
            display_name=user.display_name,
            role=user.role,  # type: ignore[arg-type]
            template_id=user.template_id,
            jira_site_url=user.site_url,
            has_api_token=bool(user.api_token),
        )
    return acc.to_public()


@router.get("/admin/users", response_model=list[UserPublic])
def admin_list_users(
    authorization: str | None = Header(None, alias="Authorization"),
    settings: Settings = Depends(get_settings),
) -> list[UserPublic]:
    user = get_current_user(authorization, settings)
    # Admin atau developer lokal dev diizinkan
    if user and user.role not in ("admin", "developer"):
        raise HTTPException(403, "Hanya admin yang memiliki izin mengelola akun pengguna.")
    return [u.to_public() for u in load_all_users(settings.storage_dir)]


@router.post("/admin/users", response_model=UserPublic, status_code=201)
def admin_create_user(
    data: UserAccountCreate,
    authorization: str | None = Header(None, alias="Authorization"),
    settings: Settings = Depends(get_settings),
) -> UserPublic:
    user = get_current_user(authorization, settings)
    if user and user.role not in ("admin", "developer"):
        raise HTTPException(403, "Hanya admin yang memiliki izin membuat akun baru.")
    try:
        acc = create_user_account(settings.storage_dir, data)
        return acc.to_public()
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.put("/admin/users/{user_id}", response_model=UserPublic)
def admin_update_user(
    user_id: str,
    data: UserAccountUpdate,
    authorization: str | None = Header(None, alias="Authorization"),
    settings: Settings = Depends(get_settings),
) -> UserPublic:
    user = get_current_user(authorization, settings)
    if user and user.role not in ("admin", "developer"):
        raise HTTPException(403, "Hanya admin yang memiliki izin mengubah akun.")
    try:
        acc = update_user_account(settings.storage_dir, user_id, data)
        return acc.to_public()
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.delete("/admin/users/{user_id}", status_code=204)
def admin_delete_user(
    user_id: str,
    authorization: str | None = Header(None, alias="Authorization"),
    settings: Settings = Depends(get_settings),
) -> None:
    user = get_current_user(authorization, settings)
    if user and user.role not in ("admin", "developer"):
        raise HTTPException(403, "Hanya admin yang memiliki izin menghapus akun.")
    try:
        delete_user_account(settings.storage_dir, user_id)
    except (KeyError, ValueError) as exc:
        raise HTTPException(400, str(exc)) from exc


@router.post("/jira/connect", response_model=JiraStatus)
async def jira_connect(req: JiraConnectRequest) -> JiraStatus:
    client = JiraClient(req.site_url, req.email, req.api_token)
    try:
        res = await client._client.get("/rest/api/3/myself")
        if res.status_code == 200:
            user_info = res.json()
            token = secrets.token_urlsafe(32)
            display_name = user_info.get("displayName", req.email)
            account_id = user_info.get("accountId", req.email)
            sess = UserSession(
                token=token,
                email=user_info.get("emailAddress", req.email),
                api_token=req.api_token,
                site_url=req.site_url,
                display_name=display_name,
                account_id=account_id,
            )
            SESSIONS[token] = sess
            return JiraStatus(
                connected=True,
                site_url=req.site_url,
                email=sess.email,
                display_name=display_name,
                account_id=account_id,
                token=token,
                message=f"Berhasil terhubung sebagai {display_name}",
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
async def upload_signature(
    role: str,
    file: UploadFile,
    authorization: str | None = Header(None, alias="Authorization"),
    settings: Settings = Depends(get_settings),
) -> None:
    """Employee diunggah karyawan; Team Lead diunggah Team Lead sendiri."""
    if role not in SIGNATURE_ROLES:
        raise HTTPException(404, "Role tidak dikenal")
    ext = {"image/png": "png", "image/jpeg": "jpg"}.get(file.content_type or "")
    if not ext:
        raise HTTPException(415, "Format harus PNG atau JPG")
    content = await file.read()
    if len(content) > MAX_SIGNATURE_BYTES:
        raise HTTPException(413, "Ukuran maksimum 1 MB")

    user = get_current_user(authorization, settings)
    user_id = user.account_id.replace(":", "_") if user else "default"

    root_folder = settings.storage_dir / "signatures"
    root_folder.mkdir(parents=True, exist_ok=True)
    for old in root_folder.glob(f"{role}.*"):
        old.unlink()
    (root_folder / f"{role}.{ext}").write_bytes(content)

    if user:
        user_folder = root_folder / user_id
        user_folder.mkdir(parents=True, exist_ok=True)
        for old in user_folder.glob(f"{role}.*"):
            old.unlink()
        (user_folder / f"{role}.{ext}").write_bytes(content)


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "today": date.today().isoformat()}
