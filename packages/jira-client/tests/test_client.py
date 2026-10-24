import asyncio
import json
from datetime import date

import httpx
from jira_client import JiraClient


def make_transport():
    state = {"myself_calls": 0, "subtask_pages": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/rest/api/3/myself":
            state["myself_calls"] += 1
            if state["myself_calls"] == 1:  # rate limit dulu, lalu sukses
                return httpx.Response(429, headers={"Retry-After": "0"})
            return httpx.Response(200, json={"accountId": "me"})
        assert path == "/rest/api/3/search/jql"
        body = json.loads(request.content)
        if "subTaskIssueTypes" in body["jql"]:
            state["subtask_pages"] += 1
            if "nextPageToken" not in body:  # halaman 1
                return httpx.Response(
                    200,
                    json={
                        "nextPageToken": "t2",
                        "issues": [
                            {
                                "key": "BPAS-2",
                                "fields": {"summary": "development endpoint", "parent": {"key": "BPAS-1"}},
                                "changelog": {
                                    "histories": [
                                        {
                                            "author": {"accountId": "me"},
                                            "created": "2026-01-12T10:00:00.000+0700",
                                        },
                                        {
                                            "author": {"accountId": "me"},
                                            "created": "2026-01-12T15:00:00.000+0700",
                                        },
                                        {
                                            "author": {"accountId": "other"},
                                            "created": "2026-01-14T10:00:00.000+0700",
                                        },
                                    ]
                                },
                            }
                        ],
                    },
                )
            return httpx.Response(
                200,
                json={  # halaman 2
                    "issues": [
                        {
                            "key": "BPAS-3",
                            "fields": {"summary": "unit test", "parent": {"key": "BPAS-1"}},
                            # 02:00 WIB = 19:00 UTC hari sebelumnya; harus tetap dihitung tanggal WIB (13 Jan)
                            "changelog": {
                                "histories": [
                                    {"author": {"accountId": "me"}, "created": "2026-01-13T02:00:00.000+0700"}
                                ]
                            },
                        }
                    ]
                },
            )
        assert "key in (BPAS-1)" in body["jql"]
        return httpx.Response(
            200,
            json={
                "issues": [
                    {
                        "key": "BPAS-1",
                        "fields": {
                            "summary": "BE - Optimize Query",
                            "status": {"statusCategory": {"key": "done"}},
                            "resolutiondate": "2026-01-13T09:00:00.000+0700",
                            "parent": {
                                "key": "BPAS-0",
                                "fields": {"summary": "Stabilization Kairos", "issuetype": {"name": "Epic"}},
                            },
                            "timeoriginalestimate": 5 * 8 * 3600,
                            "customfield_10016": None,
                        },
                    }
                ]
            },
        )

    return httpx.MockTransport(handler), state


def test_fetch_month_maps_subtasks_story_and_epic():
    transport, state = make_transport()
    client = JiraClient("https://x.atlassian.net", "a@b.c", "token", transport=transport)
    data = asyncio.run(client.fetch_month(2026, 1))

    assert state["myself_calls"] == 2  # retry setelah 429
    assert state["subtask_pages"] == 2  # pagination lewat nextPageToken
    days = sorted((a.subtask_key, a.day) for a in data.activities)
    # BPAS-2: 2 aktivitas di hari yang sama dihitung satu hari; aktivitas "other" diabaikan
    assert days == [("BPAS-2", date(2026, 1, 12)), ("BPAS-3", date(2026, 1, 13))]
    story = data.stories["BPAS-1"]
    assert story.epic_name == "Stabilization Kairos"
    assert story.estimate_mandays == 5
    assert story.done_day == date(2026, 1, 13)
