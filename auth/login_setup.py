import os
import json
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright


load_dotenv("C:/Users/RANJITHA/Desktop/playwright project/auth/.env.qa")
auth_file = Path("C:/Users/RANJITHA/Desktop/playwright project/auth/session_storage.json")
SESSION_STORAGE_FILE = Path("C:/Users/RANJITH/Desktop/playwright project/auth/session.json")
async def login():
    username = os.getenv("B2B_AGENT_USERNAME")
    password = os.getenv("B2B_AGENT_PASSWORD")
    if not username and not password:
        raise ValueError("un and pwd is missing env file")

#     async with async_playwright() as playwright:
#         browser = await playwright.chromium.launch(headless=False)
#         context = await browser.new_context()
#         page = await context.new_page()
#         if auth_file.exists():
#             await page.goto("https://agents.akbartravelsonline.com/b2bplus/flight")
#             if "login" not in page.url:
#                 print("existing session still valid")
#                 await browser.close()
#                 return
#         print("Logging in to geanrate a session")
#         await page.goto("https://agents.akbartravelsonline.com/b2bplus/login")
#         await page.locator("//input[@name='username']").fill(username)
#         await page.locator("//input[@name='password']").fill(password)
#         await page.get_by_text(" Sign In ").click()

#         await page.locator("//h1[text()='Search Flights']").wait_for(state="visible",timeout=30000)
#         await page.wait_for_load_state("networkidle")
#         await context.storage_state(path=str(auth_file))
#         await page.wait_for_load_state("networkidle")

#         # session explicitly
#         session_data = await page.evaluate("()=>JSON.stringify(window.sessionStorage)")
#         SESSION_STORAGE_FILE.write_text(session_data)
#         print("new session is created")
#         await browser.close()

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(login())
    
import asyncio
import pytest
from pathlib import Path

import pytest_asyncio
from playwright.async_api import async_playwright

from tests.auth.login_setup import login
AUTH_FILE = Path("D:/AI/Python_playwright/tests/auth/loginsession.json")
SESSION_STORAGE_FILE = Path("D:/AI/Python_playwright/tests/auth/session_storage.json")

def pytest_sessionstart(session):
    """Pytest hook running globally BEFORE any test execution begins."""
    print("\n--- Running Global Authentication Setup ---")
    asyncio.run(login())

@pytest.fixture
async def authenticated_page():
    """Fully async fixture providing an authenticated Playwright page."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        # Build context arguments with storage state if available
        context_args = {}
        if AUTH_FILE.exists():
            context_args["storage_state"] = str(AUTH_FILE)

        context = await browser.new_context(**context_args)

        # Re-inject sessionStorage tokens into the browser context
        if SESSION_STORAGE_FILE.exists():
            session_data = SESSION_STORAGE_FILE.read_text()
            await context.add_init_script(f"""
                const data = {session_data};
                for (const [key, val] of Object.entries(data)) {{
                    window.sessionStorage.setItem(key, val);
                }}
            """)

        page = await context.new_page()
        yield page
        await context.close()
        await browser.close()

@pytest_asyncio.fixture
async def async_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        yield page
        await browser.close()
        #python -m pip install pytest_asyncio


#
# @pytest.fixture(scope="session")
# def api_request(playwright: Playwright):
#
#     api = playwright.request.new_context(
#         base_url="https://parabank.parasoft.com",
#         extra_http_headers={
#             "Accept": "application/json"
#         }
#     )
#
#     yield api
#
#     api.dispose()   

#--------------------------------------------------------------
import pytest
@pytest.mark.asyncio
async def test_serach_(authenticated_page):
    await authenticated_page.goto("https://agents.akbartravelsonline.com/b2bplus/flight")
    assert "login" not in await authenticated_page.current_url
    header =  authenticated_page.locator("//h1[text()='Search Flights']")
    await   header.wait_for_load(state = "visible",timeout=5000)
    assert await header.is_visible()
    

