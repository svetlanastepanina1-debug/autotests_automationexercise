from selenium.webdriver.common.by import By

from ui.pages.base_page import BasePage


class LoginPage(BasePage):
    """Page Object for https://automationexercise.com/login"""

    URL = "https://automationexercise.com/login"
    SIGNUP_URL = "https://automationexercise.com/signup"

    LOGIN_HEADING = (By.CSS_SELECTOR, ".login-form h2")
    SIGNUP_HEADING = (By.CSS_SELECTOR, ".signup-form h2")
    LOGIN_EMAIL = (By.CSS_SELECTOR, "input[data-qa='login-email']")
    LOGIN_PASSWORD = (By.CSS_SELECTOR, "input[data-qa='login-password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[data-qa='login-button']")
    LOGIN_ERROR = (By.CSS_SELECTOR, ".login-form p")

    SIGNUP_NAME = (By.CSS_SELECTOR, "input[data-qa='signup-name']")
    SIGNUP_EMAIL = (By.CSS_SELECTOR, "input[data-qa='signup-email']")
    SIGNUP_BUTTON = (By.CSS_SELECTOR, "button[data-qa='signup-button']")

    NAV_LOGOUT = (By.CSS_SELECTOR, "a[href='/logout']")

    def open_login_page(self):
        self.open(self.URL)

    def get_login_heading_text(self) -> str:
        return self.get_text(self.LOGIN_HEADING)

    def get_signup_heading_text(self) -> str:
        return self.get_text(self.SIGNUP_HEADING)

    def login(self, email: str, password: str):
        self.type_text(self.LOGIN_EMAIL, email)
        self.type_text(self.LOGIN_PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

    def get_login_error_text(self) -> str:
        return self.get_text(self.LOGIN_ERROR)

    def go_to_signup(self, name: str, email: str):
        """Fill signup form on login page and submit to open the signup flow."""
        self.type_text(self.SIGNUP_NAME, name)
        self.type_text(self.SIGNUP_EMAIL, email)
        self.click(self.SIGNUP_BUTTON)

    def is_logout_link_visible(self) -> bool:
        return self.is_element_visible(self.NAV_LOGOUT)

    def click_logout(self):
        self.click(self.NAV_LOGOUT)
