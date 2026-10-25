
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "https://demowebshop.tricentis.com"

PROJECT_DIR = Path(__file__).resolve().parents[2]
AUTH_DIR = PROJECT_DIR / "playwright" / ".auth"
STATE_FILE = AUTH_DIR / "user.json"


def main():
    AUTH_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto(f"{BASE_URL}/login", wait_until="domcontentloaded")

            print("Browser opened. Sign in to DemoWebShop.")
            input("After successful login, return to this terminal ""and press Enter.\n")

            if not browser.is_connected() or page.is_closed():
                print("Browser was closed before the session was saved.")
                return

            logout_link = page.get_by_role("link", name="Log out", exact=True)

            if logout_link.count() == 0 or not logout_link.is_visible():
                print("Login was not detected. Session was not saved.")
                print("Current URL:", page.url)
                print("Please verify that you successfully signed in.")
                return

            context.storage_state(path=str(STATE_FILE))

            print("Login verified successfully.")
            print("Session saved to:", STATE_FILE)

        finally:
            if browser.is_connected():
                browser.close()


if __name__ == "__main__":
    main()
    