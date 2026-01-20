import os
import zipfile
from datetime import datetime

import pytest
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

# Directory where reports and screenshots will be saved
REPORT_DIR = os.getenv("REPORT_DIR", "reports")
os.makedirs(REPORT_DIR, exist_ok=True)


@pytest.fixture
async def browser():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    yield browser
    await browser.close()
    await playwright.stop()


@pytest.fixture
async def page(browser):
    page = await browser.new_page()
    yield page
    await page.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
    results = getattr(item.config, "_test_results", [])
    if rep.when == "call":
        results.append({"nodeid": item.nodeid, "outcome": rep.outcome, "longrepr": str(rep.longrepr) if rep.failed else ""})
        item.config._test_results = results


@pytest.fixture(autouse=True)
async def screenshot_on_failure(request, page):
    yield
    rep = getattr(request.node, "rep_call", None)
    if rep and rep.failed:
        safe_name = request.node.nodeid.replace("::", "_").replace("/", "_")
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        screenshot_path = os.path.join(REPORT_DIR, f"{safe_name}-{ts}.png")
        try:
            await page.screenshot(path=screenshot_path, full_page=True)
        except Exception:
            # Page/context may already be closed; ignore screenshot errors
            screenshot_path = ""
        # attach screenshot path to the results entry
        results = getattr(request.config, "_test_results", [])
        for r in results:
            if r.get("nodeid") == request.node.nodeid:
                r["screenshot"] = screenshot_path
        request.config._test_results = results


def pytest_sessionfinish(session, exitstatus):
    results = getattr(session.config, "_test_results", [])
    report_path = os.path.join(REPORT_DIR, "report.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("<html><head><meta charset='utf-8'><title>Test Report</title></head><body>")
        f.write(f"<h1>Test Report - {datetime.now().isoformat()}</h1>")
        f.write("<table border='1' cellpadding='6' cellspacing='0'>")
        f.write("<tr><th>Test</th><th>Result</th><th>Screenshot</th></tr>")
        for r in results:
            nodeid = r.get("nodeid")
            outcome = r.get("outcome")
            screenshot = r.get("screenshot", "")
            f.write("<tr>")
            f.write(f"<td>{nodeid}</td>")
            f.write(f"<td>{outcome}</td>")
            if screenshot:
                rel = os.path.relpath(screenshot, REPORT_DIR)
                f.write(f"<td><a href='./{rel}'>screenshot</a></td>")
            else:
                f.write("<td>-</td>")
            f.write("</tr>")
        f.write("</table></body></html>")

    # Zip the report directory for easy download
    zip_path = os.path.join(REPORT_DIR, "report.zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(REPORT_DIR):
            for file in files:
                if file == os.path.basename(zip_path):
                    continue
                full = os.path.join(root, file)
                arcname = os.path.relpath(full, REPORT_DIR)
                zf.write(full, arcname)
