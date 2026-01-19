# CONSTRUCT Login Automation - Beginner Friendly

Simple login automation framework using Playwright and Pytest.

## Project Files

```
Construct automation/
├── conftest.py              # Pytest setup (fixtures)
├── .env                     # Your email and password
├── requirements.txt         # Python packages to install
├── pages/
│   └── login_page.py        # Login page object (element locators + methods)
└── tests/
    └── test_login.py        # Login tests
```

## Setup (First Time Only)

### Step 1: Install Python packages
```bash
pip install -r requirements.txt
```

### Step 2: Install Playwright browser
```bash
playwright install chromium
```

That's it! Now you're ready to run tests.

## Running Tests

### Run all login tests:
```bash
pytest tests/test_login.py -v
```

### Run a specific test:
```bash
pytest tests/test_login.py::TestLoginFlow::test_05_login_with_valid_credentials -v
```

### Run with more details (print statements visible):
```bash
pytest tests/test_login.py -v -s
```

## How It Works - Simple Explanation

### conftest.py
- Sets up the browser and page
- Think of it as "opening Chrome browser" before each test

### pages/login_page.py
- Contains the LoginPage class
- Has "locators" (where to find email box, password box, etc)
- Has "methods" (type email, click button, etc)

### tests/test_login.py
- Contains the actual tests
- Each test_ function is a different test
- They use LoginPage to interact with the website

## Tests Explained

1. **test_01_login_page_loads** - Checks if page loads
2. **test_02_type_email** - Checks if email field works
3. **test_03_type_password** - Checks if password field works
4. **test_04_login_button_exists** - Checks if login button exists
5. **test_05_login_with_valid_credentials** - ACTUAL LOGIN TEST

## What is "async"?

You might see `async def` and `await` - don't worry!
- `async` = This function can wait for things (like clicking button, loading page)
- `await` = Wait for this action to finish before moving to next line

Example:
```python
await login_page.type_email(email)  # Wait for email to be typed
await login_page.type_password(password)  # Then wait for password to be typed
```

## Troubleshooting

### Tests fail with browser doesn't open
```bash
playwright install chromium
```

### Tests are too fast to see
Add to pytest.ini:
```
addopts = -v -s
```

### Want to see browser operations
The browser should already open (headless=False in conftest.py). If not, check that your code is using the `page` fixture.

## Next: What to do after login works?

Once login test passes:
1. Explore what page we land on after login
2. Create a DashboardPage class (like LoginPage)
3. Create tests for dashboard functionality
4. Create a UserCreationPage for registration flow
