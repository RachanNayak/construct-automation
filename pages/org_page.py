import uuid

from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError


DEFAULT_WELCOME_URL = "https://dev-app.helpconstruct.com/welcome"


class OrgPage:
    def __init__(self, page: Page, welcome_url: str = DEFAULT_WELCOME_URL):
        self.page = page
        self.welcome_url = welcome_url

        # Welcome
        self.start_button = self.page.get_by_role("button", name="Start")

        # Create organization
        self.org_name_input = self.page.get_by_placeholder("ABC Corp")
        self.create_business_button = self.page.get_by_role("button", name="Create a business")

        # Setup
        self.address_input = self.page.get_by_placeholder("Type to search address...")
        self.phone_input = self.page.get_by_placeholder("9876543210")
        self.email_input = self.page.get_by_placeholder("person@example.com")
        self.website_input = self.page.get_by_placeholder("www.example.com")
        self.ceo_input = self.page.get_by_role("textbox", name="CEO / Business Unit Head")
        # ownership_dropdown will be resolved dynamically in the form method to handle variations
        self.ownership_dropdown = None
        self.employees_input = self.page.get_by_placeholder("e.g. 100")
        self.next_button = self.page.get_by_role("button", name="Next")

    async def click_start_on_welcome(self):
        if "/welcome" not in self.page.url:
            await self.page.goto(self.welcome_url)
        await self.page.wait_for_url("**/welcome", timeout=15000)
        await self.start_button.click()

    async def create_org(self, name: str):
        await self.page.wait_for_url("**/organization/create-organization", timeout=20000)

        async def _attempt(org_name: str) -> bool:
            await self.org_name_input.fill(org_name)
            await self.create_business_button.click()
            await self.page.wait_for_load_state("networkidle", timeout=30000)
            try:
                await self.page.wait_for_function(
                    "location.href.includes('/organization/setup/')",
                    timeout=30000,
                )
                return True
            except PlaywrightTimeoutError:
                return False

        # First try with provided name
        ok = await _attempt(name)
        if not ok:
            # Retry once with a random suffix to avoid "already exists" errors
            suffix = uuid.uuid4().hex[:6].upper()
            fallback_name = f"{name} {suffix}"
            ok = await _attempt(fallback_name)

        if not ok:
            raise PlaywrightTimeoutError("Could not reach setup page after creating org")

        await self.page.wait_for_selector('text=\"Tell Us About Your Business\"', timeout=20000)

    async def fill_setup_form(
        self,
        address_prefix: str,
        ownership: str,
        phone: str,
        email: str,
        website: str,
        ceo_name: str,
        employees: str,
    ):
        # Ensure we are on the setup form by waiting for address input
        await self.address_input.wait_for(state="visible", timeout=20000)

        # Address autocomplete: type first 3 characters, wait for suggestions, pick the first visible suggestion.
        await self.address_input.click()
        address_three = (address_prefix or "")[:3]
        await self.address_input.fill(address_three)

        suggestion_selectors = [
            "role=option",
            "ul[role='listbox'] li",
            "div[role='listbox'] [role='option']",
            ".autocomplete-item",
            ".suggestion-item",
            "li[role='option']",
        ]

        clicked = False
        for sel in suggestion_selectors:
            try:
                locator = self.page.locator(sel).first
                await locator.wait_for(state="visible", timeout=3000)
                await locator.click()
                clicked = True
                break
            except Exception:
                continue

        if not clicked:
            # Fallback: press Enter to accept the typed address
            await self.page.keyboard.press("Enter")

        await self.phone_input.fill(phone)
        await self.email_input.fill(email)
        await self.website_input.fill(website)
        await self.ceo_input.fill(ceo_name)

        # Ownership dropdown selection - resolve locator robustly
        ownership_locators = [
            lambda: self.page.get_by_label("Ownership Type"),
            lambda: self.page.get_by_placeholder("Select an option"),
            lambda: self.page.get_by_role("combobox").first,
        ]
        ownership_locator = None
        for loc_fn in ownership_locators:
            try:
                candidate = loc_fn()
                # check if visible
                await candidate.wait_for(state="visible", timeout=2000)
                ownership_locator = candidate
                break
            except Exception:
                continue
        if ownership_locator is None:
            raise PlaywrightTimeoutError("Could not find ownership dropdown")
        await ownership_locator.click()
        # select the requested ownership option
        await self.page.get_by_role("option", name=ownership).first.click()

        await self.employees_input.fill(employees)

    async def click_next(self):
        await self.next_button.wait_for(state="visible", timeout=10000)
        await self.next_button.click()
        await self.page.wait_for_load_state("networkidle", timeout=15000)

    async def is_hello_page_displayed(self) -> bool:
        try:
            await self.page.wait_for_selector('text="Hello"', timeout=20000)
            return await self.page.get_by_text("Hello").is_visible()
        except PlaywrightTimeoutError:
            return False

    async def complete_flow_from_welcome(
        self,
        org_name: str,
        address_prefix: str,
        ownership: str,
        phone: str,
        email: str,
        website: str,
        ceo_name: str,
        employees: str,
    ):
        current = self.page.url
        if "/organization/setup/" in current:
            await self.fill_setup_form(address_prefix, ownership, phone, email, website, ceo_name, employees)
            await self.click_next()
            return

        if "/organization/create-organization" in current:
            await self.create_org(org_name)
            await self.fill_setup_form(address_prefix, ownership, phone, email, website, ceo_name, employees)
            await self.click_next()
            return

        if "/welcome" not in current:
            await self.page.goto(self.welcome_url)

        await self.click_start_on_welcome()
        await self.create_org(org_name)
        await self.fill_setup_form(address_prefix, ownership, phone, email, website, ceo_name, employees)
        await self.click_next()

    async def complete_flow_from_current_url(
        self,
        org_name: str,
        address_prefix: str,
        ownership: str,
        phone: str,
        email: str,
        website: str,
        ceo_name: str,
        employees: str,
    ):
        current = self.page.url
        if "/organization/setup/" in current:
            await self.fill_setup_form(address_prefix, ownership, phone, email, website, ceo_name, employees)
            await self.click_next()
            return
        if "/organization/create-organization" in current:
            await self.create_org(org_name)
            await self.fill_setup_form(address_prefix, ownership, phone, email, website, ceo_name, employees)
            await self.click_next()
            return
        await self.complete_flow_from_welcome(org_name, address_prefix, ownership, phone, email, website, ceo_name, employees)
