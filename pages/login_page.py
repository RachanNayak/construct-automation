import os
from dotenv import load_dotenv

load_dotenv()

class LoginPage:
    """
    LoginPage class - This is like a remote control for the login page
    
    It contains:
    - Locators: Where to find elements (email box, password box, login button)
    - Methods: What actions to perform (type email, type password, click login)
    """
    
    def __init__(self, page):
        """
        Initialize - setup the page and element locations
        
        page: This is the browser page/tab we are testing
        """
        self.page = page
        
        # LOCATORS - These are like "addresses" of elements on the page
        self.email_input = 'input[placeholder="Enter your email"]'
        self.password_input = 'input[placeholder="Enter your password"]'
        self.login_button = 'button:has-text("Login")'
        self.login_heading = 'h1:has-text("Login")'
    
    async def go_to_login_page(self):
        """Navigate to the login page"""
        url = os.getenv("WEBSITE_URL")
        print(f"Opening: {url}")
        await self.page.goto(url)
    
    async def type_email(self, email):
        """Type email into the email field"""
        print(f"Typing email: {email}")
        # Wait for the email input to be visible and ready
        await self.page.wait_for_selector(self.email_input, timeout=5000)
        is_visible = await self.page.is_visible(self.email_input)
        print(f"  Email input visible: {is_visible}")
        # Use fill() method which is more reliable
        await self.page.fill(self.email_input, email)
    
    async def type_password(self, password):
        """Type password into the password field"""
        print(f"Typing password")
        # Wait for the password input to be visible and ready
        await self.page.wait_for_selector(self.password_input, timeout=5000)
        is_visible = await self.page.is_visible(self.password_input)
        print(f"  Password input visible: {is_visible}")
        # Use fill() method which is more reliable
        await self.page.fill(self.password_input, password)
    
    async def click_login_button(self):
        """Click the Login button"""
        print("Clicking Login button")
        # Wait for button to be visible and ready
        await self.page.wait_for_selector(self.login_button, timeout=5000)
        is_visible = await self.page.is_visible(self.login_button)
        print(f"  Login button visible: {is_visible}")
        
        # Get button text to verify it's the right button
        button_text = await self.page.text_content(self.login_button)
        print(f"  Button text: {button_text}")
        
        await self.page.click(self.login_button)
    
    async def is_login_page_displayed(self):
        """Check if we are still on the login page"""
        is_visible = await self.page.is_visible(self.login_heading)
        return is_visible
    
    async def login(self, email, password):
        """
        Complete login flow - do all steps together
        
        Steps:
        1. Type email
        2. Type password  
        3. Click login button
        4. Wait for page to load
        """
        await self.type_email(email)
        await self.type_password(password)
        
        # Debug: Check what's in the input fields BEFORE clicking login
        email_value = await self.page.input_value(self.email_input)
        password_value = await self.page.input_value(self.password_input)
        print(f"  [DEBUG] Email field value: {email_value}")
        print(f"  [DEBUG] Password field value: {'*' * len(password_value) if password_value else 'EMPTY'}")
        
        # Check for CAPTCHA or other security elements
        print("\n  [CHECKING FOR SECURITY ELEMENTS]")
        captcha_elements = await self.page.locator('[class*="captcha"], [id*="captcha"], iframe[title*="captcha"]').all()
        print(f"  - CAPTCHA elements found: {len(captcha_elements)}")
        
        recaptcha = await self.page.locator('iframe[src*="recaptcha"]').all()
        print(f"  - reCAPTCHA found: {len(recaptcha)}")
        
        mfa_elements = await self.page.locator('text=/2fa|two.factor|mfa|verification code/i').all()
        print(f"  - MFA/2FA elements found: {len(mfa_elements)}")
        
        otp_elements = await self.page.locator('input[placeholder*="OTP"], input[placeholder*="code"], input[type="tel"]').all()
        print(f"  - OTP/Code input found: {len(otp_elements)}")
        
        print("\n  [SUBMITTING FORM]")
        await self.click_login_button()
        
        # Wait for the page to load after login - use multiple strategies
        print("  - Waiting for page load...")
        try:
            await self.page.wait_for_url("**/welcome", timeout=5000)
            print("  ✓ Redirected to welcome page!")
        except:
            print("  ⚠️  Did not redirect to welcome page")
        
        # Fallback: wait for navigation/load
        await self.page.wait_for_load_state("networkidle", timeout=10000)
        
        # Debug: Check for error messages on page
        error_messages = await self.page.locator("text=/error|invalid|incorrect|unauthorized/i").all()
        if error_messages:
            print(f"⚠️  Found {len(error_messages)} potential error messages on page")
            for i, err in enumerate(error_messages):
                try:
                    text = await err.text_content()
                    print(f"   Error {i+1}: {text[:100]}")
                except:
                    pass
