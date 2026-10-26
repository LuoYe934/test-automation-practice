# Git 练习（本地即可完成，不需要队友）

目标：不是背命令，而是**留下连续 14 天的提交记录**——面试官会真的点开你的 GitHub 看。

## 第 1 步：初始化并做第一次提交

```powershell
cd c:/Users/LY/Projects/test-8week
git init
git config user.name "你的名字"
git config user.email "你的邮箱"

# .gitignore 先写好，避免把 .db / __pycache__ 传上去
git add .
git commit -m "chore: 初始化测试练习项目"
```

`.gitignore` 建议内容（已帮你建好同名文件，可自行补充）：

```
__pycache__/
.pytest_cache/
*.db
.venv/
allure-results/
```

## 第 2 步：每天练习的命令

```powershell
git status                  # 看改了哪些文件
git diff                    # 看具体改了什么
git add 01-selenium         # 只提交当天学的目录
git commit -m "test: 补充登录反向用例"
git log --oneline           # 看提交历史
```

提交信息规范（面试加分）：`feat:` 新功能 / `test:` 用例 / `fix:` 修复 / `docs:` 文档 / `chore:` 杂项。

## 第 3 步：分支与合并

```powershell
git checkout -b feature/api-test     # 新建并切换分支
# ... 写完接口用例 ...
git add . && git commit -m "feat: 接口测试用例"
git checkout main
git merge feature/api-test           # 合并回来
git branch -d feature/api-test       # 删掉已合并分支
```

## 第 4 步：亲手制造并解决一次冲突（重要）

```powershell
git checkout -b conflict-a
# 把 README.md 第 1 行改成 AAAAA，提交
git commit -am "docs: A 分支改动"

git checkout main
git checkout -b conflict-b
# 把 README.md 第 1 行改成 BBBBB，提交
git commit -am "docs: B 分支改动"

git checkout main
git merge conflict-a        # 成功
git merge conflict-b        # 报 CONFLICT
```

打开冲突文件，会看到：

```
<<<<<<< HEAD
AAAAA
=======
BBBBB
>>>>>>> conflict-b
```

手动改成想要的内容，删掉这些标记，然后：

```powershell
git add README.md
git commit -m "fix: 解决 README 合并冲突"
```

## 第 5 步：推送到 GitHub

```powershell
# GitHub 网页上新建空仓库（不要勾 README），然后：
git remote add origin https://github.com/<你的用户名>/<仓库名>.git
git branch -M main
git push -u origin main
```

之后每天：`git push`

## 常用急救命令

| 场景 | 命令 |
|---|---|
| 改错了但还没 add | `git checkout -- 文件名` |
| 已经 add 了想撤销 | `git restore --staged 文件名` |
| 上一次 commit 信息写错 | `git commit --amend -m "新信息"` |
| 想临时存一下改动 | `git stash` / `git stash pop` |
| 看某行是谁改的 | `git blame 文件名` |
