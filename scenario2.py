from pathlib import Path
import re
import pytest
from playwright.sync_api import expect, Error as PlaywrightError

# Get the directory containing scene2.py
PROJECT_DIR = Path(__file__).resolve().parent

# Authentication state saved by scene1.py
STATE_FILE = PROJECT_DIR / "auth" / "webshop_state.json"

BASE_URL = "https://demowebshop.tricentis.com"
BOOK_SEARCH = "Computing and Internet"


def test_reuse_session_and_add_book(browser):
    # A missing state file is a test failure, not a skip.
    if not STATE_FILE.is_file():
        pytest.fail(
            f"Authentication state file is missing: {STATE_FILE}\n"
            "Run save_webshop_state.py successfully before this test."
        )

    try:
        context = browser.new_context(
            storage_state=str(STATE_FILE)
        )
    except (PlaywrightError, ValueError, OSError) as error:
        pytest.fail(
            f"Could not load authentication state from {STATE_FILE}. "
            f"The file may be invalid or corrupted. Details: {error}"
        )

    try:
        page = context.new_page()

        # Step 1: Verify the saved session before shopping.
        page.goto(f"{BASE_URL}/customer/info")

        logout_link = page.get_by_role(
            "link", name="Log out", exact=True
        )

        expect(logout_link).to_be_visible(timeout=15000)
        print("PASS: Authentication persisted in a fresh context.")

        # Step 2: Navigate to Books without logging in again.
        page.goto(f"{BASE_URL}/books")
        expect(page.locator("#small-searchterms")).to_be_visible()

        # Step 3: Search for a specific book.
        search_box = page.locator("#small-searchterms")
        search_box.fill(BOOK_SEARCH)
        search_box.press("Enter")

        expect(page.locator(".product-item").first).to_be_visible(
            timeout=15000
        )

        # Step 4: Select the matching product by its title.
        products = page.locator(".product-item")
        matching_card = None

        for index in range(products.count()):
            card = products.nth(index)
            title_link = card.locator("h2 a")

            if title_link.count() > 0:
                title = title_link.inner_text().strip()

                if BOOK_SEARCH.lower() in title.lower():
                    matching_card = card
                    break

        if matching_card is None:
            pytest.fail(
                f"Book '{BOOK_SEARCH}' was not found in the search results."
            )

        product_title = matching_card.locator("h2 a").inner_text().strip()
        matching_card.locator("h2 a").click()

        # Step 5: Verify the product page and add the book.
        expect(page.locator(".product-name")).to_contain_text(
            product_title, timeout=10000
        )

        add_button = page.locator(
            "input.button-1.add-to-cart-button"
        )

        expect(add_button).to_be_visible(timeout=10000)
        expect(add_button).to_be_enabled()
        add_button.click()

        # Step 6: Verify that the cart quantity is positive.
        cart_quantity = page.locator(".cart-qty")

        expect(cart_quantity).to_have_text(
            re.compile(r"\(([1-9]\d*)\)"),
            timeout=15000
        )

        print(f"PASS: Added '{product_title}' to the cart.")
        print("Cart quantity:", cart_quantity.inner_text())

    finally:
        context.close()