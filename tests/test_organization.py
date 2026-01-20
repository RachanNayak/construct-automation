import os

import pytest
from dotenv import load_dotenv

from pages.login_page import LoginPage
from pages.org_page import OrgPage

load_dotenv()

pytestmark = pytest.mark.asyncio

WEBSITE_URL = os.getenv("WEBSITE_URL", "https://dev-app.helpconstruct.com")
TEST_EMAIL = os.getenv("TEST_EMAIL")
TEST_PASSWORD = os.getenv("TEST_PASSWORD")


class TestOrganizationFlow:
    async def test_create_org(self, page):
        if not TEST_EMAIL or not TEST_PASSWORD:
            pytest.skip("TEST_EMAIL and TEST_PASSWORD must be set in .env")

        login_page = LoginPage(page, base_url=WEBSITE_URL)
        org_page = OrgPage(page)

        await login_page.go_to_login_page()
        await login_page.login(TEST_EMAIL, TEST_PASSWORD)
        await page.wait_for_load_state("networkidle", timeout=15000)
        await page.wait_for_function(
            "location.href.toLowerCase().includes('login') === false",
            timeout=30000,
        )

        company_name = os.getenv("COMPANY_NAME", "RRR Vendor")
        await org_page.complete_flow_from_current_url(
            org_name=company_name,
            address_prefix="123",
            ownership="Sole Proprietorship",
            phone="9876543210",
            email="rrr.vendor@example.com",
            website="https://rrrvendor.example.com",
            ceo_name="Alex CEO",
            employees="120",
        )

        assert await org_page.is_hello_page_displayed(), "Hello page should be visible after setup"
