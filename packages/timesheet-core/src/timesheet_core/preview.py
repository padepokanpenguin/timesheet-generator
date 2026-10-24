"""Membangun draf timesheet dari data Jira (Bagian 5.4 dan 5.5 PRD)."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, time

from timesheet_core import calendar as cal
from timesheet_core.domain import RawJiraData
from timesheet_core.progress import (
    estimate_in_mandays,
    split_progress,
    total_progress,
    validate_manual,
)
from timesheet_core.schemas import (
    DayRow,
    StoryEntry,
    StoryState,
    TemplateSpec,
    TimesheetDraft,
)


def _hhmm(value: str) -> time:
    h, m = value.split(":")
    return time(int(h), int(m))


def default_working_hours(time_in: str, time_out: str, break_minutes: int) -> float:
    a, b = _hhmm(time_in), _hhmm(time_out)
    minutes = (b.hour * 60 + b.minute) - (a.hour * 60 + a.minute) - break_minutes
    return round(minutes / 60, 2)


KNOWN_TYPOS = {
    "100$": "seharusnya 100%",
    "ednpoint": "endpoint",
    "pacakge": "package",
    "dependecy": "dependency",
    "integation": "integration",
    "implemenation": "implementation",
}


def detect_typos(text: str) -> list[str]:
    lower = text.lower()
    found: list[str] = []
    for typo, correction in KNOWN_TYPOS.items():
        if typo in lower:
            found.append(f"'{typo}' (mungkin '{correction}')")
    return found


def build_draft(
    *,
    year: int,
    month: int,
    template: TemplateSpec,
    data: RawJiraData,
    leave_dates: set[date] | None = None,
    manual_percent: dict[str, dict[date, int]] | None = None,
    story_state: dict[str, StoryState] | None = None,
    reroll_seed: int = 0,
    show_all_days: bool | None = None,
    non_ticket_entries: dict[date, str] | None = None,
    manual_estimates: dict[str, float] | None = None,
    manual_epics: dict[str, str] | None = None,
    custom_hours: dict[date, dict[str, str | float]] | None = None,
) -> TimesheetDraft:
    leave_dates = leave_dates or set()
    manual_percent = manual_percent or {}
    story_state = story_state or {}
    non_ticket_entries = non_ticket_entries or {}
    manual_estimates = manual_estimates or {}
    manual_epics = manual_epics or {}
    custom_hours = custom_hours or {}
    cfg = template.formula

    dates = cal.month_dates(year, month)
    holidays = cal.holidays_for(year, template.holiday_country, template.extra_holidays)

    def kind_of(d: date) -> str:
        if d in leave_dates:
            return "leave"
        if d in holidays:
            return "holiday"
        if cal.is_weekend(d):
            return "weekend"
        return "work"

    warnings: list[str] = []
    blockers: list[str] = []

    # 1) Kelompokkan aktivitas per (story, hari kerja). Aktivitas di akhir pekan/libur/cuti diabaikan.
    per_story_day: dict[str, dict[date, list[str]]] = defaultdict(lambda: defaultdict(list))
    no_subtask: set[tuple[str, date]] = set()
    for act in data.activities:
        if kind_of(act.day) != "work" or act.day not in set(dates):
            if act.day in set(dates):
                warnings.append(f"Aktivitas {act.story_key} pada {act.day} diabaikan (bukan hari kerja)")
            continue
        bucket = per_story_day[act.story_key][act.day]
        if act.subtask_summary:
            if act.subtask_summary not in bucket:
                bucket.append(act.subtask_summary)
        else:
            no_subtask.add((act.story_key, act.day))

    # 2) Persentase per story: manual (opsi A) atau acak terkunci (opsi B).
    percent_map: dict[str, dict[date, int | None]] = {}
    end_state: dict[str, StoryState] = {}
    last_day = dates[-1]
    for key, by_day in per_story_day.items():
        story = data.stories.get(key)
        days = sorted(by_day)
        state = story_state.get(key, StoryState())
        prior = state.prior_active_days if cfg.carry_over_between_months else 0
        start = state.previous_percent if cfg.carry_over_between_months else 0
        done = bool(story and story.done_day and story.done_day <= last_day)
        estimate = manual_estimates.get(key)
        if estimate is None and story:
            estimate = estimate_in_mandays(story.estimate_mandays, story.story_points, cfg)
        if estimate is None and not done:
            estimate = float(max(1, len(days)))
        end = total_progress(
            done=done,
            prior_active_days=prior,
            active_days=len(days),
            estimate=estimate,
            previous_percent=start,
            cfg=cfg,
        )

        manual = manual_percent.get(key)
        if manual:
            values = [manual[d] for d in days if d in manual]
            if len(values) == len(days):
                validate_manual(values, start=start, end=end)
                percent_map[key] = dict(zip(days, values, strict=True))
            else:
                warnings.append(f"{key}: persentase manual belum lengkap untuk semua hari aktif")
        if key not in percent_map:
            if end is None:
                blockers.append(f"{key}: Estimasi kosong dan persentase belum diisi manual")
                warnings.append(f"{key}: estimasi kosong, persentase perlu diisi manual")
                percent_map[key] = {d: None for d in days}
            else:
                seed = f"{key}:{year}-{month:02d}:{reroll_seed}"
                values = split_progress(start=start, end=end, days=len(days), cfg=cfg, seed=seed)
                percent_map[key] = dict(zip(days, values, strict=True))
        final = percent_map[key][days[-1]]
        end_state[key] = StoryState(previous_percent=final or start, prior_active_days=prior + len(days))

        epic_label = manual_epics.get(key) or (story.epic_name if story else None)
        if not epic_label:
            blockers.append(f"{key}: Story tanpa Epic ([Label] wajib diisi sebelum ekspor)")
            warnings.append(f"{key}: story tanpa Epic, label wajib diisi manual")
        if not story:
            warnings.append(f"{key}: detail story tidak ditemukan di Jira")

    # 3) Susun baris per hari.
    rows: list[DayRow] = []
    for d in dates:
        kind = kind_of(d)
        row = DayRow(date=d, kind=kind)  # type: ignore[arg-type]
        if kind == "work":
            entries: list[StoryEntry] = []
            for key in sorted(per_story_day):
                if d not in per_story_day[key]:
                    continue
                story = data.stories.get(key)
                title = story.summary if story else key
                epic = manual_epics.get(key) or (story.epic_name if story else None)
                entry = StoryEntry(
                    key=key,
                    title=title,
                    epic=epic,
                    percent=percent_map[key].get(d),
                    activities=per_story_day[key][d],
                )
                for typo_msg in detect_typos(title):
                    row.warnings.append(f"Kemungkinan typo pada judul {key}: {typo_msg}")
                for act in entry.activities:
                    for typo_msg in detect_typos(act):
                        row.warnings.append(f"Kemungkinan typo pada sub-task {key}: {typo_msg}")
                if (key, d) in no_subtask and not entry.activities:
                    row.warnings.append(f"{key}: story tanpa sub-task, aktivitas dikosongkan")
                if not entry.epic:
                    row.warnings.append(f"{key}: label Epic wajib diisi manual")
                    row.blockers.append(f"{key}: Story tanpa Epic ([Label] wajib diisi)")
                entries.append(entry)
            row.stories = entries
            if entries:
                row.time_in, row.time_out = template.work_start, template.work_end
                row.working_hours = default_working_hours(
                    template.work_start, template.work_end, template.break_minutes
                )
            else:
                row.warnings.append("Perlu dicek: hari kerja tanpa aktivitas")

        # Entri non-tiket jika ada
        if d in non_ticket_entries:
            row.free_text = non_ticket_entries[d]

        # Custom jam kerja jika di-override
        if d in custom_hours:
            ch = custom_hours[d]
            if "time_in" in ch and isinstance(ch["time_in"], str):
                row.time_in = ch["time_in"]
            if "time_out" in ch and isinstance(ch["time_out"], str):
                row.time_out = ch["time_out"]
            if "working_hours" in ch and isinstance(ch["working_hours"], (int, float)):
                row.working_hours = float(ch["working_hours"])
        rows.append(row)

    effective_show_all = template.show_all_days if show_all_days is None else show_all_days
    if not effective_show_all:
        rows = [r for r in rows if r.kind in ("work", "leave")]

    return TimesheetDraft(
        year=year,
        month=month,
        template_id=template.id,
        rows=rows,
        warnings=warnings,
        blockers=blockers,
        story_end_state=end_state,
    )
