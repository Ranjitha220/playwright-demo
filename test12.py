
import re
import pytest
from playwright.sync_api import expect

BASE_URL = "https://demowebshop.tricentis.com"


def test_product_search(page):
    """Search for a product and verify results."""
    page.goto(BASE_URL)

    search_box = page.locator("#small-searchterms")
    search_box.fill("book")
    search_box.press("Enter")

    page.wait_for_url("**/search**", timeout=15000)

    products = page.locator(".product-item")
    expect(products.first).to_be_visible(timeout=15000)

    print(f"Product results found: {products.count()}")


def test_select_product_and_validate_cart(page):
    """Select a product dynamically and validate the cart."""
    page.goto(BASE_URL)

    search_box = page.locator("#small-searchterms")
    search_box.fill("book")
    search_box.press("Enter")

    products = page.locator(".product-item")
    expect(products.first).to_be_visible(timeout=15000)

    matching_card = None

    for index in range(products.count()):
        card = products.nth(index)
        title = card.locator("h2 a")

        if title.count() > 0:
            product_name = title.inner_text().strip()

            if "book" in product_name.lower():
                matching_card = card
                break

    if matching_card is None:
        pytest.skip("No product matching 'book' was found.")

    product_name = matching_card.locator("h2 a").inner_text().strip()

    add_button = matching_card.locator(
        "input.button-2.product-box-add-to-cart-button"
    )

    if add_button.count() == 0:
        pytest.skip(f"Add-to-cart control missing for {product_name}.")

    if not add_button.is_visible() or not add_button.is_enabled():
        pytest.skip(f"Product unavailable: {product_name}.")

    add_button.click()

    cart_quantity = page.locator(".cart-qty")

    # Wait until the cart quantity becomes positive.
    expect(cart_quantity).to_have_text(
        re.compile(r"\(([1-9]\d*)\)"),
        timeout=15000
    )

    print(f"Cart validation passed for: {product_name}")


def test_reuse_saved_session(page, browser, auth_state_path):
    """Load saved authentication into a fresh browser context."""

    if not auth_state_path.is_file():
        pytest.skip(
            "Saved session missing. Run save_session.py "
            "and sign in first."
        )

    # Use the browser fixture; do not start sync_playwright() again.
    context = browser.new_context(
        storage_state=str(auth_state_path)
    )

    try:
        authenticated_page = context.new_page()
        authenticated_page.goto(f"{BASE_URL}/customer/info")

        logout_link = authenticated_page.get_by_role(
            "link", name="Log out", exact=True
        )

        if not logout_link.is_visible():
            pytest.fail(
                "Saved session is expired or invalid. "
                "Run save_session.py and sign in again."
            )

        expect(logout_link).to_be_visible()

        print("Saved session successfully reused.")

    finally:
        context.close()