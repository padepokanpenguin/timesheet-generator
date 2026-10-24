"""Data mentah hasil tarikan Jira (sudah dinormalisasi ke zona waktu template)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class SubtaskActivity:
    """Satu aktivitas user pada sub-task di tanggal tertentu."""

    story_key: str
    day: date
    subtask_key: str | None = None
    subtask_summary: str | None = None  # None = aktivitas langsung di story (tanpa sub-task)


@dataclass
class StoryInfo:
    key: str
    summary: str
    epic_name: str | None = None
    estimate_mandays: float | None = None  # dari Original Estimate
    story_points: float | None = None
    done_day: date | None = None  # tanggal story Done (jika Done)


@dataclass
class RawJiraData:
    activities: list[SubtaskActivity] = field(default_factory=list)
    stories: dict[str, StoryInfo] = field(default_factory=dict)
