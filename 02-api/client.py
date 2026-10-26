

"""接口客户端封装：统一管理 base_url、超时、鉴权头。

这是「封装公共方法」的最小示例，阶段3的项目可以直接复用这个思路。
"""
import requests


class ApiClient:
    def __init__(self, base_url: str, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.token: str | None = None

    # ---------- 内部工具 ----------
    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _headers(self, auth: bool = False) -> dict:
        headers = {"Content-Type": "application/json"}
        if auth and self.token:
            headers["Authorization"] = self.token
        return headers

    # ---------- 鉴权 ----------
    def login(self, username: str, password: str) -> requests.Response:
        r = self.session.post(
            self._url("/api/login"),
            json={"username": username, "password": password},
            timeout=self.timeout,
        )
        data = r.json()
        if data.get("code") == 0:
            self.token = data["data"]["token"]
        return r

    def logout(self) -> requests.Response:
        r = self.session.post(self._url("/api/logout"),
                              headers=self._headers(auth=True),
                              timeout=self.timeout)
        self.token = None
        return r

    # ---------- 商品 ----------
    def list_products(self, q: str | None = None, category: str | None = None):
        params = {}
        if q is not None:
            params["q"] = q
        if category is not None:
            params["category"] = category
        return self.session.get(self._url("/api/products"),
                                params=params, timeout=self.timeout)

    def get_product(self, product_id: int):
        return self.session.get(self._url(f"/api/products/{product_id}"),
                                timeout=self.timeout)

    def create_product(self, name: str, price: float, stock: int, category: str = "其他"):
        return self.session.post(self._url("/api/products"),
                                 headers=self._headers(auth=True),
                                 json={"name": name, "price": price,
                                       "stock": stock, "category": category},
                                 timeout=self.timeout)

    def update_product(self, product_id: int, **fields):
        return self.session.put(self._url(f"/api/products/{product_id}"),
                                headers=self._headers(auth=True),
                                json=fields, timeout=self.timeout)

    def delete_product(self, product_id: int):
        return self.session.delete(self._url(f"/api/products/{product_id}"),
                                   headers=self._headers(auth=True),
                                   timeout=self.timeout)

    def secure_products(self):
        """需要 token 才能访问的接口"""
        return self.session.get(self._url("/api/secure/products"),
                                headers=self._headers(auth=True), timeout=self.timeout)

    # ---------- 通用（练手用）----------
    def get(self, path: str, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return self.session.get(self._url(path), **kwargs)
