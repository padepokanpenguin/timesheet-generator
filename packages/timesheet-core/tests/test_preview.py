from datetime import date

from timesheet_core.preview import build_draft
from timesheet_core.sample_data import sample_month
from timesheet_core.templates import get_template

T = get_template("default-id")


def draft(**kw):
    return build_draft(year=2026, month=1, template=T, data=sample_month(2026, 1), **kw)


def by_date(d):
    return {r.date: r for r in d.rows}


def test_all_calendar_days_by_default():
    d = draft()
    assert len(d.rows) == 31
    rows = by_date(d)
    assert rows[date(2026, 1, 3)].kind == "weekend"
    assert rows[date(2026, 1, 1)].kind == "holiday"  # Tahun Baru


def test_weekend_activity_is_ignored():
    d = draft()
    row = by_date(d)[date(2026, 1, 24)]  # Sabtu
    assert row.kind == "weekend" and row.stories == []
    assert any("diabaikan" in w for w in d.warnings)


def test_story_done_ends_at_100_and_is_random_but_stable():
    d1, d2 = draft(), draft()
    rows = by_date(d1)
    pct = [rows[date(2026, 1, x)].stories[0].percent for x in (21, 22, 23)]
    assert rows[date(2026, 1, 26)].stories[0].percent == 100
    assert pct == sorted(pct)
    assert [r.model_dump() for r in d1.rows] == [r.model_dump() for r in d2.rows]


def test_manual_percent_overrides_random():
    manual = {
        "BPAS-5437": {
            date(2026, 1, 21): 20,
            date(2026, 1, 22): 40,
            date(2026, 1, 23): 60,
            date(2026, 1, 26): 100,
        }
    }
    rows = by_date(draft(manual_percent=manual))
    assert [rows[date(2026, 1, x)].stories[0].percent for x in (21, 22, 23, 26)] == [20, 40, 60, 100]


def test_leave_and_warnings():
    d = draft(leave_dates={date(2026, 1, 14)})
    rows = by_date(d)
    assert rows[date(2026, 1, 14)].kind == "leave" and rows[date(2026, 1, 14)].stories == []
    assert any("tanpa Epic" in w for w in d.warnings)
    assert any("tanpa sub-task" in w for r in d.rows for w in r.warnings)


def test_workdays_only_option_renumbers_rows():
    t = T.model_copy(update={"show_all_days": False})
    d = build_draft(year=2026, month=1, template=t, data=sample_month(2026, 1))
    assert all(r.kind == "work" for r in d.rows)


def test_end_state_for_carry_over():
    d = draft()
    assert d.story_end_state["BPAS-5437"].previous_percent == 100
    assert d.story_end_state["BPAS-5437"].prior_active_days == 4


def test_september_golden_reference_matches_workdays():
    data = sample_month(2026, 9)
    d = build_draft(year=2026, month=9, template=T, data=data)
    assert len(d.rows) == 30
    work_rows = [r for r in d.rows if r.kind == "work"]
    assert len(work_rows) == 22
    assert all(len(r.stories) > 0 for r in work_rows)
