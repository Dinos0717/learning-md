# Git 命令行 2——分支操作与冲突解决

> 基于陈泽鹏老师视频课程整理编写 · 2026年6月27日

---

## 目录

- [一、课程背景与目标](#一课程背景与目标)
- [二、分支管理](#二分支管理)
  - [2.1 查看分支](#21-查看分支)
  - [2.2 创建分支](#22-创建分支)
  - [2.3 推送分支到远端](#23-推送分支到远端)
  - [2.4 切换分支](#24-切换分支)
  - [2.5 删除分支](#25-删除分支)
  - [2.6 从远端拉取分支到本地](#26-从远端拉取分支到本地)
- [三、分支合并——Fast Forward 深度解析](#三分支合并fast-forward-深度解析)
  - [3.1 什么是 Fast Forward](#31-什么是-fast-forward)
  - [3.2 Non Fast Forward 合并](#32-non-fast-forward-合并)
  - [3.3 强制 Non Fast Forward 合并（--no-ff）](#33-强制-non-fast-forward-合并--no-ff)
  - [3.4 三种合并方式对比](#34-三种合并方式对比)
- [四、Rebase——变基操作](#四rebase变基操作)
  - [4.1 命令行 Rebase](#41-命令行-rebase)
  - [4.2 Rebase 后何时需要 Force Push](#42-rebase-后何时需要-force-push)
- [五、分支对比——log 与 diff](#五分支对比log-与-diff)
  - [5.1 git log 比较提交](#51-git-log-比较提交)
  - [5.2 git diff 比较文件](#52-git-diff-比较文件)
- [六、Squash Merge——压缩合并](#六squash-merge压缩合并)
- [七、冲突解决](#七冲突解决)
  - [7.1 Merge 冲突解决](#71-merge-冲突解决)
  - [7.2 Rebase 冲突解决](#72-rebase-冲突解决)
- [八、Cherry Pick——拣选提交](#八cherry-pick拣选提交)
- [九、命令速查表](#九命令速查表)
- [十、课后练习](#十课后练习)
- [十一、课程小结](#十一课程小结)

---

## 一、课程背景与目标

### 1.1 前情回顾

上节课（Git 命令行 1）你掌握了 Git 的**基础命令**（clone/status/add/commit/push/pull）和**四种后悔药**（restore/reset/revert/amend）。这些是"单人操作"——你在自己的分支上修改、提交、撤回。

> 本课进入 Git 命令行**最核心的领域**：分支操作。这是多人协作的基础，也是 Git 作为分布式版本控制系统最强大的能力所在。

### 1.2 本课要掌握的目标

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  目标一：掌握分支的全生命周期管理                           │
│         ├── 创建/切换/推送/删除/拉取远端分支              │
│         └── 熟练使用 git branch -a 查看全部分支           │
│                                                         │
│  目标二：深刻理解 Fast Forward 概念                       │
│         ├── Fast Forward 是什么                          │
│         ├── Non Fast Forward 的区别                      │
│         └── --no-ff 的使用场景                           │
│                                                         │
│  目标三：掌握高级合并与冲突解决                            │
│         ├── Squash Merge（压缩合并）                      │
│         ├── Cherry Pick（拣选提交）                       │
│         ├── Merge 冲突解决                                │
│         └── Rebase 冲突解决                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 二、分支管理

### 2.1 查看分支

```bash
# 查看本地分支
git branch

# 查看所有分支（包括远端）
git branch -a
```

```
输出示例：

$ git branch
  feature
  feature2
* main          ← 星号 * 表示当前所在分支

$ git branch -a
* main
  feature
  feature2
  remotes/origin/main        ← 远端分支
  remotes/origin/feature
  remotes/origin/feature2
```

```
分支颜色含义（命令行）：
├── 绿色 = 本地分支
├── 白色 = 远端分支（前面带 remotes/origin/）
└── 带 * 号 = 当前所在分支
```

### 2.2 创建分支

```bash
# 方式一：创建并切换（推荐）
git checkout -b <新分支名>

# 示例：基于当前分支创建 feature2
git checkout -b feature2

# 方式二：只创建，不切换
git branch <新分支名>
```

```
创建分支的关键规则：

新分支基于「当前所在分支」创建！
├── 创建前用 git branch 确认当前在哪个分支
└── 如果想基于 main 创建 → 先 git switch main → 再创建
```

### 2.3 推送分支到远端

```bash
# 推送本地分支到远端，并设置追踪关系
git push --set-upstream origin <分支名>

# 示例
git push --set-upstream origin feature2

# 简短写法
git push -u origin feature2
```

```
--set-upstream 的作用：

把本地分支和远端分支"关联"起来
├── 关联后，直接用 git push/pull 不需要每次指定分支
└── 关联关系保存在 .git/config 中
```

### 2.4 切换分支

```bash
# 方式一：git switch（新命令，推荐）
git switch <分支名>

# 方式二：git checkout（传统命令）
git checkout <分支名>

# 示例
git switch main        # 切换到 main 分支
git switch feature     # 切换到 feature 分支
```

```
git switch vs git checkout：

git switch（Git 2.23+ 新命令）：
├── 专门用于切换分支
├── 语义清晰，不会和"恢复文件"混淆
└── 推荐使用

git checkout（传统命令）：
├── 既可以切换分支，又可以恢复文件
├── 功能多但容易混淆
└── 老版本 Git 的唯一选择
```

### 2.5 删除分支

```bash
# ⚠️ 删除前必须先切换到其他分支！
# （不能删除当前所在的分支）

# 删除本地分支（普通删除）
git branch -d <分支名>

# 删除本地分支（强制删除）
git branch -D <分支名>

# 删除远端分支
git push origin --delete <分支名>
```

```
-d vs -D 的区别：

git branch -d feature2：
├── 安全删除
├── 如果分支未合并 → 给出警告，拒绝删除
└── 这是 Git 的保护机制，防止误删

git branch -D feature2：
├── 强制删除
├── 无论是否合并，直接删除
└── ⚠️ 确认不要这个分支了再用
```

```bash
# ── 完整删除流程示例 ──

# 1. 查看当前在哪个分支
git branch

# 2. 切换到其他分支（不能删自己！）
git switch main

# 3. 删除本地分支
git branch -d feature2

# 4. 删除远端分支
git push origin --delete feature2

# 5. 验证删除成功
git branch -a
```

### 2.6 从远端拉取分支到本地

```
场景：同事在 GitHub 上创建了一个 feature3 分支
      你需要把它拉取到本地

Step 1: 同步远端分支信息
git fetch
# fetch 不会自动同步分支列表，必须手动执行
# 执行后 git branch -a 才能看到新分支

Step 2: 查看远端分支是否出现
git branch -a
# 应该能看到 remotes/origin/feature3

Step 3: 检出到本地
git checkout feature3
# Git 会自动把远端的 feature3 关联到本地
```

```bash
# ── 完整流程 ──

# GitHub 上同事创建了 feature3
# 你本地还不知道

git branch -a
# 看不到 feature3

git fetch
# Fetching origin...
# * [new branch]      feature3  -> origin/feature3

git branch -a
# 出现了！remotes/origin/feature3

git checkout feature3
# Branch 'feature3' set up to track remote branch 'feature3'
# Switched to a new branch 'feature3'

# ✅ 现在你本地就在 feature3 分支上了
```

---

## 三、分支合并——Fast Forward 深度解析

### 3.1 什么是 Fast Forward

> Fast Forward = **快速前进**。当两个分支没有分叉时，合并只需把指针向前移动。

```
Fast Forward 状态（没有分叉）：

main:     A → B → C
                    ↘
feature:              D → E

feature 从 main 的 C 创建后，只有 feature 一个分支有提交
main 没有任何新提交 → 两个分支在一条线上

合并 feature 到 main：
git switch main
git merge feature

结果：
main:     A → B → C → D → E
                         ↑
                    指针直接前移！
                    没有产生新的 merge 提交
```

```bash
# ── Fast Forward 合并演示 ──

# 状态确认
git log --oneline --graph
# * C (main, feature)  ← 两个分支在同一个提交

# 在 feature 上做两次提交
git switch feature
# 修改文件 → commit → 修改文件 → commit
# * D (feature)
# * C (main)

# feature 在 main 前面，没有分叉

# 合并
git switch main
git merge feature
# Fast-forward  ← 出现了这行字！
# main 指针从 C 移到 D ✅
```

### 3.2 Non Fast Forward 合并

> Non Fast Forward = 非快速前进。当两个分支**产生了分叉**时，合并必须创建一个新的 Merge 提交。

```
Non Fast Forward 状态（有分叉）：

main:     A → B → C → D（main 的提交）
                    ↘
feature:              E → F（feature 的提交）

两个分支都各有新提交 → 产生了分叉

合并 feature 到 main：
git switch main
git merge feature

结果：
main:     A → B → C → D ──┐
                    ↘      M（新的 Merge 提交）
feature:              E → F

产生了一个新的 Merge 提交 M！
```

```
Fast Forward vs Non Fast Forward 的核心区别：

Fast Forward（无分叉）：          Non Fast Forward（有分叉）：
main:  A→B→C→D→E (一条线)        main:  A→B→C→D─┐
                                               M (产生新提交)
                                    feature:  E→F─┘

指针前移，不产生新提交            产生新的 Merge 提交
```

### 3.3 强制 Non Fast Forward 合并（--no-ff）

> 即使两个分支处于 Fast Forward 状态，你也可以**强制**生成一个 Merge 提交。

```bash
# --no-ff = no fast forward
# 即使能快速前进，也强制创建一个 Merge 提交

git merge --no-ff <分支名>
```

```
为什么要用 --no-ff？

场景：feature 在 main 前面（Fast Forward 状态）

普通 merge（Fast Forward）：
main:  A → B → C → D → E
    指针前移，看不出"这里发生了一次合并"

--no-ff merge：
main:  A → B → C ──┐
                    M（明显的合并节点）
feature:          D → E

好处：
├── 保留分支的历史痕迹
├── 能一眼看出哪些提交是作为一个 feature 合并进来的
└── 方便以后回滚整个 feature（回退到 M 之前即可）
```

### 3.4 三种合并方式对比

| 方式 | 条件 | 命令 | 产生新提交？ | 效果 |
|---|---|---|---|---|
| **Fast Forward** | 无分叉（默认行为） | `git merge feature` | ❌ 不产生 | 指针前移 |
| **Non Fast Forward** | 有分叉（自动触发） | `git merge feature` | ✅ 产生 Merge 提交 | 拉线合并 |
| **强制 --no-ff** | 即使无分叉也强制 | `git merge --no-ff feature` | ✅ 强制产生 | 保留分支痕迹 |

---

## 四、Rebase——变基操作

### 4.1 命令行 Rebase

```bash
# 先切换到接受变基的分支
git switch <目标分支>

# 执行变基
git rebase <源分支>

# 示例：把 main 的更新 rebase 到 feature 上
git switch feature
git rebase main
```

```
Rebase 的效果：

Rebase 前：
main:     A → B → C → D
                    ↘
feature:              E → F

git switch feature
git rebase main

Rebase 后：
main:     A → B → C → D
                        ↘
feature:                  E' → F'
（E 和 F 被"搬"到了 D 之后）
```

### 4.2 Rebase 后何时需要 Force Push

> ⚠️ **重要认知**：Rebase 之后不是所有情况都需要 Force Push。

```
Rebase 后的 Push 规则：

情况一：Fast Forward 状态（两个分支无分叉）
    Rebase 后 → 普通 git push 即可 ✅
    原因：没有重写远端已有的历史

情况二：Non Fast Forward 状态（两个分支有分叉）
    Rebase 后 → 必须 Force Push！
    原因：commit 被重新生成（E→E'），远端历史被改写

判断方法：
    看你的分支和远端是否有分叉
    git status 会告诉你 "Your branch and 'origin/feature' have diverged"
    → 这就是需要 Force Push 的信号
```

```bash
# ── 需要 Force Push 的情况 ──

git switch feature
git rebase main
# 如果 rebase 重写了提交历史...

git push
# ❌ rejected！

git push -f
# ✅ 强制推送成功
# ⚠️ 只在个人分支上用！
```

---

## 五、分支对比——log 与 diff

### 5.1 git log 比较提交

```bash
# ── 两点比较（有方向）──
# B 有而 A 没有的提交
git log <分支A>..<分支B>

# 示例：main 有而 feature 没有的
git log feature..main

# 反过来：feature 有而 main 没有的
git log main..feature

# ── 三点比较（双向）──
# A 独有的 + B 独有的（两边加起来）
git log <分支A>...<分支B>

# 示例
git log main...feature
```

```
两点（..）vs 三点（...）比较：

假设：
main:     A → B → C → D（red 提交）
                    ↘
feature:              E → F（blue 提交）

git log feature..main：
显示 D（red）→ main 有，feature 没有

git log main..feature：
显示 E、F（blue）→ feature 有，main 没有

git log main...feature：
显示 D（red）+ E、F（blue）→ 两边独有的都显示
```

### 5.2 git diff 比较文件

```bash
# 比较两个分支的文件差异
git diff <分支A>..<分支B>

# 示例：feature 和 main 的文件差异
git diff feature..main

# 反过来比较
git diff main..feature
```

```
git log vs git diff：

git log 比较的是「提交记录」
├── 告诉你：哪些 commit 在这个分支上但不在那个分支上
└── 适合了解"做了什么"

git diff 比较的是「文件内容」
├── 告诉你：两个分支的文件具体哪里不同
├── 绿色 + = 增加的行
└── 红色 - = 删除的行
```

---

## 六、Squash Merge——压缩合并

> Squash Merge 把多个 commit 压缩成**一个 commit** 再合并进来。

```
Squash Merge 的效果：

feature2 有 3 个提交：
Commit 1: "add green"
Commit 2: "add blue"  
Commit 3: "add red"

普通 merge → 3 个提交全部进来
Squash merge → 合并成 1 个提交："squash three into one"
```

```bash
# ── Squash Merge 操作步骤 ──

# Step 1: 先比较一下两个分支的差异
git log feature..feature2
# 看到 feature2 有 3 个额外的提交

# Step 2: 切换到接受合并的分支
git switch feature

# Step 3: 执行 Squash Merge
git merge --squash feature2
# 注意：--squash 只是把改动放到暂存区，不会自动 commit！

# Step 4: 手动提交
git commit -m "squash three commits into one"

# Step 5: 推送到远端
git push
```

```
Squash Merge vs 普通 Merge：

普通 Merge：
feature:  Commit 1 → Commit 2 → Commit 3（3 个 commit 都在）
→ 历史保留了完整细节

Squash Merge：
feature:  单个 Commit（3 个 commit 压缩成 1 个）
→ 历史简洁，但丢失了中间步骤

适用场景：
├── feature 分支上有很多零碎的"fix typo"提交 → Squash
└── 想保留完整开发过程 → 普通 Merge
```

---

## 七、冲突解决

### 7.1 Merge 冲突解决

```bash
# ── 场景：两个分支修改了同一文件的同一行 ──

# 执行合并
git merge feature2
# CONFLICT (content): Merge conflict in test5.py
# Automatic merge failed; fix conflicts and then commit the result.

# Step 1: 查看冲突文件
git status
# both modified:   test5.py

# Step 2: 编辑冲突文件（用 VS Code 或任何编辑器）
# 删除 <<<<<<< ======= >>>>>>> 标记
# 保留想要的内容

# Step 3: 标记冲突已解决
git add test5.py

# Step 4: 查看状态确认
git status
# All conflicts fixed but you are still merging.

# Step 5: 提交
git commit -m "resolve merge conflict"

# Step 6: 推送
git push
```

### 7.2 Rebase 冲突解决

> Rebase 冲突解决的流程和 Merge 类似，但使用了不同的"继续"命令。

```bash
# ── 场景：rebase 时出现冲突 ──

git rebase feature2
# CONFLICT (content): Merge conflict in test5.py
# Resolve all conflicts manually, mark them as resolved with
# "git add <file>", and run "git rebase --continue".
# You can instead skip this commit: run "git rebase --skip".
# To abort: run "git rebase --abort".

# Step 1: 编辑冲突文件
# （和 Merge 冲突解决完全一样）

# Step 2: 标记已解决
git add test5.py

# Step 3: 继续 rebase
git rebase --continue
# 会弹出编辑器让你确认 commit message
# ESC → :wq! → 回车

# Step 4: 如果 rebase 重写了提交，需要 Force Push
git push -f
```

```
Rebase 冲突时的三个选项：

1. git rebase --continue
   ├── 解决完冲突后继续 rebase
   └── 最常用的选项

2. git rebase --skip
   ├── 跳过当前这个有冲突的 commit
   └── 适用：这个 commit 的改动不再需要了

3. git rebase --abort
   ├── 放弃整个 rebase，回到 rebase 之前的状态
   └── 适用：冲突太多太复杂，先放弃，换个方式
```

```
Merge 冲突 vs Rebase 冲突 对比：

Merge 冲突：
├── 一次性处理所有冲突
├── git add → git commit → 完成
└── 如果搞不定 → git merge --abort

Rebase 冲突：
├── 可能多次出现（每次 rebase 一个 commit 都可能冲突）
├── git add → git rebase --continue → 可能还有下一轮
└── 如果搞不定 → git rebase --abort
```

---

## 八、Cherry Pick——拣选提交

> Cherry Pick 让你**只把某几个 commit 拣选到当前分支**，而不是合并整个分支。

```
场景：
feature 分支有 3 个提交：
Commit 1: "add green"
Commit 2: "add blue"  
Commit 3: "add red"

你只想把 "green" 和 "blue" 拣选到 main 分支
"red" 不要
```

```bash
# ── Cherry Pick 操作步骤 ──

# Step 1: 查看要拣选的 commit
git log main..feature
# 记录下想要的 commit id
# 例如：abc123 (green) 和 def456 (blue)

# Step 2: 切换到接受提交的分支
git switch main

# Step 3: 执行 Cherry Pick
git cherry-pick abc123 def456

# 按顺序执行：
# 先 cherry-pick abc123（green）
# 再 cherry-pick def456（blue）
# red 的提交被跳过！

# Step 4: 如有冲突，解决冲突
# git add → git cherry-pick --continue

# Step 5: 推送
git push
```

```
Cherry Pick 的典型场景：

场景 1：跨分支复用
feature-A 上写了一个通用工具函数
feature-B 也需要 → cherry-pick 那一个 commit 过来

场景 2：紧急修复
在 release 分支上发现了一个 bug
修复在 main 上 → cherry-pick 修复 commit 到 release

场景 3：选择性合并
同事的 feature 分支有 10 个 commit
但你只需要其中 2 个
```

---

## 九、命令速查表

| 操作 | 命令 | 说明 |
|---|---|---|
| 查看本地分支 | `git branch` | 当前分支带 * |
| 查看所有分支 | `git branch -a` | 含远端 |
| 创建+切换分支 | `git checkout -b <name>` | 基于当前分支 |
| 切换分支 | `git switch <name>` | 推荐（Git 2.23+） |
| 推送分支到远端 | `git push -u origin <name>` | 设置追踪关系 |
| 删除本地分支 | `git branch -d <name>` | 安全删除 |
| 强制删除本地分支 | `git branch -D <name>` | 忽略未合并警告 |
| 删除远端分支 | `git push origin --delete <name>` | |
| 同步远端分支 | `git fetch` | 获取远端新分支信息 |
| **合并分支** | `git merge <branch>` | Fast Forward 或 Non FF |
| **强制 No FF** | `git merge --no-ff <branch>` | 始终生成 Merge 提交 |
| **变基** | `git rebase <branch>` | 把当前分支变到目标分支后 |
| **压缩合并** | `git merge --squash <branch>` | 多个 commit → 1 个 |
| 比较提交（两点） | `git log A..B` | B 有而 A 没有 |
| 比较提交（三点） | `git log A...B` | A + B 各自独有的 |
| 比较文件 | `git diff A..B` | 文件内容差异 |
| **Cherry Pick** | `git cherry-pick <id1> <id2>` | 拣选特定提交 |
| Rebase 继续 | `git rebase --continue` | 解决冲突后继续 |
| Rebase 放弃 | `git rebase --abort` | 放弃整个 rebase |
| 解决冲突后提交 | `git add .` → `git commit -m "..."` | Merge 冲突标准流程 |

---

## 十、课后练习

### 练习一：基础——分支全生命周期管理

**题目**：只用命令行完成分支的创建→推送→切换→删除全流程。

**要求**：
1. 创建分支 `test-branch` → push 到远端
2. 切换到 `test-branch`，新建一个文件，commit，push
3. 切换回 main，删除本地 `test-branch`
4. 删除远端 `test-branch`
5. 每一步用 `git branch -a` 确认状态

### 练习二：进阶——Fast Forward 与非 FF 对比

**题目**：分别演示 Fast Forward 合并和 `--no-ff` 合并，对比两者的提交历史。

**要求**：
1. 创建 feature 分支，做 2 次 commit
2. main 分支不做任何修改（保持 Fast Forward 状态）
3. 用普通 merge 合并 → `git log --graph` 查看历史
4. 用 `git reset --hard` 回到合并前
5. 用 `--no-ff` 再次合并 → 对比历史差异

### 练习三：综合——Squash + Cherry Pick 组合

**题目**：在一个 feature 分支上做 5 个零碎 commit，然后分别用 Squash Merge 和 Cherry Pick 两种方式处理。

**要求**：
1. 创建 feature 分支，做 5 个 commit（模拟零碎修改）
2. **方式一**：用 `--squash` 把 5 个合并成 1 个 merge 进 main
3. 回到合并前状态
4. **方式二**：用 `cherry-pick` 只拣选其中 3 个 commit 到 main
5. 对比两种方式的适用场景

---

## 十一、课程小结

### 11.1 核心知识图谱

```
┌────────────────────────────────────────────────────────────┐
│        Git 命令行 2——核心知识体系                              │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  分支全生命周期                                         │
│      ├── 查看：git branch / git branch -a                   │
│      ├── 创建：git checkout -b / git switch -c              │
│      ├── 推送：git push -u origin <branch>                  │
│      ├── 删除：git branch -d/-D / git push --delete         │
│      └── 拉取远端：git fetch → git checkout <branch>       │
│                                                            │
│  2️⃣  Fast Forward 概念                                      │
│      ├── Fast Forward：无分叉，指针前移，不产生新提交        │
│      ├── Non Fast Forward：有分叉，产生 Merge 提交          │
│      └── --no-ff：强制产生 Merge 提交（保留分支痕迹）       │
│                                                            │
│  3️⃣  高级合并操作                                           │
│      ├── Rebase：变基，提交搬到目标之后                      │
│      ├── Squash Merge：多提交压缩成一个                      │
│      └── Cherry Pick：拣选特定提交                           │
│                                                            │
│  4️⃣  冲突解决                                              │
│      ├── Merge 冲突：git add → git commit                   │
│      ├── Rebase 冲突：git add → git rebase --continue       │
│      └── 放弃：git merge --abort / git rebase --abort       │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 11.2 一句话总结

> **Git 命令行 2 聚焦于"分支"——从创建到删除的全生命周期管理，从 Fast Forward 到 Rebase 的合并策略选择，从 Squash 到 Cherry Pick 的高级操作技巧。理解 Fast Forward 的概念是理解所有合并行为的关键：无分叉 = 指针前移，有分叉 = 产生新提交。**

### 11.3 系列课程定位

```
┌─────────────────────────────────────────────────────────┐
│              GitHub 系列课程                               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  第1-13课：Desktop + IDEA + 概念基础（已完成）            │
│  第14课：Git 命令行 1——基础命令 + 四种后悔药              │
│  第15课（本课）：Git 命令行 2——分支操作 + 冲突解决         │
│         ← 你在这里                                       │
│                                                         │
│  Git 命令行系列共 2 课，覆盖了：                          │
│  ✅ 基础操作（clone/status/add/commit/push/pull）        │
│  ✅ 四种后悔药（restore/reset/revert/amend）             │
│  ✅ 分支管理（create/switch/delete/push/fetch）          │
│  ✅ 合并策略（FF/non-FF/squash/rebase/cherry-pick）      │
│  ✅ 冲突解决（merge conflict + rebase conflict）          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

*本教学文档基于陈泽鹏老师视频课程整理编写 · 2026年6月27日*
