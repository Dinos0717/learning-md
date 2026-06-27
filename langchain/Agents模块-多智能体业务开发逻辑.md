# Agents 模块——多智能体业务开发逻辑

> 基于陈泽鹏老师视频课程整理编写 · 2026年6月26日

---

## 目录

- [一、本节概述与学习目标](#一本节概述与学习目标)
- [二、为什么需要多 Agent——单 Agent 的困境](#二为什么需要多-agent单-agent-的困境)
- [三、系统 Agent 架构全景图](#三系统-agent-架构全景图)
- [四、Agent 目录结构与文件清单](#四agent-目录结构与文件清单)
- [五、Router Agent——意图识别的全局单例](#五router-agent意图识别的全局单例)
- [六、Chat Agent——ReAct 模式 + 工具 + 记忆](#六chat-agentreact-模式--工具--记忆)
- [七、Meeting Agent——简约的结构化输出](#七meeting-agent简约的结构化输出)
- [八、Tools 工具集——Agent 的手和脚](#八tools-工具集agent-的手和脚)
- [九、Factory 工厂模式——Agent 的创建策略](#九factory-工厂模式agent-的创建策略)
- [十、完整工作流程——从输入到回复](#十完整工作流程从输入到回复)
- [十一、与 Session/Memory 模块的集成](#十一与-sessionmemory-模块的集成)
- [十二、如何新增一个 Agent](#十二如何新增一个-agent)
- [十三、测试 Agent 模块](#十三测试-agent-模块)
- [十四、常见问题与排错指南](#十四常见问题与排错指南)
- [十五、课后练习](#十五课后练习)
- [十六、本节小结](#十六本节小结)

---

## 一、本节概述与学习目标

### 1.1 本节定位

> 这是「多 Agent 开发实战」系列中**最核心的一课**。前面所有模块——Core（配置）、Schema（数据格式）、Memory（记忆）、Session（会话管理）——都是为 Agent 层服务的。本课把所有这些模块**串联起来**，实现三个具有不同能力的智能体，并让它们按照统一的工作流程协同工作。

```
┌─────────────────────────────────────────┐
│           本系列课程体系                   │
├─────────────────────────────────────────┤
│                                         │
│  开篇：课程总览                           │
│  第1课：为什么学 + 范式转变                │
│  第2课：架构总览                          │
│  第3课：Core 模块精讲                     │
│  第4课：Schema 模块                      │
│  第5课：Memory 模块                      │
│  第6课：Session 模块                     │
│  第7课（本节）：Agents 模块  ← 你在这里     │
│  后续课程：Service 部署 → 生产环境         │
│                                         │
│  本课是所有模块的"汇合点"                  │
│                                         │
└─────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────────┐
│                    架构层级（从下往上）                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  入口层 (run_agent.py / run_service.py)                      │
│      ↑ 调用                                                  │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Agents 层（本课）  ← 核心业务逻辑                 │       │
│  │  • router_agent.py：意图识别（全局单例）           │       │
│  │  • chat_agent.py：ReAct 对话（每会话独立）         │       │
│  │  • meeting_agent.py：纪要整理（全局单例）          │       │
│  │  • agent_factory.py：工厂创建 + 全局管理           │       │
│  │  • tools.py：工具函数集合                         │       │
│  │  • prompts/：各 Agent 的提示词模板                │       │
│  │                                                  │       │
│  │  依赖：Session + Memory + Schema + Core           │       │
│  └──────────────────────────────────────────────────┘       │
│      ↑ 依赖                                                  │
│  Session 层 → Memory 层 → Schema 层 → Core 层               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 前情回顾

在之前的课程中，我们已经完成了所有基础设施：

| 模块 | 关键能力 | Agent 怎么用它 |
|---|---|---|
| **Core** | `get_llm()` 获取大模型实例 | Agent 调用 LLM 的核心方法 |
| **Schema** | `RouterDecision`、`MeetingSummary` 等数据结构 | Agent 的输出格式定义 |
| **Memory** | `MemoryManager`——记忆的存储与检索 | Chat Agent 维持多轮对话上下文 |
| **Session** | `SessionManager`——会话隔离与生命周期 | 每个会话窗口绑定独立 Memory |

> 本课的任务：用这些积木搭建出三个真正能工作的 Agent。

### 1.3 本课要掌握的目标

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  目标一：理解多 Agent 架构的设计理念                       │
│         ├── 为什么不用一个 Agent 做所有事                 │
│         ├── 路由 Agent → 子 Agent 的分发模式             │
│         └── 全局单例 vs 每会话创建的决策依据              │
│                                                         │
│  目标二：掌握三种 Agent 的实现方式                         │
│         ├── Router Agent：结构化输出 + 全局单例           │
│         ├── Chat Agent：ReAct 模式 + 工具 + 记忆         │
│         └── Meeting Agent：纯结构化输出（无状态）         │
│                                                         │
│  目标三：掌握 Agent 工厂模式                              │
│         ├── 为什么 Router/Meeting 用全局单例             │
│         ├── 为什么 Chat 需要每会话创建                   │
│         └── Factory 的统一创建接口                       │
│                                                         │
│  目标四：理解完整的请求处理流程                           │
│         ├── 用户输入 → Router → Chat/Meeting             │
│         ├── Session 如何与 Agent 联动                    │
│         └── 如何新增一个自定义 Agent                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 二、为什么需要多 Agent——单 Agent 的困境

### 2.1 把所有任务交给一个 Agent 会怎样？

想象一下，如果只有一个 Agent 处理所有事情：

```
┌─────────────────────────────────────────────────────────┐
│              单一巨型 Agent 的问题                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  一个 prompt 要同时处理：                                 │
│  ├── 意图判断："用户这句话是想聊天还是整理会议纪要？"      │
│  ├── 闲聊对话："用友好的语气回复用户"                     │
│  ├── 工具调用："需要查日期吗？需要计算吗？"               │
│  ├── 会议纪要："提取标题、日期、参会人、行动项..."        │
│  ├── 记忆管理："记住之前说了什么"                         │
│  └── 格式输出："按 JSON/Markdown 输出"                   │
│                                                         │
│  问题：                                                  │
│  😰 prompt 超级长 → Token 消耗大                        │
│  😰 判断逻辑混乱 → Agent 容易"迷失方向"                  │
│  😰 某个能力需要调整 → 整个 prompt 都要改                │
│  😰 难以测试 → 不知道哪个环节出了问题                    │
│  😰 维护困难 → 改动一处可能影响全局                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.2 多 Agent 分工的核心理念

> **不同的事情交给不同的"专业人士"。** 就像公司里有不同的部门——前台负责接待（路由），客服负责聊天（对话），秘书负责记录（会议纪要）。每个角色专注做好自己的事。

```
┌─────────────────────────────────────────────────────────┐
│              多 Agent 分工的优势                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1️⃣  职责单一：每个 Agent 只做一件事，容易做好           │
│                                                         │
│  2️⃣  独立维护：改 Chat Agent 不影响 Meeting Agent       │
│                                                         │
│  3️⃣  灵活扩展：加新 Agent 只需新增一个类 + 注册到工厂    │
│                                                         │
│  4️⃣  独立测试：可以单独测试每个 Agent 的功能             │
│                                                         │
│  5️⃣  差异化设计：不同 Agent 用不同模式                   │
│      ├── 路由 Agent：极简（只做意图判断）                 │
│      ├── 对话 Agent：复杂（ReAct + 工具 + 记忆）          │
│      └── 会议 Agent：中等（结构化输出）                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 三、系统 Agent 架构全景图

### 3.1 三个 Agent 的协作关系

```
                          客户端请求
                              │
                              ▼
                    ┌──────────────────┐
                    │   Router Agent    │
                    │   (路由智能体)     │
                    │                  │
                    │  职责：意图识别    │
                    │  模式：结构化输出   │
                    │  实例：全局单例    │
                    │  状态：无状态     │
                    └──────┬───────────┘
                           │
              intent=chat  │  intent=meeting_notes
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
   ┌──────────────────┐    ┌──────────────────────┐
   │   Chat Agent      │    │   Meeting Agent       │
   │   (对话智能体)     │    │   (会议纪要智能体)      │
   │                   │    │                       │
   │  职责：多轮对话    │    │  职责：结构化整理会议   │
   │  模式：ReAct       │    │  模式：结构化输出      │
   │  实例：每会话创建   │    │  实例：全局单例       │
   │  状态：有状态      │    │  状态：无状态          │
   │                   │    │                       │
   │  能力：            │    │  能力：               │
   │  ├── 记忆          │    │  ├── 结构化输出       │
   │  ├── 工具调用      │    │  └── Markdown 格式化  │
   │  └── 思考+反思     │    │                       │
   └──────────────────┘    └──────────────────────┘
```

### 3.2 三种 Agent 对比

| 维度 | Router Agent | Chat Agent | Meeting Agent |
|---|---|---|---|
| **核心职责** | 意图识别 | 多轮对话 | 会议纪要整理 |
| **实现复杂度** | ⭐ 简单 | ⭐⭐⭐ 复杂 | ⭐⭐ 中等 |
| **底层模式** | 结构化输出 | ReAct Agent | 结构化输出 |
| **是否需要记忆** | ❌ 无状态 | ✅ 有状态 | ❌ 无状态（当前版本） |
| **是否需要工具** | ❌ | ✅ | ❌（可扩展） |
| **实例化策略** | 全局单例 | **每会话创建** | 全局单例 |
| **核心方法** | `decide(message)` | `invoke(message)` | `summarize(content)` |
| **输出类型** | `RouterDecision` | `str`（AI 回复文本） | `MeetingSummary` |

### 3.3 为什么 Router 和 Meeting 用全局单例，Chat 却每会话创建？

```
┌─────────────────────────────────────────────────────────┐
│          实例化策略的决策逻辑                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Router Agent → 全局单例 ✅                              │
│  原因：                                                  │
│  ├── 没有记忆，不需要"记住"不同用户                       │
│  ├── 每个请求的处理完全独立（只看当前输入做意图判断）     │
│  ├── 一个实例服务所有请求就够了                           │
│  └── 节省资源，不需要反复创建销毁                         │
│                                                         │
│  Meeting Agent → 全局单例 ✅                              │
│  原因：                                                  │
│  ├── 当前设计是一次性输入（无记忆）                       │
│  ├── 不需要区分不同用户                                  │
│  └── 一个实例处理所有整理请求                             │
│                                                         │
│  Chat Agent → 每会话创建 ✅                               │
│  原因：                                                  │
│  ├── 有记忆！不同会话需要不同的 Memory                    │
│  ├── 每个 session_id → 独立的 Memory → 独立的 Agent     │
│  ├── Agent 需要绑定特定会话的 MemoryManager              │
│  └── 不同用户的对话内容不能混淆                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 四、Agent 目录结构与文件清单

```
SRC/agents/
├── __init__.py
├── router_agent.py          # 路由 Agent——意图识别
├── chat_agent.py            # 对话 Agent——ReAct 模式
├── meeting_agent.py         # 会议纪要 Agent——结构化输出
├── agent_factory.py         # 工厂函数——统一创建入口
├── tools.py                 # 工具函数集合（被 Chat Agent 调用）
└── prompts/
    ├── __init__.py
    ├── router_prompts.py    # 路由 Agent 的系统/用户提示词
    ├── chat_prompts.py      # 对话 Agent 的系统提示词
    └── meeting_prompts.py   # 会议纪要 Agent 的系统/用户提示词
```

| 文件 | 核心内容 |
|---|---|
| `router_agent.py` | `RouterAgent` 类，`decide()` 方法，结构化输出 `RouterDecision` |
| `chat_agent.py` | `ChatAgent` 类，`create_react_agent()`，`invoke()` 方法，记忆管理 |
| `meeting_agent.py` | `MeetingAgent` 类，`summarize()` 方法，结构化输出 `MeetingSummary` |
| `agent_factory.py` | `create_router_agent()`、`create_chat_agent()`、`create_meeting_agent()` 等工厂函数 |
| `tools.py` | `@tool` 装饰的工具函数：获取时间、计算表达式等 |

---

## 五、Router Agent——意图识别的全局单例

### 5.1 设计理念

> Router Agent 是整个系统的**入口**。它只做一件事：看用户说了什么，判断该分给哪个子 Agent。它的设计极简——LLM + 结构化输出，没有记忆，没有工具。

```
用户输入："帮我整理一下上周的项目会议记录"
        │
        ▼
┌──────────────────────┐
│    Router Agent       │
│                      │
│  系统提示词：          │
│  "你是一个意图识别     │
│   专家..."            │
│                      │
│  结构化输出：          │
│  RouterDecision       │
│                      │
│  输出：               │
│  intent="meeting"     │
│  confidence=0.96     │
└──────────────────────┘
        │
        ▼
   分发给 Meeting Agent
```

### 5.2 RouterDecision 数据结构

```python
# ── 回顾 Schema 模块中的定义 ──

from enum import Enum
from pydantic import BaseModel, Field

class Intent(str, Enum):
    CHAT = "chat"
    MEETING_NOTES = "meeting_notes"
    UNKNOWN = "unknown"

class RouterDecision(BaseModel):
    """路由 Agent 的结构化输出"""
    intent: Intent = Field(description="识别出的用户意图")
    confidence: float = Field(ge=0.0, le=1.0, description="置信度")
    reasoning: str = Field(default="", description="推理过程")
```

### 5.3 提示词设计

```python
# ── prompts/router_prompts.py ──

ROUTER_SYSTEM_PROMPT = """
你是一个意图识别的专家。你的任务是判断用户输入的意图。

目前你可以提供以下两种服务：
1. chat（闲聊对话）：用户想要进行普通的对话交流
2. meeting_notes（会议纪要）：用户想要整理会议内容，生成结构化的会议纪要

请根据用户输入，判断他想要什么服务。

重要：请以 JSON 格式输出你的判断结果，包含以下字段：
- intent: 意图类型，可选值为 "chat"、"meeting_notes"、"unknown"
- confidence: 置信度，0.0 到 1.0 之间的浮点数
- reasoning: 你的推理过程（简要说明为什么做出这个判断）
"""

ROUTER_USER_PROMPT = """
以下是用户的输入内容，请判断他的意图：

{user_input}
"""
```

### 5.4 RouterAgent 完整实现

```python
# ── agents/router_agent.py ──

from typing import Optional
from langchain_core.language_models import BaseChatModel

from src.core.llm_driver import get_llm
from src.schemas.router_schema import RouterDecision
from src.agents.prompts.router_prompts import (
    ROUTER_SYSTEM_PROMPT,
    ROUTER_USER_PROMPT
)


class RouterAgent:
    """
    路由 Agent——意图识别
    
    设计特点：
    - 全局单例：整个服务只需一个实例
    - 无状态：每次判断完全独立
    - 结构化输出：返回 RouterDecision 对象而非纯文本
    
    使用示例：
        agent = RouterAgent()
        decision = agent.decide("帮我整理会议记录")
        print(decision.intent)  # Intent.MEETING_NOTES
    """
    
    def __init__(self, llm: Optional[BaseChatModel] = None):
        """
        初始化路由 Agent
        
        Args:
            llm: 可选的 LLM 实例。不传则使用默认模型
        """
        # ── 获取 LLM ──
        self.llm = llm if llm is not None else get_llm()
        
        # ── 结构化输出 LLM ──
        # with_structured_output 让 LLM 的输出自动填充到 RouterDecision 对象中
        self.structured_llm = self.llm.with_structured_output(RouterDecision)
    
    def decide(self, user_input: str) -> RouterDecision:
        """
        判断用户输入的意图
        
        Args:
            user_input: 用户输入的消息
        
        Returns:
            RouterDecision: 包含 intent、confidence、reasoning 的结构化对象
        """
        # ── 构建消息列表 ──
        messages = [
            # 系统提示词：告诉 LLM 它的角色和任务
            {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
            # 用户提示词：填入实际的用户输入
            {"role": "user", "content": ROUTER_USER_PROMPT.format(
                user_input=user_input
            )}
        ]
        
        # ── 调用 LLM 获取结构化输出 ──
        decision: RouterDecision = self.structured_llm.invoke(messages)
        return decision
    
    async def a_decide(self, user_input: str) -> RouterDecision:
        """
        异步版本：判断用户输入的意图
        
        Args:
            user_input: 用户输入的消息
        
        Returns:
            RouterDecision: 包含 intent、confidence、reasoning 的结构化对象
        """
        messages = [
            {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
            {"role": "user", "content": ROUTER_USER_PROMPT.format(
                user_input=user_input
            )}
        ]
        
        # 异步调用：ainvoke 代替 invoke
        decision: RouterDecision = await self.structured_llm.ainvoke(messages)
        return decision
```

### 5.5 使用示例

```python
# ── 使用 RouterAgent ──
from src.agents.router_agent import RouterAgent
from src.schemas.router_schema import Intent

agent = RouterAgent()

# 测试1：闲聊意图
decision = agent.decide("你好，今天天气怎么样？")
print(decision.intent)       # Intent.CHAT
print(decision.confidence)   # 0.95

# 测试2：会议纪要意图
decision = agent.decide("帮我整理上周的项目例会内容")
print(decision.intent)       # Intent.MEETING_NOTES
print(decision.confidence)   # 0.96
```

---

## 六、Chat Agent——ReAct 模式 + 工具 + 记忆

### 6.1 设计理念

> Chat Agent 是三个 Agent 中**最复杂**的一个。它不仅要做对话，还要：
> - 使用 **ReAct 模式**（Reasoning + Acting）进行思考和行动
> - 调用**工具**（获取时间、计算等）
> - 维护**记忆**（多轮对话的上下文）
>
> 因为不同用户/会话需要独立的记忆，Chat Agent 采用**每会话创建**的策略。

### 6.2 ReAct 模式简介

```
┌─────────────────────────────────────────────────────────┐
│              ReAct 模式的工作流程                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  用户提问："现在几点了？帮我算一下 365×24"                 │
│                                                         │
│  Step 1: Thought（思考）                                 │
│  "用户想知道当前时间，需要一个获取时间的工具。              │
│   用户还想做乘法计算，需要数学计算工具。"                  │
│                                                         │
│  Step 2: Action（行动）                                  │
│  调用工具 get_current_time() → 返回 "2026-06-26 09:00"   │
│                                                         │
│  Step 3: Observation（观察）                             │
│  "现在时间是 2026-06-26 09:00"                            │
│                                                         │
│  Step 4: Thought（再思考）                                │
│  "时间拿到了，还需要计算 365×24"                           │
│                                                         │
│  Step 5: Action（再行动）                                 │
│  调用工具 calculate("365*24") → 返回 8760                 │
│                                                         │
│  Step 6: Observation（观察）                              │
│  "365×24 = 8760"                                         │
│                                                         │
│  Step 7: Final Answer（最终回答）                         │
│  "现在是 2026年6月26日上午9点。365×24=8760。"            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

> ReAct = **Re**asoning（推理）+ **Act**ing（行动）。Agent 会循环执行"思考→行动→观察→再思考"，直到它能给出最终答案。LangGraph 的 `create_react_agent` 已经帮我们封装好了这个模式。

### 6.3 ChatAgent 完整实现

```python
# ── agents/chat_agent.py ──

from typing import Optional, List
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent

from src.core.llm_driver import get_llm
from src.memory.memory_manager import MemoryManager
from src.agents.tools import get_default_tools
from src.agents.prompts.chat_prompts import CHAT_SYSTEM_PROMPT


class ChatAgent:
    """
    对话 Agent——ReAct 模式 + 工具 + 记忆
    
    设计特点：
    - ReAct 模式：思考→行动→观察→再思考
    - 工具调用：可以调用 get_current_time、calculate 等工具
    - 记忆绑定：每个会话绑定独立的 MemoryManager
    - 每会话创建：不同 session_id → 不同的 ChatAgent 实例
    
    使用示例：
        agent = ChatAgent(memory=memory_manager, tools=[...])
        response = agent.invoke("现在几点了？")
    """
    
    def __init__(
        self,
        memory: MemoryManager,
        llm: Optional[BaseChatModel] = None,
        tools: Optional[List] = None,
        system_prompt: Optional[str] = None
    ):
        """
        初始化对话 Agent
        
        Args:
            memory: 记忆管理器（必传！每个会话独立的记忆）
            llm: 大模型实例，不传则使用默认
            tools: 工具列表，不传则使用默认工具集
            system_prompt: 系统提示词，不传则使用默认
        """
        # ═══ 大模型 ═══
        self.llm = llm if llm is not None else get_llm()
        
        # ═══ 工具集 ═══
        self.tools = tools if tools is not None else get_default_tools()
        
        # ═══ 记忆 ═══
        self.memory = memory
        
        # ═══ 系统提示词 ═══
        self.system_prompt = system_prompt or CHAT_SYSTEM_PROMPT
        
        # ═══ 创建 ReAct Agent ═══
        # create_react_agent 是 LangGraph 提供的工厂方法
        # 它会自动构建 ReAct 循环：思考 → 行动 → 观察
        self._agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=self.system_prompt
        )
    
    def invoke(self, user_input: str) -> str:
        """
        处理用户消息并返回回复
        
        Args:
            user_input: 用户输入的消息
        
        Returns:
            str: AI 的回复内容
        
        关键流程：
        1. 从记忆加载历史对话
        2. 构建完整的消息列表（历史 + 当前）
        3. 调用 ReAct Agent 处理
        4. 保存本轮对话到记忆
        5. 提取最终的 AI 回复
        """
        # Step 1: 将用户消息存入记忆
        self.memory.add_user_message(user_input)
        
        # Step 2: 构建消息列表（历史 + 当前用户输入）
        history = self.memory.get_history()
        messages = list(history)  # 历史消息
        
        # ⚠️ 历史消息中已包含当前的用户输入
        # （因为 Step 1 已经 add_user_message）
        
        # Step 3: 调用 ReAct Agent
        result = self._agent.invoke({"messages": messages})
        
        # Step 4: 提取 AI 的最终回复
        response_text = self._extract_response(result)
        
        # Step 5: 将 AI 回复存入记忆
        self.memory.add_ai_message(response_text)
        
        return response_text
    
    def _extract_response(self, result: dict) -> str:
        """
        从 ReAct Agent 的输出中提取最终的回复文本
        
        ReAct Agent 的输出包含多个消息（思考过程、工具调用等），
        我们只需要最后一条 AI 消息的内容。
        
        Args:
            result: ReAct Agent 的返回结果
        
        Returns:
            str: 提取的 AI 回复文本
        """
        messages = result.get("messages", [])
        
        # 倒序遍历，找到最后一条 AIMessage
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and msg.content:
                # 跳过工具调用的消息（tool_calls 不为空的是中间步骤）
                if not hasattr(msg, 'tool_calls') or not msg.tool_calls:
                    return msg.content
        
        # 如果没找到纯文本回复，返回最后一条消息的内容
        if messages:
            return str(messages[-1].content)
        return ""
```

### 6.4 记忆管理的关键代码

```python
# ── 记忆的生命周期管理 ──

# invoke 方法中的记忆操作：
def invoke(self, user_input: str) -> str:
    # ═══ 写入记忆（对话前） ═══
    self.memory.add_user_message(user_input)
    # 把用户刚说的话存进记忆
    
    # ... ReAct Agent 处理 ...
    
    # ═══ 写入记忆（对话后） ═══
    self.memory.add_ai_message(response_text)
    # 把 AI 的回复也存进记忆
    
    return response_text


# ── 记忆如何在多轮对话中发挥作用 ──

# 第1轮
agent.invoke("我叫陈泽鹏")
# 记忆：[HumanMessage("我叫陈泽鹏"), AIMessage("你好陈泽鹏！")]

# 第2轮
agent.invoke("我是谁？")
# 记忆加载：[HumanMessage("我叫陈泽鹏"), AIMessage("你好陈泽鹏！")]
# → 传给 LLM 的 prompt 包含了历史
# → LLM 知道用户叫"陈泽鹏"
# → 回复："你是陈泽鹏！"

# 记忆：[..., HumanMessage("我是谁？"), AIMessage("你是陈泽鹏！")]
```

---

## 七、Meeting Agent——简约的结构化输出

### 7.1 设计理念

> Meeting Agent 的设计前提是：**用户一次性给出完整的会议内容**，Agent 将其整理成结构化格式。因为是一次性输入，不需要记忆，所以和 Router Agent 一样采用全局单例。

```
用户输入一段会议记录文本
        │
        ▼
┌──────────────────────┐
│   Meeting Agent       │
│                      │
│  系统提示词：          │
│  "你是一个会议纪要     │
│   整理助手..."         │
│                      │
│  结构化输出：          │
│  MeetingSummary       │
│                      │
│  输出：               │
│  {title, date,        │
│   attendees, content, │
│   resolutions,        │
│   actions, notes}     │
└──────────────────────┘
        │
        ▼
  可调用 to_markdown()
  输出格式化的 Markdown
```

### 7.2 提示词设计

```python
# ── prompts/meeting_prompts.py ──

MEETING_SYSTEM_PROMPT = """
你是一个专业的会议纪要整理助手。你的任务是将用户提供的会议内容，
整理成结构化的会议纪要。

请按照以下字段提取信息，并以 JSON 格式输出：
- title: 会议标题/主题
- date: 会议日期
- attendees: 参会人员列表
- content: 会议内容摘要
- resolutions: 会议决议（可选，没有则为空列表）
- actions: 行动项列表（可选，每个行动项包含 description、responsible_person、deadline）
- notes: 备注信息（可选，没有则为空字符串）

注意：
1. 如果有信息原文中没有提到，用合理的默认值或留空
2. 确保输出是合法的 JSON 格式
"""

MEETING_USER_PROMPT = """
请根据以下会议内容，整理会议纪要：

{meeting_content}
"""
```

### 7.3 MeetingAgent 完整实现

```python
# ── agents/meeting_agent.py ──

from typing import Optional
from langchain_core.language_models import BaseChatModel

from src.core.llm_driver import get_llm
from src.schemas.meeting_schema import MeetingSummary
from src.agents.prompts.meeting_prompts import (
    MEETING_SYSTEM_PROMPT,
    MEETING_USER_PROMPT
)


class MeetingAgent:
    """
    会议纪要 Agent——结构化输出
    
    设计特点：
    - 全局单例：整个服务只需一个实例
    - 无状态：每次整理完全独立（一次性输入）
    - 结构化输出：返回 MeetingSummary 对象
    - 支持 Markdown 格式化：MeetingSummary.to_markdown()
    
    使用示例：
        agent = MeetingAgent()
        summary = agent.summarize("会议内容：今天讨论了...")
        print(summary.to_markdown())
    """
    
    def __init__(self, llm: Optional[BaseChatModel] = None):
        """
        初始化会议纪要 Agent
        
        Args:
            llm: 可选的 LLM 实例。不传则使用默认模型
        """
        # ── 获取 LLM ──
        self.llm = llm if llm is not None else get_llm()
        
        # ── 结构化输出 LLM ──
        # 输出自动填充到 MeetingSummary 对象
        self.structured_llm = self.llm.with_structured_output(MeetingSummary)
    
    def summarize(self, meeting_content: str) -> MeetingSummary:
        """
        将会议内容整理为结构化纪要
        
        Args:
            meeting_content: 完整的会议内容文本
        
        Returns:
            MeetingSummary: 结构化的会议纪要对象
        """
        # ── 构建消息列表 ──
        messages = [
            {"role": "system", "content": MEETING_SYSTEM_PROMPT},
            {"role": "user", "content": MEETING_USER_PROMPT.format(
                meeting_content=meeting_content
            )}
        ]
        
        # ── 调用 LLM 获取结构化输出 ──
        summary: MeetingSummary = self.structured_llm.invoke(messages)
        return summary
    
    async def a_summarize(self, meeting_content: str) -> MeetingSummary:
        """
        异步版本：将会议内容整理为结构化纪要
        """
        messages = [
            {"role": "system", "content": MEETING_SYSTEM_PROMPT},
            {"role": "user", "content": MEETING_USER_PROMPT.format(
                meeting_content=meeting_content
            )}
        ]
        
        summary: MeetingSummary = await self.structured_llm.ainvoke(messages)
        return summary
```

### 7.4 与 Router Agent 的相似性

```
Router Agent 和 Meeting Agent 的实现几乎一样：

共同点：
├── 都是 LLM + with_structured_output()
├── 都有系统提示词 + 用户提示词
├── 都需要同步/异步两个版本
├── 都是全局单例
└── 都不需要记忆

唯一区别：
├── Router → 输出 RouterDecision（intent + confidence + reasoning）
└── Meeting → 输出 MeetingSummary（title + date + attendees + ...）

这种一致性是有意为之的：
"简单的事情，用最简单的方案解决"
```

---

## 八、Tools 工具集——Agent 的手和脚

### 8.1 工具在 Agent 系统中的角色

> 工具（Tools）是 Agent 与外部世界交互的接口。没有工具，Agent 只能"空想"；有了工具，Agent 才能"行动"。

```
┌─────────────────────────────────────────────────────────┐
│          工具在 ReAct 循环中的角色                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Thought: "用户想知道当前时间"                             │
│      │                                                  │
│      ▼                                                  │
│  Action: 调用 get_current_time()  ← 工具！              │
│      │                                                  │
│      ▼                                                  │
│  Observation: "当前时间是 2026-06-26 09:00"              │
│      │                                                  │
│      ▼                                                  │
│  Final Answer: "现在是 6 月 26 日上午 9 点。"            │
│                                                         │
│  没有工具 → Agent 只会说"我不知道现在几点"                 │
│  有工具 → Agent 能真正获取实时数据                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 8.2 工具函数实现

```python
# ── agents/tools.py ──

from datetime import datetime
from langchain_core.tools import tool


@tool
def get_current_time() -> str:
    """
    获取当前的日期和时间
    
    当用户询问"现在几点"、"今天几号"等问题时使用此工具。
    
    Returns:
        str: 格式化的日期时间字符串，如 "2026-06-26 09:00:00"
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


@tool
def calculate(expression: str) -> str:
    """
    计算数学表达式的结果
    
    当用户需要进行数学计算时使用此工具。
    支持加减乘除、括号、幂运算等基本运算。
    
    Args:
        expression: 数学表达式字符串，如 "365 * 24"、"2**10"
    
    Returns:
        str: 计算结果
    """
    try:
        # ⚠️ eval 有安全风险，生产环境应使用更安全的方式
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算出错: {str(e)}"


@tool
def get_greeting(name: str = "用户") -> str:
    """
    生成个性化的问候语
    
    Args:
        name: 用户的名字，默认为"用户"
    
    Returns:
        str: 问候语
    """
    return f"你好，{name}！很高兴为你服务。"


# ── 工具集合 ──

def get_default_tools() -> list:
    """
    获取默认的工具列表
    
    所有 Chat Agent 默认可以使用这些工具。
    你也可以自定义工具列表，只传入需要的工具。
    
    Returns:
        list: 工具函数列表
    """
    return [
        get_current_time,
        calculate,
        get_greeting,
    ]
```

### 8.3 工具扩展指南

```
如何添加新工具？

1. 在 tools.py 中定义新函数，加上 @tool 装饰器
2. 在 get_default_tools() 中注册
3. 或者：在创建 ChatAgent 时手动传入自定义工具列表

示例：添加一个查天气的工具

@tool
def get_weather(city: str) -> str:
    """查询指定城市的天气"""
    # 调用天气 API...
    return f"{city}今天晴，25°C"

# 在 get_default_tools() 中加一行
def get_default_tools():
    return [
        get_current_time,
        calculate,
        get_greeting,
        get_weather,  # ← 新增
    ]

或者创建 Agent 时手动传入：
agent = ChatAgent(
    memory=memory,
    tools=[get_current_time, get_weather]  # 自定义工具集
)
```

---

## 九、Factory 工厂模式——Agent 的创建策略

### 9.1 为什么需要工厂模式

> 三个 Agent 的创建逻辑各不相同（全局单例 vs 每会话创建），如果每次都手动写创建代码，容易出错且不统一。工厂模式把创建逻辑集中管理，对外提供简洁的接口。

```python
# ── agents/agent_factory.py ──

from typing import Optional, List
from langchain_core.language_models import BaseChatModel

from src.core.llm_driver import get_llm
from src.memory.memory_manager import MemoryManager
from src.session.session_manager import SessionManager

from src.agents.router_agent import RouterAgent
from src.agents.chat_agent import ChatAgent
from src.agents.meeting_agent import MeetingAgent


# ══════════════════════════════════════════════════════
# 全局单例：Router Agent 和 Meeting Agent
# ══════════════════════════════════════════════════════

# 使用模块级别的全局变量
_global_router_agent: Optional[RouterAgent] = None
_global_meeting_agent: Optional[MeetingAgent] = None


def create_router_agent(
    llm: Optional[BaseChatModel] = None
) -> RouterAgent:
    """
    获取全局路由 Agent（单例模式）
    
    如果全局实例不存在，则创建；如果已存在，直接返回。
    这样确保整个服务中只有一个 Router Agent。
    
    Args:
        llm: 可选的大模型实例
    
    Returns:
        RouterAgent: 全局唯一的路由 Agent 实例
    """
    global _global_router_agent
    
    if _global_router_agent is None:
        _global_router_agent = RouterAgent(llm=llm)
    
    return _global_router_agent


def create_meeting_agent(
    llm: Optional[BaseChatModel] = None
) -> MeetingAgent:
    """
    获取全局会议纪要 Agent（单例模式）
    
    Args:
        llm: 可选的大模型实例
    
    Returns:
        MeetingAgent: 全局唯一的会议纪要 Agent 实例
    """
    global _global_meeting_agent
    
    if _global_meeting_agent is None:
        _global_meeting_agent = MeetingAgent(llm=llm)
    
    return _global_meeting_agent


# ══════════════════════════════════════════════════════
# 每会话创建：Chat Agent
# ══════════════════════════════════════════════════════

def create_chat_agent(
    memory: MemoryManager,
    llm: Optional[BaseChatModel] = None,
    tools: Optional[List] = None,
    system_prompt: Optional[str] = None
) -> ChatAgent:
    """
    创建对话 Agent（每次调用都创建新实例）
    
    因为每个会话需要独立的记忆，所以 Chat Agent 不能是单例。
    
    Args:
        memory: 记忆管理器（必传！）
        llm: 可选的大模型实例
        tools: 可选的工具列表
        system_prompt: 可选的系统提示词
    
    Returns:
        ChatAgent: 新的对话 Agent 实例
    """
    return ChatAgent(
        memory=memory,
        llm=llm,
        tools=tools,
        system_prompt=system_prompt
    )


# ══════════════════════════════════════════════════════
# 便捷方法
# ══════════════════════════════════════════════════════

def create_all_agents() -> tuple[RouterAgent, MeetingAgent]:
    """
    一次性初始化所有全局 Agent
    
    Returns:
        tuple: (RouterAgent, MeetingAgent)
    """
    router = create_router_agent()
    meeting = create_meeting_agent()
    return router, meeting


def create_agent_for_session(
    session_manager: SessionManager,
    session_id: Optional[str] = None
) -> tuple[str, ChatAgent]:
    """
    为一个会话窗口创建 Chat Agent
    
    封装了 Session 管理和 Chat Agent 创建的完整逻辑：
    1. 通过 SessionManager 获取或创建会话
    2. 从会话中取出 MemoryManager
    3. 用 MemoryManager 创建 ChatAgent
    
    Args:
        session_manager: 会话管理器
        session_id: 可选的会话 ID
    
    Returns:
        tuple: (session_id, ChatAgent)
    """
    # 获取或创建会话 → 得到 session_id + memory
    sid, memory = session_manager.get_or_create(session_id)
    
    # 用这个会话的 memory 创建 Chat Agent
    agent = create_chat_agent(memory=memory)
    
    return sid, agent
```

### 9.2 工厂模式的全景图

```
┌─────────────────────────────────────────────────────────┐
│           Agent 工厂的创建策略                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  create_router_agent()                                  │
│  ├── 第1次调用 → 创建 RouterAgent → 存入全局变量         │
│  ├── 第2次调用 → 检查全局变量已有 → 直接返回同一个       │
│  └── 第N次调用 → 始终返回同一个实例                      │
│                                                         │
│  create_meeting_agent()                                 │
│  ├── 第1次调用 → 创建 MeetingAgent → 存入全局变量        │
│  ├── 第2次调用 → 检查全局变量已有 → 直接返回同一个       │
│  └── 第N次调用 → 始终返回同一个实例                      │
│                                                         │
│  create_chat_agent(memory=xxx)                          │
│  ├── 每次调用 → 创建全新的 ChatAgent                     │
│  ├── agent_1: memory_1（用户A的记忆）                    │
│  ├── agent_2: memory_2（用户B的记忆）                    │
│  └── 每次的 memory 参数不同 → Agent 实例不同            │
│                                                         │
│  create_agent_for_session(session_manager, sid)         │
│  ├── 封装了 Session + Memory + Agent 的创建流程         │
│  └── 一步到位地创建绑定特定会话的 ChatAgent              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 9.3 工厂模式使用示例

```python
# ── 方式一：单独创建 ──
from src.agents.agent_factory import (
    create_router_agent,
    create_meeting_agent,
    create_chat_agent,
    create_agent_for_session
)

# 全局单例（只需创建一次）
router = create_router_agent()
meeting = create_meeting_agent()

# 每会话创建（每次新会话都创建）
chat_agent_for_user_a = create_chat_agent(memory=memory_a)
chat_agent_for_user_b = create_chat_agent(memory=memory_b)


# ── 方式二：结合 Session 管理器 ──
from src.session.session_manager import SessionManager

session_manager = SessionManager()

# HTTP 请求处理
sid, chat_agent = create_agent_for_session(
    session_manager,
    session_id=request.session_id  # 可能为 None
)
response = chat_agent.invoke(request.message)
session_manager.update_activity(sid)


# ── 方式三：一次性初始化 ──
router, meeting = create_all_agents()
```

---

## 十、完整工作流程——从输入到回复

### 10.1 Agent 协作全景图

```
用户输入
    │
    ▼
┌──────────────────────────────────────────────┐
│  Step 1: Router Agent 判断意图               │
│                                              │
│  decision = router.decide(user_input)         │
│  intent = decision.intent                    │
│                                              │
│  可能的意图：                                  │
│  ├── "chat"           → 走对话流程           │
│  ├── "meeting_notes"  → 走会议纪要流程       │
│  └── "unknown"        → 返回兜底回复         │
└──────────────┬───────────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌──────────────┐  ┌──────────────────┐
│  Chat 流程    │  │  Meeting 流程     │
│              │  │                  │
│  1. Session  │  │  1. 调用 Meeting │
│     管理器    │  │     Agent        │
│     ↓        │  │                  │
│  2. 获取/创建 │  │  2. 结构化输出    │
│     Memory   │  │     ↓            │
│     ↓        │  │  3. MeetingSummary│
│  3. 创建 Chat │  │     ↓            │
│     Agent    │  │  4. to_markdown() │
│     ↓        │  │     ↓            │
│  4. invoke() │  │  5. 返回格式化     │
│     (ReAct)   │  │     结果          │
│     ↓        │  │                  │
│  5. 更新活跃  │  └──────────────────┘
│     时间      │
│     ↓        │
│  6. 返回回复  │
└──────────────┘
```

### 10.2 主入口代码（run_agent.py）

```python
# ── run_agent.py ── 简化的主入口逻辑

from src.agents.agent_factory import (
    create_router_agent,
    create_meeting_agent,
    create_agent_for_session
)
from src.session.session_manager import SessionManager
from src.schemas.router_schema import Intent

# ── 初始化全局组件 ──
router = create_router_agent()
meeting = create_meeting_agent()
session_manager = SessionManager(timeout_hours=24)


def process_message(user_input: str, session_id: str = None) -> dict:
    """
    处理一条用户消息的完整流程
    
    Args:
        user_input: 用户的输入
        session_id: 可选的会话 ID
    
    Returns:
        dict: 包含回复内容和会话 ID
    """
    
    # Step 1: 路由——判断意图
    decision = router.decide(user_input)
    
    # Step 2: 根据意图分发
    if decision.intent == Intent.MEETING_NOTES:
        # ── 会议纪要流程 ──
        summary = meeting.summarize(user_input)
        response_text = summary.to_markdown()
        
        return {
            "response": response_text,
            "intent": "meeting_notes",
            "session_id": session_id
        }
    
    elif decision.intent == Intent.CHAT:
        # ── 对话流程 ──
        # 获取或创建会话 + 创建 ChatAgent
        sid, chat_agent = create_agent_for_session(
            session_manager, session_id
        )
        
        # 调用 Chat Agent 处理
        response_text = chat_agent.invoke(user_input)
        
        # 更新会话活跃时间
        session_manager.update_activity(sid)
        
        return {
            "response": response_text,
            "intent": "chat",
            "session_id": sid
        }
    
    else:
        # ── 未知意图兜底 ──
        return {
            "response": "抱歉，我没有理解你的意图。请尝试更明确地描述你的需求。",
            "intent": "unknown",
            "session_id": session_id
        }


# ── 命令行交互循环 ──
if __name__ == "__main__":
    current_session_id = None
    
    print("🤖 多 Agent 系统已启动！输入 'quit' 退出。")
    
    while True:
        user_input = input("\n你: ")
        
        if user_input.lower() == "quit":
            break
        
        result = process_message(user_input, current_session_id)
        current_session_id = result["session_id"]
        
        print(f"\n[意图: {result['intent']}]")
        print(f"AI: {result['response']}")
```

### 10.3 完整流程演示

```
$ python run_agent.py
🤖 多 Agent 系统已启动！

你: 你好！
[意图: chat]
AI: 你好！有什么可以帮助你的吗？

你: 我是陈泽鹏，我喜欢苹果
[意图: chat]
AI: 你好陈泽鹏！很高兴认识你。苹果确实是一种很棒的水果！

你: 我是谁？我喜欢什么水果？
[意图: chat]
AI: 你是陈泽鹏，你喜欢苹果！ ← 有记忆！✅

你: 帮我整理以下会议：
    2026年6月25日，技术部周会，
    参会人：张三、李四、王五，
    讨论了Q3功能排期和性能优化方案，
    决定下周一前完成性能测试，
    张三负责性能测试，李四负责排期方案

[意图: meeting_notes]
AI: # 技术部周会
    ## 日期
    2026-06-25
    ## 参会人员
    张三、李四、王五
    ## 摘要
    讨论了Q3功能排期和性能优化方案...
    ← 结构化会议纪要输出 ✅
```

---

## 十一、与 Session/Memory 模块的集成

### 11.1 Chat Agent 的完整创建链路

```
HTTP 请求到达（带 session_id）
    │
    ▼
SessionManager.get_or_create(session_id)
    │
    ├── session_id 存在 → 取出已有 SessionData
    ├── session_id 不存在 → 创建新 SessionData
    │
    ▼
SessionData.memory  ← MemoryManager 实例
    │
    ▼
create_chat_agent(memory=memory)
    │
    ▼
ChatAgent 实例（绑定了这个会话的记忆）
    │
    ▼
chat_agent.invoke(user_input)
    │
    ├── memory.get_history()  ← 加载历史
    ├── ReAct Agent 处理
    ├── memory.add_user_message()
    ├── memory.add_ai_message()
    └── 返回 AI 回复
    │
    ▼
session_manager.update_activity(session_id)
    │
    ▼
返回 {response, session_id}
```

### 11.2 为什么 Chat Agent 不能是全局单例

```python
# ── ❌ 错误做法：Chat Agent 也用全局单例 ──

_global_chat_agent = ChatAgent(memory=MemoryManager())

# 用户A 发消息
_global_chat_agent.invoke("我叫张三")  # 存入 memory

# 用户B 发消息（同一个 Agent，同一个 memory！）
_global_chat_agent.invoke("帮我订机票")  # 存入同一个 memory！

# 用户A 再发消息
_global_chat_agent.invoke("我是谁？")
# → 记忆里有张三 + 订机票的内容
# → 回答混乱！❌


# ── ✅ 正确做法：每个会话创建独立的 ChatAgent ──

# 用户A（session_id="abc"）
sid_a, agent_a = create_agent_for_session(session_manager, "abc")
agent_a.invoke("我叫张三")  # 存入 memory_a

# 用户B（session_id="xyz"）
sid_b, agent_b = create_agent_for_session(session_manager, "xyz")
agent_b.invoke("帮我订机票")  # 存入 memory_b

# 用户A 再发消息
sid_a2, agent_a2 = create_agent_for_session(session_manager, "abc")
agent_a2.invoke("我是谁？")
# → 记忆里只有"我叫张三"
# → 正确回答："你是张三！" ✅
```

---

## 十二、如何新增一个 Agent

### 12.1 新增 Agent 的四步清单

```
你想新增一个 Agent？按以下四步走：

Step 1: 定义 Schema（如果需要新的数据格式）
    → 在 src/schemas/ 下新增数据结构

Step 2: 编写 Agent 类
    → 在 src/agents/ 下新增 .py 文件
    → 参考 RouterAgent（简单）或 ChatAgent（复杂）

Step 3: 编写提示词
    → 在 src/agents/prompts/ 下新增提示词文件

Step 4: 在工厂中注册
    → 在 agent_factory.py 中新增 create_xxx_agent() 函数
    → 决定是全局单例还是每会话创建
```

### 12.2 示例：新增一个翻译 Agent

```python
# ── Step 1: Schema（如果需要）──
# src/schemas/translate_schema.py

class TranslateRequest(BaseModel):
    text: str = Field(description="待翻译文本")
    source_lang: str = Field(default="auto", description="源语言")
    target_lang: str = Field(default="en", description="目标语言")

class TranslateResponse(BaseModel):
    translated_text: str = Field(description="翻译结果")
    confidence: float = Field(ge=0.0, le=1.0, description="翻译置信度")


# ── Step 2: Agent 类 ──
# src/agents/translate_agent.py

class TranslateAgent:
    """翻译 Agent——全局单例"""
    
    def __init__(self, llm=None):
        self.llm = llm or get_llm()
        self.structured_llm = self.llm.with_structured_output(
            TranslateResponse
        )
    
    def translate(self, text: str, target_lang: str = "en") -> TranslateResponse:
        messages = [
            {"role": "system", "content": TRANSLATE_SYSTEM_PROMPT},
            {"role": "user", "content": f"翻译成{target_lang}：{text}"}
        ]
        return self.structured_llm.invoke(messages)


# ── Step 3: 提示词 ──
# src/agents/prompts/translate_prompts.py

TRANSLATE_SYSTEM_PROMPT = """
你是一个专业的翻译助手。请准确翻译用户提供的文本。
输出格式为 JSON：{"translated_text": "...", "confidence": 0.95}
"""


# ── Step 4: 工厂注册 ──
# agent_factory.py 中新增

_global_translate_agent = None

def create_translate_agent(llm=None):
    global _global_translate_agent
    if _global_translate_agent is None:
        _global_translate_agent = TranslateAgent(llm=llm)
    return _global_translate_agent
```

```
新增 Agent 的决策问题：

1. 需要记忆吗？
   ├── 不需要 → 全局单例（简单）
   └── 需要 → 每会话创建（复杂）

2. 需要工具吗？
   ├── 不需要 → 纯 LLM + 结构化输出
   └── 需要 → ReAct 模式

3. 需要特殊的输出格式吗？
   ├── 需要 → 定义 Schema + with_structured_output
   └── 不需要 → 直接返回字符串
```

---

## 十三、测试 Agent 模块

### 13.1 Router Agent 测试

```python
# ── test_router_agent.py ──

import pytest
from src.agents.router_agent import RouterAgent
from src.schemas.router_schema import Intent


class TestRouterAgent:
    """路由 Agent 的单元测试"""
    
    def test_initialization(self):
        """测试：RouterAgent 正常初始化"""
        agent = RouterAgent()
        
        # 验证核心属性存在
        assert agent.llm is not None
        assert agent.structured_llm is not None
    
    def test_decide_chat_intent(self):
        """测试：识别闲聊意图"""
        agent = RouterAgent()
        
        decision = agent.decide("你好，今天天气怎么样？")
        
        assert decision.intent == Intent.CHAT
        assert 0.0 <= decision.confidence <= 1.0
    
    def test_decide_meeting_intent(self):
        """测试：识别会议纪要意图"""
        agent = RouterAgent()
        
        decision = agent.decide(
            "帮我整理上周五的项目周会内容，"
            "参会人有张三、李四，讨论了排期问题"
        )
        
        assert decision.intent == Intent.MEETING_NOTES
        assert 0.0 <= decision.confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_async_decide(self):
        """测试：异步版本正常工作"""
        agent = RouterAgent()
        
        decision = await agent.a_decide("你好！")
        
        assert decision is not None
        assert decision.intent is not None
```

### 13.2 Meeting Agent 测试

```python
# ── test_meeting_agent.py ──

import pytest
from src.agents.meeting_agent import MeetingAgent


class TestMeetingAgent:
    """会议纪要 Agent 的单元测试"""
    
    def test_initialization(self):
        """测试：正常初始化"""
        agent = MeetingAgent()
        
        assert agent.llm is not None
        assert agent.structured_llm is not None
    
    def test_summarize_meeting(self):
        """测试：整理会议纪要"""
        agent = MeetingAgent()
        
        meeting_text = """
        2026年6月25日产品组周会
        参会人员：张三（PM）、李四（开发）、王五（测试）
        讨论了Q3用户增长策略，决定加大内容营销投入。
        张三负责在下周一前完成增长方案初稿。
        """
        
        summary = agent.summarize(meeting_text)
        
        # 验证核心字段
        assert summary.title is not None
        assert len(summary.title) > 0
        assert summary.attendees is not None
        assert len(summary.attendees) >= 2
        assert summary.content is not None
    
    def test_to_markdown(self):
        """测试：Markdown 格式化输出"""
        agent = MeetingAgent()
        
        summary = agent.summarize("测试会议内容")
        markdown = summary.to_markdown()
        
        # 验证 Markdown 结构
        assert markdown.startswith("# ")
        assert "## " in markdown
```

### 13.3 测试要点总结

```
┌─────────────────────────────────────────────────────────┐
│           Agent 测试的核心关注点                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1️⃣  初始化 —— LLM 和 structured_llm 是否正常创建       │
│                                                         │
│  2️⃣  同步调用 —— invoke/decide/summarize 返回值是否正确  │
│                                                         │
│  3️⃣  异步调用 —— ainvoke/a_decide/a_summarize 是否工作  │
│                                                         │
│  4️⃣  输出结构 —— 返回的对象字段是否完备                  │
│                                                         │
│  5️⃣  边界情况 —— 空输入、超长输入、特殊字符              │
│                                                         │
│  6️⃣  记忆集成 —— Chat Agent 多轮对话记忆是否保留        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 十四、常见问题与排错指南

### 14.1 错误速查表

| 错误现象 | 原因 | 解决方法 | 优先级 |
|---|---|---|---|
| **Router 总是返回 unknown** | 提示词中的服务描述不够清晰 | 在 `ROUTER_SYSTEM_PROMPT` 中更详细地描述每个意图的特征和关键词 | 🔴 高 |
| **Chat Agent 不记得之前的对话** | 没有正确传入 memory，或 memory 没持久化 | 检查 `create_chat_agent(memory=memory)` 是否正确绑定了会话的 memory | 🔴 高 |
| **ReAct Agent 不调用工具** | 工具描述不够清晰，LLM 不知道有这个工具 | 确保 `@tool` 装饰的函数有清晰的 docstring | 🟡 中 |
| **Meeting 纪要关键字段为空** | LLM 没有从输入中提取到相关信息 | 在 `MEETING_SYSTEM_PROMPT` 中强调必填字段；考虑给字段设默认值 | 🟡 中 |
| **不同用户对话串台** | Chat Agent 使用了全局单例而不是每会话创建 | 确保 Chat Agent 是每会话创建的（通过 `create_agent_for_session`） | 🔴 高 |
| **结构化输出 ValidationError** | LLM 输出不符合 Schema 定义 | 检查 Schema 的 `description` 是否清晰；考虑 retry 机制 | 🟡 中 |
| **异步调用报错** | 使用了同步的 `invoke` 而非 `ainvoke` | 在异步环境中使用 `await agent.a_decide()` 等异步方法 | 🟢 低 |
| **会议纪要日期总是错的** | Meeting Agent 当前没有获取当前日期的能力 | 给 Meeting Agent 也加入 ReAct 模式 + 时间工具（改进方向） | 🟢 低 |

### 14.2 排查流程

```
Agent 不按预期工作？
    │
    ├── Router 判断错误？
    │   └── 检查 ROUTER_SYSTEM_PROMPT 是否清晰描述了每个意图
    │       → 添加更多关键词示例
    │
    ├── Chat 回答不准确？
    │   ├── ReAct 模式在工作吗？→ 观察日志中的 Thought/Action
    │   ├── 工具正确调用了吗？→ 检查 tools.py 中的工具定义
    │   └── 提示词合适吗？→ 调整 CHAT_SYSTEM_PROMPT
    │
    ├── Meeting 输出不完整？
    │   └── 检查 MEETING_SYSTEM_PROMPT 中对字段的描述
    │       → 强调必填字段，给出示例
    │
    └── 记忆丢失？
        ├── 检查 memory 是否正确传入
        ├── 检查 add_user_message/add_ai_message 是否被调用
        └── 检查 Session 是否过期被清理了
```

---

## 十五、课后练习

### 练习一：基础——跟踪一次完整的 Agent 调用

**题目**：运行 `run_agent.py`，分别测试闲聊和会议纪要两种场景，观察 Router 的判断和子 Agent 的回复。

**要求**：
- 测试 3 句闲聊（验证 Chat Agent 的记忆能力）
- 测试 1 段会议内容（验证 Meeting Agent 的结构化输出）
- 记录每次 Router 返回的 intent 和 confidence
- 截图保存 Meeting Agent 的 Markdown 输出

### 练习二：进阶——新增一个工具并验证

**题目**：在 `tools.py` 中新增一个工具（例如 `get_word_count(text)` 统计文本字数），验证 Chat Agent 能否自动发现并使用它。

**要求**：
- 定义 `@tool` 装饰的函数
- 在 `get_default_tools()` 中注册
- 向 Chat Agent 提问"这篇文章有多少字？"
- 观察 Agent 是否调用了你的新工具

<details>
<summary>参考答案</summary>

```python
# tools.py 中新增
@tool
def get_word_count(text: str) -> str:
    """统计文本的字数。当用户询问"有多少字"时使用。"""
    # 中文字数统计（去掉空格和标点）
    import re
    chinese_chars = re.findall(r'[一-鿿]', text)
    return f"文本共有 {len(chinese_chars)} 个汉字"

# 注册
def get_default_tools():
    return [
        get_current_time,
        calculate,
        get_greeting,
        get_word_count,  # ← 新增
    ]
```
</details>

### 练习三：综合实战——新增一个 Agent

**题目**：按照"十二、如何新增一个 Agent"的指南，新增一个**代码审查 Agent（CodeReviewAgent）**。

**要求**：
- 定义 Schema：`CodeReviewResult`（包含 `summary`、`issues` 列表、`score` 评分）
- 编写 Agent 类：接收代码文本，返回结构化审查结果
- 编写提示词：系统提示词定义审查规则
- 在工厂中注册
- 写测试用例验证

<details>
<summary>参考框架</summary>

```python
# Step 1: Schema
class CodeIssue(BaseModel):
    line: int = Field(description="问题行号")
    severity: str = Field(description="严重程度：error/warning/info")
    description: str = Field(description="问题描述")

class CodeReviewResult(BaseModel):
    summary: str = Field(description="审查总结")
    issues: List[CodeIssue] = Field(description="发现的问题列表")
    score: int = Field(ge=0, le=100, description="代码质量评分")

# Step 2: Agent
class CodeReviewAgent:
    def __init__(self, llm=None):
        self.llm = llm or get_llm()
        self.structured_llm = self.llm.with_structured_output(CodeReviewResult)
    
    def review(self, code: str) -> CodeReviewResult:
        messages = [
            {"role": "system", "content": CODE_REVIEW_PROMPT},
            {"role": "user", "content": f"请审查以下代码：\n{code}"}
        ]
        return self.structured_llm.invoke(messages)
```
</details>

---

## 十六、本节小结

### 16.1 核心知识图谱

```
┌────────────────────────────────────────────────────────────┐
│              Agents 模块核心知识体系                          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  多 Agent 架构理念                                       │
│      ├── 职责单一：每个 Agent 只做一件事                      │
│      ├── 路由分发：Router → Chat / Meeting                  │
│      └── 差异化设计：简单的事简单做，复杂的事用 ReAct         │
│                                                            │
│  2️⃣  三种 Agent 实现                                         │
│      ├── Router Agent：结构化输出 + 全局单例 + 无状态        │
│      ├── Chat Agent：ReAct + 工具 + 记忆 + 每会话创建       │
│      └── Meeting Agent：结构化输出 + 全局单例 + 无状态       │
│                                                            │
│  3️⃣  实例化策略                                              │
│      ├── 全局单例（Router、Meeting）：无记忆、请求独立        │
│      └── 每会话创建（Chat）：有记忆、会话隔离                 │
│                                                            │
│  4️⃣  Factory 工厂模式                                        │
│      ├── create_router_agent() → 检查全局变量 → 单例        │
│      ├── create_meeting_agent() → 同上                      │
│      ├── create_chat_agent(memory) → 每次新建               │
│      └── create_agent_for_session() → Session + Agent 联动  │
│                                                            │
│  5️⃣  完整请求流程                                            │
│      ├── Router 判断意图 → 分发到子 Agent                    │
│      ├── Chat：Session → Memory → Agent → invoke           │
│      └── Meeting：直接调用 → 结构化输出 → to_markdown       │
│                                                            │
│  6️⃣  扩展指南                                               │
│      ├── 新增 Agent：Schema + Agent类 + Prompt + 工厂注册   │
│      ├── 新增工具：@tool 函数 + get_default_tools() 注册    │
│      └── 决策：需要记忆？→ 每会话创建 : 全局单例             │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 16.2 模块依赖全景图

```
┌─────────────────────────────────────────────────────────┐
│              项目完整依赖关系（所有模块已完成）              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  入口层 (run_agent.py / run_service.py)                  │
│      ↑ 调用 Agents                                       │
│                                                         │
│  Agents 层（本课）✅                                     │
│  ├── RouterAgent   ← 依赖 Schema + Core                 │
│  ├── ChatAgent     ← 依赖 Schema + Core + Memory + Tools│
│  └── MeetingAgent  ← 依赖 Schema + Core                 │
│      ↑                                                   │
│  ┌───┴──────────────────────────┐                       │
│  │                               │                       │
│  Session 层 ✅                    Schema 层 ✅             │
│  ├── SessionManager              ├── RouterDecision      │
│  └── SessionData                 ├── MeetingSummary      │
│      ↑                           └── ChatRequest/Response│
│  Memory 层 ✅                         ↑                   │
│  └── MemoryManager               Core 层 ✅               │
│      ↑                           └── config + llm_driver │
│  Core 层 ✅                                               │
│                                                         │
│  ✅ 全部 5 层模块已完成！                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 16.3 一句话总结

> **Agents 模块是系统的"大脑"——Router 负责"判断该找谁"，Chat 负责"思考+行动+记住"，Meeting 负责"整理输出"。Factory 工厂模式根据"是否需要记忆"来决定创建策略：无记忆的全局共用，有记忆的每会话独享。整个系统通过 Router → 子 Agent 的分发模式，让每个智能体各司其职、协同工作。**

### 16.4 系列课程定位

```
┌─────────────────────────────────────────────────────────┐
│              多 Agent 开发实战 · 系列课程                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  开篇：课程总览                                           │
│  第1课：为什么现在必须学 Agent 开发                         │
│  第2课：多 Agent 项目架构总览                              │
│  第3课：Core 模块——配置 + 大模型驱动                       │
│  第4课：Schema 模块——数据结构决定 Agent 规范               │
│  第5课：Memory 模块——让 Agent 记住上下文                   │
│  第6课：Session 模块——多用户会话管理                       │
│  第7课（本课）：Agents 模块——多智能体业务逻辑  ← 你在这里   │
│  后续：Service 入口 → 生产部署                             │
│                                                         │
│  🎉 恭喜！所有核心模块已经完成！                            │
│                                                         │
│  从底层到上层，你已完整掌握了：                              │
│  ✅ Core：怎么配置和调用大模型                             │
│  ✅ Schema：怎么定义 Agent 的输入输出格式                  │
│  ✅ Memory：怎么让 Agent 记住多轮对话                      │
│  ✅ Session：怎么隔离不同用户的会话                        │
│  ✅ Agents：怎么让多个 Agent 分工协作                       │
│                                                         │
│  你已经具备了从零搭建多 Agent 系统的完整能力！               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

*本教学文档基于陈泽鹏老师视频课程整理编写 · 2026年6月26日*
