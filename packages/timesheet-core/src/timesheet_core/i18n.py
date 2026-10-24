"""Label dan nama bulan per bahasa template (Bagian 5.6 PRD)."""

from __future__ import annotations

MONTHS = {
    "id": [
        "Januari",
        "Februari",
        "Maret",
        "April",
        "Mei",
        "Juni",
        "Juli",
        "Agustus",
        "September",
        "Oktober",
        "November",
        "Desember",
    ],
    "en": [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ],
}

LABELS = {
    "id": {"period": "Periode", "leave": "CUTI", "employee": "Employee", "team_lead": "Team Lead"},
    "en": {"period": "Period", "leave": "LEAVE", "employee": "Employee", "team_lead": "Team Lead"},
}


def month_name(lang: str, month: int) -> str:
    return MONTHS[lang][month - 1]


def label(lang: str, key: str) -> str:
    return LABELS[lang][key]
