import json
import os
import zipfile
from datetime import datetime
from html import escape

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
        entry = {
            "nodeid": item.nodeid,
            "outcome": rep.outcome,
            "longrepr": str(rep.longrepr) if rep.failed else "",
            "duration": getattr(rep, "duration", 0),
            "start": datetime.utcnow().isoformat(),
        }
        results.append(entry)
        item.config._test_results = results


@pytest.fixture(autouse=True)
async def screenshot_on_failure(request, page):
    yield
    rep = getattr(request.node, "rep_call", None)
    results = getattr(request.config, "_test_results", [])
    # find the entry for this test
    entry = next((r for r in results if r.get("nodeid") == request.node.nodeid), None)
    if rep and rep.failed:
        safe_name = request.node.nodeid.replace("::", "_").replace("/", "_")
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        screenshot_path = os.path.join(REPORT_DIR, f"{safe_name}-{ts}.png")
        page_url = ""
        try:
            page_url = page.url
            await page.screenshot(path=screenshot_path, full_page=True)
        except Exception:
            # Page/context may already be closed; ignore screenshot errors
            screenshot_path = ""
        # attach screenshot path and page URL to the results entry
        if entry is not None:
            entry["screenshot"] = screenshot_path
            entry["page_url"] = page_url
            entry["longrepr"] = entry.get("longrepr", "")
        request.config._test_results = results

    # Always write per-test JSON (useful for CI)
    if entry is None:
        entry = {"nodeid": request.node.nodeid, "outcome": getattr(rep, "outcome", "unknown")}
    per_test_path = os.path.join(REPORT_DIR, f"{request.node.name}.json")
    try:
        with open(per_test_path, "w", encoding="utf-8") as pf:
            json.dump(entry, pf, indent=2)
    except Exception:
        pass


def _format_duration(s):
    try:
        return f"{s:.2f}s"
    except Exception:
        return str(s)


def pytest_sessionfinish(session, exitstatus):
    results = getattr(session.config, "_test_results", [])
    report_path = os.path.join(REPORT_DIR, "report.html")
    now = datetime.now().isoformat()
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("<!doctype html><html><head><meta charset='utf-8'><title>Test Report</title>")
        f.write("<style>body{font-family:Arial,Helvetica,sans-serif;padding:18px}table{border-collapse:collapse;width:100%}th,td{border:1px solid #ddd;padding:8px}th{background:#f4f6f8}tr.fail{background:#ffecec}tr.pass{background:#ecffec}details{margin-top:6px}</style>")
        f.write("</head><body>")
        f.write(f"<h1>Test Report</h1><p>Run at: {escape(now)}</p>")
        f.write(f"<p>Total tests: {len(results)} | Exit status: {exitstatus}</p>")
        f.write("<table>")
        f.write("<tr><th>Test</th><th>Result</th><th>Duration</th><th>Page</th><th>Screenshot</th></tr>")
        for r in results:
            nodeid = escape(r.get("nodeid", ""))
            outcome = r.get("outcome", "")
            duration = _format_duration(r.get("duration", 0))
            page_url = escape(r.get("page_url", ""))
            screenshot = r.get("screenshot", "")
            row_class = "pass" if outcome == "passed" else "fail" if outcome == "failed" else ""
            f.write(f"<tr class='{row_class}'>")
            f.write(f"<td>{nodeid}</td>")
            f.write(f"<td>{outcome}</td>")
            f.write(f"<td>{duration}</td>")
            if page_url:
                f.write(f"<td><a href='{page_url}' target='_blank'>open</a></td>")
            else:
                f.write("<td>-</td>")
            if screenshot:
                rel = os.path.relpath(screenshot, REPORT_DIR)
                f.write(f"<td><a href='./{rel}' target='_blank'><img src='./{rel}' style='height:60px'></a></td>")
            else:
                f.write("<td>-</td>")
            f.write("</tr>")
            if r.get("longrepr"):
                f.write("<tr><td colspan='5'><details><summary>Failure details</summary><pre>")
                f.write(escape(r.get("longrepr")))
                f.write("</pre></details></td></tr>")
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
