"""商品列表页 Page Object。"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class ProductPage(BasePage):
    SEARCH_INPUT = (By.ID, "search-input")
    SEARCH_BTN = (By.ID, "search-btn")
    CATEGORY_SELECT = (By.ID, "category-select")
    PRODUCT_LIST = (By.ID, "product-list")
    PRODUCT_CARD = (By.CSS_SELECTOR, ".product-card")
    CARD_TITLE = (By.CSS_SELECTOR, ".product-card h3")
    EMPTY_TIP = (By.ID, "empty-tip")
    RESULT_COUNT = (By.ID, "result-count")
    CART_COUNT = (By.ID, "cart-count")
    LOGOUT_BTN = (By.ID, "logout-btn")
    LOAD_MORE_BTN = (By.ID, "load-more-btn")
    STOCK_INFO = (By.ID, "stock-info")
    ALERT_BTN = (By.ID, "alert-btn")
    CONFIRM_BTN = (By.ID, "confirm-btn")
    FEEDBACK_FRAME = (By.ID, "feedback-frame")

    # iframe 内部元素
    FB_EMAIL = (By.ID, "fb-email")
    FB_CONTENT = (By.ID, "fb-content")
    FB_SUBMIT = (By.ID, "fb-submit")
    FB_RESULT = (By.ID, "fb-result")

    def _render_id(self) -> str:
        """读取列表的渲染版本号（页面每重绘一次 +1）。"""
        return self.driver.find_element(*self.PRODUCT_LIST).get_attribute("data-render-id") or ""

    def _wait_list_refreshed(self, old_render_id: str):
        """等待列表重新渲染完成再断言。

        为什么不用 EC.staleness_of(旧元素)：本地接口响应极快，脚本还没拿到旧元素
        DOM 就已经重建完了，staleness 会永远等不到（真实项目里的经典坑）。
        用「渲染版本号变化」判断则稳定可靠。
        """
        from selenium.webdriver.support.ui import WebDriverWait

        WebDriverWait(self.driver, self.TIMEOUT).until(
            lambda d: self._render_id() != old_render_id
        )
        return self

    # ---------- 业务动作 ----------
    def search(self, keyword: str):
        self.type(self.SEARCH_INPUT, keyword)
        old = self._render_id()
        self.click(self.SEARCH_BTN)
        return self._wait_list_refreshed(old)

    def filter_by_category(self, category: str):
        from selenium.webdriver.support.select import Select

        old = self._render_id()
        Select(self.wait_visible(self.CATEGORY_SELECT)).select_by_visible_text(category)
        return self._wait_list_refreshed(old)

    def product_names(self) -> list[str]:
        return [el.text for el in self.driver.find_elements(*self.CARD_TITLE)]

    def product_count(self) -> int:
        return self.count(self.PRODUCT_CARD)

    def add_to_cart(self, product_id: int):
        btn = (By.CSS_SELECTOR, f".product-card[data-id='{product_id}'] .add-cart-btn")
        self.click(btn)
        return self

    def cart_count(self) -> int:
        return int(self.text_of(self.CART_COUNT))

    def load_stock_info(self):
        """点击后 2 秒才出现结果 —— 必须用显式等待，不能用 sleep。"""
        self.click(self.LOAD_MORE_BTN)
        self.wait_visible(self.STOCK_INFO, timeout=10)
        return self.text_of(self.STOCK_INFO)

    def submit_feedback(self, email: str, content: str) -> str:
        """演示 iframe 切换：进 frame -> 操作 -> 切回主文档。"""
        self.switch_to_frame(self.FEEDBACK_FRAME)
        try:
            self.type(self.FB_EMAIL, email)
            self.type(self.FB_CONTENT, content)
            self.click(self.FB_SUBMIT)
            return self.text_of(self.FB_RESULT)
        finally:
            self.switch_to_default()
