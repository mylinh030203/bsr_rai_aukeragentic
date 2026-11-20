"""Playwright fixtures: a real server on a throwaway database."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="session")
def base_url(tmp_path_factory):
    database = tmp_path_factory.mktemp("e2e") / "e2e.db"
    server_log = open(database.parent / "server.log", "wb")
    port = _free_port()
    env = {
        **os.environ,
        "BSR_DATABASE": str(database),
        "BSR_NO_RELOAD": "1",
        "BSR_PORT": str(port),
        "BSR_SEED_ON_START": "1",
        "BSR_RATE_LIMIT_LOGIN": "1000",
        "BSR_RATE_LIMIT_ASSISTANT": "1000",
        "BSR_RATE_LIMIT_UPLOAD": "1000",
        "BSR_RATE_LIMIT_EXPORT": "1000",
    }
    process = subprocess.Popen(
        [sys.executable, "run.py"],
        cwd=PROJECT_ROOT,
        env=env,
        stdout=server_log,
        stderr=subprocess.STDOUT,
    )
    url = f"http://127.0.0.1:{port}"
    deadline = time.time() + 40
    while time.time() < deadline:
        if process.poll() is not None:
            server_log.close()
            output = (database.parent / "server.log").read_text(errors="replace")
            raise RuntimeError(f"server exited before becoming ready:\n{output}")
        try:
            with urllib.request.urlopen(f"{url}/api/health", timeout=1) as response:
                if response.status == 200:
                    break
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            time.sleep(0.2)
    else:
        process.terminate()
        raise RuntimeError("server did not become ready within 40 seconds")

    yield url

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
    server_log.close()


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture()
def page(browser, base_url):
    context = browser.new_context(base_url=base_url, viewport={"width": 1440, "height": 900})
    page = context.new_page()
    page.goto("/")
    yield page
    context.close()
