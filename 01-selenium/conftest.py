"""pytest 夹具：负责浏览器的启动与关闭。

想让浏览器无界面运行：设置环境变量 HEADLESS=1
    PowerShell:  $env:HEADLESS=1
"""
import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture()
def driver():
    options = Options()
    if os.getenv("HEADLESS") == "1":
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    d = webdriver.Chrome(options=options)
    # 故意设为 0：强制全程使用显式等待，养成正确习惯
    d.implicitly_wait(0)
    yield d
    d.quit()


@pytest.fixture()
def login_page(driver, base_url):
    from pages.login_page import LoginPage

    return LoginPage(driver, base_url).open("/")


@pytest.fixture()
def product_page(driver, base_url):
    """已登录状态下直接进入商品页。"""
    from pages.login_page import LoginPage

    return LoginPage(driver, base_url).open("/").login("admin", "123456")
