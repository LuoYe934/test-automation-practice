"""登录页 Page Object。"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPage(BasePage):
    URL = "/"

    # 定位器集中管理（改页面时只改这里）
    USERNAME = (By.ID, "username")
    PASSWORD = (By.ID, "password")
    LOGIN_BTN = (By.ID, "login-btn")
    ERROR_MSG = (By.ID, "error-msg")
    SUCCESS_MSG = (By.ID, "success-msg")
    APP_SECTION = (By.ID, "app-section")

    def submit(self, username: str, password: str):
        """只提交表单、不判断结果，供「反向用例」使用。"""
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.LOGIN_BTN)
        return self

    def login(self, username: str, password: str):
        """执行登录，成功后返回商品页对象（页面跳转的 OO 表达）。"""
        from pages.product_page import ProductPage

        self.submit(username, password)
        page = ProductPage(self.driver, self.base_url)
        page.wait_visible(page.SEARCH_INPUT)
        return page

    def error_text(self) -> str:
        return self.text_of(self.ERROR_MSG)

    def success_text(self) -> str:
        return self.text_of(self.SUCCESS_MSG)

    def is_login_success(self) -> bool:
        return self.is_visible(self.APP_SECTION, timeout=3)
