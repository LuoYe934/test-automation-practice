# SQL 练习（本地 SQLite，零安装）

先生成数据库：

```powershell
python 03-sql/init_db.py
```

进入交互查询：

```powershell
python -c "import sqlite3; c=sqlite3.connect('03-sql/shop.db'); [print(r) for r in c.execute('SELECT * FROM users')]"
```

推荐装个可视化工具看得更舒服：**DB Browser for SQLite**（免费，官网直接下载）。

表结构：
- `users(id, name, city, reg_date)`
- `products(id, name, price, category, stock)`
- `orders(id, user_id, status, amount, created_at)`
- `order_items(id, order_id, product_id, quantity)`

---

## 题目（先自己做，再对答案）

### 基础
1. 查询所有「北京」的用户姓名。
2. 查询价格大于 500 的商品名称和价格，按价格降序排列。
3. 查询库存为 0 的商品（售罄）。
4. 查询姓「张」的用户（`LIKE`）。

### 聚合
5. 统计每个城市的用户数量。
6. 统计 `paid` 状态的订单数量和总金额。
7. 统计每个分类的商品数量和平均价格。

### 多表联查 JOIN
8. 查询所有已支付订单：用户姓名 + 订单金额（INNER JOIN）。
9. 查询每个用户的订单数量（**包含没有下单的用户**，用 LEFT JOIN）。
10. 查询每个商品的总销量（JOIN `order_items` + GROUP BY）。
11. 查询从未下过单的用户（`LEFT JOIN ... IS NULL` 或 `NOT IN`）。
12. 查询下单次数 ≥ 2 的用户（`GROUP BY` + `HAVING`）。

### 子查询
13. 查询单笔订单金额最高的用户姓名。
14. 查询价格高于「外设」分类平均价格的商品。

---

## 答案

<details>
<summary>点开查看答案</summary>

```sql
-- 1
SELECT name FROM users WHERE city = '北京';

-- 2
SELECT name, price FROM products WHERE price > 500 ORDER BY price DESC;

-- 3
SELECT name FROM products WHERE stock = 0;

-- 4
SELECT * FROM users WHERE name LIKE '张%';

-- 5
SELECT city, COUNT(*) AS cnt FROM users GROUP BY city;

-- 6
SELECT COUNT(*) AS order_cnt, SUM(amount) AS total FROM orders WHERE status = 'paid';

-- 7
SELECT category, COUNT(*) AS cnt, AVG(price) AS avg_price FROM products GROUP BY category;

-- 8
SELECT u.name, o.amount
FROM orders o
JOIN users u ON o.user_id = u.id
WHERE o.status = 'paid';

-- 9
SELECT u.name, COUNT(o.id) AS order_cnt
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;

-- 10
SELECT p.name, SUM(oi.quantity) AS sold
FROM products p
JOIN order_items oi ON p.id = oi.product_id
GROUP BY p.id, p.name
ORDER BY sold DESC;

-- 11
SELECT u.name
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;

-- 12
SELECT u.name, COUNT(o.id) AS cnt
FROM users u
JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name
HAVING COUNT(o.id) >= 2;

-- 13
SELECT u.name
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.amount = (SELECT MAX(amount) FROM orders);

-- 14
SELECT name, price FROM products
WHERE price > (SELECT AVG(price) FROM products WHERE category = '外设');
```

</details>

---

## 索引（面试必背，用嘴说就行）

```sql
-- 建索引
CREATE INDEX idx_orders_user ON orders(user_id);
-- 看执行计划
EXPLAIN QUERY PLAN SELECT * FROM orders WHERE user_id = 1;
```

必背要点：

| 问题 | 答案要点 |
|---|---|
| 索引用什么结构 | B+ 树（层数少、磁盘 IO 少；叶子节点有链表，适合范围查询） |
| 聚簇 vs 非聚簇 | 聚簇索引叶子节点存整行数据（InnoDB 主键）；非聚簇存主键值，需回表 |
| 最左前缀原则 | 联合索引 `(a,b,c)` 必须从 a 开始匹配，跳字段则后面的索引失效 |
| 优点 | 加快查询、加快排序/分组、加快表连接 |
| 缺点 | 占磁盘空间；增删改要维护索引，**写多读少的表不宜建太多索引** |
| 什么时候失效 | 对列做函数运算、`LIKE '%xx'` 前置通配符、隐式类型转换、违反最左前缀 |

口述版（30 秒）：
> 索引类似书的目录，MySQL InnoDB 用 B+ 树实现，层数低所以磁盘 IO 少，叶子节点用链表相连方便范围扫描。主键是聚簇索引，二级索引叶子存主键值需要回表。优点是加速查询，代价是占空间、拖慢写入，所以写多读少的表要少建。联合索引要遵守最左前缀，遇到函数运算或 `%` 开头的 like 会失效。
