"""创建本地 SQLite 练习库：无需安装任何数据库，Python 自带。

运行：
    python 03-sql/init_db.py
生成：
    03-sql/shop.db
查询：
    python -c "import sqlite3;print(sqlite3.connect(r'03-sql/shop.db').execute('select * from users').fetchall())"
或装个可视化工具：DB Browser for SQLite（免费）
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "shop.db"

SCHEMA = """
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id       INTEGER PRIMARY KEY,
    name     TEXT    NOT NULL,
    city     TEXT,
    reg_date TEXT
);

CREATE TABLE products (
    id       INTEGER PRIMARY KEY,
    name     TEXT    NOT NULL,
    price    REAL,
    category TEXT,
    stock    INTEGER
);

CREATE TABLE orders (
    id         INTEGER PRIMARY KEY,
    user_id    INTEGER,
    status     TEXT,      -- paid / unpaid / cancelled
    amount     REAL,
    created_at TEXT
);

CREATE TABLE order_items (
    id         INTEGER PRIMARY KEY,
    order_id   INTEGER,
    product_id INTEGER,
    quantity   INTEGER
);
"""

USERS = [
    (1, "张三", "北京", "2024-01-05"),
    (2, "李四", "上海", "2024-02-11"),
    (3, "王五", "北京", "2024-03-02"),
    (4, "赵六", "广州", "2024-05-20"),
    (5, "孙七", "上海", "2024-06-18"),
]

PRODUCTS = [
    (1, "机械键盘", 299.0, "外设", 50),
    (2, "无线鼠标", 99.0, "外设", 120),
    (3, "27寸显示器", 1299.0, "显示", 8),
    (4, "USB-C 扩展坞", 189.0, "配件", 0),
    (5, "降噪耳机", 799.0, "音频", 30),
    (6, "人体工学椅", 1599.0, "家具", 3),
]

ORDERS = [
    (1, 1, "paid", 398.0, "2024-07-01"),
    (2, 1, "unpaid", 1299.0, "2024-07-03"),
    (3, 2, "paid", 898.0, "2024-07-05"),
    (4, 3, "paid", 99.0, "2024-07-08"),
    (5, 3, "cancelled", 1599.0, "2024-07-10"),
    (6, 5, "paid", 1898.0, "2024-07-15"),
]

ORDER_ITEMS = [
    (1, 1, 1, 1),
    (2, 1, 2, 1),
    (3, 2, 3, 1),
    (4, 3, 5, 1),
    (5, 3, 2, 1),
    (6, 4, 2, 1),
    (7, 5, 6, 1),
    (8, 6, 3, 1),
    (9, 6, 6, 1),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.executemany("INSERT INTO users VALUES (?,?,?,?)", USERS)
    conn.executemany("INSERT INTO products VALUES (?,?,?,?,?)", PRODUCTS)
    conn.executemany("INSERT INTO orders VALUES (?,?,?,?,?)", ORDERS)
    conn.executemany("INSERT INTO order_items VALUES (?,?,?,?)", ORDER_ITEMS)
    conn.commit()
    conn.close()
    print(f"已创建练习库：{DB_PATH}")
    print("表：users / products / orders / order_items")


if __name__ == "__main__":
    main()
