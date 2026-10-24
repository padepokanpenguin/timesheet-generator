import pytest
from timesheet_core.progress import (
    ProgressError,
    split_progress,
    total_progress,
    validate_manual,
)
from timesheet_core.schemas import FormulaConfig

CFG = FormulaConfig()


def test_split_sums_and_is_monotonic():
    values = split_progress(start=0, end=100, days=3, cfg=CFG, seed="BPAS-1:2026-01:0")
    assert len(values) == 3
    assert values[-1] == 100
    assert values == sorted(values)
    assert all(v % 5 == 0 for v in values)
    # porsi harian minimal 5%
    portions = [b - a for a, b in zip([0, *values], values, strict=False)]
    assert all(p >= 5 for p in portions)


def test_split_is_deterministic_and_reroll_changes_result():
    a = split_progress(start=0, end=100, days=4, cfg=CFG, seed="X:2026-01:0")
    b = split_progress(start=0, end=100, days=4, cfg=CFG, seed="X:2026-01:0")
    assert a == b
    others = {
        tuple(split_progress(start=0, end=100, days=4, cfg=CFG, seed=f"X:2026-01:{i}")) for i in range(1, 8)
    }
    assert any(list(o) != a for o in others)


def test_split_continues_from_previous_month():
    values = split_progress(start=60, end=100, days=2, cfg=CFG, seed="Y")
    assert values[-1] == 100 and values[0] > 60


def test_split_when_total_too_small_still_ends_at_target():
    values = split_progress(start=0, end=10, days=5, cfg=CFG, seed="Z")
    assert values[-1] == 10 and values == sorted(values)


def test_total_progress_done_and_in_progress():
    assert (
        total_progress(done=True, prior_active_days=0, active_days=3, estimate=5, previous_percent=0, cfg=CFG)
        == 100
    )
    # 3 hari aktif dari estimasi 5 mandays = 60%
    assert (
        total_progress(
            done=False, prior_active_days=0, active_days=3, estimate=5, previous_percent=0, cfg=CFG
        )
        == 60
    )
    # dibatasi 95%
    assert (
        total_progress(
            done=False, prior_active_days=0, active_days=9, estimate=5, previous_percent=0, cfg=CFG
        )
        == 95
    )
    assert (
        total_progress(
            done=False, prior_active_days=0, active_days=2, estimate=None, previous_percent=0, cfg=CFG
        )
        is None
    )


def test_validate_manual():
    validate_manual([20, 40, 100], start=0, end=100)
    with pytest.raises(ProgressError):
        validate_manual([40, 20, 100], start=0, end=100)
    with pytest.raises(ProgressError):
        validate_manual([20, 40, 80], start=0, end=100)
