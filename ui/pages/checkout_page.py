from selenium.webdriver.common.by import By

from ui.pages.base_page import BasePage
from ui.utils.pricing import parse_rs_amount


class CheckoutPage(BasePage):
    """Page Object for https://automationexercise.com/checkout"""

    REVIEW_HEADING = (By.XPATH, "//h2[contains(., 'Review Your Order')]")
    ORDER_TABLE = (By.CSS_SELECTOR, "table.table-condensed")
    ORDER_ITEM_NAMES = (By.CSS_SELECTOR, "table.table-condensed td.cart_description h4")

    def is_review_section_visible(self) -> bool:
        return self.is_element_visible(self.REVIEW_HEADING)

    def get_order_product_names(self) -> list[str]:
        return [el.text.strip() for el in self.find_elements(self.ORDER_ITEM_NAMES)]

    def get_order_total_text(self) -> str:
        rows = self.driver.find_elements(By.CSS_SELECTOR, "table.table-condensed tr")
        for row in rows:
            if "Total Amount" in row.text:
                for cell in row.find_elements(By.TAG_NAME, "p"):
                    if "Rs." in cell.text:
                        return cell.text.strip()
                parts = row.text.split("\n")
                for part in parts:
                    if "Rs." in part:
                        return part.strip()
        return ""

    def get_order_total_amount(self) -> int:
        return parse_rs_amount(self.get_order_total_text())
