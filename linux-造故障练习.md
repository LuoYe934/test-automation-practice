# Linux 造故障练习（5 个配方）

> 原理：排障的第一能力是知道"正常"长什么样。别对着空气敲命令——**自己制造故障，再用命令抓它**。
> 环境：VMware 虚拟机（Ubuntu/CentOS 均可）。每完成一个配方，把命令和输出记到 Day0 答案的订正版里。

## 配方 1：CPU 打满（练 Day0 卷 Q1）

```bash
# 造故障：开 4 个死循环进程把 CPU 吃满
yes > /dev/null &
yes > /dev/null &
yes > /dev/null &
yes > /dev/null &

# 抓故障：完整排查链路
top                      # 1. 看 CPU 使用率和占用最高的进程 PID（按 P 按 CPU 排序）
ps -ef | grep yes        # 2. 确认是哪个进程
top -H -p <PID>          # 3. 看该进程内的线程
cat /proc/<PID>/status | grep Threads   # 线程数

# 收尾：清理
kill %1 %2 %3 %4         # 或 pkill yes
```

**复盘要点**：如果这是 Java 进程，下一步该干什么？（`jstack <PID>` 看线程栈——面试常追问）

## 配方 2：大文件与 find（练 Q2）

```bash
# 造故障：造一个 500MB 的文件
dd if=/dev/zero of=/tmp/big.file bs=1M count=500

# 抓故障：找出 /var/log 下 7 天内修改过且大于 100MB 的文件
find /var/log -mtime -7 -size +100M
find /tmp -size +100M        # 先在 /tmp 上练手

# Dry-run 好习惯：先打印确认，再删（-delete 放最后）
find /tmp -size +100M -print
# 确认无误后再：
# find /tmp -size +100M -delete
```

**复盘要点**：为什么 `-delete` 要放在命令最后？直接删生产文件前应该做什么？（先 -print 确认清单）

## 配方 3：端口占用（练 Q4）

```bash
# 造故障：起两个服务抢同一个端口
python3 -m http.server 8080 &      # 第一个成功
python3 -m http.server 8080        # 第二个报错：Address already in use

# 抓故障
ss -ltnp | grep 8080               # 看端口被哪个 PID 占了（老系统用 netstat -ltnp）
lsof -i :8080                      # 另一种查法

# 解决
kill <PID>                          # 确认不重要后再杀
```

**复盘要点**：`ss -ltnp` 五个字母分别是什么含义？（ listening / tcp / numeric / program ）

## 配方 4：crontab 定时任务（练 Q5）

```bash
crontab -e                          # 加入下面一行（每分钟写一次时间戳）
* * * * * date >> /tmp/cron.log

# 验证：等 60-70 秒
cat /tmp/cron.log                   # 应该每分钟多一行

# 查看与清理
crontab -l
crontab -r                          # 删除全部（谨慎）
```

**复盘要点**：标准答案格式——`0 2 * * * /opt/backup.sh >> /var/log/backup.log 2>&1`，能解释每一段吗？

## 配方 5：load 高但 CPU 低（练 Q3，最有意思的一个）

```bash
# 造故障：疯狂读写磁盘制造 IO 等待
dd if=/dev/zero of=/tmp/ioheavy bs=1M count=20000 &

# 观察：另开一个终端
uptime                              # load average 第一个数会往上爬
top                                 # 注意看 %wa（iowait）那一行——CPU 使用率不高但 load 高
```

**复盘要点**：load average 三个数 = 最近 1/5/15 分钟的平均负载（等待 CPU + 等待磁盘 IO 的任务数）。
**load 高 + CPU 低 = 大量任务卡在磁盘 IO 上**（D 状态进程），查法：`iostat -x 1` 或 `ps -eo state,pid,cmd | grep "^D"`。

---

## 完成标准

- [ ] 5 个配方全部亲手跑过，命令输出截图/贴入订正版
- [ ] 能脱稿说出 Q1 的完整排查链路：top → 定位 PID → 分用户态/内核态 → 线程 → 代码/日志
- [ ] 能解释 502 vs 504（网关收到无效响应 vs 网关等上游超时）——这是 Day0 卷里你空着的题，补上
