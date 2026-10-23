#Multi-Step Forms and Data Persistence
from playwright.sync_api import Page, expect


def test_multistep_form_data_persistence(page: Page):

    page.set_content("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mock Checkout Form</title>
        </head>
        <body>
            <h2>Mock Checkout - Step 1: Delivery Details</h2>

            <form id="deliveryForm">
                <label for="fullName">Test Name:</label>
                <input id="fullName" name="fullName" />

                <br><br>

                <label for="city">Test City:</label>
                <input id="city" name="city" />

                <br><br>

                <button type="button" id="nextStep">
                    Continue to Review
                </button>
            </form>

            <section id="reviewStep" hidden>
                <h2>Step 2: Review Details</h2>

                <p>Name: <span id="reviewName"></span></p>
                <p>City: <span id="reviewCity"></span></p>

                <button type="button" id="backStep">
                    Back to Delivery Details
                </button>
            </section>

            <script>
                const nameInput = document.getElementById("fullName");
                const cityInput = document.getElementById("city");
                const deliveryForm = document.getElementById("deliveryForm");
                const reviewStep = document.getElementById("reviewStep");

                document.getElementById("nextStep").addEventListener(
                    "click", () => {
                        document.getElementById("reviewName").textContent =
                            nameInput.value;
                        document.getElementById("reviewCity").textContent =
                            cityInput.value;

                        deliveryForm.hidden = true;
                        reviewStep.hidden = false;
                    }
                );

                document.getElementById("backStep").addEventListener(
                    "click", () => {
                        reviewStep.hidden = true;
                        deliveryForm.hidden = false;
                    }
                );
            </script>
        </body>
        </html>
    """)

    full_name = "Test User"
    city = "Test City"

    name_input = page.locator("#fullName")
    city_input = page.locator("#city")

    expect(name_input).to_be_visible()
    expect(city_input).to_be_visible()

    name_input.fill(full_name)
    city_input.fill(city)

    print("\nStep 1: Sample test data entered.")

    page.locator("#nextStep").click()

    review_step = page.locator("#reviewStep")
    expect(review_step).to_be_visible()

    expect(page.locator("#reviewName")).to_have_text(full_name)
    expect(page.locator("#reviewCity")).to_have_text(city)

    print("Step 2: Review details validated.")

    page.locator("#backStep").click()

    expect(page.locator("#deliveryForm")).to_be_visible()

    expect(name_input).to_have_value(full_name)
    expect(city_input).to_have_value(city)

    print("PASS: Name persisted after backward navigation.")
    print("PASS: City persisted after backward navigation.")

    page.locator("#nextStep").click()

    expect(review_step).to_be_visible()
    expect(page.locator("#reviewName")).to_have_text(full_name)
    expect(page.locator("#reviewCity")).to_have_text(city)

    print("PASS: Data persisted after forward navigation.")
   