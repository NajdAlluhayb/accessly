"""Run inside the image: python container_smoke.py. Makes no model/email calls."""
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from strands import Agent
from strands_tools.browser import LocalChromiumBrowser
from playwright.sync_api import sync_playwright

with tempfile.TemporaryDirectory() as directory:
    env = dict(os.environ, ACCESSLY_PUBLIC_MODE="1", ACCESSLY_DATA_DIR=directory,
               ACCESSLY_ALLOWED_ORIGINS="https://frontend.example.invalid",
               ACCESSLY_TEST_RECIPIENT="test@example.invalid", PYTHON_DOTENV_DISABLED="1")
    port = os.getenv("SMOKE_PORT", "8765")
    process = subprocess.Popen([sys.executable, "-m", "uvicorn", "api:app",
                                "--host", "0.0.0.0", "--port", port], env=env)
    try:
        for attempt in range(60):
            if process.poll() is not None:
                raise RuntimeError("FastAPI exited before becoming healthy")
            try:
                with urllib.request.urlopen("http://127.0.0.1:" + port + "/health", timeout=2) as response:
                    assert json.load(response) == {"status": "ok"}
                break
            except OSError:
                time.sleep(0.5)
        else:
            raise RuntimeError("FastAPI health check timed out")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content("<title>Accessly smoke test</title><h1>Chromium works</h1>")
            assert page.title() == "Accessly smoke test"
            browser.close()
        print("PASS: Strands/browser imports, FastAPI startup, /health, headless Chromium")
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
