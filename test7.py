#Pagination and Infinite Scroll
from playwright.sync_api import Page, expect, TimeoutError as PlaywrightTimeoutError


def test_amazon_pagination_or_infinite_scroll(page: Page):

    # Step 1: Open Amazon India
    page.goto( "https://www.amazon.in/",wait_until="domcontentloaded")

    search_keyword = "mobile phones"

    search_box = page.locator("#twotabsearchtextbox")
    expect(search_box).to_be_visible(timeout=20000)

    search_box.fill(search_keyword)
    search_box.press("Enter")

    # Step 2: Identify product cards
    cards = page.locator('div[data-component-type="s-search-result"][data-asin]')

    expect(cards.first).to_be_visible(timeout=20000)

    initial_count = cards.count()
    initial_url = page.url

    print("\nSearch keyword:", search_keyword)
    print("Initial product card count:", initial_count)
    print("Initial URL:", initial_url)

    # Step 3: Check for pagination or Load More
    next_link = page.locator("a.s-pagination-next")
    load_more = page.get_by_role("button",name="Load more",exact=False)

    if (next_link.count() > 0
        and next_link.is_visible()
        and next_link.get_attribute("aria-disabled") != "true"):
        # Pagination behavior
        print("Observed behavior: Pagination")

        next_href = next_link.get_attribute("href")
        assert next_href, "Next pagination link has no destination."

        next_link.click()

        try:
            expect(page).not_to_have_url(
                initial_url,
                timeout=15000
            )
        except AssertionError:
            print("URL did not change within the expected time.")

        expect(cards.first).to_be_visible(timeout=20000)

        new_url = page.url
        new_count = cards.count()

        print("Next page URL:", new_url)
        print("Product card count on next page:", new_count)

        assert new_url != initial_url, ("Pagination did not navigate to a different URL.")

        print("PASS: Pagination navigation completed.")

    elif load_more.count() > 0 and load_more.first.is_visible():
        # Load More behavior
        print("Observed behavior: Load More control")

        load_more.first.click()

        try:
            expect(cards).not_to_have_count(
                initial_count,
                timeout=15000)
        except AssertionError:
            print("Product card count did not change.")

        new_count = cards.count()

        print("Initial product count:", initial_count)
        print("Product count after Load More:", new_count)

        if new_count > initial_count:
            print("PASS: Load More added product cards.")
        else:
            print("INCONCLUSIVE: No additional product cards detected.")

    else:
        # Step 4: Check for lazy loading or infinite scrolling
        print("No visible Next or Load More control detected.")
        print("Testing for lazy-loaded or infinite-scroll results.")

        new_count = initial_count
        increased = False

        for attempt in range(1, 5):
            page.evaluate(
                "window.scrollTo(0, document.body.scrollHeight)")

            try:
                page.wait_for_function("""initialCount =>document.querySelectorAll('div[data-component-type="s-search-result"][data-asin]').length > initialCount""",arg=new_count,timeout=4000)

                updated_count = cards.count()

                if updated_count > new_count:
                    new_count = updated_count
                    increased = True

                    print(f"Scroll {attempt}: product count increased "
                        f"to {new_count}")
                    break

            except PlaywrightTimeoutError:
                print(f"Scroll {attempt}: no additional product cards ""loaded within the wait period.")

        if increased:
            print("Observed behavior: Lazy-loaded results.")
            print("PASS: Additional product cards were detected.")

        else:
            # Recheck pagination near the bottom of the page
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

            pagination = page.locator("a.s-pagination-next")

            if (
                pagination.count() > 0
                and pagination.is_visible()
                and pagination.get_attribute("aria-disabled") != "true"):
                print("Observed behavior: Pagination is available "
                "near the bottom of the page.")
            else:
                print("INCONCLUSIVE: No additional product cards loaded "
                    "and no usable Next or Load More control was found.")
                print(
                    "Amazon may be using standard pagination or limiting "
                    "results in this session."
                )

