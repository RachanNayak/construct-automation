import re


class LoginPage:
    def __init__(self, page, base_url):
        self.page = page
        self.base_url = base_url
        self.email_input = page.get_by_placeholder("Enter your email")
        self.password_input = page.get_by_placeholder("Enter your password")
        self.login_button = page.get_by_role("button", name=re.compile(r"login|sign\s*in", re.I))
        self.login_heading = page.get_by_role("heading", name=re.compile(r"login", re.I))

    async def go_to_login_page(self):
        await self.page.goto(self.base_url)

    async def type_email(self, email):
        await self.email_input.wait_for(state="visible", timeout=5000)
        await self.email_input.fill(email)

    async def type_password(self, password):
        await self.password_input.wait_for(state="visible", timeout=5000)
        await self.password_input.fill(password)

    async def click_login_button(self):
        await self.login_button.wait_for(state="visible", timeout=5000)
        await self.login_button.click()

    async def is_login_page_displayed(self):
        return await self.login_heading.is_visible()

    async def login(self, email, password):
        await self.type_email(email)
        await self.type_password(password)
        await self.click_login_button()
        await self.page.wait_for_load_state("networkidle", timeout=10000)
