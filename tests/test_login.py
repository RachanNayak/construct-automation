import pytest
import os
from dotenv import load_dotenv
from pages.login_page import LoginPage

load_dotenv()

class TestLoginFlow:
    """
    Test class for LOGIN functionality
    
    Each method starting with "test_" is a separate test
    """
    
    @pytest.mark.asyncio
    async def test_01_login_page_loads(self, page):
        """
        TEST 1: Check if login page loads
        
        What we do:
        1. Go to website
        2. Check if login page is displayed
        """
        login_page = LoginPage(page)
        await login_page.go_to_login_page()
        
        # Assert - check if login page is shown
        is_displayed = await login_page.is_login_page_displayed()
        assert is_displayed, "Login page should be displayed"
        print("✓ Login page loaded successfully")
    
    @pytest.mark.asyncio
    async def test_02_type_email(self, page):
        """
        TEST 2: Check if email input accepts text
        
        What we do:
        1. Go to login page
        2. Type email
        3. Check if email was entered
        """
        login_page = LoginPage(page)
        await login_page.go_to_login_page()
        
        email = "test@example.com"
        await login_page.type_email(email)
        
        # Get the value in the email field and check it matches
        email_value = await page.input_value(login_page.email_input)
        assert email_value == email, f"Email should be {email} but got {email_value}"
        print("✓ Email input works correctly")
    
    @pytest.mark.asyncio
    async def test_03_type_password(self, page):
        """
        TEST 3: Check if password input accepts text
        """
        login_page = LoginPage(page)
        await login_page.go_to_login_page()
        
        password = "TestPassword123"
        await login_page.type_password(password)
        
        # Check password field has the value
        password_value = await page.input_value(login_page.password_input)
        assert password_value == password, f"Password should be {password} but got {password_value}"
        print("✓ Password input works correctly")
    
    @pytest.mark.asyncio
    async def test_04_login_button_exists(self, page):
        """
        TEST 4: Check if login button is visible
        """
        login_page = LoginPage(page)
        await login_page.go_to_login_page()
        
        # Check if login button is visible
        is_button_visible = await page.is_visible(login_page.login_button)
        assert is_button_visible, "Login button should be visible"
        print("✓ Login button is visible")
    
    @pytest.mark.asyncio
    async def test_05_login_with_valid_credentials(self, page):
        """
        TEST 5: MAIN TEST - Login with real credentials
        
        This is the actual login test!
        We use the credentials from .env file
        """
        login_page = LoginPage(page)
        
        # Get email and password from .env file
        email = os.getenv("TEST_EMAIL")
        password = os.getenv("TEST_PASSWORD")
        
        print(f"\nLogging in with: {email}")
        
        # Go to login page
        await login_page.go_to_login_page()
        
        # Perform login
        await login_page.login(email, password)
        
        # After login, we should NOT be on login page anymore
        # Check if URL changed (we are now on dashboard or home page)
        current_url = page.url
        print(f"After login, URL is: {current_url}")
        
        # Assert that we are no longer on login page
        assert "login" not in current_url.lower(), f"Should not be on login page, but URL is {current_url}"
        print("✓ Login successful! User is now logged in")
