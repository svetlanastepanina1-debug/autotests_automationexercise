import os
from pathlib import Path

import pytest
from pytest_html import extras as html_extras
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService

from api.config.settings import Settings, get_settings


def _path_without_chromedriver() -> str:
    """Drop PATH entries that contain a chromedriver binary (often outdated)."""
    parts = []
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if not directory:
            continue
        driver_path = os.path.join(directory, "chromedriver")
        if os.path.isfile(driver_path):
            continue
        parts.append(directory)
    return os.pathsep.join(parts)


def pytest_addoption(parser):
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run tests in headless browser mode",
    )


@pytest.fixture(scope="session")
def browser_options(request):
    options = Options()
    if request.config.getoption("--headless"):
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--window-size=1920,1080")
    return options


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(scope="session")
def existing_user(settings: Settings) -> dict:
    if not settings.test_user_email or not settings.test_user_password:
        pytest.skip("TEST_USER_EMAIL and TEST_USER_PASSWORD must be set in .env for login tests")
    return {
        "email": settings.test_user_email,
        "password": settings.test_user_password,
    }


@pytest.fixture(scope="function")
def driver(browser_options):
    path_backup = os.environ.get("PATH")
    try:
        # Ignore stale chromedriver in PATH (e.g. /usr/local/bin); use Selenium Manager.
        os.environ["PATH"] = _path_without_chromedriver()
        chrome_driver = webdriver.Chrome(
            service=ChromeService(),
            options=browser_options,
        )
    finally:
        if path_backup is not None:
            os.environ["PATH"] = path_backup

    chrome_driver.implicitly_wait(10)
    yield chrome_driver
    chrome_driver.quit()


SCREENSHOTS_DIR = Path("reports/screenshots")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Save a browser screenshot when a UI test fails."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or report.passed:
        return

    driver = item.funcargs.get("driver")
    if driver is None:
        return

    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = item.nodeid.replace("/", "_").replace("::", "__")
    screenshot_path = SCREENSHOTS_DIR / f"{safe_name}.png"
    try:
        driver.save_screenshot(str(screenshot_path))
        report.extras = getattr(report, "extras", [])
        report.extras.append(html_extras.image(str(screenshot_path)))
    except Exception:
        pass
