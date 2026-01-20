import os

import pytest
from dotenv import load_dotenv

from pages.login_page import LoginPage

load_dotenv()

pytestmark = pytest.mark.asyncio

WEBSITE_URL = os.getenv("WEBSITE_URL", "https://dev-app.helpconstruct.com")
TEST_EMAIL = os.getenv("TEST_EMAIL")
TEST_PASSWORD = os.getenv("TEST_PASSWORD")


@pytest.fixture
def login_page(page):
    return LoginPage(page, base_url=WEBSITE_URL)


class TestLoginFlow:
    async def test_login_page_loads(self, login_page):
        await login_page.go_to_login_page()
        assert await login_page.is_login_page_displayed(), "Login page should be visible"

    async def test_type_email(self, login_page, page):
        await login_page.go_to_login_page()
        sample_email = "test@example.com"
        await login_page.type_email(sample_email)
        assert await login_page.email_input.input_value() == sample_email

    async def test_type_password(self, login_page, page):
        await login_page.go_to_login_page()
        sample_password = "TestPassword123"
        await login_page.type_password(sample_password)
        assert await login_page.password_input.input_value() == sample_password

    async def test_login_button_exists(self, login_page, page):
        await login_page.go_to_login_page()
        await login_page.login_button.wait_for(state="visible", timeout=10000)
        assert True

    async def test_login_with_valid_credentials(self, login_page, page):
        if not TEST_EMAIL or not TEST_PASSWORD:
            pytest.skip("TEST_EMAIL and TEST_PASSWORD must be set in .env")

        await login_page.go_to_login_page()
        await login_page.login(TEST_EMAIL, TEST_PASSWORD)
        await page.wait_for_load_state("networkidle", timeout=15000)
        await page.wait_for_function(
            "location.href.toLowerCase().includes('login') === false",
            timeout=30000,
        )
        current_url = page.url
        assert "login" not in current_url.lower(), f"Should not stay on login page, current URL: {current_url}"
