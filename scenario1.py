
import os
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, expect

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# .env is in the Automation root folder
ENV_FILE = PROJECT_ROOT / ".env"

# Save the authentication state inside Assigment5
AUTH_DIR = SCRIPT_DIR / "auth"
STATE_FILE = AUTH_DIR / "webshop_state.json"

def main():
    # Load credentials from the project-root .env file.
    if not ENV_FILE.is_file():
        raise FileNotFoundError(f".env file not found: {ENV_FILE}")

    load_dotenv(ENV_FILE)
    base_url = os.getenv(
    "BASE_URL",
    "https://demowebshop.tricentis.com"
    ).rstrip("/")

    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")

    if not email or not password:
        raise ValueError(
            "TEST_EMAIL or TEST_PASSWORD is missing from the .env file."
        )

    AUTH_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto(f"{base_url}/login", wait_until="domcontentloaded")

            page.locator("#Email").fill(email)
            page.locator("#Password").fill(password)
            page.locator("input.login-button").click()

            # Confirm that login succeeded before saving state.
            logout_link = page.get_by_role(
                "link", name="Log out", exact=True
            )
            expect(logout_link).to_be_visible(timeout=15000)

            # Save cookies and browser storage.
            context.storage_state(path=str(STATE_FILE))

            print("Login successful!")
            print(f"Authentication state saved to: {STATE_FILE}")

        finally:
            browser.close()


if __name__ == "__main__":
    main()