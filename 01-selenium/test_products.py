"""商品列表页测试用例 —— 覆盖搜索、购物车、动态元素、弹窗、iframe。"""


class TestSearch:
    def test_search_by_keyword(self, product_page):
        product_page.search("键盘")
        assert product_page.product_names() == ["机械键盘"]

    def test_search_partial_keyword(self, product_page):
        product_page.search("显示")
        names = product_page.product_names()
        assert len(names) == 1 and "显示器" in names[0]

    def test_search_no_result(self, product_page):
        product_page.search("不存在的商品xyz")
        assert product_page.product_count() == 0
        assert product_page.is_visible(product_page.EMPTY_TIP)

    def test_search_category_filter(self, product_page):
        product_page.filter_by_category("外设")
        assert product_page.product_count() == 2

    def test_search_then_clear(self, product_page):
        product_page.search("键盘")
        assert product_page.product_count() == 1
        product_page.search("")
        assert product_page.product_count() == 6


class TestCart:
    def test_add_one_product(self, product_page):
        product_page.add_to_cart(1)
        assert product_page.cart_count() == 1

    def test_add_two_products(self, product_page):
        product_page.add_to_cart(1)
        product_page.add_to_cart(2)
        assert product_page.cart_count() == 2

    def test_sold_out_button_disabled(self, product_page):
        """库存为 0 的商品（USB-C 扩展坞，id=4）按钮应不可点击"""
        from selenium.webdriver.common.by import By

        btn = (By.CSS_SELECTOR, ".product-card[data-id='4'] .add-cart-btn")
        assert not product_page.is_enabled(btn)


class TestDynamicElement:
    def test_wait_for_lazy_loaded_element(self, product_page):
        """动态元素：点击后 2 秒才出现，考察显式等待掌握情况"""
        assert not product_page.is_visible(product_page.STOCK_INFO, timeout=1)
        text = product_page.load_stock_info()
        assert "库存同步完成" in text


class TestAlertAndFrame:
    def test_alert_text(self, product_page):
        product_page.click(product_page.ALERT_BTN)
        assert product_page.accept_alert() == "操作成功"

    def test_confirm_accept_clears_cart(self, product_page):
        product_page.add_to_cart(1)
        assert product_page.cart_count() == 1
        product_page.click(product_page.CONFIRM_BTN)
        product_page.accept_alert()
        assert product_page.cart_count() == 0

    def test_fill_form_in_iframe(self, product_page):
        result = product_page.submit_feedback("tester@example.com", "页面很好用")
        assert "提交成功" in result

    def test_iframe_required_field(self, product_page):
        result = product_page.submit_feedback("", "缺少邮箱")
        assert "不能为空" in result
