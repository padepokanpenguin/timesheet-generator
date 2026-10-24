"""Manajemen akun pengguna (hanya admin yang dapat membuat dan mengedit akun)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel
from timesheet_core.schemas import UserAccountCreate, UserAccountUpdate, UserPublic, UserRole


class UserAccount(BaseModel):
    id: str
    username: str
    email: str
    display_name: str
    password: str
    role: UserRole = "developer"
    template_id: str = "default-id"
    jira_site_url: str = "https://ict-siloamhospitals.atlassian.net"
    jira_api_token: str = ""
    created_at: str = ""

    def to_public(self) -> UserPublic:
        return UserPublic(
            id=self.id,
            username=self.username,
            email=self.email,
            display_name=self.display_name,
            role=self.role,
            template_id=self.template_id,
            jira_site_url=self.jira_site_url,
            has_api_token=bool(self.jira_api_token and self.jira_api_token.strip()),
        )


def _users_file(storage_dir: Path) -> Path:
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir / "users.json"


def _initial_users() -> list[UserAccount]:
    now = datetime.now().isoformat()
    return [
        UserAccount(
            id="admin",
            username="admin",
            email="admin@example.com",
            display_name="Admin PMO",
            password="admin123",
            role="admin",
            template_id="default-id",
            jira_site_url="",
            jira_api_token="",
            created_at=now,
        ),
        UserAccount(
            id="developer",
            username="developer",
            email="developer@example.com",
            display_name="Developer",
            password="dev123",
            role="developer",
            template_id="default-id",
            jira_site_url="",
            jira_api_token="",
            created_at=now,
        ),
    ]


def load_all_users(storage_dir: Path) -> list[UserAccount]:
    f = _users_file(storage_dir)
    if not f.exists():
        initial = _initial_users()
        save_all_users(storage_dir, initial)
        return initial
    try:
        raw = json.loads(f.read_text(encoding="utf-8"))
        return [UserAccount.model_validate(u) for u in raw]
    except Exception:
        initial = _initial_users()
        save_all_users(storage_dir, initial)
        return initial


def save_all_users(storage_dir: Path, users: list[UserAccount]) -> None:
    f = _users_file(storage_dir)
    data = [u.model_dump() for u in users]
    f.write_text(json.dumps(data, indent=2), encoding="utf-8")


def authenticate_user(storage_dir: Path, username_or_email: str, password: str) -> UserAccount | None:
    users = load_all_users(storage_dir)
    target = username_or_email.strip().lower()
    for u in users:
        if (u.username.lower() == target or u.email.lower() == target) and u.password == password:
            return u
    return None


def get_user_by_id(storage_dir: Path, user_id: str) -> UserAccount | None:
    users = load_all_users(storage_dir)
    for u in users:
        if u.id == user_id:
            return u
    return None


def create_user_account(storage_dir: Path, data: UserAccountCreate) -> UserAccount:
    users = load_all_users(storage_dir)
    uname = data.username.strip().lower()
    for u in users:
        if u.username.lower() == uname:
            raise ValueError(f"Username '{data.username}' sudah digunakan")
        if u.email.lower() == data.email.strip().lower():
            raise ValueError(f"Email '{data.email}' sudah terdaftar")

    new_id = uname.replace(" ", ".")
    now = datetime.now().isoformat()
    acc = UserAccount(
        id=new_id,
        username=data.username.strip(),
        email=data.email.strip(),
        display_name=data.display_name.strip(),
        password=data.password,
        role=data.role,
        template_id=data.template_id,
        jira_site_url=data.jira_site_url.strip(),
        jira_api_token=data.jira_api_token.strip(),
        created_at=now,
    )
    users.append(acc)
    save_all_users(storage_dir, users)
    return acc


def update_user_account(storage_dir: Path, user_id: str, data: UserAccountUpdate) -> UserAccount:
    users = load_all_users(storage_dir)
    target = None
    for u in users:
        if u.id == user_id:
            target = u
            break
    if not target:
        raise KeyError(f"User '{user_id}' tidak ditemukan")

    if data.email is not None:
        target.email = data.email.strip()
    if data.display_name is not None:
        target.display_name = data.display_name.strip()
    if data.password is not None and data.password.strip():
        target.password = data.password
    if data.role is not None:
        target.role = data.role
    if data.template_id is not None:
        target.template_id = data.template_id
    if data.jira_api_token is not None:
        target.jira_api_token = data.jira_api_token.strip()
    if data.jira_site_url is not None:
        target.jira_site_url = data.jira_site_url.strip()

    save_all_users(storage_dir, users)
    return target


def delete_user_account(storage_dir: Path, user_id: str) -> None:
    if user_id == "admin":
        raise ValueError("Akun admin utama tidak boleh dihapus")
    users = load_all_users(storage_dir)
    filtered = [u for u in users if u.id != user_id]
    if len(filtered) == len(users):
        raise KeyError(f"User '{user_id}' tidak ditemukan")
    save_all_users(storage_dir, filtered)
