# LangGraph 实战——05 从原型到生产，构建企业级应用

> 基于教学视频课程整理编写 · 2026年6月

---

## 目录

- [一、课程背景与目标](#一课程背景与目标)
- [二、生产环境全景蓝图](#二生产环境全景蓝图)
- [三、项目目录结构与工程规范](#三项目目录结构与工程规范)
- [四、LangGraph CLI——项目管理工具](#四langgraph-cli项目管理工具)
- [五、模板工程剖析——demo-agent](#五模板工程剖析demo-agent)
- [六、LangGraph Studio——可视化开发与调试](#六langgraph-studio可视化开发与调试)
- [七、LangSmith——云端部署与全链路追踪](#七langsmith云端部署与全链路追踪)
- [八、实战演练——从零到部署完整链路](#八实战演练从零到部署完整链路)
- [九、生产环境 checklist](#九生产环境-checklist)
- [十、常见问题与排错指南](#十常见问题与排错指南)
- [十一、课后练习](#十一课后练习)
- [十二、课程小结](#十二课程小结)

---

## 一、课程背景与目标

### 1.1 前情回顾

在前四课中，我们从零开始逐步构建了 LangGraph 的完整能力栈：

| 课程 | 核心能力 | 开发阶段 |
|------|----------|:------:|
| **01 入门和组件** | State / Node / Edge / Graph 搭建 | 原型验证 |
| **02 可记忆可恢复** | Checkpoint / Thread / Durable Execution | 核心能力 |
| **03 人机协作与时间旅行** | Streaming / interrupt / 时间旅行 | 交互完善 |
| **04 多智能体协作** | Subgraph / 四种协作模式 / 并行调度 | 架构构建 |

**前四课的共同问题**：所有代码都在 Jupyter Notebook 或单个脚本中运行。在真实的生产环境中，代码结构、部署方式、监控体系都完全不同。

> 本课是 LangGraph 系列课程的**最后一课**——教你如何把之前学到的所有能力，从一个"能跑的 demo"变成"能上线的产品"。

### 1.2 本节课的核心问题

> **代码写好了，怎么把它部署到生产环境？怎么监控运行状态？怎么确保稳定可靠？**

```
本课要解决的关键问题：

问题1：代码太乱，无法协作
	    State 定义、工具、节点、图全挤在一个文件里
	    → 项目结构应该怎么组织？

问题2：本地能跑，线上怎么办？
	    Jupyter 里 invoke 一下就行，但用户怎么调用？
	    → 如何部署成 API 服务？

问题3：出错了不知道
	    Agent 在生产环境中运行，执行到一半出错了怎么发现？
	    → 如何监控每一步的执行状态？

问题4：调了啥不知道
	    Agent 调了哪个工具？用了多少 Token？花了多少钱？
	    → 如何全链路追踪？
```

### 1.3 本课要掌握的目标

```
┌───────────────────────────────────────────────────────┐
│                                                       │
│  目标一：掌握 LangGraph 生产级项目结构                    │
│         ├── state / tools / nodes / graph 目录规范      │
│         ├── context 配置管理模式                        │
│         ├── .env 环境变量管理                           │
│         └── 链式 API 构建图的新写法                      │
│                                                       │
│  目标二：掌握 LangGraph CLI 工具链                       │
│         ├── langgraph build：构建 Docker 镜像           │
│         ├── langgraph dev：本地开发模式                 │
│         └── langgraph up：启动完整服务栈                 │
│                                                       │
│  目标三：掌握 LangSmith 部署与监控                       │
│         ├── LangGraph Studio 可视化调试                 │
│         ├── 自动生成 API 端点 + WebSocket               │
│         └── 全链路追踪（执行步骤/Token用量/延迟）         │
│                                                       │
│  目标四：完成从原型到生产的完整链路                         │
│         ├── 用 CLI 创建模板工程                         │
│         ├── 配置联网搜索 + 时间感知工具                   │
│         ├── 本地 dev 模式调试                           │
│         └── LangSmith 追踪每一步执行                     │
│                                                       │
└───────────────────────────────────────────────────────┘
```

---

## 二、生产环境全景蓝图

### 2.1 从原型到生产的跨越

```
原型阶段（前四课）                生产阶段（本课）
┌───────────────────┐          ┌─────────────────────────┐
│                   │          │                         │
│  📓 Jupyter/脚本   │          │  📁 标准化项目目录        │
│  单文件代码        │   ──→   │  State/Tools/Nodes 分离  │
│                   │          │                         │
│  🏠 本地 invoke     │          │  🌐 API 端点 + WebSocket │
│  手动调 app.invoke│   ──→   │  自动生成 HTTP 接口       │
│                   │          │                         │
│  👀 print 调试     │          │  📊 LangSmith 全链路追踪  │
│  肉眼看出不出错    │   ──→   │  每一步输入/输出/Token    │
│                   │          │                         │
│  🔑 硬编码 API Key │          │  🔐 .env 环境变量管理    │
│  写在代码里        │   ──→   │  安全注入，不进入版本控制  │
│                   │          │                         │
│  ❌ 无测试         │          │  ✅ 单元/集成/端到端测试   │
│  改了不知道坏了没  │   ──→   │  每次改动都有保障         │
│                   │          │                         │
└───────────────────┘          └─────────────────────────┘
```

### 2.2 生产环境五层架构

```
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph 生产环境全景                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  第一层：代码组织层                                           │
│      ├── 标准化项目目录结构（state/ tools/ nodes/ graph/）     │
│      ├── 环境变量管理（.env）                                 │
│      ├── 配置集中管理（context）                              │
│      └── 链式 API 构建图                                     │
│                                                             │
│  第二层：测试保障层                                           │
│      ├── 单元测试：单个节点独立验证                           │
│      ├── 集成测试：整个图的端到端流程                         │
│      └── 端到端测试：模拟真实用户场景                         │
│                                                             │
│  第三层：可视化开发层                                         │
│      ├── LangGraph Studio：图形化查看和编辑 Agent 流程        │
│      ├── 实时调试：单步执行，查看中间状态                     │
│      └── 错误定位：精确到节点级别的故障追踪                   │
│                                                             │
│  第四层：部署服务层                                           │
│      ├── LangSmith Deploy：一键部署到云端                    │
│      ├── 自动生成 REST API 端点                             │
│      ├── WebSocket 支持（流式输出）                          │
│      ├── 内置认证机制                                        │
│      └── Docker / Kubernetes 灵活部署                      │
│                                                             │
│  第五层：可观测性层                                           │
│      ├── 请求追踪：每个请求的完整调用链                       │
│      ├── 性能指标：响应时间、错误率                          │
│      ├── 成本指标：Token 用量、费用统计                      │
│      ├── 告警预置：异常自动通知                              │
│      └── 日志聚合：集中管理和检索                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 LangGraph 生产环境工具链

| 工具 | 用途 | 使用阶段 |
|------|------|:------:|
| **LangGraph CLI** | 创建项目、构建镜像、本地开发 | 开发 + 构建 |
| **LangGraph Studio** | 可视化图的编辑、运行和调试 | 开发 + 调试 |
| **LangSmith** | 云端部署、API 托管、全链路监控 | 部署 + 运维 |
| **Docker** | 容器化打包和分发 | 构建 + 部署 |
| **UV** | Python 依赖管理（快速、现代） | 开发 |

---

## 三、项目目录结构与工程规范

### 3.1 标准项目结构

在生产环境中，LangGraph 项目遵循一套**标准化的目录结构**：

```
demo-agent/                      # 项目根目录
├── .env                         # 环境变量（API Keys、项目配置等）
├── .gitignore                   # Git 忽略规则
├── langgraph.json               # LangGraph 项目配置文件
├── pyproject.toml               # Python 项目元数据和依赖（UV 管理）
├── uv.lock                      # 依赖锁定文件
├── Makefile                     # 常用命令快捷方式
│
└── src/                         # 源代码目录
    └── agent/                   # Agent 模块
        ├── __init__.py
        ├── graph.py             # 图的定义（主入口）
        ├── state.py             # State 类型定义
        ├── context.py           # 配置上下文（模型参数等）
        ├── nodes.py             # 节点函数实现
        ├── tools.py             # 工具定义
        └── prompts.py           # 提示词模板（可选）
```

### 3.2 各文件职责详解

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  state.py —— 统一的状态定义                                   │
│      ├── 定义所有 TypedDict State 类型                        │
│      ├── 定义 Reducer（add_messages 等）                     │
│      ├── 是整个项目的"数据契约"                                 │
│      └── 所有节点都依赖 State 的定义                          │
│                                                             │
│  context.py —— 配置上下文                                    │
│      ├── 模型名称和参数                                      │
│      ├── API 端点配置                                       │
│      ├── 环境变量加载                                        │
│      └── 集中管理，修改配置不改代码                            │
│                                                             │
│  tools.py —— 工具定义                                        │
│      ├── @tool 装饰器定义的工具函数                           │
│      ├── 工具的参数 Schema                                  │
│      └── 所有 Agent 可以调用的工具集中管理                     │
│                                                             │
│  nodes.py —— 节点函数                                        │
│      ├── 每个节点的业务逻辑                                  │
│      ├── 输入 State，返回 State 的部分更新                    │
│      └── 单一职责，方便单元测试                               │
│                                                             │
│  graph.py —— 图的组装                                        │
│      ├── 定义 StateGraph                                    │
│      ├── 添加节点和边                                       │
│      ├── 设置条件路由                                       │
│      ├── compile 图                                         │
│      └── 导出 app 供外部调用                                 │
│                                                             │
│  prompts.py —— 提示词模板（可选）                              │
│      ├── 系统提示词                                          │
│      ├── 可能在不同节点复用                                   │
│      └── 便于 A/B 测试不同提示词效果                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 与原型代码的对比

```python
# ── ❌ 原型阶段：所有代码挤在一个文件 ──
# my_agent.py（800 行，什么都在里面）

import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage

# State 定义（100 行后还得翻回来找...）
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    # ... 更多的字段

# 工具定义
@tool
def my_tool(query: str) -> str:
    # ...
    pass

# 节点函数
def my_node(state: State) -> State:
    # ...
    pass

# 图定义
graph = StateGraph(State)
# ...

# 调用
app = graph.compile()
result = app.invoke(...)

# =============================================
# ── ✅ 生产阶段：职责分离，模块化管理 ──

# state.py —— 纯数据定义
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# context.py —— 纯配置
model = ChatOpenAI(model="qwen-3b", ...)

# tools.py —— 纯工具
@tool
def my_tool(query: str) -> str:
    ...

# nodes.py —— 纯业务逻辑
def my_node(state: State) -> State:
    ...

# graph.py —— 纯组装
from .state import State
from .nodes import my_node
from .tools import my_tool

graph = StateGraph(State)
graph.add_node("my_node", my_node)
# ...
app = graph.compile()
```

| 维度 | 原型阶段 | 生产阶段 |
|------|----------|----------|
| **文件数量** | 1 个 | 5-8 个 |
| **单文件行数** | 500-1000 行 | 50-150 行 |
| **职责边界** | 模糊 | 清晰（每个文件一个职责） |
| **团队协作** | 容易冲突 | 不同人改不同文件 |
| **单元测试** | 困难（全部耦合） | 容易（每个节点独立测） |
| **代码复用** | 复制粘贴 | import 即可 |

---

## 四、LangGraph CLI——项目管理工具

### 4.1 安装

```bash
# ── 使用 UV 安装（推荐，全局可用）──
uv tool install langgraph-cli

# ── 或使用 pip 安装 ──
pip install langgraph-cli

# ── 验证安装 ──
langgraph --help
```

### 4.2 核心命令速查

| 命令 | 用途 | 使用阶段 |
|------|------|:------:|
| `langgraph build` | 将项目构建为 Docker 镜像 | 构建发布 |
| `langgraph dev` | 启动本地开发模式（连接 LangSmith Studio） | 开发调试 |
| `langgraph up` | 启动完整的服务栈（API + UI + 数据库） | 本地完整测试 |
| `langgraph new` | 基于模板创建新项目 | 项目初始化 |
| `langgraph dockerfile` | 生成 Dockerfile | 自定义构建 |

### 4.3 创建新项目

```bash
# ── 基于 Python 模板创建新项目 ──
langgraph new demo-agent --template new-langgraph-project-python

# 命令说明：
# demo-agent                      → 项目名称（也是目录名）
# --template                      → 指定模板
# new-langgraph-project-python    → Python 项目模板
#
# 还支持 TypeScript 模板：
# langgraph new my-agent --template new-langgraph-project-ts

# 执行过程：
# 1. 从 GitHub 下载模板项目
# 2. 将模板文件复制到本地 demo-agent/ 目录
# 3. 初始化 Git 仓库
# 4. 提示下一步操作

# 创建后的目录结构：
# demo-agent/
# ├── .env.example
# ├── .gitignore
# ├── langgraph.json
# ├── Makefile
# ├── pyproject.toml
# └── src/
#     └── agent/
#         ├── __init__.py
#         ├── graph.py
#         ├── state.py
#         ├── context.py
#         └── ...
```

### 4.4 langgraph.json 配置文件

```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./src/agent/graph.py:app"
  },
  "env": ".env",
  "python_version": "3.13",
  "dockerfile_lines": []
}
```

| 字段 | 说明 |
|------|------|
| `dependencies` | 项目依赖路径，`.` 表示当前目录 |
| `graphs` | 图的入口映射：`"图名称": "文件路径:导出变量名"` |
| `env` | 环境变量文件路径 |
| `python_version` | 指定 Python 版本（3.13+ 对 LangGraph 支持最佳） |
| `dockerfile_lines` | 自定义 Dockerfile 行（安装额外系统依赖等） |

### 4.5 本地开发模式

```bash
# ── 启动本地开发服务器 ──
# 如果用 UV 管理依赖，前面加 uv run
uv run langgraph dev

# 启动效果：
# ✓ 本地启动 API 服务（默认端口 2024）
# ✓ 自动连接到 LangSmith（云端可视化）
# ✓ 自动打开浏览器到 LangGraph Studio
# ✓ 修改代码后热重载

# 输出示例：
# 🚀 Running LangGraph API server at http://127.0.0.1:2024
# 📊 Connected to LangSmith
# 🌐 Opening LangGraph Studio...
```

---

## 五、模板工程剖析——demo-agent

### 5.1 环境变量配置（.env）

```bash
# ═══════════════════════════════════════════
#  .env 文件 —— 生产环境配置管理
#  ⚠️ .env 不应提交到 Git！加入 .gitignore
# ═══════════════════════════════════════════

# ── LangSmith 项目配置 ──
# LangSmith 中的项目名称，用于在控制台识别
LANGSMITH_PROJECT=demo-agent

# 开启 LangChain/LangGraph 调用追踪
# 设为 true 后，每一步 Agent 调用都会被记录到 LangSmith
LANGCHAIN_TRACING_V2=true

# LangSmith API 密钥（在 smith.langchain.com 免费获取）
LANGSMITH_API_KEY=lsv2_pt_your_api_key_here

# ── 大模型配置 ──
# 硅基流动（或其他模型提供商的 API Key）
SILICONFLOW_API_KEY=sk-your-api-key-here

# 模型端点（可选，使用默认即可）
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1

# ── 联网搜索工具配置 ──
# Tavily Search API Key（免费，每天有固定免费额度）
TAVILY_API_KEY=tvly-your-api-key-here

# ── 项目说明 ──
# LANGSMITH_PROJECT：可在 LangSmith 控制台看到此项目名
# LANGCHAIN_TRACING_V2：开启后所有调用自动上报 LangSmith
# 所有 API Key 从环境变量读取，绝不硬编码在代码中！
```

### 5.2 配置上下文（context.py）

```python
# ── src/agent/context.py ──
"""
配置上下文模块。
集中管理模型名称、模型参数等配置信息。
修改配置只需改这个文件，不需要动业务代码。
"""
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# ── 模型配置 ──
# 集中声明，方便切换模型时只需改这里
MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
MODEL_BASE_URL = os.getenv(
    "SILICONFLOW_BASE_URL",
    "https://api.siliconflow.cn/v1"
)
MODEL_API_KEY = os.getenv("SILICONFLOW_API_KEY")
MODEL_TEMPERATURE = 0.7
MODEL_MAX_TOKENS = 4096

# ── LangSmith 配置 ──
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "demo-agent")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")

# ── 工具配置 ──
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
```

### 5.3 State 定义（state.py）

```python
# ── src/agent/state.py ──
"""
State 类型定义模块。
定义图中所有节点共享的状态结构。
这是整个项目的"数据契约"——所有节点都依赖于这里的定义。
"""
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

# ⚠️ 注意：使用 TypedDict 而不是普通 dict
# 这样 LangGraph 和 IDE 都能提供类型检查和自动补全
class AgentState(TypedDict):
    """
    Agent 的全局状态。

    messages: 对话消息队列
        - Annotated[list, add_messages] 表示消息会累加而非覆盖
        - reducer=add_messages 是 LangGraph 内置的消息合并函数
    """
    messages: Annotated[list[BaseMessage], add_messages]
```

### 5.4 工具定义（tools.py）

```python
# ── src/agent/tools.py ──
"""
工具定义模块。
所有 Agent 可调用的工具集中在这里定义。
每个工具独立，方便单独测试和复用。
"""
from datetime import datetime
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from .context import TAVILY_API_KEY

# ── 工具1：获取当前时间 ──
@tool
def get_current_time() -> str:
    """
    获取当前的日期和时间信息。

    为什么需要这个工具？
    在进行联网检索时，如果不指定当前日期，
    搜索到的信息可能与当前日期不匹配。
    先获取当前时间，再进行联网检索，
    得到的结果更加可控和准确。
    """
    now = datetime.now()
    return (
        f"当前日期：{now.strftime('%Y年%m月%d日')}\n"
        f"当前时间：{now.strftime('%H:%M:%S')}\n"
        f"星期：{['周一','周二','周三','周四','周五','周六','周日'][now.weekday()]}"
    )

# ── 工具2：联网检索 ──
@tool
def tavily_search(query: str) -> str:
    """
    使用 Tavily 搜索引擎进行联网检索。
    当需要获取最新信息、实时数据时使用此工具。

    Args:
        query: 搜索关键词

    Returns:
        搜索结果的文本摘要
    """
    search_tool = TavilySearchResults(
        api_key=TAVILY_API_KEY,
        max_results=5,          # 最多返回 5 条结果
        search_depth="basic",   # basic 或 advanced
    )
    results = search_tool.invoke(query)
    # 格式化为易读的文本
    formatted = "\n\n".join([
        f"📎 {r.get('title', '无标题')}\n{r.get('content', '无内容')[:200]}..."
        for r in results
    ])
    return formatted
```

### 5.5 模型调用（graph.py 中的 call_model）

```python
# ── 模型调用函数 ──
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from datetime import datetime
from .context import MODEL_NAME, MODEL_BASE_URL, MODEL_API_KEY
from .state import AgentState
from .tools import get_current_time, tavily_search

# ── 绑定工具 ──
# 声明工具列表，绑定到模型
TOOLS = [get_current_time, tavily_search]

# ── 初始化模型 ──
llm = ChatOpenAI(
    model=MODEL_NAME,
    base_url=MODEL_BASE_URL,
    api_key=MODEL_API_KEY,
    temperature=0.7,
).bind_tools(TOOLS)  # ⚠️ 关键：将工具绑定到模型

# ── 系统提示词 ──
SYSTEM_PROMPT = f"""你是一个智能助手。你的能力包括：

1. **获取当前时间**：如果需要知道当前日期或时间，使用 get_current_time 工具。
2. **联网检索**：如果需要最新的信息（新闻、天气、实时数据等），使用 tavily_search 工具。
3. **一般推理**：如果不需要最新信息，直接用你的知识回答。

当前日期是 {datetime.now().strftime('%Y年%m月%d日')}。

注意：
- 回答一般性问题时，直接推理输出
- 需要最新信息时，务必先调用 tavily_search 获取最新数据
- 如果用户问的是当前时间或日期，使用 get_current_time
"""

# ── 模型调用节点 ──
def call_model(state: AgentState) -> AgentState:
    """
    调用 LLM 模型，根据对话历史生成回复或决定调用工具。

    这个函数是 Agent 的"大脑"——接收消息，返回推理结果或工具调用请求。
    """
    # 构建完整消息列表：系统提示词 + 历史对话
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}
```

### 5.6 图的组装（graph.py——链式 API）

```python
# ── src/agent/graph.py ──
"""
图的组装模块。
使用 LangGraph 的链式 API 构建图。
这种方式比之前的逐步 add_node/add_edge 更加流畅。
"""
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from .state import AgentState
from .tools import TOOLS

# ── 导入节点函数 ──
from .graph import call_model  # 或从 nodes.py 导入

# ═══════════════════════════════════════════════
#  链式 API 构建图（LangGraph 1.2+ 新特性）
# ═══════════════════════════════════════════════

# 创建 StateGraph
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(TOOLS))

# 设置入口
workflow.add_edge(START, "agent")

# 条件路由：agent 节点执行后判断是否需要调用工具
workflow.add_conditional_edges(
    "agent",
    # 路由函数：检查最后一条消息是否包含 tool_calls
    lambda state: "tools" if state["messages"][-1].tool_calls else END,
    {
        "tools": "tools",
        END: END,
    }
)

# 工具执行完后回到 agent 继续推理
workflow.add_edge("tools", "agent")

# 编译图
app = workflow.compile()
```

#### 链式 API vs 逐步式 API 对比

```python
# ── 逐步式 API（前四课使用的方式）──
graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", router, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")
app = graph.compile()

# ── 链式 API（本课使用的方式，LangGraph 1.2+）──
workflow = StateGraph(State)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
# 也可以链式调用（项目模板中的写法）：
# workflow.add_node("agent", agent_node).add_node("tools", tool_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", router, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")
app = workflow.compile()

# 两种方式本质相同，链式 API 更流畅，支持 IDE 自动补全链式调用
```

### 5.7 完整图流程图

```
            ┌─────────┐
            │  START  │
            └────┬────┘
                 ↓
          ┌─────────────┐
          │   agent     │ ← call_model：调用 LLM 推理
          │  (模型推理)  │
          └──────┬──────┘
                 ↓
          ┌─────────────┐
          │ should       │ ← 条件判断：是否有 tool_calls？
          │ continue?    │
          └──┬───────┬──┘
             ↓       ↓
        有 tool_call  无 tool_call
             ↓           ↓
      ┌─────────────┐   END
      │   tools     │ ← ToolNode 执行工具
      │ (联网/时间)  │
      └──────┬──────┘
             ↓
      回到 agent（循环）
      （工具结果交给 LLM 再推理）
```

---

## 六、LangGraph Studio——可视化开发与调试

### 6.1 什么是 LangGraph Studio

> **LangGraph Studio** 已集成到 LangSmith 平台中，提供**图形化**的 Agent 开发体验。你可以在浏览器中直观地看到图的结构、实时运行状态、每一步的输入输出。

```
LangGraph Studio 提供的能力：

📊 图形化视图  →  以可视化方式查看和编辑 Agent 流程图
▶️  单步执行    →  一步步运行，观察每个节点的输入/输出
🔍 实时调试    →  精确到节点级别的故障定位
📝 历史记录    →  查看每一次调用的完整执行链路
🔄 热重载      →  修改代码后自动刷新图结构
```

### 6.2 启动 Studio 开发模式

```bash
# ── 在项目根目录下运行 ──
# 如果使用 UV 管理依赖
uv run langgraph dev

# 启动后：
# 1. 本地启动 API 服务器（默认 http://127.0.0.1:2024）
# 2. 自动连接到 LangSmith 平台
# 3. 自动打开浏览器到 LangGraph Studio 界面
# 4. 图的定义同步到云端可视化展示

# 关键输出信息：
# 🚀 LangGraph API: http://127.0.0.1:2024
# 📊 LangSmith Tracing: Enabled
# 🌐 Opening LangSmith Studio...
```

### 6.3 Studio 界面功能

```
┌─────────────────────────────────────────────────────────┐
│  LangGraph Studio 界面布局                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐  ┌──────────────────────────────────┐  │
│  │  图结构面板   │  │         执行详情面板               │  │
│  │             │  │                                  │  │
│  │  START      │  │  当前节点：agent                   │  │
│  │   ↓        │  │  输入：[SystemMessage, HumanMsg]  │  │
│  │  agent ──→ │  │  输出：[AIMessage(tool_calls)]    │  │
│  │   ↓   ↓   │  │  Token 消耗：1,234                  │  │
│  │  END tools │  │  延迟：2.3s                         │  │
│  │   ↑___↓   │  │                                  │  │
│  │             │  │  调用栈：                          │  │
│  │  图例：      │  │  agent → tools → agent → END     │  │
│  │  实线=固定边 │  │                                  │  │
│  │  虚线=条件边 │  │                                  │  │
│  └─────────────┘  └──────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  输入区域                                          │   │
│  │  ┌────────────────────────────────────────────┐  │   │
│  │  │ 输入消息...                    [发送]       │  │   │
│  │  └────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 6.4 Studio 调试实战流程

```
调试流程：

Step 1: 在 Studio 中输入测试消息
    └── 例如："今天天气怎么样？"

Step 2: 观察图的执行路径
    └── 哪个节点高亮 = 当前执行到哪个节点
        观察条件边的分支走向（虚线的哪条实线）

Step 3: 查看节点的输入/输出
    └── 点击高亮节点 → 右侧面板显示详细的输入输出数据
        检查 prompt 是否正确、tool_calls 是否完整

Step 4: 发现异常时定位
    └── 节点变红 = 执行出错
        右侧面板显示错误堆栈和具体原因

Step 5: 修改代码后热重载
    └── 保存 Python 文件 → Studio 自动刷新图结构
        不需要重启服务

Step 6: 重新测试
    └── 再次输入相同消息 → 观察修复是否生效
```

---

## 七、LangSmith——云端部署与全链路追踪

### 7.1 LangSmith 平台概述

> **LangSmith**（smith.langchain.com）是 LangGraph 生态中的**云端监控和部署平台**。它提供免费额度，适合开发和小规模生产使用。

```
LangSmith 三大核心能力：

┌─────────────────────────────────────────────────────┐
│                                                     │
│  1️⃣  LangGraph Studio（可视化开发）                   │
│      └── 图的图形化查看、单步调试、热重载             │
│                                                     │
│  2️⃣  LangSmith Deploy（云端部署）                     │
│      ├── 自动生成 REST API 端点                      │
│      ├── WebSocket 支持流式输出                      │
│      ├── 内置认证机制（API Key）                     │
│      └── Docker / K8s 灵活部署                      │
│                                                     │
│  3️⃣  LangSmith Tracing（全链路追踪）                  │
│      ├── 每一步执行的输入/输出追踪                    │
│      ├── Token 用量统计                             │
│      ├── 延迟分析（每个节点耗时）                     │
│      ├── 成本核算（按模型、按项目）                   │
│      └── 错误定位与告警                              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 7.2 Tracing——全链路追踪详解

> 当你在 `.env` 中设置了 `LANGCHAIN_TRACING_V2=true`，每一步 Agent 调用都会自动上报到 LangSmith。

#### 追踪信息的层次

```
一次 Agent 调用的完整追踪记录：

📋 Run: "2025年意大利超级杯冠军是谁？"
├── 🔵 agent (LLM 调用)
│   ├── 输入: [SystemMessage, HumanMessage]
│   ├── 输出: AIMessage(tool_calls=[tavily_search])
│   ├── Token: 输入 456 + 输出 32 = 488
│   ├── 延迟: 1.2s
│   └── 模型: Qwen/Qwen2.5-3B-Instruct
│
├── 🟢 tools (工具调用)
│   ├── 工具: tavily_search
│   ├── 输入: {"query": "2025年意大利超级杯冠军"}
│   ├── 输出: "那不勒斯赢得2025年意大利超级杯..."
│   ├── Token: 0（工具调用不消耗 Token）
│   └── 延迟: 2.1s
│
├── 🔵 agent (LLM 第二次调用)
│   ├── 输入: [..., ToolMessage(搜索结果)]
│   ├── 输出: AIMessage("2025年意大利超级杯冠军是那不勒斯...")
│   ├── Token: 输入 890 + 输出 156 = 1046
│   ├── 延迟: 1.8s
│   └── 模型: Qwen/Qwen2.5-3B-Instruct
│
└── ⚪ should_continue
    └── 决策: END（无需继续）

总计：Token 1,534 | 延迟 5.1s | 工具调用 1 次 | LLM 调用 2 次
```

### 7.3 LangSmith 控制台关键指标

| 指标 | 说明 | 如何使用 |
|------|------|----------|
| **总调用次数** | 一段时间内的 Agent 调用总量 | 评估系统负载，决定是否需要扩容 |
| **平均响应时间** | 端到端延迟（用户等待时间） | SLA 监控，超时告警 |
| **Token 消耗** | 按模型/按项目的 Token 用量 | 成本控制，选择更具性价比的模型 |
| **错误率** | 失败调用占总调用的比例 | 系统健康度指标，异常告警 |
| **工具调用成功率** | 工具节点执行成功的比例 | 外部依赖可靠性监控 |
| **条件路由分布** | 各种条件分支被命中的频率 | 了解用户行为模式 |

### 7.4 部署到 LangSmith

```bash
# ── 方法一：通过 LangSmith UI 部署 ──
# 1. 在 smith.langchain.com 创建 Deployment
# 2. 关联 GitHub 仓库（或上传 Docker 镜像）
# 3. 配置环境变量
# 4. 一键部署

# ── 方法二：通过 CLI 构建 Docker 镜像 ──
# 将项目构建为 Docker 镜像
langgraph build

# 输出：
# ✓ 构建完成 → demo-agent:latest
# 镜像可以推送到任何容器注册中心
# 然后在 LangSmith 中关联此镜像

# ── 方法三：自定义 Dockerfile ──
# 生成 Dockerfile
langgraph dockerfile

# 输出：
# ✓ Dockerfile 生成于 ./Dockerfile
# 可以基于此自定义构建流程
```

### 7.5 部署后的 API 调用

```python
# ── 部署到 LangSmith 后，自动生成 API 端点 ──
# REST API 调用示例
import requests

API_URL = "https://api.smith.langchain.com/v1/agents/your-agent/invoke"
API_KEY = "lsv2_pt_your_key"

response = requests.post(
    API_URL,
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "input": {
            "messages": [
                {"role": "user", "content": "2025年超级杯冠军是谁？"}
            ]
        },
        "config": {
            "configurable": {
                "thread_id": "user-session-001"  # 保持会话上下文
            }
        }
    }
)

print(response.json())
```

```javascript
// ── WebSocket 流式调用（打字机效果）──
const ws = new WebSocket(
  "wss://api.smith.langchain.com/v1/agents/your-agent/stream"
);

ws.onopen = () => {
  ws.send(JSON.stringify({
    input: {
      messages: [{ role: "user", content: "讲个笑话" }]
    },
    config: { configurable: { thread_id: "ws-demo" } },
    stream_mode: ["messages"]  // Token 级流式输出
  }));
};

ws.onmessage = (event) => {
  const chunk = JSON.parse(event.data);
  // 逐 Token 显示，实现打字机效果
  process.stdout.write(chunk.content);
};
```

---

## 八、实战演练——从零到部署完整链路

### 8.1 实战目标

> 用 LangGraph CLI 创建项目 → 配置联网搜索 Agent → 本地 dev 模式调试 → LangSmith 全链路追踪。

### 8.2 Step 1：安装 CLI 并创建项目

```bash
# ── 安装 LangGraph CLI（全局）──
uv tool install langgraph-cli

# ── 创建新项目 ──
langgraph new demo-agent --template new-langgraph-project-python

# ── 进入项目 ──
cd demo-agent
```

### 8.3 Step 2：配置 .env 文件

```bash
# .env
LANGSMITH_PROJECT=demo-agent
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=lsv2_pt_xxxxxxxxxxxxx

SILICONFLOW_API_KEY=sk-xxxxxxxxxxxxx
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1

TAVILY_API_KEY=tvly-xxxxxxxxxxxxx
```

### 8.4 Step 3：完善代码

按照[第五章](#五模板工程剖析demo-agent)中的代码结构，完善以下文件：

| 文件 | 内容 |
|------|------|
| `src/agent/state.py` | AgentState 定义（messages + add_messages） |
| `src/agent/context.py` | 加载 .env，导出配置常量 |
| `src/agent/tools.py` | get_current_time + tavily_search 两个工具 |
| `src/agent/graph.py` | call_model + graph 定义 + compile |

### 8.5 Step 4：本地开发调试

```bash
# ── 启动本地开发模式 ──
uv run langgraph dev

# 浏览器自动打开 LangGraph Studio
# 在 Studio 中输入测试消息，观察执行流程
```

#### 测试用例

```
测试 1：一般性问题（不走 tools）
   输入："你好，请介绍一下你自己"
   预期：直接走 agent → END，不经过 tools 节点

测试 2：需要联网检索（走 tools → agent → END）
   输入："2025年意大利超级杯冠军是谁？"
   预期：agent → tools(tavily_search) → agent → END
         最终回答：那不勒斯

测试 3：需要时间信息（走 tools → agent → END）
   输入："今天几号？星期几？"
   预期：agent → tools(get_current_time) → agent → END

测试 4：需要最新信息的复杂问题（多轮 tools 调用可能）
   输入："Jimeng 3 最厉害的特点是什么？和上一个版本比有什么提升？"
   预期：agent → tools(tavily_search) → agent → (可能再调 tools) → END
```

### 8.6 Step 5：在 LangSmith 中查看追踪

```
1. 打开 smith.langchain.com 登录
2. 在左侧 Project 列表中找到 "demo-agent"
3. 点击进入 → 看到所有调用的列表
4. 点击任意一次调用 → 查看详细追踪信息：
   ├── 执行路径（agent → tools → agent → END）
   ├── 每步的输入/输出
   ├── Token 消耗明细
   ├── 延迟分解
   └── 使用的模型和参数
5. 对比不同调用的性能和成本
```

### 8.7 演示案例执行效果

```
══════════════════════════════════════════
  LangGraph 生产环境演示 —— demo-agent
══════════════════════════════════════════

📋 输入："你好，你能做什么？"

执行路径：agent ──→ END
说明：一般性问题，LLM 直接推理回答，不调用工具

──────────────────────────────────────────

📋 输入："2025年意大利超级杯冠军是谁？"

执行路径：
  agent ──→ tools(tavily_search) ──→ agent ──→ END
     │              │                      │
     │              │                      └── "冠军是那不勒斯"
     │              └── 搜索"2025意大利超级杯"...
     └── 判断需要联网检索 → 调用 tavily_search

Trace 信息（在 LangSmith 中查看）：
  • agent 第1次调用：456 input + 32 output tokens
  • tavily_search 工具调用：搜索返回 5 条相关结果
  • agent 第2次调用：890 input + 156 output tokens
  • 总计 Token：1,534 | 延迟：5.1s
```

---

## 九、生产环境 checklist

### 9.1 上线前检查清单

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  ✅ 代码层面                                     │
│  ├── State / Tools / Nodes / Graph 分离         │
│  ├── .env 文件不提交到 Git（已加入 .gitignore）   │
│  ├── 所有 API Key 从环境变量读取                 │
│  ├── 模型参数集中在 context.py 管理              │
│  └── 代码已通过单元测试和集成测试                   │
│                                                 │
│  ✅ 配置层面                                     │
│  ├── LANGCHAIN_TRACING_V2=true                  │
│  ├── LANGSMITH_PROJECT 正确设置                  │
│  ├── 生产环境的 API Key 与开发环境分开            │
│  └── 模型 endpoint 指向生产服务                   │
│                                                 │
│  ✅ 部署层面                                     │
│  ├── langgraph.json 配置正确                     │
│  ├── Python 版本 >= 3.13                        │
│  ├── Docker 镜像构建成功                         │
│  ├── 容器健康检查配置到位                         │
│  └── 日志输出配置标准格式（JSON lines）           │
│                                                 │
│  ✅ 监控层面                                     │
│  ├── LangSmith Tracing 已启用                    │
│  ├── 关键指标已配置告警（错误率/延迟/成本）        │
│  ├── API 端点有认证保护                          │
│  └── 定期检查 Token 消耗和成本                    │
│                                                 │
│  ✅ 安全层面                                     │
│  ├── API Key 定期轮换                           │
│  ├── 敏感数据不记录到日志                         │
│  ├── 用户输入做安全过滤                           │
│  └── 工具调用权限最小化                           │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 9.2 Python 版本选择

| Python 版本 | LangGraph 兼容性 | 建议 |
|:----------:|:--------------:|:----:|
| 3.10 | 基本支持 | ⚠️ 建议升级 |
| 3.11 | 支持 | ✅ 可用 |
| 3.12 | 良好支持 | ✅ 可用 |
| **3.13+** | **最佳支持** | **⭐ 推荐** |

> LangGraph 项目模板默认推荐 Python 3.13+，因为 3.13 版本对 LangGraph 的异步执行和类型系统有更好的支持。

### 9.3 密钥管理最佳实践

```bash
# ✅ 推荐：用 .env 文件（本地开发）+ 环境变量注入（生产）
# .env 文件仅在本地开发使用，不提交到 Git

# 生产环境注入方式：
# ── Docker ──
docker run -e LANGSMITH_API_KEY=xxx ...

# ── Kubernetes ──
# 使用 Secret 资源 + envFrom

# ── CI/CD ──
# 在 CI 变量中设置，运行时注入

# ❌ 绝对禁止
# 1. 将 API Key 硬编码在代码中
# 2. 将 .env 文件提交到 Git
# 3. 在日志中打印 API Key
# 4. 通过 URL 参数传递 API Key
```

---

## 十、常见问题与排错指南

### 10.1 错误速查表

| 错误信息 | 原因 | 解决方法 | 优先级 |
|----------|------|----------|:------:|
| `langgraph: command not found` | CLI 未安装或未在 PATH 中 | `uv tool install langgraph-cli` 或检查 PATH | 🔴 高 |
| `ModuleNotFoundError: No module named 'agent'` | Python 路径问题 | 确认在项目根目录运行；检查 `langgraph.json` 中的路径 | 🔴 高 |
| LangSmith 中没有追踪数据 | `LANGCHAIN_TRACING_V2` 未设为 `true` 或 API Key 无效 | 检查 `.env` 文件；确认 `LANGSMITH_API_KEY` 正确 | 🔴 高 |
| `Connection refused` 访问 LangGraph Studio | 本地 API 服务未启动 | 运行 `uv run langgraph dev` 并确认端口 2024 未被占用 | 🟡 中 |
| Docker 构建失败 | 依赖冲突或 Python 版本不兼容 | 检查 `pyproject.toml` 中的依赖版本；确认 Python >= 3.13 | 🟡 中 |
| 工具调用失败 | API Key 未配置或网络问题 | 检查对应工具的 API Key（如 TAVILY_API_KEY） | 🟡 中 |
| Studio 中图不对 | 代码修改后未重启 | Studio 支持热重载，但有时需手动刷新浏览器 | 🟢 低 |
| Token 消耗异常高 | 系统提示词太长或对话历史过多 | 精简提示词；使用 Summary 记忆压缩历史 | 🟢 低 |

### 10.2 排查流程

```
LangGraph 生产环境问题排查流程：

Step 1: 确认 CLI 和环境
    ├── langgraph --version（确认 CLI 版本）
    ├── python --version（确认 >= 3.13）
    └── uv --version（确认包管理器可用）

Step 2: 确认本地能跑
    ├── cd 项目目录
    ├── python -c "from src.agent.graph import app; print('OK')"
    └── 确保 import 不报错

Step 3: 确认 dev 模式正常
    ├── uv run langgraph dev
    ├── 浏览器中打开 Studio
    └── 输入简单测试消息，观察执行

Step 4: 确认 LangSmith 连接
    ├── 登录 smith.langchain.com
    ├── 检查 Project 列表是否有你的项目
    └── 确认有追踪数据进入

Step 5: 确认线上部署
    ├── langgraph build（构建 Docker 镜像）
    ├── 检查镜像大小和构建日志
    └── 部署后测试 API 端点
```

### 10.3 常见陷阱

**陷阱一：.env 文件提交到了 Git**

```bash
# ❌ 危险：包含 API Key 的 .env 被提交
# 任何人 clone 仓库都能看到你的密钥！

# ✅ 正确：
# 1. .gitignore 中确保有 .env
echo ".env" >> .gitignore

# 2. 提供 .env.example 模板（不含真实密钥）
# .env.example:
# LANGSMITH_API_KEY=your_api_key_here
# SILICONFLOW_API_KEY=your_api_key_here
```

**陷阱二：开发环境 API Key 与生产环境混用**

```bash
# ❌ 开发和生产用同一套 Key
# 开发时疯狂测试 → 额度用完 → 生产环境挂了！

# ✅ 开发和生成使用不同的 API Key
# .env.dev（开发）
SILICONFLOW_API_KEY=sk-dev-xxxxxxxx

# .env.prod（生产）
SILICONFLOW_API_KEY=sk-prod-xxxxxxxx
```

**陷阱三：忘记开启 Tracing**

```bash
# ❌ .env 中没有设置 LANGCHAIN_TRACING_V2
# Agent 在生产运行，但 LangSmith 中什么也看不到

# ✅ 务必设置
LANGCHAIN_TRACING_V2=true
```

---

## 十一、课后练习

### 练习一：项目结构搭建（⭐）

**目标**：将前几课的一个 Agent 重构为标准项目结构

**场景**：把"03 人机协作与时间旅行"中的内容审核 Agent 拆分为标准项目。

**要求**：
- 创建 `content_review/` 项目目录
- 拆分为 `state.py`, `tools.py`, `nodes.py`, `graph.py`, `context.py`
- 配置 `.env` 管理 API Key
- 确保重构后功能不变

**验收标准**：
- 文件拆分后 import 关系正确
- `python -c "from content_review.graph import app"` 不报错
- 重构后与原版行为完全一致

### 练习二：LangGraph CLI 操作（⭐⭐）

**目标**：用 CLI 创建、配置和运行项目

**要求**：
- 用 `langgraph new` 创建项目
- 配置 `.env` 文件
- 用 `uv run langgraph dev` 启动本地开发
- 在 LangGraph Studio 中输入消息并观察执行

**验收标准**：
- Studio 中能正确显示图结构
- 输入消息能正常执行并返回结果
- LangSmith 中有对应的追踪记录

### 练习三：工具扩展（⭐⭐⭐）

**目标**：为 demo-agent 添加自定义工具

**要求**：
- 添加一个"天气查询"工具（模拟城市→天气的映射）
- 添加一个"货币转换"工具（简单汇率计算）
- 更新系统提示词，让 LLM 知道何时使用这些工具
- 在 Studio 中测试新工具是否被正确调用

**验收标准**：
- 问"北京今天天气怎么样"→ 调用天气工具
- 问"100 美元等于多少人民币"→ 调用货币转换工具
- LangSmith 追踪中能看到工具调用记录

### 练习四：多项目追踪对比（⭐⭐⭐）

**目标**：创建两个不同的 Agent 项目，对比追踪数据

**要求**：
- 项目 A：简单问答 Agent（无工具）
- 项目 B：联网搜索 Agent（有 tavily_search 工具）
- 分别配置不同的 `LANGSMITH_PROJECT` 名称
- 对两个项目分别输入相同问题，对比追踪数据

**验收标准**：
- LangSmith 中两个项目的追踪数据分开显示
- 能对比两个 Agent 的 Token 消耗、延迟、执行路径
- 写出对比分析报告

### 练习五：综合实战——企业客服 Agent（⭐⭐⭐⭐）

**目标**：构建一个完整的企业级客服 Agent 并部署

**场景**：一个电商客服 Agent，能回答订单查询、退款进度、产品咨询。

**要求**：
1. **标准项目结构**：state / tools / nodes / graph / context 分离
2. **工具集成**：
   - `query_order(order_id)`：查询订单状态
   - `check_refund(refund_id)`：查询退款进度
   - `search_product(query)`：查询产品信息
   - `get_current_time()`：获取当前时间
3. **Supervisor 路由**：根据用户意图分发到不同工具
4. **本地 dev 调试**：在 Studio 中测试
5. **LangSmith 追踪**：确认全链路数据完整
6. **文档**：写一份简单的 README 说明部署方式

**验收标准**：
- 能正确识别"我的订单 12345 到哪了"→ 调用订单查询工具
- 能正确识别"退款什么时候到账"→ 调用退款查询工具
- 能正确识别"你们有蓝牙耳机吗"→ 调用产品搜索工具
- LangSmith 追踪完整，能看到每一步的执行细节
- API 端点对外可调用

---

## 十二、课程小结

### 12.1 核心知识图谱

```
┌──────────────────────────────────────────────────────────────┐
│    LangGraph 05——从原型到生产，构建企业级应用 核心知识体系        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1️⃣  生产环境全景                                             │
│      ├── 五层架构：代码组织 → 测试保障 → 可视化 → 部署 → 监控   │
│      ├── 工具链：CLI + Studio + LangSmith + Docker + UV      │
│      └── 从原型到生产的六大跨越                                │
│                                                              │
│  2️⃣  标准化项目结构                                           │
│      ├── state.py：统一 State 定义（数据契约）                  │
│      ├── context.py：集中配置管理                              │
│      ├── tools.py：工具集中定义                                │
│      ├── nodes.py：节点业务逻辑                                │
│      ├── graph.py：图组装（链式 API）                          │
│      └── .env：环境变量（不提交 Git）                          │
│                                                              │
│  3️⃣  LangGraph CLI                                           │
│      ├── langgraph new：基于模板创建项目                       │
│      ├── langgraph dev：本地开发 + Studio 连接                 │
│      ├── langgraph build：构建 Docker 镜像                    │
│      └── langgraph up：启动完整服务栈                          │
│                                                              │
│  4️⃣  LangGraph Studio                                        │
│      ├── 图形化查看图的节点和边                                │
│      ├── 单步执行调试                                         │
│      ├── 实时查看中间状态                                     │
│      └── 热重载（改代码自动刷新）                              │
│                                                              │
│  5️⃣  LangSmith 平台                                          │
│      ├── Tracing：每一步的输入/输出/Token/延迟                 │
│      ├── Deploy：自动生成 API 端点 + WebSocket                │
│      ├── Monitor：性能/成本/错误率指标                        │
│      └── Free Tier：免费额度，开发和小规模生产可用              │
│                                                              │
│  6️⃣  实战——demo-agent                                         │
│      ├── 联网搜索 + 时间感知 Agent                             │
│      ├── CLI 创建 → 配置 → 完善代码 → dev 调试                │
│      ├── Studio 中测试三种场景（一般/联网/时间）                │
│      └── LangSmith 中查看完整追踪链路                          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 12.2 一句话总结

> **LangGraph 05 是连接"代码"与"产品"的桥梁**——通过标准化项目结构让代码可维护、可协作，通过 LangGraph CLI 实现一键创建和构建，通过 LangGraph Studio 实现可视化开发和调试，通过 LangSmith 实现云端部署和全链路可观测，最终将前四课学到的所有 Agent 能力转化为可上线、可监控、可迭代的企业级产品。

### 12.3 关键命令速查

| 命令/配置 | 用途 |
|-----------|------|
| `uv tool install langgraph-cli` | 安装 CLI |
| `langgraph new <name> --template new-langgraph-project-python` | 创建项目 |
| `uv run langgraph dev` | 启动本地开发 |
| `langgraph build` | 构建 Docker 镜像 |
| `LANGCHAIN_TRACING_V2=true` | 开启全链路追踪 |
| `LANGSMITH_PROJECT=项目名` | 指定 LangSmith 项目 |
| `LANGSMITH_API_KEY=lsv2_...` | LangSmith API 密钥 |

### 12.4 LangGraph 系列课程全览

```
LangChain 系列（18课）→ 模型调用、提示词、链式调用、Agent 基础
                          ↓
LangGraph 系列（5课）  → Agent 编排、状态持久化、多智能体、生产部署
    ├── 00 开篇                      ✅  系列总览与课程体系
    ├── 01 核心概念与入门              ✅  State/Node/Edge/Graph
    ├── 02 状态持久化与记忆            ✅  Checkpoint/Durable Execution/Memory
    ├── 03 人机协作与时间旅行          ✅  Streaming/interrupt/TimeTravel
    ├── 04 构筑多智能体协作系统         ✅  Subgraph/四种协作模式
    └── 05 从原型到生产                 ✅ 🆕  ← 你在这里（最终课）

每一课的能力递进：

  01: 能跑起来     ──→  02: 能记住、能恢复
       ↓                        ↓
  03: 人能参与、能回溯          04: 多引擎协同
       ↓                        ↓
  05: 能上线、能监控 ────────────┘

从 01 的"Hello World"到 05 的"企业级部署"，
你已经掌握了 LangGraph 的完整能力栈。
```

### 12.5 后续学习建议

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  📚 深入学习方向：                                            │
│                                                             │
│  1. LangGraph 官方文档（最新版本）                             │
│     └── 关注新版本的特性和 API 变化                           │
│                                                             │
│  2. LangSmith 高级功能                                       │
│     ├── 自定义 Evaluator（自动评估 Agent 输出质量）           │
│     ├── Dataset 管理（测试用例集）                            │
│     └── A/B 实验（对比不同模型和提示词效果）                   │
│                                                             │
│  3. 性能优化                                                 │
│     ├── 并行节点优化                                         │
│     ├── Checkpoint 存储选型（Postgres vs Redis）             │
│     └── 缓存策略（减少重复 LLM 调用）                         │
│                                                             │
│  4. 安全加固                                                 │
│     ├── 用户输入过滤和敏感信息脱敏                            │
│     ├── 工具调用权限控制                                     │
│     └── API 端点限流和认证                                   │
│                                                             │
│  5. 综合实战（关注老师后续课程）                               │
│     └── LangChain + LangGraph 综合实战项目                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

*本教学文档基于陈泽鹏老师视频课程整理编写。*
*本文档涵盖 LangGraph v1.2 生产环境的标准化项目结构、LangGraph CLI 工具链使用、LangGraph Studio 可视化开发调试、LangSmith 云端部署与全链路追踪，并以联网搜索 Agent（demo-agent）为实战案例完成从原型到生产的完整链路演示。*
