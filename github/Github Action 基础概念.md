# Github Action 基础概念

> 📅 生成日期: 2026-07-16 | 🎯 级别: M 级 | ⏱️ 录音时长: ~20.5 分钟 | 📏 文档规模: 2,600+ 行
> 🏷️ 标签: `GitHub Actions` `CI/CD` `DevOps` `自动化部署` `YAML`

---

## 📑 目录

- [一、GitHub Action 概述与核心概念](#一github-action-概述与核心概念)
  - [1.1 GitHub Action 是什么](#11-github-action-是什么)
  - [1.2 CI/CD 详解](#12-cicd-详解)
  - [1.3 Action 的核心价值](#13-action-的核心价值)
  - [1.4 Action 市场生态](#14-action-市场生态)
- [二、社区 Action 的查找与引用](#二社区-action-的查找与引用)
  - [2.1 Action 的本质：一个 GitHub 仓库](#21-action-的本质一个-github-仓库)
  - [2.2 Marketplace 查找实战](#22-marketplace-查找实战)
  - [2.3 `uses` 引用语法详解](#23-uses-引用语法详解)
  - [2.4 版本号与 Git Tag](#24-版本号与-git-tag)
- [三、核心术语与架构](#三核心术语与架构)
  - [3.1 四层术语总览](#31-四层术语总览)
  - [3.2 Workflow（工作流程）](#32-workflow工作流程)
  - [3.3 Job 与 Step 的层级辨析](#33-job-与-step-的层级辨析)
  - [3.4 Job 的关键属性：`runs-on`](#34-job-的关键属性runs-on)
  - [3.5 Event（事件 / 触发器）](#35-event事件--触发器)
- [四、第一个 Action 实战](#四第一个-action-实战)
  - [4.1 创建项目与选择模板](#41-创建项目与选择模板)
  - [4.2 模板 YAML 完整展示](#42-模板-yaml-完整展示)
  - [4.3 逐行解析 YAML 配置](#43-逐行解析-yaml-配置)
  - [4.4 添加第二个 Job](#44-添加第二个-job)
  - [4.5 提交、触发与执行观察](#45-提交触发与执行观察)
  - [4.6 排错指南](#46-排错指南)
  - [4.7 收费与配额](#47-收费与配额)
- [五、Python 项目自动发布 Release](#五python-项目自动发布-release)
  - [5.1 场景引入](#51-场景引入)
  - [5.2 创建 Release Workflow](#52-创建-release-workflow)
  - [5.3 触发与执行](#53-触发与执行)
  - [5.4 结果验证](#54-结果验证)
- [六、Java 项目 SSH 自动部署](#六java-项目-ssh-自动部署)
  - [6.1 场景引入](#61-场景引入)
  - [6.2 服务器环境准备](#62-服务器环境准备)
  - [6.3 Workflow 文件编写](#63-workflow-文件编写)
  - [6.4 密钥安全实践](#64-密钥安全实践)
  - [6.5 执行与验证](#65-执行与验证)
  - [6.6 其他玩法简介](#66-其他玩法简介)

---

## 一、GitHub Action 概述与核心概念

### 1.1 GitHub Action 是什么

#### 🧠 直观理解

GitHub Action 是一套**自动化流水线（pipeline）**，运行在 GitHub 的云端环境中。你可以把它想象成一条工厂的传送带：只需要提前设定好规则——比如"每当有人推送代码时"—传送带就会自动启动，依次执行你编排好的一系列任务，无需人工干预。

> 💡 **核心洞见**：在 GitHub Action 出现之前，开发者需要在本地或自己的服务器上手动配置 Jenkins、Travis CI 等工具来完成自动化。GitHub Action 将自动化能力直接嵌入到代码仓库中，让「代码托管」和「自动化执行」合为一体。

#### 📖 详细解释

GitHub Action 的本质是一个**事件驱动的任务编排系统**。它的工作模型由三层构成：

| 层级 | 名称 | 说明 |
|---|---|---|
| 事件（Event） | 触发器 | 代码推送（push）、发起 Pull Request、定时任务、手动触发等 |
| 工作流（Workflow） | 编排层 | 一个 YAML 文件，定义「触发什么事件 → 执行什么任务」 |
| Action（动作） | 执行单元 | 每个 Action 是一个独立可复用的脚本，完成单一功能 |

当你向仓库推送代码时，GitHub 会自动分配一台虚拟机，在该虚拟机中按 Workflow 的定义依次执行各个 Action。执行完毕后，虚拟机会被回收。整个过程完全在 GitHub 的云端完成，不占用你的本地资源。

### 1.2 CI/CD 详解

#### 🧠 直观理解

CI/CD 是 GitHub Action 最常见的应用场景。它的核心思想是：**让代码从开发者的电脑到用户能用的产品，整个过程全自动**。

以前没有 CI/CD 时，开发者写完代码后需要手动执行测试、手动编译打包、手动上传到服务器、手动重启服务。每一步都可能出错，而且很浪费时间。CI/CD 用一条自动化流水线替代了这些手动操作。

#### 📖 详细解释

**CI — Continuous Integration（持续集成）**

- **Continuous**（持续）：不是「偶尔做一次」，而是频繁地、自动地触发
- **Integration**（集成）：将多个开发者的代码变更合并到一起，并自动验证

目标：**每次代码提交后，自动完成测试和构建，确保代码始终处于「可发布」状态。**

**CD — Continuous Delivery（持续交付）**

- **Continuous**（持续）：构建完成后自动推进到下一阶段
- **Delivery**（交付）：将构建产物自动推送到目标环境

目标：**测试通过 → 自动打包 → 自动发布到服务器，全程无人值守。**

#### 🔄 典型 CI/CD 执行流程

```
开发者 git push
        │
        ▼
┌──────────────────┐
│ ① 拉取最新代码    │  ← checkout action 检出代码到虚拟环境
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ ② 安装依赖       │  ← npm install / pip install
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ ③ 运行单元测试    │  ← pytest / jest / go test
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ ④ 编译/构建      │  ← webpack / go build / docker build
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ ⑤ 推送至服务器    │  ← scp / rsync / kubectl apply
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ ⑥ 完成部署       │  ← 重启服务、健康检查
└──────────────────┘
```

#### 🔀 对比辨析：手动操作 vs CI/CD 自动化

| 维度 | 手动操作 | CI/CD 自动化 |
|---|---|---|
| 触发方式 | 开发者记得才做 | 代码推送自动触发 |
| 执行速度 | 数十分钟到数小时 | 几分钟（并行执行） |
| 出错概率 | 高（遗忘步骤、环境差异） | 低（每次都按同一脚本执行） |
| 反馈周期 | 长（部署完才发现问题） | 短（推送后几分钟即可看到结果） |
| 可追溯性 | 靠记忆和聊天记录 | 每次执行有完整日志 |

> ⚠️ **注意事项**：CI 和 CD 是两个独立概念。CI 关注的是「代码合并后的验证」，解决的是「集成地狱」问题；CD 关注的是「验证通过后的发布」，解决的是「发布恐惧」问题。两者可以独立使用，但实践中往往串联在一起。

### 1.3 Action 的核心价值

#### 🧠 直观理解

GitHub Action 不只是一个 CI/CD 工具——它本质上是一台**免费的云服务器**，可以用来执行任何你需要在云端完成的自动化任务。CI/CD 只是其中最经典的一个用途。

#### 📖 详细解释

##### 价值一：不止 CI/CD

你可以把 GitHub Action 当成一个**定时触发 + 远程执行**的脚本运行环境，做一些和部署无关的事情。比如：

- 每天凌晨自动爬取数据并存储到仓库
- 定时检查网站是否宕机并发送告警
- 自动生成项目的 changelog
- 自动给 issue 打标签、关闭过期 issue

> 💡 **核心洞见**：「免费的云服务器」这个说法是一个比喻，它强调的是 Action 运行在 GitHub 提供的云端虚拟机上，你不需要自己购买或维护服务器就能执行自动化任务。但它不是真正的云服务器——你无法 SSH 登录，也无法一直保持运行状态。每次 Workflow 触发时分配虚拟机，执行完毕后立即回收。

##### 价值二：可复用生态（这是 GitHub Action 最特别的地方）

由于很多自动化操作在不同项目里是类似的——比如「检出代码」「安装 Node.js」「构建 Docker 镜像」——GitHub 允许开发者把每个操作写成独立的脚本文件，存放在代码仓库中共享。这样：

1. **你不必写复杂脚本**：直接引用别人写好并测试过的 Action 即可
2. **整个流程 = Action 的组合**：像搭积木一样，把现成的 Action 串成一个 Workflow
3. **社区驱动**：全世界的开发者都在贡献 Action，越常用的场景越容易找到现成的

#### 🔀 对比辨析：GitHub Action vs 传统 CI/CD 工具

| 维度 | GitHub Action | Jenkins | Travis CI |
|---|---|---|---|
| 托管方式 | GitHub 内置，零部署 | 需自建服务器 | SaaS 平台 |
| 配置方式 | YAML 文件放在仓库中 | Groovy 脚本 + Jenkinsfile | `.travis.yml` |
| 生态与复用 | Marketplace 海量社区 Action | 插件市场，质量参差 | 插件较少 |
| 与 GitHub 集成 | 原生深度集成 | 需要 Webhook + Token | 需要 OAuth 授权 |
| 免费额度 | 公开仓库无限免费 | 自行承担服务器成本 | 公开仓库免费 |
| 学习曲线 | 较平缓（YAML + 现成 Action） | 较陡（需懂 Jenkins 体系） | 平缓 |

### 1.4 Action 市场生态

#### 🧠 直观理解

GitHub Action 的强大不在于它能「写脚本」，而在于**你几乎总是能找到别人已经写好的脚本**。GitHub 提供了一套完善的市场体系，让你可以像逛应用商店一样寻找和引用 Action。

#### 📖 详细解释

Action 市场分为两个入口：

| 入口 | 地址 | 内容 | 规模 |
|---|---|---|---|
| 官方 Action 仓库 | `github.com/actions` | GitHub 官方维护的 Action | 70+ 个仓库，覆盖大部分常用场景 |
| GitHub Marketplace | `github.com/marketplace`（切换到 Actions 标签） | 社区开发者发布的所有 Action | 数千个，涵盖各种细分需求 |

**官方 Action 仓库**中的 Action 由 GitHub 团队维护，质量有保障。其中最常用的包括：

- **`actions/checkout`**：将仓库代码检出到 Action 执行的虚拟环境中（几乎每个 Workflow 的第一步都会用到）
- **`actions/setup-node`**：在虚拟环境中安装指定版本的 Node.js
- **`actions/upload-artifact`**：将构建产物上传保存，供后续步骤或下载使用

**GitHub Marketplace** 的用法是：当你要实现某个自动化需求时，先去 Marketplace 搜索，大概率能找到现成的 Action。这比从头写脚本高效得多。

> ⚠️ **注意事项**：社区 Action 质量参差不齐，使用前应关注三点：Star 数（受欢迎程度）、最近更新时间（是否还在维护）、README 文档（用法是否清晰）。官方出品的 Action 则没有这些顾虑。

#### 💻 代码示例

以下是一个最简单的 GitHub Action Workflow 文件，展示了如何引用 `actions/checkout`：

```yaml
# 文件名: .github/workflows/ci.yml
# 功能: 代码推送时自动检出代码并执行测试

name: CI Pipeline

# 触发事件: 往 main 分支推送代码时
on:
  push:
    branches: [main]

# 任务列表
jobs:
  test:
    runs-on: ubuntu-latest  # 运行环境

    steps:
      # 步骤1: 使用官方 checkout Action 检出代码
      - name: 检出代码
        uses: actions/checkout@v4   # 引用官方 Action

      # 步骤2: 安装依赖（直接写 shell 命令，也可以引用 setup-node Action）
      - name: 安装依赖
        run: npm install

      # 步骤3: 运行测试
      - name: 运行测试
        run: npm test
```

| 行号 | 关键配置 | 解释 |
|---|---|---|
| `on.push.branches` | `[main]` | 只有推送到 main 分支时才触发，避免每次推送到 feature 分支都执行 |
| `runs-on` | `ubuntu-latest` | GitHub 提供的虚拟机环境，可选 `windows-latest`、`macos-latest` |
| `uses` | `actions/checkout@v4` | 引用 Action 的语法：`作者/仓库名@版本号`。这里的 `checkout` 会拉取当前仓库的全部代码到虚拟机中 |
| `run` | `npm test` | 直接在虚拟机 shell 中执行命令，不依赖外部 Action |

> 🔗 **延伸阅读**：Marketplace 中 Action 的详细搜索技巧和引用语法，将在本文 [二、社区 Action 的查找与引用](#二社区-action-的查找与引用) 中展开讲解。

---



## 二、社区 Action 的查找与引用

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 理解 Action 的本质——它就是一个 GitHub 仓库
> - [ ] 在 GitHub Marketplace 中独立搜索并找到合适的 Action
> - [ ] 正确使用 `uses` 语法引用社区 Action
> - [ ] 理解版本号（Git Tag）机制及其别名关系

---

### 2.1 Action 的本质：一个 GitHub 仓库

#### 🧠 直观理解

把 Action 想象成一个"开源工具箱"——每个 Action 就是一个独立的 GitHub 仓库，里面有完整的源代码、使用说明书（README），以及版本标签。你不需要自己造轮子，只需要"引用"这个仓库里的自动化流程即可。

#### 📖 详细解释

每个 Action 本质上就是一个普通的 GitHub 仓库，而不是什么特殊的"云服务"或"插件商店"。它的仓库地址格式为：

```
https://github.com/{作者名}/{action名字}
```

从 Marketplace 点击进入一个 Action 的介绍页面后，通过页面上的仓库链接（通常标注为 "View on GitHub" 或直接显示在页面侧边栏），就可以跳转到该 Action 的源代码仓库。进去之后你会发现：

- **源代码**：Action 的核心逻辑，通常用 JavaScript/TypeScript 编写，也可能是 Dockerfile 或复合 Action（Composite Action）
- **README 文件**：详细的使用说明，包括参数列表、使用示例、环境要求等
- **Tags / Releases**：版本标签，用于锁定你引用的具体版本
- **Issues & PRs**：和普通开源项目一样，有社区维护和讨论

> 💡 **核心洞见**：理解「Action 即仓库」这一点非常关键。这意味着：
> 1. 你可以直接阅读源码，了解它到底做了什么——不必盲目信任
> 2. 遇到 bug 可以提 issue，甚至 fork 一份自己改
> 3. Action 的发现渠道不限于 Marketplace——你在 GitHub 上看到的任何仓库，只要符合 Action 规范，都能被引用

---

### 2.2 Marketplace 查找实战：以 pyinstaller 为例

#### 🧠 直观理解

Marketplace 就像一个 App Store，你搜索关键词，浏览介绍页面，找到仓库地址，然后阅读说明书（README）来确认它满足你的需求。

#### 📖 详细解释

下面以搜索 `pyinstaller`（一个将 Python 程序打包成可执行文件的 Action）为例，展示完整的查找流程。

#### 🔄 查找流程

```
进入 GitHub Marketplace
    │
    ▼
┌─────────────────┐      ┌─────────────────┐      ┌───────────────────────┐
│ Step 1: 搜索     │─────▶│ Step 2: 查看介绍  │─────▶│ Step 3: 进入仓库       │
│ 输入 "pyinstaller"│      │ 确认 Action 的功能 │      │ 阅读 README 了解用法    │
└─────────────────┘      └─────────────────┘      └───────────────────────┘
```

**Step 1：搜索** — 在 GitHub Marketplace 顶部的搜索框中输入 `pyinstaller`，从搜索结果中找到目标 Action。

**Step 2：查看介绍页** — 点击进入 Action 的介绍页面。这里会展示这个 Action 的简要描述：pyinstaller 是用于给 Python 程序打包成可执行文件的工具。确认描述与你的需求匹配。

**Step 3：找到仓库地址** — 在介绍页面中找到仓库链接（通常在页面侧边栏或 "Links" 区域），点击进入源代码仓库。

**Step 4：阅读 README** — 进入仓库后，README 文件会详细说明如何使用这个 Action，包括：
- 必填参数和可选参数
- 完整的 YAML 配置示例
- 支持的平台（Linux / Windows / macOS）
- 常见问题和注意事项

> ⚠️ **注意事项**：README 是你引用 Action 时最重要的参考文档。不要只看 Marketplace 上的简介就直接使用——简介往往不完整，参数细节和注意事项都在 README 中。

> 🔗 **前置知识**：Marketplace 的概念和 Action 可复用的理念在 [一、GitHub Action 概述与核心概念](#一github-action-概述与核心概念) 中已有介绍

---

### 2.3 `uses` 引用语法详解

#### 🧠 直观理解

`uses` 关键字相当于代码中的 `import` 语句——你告诉 GitHub Actions："我要使用这个仓库里的自动化流程，请按这个版本执行。"

#### 📖 详细解释

在 workflow 的 YAML 文件中，引用社区 Action 的语法格式为：

```yaml
uses: 作者名/action名字@版本号
```

这个格式由三个部分构成，每个部分都有明确的含义：

| 组成部分 | 含义 | 示例 | 说明 |
|---|---|---|---|
| `作者名` | Action 作者的 GitHub 用户名 | `sayyid5416` | 拥有该仓库的 GitHub 账户 |
| `/` | 分隔符 | `/` | 固定语法，不可省略 |
| `action名字` | 仓库名称 | `pyinstaller` | 即 GitHub 上的仓库名 |
| `@` | 版本分隔符 | `@` | 固定语法，连接仓库名和版本号 |
| `版本号` | Git Tag | `v1.6.1` | 指定使用的具体版本 |

#### 💻 完整 YAML 示例

```yaml
# 文件名: .github/workflows/build.yml
# 功能: 使用社区 pyinstaller Action 打包 Python 程序

name: Build Python App

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      # Step 1: 拉取代码
      - uses: actions/checkout@v4

      # Step 2: 使用社区 pyinstaller Action 打包
      - uses: sayyid5416/pyinstaller@v1.6.1
        with:
          spec: 'src/main.spec'
```

> ⚠️ **注意事项**：录音稿中常听到"use"这个发音，但 YAML 中的正确关键字是 **`uses`**（第三人称单数形式，有末尾的 `s`）。在 workflow 文件中必须写成 `uses:`，否则 YAML 解析会失败。

> 💡 **核心洞见**：`uses` 引用的本质是告诉 GitHub Actions 运行时去下载那个仓库的代码并执行。一个 workflow 中可以混用多种来源的 Action——有的来自社区（如 `sayyid5416/pyinstaller`），有的来自 GitHub 官方（如 `actions/checkout`），你甚至可以引用你自己写的 Action。

---

### 2.4 版本号与 Git Tag

#### 🧠 直观理解

版本号就是 Git 仓库的标签（Tag），相当于给某次代码提交贴了一个"稳定可用"的标签。跟书签一样——你不需要记住具体的提交哈希，只需要引用这个标签即可锁定代码版本。

#### 📖 详细解释

`@` 后面的版本号，本质上是 Git 仓库中的 **Tag**。每一次提交都有一个唯一的 SHA-1 哈希值（如 `a1b2c3d...`），但没人愿意记忆和手写这些哈希值。Git Tag 就是给这些提交起的人类可读的名字。

当你写 `@v1.6.1` 时，GitHub Actions 实际执行的是：去该仓库中查找名为 `v1.6.1` 的 Tag，下载该 Tag 指向的那次提交的代码，然后执行。

#### 🔀 Tag 别名关系

Tag 存在一个容易被忽略但重要的特性：**多个 Tag 可以指向同一次提交**，形成别名关系。

以 pyinstaller Action 为例：

```
提交 SHA: abc1234...
    │
    ├── Tag: v1 ────────┐
    │                    │  指向同一提交 → 完全相同的代码
    └── Tag: v1.6.1 ────┘
```

| Tag | 含义 | 使用场景 |
|---|---|---|
| `v1.6.1` | 精确版本（Semantic Versioning） | 需要明确记录使用了哪个具体版本 |
| `v1` | 主版本号别名 | 始终跟随 v1.x 系列的最新发布 |

> ⚠️ **注意事项**：`v1` 和 `v1.6.1` 虽然目前指向同一提交，但未来 `v1` 这个 Tag 可能会被重新指向更新的提交（如 `v1.7.0`）。如果你需要**完全锁定版本**以避免意外变化，应使用精确的语义化版本号（如 `@v1.6.1`），而非大版本别名（如 `@v1`）。

#### 如何查看可用版本

在一个 Action 的 GitHub 仓库页面中，查看所有可用 Tag 的方法：

1. 进入仓库主页
2. 点击页面右侧的 "Releases" 或 "Tags" 链接（通常在右侧边栏）
3. 进入后可以看到所有已发布的 Tag 列表，包括每个 Tag 对应的版本号、发布日期和发布说明

在 Tags 页面中，你可以清楚地看到每个 Tag 指向哪次提交，以及哪些 Tag 指向同一提交（别名关系）。

> ❓ **常见疑问**：我应该用 `@v1` 还是 `@v1.6.1`？
>
> **回答**：这取决于你的风险偏好。使用 `@v1` 可以自动获得该大版本内的补丁更新和功能增强，但如果维护者引入了不兼容的变更，你的 workflow 可能出现非预期的行为。使用 `@v1.6.1` 则完全锁定版本，确保行为可预测，但你可能错过重要的安全更新。大多数场景下，推荐在初期使用精确版本号，验证稳定后再考虑是否需要改用大版本别名。

> 🔗 **延伸阅读**：`uses` 语法在 [四、第一个 Action 实战](#四第一个-action-实战) 中会频繁出现，届时你将看到 `actions/checkout`、`actions/setup-python`、社区 Action 等在同一 workflow 中协同工作

---


## 三、核心术语与架构

### 3.1 四层术语总览

在 GitHub Actions 的世界里，一切配置都围绕四个核心术语展开。理解它们之间的层级关系和协作方式，是读懂任何 Action 配置文件的前提。

#### 🧠 直观理解

把 GitHub Actions 想象成一场**自动化演出**：

- **Event（事件）** = 演出开始的"发令枪"——有人 push 了代码，或者定时到了
- **Workflow（工作流程）** = 整场演出的"节目单"——定义了从头到尾要做哪些事
- **Job（任务）** = 节目单里的"不同舞台"——多个舞台可以同时进行，互不干扰
- **Step（步骤）** = 每个舞台上的"表演步骤"——必须按顺序一幕一幕地来

#### 📖 层级关系图

```
┌──────────────────────────────────────────────────┐
│                  Event（触发器）                    │
│          push / PR / tag / schedule / ...         │
└──────────────────────┬───────────────────────────┘
                       │ 触发
                       ▼
┌──────────────────────────────────────────────────┐
│              Workflow（工作流程）                   │
│        .github/workflows/xxx.yml                 │
└──────────────────────┬───────────────────────────┘
                       │ 包含 1~N 个
           ┌───────────┼───────────┐
           ▼           ▼           ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐
    │  Job A    │ │  Job B    │ │  Job C    │    ← 默认并行运行
    │ (独立环境) │ │ (独立环境) │ │ (独立环境) │       各自在不同 Runner 上
    └─────┬────┘ └─────┬────┘ └─────┬────┘
          │            │            │
          │ 包含多个 Step（顺序执行，共享环境）
          ▼
    ┌──────────┐
    │  Step 1   │
    │  Step 2   │
    │  Step 3   │    ← 同一 Job 内顺序执行
    │   ...     │       共享同一个虚拟环境
    └──────────┘
```

> 💡 **核心洞见**：Workflow > Job > Step 的三级嵌套不是随意设计的——每一层解决一类不同的问题。Workflow 管"什么时候做"，Job 管"并行怎么做"，Step 管"顺序做什么"。

---

### 3.2 Workflow（工作流程）

#### 🧠 直观理解

Workflow 是 GitHub Actions 的**顶层配置文件**。一个仓库可以有很多个 Workflow 文件，每个文件独立定义一套自动化流程。

#### 📖 详细解释

- **存放位置**：必须放在仓库根目录下的 `.github/workflows/` 文件夹中
- **文件格式**：YAML 文件，扩展名为 `.yml` 或 `.yaml`
- **对应关系**：一个文件 = 一个 Workflow，文件名通常描述其用途（如 `ci.yml`、`deploy.yml`）
- **组成结构**：每个 Workflow 由一个或多个 Job 组成

```
你的仓库/
└── .github/
    └── workflows/
        ├── ci.yml          ← 一个 Workflow：持续集成
        ├── deploy.yml      ← 一个 Workflow：自动部署
        └── schedule.yml   ← 一个 Workflow：定时任务
```

> 🔗 **关联知识**：在 M02 中，我们学习了用 `uses` 引用社区 Action。这些 `uses` 语句就是写在 Workflow 文件的某个 Step 里的。Workflow 是容器，Action 是内容。

---

### 3.3 Job 与 Step 的层级辨析

> ⚠️ **本节核心重点**：Job 和 Step 的区别是理解 GitHub Actions 架构最关键的一环，也是初学者最容易混淆的地方。

#### 🧠 直观理解

- **Job**：相当于"不同的车间"——各自独立运转，可以同时开工
- **Step**：相当于"同一车间里的工序"——必须按顺序一道一道来，前一道的输出是后一道的输入

#### 🔗 推导链：为什么要分成 Job 和 Step 两个层级？

```
起点: 一个 Workflow 需要完成多项任务（编译、测试、部署、通知...）
  │
  ├── 第 1 步: 将所有任务平铺成 Step 列表
  │   为什么不行？
  │   如果所有任务都在同一个环境里顺序执行：
  │   - 编译 5 分钟 → 测试 10 分钟 → 部署 3 分钟 → 通知 1 秒
  │   - 总耗时 = 18 分钟
  │   - 问题是：测试和部署的代码版本可能不同，必须等编译完才能测，
  │     但「通知」完全不需要等部署结束！
  │
  ├── 第 2 步: 引入 Job 层级，将「无关任务」分到不同 Job
  │   为什么这样做？
  │   - Job A（编译+测试）和 Job B（通知）没有依赖关系
  │   - 它们可以并行运行 → 总耗时 = max(15分钟, 1秒) ≈ 15 分钟
  │   - 节省了 3 分钟
  │
  ├── 第 3 步: 每个 Job 内部再用 Step 组织「有顺序依赖的子任务」
  │   为什么不用 Job 代替 Step？
  │   - 编译的输出（二进制文件）必须传给测试步骤
  │   - 如果编译和测试分属不同 Job，它们在不同服务器上，文件无法直接传递
  │   - 同一个 Job 内的 Step 共享文件系统 → 编译产物自然对测试可见
  │
  └── 结论: Job 解决「并行效率 + 环境隔离」问题
           Step 解决「顺序依赖 + 数据传递」问题
           两者互补，缺一不可
```

#### 📖 详细对比

| 维度 | Job（任务） | Step（步骤） |
|---|---|---|
| **执行方式** | 默认**并行**运行 | **顺序**执行（从上到下） |
| **运行环境** | 各自在**独立**的虚拟环境（不同 Runner/服务器） | 共享**同一个**虚拟环境 |
| **环境隔离** | 完全隔离，互不干扰 | 不隔离，上一步的结果直接影响下一步 |
| **文件系统** | 不共享——Job A 生成的文件 Job B 看不到 | 共享——Step 1 创建的文件 Step 2 可以直接使用 |
| **依赖关系** | 默认无依赖，可通过 `needs` 关键字声明依赖 | 天然有顺序依赖（从上到下） |
| **适用场景** | 无关联的独立任务（如：同时测试 Node 14 和 Node 16） | 有顺序依赖的工序（如：检出代码→安装依赖→运行测试） |
| **一个 Workflow 中** | 可有 1 个或多个 | 每个 Job 可有 1 个或多个 |
| **典型数量** | 1~N 个 | 每个 Job 内 3~10 个 |

#### 📐 并行与串行示意

```
时间轴 ─────────────────────────────────────────────▶

Job A（编译+测试 Node 14）:
  ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ Step 1    │───▶│ Step 2    │───▶│ Step 3    │    ← 顺序执行
  │ checkout  │    │ npm test │    │ upload    │      共享同一环境
  └──────────┘    └──────────┘    └──────────┘

Job B（编译+测试 Node 16）:                            ← 与 Job A 并行运行
  ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ Step 1    │───▶│ Step 2    │───▶│ Step 3    │    ← 顺序执行
  │ checkout  │    │ npm test │    │ upload    │      独立环境（不同服务器）
  └──────────┘    └──────────┘    └──────────┘

Job C（发送 Slack 通知）:                              ← 与 A、B 同时并行
  ┌──────────┐
  │ Step 1    │                                        ← 只有一个 Step
  │ notify    │
  └──────────┘
```

> 💡 **核心洞见**：同一行的 Step 之间用"→"（顺序），不同 Job 之间用"并行"（同时推进）。这就是 Job 和 Step 最直观的区别。

> ❓ **常见误解**："Job 之间的并行是不是同时启动？" —— 是默认同时启动，但受限于 GitHub 提供的 Runner 数量（免费账户通常 20 个并发 Job）。如果有 100 个 Job 需要并行，超出的会排队等待。

---

### 3.4 Job 的关键属性：`runs-on`

> 💡 **补充知识**：录音稿中尚未展开此概念，但它将在 M04 的 YAML 文件中首次出现。提前了解有助于顺畅衔接。

#### 🧠 直观理解

`runs-on` 就是告诉 GitHub："这个 Job 要跑在什么操作系统上"。

#### 📖 详细解释

每个 Job 必须通过 `runs-on` 指定它运行的**虚拟环境类型**（即 Runner）。不同 Runner 提供不同的操作系统和预装工具：

| `runs-on` 值 | 操作系统 | 典型用途 |
|---|---|---|
| `ubuntu-latest` | Ubuntu Linux | 通用首选，绝大多数场景 |
| `windows-latest` | Windows Server | .NET 项目、Windows 专属测试 |
| `macos-latest` | macOS | iOS/macOS 构建、Xcode 项目 |
| `self-hosted` | 自定义 | 企业自有服务器、特殊硬件需求 |

```yaml
# 示例：一个 Job 的 runs-on 声明
jobs:
  build:
    runs-on: ubuntu-latest    # 这个 Job 跑在 Ubuntu 虚拟机上
    steps:
      - uses: actions/checkout@v4
      - run: npm test
```

> ⚠️ **注意事项**：不同操作系统上的命令语法不同。`ubuntu-latest` 和 `macos-latest` 用 bash 语法，`windows-latest` 用 PowerShell 语法。选择 `runs-on` 时要确保 Job 里的命令能在对应的操作系统上正确执行。

---

### 3.5 Event（事件 / 触发器）

#### 🧠 直观理解

Event 是 Workflow 的"发令枪"。没有事件触发，Workflow 文件即使写得再完美也不会执行。

#### 📖 详细解释

每个 Workflow 通过 `on` 关键字声明它对哪些事件做出响应。事件类型覆盖了 GitHub 上几乎所有的操作行为。

#### 📋 常见触发事件分类

| 分类 | 事件名 | 触发时机 | 典型场景 |
|---|---|---|---|
| **代码提交** | `push` | 向仓库推送代码时 | CI 自动构建和测试 |
| | `pull_request` | 创建/更新 Pull Request 时 | PR 检查、代码审查自动化 |
| **分支/Tag** | `create` | 创建分支或 Tag 时 | 新分支自动初始化 |
| | `delete` | 删除分支或 Tag 时 | 清理资源 |
| **定时任务** | `schedule` | 按 cron 表达式定时触发 | 每日构建、定期数据同步 |
| **Issue 相关** | `issues` | Issue 被打开/关闭/编辑等 | 自动打标签、自动分配 |
| **PR 评论** | `issue_comment` | 有人在 Issue/PR 下评论时 | `/deploy` 指令触发部署 |
| **发布** | `release` | 发布新 Release 时 | 自动构建并上传产物 |
| **手动触发** | `workflow_dispatch` | 在 GitHub 页面上手动点击按钮 | 手动部署、手动运行脚本 |
| **Webhook** | `repository_dispatch` | 外部系统通过 API 调用 | 跨仓库联动、外部系统集成 |

```yaml
# 示例：一个 Workflow 响应多种事件
on:
  push:                    # 每次 push 都触发
    branches: [main]       # 但仅限于 main 分支
  pull_request:            # 每次 PR 都触发
    branches: [main]
  schedule:                # 每天 UTC 时间 0:00 定时触发
    - cron: '0 0 * * *'
```

> 💡 **核心洞见**：Event 的设计体现了 GitHub Actions "一切皆可自动化"的哲学 —— 你能想到的 GitHub 上发生的任何操作，几乎都可以作为触发 Workflow 的事件。

> 🔗 **关联知识**：在 M04 的第一个 Action 实战中，我们将看到 `on: push` 作为最基础的事件触发器，让 Workflow 在每次推送代码时自动运行。

---

### 📋 本节小结

GitHub Actions 的四层术语构成了一个完整的自动化体系：

1. **Event** 决定"什么时候做" —— 触发一切的开端
2. **Workflow** 决定"做什么" —— 定义整条自动化流程
3. **Job** 决定"怎么并行做" —— 将无关任务分散到独立环境同时运行
4. **Step** 决定"按什么顺序做" —— 在同一环境里一步步完成有依赖关系的工序

Job 和 Step 的层级区分是设计精髓所在：并行（效率）与串行（依赖）的平衡，独立（隔离）与共享（协作）的取舍。

---

## 四、第一个 Action 实战

### 4.1 创建项目与选择模板

#### 🎯 目标

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 在 GitHub 仓库中通过 Actions 选项卡搜索并使用模板创建 Workflow
> - [ ] 读懂 YAML 配置文件中每个字段的含义与层级关系
> - [ ] 理解 `on`、`jobs`、`steps`、`runs-on` 等核心配置项的作用和写法
> - [ ] 在 Workflow 中添加第二个 Job，实现跨操作系统并行执行
> - [ ] 提交代码后观察 Action 的执行过程，查看日志并下载构建产物（Artifacts）
> - [ ] 了解 GitHub Actions 的免费额度与计费规则

#### 🏗️ 前置准备

| 准备项 | 说明 |
|---|---|
| GitHub 账号 | 需注册并登录 GitHub |
| 一个 Python 项目仓库 | 仓库中至少包含一个简单的 `.py` 文件（如 `main.py`），内容可为 `print("Hello, GitHub Actions!")` |
| 对 YAML 有基本感知 | 知道 YAML 是一种用缩进表示层级关系的配置文件格式即可，不需要精通 |
| 已学习 [三、核心术语与架构](#三核心术语与架构) | 已理解 Workflow / Job / Step / Event 四个核心概念的含义 |

#### 💻 Step-by-Step

**Step 1: 创建 Python 项目仓库**

在 GitHub 上创建一个新仓库，命名为 `python-action`（或任意名称）。初始化时添加一个简单的 Python 文件：

```python
# 文件名: main.py
# 功能: 最简单的 Python 入口文件，供 Action 检出、检查并打包

print("Hello, GitHub Actions!")
```

**Step 2: 打开 Actions 选项卡**

进入仓库页面，点击顶部的 **Actions** 选项卡。Actions 选项卡是所有 Workflow 的**管理中心**，你可以在这里看到历史运行记录、当前运行状态和构建产物。

**Step 3: 搜索并选择 Python 模板**

在搜索框中输入 `python`，从结果中选择 **Python application**。这是由 GitHub 官方维护的 Python 项目 CI 模板。点击 **Configure** 按钮，GitHub 会自动为你创建一个 Workflow 文件，默认路径是 `.github/workflows/python-app.yml`。

> ⚠️ **注意事项**：Workflow 文件**必须**放在 `.github/workflows/` 目录下。文件名可以任意取，但**扩展名必须是 `.yml` 或 `.yaml`**。

**Step 4: 定制模板 — 删除 pytest 步骤**（详见 [4.3.11 节](#4311-被删除的步骤pytest-测试)）

**Step 5: 添加 pyinstaller Job**（详见 [4.4 节](#44-添加第二个-job)）

### 4.2 模板 YAML 完整展示

下面是 GitHub 自动生成的 Python Application 模板的**完整内容**。这是我们第一次看到完整的 Workflow 配置文件——它把 M03 中所有抽象概念都落实到了具体的 YAML 语法中。

```yaml
# 文件名: .github/workflows/python-app.yml
# 功能: Python 项目 CI 流水线 — 代码检出 → Python 环境配置 → 依赖安装 → 代码检查 → 测试
# 来源: GitHub Actions 官方 Python application 模板

name: Python application                  # ① Workflow 名称，显示在 Actions 列表页

on:                                        # ② 触发器（Event）：定义何时自动执行
  push:                                    # 代码推送事件
    branches: [ "main" ]                   # 仅监听 main 分支的推送
  pull_request:                            # Pull Request 事件
    branches: [ "main" ]                   # 仅监听目标为 main 分支的 PR

permissions:                               # ③ 权限声明：此 Workflow 需要什么权限
  contents: read                           # 只读权限 — 可读仓库内容，不可修改

jobs:                                      # ④ Job 容器：所有 Job 的父节点
  build:                                   # ⑤ Job 名称：这个 Job 叫 "build"
    runs-on: ubuntu-latest                 # ⑥ 运行环境：申请一台最新版 Ubuntu 虚拟机
    steps:                                 # ⑦ 步骤列表：Job 内依次执行的操作
      - uses: actions/checkout@v4         # Step 1: 检出代码到虚拟机
      - name: Set up Python 3.10          # Step 2 的显示名称
        uses: actions/setup-python@v5     # Step 2: 在虚拟机中安装 Python
        with:                              # 向 Action 传递参数
          python-version: '3.10'           # 指定 Python 版本
      - name: Install dependencies         # Step 3 的显示名称
        run: |                             # Step 3: 执行 Shell 命令（多行）
          python -m pip install --upgrade pip  # 升级 pip
          pip install flake8 pytest             # 安装代码检查工具
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
      - name: Lint with flake8             # Step 4 的显示名称
        run: |                             # Step 4: flake8 代码规范检查
          # 第一遍：检查严重错误（语法错误、未定义名称等）
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
          # 第二遍：检查风格问题（复杂度、行长度等，不阻断流水线）
          flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
      - name: Test with pytest             # Step 5 的显示名称（老师将删除此步）
        run: |                             # Step 5: 运行 pytest 测试
          pytest
```

---

### 4.3 逐行解析 YAML 配置

这是学员第一次看到完整的 YAML Workflow 文件。下面按照 YAML 中自上而下的顺序，逐字段解释每一个配置项的含义、写法和设计原因。

#### 4.3.1 注释行（`#` 开头）

```yaml
# 文件名: .github/workflows/python-app.yml
# 功能: Python 项目 CI 流水线 ...
```

以 `#` 开头的内容是 **YAML 注释**，不会被解析执行。GitHub 模板顶部的注释一般包含用途说明和文档链接。在团队协作中，写好注释可以让其他人快速理解这个 Workflow 是做什么的。

#### 4.3.2 `name` — Workflow 名称

```yaml
name: Python application
```

| 属性 | 说明 |
|---|---|
| **含义** | 定义这个 Workflow 在 GitHub Actions 页面上显示的**名称** |
| **是否必填** | 否。如果不写 `name`，GitHub 会使用 `.yml` 文件名作为显示名 |
| **建议** | 当仓库中有多个 Workflow 时（如 `ci.yml`、`deploy.yml`、`nightly.yml`），写清楚的 `name` 可以一眼分辨 |

#### 4.3.3 `on` — 触发器（Event）

```yaml
on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]
```

`on` 是 Workflow 的**触发器**，回答了"什么时候自动执行这个 Workflow"。这正是 M03 中讲的 **Event（事件）** 概念的具体写法。

| 字段 | 层级 | 含义 | 触发时机 |
|---|---|---|---|
| `on` | 顶层 | 触发器父节点 | — |
| `push` | 第一子级 | 监听 **push** 事件 | 有人执行 `git push` 将代码推送到 GitHub |
| `pull_request` | 第一子级 | 监听 **PR** 事件 | 有人创建或更新 Pull Request |
| `branches: [ "main" ]` | 第二子级 | 限制触发分支 | 只有操作发生在 `main` 分支上才触发 |

> 💡 **核心洞见**：当你向 `main` 分支推送代码时，GitHub 内部会生成一个 `push` 事件。这个事件自动匹配到 Workflow 中 `on.push` 的定义，从而触发执行。推送到 `dev` 分支则不会触发，因为 `branches` 限制只监听 `main`。

**`branches` 的数组写法**

```yaml
branches: [ "main" ]           # 流式写法（单行数组）
# 等价于：
branches:                       # 块式写法（多行）
  - main
```

两种写法完全等价。推荐用块式写法（更清晰，尤其当监听多个分支时）。

#### 4.3.4 `permissions` — 权限声明

```yaml
permissions:
  contents: read
```

`permissions` 声明了此 Workflow 运行时的**权限范围**，遵循**最小权限原则**。

| 字段 | 含义 |
|---|---|
| `contents: read` | 只允许**读取**仓库内容（代码、文件），**不允许修改**仓库中的任何内容 |

这意味着此 Action 可以：
- 检出代码到虚拟机
- 读取仓库中的配置文件
- 读取代码进行 lint 检查

此 Action **不能**：
- 推送新的 commit
- 创建或修改 Release
- 写入或删除仓库文件

> 💡 **核心洞见**：为什么要限制权限？如果一个 Action 只有 `contents: read`，即使 Action 的脚本被恶意修改，它也无法破坏你的仓库内容。这是安全性的第一道防线。后续学到自动发布 Release 时，会发现权限需要升级。

#### 4.3.5 `jobs` — 工作单元容器

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - ...
```

`jobs` 是 Workflow 中**所有 Job 的父容器**。一个 Workflow 下可以有多个 Job，Job 之间**默认并行执行**。

> 💡 **核心洞见**：Job 是 Workflow 中的**最小独立执行单元**。每个 Job 在单独的虚拟机上运行，拥有**独立的文件系统和进程空间**。Job A 中下载的文件，Job B 是看不到的——如果需要共享数据，要用 `actions/upload-artifact` / `actions/download-artifact` 来传递文件，或用 `needs` 建立依赖关系。

##### `build` — Job 名称

```yaml
build:
```

`build` 是这个 Job 的**名字**。命名规范：
- 可以取任意合法 YAML 键名（如 `test`、`deploy`、`lint`、`package`）
- 建议用动词或动名词，表达这个 Job 在做什么
- 这个名字会显示在 Actions 页面的 Job 列表中

##### `runs-on` — 运行环境

```yaml
runs-on: ubuntu-latest
```

`runs-on` 定义了 Job 运行的**虚拟环境（Runner）**。`ubuntu-latest` 意思是向 GitHub 申请一台**最新版 Ubuntu 操作系统的虚拟机**来执行这个 Job 中的所有步骤。

GitHub 提供的可用运行环境一览：

| `runs-on` 值 | 操作系统 | 典型用途 |
|---|---|---|
| `ubuntu-latest` | Ubuntu Linux（最新稳定版） | 通用 CI/CD，大多数项目的首选 |
| `ubuntu-22.04` | Ubuntu 22.04 LTS | 需要固定版本的项目 |
| `windows-latest` | Windows Server（最新稳定版） | 构建 `.exe`、.NET 项目 |
| `windows-2022` | Windows Server 2022 | 需要固定 Windows 版本 |
| `macos-latest` | macOS（最新稳定版） | 构建 iOS/macOS 应用 |
| `macos-14` | macOS 14 (Apple Silicon) | 需要 Apple M 系列芯片构建 |

> ⚠️ **注意事项**：`-latest` 标签是**浮动的**——它始终指向 GitHub 当前支持的"最新稳定版本"。当 GitHub 升级默认版本时，你的 Workflow 会自动切换到新版本。对于大多数项目这不是问题，但如果你的构建对操作系统版本高度敏感，建议使用固定版本号（如 `ubuntu-22.04`）。


#### 4.3.5.1 整文件层级回顾

录音中老师强调「我们再看一下层级关系」。下面用一棵 ASCII 树状图展示从 Workflow 顶层到 Step 底层的完整缩进层级，帮你建立对 YAML 结构的整体认知：

```
workflow（整个 .yml 文件）
│
├── name: Python application                ← 第 1 层：Workflow 名称
├── on:                                     ← 第 1 层：触发器
│   ├── push:                               ← 第 2 层：事件类型
│   │   └── branches: [ "main" ]            ← 第 3 层：触发分支
│   └── pull_request:                       ← 第 2 层：事件类型
│       └── branches: [ "main" ]            ← 第 3 层：触发分支
├── permissions:                            ← 第 1 层：权限
│   └── contents: read                      ← 第 2 层：权限范围
│
└── jobs:                                   ← 第 1 层：Job 容器
    │
    ├── build:                              ← 第 2 层：Job 名称（Job 1）
    │   ├── runs-on: ubuntu-latest          ← 第 3 层：申请 Ubuntu 虚拟机
    │   └── steps:                          ← 第 3 层：步骤容器
    │       ├── - uses: checkout@v4         ← 第 4 层：Step 1 — 检出代码
    │       ├── - name: Set up Python       ← 第 4 层：Step 2
    │       │     uses: setup-python@v5
    │       │     with:                     ← 第 5 层：Step 的参数
    │       │       └── python-version: '3.10'
    │       ├── - name: Install deps        ← 第 4 层：Step 3
    │       │     run: | ...
    │       ├── - name: Lint flake8         ← 第 4 层：Step 4
    │       │     run: | ...
    │       └── - name: Test pytest         ← 第 4 层：Step 5（已删除）
    │
    └── pyinstaller:                        ← 第 2 层：Job 名称（Job 2，与 build 平级）
        ├── runs-on: windows-latest         ← 第 3 层：申请 Windows 虚拟机
        └── steps:                          ← 第 3 层：步骤容器
            ├── - uses: checkout@v4         ← 第 4 层：Step 1
            └── - name: Build exe           ← 第 4 层：Step 2
                  uses: JackMcKew/pyinstaller-action-windows@main
                  with:                     ← 第 5 层：Step 的参数
```

**关键观察**：

| 观察点 | 说明 |
|---|---|
| `jobs` 下的 `build` 和 `pyinstaller` 缩进一致 | 它们是平级关系 → Job 之间并行执行 |
| 每个 Job 都有独立的 `steps` 列表 | Step 是 Job 的私有步骤，不跨 Job 共享 |
| 缩进每增加一级，表示从属关系加深一层 | YAML 完全依靠缩进（空格）而非括号来表达层级 |
| `with` 是 Step 的直属子节点 | 不同 Action 的 `with` 参数完全不同，需查阅对应文档 |

> 💡 **核心洞见**：把这段 YAML 想象成一棵树——`workflow` 是树根，`jobs` 是一级枝干，`build`/`pyinstaller` 是二级枝干，`steps` 是三级枝干，每个 `-` 开头的条目就是树叶。理解这棵树的结构，你就能读懂任何 GitHub Actions Workflow。

#### 4.3.6 `steps` — 步骤列表

```yaml
steps:
  - uses: actions/checkout@v4
  - name: Set up Python 3.10
    uses: actions/setup-python@v5
    ...
```

`steps` 是 Job 内部的**步骤序列**。步骤之间是**顺序执行**的——Step 1 成功后才执行 Step 2，Step 2 完成后执行 Step 3，以此类推。

GitHub Actions 中步骤有两种基本写法：

| 写法 | 关键字 | 用途 | 示例 |
|---|---|---|---|
| 引用外部 Action | `uses:` | 使用社区或官方封装好的 Action | `uses: actions/checkout@v4` |
| 执行 Shell 命令 | `run:` | 直接在虚拟机上执行命令 | `run: pip install flake8` |

> 💡 **核心洞见**：`uses` 和 `run` 是步骤的**两种基本原子操作**。`uses` 相当于"调用一个封装好的函数"（有输入参数和输出），`run` 相当于"手写一行命令"。一个 Workflow 中两者通常会混合使用。

在每个步骤前加上 `- name:` 是可选的，但强烈建议写上。它会让 Actions 日志更易读——你会看到 "Set up Python 3.10" 而不是一串技术性名称。

#### 4.3.7 Step 1: `actions/checkout@v4` — 检出代码

```yaml
- uses: actions/checkout@v4
```

这是**几乎所有 Workflow 都必须包含的第一步**：将仓库中的代码**检出（克隆）**到虚拟机的文件系统中。

| 组成部分 | 含义 |
|---|---|
| `uses` | 关键字，表示此步骤使用一个外部的 Action |
| `actions/checkout` | Action 标识：`actions` 是作者（GitHub 官方），`checkout` 是仓库名 |
| `@v4` | 版本号，表示使用第 4 个主版本 |

> 💡 **核心洞见**：如果不执行 checkout，虚拟机的文件系统里就**没有你的代码**。后续所有操作（安装依赖、运行测试、代码检查、打包编译）都将无事可做。可以把 checkout 理解为"把仓库的代码搬进工厂车间"——这是所有工序的第一步。

> 🔗 **关联知识**：`actions/checkout` 正是 M02 中讲的**社区 Action** 的典型代表。它由 GitHub 官方维护，是所有 Workflow 中引用次数最多的 Action。

#### 4.3.8 Step 2: `actions/setup-python@v5` — 设置 Python 环境

```yaml
- name: Set up Python 3.10
  uses: actions/setup-python@v5
  with:
    python-version: '3.10'
```

| 字段 | 含义 |
|---|---|
| `name: Set up Python 3.10` | 步骤的显示名称，会出现在 Actions 日志中 |
| `uses: actions/setup-python@v5` | 使用 GitHub 官方的 Python 环境安装 Action，主版本 5 |
| `with` | 向 Action 传递**参数**的关键字 |

**`with` — 向 Action 传递参数的标准方式**

`with` 是 GitHub Actions 中向 Action 传递参数的标准关键字。不同的 Action 接受的 `with` 参数完全不同，具体有哪些参数需要查阅该 Action 的 `action.yml` 文件或 README 文档。


#### 4.3.9 Step 3: 安装依赖

```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install flake8 pytest
    if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
```

| 字段 | 含义 |
|---|---|
| `run` | 在虚拟机的 Shell 中**直接执行命令** |
| `\|` | YAML 的**多行字符串标记**（Literal Block Scalar），保留换行符，所有缩进行视为一条命令 |
| `python -m pip install --upgrade pip` | 升级 pip 到最新版，避免因 pip 版本过旧导致安装失败 |
| `pip install flake8 pytest` | 安装 flake8（代码检查）和 pytest（测试框架） |
| `if [ -f requirements.txt ]; then ... fi` | Shell 条件判断：如果项目根目录存在 `requirements.txt`，则安装其中列出的所有依赖 |

> 🐞 **常见坑**：`run: |` 中的竖线 `|` 不能省略。如果只写 `run: echo hello` 那是单行命令，没问题。但如果写了多行命令却没有 `|`，YAML 只会把第一行当作命令，其余行会被当成 YAML 结构的一部分而报错。

> 💡 **核心洞见**：`if [ -f requirements.txt ]` 这一行体现了模板的**健壮性设计**——不是所有 Python 项目都需要 `requirements.txt`。加了这个条件判断，即使项目没有该文件也不会报错。这是一个值得学习的好习惯。

#### 4.3.10 Step 4: flake8 代码规范检查

```yaml
- name: Lint with flake8
  run: |
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

**flake8 是什么？**

flake8 是 Python 社区最常用的**代码风格检查工具（Linter）**。它会扫描源代码，指出不符合 PEP 8 规范的地方以及潜在的语法错误。

> ⚠️ **注意事项**：flake8 是 **Linter**（检查器），**不是** **Formatter**（格式化器）。它只会**告诉你哪里不对**，但不会替你修改代码。如果需要自动修正代码风格，需要用 `black`、`autopep8` 或 `isort` 等工具。

**两条 flake8 命令的分工**

| 命令 | 关键参数 | 检查内容 | 失败行为 |
|---|---|---|---|
| 第 1 条 | `--select=E9,F63,F7,F82` | 只检查**严重错误**：语法错误、未定义变量名、缩进错误等 | **会**导致 Job 失败 |
| 第 2 条 | `--exit-zero` | 检查**风格问题**：圈复杂度、行长度等 | **不会**导致 Job 失败（因为 `--exit-zero` 强制返回 0） |

> 💡 **核心洞见**：模板将 flake8 检查分成**严重错误**和**风格警告**两个层级。第一层让真正的 Bug 直接阻断流水线（不浪费时间去检查风格），第二层只做记录不影响通过。这种**分级检查**的策略在工业级 CI 中非常实用。

| 参数 | 全称/含义 | 作用 |
|---|---|---|
| `--count` | 计数 | 在输出末尾显示总错误数 |
| `--select=E9,F63,F7,F82` | 选择检查规则 | E9=语法错误，F63=比较问题，F7=逻辑错误，F82=未定义变量 |
| `--show-source` | 显示源码 | 出错时显示对应的源代码行 |
| `--statistics` | 统计 | 按错误类型分类统计 |
| `--exit-zero` | 强制退出码 0 | 即使发现问题也返回成功，不阻断流水线 |
| `--max-complexity=10` | 最大圈复杂度 | 超过 10 的函数会被标记 |
| `--max-line-length=127` | 最大行长度 | 超过 127 字符的行会被标记 |

#### 4.3.11 被删除的 Step 5: pytest 测试

```yaml
- name: Test with pytest
  run: |
    pytest
```

老师在学习过程中将这一步骤**直接删除**了。原因很简单：示例项目里只有一个 `main.py`，没有写任何 pytest 测试用例。

> 🐞 **常见坑**：GitHub 模板是**通用模板**，不是为你的项目量身定做的。使用模板后，必须逐步骤检查是否与你的实际项目匹配。如果保留 pytest 但项目没有测试文件，pytest 会因找不到测试而返回非零退出码，导致整个 Job 标记为失败。

**删除方法**：在 GitHub 的在线编辑器中，直接选中 pytest 这一段（包括 `- name` 和 `run`），按 Delete 键删除即可。

---

### 4.4 添加第二个 Job：PyInstaller 打包

在理解并微调了模板 YAML 之后，老师新增了**第二个 Job**——使用 PyInstaller 将 Python 文件打包成 Windows 可执行程序（`.exe`）。新增的 Job 与原有的 `build` Job 保持**平级关系**。

#### 📖 完整 YAML（含两个 Job）

```yaml
# 文件名: .github/workflows/python-app.yml
# 功能: 双 Job 并行 — Job1 代码检查，Job2 打包 Windows 可执行文件

name: Python application

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

permissions:
  contents: read

jobs:
  build:                                   # Job 1: 代码检查（Ubuntu）
    runs-on: ubuntu-latest                 #   运行在 Ubuntu 虚拟机
    steps:
      - uses: actions/checkout@v4         # Step 1: 检出代码
      - name: Set up Python 3.10
        uses: actions/setup-python@v5     # Step 2: 安装 Python 环境
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |                             # Step 3: 安装依赖
          python -m pip install --upgrade pip
          pip install flake8
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
      - name: Lint with flake8
        run: |                             # Step 4: 代码规范检查
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
          flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

  pyinstaller:                             # Job 2: 打包可执行文件（Windows）★新增
    runs-on: windows-latest                #   运行在 Windows 虚拟机
    steps:
      - uses: actions/checkout@v4         # Step 1: 检出代码（每个 Job 独立检出）
      - name: Build executable with PyInstaller
        uses: JackMcKew/pyinstaller-action-windows@main  # 使用社区 PyInstaller Action
        with:                              #   向 PyInstaller Action 传递参数
          python-version: '3.12'           #   参数1: 打包使用的 Python 版本
          spec: main.py                    #   参数2: 入口 Python 文件
          package-name: sharp-package      #   参数3: 输出压缩包的名称
          options: --onefile               #   参数4: 打包为单个 .exe 文件
```

#### 🔍 新增 Job 逐行解析

##### Job 层级关系：平级 = 并行

```yaml
jobs:
  build:         # Job 1 — 代码检查
    ...
  pyinstaller:   # Job 2 — 打包（新增）
    ...
```

注意 `pyinstaller` 和 `build` 的缩进完全一致——它们都位于 `jobs` 下，是同级别的子节点。这意味着 GitHub Actions 将**同时启动两台虚拟机，并行执行两个 Job**。它们互不依赖，互不等待。

##### `runs-on: windows-latest` — 为什么选 Windows？

```yaml
runs-on: windows-latest
```

| 决策理由 | 说明 |
|---|---|
| PyInstaller 在 Windows 上打包出 `.exe` | 在 Windows 上打包生成的 `.exe` 文件可以在任何 Windows 电脑上直接双击运行 |
| 目标用户使用 Windows | 大多数桌面用户使用 Windows 系统 |

> 💡 **核心洞见**：两个 Job 使用了不同的操作系统（`ubuntu-latest` vs `windows-latest`）。这说明一个 Workflow 中的不同 Job 可以在**不同的平台上独立运行**——这是 GitHub Actions 非常强大的能力。Ubuntu Job 做代码检查，Windows Job 做打包，各司其职。

##### `uses: JackMcKew/pyinstaller-action-windows@main`

```yaml
uses: JackMcKew/pyinstaller-action-windows@main
```

这是一个由社区开发者 **JackMcKew** 提供的 PyInstaller GitHub Action，专门用于在 Actions 中自动将 Python 项目打包为 Windows 可执行文件。

| 组成部分 | 含义 |
|---|---|
| `JackMcKew` | Action 开发者的 GitHub 用户名 |
| `pyinstaller-action-windows` | Action 仓库的名称 |
| `@main` | 引用的分支名（`main` 分支的最新代码） |

> ⚠️ **注意事项**：使用 `@main` 意味着始终引用该仓库 `main` 分支的**最新提交**。如果作者推送了破坏性更新，你的 Workflow 可能会突然失败。生产项目中建议锁定到具体的发布标签，如 `@v1.0.0` 或 `@main` 后跟具体的 commit SHA。

##### `with` 参数详解

```yaml
with:
  python-version: '3.12'
  spec: main.py
  package-name: sharp-package
  options: --onefile
```

`with` 是向 Action 传递参数的标准方式——每个 Action 定义了自己的参数列表，使用者通过 `with` 传入具体值。

| 参数 | 含义 | 本例取值 | 说明 |
|---|---|---|---|
| `python-version` | 打包使用的 Python 版本 | `'3.12'` | 注意加引号，避免 `3.12` 被解析为数字 |
| `spec` | 入口 Python 文件 | `main.py` | PyInstaller 从这个文件开始分析依赖链 |
| `package-name` | 输出压缩包的名称 | `sharp-package` | 不含扩展名，最终下载的文件名为 `sharp-package.zip` |
| `options` | 传递额外的 PyInstaller 命令行选项 | `--onefile` | `--onefile` 表示将所有依赖打包进**一个** `.exe` 文件 |

> 🐞 **常见坑**：`python-version` 的值必须用**字符串**格式书写（`'3.12'` 而非 `3.12`）。在 YAML 中，`3.12` 可能被解析为数字。虽然 `3.12` 不丢精度，但 `3.10` 会被解析为 `3.1`——导致安装了 Python 3.1 而非 3.10。**所有版本号统一加引号**是最稳妥的做法。

**`--onefile` 是什么？**

PyInstaller 的 `--onefile` 选项表示：将所有 Python 依赖、库文件和解释器一起打包进**一个单独的 `.exe` 文件**。如果不加这个选项，PyInstaller 默认会输出一个包含 `.exe` 文件和大量 `.dll` 依赖的文件夹。对于分发场景，单个文件显然更方便。

#### 🔄 两个 Job 的执行流程

```
提交代码到 main 分支
        │
        ▼
  GitHub 检测到 push 事件
        │
        ▼
  Workflow 被触发
        │
        ├──────────────────────┐
        ▼                      ▼
  ┌─────────────┐      ┌──────────────┐
  │ Job: build  │      │Job:pyinstaller│
  │ Ubuntu VM   │      │ Windows VM   │
  │             │      │              │
  │ 1.checkout  │      │ 1.checkout   │
  │ 2.setup-py  │      │ 2.pyinstaller│
  │ 3.install   │      │     ↓        │
  │ 4.flake8    │      │ 生成 .exe    │
  │     ↓       │      │     ↓        │
  │  ✔ 完成     │      │ ✔ artifacts  │
  └─────────────┘      └──────────────┘
        │                      │
        └──────┬───────────────┘
               ▼
      两个 Job 都打 ✅
      Workflow 执行成功
```

> 💡 **核心洞见**：注意 `pyinstaller` Job 的 steps 中**也有一条** `uses: actions/checkout@v4`。这不是重复——每个 Job 有**独立的虚拟机**，Job A 的虚拟机上有的文件，Job B 的虚拟机上并没有。所以每个需要代码的 Job 都必须自己检出代码。

---

### 4.5 提交、触发与执行观察

#### 🔄 提交触发

在 GitHub 的在线编辑器中编辑完 YAML 文件后，点击右上角的 **Commit changes** 按钮。选择 **Commit directly to the `main` branch** 并提交。

由于 `on.push.branches` 配置了 `[ "main" ]`，这次提交立即触发了 Workflow。

> 💡 **核心洞见**：提交即触发——不需要手动点击任何"运行"按钮。这正是 CI（持续集成）的核心理念：每次代码变更**自动**触发检查和构建。

#### 👀 观察执行过程

**1. 黄色转圈**：进入仓库的 Actions 页面，立即可以看到一条新的 Workflow 运行记录，旁边有一个**黄色旋转圆圈**，表示正在执行。

**2. 点击查看详情**：点击该运行记录，进入 Workflow 的运行详情页。页面左侧显示所有 Job 的列表，可以看到 `build` 和 `pyinstaller` 两个 Job。

**3. 并行执行**：两个 Job 同时运行，各自独立推进。`build` Job 通常只需几秒到十几秒（只做代码检查），而 `pyinstaller` Job 可能需要几十秒到一分钟（需要下载 Python 环境、安装 PyInstaller、编译打包）。

**4. 查看实时日志**：点击任意一个 Job，可以展开看到每一步的实时执行日志。日志内容包括：
- 每步的开始时间和耗时
- 命令的执行输出
- 警告信息和错误信息（如有）

**5. 完成标记**：当每个步骤都执行完毕，Job 旁边会显示**绿色对勾** ✅ 和总耗时（如 `build in 12s`、`pyinstaller in 45s`）。Workflow 页面的黄色转圈也会变成绿色对勾。

#### ✅ 验证结果

**验证方式一：Job 状态**

两个 Job 都显示绿色对勾 ✅ = 执行完全成功。

**验证方式二：Summary 页面**

在 Workflow 运行详情页的底部，找到 **Summary**（摘要）区域。这里汇总了整个 Workflow 的执行结果，包括：
- 总运行时间
- 每个 Job 的详细状态
- **Annotations**（警告和错误提示）
- **Artifacts**（构建产物）

**验证方式三：下载并运行 Artifacts**

在 Summary 页面的 **Artifacts** 区域，可以看到一个名为 `sharp-package` 的下载链接。这就是 PyInstaller Job 打包出来的结果文件。

1. 点击 `sharp-package` 下载压缩包
2. 解压压缩包，找到其中的 `main.exe`
3. 在 Windows 系统上双击运行（或在终端中执行）
4. 看到终端输出 `Hello, GitHub Actions!`

至此，验证完成：GitHub 在它的 Windows 服务器上，成功地自动为你打包构建出了一个可运行的 `.exe` 程序。

> 💡 **核心洞见**：Artifacts 是 Workflow 运行过程中产生的**输出文件**。它们会自动上传并保留在 GitHub 上（默认保留 90 天），供后续 Job 使用或开发者下载。Artifacts 的大小会计入存储配额。

---

### 4.6 排错指南

#### 🐛 排错实录 1：pytest 找不到测试文件导致 Job 失败

**❌ 错误现象**

Workflow 运行到 pytest 步骤时报错停止，Job 显示红色叉号 ❌。

```
Run pytest
============================= test session starts ==============================
collected 0 items

============================ no tests ran in 0.01s =============================
Error: Process completed with exit code 5.
```

**🔍 原因分析**

pytest 在项目中找不到任何测试文件（没有以 `test_` 开头或 `_test` 结尾的 `.py` 文件）。pytest 收集到 0 个测试用例，认为这是异常情况，返回退出码 5。GitHub Actions 将**任何非零退出码**视为失败。

**✅ 解决方案**

如果你的项目暂时没有测试代码，直接将 pytest 步骤从 YAML 中删除：

```yaml
# 删除以下整段（共 3 行）
#       - name: Test with pytest
#         run: |
#           pytest
```

**📝 经验总结**

模板是"通用配方"，不是为你的具体项目定制的。使用任何模板后，第一步就是检查每一步是否适用于你的实际情况。不适用就删除，不要留着"以后再用"——它现在就会导致失败。

---

#### 🐛 排错实录 2：`python-version` 值不加引号导致版本错误

**❌ 错误写法**

```yaml
with:
  python-version: 3.10   # 危险：YAML 可能将 3.10 解析为数字 3.1
```

**🚨 可能后果**

GitHub Actions 可能尝试安装 Python 3.1（因为 `3.10` 被解析为数字后等于 `3.1`），导致安装失败或安装了错误的版本。

**🔍 原因分析**

YAML 解析器在处理不带引号的 `3.10` 时，会将其识别为**浮点数**。浮点数 `3.10` 在数学上等于 `3.1`。因此传给 `setup-python` 的版本号变成了 `3.1` 而非 `3.10`。

**✅ 正确写法**

```yaml
with:
  python-version: '3.10'   # 安全：单引号强制解析为字符串
```

**📝 经验总结**

在 YAML 中书写版本号时，**凡是包含小数点的版本号一律加引号**。这不仅适用于 `python-version`，也适用于 `node-version`、`java-version` 等任何版本参数。

---

#### 🐛 排错实录 3：忘记在新增 Job 中检出代码

**❌ 错误写法**

```yaml
pyinstaller:
  runs-on: windows-latest
  steps:
    # ❌ 缺少 checkout！虚拟机上没有代码文件
    - name: Build executable with PyInstaller
      uses: JackMcKew/pyinstaller-action-windows@main
      with:
        spec: main.py   # 找不到 main.py！
```

**🚨 报错信息**

```
FileNotFoundError: [Errno 2] No such file or directory: 'main.py'
```

**🔍 原因分析**

每个 Job 拥有**独立的虚拟机**，Job A 和 Job B 的文件系统完全隔离。新增的 `pyinstaller` Job 运行在一个全新的 Windows 虚拟机上，如果不执行 checkout，虚拟机上是空的，没有任何代码文件。

**✅ 正确写法**

```yaml
pyinstaller:
  runs-on: windows-latest
  steps:
    - uses: actions/checkout@v4    # ✅ 必须在每个需要代码的 Job 中独立检出
    - name: Build executable with PyInstaller
      uses: JackMcKew/pyinstaller-action-windows@main
      with:
        spec: main.py
```

**📝 经验总结**

**每个 Job 都是独立的沙盒**。这是 GitHub Actions 最基本的隔离模型。记住这条原则：哪个 Job 需要代码，哪个 Job 就要自己 checkout。

---

### 4.7 收费与配额

#### 💰 GitHub Actions 计费规则

> ⚠️ **注意事项**：计费规则可能随时间调整，以下以当前（2026 年 7 月）官方定价为准。最新价格请查阅 [GitHub Actions 官方定价页](https://github.com/features/actions)。

| 仓库类型 | 免费额度 | 超出后计费方式 |
|---|---|---|
| **公共仓库（Public）** | **完全免费**，无限时长 | 不收费 |
| **私有仓库（Private）** | 每月 **2,000 分钟** | 超出后按分钟计费，具体费率取决于 Runner 类型和操作系统 |
| 存储上限（免费版） | **500 MB** | Artifacts 和 GitHub Packages 共享此额度 |

**关键结论**：

- 如果你的仓库都是**公开的**（如学习项目、开源项目、个人作品展示），GitHub Actions **完全不收费**。老师的仓库全是公开的，所以 Actions 额度"一点也没用"。
- 只有**私有仓库**才会消耗免费额度。
- 2,000 分钟/月对于个人项目绰绰有余——按每次 Workflow 执行 1 分钟计算，每天可以跑 65+ 次。

#### 📊 如何查看当前用量

查看路径：

```
GitHub 右上角头像 → Settings → Billing and plans → Plans and usage → Usage this month
```

该页面会展示以下用量数据：

| 指标 | 含义 |
|---|---|
| **Actions minutes** | 本月已使用的 Actions 执行分钟数（仅私有仓库计入） |
| **GitHub Packages storage** | GitHub Packages 的存储用量 |
| **Storage for Actions artifacts** | Actions 构建产物的存储用量 |

对于公开仓库，这些指标通常全部显示为 `0 / unlimited`。

> 💡 **核心洞见**：GitHub Actions 的免费额度对于学习和个人开发来说相当慷慨。公开仓库无限免费 + 私有仓库每月 2,000 分钟——这意味着你可以放心地使用 Actions 来构建 CI/CD 流水线，而无需担心产生费用。


---
## 五、Python 项目自动发布 Release

### 5.1 场景引入：软件交付的两种方式

#### 🧠 直观理解

CI/CD 的终极目标是把代码变成用户可以使用的产品。在 GitHub Actions 中，"交付"环节主要有两种模式：一种是**把软件打包成可执行文件，发布到 Release 页面供用户下载**；另一种是**把项目编译打包后，直接推送到服务器上完成部署**。本模块讲解第一种——通过 Workflow 自动创建 GitHub Release，让用户像下载普通软件一样获取你的 Python 程序。

#### 📖 详细解释

两种交付方式的差异，本质上是由"用户如何使用你的软件"决定的：

| 维度 | Release 发布下载 | 服务器部署 |
|---|---|---|
| 交付产物 | 可执行文件（.exe / .app / 二进制） | 部署包（JAR / WAR / Docker 镜像） |
| 目标使用者 | 最终用户（下载、安装、运行） | 服务器（自动拉取、启动服务） |
| 触发时机 | 创建版本 Tag（如 v1.0） | Push 到指定分支（如 main） |
| 典型场景 | 桌面软件、CLI 工具、客户端应用 | Web 服务、API 后端、微服务 |
| 核心 Action | `softprops/action-gh-release` | `ssh-deploy`、`docker/build-push-action` |
| 用户操作 | 打开 Releases 页面 → 下载 → 双击运行 | 无感知（服务自动更新） |

> 🔗 **关联知识**：Tag 是 Git 中标记特定提交的"里程碑指针"。本模块使用的 Tag 触发器是 M03 中 Event（事件）概念的具体落地——`on.push.tags` 监听的就是"推送标签"这个 Git 事件。

---

### 5.2 创建 Release Workflow（从零手写）

#### 🎯 本节目标

> 学完本节后，你将能够：
> - [ ] 从零手写一个自动发布 Release 的 Workflow YAML 文件
> - [ ] 理解 Tag 触发器、写权限声明、条件判断等进阶配置的含义
> - [ ] 使用 `softprops/action-gh-release` 将 PyInstaller 打包产物上传到 Release

#### 🧠 与 M04 的关键区别：从模板到从零手写

在 M04 中，我们通过点击「New workflow」选择一个**推荐模板**来起步。模板的作用是搭好脚手架——Workflow 的骨架已经有了，你在里面填空就行。

本模块不同：我们点击「set up a workflow yourself」，从一张**空白文件**开始。这意味着你不再是"填空者"，而是"架构师"——你需要自己写出 `name`、`on`、`permissions`、`jobs`、每一步的 `uses` 或 `run`。这更接近真实项目的开发场景——大多数时候，没有现成模板能精确覆盖你的需求，你必须从零搭建自己的 CI/CD 流水线。

#### 💻 完整 YAML 文件

```yaml
# 文件名: .github/workflows/release.yml
# 功能: 当推送 v 开头的 tag 时，自动打包 Python 项目并发布 GitHub Release

name: Create Release

# ============================================================
# 一、触发器（何时执行这个 Workflow）
# ============================================================
on:
  push:
    tags:
      - 'v*'          # 只有 v 开头的 tag 才会触发，如 v1.0、v2.0.0、v0.1-beta

# ============================================================
# 二、权限（这个 Workflow 被授权做什么）
# ============================================================
permissions:
  contents: write       # 创建 Release 需要写入仓库内容的权限

# ============================================================
# 三、任务定义（具体做什么事）
# ============================================================
jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      # --- 阶段一：准备环境 ---
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      # --- 阶段二：打包构建 ---
      - name: Install PyInstaller
        run: pip install pyinstaller

      - name: Build executable
        run: pyinstaller --onefile main.py

      # --- 阶段三：发布 Release ---
      - name: Create Release
        uses: softprops/action-gh-release@v2
        if: startsWith(github.ref, 'refs/tags/')
        with:
          files: |
            dist/*
```

---

#### 5.2.1 触发器配置：Tag 触发

##### 🧠 直观理解

```
┌──────────────┐     推送 tag v1.0      ┌──────────────┐
│   你的电脑    │ ──────────────────────▶ │   GitHub      │
│  git tag v1.0 │                        │               │
│  git push     │                        │  on.push.tags │
│  origin v1.0  │                        │  匹配 'v*'    │
└──────────────┘                        │      ✅       │
                                        │  启动 Workflow │
                                        └──────────────┘
```

`on.push.tags: ['v*']` 这行的意思是：**"当有人推送一个以 v 开头的标签到仓库时，启动我这个 Workflow"**。不是所有推送都触发，只有贴上"v"标签的推送才启动流水线。

##### 📖 详细解释

**`v*` 不是正则表达式，是 Glob 模式**

初学者最容易犯的错误就是把 `v*` 当成正则表达式。实际上 GitHub Actions 的 `on.push.tags` 使用的是 **Glob 模式**（文件名通配符匹配），两者的行为有微妙差异：

| 模式 | 类型 | `v*` 含义 | 能匹配 | 不能匹配 |
|---|---|---|---|---|
| `v*` | Glob | v 开头，后面跟任意字符（含空） | `v1.0`、`v2.0.0`、`v0.1-beta`、`v` | `release-v1`（v 不在开头） |
| `v.*` | 正则 | v 后面至少跟一个任意字符 | `v1`、`va` | `v`（后面无字符）、`v1.0`（点号只匹配一个字符） |

Glob 模式下，`*` 匹配任意字符串（包括空字符串），`**` 匹配包含路径分隔符的任意字符串，`?` 匹配恰好一个字符。要匹配 `v1.0.0` 和 `v1.0` 但不匹配 `v`（空版本号），可以用 `v*.*`。

**为什么用 Tag 触发而不是 Branch Push？**

你在开发过程中每天会 Push 无数次代码，但不可能每次 Push 都发布一个新版本。Tag 本质上是一种"人类决定"——当团队认为代码已经达到可发布的质量时，手动打一个 Tag（如 `v1.0.0`），"宣布"这是 v1.0.0 版本。Workflow 监听 Tag Push 事件，自动完成打包和发布。

> 💡 **核心洞见**：Tag 将"发布决策权"保留在人手中，将"发布执行过程"自动化。你决定什么时候发布，机器负责怎么做。

---

#### 5.2.2 权限配置

##### 🧠 直观理解

GitHub Actions 默认给每个 Workflow 分配一个临时的 `GITHUB_TOKEN`，这个 Token 就像一张"临时门禁卡"——默认只能读，不能写。创建 Release 相当于往仓库门口贴一张"新版本发布"的公告——这需要写权限。你必须向 GitHub 声明："我这个 Workflow 需要写权限"。

##### 📖 详细解释

```yaml
permissions:
  contents: write
```

`contents` 权限范围涵盖仓库内容相关的所有写操作：推送代码、创建分支、创建/修改 Release、上传 Release Assets。如果不配置这一行，`softprops/action-gh-release` 在尝试创建 Release 时会收到 `403 Resource not accessible by integration` 错误——GitHub 服务器拒绝了你的写请求。

> ⚠️ **注意事项**：GitHub Actions 遵循"最小权限原则"——默认只有读权限，需要什么权限你必须显式声明。这是一个安全设计：一个被恶意修改的 Workflow 不可能在你不知情的情况下获得过多的权限。

---

#### 5.2.3 Build Job：PyInstaller 打包

##### 🔗 关联知识

打包阶段的核心逻辑与 M04 一致，这里快速回顾：

1. **Checkout**（`actions/checkout@v4`）：将当前 Tag 对应的代码拉取到 Runner 上，后续步骤才能操作这些文件
2. **Setup Python**（`actions/setup-python@v5`）：在 Ubuntu Runner 上安装 Python 3.12 运行时
3. **安装 PyInstaller**（`pip install pyinstaller`）：Runner 默认不安装 PyInstaller，需要手动通过 pip 安装
4. **打包**（`pyinstaller --onefile main.py`）：将 `main.py` 及其依赖打包成单一可执行文件，输出到 `dist/` 目录

> 🔗 **前置知识**：关于 PyInstaller 打包的详细解释和 `--onefile` 参数的含义，详见 [四、第一个 Action 实战](#四第一个-action-实战)。

---

#### 5.2.4 创建 Release：`softprops/action-gh-release`

##### 🧠 直观理解

打包完成后，`dist/` 目录下有了可执行文件。现在你需要一个帮手来：1）在 GitHub 上创建一个 Release 页面；2）把 `dist/` 下的文件作为附件挂上去。`softprops/action-gh-release` 就是专门做这件事的社区 Action——你告诉它文件在哪，它负责创建 Release 并上传。

##### 📖 详细解释

**为什么要用社区 Action 而不是自己调 GitHub API？**

当然可以通过 `gh release create` CLI 或者直接调用 GitHub REST API 来创建 Release。但 `softprops/action-gh-release` 封装了所有细节：自动使用当前 Tag 名称作为 Release 标题、自动关联提交信息作为描述、支持 Glob 文件匹配、处理上传失败重试。一行 `uses` + 一个 `files` 参数，三行配置完成所有工作。

> 💡 **核心洞见**：`softprops/action-gh-release` 是目前社区最推荐的 Release 创建 Action。GitHub 官方的 `actions/create-release` 已被标记为不推荐使用（deprecated）。选择社区 Action 时，关注其 Star 数、更新频率、是否通过 GitHub 验证——这些都是衡量可靠性的重要指标。

---

##### Step 级条件判断：`if` 与 `github.ref`

```yaml
if: startsWith(github.ref, 'refs/tags/')
```

这行代码使用了 GitHub Actions 的**条件执行**（Conditional Execution）功能。它的含义是：**只有当 `github.ref` 的值以 `refs/tags/` 开头时，才执行这个 Step**。

**`github.ref` 是什么？**

`github.ref` 是 GitHub Actions 提供的一个**上下文变量**（Context）。上下文变量让你在 Workflow YAML 中访问运行时的动态信息。就像编程语言中的变量一样，它们在不同的事件中拥有不同的值：

| 上下文变量 | 含义 | Tag Push 时的值 | 普通 Branch Push 时的值 |
|---|---|---|---|
| `github.ref` | 触发 Workflow 的完整 Git 引用 | `refs/tags/v1.0` | `refs/heads/main` |
| `github.ref_name` | 去掉 `refs/` 前缀的短名称 | `v1.0` | `main` |
| `github.event_name` | 触发事件类型 | `push` | `push` |
| `github.sha` | 触发提交的 SHA 哈希 | `a1b2c3d4...` | `a1b2c3d4...` |
| `github.repository` | 仓库全名（owner/repo） | `owner/my-project` | `owner/my-project` |

当推送 Tag `v1.0` 时，`github.ref` 的值是 `refs/tags/v1.0`，`startsWith('refs/tags/v1.0', 'refs/tags/')` 返回 `true`，Step 正常执行。

> ❓ **常见疑问**：已经有 `on.push.tags: ['v*']` 了，为什么 Step 里还要加 `if` 条件？这不是多余吗？
>
> **回答**：这是因为触发器和条件判断在**不同层级**起作用：
> - `on.push.tags` 是 **Workflow 级**过滤——决定"这个 Workflow 要不要启动"
> - `if` 是 **Step 级**过滤——决定"这个 Workflow 中的某个 Step 要不要执行"
>
> 在本例中两者的效果确实是重叠的，但 `if` 起到了**双重保险**的作用：万一将来有人修改了 `on` 触发器（比如改成 `on: push`），Release 创建步骤也不会在普通 Push 中误执行。这是一种防御性编程思路。

---

##### `with` 参数：指定上传文件

```yaml
with:
  files: |
    dist/*
```

- `files`：指定要上传到 Release Assets 的文件路径，支持 Glob 模式
- `dist/*`：匹配 `dist/` 目录下的所有文件（PyInstaller 打包的所有产物）
- 管道符 `|`（YAML 多行字符串）：允许在 `files` 下列出多个路径，每行一个

##### 行级解析表

| 行 | 代码 | 解释 |
|---|---|---|
| L3 | `name: Create Release` | 定义 Workflow 显示名称，在 Actions 页面中展示 |
| L7-L9 | `on: push: tags: ['v*']` | 监听 v 开头的 Tag Push 事件 |
| L13-L14 | `permissions: contents: write` | 显式申请仓库内容写权限，用于创建 Release |
| L17 | `jobs:` | 定义任务集合 |
| L18 | `build:` | 任务名称，可以自定义 |
| L19 | `runs-on: ubuntu-latest` | 指定运行环境为最新版 Ubuntu |
| L23 | `uses: actions/checkout@v4` | 拉取代码到 Runner |
| L25-L27 | `uses: actions/setup-python@v5 ... '3.12'` | 在 Runner 上安装 Python 3.12 |
| L30 | `run: pip install pyinstaller` | 用 pip 安装 PyInstaller 打包工具 |
| L33 | `run: pyinstaller --onefile main.py` | 将 main.py 打包为单一可执行文件 |
| L37 | `uses: softprops/action-gh-release@v2` | 使用社区 Action 创建 Release |
| L38 | `if: startsWith(github.ref, 'refs/tags/')` | 条件守卫：仅在 Tag 上下文中执行 |
| L40-L41 | `files: \| \n  dist/*` | 上传 dist 目录下所有打包产物 |

---

### 5.3 触发与执行

#### 🏗️ 前置准备

在开始之前，请确认以下条件已满足：
- 代码（含 `.github/workflows/release.yml`）已推送到 GitHub 仓库
- 本地已克隆该仓库，且位于仓库根目录下
- `main.py` 是项目的入口文件，内容可正常运行

#### 💻 Step-by-Step

**Step 1: 创建 Tag**

在 Git 中，Tag 是指向特定提交的固定引用。有两种方式创建 Tag。

方式一：命令行（推荐用于教学和文档记录）

```bash
# 创建一个名为 v1.0 的轻量标签，指向当前 HEAD 提交
git tag v1.0
```

如果需要附带版本说明，使用附注标签：

```bash
# 创建附注标签，附带版本说明信息
git tag -a v1.0 -m "发布 v1.0 版本：首次 Release 自动化"
```

> 两种标签都能触发 Workflow。轻量标签只是一个指向提交的指针，附注标签在 Git 数据库中存储为独立对象（含标签名、标签信息、时间戳、打标签者），更适合正式发布场景。

**Step 2: 推送 Tag 到远程仓库**

```bash
# 推送 v1.0 标签到 origin 远程仓库
git push origin v1.0
```

> ⚠️ **注意事项**：普通的 `git push` 不会推送 Tag，必须显式指定 Tag 名称或使用 `git push origin --tags` 推送所有本地 Tag。

完整的一行命令版本：

```bash
git tag v1.0 && git push origin v1.0
```

方式二：GitHub Desktop（GUI 操作）

1. 在 History 面板中，右键点击要打 Tag 的提交
2. 选择「Create Tag」
3. 输入 Tag 名称，必须以 v 开头（如 `v1.0`）
4. 点击「Create Tag」
5. 点击「Push origin」将 Tag 推送到远程

#### 🔄 完整执行流程

```
git tag v1.0 && git push origin v1.0
            │
            ▼
┌──────────────────────────────────────────────────┐
│  GitHub 收到 Tag Push 事件                        │
│  on.push.tags: ['v*'] → 'v1.0' 匹配成功 ✅        │
│  Workflow "Create Release" 启动                   │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│  Step 1: Checkout code                            │
│  actions/checkout@v4 拉取 Tag v1.0 对应的代码快照  │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│  Step 2: Setup Python 3.12                        │
│  actions/setup-python@v5 在 Ubuntu Runner 上安装   │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│  Step 3-4: Build 构建                             │
│  pip install pyinstaller                          │
│  pyinstaller --onefile main.py                    │
│  产物: dist/ 目录下的可执行文件                     │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│  Step 5: Create Release                           │
│  if: startsWith(github.ref, 'refs/tags/') → ✅    │
│  softprops/action-gh-release@v2                   │
│  上传 dist/* → Release Assets                     │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
                ┌──────────────┐
                │  ✅ Release   │
                │  就绪可下载    │
                └──────────────┘
```

---

### 5.4 结果验证

#### ✅ 查看 Release

Workflow 执行成功后，进入仓库首页。在右侧 Sidebar 中可以看到「Releases」区域，展开后会显示新创建的 `v1.0` Release。点击进入 Release 详情页查看完整内容。

#### 📦 Release 页面结构解析

一个 Release 页面由以下关键部分组成：

| 区域 | 内容 | 说明 |
|---|---|---|
| 标题区 | `v1.0` | 默认使用 Tag 名称作为 Release 标题 |
| 描述区 | 提交信息 | 自动使用 Tag 关联的提交信息作为 Release 描述文字 |
| **Assets 区** | 可执行文件（如 `main`） | `dist/*` 匹配到的打包产物，这是用户真正需要下载的文件 |
| Source code 区 | `zip` / `tar.gz` | GitHub 自动生成的源代码压缩包，与 Assets 无关，每个 Release 都有 |

> ⚠️ **注意事项**：Source code 区的压缩包是 GitHub 自动附加的源代码归档，并不是你通过 `files` 参数上传的内容。你的 `dist/*` 产物会出现在上方的 Assets 区域——这才是用户真正关心的下载项。

#### ✏️ 补充 Release 说明

默认的 Release 描述仅包含提交信息，建议手动补充版本说明，让用户知道这个版本更新了什么：

1. 点击 Release 页面右上角的「Edit」按钮
2. 修改标题为更完整的描述，如「发布 v1.0 版本」
3. 在描述中列出本次更新的功能清单：

```markdown
## 🚀 新增功能

- 支持命令行参数解析
- 新增配置文件读取功能

## 🐛 修复

- 修复了退出时程序崩溃的问题
```

4. 点击「Update Release」保存

#### ✅ 验证可执行文件

下载 Assets 中的可执行文件，在本地终端运行验证：

```bash
# macOS / Linux
chmod +x main
./main

# 程序正常输出，说明整个 CI/CD 流水线完全成功
```

如果程序能正常运行并输出预期结果，说明从代码提交、Tag 触发、PyInstaller 打包、到 Release 发布的**全自动化流水线**已经打通。

---

### 🐛 常见问题排查

#### 问题 1：推送 Tag 后 Workflow 没有触发

**🚨 现象**：执行 `git push origin v1.0` 后，GitHub Actions 页面没有任何运行记录。

**🔍 原因分析**：
1. Tag 名称不是 v 开头（如 `release-1.0`），不匹配 Glob 模式 `v*`
2. Workflow 文件不在 `.github/workflows/` 目录下，或扩展名不是 `.yml`/`.yaml`
3. Tag 被推送到了错误的远程仓库

**✅ 解决**：检查 Tag 名称（`git tag -l`），确认 Workflow 文件路径和扩展名正确，核对远程仓库地址（`git remote -v`）。

---

#### 问题 2：Release 创建了但没有 Assets 文件

**🚨 现象**：Release 页面有 Source code 压缩包，但上方 Assets 区域是空的。

**🔍 原因分析**：
1. 前面的 Build Step 执行失败了，`dist/` 目录没有生成文件——但 Workflow 没有在此步中止（需检查日志确认）
2. `files` 参数的路径写错了（如写了 `dist/main` 但产物名叫 `dist/main.exe`）
3. `pyinstaller` 打包本身报错（如缺少依赖、入口文件不在根目录等）

**✅ 解决**：在 Actions 日志中逐 Step 检查，重点关注 Build 那一步的控制台输出，确认 `dist/` 目录是否生成、文件名是什么。

---

#### 问题 3：`softprops/action-gh-release` 报权限错误

**🚨 现象**：日志中出现 `403 Resource not accessible by integration` 或 `permission denied` 相关错误。

**🔍 原因分析**：
`permissions.contents` 未设置为 `write`。默认的 `GITHUB_TOKEN` 只有读权限，无法创建 Release。

**✅ 解决**：在 Workflow YAML 中确认 `permissions.contents: write` 已配置，且没有拼写错误（如 `premissions`、`content` 少了 s）。

---

### 🔗 推导链：从零手写 Release Workflow 的完整思维过程

```
起点: 我需要一个自动发布 Release 的流水线，该从哪里开始？
  │
  ├── 第1步: 什么时候执行这个流水线？
  │   为什么？发布 Release 不是每次 Push 都要做。只有团队"决定发版"时才触发。
  │   → 思路：用 Tag 标记"这是正式版本"，Workflow 监听 Tag Push 事件
  │   → 实现：on.push.tags: ['v*']，Glob 模式只匹配 v 开头的标签
  │
  ├── 第2步: 这个流水线需要什么额外权限？
  │   为什么？创建 Release 是写操作，默认 GITHUB_TOKEN 只有读权限。
  │   → 实现：permissions.contents: write，显式声明需要写内容权限
  │
  ├── 第3步: 软件如何从源码变成可执行文件？
  │   为什么？用户不能直接运行 .py 源码，需要打包成独立可执行文件。
  │   → 实现：PyInstaller --onefile（复用 M04 知识），输出到 dist/
  │
  ├── 第4步: 如何以编程方式创建 GitHub Release？
  │   为什么？手动在网页上创建 Release 太繁琐，且容易遗漏文件。
  │   → 思路：使用社区 Action 封装 GitHub API 调用
  │   → 实现：uses: softprops/action-gh-release@v2，指定 files: dist/*
  │
  ├── 第5步: 如何防止这个创建步骤在不该执行时执行？
  │   为什么？防御性编程——万一触发器配置被修改，Release 步骤也不应在普通 Push 中触发。
  │   → 实现：if: startsWith(github.ref, 'refs/tags/')，双重保险
  │
  └── 结论: 完整的 Release Workflow
      触发器(Tag) → 拉代码 → 装环境 → 打包 → 发布Release
      一条龙自动化，开发者只需 git tag && git push。
```


## 六、Java 项目 SSH 自动部署

### 6.1 场景引入：从「打包」到「部署上线」

#### 🧠 直观理解

上一节我们学会了把 Python 包自动发布到 PyPI，那是一种「发布给别人用」的交付方式。这一节我们换一种更常见的交付方式——**把应用直接部署到自己的服务器上，让它跑起来**。想象你写完了一个 Spring Boot 项目，现在每次改完代码都要手动打包、手动上传、手动重启服务，重复又容易出错。GitHub Actions 可以帮你把这整套流程自动化：代码一推送，jar 包就自动飞到服务器上并重启运行。

#### 📖 详细解释

本节的示例是一个 **Java 项目，使用 Maven 进行构建管理**。整个 CI/CD 流水线的目标是：

1. 开发者推送代码到 GitHub 仓库的 `main` 分支
2. GitHub Actions 自动触发，检出代码
3. 配置 JDK 17 环境
4. 执行 `mvn package` 打包成 jar 文件
5. 通过 SSH 将 jar 包上传到远程服务器
6. 在服务器上杀掉旧进程，启动新进程，完成部署

```
┌──────────┐     git push      ┌───────────────┐      SSH       ┌──────────────┐
│  开发者   │─────────────────▶│ GitHub Actions │───────────────▶│  远程服务器   │
│ 本地编码  │                   │ maven.yml     │  upload jar +  │ 运行 jar 包  │
└──────────┘                   └───────────────┘  restart proc  └──────────────┘
```

> 💡 **核心洞见**：SSH 部署的本质是「把 GitHub Actions 的 runner 当作一个跳板机」，它通过 SSH 协议连接到你的服务器，完成文件传输和命令执行。这和 M04 中 runner 在 GitHub 提供的虚拟机上运行不同——这里的最终运行环境是你的**自有服务器**。

> 🔗 **关联知识**：本节使用的 SSH Deploy Action 是 M02 中「社区 Action」概念的又一次实战；密钥存 `secrets` 是 M04 中 `permissions` 概念的延伸——两者都在解决「如何安全地给 Action 授权」这个核心问题。

---

### 6.2 服务器环境准备（三步走）

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 在 Linux 服务器上生成 SSH 密钥对并配置密钥登录
> - [ ] 将私钥安全地下载到本地
> - [ ] 安装 OpenJDK 17 并验证安装

在写 Workflow 之前，服务器端必须先准备好三样东西：**SSH 密钥登录**、**部署目录**、**Java 运行环境**。下面以 Ubuntu 服务器为例，逐步演示。

---

#### Step 1: 配置 SSH 密钥登录

**为什么需要密钥登录？** GitHub Actions 的 runner 需要通过 SSH 连接到你的服务器。如果使用密码登录，你需要把密码写在某个地方——这是安全红线。密钥登录不需要传输密码，且私钥可以存储在 GitHub Secrets 中，安全性高得多。

**Step 1.1: 在服务器上生成密钥对**

```bash
# 登录你的远程服务器后，执行以下命令生成 SSH 密钥对
ssh-keygen -t rsa -b 4096
```

> 执行后一路按回车即可，不需要填写 passphrase（如果填了 passphrase，后续 SSH Deploy Action 连接时需要额外处理，会增加复杂度）。

命令执行后会输出类似以下信息：

```
Your identification has been saved in /root/.ssh/id_rsa
Your public key has been saved in /root/.ssh/id_rsa.pub
```

| 文件 | 说明 |
|---|---|
| `id_rsa` | **私钥**（Private Key）——必须保密，只有你自己和 GitHub Secrets 能持有 |
| `id_rsa.pub` | **公钥**（Public Key）——放在服务器上，可以公开 |

**Step 1.2: 将公钥写入 authorized_keys**

```bash
# 进入 .ssh 目录
cd /root/.ssh

# 将公钥追加写入 authorized_keys 文件
cat id_rsa.pub >> authorized_keys
```

> ⚠️ **注意事项**：这里的 `>>` 是**追加**（append），不是覆盖。如果使用单个 `>` 会把 authorized_keys 文件中原有的其他公钥全部清空，导致之前配置的密钥登录全部失效。如果 authorized_keys 文件不存在，`>>` 也会自动创建。

**Step 1.3: 下载私钥到本地**

生成后，需要把服务器上的私钥文件 `id_rsa` 下载到本地电脑。可以使用 SCP、SFTP 工具或云服务商控制台的「下载文件」功能。

```bash
# 在本地终端执行（示例：使用 scp 下载）
scp root@你的服务器IP:/root/.ssh/id_rsa ./id_rsa
```

私钥文件内容格式如下（粘贴到 GitHub Secrets 时必须以完整格式粘贴）：

```
-----BEGIN RSA PRIVATE KEY-----
（一大段 Base64 编码的密钥内容）
-----END RSA PRIVATE KEY-----
```

> ⚠️ **注意事项**：粘贴私钥到 GitHub Secrets 时，`-----BEGIN RSA PRIVATE KEY-----` 和 `-----END RSA PRIVATE KEY-----` 这两行**必须保留**，它们是密钥格式的边界标记，缺少任何一行都会导致 SSH 连接失败。

**Step 1.4: 验证密钥登录**

修改 SSH 客户端配置，使用私钥文件替代密码登录。重新连接服务器，如果无需输入密码即成功连接，说明密钥登录配置正确。

---

#### Step 2: 创建部署目录

```bash
# 确认当前在 root 目录
pwd
# 输出: /root

# 创建用于存放 jar 包的目录
mkdir /root/spring-boot

# 验证目录已创建
ls -la /root/spring-boot
```

> 这个目录就是后续 jar 包上传的目标路径。命名可以自定，但必须与 Workflow YAML 中的 `target` 参数保持一致。

---

#### Step 3: 安装 Java 运行环境（OpenJDK 17）

服务器需要 Java 运行时才能执行 jar 包。这里安装 OpenJDK 17，与项目编译时使用的 JDK 版本保持一致。

```bash
# Step 3.1: 更新 apt 包索引
sudo apt update

# Step 3.2: 安装 OpenJDK 17
sudo apt install openjdk-17-jdk -y

# Step 3.3: 验证安装
java -version
```

> `-y` 参数表示自动确认安装，不需要手动输入 `Y`。如果服务器在国内，建议先更换 apt 镜像源（如阿里云镜像）以加速下载。

预期输出类似：

```
openjdk version "17.0.x" 202x-xx-xx
OpenJDK Runtime Environment (build 17.0.x+x)
OpenJDK 64-Bit Server VM (build 17.0.x+x, mixed mode, sharing)
```

> ⚠️ **注意事项**：服务器上的 JDK 版本应**与本地开发和 GitHub Actions runner 中的 JDK 版本一致**。版本不一致可能导致编译出的 class 文件在服务器上无法运行（高版本编译的 class 无法在低版本 JVM 上执行）。

---

### 6.3 Workflow 文件编写：`maven.yml` 逐段解析

#### 🎯 目标

编写一个完整的 GitHub Actions Workflow 文件，实现：代码推送到 `main` 分支 → 自动 Maven 打包 → SSH 上传 jar 包到服务器 → 重启 Java 进程。

#### 🏗️ 前置准备

- GitHub 仓库中存在一个 Maven 管理的 Spring Boot 项目
- 服务器已完成 6.2 节的三步准备
- 私钥文件已下载到本地（后续要粘贴到 GitHub Secrets）

---

#### 💻 完整 YAML 文件

```yaml
# 文件名: .github/workflows/maven.yml
# 功能: Maven 打包 + SSH 自动部署到远程服务器

name: Maven Build and Deploy

# ========== 触发器 ==========
on:
  push:
    branches:
      - main

# ========== Job 定义 ==========
jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      # ------ Step 1: 检出代码 ------
      - name: Checkout code
        uses: actions/checkout@v4

      # ------ Step 2: 配置 Java 环境 ------
      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      # ------ Step 3: Maven 打包 ------
      - name: Build with Maven
        run: mvn clean package -DskipTests

      # ------ Step 4: SSH 部署到服务器 ------
      - name: Deploy to server via SSH
        uses: easingthemes/ssh-deploy@v5
        with:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
          SOURCE: 'target/*.jar'
          REMOTE_HOST: ${{ secrets.REMOTE_HOST }}
          REMOTE_USER: ${{ secrets.REMOTE_USER }}
          TARGET: '/root/spring-boot/github-action.jar'
          SCRIPT_AFTER: |
            pkill -f 'github-action.jar' || true
            nohup java -jar /root/spring-boot/github-action.jar > /root/spring-boot/app.log 2>&1 &
```

---

#### 📖 逐段解析

**触发器（on）**

```yaml
on:
  push:
    branches:
      - main
```

当有代码推送到 `main` 分支时触发。这里只监听 `main` 分支，开发分支（如 `dev`、`feature/*`）的推送不会触发部署——这是一个常见的最佳实践，确保只有合并到主分支的代码才会被部署。

**运行环境（runs-on）**

```yaml
runs-on: ubuntu-latest
```

Job 运行在 GitHub 提供的 Ubuntu 虚拟机上。这里的 `ubuntu-latest` 只是构建环境（runner），而不是最终的部署目标——真正运行 jar 包的是 `REMOTE_HOST` 指向的服务器。

**Step 1: 检出代码（actions/checkout）**

```yaml
- name: Checkout code
  uses: actions/checkout@v4
```

将仓库代码克隆到 runner 的工作目录中。这是几乎所有 Workflow 的第一步，没有这一步后续的 Maven 打包就找不到源代码。

**Step 2: 配置 JDK 17（actions/setup-java）**

```yaml
- name: Set up JDK 17
  uses: actions/setup-java@v4
  with:
    java-version: '17'
    distribution: 'temurin'
```

在 runner 上安装 JDK 17。`distribution: 'temurin'` 指定使用 Eclipse Temurin（原 AdoptOpenJDK）发行版——这是目前社区最广泛使用的 OpenJDK 构建版本。

> 💡 **核心洞见**：`actions/setup-java` 会自动处理 JDK 的下载、安装和 `JAVA_HOME` 环境变量的设置，你不需要手动执行任何安装命令。

**Step 3: Maven 打包**

```yaml
- name: Build with Maven
  run: mvn clean package -DskipTests
```

执行 Maven 构建命令。各参数说明：

| 参数 | 含义 |
|---|---|
| `clean` | 清除之前的构建产物（`target/` 目录），确保全新编译 |
| `package` | 执行编译、测试、打包全流程，最终生成 jar 包 |
| `-DskipTests` | 跳过单元测试的执行（但**仍编译测试代码**） |

> ⚠️ **注意事项**：`-DskipTests` 会跳过测试执行，适合快速部署演示。但在生产项目中，建议去掉此参数（或使用 `-Dmaven.test.skip=true` 完全跳过测试编译），确保部署前所有测试通过。

**Step 4: SSH 部署（easingthemes/ssh-deploy）**

这是整个 Workflow 的核心步骤。`easingthemes/ssh-deploy` 是一个社区 Action，它通过 SSH 协议连接到远程服务器，上传文件并执行命令。

---

### 6.4 密钥安全：GitHub Secrets 配置详解

> ⚠️ **安全红线：永远不要把私钥、密码、Token 等敏感信息直接写在项目文件中！**

这是本节最重要的一条原则。一旦私钥被写入代码仓库，任何能访问该仓库的人都能看到它——包括过去的 commit 历史。即使你后续删除了，Git 的历史记录中仍然保留。

#### 正确做法：使用 GitHub Secrets

**配置流程：**

1. 进入你的 GitHub 仓库页面
2. 点击顶部导航栏的 **Settings** 标签页
3. 在左侧菜单中找到 **Secrets and variables** → **Actions**
4. 点击绿色的 **New repository secret** 按钮
5. 填写 Name 和 Secret 值
6. 点击 **Add secret** 保存

| Secret Name | 值 | 说明 |
|---|---|---|
| `SSH_PRIVATE_KEY` | 私钥文件的完整内容（含 `BEGIN` 和 `END` 行） | 用于 SSH 连接认证 |
| `REMOTE_HOST` | 服务器 IP 地址，如 `123.45.67.89` | 部署目标服务器 |
| `REMOTE_USER` | 服务器用户名，如 `root` | SSH 登录用户 |

> ⚠️ **注意事项**：Secret 一旦保存就无法在网页上查看其内容（只能更新或删除）。这是 GitHub 的安全设计——即使仓库管理员也无法读取已存储的 Secret 值。如果需要修改，只能「更新」覆盖旧值。

#### 在 YAML 中引用 Secrets

```yaml
SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
REMOTE_HOST: ${{ secrets.REMOTE_HOST }}
REMOTE_USER: ${{ secrets.REMOTE_USER }}
```

使用 `${{ secrets.XXX }}` 语法引用。GitHub Actions 在运行时会自动将 Secret 值注入到对应的参数中，且在日志中 Secret 值会被自动打码（显示为 `***`），防止泄露。

#### SSH Deploy Action 参数详解

| 参数 | 含义 | 示例值 |
|---|---|---|
| `SSH_PRIVATE_KEY` | SSH 私钥，用于认证 | `${{ secrets.SSH_PRIVATE_KEY }}` |
| `SOURCE` | 要上传的本地文件路径（在 runner 上） | `target/*.jar` |
| `REMOTE_HOST` | 服务器 IP 地址 | `${{ secrets.REMOTE_HOST }}` |
| `REMOTE_USER` | SSH 登录用户名 | `${{ secrets.REMOTE_USER }}` |
| `TARGET` | 上传到服务器上的目标路径 | `/root/spring-boot/github-action.jar` |
| `SCRIPT_AFTER` | 上传完成后在服务器上执行的命令 | 见下方解析 |

**`SOURCE` 路径说明：**

```yaml
SOURCE: 'target/*.jar'
```

Maven 打包后，jar 文件生成在 runner 工作目录的 `target/` 子目录下。使用通配符 `*.jar` 匹配所有 jar 文件（通常 `mvn package` 会产生两个 jar：一个普通 jar 和一个 `-sources.jar`，通配符会把它们都上传；如果只想上传主 jar，可以使用更精确的文件名匹配）。

**`TARGET` 路径说明：**

```yaml
TARGET: '/root/spring-boot/github-action.jar'
```

一次指定完整的目标文件路径（包含文件名）。如果 `TARGET` 以 `/` 结尾则视为目录，上传的文件将保持原名；这里写完整路径可以让上传后的 jar 包统一命名为 `github-action.jar`，便于后续的进程管理命令引用。

**`SCRIPT_AFTER` 详解：**

```yaml
SCRIPT_AFTER: |
  pkill -f 'github-action.jar' || true
  nohup java -jar /root/spring-boot/github-action.jar > /root/spring-boot/app.log 2>&1 &
```

> 使用 YAML 的 `|`（literal block scalar）语法书写多行命令，保持脚本的可读性。

**第一行：杀掉旧进程**

```bash
pkill -f 'github-action.jar' || true
```

| 部分 | 含义 |
|---|---|
| `pkill` | 按进程名（或命令行参数）杀掉进程 |
| `-f` | 匹配完整的命令行（而不仅仅是进程名），这样可以精确匹配包含 `github-action.jar` 的 java 进程 |
| `\| true` | 如果没找到匹配的进程（首次部署时），`pkill` 会返回非零退出码导致整个脚本失败。`\| true` 确保即使没有旧进程可杀，脚本也继续执行 |

**第二行：后台启动新进程**

```bash
nohup java -jar /root/spring-boot/github-action.jar > /root/spring-boot/app.log 2>&1 &
```

| 部分 | 含义 |
|---|---|
| `nohup` | no hang up——即使 SSH 会话断开，进程也继续运行。部署完成后 runner 会断开 SSH 连接，没有 `nohup` 进程会被杀掉 |
| `java -jar xxx.jar` | 启动 Spring Boot jar 包 |
| `> /root/spring-boot/app.log` | 将标准输出重定向到日志文件，方便排查问题 |
| `2>&1` | 将标准错误也重定向到同一个日志文件 |
| `&` | 在后台运行，不阻塞当前终端 |

> ⚠️ **注意事项**：`pkill -f` 的匹配模式要足够精确。如果模式太宽泛（如 `pkill -f 'java'`），会误杀服务器上其他正在运行的 Java 进程。这里的 `'github-action.jar'` 是 jar 包的唯一命名，可以精准匹配。

---

### 6.5 执行与验证：从 Push 到上线

#### 触发部署

```bash
# 在本地项目目录中提交并推送代码
git add .
git commit -m "deploy: 配置 SSH 自动部署"
git push origin main
```

推送完成后，进入 GitHub 仓库的 **Actions** 标签页，可以看到 `Maven Build and Deploy` Workflow 已经开始运行。

#### 观察执行过程

点击正在运行的 Workflow，可以看到每个 Step 的实时日志：

1. **Checkout code** — 代码检出成功
2. **Set up JDK 17** — JDK 17 安装完成
3. **Build with Maven** — Maven 编译打包，输出 `BUILD SUCCESS`
4. **Deploy to server via SSH** — SSH 连接 → 上传 jar → 执行 `SCRIPT_AFTER`

> 如果任何一步失败，点击该步展开日志查看错误信息。常见问题包括：私钥格式不完整、服务器 IP 不可达、`pkill` 匹配模式错误等。

#### 服务器端验证

```bash
# 1. 查看 jar 包是否上传成功
ls -la /root/spring-boot/
# 预期输出: github-action.jar

# 2. 查看 Java 进程是否正在运行
ps aux | grep github-action.jar
# 预期输出: 一行包含 java -jar ... github-action.jar 的进程信息

# 3. 查看应用日志
tail -f /root/spring-boot/app.log
# 预期输出: Spring Boot 启动日志，包含 Tomcat started on port(s): 8080
```

#### 浏览器验证

在浏览器中访问 `http://服务器IP:8080/actions`，如果能看到应用返回的响应内容，说明部署完全成功。

```
┌──────────────────────────────────────────────┐
│           部署验证清单                         │
├──────────────────────────────────────────────┤
│ ☐ Actions 标签页显示 Workflow 运行成功          │
│ ☐ 服务器 /root/spring-boot/ 下存在 jar 文件     │
│ ☐ ps aux 能看到 java 进程                      │
│ ☐ 浏览器访问应用返回正常响应                     │
└──────────────────────────────────────────────┘
```

---

### 6.6 其他玩法简介：GitHub Actions 的更多可能性

录音中老师提到，GitHub Actions 的能力远不止打包部署。这里简要列举几个方向的玩法：

| 玩法 | 说明 | 触发器示例 |
|---|---|---|
| **定时任务** | 定期执行脚本，如每天早晨推送天气通知 | `schedule: cron: '0 8 * * *'` |
| **自动化测试** | PR 提交时自动运行测试套件 | `pull_request: branches: [main]` |
| **代码质量检查** | 集成 SonarQube、ESLint 等工具自动扫描 | `push` 事件触发 |
| **跨平台构建** | 使用 matrix 策略同时在 Windows/macOS/Linux 上构建 | `strategy: matrix: os: [ubuntu, windows, macos]` |
| **通知推送** | 构建/部署完成后发送企业微信、Slack、邮件通知 | 在 job 末尾添加通知 Step |

> 💡 **核心洞见**：GitHub Actions 本质上是一个「事件驱动的自动化执行器」。只要你能用脚本完成的事情，几乎都可以用 Action 来自动化。关键在于：**找到合适的触发事件 + 编写正确的执行步骤 + 安全地管理密钥**。

---



---

## 📋 课程小结

### 🗺️ 知识图谱

```
                         ┌─────────────────────────────┐
                         │     GitHub Actions           │
                         │   GitHub 内置自动化平台       │
                         └──────────────┬──────────────┘
                                        │
              ┌─────────────────────────┼─────────────────────────┐
              │                         │                         │
              ▼                         ▼                         ▼
    ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
    │   Marketplace    │     │   Workflow      │     │   Runner        │
    │   社区 Action 生态 │     │   YAML 配置文件   │     │   虚拟执行环境    │
    └────────┬────────┘     └────────┬────────┘     └────────┬────────┘
             │                       │                       │
             ▼                       ▼                       ▼
    ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
    │  uses: 引用语法   │     │  Event 触发器     │     │  ubuntu-latest  │
    │  author/act@ver  │     │  push/PR/tag/... │     │  windows-latest │
    └─────────────────┘     └────────┬────────┘     │  macos-latest   │
                                     │               └─────────────────┘
                      ┌──────────────┼──────────────┐
                      │              │              │
                      ▼              ▼              ▼
            ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
            │    Job A      │ │    Job B      │ │    Job C      │
            │  (并行/独立)   │ │  (并行/独立)   │ │  (并行/独立)   │
            └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
                   │                │                │
                   ▼
            ┌──────────────┐
            │ Step 1 → 2 → 3│  ← 顺序执行，共享环境
            │ checkout      │
            │ setup → build │
            │ deploy        │
            └──────────────┘
```

### 💡 一句话总结

> GitHub Actions 是一套 **事件驱动、社区可复用、YAML 配置** 的云端自动化流水线——掌握了 Workflow/Job/Step/Event 四层结构和 `uses` 引用语法，就能将任何重复性开发操作自动化。

### 📍 系列定位

> 📍 **系列定位**：本文是「GitHub 全系列」第 17 篇。
> - 上一篇：[Git 命令行 3] — Git 高级命令行操作与工作流
> - 下一篇：GitHub Action 进阶案例 — 多环境部署、矩阵构建、自定义 Action 开发

---

## 📝 课后练习

### 练习 1: 创建你的第一个 Action

**题目**：在自己的 GitHub 仓库中，使用 Python Application 模板创建一个 Workflow，添加第二个 Job 使用 pyinstaller 打包，提交代码后观察两个 Job 的并行执行。

**验收标准**：
- [ ] `.github/workflows/` 目录下存在一个 `.yml` 文件
- [ ] 包含至少两个 Job（如 build + pyinstaller）
- [ ] push 代码后 Actions 页面出现一次成功的 Workflow 运行记录
- [ ] 能从 Artifacts 中下载打包产物

### 练习 2: 手写一个 Release Workflow

**题目**：为一个 Python 项目从零手写一个 Release Workflow，当推送 `v` 开头的 tag 时自动打包并创建 GitHub Release。

**验收标准**：
- [ ] Workflow 在推送 `v*` tag 时触发
- [ ] 使用 `softprops/action-gh-release` 创建 Release
- [ ] Release 页面 Assets 中包含打包产物
- [ ] 不使用模板，所有 YAML 从零手写

### 练习 3: 配置 SSH 自动部署

**题目**：将任意 Java/Node.js/Python 项目配置为 push 到 main 分支时自动 SSH 部署到服务器。

**验收标准**：
- [ ] 服务器已配置 SSH 密钥登录
- [ ] 私钥存储于 GitHub Secrets 中（不在项目文件中）
- [ ] push 代码后自动上传文件到服务器并重启服务
- [ ] 浏览器访问服务器能确认部署成功

---

> 📅 生成日期: 2026-07-16 | 🎯 级别: M 级 | ⏱️ 录音时长: ~20.5 分钟 | 📏 文档规模: 2,500+ 行
> 🤖 由 transcript-to-doc v4.2 生成
