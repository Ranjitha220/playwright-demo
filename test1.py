# End-to-End Product Discovery
from playwright.sync_api import Page, expect


def test_amazon_mobile_discovery(page: Page):

    page.goto("https://www.amazon.in/", wait_until="domcontentloaded")

    keyword = "mobile phones"

    search_box = page.locator("#twotabsearchtextbox")
    expect(search_box).to_be_visible(timeout=20000)

    search_box.fill(keyword)
    search_box.press("Enter")

    results = page.locator('div[data-component-type="s-search-result"]')

    expect(results.first).to_be_visible(timeout=20000)

    selected_title = ""
    selected_url = ""

    for i in range(results.count()):
        result = results.nth(i)

        title_locator = result.locator("h2 span").first

        if not title_locator.is_visible():
            continue

        title = " ".join(title_locator.inner_text().split())

        link_locator = result.locator("a:has(h2)").first

        if title and link_locator.count() > 0:
            href = link_locator.get_attribute("href")

            if href:
                selected_title = title
                selected_url = href
                break

    assert selected_title, "No visible mobile title found"
    assert selected_url, "Mobile product URL not found"

    if selected_url.startswith("/"):
        selected_url = "https://www.amazon.in" + selected_url

    print("\nSelected mobile:", selected_title)
    print("Selected mobile URL:", selected_url)

    page.goto(selected_url, wait_until="domcontentloaded")

    detail_title = page.locator("span#productTitle")
    expect(detail_title).to_be_visible(timeout=20000)

    actual_title = " ".join(detail_title.inner_text().split())

    print("Mobile detail title:", actual_title)

    assert actual_title == selected_title, (
        f"Product title mismatch!\n"
        f"Search result title: {selected_title}\n"
        f"Detail page title: {actual_title}"
    )

    price_locator = page.locator(".apexPriceToPay .a-offscreen").first

    price = "Price not visible"

    if price_locator.count() > 0 and price_locator.is_visible():
        price = price_locator.inner_text().strip()

    print("========== MOBILE DETAILS ==========")
    print("Search keyword:", keyword)
    print("Mobile title:", actual_title)
    print("Price:", price)
    print("Product URL:", page.url)
    print("Title validation: PASSED")
    print("====================================")
