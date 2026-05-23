"""
UI tests for https://automationexercise.com/view_cart

Coverage:
  C-01  Empty cart message
  C-02  Add from products and open cart
  C-03  Item name in cart
  C-04  Item price (Rs.)
  C-05  Quantity
  C-06  Remove item
  C-07  Proceed to checkout (visible; navigation when logged in)
  C-08  Line total equals price × quantity (business rule)
  C-09  Cart line matches product card from catalog
  C-10  Checkout review shows ordered product and total
"""

import pytest
from ui.pages.cart_page import CartPage
from ui.pages.products_page import ProductsPage

pytestmark = pytest.mark.ui


@pytest.fixture
def cart_page(driver) -> CartPage:
    return CartPage(driver)


@pytest.fixture
def cart_with_one_item(driver) -> CartPage:
    """Add first product on /products, then open the cart via the modal link."""
    products = ProductsPage(driver)
    products.open_products_page()
    products.hover_and_add_to_cart(index=0)
    products.click_view_cart_in_modal()
    return CartPage(driver)


class TestEmptyCart:
    """C-01 — empty cart state"""

    def test_empty_cart_message(self, cart_page: CartPage):
        cart_page.open_cart_page()
        assert cart_page.is_cart_empty()
        info = cart_page.get_cart_info_text()
        assert "empty" in info.lower()
        assert "products" in info.lower()

    def test_empty_cart_breadcrumb(self, cart_page: CartPage):
        cart_page.open_cart_page()
        assert "shopping cart" in cart_page.get_breadcrumb_text().lower()


class TestCartWithItem:
    """C-02 — C-08 — cart with at least one line item"""

    def test_cart_url_after_add_from_products(self, cart_with_one_item: CartPage):
        assert "view_cart" in cart_with_one_item.get_current_url()

    def test_cart_has_one_row(self, cart_with_one_item: CartPage):
        assert cart_with_one_item.get_cart_item_count() == 1

    def test_item_name_not_empty(self, cart_with_one_item: CartPage):
        assert cart_with_one_item.get_first_item_name().strip() != ""

    def test_item_price_contains_rs(self, cart_with_one_item: CartPage):
        assert "Rs." in cart_with_one_item.get_first_item_price()

    def test_item_quantity_default(self, cart_with_one_item: CartPage):
        assert cart_with_one_item.get_first_item_quantity() == "1"

    def test_proceed_to_checkout_visible(self, cart_with_one_item: CartPage):
        assert cart_with_one_item.is_checkout_visible()

    def test_line_total_equals_price_times_quantity(self, cart_with_one_item: CartPage):
        assert cart_with_one_item.line_total_equals_price_times_quantity()


class TestRemoveFromCart:
    """C-06 — delete line item"""

    def test_remove_item_empties_cart(self, cart_with_one_item: CartPage):
        cart_with_one_item.remove_first_item()
        assert cart_with_one_item.is_cart_empty()


class TestCartMatchesCatalog:
    """C-09 — cart content mirrors the product card added from /products"""

    def test_cart_item_matches_product_card(self, driver):
        products = ProductsPage(driver)
        products.open_products_page()
        expected_name = products.get_product_name_at(0)
        expected_price = products.get_product_price_at(0)

        products.hover_and_add_to_cart(index=0)
        products.click_view_cart_in_modal()

        cart = CartPage(driver)
        assert cart.get_first_item_name() == expected_name
        assert cart.get_first_item_price() == expected_price


class TestCheckoutWhenLoggedIn:
    """C-07 / C-10 — checkout requires login; order review reflects the cart"""

    def test_checkout_navigates_when_logged_in(self, driver, existing_user: dict):
        from ui.pages.login_page import LoginPage

        login = LoginPage(driver)
        login.open_login_page()
        login.login(existing_user["email"], existing_user["password"])
        login.wait_for_url_contains("automationexercise.com")

        products = ProductsPage(driver)
        products.open_products_page()
        products.hover_and_add_to_cart(index=0)
        products.click_view_cart_in_modal()

        cart = CartPage(driver)
        cart.click_proceed_to_checkout()
        cart.wait_for_url_contains("checkout")
        assert "checkout" in cart.get_current_url()

    def test_checkout_review_matches_cart_item(self, driver, existing_user: dict):
        from ui.pages.checkout_page import CheckoutPage
        from ui.pages.login_page import LoginPage

        products = ProductsPage(driver)
        products.open_products_page()
        product_name = products.get_product_name_at(0)

        login = LoginPage(driver)
        login.open_login_page()
        login.login(existing_user["email"], existing_user["password"])
        login.wait_for_url_contains("automationexercise.com")

        products.open_products_page()
        products.hover_and_add_to_cart(index=0)
        products.click_view_cart_in_modal()

        cart = CartPage(driver)
        line_total = cart.get_line_total_amount()

        cart.click_proceed_to_checkout()
        cart.wait_for_url_contains("checkout")

        checkout = CheckoutPage(driver)
        assert checkout.is_review_section_visible()
        assert product_name in checkout.get_order_product_names()
        assert checkout.get_order_total_amount() == line_total
