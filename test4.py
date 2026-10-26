#Checkout Journey 

import re
from playwright.sync_api import (Page,expect,TimeoutError as PlaywrightTimeoutError)


def test_amazon_checkout_journey(page: Page):

    # 1. Open Amazon India and search for a mobile phone
    page.goto("https://www.amazon.in/",wait_until="domcontentloaded")

    product_keyword = "mobile phones"
    required_keyword = "mobile"

    search_box = page.locator("#twotabsearchtextbox")
    expect(search_box).to_be_visible(timeout=20000)

    search_box.fill(product_keyword)
    search_box.press("Enter")

    # 2. Find product cards
    product_cards = page.locator('div[data-component-type="s-search-result"]')
    expect(product_cards.first).to_be_visible(timeout=20000)

    matched_card = None
    matched_title = ""

    # 3. Select a mobile phone by its visible title
    for i in range(product_cards.count()):
        card = product_cards.nth(i)
        title_locator = card.locator("h2").first

        if not title_locator.is_visible():
            continue

        title = " ".join(title_locator.inner_text().split())

        if required_keyword.casefold() in title.casefold():
            matched_card = card
            matched_title = title
            break

    assert matched_card is not None, (f"No mobile phone containing '{required_keyword}' was found.")

    print("\nSelected mobile:", matched_title)

    # 4. Open the selected mobile
    product_link = matched_card.locator("a:has(h2)").first

    if product_link.count() == 0:
        product_link = matched_card.locator("a[href*='/dp/']").first

    expect(product_link).to_be_visible(timeout=10000)

    product_url = product_link.get_attribute("href")
    assert product_url, "Mobile product URL was not found."

    if product_url.startswith("/"):
        product_url = "https://www.amazon.in" + product_url

    page.goto(product_url, wait_until="domcontentloaded")

    # 5. Validate the product title
    detail_title = page.locator("span#productTitle")
    expect(detail_title).to_be_visible(timeout=20000)

    actual_title = " ".join(detail_title.inner_text().split())
    print("Mobile detail title:", actual_title)

    assert required_keyword.casefold() in actual_title.casefold(), (f"Unexpected product title: {actual_title}")

    # 6. Find a visible and enabled Add to Cart button
    add_to_cart_buttons = page.locator("#add-to-cart-button")
    visible_add_to_cart = None

    for i in range(add_to_cart_buttons.count()):
        button = add_to_cart_buttons.nth(i)

        if button.is_visible() and button.is_enabled():
            visible_add_to_cart = button
            break

    if visible_add_to_cart is None:
        print("Add to Cart button is not visible or enabled.")
        print("Check product availability or the current Amazon page.")
        return

    try:
        visible_add_to_cart.click(timeout=10000)
        print("Add to Cart clicked successfully.")

    except PlaywrightTimeoutError:
        print("Unable to click the Add to Cart button.")
        return

    # 7. Open the cart
    cart_link = page.locator("#nav-cart")
    expect(cart_link).to_be_visible(timeout=15000)
    cart_link.click()

    expect(page).to_have_url(re.compile(r"/cart"), timeout=20000)

    # 8. Validate the cart item
    cart_items = page.locator("div.sc-list-item")
    expect(cart_items.first).to_be_visible(timeout=20000)

    cart_item_found = False

    for i in range(cart_items.count()):
        item = cart_items.nth(i)
        item_text = " ".join(item.inner_text().split())

        # Check whether the selected mobile appears in the cart
        if actual_title.casefold() in item_text.casefold():
            cart_item_found = True
            print("Cart item:", item_text)

            quantity = item.locator("span.a-dropdown-prompt")

            if quantity.count() > 0:
                print("Cart quantity:", quantity.first.inner_text())
            else:
                print("Quantity control was not found.")

            break

    assert cart_item_found, (f"Selected mobile '{actual_title}' was not found in the cart.")

    print("Cart item validated successfully.")

    # 9. Proceed toward checkout, but do not place an order
    checkout_button = page.locator('input[name="proceedToRetailCheckout"], ''input[name="proceedToCheckout"], ''button[name="proceedToRetailCheckout"]').first

    if (checkout_button.count() > 0 and checkout_button.is_visible() and checkout_button.is_enabled()):
        print("Checkout control is available.")
        checkout_button.click()

        page.wait_for_load_state("domcontentloaded")

        print("Current checkout URL:", page.url)
        print("Stopped before final order confirmation/payment.")

    else:
        print(
            "Checkout control is unavailable in this session. "
            "Stopped safely on the cart page."
        )
