"""本地练习服务器：同时提供「Web 练习页面」和「REST 接口」。

启动：
    python tools/server.py

打开：
    http://127.0.0.1:8000          <- Selenium 练手的网页
    http://127.0.0.1:8000/api/...  <- 接口自动化练手的 API
"""

import json
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HOST = "127.0.0.1"
PORT = 8000

ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT / "practice_site"

# 账号：正确 admin / 123456
USERS = {"admin": "123456", "tester": "test123"}

# 已签发的 token
TOKENS: set[str] = set()
LOCK = threading.Lock()


def _default_products():
    return [
        {"id": 1, "name": "机械键盘", "price": 299.0, "stock": 50, "category": "外设"},
        {"id": 2, "name": "无线鼠标", "price": 99.0, "stock": 120, "category": "外设"},
        {"id": 3, "name": "27寸显示器", "price": 1299.0, "stock": 8, "category": "显示"},
        {"id": 4, "name": "USB-C 扩展坞", "price": 189.0, "stock": 0, "category": "配件"},
        {"id": 5, "name": "降噪耳机", "price": 799.0, "stock": 30, "category": "音频"},
        {"id": 6, "name": "人体工学椅", "price": 1599.0, "stock": 3, "category": "家具"},
    ]


PRODUCTS: list[dict] = _default_products()
NEXT_ID = 7


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    # ---------- 基础工具 ----------
    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))

    def _json(self, code: int, body: dict):
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _html(self, rel: str):
        file_path = (SITE_DIR / rel).resolve()
        if not str(file_path).startswith(str(SITE_DIR.resolve())) or not file_path.exists():
            return self._json(404, {"code": 404, "msg": "页面不存在"})
        raw = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _payload(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            return {}

    def _auth(self) -> bool:
        token = self.headers.get("Authorization") or self.headers.get("X-Token") or ""
        return token in TOKENS

    def _find(self, pid: int):
        for p in PRODUCTS:
            if p["id"] == pid:
                return p
        return None

    # ---------- GET ----------
    def do_GET(self):
        url = urlparse(self.path)
        path, query = url.path, parse_qs(url.query)

        if path in ("/", "/index.html"):
            return self._html("index.html")
        if path == "/iframe.html":
            return self._html("iframe.html")

        if path == "/api/products":
            keyword = (query.get("q") or [""])[0].strip()
            category = (query.get("category") or [""])[0].strip()
            items = PRODUCTS
            if keyword:
                items = [p for p in items if keyword in p["name"]]
            if category:
                items = [p for p in items if p["category"] == category]
            return self._json(200, {"code": 0, "msg": "ok",
                                    "data": {"total": len(items), "items": items}})

        if path.startswith("/api/products/"):
            try:
                pid = int(path.rsplit("/", 1)[-1])
            except ValueError:
                return self._json(400, {"code": 400, "msg": "id 必须是整数"})
            item = self._find(pid)
            if not item:
                return self._json(404, {"code": 404, "msg": "商品不存在"})
            return self._json(200, {"code": 0, "msg": "ok", "data": item})

        if path == "/api/secure/products":
            if not self._auth():
                return self._json(401, {"code": 401, "msg": "未登录或 token 无效"})
            return self._json(200, {"code": 0, "msg": "ok",
                                    "data": {"total": len(PRODUCTS), "items": PRODUCTS}})

        # 延迟返回：练 timeout
        if path == "/api/slow":
            delay = float((query.get("delay") or ["2"])[0])
            time.sleep(min(delay, 10))
            return self._json(200, {"code": 0, "msg": f"延迟 {delay}s 返回"})

        # 随机失败：练重试 / 稳定性用例
        if path == "/api/flaky":
            import random
            if random.random() < 0.5:
                return self._json(500, {"code": 500, "msg": "服务不稳定，请重试"})
            return self._json(200, {"code": 0, "msg": "运气不错"})

        if path == "/api/error/500":
            return self._json(500, {"code": 500, "msg": "服务器内部错误"})

        return self._json(404, {"code": 404, "msg": "接口不存在"})

    # ---------- POST ----------
    def do_POST(self):
        path = urlparse(self.path).path
        body = self._payload()

        if path == "/api/login":
            username = body.get("username", "")
            password = body.get("password", "")
            if USERS.get(username) != password:
                return self._json(200, {"code": 1, "msg": "用户名或密码错误"})
            token = "tk-" + uuid.uuid4().hex[:12]
            with LOCK:
                TOKENS.add(token)
            return self._json(200, {"code": 0, "msg": "登录成功",
                                    "data": {"token": token, "username": username}})

        if path == "/api/logout":
            token = self.headers.get("Authorization") or ""
            with LOCK:
                TOKENS.discard(token)
            return self._json(200, {"code": 0, "msg": "已退出"})

        if path == "/api/products":
            if not self._auth():
                return self._json(401, {"code": 401, "msg": "未登录或 token 无效"})
            global NEXT_ID
            item = {
                "id": NEXT_ID,
                "name": body.get("name", ""),
                "price": float(body.get("price", 0)),
                "stock": int(body.get("stock", 0)),
                "category": body.get("category", "其他"),
            }
            NEXT_ID += 1
            PRODUCTS.append(item)
            return self._json(201, {"code": 0, "msg": "创建成功", "data": item})

        return self._json(404, {"code": 404, "msg": "接口不存在"})

    # ---------- PUT ----------
    def do_PUT(self):
        path = urlparse(self.path).path
        body = self._payload()
        if not path.startswith("/api/products/"):
            return self._json(404, {"code": 404, "msg": "接口不存在"})
        if not self._auth():
            return self._json(401, {"code": 401, "msg": "未登录或 token 无效"})
        try:
            pid = int(path.rsplit("/", 1)[-1])
        except ValueError:
            return self._json(400, {"code": 400, "msg": "id 必须是整数"})
        item = self._find(pid)
        if not item:
            return self._json(404, {"code": 404, "msg": "商品不存在"})
        for key in ("name", "price", "stock", "category"):
            if key in body:
                item[key] = body[key]
        return self._json(200, {"code": 0, "msg": "更新成功", "data": item})

    # ---------- DELETE ----------
    def do_DELETE(self):
        path = urlparse(self.path).path
        if not path.startswith("/api/products/"):
            return self._json(404, {"code": 404, "msg": "接口不存在"})
        if not self._auth():
            return self._json(401, {"code": 401, "msg": "未登录或 token 无效"})
        try:
            pid = int(path.rsplit("/", 1)[-1])
        except ValueError:
            return self._json(400, {"code": 400, "msg": "id 必须是整数"})
        item = self._find(pid)
        if not item:
            return self._json(404, {"code": 404, "msg": "商品不存在"})
        PRODUCTS.remove(item)
        return self._json(200, {"code": 0, "msg": "删除成功"})


def main():
    print(f"练习服务器已启动： http://{HOST}:{PORT}")
    print("  Web 页面：http://127.0.0.1:8000")
    print("  接口文档：见 README.md")
    print("按 Ctrl+C 停止")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
