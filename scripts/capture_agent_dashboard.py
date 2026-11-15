"""Capture authentic screenshots of the running synthetic-only local dashboard.

Optional dependency: playwright + installed Chromium. No third-party
screenshot service, no production patient data, no persistent browser token.
"""
from __future__ import annotations

import argparse
import os
import secrets
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.request import urlopen


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture real HealthQualify demo UI with synthetic inputs only")
    parser.add_argument("--output-dir", default=".healthqualify/screenshots")
    args = parser.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Install optional Playwright: pip install playwright && python -m playwright install chromium",
              file=sys.stderr)
        return 2

    out = Path(args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    port = free_port()
    token = secrets.token_urlsafe(40)
    addr = f"http://127.0.0.1:{port}"
    with tempfile.TemporaryDirectory(prefix="healthqualify-visual-") as td:
        env = dict(os.environ, HEALTHQUALIFY_AGENT_TOKEN=token)
        proc = subprocess.Popen(
            [sys.executable, "-m", "healthqualify.agent_dashboard",
             "--port", str(port), "--db", str(Path(td) / "agent-history.db"),
             "--protocol", "examples/synthetic_lis_v3/protocol.json",
             "--registry", "examples/agents/dependencies.json",
             "--changed", "healthqualify/healthcare.py"],
            env=env, cwd=str(Path(__file__).resolve().parents[1]),
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        )
        try:
            for _ in range(60):
                if proc.poll() is not None:
                    raise RuntimeError("Dashboard exited before it became available")
                try:
                    with urlopen(addr, timeout=0.5) as response:
                        if response.status == 200:
                            break
                except OSError:
                    time.sleep(.15)
            else:
                raise RuntimeError("Local dashboard failed to start")

            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                try:
                    # Capture actual application content at three screen sizes.
                    for label, width, height in (
                        ("desktop", 1440, 900),
                        ("tablet", 768, 1024),
                        ("mobile", 390, 844),
                    ):
                        page = browser.new_page(viewport={"width": width, "height": height},
                                                device_scale_factor=1)
                        page.goto(addr, wait_until="domcontentloaded")
                        page.locator("#token").fill(token)
                        page.get_by_role("button", name="Load history").click()
                        if label == "desktop":
                            page.get_by_role("button", name="Run all five agents").click()
                            page.wait_for_function(
                                "() => document.querySelector('#result').textContent.includes('qualification_approved')",
                                timeout=30000)
                        page.screenshot(path=str(out / f"agent-dashboard-{label}.png"),
                                        full_page=True, animations="disabled")
                        page.close()
                        print(out / f"agent-dashboard-{label}.png")
                finally:
                    browser.close()
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
    print("Review captures manually for confidential data before committing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
