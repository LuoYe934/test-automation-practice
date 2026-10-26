"""pytest 夹具：提供接口客户端。

conftest.py 的作用：同目录下的测试文件自动共享这些 fixture。
"""
import os

import pytest

from client import ApiClient

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture()
def client(base_url) -> ApiClient:
    """未登录的客户端"""
    return ApiClient(base_url)


@pytest.fixture()
def logged_client(base_url) -> ApiClient:
    """已登录的客户端（自动带上 token）"""
    c = ApiClient(base_url)
    resp = c.login("admin", "123456")
    assert resp.json()["code"] == 0, "登录失败，检查服务是否已启动"
    return c
