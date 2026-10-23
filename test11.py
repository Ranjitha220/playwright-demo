
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright, expect

BASE_URL = "https://demowebshop.tricentis.com"
STATE_FILE = (
    Path(__file__).resolve().parents[2]
    / "playwright"
    / ".auth"
    / "user.json"
)


def test_reuse_saved_browser_session():
    if not STATE_FILE.is_file():
        pytest.fail(f"Session state not found: {STATE_FILE}\n" "Run save_session.py and sign in first." )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        try:
            context = browser.new_context(storage_state=str(STATE_FILE))
            page = context.new_page()

            page.goto(f"{BASE_URL}/customer/info")

            expect(page.get_by_role("link", name="Log out")).to_be_visible(timeout=15000)

            print("PASS: Saved session is authenticated.")
            print(f"Current URL: {page.url}")

            context.close()

        finally:
            browser.close()