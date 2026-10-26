#Dynamic Product Selection with Robust Locators
from playwright.sync_api import Page, expect


def test_dynamic_product_selection(page: Page):

    page.goto("https://www.amazon.in/", wait_until="domcontentloaded")

    keyword = "mobile phones"
    required_keyword = "mobile"

    # 1. Search for mobile phones
    search_box = page.locator("#twotabsearchtextbox")
    expect(search_box).to_be_visible(timeout=20000)

    search_box.fill(keyword)
    search_box.press("Enter")

    # 2. Find all product cards
    cards = page.locator('div[data-component-type="s-search-result"]')

    expect(cards.first).to_be_visible(timeout=20000)

    print("\nTotal product cards:", cards.count())

    matched_card = None
    matched_title = ""

    # 3. Match a product using its visible title
    for i in range(cards.count()):
        card = cards.nth(i)
        title_locator = card.locator("h2").first

        if not title_locator.is_visible():
            continue

        title = " ".join(title_locator.inner_text().split())

        if not title:
            continue

        print("Available product:", title)

        if required_keyword.casefold() in title.casefold():
            matched_card = card
            matched_title = title
            break

    # 4. Fail clearly if no matching product is found
    assert matched_card is not None, (f"No product containing '{required_keyword}' "f"was found for search '{keyword}'.")

    print("Matched product:", matched_title)

    # 5. Find the product link only within the matched card
    product_link = matched_card.locator("a:has(h2)").first

    if product_link.count() == 0:
        product_link = matched_card.locator("a[href*='/dp/']").first

    assert product_link.count() > 0, (f"No product link found for: {matched_title}")

    product_url = product_link.get_attribute("href")
    assert product_url, "Product URL was not found."

    if product_url.startswith("/"):
        product_url = "https://www.amazon.in" + product_url

    print("Product URL:", product_url)

    # 6. Open the selected product
    page.goto(product_url, wait_until="domcontentloaded")

    # 7. Validate the product detail title
    detail_title = page.locator("span#productTitle")
    expect(detail_title).to_be_visible(timeout=30000)

    actual_title = " ".join(detail_title.inner_text().split())

    print("Detail page title:", actual_title)

    assert (matched_title.casefold() in actual_title.casefold()
        or actual_title.casefold() in matched_title.casefold())
    (
        f"Product title mismatch!\n"
        f"Search result: {matched_title}\n"
        f"Detail page: {actual_title}"
    )

    print("Final URL:", page.url)
    print("Dynamic product selection: PASSED")
