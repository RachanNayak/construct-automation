import pytest
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
async def browser():
    """Create and provide a browser instance"""
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    yield browser
    await browser.close()
    await playwright.stop()

@pytest.fixture
async def page(browser):
    """Create and provide a fresh page for each test"""
    page = await browser.new_page()
    yield page
    await page.close()
