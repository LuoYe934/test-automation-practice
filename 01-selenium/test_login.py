"""登录功能测试用例 —— 覆盖等价类划分 + 边界值分析（呼应阶段1）。"""
import pytest


class TestLoginSuccess:
    """正向等价类：合法账号"""

    @pytest.mark.parametrize("username,password", [
        ("admin", "123456"),
        ("tester", "test123"),
    ])
    def test_valid_account(self, login_page, username, password):
        page = login_page.login(username, password)
        assert page.product_count() == 6, "登录后应展示全部 6 个商品"
        assert page.cart_count() == 0, "初始购物车应为空"


class TestLoginFailure:
    """反向等价类：非法账号"""

    @pytest.mark.parametrize("username,password,desc", [
        ("admin", "wrongpwd", "密码错误"),
        ("admin", "", "密码为空"),
        ("", "123456", "用户名为空"),
        ("", "", "两者都为空"),
        ("notexist", "123456", "用户名不存在"),
        ("ADMIN", "123456", "用户名大小写敏感"),
        ("admin", "12345", "密码少一位（边界）"),
        ("admin", "1234567", "密码多一位（边界）"),
    ])
    def test_invalid_account(self, login_page, username, password, desc):
        login_page.submit(username, password)
        assert not login_page.is_login_success(), f"{desc}：不应登录成功"
        assert login_page.error_text() != "", f"{desc}：应给出错误提示"


class TestLoginSecurity:
    """安全性 / 特殊输入"""

    def test_sql_injection_like_input(self, login_page):
        login_page.submit("admin' --", "123456")
        assert not login_page.is_login_success()

    def test_xss_like_input(self, login_page):
        login_page.submit("<script>alert(1)</script>", "123456")
        assert not login_page.is_login_success()

    def test_very_long_username(self, login_page):
        login_page.submit("a" * 200, "123456")
        assert not login_page.is_login_success()


class TestLogout:
    def test_logout_back_to_login(self, driver, base_url):
        from pages.login_page import LoginPage

        page = LoginPage(driver, base_url).open("/").login("admin", "123456")
        page.click(page.LOGOUT_BTN)
        assert LoginPage(driver, base_url).is_visible(LoginPage.USERNAME, timeout=5)
