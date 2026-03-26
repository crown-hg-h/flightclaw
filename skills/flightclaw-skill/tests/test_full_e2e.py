"""Smoke: run Click CLI via subprocess."""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

_SKILL_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _env() -> dict[str, str]:
    env = os.environ.copy()
    root = str(_SKILL_ROOT)
    env["PYTHONPATH"] = root + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    return env


def test_cli_today_json():
    r = subprocess.run(
        [sys.executable, "-m", "flightclaw", "--json", "today"],
        cwd=str(_SKILL_ROOT),
        env=_env(),
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(r.stdout)
    assert "today" in data


def test_cli_search_json():
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "flightclaw",
            "--json",
            "search",
            "--from",
            "BJS",
            "--to",
            "SHA",
            "--date",
            "2026-04-01",
        ],
        cwd=str(_SKILL_ROOT),
        env=_env(),
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(r.stdout)
    assert data["provider"] == "example"
    assert data["query"]["origin"] == "BJS"
