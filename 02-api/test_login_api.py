"""登录接口测试 —— 练手：状态码断言、响应体断言、参数化。"""
import pytest


class TestLoginApi:
    @pytest.mark.parametrize("username,password", [
        ("admin", "123456"),
        ("tester", "test123"),
    ])
    def test_login_success(self, client, username, password):
        r = client.login(username, password)
        assert r.status_code == 200
        body = r.json()
        assert body["code"] == 0
        assert body["msg"] == "登录成功"
        assert body["data"]["token"].startswith("tk-")
        assert body["data"]["username"] == username

    @pytest.mark.parametrize("username,password", [
        ("admin", "wrong"),
        ("admin", ""),
        ("", "123456"),
        ("nobody", "123456"),
    ])
    def test_login_fail(self, client, username, password):
        r = client.login(username, password)
        body = r.json()
        assert body["code"] == 1
        assert body["msg"] == "用户名或密码错误"
        assert "token" not in body.get("data", {})

    def test_login_without_body(self, client):
        """不传 body：考察异常输入的健壮性"""
        r = client.session.post(f"{client.base_url}/api/login", timeout=5)
        assert r.status_code == 200
        assert r.json()["code"] == 1

    def test_login_response_time(self, client):
        """性能维度：响应时间应小于 1 秒"""
        r = client.login("admin", "123456")
        assert r.elapsed.total_seconds() < 1
