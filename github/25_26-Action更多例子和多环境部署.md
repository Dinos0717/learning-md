# 25-26 Action 更多例子和多环境部署

> 📅 生成日期: 2026-07-18 | 🎯 级别: M 级 | ⏱️ 录音时长: ~17 分钟 | 📏 文档规模: 4,000+ 行
> 🏷️ 标签: `GitHub Actions` `CI/CD` `PyInstaller` `多环境部署` `Secrets` `Cron` `DevOps`

---

## 📑 目录

- [一、课程概述与三个样例介绍](#一课程概述与三个样例介绍)
  - [1.1 GitHub Actions 是什么](#11-github-actions-是什么)
  - [1.2 本节课三个样例总览](#12-本节课三个样例总览)
  - [1.3 快速上手：使用他人的 Action 仓库](#13-快速上手使用他人的-action-仓库)
- [二、样例一：PyInstaller 编译打包 — 运行与配置解析](#二样例一pyinstaller-编译打包--运行与配置解析)
  - [2.1 从运行到理解](#21-从运行到理解先看效果再读配置)
  - [2.2 实操：手动触发 Workflow 并下载产物](#22-实操手动触发-workflow-并下载产物)
  - [2.3 YAML 配置文件逐项解析](#23-yaml-配置文件逐项解析)
  - [2.4 Workflow 完整执行流程](#24-workflow-完整执行流程端到端)
  - [2.5 排错实录](#25-排错实录)
- [三、样例一：多操作系统构建与乌邦图虚拟机实测](#三样例一多操作系统构建与乌邦图虚拟机实测)
  - [3.1 跨平台构建](#31-跨平台构建为什么需要多操作系统打包)
  - [3.2 核心洞察：只改 runs-on](#32-核心洞察只改-runs-on不改其他配置)
  - [3.3 GitHub 虚拟机运行环境](#33-github-提供的虚拟机运行环境)
  - [3.4 Ubuntu 虚拟机实测 Step-by-Step](#34-ubuntu-虚拟机实测-step-by-step)
  - [3.5 跨平台构建核心要点](#35-跨平台构建核心要点)
- [四、样例二：天气推送 — 定时触发与环境变量](#四样例二天气推送--定时触发与环境变量)
  - [4.1 场景需求分析](#41-场景需求分析)
  - [4.2 GitHub Secrets 配置](#42-前置准备github-secrets-配置)
  - [4.3 Cron 表达式与定时触发](#43-cron-表达式与定时触发)
  - [4.4 YAML 配置文件逐段解析](#44-github-actions-yaml-配置文件逐段解析)
  - [4.5 环境变量传递机制详解](#45-环境变量传递机制详解)
  - [4.6 执行验证：手动触发](#46-执行验证手动触发)
  - [4.7 排错指南](#47-排错指南)
- [五、样例三：京东签到 — Cookie 获取与配置](#五样例三京东签到--cookie-获取与配置)
  - [5.1 场景说明与目标](#51-场景说明与目标)
  - [5.2 Action 配置回顾与对比](#52-action-配置回顾与天气推送的对比)
  - [5.3 Cookie 的概念与作用](#53-cookie-的概念与作用)
  - [5.4 Step-by-Step：获取京东 Cookie](#54-step-by-step获取京东-cookie)
  - [5.5 GitHub Secret 配置](#55-github-secret-配置)
  - [5.6 执行时间与触发机制](#56-执行时间与触发机制)
  - [5.7 Cookie 安全三原则](#57-⚠️-cookie-安全三原则)
- [六、GitHub Actions Marketplace 市场](#六github-actions-marketplace-市场)
  - [6.1 Marketplace 是什么](#61-github-marketplace-是什么)
  - [6.2 回顾：PyInstaller Action 的来源](#62-回顾我们使用过的-pyinstaller-action)
  - [6.3 Marketplace 热门分类一览](#63-marketplace-热门分类一览)
  - [6.4 使用社区 Action 的四大优势](#64-使用社区-action-的四大优势)
  - [6.5 如何选择靠谱的 Action](#65-如何选择靠谱的-action)
- [七、多环境部署 — 环境配置与保护规则](#七多环境部署--环境配置与保护规则)
  - [7.1 为什么要多环境部署](#71-为什么要多环境部署)
  - [7.2 三种环境概览](#72-三种环境概览)
  - [7.3 Environments 配置入口](#73-github-environments-配置入口)
  - [7.4 QA 环境配置](#74-qa-环境--测试环境配置)
  - [7.5 Staging 环境配置](#75-staging-环境--沙箱预发布环境配置)
  - [7.6 Production 环境配置](#76-production-环境--生产环境配置)
  - [7.7 Protection Rules 综合对比](#77-protection-rules-综合对比)
  - [7.8 Secrets vs Variables](#78-environment-secrets-vs-environment-variables)
- [八、多环境部署 — 并行 Job 工作流与审批流演示](#八多环境部署--并行-job-工作流与审批流演示)
  - [8.1 实操概览](#81-实操概览)
  - [8.2 Workflow YAML 完整展示](#82-workflow-yaml-文件完整展示)
  - [8.3 environment 字段详解](#83-environment-字段详解)
  - [8.4 并行执行机制](#84-三个-job-的并行执行机制)
  - [8.5 实际执行演示](#85-实际执行演示)
  - [8.6 验证结果](#86-验证结果)
  - [8.7 三种环境保护规则对比](#87-三种环境保护规则的执行效果对比)
  - [8.8 常见坑与排错指南](#88-关键要点与排错指南)
- [九、多环境部署 — 环境专属密钥与变量实战](#九多环境部署--环境专属密钥与变量实战)
  - [9.1 实战场景与目标](#91-实战场景与目标)
  - [9.2 前置准备](#92-前置准备)
  - [9.3 Step-by-Step](#93-step-by-step在-workflow-中引用环境专属变量)
  - [9.4 验证结果](#94-验证结果)
  - [9.5 排错指南](#95-排错指南)
  - [9.6 Secrets vs Variables 对比总结](#96-secrets-vs-variables-对比总结)

---


## 一、课程概述与三个样例介绍

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 说出 GitHub Actions 的三种典型应用场景
> - [ ] 理解 GitHub Actions 解决的核心痛点——多平台编译无需自建环境
> - [ ] 掌握使用他人 Action 仓库的标准流程：Fork → Actions 页面 → 手动触发
> - [ ] 在 Actions 页面中找到执行记录并查看详细步骤

---

### 1.1 GitHub Actions 是什么

#### 🧠 直观理解

GitHub Actions 是 GitHub 内置的自动化引擎。你可以把它想象成「GitHub 帮你请了一个不要钱的机器人」，你告诉它什么时候干什么事——比如每天早上 8 点推送天气预报、帮你自动签到、或者把你写的 Python 代码一键编译成 Windows/Mac/Linux 三个平台的可执行程序——它就按时执行，不需要你有一台 24 小时开机的服务器。

#### 📖 详细解释

GitHub Actions 本质上是一套运行在 GitHub 服务器上的**事件驱动型自动化工作流**。它解决了一个长期困扰开发者的实际问题：

> **你的代码写好了，但要想让它在不同操作系统上运行，难道要在每台机器上都装一遍环境再编译吗？**

在没有 GitHub Actions 之前，如果你想将一个 Python 程序打包成 macOS、Ubuntu、Windows 上的可执行文件，你需要：

1. 找一台 Mac 电脑，装好 Python 环境，运行 PyInstaller 编译
2. 找一台 Ubuntu 机器，再装一遍 Python 环境，再编译一次
3. 找一台 Windows 机器，再装一遍 Python 环境，再编译一次

每一步都涉及环境搭建、依赖安装、交叉编译的配置问题，繁琐且容易出错。

有了 GitHub Actions，这些繁琐的操作被抽象为**在云端根据不同操作系统自动拉起运行环境、执行编译任务、产出结果**。你只需要在仓库中写好一个 YAML 配置文件，GitHub 就会在对应的 trigger 触发时自动执行。

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Actions 工作模型               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   触发器（Trigger）          执行器（Runner）            │
│   ────────────────          ────────────────            │
│   · 定时 cron               · windows-latest            │
│   · push 代码               · ubuntu-latest              │
│   · 手动 workflow_dispatch   · macos-latest              │
│   · Issue/PR 事件            └──────┬───────             │
│        │                           │                     │
│        └───────────┬───────────────┘                     │
│                    ▼                                     │
│           ┌────────────────┐                             │
│           │   workflow.yml  │                             │
│           │   定义：做什么    │                             │
│           │   在什么环境做   │                             │
│           │   做完了怎么办   │                             │
│           └────────────────┘                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### 🔀 对比辨析

| 维度 | 没有 GitHub Actions | 使用 GitHub Actions |
|---|---|---|
| 多平台编译 | 手动搭 3 套环境，逐台执行 | 一个 YAML 文件，GitHub 并行执行 |
| 定时任务 | 需要自有服务器 + cron | GitHub 云端 cron，免费额度内零成本 |
| 操作门槛 | 需要懂各 OS 的环境配置 | Fork 别人的 Action 仓库，点一下就能跑 |
| 执行过程 | 黑盒，出了问题难排查 | Actions 页面展示每一步的详细日志 |

> 💡 **核心洞见**：GitHub Actions 不是用来替代你写代码的——它是用来替代你**做重复性运维劳动**的。编译、测试、部署、定时推送、签到，这些属于「有明确规则、可以自动化」的重复性工作，正是 Actions 擅长解决的领域。

> ⚠️ **注意事项**：本节课介绍的 GitHub Actions 使用方式，属于「拿来主义」——通过 Fork 他人已经写好的 Action 仓库来使用。学会 Fork + 触发是使用 Actions 的第一步，后续章节会深入讲解如何自己编写 workflow 配置文件。

---

### 1.2 本节课三个样例总览

本节课的三个样例覆盖了 GitHub Actions 最常见的三类应用场景。每个样例都有独立的仓库（`github-action-sample`），老师已经提前写好了完整的 Action 脚本和配套代码。

```
              ┌──────────────────────────┐
              │  GitHub Actions 三大场景   │
              └────────────┬─────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
   ┌──────────┐    ┌──────────────┐    ┌──────────┐
   │ 样例一    │    │   样例二      │    │ 样例三    │
   │ 编译打包  │    │  天气推送     │    │ 京东签到  │
   └────┬─────┘    └──────┬───────┘    └────┬─────┘
        │                 │                 │
   Python→EXE       定时+API调用      Cookie+模拟请求
   多OS并⾏         每天自动推送      每天自动签到
```

| 序号 | 样例主题 | 核心场景 | 技术要点 | 一句话概述 |
|---|---|---|---|---|
| 样例一 | 编译打包 | 代码发布 | PyInstaller 多平台编译 | 用 Python 画了一个爱心，通过 Actions 一键编译成 Windows/Mac/Ubuntu 上的可执行程序 |
| 样例二 | 天气推送 | 定时任务 | 定时触发 + API 调用 | 每天定时获取天气信息并推送到指定渠道，无需自有服务器 |
| 样例三 | 京东签到 | 自动化薅羊毛 | Cookie 管理 + 定时 HTTP 请求 | 每天自动执行京东签到，获取京豆奖励，零人工介入 |

> 🔗 **关联知识**：样例一将在第二章深入演示——从 Fork 项目到手动触发、查看执行步骤、获取编译产物。样例二和样例三将在后续章节分别展开。本章只建立整体认知，不深入细节。

---

### 1.3 快速上手：使用他人的 Action 仓库

使用 GitHub Actions 不需要从零开始。老师已经在 `github-action-sample` 仓库中写好了一切，你需要的只是三步操作。

#### 🔄 执行流程

```
你（用户）                       GitHub
    │                              │
    │  ① Fork 仓库到自己的账号      │
    │─────────────────────────────▶│
    │                              │  复制仓库到你名下
    │                              │
    │  ② 进入 Actions 页面         │
    │─────────────────────────────▶│
    │                              │  展示所有可用 Workflow
    │                              │
    │  ③ 点击 Run workflow         │
    │─────────────────────────────▶│
    │                              │  拉起 Runner 执行任务
    │                              │  显示每一步的实时日志
    │                              │
    │  ④ 刷新页面查看结果          │
    │◀─────────────────────────────│
    │                              │
```

#### Step 1: Fork 项目

这是使用他人 Action 仓库的**标准第一步**。Fork 操作会将原作者的仓库完整复制到你自己的 GitHub 账号下，这样你就有权限修改配置、触发 Actions、查看执行结果。

> ⚠️ **注意事项**：大部分公开的 GitHub Actions 仓库都是通过 Fork 方式分发的。Fork 之后，Actions 的运行计入**你自己的免费额度**，与原作者无关。GitHub 为公开仓库提供无限免费的 Actions 分钟数，所以你不用担心费用问题。

在仓库页面右上角点击 **Fork** 按钮即可完成。

#### Step 2: 进入 Actions 页面

Fork 成功后，进入你自己的仓库页面（`github.com/你的用户名/仓库名`），点击顶部导航栏中的 **Actions** 标签。

Actions 页面左侧列出了本仓库中所有可用的 Workflow。以样例一为例，你会看到老师编写的两个 Action：

- **画爱心 - Windows 版本**：在 Windows 环境下编译打包
- 其他平台的编译版本

每个 Workflow 都像是一个独立的「脚本入口」，你可以分别触发、分别查看执行结果。

#### Step 3: 手动触发执行

以 Windows 版本为例：

1. 点击「画爱心 - Windows 版本」进入该 Workflow 详情页
2. 页面右侧会看到一个 **Run workflow** 按钮（这就是 `workflow_dispatch` 触发方式的 UI 入口）
3. 点击下拉箭头，选择分支（默认 `main`），然后点击绿色的 **Run workflow** 按钮
4. 刷新页面，你会看到一个新的 Workflow Run 出现在列表中，状态为黄色（执行中）或绿色（已完成）

> 💡 **核心洞见**：`workflow_dispatch` 是 GitHub Actions 提供的手动触发方式。老师在编写 Workflow 时开启了 `workflow_dispatch` 事件，所以你才能在 Actions 页面上看到 Run workflow 按钮。这让你不需要 push 任何代码，只需点击按钮就能触发执行——非常适合「先用别人的 Action 看看效果」这种学习场景。

#### ✅ 验证结果

点击任意一个 Workflow Run，可以看到**详细的执行步骤**（称为 Jobs 和 Steps）：

- 每一步都有展开/折叠的日志
- 绿色对勾表示该步执行成功
- 红色叉号表示该步执行失败（点击可查看报错详情）
- 编译产物（如 `.exe` 文件）通常以 **Artifacts** 的形式提供下载

这就是 GitHub Actions 的完整使用体验：你不需要懂每一步的内部原理，但你可以清楚地看到每一步做了什么、是否成功。后续章节会逐一拆解这些 Workflow 配置的原理。

---


## 二、样例一：PyInstaller 编译打包 — 运行与配置解析

### 2.1 从运行到理解：先看效果再读配置

#### 🧠 直观理解

GitHub Actions 就像一个"云端自动化工坊"——你给它一张配方（YAML 配置文件），它就会在远程虚拟机上自动帮你执行一系列任务。本模块要分析的这个 Workflow，能够将你的 Python 项目自动编译打包成 Windows 可执行文件（.exe），本地不需要安装任何编译工具链。

#### 📖 详细解释

在学习 YAML 配置之前，老师采用的是"反向学习"策略——先看这个 Workflow 已经跑完的样子，再逐行拆解配方中的每一条指令。这种"先看成品、再学配方"的节奏，让你在脑中先建立完整的感性认知（"它能跑、能产出可下载的 exe"），回头再读 YAML 时，每个字段的作用就有了评价基准。

> 💡 **核心洞见**：先跑通再理解，比从零啃配置要高效得多。绿灯亮起、Artifact 生成成功，你就知道这个配置整体是对的，后续学习每个字段只是在解释"为什么对"。

---

### 2.2 实操：手动触发 Workflow 并下载产物

#### 🎯 本节目标

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 在 GitHub 仓库中手动触发一个 Actions Workflow
> - [ ] 读懂 Workflow 执行状态指示灯（绿灯 / 黄灯 / 红灯）
> - [ ] 找到并下载 Workflow 生成的 Artifact 产物
> - [ ] 在本地运行编译出的可执行文件并验证功能

#### 🏗️ 前置准备

| 准备项 | 说明 |
|---|---|
| GitHub 账号 | 需要有一个已注册的 GitHub 账号 |
| 已 Fork 的项目仓库 | 将老师提供的示例项目 Fork 到自己的账号下 |
| 网络环境 | 能够正常访问 GitHub Actions 页面和 Artifacts 下载 |

#### 💻 Step-by-Step

**Step 1: 进入 Actions 页面**

在项目仓库顶部的导航栏中，点击 **Actions** 标签，进入当前仓库的 Workflow 列表页面。

```
仓库首页 → 顶部导航栏 → Actions 标签
```

页面左侧会列出该仓库中所有已定义的 Workflow，右侧显示最近的执行历史。

**Step 2: 选择并手动触发 Workflow**

在左侧 Workflow 列表中找到 Workflow，点击进入其详情页。页面右侧会出现一个 **"Run workflow"** 下拉按钮：

1. 点击 "Run workflow" 下拉
2. 选择目标分支（通常为 `main` 或 `master`）
3. 点击绿色的 **"Run workflow"** 按钮确认触发

```
┌──────────────────────────────┐
│     Actions 页面              │
│                               │
│  ┌── Workflows ────────────┐ │
│  │ ● PyInstaller Build     │ │
│  └─────────────────────────┘ │
│              │                │
│              ▼                │
│  ┌── Run workflow ─────────┐ │
│  │ Branch: main       [▾]  │ │
│  │ [Run workflow]  (绿色)  │ │
│  └─────────────────────────┘ │
└──────────────────────────────┘
```

**Step 3: 观察执行过程与状态指示灯**

触发后，页面会自动出现一个新的 Workflow Run。点击进入可以看到实时执行进度：

| 指示灯 | 状态 | 含义 |
|---|---|---|
| 🟡 黄色圆点 | `pending` / `in_progress` | 正在排队等待资源 / 正在执行中 |
| 🟢 绿色对勾 | `success` | 所有 Step 执行成功，Workflow 正常结束 |
| 🔴 红色叉号 | `failure` | 某个 Step 执行失败，Workflow 异常终止 |

> ⚠️ **注意事项**：老师特别强调"这里会亮一个绿灯"——绿色表示 Workflow **完全成功**，这是确认一切正常的核心信号。如果是红灯，必须展开运行日志逐步骤排查。

**Step 4: 找到并下载 Artifact**

Workflow 执行成功后，在 Run 详情页面的底部会出现 **Artifacts** 区域。这里保存了 Workflow 执行过程中通过 `upload-artifact` 步骤上传的所有构建产物。

```
┌──────────────────────────────────────────┐
│  Artifacts（默认保留 90 天）              │
│                                           │
│  ┌────────────────────────────────────┐  │
│  │ 📦 love-heart  (打包产物压缩包)      │  │
│  │    [Download] ← 点击下载            │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

> 📖 **Artifacts 概念**：Artifact 是 GitHub Actions 的"工作流产物"机制。Workflow 中的 Step 可以产出文件（如编译后的二进制、测试报告等），这些文件通过 `actions/upload-artifact` 步骤上传后，你可以在 Web 页面直接下载。Artifacts 默认保留 90 天，过期自动清理。

**Step 5: 下载后本地运行验证**

将下载的压缩包解压，双击 `love-heart.exe` 即可看到一个窗口化的 GUI 应用程序。因为打包时使用了 `noconsole: true` 参数，运行时不会弹出命令行黑框。

#### ✅ 验证结果

| 验证项 | 预期结果 | 未通过的排查方向 |
|---|---|---|
| Workflow Run 状态图标 | 绿色对勾（success） | 点击 Run 详情查看失败 Step 的日志 |
| Artifacts 区域 | 出现可下载的压缩包 | 检查 YAML 是否包含 `upload-artifact` 步骤 |
| 下载后解压双击运行 | 弹出 GUI 窗口 | 检查 `noconsole` 参数是否为 `true` |

#### 🐛 排错指南

**🐛 常见坑 1：Workflow 跑完但找不到 Artifacts**

- **🚨 现象**：Workflow 绿色成功，但 Run 详情页底部没有 Artifacts 区域
- **🔍 原因**：YAML 中缺少 `actions/upload-artifact` 步骤
- **✅ 解决**：在 `steps` 末尾添加：

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: love-heart
    path: dist/love-heart.exe
```

**🐛 常见坑 2：下载的 exe 双击闪退**

- **🚨 现象**：双击 exe 后窗口一闪而过
- **🔍 原因**：可能打包时未设置 `noconsole: true`，或程序内部有未捕获异常
- **✅ 解决**：确认 `with` 块中 `noconsole: true` 已设置；调试阶段临时将 `noconsole` 设为 `false`

---

### 2.3 YAML 配置文件逐项解析

#### 🔄 Workflow 结构层次总览

```
GitHub Actions Workflow 完整层次结构

┌───────────────────────────────────────────────────────┐
│  name: "PyInstaller Build"  ← Workflow 的显示名称     │
└───────────────────────────────────────────────────────┘
│
┌───────────────────────────────────────────────────────┐
│  on:                            ← 触发条件配置         │
│    workflow_dispatch:           ← 手动触发模式         │
│    # schedule:                  ← 也可加定时触发       │
│    # push:                      ← 也可加代码提交触发   │
└───────────────────────────────────────────────────────┘
│
┌───────────────────────────────────────────────────────┐
│  jobs:                          ← 任务组（核心）       │
│    ┌─────────────────────────────────────────────┐    │
│    │  build:                    ← job 的唯一 ID    │    │
│    │    runs-on: windows-latest ← 运行的操作系统   │    │
│    │    steps:                  ← 步骤列表         │    │
│    │    ┌─────────────────────────────────────┐   │    │
│    │    │  - uses: actions/checkout@v4        │   │    │
│    │    │    作用: 拉取仓库代码到虚拟机         │   │    │
│    │    └─────────────────────────────────────┘   │    │
│    │    ┌─────────────────────────────────────┐   │    │
│    │    │  - uses: JackMcKew/...@main         │   │    │
│    │    │    with:                             │   │    │
│    │    │      python_ver: "3.11"             │   │    │
│    │    │      spec: "love.py"                │   │    │
│    │    │      exe_name: "love-heart"         │   │    │
│    │    │      onefile: true                  │   │    │
│    │    │      noconsole: true                │   │    │
│    │    └─────────────────────────────────────┘   │    │
│    └─────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────┘
```

> 💡 **核心洞见**：GitHub Actions YAML 的层级关系是**严格的一对多树形结构**——一个仓库有多个 Workflow 文件，一个 Workflow 有多个 Job，一个 Job 有多个 Step，一个 Step 要么是 Shell 命令要么是引用的外部 Action。

---

#### 2.3.1 `name`：Workflow 的名称

```yaml
name: PyInstaller Build
```

| 维度 | 说明 |
|---|---|
| **位置** | YAML 文件最顶部 |
| **作用** | 定义此 Workflow 在 GitHub Actions 页面左侧列表中的**显示名称** |
| **是否必填** | 可选。不写时 GitHub 使用文件名作为默认名称 |
| **最佳实践** | 使用有意义的名称，让协作者一眼识别 Workflow 的用途 |

---

#### 2.3.2 `on`：触发条件

```yaml
on:
  workflow_dispatch:
```

`on` 定义了"在什么事件发生时自动运行这个 Workflow"。老师提到了三种触发方式：

#### 触发条件三种类型对比

| 触发类型 | YAML 键名 | 触发时机 | 谁来触发 | 典型场景 |
|---|---|---|---|---|
| **手动触发** | `workflow_dispatch` | 用户点击 "Run workflow" 按钮 | 人类操作者 | 临时打包、手动部署 |
| **定时触发** | `schedule` + cron | 按 cron 定时规则自动触发 | 系统定时器 | 夜间构建、定期巡检 |
| **代码事件触发** | `push` / `pull_request` | 代码推送或发起 PR | Git 操作 | CI/CD 自动化测试 |

##### 写法详解

**方式一：手动触发（本示例使用）**

```yaml
on:
  workflow_dispatch:
```

最简形式只需 `workflow_dispatch:`，即可在 Actions 页面看到 "Run workflow" 按钮。

**方式二：定时触发**

```yaml
on:
  schedule:
    - cron: "0 2 * * *"    # 每天 UTC 时间 02:00 执行
```

**方式三：代码事件触发**

```yaml
on:
  push:
    branches:
      - main            # 向 main 分支推送代码时触发
  pull_request:
    branches:
      - main            # 向 main 分支发起 PR 时触发
```

> 💡 **核心洞见**：三种触发方式**可以组合使用**。同一个 Workflow 可同时配置 `workflow_dispatch` + `schedule` + `push`。

##### 触发方式决策树

```
你的场景是什么？
    │
    ├── 每次代码提交后都需要验证？
    │   └── 是 → 使用 push / pull_request 触发器
    │
    ├── 需要在固定时间点自动执行？
    │   └── 是 → 使用 schedule + cron 触发器
    │
    ├── 需要人工判断、临时执行？
    │   └── 是 → 使用 workflow_dispatch 手动触发器
    │
    └── 以上多个需求同时存在？
        └── 是 → 三种触发器组合使用
```

---

#### 2.3.3 `jobs`：任务容器

```yaml
jobs:
  build:                         # job 的唯一标识符（ID）
    runs-on: windows-latest      # 运行环境
    steps:                       # 步骤列表
      # ...
```

| 要素 | 说明 |
|---|---|
| **Job ID** | `build`：内部引用的唯一标识 |
| **核心特性** | 一个 Workflow 可包含多个 Job，默认**并行执行**，互不干扰 |
| **依赖声明** | 通过 `needs: [job_id]` 实现 Job 之间的**串行依赖** |

> 📖 **为什么 Job 要并行**：不同 Job 各自运行在**独立的虚拟机**上。GitHub Actions 默认并行执行所有 Job 以缩短总耗时。

> ❓ **常见疑问**：本示例只有一个 Job，为什么不直接用 Step 就行了？
>
> Step 是 Job 内部的执行单元，不能脱离 Job 存在。`jobs` 是一个容器层级——即使只有一个 Job，也必须定义 `jobs`。本质上：**Workflow = 一组 Job，Job = 一组 Step**。

---

#### 2.3.4 `runs-on`：申请虚拟机

```yaml
runs-on: windows-latest
```

老师原话："申请了一个虚拟机来执行这个任务"——**GitHub 为你创建一台临时的云虚拟机**，跑完即销毁。

| 可用值 | 操作系统 | 典型用途 |
|---|---|---|
| `ubuntu-latest` | Ubuntu Linux | 通用 Linux 构建、Docker 镜像 |
| `windows-latest` | Windows Server | Windows .exe 打包、.NET 编译 |
| `macos-latest` | macOS | iOS/macOS 应用构建 |

> 💡 **核心洞见**：为什么本示例用 `windows-latest`？因为 PyInstaller 打包出的可执行文件是**平台相关的**——你在 Windows 虚拟机上编译，生成的就是 Windows 平台的 `.exe`。**目标用户的系统决定了 `runs-on` 选什么**。

---

#### 2.3.5 `steps`：步骤序列

```yaml
steps:
  - uses: actions/checkout@v4       # Step 1：拉取代码
  - uses: JackMcKew/pyinstaller-action-windows@main  # Step 2：打包
    with:
      python_ver: "3.11"
      spec: "love.py"
      # ...
```

`steps` 是一个**有序列表**——Step 按书写顺序**串行执行**。每个 Step 可以使用两种基本形式：

| Step 形式 | 语法 | 用途 |
|---|---|---|
| **运行 Shell 命令** | `run: pip install -r requirements.txt` | 执行任意命令行指令 |
| **引用外部 Action** | `uses: actions/checkout@v4` | 复用社区或官方预定义的 Action |

##### Step 执行顺序图

```
Step 1: actions/checkout@v4
    │  将仓库代码克隆到虚拟机的 $GITHUB_WORKSPACE 目录
    ▼
Step 2: PyInstaller Action
    │  读取 love.py → 安装 PyInstaller → 编译打包
    ▼
Step 3 (可选): actions/upload-artifact@v4
    │  将 dist/ 目录下的产物上传为可下载的 Artifact
    ▼
   ✅ 完成
```

---

#### 2.3.6 `uses`：引用社区 Action

```yaml
- uses: JackMcKew/pyinstaller-action-windows@main
```

**格式拆解**：`{owner}/{repository}@{ref}`

| 组成部分 | 本示例的值 | 含义 |
|---|---|---|
| `{owner}` | `JackMcKew` | GitHub 用户名或组织名 |
| `{repository}` | `pyinstaller-action-windows` | Action 的仓库名 |
| `@{ref}` | `@main` | 版本引用：分支名、tag 或 commit SHA |

> 💡 **核心洞见**：`uses` 是 GitHub Actions 生态最强大的能力——数万个社区 Action 构成了一个庞大的"技能市场"。你不需要重复造轮子，找到合适的 Action、引用它、传参即可。

> ⚠️ **注意事项**：`@main` 指向分支的最新提交，功能最新但可能不兼容。生产环境建议用 `@v1`、`@v1.2.0` 等固定版本。

---

#### 2.3.7 `with`：向 Action 传递参数

```yaml
with:
  python_ver: "3.11"
  spec: "love.py"
  exe_name: "love-heart"
  onefile: true
  noconsole: true
```

**`uses` 与 `with` 的关系**：

```
uses: JackMcKew/pyinstaller-action-windows@main
       │
       │  选择了"哪个厨师"来执行打包
       ▼
┌──────────────────────────────────────────────┐
│  pyinstaller-action-windows                  │
│  内部已经写好了打包的完整流程                   │
│  但它需要知道：                                │
│    - 用哪个 Python 版本？       ← python_ver  │
│    - 入口文件是哪个？            ← spec        │
│    - 输出文件叫什么名字？        ← exe_name    │
│    - 打成单文件还是文件夹？      ← onefile     │
│    - 要不要显示控制台窗口？      ← noconsole   │
└──────────────────────────────────────────────┘
       ▲
       │  "口味偏好"——告诉 Action 具体怎么执行
with: ...
```

> 💡 **直观类比**：`uses` 是你选定了餐厅和主厨，`with` 是你告诉主厨口味偏好（少油、加辣、不放香菜）。

##### `with` 参数逐项详解

| 参数 | 本示例的值 | 作用 | 对应 PyInstaller CLI |
|---|---|---|---|
| `python_ver` | `"3.11"` | Action 内部安装此版本的 Python | 环境准备阶段 |
| `spec` | `"love.py"` | 打包的**入口 Python 文件** | 命令行第一个位置参数 |
| `exe_name` | `"love-heart"` | 生成的 `.exe` 文件的**名称** | `--name love-heart` |
| `onefile` | `true` | 打包成单个 exe 文件（vs 文件夹） | `--onefile` |
| `noconsole` | `true` | 窗口化运行，不弹出命令行黑框 | `--noconsole` |

##### `onefile` 对比：单文件 vs 文件夹模式

| 维度 | `onefile: true`（单文件） | `onefile: false`（文件夹） |
|---|---|---|
| **产物形态** | 1 个 `.exe` 文件 | 1 个文件夹（含 .exe + .dll + 资源） |
| **启动速度** | 稍慢（运行前需自解压） | 较快（文件已就绪） |
| **分发便利性** | 极佳——一个文件直接发 | 需要压缩整个文件夹 |
| **适用场景** | 发布 Release、给最终用户 | 内部调试、开发阶段 |

##### `noconsole` 对比：窗口化 vs 控制台模式

| 维度 | `noconsole: true`（窗口化） | `noconsole: false`（控制台） |
|---|---|---|
| **运行时外观** | 只有 GUI 窗口 | GUI 窗口 + 命令行黑框 |
| **调试便利性** | 看不到 `print()` 输出 | 可在控制台查看日志 |
| **适用场景** | 正式发布版本 | 开发调试阶段 |

> ⚠️ **注意事项**：开发阶段建议临时改为 `noconsole: false`，方便看到 `print` 日志和 Python 异常堆栈。确认功能正常后，发布时再改回 `noconsole: true`。

---

### 2.4 Workflow 完整执行流程（端到端）

```
用户点击 "Run workflow"（手动触发 workflow_dispatch）
    │
    ▼
┌───────────────────────────────────────────────────────┐
│  GitHub 创建一台 windows-latest 虚拟机                 │
│  - 全新环境，无预装 Python                             │
│  - 设置 $GITHUB_WORKSPACE 工作目录                    │
└─────────────────────────┬─────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────┐
│  Step 1: actions/checkout@v4                          │
│  将仓库完整代码克隆到虚拟机的 $GITHUB_WORKSPACE         │
└─────────────────────────┬─────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────┐
│  Step 2: pyinstaller-action-windows                   │
│  内部子步骤:                                           │
│    2a. 安装 Python 3.11                                │
│    2b. pip install pyinstaller                         │
│    2c. pyinstaller --onefile --noconsole --name        │
│        love-heart love.py                              │
│    2d. 将产物移至输出目录                               │
└─────────────────────────┬─────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────┐
│  Step 3: actions/upload-artifact@v4（如配置）          │
│  将 dist/love-heart.exe 压缩上传为 Artifact             │
└─────────────────────────┬─────────────────────────────┘
                          │
                          ▼
                     🟢 绿灯
               Workflow 执行成功，虚拟机自动销毁
```

> ⚠️ **注意事项**：Step 3 的 `upload-artifact` 并非自动存在——必须在 YAML 中显式声明。如果省略此步骤，编译出的 `.exe` 随虚拟机一起销毁，**无法下载**。

---

### 2.5 排错实录

#### 🐛 排错实录 1：`spec` 路径指定错误

**❌ 错误写法**
```yaml
with:
  spec: "src/love.py"
```

**🚨 报错信息**
```
FileNotFoundError: No such file or directory: 'src/love.py'
```

**🔍 原因分析**

Checkout 将仓库代码克隆到仓库根目录。`spec` 参数指定的路径是**相对于仓库根目录**的。如果 `love.py` 在根目录而 `spec` 写成 `src/love.py`，Action 找不到文件。

**✅ 正确写法**
```yaml
with:
  spec: "love.py"     # 确认 love.py 确实在仓库根目录下
```

---

#### 🐛 排错实录 2：依赖缺失导致打包后运行时崩溃

**❌ 错误现象**

Workflow 绿灯，下载的 exe 双击后闪退。

**🚨 报错信息**（命令行运行时）
```
ModuleNotFoundError: No module named 'requests'
```

**🔍 原因分析**

PyInstaller 通过静态分析 `import` 语句来自动收集依赖。但动态导入（`__import__()`、`importlib`）会导致依赖遗漏。

**✅ 解决方法**

1. 确保项目根目录有 `requirements.txt` 并列出所有依赖
2. 在 `with` 中显式指定依赖文件路径：
```yaml
with:
  requirements: "requirements.txt"
```

**📝 经验总结**

维护一个精确的 `requirements.txt` 是 CI/CD 打包的基础。每次安装新依赖后，及时 `pip freeze > requirements.txt`。

---

### 📝 本模块小结

#### 🗺️ 知识图谱

```
                    ┌─────────────────────────────────┐
                    │     GitHub Actions Workflow      │
                    │        YAML 配置文件             │
                    └───────────────┬─────────────────┘
                                    │
          ┌─────────────┬───────────┼───────────┬─────────────┐
          ▼             ▼           ▼           ▼             ▼
    ┌──────────┐  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
    │  name    │  │   on     │ │  jobs    │ │  steps   │ │  uses    │
    │ 工作流名  │  │ 触发条件  │ │ 任务容器  │ │ 步骤序列  │ │ 复用Action│
    └──────────┘  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
                       │            │            │            │
                  ┌────┴────┐  ┌────┴────┐       │       ┌────┴────┐
                  ▼    ▼    ▼  ▼         ▼       │       ▼         ▼
             手动 定时 代码  runs-on  job-ID     │     with      Artifact
             触发 触发 触发  (虚拟机) (依赖)      │    (传参)     (产物)
                                                 │
                                           ┌─────┴──────┐
                                           ▼            ▼
                                      shell命令    引用Action
```

#### 💡 一句话总结

> GitHub Actions YAML 是一个分层自动化配方：`name` 命名、`on` 定义触发时机、`jobs` 组织任务、`runs-on` 申请虚拟机、`steps` 顺序执行操作，而 `uses` + `with` 让你通过复用社区 Action 并传参，用几行 YAML 配置就完成了 Python 项目的编译打包——无需手写编译脚本，无需管理构建环境。

---

## 三、样例一：多操作系统构建与乌邦图虚拟机实测

### 3.1 跨平台构建：为什么需要多操作系统打包

#### 🎯 目标

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 理解 GitHub Actions 跨平台构建的核心原理：只改 `runs-on`，配置复用
> - [ ] 区分 `windows-latest`、`ubuntu-latest`、`macos-latest` 三种运行环境
> - [ ] 独立完成 Ubuntu 虚拟机上的构建产物实测验证
> - [ ] 理解 Linux 可执行文件需要额外赋予执行权限的原因

#### 🧠 直观理解

假设你写好了一个 Python GUI 程序，用 PyInstaller 在 Windows 上打出了 `.exe`，功能完美。但你的用户有相当一部分用的是 macOS 和 Ubuntu——Windows 的 `.exe` 拿给他们，根本打不开。

传统的做法是：找三台不同系统的电脑，或者在本地装三个虚拟机，逐一登录、拉代码、装依赖、跑打包命令。流程繁琐不说，三次打包之间你还可能不小心改了代码，导致三个平台的产物行为不一致。

GitHub Actions 提供的解法非常优雅：**你只需写一份打包脚本，告诉 GitHub"请分别在 Windows、Ubuntu、macOS 的虚拟机上帮我执行这份脚本"。GitHub 会自动并行分配三台虚拟机，各自产出一个对应平台的可执行文件。**

而这一切的核心技巧，浓缩成一句话就是：**三份配置文件几乎一模一样，只有 `runs-on` 这一行不同。**

### 3.2 核心洞察：只改 runs-on，不改其他配置

#### 🔗 推导链：从单平台到多平台

```
起点: Windows 版 YAML 已配置完毕（PyInstaller 打包 + artifact 上传）
  │
  ├── 第1步: 完整复制 Windows 的 YAML 配置
  │   为什么？三个平台的打包逻辑完全相同——同一个 Python 脚本、同一条 PyInstaller 命令、
  │   Python 依赖也都是跨平台的。没有理由重写。
  │
  ├── 第2步: 只修改 runs-on 字段
  │   为什么？runs-on 是 GitHub Actions 的"平台选择器"。它告诉 GitHub 分配哪种操作系统
  │   的虚拟机来执行后续所有 steps。打包工具 PyInstaller 本身是跨平台的，只要 Python 和
  │   PyInstaller 安装成功，同一条命令在三个系统上都能正常工作。
  │
  ├── 第3步: 适当修改工作流名称和 artifact 名称（方便区分产物）
  │   为什么？不是功能必须，纯粹是为了管理方便——你不会想在 Actions 列表里看到三个同名的
  │   workflow，也不会想下载三个同名 artifact 分不清哪个是哪个。
  │
  └── 结论: 配置复用率接近 100%。runs-on 是唯一的"操作系统开关"
```

> ⚠️ **注意事项**：这个方案的成立有一个关键前提——PyInstaller **不支持交叉编译**。也就是说，在 Windows 虚拟机上只能打出 Windows `.exe`，在 Ubuntu 虚拟机上只能打出 Linux 二进制，在 macOS 虚拟机上只能打出 macOS 可执行文件。正因为有这个限制，我们才**必须**用 GitHub Actions 分别分配三种虚拟机来构建。如果 PyInstaller 支持交叉编译（比如在 Windows 上直接打出 Linux 二进制），那就不需要三台虚拟机了。

> 💡 **核心洞见**：跨平台 CI 的真正威力不在于配置有多复杂，而在于**配置的可复用性**。如果你的构建步骤不依赖某个操作系统的专有功能（比如没有用 PowerShell 特有的 cmdlet），那同一份 steps 定义就能通吃三个平台。`runs-on` 是唯一需要改的东西——它是"系统开关"，不是"配置开关"。

#### 💻 三个 YAML 文件逐行对比

以下是同一个项目（打包 `love.py` 为 `love heart` 可执行文件）在三个操作系统上的完整 YAML 配置。请逐行对比——**除了 `runs-on`，steps 部分一个字都没变。**

**Windows 版 (`build-windows.yml`)**

```yaml
# 文件名: build-windows.yml
# 功能: 在 Windows 虚拟机上用 PyInstaller 打包 love.py

name: Build Windows Executable

on: [push]

jobs:
  build:
    runs-on: windows-latest          # ← 指定 Windows 虚拟机

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          pip install pyinstaller

      - name: Build executable
        run: |
          pyinstaller --onefile --windowed --name "love heart" love.py

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: love-heart-windows
          path: dist/
```

**Ubuntu 版 (`build-ubuntu.yml`)**

```yaml
# 文件名: build-ubuntu.yml
# 功能: 在 Ubuntu 虚拟机上用 PyInstaller 打包 love.py

name: Build Ubuntu Executable

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest           # ← 唯一实质性变化：改成 Ubuntu

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          pip install pyinstaller

      - name: Build executable
        run: |
          pyinstaller --onefile --windowed --name "love heart" love.py

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: love-heart-ubuntu
          path: dist/
```

**macOS 版 (`build-macos.yml`)**

```yaml
# 文件名: build-macos.yml
# 功能: 在 macOS 虚拟机上用 PyInstaller 打包 love.py

name: Build macOS Executable

on: [push]

jobs:
  build:
    runs-on: macos-latest            # ← 唯一实质性变化：改成 macOS

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          pip install pyinstaller

      - name: Build executable
        run: |
          pyinstaller --onefile --windowed --name "love heart" love.py

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: love-heart-macos
          path: dist/
```

#### 📊 三平台 YAML 差异一览

| 配置项 | Windows | Ubuntu | macOS |
|---|---|---|---|
| `runs-on` | `windows-latest` | `ubuntu-latest` | `macos-latest` |
| `name`（工作流显示名） | Build Windows Executable | Build Ubuntu Executable | Build macOS Executable |
| artifact `name` | `love-heart-windows` | `love-heart-ubuntu` | `love-heart-macos` |
| **所有 steps** | 完全一致 | 完全一致 | 完全一致 |
| PyInstaller 命令 | `--onefile --windowed --name "love heart" love.py` | **完全相同的命令** | **完全相同的命令** |
| 产物格式 | `.exe` | ELF 二进制（无扩展名） | Mach-O 可执行文件 |

> 💡 **核心洞见**：工作流名称和 artifact 名称的修改，纯粹是为了"管理上的可辨识性"——让你在 Actions 面板里一眼看出哪个是哪个。**构建逻辑（steps）一个字都不需要改。** 这就是 GitHub Actions 跨平台设计最优雅的地方：操作系统是"可插拔的运行时环境"，而构建脚本与平台解耦。

### 3.3 GitHub 提供的虚拟机运行环境

#### 📖 三种 Runner 镜像

GitHub Actions 官方维护了三套虚拟机镜像，`*-latest` 标签会随 GitHub 的升级策略滚动更新。以下是当前版本的概况：

| `runs-on` 值 | 底层操作系统 | 预装的关键工具链 | 典型匹配场景 |
|---|---|---|---|
| `windows-latest` | Windows Server 2022 | Visual Studio Build Tools, MSYS2, PowerShell 7 | .NET/WPF 项目、Windows 专属 GUI、MSVC 编译 |
| `ubuntu-latest` | Ubuntu 22.04 / 24.04 | GCC, Python 3.x, Docker Engine, Bash | 绝大多数开源后端项目、Web 服务、Docker 镜像构建 |
| `macos-latest` | macOS 14 (Sonoma) | Xcode, Homebrew, Apple CLT, Bash | iOS/macOS 原生应用、Swift/ObjC 编译、跨平台兼容性验证 |

> ⚠️ **注意事项**：`-latest` 标签指向的具体版本会随时间变化。如果你的项目对系统库版本敏感（比如依赖特定版本的 glibc 或 Xcode），建议锁定版本号——例如 `ubuntu-22.04`、`macos-14`。否则可能出现"昨天还能跑的构建，今天突然崩了"的情况，排查之后才发现是 GitHub 悄悄把 `-latest` 升级了。

### 3.4 Ubuntu 虚拟机实测 Step-by-Step

#### 🏗️ 前置准备

在进行 Ubuntu 虚拟机实测之前，请确认以下环境已就绪：

| 前置条件 | 说明 |
|---|---|
| Hyper-V 已启用 | Windows 10/11 专业版/企业版自带，在"控制面板 → 启用或关闭 Windows 功能"中勾选 Hyper-V |
| Ubuntu 22.04 虚拟机 | 可通过 Hyper-V 快速创建功能直接安装，或从 ubuntu.com 下载 ISO 手动安装 |
| 虚拟机网络连通 | 需能访问 GitHub.com，以下载 Actions workflow 产出的 artifact |
| GitHub Actions 构建已完成 | `build-ubuntu.yml` workflow 绿色通过，artifact 可供下载 |

> ⚠️ **注意事项**：Hyper-V 是 Windows 原生虚拟化平台，性能优于 VirtualBox/VMware。但需要注意：Hyper-V 仅在 Windows 专业版、企业版和教育版中可用，**Windows 家庭版不支持**。如果你用的是家庭版，需要用 VirtualBox 或 VMware Workstation Player 替代。

#### 💻 Step-by-Step

**Step 1: 确认虚拟机系统版本**

启动 Hyper-V 中的 Ubuntu 虚拟机，打开终端，确认系统版本。

```bash
# 在 Ubuntu 虚拟机终端中执行
lsb_release -a
# 预期输出:
# Distributor ID: Ubuntu
# Description:    Ubuntu 22.04.x LTS
# Release:        22.04
# Codename:       jammy
```

> 系统版本确认为 Ubuntu 22.04 LTS，与当时 GitHub Actions 中 `ubuntu-latest` 所指的版本一致。大版本号相同意味着 glibc、libstdc++ 等核心系统库的 ABI 兼容，GitHub 上构建出来的二进制可以直接在这个本地虚拟机上运行。

**Step 2: 获取构建产物**

从 GitHub 仓库的 Actions 标签页，找到 `Build Ubuntu Executable` 这个 workflow 的最新一次成功运行，下载名为 `love-heart-ubuntu` 的 artifact。

下载的 zip 包解压后，将可执行文件 `love heart` 放到 Ubuntu 虚拟机的桌面上。

```bash
# 确认文件已就位
ls -lh ~/Desktop/"love heart"
# 预期输出示例:
# -rw-r--r-- 1 user user 15M Jul 18 10:30 love heart
```

> PyInstaller 的 `--onefile` 模式下，所有 Python 解释器、依赖库、资源文件全部被打包进这一个文件。所以桌面上只有 `love heart` 这一个文件，不需要额外的 `_internal` 文件夹。

**Step 3: 赋予执行权限（Linux 特有步骤）**

这是 Linux 与 Windows 在可执行文件处理上最关键的差异。Windows 靠文件扩展名（`.exe`）识别可执行文件；Linux 完全不看扩展名，只看文件系统元数据中的**执行权限位（execute bit，简称 x bit）**。

GitHub 的 artifact 下载后是 zip 格式，而 zip 格式**不保留 Unix 权限位**。解压后文件默认只有读写权限（`rw-`），缺少执行权限（`x`）。

```bash
# 方式一：命令行授权（推荐）
chmod +x ~/Desktop/"love heart"

# 方式二：图形界面操作
# 右键文件 → "属性" → "权限"标签 → 勾选"允许作为程序执行文件"
```

```bash
# 验证权限已生效
ls -l ~/Desktop/"love heart"
# 关注第一列权限字符串中是否出现 x:
# -rwxr-xr-x 1 user user 15M Jul 18 10:30 love heart
#   ^  ^  ^
#   │  │  └── 其他用户: 读 + 执行
#   │  └───── 组用户:   读 + 执行
#   └──────── 所有者:   读 + 写 + 执行
```

> ⚠️ **注意事项**：即使 PyInstaller 正确打包出了 Linux ELF 二进制，如果缺少 `x` 权限，双击文件不会有任何反应，终端执行也会报 `Permission denied`。**从网络下载到 Linux 的任何可执行文件，第一件事一定是 `chmod +x`。** 这是 Linux 使用者的肌肉记忆，也是从 Windows 转到 Linux 最容易踩的坑。

**Step 4: 运行验证**

双击桌面上已赋予权限的 `love heart` 文件，或在终端中执行：

```bash
# 终端运行方式
~/Desktop/"love heart"

# 如果一切正常，GUI 窗口会正常弹出
```

> 程序启动后，你看到的 GUI 窗口在功能、布局、交互上与 Windows 版本完全一致。这说明 PyInstaller 成功地将 Python 脚本及其依赖的 GUI 框架（如 tkinter、PyQt 等）打包成了 Linux 原生可执行文件。

#### 🔄 完整执行流程

```
GitHub Actions 云端（ubuntu-latest 虚拟机）
    │
    ├── actions/checkout@v4          ── 拉取仓库源码（love.py）
    ├── actions/setup-python@v5      ── 配置 Python 3.x 环境
    ├── pip install pyinstaller      ── 安装打包工具
    ├── pyinstaller --onefile ...    ── 打包为单文件 Linux 二进制
    ├── actions/upload-artifact@v4    ── 上传产物到 GitHub
    │
    ▼
开发者本地操作（Windows 宿主机）
    │
    ├── 浏览器打开 GitHub Actions 页面
    ├── 下载 love-heart-ubuntu artifact（zip）
    ├── 解压得到 "love heart" 文件
    └── 将文件传入 Hyper-V Ubuntu 22.04 虚拟机
    │
    ▼
本地 Ubuntu 22.04 虚拟机内
    │
    ├── ls -l "love heart"           ── 发现缺少 x 权限（rw-r--r--）
    ├── chmod +x "love heart"        ── 赋予执行权限（rwxr-xr-x）
    ├── 双击 / 终端执行               ── 运行程序
    └── ✅ GUI 窗口正常弹出，功能完整
```

#### ✅ 验证结果

| 验证项 | 预期表现 | 实际结果 |
|---|---|---|
| 文件存在性 | 桌面出现 `love heart` 文件 | 下载解压后确认存在 |
| 执行权限 | `ls -l` 显示 `x` 权限位 | 初始无 `x`，`chmod +x` 后正常 |
| 程序启动 | 双击后弹出 GUI 窗口 | 正常弹出，响应迅速 |
| 功能完整性 | 与 Windows 版功能一致 | Python 跨平台特性保证了这一点 |
| 文件大小 | 与 Windows 版相近（都含 Python 运行时） | 差异在 ~1MB 以内 |

#### 🐛 排错指南

##### 🐛 排错实录 1：双击文件无反应

**❌ 错误现象**

在 Ubuntu 文件管理器（Nautilus）中双击 "love heart" 文件，鼠标转圈后无任何窗口弹出，也没有任何报错提示。

**🚨 报错信息（终端运行可见）**

```
bash: ./love heart: Permission denied
```

**🔍 原因分析**

GitHub artifact 以 zip 格式打包下载。zip 格式诞生于 DOS 时代，其规范不包含 Unix 文件权限位。解压后所有文件的权限默认为 `rw-r--r--`（即 644），没有执行权限位。Linux 内核在 `execve()` 系统调用时会先检查文件的 `x` 位——没有则直接返回 `EACCES`（Permission denied），根本不会尝试加载文件内容。

**✅ 解决方法**

```bash
chmod +x ~/Desktop/"love heart"
```

**📝 经验总结**

任何从网络下载到 Linux 的可执行文件或脚本（`.sh`、`.AppImage`、`.run`），第一件事就是 `chmod +x`。这一点与 Windows 的用户习惯完全不同——Windows 用户看到 `.exe` 就知道能双击，Linux 用户需要先确认权限位。

##### 🐛 排错实录 2：文件名含空格导致命令报错

**❌ 错误现象**

```bash
chmod +x ~/Desktop/love heart
# 报错: chmod: cannot access 'love': No such file or directory
#       chmod: cannot access 'heart': No such file or directory
```

**🔍 原因分析**

shell 以空格为参数分隔符。`love heart` 中间的空格被解析为两个独立参数 `love` 和 `heart`。必须用引号包裹或使用转义。

**✅ 正确写法**

```bash
chmod +x ~/Desktop/"love heart"
# 或
chmod +x ~/Desktop/love\ heart
```

**📝 经验总结**

这是 Linux 命令行的基本功——文件名含空格必须加引号或反斜杠转义。实际上，**建议从一开始就不要在文件名中使用空格**，用下划线或连字符替代（如 `love-heart`），能避免大量不必要的麻烦。

### 3.5 跨平台构建核心要点

#### 📊 三平台打包体验对比

| 维度 | Windows | Ubuntu | macOS |
|---|---|---|---|
| `runs-on` 值 | `windows-latest` | `ubuntu-latest` | `macos-latest` |
| 构建产物格式 | `.exe`（PE 格式） | ELF 二进制（无扩展名） | Mach-O / `.app` bundle |
| 执行方式 | 直接双击 `.exe` | 先 `chmod +x`，再双击 | 双击 `.app` 或二进制 |
| 额外步骤 | 无 | **必须手动赋执行权限** | 可能需要解除 Gatekeeper 隔离 |
| 构建配置差异 | 基线 | 仅 `runs-on` 不同 | 仅 `runs-on` 不同 |
| 配置复用率 | — | ~100%（除 runs-on 外完全一致） | ~100%（除 runs-on 外完全一致） |

> 💡 **核心洞见**：GitHub Actions 的跨平台价值不在于它能同时跑三个系统——而在于**你不需要为三个系统写三套构建逻辑**。`runs-on` 就是你的平台选择器，改这一个字段，GitHub 自动帮你分配对应的虚拟机、预装对应的工具链。一套 steps，三份产物——这就是 CI 跨平台的最佳实践。

> 🔗 **延伸阅读**：本文演示的是三份独立 YAML 的实现方式。GitHub Actions 还支持 Matrix Strategy（矩阵策略），可以将三个平台的构建合并到一份 YAML 中，避免配置重复。在后续关于 workflow 优化的章节中将详细展开。

## 四、样例二：天气推送 — 定时触发与环境变量

### 4.1 场景需求分析

#### 🧠 直观理解

本次实操的目标是：**不购买云服务器、不花一分钱，每天早晨 7 点自动收到一条微信天气推送消息**。整个方案依赖 GitHub Actions 提供的免费 CI/CD 计算资源来完成定时任务调度和脚本执行。

#### 📖 详细解释

传统上，要实现"每天定时执行一个脚本"，需要一台 24 小时运行的服务器（VPS、云主机等），这意味着需要付费、需要维护操作系统、需要处理进程守护。GitHub Actions 提供了一个巧妙的替代方案：

- **GitHub Actions 的免费额度**：公开仓库的 Actions 完全免费，私有仓库每月有 2000 分钟免费额度，对于每天执行一次、每次几秒钟的天气推送来说绰绰有余。
- **定时触发能力**：Actions 支持 `schedule` 事件，使用标准 cron 表达式定义触发时间。
- **敏感数据管理**：通过 GitHub Secrets 安全存储 API 密钥等敏感信息，不需要将这些值硬编码在代码中或暴露在仓库里。

```
┌──────────────────────────────────────────────────────────┐
│  整体架构                                                  │
│                                                            │
│  GitHub Secrets              GitHub Actions               │
│  ┌────────────┐   注入       ┌──────────────────┐         │
│  │ APP_ID     │─────────────▶│  Ubuntu 虚拟机     │         │
│  │ APP_SECRET │              │                    │         │
│  │ OPEN_ID    │              │  1. 检出代码        │         │
│  │ TEMPLATE_ID│              │  2. 配置 Python 3.12│         │
│  └────────────┘              │  3. pip install 依赖 │         │
│                              │  4. 执行天气脚本     │────▶ 微信推送
│                              └──────────────────┘         │
│                                     ▲                      │
│                              Cron 定时 + 手动触发            │
└──────────────────────────────────────────────────────────┘
```

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 在 GitHub 仓库中配置 Secrets 存储敏感信息
> - [ ] 编写 cron 表达式实现每日定时触发，并正确处理 UTC 时区转换
> - [ ] 编写完整的 GitHub Actions YAML 文件配置 Python 运行环境
> - [ ] 理解环境变量从 Secrets → YAML → Python 代码的完整传递链路

---

### 4.2 前置准备：GitHub Secrets 配置

#### 🎯 目标

在仓库的安全存储区中配置四个环境变量，用于微信测试号 API 的身份认证和消息推送。这些值从上一期视频中申请微信测试号时获取。

#### 💻 Step-by-Step

**Step 1：进入 Secrets 配置页面**

在仓库主页面点击顶部导航栏的 **Settings** 选项卡，进入仓库设置页面。在左侧导航栏中找到 **Secrets and variables** 分组，点击其下方的 **Actions**。此时看到的是当前仓库的 Actions 密钥管理页面。

> ⚠️ **注意事项**：GitHub 的 Secrets 配置路径由三层导航组成，路径为 **Settings（仓库设置）→ Secrets and variables（密钥与变量）→ Actions（Actions 专用）**。不要混淆到组织级别的 Secrets 或其他分组。

**Step 2：创建 Secrets**

点击绿色的 **New repository secret** 按钮，依次创建以下四个 Secrets：

| Secret Name | 值来源 | 用途 |
|---|---|---|
| `APP_ID` | 微信测试号 appID | 标识微信应用身份 |
| `APP_SECRET` | 微信测试号 appsecret | 用于换取 access_token 的密钥 |
| `OPEN_ID` | 关注测试号用户的 openID | 指定消息接收者 |
| `TEMPLATE_ID` | 测试号中创建的消息模板 ID | 指定推送消息的格式模板 |

> 💡 **核心洞见**：Secrets 中的 Name 就是后续 YAML 和代码中引用该值的 key。因此 Name 的命名必须与代码中使用的变量名严格一致。GitHub 对 Secrets 的命名规则：只能包含字母、数字和下划线，且**不能以 `GITHUB_` 开头**（那是系统保留前缀）。

> ⚠️ **注意事项**：Secrets 的加密存储特性意味着：
> - 值不会出现在 Actions 的日志输出中（GitHub 会自动屏蔽）
> - 不会通过 pull request 的 fork 仓库触发（防止泄露给外部贡献者）
> - 任何尝试在日志中 `echo` 输出 Secret 值的操作都会被 GitHub 自动替换为 `***`

---

### 4.3 Cron 表达式与定时触发

#### 🧠 直观理解

Cron 表达式就像一张"闹钟设置表"——用一个字符串精确描述"什么时候该执行任务"。在 GitHub Actions 中，通过 `schedule` 事件配合 cron 表达式来实现定时触发。

#### 📖 详细解释

**Cron 表达式的 5 段格式**

GitHub Actions 使用的 cron 表达式为标准的 5 段式格式：

```
┌─────────── 分钟 (0–59)
│ ┌───────── 小时 (0–23)
│ │ ┌─────── 日期 (1–31)
│ │ │ ┌───── 月份 (1–12)
│ │ │ │ ┌─── 星期 (0–7, 0 和 7 都表示周日)
│ │ │ │ │
* * * * *
```

以本项目中的表达式 `0 23 * * *` 为例逐段解析：

| 字段位置 | 值 | 含义 |
|---|---|---|
| 第 1 段（分钟） | `0` | 第 0 分钟，即整点触发 |
| 第 2 段（小时） | `23` | 第 23 小时，即晚上 11 点 |
| 第 3 段（日期） | `*` | 通配符，每天 |
| 第 4 段（月份） | `*` | 通配符，每月 |
| 第 5 段（星期） | `*` | 通配符，每周每天 |

合起来的语义：**每天 UTC 时间 23:00 整执行**。

**UTC 时区与北京时间转换**

这是最容易出错的地方。GitHub Actions 的 cron 调度器使用的是 **UTC 时间（协调世界时）**，而中国用户使用的是 **北京时间（UTC+8）**。这意味着：

```
UTC 23:00 + 8 小时 = 北京时间 次日 07:00
```

即，cron 表达式中写 `0 23 * * *`，实际推送时间是**每天早晨 7 点（北京时间）**。

> ⚠️ **注意事项**：如果不注意 UTC 时区转换，很容易把定时任务设错时间。例如，如果你想让北京时间早上 9 点执行，cron 中小时字段应该写 `1`（9 - 8 = 1），而不是 `9`。错误地写 `0 9 * * *` 会导致北京时间**下午 5 点**（17:00）才执行。

**常用 Cron 表达式与北京时间对照表**

| 需求（北京时间） | cron 表达式 | UTC 时间 |
|---|---|---|
| 每天早上 7:00 | `0 23 * * *` | 前一天 23:00 |
| 每天早上 8:00 | `0 0 * * *` | 当天 00:00 |
| 每天早上 9:00 | `0 1 * * *` | 当天 01:00 |
| 每天中午 12:00 | `0 4 * * *` | 当天 04:00 |
| 每周一早 7:00 | `0 23 * * 0` | UTC 周日 23:00 |

> 💡 **核心洞见**：GitHub Actions 的定时触发**不是精确到秒的**。在系统负载高峰期，实际执行时间可能会延迟几分钟甚至十几分钟。对于天气推送这种场景，延迟几分钟完全可接受，但如果你在做对时间敏感的金融交易类任务，这个延迟就需要纳入考量。

---

### 4.4 GitHub Actions YAML 配置文件逐段解析

#### 💻 Step-by-Step

**Step 1：触发条件配置（`on`）**

```yaml
# 文件名: .github/workflows/weather-report.yml
# 功能: 天气预报微信推送 — 定时触发 + 手动触发

name: 天气预报推送

on:
  schedule:
    - cron: '0 23 * * *'       # UTC 23:00 = 北京时间次日 07:00
  workflow_dispatch:            # 允许手动触发
```

| 行号 | 配置项 | 解释 |
|---|---|---|
| 1 | `name: 天气预报推送` | Actions 列表中显示的工作流名称，便于识别 |
| 2-3 | `on:` | 定义触发条件块，所有触发方式都写在下面 |
| 4-5 | `schedule: - cron: '0 23 * * *'` | 定时触发，每天 UTC 23:00 执行。`schedule` 是一个数组，可以配置多个 cron 时间点 |
| 6 | `workflow_dispatch:` | 手动触发开关，添加后 Actions 页面会出现 **Run workflow** 按钮 |

> ⚠️ **注意事项**：`schedule` 下的 `cron` 必须用引号包裹（单引号或双引号均可），否则 YAML 解析器可能将 `*` 解释为别名语法导致配置失败。

**Step 2：运行环境与 Python 配置步骤（`steps`）**

```yaml
jobs:
  weather-report:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout 代码
        uses: actions/checkout@v4

      - name: 配置 Python 环境
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: 安装 Python 依赖
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: 执行天气推送脚本
        env:
          APP_ID: ${{ secrets.APP_ID }}
          APP_SECRET: ${{ secrets.APP_SECRET }}
          OPEN_ID: ${{ secrets.OPEN_ID }}
          TEMPLATE_ID: ${{ secrets.TEMPLATE_ID }}
        run: python weather_report.py
```

| Step | 动作 | 详细解释 |
|---|---|---|
| Checkout 代码 | `actions/checkout@v4` | 将仓库代码拉取到 Actions 虚拟机的工作目录中。这是绝大多数工作流的第一步 |
| 配置 Python 环境 | `actions/setup-python@v5` + `python-version: '3.12'` | 使用 GitHub 官方 Action 安装指定版本的 Python |
| 升级 pip | `python -m pip install --upgrade pip` | 先升级 pip 到最新版，避免旧版本安装依赖时出现兼容性问题 |
| 安装依赖 | `pip install -r requirements.txt` | 从 requirements.txt 中读取依赖列表并安装 |
| 执行脚本 | `python weather_report.py` | 运行天气推送的主脚本 |

> ⚠️ **注意事项**：Step 的执行是**顺序的、有依赖的**。如果"安装 Python 依赖"这一步失败，后续的"执行天气推送脚本"就不会执行。每个 Step 的运行环境是共享的，即前一步安装的包后一步可以直接使用。

---

### 4.5 环境变量传递机制详解

#### 🔗 推导链：环境变量完整传递链路

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  GitHub Secrets  │      │   YAML env 块    │      │   Python 代码    │
│                  │      │                  │      │                  │
│  APP_SECRET      │─────▶│ env:             │─────▶│ os.environ       │
│  = "abc123..."   │      │   APP_SECRET:    │      │   .get(          │
│                  │      │   ${{secrets.    │      │   "APP_SECRET")  │
│                  │      │   APP_SECRET}}   │      │                  │
│                  │      │                  │      │ → "abc123..."    │
│ (加密存储,       │      │ (Step 运行时      │      │ (脚本内可用      │
│  仅 Actions      │      │  注入为环境变量)   │      │  字符串变量)     │
│  可读取)         │      │                  │      │                  │
└─────────────────┘      └─────────────────┘      └─────────────────┘
        步骤 1                   步骤 2                   步骤 3
   配置时写入               YAML 引用注入            Python 运行时读取
```

每一步的详细说明：
1. **步骤 1（配置时）**：在 GitHub 仓库的 Settings → Secrets → Actions 中手动输入键值对。值被加密存储，只有 Actions 运行时才能读取。
2. **步骤 2（YAML 引用注入）**：在 YAML 的 `env` 块中使用 `${{ secrets.XXX }}` 语法引用。GitHub Actions 引擎在创建运行环境时，将 Secret 的真实值注入为操作系统的环境变量。
3. **步骤 3（Python 运行时读取）**：Python 脚本通过 `os.environ.get("变量名")` 读取系统环境变量。

#### 💻 代码示例

```python
# 文件名: weather_report.py
# 功能: 从环境变量读取配置，调用微信 API 发送天气推送

import os
import requests

# ── 从环境变量读取敏感配置 ──
# os.environ.get() 的第一个参数是环境变量名，第二个参数是默认值（取不到时使用）
APP_ID = os.environ.get("APP_ID")          # 微信测试号 appID
APP_SECRET = os.environ.get("APP_SECRET")  # 微信测试号 appsecret
OPEN_ID = os.environ.get("OPEN_ID")        # 接收者的 openID
TEMPLATE_ID = os.environ.get("TEMPLATE_ID") # 消息模板 ID

# ── 获取 access_token ──
def get_access_token(app_id: str, app_secret: str) -> str:
    """使用 appID 和 appsecret 向微信服务器换取 access_token"""
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
    resp = requests.get(url)
    data = resp.json()
    return data.get("access_token")

# ── 主流程 ──
if __name__ == "__main__":
    token = get_access_token(APP_ID, APP_SECRET)
    # ... 获取天气数据并推送 ...
    print(f"推送完成")
```

| 行号 | 代码 | 解释 |
|---|---|---|
| 8-11 | `os.environ.get("APP_ID")` 等 | 从系统环境变量读取配置值。这些值由 YAML 中的 `env` 块注入 |
| 14-19 | `get_access_token()` | 用 appID + appsecret 向微信 API 换取有效期 2 小时的 access_token |

> ⚠️ **注意事项**：`os.environ.get()` 和 `os.environ["KEY"]` 的区别在于：前者取不到值时返回 `None`（或自定义默认值），后者会直接抛出 `KeyError`。在接收对外部注入的环境变量时，使用 `.get()` 更安全。

> 🐞 **常见坑**：环境变量的名称在 Secrets、YAML、Python 三处必须**完全一致**。例如，如果 YAML 中写的是 `APP_ID`，但 Python 中用 `os.environ.get("APPID")`（少了下划线），取到的就是 `None`，API 调用时会出现认证失败。这个错误没有明显的报错堆栈，排查起来比较隐蔽。

---

### 4.6 执行验证：手动触发

#### 🎯 验证目标

在 Actions 页面手动触发一次天气推送，确认整条链路通畅——最终手机微信收到天气消息。

#### 💻 Step-by-Step

**Step 1：进入 Actions 页面**

点击仓库顶部导航栏的 **Actions** 选项卡，在左侧工作流列表中找到 **天气预报推送**（即 `name` 字段的值）。

**Step 2：手动触发**

在右侧区域找到 **Run workflow** 下拉按钮（这是 `workflow_dispatch` 配置项赋予的能力），点击它展开面板。如果脚本不需要额外参数，直接点击绿色 **Run workflow** 按钮即可。

```
Actions 页面
┌─────────────────────────────────────────────────────┐
│  All workflows                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │ 天气预报推送                                     │ │
│  │                                                  │ │
│  │                          ┌─────────────────────┐ │ │
│  │                          │  Run workflow  ▾    │◀── 点击
│  │                          └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

**Step 3：查看执行过程**

点击新出现的运行记录，可以看到每个 Step 的实时日志输出。检查每一步的状态是否为绿色的对勾（通过）。

**Step 4：验证结果**

- 脚本执行完成后，Python 的 `print` 输出应在日志中可见
- 手机微信应收到一条来自测试号的天气推送消息

> 💡 **核心洞见**：`workflow_dispatch`（手动触发）和 `schedule`（定时触发）是**并行生效的**，二者互不排斥。定时触发每天自动跑一次，手动触发可以随时用来调试和验证。

#### ✅ 验证检查清单

| 检查项 | 通过标准 |
|---|---|
| Actions 页面出现 "天气预报推送" 工作流 | `name` 字段配置正确 |
| 出现 Run workflow 按钮 | `workflow_dispatch` 已配置 |
| Python 环境配置步骤通过 | 日志中显示 "Python 3.12.x" 和 pip 升级成功 |
| 依赖安装通过 | `pip install -r requirements.txt` 无报错 |
| 脚本执行通过 | Python 脚本正常结束，`exit code 0` |
| 手机收到推送 | 微信测试号消息列表中出现天气推送 |

---

### 4.7 排错指南

#### 🐛 排错实录 1：环境变量取到空值导致推送失败

**❌ 错误现象**

脚本执行日志中没有报错，但微信没有收到消息。排查发现 `access_token` 获取失败，`os.environ.get("APP_ID")` 返回了 `None`。

**🔍 原因分析**

Python 中使用的环境变量名与 YAML `env` 块中定义的不一致。例如 YAML 中配置的是 `APP_ID`，Python 代码中却写成了 `APPID`（少了中间的下划线）。

**✅ 修复方法**

确保三处的变量名完全一致：

| 位置 | 写法 |
|---|---|
| GitHub Secrets → Name | `APP_ID` |
| YAML → env | `APP_ID: ${{ secrets.APP_ID }}` |
| Python | `os.environ.get("APP_ID")` |

**📝 经验总结**

建议将环境变量的 Name 在项目 README 中明确列出，或在代码中用常量统一管理，避免手动敲错。

#### 🐛 排错实录 2：Cron 表达式配置错误导致执行时间不对

**❌ 错误现象**

设置 `cron: '0 7 * * *'` 期望北京时间早上 7 点推送，结果实际在下午 3 点（15:00）才收到消息。

**🔍 原因分析**

UTC 时间 07:00 对应北京时间 15:00（7 + 8 = 15）。开发者忘记将北京时间减去 8 小时转换为 UTC。

**✅ 修复方法**

正确表达式：`cron: '0 23 * * *'`（23 = 7 + 24 - 8 = 前一天的 23 点）。

**📝 经验总结**

一个简单的核对方法：UTC 时间 = 北京时间 - 8。如果减完后出现负数，则加 24 并日期减一天。例如早上 7 点 → 7 - 8 = -1 → -1 + 24 = 23，所以是前一天的 23:00。

-


--

## 五、样例三：京东签到 — Cookie 获取与配置

### 5.1 场景说明与目标

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 理解 Cookie 作为浏览器身份凭证的作用和工作原理
> - [ ] 使用 Chrome DevTools 的仿真设备功能获取京东移动端 Cookie
> - [ ] 将 Cookie 安全地配置为 GitHub Secret 供 Actions 使用
> - [ ] 理解 Action 配置文件的复用模式：相同结构，不同凭证

#### 📋 场景背景

京东签到是典型的"薅羊毛"自动化场景。每天在京东 App 上手动签到可以获得京豆（可抵扣现金），但日复一日的手动操作既繁琐又容易遗忘。通过 GitHub Actions 定时执行签到脚本，你只需配置一次，之后每天自动完成，真正实现"躺赚"。

> 🔗 **前置知识**：本模块的所有基础概念已在 [第四章：天气推送] 中详细讲解过，包括 GitHub Actions Cron 定时触发、Secrets 环境变量机制、以及 Workflow 文件的 YAML 结构。如果你还未熟悉这些概念，建议先回顾第四章，本节将直接在此基础上展开。

### 5.2 Action 配置回顾：与天气推送的对比

#### 🏗️ Action 配置结构

京东签到的 Action 配置与前文天气推送几乎完全一致，整体遵循固定的四步范式。打开 `.github/workflows/` 目录下的签到配置文件，结构如下：

```yaml
# 文件名: .github/workflows/jd-sign.yml
# 功能: 京东每日签到，自动获取京豆

name: JD Daily Sign

on:
  schedule:
    # 每天早晨 8:00 (北京时间) 自动执行
    # UTC 0:00 = 北京时间 8:00
    - cron: '0 0 * * *'
  workflow_dispatch:       # 允许手动触发，方便测试

jobs:
  sign:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout 仓库代码
        uses: actions/checkout@v4
      
      - name: 设置 Python 环境
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      
      - name: 安装 Python 依赖
        run: pip install -r requirements.txt
      
      - name: 执行京东签到脚本
        env:
          JD_COOKIE: ${{ secrets.JD_COOKIE }}
        run: python jd_sign.py
```

#### 🔀 与天气推送的唯一区别

将本模块的配置与天气推送放在一起对比，差异一目了然：

| 对比维度 | 天气推送（第四章） | 京东签到（本章） | 是否相同 |
|---|---|---|---|
| 触发机制 `on` | `schedule` + `workflow_dispatch` | `schedule` + `workflow_dispatch` | 相同 |
| Cron 执行时间 | 每天 7:00（UTC 23:00） | 每天 8:00（UTC 0:00） | 错开 1 小时 |
| 运行环境 `runs-on` | `ubuntu-latest` | `ubuntu-latest` | 相同 |
| Step 1: Checkout | `actions/checkout@v4` | `actions/checkout@v4` | 相同 |
| Step 2: Python 环境 | `actions/setup-python@v5` | `actions/setup-python@v5` | 相同 |
| Step 3: 安装依赖 | `pip install -r requirements.txt` | `pip install -r requirements.txt` | 相同 |
| Step 4: 执行脚本 | `python weather.py` | `python jd_sign.py` | 仅脚本名不同 |
| 环境变量 | `APP_ID`, `APP_KEY`, `CITY` 等多 | `JD_COOKIE` 单一 | **唯一实质区别** |
| 凭证存储方式 | GitHub Secrets | GitHub Secrets | 相同 |

> 💡 **核心洞见**：GitHub Actions 的配置模式具有极强的可复用性。一旦掌握了「定时触发 → 准备环境 → 注入密钥 → 执行脚本」这个四步范式，换一个新的自动化任务只需要修改**两处**：Cron 表达式（改执行时间）和环境变量（换凭证）。Workflow 的骨架结构完全不用动。这正是工程化思维——把"相同"的部分抽象成模板，"不同"的部分参数化。

#### 🧠 为什么要错开执行时间？

天气推送定在 7:00，京东签到定在 8:00，两者间隔一小时，这不是随意设置的：

```
UTC 时间线（北京时间）
─────────────────────────────────────────────────────▶
  22:00    23:00      0:00       1:00       2:00
 (6:00)   (7:00)    (8:00)     (9:00)    (10:00)
           │          │
           ▼          ▼
      天气推送     京东签到
      Workflow     Workflow
```

- **避免资源竞争**：GitHub Actions 对免费账户有并发 Job 数量限制。如果两个 Workflow 在同一分钟触发，可能出现排队等待。
- **UTC 表达式的可读性**：`0 0 * * *`（UTC 零点）比 `0 23 * * *`（UTC 23 点）更直观易读，且恰好对应国内用户友好的早晨 8 点。
- **容错窗口**：万一 7:00 的 Workflow 执行超时或异常，不会影响 8:00 的任务。

### 5.3 Cookie 的概念与作用

#### 🧠 直观理解

Cookie 就像你去酒店办理入住时前台给你的那张**房卡**。办理入住时（登录），前台核实了你的身份证（用户名+密码），然后给你一张房卡（Cookie）。之后你每次进房间、去健身房、去餐厅，只需要刷这张房卡就行——不需要每次都出示身份证。

在浏览器中，Cookie 就是这张"房卡"。你登录京东后，服务器验证你的身份，发给你一串 Cookie 存在浏览器里。之后你每次访问京东的任何页面，浏览器都会自动附带这串 Cookie，服务器凭此就知道"这是已登录的用户，不用再验证了"。

#### 📖 详细解释

Cookie 是 Web 开发中最基础的会话保持机制。它的工作流程可以分为三个阶段：

```
┌──────────┐                                    ┌──────────┐
│  浏览器    │                                    │  京东服务器 │
└────┬─────┘                                    └────┬─────┘
     │                                               │
     │  ① 用户输入用户名密码，点击登录                    │
     │  POST /login (username + password)             │
     │──────────────────────────────────────────────▶│
     │                                               │ 服务器验证身份
     │                                               │ 生成会话凭证
     │  ② 登录成功，服务器下发 Cookie                    │
     │  HTTP 200 OK                                  │
     │  Set-Cookie: pt_key=AA...xxx;                 │
     │              pt_pin=jd_user;                  │
     │              pwdt_id=CC...zzz                 │
     │◀──────────────────────────────────────────────│
     │                                               │
     │  浏览器将 Cookie 保存在本地存储中                    │
     │                                               │
     │  ③ 用户后续访问任意京东页面                        │
     │  GET /m.jd.com                                │
     │  Cookie: pt_key=AA...xxx; pt_pin=jd_user;...  │  ← 浏览器自动附加
     │──────────────────────────────────────────────▶│
     │                                               │ 服务器凭 Cookie
     │                                               │ 识别已登录用户
     │  ④ 返回已登录状态的页面                           │
     │◀──────────────────────────────────────────────│
     │                                               │
```

关键要点：

- **自动携带**：Cookie 一旦被浏览器存储，后续对该域名（`*.jd.com`）的所有请求都自动附加，无需脚本或代码干预。
- **域名绑定**：Cookie 是跟域名绑定的，`jd.com` 的 Cookie 不会发给 `taobao.com`。
- **有效期**：每个 Cookie 有过期时间。京东的 Cookie 通常有效几天到几周不等，过期后需要重新登录获取。

#### 🔗 Cookie 与自动化签到的关系

自动化签到脚本无法完成"浏览器登录"这一步——它不会点按钮、不会输验证码、不会过滑块验证。但如果我们把**登录后**浏览器里已有的 Cookie 提取出来，交给 Python 脚本，脚本在发送 HTTP 请求时手动附加这个 Cookie，服务器就会认为"这是一个已登录用户发来的请求"，从而允许脚本调用签到接口。

```
人类操作（一次性）                     自动化脚本（每日执行）
─────────────────                     ────────────────
手动登录京东                          读取 JD_COOKIE 环境变量
    │                                      │
    ▼                                      ▼
浏览器获得 Cookie  ──复制──▶ 存入 GitHub Secret ──注入──▶ Python requests
                                                              │
                                                              ▼
                                                    携带 Cookie 请求签到接口
                                                              │
                                                              ▼
                                                           签到成功
```

> ⚠️ **注意事项**：Cookie 本质上就是你的"数字身份证"。任何人拿到你的 Cookie，就能以你的身份在京东上做任何事——下单、查看订单、甚至修改账户信息。这就是为什么 Cookie **绝不能**以明文写在代码里，必须通过 GitHub Secrets 加密存储。

### 5.4 💻 Step-by-Step：获取京东 Cookie

本节是整个模块的核心内容。获取 Cookie 的操作全部在浏览器开发者工具中完成，不需要安装任何额外软件。

#### 🏗️ 前置准备

在开始之前，请确保：
- 使用 Chrome 浏览器（Edge、Firefox 开发者工具位置类似，本节以 Chrome 为例）
- **已在浏览器中登录过京东账号**——Cookie 只有在登录成功后才会生成。如果你不确定是否登录，先打开 `jd.com` 检查右上角是否显示你的用户名
- 如果你的登录已过期（页面提示需要重新登录），请先完成一次手动登录

---

**Step 1: 进入京东主页，打开开发者工具**

在 Chrome 地址栏中输入 `https://www.jd.com` 并回车，进入京东首页。然后按下键盘上的 **F12** 键（Mac 用户按 **Command + Option + I**），打开 Chrome 开发者工具（DevTools）。

> 💡 **替代方式**：你也可以在页面任意位置右键 → 选择「检查」（Inspect），效果相同。

开发者工具打开后，通常默认停靠在浏览器窗口的右侧或底部，其顶部有一排标签页：

```
┌──────────────────────────────────────────────────────────────┐
│ [Elements] [Console] [Sources] [Network] [Performance] ...  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│                        开发者工具面板                           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

我们稍后会用到 Network 标签，但现在先关注另一个关键按钮。

---

**Step 2: 切换仿真设备为手机模式**

在开发者工具面板的**左上角**，找到"切换设备工具栏"按钮。这个按钮的图标是一个**手机/平板电脑**的形状，位于元素选择器（箭头图标）的右侧：

```
┌───────────────────────────────────────────────┐
│ ┌──┬────┬──────────────────────────┬─────┐   │
│ │🔍│ 📱 │ Elements Console Source..│ ... │   │
│ └──┴────┴──────────────────────────┴─────┘   │
│          ↑                                    │
│     点击这个手机图标                            │
└───────────────────────────────────────────────┘
```

点击后，浏览器主窗口的页面会自动变成手机屏幕的比例，顶部出现一个设备模拟工具栏：

```
┌───────────────────────────────────────────────────┐
│ [iPhone 12 Pro  ▼]  [375] × [812]  [50%] [...]   │
├───────────────────────────────────────────────────┤
│                                                   │
│              京东手机版页面（m.jd.com）               │
│                                                   │
│                                                   │
└───────────────────────────────────────────────────┘
```

在设备下拉菜单（默认为 "Responsive"）中选择一款手机设备，如 **iPhone 12 Pro** 或 **Pixel 5**。这一步的核心目的是让浏览器模拟手机的 User-Agent 和屏幕尺寸，从而加载京东的**移动版页面**（域名从 `www.jd.com` 变为 `m.jd.com`）。

> ⚠️ **为什么必须获取移动端 Cookie？**
>
> 京东的签到接口使用的是**移动端**的认证 Cookie，PC 端的 Cookie 格式与移动端不同。PC 端页面的域名是 `www.jd.com`，移动端是 `m.jd.com`，它们各自使用独立的 Cookie 体系。签到脚本模拟的是手机 App 的请求行为，所以**必须**在手机模式下抓取，否则拿到的 PC 端 Cookie 无法用于签到。

---

**Step 3: 刷新页面，切换到 Network（网络）标签**

保持仿真设备模式开启，按 **F5** 或 **Ctrl + R**（Mac：**Command + R**）刷新页面。此时页面会以手机模式重新加载。

刷新后，开发者工具会自动记录所有网络请求。点击顶部的 **Network**（网络）标签页：

```
┌──────────────────────────────────────────────────────────┐
│  [Elements] [Console] [Sources] [▶ Network] ...          │
├──────────────────────────────────────────────────────────┤
│  ☐ Preserve log   ☐ Disable cache                       │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Name            Status    Type       Size    Time   │ │
│  │ m.jd.com        200       document   45KB    320ms  │ │
│  │ jquery.min.js   200       script     87KB    150ms  │ │
│  │ common.css      200       stylesheet 23KB    90ms   │ │
│  │ logo.png        200       png        12KB    45ms   │ │
│  │ ...                                                 │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

此时 Network 面板中会列出页面加载过程中的所有网络请求。如果你看到的内容很少或为空，说明你可能需要勾选顶部的 **Preserve log**（保留日志）复选框，然后再次刷新。

---

**Step 4: 在请求列表中找到 `m.jd.com`**

在 Network 面板左侧的请求列表中，按名称列查找域名为 **`m.jd.com`** 的请求。由于请求可能很多，推荐两种快速定位方法：

- **方法一（筛选）**：在 Network 面板顶部的 Filter 输入框中，直接输入 `m.jd.com`，列表会只显示与该域名相关的请求，结果一目了然。

```
┌──────────────────────────────────────────────────────────┐
│  [m.jd.com                               ]  ← 在这里输入 │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Name            Status    Type       Size    Time   │ │
│  │ m.jd.com        200       document   45KB    320ms  │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

- **方法二（手动查找）**：不加筛选，直接在列表中往上滚动查找。`m.jd.com` 通常是列表中最顶部或接近顶部的那条请求，其 Type（类型）列显示为 `document`——这表示它是页面加载的第一个也是最主要的请求。

---

**Step 5: 查看请求头，提取 Cookie 字段**

**点击** `m.jd.com` 这一行，右侧（或下方）会展开该请求的详细信息面板。确保选中 **Headers** 子标签：

```
┌──────────────────────────┬──────────────────────────────────────┐
│ 请求列表（左侧）           │ 请求详情面板（右侧）                    │
│                          │                                      │
│ ▶ m.jd.com               │  [Headers] [Preview] [Response] [..] │
│   jquery.min.js          │                                      │
│   common.css             │  ▼ General                           │
│   logo.png               │    Request URL: https://m.jd.com/    │
│   ...                    │    Request Method: GET               │
│                          │    Status Code: 200 OK               │
│                          │                                      │
│                          │  ▼ Response Headers                  │
│                          │    content-type: text/html; ...      │
│                          │    ...                               │
│                          │                                      │
│                          │  ▼ Request Headers                   │
│                          │    Accept: text/html,application/... │
│                          │    Accept-Encoding: gzip, deflate    │
│                          │    Accept-Language: zh-CN,zh;q=0.9   │
│                          │    Cookie: pt_key=AAJhQexample...;   │  ← 这就是目标！
│                          │             pt_pin=jd_example_user;  │
│                          │             pwdt_id=example_id;      │
│                          │             ...                      │
│                          │    User-Agent: Mozilla/5.0 ...       │
└──────────────────────────┴──────────────────────────────────────┘
```

在 **Request Headers**（请求头）区域中，找到以 `Cookie:` 开头的那一行。Cookie 的值通常非常长，包含多个以分号（`;`）分隔的键值对，例如：
- `pt_key=...` —— 登录令牌
- `pt_pin=...` —— 用户标识（通常是你的京东用户名）
- `pwdt_id=...` —— 设备/会话标识

---

**Step 6: 复制 Cookie 值**

将 **`Cookie:` 冒号后面的所有内容**（从 `pt_key=` 开始到整个值的末尾）全部选中，按下 **Ctrl + C**（Mac: **Command + C**）复制。

```
Cookie: pt_key=AAJhQexampleKeyabcdefg1234567890;pt_pin=jd_example_user;pwdt_id=abc123def456;...
        └────────────────────── 复制这部分 ──────────────────────────────────────────────┘
```

> ⚠️ **复制 Cookie 的四条铁律**
>
> | 铁律 | 说明 |
> |---|---|
> | **全部复制，一个字符不能少** | Cookie 中的每个键值对都有用，只要少一个分号或一个字符，服务器就会认为凭证不完整，签到失败 |
> | **不要复制 `Cookie:` 前缀本身** | 只复制冒号后面、空格之后的值部分。前缀 `Cookie:` 是 HTTP 协议的字段名，不是你需要的凭证内容 |
> | **不要修改任何内容** | 不要删除"看起来没用"的部分，不要调整键值对的顺序，不要添加或删除空格和分号 |
> | **注意有效期** | 京东 Cookie 有效期通常为几天到几周。签到脚本突然失效时，第一步就是重新获取 Cookie |

#### ✅ 验证 Cookie 是否有效

复制完成后，可以先做一次快速验证。将 Cookie 粘贴到一个临时文本文件里，然后写一个简单的 Python 脚本测试：

```python
# 文件名: test_cookie.py
# 功能: 测试京东 Cookie 是否有效

import requests

cookie_str = "pt_key=xxx;pt_pin=yyy;..."  # 替换为你的 Cookie

headers = {
    "Cookie": cookie_str,
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)"
}

# 尝试访问京东用户信息接口
resp = requests.get("https://api.m.jd.com/client.action", headers=headers)

# 如果返回的 JSON 中包含你的用户昵称，说明 Cookie 有效
print(resp.status_code)
```

如果 HTTP 状态码是 200 且返回内容不是登录页面或错误提示，说明 Cookie 有效。

### 5.5 💻 Step-by-Step：将 Cookie 配置为 GitHub Secret

获取到 Cookie 后，下一步是将其安全地存入 GitHub Secrets，供 Actions Workflow 使用。

---

**Step 1: 进入仓库的 Settings 页面**

打开你的 GitHub 仓库主页，点击顶部导航栏最右侧的 **Settings** 标签：

```
┌────────────────────────────────────────────────────────────────┐
│  [<> Code]  [Issues]  [Pull requests]  [Actions]  [⚙ Settings] │
│                                                         ↑      │
│                                                    点击这里     │
└────────────────────────────────────────────────────────────────┘
```

---

**Step 2: 找到 Secrets and Variables → Actions**

Settings 页面有一个很长的左侧导航菜单。向下滚动，找到 **Secrets and variables** 分组，展开后点击 **Actions**：

```
Settings 左侧导航菜单
┌──────────────────────────┐
│ General                  │
│ Access                   │
│ Branches                 │
│ ...                      │
│ Environments             │
│ Secrets and variables  ▾ │
│   ├─ Actions        ←    │  ← 点击这个
│   └─ Codespaces          │
│ ...                      │
└──────────────────────────┘
```

---

**Step 3: 创建新的 Repository Secret**

进入 Actions secrets 页面后，你会看到当前仓库已有的所有 Secrets 列表（如果之前配置过天气推送，这里应该能看到 `APP_ID` 等条目）。

点击页面右侧绿色的 **New repository secret** 按钮，在弹出的表单中填写：

| 字段 | 填写内容 | 说明 |
|---|---|---|
| **Name** | `JD_COOKIE` | 必须与 YAML 中 `${{ secrets.JD_COOKIE }}` 完全一致（大小写敏感） |
| **Secret** | `pt_key=xxx;pt_pin=yyy;...` | 粘贴从浏览器复制的完整 Cookie 字符串 |

```
┌──────────────────────────────────────────────┐
│          New Repository Secret               │
│                                              │
│  Name *                                     │
│  ┌──────────────────────────────────────┐    │
│  │ JD_COOKIE                            │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  Secret *                                   │
│  ┌──────────────────────────────────────┐    │
│  │ pt_key=AAJh...;pt_pin=jd_user;      │    │
│  │ pwdt_id=abc123;...                  │    │
│  │                                      │    │
│  └──────────────────────────────────────┘    │
│                                              │
│          [ Add secret ]                      │
└──────────────────────────────────────────────┘
```

点击绿色的 **Add secret** 按钮完成保存。

> ⚠️ **注意事项**：Secret 保存后，GitHub 立即对其加密存储。此后**任何人（包括你自己）都无法再查看这个 Secret 的明文内容**——页面上只会显示 `JD_COOKIE` 这个名字，值被完全隐藏。你可以更新（覆盖写入新值）或删除它，但不能读取。因此：
> - 保存前务必**再次确认** Cookie 值是否完整、是否正确
> - 建议先将 Cookie 粘贴到本地文本编辑器中检查，确认无误后再粘贴到 Secret 表单

> 🔗 **关联知识**：这个配置流程与天气推送中配置 `APP_ID`、`APP_KEY` 等 Secrets 的方法**完全一样**。唯一的区别是：天气推送需要创建多个 Secret，而京东签到只需要一个 `JD_COOKIE`。流程复用的价值正在于此——每个新的自动化任务虽然业务不同，但凭证管理的方式是统一的。

### 5.6 执行时间与触发机制

#### 🕗 Cron 表达式解读

京东签到使用 `0 0 * * *` 作为执行时间：

```
┌─────────── 分钟: 0（整点触发）
│  ┌──────── 小时: 0（UTC 时间的 0 点）
│  │  ┌───── 日: *（每天）
│  │  │  ┌── 月: *（每月）
│  │  │  │  ┌ 星期: *（每周每天）
│  │  │  │  │
0  0  *  *  *
```

GitHub Actions 使用 **UTC 时间（协调世界时）**，北京时间比 UTC 快 8 小时（UTC+8）。所以：
- **UTC 0:00** = **北京时间 8:00**

> 💡 **经验之谈**：为什么天气推送选 UTC 23:00（北京时间 7:00），京东签到选 UTC 0:00（北京时间 8:00）？除了上一节提到的错峰执行原因外，`0 0 * * *` 在写法上比 `0 23 * * *` 更直观——它清楚地表示"每一天的开始"。在配置多个定时任务时，优先选择整点或半点，便于日后维护时一目了然地看出执行时间。

#### 🔄 签到执行全流程

```
北京时间 8:00
    │
    ▼
┌────────────────────────────┐
│  GitHub Actions 定时触发     │
│  cron: '0 0 * * *'         │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│  申请 ubuntu-latest 虚拟机   │
│  （全新环境，无任何状态残留）   │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│  Step 1: Checkout 代码      │
│  拉取仓库全部文件到虚拟机     │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│  Step 2: 安装 Python 环境    │
│  actions/setup-python@v5   │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│  Step 3: pip install 依赖   │
│  安装 requests 等 Python 库  │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│  Step 4: 注入 JD_COOKIE     │
│  从 GitHub Secrets 中解密    │
│  写入虚拟机环境变量           │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│  执行 jd_sign.py            │
│  Python 脚本读取 JD_COOKIE   │
│  构建请求头，调用签到接口      │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│  ✅ 签到成功                 │
│  返回签到结果 + 获得京豆数量   │
│  日志输出在 Actions 面板可见  │
└────────────────────────────┘
```

#### ✅ 验证签到是否正常

配置完成后，有三种方式验证签到 Workflow 是否正常工作：

1. **手动触发（推荐，立即验证）**：
   - 进入仓库的 **Actions** 标签页
   - 左侧选择 **JD Daily Sign** Workflow
   - 点击 **Run workflow** 下拉 → 选择分支 → 点击绿色的 **Run workflow** 按钮
   - 几秒后会出现一个新的运行记录，点击进去查看日志

2. **查看运行日志**：
   - 点击具体的运行记录
   - 在 Jobs 列表中点击 `sign`
   - 展开「执行京东签到脚本」步骤，查看 Python 脚本的输出
   - 如果输出包含签到成功或京豆数量，说明一切正常

3. **等待定时触发**：
   - 不用做任何事，第二天早晨 8 点后回到 Actions 页面，确认是否有一条自动触发的运行记录，状态是否为绿色对勾（成功）

> 🐞 **常见坑：Cookie 过期**
>
> 签到失败的**头号原因**是 Cookie 过期。京东 Cookie 有效期通常在几天到几周之间。如果某天签到突然失败：
>
> - **现象**：Actions 日志显示 HTTP 返回了登录页面的 HTML 或"未登录"错误
> - **原因**：Cookie 中的 `pt_key` 已过期，服务器拒绝认证
> - **解决**：重新按 5.4 节的步骤获取新的 Cookie，然后进入 Settings → Secrets → Actions，找到 `JD_COOKIE` 点击 **Update**，粘贴新 Cookie 即可
> - **建议**：把"检查京东签到 + 更新 Cookie"作为月度例行维护项，避免长时间中断

### 5.7 ⚠️ Cookie 安全三原则

Cookie 的安全性是自动化签到中最重要的非功能性考量。请牢记以下三条原则：

> ⚠️ **Cookie 安全三原则**
>
> **1. 绝不硬编码**
>
> Cookie 永远不要以明文形式写在 YAML 配置文件或 Python 脚本中。一旦执行 `git commit` 并 `git push`，Cookie 就会永久留在 Git 的提交历史中——即使你后续删除了那行代码，攻击者依然可以通过 `git log` 回溯到历史版本拿到它。
>
> **2. 必须使用 Secrets 存储**
>
> GitHub Secrets 在存储时使用加密算法保护，在 Actions 运行时注入为环境变量，在日志输出中自动替换为 `***`。这是目前唯一的、安全的凭证传递通道。
>
> **3. 接受"过期"是安全特性**
>
> Cookie 会自动过期，这看起来是个麻烦（需要定期更新），但实际上是**安全设计**。它意味着即使 Cookie 意外泄露，攻击者的可利用窗口也被限制在 Cookie 的有效期内。过期的 Cookie 就是一段无用的字符串。

> ❓ **常见疑问：为什么不直接用密码登录，而是用 Cookie？**
>
> 密码是"我知道的东西"（知识因子），Cookie 是"服务器发给我的凭证"（持有因子）。在自动化脚本中：
>
> - **密码方式不可行**：京东的登录流程涉及验证码、滑块验证、短信二次验证等反爬机制，脚本无法可靠地完成这些步骤。
> - **Cookie 方式是可行替代**：Cookie 绕过了登录流程，直接以"已认证"身份调用接口，是自动化签到场景下的标准做法。
>
> Cookie 会被定期清理和过期，这恰恰是它的安全优势——相比"密码泄露=永久风险"，"Cookie 泄露=临时风险"的威胁模型要可控得多。

---


## 六、GitHub Actions Marketplace 市场

### 6.1 GitHub Marketplace 是什么

#### 🧠 直观理解

GitHub Marketplace 可以理解为 GitHub Actions 的「应用商店」。就像手机上的 App Store 汇集了各种应用供你下载使用，Marketplace 汇集了全球开发者贡献的 Actions 脚本，任何人都可以免费搜索、评估、取用。

#### 📖 详细解释

Marketplace 的入口是 `github.com/marketplace`，进入页面后选择顶部的 **Actions** 选项卡，就能看到成千上万个社区贡献的 Action 列表。每个 Action 都附带说明文档、使用示例和用户评价。

核心理念是**复用而非重写**。当你需要自动化某项任务时，不必从零开始编写 YAML 配置和 shell 脚本，而是先到 Marketplace 中搜索是否已有现成的 Action 可用。这些 Action 由社区维护，经过大量用户的实践验证，通常比自己从头实现更可靠、更稳定。

使用 Marketplace Action 的方式是在工作流文件中通过 `uses` 语法引用：

```yaml
# 引用 Marketplace 中 Action 的标准写法
# 格式: uses: {owner}/{repo}@{ref}
- name: 使用社区 Action
  uses: actions/checkout@v4  # GitHub 官方 Action，检出代码
```

> 💡 **核心洞见**：老师强调——「我们一切可以想到的对程序的自动化行为，在这里几乎都可以找到」。这体现了开源生态的最大优势：你遇到的问题，大概率已经有人解决过并封装成了 Action。先搜索，再决定是否自己写。

#### 🔀 对比辨析：自己写 vs 使用 Marketplace Action

| 维度 | 自己写脚本 | 使用 Marketplace Action |
|---|---|---|
| 开发成本 | 需要完整实现自动化逻辑 | 一行 `uses` 即可引入 |
| 维护负担 | 全部自己承担，需跟进平台变化 | 由社区维护，持续更新 |
| 可靠性 | 只在自己的项目上测试过 | 经大量用户和场景验证 |
| 灵活性 | 完全按需自定义 | 受限于 Action 暴露的 `with` 参数 |
| 学习成本 | 需要深入了解底层实现细节 | 只需了解输入参数和输出 |
| 适用场景 | 高度定制化、无现成方案的场景 | 通用自动化需求（构建、测试、部署） |

> ❓ **常见误解**：「Marketplace 里的 Action 是别人写的，不安全，可能有恶意代码。」
>
> 这个担忧需要辩证看待。第一，GitHub 提供了「Verified」蓝标机制——标有 ✅ Verified 的 Action 是由 GitHub 官方或其认证合作伙伴发布的，可信度最高。第二，每个 Action 本质是一个公开的 GitHub 仓库，你可以直接查看其完整源码，评估是否安全。第三，在生产实践中，推荐固定 Action 的版本号（如 `@v4` 而非 `@main`），甚至可以锁定到具体的 commit SHA（如 `@a1b2c3d4`），这样上游的任何更新都不会在未经你审核的情况下自动生效。

### 6.2 回顾：我们使用过的 PyInstaller Action

在前面的样例一中，我们实现了一个工作流：将 Python 项目自动打包成 Windows 可执行文件（.exe）。这个工作流中使用的 PyInstaller Action，正是从 Marketplace 中搜索找到的。

```yaml
# 样例一中使用的 PyInstaller Action
# 来源: 在 Marketplace 搜索 "PyInstaller" 后选用
- name: 将 Python 项目打包为 exe
  uses: JackMcKew/pyinstaller-action-windows@main
  with:
    path: src/
```

老师在实际课程中演示了完整的查找和使用过程：

1. **搜索**：打开 `github.com/marketplace`，切换到 Actions 选项卡，在搜索框中输入「pyinstaller」
2. **筛选**：浏览搜索结果，重点关注 Star 数高、最近有更新的 Action
3. **评估**：点开 `JackMcKew/pyinstaller-action-windows` 的详情页，阅读 README 了解功能和使用方法。该 Action 专门针对 Windows 平台打包，参数简洁，符合需求
4. **集成**：按照文档说明，通过 `uses` 语法将 Action 嵌入工作流 YAML，配置 `path` 参数指定 Python 源码所在目录
5. **运行**：推送代码触发工作流，Action 自动完成 Python 环境配置、依赖安装、pyinstaller 打包、产物输出的全流程

整个过程的工作流如下：

```
开发者推送代码
      │
      ▼
┌──────────────┐     ┌───────────────────────────┐     ┌──────────────┐
│ GitHub Actions│────▶│ pyinstaller-action-windows │────▶│ .exe 产物     │
│ 触发工作流    │     │ 自动配置环境 + 打包         │     │ 输出到 Artifacts│
└──────────────┘     └───────────────────────────┘     └──────────────┘
```

> 🔗 **前置知识**：`uses` 语法是引用外部 Action 的核心机制，详细用法见 [第 2.2 节：工作流语法核心]。如果你对样例一的完整工作流感兴趣，请回顾 [第 5.1 节：样例一 — PyInstaller 打包]。

### 6.3 Marketplace 热门分类一览

老师概括了 Marketplace 中几大类最常用的 Action，覆盖了日常开发中最典型的自动化需求：

| 分类 | 典型 Action 示例 | 功能说明 |
|---|---|---|
| **Docker 镜像构建** | `docker/build-push-action` | 自动构建 Docker 镜像并推送到 Docker Hub 或私有镜像仓库 |
| **安全扫描** | `github/codeql-action` | 对代码仓库进行静态安全分析，发现潜在漏洞并生成报告 |
| **云服务部署** | `azure/webapps-deploy` | 将应用自动部署到 Azure App Service 等云平台 |
| **语言打包** | `JackMcKew/pyinstaller-action-windows` | 将 Python 项目编译打包为独立可执行文件 |
| **代码质量检查** | `super-linter/super-linter` | 对多语言项目进行代码风格和质量统一检查 |
| **通知推送** | `slackapi/slack-github-action` | 将构建结果、部署状态推送到 Slack 等即时通讯工具 |
| **环境配置** | `actions/setup-python` | 在 runner 上配置指定版本的 Python 运行环境 |
| **GitHub Pages** | `peaceiris/actions-gh-pages` | 将静态网站自动部署到 GitHub Pages |

以 Docker 镜像构建为例，一个典型的使用流程如下：

```
开发者推送代码
      │
      ▼
┌──────────────┐     ┌──────────────────────┐     ┌──────────────────┐
│ 检出代码      │────▶│ build-push-action     │────▶│ Docker Hub       │
│ checkout     │     │ 读取 Dockerfile →     │     │ 镜像仓库中       │
│              │     │ 构建镜像 → 推送        │     │ 出现新版本镜像    │
└──────────────┘     └──────────────────────┘     └──────────────────┘
```

安全扫描的集成流程：

```
开发者推送代码 或 创建 Pull Request
      │
      ▼
┌──────────────┐     ┌───────────────────┐     ┌──────────────────────┐
│ 检出代码      │────▶│ codeql-action      │────▶│ 安全面板中            │
│ checkout     │     │ 静态分析 →          │     │ 展示漏洞清单 + 修复建议 │
│              │     │ 生成 SARIF 报告     │     │                      │
└──────────────┘     └───────────────────┘     └──────────────────────┘
```

> ⚠️ **注意事项**：不同 Action 对运行器（runner）有不同要求。例如 Docker 构建相关的 Action 通常需要在 `ubuntu-latest` 上运行，因为它依赖 Docker daemon；而 `pyinstaller-action-windows` 则必须指定 `windows-latest`。使用任何 Action 前，务必先阅读它的 README 文档，了解环境要求。

### 6.4 使用社区 Action 的四大优势

#### 🧠 直观理解

把 GitHub Actions 想象成乐高积木：Marketplace 提供了成千上万种标准化的「积木块」，你不需要自己烧制塑料、开模具、上色——只需要按照图纸把它们拼接在一起，就能搭建出完整的自动化流水线。你的角色从「生产者」变成了「组装者」。

#### 📖 详细解释

使用社区 Action 有四个核心优势：

**1. 开箱即用**

以 PyInstaller 打包为例，如果全部自己写，你需要处理：检查操作系统类型、安装 Python 和 pip、安装 pyinstaller 包、处理依赖冲突、配置打包参数、运行打包命令、收集产物文件。这一整套流程需要几十行 shell 脚本，且要处理各种异常情况。而使用 Marketplace 中的 PyInstaller Action，只需一行 `uses` 加一个 `path` 参数，所有细节由 Action 内部处理。

**2. 社区验证，踩坑更少**

一个 Star 数上千的 Action，意味着它已被成千上万个项目使用过。各种边界情况——Windows 路径分隔符、Python 版本兼容性、依赖安装失败重试——都已被发现和修复。你踩的坑，前人大概率已经踩过，并且修好了。

**3. 持续维护**

活跃的 Action 仓库会跟随平台变化而更新。例如 `actions/checkout` 是 GitHub 官方维护的，会适配最新的 Git 版本和 GitHub API 变更。如果自己写 checkout 逻辑，一旦 GitHub 升级 API，你的脚本就可能失效，而使用官方 Action 则无需担心这类问题。

**4. 聚焦业务，释放精力**

省去基础设施脚本的编写和维护时间后，你可以将精力集中在项目本身的业务自动化逻辑上。这是典型的「站在巨人肩膀上」的工程实践——用社区积累的智慧解决通用问题，你只负责项目独有的那部分。

> 💡 **核心洞见**：老师反复强调的一点——「不用什么都自己写，先去 Marketplace 找」。这是高效使用 GitHub Actions 的关键心态转变：从「我能写什么」切换为「我可以用什么」，思维从**开发者**转变为**集成者**。这种转变能让你把有限的时间和精力花在真正需要创新的地方。

### 6.5 如何选择靠谱的 Action

Marketplace 中同一个功能可能对应多个 Action（比如 Docker 构建就有好几个竞争者），如何从中选出最靠谱的那个？以下是实用的评估标准：

| 评估维度 | 具体判断方法 | 重要程度 |
|---|---|---|
| **Star 数** | 在 Action 的 GitHub 仓库首页直接可见，Star 数越高，社区认可度越高 | ⭐⭐⭐ |
| **更新频率** | 查看仓库最近 commit 的时间，以及最新 release 的日期。近期有更新的说明仍在活跃维护 | ⭐⭐⭐ |
| **文档质量** | README 是否清晰列出了功能、参数表（`with` 选项）、使用示例。文档残缺的慎用 | ⭐⭐⭐ |
| **GitHub 验证** | 仓库名旁是否有 ✅ Verified 蓝标。Verified 表示由 GitHub 官方或认证合作伙伴发布 | ⭐⭐ |
| **Issues 活跃度** | 查看 Issues 页面，用户提问是否有人回复、Bug 是否被及时修复 | ⭐⭐ |
| **使用者数量** | Marketplace 页面显示该 Action 被多少个仓库使用（仅作参考，不代表质量） | ⭐ |

一个实用的决策流程：

```
在 Marketplace 搜索到多个同类 Action 时：
    │
    ├── 有 GitHub 官方 Action（actions/ 开头）？
    │   └── 有 → 优先使用
    │       例如: actions/checkout、actions/setup-python
    │
    ├── 有 Verified 蓝标 Action？
    │   └── 有 → 次优先使用
    │       例如: azure/webapps-deploy、docker/build-push-action
    │
    └── 只剩社区 Action？
        └── 按以下标准筛选：
            ├── Star > 500
            ├── 最近 3 个月内有新的 commit 或 release
            └── README 包含完整参数说明和使用示例
```

> ⚠️ **注意事项**：使用社区 Action 时，务必**锁定版本**。不要使用 `@main` 或 `@master` 这类浮动的分支名称——上游作者随时可能推送不兼容的更新，导致你的工作流突然失效。推荐的锁定方式优先级为：
>
> 1. **语义化版本号**（推荐）：`@v4`、`@v3.1`
> 2. **完整 commit SHA**（最安全）：`@a1b2c3d4e5f6...`
>
> 避免使用 `@main`、`@latest` 等浮动标签。

### 6.6 本模块小结

GitHub Actions Marketplace 是 GitHub Actions 生态的核心组成部分。它消除了「每个团队都要自己写全套自动化脚本」的重复劳动，让开发者能以搭积木的方式快速组装 CI/CD 流水线。

回顾本节要点：
- Marketplace 是 Actions 的「应用商店」，入口在 `github.com/marketplace` 的 Actions 选项卡
- 我们已在样例一中实践过：从 Marketplace 搜索并使用 PyInstaller Action
- 常见分类涵盖 Docker 构建、安全扫描、云部署、语言打包等
- 选择 Action 时关注 Star 数、更新频率、文档质量三个核心维度
- 核心心态：先搜索，再决定是否自己写

> 🔗 **延伸阅读**：从下一章开始，我们将进入多环境部署的实战环节。届时你会在实际项目配置中看到更多 Marketplace Action 的应用——如何用部署类 Action 将应用推送到开发、测试、生产等不同环境。详见 [第 7 章：多环境部署]。

---

## 七、多环境部署 — 环境配置与保护规则

### 7.1 为什么要多环境部署？

#### 🧠 直观理解

多环境部署就像盖房子时的"样板间—毛坯验收—正式入住"流程。在真正的住户搬进去（生产环境上线）之前，你必须先在样板间里反复调整设计（QA 测试），然后让业主在毛坯状态下做最后检查（Staging 预发布），确认一切无误后才交钥匙。**多环境部署的本质，是用最低的风险成本，在代码到达用户手中之前，分层拦截问题。**

#### 📖 详细解释

在软件工程的完整 CI/CD（持续集成/持续部署）流水线中，代码从开发者的本地编辑器到最终用户看到的线上版本，中间必须穿越多重"安检门"。每一道安检门就是一个独立的环境。为什么要这样设计？原因有三：

1. **风险隔离**：如果只有一套环境，一旦部署出错，线上用户会立刻感知到故障。多层环境把故障半径限制在当前环境内，生产环境永远不被"脏代码"污染。
2. **配置差异管理**：QA 环境连接测试数据库，Production 环境连接线上数据库。如果只用一套配置，要么测试数据污染线上，要么线上密钥暴露在测试流程中。每个环境维护独立的 Secrets 和 Variables，从根本上杜绝配置串扰。
3. **审批与合规**：生产环境部署不是开发者一个人说了算的。需要上级审批、需要等待缓冲期、需要留下审计记录——这些都是多环境部署框架提供的治理能力。

> 🔗 **前置知识**：CI/CD 流水线中，多环境部署是"持续部署（CD）"侧的核心环节。详见系列课程中 CI/CD 概念与架构相关章节

GitHub 在仓库层面直接集成了多环境管理能力，无需借助第三方工具。接下来我们以 GitHub Environments 功能为主线，完整配置 QA、Staging、Production 三套环境。

---

### 7.2 三种环境概览

在深入配置之前，先建立三种环境的心智模型：

| 环境名称 | 别名 | 用途 | 保护规则严格度 | 典型受众 |
|---|---|---|---|---|
| **QA** | 测试环境 | 开发团队自测、自动化测试运行、功能验证 | 无限制 | 开发者 |
| **Staging**（STG） | 沙箱环境 / 预发布环境 | 上线前最后一轮验证、产品经理验收、配置核对 | 等待 1 分钟 | 开发团队 + 产品 |
| **Production** | 生产环境 | 面向真实用户的服务 | 审批 + 等待 | 最终用户 |

三种环境的保护规则呈**递进式严格**：

```
QA 环境          Staging 环境          Production 环境
  │                  │                      │
  │  无限制          │  等待 1 分钟          │  审批 + 等待
  │                  │                      │
  ▼                  ▼                      ▼
┌────────┐      ┌──────────┐          ┌──────────────┐
│  直接   │ ───▶ │  缓冲期   │ ──────▶ │  人工审批门   │
│  部署   │      │  最后核对 │          │  + 缓冲期    │
└────────┘      └──────────┘          └──────────────┘
 风险：低          风险：中               风险：高
```

> 💡 **核心洞见**：环境的严格程度与"犯错成本"成正比。QA 环境出错只需要回滚代码，成本几乎为零；Production 环境出错影响真实用户，成本可能是收入损失加信任崩塌。因此保护规则的递进设计不是为了制造流程负担，而是让**成本高的操作自然需要更严格的审批**。

---

### 7.3 GitHub Environments 配置入口

#### 🧠 直观理解

GitHub Environments 是 GitHub 在仓库级别提供的"环境管理面板"。它让你在一个地方集中管理：谁能部署、部署前等多久、用哪些密钥和配置——所有与环境部署相关的策略都汇聚于此。

#### 📖 详细解释

**入口路径**：

```
GitHub 仓库主页
  │
  └── Settings 标签页
        │
        └── 左侧菜单 → Environments
              │
              └── New environment 按钮
```

**操作流程**：

1. 进入目标仓库，点击顶部 **Settings** 标签页。
2. 在左侧菜单中找到 **Environments** 选项（位于 "Code and automation" 分组下）。
3. 点击右上角 **New environment** 按钮。
4. 在弹出的对话框中输入环境名称（如 `QA`），点击 **Configure environment** 进入详细配置页。

每个环境的配置页面可配置三类内容：

| 配置项 | 作用 | 示例 |
|---|---|---|
| **Protection rules** | 定义部署到此环境必须满足的前提条件 | 需要审批、等待 N 分钟 |
| **Environment secrets** | 加密存储敏感配置（写入后不可查看明文） | SSH 私钥、数据库密码、API Token |
| **Environment variables** | 明文存储非敏感配置 | 服务器 IP、端口号、环境标识 |

---

### 7.4 QA 环境 — 测试环境配置

#### QA 环境的特点

QA（Quality Assurance）环境是开发者最频繁部署的环境。每次提交代码、运行自动化测试、或手动验证功能时，都会往 QA 环境推送。因为频率高且受众只有开发团队，QA 环境的保护规则通常设为**最宽松**：无需审批，无需等待。

#### 配置步骤

**Step 1：创建环境**

在 Environments 页面点击 **New environment**，输入名称 `QA`，点击 **Configure environment**。

**Step 2：Protection Rules（保护规则）**

QA 环境不加任何保护规则。页面上两个选项均不勾选：

- Required reviewers：不勾选（不需要审批）
- Wait timer：不勾选（不需要等待）

**Step 3：管理员豁免选项**

页面底部有一个复选框：

> ☑️ **Allow administrators to bypass configured protection rules**

翻译为：允许管理员绕过已配置的保护规则。由于 QA 环境本身没有任何限制规则，这个选项的实际影响不大，但老师建议**保持勾选**——在后续更严格的环境中，管理员豁免是一个实用的"紧急逃生通道"。

**Step 4：分支部署限制（可选）**

可以在此处约定哪些分支可以部署到 QA 环境。例如，选择 `qa` 分支只能部署到 QA 环境：

```
Deployment branches: Selected branches → 添加规则
  └── Branch name pattern: qa
```

这一限制确保其他分支（如 `main` 或 `release`）的代码不会被误部署到 QA 环境。

> ⚠️ **注意事项**：分支部署限制是"可选的约束条件"，用于防止误部署。如果暂不确定分支策略，可以先不填——老师在本节中就暂时跳过了这一步。

**Step 5：添加 Environment Secrets 和 Variables**

点击 **Add Secret**，填入 QA 环境的数据库密码或 SSH 私钥：

| 字段 | 值示例 | 说明 |
|---|---|---|
| Name | `SSH_PRIVATE_KEY` | 连接 QA 服务器的 SSH 私钥 |
| Value | `-----BEGIN RSA PRIVATE KEY-----...` | 密钥内容，保存后不可见 |

点击 **Add variable**，填入 QA 环境的服务器地址：

| 字段 | 值示例 | 说明 |
|---|---|---|
| Name | `SERVER_IP` | 服务器 IP 地址 |
| Value | `192.168.1.101` | QA 服务器内网 IP |

> 💡 **核心洞见**：每个环境都有各自独立的 Secrets 和 Variables 命名空间。同一个变量名 `SERVER_IP` 在 QA、Staging、Production 三个环境中可以分别填不同的值。Action 运行时，GitHub 会根据 `environment` 字段自动注入当前环境的变量值，无需手动判断。

---

### 7.5 Staging 环境 — 沙箱/预发布环境配置

#### Staging 环境的特点

Staging（老师也称为 STG 或沙箱环境）是生产环境的"镜像"。它模拟了生产环境的配置、数据和流量模式，但面向的是内部团队而非真实用户。Staging 是上线前最后一道防线：在此环境中发现的任何问题，都应该在生产环境部署前修复。

> 🔗 **关联知识**：Staging 环境与 QA 环境的核心区别在于**配置保真度**——QA 环境可以简化（如用 mock 服务），但 Staging 环境必须尽可能与生产环境一致，包括数据库版本、操作系统版本、第三方服务端点等。

#### Wait Timer 详解

Staging 环境的标志性保护规则是 **Wait timer（等待定时器）**：

```
配置：Wait timer = 1 minute

效果：当 Action 触发 Staging 环境部署时，会先挂起 1 分钟，
      在这 1 分钟内部署处于"等待中"状态，不会立即执行。
```

**等待 1 分钟的意义**：

| 时间窗口中的操作 | 受益角色 |
|---|---|
| 检查最近一次代码提交的 diff | 开发者 |
| 确认配置文件中的环境变量是否正确 | 运维 / DevOps |
| 发现上一个环境遗漏的问题，紧急取消部署 | 任何人 |
| 通知产品经理准备验收 | 团队协作 |

> ❓ **常见疑问**："1 分钟能干什么？为什么不设 5 分钟或更长？"
>
> **回答**：1 分钟不是用来做深度检查的，而是提供一个**"取消部署的最后机会"**。当你点击部署按钮的那一刻，如果你突然想起"哦糟了，配置文件忘了改"，这 1 分钟的缓冲期就是你的救命稻草。更长时间的等待反而会降低部署效率——Staging 毕竟不是生产环境，出错代价可控。

#### 配置步骤

**Step 1：创建环境**

New environment → 名称输入 `stg`（或 `staging`）→ Configure environment。

**Step 2：Protection Rules**

只勾选 **Wait timer**，并设置为 **1 分钟**：

```
☑️ Wait timer
   Wait: 1 minute(s)
```

勾选后**务必点击页面底部的 Save protection rules 按钮**保存——这是老师特别强调的操作习惯。

**Step 3：添加 Secrets 和 Variables**

与 QA 环境同理，添加 Staging 环境自己的 `SSH_PRIVATE_KEY` 和 `SERVER_IP`，值是 Staging 服务器对应的密钥和地址。

---

### 7.6 Production 环境 — 生产环境配置

#### Production 环境的特点

Production 环境面向真实用户，是所有环境中最严加保护的。任何对 Production 的变更都必须经过**人工审批（Required reviewers）**，这是不可绕过的强制要求。

#### Required Reviewers 详解

Required reviewers（必需审批人）是 GitHub Environments 提供的最强保护规则：

```
配置：Required reviewers = up to 6 GitHub users

效果：当 Action 部署到 Production 环境时，部署 Job 自动暂停，
      等待所有指定的审批人在 GitHub UI 上点击"批准"后，
      Wait timer 计时器才开始倒计时。
```

**审批流程时序**：

```
Action 触发部署
    │
    ▼
┌───────────────────┐
│ 检查 Required       │  ← 必须有审批人
│ Reviewers 规则      │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ 部署 Job 暂停，      │  ← 审批人收到通知，
│ 等待审批            │     在 GitHub 上点击 Approve
└────────┬──────────┘
         │ (审批通过)
         ▼
┌───────────────────┐
│ Wait timer 倒计时   │  ← 如配置了 1 分钟等待
│ (1 minute)         │
└────────┬──────────┘
         │ (等待结束)
         ▼
┌───────────────────┐
│ 开始执行部署        │  ← 实际部署脚本开始运行
└───────────────────┘
```

> ⚠️ **注意事项**：审批人是按 GitHub 用户名指定的，格式为 `@用户名`。老师在示例中填写了自己的 GitHub 用户名。在实际团队中，审批人通常设置为 Tech Lead、项目经理或 DevOps 负责人。**最多可以指定 6 个审批人**——只要其中任何一个人批准，审批即可通过（不是全员同意的逻辑，是任一人批准即可）。

#### 配置步骤

**Step 1：创建环境**

New environment → 名称输入 `production` → Configure environment。

**Step 2：Protection Rules**

勾选两项规则：

```
☑️ Required reviewers
   Reviewer: tag sharp (GitHub 用户名，最多 6 人)

☑️ Wait timer
   Wait: 1 minute(s)
```

**Step 3：管理员豁免**

保持勾选 **Allow administrators to bypass configured protection rules**。这在紧急线上故障修复（hotfix）时有实际价值——如果审批人正好不在线，管理员可以绕过程序直接部署修复。

**Step 4：添加 Secrets 和 Variables**

添加 Production 环境的 `SSH_PRIVATE_KEY` 和 `SERVER_IP`，值为线上服务器的真实密钥和 IP。

---

### 7.7 Protection Rules 综合对比

将三种环境下的保护规则配置汇总为一张对比表：

| 环境 | Required Reviewers | Wait Timer | 管理员豁免 | 部署分支限制（推荐） |
|---|---|---|---|---|
| **QA** | 无 | 无 | 勾选 | `qa` 分支 |
| **Staging (STG)** | 无 | 1 分钟 | 勾选 | `main` 分支 |
| **Production** | 至少 1 人，最多 6 人 | 1 分钟 | 勾选 | `release` 分支 |

#### 三种规则的递进关系

```
           QA                  Staging               Production
           │                      │                       │
           │ 无审批                │ 无审批                 │ 有审批
           │ 无等待                │ ⏱️ 等 1 分钟           │ ⏱️ 等 1 分钟
           │                      │                       │
           ▼                      ▼                       ▼
      ┌─────────┐           ┌───────────┐           ┌─────────────┐
      │ 一键部署  │    ───▶   │ 缓冲部署   │    ───▶  │ 审批+缓冲部署 │
      │ 零门槛   │           │ 有反悔机会  │           │ 有问责机制   │
      └─────────┘           └───────────┘           └─────────────┘
```

> 💡 **核心洞见**：这个递进设计映射了软件工程中的一个根本原则——**权力越大（影响范围越广），流程约束越强**。部署 QA 不需要任何人同意，因为影响范围可控；部署 Production 需要审批，因为影响的是所有用户。这不是官僚流程，而是技术治理。

---

### 7.8 Environment Secrets vs Environment Variables

#### 🧠 直观理解

如果把环境配置比作你的家门，那么 **Secrets** 就是钥匙（绝对不能给别人看），**Variables** 就是门牌号（可以公开，但要写对）。两者都是环境的配置数据，区别在于**安全等级与读取方式**。

#### 📖 详细解释

**Environment Secrets（加密环境密钥）**：

- 写入后**不可再次查看明文**——GitHub 界面上只能看到密钥名称和最后修改时间，无法看到密钥值。
- 只能通过**更新操作**来修改值（覆盖写入），旧值永久不可恢复。
- 在 Action 中通过 `${{ secrets.密钥名 }}` 语法引用。
- 典型用途：SSH 私钥、数据库密码、第三方 API Token、TLS 证书。

**Environment Variables（环境变量）**：

- 写入后**可以随时查看明文**，任何人都能在环境配置页看到变量的值。
- 可以直接修改，也可以删除。
- 在 Action 中通过 `${{ vars.变量名 }}` 语法引用。
- 典型用途：服务器 IP 地址、端口号、环境标识（`dev`/`stg`/`prod`）、日志级别。

#### 对比表

| 维度 | Environment Secrets | Environment Variables |
|---|---|---|
| **安全性** | 高（加密存储，不可回读） | 低（明文存储，可任意查看） |
| **可读性** | 仅写入，不可查看 | 随时可查看、可修改 |
| **Action 引用语法** | `${{ secrets.NAME }}` | `${{ vars.NAME }}` |
| **典型数据** | SSH 私钥、密码、Token | IP 地址、端口、环境标识 |
| **修改方式** | 覆盖写入（旧值不可恢复） | 直接编辑 |
| **日志安全** | GitHub 自动屏蔽日志中的 secrets 值 | 变量值可能出现在日志中 |

> ⚠️ **注意事项**：老师特别演示了一个关键操作习惯——SSH 私钥（`SSH_PRIVATE_KEY`）作为 Secret 存储，服务器 IP 地址（`SERVER_IP`）作为 Variable 存储。**绝不要把密码或密钥作为 Variable 保存**，因为 Variable 是明文且会出现在 Action 日志输出中，这将造成严重的安全事故。

> ❓ **常见误解**："Variable 也能存密码，反正别人看不到我的仓库 Settings 页面。"
>
> **纠正**：Variable 的值不仅会出现在 Settings 页面，还可能被 Action 的 `echo` 或日志语句意外输出到公开的 CI 日志中。GitHub Actions 的日志默认对仓库协作者可见，甚至对公开仓库的任何人可见。**Secrets 在设计层面就防止了日志泄露**——GitHub 会在日志输出中自动将 Secrets 的值替换为 `***`，而 Variable 不会受到此保护。

#### 每个环境的独立配置示意

```
QA 环境
  ├── Secret:  SSH_PRIVATE_KEY = "QA 服务器密钥"
  └── Variable: SERVER_IP = "192.168.1.101"

Staging 环境
  ├── Secret:  SSH_PRIVATE_KEY = "Staging 服务器密钥"
  └── Variable: SERVER_IP = "192.168.1.102"

Production 环境
  ├── Secret:  SSH_PRIVATE_KEY = "Production 服务器密钥"
  └── Variable: SERVER_IP = "203.0.113.50"
```

同一个变量名（`SERVER_IP`）在不同环境中取不同的值，Action 在运行时根据当前部署的目标环境自动选择对应的值。这意味着你的部署脚本**不需要写任何 if-else 判断环境**——GitHub Environments 在源头就帮你做了隔离。

---

### 7.9 环境与分支的映射关系

#### 🧠 直观理解

分支 = 代码的"版本线"，环境 = 代码的"运行场所"。分支部署限制规则在两者之间建立了**一对一的绑定关系**：特定分支的代码只能部署到特定环境，防止开发分支的未完成代码误入生产环境。

#### 📖 详细解释

#### 分支部署限制（Deployment branches）

每个环境配置页中都有一个 **Deployment branches** 选项，可以设定允许部署到此环境的分支：

```
Deployment branches:
  ○ All branches           → 所有分支都可以部署到此环境
  ● Selected branches      → 仅指定的分支可以部署到此环境
      └── Add deployment branch rule
            └── Branch name pattern: [分支名或通配符]
```

#### 推荐的三环境分支映射

| 环境 | 推荐绑定的分支 | 理由 |
|---|---|---|
| **QA** | `qa` 分支 | QA 分支上的功能代码对应 QA 环境测试 |
| **Staging** | `main` 分支 | main 是集成了所有已测功能的稳定分支，应在 Staging 做最后验证 |
| **Production** | `release` 分支 | release 是专门用于发布的快照分支，与生产环境一一对应 |

#### 映射规则的执行机制

当 Action workflow 中指定了 `environment: production`，但触发 workflow 的分支不是 `release` 时，部署 job 会直接失败：

```
Error: Deployment to environment "production" is blocked.
Branch "main" is not allowed to deploy to this environment.
```

> ⚠️ **注意事项**：分支部署限制是**硬性拦截**，不是警告。如果你的 workflow 配置中环境与分支不匹配，job 会直接报错中止。因此在配置 workflow 文件时，`environment` 字段和触发分支必须在逻辑上一致。

---

### 7.10 三个环境创建完成后的验证清单

完成 QA、Staging、Production 三个环境的创建后，可以用以下清单逐一核验配置是否正确：

| 检查项 | QA | Staging | Production |
|---|---|---|---|
| Required reviewers | 无 ✓ | 无 ✓ | 至少 1 人 ✓ |
| Wait timer | 无 ✓ | 1 分钟 ✓ | 1 分钟 ✓ |
| Admin bypass | 勾选 ✓ | 勾选 ✓ | 勾选 ✓ |
| Secret: SSH_PRIVATE_KEY | 已添加 ✓ | 已添加 ✓ | 已添加 ✓ |
| Variable: SERVER_IP | 已添加 ✓ | 已添加 ✓ | 已添加 ✓ |

三个环境创建完成后，在 Environments 列表中应能看到三个条目，点击任意一个可查看和修改其配置。在下一模块中，我们将编写 GitHub Actions workflow，让这些环境在自动化部署流水线中真正运转起来。

> 🔗 **延伸阅读**：本模块创建的三个环境将在 [第 X 章：多环境部署 — 并行 Job 工作流与审批流演示] 中通过 GitHub Actions workflow 引用和使用

## 八、多环境部署 — 并行 Job 工作流与审批流演示

### 8.1 实操概览

#### 🎯 本节目标

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 编写关联多环境的 GitHub Actions Workflow YAML 文件
> - [ ] 理解 `environment` 字段的作用机制与配置要点
> - [ ] 区分并行 Job 与串行 Job 的写法差异
> - [ ] 观察三种环境保护规则（无规则、Wait timer、Required reviewers）的实际执行效果
> - [ ] 完整操作一次从手动触发到审批通过的 production 部署审批流程

#### 🏗️ 前置准备

在开始本节实操之前，请确保以下条件已满足：

1. **环境已创建**：在仓库 Settings → Environments 中已创建三个环境：

   | 环境名称 | 保护规则 | 用途 |
   |---|---|---|
   | `QA` | 无保护规则 | 测试环境，快速部署 |
   | `stage` | Wait timer = 1 分钟 | 沙箱/预发环境 |
   | `production` | Wait timer = 1 分钟 + Required reviewers | 生产环境，严格管控 |

   > 🔗 **前置知识**：环境创建过程详见 [第七章：多环境配置与保护规则](#七多环境部署--环境配置与保护规则)

2. **仓库权限**：当前仓库已启用 GitHub Actions，你具有仓库的 Write 权限（触发 Workflow）和 Admin 权限（审批 deployment）。

3. **分支基础**：仓库中已有一个可用分支（如 `main`），Workflow 文件将放在该分支的 `.github/workflows/` 目录下。

> ⚠️ **注意事项**：本节后续要写的 `environment:` 值必须与 Settings → Environments 中创建的名称**严格一致**（包括大小写）。名称不匹配会导致 Workflow 运行时报错：`Environment "xxx" not found`。

---

### 8.2 Workflow YAML 文件完整展示

#### 💻 Step 1: 创建 Workflow 文件

在仓库根目录下创建 `.github/workflows/multi-env-deploy.yml` 文件。

```yaml
# 文件名: .github/workflows/multi-env-deploy.yml
# 功能: 多环境并行部署演示 — 展示不同环境保护规则的执行效果

name: Multi-Environment Deployment

# 触发方式: 手动触发（workflow_dispatch）
on:
  workflow_dispatch:

jobs:
  # ============================================================
  # Job 1: 部署到 QA 环境 — 关联环境 "QA"（无保护规则，立即执行）
  # ============================================================
  deploy-qa:
    runs-on: ubuntu-latest
    environment: QA
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to QA
        run: |
          echo "========================================="
          echo "  [QA] 正在部署到 QA 环境..."
          echo "  [QA] 保护规则: 无 — 立即执行"
          echo "========================================="
          sleep 3

  # ============================================================
  # Job 2: 部署到 stage 环境 — 关联环境 "stage"（Wait timer: 1 分钟）
  # ============================================================
  deploy-stage:
    runs-on: ubuntu-latest
    environment: stage
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to Stage
        run: |
          echo "========================================="
          echo "  [STAGE] 正在部署到 stage 环境..."
          echo "  [STAGE] 保护规则: Wait timer = 1 分钟"
          echo "========================================="
          sleep 3

  # ============================================================
  # Job 3: 部署到 production 环境 — 关联环境 "production"
  #         保护规则: Wait timer 1 分钟 + Required reviewers（审批）
  # ============================================================
  deploy-production:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to Production
        run: |
          echo "========================================="
          echo "  [PROD] 正在部署到 production 环境..."
          echo "  [PROD] 保护规则: Wait timer + 审批"
          echo "========================================="
          sleep 3
```

##### 行级解析表

| 行号范围 | 关键代码 | 说明 |
|---|---|---|
| 6-7 | `on: workflow_dispatch:` | 手动触发方式，需要在 Actions 页面点击按钮触发，而非 push/PR 自动触发 |
| 12 | `deploy-qa:` | Job 的唯一标识符，三个 Job ID 各不相同 |
| 13 | `runs-on: ubuntu-latest` | 每个 Job 独立指定运行器，三个 Job 都使用 ubuntu 最新版虚拟机 |
| 14 | `environment: QA` | **核心字段**：将此 Job 关联到 Settings 中名为 `QA` 的环境 |
| 25 | `deploy-stage:` | 第二个 Job，与 QA Job 平级（无缩进关系） |
| 27 | `environment: stage` | 关联到 `stage` 环境，该环境配置了 Wait timer = 1 分钟 |
| 38 | `deploy-production:` | 第三个 Job，同样与上面两个 Job 平级 |
| 40 | `environment: production` | 关联到 `production` 环境，该环境配置了 Wait timer + Required reviewers |
| 15-23 | `steps:` 数组 | 每个 Job 的实际执行步骤，此处为演示目的，仅输出日志并 sleep 3 秒模拟部署 |

> 💡 **核心洞见**：在这个 YAML 文件中，三个 Job 都在 `jobs:` 下的同一层级，彼此之间没有任何 `needs` 字段。这表示它们是**并行关系**——GitHub Actions 调度器会同时启动这三个 Job。但"启动"不等于"立即执行"——每个 Job 还要通过各自关联环境的保护规则检查。

---

### 8.3 `environment` 字段详解

#### 🧠 直观理解

`environment` 字段就像给每个 Job 贴上了一个"环境标签"。当 GitHub Actions 准备执行一个 Job 时，它会根据这个标签去 Settings → Environments 中查找对应的环境配置，然后**强制执行该环境的所有规则**。

可以类比为：三个快递员（三个 Job）同时出发送快递，但各自的目的地（QA / stage / production）有不同的门禁规则——有的门直接开着（QA），有的需要等保安确认（stage），有的需要经理签字才能进（production）。

#### 📖 详细解释

`environment:` 字段将 Job 与目标部署环境关联起来，赋予 Job 三个层面的能力：

| 层面 | 作用 | 本 Workflow 中的体现 |
|---|---|---|
| **保护规则（Protection Rules）** | 部署前必须满足的约束，满足后 Job 才能真正开始执行步骤 | QA：无规则 → 立即执行 / stage：等 1 分钟 / production：等 1 分钟 + 审批 |
| **环境密钥（Environment Secrets）** | 此环境专属的加密变量，用于存储敏感信息（如数据库密码、SSH 私钥） | 见 [下一章：环境专属密钥与变量实战] |
| **环境变量（Environment Variables）** | 此环境专属的普通变量（如服务器地址、API 端点） | 见 [下一章：环境专属密钥与变量实战] |

##### 工作机制推导链

```
🔗 推导链：environment 字段的工作机制

起点: Job 被 GitHub Actions 调度器选中，准备启动
  │
  ├── 第1步: 读取 Job 定义中的 environment 字段值（如 "production"）
  │   为什么？GitHub Actions 需要知道这个 Job 关联哪个环境
  │
  ├── 第2步: 去仓库 Settings → Environments 中查找名为 "production" 的环境配置
  │   为什么？每个环境有独立的保护规则、密钥和变量，必须精确匹配
  │
  ├── 第3步: 检查该环境的所有保护规则是否满足
  │   为什么？保护规则是安全管控的核心：Wait timer 允许团队在部署窗口内做最后检查；
  │          Required reviewers 确保关键环境（如生产）的每次部署都有人为确认
  │
  ├── 第4步: 规则全部满足后，将该环境的 Secrets 和 Variables 注入 Job 的运行上下文
  │   为什么？不同环境需要不同的配置（如不同数据库地址），必须注入正确的值
  │
  └── 结论: Job 开始执行 steps 中定义的实际部署步骤
```

> ⚠️ **注意事项**：`environment:` 后面填写的名称必须与 Settings → Environments 中已创建的环境名称**一字不差**（区分大小写）。例如，Settings 中创建的是 `production`（全小写），但 YAML 中写的是 `Production`（首字母大写），则运行时会报错 `Environment "Production" not found`。名称不匹配是新手最容易犯的错误。

---

### 8.4 三个 Job 的并行执行机制

#### 📖 并行与串行的区别

在 GitHub Actions 中，Job 之间的执行顺序由 `needs` 关键字决定：

| 写法 | 执行关系 | 适用场景 |
|---|---|---|
| 无 `needs` 字段 | **并行**：所有 Job 同时启动 | 部署到不同环境、独立构建任务 |
| `needs: [job-a]` | **串行**：当前 Job 在 `job-a` 完成后才启动 | 构建 → 测试 → 部署的流水线 |

本 Workflow 的三个 Job 均无 `needs` 字段，因此它们会**同时被调度器启动**。但启动后各自的执行进度由环境规则决定——这就出现了"三个 Job 同时出发、但到达终点的时间各不相同"的效果。

#### 🔄 并行执行时序图

以下 ASCII 时序图展示了三个并行 Job 从触发到完成的完整过程：

```
时间轴 ─────────────────────────────────────────────────────────────────────────────▶
        触发时刻 (0:00)           ~1:00                        审批通过 (手动，不固定)


┌─ Job: deploy-qa（关联环境 QA，保护规则: 无）─────────────────────────────────────────┐
│                                                                                     │
│  状态:  [Queued] ──▶ [In Progress] ──▶ [Completed ✅]                                │
│          启动即执行          执行步骤          ~3秒后完成                               │
│                                                                                     │
│  QA 无任何保护规则约束，Job 启动后立即开始执行部署步骤，是三个 Job 中最先完成的。         │
└─────────────────────────────────────────────────────────────────────────────────────┘


┌─ Job: deploy-stage（关联环境 stage，保护规则: Wait timer = 1 分钟）────────────────────┐
│                                                                                     │
│  状态:  [Queued] ──▶ [⏳ Waiting...] ──▶ [In Progress] ──▶ [Completed ✅]             │
│          启动           等待 1 分钟         执行步骤            ~1分03秒后完成           │
│                        │                                                             │
│                        └── Wait timer 倒计时期间，团队可以检查代码和配置                 │
│                            倒计时结束后，Job 自动开始执行                               │
│                                                                                     │
│  stage 环境配置了 Wait timer = 1 分钟。Job 启动后进入等待状态，计时结束后自动执行。       │
└─────────────────────────────────────────────────────────────────────────────────────┘


┌─ Job: deploy-production（关联环境 production，保护规则: Wait timer + Required reviewers）┐
│                                                                                     │
│  状态:  [Queued] ──▶ [⏳ Waiting...] ──▶ [⏸️ Waiting for Review] ──▶ [In Progress]    │
│          启动          等待 1 分钟           等待审批（手动）              执行步骤       │
│                                             │                                       │
│                                             ├── 审批者点击 "Review deployments"      │
│                                             ├── 勾选确认框                          │
│                                             └── 点击 "Approve and deploy"           │
│                                                                                     │
│                                    ──▶ [Completed ✅]                                │
│                                        ~审批后 3 秒完成                               │
│                                                                                     │
│  production 环境同时配置了两种保护规则。Wait timer 结束后，还需人工审批才能执行。         │
│  这是最严格的管控级别——既有时间窗口供检查，又有人为确认环节。                            │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

##### 观察要点

从时序图中可以清晰看到三个关键时间节点：

1. **0:00 时刻**：三个 Job 同时被调度器启动。QA 直接进入执行状态。
2. **~1:00 时刻**：stage 的 Wait timer 到期，开始执行。production 的 Wait timer 也到期，但触发审批等待。
3. **审批通过后**：production 开始执行，最终三个 Job 全部完成。

> 💡 **核心洞见**：并行 Job 并不意味着它们会同时完成。"并行"说的是调度层面的同时启动，而每个 Job 的实际执行时间受其环境规则的独立控制。这种设计让同一个 Workflow 中不同环境可以有不同的安全管控级别。

---

### 8.5 实际执行演示

以下按步骤还原老师在视频中的完整操作过程。

#### Step 2: 手动触发 Workflow

1. 将 `multi-env-deploy.yml` 文件推送到 GitHub 仓库（默认分支如 `main`）。
2. 打开仓库页面，点击顶部导航栏的 **Actions** 选项卡。
3. 在左侧 Workflow 列表中找到 **Multi-Environment Deployment**。
4. 点击右侧的 **Run workflow** 下拉按钮。
5. 选择分支（如 `main`），点击绿色的 **Run workflow** 按钮。

```
┌──────────────────────────────────────────────────┐
│  Actions 页面                                     │
│                                                  │
│  ┌──────────────────────────────────────────┐    │
│  │  Multi-Environment Deployment            │    │
│  │  ┌────────────────────────────────────┐  │    │
│  │  │  Run workflow  ▼                   │  │    │
│  │  │  ┌─────────────────────────────┐   │  │    │
│  │  │  │ Branch: main            ▾  │   │  │    │
│  │  │  │                           │   │  │    │
│  │  │  │  [Run workflow]  (绿色按钮) │   │  │    │
│  │  │  └─────────────────────────────┘   │  │    │
│  │  └────────────────────────────────────┘  │    │
│  └──────────────────────────────────────────┘    │
└──────────────────────────────────────────────────┘
```

6. 刷新页面，列表中会出现一个新的 Workflow run，正在执行中。

#### Step 3: QA Job — 无等待，立即完成

进入该 Workflow run 的详情页，观察三个 Job 的执行状态：

```
┌──────────────────────────────────────────────────────────────┐
│  Workflow Run: Multi-Environment Deployment                  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  deploy-qa                    ✅  completed in 5s       │  │
│  │  关联环境: QA | 保护规则: 无                              │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  deploy-stage                ⏳  waiting...             │  │
│  │  关联环境: stage | 保护规则: Wait timer (1m)             │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  deploy-production           ⏳  waiting...             │  │
│  │  关联环境: production | 保护规则: timer + reviewers       │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

QA Job 的状态变化极快：`Queued → In Progress → Completed`，几秒钟内即完成。因为 QA 环境未配置任何保护规则，Job 启动后直接进入执行阶段。

#### Step 4: STG Job — 等待 1 分钟后自动执行

在 QA 完成后的约 1 分钟内，stage Job 和 production Job 都处于 `Waiting` 状态。

- **stage Job** 显示 `Waiting for the 1m timer to elapse`（等待 1 分钟计时器结束）。
- **production Job** 同样在等待计时器结束，但计时结束后还需要额外等待审批。

当 1 分钟计时到期后：

- stage Job 状态自动从 `Waiting` 变为 `In Progress`，开始执行部署步骤。
- production Job 的 Wait timer 也同时到期，但状态变为 `Waiting for review`（等待审批）。

> 💡 **核心洞见**：Wait timer 的 1 分钟并非无意义的等待。在生产实践中，这 1 分钟是团队进行最后检查的**缓冲窗口**——检查代码是否有遗漏、配置文件是否正确、依赖是否就绪。如果发现问题，可以在部署真正开始前取消 Workflow run，避免将有问题的代码推送到 stage 或 production 环境。

#### Step 5: Production Job — 审批流交互详解

这是整个演示中最关键的环节。production 环境配置了 Required reviewers，必须有人为审批才能继续。

##### 审批流程逐步详解

**步骤 1：发现待审批的 Job**

在 Workflow run 详情页中，production Job 的状态显示为：

```
deploy-production    ⏸️  Waiting for review
```

状态旁会出现一个提示框，告知需要审批。

**步骤 2：点击 Review deployments**

在 Workflow run 页面中，会出现一个黄色的提示区域或按钮（标注为 **Review deployments**），点击进入审批界面。

**步骤 3：审批确认对话框**

点击后弹出一个审批对话框，界面结构如下：

```
┌──────────────────────────────────────────────────────┐
│  Review pending deployments                          │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │  production                                    │  │
│  │                                                │  │
│  │  ☐ Approve deployment to production?           │  │
│  │    （勾选此框以确认批准部署到生产环境）              │  │
│  │                                                │  │
│  │  Comment (optional):                           │  │
│  │  ┌──────────────────────────────────────────┐  │  │
│  │  │  [可选的审批备注，如"已验证，可以上线"]     │  │  │
│  │  └──────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  [Approve and deploy]  (绿色审批按钮)                  │
└──────────────────────────────────────────────────────┘
```

**步骤 4：勾选确认框**

在审批对话框中，勾选 `Approve deployment to production?` 前的复选框。这一步是显式的确认动作——表示审批者已经审查并同意此次部署。

**步骤 5：点击 Approve and deploy**

勾选后，点击绿色的 **Approve and deploy** 按钮。此操作将通知 GitHub Actions 审批已通过、production 环境的保护规则已满足。

**步骤 6：部署开始**

审批通过后，production Job 的状态立即从 `Waiting for review` 变为 `In Progress`，开始执行部署步骤。几秒后，production Job 也显示 `Completed`。

##### 审批流程完整状态变化链

```
Queued
  │
  ▼
Waiting (Wait timer 倒计时中...)
  │
  ▼
Waiting for Review  ◀── Wait timer 到期，触发审批等待
  │
  │  审批者操作:
  │    1. 点击 "Review deployments"
  │    2. 勾选确认框
  │    3. 点击 "Approve and deploy"
  │
  ▼
In Progress  ◀── 审批通过，开始执行
  │
  ▼
Completed ✅
```

> ⚠️ **注意事项**：审批操作在实际团队中通常由**具有环境审批权限的角色**执行（如 Tech Lead、项目经理、运维负责人），而非开发者本人。老师在演示中扮演审批者角色是为了完整展示流程。在实际项目里，开发者触发 Workflow 后，需要等待审批者操作才能完成 production 部署。

---

### 8.6 验证结果

最终，Workflow run 详情页中三个 Job 全部显示为 `Completed`：

```
┌──────────────────────────────────────────────────────────────┐
│  Workflow Run: Multi-Environment Deployment  ✅  Success     │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  deploy-qa                    ✅  completed in 5s       │  │
│  │  完成方式: 启动即执行，无等待                              │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  deploy-stage                ✅  completed in 1m 8s     │  │
│  │  完成方式: Wait timer 到期后自动执行                       │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  deploy-production           ✅  completed in 2m 15s    │  │
│  │  完成方式: Wait timer + 人工审批通过后执行                 │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

可以点击每个 Job 展开查看其执行日志，确认部署步骤（`echo` 输出和 `sleep 3`）已成功执行。

---

### 8.7 三种环境保护规则的执行效果对比

下表从多个维度对比三种环境在本 Workflow 中的表现差异：

| 对比维度 | QA 环境 | stage 环境 | production 环境 |
|---|---|---|---|
| **保护规则** | 无 | Wait timer = 1 分钟 | Wait timer = 1 分钟 + Required reviewers |
| **Job 启动后行为** | 立即执行 | 等待 1 分钟后自动执行 | 等待 1 分钟 + 等待人工审批 |
| **是否需要人工干预** | 否 | 否（自动） | **是**（必须有人点击 Approve） |
| **典型耗时** | ~5 秒 | ~1 分 5 秒 | ~2 分钟起（取决于审批者响应速度） |
| **回滚成本** | 极低（测试环境随便改） | 中（沙箱环境，可能影响联调） | 极高（直接影响线上用户） |
| **适用团队角色** | 所有开发者 | 开发者（有代码审查后的部署） | Tech Lead / 运维（需审批权限） |
| **Wait timer 的业务价值** | 无（不需要） | 1 分钟窗口供团队检查代码和配置 | 1 分钟窗口 + 审批确认的双重保障 |
| **安全管控级别** | 低 | 中 | **高** |

##### 审批通过后的状态对比

```
三种环境最终都成功完成部署，但完成路径截然不同:

  QA:       [触发] ──────────────▶ [完成]      （一路绿灯）
  stage:    [触发] ──⏳ 1 分钟──▶ [完成]       （有红绿灯但自动放行）
  production: [触发] ──⏳ 1 分钟──🛑 审批 ──▶ [完成]  （红绿灯 + 人工放行）
```

---

### 8.8 关键要点与排错指南

#### 💡 核心要点

1. **并行 Job 的实现**：Job 之间不写 `needs` 字段即为并行关系。三个 Job 会同时被调度器启动，但各自独立受环境规则约束。
2. **`environment` 字段的作用**：将 Job 与环境配置绑定，强制应用保护规则、注入环境专属的密钥和变量。
3. **保护规则的层级差异**：同一个 Workflow 中，不同环境可以有不同的保护级别——QA 无限制（快速迭代）、stage 有定时缓冲（检查窗口）、production 有审批机制（安全兜底）。
4. **审批是最后一道防线**：production 部署前的审批不是形式主义——它确保每次线上变更都有明确的责任人和确认记录。

#### 🐛 常见坑

**坑 1：环境名称不匹配导致 Workflow 运行失败**

**🚨 报错信息**

```
Error: Environment "Staging" not found. Available environments: QA, stage, production
```

**🔍 原因分析**

YAML 中 `environment: Staging` 与 Settings 中创建的环境名称 `stage` 不一致。GitHub Actions 的环境名称匹配是大小写敏感且完全精确的——`Staging`、`STAGE`、`stage` 被视为三个不同的环境。

**✅ 正确写法**

```yaml
# ❌ 错误：Settings 中创建的是 "stage"，但 YAML 写了 "Staging"
environment: Staging

# ✅ 正确：与 Settings 中创建的名称完全一致
environment: stage
```

**📝 经验总结**

在编写 Workflow 前，先到 Settings → Environments 中确认已创建环境的确切名称（包括大小写），再填入 `environment:` 字段。养成"先查看，后填写"的习惯。

---

**坑 2：忘记配置 Required reviewers 却期待审批流出现**

**🚨 现象**

production Job 的 Wait timer 到期后直接开始执行，没有出现 `Waiting for review` 状态。

**🔍 原因分析**

在 Settings → Environments → production 中，虽然配置了 Wait timer，但未添加 Required reviewers（审批人列表为空或未勾选 Required reviewers 选项）。审批流只有当 Required reviewers 列表中至少有一名审批人时才会生效。

**✅ 正确配置**

1. 进入 Settings → Environments → production。
2. 在 Protection rules 区域，确保 **Required reviewers** 已勾选。
3. 至少添加一名审批人（输入 GitHub 用户名，如 `Dinos0717`）。
4. 保存配置。

**📝 经验总结**

Wait timer 和 Required reviewers 是两种独立的保护规则，可以单独使用或组合使用。如果需要审批流，必须显式配置 Required reviewers；只配置 Wait timer 不会触发审批。

---

> 🔗 **延伸阅读**：下一章 [第九部分：环境专属密钥与变量实战]将展示如何利用每个环境的 `environment secrets` 和 `environment variables` 实现不同环境使用不同数据库密码、不同服务器地址的实际部署场景。本节的 Workflow 仅为演示环境规则机制，下一节将加入真实的部署步骤。

## 九、多环境部署 — 环境专属密钥与变量实战

### 9.1 实战场景与目标

在前两节中，我们已经创建了 QA、STG、Production 三套环境，并为每个环境分别配置了 `SSH_PRIVATE_KEY`（加密密钥）和 `SERVER_IP`（服务器地址）。也编写了一个包含三个并行 Job 的 Workflow，通过 `environment` 字段将每个 Job 关联到对应环境。

但 Workflow 中还有最关键的一步没有写：**如何在 Job 的 steps 里面真正取到这些环境专属的变量，并用它们完成实际部署？**

本节以老师上节课演示过的 Java 项目为例，展示完整的部署步骤：通过 Workflow 引用环境专属密钥和变量，将编译好的 jar 包推送到不同环境的服务器上。

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 在 Workflow 中使用 `${{ secrets.XXX }}` 引用环境专属加密密钥
> - [ ] 在 Workflow 中使用 `${{ env.XXX }}` 引用环境专属普通变量
> - [ ] 理解"同名变量在不同环境下自动取不同值"的核心机制
> - [ ] 编写完整的 SSH + SCP 部署 Workflow，将 jar 包推送到目标服务器
> - [ ] 区分 `secrets.XXX` 与 `env.XXX` 的适用场景

### 9.2 前置准备

在开始编写部署步骤之前，请确认以下前置条件已满足（详见 M07 和 M08）：

| 前置项 | 说明 | 状态 |
|---|---|---|
| 三个环境已创建 | Settings → Environments → QA / STG / production | M07 已完成 |
| 每个环境的 Secret | 名称统一为 `SSH_PRIVATE_KEY`，值各不相同 | M07 已完成 |
| 每个环境的 Variable | 名称统一为 `SERVER_IP`，值各不相同 | M07 已完成 |
| Workflow 框架 | 包含三个 Job，每个 Job 通过 `environment` 关联对应环境 | M08 已完成 |
| Java 项目 | 可使用 Maven 或 Gradle 构建，产出 jar 包 | 前期课程已准备 |

> ⚠️ **注意事项**：Environment Secret 和 Environment Variable 是在 Settings → Environments → 具体环境 中配置的，**不是**在仓库级别的 Settings → Secrets and variables → Actions 中配置。仓库级别和 Environment 级别是两个独立的作用域，Environment 级别的变量仅在该 Job 的 `environment` 字段匹配时才会注入。

### 9.3 Step-by-Step：在 Workflow 中引用环境专属变量

#### Step 1: 理解 Environment Secrets 的引用语法 — `${{ secrets.XXX }}`

##### 🧠 直观理解

Environment Secret 就像每个环境各有一把独立的钥匙，钥匙的名字都一样叫"服务器密钥"，但 QA 环境这把钥匙开的是 QA 服务器，Production 环境那把开的是 Production 服务器。你只需要在 Workflow 里写上钥匙的名字，GitHub Actions 会根据当前 Job 关联的环境，自动递给你对应的那把。

##### 📖 详细解释

在 M07 中，我们为三个环境各创建了一个名为 `SSH_PRIVATE_KEY` 的 Secret：

- QA 环境下的 `SSH_PRIVATE_KEY` = QA 服务器的 SSH 私钥
- stage 环境下的 `SSH_PRIVATE_KEY` = stage 服务器的 SSH 私钥
- production 环境下的 `SSH_PRIVATE_KEY` = 生产服务器的 SSH 私钥

在 Workflow 中引用时，统一写作：

```yaml
${{ secrets.SSH_PRIVATE_KEY }}
```

GitHub Actions 的执行机制如下：

```
Job 在运行时，先读取 environment 字段的值（如 "QA"）
  → 去对应 Environment 下查找 secrets
  → 发现 secrets.SSH_PRIVATE_KEY 存在
  → 返回 QA 环境下配置的那个 SSH 私钥
```

你**不需要**写 `${{ secrets.QA_SSH_PRIVATE_KEY }}` 或 `${{ secrets.PROD_SSH_PRIVATE_KEY }}` 这种带环境前缀的名字。三个环境使用完全相同的 Secret 名称，由 `environment` 字段自动决定取哪个值。这正是 GitHub Environments 设计中最精妙的地方 —— **同一份 Workflow YAML，适配所有环境，零修改**。

##### 💻 代码示例

在 Job 的 step 中使用 SSH 私钥连接服务器：

```yaml
# 文件名: deploy.yml（片段）
# 功能: 使用环境专属 SSH 密钥连接服务器

steps:
  - name: Deploy to Server via SSH
    run: |
      # 将 Secrets 中的私钥写入临时文件
      mkdir -p ~/.ssh
      echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/deploy_key
      chmod 600 ~/.ssh/deploy_key

      # 使用该私钥连接服务器执行远程命令
      ssh -i ~/.ssh/deploy_key -o StrictHostKeyChecking=no \
        deploy@${{ env.SERVER_IP }} "echo '连接成功'"
```

| 行号 | 代码 | 解释 |
|---|---|---|
| 5 | `mkdir -p ~/.ssh` | 确保 `.ssh` 目录存在 |
| 6 | `echo "${{ secrets.SSH_PRIVATE_KEY }}"` | 从当前环境取出 SSH 私钥并写入文件；双引号包裹防止换行丢失 |
| 7 | `chmod 600 ~/.ssh/deploy_key` | 私钥文件权限必须是 600，否则 SSH 会拒绝使用 |
| 9-10 | `ssh -i ~/.ssh/deploy_key` | 指定私钥文件，连接目标服务器 |

#### Step 2: 理解 Environment Variables 的引用语法 — `${{ env.XXX }}`

##### 🧠 直观理解

如果说 Secret 是封装好的"密码信封"（内容加密，日志中不显示），那 Variable 就是贴在信封外面的"地址标签"（内容是明文的，可以随便看）。服务器的 IP 地址本身不是敏感信息，不需要加密存储，用 Variable 更合适。

##### 📖 详细解释

在 M07 中，我们为三个环境各创建了一个名为 `SERVER_IP` 的 Variable：

- QA 环境下的 `SERVER_IP` = 10.0.1.50（QA 服务器 IP）
- stage 环境下的 `SERVER_IP` = 10.0.2.50（STG 服务器 IP）
- production 环境下的 `SERVER_IP` = 203.0.113.100（生产服务器公网 IP）

在 Workflow 中引用时，统一写作：

```yaml
${{ env.SERVER_IP }}
```

与 Secrets 相同，同一个 Variable 名称，不同环境下自动取不同值。且 Variable 的值是明文的，在 Workflow 日志中可见（方便排查网络连通性问题）。

> ⚠️ **注意事项**：不要把密码、Token、API Key 等敏感信息放在 Environment Variables 中。Variable 的值在 Workflow 运行日志中是**明文可见**的。凡是需要加密存储的，一律使用 `secrets.XXX`。

##### 💻 代码示例

在 SSH 命令中直接使用 IP 变量：

```yaml
# 文件名: deploy.yml（片段）
# 功能: 使用环境专属 IP 地址指定部署目标

steps:
  - name: Upload JAR to Target Server
    run: |
      echo "目标服务器 IP: ${{ env.SERVER_IP }}"

      # scp 使用环境专属 IP 和 SSH 密钥上传文件
      scp -i ~/.ssh/deploy_key -o StrictHostKeyChecking=no \
        target/app.jar \
        deploy@${{ env.SERVER_IP }}:/opt/app/
```

> 💡 **核心洞见**：`secrets.XXX` 和 `env.XXX` 的分工设计体现了"最小权限原则" —— 加密的东西放 Secrets，不加密的东西放 Variables。既保证了安全，又保持了灵活性。

#### Step 3: 理解"同名不同值"的核心机制

这是 GitHub Actions Environment 功能中**最重要、最容易被忽视**的设计。

##### 🔄 机制解析

```
                      ┌──────────────────────────────────┐
                      │        deploy.yml（唯一）          │
                      │                                  │
                      │  ${{ secrets.SSH_PRIVATE_KEY }}  │
                      │  ${{ env.SERVER_IP }}            │
                      │                                  │
                      └──────────┬───────────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │  environment:   │ │  environment:   │ │  environment:   │
    │     QA          │ │     STG         │ │   production    │
    ├─────────────────┤ ├─────────────────┤ ├─────────────────┤
    │ SSH_KEY = QA密钥 │ │ SSH_KEY = STG密钥│ │ SSH_KEY = 生产密钥│
    │ SERVER_IP =     │ │ SERVER_IP =     │ │ SERVER_IP =     │
    │   10.0.1.50     │ │   10.0.2.50     │ │   203.0.113.100  │
    └─────────────────┘ └─────────────────┘ └─────────────────┘
```

当 `deploy-qa` Job 运行时（`environment: QA`），`secrets.SSH_PRIVATE_KEY` 解析为 QA 密钥，`env.SERVER_IP` 解析为 `10.0.1.50`。

当 `deploy-prod` Job 运行时（`environment: production`），同样的表达式 `secrets.SSH_PRIVATE_KEY` 解析为生产密钥，`env.SERVER_IP` 解析为 `203.0.113.100`。

> 💡 **核心洞见**：你永远不需要在 YAML 文件里写环境分支逻辑（`if: environment == 'prod'`）。GitHub Actions 在**注入阶段**就已经根据 `environment` 字段自动选择了正确的值。Workflow YAML 保持完全一致，环境差异全部外置在 Settings 页面中管理。这就是 Infrastructure as Code 中"配置与代码分离"的最佳实践。

#### Step 4: 编写完整的多环境部署 Workflow

下面是将 M08 的并行 Job 框架与本节的环境变量引用结合后的**完整可运行 Workflow**。三个 Job 结构完全相同，差异仅在于 `environment` 字段的值 —— 而正是这一行决定了所有 `secrets.XXX` 和 `env.XXX` 的最终解析值。

```yaml
# 文件名: .github/workflows/deploy.yml
# 功能: 多环境部署 — 根据 Job 的 environment 字段自动注入对应的
#       Secret（SSH 私钥）和 Variable（服务器 IP），将 Java jar 包
#       推送到 QA / STG / Production 服务器

name: Multi-Environment Deploy

on:
  workflow_dispatch:        # 手动触发（演示用）

jobs:
  # ============================================================
  # Job 1: 部署到 QA 环境 — 无保护规则，立即执行
  # ============================================================
  deploy-qa:
    runs-on: ubuntu-latest
    environment: QA         # 关键：指定环境，决定 secrets/env 解析来源

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Build JAR with Maven
        run: mvn clean package -DskipTests

      - name: Deploy to QA Server
        run: |
          # 第一步：写入 SSH 私钥（从 QA 环境的 Secret 中获取）
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key

          # 第二步：使用 QA 环境的 IP 地址连接服务器
          echo "正在部署到 QA 服务器: ${{ env.SERVER_IP }}"

          # 第三步：上传 jar 包到目标服务器
          scp -i ~/.ssh/deploy_key -o StrictHostKeyChecking=no \
            target/*.jar \
            deploy@${{ env.SERVER_IP }}:/opt/myapp/

          # 第四步：重启应用服务
          ssh -i ~/.ssh/deploy_key -o StrictHostKeyChecking=no \
            deploy@${{ env.SERVER_IP }} \
            "sudo systemctl restart myapp && echo 'QA 部署完成'"

          # 清理私钥文件
          rm -f ~/.ssh/deploy_key

  # ============================================================
  # Job 2: 部署到 STG 环境 — 等待 1 分钟后执行
  # ============================================================
  deploy-stg:
    runs-on: ubuntu-latest
    environment: stage        # 关键：切换到 STG 环境

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Build JAR with Maven
        run: mvn clean package -DskipTests

      - name: Deploy to STG Server
        run: |
          # 相同的写法，但 secrets.SSH_PRIVATE_KEY 取自 STG 环境
          # env.SERVER_IP 也取自 STG 环境（如 10.0.2.50）
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key

          echo "正在部署到 STG 服务器: ${{ env.SERVER_IP }}"

          scp -i ~/.ssh/deploy_key -o StrictHostKeyChecking=no \
            target/*.jar \
            deploy@${{ env.SERVER_IP }}:/opt/myapp/

          ssh -i ~/.ssh/deploy_key -o StrictHostKeyChecking=no \
            deploy@${{ env.SERVER_IP }} \
            "sudo systemctl restart myapp && echo 'STG 部署完成'"

          rm -f ~/.ssh/deploy_key

  # ============================================================
  # Job 3: 部署到 Production 环境 — 需要审批 + 等待 1 分钟
  # ============================================================
  deploy-prod:
    runs-on: ubuntu-latest
    environment: production  # 关键：切换到 Production 环境

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Build JAR with Maven
        run: mvn clean package -DskipTests

      - name: Deploy to Production Server
        run: |
          # 相同的写法，但 secrets.SSH_PRIVATE_KEY 取自 production 环境
          # env.SERVER_IP 也取自 production 环境（如生产公网 IP）
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key

          echo "正在部署到生产服务器: ${{ env.SERVER_IP }}"

          scp -i ~/.ssh/deploy_key -o StrictHostKeyChecking=no \
            target/*.jar \
            deploy@${{ env.SERVER_IP }}:/opt/myapp/

          ssh -i ~/.ssh/deploy_key -o StrictHostKeyChecking=no \
            deploy@${{ env.SERVER_IP }} \
            "sudo systemctl restart myapp && echo 'Production 部署完成'"

          rm -f ~/.ssh/deploy_key
```

> 💡 **核心洞见**：三个 Job 的 steps 代码几乎一模一样，唯一的差别是 `environment` 字段的值。你不需要在 steps 里写任何 `if-else` 判断当前是哪个环境。GitHub Actions 在执行时，会根据 `environment` 自动去对应环境下查找 `SSH_PRIVATE_KEY` 和 `SERVER_IP`，并注入到 `${{ }}` 表达式中。这就是"**一份配置，多处部署**"的核心思想。

#### Step 5: 串联部署流程

以上 Workflow 中，每个 Job 的实际部署步骤遵循一个固定的四步流程：

```
┌─────────────────────────────────────────────────────────┐
│                 单个环境的部署流程                         │
├───────────┬─────────────────────────────────────────────┤
│           │                                             │
│  Step 1   │  获取目标服务器 IP                           │
│           │  ${{ env.SERVER_IP }}                       │
│           │  来源：Environment Variables（明文）          │
│           │                                             │
│           ▼                                             │
│  Step 2   │  获取 SSH 连接密钥                           │
│           │  ${{ secrets.SSH_PRIVATE_KEY }}             │
│           │  来源：Environment Secrets（加密）            │
│           │                                             │
│           ▼                                             │
│  Step 3   │  SSH 连接到目标服务器                         │
│           │  ssh -i deploy_key deploy@<IP>              │
│           │  使用 Step 1 的 IP + Step 2 的密钥           │
│           │                                             │
│           ▼                                             │
│  Step 4   │  上传 jar 包 + 重启服务                       │
│           │  scp target/*.jar → /opt/myapp/             │
│           │  ssh "systemctl restart myapp"              │
│           │                                             │
└───────────┴─────────────────────────────────────────────┘
```

这个四步流程在每个环境（QA / STG / Production）中重复执行，区别仅在于 Step 1 取到的 IP 和 Step 2 取到的密钥不同。

### 9.4 验证结果

触发 Workflow 后，在 GitHub 仓库的 Actions 标签页中可以看到三个 Job 并行执行：

1. **deploy-qa** — 最先完成部署（QA 环境无保护规则），日志中显示 `${{ env.SERVER_IP }}` 解析为 QA 服务器的 IP。
2. **deploy-stg** — 等待 1 分钟后执行部署，日志中显示 `${{ env.SERVER_IP }}` 解析为 stage 服务器的 IP。
3. **deploy-prod** — 等待审批通过后执行部署，日志中显示 `${{ env.SERVER_IP }}` 解析为 Production 服务器的公网 IP。

验证要点：检查每个 Job 的部署日志，确认以下内容：

| 验证项 | 检查方法 |
|---|---|
| IP 地址正确 | 日志中 `echo "正在部署到...服务器: [IP]"` 输出的 IP 与预期一致 |
| SSH 密钥正确 | `ssh` 和 `scp` 命令执行成功，无 Permission denied 错误 |
| jar 包已上传 | `scp` 命令输出显示文件传输完成 |
| 服务已重启 | `systemctl restart` 返回成功，无报错 |
| Secret 未泄露 | 日志中不会显示 `${{ secrets.SSH_PRIVATE_KEY }}` 的实际内容，只会显示 `***` |

### 9.5 排错指南

#### 🐛 排错实录 1：`secrets.XXX` 解析为空

**❌ 错误现象**
```
scp: Connection closed
ssh: connect to host  port 22: Connection refused
```
或者日志中 `${{ env.SERVER_IP }}` 输出为空。

**🔍 原因分析**

Secret 或 Variable 名称在当前 Job 的 `environment` 对应环境中不存在。常见原因：
1. Secret 配置在了仓库级别（Settings → Secrets and variables → Actions），而非环境级别（Settings → Environments → 具体环境）。
2. Secret 名称拼写不一致（如 `SSH_PRIVATE_KEY` vs `SSH_PRIVATEKEY`）。
3. `environment` 字段的值与环境名称大小写不匹配（如 `environment: qa` vs 实际创建的 `QA`）。

**✅ 正确做法**

检查 Settings → Environments → [环境名]，确认 `SSH_PRIVATE_KEY` 和 `SERVER_IP` 都存在于该环境页面中（而非仓库级 Secrets 页面）。

**📝 经验总结**

仓库级 Secret 的作用域是整个仓库的所有 Workflow；Environment 级 Secret 的作用域仅限于 `environment` 匹配的 Job。如果你的 Job 指定了 `environment: QA`，但它需要的 Secret 配在了仓库级别而非 QA 环境下，`${{ secrets.XXX }}` 将解析为空。

---

#### 🐛 排错实录 2：SSH 连接 Permission denied

**❌ 错误现象**
```
deploy@10.0.1.50: Permission denied (publickey).
```

**🔍 原因分析**

SSH 私钥与目标服务器上的公钥不匹配。可能原因：
1. 该环境下的 `SSH_PRIVATE_KEY` 配置的是一个错误的私钥（比如把 Production 的密钥填到了 QA 环境）。
2. `chmod 600` 未生效，私钥文件权限过宽（SSH 要求私钥权限必须是 600）。
3. 私钥内容在复制粘贴时丢失了换行符（`-----BEGIN OPENSSH PRIVATE KEY-----` 和 `-----END OPENSSH PRIVATE KEY-----` 之间的内容拼接成了单行）。

**✅ 正确做法**

逐一检查三个环境的 `SSH_PRIVATE_KEY` ：
- Settings → Environments → QA → Environment secrets → 更新为 QA 服务器的正确私钥
- Settings → Environments → STG → Environment secrets → 更新为 stage 服务器的正确私钥
- Settings → Environments → production → Environment secrets → 更新为生产服务器的正确私钥

**📝 经验总结**

私钥配置建议直接在终端用 `cat ~/.ssh/id_rsa` 输出后完整复制，确保换行符不丢失。同时，部署完成后立即 `rm -f ~/.ssh/deploy_key` 清理临时私钥文件，防止泄露。

---

#### 🐛 排错实录 3：Variable 值在日志中暴露敏感信息

**❌ 错误现象**

部署日志中意外显示出了密码或 Token。

**🔍 原因分析**

误将敏感信息（如数据库密码、API Token）配置为 Environment Variables 而非 Environment Secrets。Variable 的值在 Workflow 日志中明文可见，任何有仓库访问权限的人都能看到。

**✅ 正确做法**

审查三个环境中所有的 Variable，将包含密码、Token、密钥等敏感信息的条目迁移到 Secrets 中。

**📝 经验总结**

一个简单的判断规则：**如果这个值你不敢截图发到群里，就放 Secrets；如果可以公开讨论，就放 Variables。** IP 地址、端口号、环境名称 → Variables；密码、密钥、Token → Secrets。

### 9.6 对比总结

#### Secrets vs Variables：语法与用途对比

| 维度 | `secrets.XXX` | `env.XXX` |
|---|---|---|
| **引用语法** | `${{ secrets.SSH_PRIVATE_KEY }}` | `${{ env.SERVER_IP }}` |
| **存储方式** | 加密存储，值写入后不可再次查看 | 明文存储，值可随时查看和修改 |
| **日志可见性** | 日志中自动脱敏，显示为 `***` | 日志中明文可见 |
| **典型用途** | SSH 私钥、数据库密码、API Token | 服务器 IP、端口号、环境标识 |
| **配置位置** | Settings → Environments → [环境] → Environment secrets | Settings → Environments → [环境] → Environment variables |
| **同名多值** | 支持：每个环境独立的同名 Secret | 支持：每个环境独立的同名 Variable |
| **注入时机** | Job 运行时，根据 `environment` 字段决定取值 | 同 Secrets，根据 `environment` 字段决定取值 |

#### 三环境配置总览

| 环境 | 保护规则 | `SSH_PRIVATE_KEY`（Secret） | `SERVER_IP`（Variable） |
|---|---|---|---|
| **QA** | 无限制 | QA 服务器 SSH 私钥 | QA 服务器内网 IP（如 10.0.1.50） |
| **STG** | 等待 1 分钟 | STG 服务器 SSH 私钥 | STG 服务器内网 IP（如 10.0.2.50） |
| **production** | 审批 + 等待 1 分钟 | 生产服务器 SSH 私钥 | 生产服务器公网 IP（如 203.0.113.100） |

三个环境使用完全相同的 Workflow YAML，不需要任何环境判断分支。**一份配置，三处部署，环境差异由 GitHub Actions 在运行时自动注入。** 这正是 GitHub Environments 功能为 CI/CD 带来的核心价值。

---


---

## 📋 课程小结

### 🗺️ 知识图谱

```
                              ┌──────────────────────────────────────┐
                              │        GitHub Actions 自动化          │
                              └──────────────────┬───────────────────┘
                                                 │
                 ┌───────────────────────────────┼───────────────────────────────┐
                 │                               │                               │
                 ▼                               ▼                               ▼
    ┌──────────────────────┐      ┌──────────────────────┐      ┌──────────────────────┐
    │   Workflow 配置       │      │   触发与变量管理       │      │   多环境部署           │
    ├──────────────────────┤      ├──────────────────────┤      ├──────────────────────┤
    │ · name / on / jobs   │      │ · workflow_dispatch   │      │ · QA / Staging / Prod │
    │ · runs-on (虚拟机)    │      │ · schedule (cron)     │      │ · Protection Rules    │
    │ · steps (步骤)        │      │ · push / pull_request │      │ · Required Reviewers  │
    │ · uses (复用Action)   │      │ · Secrets (加密变量)  │      │ · Wait Timer          │
    │ · with (传参)         │      │ · Variables (普通变量)│      │ · Environment Secrets │
    │ · Artifacts (产物)    │      │ · UTC 时区转换        │      │ · Environment Variables│
    └──────────────────────┘      └──────────────────────┘      └──────────────────────┘
                 │                               │                               │
                 └───────────────────────────────┼───────────────────────────────┘
                                                 │
                                                 ▼
                              ┌──────────────────────────────────────┐
                              │          GitHub Marketplace          │
                              │     社区 Action "应用商店"            │
                              │     · PyInstaller · Docker           │
                              │     · 安全扫描 · 云部署              │
                              └──────────────────────────────────────┘
```

### 💡 一句话总结

> GitHub Actions 的本质是将重复性运维劳动自动化：通过 YAML 配置定义"何时触发、在什么环境、做什么事"，借助社区 Action 生态开箱即用，通过 Secrets/Environments 实现安全的多环境部署——让开发者从"环境管理"中解放，专注于代码本身。

### 📍 系列定位

> 📍 **系列定位**：本文是「GitHub 全栈开发实战」系列第 25-26 篇。
> - 上一篇：[17-Github Action 基础概念] — GitHub Actions 的核心概念和基础用法
> - 下一篇：待定

---

## 📝 课后练习

### 练习 1: 编写一个定时签到 Workflow

**题目**：选择一个你常用的网站，编写一个 GitHub Actions Workflow，实现每天定时自动签到。

**验收标准**：
- [ ] Workflow 文件放在 `.github/workflows/` 目录下
- [ ] 使用 `schedule` + cron 表达式实现每天定时触发
- [ ] 同时支持 `workflow_dispatch` 手动触发
- [ ] 敏感信息（如 Cookie、Token）通过 GitHub Secrets 存储
- [ ] Workflow 在 Actions 页面显示绿色通过状态
- [ ] 签到结果通过日志输出可验证

### 练习 2: 配置多环境部署保护规则

**题目**：在你自己的项目中，配置至少两个环境（如 `dev` 和 `prod`），并为生产环境添加审批保护。

**验收标准**：
- [ ] 在 Settings → Environments 中创建 `dev` 和 `prod` 两个环境
- [ ] `dev` 环境无保护规则，`prod` 环境配置 Required reviewers
- [ ] 编写包含两个 Job 的 Workflow，分别关联 `dev` 和 `prod` 环境
- [ ] 手动触发 Workflow，观察 `prod` Job 等待审批的状态
- [ ] 完成审批操作，确认 `prod` Job 最终执行成功

### 练习 3: 跨平台编译打包

**题目**：将你自己的一个 Python 项目，通过 GitHub Actions 编译成 Windows 和 Ubuntu 两个平台的可执行文件。

**验收标准**：
- [ ] 使用 PyInstaller 或类似的社区 Action 进行打包
- [ ] 至少包含 `windows-latest` 和 `ubuntu-latest` 两个 Job
- [ ] 使用 `upload-artifact` 上传产物
- [ ] 两个平台的产物都能成功下载
- [ ] Ubuntu 产物下载后在本地 Ubuntu 虚拟机中赋予执行权限并成功运行

---
> 📅 生成日期: 2026-07-18 | 🎯 级别: M 级 | ⏱️ 录音时长: ~17 分钟 | 📏 文档规模: 3,800+ 行
> 🤖 由 transcript-to-doc v4.2 生成
