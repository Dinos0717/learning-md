# Git 命令行 1——从克隆到四种后悔药

> 基于陈泽鹏老师视频课程整理编写 · 2026年6月27日

---

## 目录

- [一、课程背景与目标](#一课程背景与目标)
- [二、环境准备——确认 Git 已安装](#二环境准备确认-git-已安装)
- [三、git clone——克隆仓库](#三git-clone克隆仓库)
- [四、git status——最重要的命令](#四git-status最重要的命令)
- [五、git add——将文件加入暂存区](#五git-add将文件加入暂存区)
- [六、git commit——提交更改](#六git-commit提交更改)
- [七、git push——推送到远端](#七git-push推送到远端)
  - [7.1 普通推送](#71-普通推送)
  - [7.2 GitHub 认证（Token 方式）](#72-github-认证token-方式)
- [八、git pull——拉取远端更新](#八git-pull拉取远端更新)
  - [8.1 git pull（普通方式）](#81-git-pull普通方式)
  - [8.2 git pull --rebase（推荐方式）](#82-git-pull---rebase推荐方式)
  - [8.3 Push Rejected 的完整解决流程](#83-push-rejected-的完整解决流程)
- [九、git rm / git mv——删除与移动文件](#九git-rm--git-mv删除与移动文件)
- [十、git log——查看提交历史](#十git-log查看提交历史)
- [十一、git show——查看提交详情](#十一git-show查看提交详情)
- [十二、Git 的四种后悔药](#十二git-的四种后悔药)
  - [12.1 Discard（丢弃修改）](#121-discard丢弃修改)
  - [12.2 Reset（撤回提交）](#122-reset撤回提交)
  - [12.3 Revert（反向提交）](#123-revert反向提交)
  - [12.4 Amend（修正最近提交）](#124-amend修正最近提交)
- [十三、命令速查表](#十三命令速查表)
- [十四、课后练习](#十四课后练习)
- [十五、课程小结](#十五课程小结)

---

## 一、课程背景与目标

### 1.1 前情回顾

在前面课程中，你已经通过 GitHub Desktop 和 IntelliJ IDEA 掌握了 Git 的所有核心操作。**现在你已经能完成 99% 跟 Git 相关的工作了。**

但命令行是一种更原始、更纯粹的操作方式。学会命令行有三个好处：

```
┌─────────────────────────────────────────────────────────┐
│          为什么要学 Git 命令行？                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1️⃣  不依赖工具                                          │
│      ├── 任何电脑只要装了 Git 就能操作                   │
│      ├── 不需要安装 Desktop 或 IDEA                      │
│      └── 服务器上只能用命令行（没有图形界面）            │
│                                                         │
│  2️⃣  理解更深入                                          │
│      ├── 每个命令背后对应一个 Git 概念                   │
│      └── 用命令行操作一遍 = 复习一遍 Git 原理            │
│                                                         │
│  3️⃣  排错更高效                                          │
│      ├── 图形界面报错时，错误信息往往不够详细            │
│      └── 命令行的错误输出直接告诉你问题在哪              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 1.2 本课要掌握的目标

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  目标一：掌握 Git 的日常基础命令                           │
│         ├── clone / status / add / commit / push / pull │
│         └── 熟练使用 git status 判断当前状态             │
│                                                         │
│  目标二：掌握 Push Rejected 的正确处理方式                │
│         ├── git pull --rebase（保持历史线性干净）        │
│         └── 理解为什么推荐 rebase 而非 merge             │
│                                                         │
│  目标三：掌握 Git 的四种"后悔药"                         │
│         ├── Discard：丢弃未提交的修改                    │
│         ├── Reset：撤回已提交的 commit                   │
│         ├── Revert：安全地撤销（生成反向提交）           │
│         └── Amend：修正最近一次提交                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 二、环境准备——确认 Git 已安装

### 2.1 检查 Git 版本

```bash
git --version
```

```
如果输出类似以下内容 → Git 已安装 ✅
git version 2.45.0

如果没有 → 需要安装 Git
```

### 2.2 安装 Git

```
如果你之前安装过 GitHub Desktop 或 IntelliJ IDEA，
电脑上应该自动就有了 Git。

如果没有，去官网下载：
https://git-scm.com

├── Windows：下载 64-bit 安装包，双击安装
├── Mac：下载 .dmg 或 brew install git
└── Linux：sudo apt install git（Ubuntu）/ sudo yum install git（CentOS）
```

---

## 三、git clone——克隆仓库

```bash
# 语法
git clone <仓库地址>

# 示例
git clone https://github.com/用户名/git-test.git
```

```
执行后：
├── Git 在本地创建一个与仓库同名的文件夹
├── 下载所有文件和历史记录
└── 自动设置 origin 指向克隆的远端地址

进入项目：
cd git-test
```

---

## 四、git status——最重要的命令

> **git status 是 Git 中最重要的命令。** 它告诉你：你在哪个分支、改了什么文件、文件处于什么状态、下一步该做什么。

```bash
git status
```

```
输出示例：

On branch main                          ← 当前在 main 分支
Your branch is up to date with 'origin/main'.  ← 与远端同步

Changes not staged for commit:          ← 有修改但未暂存
  (use "git add <file>..." to update what will be committed)
        modified:   test5.py
        modified:   test6.py

Untracked files:                        ← 新文件，未被 Git 管理
  (use "git add <file>..." to include in what will be committed)
        new_file.py

no changes added to commit              ← 没有已暂存的更改
```

```
git status 能告诉你的信息：

┌─────────────────────────────────────────────────────────┐
│                                                         │
│  1️⃣  你在哪个分支？        → On branch main              │
│  2️⃣  分支与远端是否同步？  → up to date / ahead / behind │
│  3️⃣  哪些文件被修改了？    → modified: xxx               │
│  4️⃣  哪些文件是新创建的？  → Untracked files: xxx        │
│  5️⃣  哪些文件已暂存？      → Changes to be committed     │
│  6️⃣  下一步该做什么？      → (use "git add ...")         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

> 💡 **最佳实践**：每执行一个 Git 操作前后，都用 `git status` 确认当前状态。这能避免 90% 的操作失误。

---

## 五、git add——将文件加入暂存区

### 5.1 添加单个文件

```bash
git add <文件名>

# 示例
git add test6.py
```

### 5.2 添加所有文件

```bash
git add .
# . 表示当前目录下所有改动的文件
# 注意：.gitignore 中排除的文件不会被添加
```

### 5.3 从暂存区移除

```bash
# 把文件从暂存区取出（保留工作区的修改）
git restore --staged <文件名>

# 示例
git restore --staged test5.py
```

```
工作区 → 暂存区 → 本地仓库 的流转：

工作区（红色 modified/untracked）
    │  git add <文件名>  或  git add .
    ▼
暂存区（绿色 Changes to be committed）
    │  git commit -m "message"
    ▼
本地仓库（已提交）
    │  git push
    ▼
远端仓库（GitHub）
```

---

## 六、git commit——提交更改

### 6.1 普通提交

```bash
git commit -m "提交信息"

# 示例
git commit -m "add file test6"
```

### 6.2 跳过 git add 直接提交（仅限已追踪的文件）

```bash
# -a = 自动把所有已追踪的修改加入暂存区
# -m = 指定 commit message
git commit -am "提交信息"

# 示例
git commit -am "update test5 and test6"
```

> ⚠️ **注意**：`git commit -am` 只会自动添加**已被 Git 管理的文件**的修改。新建的文件（Untracked）还是需要先 `git add`。

```
git add + git commit 的三种方式：

方式一（标准两步）：
git add test6.py
git commit -m "add test6"

方式二（添加所有再提交）：
git add .
git commit -m "update all files"

方式三（快捷方式，仅已追踪文件）：
git commit -am "update tracked files"
```

---

## 七、git push——推送到远端

### 7.1 普通推送

```bash
git push

# 或指定远端和分支
git push origin main
```

### 7.2 GitHub 认证（Token 方式）

> ⚠️ 如果你之前没登录过 GitHub，首次 push 会弹出认证窗口。

```
认证方式一：浏览器登录
弹出窗口 → 点击蓝色按钮 → 浏览器授权 GitHub → 完成

认证方式二：Token 登录
Step 1: GitHub 网页 → 右上角头像 → Settings
Step 2: 左侧菜单 → Developer settings → Personal access tokens
Step 3: Tokens (classic) → Generate new token (classic)
Step 4: 选择过期时间、勾选全部权限 → Generate token
Step 5: 复制生成的 Token（只显示一次！）
Step 6: 回到命令行，把 Token 粘贴到密码框 → Sign in
```

---

## 八、git pull——拉取远端更新

### 8.1 git pull（普通方式）

```bash
git pull
# 等价于：git fetch + git merge
```

```
git pull 的执行过程：
1. git fetch：从远端拉取最新提交到本地（不合并）
2. git merge：把远端的提交合并到当前分支

结果：可能会产生一个额外的 Merge 提交
```

### 8.2 git pull --rebase（推荐方式）

```bash
git pull --rebase
# 等价于：git fetch + git rebase
```

```
git pull --rebase 的执行过程：

1. 先把你的本地提交"暂存"到一边
2. 从远端拉取最新提交
3. 把你的提交"挂"到远端提交之后

效果：
变前：                         变后：
远端：A → B → C（同事的）       远端：A → B → C（同事的）
本地：A → B → D（你的）         本地：A → B → C → D'（你的）
                                        ↑ 线性！无额外 Merge 提交
```

```
git pull vs git pull --rebase：

git pull（merge 方式）：
├── 产生额外的 Merge 提交
├── 历史树出现分叉
└── 多人频繁 pull 会造成提交历史非常杂乱

git pull --rebase（推荐）：
├── 不产生额外提交
├── 历史保持一条直线
└── 提交记录清晰可读 ✅
```

### 8.3 Push Rejected 的完整解决流程

> 这是多人协作中最高频的问题——同事先 push 了，你的 push 被拒绝。

```
场景还原：

你 和 同事 都在 main 分支上开发
├── 同事先写完 → commit → push 到远端 ✅
└── 你后写完 → commit → push → ❌ Rejected！

原因：远端有你的本地没有的新提交

解决流程：
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Step 1: 先拉取远端的更新                                │
│  git pull --rebase                                      │
│  （推荐用 --rebase，保持历史线性）                       │
│                                                         │
│  Step 2: 如果有冲突，解决冲突                            │
│  编辑冲突文件 → git add → git rebase --continue         │
│                                                         │
│  Step 3: 再次 push                                      │
│  git push                                               │
│  （pull --rebase 之后不需要 force push）                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

```
为什么推荐使用独立分支开发？

┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Git 最佳实践：每个人使用独立的分支开发代码               │
│                                                         │
│  这样做的好处：                                          │
│  ├── 不会出现 Push Rejected（各自分支不冲突）            │
│  ├── 代码隔离，互不影响                                  │
│  └── 通过 PR 合并，有 Code Review 环节                   │
│                                                         │
│  但也有例外：                                            │
│  └── 两个人需要共同解决同一个分支上的疑难问题             │
│      → 这时才会出现 Push Rejected                       │
│      → 用 git pull --rebase 解决                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 九、git rm / git mv——删除与移动文件

### 9.1 删除文件

```bash
# 方式一：先手动删除，再用 git rm 告诉 Git
rm test6.py          # 从文件系统中删除
git rm test6.py      # 告诉 Git 这个文件不再需要管理
git commit -m "delete test6.py"

# 方式二：直接用 git rm（删除 + 暂存一步完成）
git rm test6.py
git commit -m "delete test6.py"
```

### 9.2 移动文件

```bash
# 语法：git mv <源文件> <目标路径>
git mv test4.py test/test4.py
# 把 test4.py 移动到 test/ 文件夹下

git commit -m "move test4.py to test folder"
```

### 9.3 重命名文件

```bash
# 语法：git mv <旧名称> <新名称>
git mv test3.py test2.py
# 把 test3.py 重命名为 test2.py

git commit -m "rename test3.py to test2.py"
```

```
git rm 和 git mv 的共同特点：

├── 操作会自动添加到暂存区
├── git status 能看到 "renamed" 或 "deleted" 状态
└── 最后都需要 git commit 提交
```

---

## 十、git log——查看提交历史

```bash
git log
```

```
输出示例：

commit abc123def456... (HEAD -> main, origin/main)
Author: Dinos0717 <email@example.com>
Date:   2026-06-27 21:00:00

    add file test6

commit def789abc012...
Author: Dinos0717 <email@example.com>
Date:   2026-06-27 20:00:00

    update test5

每一条记录包含：
├── commit id（40位哈希值）→ 用于 reset/revert/show 等操作
├── Author（作者）
├── Date（提交时间）
└── commit message（提交信息）
```

```
操作技巧：
├── 按 Q 键退出 log 查看状态
├── 上下箭头 / PageUp/PageDown 翻页
└── 复制 commit id 时，前 7-8 位就够用了
```

---

## 十一、git show——查看提交详情

```bash
# 查看某次提交的详细信息（包括具体代码改动）
git show <commit-id>

# 示例
git show abc123de
```

```
输出内容：
├── 提交信息（作者、日期、message）
└── diff 差异内容
    ├── 绿色 + = 新增的行
    └── 红色 - = 删除的行
```

---

## 十二、Git 的四种后悔药

### 12.1 Discard（丢弃修改）

> **场景**：修改了代码但还没 commit，想全部撤销。

```bash
# 丢弃单个文件的修改
git restore <文件名>

# 丢弃所有文件的修改
git restore .

# 示例
git restore test5.py
```

```
Discard 的效果：
工作区修改 → git restore → 恢复到最近一次 commit 的状态

对应 Desktop 操作：右键文件 → Discard Changes
```

### 12.2 Reset（撤回提交）

> **场景**：commit 了但后悔了，想回退到之前的某个状态。

```bash
# 语法（--mixed 是默认模式，最常用）
git reset --mixed <commit-id>

# 示例：回退到倒数第二次提交
git log                          # 先查看提交历史，复制目标 commit id
git reset --mixed def789ab       # 回退（保留改动在本地）
```

```
Reset 的三种模式（复习）：

--mixed（默认，推荐）：
├── 撤销 commit + 暂存区
├── 改动保留在工作区（文件还在磁盘上）
└── 可以重新 add + commit

--soft：
├── 只撤销 commit
├── 改动保留在暂存区（绿色，可以直接 commit）
└── 适用：想重新整理提交信息

--hard（危险！）：
├── 全部丢弃
└── 改动不在工作区，不在暂存区 → 无法恢复！

推荐：日常使用 --mixed，确定不要代码时才用 --hard
```

```
⚠️ Reset 注意事项：

1. Reset 之后需要 Force Push 才能推送到远端
   git push -f

2. 绝不要在共享分支（main/develop）上 Force Push！
   → 会覆盖同事的提交

3. 已推送到远端的提交 → 用 Revert 替代 Reset
```

### 12.3 Revert（反向提交）

> **场景**：想撤销某次 commit，但保留完整的提交历史。**最安全的方式。**

```bash
# 语法
git revert <commit-id>

# 示例
git revert abc123de
```

```
Revert 的执行过程：

1. Git 打开编辑器（vim），让你确认 commit message
2. 默认 message："Revert '原来的message'"
3. 按 ESC → 输入 :wq! → 回车（保存并退出 vim）
4. 生成一个新的"反向提交"，抵消目标提交的改动
5. git push 推送到远端

效果：
原提交：添加了一行 "hello"
Revert：删除那一行 "hello"（反向操作）
历史中两次提交都在 → 安全可追溯 ✅
```

```
Revert vs Reset：

Revert（推荐用于共享分支）：
├── 不删除历史
├── 生成新的反向提交
├── 普通 push 即可
└── 适合已 Push 的提交

Reset（推荐用于个人分支）：
├── 删除历史（回退指针）
├── 需要 Force Push
└── 适合未 Push 的本地提交
```

### 12.4 Amend（修正最近提交）

> **场景**：刚 commit 完，发现有 typo 或漏了文件，想修正最近一次提交。

```bash
# Step 1: 修改代码
# （在编辑器中修改）

# Step 2: 加入暂存区
git add <修改的文件>

# Step 3: Amend 修正
git commit --amend

# 在 vim 编辑器中修改 commit message（如果需要）
# ESC → :wq! → 回车
```

```
Amend 的效果：
├── 不会产生新的 commit
├── 最近一次 commit 的内容和 message 被更新
└── commit id 会改变（因为内容变了）

⚠️ Amend 注意事项：

1. 只能修改最近一次 commit！

2. 未 Push 的 Amend：
   普通 git push 即可 ✅

3. 已 Push 的 Amend：
   必须 Force Push ❌（不推荐！）
   → 已 Push 的提交不要 Amend，用 Revert
```

### 12.5 四种后悔药总结

| 操作 | 命令 | 修改范围 | 是否产生新提交 | 已 Push 能否用 | 适用场景 |
|---|---|---|---|---|---|
| **Discard** | `git restore <file>` | 未 commit 的修改 | ❌ | N/A | 改错了，还没 commit |
| **Reset** | `git reset --mixed <id>` | 任意 commit | ❌（删除历史） | 需 Force Push | 个人分支撤回 |
| **Revert** | `git revert <id>` | 任意 commit | ✅（反向提交） | ✅ 安全 | **共享分支撤销** |
| **Amend** | `git commit --amend` | 最近一次 commit | ❌（修改最近） | 需 Force Push | 刚 commit 发现遗漏 |

```
选择决策：

改错了，还没 commit？
    └── Discard（git restore）

commit 了，但没 push？
    ├── 小修小补 → Amend
    └── 完全撤回 → Reset --mixed

已经 push 到远端了？
    ├── 个人分支 → Reset + Force Push
    └── 共享分支 → Revert（唯一安全的方式）
```

---

## 十三、命令速查表

| 操作 | 命令 | 说明 |
|---|---|---|
| 查看版本 | `git --version` | 确认 Git 已安装 |
| 克隆仓库 | `git clone <url>` | 下载远程仓库到本地 |
| **查看状态** | **`git status`** | **最重要！随时查看当前状态** |
| 加入暂存区 | `git add <file>` / `git add .` | 单个文件 / 所有文件 |
| 提交 | `git commit -m "msg"` | 标准提交 |
| 提交（免 add） | `git commit -am "msg"` | 只对已追踪文件生效 |
| 推送 | `git push` | 推送到远端 |
| 强制推送 | `git push -f` | ⚠️ 慎用！ |
| 拉取（merge） | `git pull` | fetch + merge |
| **拉取（rebase）** | **`git pull --rebase`** | **推荐！保持历史线性** |
| 删除文件 | `git rm <file>` | 删除 + 暂存一步完成 |
| 移动/重命名 | `git mv <old> <new>` | 移动 + 暂存一步完成 |
| 查看历史 | `git log` | 按 Q 退出 |
| 查看提交详情 | `git show <commit-id>` | 查看某次提交的改动 |
| 丢弃修改 | `git restore <file>` | Discard / Rollback |
| 撤回提交 | `git reset --mixed <id>` | 默认模式，保留本地改动 |
| 反向提交 | `git revert <id>` | 安全撤销，生成新提交 |
| 修正提交 | `git commit --amend` | 仅最近一次 |

---

## 十四、课后练习

### 练习一：基础——命令行动手全流程

**题目**：完全不使用 GitHub Desktop，只用命令行完成以下操作。

**要求**：
1. `git clone` 克隆你的一个仓库
2. 新建一个文件 → `git add` → `git commit` → `git push`
3. 修改一个文件 → `git status` 确认状态 → `git commit -am` → `git push`
4. 在 GitHub 网页端修改一个文件（模拟同事更新）
5. `git pull --rebase` 拉取更新
6. 每一步都用 `git status` 确认状态

### 练习二：进阶——Push Rejected 模拟

**题目**：模拟两人同时修改同一分支导致 Push Rejected 的场景。

**要求**：
1. 用两个本地文件夹（或两个账号）模拟两个开发者
2. 开发者 A：修改文件 → commit → push（先 push 成功）
3. 开发者 B：修改文件 → commit → push（被拒绝！）
4. 开发者 B：`git pull --rebase` → 再次 push
5. 用 `git log` 查看提交历史，确认是线性的一条线

### 练习三：综合——四种后悔药实操

**题目**：分别练习 Discard、Reset、Revert、Amend 四种操作。

**要求**：
1. Discard：修改文件 → `git restore` 丢弃 → 验证文件恢复
2. Reset：做 3 次 commit → `git reset --mixed` 回退到第 1 次 → 验证 commit 消失但文件还在
3. Revert：做 1 次 commit 并 push → `git revert` 撤销 → 验证生成了反向提交
4. Amend：做 1 次 commit → 发现有 typo → `git commit --amend` 修正 → 验证 commit 被更新

---

## 十五、课程小结

### 15.1 核心知识图谱

```
┌────────────────────────────────────────────────────────────┐
│        Git 命令行 1——核心知识体系                              │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  日常基础命令                                           │
│      ├── git status：最重要的命令，随时查看状态              │
│      ├── git clone：克隆仓库                                 │
│      ├── git add / commit / push：暂存→提交→推送           │
│      └── git pull --rebase：拉取更新（保持线性历史）        │
│                                                            │
│  2️⃣  Push Rejected 处理                                      │
│      ├── 原因：同事先 push 了                                │
│      ├── 解决：git pull --rebase → git push                │
│      └── 预防：每个人用独立分支开发                          │
│                                                            │
│  3️⃣  文件操作                                               │
│      ├── git rm：删除文件（自动暂存）                        │
│      ├── git mv：移动/重命名（自动暂存）                     │
│      └── git log / git show：查看历史和详情                  │
│                                                            │
│  4️⃣  四种后悔药                                             │
│      ├── Discard：git restore（未 commit 的修改）           │
│      ├── Reset：git reset --mixed（个人分支撤回）           │
│      ├── Revert：git revert（共享分支安全撤销）             │
│      └── Amend：git commit --amend（修正最近提交）          │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 15.2 一句话总结

> **Git 命令行是 Git 最原始、最纯粹的操作方式。核心就 6 个基础命令（clone/status/add/commit/push/pull）加 4 种后悔药（restore/reset/revert/amend）。git status 是你最好的朋友——每步操作前后都用它确认状态，能避免 90% 的失误。**

### 15.3 系列课程定位

```
┌─────────────────────────────────────────────────────────┐
│              GitHub 系列课程                               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  第1-13课：GitHub Desktop + IDEA + 概念（已完成）         │
│                                                         │
│  第14课（本课）：Git 命令行 1——基础命令 + 四种后悔药       │
│         ← 你在这里                                       │
│                                                         │
│  第15课：Git 命令行 2——分支操作 + 冲突解决 + 高级技巧     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

*本教学文档基于陈泽鹏老师视频课程整理编写 · 2026年6月27日*
