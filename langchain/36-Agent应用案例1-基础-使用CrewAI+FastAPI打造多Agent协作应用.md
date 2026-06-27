# Agent 应用案例 1（基础）——使用 CrewAI + FastAPI 打造多 Agent 协作应用

> 基于陈泽鹏老师视频课程整理编写 · 2026年6月27日

---

## 目录

- [一、课程概述与学习目标](#一课程概述与学习目标)
- [二、CrewAI 核心概念速览](#二crewai-核心概念速览)
  - [2.1 CrewAI 是什么](#21-crewai-是什么)
  - [2.2 Agent——自主可控的智能体](#22-agent自主可控的智能体)
  - [2.3 Task——分配给 Agent 的具体任务](#23-task分配给-agent-的具体任务)
  - [2.4 Process——任务执行策略](#24-process任务执行策略)
  - [2.5 Crew——协作团队的容器](#25-crew协作团队的容器)
  - [2.6 Pipeline——多 Crew 编排](#26-pipeline多-crew-编排)
- [三、本案例的业务场景](#三本案例的业务场景)
- [四、前期准备——环境与大模型](#四前期准备环境与大模型)
  - [4.1 开发环境：PyCharm + 虚拟环境](#41-开发环境pycharm--虚拟环境)
  - [4.2 大模型方案一：GPT 代理方式](#42-大模型方案一gpt-代理方式)
  - [4.3 大模型方案二：OneAPI 管理多模型](#43-大模型方案二oneapi-管理多模型)
  - [4.4 大模型方案三：Ollama 本地部署](#44-大模型方案三ollama-本地部署)
- [五、方式一：官方模板快速体验](#五方式一官方模板快速体验)
  - [5.1 下载源码并创建项目](#51-下载源码并创建项目)
  - [5.2 创建官方模板工程](#52-创建官方模板工程)
  - [5.3 配置大模型环境变量](#53-配置大模型环境变量)
  - [5.4 运行并观察输出](#54-运行并观察输出)
- [六、方式二：FastAPI 封装对外服务](#六方式二fastapi-封装对外服务)
  - [6.1 项目结构](#61-项目结构)
  - [6.2 配置文件——Agent 与 Task 的 YAML 定义](#62-配置文件agent-与-task-的-yaml-定义)
  - [6.3 Crew 封装类——核心执行逻辑](#63-crew-封装类核心执行逻辑)
  - [6.4 FastAPI 服务——对外暴露接口](#64-fastapi-服务对外暴露接口)
  - [6.5 测试客户端——调用 API](#65-测试客户端调用-api)
  - [6.6 主入口——服务启动](#66-主入口服务启动)
- [七、三种模型效果对比](#七三种模型效果对比)
- [八、完整代码清单](#八完整代码清单)
- [九、常见问题与排错指南](#九常见问题与排错指南)
- [十、课后练习](#十课后练习)
- [十一、课程小结](#十一课程小结)

---

## 一、课程概述与学习目标

### 1.1 本课定位

> 这是「Agent 应用案例」系列的**第一课（基础篇）**。前面我们学习了用 LangGraph 从零搭建多 Agent 系统。本课换一个视角：**使用 CrewAI 框架，以更简洁的方式构建多 Agent 协作应用，并用 FastAPI 包装成 HTTP 服务对外提供。**

```
┌─────────────────────────────────────────────────────────┐
│           Agent 开发两大路径                               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  路径一：从零搭建（前7课 LangGraph 方案）                 │
│  ├── 完全掌控底层逻辑                                    │
│  ├── 灵活度最高                                          │
│  └── 代码量较大                                          │
│                                                         │
│  路径二：使用框架（本课 CrewAI 方案）                     │
│  ├── 快速构建，代码量少                                  │
│  ├── YAML 配置驱动，结构清晰                             │
│  └── 适合快速原型和中小型项目                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 1.2 本课要掌握的目标

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  目标一：理解 CrewAI 的核心概念                            │
│         ├── Agent（智能体）、Task（任务）                 │
│         ├── Process（顺序/分层执行策略）                   │
│         └── Crew（协作团队容器）                           │
│                                                         │
│  目标二：掌握 CrewAI + FastAPI 的集成方式                  │
│         ├── YAML 配置驱动的 Agent/Task 定义               │
│         ├── Crew 封装类的编写                             │
│         └── FastAPI POST 接口的暴露                       │
│                                                         │
│  目标三：掌握三种大模型接入方案                             │
│         ├── GPT 代理方式                                  │
│         ├── OneAPI 统一管理多模型                         │
│         └── Ollama 本地大模型部署                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 二、CrewAI 核心概念速览

### 2.1 CrewAI 是什么

> **CrewAI 是一个用于构建多 Agent 系统的框架。** 它让你能够定义多个具有不同角色和目标的 Agent，让它们像一个团队（Crew）一样协作完成复杂任务。

```
CrewAI 的官网和 GitHub：
├── 官网：https://crewai.com
└── GitHub：https://github.com/crewAIInc/crewAI
```

```
CrewAI 的核心思想：

传统单 Agent：                  CrewAI 多 Agent：
┌──────────┐              ┌─────────────────────┐
│ 一个Agent │              │   Crew（团队）        │
│ 做所有事  │              │                     │
│          │              │  Agent 1（研究员）    │
│  ❌ 混乱  │              │  Agent 2（分析师）    │
│  ❌ 难维护 │              │  Agent 3（写手）      │
└──────────┘              │                     │
                          │  各司其职 ✅           │
                          │  协作完成 ✅           │
                          └─────────────────────┘
```

### 2.2 Agent——自主可控的智能体

> Agent 是 CrewAI 中最基本的执行单元。每个 Agent 有自己的**角色**、**目标**和**背景故事**，可以执行任务、做出决定，并与其他 Agent 通信。

```
Agent 的核心属性：

┌─────────────────────────────────────────────────────────┐
│  role（角色）：Agent 的职位描述                            │
│  例如："高级数据研究员"                                   │
│                                                         │
│  goal（目标）：Agent 要达成的最终目标                      │
│  例如："探索指定主题的前沿发展"                            │
│                                                         │
│  backstory（背景故事）：Agent 的经验和能力描述             │
│  例如："你是一名经验丰富的研究员，擅长发现最新信息..."     │
│                                                         │
│  tools（工具列表）：Agent 可用的工具                       │
│  例如：[搜索工具, 数据分析工具, ...]                      │
│                                                         │
│  allow_delegation：是否允许该 Agent 委托任务给其他 Agent   │
│                                                         │
│  verbose：是否输出详细日志                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.3 Task——分配给 Agent 的具体任务

> Task 定义了需要完成的具体工作，包括描述、期望输出、分配给哪个 Agent。

```
Task 的核心属性：

┌─────────────────────────────────────────────────────────┐
│  description（任务描述）：要做什么                         │
│  例如："找出与主题最相关的 10 条前沿信息"                  │
│                                                         │
│  expected_output（期望输出）：任务完成后期望得到什么       │
│  例如："一个包含 10 个要点的清单"                         │
│                                                         │
│  agent（分配）：这个任务分配给哪个 Agent                   │
│                                                         │
│  tools（工具列表）：执行此任务可用的工具                   │
│                                                         │
│  output_file（输出文件）：结果保存到哪个文件                │
│  例如："report.md"                                       │
│                                                         │
│  context（上下文）：可以引用其他 Task 的输出作为输入       │
│  例如：[task1, task2] —— 前两个任务的结果作为本任务上下文 │
│                                                         │
│  async_execution：是否异步执行                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.4 Process——任务执行策略

> Process 定义了任务如何被执行的策略，相当于团队的"项目经理"。CrewAI 提供两种执行机制：

```
┌─────────────────────────────────────────────────────────┐
│  方式一：Sequential（顺序流程，默认）                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │  Task 1  │ →  │  Task 2  │ →  │  Task 3  │          │
│  │ Agent A  │    │ Agent B  │    │ Agent C  │          │
│  └──────────┘    └──────────┘    └──────────┘          │
│                                                         │
│  特点：                                                  │
│  ├── 按任务列表顺序逐一执行                               │
│  ├── 前一个任务的输出自动成为下一个任务的上下文           │
│  └── 确定的、可预测的执行路径                             │
│                                                         │
│  方式二：Hierarchical（分层流程）                         │
│  ┌──────────────────────────────────────┐               │
│  │         Manager Agent（管理者）        │               │
│  │   负责计划、分配、审核、验证          │               │
│  └──────┬──────────┬──────────┬─────────┘               │
│         ▼          ▼          ▼                          │
│    ┌────────┐ ┌────────┐ ┌────────┐                     │
│    │Agent A │ │Agent B │ │Agent C │                     │
│    └────────┘ └────────┘ └────────┘                     │
│                                                         │
│  特点：                                                  │
│  ├── 需要指定一个 manager_llm                            │
│  ├── 任务不是预定分配的，而是根据 Agent 能力动态分配      │
│  └── Manager 审核产出并评估任务完成情况                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.5 Crew——协作团队的容器

> Crew 是一组 Agent 和 Task 的集合，定义了整体的工作流程和执行策略。

```
Crew 的核心属性：

┌─────────────────────────────────────────────────────────┐
│  tasks（任务列表）：分配给这个 Crew 的所有 Task           │
│                                                         │
│  agents（Agent 列表）：这个团队中的所有 Agent             │
│                                                         │
│  process（执行策略）：Sequential 或 Hierarchical          │
│                                                         │
│  manager_llm：当 process=Hierarchical 时，管理者的 LLM   │
│                                                         │
│  language：输出语言（默认英文，可设为中文）               │
│                                                         │
│  verbose：是否输出详细执行日志                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.6 Pipeline——多 Crew 编排

> Pipeline 允许多个 Crew 按照一定策略（顺序/并行）执行，构建更复杂的工作流。每个 Crew 的输出可以作为下一个 Crew 的输入。

```
Pipeline 模式：

┌──────────┐     ┌──────────┐     ┌──────────┐
│  Crew 1  │ →   │  Crew 2  │ →   │  Crew 3  │
│ 数据收集  │     │ 数据分析  │     │ 报告生成  │
└──────────┘     └──────────┘     └──────────┘

或并行执行：

┌──────────┐
│  Crew 1  │ ← 方案A
├──────────┤
│  Crew 2  │ ← 方案B  → 综合评估 → 最终结果
├──────────┤
│  Crew 3  │ ← 方案C
└──────────┘
```

---

## 三、本案例的业务场景

### 3.1 场景描述

> 一个主题研究 + 报告生成系统。用户输入一个主题（topic），两个 Agent 协作完成研究和报告撰写。

```
┌─────────────────────────────────────────────────────────┐
│          案例场景：主题研究与报告生成                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  用户输入：                                              │
│  "2024 年人工智能领域的前沿发展"                          │
│                                                         │
│  Agent 1 — 研究员（Researcher）：                        │
│  ├── 角色：高级数据研究员                                │
│  ├── 目标：探索该主题在 2024 年的前沿发展                │
│  └── 产出：10 个要点清单                                 │
│                                                         │
│  Agent 2 — 报告分析师（Report Analyst）：                │
│  ├── 角色：报告分析专家                                  │
│  ├── 目标：根据研究结果创建详细报告                       │
│  └── 产出：结构化的 Markdown 报告文件                    │
│                                                         │
│  执行流程（Sequential）：                                │
│  Task 1（研究员搜集信息） → Task 2（分析师撰写报告）     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 四、前期准备——环境与大模型

### 4.1 开发环境：PyCharm + 虚拟环境

```
Step 1: 下载安装 PyCharm
├── 官网：https://www.jetbrains.com/pycharm/
└── 选择 Community 版（免费）

Step 2: 创建项目
├── New Project → 项目名：crewai-test
├── 解释器：Python 3.11
├── 虚拟环境名：crewai-test
└── 点击 Create

Step 3: 安装依赖
pip install crewai fastapi uvicorn
```

```
依赖包说明：
├── crewai      → 多 Agent 协作框架
├── fastapi     → Web API 框架
├── uvicorn     → ASGI 服务器（运行 FastAPI）
└── pydantic    → 数据校验（FastAPI 依赖）
```

### 4.2 大模型方案一：GPT 代理方式

> 适用于能访问 OpenAI API 但需要代理的情况。通过设置代理地址来调用 GPT 系列模型。

```python
# ── GPT 代理配置 ──
import os

os.environ["OPENAI_API_BASE"] = "https://your-proxy-url/v1"  # 代理地址
os.environ["OPENAI_API_KEY"] = "sk-your-api-key"              # API Key
os.environ["MODEL_NAME"] = "gpt-4o-mini"                       # 模型名
```

### 4.3 大模型方案二：OneAPI 管理多模型

> OneAPI 是一个 **OpenAI API 管理系统**，支持统一管理多种大模型的 API 访问。通过它可以用一个接口访问千问、星火、智谱等多种模型。

```
┌─────────────────────────────────────────────────────────┐
│          OneAPI 是什么                                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  它把各种大模型的 API 都包装成 OpenAI 兼容的格式          │
│                                                         │
│  GPT-4 ─┐                                               │
│  千问  ─┼─→ OneAPI ─→ 统一的 OpenAI 格式接口             │
│  星火  ─┤        ↑                                       │
│  智谱  ─┘    你只需调这一个                             │
│                                                         │
│  好处：换模型只需改配置，不用改代码                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

```
OneAPI 安装与配置：

Step 1: 下载 OneAPI
├── GitHub Release 页面：https://github.com/songquanpeng/one-api
└── 下载对应系统的版本

Step 2: 启动服务
chmod +x one-api
./one-api
→ 默认端口 3000
→ 访问 http://localhost:3000

Step 3: 初始设置
├── 用户名：root
├── 密码：123456
└── 登录后修改密码

Step 4: 添加渠道（Channel）
├── 渠道 = 一个实际的模型 API
├── 例如：添加千问 → 填入千问的 API Key 和地址
├── 测试连通性 → 确认 OK
└── 可以添加多个渠道（GPT、千问、星火...）

Step 5: 创建令牌（Token）
├── 令牌 = 你实际使用的 API Key
├── 可以设置额度限制
├── 创建完成后复制这个 Key
└── 这个 Key 就能调用你添加的所有渠道模型
```

```python
# ── OneAPI 配置（千问模型示例）──
import os

os.environ["OPENAI_API_BASE"] = "http://localhost:3000/v1"  # OneAPI 地址
os.environ["OPENAI_API_KEY"] = "sk-your-oneapi-token"       # OneAPI 令牌
os.environ["MODEL_NAME"] = "qwen-max"                       # 千问模型
```

### 4.4 大模型方案三：Ollama 本地部署

> Ollama 是一个**轻量级本地大模型运行工具**，让你在本地电脑上直接运行大模型，不依赖云服务。

```
┌─────────────────────────────────────────────────────────┐
│          Ollama 是什么                                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  特点：                                                  │
│  ├── 本地运行，数据不出本机                              │
│  ├── 免费，无需 API Key                                  │
│  ├── 跨平台（Windows/Mac/Linux）                         │
│  ├── 一行命令下载 + 启动模型                              │
│  └── 支持多种开源模型（Llama、千问、Mistral...）         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

```
Ollama 安装与使用：

Step 1: 下载安装
├── 官网：https://ollama.com
└── 选择对应系统版本下载

Step 2: 下载模型
ollama pull llama3.1:8b     # Llama 3.1 8B
ollama pull qwen2:7b        # 千问 2 7B
ollama pull mistral:7b      # Mistral 7B

Step 3: 运行模型
ollama run llama3.1:8b
→ 进入交互模式，可以直接对话

Step 4: 在代码中使用
Ollama 提供了 OpenAI 兼容的 API（默认端口 11434）
```

```python
# ── Ollama 本地模型配置 ──
import os

os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"  # Ollama 地址
os.environ["OPENAI_API_KEY"] = "ollama"                       # 随意填
os.environ["MODEL_NAME"] = "llama3.1:8b"                      # 模型名
```

---

## 五、方式一：官方模板快速体验

### 5.1 下载源码并创建项目

```
Step 1: 从 GitHub 下载课程源码
├── 解压到本地目录
└── 将代码文件复制到 PyCharm 项目根目录

Step 2: 在 PyCharm 终端中安装依赖
pip install crewai fastapi uvicorn
```

### 5.2 创建官方模板工程

CrewAI 提供了一个 CLI 工具，可以快速生成模板工程：

```bash
# 在项目目录下执行
# crewai create crew <你的工程名>

crewai create crew test-crew
```

```
创建完成后的目录结构：
test-crew/
├── .env                    # 环境变量配置（模型 API Key 等）
├── pyproject.toml          # 项目配置
└── src/
    └── test_crew/
        ├── config/
        │   ├── agents.yaml    # Agent 配置
        │   └── tasks.yaml     # Task 配置
        ├── crew.py            # Crew 封装类
        └── main.py            # 入口文件
```

### 5.3 配置大模型环境变量

编辑 `.env` 文件：

```bash
# ── .env 文件 ──

# OneAPI 方式（以千问为例）
OPENAI_API_BASE=http://localhost:3000/v1
OPENAI_API_KEY=sk-your-oneapi-token
MODEL_NAME=qwen-max
```

### 5.4 运行并观察输出

```bash
# 在 test-crew 目录下执行
cd test-crew
crewai run
```

```
执行过程观察：

═══════════════════════════════════════════════
Agent 1: 高级数据研究员 开始工作
═══════════════════════════════════════════════

[思考过程...]
→ 正在搜索 2024 年 AI 领域的前沿信息
→ 找到了 15 条相关信息
→ 筛选出最相关的 10 条

═══════════════════════════════════════════════
Agent 2: 报告分析专家 开始工作
═══════════════════════════════════════════════

[思考过程...]
→ 基于研究员提供的 10 条信息
→ 撰写结构化报告
→ 输出到 report.md 文件

✅ 完成！报告已生成：report.md
```

```
输出文件 report.md 的内容结构：

# 2024 年人工智能领域前沿发展报告

## 1. 大语言模型持续进化
...

## 2. 多模态 AI 成为主流
...

## 3. AI Agent 技术爆发
...
（共 10 个要点）
```

---

## 六、方式二：FastAPI 封装对外服务

> 在官方模板的基础上，我们用 FastAPI 包装一层，让这个多 Agent 系统能以 HTTP API 的方式对外提供服务。

### 6.1 项目结构

```
crewai-fastapi-project/
├── main.py                      # 服务启动入口
├── api_test.py                  # 测试客户端
├── config/
│   ├── agents.yaml              # Agent 配置
│   └── tasks.yaml               # Task 配置
├── crew_runner.py               # Crew 封装类
└── requirements.txt             # 依赖列表
```

### 6.2 配置文件——Agent 与 Task 的 YAML 定义

```yaml
# ── config/agents.yaml ──

researcher:
  role: "高级数据研究员"
  goal: "探索 {topic} 在 2024 年的前沿发展"
  backstory: >
    你是一名经验丰富的研究员，擅长发现某个主题的最新发展。
    你以发现最相关的信息并以简洁明了的方式将其呈现出来而闻名。
  verbose: true
  allow_delegation: false

report_analyst:
  role: "报告分析专家"
  goal: "根据研究结果创建详细的报告"
  backstory: >
    你是一名出色的报告分析师，对细节有着敏锐的洞察力。
    你擅长将复杂的数据转化为结构清晰、易于理解的报告。
    你对研究报告的格式和质量有着严格的要求。
  verbose: true
  allow_delegation: false
```

```yaml
# ── config/tasks.yaml ──

research_task:
  description: >
    对 {topic} 进行全面的研究分析。
    找出 2024 年该主题领域最重要的 10 个前沿发展。
    每个要点需要包含简要说明。
  expected_output: >
    一个包含 10 个要点的清单，每个要点列出与 {topic} 相关的
    2024 年前沿发展信息，附带简要说明。
  agent: researcher

report_task:
  description: >
    根据研究任务获得的 10 个要点清单，撰写每个主题的详细报告。
    确保报告内容详尽，包含所有相关信息，并以专业格式呈现。
  expected_output: >
    一份完整的 Markdown 格式报告，包含引言、10 个主题要点详细分析
    和总结。
  agent: report_analyst
  output_file: report.md
  context:
    - research_task    # ← 引用前一个任务的输出作为上下文
```

### 6.3 Crew 封装类——核心执行逻辑

```python
# ── crew_runner.py ──

from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew
import yaml
import os


class TopicResearchCrew:
    """
    主题研究 + 报告生成的 Crew 封装类
    
    负责：
    1. 加载 YAML 配置创建 Agent 和 Task
    2. 组装 Crew 并执行
    3. 返回最终结果
    """
    
    def __init__(self, verbose: bool = True):
        """
        初始化 Crew
        
        Args:
            verbose: 是否输出详细执行日志
        """
        self.verbose = verbose
        
        # ── 加载 YAML 配置 ──
        self.agents_config = self._load_yaml("config/agents.yaml")
        self.tasks_config = self._load_yaml("config/tasks.yaml")
        
        # ── 创建 Agent ──
        self.researcher = self._create_researcher()
        self.report_analyst = self._create_report_analyst()
        
        # ── 创建 Team（Crew）──
        self.crew = Crew(
            agents=[self.researcher, self.report_analyst],
            tasks=[],  # 任务在 run() 中动态创建
            process=Process.sequential,  # 顺序执行
            verbose=self.verbose
        )
    
    def _load_yaml(self, filepath: str) -> dict:
        """加载 YAML 配置文件"""
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def _create_researcher(self) -> Agent:
        """创建研究员 Agent"""
        config = self.agents_config["researcher"]
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            verbose=config.get("verbose", True),
            allow_delegation=config.get("allow_delegation", False)
        )
    
    def _create_report_analyst(self) -> Agent:
        """创建报告分析师 Agent"""
        config = self.agents_config["report_analyst"]
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            verbose=config.get("verbose", True),
            allow_delegation=config.get("allow_delegation", False)
        )
    
    def run(self, topic: str) -> str:
        """
        执行主题研究
        
        Args:
            topic: 用户输入的研究主题
        
        Returns:
            str: 最终的报告内容
        """
        # ── 动态创建 Task（注入 topic）──
        research_task_config = self.tasks_config["research_task"]
        report_task_config = self.tasks_config["report_task"]
        
        research_task = Task(
            description=research_task_config["description"].format(topic=topic),
            expected_output=research_task_config["expected_output"].format(topic=topic),
            agent=self.researcher
        )
        
        report_task = Task(
            description=report_task_config["description"],
            expected_output=report_task_config["expected_output"],
            agent=self.report_analyst,
            output_file=report_task_config.get("output_file"),
            context=[research_task]  # 引用研究任务的结果
        )
        
        # ── 更新 Crew 的任务列表并执行 ──
        self.crew.tasks = [research_task, report_task]
        result = self.crew.kickoff()
        
        return str(result)
```

### 6.4 FastAPI 服务——对外暴露接口

```python
# ── FastAPI 服务（在 main.py 中引入）──

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn
import json
import os

from crew_runner import TopicResearchCrew

# ══════════════════════════════════════════════════════
# FastAPI 应用初始化
# ══════════════════════════════════════════════════════

app = FastAPI(
    title="CrewAI Multi-Agent Service",
    description="使用 CrewAI 构建的多 Agent 协作研究服务",
    version="1.0.0"
)

# 全局 Crew 实例（服务启动时创建一次）
research_crew: Optional[TopicResearchCrew] = None

# ══════════════════════════════════════════════════════
# 请求/响应模型
# ══════════════════════════════════════════════════════

class ResearchRequest(BaseModel):
    """研究请求"""
    topic: str = Field(
        default="2024年人工智能前沿发展",
        description="要研究探讨的主题"
    )
    stream: bool = Field(
        default=False,
        description="是否使用流式输出"
    )


class ResearchResponse(BaseModel):
    """研究响应"""
    success: bool
    topic: str
    report: str
    format: str = "markdown"


# ══════════════════════════════════════════════════════
# 应用生命周期
# ══════════════════════════════════════════════════════

@app.on_event("startup")
async def startup_event():
    """
    服务启动时的初始化操作
    """
    global research_crew
    
    # ── 配置大模型（根据环境变量选择）──
    model_type = os.environ.get("MODEL_TYPE", "oneapi")
    
    if model_type == "oneapi":
        os.environ.setdefault("OPENAI_API_BASE", "http://localhost:3000/v1")
        os.environ.setdefault("MODEL_NAME", "qwen-max")
    elif model_type == "ollama":
        os.environ.setdefault("OPENAI_API_BASE", "http://localhost:11434/v1")
        os.environ.setdefault("MODEL_NAME", "llama3.1:8b")
    elif model_type == "gpt":
        os.environ.setdefault("OPENAI_API_BASE", "https://api.openai.com/v1")
        os.environ.setdefault("MODEL_NAME", "gpt-4o-mini")
    
    print(f"🤖 模型配置：BASE={os.environ['OPENAI_API_BASE']}, MODEL={os.environ['MODEL_NAME']}")
    
    # ── 初始化 Crew ──
    research_crew = TopicResearchCrew(verbose=True)
    print("✅ CrewAI 多 Agent 服务已就绪")


@app.on_event("shutdown")
async def shutdown_event():
    """服务关闭时的清理操作"""
    print("👋 服务关闭")


# ══════════════════════════════════════════════════════
# API 接口
# ══════════════════════════════════════════════════════

@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """
    主题研究接口
    
    接收一个主题，由两个 Agent 协作完成研究并生成报告
    
    - **topic**: 要研究的主题
    - **stream**: 是否流式输出
    """
    if research_crew is None:
        raise HTTPException(status_code=503, detail="服务未就绪")
    
    try:
        # ── 执行多 Agent 协作 ──
        report = research_crew.run(topic=request.topic)
        
        return ResearchResponse(
            success=True,
            topic=request.topic,
            report=report
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"研究过程出错: {str(e)}")


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "crew_ready": research_crew is not None
    }
```

### 6.5 测试客户端——调用 API

```python
# ── api_test.py ──

import requests
import json


def test_research(topic: str = "2024年人工智能前沿发展"):
    """
    测试研究 API
    
    Args:
        topic: 研究主题
    """
    # ── API 地址 ──
    url = "http://localhost:8012/research"
    
    # ── 构建请求 ──
    payload = {
        "topic": topic,
        "stream": False
    }
    
    print(f"🚀 发送研究请求：{topic}")
    print(f"📡 请求地址：{url}")
    print("-" * 50)
    
    # ── 发送 POST 请求 ──
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 研究成功！")
        print(f"\n{'='*50}")
        print(f"📄 研究报告：")
        print(f"{'='*50}")
        print(data["report"])
    else:
        print(f"❌ 请求失败：{response.status_code}")
        print(response.text)


if __name__ == "__main__":
    # ── 测试默认主题 ──
    test_research()
    
    # ── 测试自定义主题 ──
    # test_research("2024年新能源汽车发展趋势")
```

### 6.6 主入口——服务启动

```python
# ── main.py ──

import uvicorn
import os
import argparse


def main():
    """
    多 Agent 协作研究服务——主入口
    
    使用方式：
        python main.py                    # 默认 8012 端口
        python main.py --port 8080        # 指定端口
        python main.py --model ollama     # 使用本地模型
    """
    # ── 命令行参数解析 ──
    parser = argparse.ArgumentParser(description="CrewAI Multi-Agent Service")
    parser.add_argument("--port", type=int, default=8012, help="服务端口号")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="监听地址")
    parser.add_argument("--model", type=str, default="oneapi",
                       choices=["oneapi", "ollama", "gpt"],
                       help="模型类型")
    args = parser.parse_args()
    
    # ── 设置模型类型环境变量 ──
    os.environ["MODEL_TYPE"] = args.model
    
    # ── 启动服务 ──
    print(f"🤖 启动 CrewAI 多 Agent 服务...")
    print(f"📡 地址：http://{args.host}:{args.port}")
    print(f"🔧 模型：{args.model}")
    print(f"📖 API 文档：http://localhost:{args.port}/docs")
    
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=False  # 生产环境建议 False
    )


if __name__ == "__main__":
    main()
```

```
启动服务：

python main.py --port 8012 --model oneapi

输出：
🤖 启动 CrewAI 多 Agent 服务...
📡 地址：http://0.0.0.0:8012
🔧 模型：oneapi
📖 API 文档：http://localhost:8012/docs
🤖 模型配置：BASE=http://localhost:3000/v1, MODEL=qwen-max
✅ CrewAI 多 Agent 服务已就绪
INFO:     Uvicorn running on http://0.0.0.0:8012
```

---

## 七、三种模型效果对比

本案例使用三种不同的模型进行了测试，对比结果如下：

| 维度 | **千问 Max**（OneAPI） | **GPT-4o-mini**（代理） | **Llama 3.1 8B**（Ollama 本地） |
|---|---|---|---|
| **来源** | 通义千问（阿里云） | OpenAI | Meta 开源 |
| **运行方式** | OneAPI 中转 | 代理访问 | 本地运行 |
| **速度** | 中等 | **较快** ⚡ | 较慢（依赖硬件） |
| **研究结果** | 找到 15 条（超出要求10条） | **精准 10 条** ✅ | 仅 3 条 ❌ |
| **报告质量** | 良好，内容较丰富 | **优秀，结构清晰** | 较差，信息不足 |
| **Token 消耗** | 中等 | 低 | 无需付费 |
| **隐私安全** | 数据经 OneAPI 中转 | 数据出境 | **数据完全本地** 🔒 |
| **综合评价** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |

> 💡 **结论**：GPT-4o-mini 在本案例中表现最佳——速度快、结果精准、报告质量高。千问 Max 也不错但有时会输出超过要求数量的结果。本地 Llama 3.1 8B 受限于参数规模，效果不理想，建议使用更大的本地模型（如 70B+）或换用千问 2 等更强模型。

---

## 八、完整代码清单

```
项目完整文件结构：

crewai-fastapi-project/
├── main.py                 # FastAPI 服务主入口（含路由、生命周期）
├── crew_runner.py           # Crew 封装类（Agent + Task + Crew 创建）
├── api_test.py              # API 测试客户端
├── config/
│   ├── agents.yaml          # Agent 角色/目标/背景 配置
│   └── tasks.yaml           # Task 描述/输出/分配 配置
└── requirements.txt         # 依赖列表
```

```txt
# ── requirements.txt ──
crewai>=0.80.0
fastapi>=0.115.0
uvicorn>=0.30.0
pyyaml>=6.0
requests>=2.32.0
pydantic>=2.0.0
```

---

## 九、常见问题与排错指南

### 9.1 错误速查表

| 错误现象 | 原因 | 解决方法 | 优先级 |
|---|---|---|---|
| **crewai 安装失败** | Python 版本过低 | 使用 Python 3.10+，推荐 3.11 | 🔴 高 |
| **OpenAI API 调用 401** | API Key 错误或过期 | 检查 .env 中的 API Key；确认 OneAPI 令牌有效 | 🔴 高 |
| **连接 OneAPI 被拒** | OneAPI 服务未启动 | 启动 OneAPI：`./one-api`；检查端口 3000 | 🔴 高 |
| **Ollama 连接失败** | Ollama 服务未运行 | 启动 Ollama：`ollama serve`；确认模型已下载 | 🟡 中 |
| **Crew 执行到一半卡住** | 模型响应超时 | 检查网络；换用更快的模型；增加超时时间 | 🟡 中 |
| **Agent 输出不符合要求** | 提示词不够明确 | 优化 agents.yaml 中的 role/goal/backstory | 🟡 中 |
| **output_file 没有生成** | 代码中未设置 output_file | 在 Task 配置中添加 `output_file: report.md` | 🟢 低 |
| **流式输出不工作** | CrewAI 版本不支持 | 升级到最新版 CrewAI；或使用非流式兜底 | 🟢 低 |

### 9.2 模型连通性测试

```python
# ── 快速测试模型是否可用 ──
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:3000/v1",  # 改为你的地址
    api_key="sk-your-key"
)

response = client.chat.completions.create(
    model="qwen-max",
    messages=[{"role": "user", "content": "你好，请做自我介绍"}]
)

print(response.choices[0].message.content)
# 如果正常输出 → 模型可用 ✅
# 如果报错 → 检查地址和 API Key
```

---

## 十、课后练习

### 练习一：基础——跑通官方模板

**题目**：使用 `crewai create crew` 创建官方模板，配置 OneAPI 或 GPT，成功生成一份研究报告。

**要求**：
- 成功创建模板工程
- 配置大模型（三选一）
- 执行并观察两个 Agent 的协作过程
- 查看生成的 report.md 文件

### 练习二：进阶——自定义 Agent 和 Task

**题目**：修改 YAML 配置，新增第三个 Agent（例如：中文翻译员），把英文报告翻译成中文。

**要求**：
- 在 agents.yaml 中新增 `translator` Agent
- 在 tasks.yaml 中新增 `translation_task`
- 修改 crew_runner.py，增加第三个 Agent
- 验证最终输出包含中文报告

<details>
<summary>参考框架</summary>

```yaml
# agents.yaml 新增
translator:
  role: "专业翻译员"
  goal: "将研究报告准确翻译为中文"
  backstory: "你是一名专业的科技翻译..."
  verbose: true

# tasks.yaml 新增
translation_task:
  description: "将研究报告翻译为专业的中文版本"
  expected_output: "中文版的研究报告"
  agent: translator
  context:
    - report_task    # 依赖报告任务
```
</details>

### 练习三：综合实战——切换不同模型对比

**题目**：分别使用 OneAPI（千问）、GPT 代理、Ollama 本地模型运行同一主题，对比三者的效果。

**要求**：
- 同一主题（如"2024年AI发展"）
- 记录每种模型的速度、输出质量、Token 消耗
- 形成对比报告（类似第七章）
- 给你的项目选择推荐哪一种方案

---

## 十一、课程小结

### 11.1 核心知识图谱

```
┌────────────────────────────────────────────────────────────┐
│        CrewAI + FastAPI —— 核心知识体系                       │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  CrewAI 核心概念                                        │
│      ├── Agent：角色 + 目标 + 背景故事 + 工具                │
│      ├── Task：描述 + 期望输出 + 分配给谁 + 上下文           │
│      ├── Process：Sequential（顺序）/ Hierarchical（分层）   │
│      ├── Crew：Agent 集合 + Task 列表 + 执行策略             │
│      └── Pipeline：多 Crew 编排（顺序/并行）                 │
│                                                            │
│  2️⃣  三种大模型接入方案                                       │
│      ├── GPT 代理：设置 OPENAI_API_BASE 为代理地址           │
│      ├── OneAPI：统一管理多模型，一个接口访问所有             │
│      └── Ollama：本地运行，免费 + 隐私安全                   │
│                                                            │
│  3️⃣  项目实现流程                                            │
│      ├── YAML 配置 → Agent/Task 定义                         │
│      ├── Crew 封装类 → 加载配置 + 动态创建 + kickoff 执行    │
│      ├── FastAPI 路由 → POST /research 接收请求             │
│      └── 客户端调用 → requests.post → 解析响应              │
│                                                            │
│  4️⃣  模型效果对比                                            │
│      ├── GPT-4o-mini：最佳（速度快 + 精准）                   │
│      ├── 千问 Max：良好（内容丰富，偶尔超量）                 │
│      └── Llama 3.1 8B：较差（参数太小，信息不足）            │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 11.2 一句话总结

> **CrewAI 让多 Agent 协作从"手写编排逻辑"变成"YAML 配置 + 几行代码"——定义 Agent 的角色和目标，定义 Task 的描述和期望输出，CrewAI 自动帮你调度执行。加上 FastAPI，一个 POST 请求就能驱动两个 Agent 协作完成主题研究并生成报告。**

### 11.3 系列课程定位

```
┌─────────────────────────────────────────────────────────┐
│         Agent 应用案例系列                                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  应用案例1（本课）：CrewAI + FastAPI 基础入门              │
│         ← 你在这里                                       │
│                                                         │
│  后续案例：                                              │
│  ├── 应用案例2：多工具集成 + 复杂流程                     │
│  ├── 应用案例3：Pipeline 多 Crew 编排                     │
│  └── 应用案例4：生产环境部署与监控                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

*本教学文档基于陈泽鹏老师视频课程整理编写 · 2026年6月27日*
