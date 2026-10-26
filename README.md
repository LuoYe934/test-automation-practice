# 测试工程师 2 个月计划 · 阶段2 练习环境

这套东西解决的问题：**不知道用什么练、怎么练**。
全部本地运行，不依赖外网，装好依赖就能跑。

---

## 一、5 分钟跑起来

### 1. 安装依赖

```powershell
cd c:/Users/LY/Projects/test-8week
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 启动练习服务器（**这个窗口不要关**）

```powershell
python tools/server.py
```

看到 `练习服务器已启动： http://127.0.0.1:8000` 就成功了。

它同时提供两样东西：

| 地址 | 用途 |
|---|---|
| http://127.0.0.1:8000 | **Selenium 练手网页**（登录 / 搜索 / 购物车 / 动态加载 / 弹窗 / iframe） |
| http://127.0.0.1:8000/api/... | **接口自动化练手 API**（登录鉴权 / CRUD / 超时 / 500 / 不稳定接口） |

练习账号：`admin / 123456`

### 3. 跑接口测试（不需要浏览器，马上能看到结果）

**新开一个 PowerShell 窗口**：

```powershell
cd c:/Users/LY/Projects/test-8week
pytest 02-api -v
```

看到一堆绿色的 `PASSED` 就说明环境 OK 了。

### 4. 跑 Web 自动化测试（需要 Chrome 浏览器）

```powershell
pytest 01-selenium -v
```

浏览器会自动打开、自动操作，你可以亲眼看着它跑。
不想看界面：`$env:HEADLESS=1` 后再跑。

### 5. SQL 练习

```powershell
python 03-sql/init_db.py
```

然后照着 `03-sql/practice.md` 做题（14 道题，含答案 + 索引面试要点）。

### 6. Git 练习

照着 `04-git/git_practice.md` 敲，里面有**亲手制造一次冲突再解决**的完整步骤。

---

## 二、接口清单（记下来，写用例时用）

| 方法 | 路径 | 鉴权 | 说明 |
|---|---|---|---|
| POST | `/api/login` | 否 | `{"username","password"}`，成功返回 token |
| POST | `/api/logout` | 是 | 使 token 失效 |
| GET | `/api/products?q=&category=` | 否 | 商品列表 + 搜索 + 分类过滤 |
| GET | `/api/products/{id}` | 否 | 商品详情，不存在返回 404 |
| POST | `/api/products` | 是 | 创建，返回 201 |
| PUT | `/api/products/{id}` | 是 | 更新 |
| DELETE | `/api/products/{id}` | 是 | 删除 |
| GET | `/api/secure/products` | 是 | 不带 token 返回 401 |
| GET | `/api/slow?delay=3` | 否 | 延迟返回，练超时 |
| GET | `/api/flaky` | 否 | 50% 概率 500，练重试 |
| GET | `/api/error/500` | 否 | 固定 500，练异常断言 |

---

## 三、页面元素清单（写定位器时查这里）

| 元素 | id / 选择器 |
|---|---|
| 用户名 | `#username` |
| 密码 | `#password` |
| 登录按钮 | `#login-btn` |
| 错误提示 | `#error-msg` |
| 商品页容器 | `#app-section` |
| 搜索框 / 按钮 | `#search-input` / `#search-btn` |
| 分类下拉 | `#category-select` |
| 商品卡片 | `.product-card`（带 `data-id`） |
| 加入购物车 | `.product-card[data-id='1'] .add-cart-btn` |
| 购物车计数 | `#cart-count` |
| 动态加载 | `#load-more-btn` → 2 秒后出现 `#stock-info` |
| 弹窗 | `#alert-btn` / `#confirm-btn` |
| iframe | `#feedback-frame`，内部 `#fb-email` `#fb-content` `#fb-submit` `#fb-result` |

---

## 四、练到什么程度算过关（自检清单）

- [ ] 能自己写出 `test_login.py` 里没有的 3 条新用例（比如：密码含空格、用户名前后空格）
- [ ] 全程没有用 `time.sleep()`，全靠显式等待
- [ ] 接口用例 ≥ 15 条，覆盖正常 / 异常 / 鉴权 / 超时
- [ ] 能在不看答案的情况下写出三表 JOIN 和 `HAVING`
- [ ] 能口述 B+ 树索引和最左前缀原则（30 秒讲完）
- [ ] Git 有连续提交记录，且亲手解决过一次冲突

---

## 五、什么时候用外网靶场（本地练熟之后）

| 类型 | 地址 | 说明 |
|---|---|---|
| Web 自动化 | https://www.saucedemo.com | 标准电商站，账号 `standard_user / secret_sauce`，业界最常用 |
| Web 自动化 | https://automationexercise.com | 完整电商流程（注册/下单/支付） |
| Web 自动化 | http://books.toscrape.com | 图书站，适合练 XPath 和翻页 |
| 接口 | https://jsonplaceholder.typicode.com | 经典假数据 REST API，无需注册 |
| 接口（带登录） | https://wanandroid.com | 国内稳定开放 API，有登录 cookie、收藏、题库，适合练鉴权 |
| 接口 | https://petstore.swagger.io/v2 | 完整 CRUD + Swagger 文档 |
| SQL 题库 | 牛客网「SQL 大厂面试题」 | 在线刷题，有即时反馈 |
| SQL 题库 | https://sqlzoo.net | 英文，交互式入门 |

> 建议：本地这套先跑通 2 遍，再去外网靶场。外网站点会改版、会限流，本地环境永远稳定。

---

## 六、目录结构

```
.
├── tools/server.py          练习服务器（网页 + 接口）
├── practice_site/           本地靶场网页
├── 01-selenium/             Web 自动化
│   ├── pages/               Page Object 封装
│   ├── conftest.py          浏览器夹具
│   ├── test_login.py        登录用例（等价类 + 边界值）
│   └── test_products.py     商品页用例（动态元素/弹窗/iframe）
├── 02-api/                  接口自动化
│   ├── client.py            请求封装（含 token 处理）
│   ├── conftest.py          客户端夹具
│   ├── test_login_api.py
│   └── test_products_api.py
├── 03-sql/                  SQLite 练习库 + 题目答案
└── 04-git/                  Git 练习步骤
```

---

## 七、常见报错

| 报错 | 原因 / 解决 |
|---|---|
| `Connection refused` | 练习服务器没启动，另开窗口跑 `python tools/server.py` |
| `WebDriverException: chrome not reachable` | 没装 Chrome，去 google.cn/chrome 装一个 |
| Selenium 启动报找不到 driver | Selenium 4 会自动下载；国内失败就手动下 chromedriver 放到 PATH |
| `ModuleNotFoundError: client` | 要在项目根目录跑 `pytest`，不要进子目录跑 |
