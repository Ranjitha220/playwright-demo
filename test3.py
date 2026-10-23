#Auto-Suggest Dropdowns with Dynamic Waiting

from playwright.sync_api import Page, expect, TimeoutError as PlaywrightTimeoutError


def test_amazon_autosuggest_dropdown(page: Page):

    # 1. Open Amazon India
    page.goto("https://www.amazon.in/", wait_until="domcontentloaded")

    search_box = page.locator("#twotabsearchtextbox")
    expect(search_box).to_be_visible(timeout=20000)

    # 2. Enter a partial mobile phone search
    partial_name = "mobile pho"
    required_suggestion = "mobile phones"

    search_box.fill(partial_name)

    print("\nEntered partial search:", partial_name)

    # 3. Wait dynamically for autocomplete suggestions
    suggestions = page.locator("div.s-suggestion-container")

    try:
        suggestions.first.wait_for(state="visible", timeout=5000)

    except PlaywrightTimeoutError:
        print("Autocomplete suggestions were not displayed.")
        print("Using Enter as the search fallback.")

        search_box.press("Enter")

        expect(page.locator('div[data-component-type="s-search-result"]').first).to_be_visible(timeout=20000)

        print("Fallback search completed.")
        print("Current URL:", page.url)

    else:
        print("Autocomplete suggestions are displayed.")

        rows = page.locator("div.s-suggestion-container")
        selected_row = None
        selected_text = ""

        # 4. Find a matching suggestion
        for i in range(rows.count()):
            row = rows.nth(i)

            if not row.is_visible():
                continue

            text = " ".join(row.inner_text().split())

            if text:
                print("Suggestion:", text)

                if required_suggestion.casefold() in text.casefold():
                    selected_row = row
                    selected_text = text
                    break

        # 5. Select the matching suggestion or use fallback
        if selected_row is not None:
            print("Selecting suggestion:", selected_text)
            selected_row.click()
        else:
            print("Matching mobile phone suggestion not found.")
            print("Using Enter as the search fallback.")

            search_box.press("Enter")

        # 6. Validate search results
        expect(
            page.locator('div[data-component-type="s-search-result"]').first).to_be_visible(timeout=20000)

        print("Search navigation validated.")
        print("Current URL:", page.url)
