"""罗烨的第一批接口用例"""
import pytest
from client import ApiClient


def test_get_product_404(client):
    """访问不存在的商品，应返回 404"""
    r = client.get_product(99999)
    assert r.status_code == 404


def test_fake_token_401(base_url):
    """伪造 token 访问受限接口，应返回 401（示范：代码要写在函数体里，不是 docstring 里）"""
    c = ApiClient(base_url)
    c.token = "tk-fake123"
    r = c.secure_products()
    assert r.status_code == 401


def test_secure_with_logged_client(logged_client):
    """已登录的客户端访问受限接口，应返回 200。
    TODO 你来写（两行）：
    1. r = logged_client.secure_products()
    2. 断言状态码 200，再断言响应体 code == 0（照抄 test_login_api.py 第 14 行的写法）"""
    r = logged_client.secure_products()   # 用"已登录"的客户端访问受限接口
    assert r.status_code == 200           # 断言：合法用户应该能访问，回 200
    assert r.json()["code"] == 0          # HTTP 200 只代表送达，业务成功还要断 code

def test_logout_then_401(base_url):
    """登出后旧 token 应失效：登录 → 登出 → 再访问 secure，应 401。
    TODO 你来写，三步用同一个 client：
    1. c = ApiClient(base_url)；账号用 admin/123456（⚠️ alice 这个账号不存在！）
    2. login 成功后断言 c.token 非空（注意：assert c.token 就行，末尾别加逗号）
    3. logout() 之后调 secure_products()，断言 401"""
    c = ApiClient(base_url)         # 全程只用这一个 c 对象

    # 第 1 步：登录
    r = c.login("admin", "123456")
    assert r.status_code == 200     # 登录成功
    assert c.token                  # 确认 token 真的被存进 c.token 了（非空）

    # 第 2 步：登出
    r = c.logout()
    assert r.status_code == 200     # 登出成功

    # 第 3 步：拿"旧 token"再去访问受限接口
    r = c.secure_products()
    assert r.status_code == 401     # 应该被拒

def test_search_products(logged_client):
    """搜索接口：q 参数能过滤结果。

    1. 服务器里没有"手机"这个商品！商品有：机械键盘/无线鼠标/27寸显示器/USB-C 扩展坞/降噪耳机/人体工学椅 → 用"键盘"
    2. 返回结构是 r.json()["data"]["items"]，items 才是列表，r.json() 本身是字典
    3. 断言失败信息要用 f-string：assert keyword in item["name"], f"{item['name']} 不包含 {keyword}\""""   
    keyword = "键盘"                                  # 搜索关键词，换成你数据里真有的
    r = logged_client.list_products(q=keyword)        # 发 ?q=手机 搜索
    assert r.status_code == 200                       # 搜索成功

    items = r.json()["data"]["items"]                                     # 把返回的 JSON 变成 Python 对象
    assert len(items) > 0                              # 搜"键盘"至少该搜到"机械键盘"

    for item in items:                               # 遍历每个商品
        assert keyword in item["name"], f"{item['name']} 不含关键词 {keyword}"