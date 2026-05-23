from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from ui.pages.base_page import BasePage


class ProductDetailsPage(BasePage):
    """Page Object for https://automationexercise.com/product_details/{id}"""

    DEFAULT_URL = "https://automationexercise.com/product_details/1"

    # ── Product info ──────────────────────────────────────────────────────────
    PRODUCT_DETAILS_PANEL = (By.CSS_SELECTOR, "div.product-details")
    PRODUCT_NAME = (By.CSS_SELECTOR, "div.product-information h2")
    PRODUCT_PRICE = (By.CSS_SELECTOR, "div.product-information span")
    PRODUCT_IMAGE = (By.CSS_SELECTOR, "div.product-details img")
    PRODUCT_CATEGORY_INFO = (By.CSS_SELECTOR, "div.product-information p")
    QUANTITY_INPUT = (By.ID, "quantity")
    ADD_TO_CART_BUTTON = (By.CSS_SELECTOR, "button.cart")

    # ── Review ────────────────────────────────────────────────────────────────
    WRITE_REVIEW_TAB = (By.CSS_SELECTOR, "a[href='#reviews']")
    REVIEW_FORM = (By.ID, "review-form")
    REVIEW_TEXTAREA = (By.ID, "review")

    # ── Sidebar (category / brands on details page) ───────────────────────────
    LEFT_SIDEBAR = (By.CSS_SELECTOR, "div.left-sidebar")
    BRANDS_SECTION = (By.CSS_SELECTOR, "div.brands_products h2")

    # ── Navigation ────────────────────────────────────────────────────────────
    NAV_PRODUCTS = (By.CSS_SELECTOR, "a[href='/products']")

    # ── Cart modal (shared with products page) ────────────────────────────────
    CART_MODAL = (By.ID, "cartModal")

    def open_product_details(self, product_id: int = 1):
        self.open(f"https://automationexercise.com/product_details/{product_id}")

    def get_product_name(self) -> str:
        return self.get_text(self.PRODUCT_NAME)

    def get_price_text(self) -> str:
        spans = self.find_elements(self.PRODUCT_PRICE)
        for span in spans:
            text = span.text.strip()
            if "Rs." in text:
                return text
        return spans[0].text.strip() if spans else ""

    def get_quantity_value(self) -> str:
        return self.find_element(self.QUANTITY_INPUT).get_attribute("value")

    def add_to_cart(self):
        self.driver.execute_script(
            "arguments[0].click();",
            self.wait_for_element_clickable(self.ADD_TO_CART_BUTTON),
        )

    def click_products_in_navbar(self):
        links = self.wait.until(EC.presence_of_all_elements_located(self.NAV_PRODUCTS))
        self.driver.execute_script("arguments[0].click();", links[0])
