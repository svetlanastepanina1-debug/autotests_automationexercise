from selenium.webdriver.common.by import By

from ui.pages.base_page import BasePage
from ui.utils.pricing import parse_rs_amount


class CartPage(BasePage):
    """Page Object for https://automationexercise.com/view_cart"""

    URL = "https://automationexercise.com/view_cart"

    CART_BREADCRUMB = (By.CSS_SELECTOR, "#cart_items .breadcrumb li.active")
    CART_INFO = (By.CSS_SELECTOR, "#cart_info")
    CART_ROWS = (By.CSS_SELECTOR, "#cart_info_table tbody tr")
    ITEM_NAME = (By.CSS_SELECTOR, "td.cart_description h4 a")
    ITEM_PRICE = (By.CSS_SELECTOR, "td.cart_price p")
    ITEM_QUANTITY = (By.CSS_SELECTOR, "td.cart_quantity button")
    REMOVE_BUTTON = (By.CSS_SELECTOR, "a.cart_quantity_delete")
    CHECKOUT_BUTTON = (By.CSS_SELECTOR, "a.check_out")
    ORDER_TABLE = (By.CSS_SELECTOR, "table.table-condensed")

    def open_cart_page(self):
        self.open(self.URL)

    def get_breadcrumb_text(self) -> str:
        return self.get_text(self.CART_BREADCRUMB)

    def get_cart_info_text(self) -> str:
        return self.get_text(self.CART_INFO)

    def is_cart_empty(self) -> bool:
        return len(self.driver.find_elements(*self.CART_ROWS)) == 0

    def get_cart_item_count(self) -> int:
        return len(self.driver.find_elements(*self.CART_ROWS))

    def get_item_names(self) -> list[str]:
        return [el.text.strip() for el in self.find_elements(self.ITEM_NAME)]

    def get_item_prices(self) -> list[str]:
        return [el.text.strip() for el in self.find_elements(self.ITEM_PRICE)]

    def get_item_quantities(self) -> list[str]:
        return [el.text.strip() for el in self.find_elements(self.ITEM_QUANTITY)]

    def get_first_item_name(self) -> str:
        return self.get_item_names()[0]

    def get_first_item_price(self) -> str:
        return self.get_item_prices()[0]

    def get_first_item_quantity(self) -> str:
        return self.get_item_quantities()[0]

    def remove_first_item(self):
        self.click(self.REMOVE_BUTTON)
        self.wait.until(lambda _: self.is_cart_empty())

    def is_checkout_visible(self) -> bool:
        return self.is_element_visible(self.CHECKOUT_BUTTON)

    def click_proceed_to_checkout(self):
        self.click(self.CHECKOUT_BUTTON)

    def get_line_total(self) -> str:
        """Total for the first line item (Total column in table.table-condensed)."""
        rows = self.driver.find_elements(By.CSS_SELECTOR, "table.table-condensed tr")
        for row in rows[1:]:
            if "Total Amount" in row.text:
                break
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 5 and cells[4].text.strip():
                return cells[4].text.strip()
        return ""

    def get_first_item_price_amount(self) -> int:
        return parse_rs_amount(self.get_first_item_price())

    def get_first_item_quantity_int(self) -> int:
        return int(self.get_first_item_quantity())

    def get_line_total_amount(self) -> int:
        return parse_rs_amount(self.get_line_total())

    def line_total_equals_price_times_quantity(self) -> bool:
        return (
            self.get_line_total_amount()
            == self.get_first_item_price_amount() * self.get_first_item_quantity_int()
        )

    def get_line_total_amounts(self) -> list[int]:
        """Per-line totals from the cart summary table (excludes order grand total)."""
        amounts: list[int] = []
        rows = self.driver.find_elements(By.CSS_SELECTOR, "table.table-condensed tr")
        for row in rows[1:]:
            if "Total Amount" in row.text:
                break
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 5 and cells[4].text.strip():
                amounts.append(parse_rs_amount(cells[4].text))
        return amounts
