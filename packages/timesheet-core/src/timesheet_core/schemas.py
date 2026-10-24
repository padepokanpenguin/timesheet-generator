"""Skema data. Template spec = Bagian 5.6 PRD; FormulaConfig = Bagian 5.4.3 PRD."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    """Basis semua skema: field ber-default dianggap wajib pada respons (tipe klien TS lebih akurat)."""

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)


Language = Literal["id", "en"]
RowKind = Literal["work", "weekend", "holiday", "leave"]


class FormulaConfig(ApiModel):
    """Parameter formula persentase (dikelola admin di template)."""

    hours_per_manday: float = 8.0
    story_point_to_manday: float = 1.0
    max_progress_before_done: int = 95
    rounding_step: int = 5
    min_daily_portion: int = 5
    segmentation_mode: Literal["random", "manual"] = "random"
    carry_over_between_months: bool = True


class TemplateSpec(ApiModel):
    id: str
    name: str
    language: Language = "id"
    company_name: str
    client: str
    department: str
    title: str  # jabatan karyawan
    employee_name: str
    team_lead_name: str
    work_start: str = "08:30"
    work_end: str = "17:30"
    break_minutes: int = 60
    show_all_days: bool = True  # False = hanya hari kerja, Id dinomori ulang
    timezone: str = "Asia/Jakarta"
    holiday_country: str = "ID"
    extra_holidays: list[date] = Field(default_factory=list)
    file_name_pattern: str = "TimeSheet_{name}_{year}.xlsx"
    formula: FormulaConfig = Field(default_factory=FormulaConfig)
    company_logo: str | None = None
    client_logo: str | None = None


class StoryEntry(ApiModel):
    key: str
    title: str
    epic: str | None = None
    percent: int | None = None
    activities: list[str] = Field(default_factory=list)  # judul sub-task (boleh diedit)


class DayRow(ApiModel):
    date: date
    kind: RowKind = "work"
    time_in: str | None = None  # "HH:MM"
    time_out: str | None = None
    working_hours: float | None = None
    stories: list[StoryEntry] = Field(default_factory=list)
    free_text: str | None = None  # entri non-tiket
    warnings: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)


class StoryState(ApiModel):
    """Status akhir bulan per story, disimpan agar bulan berikutnya melanjutkan."""

    previous_percent: int = 0
    prior_active_days: int = 0


class TimesheetDraft(ApiModel):
    year: int
    month: int
    template_id: str
    rows: list[DayRow]
    warnings: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    story_end_state: dict[str, StoryState] = Field(default_factory=dict)


class PreviewRequest(ApiModel):
    year: int
    month: int = Field(ge=1, le=12)
    template_id: str = "default-id"
    leave_dates: list[date] = Field(default_factory=list)
    # { "BPAS-5437": { "2026-01-21": 20, ... } }  -> segmentasi manual (opsi A)
    manual_percent: dict[str, dict[date, int]] = Field(default_factory=dict)
    story_state: dict[str, StoryState] = Field(default_factory=dict)
    reroll_seed: int = 0  # naikkan untuk "acak ulang"
    show_all_days: bool | None = None  # None = ikuti template
    non_ticket_entries: dict[date, str] = Field(default_factory=dict)
    manual_estimates: dict[str, float] = Field(default_factory=dict)
    manual_epics: dict[str, str] = Field(default_factory=dict)
    custom_hours: dict[date, dict[str, str | float]] = Field(default_factory=dict)


class GenerateRequest(ApiModel):
    draft: TimesheetDraft


class SignatureStatus(ApiModel):
    employee: bool = False
    team_lead: bool = False


class JiraStatus(ApiModel):
    connected: bool = False
    site_url: str | None = None
    email: str | None = None
    display_name: str | None = None
    account_id: str | None = None
    token: str | None = None
    message: str | None = None


class JiraConnectRequest(ApiModel):
    site_url: str
    email: str
    api_token: str


class FormulaSimulateRequest(ApiModel):
    formula: FormulaConfig = Field(default_factory=FormulaConfig)
    estimate_mandays: float = 4.0
    active_days: int = 3
    done: bool = False
    start_percent: int = 0
    seed: str = "simulation-seed"


class FormulaSimulateResponse(ApiModel):
    total_progress: int | None
    daily_percentages: list[int]


UserRole = Literal["developer", "team_lead", "admin"]


class LoginRequest(ApiModel):
    username_or_email: str
    password: str


class UserPublic(ApiModel):
    id: str
    username: str
    email: str
    display_name: str
    role: UserRole = "developer"
    template_id: str = "default-id"
    jira_site_url: str = "https://ict-siloamhospitals.atlassian.net"
    has_api_token: bool = False


class AuthResponse(ApiModel):
    token: str
    user: UserPublic
    message: str = "Login berhasil"


class UserAccountCreate(ApiModel):
    username: str
    email: str
    display_name: str
    password: str
    role: UserRole = "developer"
    template_id: str = "default-id"
    jira_api_token: str = ""
    jira_site_url: str = "https://ict-siloamhospitals.atlassian.net"


class UserAccountUpdate(ApiModel):
    email: str | None = None
    display_name: str | None = None
    password: str | None = None
    role: UserRole | None = None
    template_id: str | None = None
    jira_api_token: str | None = None
    jira_site_url: str | None = None
