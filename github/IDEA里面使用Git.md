# IDEA 里面使用 Git——IntelliJ IDEA 的 Git 全操作指南

> 基于陈泽鹏老师视频课程整理编写 · 2026年6月26日

---

## 目录

- [一、课程背景与目标](#一课程背景与目标)
  - [1.1 前情回顾](#11-前情回顾)
  - [1.2 IDEA 与 GitHub Desktop 的关系](#12-idea-与-github-desktop-的关系)
  - [1.3 本课要掌握的目标](#13-本课要掌握的目标)
- [二、安装与准备——下载 IntelliJ IDEA](#二安装与准备下载-intellij-idea)
- [三、Clone——从 GitHub 克隆项目](#三clone从-github-克隆项目)
  - [3.1 登录 GitHub 账号](#31-登录-github-账号)
  - [3.2 克隆项目到本地](#32-克隆项目到本地)
- [四、.gitignore——排除不需要版本控制的文件](#四gitignore排除不需要版本控制的文件)
  - [4.1 IDEA 自动生成的文件问题](#41-idea-自动生成的文件问题)
  - [4.2 在 IDEA 中添加 .gitignore](#42-在-idea-中添加-gitignore)
  - [4.3 .gitignore 语法要点](#43-gitignore-语法要点)
  - [4.4 特殊情况——远端已存在的文件如何忽略](#44-特殊情况远端已存在的文件如何忽略)
- [五、Commit & Push——提交与推送](#五commit--push提交与推送)
  - [5.1 新增文件加入暂存区](#51-新增文件加入暂存区)
  - [5.2 提交 Commit](#52-提交-commit)
  - [5.3 推送 Push](#53-推送-push)
- [六、Pull——拉取远端更新](#六pull拉取远端更新)
- [七、Branch——分支管理](#七branch分支管理)
  - [7.1 创建分支](#71-创建分支)
  - [7.2 推送分支到远端](#72-推送分支到远端)
  - [7.3 从远端拉取分支](#73-从远端拉取分支)
  - [7.4 Checkout——切换分支](#74-checkout切换分支)
- [八、Merge——合并分支](#八merge合并分支)
- [九、Rebase——变基操作](#九rebase变基操作)
  - [9.1 Rebase 的 IDEA 表述](#91-rebase-的-idea-表述)
  - [9.2 Rebase 之后必须 Force Push](#92-rebase-之后必须-force-push)
- [十、IDEA 与 Desktop 操作对照表](#十idea-与-desktop-操作对照表)
- [十一、文件颜色含义速查](#十一文件颜色含义速查)
- [十二、常见问题与排错指南](#十二常见问题与排错指南)
- [十三、课程小结](#十三课程小结)
  - [13.1 核心知识图谱](#131-核心知识图谱)
  - [13.2 一句话总结](#132-一句话总结)
  - [13.3 系列课程定位](#133-系列课程定位)

---

## 一、课程背景与目标

### 1.1 前情回顾

在前面课程中，你已经掌握了：

- **Git 四个分区**——工作区、暂存区、本地存储库、远端存储库
- **GitHub Desktop**——可视化的 Git 操作工具
- **命令行 Git**——git clone / add / commit / push / pull / merge / rebase
- **分支合并**——Merge、Squash、Rebase 三种策略
- **解决冲突**——内容冲突、Pull 冲突、文件名冲突

此前我们一直在用 GitHub Desktop 和命令行操作 Git。但在实际开发中，你大部分时间是泡在代码编辑器里的。如果在编辑器里就能完成 Git 操作，就不用频繁切换到 Desktop 或终端——效率会高很多。

### 1.2 IDEA 与 GitHub Desktop 的关系

> IntelliJ IDEA 是 JetBrains 公司出品的 Java/Kotlin 集成开发环境（IDE），它**内置了完整的 Git 操作功能**。本质上，IDEA 的 Git 功能和 GitHub Desktop 做的事情完全一样——都是给 Git 命令套了一个图形界面。只是按钮的名字可能不同，位置可能不同。

```
┌─────────────────────────────────────────────────────────┐
│          Git 操作的三种方式                               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 命令行           → 最底层，最灵活                    │
│  2. GitHub Desktop   → 独立 App，可视化                  │
│  3. IDE（IDEA/VS Code）→ 编辑器内置，无需切换窗口        │
│                                                         │
│  三种方式做的事情完全一样，选你最顺手的！                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 1.3 本课要掌握的目标

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  目标一：掌握 IDEA 中的 Git 基础操作                       │
│         ├── Clone（克隆项目）                             │
│         ├── Commit & Push（提交与推送）                   │
│         └── Pull（拉取远端更新）                          │
│                                                         │
│  目标二：掌握 .gitignore 的正确使用                       │
│         ├── 排除 IDEA 自动生成的文件                      │
│         ├── .gitignore 语法规则                           │
│         └── 远端已有文件的忽略处理                        │
│                                                         │
│  目标三：掌握 IDEA 中的分支与合并操作                      │
│         ├── 创建/切换/推送分支                            │
│         ├── Merge（合并）                                 │
│         └── Rebase + Force Push（变基+强制推送）          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 二、安装与准备——下载 IntelliJ IDEA

### 2.1 下载与安装

```
Step 1: 访问 JetBrains 官网
        https://www.jetbrains.com

Step 2: 选择 IntelliJ IDEA
        ├── Ultimate（旗舰版）：收费，功能最全
        └── Community（社区版）：免费，功能足够日常使用 ← 推荐

Step 3: 下载 Community Edition（免费版）
        往下滚动页面，找到 Community 版本的下载按钮

Step 4: 安装
        ├── Windows：双击 .exe 安装，一路 Next
        ├── Mac：拖拽到 Applications 文件夹
        └── Linux：解压 tar.gz，运行 bin/idea.sh
```

> 💡 JetBrains 家族还有其他 IDE（PyCharm、WebStorm、GoLand 等），Git 操作的界面和方式**完全一样**。学会 IDEA 的 Git 操作，其他 JetBrains IDE 的 Git 操作也就都会了。

---

## 三、Clone——从 GitHub 克隆项目

### 3.1 登录 GitHub 账号

```
┌─────────────────────────────────────────────────────────┐
│  Step 1: 打开 IDEA，在欢迎界面点击 "Get from VCS"        │
│          VCS = Version Control System（版本控制系统）     │
│          Git 是 VCS 的一种                               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Step 2: 在左侧列表选择 "GitHub"                         │
│                                                         │
│  Step 3: 点击 "Log In..." 登录 GitHub                   │
│          ├── 选择 "Authorize in GitHub"                 │
│          ├── 浏览器弹出授权页面                           │
│          ├── 点击授权                                   │
│          └── IDEA 显示 "Success" ✅                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

> ⚠️ 如果你之前没有用 IDEA 登录过 GitHub，需要先完成这一步授权。只做一次，之后就不需要再登录了。

### 3.2 克隆项目到本地

```
登录成功后，IDEA 会列出你 GitHub 账号下的所有仓库：

Step 1: 在列表中选择你要克隆的项目
        例如：git-learn-java

Step 2: 选择本地存放目录
        Directory: D:\learn-git\git-learn-java
        （目录名末尾加上项目名，IDEA 会自动创建文件夹）

Step 3: 点击 "Clone"
        IDEA 执行 git clone → 项目出现在本地

Step 4: 克隆完成后，IDEA 询问是否打开项目
        点击 "Trust Project" 或 "Open"
```

```
克隆完成后项目目录结构：
git-learn-java/
├── .idea/          ← IDEA 自动生成的配置文件夹
├── out/            ← IDEA 编译输出文件夹
├── src/            ← 源代码
├── git-learn-java.iml  ← IDEA 模块配置文件
└── ...
```

---

## 四、.gitignore——排除不需要版本控制的文件

### 4.1 IDEA 自动生成的文件问题

> ⚠️ IDEA 作为代码编辑器，会在项目目录中自动生成一些配置文件。这些文件**只对你自己有用**，不应该提交到 Git 仓库中。

```
IDEA 自动生成的文件/文件夹：

├── .idea/               IDEA 的项目配置（代码风格、运行配置等）
├── out/                 编译输出目录（.class 文件等）
├── *.iml                模块配置文件
└── target/              Maven/Gradle 构建输出（如果用了构建工具）

为什么要排除它们？
├── 团队中其他开发者可能用 Eclipse、VS Code 等不同编辑器
├── 这些配置文件只是你本地的编辑器设置
├── 提交到 Git 会给别人带来困扰（他们不需要这些文件）
└── 不同人的 IDEA 配置不同，提交上去会产生不必要的冲突
```

### 4.2 在 IDEA 中添加 .gitignore

```
┌─────────────────────────────────────────────────────────┐
│  方法：在文件上右键 → Git → Add to .gitignore            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Step 1: 在项目文件树中，找到要忽略的文件/文件夹          │
│          例如：git-learn-java.iml                        │
│                                                         │
│  Step 2: 右键 → Git → Add to .gitignore                 │
│                                                         │
│  Step 3: 如果项目中还没有 .gitignore 文件，              │
│          IDEA 会询问 "Create .gitignore?"                │
│          点击 "Create"                                   │
│                                                         │
│  Step 4: IDEA 询问是否要把 .gitignore 添加到暂存区       │
│          选择 "Add"（必须添加，否则 Git 不生效）         │
│                                                         │
│  Step 5: 文件变成绿色 ✅，表示已被 Git 管理              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**完整的 .gitignore 内容示例：**

```gitignore
# ── IDEA 配置文件 ──
.idea/
*.iml

# ── 编译输出 ──
out/
target/

# ── 本地配置 ──
application-local.properties
```

```
逐个添加后的操作步骤：

Step 1: 对 .idea 文件夹重复上面的操作（右键 → Add to .gitignore）
        → .gitignore 中会新增 .idea/

Step 2: 对 out 文件夹同样操作
        → .gitignore 中会新增 out/

Step 3: .gitignore 编辑完毕后
        点击工具栏上的绿色对勾（Commit 按钮）

Step 4: 勾选 .gitignore 文件

Step 5: 填写 Commit Message
        例如："add .gitignore file"

Step 6: 点击 "Commit and Push"
        → 同时完成提交和推送
```

### 4.3 .gitignore 语法要点

| 写法 | 含义 | 示例 |
|---|---|---|
| `文件名` | 排除指定文件 | `git-learn-java.iml` |
| `文件夹名/` | 排除整个文件夹 | `.idea/`、`out/` |
| `*.后缀` | 排除所有该后缀的文件 | `*.iml`、`*.log` |
| `路径/文件名` | 排除指定路径下的文件 | `src/main/resources/application-local.properties` |

```
.gitignore 语法速记：

.idea/          ← 斜杠结尾 = 文件夹（排除整个文件夹）
*.iml           ← 星号 = 通配符（排除所有 .iml 文件）
out/            ← 编译输出文件夹
target/         ← Maven/Gradle 构建输出
```

### 4.4 特殊情况——远端已存在的文件如何忽略

> ⚠️ **关键注意事项**：`.gitignore` 只对**尚未被 Git 追踪**的文件生效。如果文件**已经存在于远端仓库**中，仅仅添加到 `.gitignore` 是不够的。

```
问题场景：
application-local.properties 文件已经存在于远端仓库
你现在想用 .gitignore 忽略它 → 只写规则不管用！

原因：
.gitignore 只影响"未追踪"的文件
已经追踪的文件不受 .gitignore 影响

完整解决步骤：
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Step 1: 把文件规则添加到 .gitignore                    │
│          写入：src/main/resources/application-local      │
│                .properties                              │
│          → Commit & Push .gitignore 文件                │
│                                                         │
│  Step 2: 备份文件到桌面（或其他安全位置）                │
│          ┌── 右键文件 → Open in Explorer               │
│          └── 复制到桌面                                 │
│                                                         │
│  Step 3: 删除项目中的文件                               │
│          ┌── 选中文件 → 按 Delete 键                    │
│          └── Commit & Push 这次删除操作                  │
│              message: "delete application-local"        │
│                                                         │
│  Step 4: 确认远端文件已删除                              │
│          在 GitHub 网页端刷新 → 文件消失了 ✅            │
│                                                         │
│  Step 5: 把备份的文件拷贝回原位置                        │
│          文件重新出现 → 但颜色变成土黄色 🟠             │
│          土黄色 = 文件被 .gitignore 忽略了              │
│                                                         │
│  验证：修改这个文件 → Commit 面板中看不到任何改动        │
│  → .gitignore 生效了！✅                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

```
远端已有文件被 .gitignore 忽略的原理：

.gitignore 只阻止 Git 追踪新文件
但已经追踪的文件，Git 会继续追踪
所以要让它停止追踪，必须：
1. 添加到 .gitignore（告诉 Git "以后别管它"）
2. 从 Git 追踪中删除（git rm --cached，或直接删除+提交）
3. 文件重新放回来时，Git 就不再管它了
```

---

## 五、Commit & Push——提交与推送

### 5.1 新增文件加入暂存区

```
┌─────────────────────────────────────────────────────────┐
│  新增文件时的 IDEA 提示                                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  当你在项目中新建一个文件时，IDEA 会弹出对话框：          │
│                                                         │
│  ┌──────────────────────────────────────────────┐       │
│  │  "Do you want to add the following file      │       │
│  │   to Git?"                                   │       │
│  │                                              │       │
│  │  [Add]    [Cancel]                           │       │
│  │                                              │       │
│  │  ☐ Don't ask again                           │       │
│  └──────────────────────────────────────────────┘       │
│                                                         │
│  Add = 把文件加入暂存区（git add）→ 文件变绿色          │
│  Cancel = 不加入暂存区 → 文件保持红色（未追踪）         │
│  ☐ Don't ask again = 以后不再询问，默认按此次选择处理   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 5.2 提交 Commit

```
┌─────────────────────────────────────────────────────────┐
│  Commit 操作步骤：                                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Step 1: 点击工具栏上的绿色对勾（或 Ctrl+K）             │
│          打开 Commit 面板                                │
│                                                         │
│  Step 2: Changes 区域显示了所有有变动的文件               │
│          ├── 绿色 = 已暂存的新文件/已修改文件            │
│          ├── 勾选 = 本次要提交的文件                     │
│          └── 不勾选 = 本次不提交的文件                   │
│                                                         │
│  Step 3: 填写 Commit Message                            │
│          例如："new file: hello-date-two"               │
│                                                         │
│  Step 4: 选择提交方式                                    │
│          ├── [Commit] → 只提交到本地                    │
│          └── [Commit and Push] → 提交到本地并推送到远端  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 5.3 推送 Push

```
方式一：Commit 时直接 Push
    Commit 面板中点击 [Commit and Push] 按钮
    → 提交 + 推送一步完成

方式二：Commit 之后再 Push
    先点 [Commit] 提交到本地
    → 工具栏出现向上的箭头 ↑
    → 点击箭头或 Ctrl+Shift+K
    → 弹出 Push 确认窗口
    → 双击文件可查看改动内容
    → 确认无误后点击 [Push]

方式三：分支上右键 Push
    在左下角 Git 面板中
    → 右键当前分支
    → 选择 [Push]
```

---

## 六、Pull——拉取远端更新

### 6.1 IDEA 中的 Pull 操作

```
┌─────────────────────────────────────────────────────────┐
│  IDEA 的 "Update" = git fetch + git pull                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  方式一：使用 Update 按钮                                │
│  1. 点击左下角 "Git" 选项卡                             │
│  2. 展开分支列表                                        │
│  3. 找到要拉取的分支（如 main）                         │
│  4. 点击分支旁的蓝色下箭头 ↙                           │
│     （按钮文字：Update / Fetch and Pull）               │
│  5. IDEA 自动执行 fetch + pull                          │
│                                                         │
│  方式二：分支上右键                                      │
│  1. 在 Git 面板中找到分支                               │
│  2. 右键 → Update                                      │
│  3. 效果等同于方式一                                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

```
远端更新 → 本地拉取 的完整流程：

1. 在 GitHub 网页端修改文件（模拟同事的更新）
   例如：添加一个 README.md 文件

2. 回到 IDEA

3. 点击 Update 按钮（Fetch and Pull）
   → IDEA 从远端获取最新代码
   → 新文件出现在本地项目中 ✅
```

---

## 七、Branch——分支管理

### 7.1 创建分支

```
┌─────────────────────────────────────────────────────────┐
│  在 IDEA 中创建分支：                                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  方式一：Git 面板中创建                                  │
│  1. 点击左下角 "Git" 选项卡                             │
│  2. 点击分支列表旁的 [+] 加号按钮                       │
│     （按钮文字：New Branch）                            │
│  3. 输入分支名称（如 feature）                           │
│  4. 点击 "Create"                                       │
│                                                         │
│  ⚠️ 新分支基于「当前所在分支」创建                       │
│     创建前确认你当前在哪个分支上                         │
│                                                         │
│  方式二：菜单栏创建                                      │
│  Git → Branches → New Branch                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 7.2 推送分支到远端

```
本地创建的分支，远端还没有 → 需要推送：

Step 1: 在 Git 面板中，右键点击新创建的分支

Step 2: 选择 "Push"

Step 3: 确认 → 点击 "Push"

→ 远端刷新后，分支下拉列表中出现 feature 分支 ✅
```

### 7.3 从远端拉取分支

```
场景：同事在 GitHub 网页端创建了一个 feature2 分支
      你需要在本地获取这个分支

Step 1: 点击 Update 按钮（Fetch）
        → IDEA 从远端获取分支信息
        → Git 面板的 Remote 区域出现 feature2

Step 2: 右键点击 Remotes → origin → feature2

Step 3: 选择 "Checkout"
        → 远端分支被检出到本地工作区
        → 你现在在 feature2 分支上
```

```
Local（本地分支）vs Remote（远端分支）：

Git 面板中有两个区域：
├── Local：你本地的分支（可以直接在上面工作）
└── Remote → origin：远端的引用（不能直接工作，需要 Checkout 到本地）
```

### 7.4 Checkout——切换分支

```
┌─────────────────────────────────────────────────────────┐
│  Checkout = 切换当前工作分支                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  操作：                                                │
│  1. Git 面板 → Local 区域                              │
│  2. 找到你要切换的分支                                  │
│  3. 右键 → Checkout                                    │
│                                                         │
│  切换后：                                              │
│  ├── 右下角状态栏显示当前分支名                         │
│  ├── 项目文件自动更新为该分支的代码版本                 │
│  └── 工具栏的分支标签也会更新                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 八、Merge——合并分支

### 8.1 Merge 操作步骤

```
场景：把 main 分支的最新改动合并到 feature 分支

┌─────────────────────────────────────────────────────────┐
│  Step 1: 先 Fetch 获取远端最新状态                       │
│          点击 Update 按钮                               │
│                                                         │
│  Step 2: 切换到「接受合并」的分支                       │
│          右键 feature 分支 → Checkout                   │
│          （确认右下角显示 feature）                      │
│                                                         │
│  Step 3: 在要合并的源分支上右键                         │
│          找到 Remote → origin → main                    │
│          右键 → Merge 'main' into 'feature'             │
│                                                         │
│  Step 4: IDEA 执行合并                                  │
│          ├── 无冲突 → 合并完成                          │
│          └── 有冲突 → 弹出冲突解决窗口                  │
│                                                         │
│  Step 5: 推送合并结果到远端                             │
│          Push → feature 分支                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

```
Merge 的核心原则（和命令行一样）：

1. 先切换到「接受合并」的分支（目标分支）
2. 在「源分支」上右键 → Merge into 目标分支
3. 合并后的改动在本地，需要 Push 到远端

命令行等效：
git checkout feature         # 切换到接受合并的分支
git merge main               # 把 main 合并进来
git push origin feature      # 推送到远端
```

---

## 九、Rebase——变基操作

### 9.1 Rebase 的 IDEA 表述

> ⚠️ IDEA 中 Rebase 的表述和命令行不太一样，需要理解一下。

```
┌─────────────────────────────────────────────────────────┐
│  IDEA 中的 Rebase 菜单项：                               │
│                                                         │
│  "Rebase 'feature2' onto 'main'"                        │
│  翻译：把 feature2 变基到 main 上                        │
│                                                         │
│  两层理解：                                              │
│  1. 从效果看 = 把 main 的改动合并到 feature2            │
│  2. 从原理看 = 把 feature2 的"地基"改成 main            │
│              = feature2 的提交被"搬"到 main 最新提交之后 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

```
Rebase 操作步骤：

Step 1: 切换到接受变基的分支
        右键 feature2 → Checkout

Step 2: 在 main 分支上右键
        → "Rebase 'feature2' onto 'main'"
        → 点击执行

Step 3: IDEA 执行 Rebase
        ├── 无冲突 → 变基完成
        └── 有冲突 → 解决冲突 → Continue Rebase

Rebase 的可视化理解：
变基前：                      变基后：
main:    A → B → C           main:    A → B → C
              ↘                         ↘
feature2:      D → E          feature2:     D' → E'
（D、E 基于旧的 B）         （D'、E' 基于最新的 C）
```

### 9.2 Rebase 之后必须 Force Push

> ⚠️ **关键操作**：Rebase 重写了提交历史，普通 Push 会被拒绝，必须用 Force Push。

```
┌─────────────────────────────────────────────────────────┐
│  Rebase 后的推送步骤：                                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Step 1: 普通 Push 会失败                               │
│          尝试 Push → 提示 "Push rejected"               │
│          原因：本地历史和远端历史不一致                   │
│          → 先关掉这个提示                                │
│                                                         │
│  Step 2: 使用 Force Push                                │
│          在 Push 按钮旁有小箭头 ▼                       │
│          → 展开下拉菜单                                 │
│          → 选择 "Force Push"                            │
│                                                         │
│  Step 3: 确认 Force Push                                │
│          弹出确认窗口                                    │
│          → 点击 "Force Push"                            │
│          → 强制覆盖远端分支历史                          │
│                                                         │
│  ⚠️ Force Push 有风险：                                 │
│     ├── 只在你自己独用的分支上用！                       │
│     ├── 不要在 main 等共享分支上用！                    │
│     └── 会覆盖远端的提交历史                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 十、IDEA 与 Desktop 操作对照表

| Git 操作 | GitHub Desktop | IntelliJ IDEA | 命令行 |
|---|---|---|---|
| **克隆** | Add → Clone repository | Get from VCS → GitHub → Clone | `git clone` |
| **暂存** | 勾选文件复选框 | Add 对话框 / 勾选 Changes | `git add` |
| **提交** | 左下角填写 Summary → Commit | Ctrl+K → 写 Message → Commit | `git commit -m` |
| **推送** | Push origin | Ctrl+Shift+K → Push | `git push` |
| **拉取** | Fetch origin / Pull | Update 按钮（蓝色下箭头） | `git pull` |
| **创建分支** | New Branch 按钮 | Git 面板 [+] New Branch | `git branch` |
| **切换分支** | Current Branch 下拉 | 右键分支 → Checkout | `git checkout` |
| **合并** | Choose a branch to merge | 右键源分支 → Merge into | `git merge` |
| **变基** | Begin rebase | 右键 → Rebase onto | `git rebase` |
| **强制推送** | Force push origin | Push ▼ → Force Push | `git push --force` |
| **忽略文件** | 手动创建 .gitignore | 右键 → Add to .gitignore | 手动编辑 .gitignore |

---

## 十一、文件颜色含义速查

IDEA 用不同颜色表示文件在 Git 中的状态：

| 颜色 | Git 状态 | 含义 |
|---|---|---|
| **白色/默认** | 已提交，无改动 | 文件和上次提交一致，没有修改 |
| **绿色** 🟢 | 已暂存（Staged） | 新文件或已修改文件已加入暂存区，等待提交 |
| **蓝色** 🔵 | 已修改（Modified） | 文件有改动，但尚未加入暂存区 |
| **红色** 🔴 | 未追踪（Untracked） | 新文件，尚未被 Git 管理 |
| **土黄色** 🟠 | 已忽略（Ignored） | 文件在 .gitignore 中被排除了 |
| **灰色** ⚪ | 已删除（Deleted） | 文件已被删除，等待提交删除记录 |

```
文件颜色的变化流程：

新建文件 → 🔴红色（未追踪）
    ↓ git add 或 IDEA 弹出 Add 对话框点 Add
已暂存 → 🟢绿色（等待提交）
    ↓ git commit
无改动 → ⚪白色（已提交）

修改文件 → 🔵蓝色（已修改）
    ↓ git add（或 IDEA 自动追踪）
已暂存 → 🟢绿色（等待提交）

被忽略的文件 → 🟠土黄色（无论怎么改都不会变）
```

---

## 十二、常见问题与排错指南

### 12.1 错误速查表

| 错误现象 | 原因 | 解决方法 | 优先级 |
|---|---|---|---|
| **Push 被拒绝（rejected）** | Rebase 后没有 Force Push | 使用 Push ▼ → Force Push | 🔴 高 |
| **.gitignore 不生效，文件还是被追踪** | 文件在添加 .gitignore 之前已经被 Git 追踪了 | 先从 Git 中删除文件（备份→删除→提交），再放回来 | 🔴 高 |
| **Clone 后多了 .idea/out 等文件夹** | IDEA 自动生成的，还没加到 .gitignore | 按第四章教程添加 .gitignore | 🟡 中 |
| **Git 面板找不到** | 面板被关闭了 | 菜单 View → Tool Windows → Git（或 Alt+9） | 🟢 低 |
| **文件颜色不对，看不出状态** | 文件颜色设置被改了 | Settings → Version Control → File Status Colors | 🟢 低 |
| **切换分支时提示有未提交的改动** | 当前分支有未保存的工作 | 先 Commit 或 Stash，再切换分支 | 🟡 中 |
| **Merge 时出现冲突** | 和命令行/Destop 一样，两边改了同一行 | IDEA 会弹出冲突解决窗口，手动选择保留哪边 | 🟡 中 |
| **Force Push 后同事的提交丢了** | Force Push 覆盖了远端历史 | ⚠️ 不要在共享分支上 Force Push！如果发生了，用 `git reflog` 找回 | 🔴 高 |

### 12.2 .gitignore 不生效的完整排查

```
.gitignore 写了规则，但文件仍然被 Git 追踪？

Step 1: 确认规则写法正确
    ├── .idea/    ← 文件夹后面要加 /
    └── *.iml     ← 通配符用 *

Step 2: 确认 .gitignore 本身已被 Git 追踪
    git status → 能看到 .gitignore 吗？
    ├── 不能 → Commit & Push .gitignore 文件
    └── 能 → 进入 Step 3

Step 3: 确认文件是否之前已被追踪
    文件在远端仓库中存在吗？
    ├── 存在 → 需要先删除 + 提交删除（见 4.4 节）
    └── 不存在 → 不应该出现这个问题，检查 Step 1

Step 4: 终极检查
    git ls-files  ← 列出所有被 Git 追踪的文件
    看你要忽略的文件在不在列表中
    ├── 在列表中 → 还在被追踪，回到 Step 3
    └── 不在列表中 → 已成功排除 ✅
```

---

## 十三、课程小结

### 13.1 核心知识图谱

```
┌────────────────────────────────────────────────────────────┐
│         IDEA 中使用 Git——核心知识体系                         │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  基础操作                                              │
│      ├── Clone：Get from VCS → GitHub → 选项目 → Clone    │
│      ├── Commit：Ctrl+K → 勾选文件 → 填写 Message → Commit │
│      ├── Push：Ctrl+Shift+K → Push（或 Commit and Push）   │
│      └── Pull：左下角 Git 面板 → Update 蓝色箭头           │
│                                                            │
│  2️⃣  .gitignore                                            │
│      ├── 右键 → Git → Add to .gitignore                   │
│      ├── 语法：文件名 / 文件夹名/ / *.后缀 / 路径/文件     │
│      ├── 只对未追踪文件生效                                 │
│      └── 远端已有文件：需先删除+提交，再放回                │
│                                                            │
│  3️⃣  分支管理                                              │
│      ├── 创建：Git 面板 [+] → New Branch                   │
│      ├── 切换：右键分支 → Checkout                         │
│      ├── 推送分支：右键 → Push                             │
│      └── 拉取远端分支：Update → Remote → 右键 → Checkout  │
│                                                            │
│  4️⃣  合并与变基                                            │
│      ├── Merge：切到目标分支 → 右键源分支 → Merge into    │
│      ├── Rebase：右键 → Rebase onto → Force Push 必须！   │
│      └── Force Push：Push ▼ → Force Push                  │
│                                                            │
│  5️⃣  文件颜色                                              │
│      ├── 🟢绿色 = 已暂存    🔵蓝色 = 已修改               │
│      ├── 🔴红色 = 未追踪    🟠土黄 = 已忽略               │
│      └── ⚪白色 = 无改动    ⚫灰色 = 已删除                │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 13.2 一句话总结

> **IDEA 中的 Git 操作和 GitHub Desktop 完全等价——只是按钮名字和位置不同。核心操作就这几个：Clone（Get from VCS）、Commit（Ctrl+K）、Push（Ctrl+Shift+K）、Pull（Update）、Branch（New Branch）、Merge（Merge into）、Rebase（Rebase onto + Force Push）。掌握 IDEA 的 Git 操作，让你写代码和管版本在同一个窗口里完成。**

### 13.3 系列课程定位

```
┌─────────────────────────────────────────────────────────┐
│              GitHub 系列课程                               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  第1课：创建自己的第一个仓库                               │
│  第2课：Github 是如何工作的                               │
│  第3课：装修 Github 个人主页                              │
│  第4课：GitHub 开源协作全流程实战                          │
│  第5课：GitHub 仓库附属功能详解                            │
│  第6课：Git 四个分区的概念                                │
│  第7课：GitHub Desktop 安装配置                           │
│  第8课：GitHub Desktop 进阶操作                           │
│  第9课：分支合并——Merge · Squash · Rebase                 │
│  第10课：解决合并冲突                                     │
│  第11课：Github 做开源贡献的基本流程                       │
│  第12课（本课）：IDEA 里面使用 Git  ← 你在这里             │
│                                                         │
│  本课的独特价值：                                         │
│  ✅ 之前学的是"独立工具"操作 Git（Desktop、命令行）       │
│  ✅ 本课学的是"在编辑器内"操作 Git（开发流程不断）        │
│  ✅ IDEA 的 Git 功能学会后，PyCharm/WebStorm 也都会了    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

*本教学文档基于陈泽鹏老师视频课程整理编写 · 2026年6月26日*
