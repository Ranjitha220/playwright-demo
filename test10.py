
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, expect


# Project paths
PROJECT_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_DIR / ".env"

AUTH_DIR = PROJECT_DIR / "playwright" / ".auth"
AUTH_FILE = AUTH_DIR / "user.json"

BASE_URL = "https://demowebshop.tricentis.com"
LOGIN_URL = f"{BASE_URL}/login"


# Load credentials from the .env file
load_dotenv(ENV_FILE)

EMAIL = os.getenv("TEST_EMAIL")
PASSWORD = os.getenv("TEST_PASSWORD")


def test_save_and_reuse_authentication():
    if not EMAIL or not PASSWORD:
        pytest.fail(
            "TEST_EMAIL or TEST_PASSWORD is missing from the .env file."
        )

    AUTH_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        try:
            # Step 1: Create a new browser context
            context = browser.new_context()
            page = context.new_page()

            # Step 2: Open the login page
            page.goto(LOGIN_URL, wait_until="domcontentloaded")

            # Step 3: Enter credentials from .env
            page.get_by_label("Email:").fill(EMAIL)
            page.get_by_label("Password:").fill(PASSWORD)

            page.get_by_role("button", name="Log in").click()

            # Step 4: Verify login
            logout_link = page.get_by_role("link", name="Log out")

            try:
                expect(logout_link).to_be_visible(timeout=15000)
            except AssertionError:
                error_locator = page.locator(
                    ".validation-summary-errors"
                )

                if error_locator.count() > 0:
                    message = error_locator.inner_text()
                else:
                    message = "Login was unsuccessful."

                pytest.fail(f"Authentication failed: {message}")

            expect(page.locator("a.account")).to_be_visible()
            print("Login successful.")

            # Step 5: Save the authenticated state
            context.storage_state(path=str(AUTH_FILE))
            print("Authentication state saved locally.")

            context.close()

            # Step 6: Create a new context using saved state
            restored_context = browser.new_context(
                storage_state=str(AUTH_FILE)
            )
            restored_page = restored_context.new_page()

            # Step 7: Visit the site without logging in again
            restored_page.goto(
                BASE_URL,
                wait_until="domcontentloaded"
            )

            # Step 8: Check whether authentication was restored
            login_link = restored_page.get_by_role(
                "link", name="Log in"
            )
            restored_logout = restored_page.get_by_role(
                "link", name="Log out"
            )

            if login_link.is_visible():
                print(
                    "Session expired or not restored. "
                    "Re-authentication is required."
                )
            else:
                expect(restored_logout).to_be_visible(timeout=10000)
                expect(
                    restored_page.locator("a.account")
                ).to_be_visible()

                print("Authentication restored successfully.")

            restored_context.close()

        finally:
            browser.close()