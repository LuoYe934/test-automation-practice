"""页面基类：封装所有公共操作。

重点：全部使用「显式等待」，不出现 time.sleep()。
"""
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    """所有页面对象的父类，封装 WebDriver 常用操作。"""

    TIMEOUT = 10

    def __init__(self, driver, base_url: str = ""):
        self.driver = driver
        self.base_url = base_url

    # ---------- 导航 ----------
    def open(self, path: str = "/"):
        self.driver.get(f"{self.base_url}{path}")
        return self

    @property
    def title(self) -> str:
        return self.driver.title

    # ---------- 等待 ----------
    def wait_visible(self, locator, timeout: int | None = None):
        """等待元素可见（核心方法，替代 sleep）。"""
        return WebDriverWait(self.driver, timeout or self.TIMEOUT).until(
            EC.visibility_of_element_located(locator)
        )

    def wait_clickable(self, locator, timeout: int | None = None):
        return WebDriverWait(self.driver, timeout or self.TIMEOUT).until(
            EC.element_to_be_clickable(locator)
        )

    def wait_text_in(self, locator, text: str, timeout: int | None = None) -> bool:
        try:
            return WebDriverWait(self.driver, timeout or self.TIMEOUT).until(
                EC.text_to_be_present_in_element(locator, text)
            )
        except TimeoutException:
            return False

    # ---------- 操作 ----------
    def click(self, locator):
        self.wait_clickable(locator).click()
        return self

    def type(self, locator, text: str, clear: bool = True):
        el = self.wait_visible(locator)
        if clear:
            el.clear()
        el.send_keys(text)
        return self

    def text_of(self, locator) -> str:
        return self.wait_visible(locator).text

    def count(self, locator) -> int:
        return len(self.driver.find_elements(*locator))

    def is_visible(self, locator, timeout: int = 2) -> bool:
        try:
            self.wait_visible(locator, timeout)
            return True
        except TimeoutException:
            return False

    def is_enabled(self, locator) -> bool:
        return self.wait_visible(locator).is_enabled()

    # ---------- 切换 ----------
    def switch_to_frame(self, locator):
        self.wait_visible(locator)
        self.driver.switch_to.frame(self.driver.find_element(*locator))
        return self

    def switch_to_default(self):
        self.driver.switch_to.default_content()
        return self

    def accept_alert(self) -> str:
        """接受 alert 并返回其文本。"""
        WebDriverWait(self.driver, self.TIMEOUT).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        text = alert.text
        alert.accept()
        return text
