#UI and API Data Validation

import re
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def mock_product_api():
    # Sample mock API data matching the product being tested
    return {
        "source_endpoint": "mock://trainer-api/products/B0CHX1W1XY",
        "status_code": 200,
        "data": {
            "product_id": "B0CHX1W1XY",
            "title": "Apple iPhone 15 (128 GB) - Black"
        }
    }


def normalize_text(value):
    """Normalize whitespace and case for comparison."""
    return " ".join(value.split()).casefold()


def test_amazon_ui_api_validation(page: Page, mock_product_api):

    api_response = mock_product_api
    api_data = api_response["data"]
    endpoint = api_response["source_endpoint"]

    print("\n========== MOCK API DETAILS ==========")
    print("Source endpoint:", endpoint)
    print("Status code:", api_response["status_code"])
    print("API product ID:", api_data["product_id"])
    print("API product title:", api_data["title"])

    assert api_response["status_code"] == 200

    # Open the Amazon mobile phone page
    product_id = api_data["product_id"]
    product_url = f"https://www.amazon.in/dp/{product_id}"

    page.goto(product_url, wait_until="domcontentloaded")

    # Read the product title displayed on the UI
    ui_title_locator = page.locator("span#productTitle")
    expect(ui_title_locator).to_be_visible(timeout=20000)

    ui_title = " ".join(ui_title_locator.inner_text().split())

    print("\n========== UI DETAILS ==========")
    print("UI product URL:", page.url)
    print("UI product title:", ui_title)

    # Extract the product ID from the URL
    match = re.search(r"/dp/([A-Z0-9]{10})", page.url, re.IGNORECASE)

    assert match is not None, (
        f"Could not extract product ID.\n"
        f"Source endpoint: {endpoint}\n"
        f"UI URL: {page.url}")

    ui_product_id = match.group(1).upper()
    api_product_id = api_data["product_id"].upper()

    # Validate product ID
    assert ui_product_id == api_product_id, (
        f"Product ID mismatch!\n"
        f"Source endpoint: {endpoint}\n"
        f"API product_id: {api_product_id}\n"
        f"UI product_id: {ui_product_id}")

    print("PASS: Product IDs match.")

    # Validate product title
    api_title = normalize_text(api_data["title"])
    normalized_ui_title = normalize_text(ui_title)

    assert api_title == normalized_ui_title, (
        f"Product title mismatch!\n"
        f"Source endpoint: {endpoint}\n"
        f"API field title: '{api_data['title']}'\n"
        f"UI field title: '{ui_title}'")

    print("PASS: Product titles match.")

    # Validation report
    print("\n========== VALIDATION SUMMARY ==========")
    print("Source endpoint:", endpoint)
    print("Fields validated: product_id, title")
    print("Result: All validations passed.")
