"""
UI tests for https://automationexercise.com/product_details/{id}

Coverage:
  PD-01  URL contains product_details
  PD-02  Product name is visible and not empty
  PD-03  Product price contains Rs.
  PD-04  Product image is present
  PD-05  Quantity input default value is 1
  PD-06  Add to cart opens cart modal
  PD-07  Write Your Review section is available
  PD-08  Brands sidebar is visible on details page
  PD-09  Products link in navbar returns to /products
"""

import pytest
from ui.pages.product_details_page import ProductDetailsPage
from ui.pages.products_page import ProductsPage

pytestmark = pytest.mark.ui


@pytest.fixture
def product_details_page(driver) -> ProductDetailsPage:
    """Open first product details via Products page → View Product."""
    products = ProductsPage(driver)
    products.open_products_page()
    products.click_view_product(index=0)
    return ProductDetailsPage(driver)


class TestProductDetailsUrl:
    """PD-01 — product details URL"""

    def test_product_details_url(self, product_details_page: ProductDetailsPage):
        assert "product_details" in product_details_page.get_current_url()


class TestProductDetailsInfo:
    """PD-02 — PD-04 — product name, price, image"""

    def test_product_name_visible(self, product_details_page: ProductDetailsPage):
        name = product_details_page.get_product_name()
        assert name.strip() != ""

    def test_product_price_visible(self, product_details_page: ProductDetailsPage):
        price = product_details_page.get_price_text()
        assert "Rs." in price

    def test_product_image_visible(self, product_details_page: ProductDetailsPage):
        image = product_details_page.find_element(ProductDetailsPage.PRODUCT_IMAGE)
        src = image.get_attribute("src")
        assert src and src.strip() != ""


class TestProductDetailsQuantity:
    """PD-05 — quantity field"""

    def test_quantity_input_default(self, product_details_page: ProductDetailsPage):
        assert product_details_page.get_quantity_value() == "1"


class TestProductDetailsAddToCart:
    """PD-06 — add to cart from details page"""

    def test_add_to_cart_on_details_page(self, product_details_page: ProductDetailsPage):
        product_details_page.add_to_cart()
        assert product_details_page.is_element_visible(ProductDetailsPage.CART_MODAL)


class TestProductDetailsReview:
    """PD-07 — write review section"""

    def test_write_review_section_visible(self, product_details_page: ProductDetailsPage):
        assert product_details_page.is_element_visible(ProductDetailsPage.WRITE_REVIEW_TAB)
        assert product_details_page.is_element_visible(ProductDetailsPage.REVIEW_TEXTAREA)


class TestProductDetailsSidebar:
    """PD-08 — sidebar brands on details page"""

    def test_brands_sidebar_visible_on_details_page(self, product_details_page: ProductDetailsPage):
        assert product_details_page.is_element_visible(ProductDetailsPage.LEFT_SIDEBAR)
        assert product_details_page.is_element_visible(ProductDetailsPage.BRANDS_SECTION)


class TestProductDetailsNavigation:
    """PD-09 — navigate back to products"""

    def test_back_to_products_navigation(self, product_details_page: ProductDetailsPage):
        product_details_page.click_products_in_navbar()
        product_details_page.wait_for_url_contains("products")
        assert "product_details" not in product_details_page.get_current_url()
