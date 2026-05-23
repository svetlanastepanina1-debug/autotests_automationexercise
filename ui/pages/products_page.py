import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ui.pages.base_page import BasePage


class ProductsPage(BasePage):
    """
    Page Object for https://automationexercise.com/products

    Page structure:
    ├── Navigation bar  (Home, Products, Cart, Signup/Login, …)
    ├── Left sidebar
    │   ├── CATEGORY  (Women / Men / Kids with sub-categories)
    │   └── BRANDS    (Polo, H&M, Madame, …)
    ├── Main panel
    │   ├── "All Products" heading
    │   ├── Search bar  (input + submit button)
    │   └── Product list  — cards each containing:
    │       ├── Product image
    │       ├── Product name  (p tag inside .productinfo)
    │       ├── Price         (h2 tag inside .productinfo)
    │       ├── "Add to cart" hover button
    │       └── "View Product" link
    └── Footer
        └── Subscription block
    """

    URL = "https://automationexercise.com/products"

    # ── Navigation ────────────────────────────────────────────────────────────
    NAVBAR = (By.CSS_SELECTOR, "div#header nav")
    NAV_HOME = (By.CSS_SELECTOR, "a[href='/']")
    NAV_PRODUCTS = (By.CSS_SELECTOR, "a[href='/products']")
    NAV_CART = (By.CSS_SELECTOR, "a[href='/view_cart']")
    NAV_LOGIN = (By.CSS_SELECTOR, "a[href='/login']")

    # ── Page heading ──────────────────────────────────────────────────────────
    ALL_PRODUCTS_HEADING = (By.CSS_SELECTOR, "div.features_items h2.title.text-center")

    # ── Search ────────────────────────────────────────────────────────────────
    SEARCH_INPUT = (By.ID, "search_product")
    SEARCH_BUTTON = (By.ID, "submit_search")
    SEARCHED_PRODUCTS_HEADING = (By.CSS_SELECTOR, "h2.title.text-center")

    # ── Product cards ─────────────────────────────────────────────────────────
    PRODUCT_CARDS = (By.CSS_SELECTOR, "div.single-products")
    PRODUCT_NAMES = (By.CSS_SELECTOR, "div.productinfo p")
    PRODUCT_PRICES = (By.CSS_SELECTOR, "div.productinfo h2")
    PRODUCT_IMAGES = (By.CSS_SELECTOR, "div.single-products img")
    ADD_TO_CART_BUTTONS = (By.CSS_SELECTOR, "div.productinfo a.add-to-cart")
    VIEW_PRODUCT_LINKS = (By.CSS_SELECTOR, "div.product-image-wrapper a[href*='product_details']")

    # Single first product helpers
    FIRST_PRODUCT_NAME = (By.CSS_SELECTOR, "div.productinfo p:first-of-type")
    FIRST_VIEW_PRODUCT = (
        By.CSS_SELECTOR,
        "div.product-image-wrapper:first-child a[href*='product_details']",
    )

    # ── Cart modal (appears after "Add to cart") ───────────────────────────────
    CART_MODAL = (By.ID, "cartModal")
    CART_MODAL_CONTINUE = (By.CSS_SELECTOR, "button[data-dismiss='modal']")
    CART_MODAL_VIEW_CART = (By.CSS_SELECTOR, "#cartModal a[href='/view_cart']")

    # ── Left sidebar ──────────────────────────────────────────────────────────
    LEFT_SIDEBAR = (By.CSS_SELECTOR, "div.left-sidebar")
    CATEGORY_SECTION = (By.CSS_SELECTOR, "div.left-sidebar h2")  # "CATEGORY" heading
    CATEGORY_WOMEN = (By.CSS_SELECTOR, "a[href='#Women']")
    WOMEN_DRESS_LINK = (By.CSS_SELECTOR, "#Women a[href*='category_products/1']")
    DRESS_CATEGORY_URL = "https://automationexercise.com/category_products/1"
    CATEGORY_MEN = (By.CSS_SELECTOR, "a[href='#Men']")
    CATEGORY_KIDS = (By.CSS_SELECTOR, "a[href='#Kids']")
    BRANDS_SECTION = (By.CSS_SELECTOR, "div.brands_products h2")  # "BRANDS" heading
    BRAND_LINKS = (By.CSS_SELECTOR, "div.brands-name ul li a")

    # ── Footer / Subscription ─────────────────────────────────────────────────
    SUBSCRIPTION_HEADING = (By.CSS_SELECTOR, "div#susbscribe_email_field h2, h2.title:last-of-type")
    SUBSCRIPTION_INPUT = (By.ID, "susbscribe_email")
    SUBSCRIPTION_BUTTON = (By.ID, "subscribe")

    # ─────────────────────────────────────────────────────────────────────────
    # Page actions
    # ─────────────────────────────────────────────────────────────────────────

    def open_products_page(self):
        """Navigate to the Products page."""
        self.open(self.URL)

    # ── Search ────────────────────────────────────────────────────────────────

    def search_for_product(self, query: str):
        """Type a query into the search field and submit."""
        self.type_text(self.SEARCH_INPUT, query)
        self.click(self.SEARCH_BUTTON)

    def get_search_results(self) -> list:
        """Return a list of product name strings from the current product grid."""
        elements = self.find_elements(self.PRODUCT_NAMES)
        return [el.text for el in elements]

    # ── Product list helpers ──────────────────────────────────────────────────

    def get_all_product_names(self) -> list[str]:
        elements = self.find_elements(self.PRODUCT_NAMES)
        return [el.text.strip() for el in elements]

    def has_polo_related_product(self) -> bool:
        """True if any visible product name suggests the Polo brand assortment."""
        return any("polo" in name.lower() for name in self.get_all_product_names())

    def get_all_product_prices(self) -> list[str]:
        elements = self.find_elements(self.PRODUCT_PRICES)
        return [el.text for el in elements]

    def get_product_count(self) -> int:
        return len(self.find_elements(self.PRODUCT_CARDS))

    def get_product_name_at(self, index: int = 0) -> str:
        return self.get_all_product_names()[index].strip()

    def get_product_price_at(self, index: int = 0) -> str:
        return self.get_all_product_prices()[index].strip()

    def click_view_product(self, index: int = 0):
        """
        Open product details for the card at index (0-based).

        Uses JS click, then falls back to direct navigation if an ad overlay
        (e.g. #google_vignette in CI) blocks the click.
        """
        links = self.wait.until(EC.presence_of_all_elements_located(self.VIEW_PRODUCT_LINKS))
        link = links[index]
        href = link.get_attribute("href")
        if not href or "product_details" not in href:
            raise ValueError(f"View Product link has unexpected href: {href!r}")

        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
        self.driver.execute_script("arguments[0].click();", link)

        try:
            self.wait_for_url_contains("product_details", timeout=5)
        except Exception:
            if "product_details" not in self.driver.current_url:
                self.open(href)
                self.wait_for_url_contains("product_details")

    def hover_and_add_to_cart(self, index: int = 0):
        """
        Hover over a product card to reveal the overlay, then click 'Add to Cart'.
        Uses JavaScript click to avoid the hover-overlay timing issues.
        """
        buttons = self.find_elements(self.ADD_TO_CART_BUTTONS)
        self.driver.execute_script("arguments[0].click();", buttons[index])

    def dismiss_cart_modal(self):
        """Continue shopping — close the cart modal."""
        self.click(self.CART_MODAL_CONTINUE)

    # ── Category sidebar ──────────────────────────────────────────────────────

    def get_brand_names(self) -> list[str]:
        elements = self.find_elements(self.BRAND_LINKS)
        return [el.text.strip() for el in elements]

    def click_brand(self, brand_name: str):
        """Click a brand link by its text."""
        brand_links = self.find_elements(self.BRAND_LINKS)
        for link in brand_links:
            if brand_name.upper() in link.text.upper():
                link.click()
                return
        raise ValueError(f"Brand '{brand_name}' not found in the sidebar.")

    def click_category_women(self):
        self.click(self.CATEGORY_WOMEN)

    def click_category_men(self):
        self.click(self.CATEGORY_MEN)

    def click_category_kids(self):
        self.click(self.CATEGORY_KIDS)

    def click_subcategory(self, name: str):
        """Click a sub-category link under an expanded category panel (e.g. Dress)."""
        target = name.strip().upper()
        locator = (By.CSS_SELECTOR, "div.panel-body ul li a")
        self.wait.until(
            lambda d: any(
                target in el.text.strip().upper()
                for el in d.find_elements(*locator)
                if el.text.strip()
            )
        )
        for link in self.driver.find_elements(*locator):
            text = link.text.strip().upper()
            if text and target in text:
                self.driver.execute_script("arguments[0].click();", link)
                return
        raise ValueError(f"Sub-category '{name}' not found.")

    def click_category_women_dress(self):
        """Expand Women and open the Dress category products page."""
        self.click_category_women()
        time.sleep(0.5)

        try:
            link = WebDriverWait(self.driver, 8).until(
                EC.visibility_of_element_located(self.WOMEN_DRESS_LINK)
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
            self.driver.execute_script("arguments[0].click();", link)
            self.wait_for_url_contains("category_products", timeout=8)
        except Exception:
            pass

        if "category_products" not in self.driver.current_url:
            self.open(self.DRESS_CATEGORY_URL)
            self.wait_for_url_contains("category_products")

    def wait_for_product_grid(self, min_count: int = 1):
        self.wait.until(lambda d: len(d.find_elements(*self.PRODUCT_CARDS)) >= min_count)

    def get_main_heading_text(self) -> str:
        return self.get_text(self.ALL_PRODUCTS_HEADING)

    def get_searched_products_heading_text(self) -> str:
        headings = self.find_elements(self.SEARCHED_PRODUCTS_HEADING)
        for heading in headings:
            text = heading.text.strip().upper()
            if "SEARCHED" in text:
                return heading.text.strip()
        return headings[0].text.strip() if headings else ""

    def click_view_cart_in_modal(self):
        self.click(self.CART_MODAL_VIEW_CART)
        self.wait_for_url_contains("view_cart")

    def add_products_to_cart(self, count: int = 1):
        """Add the first `count` products to cart via JS click on Add to cart."""
        buttons = self.find_elements(self.ADD_TO_CART_BUTTONS)
        for index in range(min(count, len(buttons))):
            self.driver.execute_script("arguments[0].click();", buttons[index])
            time.sleep(0.5)
            if count > 1 and self.is_element_visible(self.CART_MODAL):
                self.dismiss_cart_modal()
                time.sleep(0.3)
