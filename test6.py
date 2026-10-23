#Managing State Across Multiple Pages
import re
from urllib.parse import quote_plus

from playwright.sync_api import Page, expect


def normalize_text(value):
    return " ".join(value.split()).casefold()


def test_product_state_across_pages(page: Page):

    # Step 1: Open Amazon and search for mobile phones
    page.goto(
        "https://www.amazon.in/",
        wait_until="domcontentloaded")

    search_keyword = "mobile phones"

    search_box = page.locator("#twotabsearchtextbox")
    expect(search_box).to_be_visible(timeout=20000)

    search_box.fill(search_keyword)
    search_box.press("Enter")

    # Step 2: Store the product title and ASIN from search results
    product_cards = page.locator('div[data-component-type="s-search-result"][data-asin]')

    expect(product_cards.first).to_be_visible(timeout=20000)

    mobile_keywords = [
        "iphone", "samsung", "galaxy", "redmi",
        "oneplus", "realme", "vivo", "oppo",
        "motorola", "smartphone", "mobile phone",
        "poco", "nothing phone", "pixel"]

    stored_title = ""
    stored_product_id = ""

    for i in range(product_cards.count()):
        card = product_cards.nth(i)

        product_id = card.get_attribute("data-asin")
        title_locator = card.locator("h2").first

        if not product_id or not re.fullmatch(r"[A-Z0-9]{10}", product_id, re.IGNORECASE):
            continue

        if title_locator.count() == 0:
            continue

        if not title_locator.is_visible():
            continue

        title = " ".join(title_locator.inner_text().split())

        if any(
            keyword in title.casefold()
            for keyword in mobile_keywords):
            stored_title = title
            stored_product_id = product_id.upper()
            break

    assert stored_title, "No mobile phone was found."
    assert stored_product_id, "Product ASIN was not captured."

    print("Search keyword:", search_keyword)
    print("Stored product title:", stored_title)
    print("Stored product ASIN:", stored_product_id)

    # Step 3: Open the selected product details page
    product_url = (f"https://www.amazon.in/dp/{stored_product_id}")

    page.goto(product_url, wait_until="domcontentloaded")

    detail_title = page.locator("span#productTitle")
    expect(detail_title).to_be_visible(timeout=20000)

    actual_title = " ".join(detail_title.inner_text().split())

    # Verify the product title
    assert (normalize_text(stored_title) in normalize_text(actual_title) or normalize_text(actual_title) in normalize_text(stored_title)),("Product title mismatch!\n" f"Stored title: {stored_title}\n" f"Actual title: {actual_title}")

    # Verify the product ASIN in the current URL
    current_id_match = re.search(r"/dp/([A-Z0-9]{10})",page.url,re.IGNORECASE)

    assert current_id_match is not None, ("Product ASIN was not found in the details URL.")

    current_product_id = current_id_match.group(1).upper()

    assert current_product_id == stored_product_id, ("Product ASIN mismatch!\n"
        f"Expected: {stored_product_id}\n"
        f"Actual: {current_product_id}")

    print("PASS: Product title and ASIN verified.")

    # Step 4: Add the same product to the cart
    # Confirm the page still displays the selected product
    expect(detail_title).to_be_visible(timeout=10000)

    current_title_before_cart = " ".join(detail_title.inner_text().split())

    assert (
        normalize_text(stored_title)
        in normalize_text(current_title_before_cart)
        or normalize_text(current_title_before_cart)
        in normalize_text(stored_title)
    ), "The selected product changed before adding to cart."

    add_to_cart = page.get_by_role("button",name=re.compile(r"^Add to cart$", re.IGNORECASE)).first

    expect(add_to_cart).to_be_visible(timeout=15000)
    expect(add_to_cart).to_be_enabled(timeout=10000)

    add_to_cart.click()

    print("PASS: Add to Cart clicked.")

    # Step 5: Open the cart and verify the product
    cart_link = page.locator("#nav-cart")
    expect(cart_link).to_be_visible(timeout=15000)

    cart_link.click()

    expect(page).to_have_url(re.compile(r"/cart"),timeout=20000)

    cart_items = page.locator("div.sc-list-item")
    expect(cart_items.first).to_be_visible(timeout=20000)

    matching_cart_item = False

    for i in range(cart_items.count()):
        item = cart_items.nth(i)
        item_text = " ".join(item.inner_text().split())

        if (normalize_text(stored_title) in normalize_text(item_text)
            or normalize_text(actual_title) in normalize_text(item_text)):
            matching_cart_item = True
            print("Cart item found:", item_text)
            break

    assert matching_cart_item, ("The selected product was not found in the cart.\n"f"Product: {stored_title}\n"f"ASIN: {stored_product_id}")

    print("PASS: Same product found in the cart.")

    # Step 6: Return to search results
    search_url = ("https://www.amazon.in/s?k=" + quote_plus(search_keyword))

    page.goto(search_url, wait_until="domcontentloaded")

    restored_search_box = page.locator("#twotabsearchtextbox")

    expect(restored_search_box).to_be_visible(timeout=15000)

    restored_keyword = restored_search_box.input_value()

    assert normalize_text(restored_keyword) == normalize_text(search_keyword), ("Search keyword was not retained.\n"
        f"Expected: {search_keyword}\n"
        f"Actual: {restored_keyword}")

    # Verify the original product is still in the search results
    restored_product = page.locator('div[data-component-type="s-search-result"]'f'[data-asin="{stored_product_id}"]').first

    expect(restored_product).to_be_visible(timeout=20000)

    print("PASS: Search keyword retained:", restored_keyword)
    print("PASS: Original product found in search results.")
   
