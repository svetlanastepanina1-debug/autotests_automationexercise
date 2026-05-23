"""
Additional UI tests for /products (category, brand, search heading, cart modal).

Coverage:
  P-16  Women → Dress category
  P-17  Brand Polo
  P-18  Searched products heading
  P-19  View cart from add-to-cart modal
  P-20  Two products in cart
  P-21  Product count decreases after category filter
  P-22  Polo brand assortment includes Polo-related product names
  P-23  Two cart lines: each total equals unit price (qty 1)
"""

import pytest
from ui.pages.cart_page import CartPage
from ui.pages.products_page import ProductsPage
from ui.utils.pricing import parse_rs_amount

pytestmark = pytest.mark.ui


@pytest.fixture
def products_page(driver) -> ProductsPage:
    page = ProductsPage(driver)
    page.open_products_page()
    return page


class TestCategoryFilter:
    """P-16 — Women → Dress"""

    def test_women_dress_category_page(self, products_page: ProductsPage):
        all_count = products_page.get_product_count()
        products_page.click_category_women_dress()
        products_page.wait_for_url_contains("category_products")
        assert "category_products" in products_page.get_current_url()
        heading = products_page.get_main_heading_text().upper()
        assert "DRESS" in heading
        filtered_count = products_page.get_product_count()
        assert 0 < filtered_count < all_count


class TestBrandFilter:
    """P-17 — Polo brand"""

    def test_polo_brand_products_page(self, products_page: ProductsPage):
        products_page.click_brand("Polo")
        products_page.wait_for_url_contains("brand_products")
        assert "brand_products/Polo" in products_page.get_current_url()
        assert products_page.get_product_count() > 0
        assert products_page.has_polo_related_product(), (
            "Expected at least one product name related to Polo brand, "
            f"got: {products_page.get_all_product_names()}"
        )


class TestSearchHeading:
    """P-18 — heading after search"""

    def test_searched_products_heading(self, products_page: ProductsPage):
        products_page.search_for_product("Top")
        heading = products_page.get_searched_products_heading_text().upper()
        assert "SEARCHED PRODUCTS" in heading


class TestCartModalNavigation:
    """P-19 — view cart from modal"""

    def test_view_cart_from_modal_navigates_to_cart(self, products_page: ProductsPage):
        products_page.hover_and_add_to_cart(index=0)
        assert products_page.is_element_visible(ProductsPage.CART_MODAL)
        products_page.click_view_cart_in_modal()
        assert "view_cart" in products_page.get_current_url()


class TestMultipleProductsInCart:
    """P-20 — two line items in cart"""

    def test_two_products_in_cart(self, driver, products_page: ProductsPage):
        products_page.add_products_to_cart(count=2)
        cart = CartPage(driver)
        cart.open_cart_page()
        assert cart.get_cart_item_count() == 2
        assert len(cart.get_item_names()) == 2


class TestCartLinePricing:
    """P-23 — each cart line total equals unit price when quantity is 1"""

    def test_two_cart_lines_match_unit_prices(self, driver, products_page: ProductsPage):
        unit_prices = [
            parse_rs_amount(products_page.get_product_price_at(0)),
            parse_rs_amount(products_page.get_product_price_at(1)),
        ]
        products_page.add_products_to_cart(count=2)

        cart = CartPage(driver)
        cart.open_cart_page()
        assert cart.get_cart_item_count() == 2
        line_totals = cart.get_line_total_amounts()
        assert line_totals == unit_prices


class TestProductCountRange:
    """P-21 — full catalog vs filtered subset"""

    def test_all_products_count_greater_than_category_subset(self, products_page: ProductsPage):
        all_count = products_page.get_product_count()
        assert all_count >= 30, f"Expected a large catalog, got {all_count} products"

        products_page.click_category_women_dress()
        products_page.wait_for_url_contains("category_products")
        dress_count = products_page.get_product_count()
        assert 0 < dress_count < all_count
