"""Klien Jira Cloud (REST API v3), read-only. Bagian 6 PRD.

Alur: sub-task yang dikerjakan user -> aktivitas per hari (changelog) -> story induk -> Epic.
TODO produksi: OAuth 2.0 (3LO) per pengguna, ambil changelog lengkap bila lebih dari
yang dikembalikan search, dan caching.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import httpx
from timesheet_core.domain import RawJiraData, StoryInfo, SubtaskActivity


class JiraError(RuntimeError):
    pass


class JiraClient:
    def __init__(
        self,
        base_url: str,
        email: str,
        api_token: str,
        *,
        story_points_field: str = "customfield_10016",
        start_date_field: str = "customfield_10015",
        expected_finish_date_field: str = "customfield_10203",
        actual_finish_date_field: str = "customfield_10200",
        timezone: str = "Asia/Jakarta",
        hours_per_manday: float = 8.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._http = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            auth=(email, api_token),
            headers={"Accept": "application/json"},
            timeout=30,
            transport=transport,  # untuk tes (httpx.MockTransport)
        )
        self._sp_field = story_points_field
        self._start_date_field = start_date_field
        self._expected_finish_date_field = expected_finish_date_field
        self._actual_finish_date_field = actual_finish_date_field
        self._tz = ZoneInfo(timezone)
        self._hours_per_manday = hours_per_manday

    async def aclose(self) -> None:
        await self._http.aclose()

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        for attempt in range(4):
            resp = await self._http.request(method, path, **kwargs)
            if resp.status_code == 429:  # rate limit: retry dengan backoff
                wait = float(resp.headers.get("Retry-After", 2**attempt))
                await asyncio.sleep(wait)
                continue
            if resp.is_error:
                raise JiraError(f"Jira {resp.status_code}: {resp.text[:300]}")
            return resp.json()
        raise JiraError("Jira rate limit: coba lagi nanti")

    async def _search(self, jql: str, fields: list[str], expand: str | None = None) -> AsyncIterator[dict]:
        token: str | None = None
        while True:
            body: dict = {"jql": jql, "fields": fields, "maxResults": 100}
            if expand:
                body["expand"] = expand
            if token:
                body["nextPageToken"] = token
            data = await self._request("POST", "/rest/api/3/search/jql", json=body)
            for issue in data.get("issues", []):
                yield issue
            token = data.get("nextPageToken")
            if not token:
                return

    def _to_local_day(self, iso: str) -> date:
        return datetime.fromisoformat(iso).astimezone(self._tz).date()

    async def fetch_month(self, year: int, month: int) -> RawJiraData:
        me = await self._request("GET", "/rest/api/3/myself")
        account_id = me["accountId"]
        start = date(year, month, 1)
        end = date(year + (month == 12), (month % 12) + 1, 1)
        last_month_day = end - timedelta(days=1)
        rng = f'("{start}", "{end}")'
        jql = (
            '(issuetype = "Subtask Development" OR issuetype in subTaskIssueTypes()) AND '
            f"(assignee = currentUser() OR assignee was currentUser() during {rng}) AND "
            f'(("Start date" <= "{last_month_day}" AND "Expected Finish Date" >= "{start}") '
            f'OR updated >= "{start}")'
        )

        data = RawJiraData()
        story_keys: set[str] = set()
        search_fields = [
            "summary",
            "parent",
            "created",
            "updated",
            "status",
            self._start_date_field,
            self._expected_finish_date_field,
            self._actual_finish_date_field,
        ]
        async for issue in self._search(jql, search_fields, expand="changelog"):
            parent = (issue["fields"].get("parent") or {}).get("key")
            # Khusus BIM-263 pada timesheet gunakan tiket subtask development
            if not parent or parent == "BIM-263":
                parent = issue["key"]
            story_keys.add(parent)

            changelog_days = {
                self._to_local_day(h["created"])
                for h in issue.get("changelog", {}).get("histories", [])
                if (h.get("author") or {}).get("accountId") == account_id
            }

            days = set()

            # Start date dan Expected Finish Date (Bagian instruksi khusus Subtask Development)
            start_raw = issue["fields"].get(self._start_date_field)
            expected_raw = issue["fields"].get(self._expected_finish_date_field)
            actual_raw = issue["fields"].get(self._actual_finish_date_field)

            start_d = None
            if start_raw:
                try:
                    start_d = date.fromisoformat(str(start_raw)[:10])
                except ValueError:
                    pass
            elif issue["fields"].get("created"):
                start_d = self._to_local_day(issue["fields"]["created"])

            end_d = None
            if expected_raw:
                try:
                    end_d = date.fromisoformat(str(expected_raw)[:10])
                except ValueError:
                    pass
            elif actual_raw:
                try:
                    end_d = self._to_local_day(str(actual_raw))
                except Exception:
                    pass
            elif issue["fields"].get("updated"):
                end_d = self._to_local_day(issue["fields"]["updated"])

            if not start_d and not end_d:
                days = set(changelog_days)
            else:
                if not start_d:
                    start_d = end_d
                if not end_d:
                    end_d = start_d
                if start_d > end_d:
                    end_d = start_d

                # Periksa irisan rentang [start_d, end_d] dengan bulan yang dipilih
                if end_d >= start and start_d <= last_month_day:
                    cur = max(start_d, start)
                    last = min(end_d, last_month_day)
                    step = cur
                    while step <= last:
                        if step.weekday() < 5:  # hanya hari kerja Senin-Jumat
                            days.add(step)
                        step += timedelta(days=1)
            for day in sorted(d for d in days if start <= d < end and d.weekday() < 5):
                data.activities.append(
                    SubtaskActivity(
                        story_key=parent,
                        day=day,
                        subtask_key=issue["key"],
                        subtask_summary=issue["fields"]["summary"],
                    )
                )

        if story_keys:
            keys = ", ".join(sorted(story_keys))
            fields = [
                "summary",
                "status",
                "resolutiondate",
                "parent",
                "timeoriginalestimate",
                self._sp_field,
                self._start_date_field,
                self._expected_finish_date_field,
                self._actual_finish_date_field,
            ]
            async for story in self._search(f"key in ({keys})", fields):
                f = story["fields"]
                parent = f.get("parent") or {}
                epic = None
                if (parent.get("fields", {}).get("issuetype", {}).get("name")) == "Epic":
                    epic = parent["fields"]["summary"]
                elif parent.get("key") == "BIM-263" or story["key"].startswith("BIM-"):
                    epic = "BIMC Implementation"
                elif story["key"].startswith("PM2-"):
                    epic = "Package Management"
                elif story["key"].startswith("KP2-"):
                    epic = "Stabilization Kairos"
                done_day = None
                status_cat = f.get("status", {}).get("statusCategory", {}).get("key")
                status_name = f.get("status", {}).get("name", "")
                is_done_status = status_cat == "done" or any(
                    term in status_name for term in ["Completed", "Done", "Resolved", "Closed"]
                )
                if is_done_status:
                    if f.get("resolutiondate"):
                        done_day = self._to_local_day(f["resolutiondate"])
                    elif f.get(self._actual_finish_date_field):
                        done_day = self._to_local_day(str(f[self._actual_finish_date_field]))
                    elif f.get(self._expected_finish_date_field):
                        try:
                            done_day = date.fromisoformat(str(f[self._expected_finish_date_field])[:10])
                        except Exception:
                            done_day = self._to_local_day(f["updated"]) if f.get("updated") else date.today()
                    elif f.get("updated"):
                        done_day = self._to_local_day(f["updated"])
                    else:
                        done_day = date.today()

                seconds = f.get("timeoriginalestimate")
                est_days = (seconds / 3600 / self._hours_per_manday) if seconds else None
                if est_days is None:
                    # Hitung estimasi dari hari kerja antara Start date dan Expected Finish Date jika ada
                    st_val = f.get(self._start_date_field)
                    exp_val = f.get(self._expected_finish_date_field)
                    if st_val and exp_val:
                        try:
                            s_d = date.fromisoformat(str(st_val)[:10])
                            e_d = date.fromisoformat(str(exp_val)[:10])
                            workday_count = sum(
                                1
                                for i in range((e_d - s_d).days + 1)
                                if (s_d + timedelta(days=i)).weekday() < 5
                            )
                            est_days = float(max(1, workday_count))
                        except Exception:
                            pass

                data.stories[story["key"]] = StoryInfo(
                    key=story["key"],
                    summary=f["summary"],
                    epic_name=epic,
                    estimate_mandays=est_days,
                    story_points=f.get(self._sp_field),
                    done_day=done_day,
                )
        return data
