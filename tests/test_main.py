"""Tests for application main.py entry point."""

from __future__ import annotations

import sys
import main


def test_main_cli_flag(monkeypatch) -> None:
    called = False

    def fake_run():
        nonlocal called
        called = True

    monkeypatch.setattr(sys, "argv", ["main.py", "--cli"])
    monkeypatch.setattr("src.cli.run", fake_run)

    main.main()
    assert called is True


def test_main_web_server_default(monkeypatch) -> None:
    launched = {}

    def fake_uvicorn_run(app_str, host, port):
        launched["app"] = app_str
        launched["host"] = host
        launched["port"] = port

    monkeypatch.setattr(sys, "argv", ["main.py", "--host", "127.0.0.1", "--port", "9090"])
    monkeypatch.setattr("uvicorn.run", fake_uvicorn_run)
    monkeypatch.setattr("webbrowser.open", lambda url: True)

    main.main()
    assert launched["app"] == "src.api:app"
    assert launched["host"] == "127.0.0.1"
    assert launched["port"] == 9090
