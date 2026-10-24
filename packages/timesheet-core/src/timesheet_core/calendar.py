"""Hari kerja, akhir pekan, dan hari libur."""

from __future__ import annotations

import calendar as _cal
from datetime import date, timedelta


def month_dates(year: int, month: int) -> list[date]:
    last = _cal.monthrange(year, month)[1]
    return [date(year, month, d) for d in range(1, last + 1)]


def is_weekend(d: date) -> bool:
    return d.weekday() >= 5


def holidays_for(year: int, country: str = "ID", extra: list[date] | None = None) -> set[date]:
    """Libur nasional dari paket `holidays` + tambahan dari template.

    Catatan: cuti bersama sebaiknya dimasukkan lewat `extra_holidays` di template.
    """
    found: set[date] = set()
    try:
        import holidays

        found = set(holidays.country_holidays(country, years=year).keys())
    except Exception:  # paket tidak tersedia / negara tidak didukung
        pass
    return found | set(extra or [])


def previous_workday(d: date, holidays: set[date]) -> date:
    d -= timedelta(days=1)
    while is_weekend(d) or d in holidays:
        d -= timedelta(days=1)
    return d
