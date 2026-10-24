"""Perhitungan persentase progres (Bagian 5.4.2 dan 5.4.3 PRD).

Semua nilai persentase bersifat KUMULATIF per hari aktif, mis. [20, 40, 100].
"""

from __future__ import annotations

import math
import random

from timesheet_core.schemas import FormulaConfig


class ProgressError(ValueError):
    pass


def _floor_step(value: float, step: int) -> int:
    return int(math.floor(value / step + 1e-9)) * step


def estimate_in_mandays(
    estimate_mandays: float | None, story_points: float | None, cfg: FormulaConfig
) -> float | None:
    """Original Estimate dulu; cadangan Story Points; selain itu None (isi manual)."""
    if estimate_mandays:
        return estimate_mandays
    if story_points:
        return story_points * cfg.story_point_to_manday
    return None


def total_progress(
    *,
    done: bool,
    prior_active_days: int,
    active_days: int,
    estimate: float | None,
    previous_percent: int,
    cfg: FormulaConfig,
) -> int | None:
    """Persentase kumulatif di akhir periode. None = tidak bisa dihitung (estimasi kosong)."""
    if done:
        return 100
    if not estimate:
        return None
    raw = (prior_active_days + active_days) / estimate * 100
    capped = min(_floor_step(raw, cfg.rounding_step), cfg.max_progress_before_done)
    return max(capped, previous_percent)


def split_progress(*, start: int, end: int, days: int, cfg: FormulaConfig, seed: str) -> list[int]:
    """Bagi (end - start) ke `days` hari secara acak, deterministik per seed.

    - Tiap porsi kelipatan `rounding_step`, minimal `min_daily_portion` bila memungkinkan.
    - Hasil kumulatif naik dan hari terakhir tepat `end`.
    """
    if days <= 0:
        return []
    step = cfg.rounding_step
    delta = end - start
    if delta < 0:
        raise ProgressError("end < start")
    units = delta // step
    min_units = max(cfg.min_daily_portion // step, 0)

    rng = random.Random(seed)
    if units < days * min_units:
        # Total terlalu kecil untuk semua hari: beri porsi minimum ke hari-hari terakhir.
        portions = [0] * days
        give = units // max(min_units, 1)
        for i in range(days - give, days):
            portions[i] = min_units
        portions[-1] += units - sum(portions)
    else:
        remaining = units - days * min_units
        if days == 1:
            extras = [remaining]
        else:
            cuts = sorted(rng.sample(range(remaining + days - 1), days - 1))
            bounds = [-1, *cuts, remaining + days - 1]
            extras = [bounds[i + 1] - bounds[i] - 1 for i in range(days)]
        portions = [min_units + e for e in extras]

    out: list[int] = []
    running = start
    for p in portions:
        running += p * step
        out.append(running)
    out[-1] = end
    return out


def validate_manual(values: list[int], *, start: int, end: int | None) -> None:
    """Opsi A: persentase manual harus naik dan hari terakhir = total progres."""
    prev = start
    for v in values:
        if not 0 <= v <= 100:
            raise ProgressError("Persentase harus 0-100")
        if v < prev:
            raise ProgressError("Persentase harian harus naik")
        prev = v
    if end is not None and values and values[-1] != end:
        raise ProgressError(f"Hari terakhir harus {end}%")
