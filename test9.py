#Conditional Execution Based on UI State

import re
import pytest
from playwright.sync_api import Page, expect


def test_conditional_add_to_cart(page: Page):

    # Step 1: Open Amazon India
    page.goto("https://www.amazon.in/",wait_until="domcontentloaded")

    search_keyword = "mobile phones"

    search_box = page.locator("#twotabsearchtextbox")
    expect(search_box).to_be_visible(timeout=20000)

    search_box.fill(search_keyword)
    search_box.press("Enter")

    # Step 2: Find a mobile phone
    cards = page.locator('div[data-component-type="s-search-result"][data-asin]')

    expect(cards.first).to_be_visible(timeout=20000)

    matched_card = None
    matched_title = ""

    mobile_keywords = ["mobile", "smartphone", "iphone", "samsung",
        "galaxy", "redmi", "oneplus", "realme",
        "vivo", "oppo", "motorola", "poco", "pixel"]

    for i in range(cards.count()):
        card = cards.nth(i)
        title_locator = card.locator("h2").first

        if title_locator.count() == 0:
            continue

        if not title_locator.is_visible():
            continue

        title = " ".join(title_locator.inner_text().split())

        if any(keyword in title.casefold()
            for keyword in mobile_keywords):
            matched_card = card
            matched_title = title
            break

    assert matched_card is not None, ("No mobile phone was found in the search results.")

    print("Selected product:", matched_title)

    # Step 3: Open the product details page
    product_link = matched_card.locator("a:has(h2)").first

    if product_link.count() == 0:
        product_link = matched_card.locator("a[href*='/dp/']").first

    expect(product_link).to_be_visible(timeout=10000)

    product_href = product_link.get_attribute("href")
    assert product_href, "Product detail URL was not found."

    if product_href.startswith("/"):
        product_href = "https://www.amazon.in" + product_href

    page.goto(product_href, wait_until="domcontentloaded")

    title_locator = page.locator("span#productTitle")
    expect(title_locator).to_be_visible(timeout=20000)

    product_title = " ".join(title_locator.inner_text().split())

    print("Product detail title:", product_title)
    print("Product URL:", page.url)

    # Step 4: Check product availability
    availability = page.locator("#availability")
    availability_text = ""

    if availability.count() > 0 and availability.first.is_visible():
        availability_text = " ".join(availability.first.inner_text().split())

    print("Availability message:",
        availability_text or "Not displayed")

    unavailable_words = (
        "currently unavailable",
        "out of stock",
        "temporarily out of stock")

    availability_indicates_unavailable = any(word in availability_text.casefold()
        for word in unavailable_words)

    # Step 5: Locate the Add to Cart button
    add_to_cart = page.locator("#add-to-cart-button").first

    control_visible = (add_to_cart.count() > 0
        and add_to_cart.is_visible())

    if not control_visible:
        add_to_cart = page.get_by_role("button",name=re.compile(r"add to cart", re.IGNORECASE)).first

        control_visible = (add_to_cart.count() > 0
            and add_to_cart.is_visible())

    control_enabled = (control_visible and add_to_cart.is_enabled())

    print("Add to Cart visible:", control_visible)
    print("Add to Cart enabled:", control_enabled)

    # Step 6: Decide whether to skip or continue
    if availability_indicates_unavailable:
        reason = ("The availability message indicates the product "
            f"is unavailable: {availability_text}")

    elif not control_visible:
        reason = ("The Add to Cart button could not be found or is not "
            "visible. The product may still be in stock.")

    elif not control_enabled:
        reason = "The Add to Cart button is disabled."

    else:
        reason = ""

    if reason:
        print("\nCART VALIDATION SKIPPED")
        print("Product:", product_title)
        print("Reason:", reason)

        pytest.skip(f"Cart validation skipped for '{product_title}'. {reason}")

    # Step 7: Add the product to the cart
    expect(add_to_cart).to_be_enabled(timeout=10000)
    add_to_cart.click()

    print("PASS: Add to Cart clicked.")

    # Step 8: Open the cart
    cart_link = page.locator("#nav-cart")
    expect(cart_link).to_be_visible(timeout=15000)

    cart_link.click()

    expect(page).to_have_url(re.compile(r"/cart"),timeout=20000)

    # Step 9: Validate the product in the cart
    cart_items = page.locator("div.sc-list-item")

    expect(cart_items.first).to_be_visible(timeout=20000)

    matching_item_found = False

    for i in range(cart_items.count()):
        item = cart_items.nth(i)

        if not item.is_visible():
            continue

        item_text = " ".join(item.inner_text().split())

        if product_title.casefold() in item_text.casefold():
            matching_item_found = True
            print("PASS: Cart item validated:", item_text)
            break

    assert matching_item_found, (f"Product was added, but '{product_title}' ""was not found in the cart.")

   
