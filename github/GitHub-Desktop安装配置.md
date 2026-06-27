# GitHub Desktop 安装配置与本地仓库管理

> 基于陈泽鹏老师视频课程整理编写 · 2026年6月

---

## 目录

- [一、课程背景与目标](#一课程背景与目标)
  - [1.1 前情回顾](#11-前情回顾)
  - [1.2 本节课的核心问题](#12-本节课的核心问题)
  - [1.3 本课要掌握的目标](#13-本课要掌握的目标)
- [二、为什么需要 GitHub Desktop](#二为什么需要-github-desktop)
  - [2.1 从网页端到本地](#21-从网页端到本地)
  - [2.2 GitHub Desktop vs 命令行 vs 网页端](#22-github-desktop-vs-命令行-vs-网页端)
- [三、安装与登录](#三安装与登录)
  - [3.1 下载安装](#31-下载安装)
  - [3.2 登录 GitHub 账号](#32-登录-github-账号)
- [四、克隆仓库——把远程项目复制到本地](#四克隆仓库把远程项目复制到本地)
  - [4.1 克隆是什么](#41-克隆是什么)
  - [4.2 克隆自己的仓库](#42-克隆自己的仓库)
  - [4.3 克隆别人的仓库（通过 URL）](#43-克隆别人的仓库通过-url)
- [五、深入理解 .git 文件夹——Git 的核心引擎](#五深入理解-git-文件夹git-的核心引擎)
  - [5.1 .git 文件夹总览](#51-git-文件夹总览)
  - [5.2 objects——存储所有数据对象](#52-objects存储所有数据对象)
  - [5.3 refs——存储分支引用](#53-refs存储分支引用)
  - [5.4 HEAD——头指针](#54-head头指针)
  - [5.5 Detached HEAD——分离头指针](#55-detached-head分离头指针)
  - [5.6 如何安全地查看历史代码](#56-如何安全地查看历史代码)
  - [5.7 其他重要文件](#57-其他重要文件)
  - [5.8 .git 文件夹结构速查](#58-git-文件夹结构速查)
- [六、在本地创建和管理分支](#六在本地创建和管理分支)
  - [6.1 在本地创建分支并推送到远端](#61-在本地创建分支并推送到远端)
  - [6.2 在网页端创建分支并拉取到本地](#62-在网页端创建分支并拉取到本地)
  - [6.3 基于任意分支创建新分支](#63-基于任意分支创建新分支)
  - [6.4 两种创建分支方式对比](#64-两种创建分支方式对比)
- [七、Fork——复刻别人的项目](#七fork复刻别人的项目)
  - [7.1 什么情况需要 Fork](#71-什么情况需要-fork)
  - [7.2 克隆别人的项目并尝试修改](#72-克隆别人的项目并尝试修改)
  - [7.3 Fork 的两种目的](#73-fork-的两种目的)
  - [7.4 Fork 后的项目长什么样](#74-fork-后的项目长什么样)
- [八、将已有文件夹初始化为 GitHub 仓库](#八将已有文件夹初始化为-github-仓库)
  - [8.1 场景说明](#81-场景说明)
  - [8.2 操作步骤](#82-操作步骤)
  - [8.3 发布到 GitHub 远端](#83-发布到-github-远端)
- [九、完整操作流程速查](#九完整操作流程速查)
- [十、常见问题与排错指南](#十常见问题与排错指南)
  - [10.1 错误速查表](#101-错误速查表)
  - [10.2 排查流程](#102-排查流程)
- [十一、课后练习](#十一课后练习)
  - [练习一：安装 GitHub Desktop 并克隆仓库](#练习一安装-github-desktop-并克隆仓库)
  - [练习二：探索 .git 文件夹](#练习二探索-git-文件夹)
  - [练习三：本地创建分支并推送](#练习三本地创建分支并推送)
  - [练习四：Fork 一个开源项目](#练习四fork-一个开源项目)
  - [练习五：将本地文件夹初始化为仓库](#练习五将本地文件夹初始化为仓库)
- [十二、课程小结](#十二课程小结)
  - [12.1 核心知识图谱](#121-核心知识图谱)
  - [12.2 一句话总结](#122-一句话总结)
  - [12.3 系列课程定位](#123-系列课程定位)

---

## 一、课程背景与目标

### 1.1 前情回顾

在前面课程中，你所有的操作都是在 **GitHub 网页端**完成的：

- 创建仓库、编辑文件、提交 Commit
- 创建分支、发起 PR、Code Review
- 使用 Wiki、Projects、Insights 等附属功能

网页端非常方便，但它有一个局限：**你只能编辑单个文件，不能使用本地编辑器（如 VS Code）的全部功能**。从这节课开始，我们要更进一步——**把代码复制到本地电脑上进行编辑**。

### 1.2 本节课的核心问题

| 问题 | 说明 |
|---|---|
| 怎么把 GitHub 上的仓库下载到本地？ | 克隆（Clone）——Git 的核心操作之一 |
| 不用命令行能用 Git 吗？ | GitHub Desktop——图形化 Git 客户端 |
| .git 文件夹是什么？里面有什么？ | Git 版本控制的核心引擎，底层原理 |
| 怎么在本地创建分支并同步到 GitHub？ | 本地创建 → Push 推送 |
| 怎么把别人的项目变成自己能改的？ | Fork（复刻）到自己名下 |
| 已有的本地文件夹怎么变成 GitHub 仓库？ | Create new repository → Publish |

> ⚠️ **关键认知**：从这节课开始，你将学会**本地 + 远程协同工作**。本地编辑代码 → 提交 Commit → 推送到 GitHub，这个流程是每个开发者每天要重复几十次的操作。

### 1.3 本课要掌握的目标

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  目标一：安装并配置 GitHub Desktop                              │
│         ├── 下载安装 GitHub Desktop                           │
│         ├── 登录 GitHub 账号并授权                            │
│         └── 理解 Desktop 在 Git 工具链中的位置                  │
│                                                             │
│  目标二：理解克隆（Clone）的概念和操作                            │
│         ├── 克隆自己的仓库到本地                                │
│         ├── 通过 URL 克隆任意公开项目                           │
│         └── 理解本地仓库和远程仓库的关系                         │
│                                                             │
│  目标三：理解 .git 文件夹的底层结构                              │
│         ├── 知道 objects / refs / HEAD 的作用                 │
│         ├── 理解 blob、tree、commit 三种对象                   │
│         └── 理解 Detached HEAD 状态及如何避免                   │
│                                                             │
│  目标四：掌握本地分支管理和 Fork 操作                            │
│         ├── 在本地创建分支并推送                               │
│         ├── 用 Fetch 同步远端分支                             │
│         ├── Fork 别人的项目到自己名下                          │
│         └── 将已有文件夹初始化为 Git 仓库并发布                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、为什么需要 GitHub Desktop

### 2.1 从网页端到本地

到目前为止，你一直在 GitHub 网页端操作：

```
网页端操作：
    优点 → 无需安装任何东西，打开浏览器就能用
    局限 → 只能编辑单个文件，不能用本地专业编辑器

本地操作：
    优点 → 用 VS Code 等强大编辑器，同时改多个文件，本地运行调试
    需要 → 一个工具把远程仓库和本地电脑连接起来
```

### 2.2 GitHub Desktop vs 命令行 vs 网页端

GitHub 提供了**三种方式**操作仓库：

| 方式 | 界面 | 上手难度 | 适合人群 |
|---|---|---|---|
| **🌐 网页端** | 浏览器 | ⭐ 最简单 | 轻度使用、快速编辑 |
| **🖥️ GitHub Desktop** | 图形界面（GUI） | ⭐⭐ 简单 | 日常开发、新手友好 |
| **⌨️ 命令行（Git CLI）** | 终端命令 | ⭐⭐⭐⭐ 较难 | 专业开发者、自动化脚本 |

```
学习路径（由简入难）：

    网页端 ──→ GitHub Desktop ──→ Git 命令行
     (前10课)      (本节课)        (后续课程)
```

**GitHub Desktop 的核心价值：**

| 优势 | 说明 |
|---|---|
| **图形化界面** | 无需记住命令行参数，所有操作可视化 |
| **简化命令** | 复杂的 Git 命令变成了点击按钮 |
| **可视化更改** | 代码改了什么，一目了然的 Diff 视图 |
| **免费开源** | 完全免费使用 |
| **跨平台** | 支持 Windows、macOS |

> 💡 **本教程的策略**：先学 GitHub Desktop（本节课），再学 Git 命令行（后续课程）。由简入难，循序渐进。Desktop 让你先用起来，命令行让你更强大。

---

## 三、安装与登录

### 3.1 下载安装

```
打开浏览器 → 访问 https://desktop.github.com/
    ↓
网站会自动识别你的操作系统
    ├── Windows → 下载 64 位安装包
    └── macOS → 下载 macOS 版本
    ↓
点击下载按钮 → 下载完成 → 双击安装包
    ↓
按照安装向导完成安装
    ↓
🎉 GitHub Desktop 安装完成！
```

### 3.2 登录 GitHub 账号

安装完成后打开 GitHub Desktop，首先需要登录：

```
打开 GitHub Desktop
    ↓
点击 "Sign in to GitHub.com"
    ↓
选择 "Continue with Browser"（通过浏览器登录）
    ↓
浏览器自动打开 → 点击 "Continue"
    ↓
点击 "Authorize Desktop"（授权 Desktop 访问你的 GitHub）
    ↓
输入双重身份验证码（如果开启了 2FA）
    ↓
🎉 登录成功！Desktop 中可以管理你的所有仓库了。
```

> ⚠️ **如果你开启了双重身份验证（2FA）**：登录过程中会要求输入 6 位验证码。这是为了保护你的账号安全，按照提示输入即可。

---

## 四、克隆仓库——把远程项目复制到本地

### 4.1 克隆是什么

**克隆（Clone）** 是 Git 的一个重要概念：**把一个远程仓库完整复制到自己电脑的某个目录下**。

```
                    克隆（Clone）
GitHub 远程仓库  ──────────────────→  你电脑上的本地仓库
(github.com/xxx/hello-world)        (D:/deepseek/hello-world)

克隆后的本地仓库包含：
    ├── 所有文件（和远程完全一样）
    ├── 完整的提交历史（所有 Commit 记录）
    ├── 所有分支（可以切换）
    └── .git 文件夹（版本控制核心）
```

> 💡 **Clone ≠ 下载 ZIP**：下载 ZIP 只拿到文件，没有版本历史。Clone 拿到的是**完整的仓库**，包括所有历史记录和 Git 功能。

### 4.2 克隆自己的仓库

**方式一：从 GitHub.com 选项卡选择**

```
GitHub Desktop → 点击 "Clone a repository"
    ↓
选择 "GitHub.com" 选项卡
    ↓
看到你名下的所有仓库列表 → 搜索找到 hello-world
    ↓
选择本地保存路径（例如 D:/deepseek）
    ↓
点击 "Clone"
    ↓
🎉 克隆完成！本地多了 hello-world 文件夹。
```

> 💡 **路径选择建议**：创建一个专门的文件夹（如 `D:/deepseek` 或 `~/projects`）来统一管理所有克隆下来的仓库。不要散落在桌面上。

### 4.3 克隆别人的仓库（通过 URL）

你也可以克隆任何公开的 GitHub 项目：

```
Step 1: 在 GitHub 网页端，打开你想克隆的项目
    ↓
Step 2: 点击绿色 "Code" 按钮 → 复制 HTTPS 链接（以 https://github.com/ 开头）
    ↓
Step 3: 回到 GitHub Desktop → 点击 "Clone a repository"
    ↓
Step 4: 选择 "URL" 选项卡 → 粘贴刚才复制的链接
    ↓
Step 5: 选择本地保存路径
    ↓
Step 6: 点击 "Clone"
    ↓
🎉 别人的项目也克隆到你本地了！
```

> ⚠️ **重要提醒**：虽然你能克隆别人的项目，但**你没有权限直接修改它**。如果要提交改动，需要先 Fork（复刻）到自己的名下——后面第七章会详细讲。

---

## 五、深入理解 .git 文件夹——Git 的核心引擎

> 克隆完成后，进入本地文件夹，你会发现一个隐藏的 `.git` 文件夹。这个文件夹是 Git 版本控制系统的**核心引擎**。以下内容是底层原理知识，看不懂也没关系，不影响你后续使用 Git，但理解了它，你会对 Git 有更深的认识。

### 5.1 .git 文件夹总览

```
hello-world/
├── .git/                  ← Git 版本控制核心（隐藏文件夹）
│   ├── objects/           ← 存储所有数据对象
│   ├── refs/              ← 存储分支引用（指针）
│   ├── HEAD               ← 头指针文件
│   ├── config             ← 仓库配置文件
│   ├── logs/              ← 分支变动历史
│   └── hooks/             ← 钩子函数（自动化脚本）
├── README.md
├── LICENSE
└── ...其他项目文件
```

> ⚠️ **绝对不能删 .git 文件夹！** 如果删了 `.git`，Git 在这个项目下就完全不能工作了。所有版本历史、分支信息都会丢失，项目退化为一个普通文件夹。

### 5.2 objects——存储所有数据对象

`objects/` 是 `.git` 中**最重要的文件夹**，存储了 Git 的所有数据对象。共有三种对象类型：

```
objects/
├── blob 对象      ← 存储文件内容
├── tree 对象      ← 存储目录结构
└── commit 对象    ← 存储提交信息
```

**① Blob 对象——存储文件内容**

```
Blob = Binary Large Object（二进制大对象）

作用：存储每个文件的内容
    ├── 每个文件 → 一个 blob 对象
    ├── 文件的每个历史版本 → 各自有独立的 blob 对象
    └── 内容相同 = blob 相同（因为哈希值相同，Git 不会重复存储）
```

> 💡 **高效存储**：如果你有 10 个内容相同的文件，Git 只存一份 blob。因为内容相同 → 哈希值相同 → 复用同一个 blob 对象。这就是 Git 在存储上的"去重"机制。

**② Tree 对象——存储目录结构**

```
Tree 对象 = 代表一个目录的内容

一个 Tree 对象记录了：
    ├── 该目录下有哪些文件（指向 blob 对象）
    ├── 该目录下有哪些子目录（指向其他 tree 对象）
    └── 每个文件/子目录的名称和权限
```

```
目录结构示例：

    / (根目录 tree)
    ├── README.md        → blob (文件内容)
    ├── src/ (子 tree)
    │   ├── index.js     → blob
    │   └── utils.js     → blob
    └── docs/ (子 tree)
        └── guide.md     → blob
```

**③ Commit 对象——存储提交信息**

```
Commit 对象 = 代表一次提交

一个 Commit 对象包含：
    ├── 作者（Author）——谁提交的
    ├── 提交时间（Date）——什么时候提交的
    ├── 提交信息（Message）——提交时写的说明
    └── 指向某个 tree 对象的引用——记录了当时的目录快照
```

```
Commit 对象 → Tree 对象 → Blob 对象
    (提交)      (目录结构)    (文件内容)

三者配合：
    Commit 指向 Tree → Tree 记录了目录结构 → Tree 指向 Blob → Blob 是文件内容
    所以：通过一个 Commit，可以还原仓库在当时的全部状态！
```

**objects 文件夹内部——Pack 文件：**

```
objects/
└── pack/          ← Git 为了节省硬盘空间，把大量对象打包到 pack 文件
    ├── *.pack     ← 压缩后的对象数据
    └── *.idx      ← pack 文件的索引
```

> 💡 Git 不会让 objects 文件夹无限膨胀。它定期把大量松散对象打包压缩成 pack 文件，大幅节省磁盘空间。

### 5.3 refs——存储分支引用

`refs/`（references 的缩写）存储了所有**引用**——本质是指向某个 Commit ID 的指针。

```
refs/
├── heads/         ← 所有本地分支
│   ├── main       ← 内容：main 分支最新一次 commit 的 ID
│   ├── feature    ← 内容：feature 分支最新一次 commit 的 ID
│   └── feature2   ← 内容：feature2 分支最新一次 commit 的 ID
├── remotes/       ← 所有远程分支
│   └── origin/
│       ├── main
│       └── feature
└── tags/          ← 所有标签
    └── v1.0.0
```

**验证：打开 heads/feature 文件：**

```
heads/feature 文件内容：
    a1b2c3d4e5f6...（一个 40 位的哈希值）

这就是 feature 分支最新一次 commit 的 ID！

在 GitHub Desktop 中切换到 feature 分支 → 找到最新 commit 的短 ID
对比发现 → 短 ID 的前 7 位和这个哈希值的前 7 位一模一样 ✅
```

> 💡 **分支的本质**：分支其实就是一个**指向某个 Commit 的指针**。`heads/feature` 文件里存的不是代码，只是一个 Commit ID。Git 通过这个 ID 找到对应的 Commit，再通过 Commit → Tree → Blob 还原出完整的文件状态。

### 5.4 HEAD——头指针

`.git/HEAD` 是一个文件，记录了**当前处于哪个分支**。

```
HEAD 文件内容：
    ref: refs/heads/main

含义：当前在 main 分支上
```

**验证：**

```
在 GitHub Desktop 中切换到 feature 分支
    ↓
再打开 HEAD 文件 → 内容变成：
    ref: refs/heads/feature

在 GitHub Desktop 中切换回 main 分支
    ↓
HEAD 文件变回：
    ref: refs/heads/main

结论：HEAD 就是一个指针，指向你当前所在的分支。
```

```
HEAD 的工作方式：

    HEAD → refs/heads/main → main 分支最新 commit ID → Commit 对象 → 仓库状态
            ↑
        HEAD 指向一个分支
        分支指向一个 Commit
        Commit 指向完整的仓库快照
```

### 5.5 Detached HEAD——分离头指针

**Detached HEAD（分离头指针）** 是 Git 中的一个特殊状态，需要特别注意避免丢失代码。

**什么情况会进入 Detached HEAD：**

```
GitHub Desktop 中：
    右键点击某个历史 commit → 选择 "Checkout commit"
    ↓
提示："You will be in a detached HEAD state."
    ↓
点击确认 → 进入 Detached HEAD 状态
```

**Detached HEAD 的含义：**

```
正常状态：                      Detached HEAD 状态：
    HEAD → 分支 → Commit           HEAD → Commit（直接指向一个历史 commit）
                                            ↑
                                      跳过了分支！

这意味着：
    ├── 你不在任何一个分支的管理下
    ├── 如果此时修改代码并提交
    │   └── 这个提交不属于任何分支！
    ├── 当你切换到其他分支时
    │   └── 这个提交可能会丢失！
    └── 所以 Detached HEAD 只适合"查看"，不适合"修改"
```

```
Detached HEAD 的使用场景：

    ✅ 适合：查看过去某个时间点的代码状态
    ✅ 适合：简单测试一下历史版本能不能跑
    ❌ 不适合：在历史状态上修改代码
    ❌ 不适合：在历史状态上做新的 Commit
```

> ⚠️ **核心警告**：在 Detached HEAD 状态下做的 Commit，切换分支后很容易丢失。因为没有任何分支在管理它。

### 5.6 如何安全地查看历史代码

如果你想在某个历史状态上修改代码，**正确的方式**是从那个历史 Commit 创建分支：

```
错误做法 ❌：                          正确做法 ✅：
历史 Commit → Checkout commit        历史 Commit → Create branch from commit
    ↓                                      ↓
进入 Detached HEAD                      创建一个新分支（如 history-branch）
    ↓                                      ↓
修改代码 → 提交                          修改代码 → 提交
    ↓                                      ↓
切换分支 → 代码丢失！😱                  代码在 history-branch 上，安全！😊
```

**在 GitHub Desktop 中的操作：**

```
找到某个历史 Commit → 右键点击
    ↓
选择 "Create branch from commit"（而不是 "Checkout commit"）
    ↓
给新分支取个名字（例如 history-branch）
    ↓
点击 "Create branch"
    ↓
🎉 现在你在一个正式的分支上，可以安全地修改代码了！
```

> 💡 **记住**：想回到历史看看 → Checkout commit（只读）。想在历史基础上改代码 → Create branch from commit（创建分支）。

### 5.7 其他重要文件

| 文件/文件夹 | 作用 |
|---|---|
| **config** | 仓库配置信息，最重要的是**远程仓库地址**（origin URL） |
| **logs/** | 每个分支的历史变动日志 |
| **hooks/** | 钩子函数，每当 Git 事件发生时自动执行（如 commit 前检查代码格式） |

### 5.8 .git 文件夹结构速查

```
┌─────────────────────────────────────────────────────────────┐
│              .git 文件夹结构速查                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  objects/        存储所有数据对象                              │
│    ├── blob      文件内容（同内容=同哈希=复用）                 │
│    ├── tree      目录结构                                    │
│    ├── commit    提交（作者+时间+信息+指向tree）                │
│    └── pack/     压缩打包后的对象                              │
│                                                             │
│  refs/           存储引用（指向 Commit ID 的指针）              │
│    ├── heads/    本地分支（每个文件存最新 commit ID）           │
│    ├── remotes/  远程分支                                    │
│    └── tags/     标签                                        │
│                                                             │
│  HEAD            头指针 → 指向当前分支 → 决定当前看到的代码      │
│                                                             │
│  Detached HEAD   HEAD 直接指向 commit（不经过分支）            │
│                  只适合查看，不适合修改！                       │
│                  修改代码请先 Create branch from commit        │
│                                                             │
│  config          仓库配置（含远程地址）                         │
│  logs/           分支变动历史                                 │
│  hooks/          自动化钩子脚本                               │
│                                                             │
│  ⚠️ 删除 .git = Git 完全失效，项目退化为普通文件夹              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 六、在本地创建和管理分支

### 6.1 在本地创建分支并推送到远端

使用 GitHub Desktop 在**本地创建分支**，然后推送到 GitHub：

```
GitHub Desktop → 点击分支选择器 → 点击 "New branch"
    ↓
输入分支名称（例如 feature3）
    ↓
选择基于哪个分支创建（默认基于当前分支）
    ↓
点击 "Create branch"
    ↓
🎉 分支在本地创建完成！

此时分支只存在于本地，GitHub 网页上还看不到
    ↓
点击 "Publish branch" 按钮
    ↓
🎉 分支推送到 GitHub 远端！网页上也能看到了。
```

```
本地创建分支 → Publish branch → GitHub 远端同步

    本地                       远端（GitHub）
    feature3  ──Publish──→    feature3
```

### 6.2 在网页端创建分支并拉取到本地

**另一种方式**——先在 GitHub 网页端创建分支，再同步到本地：

```
Step 1: 在 GitHub 网页端创建分支
       仓库 → View all branches → New branch → 输入 feature4 → 创建
    ↓
Step 2: 回到 GitHub Desktop
       此时本地还看不到 feature4 分支
    ↓
Step 3: 点击 "Fetch origin" 按钮
        （Fetch = 更新本地状态，使其与远程同步）
    ↓
Step 4: feature4 出现在分支列表中！
    ↓
🎉 远程分支同步到本地！
```

```
远端创建分支 → Fetch origin → 本地同步

    远端（GitHub）                    本地
    feature4  ──Fetch──→    feature4 出现在列表中
```

### 6.3 基于任意分支创建新分支

不仅可以基于 main 创建分支，也可以基于**任何已有分支**创建：

```
GitHub Desktop → 切换到 feature3 分支
    ↓
点击 "New branch"
    ↓
在弹出的对话框中：
    ├── 选择 "From: feature3"（基于当前分支创建）
    └── 或者选择 "From: main"（基于主干创建）
    ↓
输入分支名（如 feature5）
    ↓
点击 "Create branch"
    ↓
点击 "Publish branch" 推送到远端
    ↓
🎉 基于 feature3 的 feature5 分支创建完成！
```

### 6.4 两种创建分支方式对比

| 方式 | 操作流程 | 适用场景 |
|---|---|---|
| **本地创建 → Push** | Desktop 创建 → Publish branch | 正在本地开发，顺手创建新分支 |
| **网页创建 → Fetch** | GitHub 网页创建 → Desktop Fetch origin | 在网页端浏览时想到要开新分支 |

> 💡 两种方式最终结果一样——本地和远端都有分支。选择哪种取决于你当时在用什么工具。

---

## 七、Fork——复刻别人的项目

### 7.1 什么情况需要 Fork

当你克隆了别人的项目，修改了代码，尝试推送时……

```
你在本地改了别人的项目 → Commit → 点击 Push
    ↓
❌ 报错！你没有权限直接推送！
    ↓
GitHub Desktop 提示：你想 Fork 这个项目吗？
```

**Fork（复刻）** 就是把别人的项目**复制一份到你自己的名下**。只有你自己名下的项目，你才有权限随意修改。

### 7.2 克隆别人的项目并尝试修改

```
Step 1: 在 GitHub 网页端找到想克隆的项目 → Code → 复制 HTTPS 链接
    ↓
Step 2: GitHub Desktop → Clone → URL 选项卡 → 粘贴链接 → 克隆
    ↓
Step 3: 本地修改项目文件（如编辑 README.md）
    ↓
Step 4: Desktop 显示文件改动 → 填写 Commit Message → 点击 Commit
    ↓
Step 5: 点击 Push origin 尝试推送到远端
    ↓
Step 6: ❌ 报错！提示需要 Fork
```

### 7.3 Fork 的两种目的

GitHub Desktop 在你 Fork 时会问：**你的目的是什么？**

```
Fork 这个项目的目的是什么？

┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  ① To contribute to the parent project                      │
│     （给母项目做贡献）                                        │
│                                                             │
│     目的：你的修改最终想合并回作者的项目                        │
│     流程：Fork → 修改 → 提交 PR → 等待作者审核 → 合并         │
│     需要：作者的 Code Review 和 Merge 权限                    │
│                                                             │
│  ② For my own purpose                                       │
│     （我自己改着玩）                                          │
│                                                             │
│     目的：自己用，不改回作者的项目                              │
│     流程：Fork → 修改 → Push → 完事                          │
│     不需要：作者审核                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

> 💡 **选哪个？** 如果你修了一个 Bug 或做了一个改进想回馈给原项目 → 选 ①。如果你只是想自己改着玩、做实验 → 选 ②。

**选择"自己改着玩"后：**

```
选择 For my own purpose → 再次点击 Push
    ↓
🎉 推送成功！
    ↓
但是推送到的是你**自己名下** Fork 出来的项目
    ↓
并不会影响原作者的项目 ✅
```

### 7.4 Fork 后的项目长什么样

在 GitHub Desktop 中点击 "View on GitHub"，你看到的是自己 Fork 出来的项目：

```
仓库名下方显示：
    🍴 forked from [原作者]/[原项目]

含义：
    ├── 这个项目是从原作者那里复刻来的
    ├── 你的修改只影响你自己这份
    └── 原作者的母项目完全不受影响
```

```
Fork 的关系图：

    作者的原项目（母项目）
    │
    ├── 作者可以随意修改
    │
    └── 🍴 Fork ──→ 你名下的复刻项目
                     │
                     └── 你可以随意修改
                     
如果你想修改母项目：
    在你的 Fork 上改 → 提交 PR 给作者 → 作者审核 → 合并进母项目
```

---

## 八、将已有文件夹初始化为 GitHub 仓库

### 8.1 场景说明

你电脑上已经有一个文件夹，里面有一些代码，但它还不是 Git 仓库。怎么把它变成一个 GitHub 仓库？

```
已有文件夹 sharp-python/
├── main.py
└── utils.py

目标 → 变成一个 GitHub 仓库（有 .git、能推送、有 README、有 License）
```

### 8.2 操作步骤

```
GitHub Desktop → 点击仓库下拉列表 → 点击 "Add"
    ↓
选择 "Create new repository"
    ↓
填写信息：
    ├── Name：必须和文件夹名字一模一样！例如 sharp-python
    ├── Description：仓库描述
    ├── Local path：选择文件夹的**上一级目录**（不是文件夹本身！）
    ├── ✅ Initialize with a README（添加 README 文件）
    ├── Git ignore：可先选 None
    └── License：选择 MIT
    ↓
点击 "Create repository"
    ↓
🎉 仓库创建成功！

检查本地文件夹：
    ├── 多了 .git 文件夹 → Git 已经接管了这个项目 ✅
    ├── 多了 README.md → 项目自述文件 ✅
    └── 多了 LICENSE → 开源许可证文件 ✅
```

> ⚠️ **路径注意**：Local path 选的是**文件夹的上一级目录**，不是文件夹本身。比如文件夹在 `D:/projects/sharp-python/`，Local path 选 `D:/projects/`。

### 8.3 发布到 GitHub 远端

本地仓库创建好了，但 GitHub 网站上还没有——需要发布（Publish）：

```
GitHub Desktop → 点击 "Publish repository"
    ↓
设置：
    ├── 仓库名：确认与文件夹名一致
    ├── 描述：（可选）
    └── ☐ Keep this code private（是否私有）
         ├── 勾选 → 私有仓库
         └── 不勾选 → 公开仓库（推荐）
    ↓
点击 "Publish repository"
    ↓
🎉 推送到 GitHub 成功！
    ↓
右键仓库名 → "View on GitHub" → 在浏览器中预览
```

---

## 九、完整操作流程速查

```
┌─────────────────────────────────────────────────────────────┐
│              GitHub Desktop 操作速查卡                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  安装：https://desktop.github.com/ → 下载 → 安装 → 登录       │
│                                                             │
│  克隆自己的仓库：                                              │
│    Clone a repository → GitHub.com → 选仓库 → 选路径 → Clone │
│                                                             │
│  克隆别人的仓库：                                              │
│    网页 Code → 复制 URL → Clone → URL → 粘贴 → Clone         │
│                                                             │
│  本地创建分支：                                                │
│    New branch → 输入名称 → Create → Publish branch           │
│                                                             │
│  同步远端分支：                                                │
│    Fetch origin → 新分支出现在列表中                           │
│                                                             │
│  安全查看历史代码：                                            │
│    右键历史 Commit → Create branch from commit → 取分支名     │
│    （不要用 Checkout commit → 会进入 Detached HEAD！）        │
│                                                             │
│  Fork 别人项目：                                              │
│    克隆别人项目 → 修改 → Commit → Push 时选 Fork              │
│    → For my own purpose / To contribute                     │
│                                                             │
│  本地文件夹变仓库：                                            │
│    Add → Create new repository → 名=文件夹名                  │
│    → 路径=上级目录 → 勾选 README → 选 License → Create        │
│    → Publish repository                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 十、常见问题与排错指南

### 10.1 错误速查表

| 错误现象 | 原因 | 解决方法 | 优先级 |
|---|---|---|---|
| Push 时报权限错误 | 修改了别人的仓库却没有 Fork | Fork 到自己的名下再 Push | 🔴 高 |
| Detached HEAD 状态下做的修改丢了 | 在分离头指针状态下 Commit 后切换了分支 | 用 Create branch from commit 代替 Checkout commit | 🔴 高 |
| .git 文件夹被删除导致 Git 失效 | 误删了隐藏文件夹 | 重新 Clone 仓库（历史不会丢失，因为远端还有） | 🔴 高 |
| 本地文件夹初始化时 Name 和文件夹名不一致 | 输入了不同的名字 | Name 必须和文件夹名一模一样 | 🟡 中 |
| Clone 时路径选错 | 没有选对目录 | 创建统一的项目文件夹，避免散落各处 | 🟡 中 |
| 网页端创建的分支本地看不到 | 没有 Fetch | 点击 Fetch origin 同步远端状态 | 🟢 低 |
| 登录时双重验证失败 | 验证码输入错误或过期 | 重新生成验证码，在有效时间内输入 | 🟢 低 |

### 10.2 排查流程

```
GitHub Desktop 出问题了？
    │
    ├── 推送失败？
    │       ├── 是别人的仓库？→ Fork 到自己名下
    │       ├── 网络问题？→ 检查网络连接
    │       └── 权限不够？→ 确认你是仓库 Owner 或 Collaborator
    │
    ├── 代码丢失？
    │       ├── 是不是 Detached HEAD 状态？→ 查看 Desktop 顶部分支名
    │       ├── 在 Detached HEAD 下做了 Commit？→ 记下 Commit ID，创建分支找回
    │       └── 正常分支上提交的？→ 代码不会丢，检查是否切错了分支
    │
    ├── 远端分支看不到？
    │       ├── 本地创建后没 Publish？→ 点击 Publish branch
    │       ├── 远端创建后本地看不到？→ 点击 Fetch origin
    │       └── 网络问题？→ 检查网络，稍后重试
    │
    └── .git 文件夹相关问题？
            ├── .git 被删了？→ 重新 Clone
            ├── .git 文件夹太大？→ Git 会定期 pack 压缩
            └── 想了解内部结构？→ 回顾第五章
```

---

## 十一、课后练习

### 练习一：安装 GitHub Desktop 并克隆仓库

**目标：** 安装 Desktop 并将你的 hello-world 仓库克隆到本地。

**要求：**
- [ ] 访问 desktop.github.com 下载并安装 GitHub Desktop
- [ ] 登录你的 GitHub 账号
- [ ] 克隆你的 hello-world 仓库到本地
- [ ] 在本地文件管理器中找到克隆下来的文件夹
- [ ] 确认文件夹中包含 README.md 等文件和隐藏的 .git 文件夹

### 练习二：探索 .git 文件夹

**目标：** 理解 .git 文件夹的内部结构。

**要求：**
- [ ] 在 hello-world 的 .git 文件夹中找到 `HEAD` 文件，查看当前指向哪个分支
- [ ] 在 `refs/heads/` 中找到 main 分支文件，查看存储的 Commit ID
- [ ] 在 Desktop 中查看 main 分支最新 Commit 的短 ID，与 heads/main 文件内容的前 7 位对比
- [ ] 尝试在 Desktop 中切换分支，观察 HEAD 文件内容的变化
- [ ] 进入 `objects/` 文件夹，看看 pack 文件夹的内容

### 练习三：本地创建分支并推送

**目标：** 熟练掌握本地分支的创建和同步。

**要求：**
- [ ] 在 Desktop 中基于 main 创建一个新分支（如 `practice-local`）
- [ ] 在本地编辑 README.md，添加一行内容
- [ ] 在 Desktop 中查看改动 → 写 Commit Message → Commit
- [ ] 点击 Publish branch 推送到远端
- [ ] 在 GitHub 网页端确认新分支和修改已出现
- [ ] 在网页端创建另一个分支 `practice-web`，修改 README.md
- [ ] 回到 Desktop，点击 Fetch origin，确认新分支出现

### 练习四：Fork 一个开源项目

**目标：** 学会 Fork 和修改别人的项目。

**要求：**
- [ ] 找到一个你感兴趣的公开 GitHub 项目
- [ ] 通过 URL 克隆到本地
- [ ] 修改 README.md（添加一行内容）
- [ ] Commit 并尝试 Push → 观察 Fork 提示
- [ ] 选择 "For my own purpose"
- [ ] Push 成功后在 GitHub 网页端查看 Fork 出来的项目
- [ ] 确认项目标题下有 "forked from" 标记

### 练习五：将本地文件夹初始化为仓库

**目标：** 将已有的本地项目变成 GitHub 仓库。

**要求：**
- [ ] 在本地创建一个新文件夹（如 `my-local-project`），放入两个文本文件
- [ ] 在 Desktop 中用 Create new repository 将其初始化为仓库
- [ ] 确认 .git 文件夹已出现
- [ ] 添加 README.md 和 MIT License
- [ ] Publish repository 推送到 GitHub
- [ ] 在 GitHub 网页端确认仓库已出现

---

## 十二、课程小结

### 12.1 核心知识图谱

```
┌────────────────────────────────────────────────────────────┐
│         GitHub Desktop 安装配置 核心知识体系                   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  GitHub Desktop 定位                                    │
│      ├── 图形化 Git 客户端，免费开源                          │
│      ├── 学习路径：网页端 → Desktop → 命令行                  │
│      └── 安装：desktop.github.com → 下载 → 登录授权          │
│                                                            │
│  2️⃣  克隆（Clone）                                          │
│      ├── Clone = 把远程仓库完整复制到本地                     │
│      ├── 包含：所有文件 + 完整历史 + .git + 全部分支          │
│      ├── Clone ≠ 下载 ZIP（ZIP 没有版本历史）                │
│      └── 两种方式：从 GitHub.com 选 / 通过 URL              │
│                                                            │
│  3️⃣  .git 文件夹——Git 的核心引擎                             │
│      ├── objects/：blob(文件) + tree(目录) + commit(提交)    │
│      ├── refs/heads/：每个分支存最新 commit ID              │
│      ├── HEAD：头指针 → 指向当前分支                         │
│      ├── Detached HEAD：HEAD 直接指向 commit                │
│      │   ⚠️ 只适合查看，不适合修改！                          │
│      │   ✅ 安全做法：Create branch from commit             │
│      └── 删除 .git = Git 完全失效                           │
│                                                            │
│  4️⃣  本地分支管理                                            │
│      ├── 本地创建 → Publish branch → 远端也有了              │
│      ├── 远端创建 → Fetch origin → 本地也有了               │
│      └── 可基于任意已有分支创建新分支                          │
│                                                            │
│  5️⃣  Fork（复刻）                                           │
│      ├── Fork = 把别人的项目复制到自己名下                    │
│      ├── 两种目的：给母项目做贡献 / 自己改着玩                │
│      └── Fork 后的修改不影响原作者的项目                      │
│                                                            │
│  6️⃣  本地文件夹 → GitHub 仓库                                 │
│      ├── Create new repository → 名=文件夹名                │
│      ├── 路径选文件夹的上级目录                               │
│      └── Publish repository → 推送上线                      │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 12.2 一句话总结

> GitHub Desktop 让你告别网页端的束缚，在本地自由编辑代码；克隆、分支、Fork、初始化本地仓库——这四项操作是你从"网页用户"升级为"开发者"的必经之路。

### 12.3 系列课程定位

```
第一课：先导课
第二课：什么是 Git / GitHub
第三课：Git 与 GitHub 的历史起源
第四课：GitHub 网址基础介绍
第五课：发现工具 寻找灵感
第六课：装修 GitHub 个人主页
第七课：创建自己的第一个仓库
第八课：GitHub 是如何工作的（分支与合并请求）
第九课：GitHub 开源协作全流程实战
第十课：GitHub 仓库附属功能详解
第十一课（本课）：GitHub Desktop 安装配置  ← 你在这里
后续：Git 命令行操作实战
```

---

*本教学文档基于陈泽鹏老师视频课程（第十一课·GitHub Desktop 安装配置与本地仓库管理）整理编写。*  
*本文档涵盖 GitHub Desktop 下载安装与登录、克隆操作（自己的仓库/URL 方式）、.git 文件夹底层结构深度解析（objects 三种对象/blob-tree-commit、refs 分支引用、HEAD 头指针、Detached HEAD 状态及安全替代方案）、本地分支创建与推送（Publish/Fetch）、Fork 复刻操作（两种目的及权限机制）、以及将已有本地文件夹初始化为 Git 仓库并发布的完整流程。*
