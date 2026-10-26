"""商品接口测试 —— 练手：CRUD 链路、鉴权、异常场景、超时与重试。"""
import pytest
import requests


class TestQuery:
    def test_list_products(self, client):
        r = client.list_products()
        assert r.status_code == 200
        body = r.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 6

    @pytest.mark.parametrize("keyword,expected", [
        ("键盘", 1),
        ("显示", 1),
        ("不存在的商品", 0),
        ("", 6),
    ])
    def test_search_products(self, client, keyword, expected):
        r = client.list_products(q=keyword)
        assert r.json()["data"]["total"] == expected

    def test_filter_by_category(self, client):
        r = client.list_products(category="外设")
        assert r.json()["data"]["total"] == 2

    def test_get_product_detail(self, client):
        r = client.get_product(1)
        assert r.status_code == 200
        assert r.json()["data"]["name"] == "机械键盘"

    @pytest.mark.parametrize("product_id", [999, -1])
    def test_get_not_exist_product(self, client, product_id):
        r = client.get_product(product_id)
        assert r.status_code == 404
        assert r.json()["msg"] == "商品不存在"

    def test_invalid_id_type(self, client):
        r = client.get("/api/products/abc")
        assert r.status_code == 400


class TestAuth:
    def test_create_without_token(self, client):
        """未登录创建商品 -> 401（接口鉴权，阶段3 的难点提前练）"""
        r = client.create_product("测试商品", 9.9, 1)
        assert r.status_code == 401
        assert r.json()["msg"] == "未登录或 token 无效"

    def test_secure_endpoint_with_token(self, logged_client):
        r = logged_client.secure_products()
        assert r.status_code == 200
        assert r.json()["data"]["total"] == 6

    def test_secure_endpoint_without_token(self, client):
        assert client.secure_products().status_code == 401

    def test_token_invalid_after_logout(self, base_url):
        from client import ApiClient

        c = ApiClient(base_url)
        c.login("admin", "123456")
        token = c.token
        c.logout()
        c.token = token  # 复用已失效的 token
        assert c.secure_products().status_code == 401


class TestCrudFlow:
    def test_create_update_delete(self, logged_client):
        """完整业务链路：创建 -> 查询 -> 更新 -> 删除 -> 确认删除"""
        # 1. 创建
        r = logged_client.create_product("自动化测试商品", 66.6, 10, "测试")
        assert r.status_code == 201
        pid = r.json()["data"]["id"]

        try:
            # 2. 查询
            assert logged_client.get_product(pid).json()["data"]["name"] == "自动化测试商品"

            # 3. 更新
            r = logged_client.update_product(pid, price=88.8, stock=5)
            assert r.status_code == 200
            data = r.json()["data"]
            assert data["price"] == 88.8 and data["stock"] == 5

            # 4. 删除
            assert logged_client.delete_product(pid).status_code == 200
        finally:
            # 5. 确认已删除（无论中途是否断言失败都清理）
            logged_client.delete_product(pid)

        assert logged_client.get_product(pid).status_code == 404


class TestException:
    def test_server_error_status(self, client):
        r = client.get("/api/error/500")
        assert r.status_code == 500
        assert r.json()["code"] == 500

    def test_not_found_endpoint(self, client):
        r = client.get("/api/not-exists")
        assert r.status_code == 404

    def test_timeout(self, client):
        """超时场景：服务 3 秒返回，客户端只等 1 秒"""
        with pytest.raises(requests.exceptions.Timeout):
            client.get("/api/slow?delay=3", timeout=1)

    def test_retry_on_flaky(self, client):
        """不稳定接口的重试策略：最多重试 5 次"""
        for attempt in range(5):
            r = client.get("/api/flaky")
            if r.status_code == 200:
                break
        assert r.status_code == 200, f"重试 {attempt + 1} 次后仍失败"
