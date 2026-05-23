"""
UI tests for https://automationexercise.com/login

Coverage:
  L-01  Login page load and headings
  L-02  Valid login (requires .env credentials)
  L-03  Invalid password error
  L-04  Signup flow from login page
  L-05  Logout (requires .env credentials)
"""

import pytest
from ui.pages.login_page import LoginPage

pytestmark = pytest.mark.ui


@pytest.fixture
def login_page(driver) -> LoginPage:
    page = LoginPage(driver)
    page.open_login_page()
    return page


class TestLoginPageLoad:
    """L-01 — page URL and form headings"""

    def test_login_page_url(self, login_page: LoginPage):
        assert "login" in login_page.get_current_url()

    def test_login_heading_visible(self, login_page: LoginPage):
        assert "login to your account" in login_page.get_login_heading_text().lower()

    def test_signup_heading_visible(self, login_page: LoginPage):
        assert "new user signup" in login_page.get_signup_heading_text().lower()


class TestLoginInvalid:
    """L-03 — wrong credentials"""

    def test_invalid_password_shows_error(self, login_page: LoginPage):
        login_page.login("not-a-real-user@example.com", "wrong-password-123")
        error = login_page.get_login_error_text()
        assert "incorrect" in error.lower()


class TestLoginValid:
    """L-02 — successful login"""

    def test_valid_login_redirects_to_home(self, login_page: LoginPage, existing_user: dict):
        login_page.login(existing_user["email"], existing_user["password"])
        login_page.wait_for_url_contains("automationexercise.com")
        assert login_page.is_logout_link_visible()


class TestSignupNavigation:
    """L-04 — signup from login page"""

    def test_signup_navigates_to_signup_page(self, login_page: LoginPage):
        login_page.go_to_signup(name="Test User", email="signup-flow@example.com")
        login_page.wait_for_url_contains("signup")
        assert "signup" in login_page.get_current_url()


class TestLogout:
    """L-05 — logout after login"""

    def test_logout_returns_to_login(self, login_page: LoginPage, existing_user: dict):
        login_page.login(existing_user["email"], existing_user["password"])
        login_page.wait_for_url_contains("automationexercise.com")
        assert login_page.is_logout_link_visible()

        login_page.click_logout()
        login_page.wait_for_url_contains("login")
        assert "login" in login_page.get_current_url()
