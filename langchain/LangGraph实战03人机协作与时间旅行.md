# LangGraph 实战——03 人机协作与时间旅行

> 基于教学视频课程整理编写 · 2026年6月

---

## 目录

- [一、课程背景与目标](#一课程背景与目标)
- [二、动态流程控制——路由的四种模式](#二动态流程控制路由的四种模式)
- [三、Streaming——流式输出的三种模式](#三streaming流式输出的三种模式)
- [四、Human-in-the-Loop——人工介入机制](#四human-in-the-loop人工介入机制)
- [五、时间旅行——回溯历史与探索分支](#五时间旅行回溯历史与探索分支)
- [六、综合实战——交互式内容审核工作流](#六综合实战交互式内容审核工作流)
- [七、Streaming + Checkpoint 进阶组合](#七streaming--checkpoint-进阶组合)
- [八、interrupt 完整参数详解](#八interrupt-完整参数详解)
- [九、三种 Streaming 模式深度对比](#九三种-streaming-模式深度对比)
- [十、路由模式决策指南](#十路由模式决策指南)
- [十一、常见问题与排错指南](#十一常见问题与排错指南)
- [十二、课后练习](#十二课后练习)
- [十三、课程小结](#十三课程小结)

---

## 一、课程背景与目标

### 1.1 前情回顾

在上一课（02 可记忆、可恢复的智能体）中，我们掌握了 LangGraph 的三大核心能力：

| 知识点 | 核心内容 | 关键 API |
|--------|----------|----------|
| **State 设计** | 四大原则（最小化/清晰命名/类型安全/分层） | `TypedDict` + `Annotated` |
| **Reducer** | 状态更新机制 | `add`, `add_messages`, 自定义函数 |
| **Checkpoint** | 状态的持久化存储 | `MemorySaver`, `SqliteSaver` |
| **Thread** | 独立的执行上下文 | `config["configurable"]["thread_id"]` |
| **Durable Execution** | 断点恢复、故障容错 | Checkpoint + Thread 配合 |
| **记忆管理** | 短期记忆 + 长期记忆（事实提取+评分+衰减） | `InMemoryStore` |

上一课我们解决了"**怎么保存状态**"和"**怎么断点恢复**"的问题。本节课更进一步——解决"**怎么让 Agent 与人协作**"和"**怎么回溯到任意历史状态**"的问题。

### 1.2 本节课的核心问题

> **当 Agent 执行到关键步骤时，怎么让人类介入审核？执行完成后，怎么回到任意历史节点重新出发？**

```
本课要解决的关键问题：

问题1：Agent 铁头往前冲
	    你让 Agent 自动发邮件，它把草稿直接发出去了 😱
	    → 能不能在执行关键步骤前，先停下来等人确认？

问题2：流式输出不知道怎么选
	    LangGraph 的 streaming 有三种模式，到底该用哪种？
	    → values / updates / messages 有什么区别？

问题3：出错了想回溯
	    流程执行到一半发现前面的判断有问题
	    → 能不能回到那个节点重新来过？

问题4：复杂流程怎么灵活控制
	    用户的输入千奇百怪，固定的 if-else 不够用
	    → 怎么让大模型来动态决定下一步怎么走？
```

### 1.3 本课要掌握的目标

```
┌───────────────────────────────────────────────────────┐
│                                                       │
│  目标一：掌握动态流程控制                                │
│         ├── 基于条件的路由（规则驱动）                    │
│         ├── 基于大模型的路由（LLM 驱动）                 │
│         ├── 多级路由（漏斗式决策）                       │
│         └── Agent 行动循环（ReAct 模式）                 │
│                                                       │
│  目标二：掌握流式输出三种模式                             │
│         ├── values：全量状态快照                        │
│         ├── updates：增量状态变化                       │
│         └── messages：Token 级打字机效果                 │
│                                                       │
│  目标三：掌握 Human-in-the-Loop                          │
│         ├── interrupt 暂停流程                         │
│         ├── update_state 恢复执行                      │
│         └── 多级人工审核的实现                           │
│                                                       │
│  目标四：掌握时间旅行                                    │
│         ├── 查看执行历史（get_state_history）            │
│         ├── 回溯到任意历史节点                           │
│         └── 从历史节点创建新分支                         │
│                                                       │
└───────────────────────────────────────────────────────┘
```

---

## 二、动态流程控制——路由的四种模式

### 2.1 概述——LangGraph 的路由能力

LangGraph 中"路由"的本质是**条件边（Conditional Edge）**：在每个节点执行完成后，根据一定的逻辑决定接下来应该走向哪个节点。

```
普通边（Edge）：  A ──→ B    （固定路线，每次都一样）

条件边（Conditional Edge）：
                         ┌──→ B（条件一满足）
                    A ───┼──→ C（条件二满足）
                         └──→ D（条件三满足）
```

LangGraph 提供了四种路由模式，从简单到复杂，适用于不同场景：

| 模式 | 决策者 | 复杂度 | 适用场景 |
|------|:------:|:------:|----------|
| **基于条件的路由** | 代码规则 | ⭐ | 明确的分支逻辑（得分 > 0.8 走 A） |
| **基于大模型的路由** | LLM | ⭐⭐ | 模糊/复杂的输入需 AI 判断 |
| **多级路由** | 规则 + LLM | ⭐⭐⭐ | 先粗筛后精筛的漏斗式决策 |
| **Agent 行动循环（ReAct）** | LLM | ⭐⭐⭐ | 自主推理 + 行动 + 循环直到完成 |

### 2.2 模式一：基于条件的路由

> **由代码规则决定下一步**——最直接、最高效的路由方式。

#### 场景

一个内容评分系统，根据得分将内容分流到三个等级：

```
得分 >= 0.8  → high（高质量，直接发布）
得分 >= 0.5  → medium（中等质量，需要人工审核）
得分 < 0.5   → low（低质量，直接驳回）
```

#### 流程图

```
        ┌─────────────┐
        │    START    │
        └──────┬──────┘
               ↓
        ┌─────────────┐
        │  evaluate   │ ← 评分节点：给出 score = 0.75
        │  (打分)      │
        └──────┬──────┘
               ↓
    ┌──────────────────────┐
    │   route_by_score     │ ← 条件判断
    │   (条件路由)          │
    └──┬───────┬───────┬───┘
       ↓       ↓       ↓
   score≥0.8  score   score
       ↓     ≥0.5↓    <0.5 ↓
   ┌──────┐ ┌──────┐ ┌──────┐
   │ high │ │medium│ │ low  │
   └──┬───┘ └──┬───┘ └──┬───┘
      ↓        ↓        ↓
      └────────┼────────┘
               ↓
        ┌─────────────┐
        │     END     │
        └─────────────┘
```

#### 完整代码

```python
# ── 依赖导入 ──
import os
from typing import TypedDict
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

# ── 设置 API Key ──
os.environ["SILICONFLOW_API_KEY"] = "your-api-key-here"

# ── 定义 State ──
class RouterState(TypedDict):
    score: float          # 内容得分（0-1）
    decision: str         # 路由决策结果

# ── 评分节点 ──
def evaluate(state: RouterState) -> RouterState:
    """评估内容质量并打分"""
    # 在实际应用中，这里可以用 LLM 来打分
    # 这里用固定值 0.75 做演示
    score = 0.75
    print(f"📊 评估完成，得分：{score}")
    return {"score": score}

# ── 各分支节点 ──
def high_node(state: RouterState) -> RouterState:
    """高质量内容：直接通过"""
    print("✅ 高质量内容，自动通过！")
    return {"decision": "high_pass"}

def medium_node(state: RouterState) -> RouterState:
    """中等质量内容：需人工审核"""
    print("⚠️  中等质量内容，进入人工审核队列")
    return {"decision": "medium_review"}

def low_node(state: RouterState) -> RouterState:
    """低质量内容：直接驳回"""
    print("❌ 低质量内容，自动驳回")
    return {"decision": "low_reject"}

# ── 条件路由函数 ──
def route_by_score(state: RouterState) -> str:
    """
    根据得分决定路由方向。
    返回值必须与 add_conditional_edges 中的映射 key 对应。
    """
    score = state["score"]
    if score >= 0.8:
        return "high"
    elif score >= 0.5:
        return "medium"
    else:
        return "low"

# ── 构建图 ──
graph = StateGraph(RouterState)

graph.add_node("evaluate", evaluate)
graph.add_node("high", high_node)
graph.add_node("medium", medium_node)
graph.add_node("low", low_node)

# 边定义
graph.add_edge(START, "evaluate")
# 条件边：从 evaluate 出发，由 route_by_score 决定走向
graph.add_conditional_edges(
    "evaluate",           # 从哪个节点出发
    route_by_score,       # 路由决策函数
    {                     # 返回值 → 目标节点的映射
        "high": "high",
        "medium": "medium",
        "low": "low",
    }
)
# 三个分支都汇聚到 END
graph.add_edge("high", END)
graph.add_edge("medium", END)
graph.add_edge("low", END)

app = graph.compile()

# ── 执行 ──
result = app.invoke({"score": 0.0, "decision": ""})
print(f"\n最终结果：{result}")
"""
输出：
📊 评估完成，得分：0.75
⚠️  中等质量内容，进入人工审核队列
最终结果：{'score': 0.75, 'decision': 'medium_review'}
"""
```

#### ⚠️ 关键要点

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  add_conditional_edges 的三个参数：                    │
│  1. 源节点名（str）—— 从哪个节点出发                    │
│  2. 路由函数（callable）—— 接收 state，返回分支名       │
│  3. 路由映射（dict）—— {"返回值": "目标节点名"}          │
│                                                     │
│  ⚠️ 路由函数的返回值必须在映射表中，否则运行时报错！       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 2.3 模式二：基于大模型的路由

> **让 LLM 来分析用户输入，动态决定下一步行动**——适用于模糊、复杂、无法用简单规则覆盖的场景。

#### 场景

用户输入一句话，LLM 判断需要执行什么操作：

```
用户："今天天气怎么样？"      → LLM 判断 → 需要搜索信息
用户："帮我算 156 × 328"     → LLM 判断 → 需要计算
用户："你好啊"               → LLM 判断 → 直接回复
用户："那个，呃……"           → LLM 判断 → 需要澄清意图
```

#### 流程图

```
        ┌─────────────┐
        │  用户输入    │
        └──────┬──────┘
               ↓
        ┌─────────────┐
        │  LLM 分析   │ ← 大模型判断意图
        │  (classify) │
        └──────┬──────┘
               ↓
    ┌──────────┼──────────┬──────────┐
    ↓          ↓          ↓          ↓
 search    calculate   respond   clarify
    ↓          ↓          ↓          ↓
    └──────────┴──────────┴──────────┘
               ↓
        ┌─────────────┐
        │     END     │
        └─────────────┘
```

#### 完整代码

```python
# ── 依赖导入 ──
import os
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI

# ── 设置 API Key 和模型 ──
os.environ["OPENAI_API_KEY"] = "your-api-key-here"
# 使用硅基流动的千问 8B 模型
llm = ChatOpenAI(
    model="Qwen/Qwen2.5-7B-Instruct",
    base_url="https://api.siliconflow.cn/v1",
    api_key=os.environ.get("SILICONFLOW_API_KEY", os.environ["OPENAI_API_KEY"])
)

# ── 定义 State ──
class AgentState(TypedDict):
    user_input: str         # 用户的原始输入
    intent: str             # LLM 分析出的意图
    result: str             # 最终执行结果

# ── 意图分析节点（LLM 驱动）──
def classify_intent(state: AgentState) -> AgentState:
    """
    让 LLM 分析用户输入，判断意图类别。
    这是一个典型的 LLM 驱动路由：
    LLM 的输出决定了流程的走向。
    """
    prompt = f"""分析以下用户输入，判断其意图类别。只输出以下四个类别之一：
- search：用户需要搜索信息
- calculate：用户需要数学计算
- respond：用户需要直接回复
- clarify：用户意图不明确，需要澄清

用户输入："{state['user_input']}"

意图："""

    response = llm.invoke(prompt)
    intent = response.content.strip().lower()
    print(f"🤖 LLM 判断意图：{intent}")
    return {"intent": intent}

# ── 各行动节点 ──
def search_node(state: AgentState) -> AgentState:
    print("🔍 正在搜索相关信息...")
    return {"result": f"搜索结果：关于「{state['user_input']}」的信息如下..."}

def calculate_node(state: AgentState) -> AgentState:
    print("🧮 正在计算...")
    return {"result": f"计算结果：..."}

def respond_node(state: AgentState) -> AgentState:
    print("💬 直接回复用户...")
    response = llm.invoke(state["user_input"])
    return {"result": response.content}

def clarify_node(state: AgentState) -> AgentState:
    print("❓ 需要澄清用户意图...")
    return {"result": "请问你能再具体描述一下你的需求吗？"}

# ── LLM 路由函数 ──
def route_by_intent(state: AgentState) -> str:
    """根据 LLM 分析出的意图进行路由"""
    intent = state["intent"]
    # 防御性处理：如果 LLM 返回了预期外的值
    if intent not in ["search", "calculate", "respond", "clarify"]:
        return "respond"  # 默认走直接回复
    return intent

# ── 构建图 ──
graph = StateGraph(AgentState)

graph.add_node("classify", classify_intent)
graph.add_node("search", search_node)
graph.add_node("calculate", calculate_node)
graph.add_node("respond", respond_node)
graph.add_node("clarify", clarify_node)

graph.add_edge(START, "classify")
graph.add_conditional_edges(
    "classify",
    route_by_intent,
    {
        "search": "search",
        "calculate": "calculate",
        "respond": "respond",
        "clarify": "clarify",
    }
)
for node in ["search", "calculate", "respond", "clarify"]:
    graph.add_edge(node, END)

app = graph.compile()

# ── 执行 ──
result = app.invoke({"user_input": "今天北京的天气怎么样？", "intent": "", "result": ""})
print(f"\n最终结果：{result['result']}")
```

#### ⚠️ LLM 路由的注意事项

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  LLM 路由的关键风险：LLM 输出不可控                    │
│                                                     │
│  ❌ 风险1：LLM 可能输出预期之外的值                    │
│     防御：route 函数中做兜底处理（默认分支）            │
│                                                     │
│  ❌ 风险2：LLM 调用增加延迟和成本                      │
│     对策：能用规则解决的，不要用 LLM                    │
│                                                     │
│  ❌ 风险3：LLM 返回格式不稳定                          │
│     对策：用 StructuredOutputParser 约束输出格式       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 2.4 模式三：多级路由（漏斗式决策）

> **先粗筛，后细分**——先用大模型做初步分类，再根据分类结果进入细化的二级路由。

#### 场景

一个客服系统，需要先把用户问题分类为"科技"或"商业"，然后在科技类中再按紧急程度细分：

```
所有问题
    ├── 科技类 → 再判断紧急程度
    │       ├── urgent → 紧急技术工单
    │       └── normal → 普通技术工单
    ├── 商业类 → 直接进入商业处理
    └── 无法判断 → 转人工
```

#### 流程图

```
                  ┌─────────┐
                  │  用户输入 │
                  └────┬────┘
                       ↓
               ┌───────────────┐
               │  classify     │ ← 第一级：粗筛（LLM）
               │  初筛分类      │
               └──┬────┬────┬──┘
                  ↓    ↓    ↓
                tech   biz   unknown
                  ↓    ↓       ↓
        ┌─────────┐  biz    ┌──────┐
        │ 二级分类  │  处理   │ END  │
        │ urgency  │   ↓     └──────┘
        └──┬──┬───┘  END
           ↓  ↓
        urgent normal
           ↓     ↓
      ┌────────┐ ┌────────┐
      │tech    │ │tech    │
      │urgent  │ │normal  │
      └───┬────┘ └───┬────┘
          ↓          ↓
        END        END
```

#### 完整代码

```python
# ── 依赖导入 ──
import os
from typing import TypedDict
from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI

# ── 模型初始化 ──
llm = ChatOpenAI(
    model="Qwen/Qwen2.5-7B-Instruct",
    base_url="https://api.siliconflow.cn/v1",
    api_key="your-api-key"
)

# ── 定义 State ──
class TicketState(TypedDict):
    user_input: str         # 用户原始输入
    category: str           # 一级分类：tech / biz / unknown
    urgency: str            # 二级分类（仅科技类）：urgent / normal
    result: str             # 处理结果

# ── 第一级：粗筛分类 ──
def classify_first(state: TicketState) -> TicketState:
    """LLM 做一级分类：科技 or 商业 or 无法判断"""
    prompt = f"""分析以下用户问题，判断类别。只输出以下之一：
- tech：科技/技术相关问题
- biz：商业/业务相关问题
- unknown：无法判断

用户问题：{state['user_input']}

类别："""
    response = llm.invoke(prompt)
    category = response.content.strip().lower()
    print(f"📋 一级分类结果：{category}")
    return {"category": category}

# ── 第二级：科技类按紧急程度细分 ──
def classify_urgency(state: TicketState) -> TicketState:
    """LLM 判断科技类问题的紧急程度"""
    prompt = f"""分析以下技术问题，判断紧急程度。只输出以下之一：
- urgent：系统故障、数据丢失等需要立即处理
- normal：功能咨询、配置问题等常规处理

用户问题：{state['user_input']}

紧急程度："""
    response = llm.invoke(prompt)
    urgency = response.content.strip().lower()
    print(f"⏰ 紧急程度判断：{urgency}")
    return {"urgency": urgency}

# ── 各处理节点 ──
def tech_urgent(state: TicketState) -> TicketState:
    print("🚨 紧急技术工单！立即处理...")
    return {"result": "紧急技术工单已创建，SLA: 1小时"}

def tech_normal(state: TicketState) -> TicketState:
    print("🔧 普通技术工单，常规处理...")
    return {"result": "普通技术工单已创建，SLA: 24小时"}

def biz_process(state: TicketState) -> TicketState:
    print("💼 商业咨询处理...")
    return {"result": "商业工单已创建"}

def unknown_process(state: TicketState) -> TicketState:
    print("🔄 转人工处理...")
    return {"result": "已转接人工客服"}

# ── 路由函数 ──
def route_by_category(state: TicketState) -> str:
    """一级路由：根据类别分发"""
    category = state["category"]
    if category == "tech":
        return "tech"
    elif category == "biz":
        return "biz"
    else:
        return "unknown"

def route_by_urgency(state: TicketState) -> str:
    """二级路由：科技类按紧急程度分发"""
    urgency = state["urgency"]
    return "urgent" if urgency == "urgent" else "normal"

# ── 构建图 ──
graph = StateGraph(TicketState)

# 添加所有节点
graph.add_node("classify", classify_first)
graph.add_node("urgency_check", classify_urgency)
graph.add_node("tech_urgent", tech_urgent)
graph.add_node("tech_normal", tech_normal)
graph.add_node("biz", biz_process)
graph.add_node("unknown", unknown_process)

# 边定义
graph.add_edge(START, "classify")
graph.add_conditional_edges(
    "classify", route_by_category,
    {"tech": "urgency_check", "biz": "biz", "unknown": "unknown"}
)
graph.add_conditional_edges(
    "urgency_check", route_by_urgency,
    {"urgent": "tech_urgent", "normal": "tech_normal"}
)
for node in ["tech_urgent", "tech_normal", "biz", "unknown"]:
    graph.add_edge(node, END)

app = graph.compile()

# ── 执行 ──
result = app.invoke({
    "user_input": "我们的数据库突然宕机了，所有用户都无法访问！",
    "category": "", "urgency": "", "result": ""
})
print(f"\n最终处理：{result['result']}")
```

> 💡 **设计思想**：多级路由的本质是"漏斗式决策"——先做粗粒度的分流，缩小决策范围，再做精细化的判断。这种模式在生产环境中非常常见。

### 2.5 模式四：Agent 行动循环（ReAct 模式）

> **思考 → 行动 → 观察 → 再思考 → ……** ——这是 LangGraph 最强大的路由模式，也是构建自主 Agent 的基础。

#### 核心循环

```
        ┌────────────────────────────────┐
        ↓                                │
   用户输入                                │
        ↓                                │
  ┌──────────┐                           │
  │   THINK  │ ← 思考：我需要做什么？       │
  └────┬─────┘                           │
       ↓                                 │
  ┌─────────────┐                        │
  │ should       │                        │
  │ continue?    │── 结束 → END            │
  └──────┬──────┘                        │
         │ 继续                           │
         ↓                               │
  ┌──────────┐                           │
  │   ACT    │ ← 行动：执行某个操作         │
  └────┬─────┘                           │
       ↓                                 │
  ┌──────────┐                           │
  │ OBSERVE  │ ← 观察：看看结果怎样         │
  └────┬─────┘                           │
       │                                 │
       └─────────────────────────────────┘
```

#### 完整代码

```python
# ── 依赖导入 ──
import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

# ── 模型初始化 ──
llm = ChatOpenAI(
    model="Qwen/Qwen2.5-7B-Instruct",
    base_url="https://api.siliconflow.cn/v1",
    api_key="your-api-key"
)

# ── 定义 State ──
class AgentLoopState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]  # 对话历史（累加）
    iterations: int        # 当前已循环次数
    max_iterations: int    # 最大循环次数上限（防止死循环）
    final_answer: str      # 最终答案

# ── 思考节点 ──
def think_node(state: AgentLoopState) -> AgentLoopState:
    """
    思考节点：让 LLM 分析当前状态，决定下一步。
    如果 LLM 的回答包含"最终答案"这几个字，
    就认为 Agent 已经得出结论。
    """
    # 构建上下文
    messages = state["messages"]
    think_prompt = (
        "你需要逐步思考并解决问题。"
        "如果你得出了最终结论，请在回复中包含「最终答案」四个字。"
    )
    all_messages = [HumanMessage(content=think_prompt)] + list(messages)

    response = llm.invoke(all_messages)
    print(f"💭 Think: {response.content[:100]}...")

    # 判断是否得到了最终答案
    final_answer = ""
    if "最终答案" in response.content:
        final_answer = response.content
        print("✅ 检测到「最终答案」关键字，Agent 得出最终结论！")

    return {
        "messages": [response],
        "iterations": state["iterations"] + 1,
        "final_answer": final_answer,
    }

# ── 循环控制函数 ──
def should_continue(state: AgentLoopState) -> str:
    """
    决定是否继续循环。两种情况结束：
    1. LLM 已经给出了最终答案
    2. 循环次数达到上限（防止死循环）
    """
    # 条件1：有最终答案
    if state["final_answer"]:
        print("🎯 有最终答案，结束循环")
        return "end"

    # 条件2：达到最大循环次数
    if state["iterations"] >= state["max_iterations"]:
        print(f"⏰ 已达最大循环次数 {state['max_iterations']}，强制结束")
        return "end"

    # 否则继续循环
    print(f"🔄 继续循环（第 {state['iterations']}/{state['max_iterations']} 次）")
    return "continue"

# ── 执行节点 ──
def act_node(state: AgentLoopState) -> AgentLoopState:
    """
    执行节点：在实际应用中，这里会调用工具、访问 API 等。
    这里做简化演示：记录执行动作。
    """
    print(f"🔧 Act: 执行第 {state['iterations']} 轮操作...")
    # 实际场景中：state["messages"][-1] 中包含 tool_calls
    return {"messages": [AIMessage(content=f"[第{state['iterations']}轮执行完成]")]}

# ── 构建图 ──
graph = StateGraph(AgentLoopState)

graph.add_node("think", think_node)
graph.add_node("act", act_node)

graph.add_edge(START, "think")
graph.add_conditional_edges(
    "think",
    should_continue,
    {
        "end": END,          # 结束
        "continue": "act",   # 继续 → 先执行
    }
)
graph.add_edge("act", "think")  # 执行完再思考 ← 循环的关键！

app = graph.compile()

# ── 执行 ──
result = app.invoke({
    "messages": [HumanMessage(content="请分析一下 Python 和 Go 各自适合什么场景？")],
    "iterations": 0,
    "max_iterations": 5,     # ⚠️ 设置上限，防止无限循环
    "final_answer": "",
})
print(f"\n总共循环 {result['iterations']} 次")
print(f"最终答案：{result['final_answer'][:200] if result['final_answer'] else '未生成最终答案'}")
```

#### ⚠️ 循环控制的三大防线

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  防止 Agent 死循环的三道防线：                          │
│                                                     │
│  防线1：max_iterations 上限                           │
│        → 硬性限制，循环次数达到上限就强制结束            │
│                                                     │
│  防线2：最终答案检测                                    │
│        → LLM 返回特定标记（如「最终答案」）时结束        │
│                                                     │
│  防线3：时间限制（生产环境推荐）                          │
│        → 用 timeout 参数限制总执行时间                  │
│                                                     │
│  缺一不可！线上环境尤其要注意防线1+防线3                  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 三、Streaming——流式输出的三种模式

### 3.1 概述——LangGraph 中的流式输出

Streaming 在 LangChain 中我们已经很熟悉了——让用户第一时间看到输出，提升体感速度。在 LangGraph 中，streaming 的意义更大：

```
LangGraph Streaming 的双重价值：

1. 用户体验（同 LangChain）
   └── Token 级别打字机效果，无需等待全部生成

2. 过程可观察（LangGraph 独有）
   └── 实时监控每个节点的思考过程
   └── 不是只看最后结果，而是看到"每一步在做什么"
```

LangGraph 提供了三种 Streaming 模式，可以用一句话概括区别：

| 模式 | 一句话概括 | 返回内容 |
|------|-----------|----------|
| **values** | "给我看最新的完整剧本" | 每一步执行完后**完整图状态**的完整快照 |
| **updates** | "告诉我刚刚发生了什么变化" | 每一步执行完后**仅变化部分** |
| **messages** | "每个字都实时告诉我" | **Token 级别**的 LLM 输出流 |

### 3.2 values 模式——完整状态快照

```python
# ── values 模式示例 ──
# 触发时机：每个节点执行完毕后
# 返回数据：包含 State 中定义的所有字段，即使某些字段没有变化

# 假设 State 定义为：
# class State(TypedDict):
#     messages: list
#     user_info: dict
#     progress: int

for chunk in app.stream(
    {"messages": [HumanMessage(content="你好，帮我查一下订单")]},
    stream_mode="values"
):
    print(f"📦 完整状态快照：{chunk}")

"""
输出示例：
📦 完整状态快照：{
    'messages': [HumanMessage('你好')],
    'user_info': {'name': '张三', 'level': 'VIP'},
    'progress': 0
}
📦 完整状态快照：{
    'messages': [HumanMessage(...), AIMessage('您好...')],  # 增加了 AI 回复
    'user_info': {'name': '张三', 'level': 'VIP'},         # 没变也返回
    'progress': 0                                           # 没变也返回
}
"""
```

| 特性 | 说明 |
|------|------|
| **触发时机** | 每个节点执行完成后 |
| **数据格式** | 包含 State 中**所有字段**的完整字典 |
| **优点** | 前端或调试场景需要同步展示所有上下文 |
| **缺点** | State 字段多时数据量大，浪费带宽 |
| **典型场景** | 进度条展示（需全量 state 计算百分比） |

### 3.3 updates 模式——增量状态变化

```python
# ── updates 模式示例 ──
# 触发时机：每个节点执行完毕后
# 返回数据：仅返回当前节点产生变化的部分

for chunk in app.stream(
    {"messages": [HumanMessage(content="你好")]},
    stream_mode="updates"
):
    # chunk 是一个字典：{节点名称: 该节点的输出}
    print(f"🔄 变化：{chunk}")

"""
输出示例：
🔄 变化：{"agent": {"messages": [AIMessage('您好！有什么可以帮助您的？')]}}
🔄 变化：{"tools": {"messages": [ToolMessage('查询结果...')]}}
"""
```

| 特性 | 说明 |
|------|------|
| **触发时机** | 每个节点执行完成后 |
| **数据格式** | 字典：`{节点名称: 该节点的输出结果}` |
| **优点** | 节省带宽，知道"哪个 agent 在干活及产出了什么" |
| **典型场景** | 多 Agent 场景追踪；前端只需追加新消息 |

### 3.4 messages 模式——Token 级打字机效果

```python
# ── messages 模式示例 ──
# 类似 LangChain 的 .stream()，以 Token 粒度输出 LLM 生成的内容

for chunk in app.stream(
    {"messages": [HumanMessage(content="讲个笑话")]},
    stream_mode="messages"
):
    # chunk 是 LLM 逐 Token 输出的内容
    print(chunk, end="", flush=True)  # 不换行，实现打字机效果

"""
输出效果（逐步出现）：
好|的|，|这|里|给|你|讲|一|个|笑|话|……
"""
```

| 特性 | 说明 |
|------|------|
| **触发时机** | LLM 生成 Token 时实时输出 |
| **数据格式** | Token 级别的增量文本 |
| **优点** | 最好的用户体验（打字机效果） |
| **典型场景** | 聊天 UI 需要打字机效果 |

### 3.5 多模式组合

LangGraph 允许**同时开启多种 streaming 模式**：

```python
# ── 同时使用 updates + messages ──
# 既知道哪个 Agent 在工作（updates），又享受打字机效果（messages）

for chunk in app.stream(
    {"messages": [HumanMessage(content="帮我分析这段代码")]},
    stream_mode=["updates", "messages"]  # ⚠️ 注意：是列表
):
    print(f"📡 {chunk}")
```

---

## 四、Human-in-the-Loop——人工介入机制

### 4.1 概述

> **Human-in-the-Loop（人机协作）**：在 Agent 执行的关键节点处暂停，等待人类确认、审核或修改数据后，再继续执行。

```
没有 Human-in-the-Loop 的 Agent：
    用户输入 → AI分析 → AI执行 → AI决策 → 输出结果
    🚨 问题：AI 直接发邮件、AI 直接拒绝退款、AI 直接删除数据……

有 Human-in-the-Loop 的 Agent：
    用户输入 → AI分析 → AI执行 → ⏸️ 暂停等人工确认
                                    ↓
                              人类审核（通过/驳回/修改）
                                    ↓
                              继续执行 → 输出结果
    ✅ 安全：关键决策由人把关
```

### 4.2 核心方法：interrupt

`interrupt` 是 Human-in-the-Loop 的核心方法，它可以在节点内部暂停整个图的执行：

```python
from langgraph.types import interrupt

# interrupt 会在调用处暂停图的执行
# 暂停后，需要通过 app.update_state() 来恢复
```

#### 流程详解

```
invoke(graph)                    update_state(graph)
      ↓                                ↓
  ┌─────────┐                    ┌─────────┐
  │ 节点A   │ 执行完成              │ 注入人类  │
  └────┬────┘                    │ 的决策    │
       ↓                         └────┬────┘
  ┌─────────┐                         ↓
  │ 节点B   │                    ┌─────────┐
  │ interrupt│ ← ⏸️ 暂停在这里     │ 节点C   │ 从暂停处继续
  └─────────┘                    └────┬────┘
                                      ↓
                                  ┌─────────┐
                                  │ 节点D   │
                                  └─────────┘
```

### 4.3 完整示例——内容审核系统

```python
# ── 依赖导入 ──
import os
from typing import TypedDict
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt  # ⚠️ 核心：interrupt 方法
from langchain_openai import ChatOpenAI

# ── 模型初始化 ──
llm = ChatOpenAI(
    model="Qwen/Qwen2.5-7B-Instruct",
    base_url="https://api.siliconflow.cn/v1",
    api_key="your-api-key"
)

# ── 定义 State ──
class ReviewState(TypedDict):
    content: str            # 待审核的内容
    ai_analysis: str        # AI 的分析结果
    approved: bool          # 人工审核结果
    final_result: str       # 最终结果

# ── 生成节点 ──
def generate_content(state: ReviewState) -> ReviewState:
    """AI 生成或分析内容"""
    print("📝 AI 正在生成/分析内容...")
    analysis = llm.invoke(f"请分析以下内容的质量：{state['content']}")
    return {"ai_analysis": analysis.content}

# ── 人工审核节点（含 interrupt）──
def review_node(state: ReviewState) -> ReviewState:
    """
    人工审核节点。
    包含 interrupt 调用，执行到这里时会暂停，
    等待人类通过 update_state 确认后继续。
    """
    print(f"📋 待审核内容：{state['content'][:100]}...")
    print(f"🤖 AI 分析结果：{state['ai_analysis'][:100]}...")

    # ⚠️ interrupt：在这里暂停，等待人工决策
    # interrupt 的参数会作为提示信息返回给调用方
    human_decision = interrupt({
        "message": "请审核以下内容，是否批准发布？",
        "options": ["approve", "reject", "request_changes"],
        "content": state["content"],
        "ai_analysis": state["ai_analysis"],
    })

    # 人类通过 update_state 注入决策后，代码从这里继续执行
    print(f"👤 人工审核结果：{human_decision}")
    return {"approved": human_decision.get("decision") == "approve"}

# ── 发布节点 ──
def publish_node(state: ReviewState) -> ReviewState:
    print("✅ 内容审核通过，已发布！")
    return {"final_result": "已发布"}

# ── 驳回节点 ──
def reject_node(state: ReviewState) -> ReviewState:
    print("❌ 内容被驳回")
    return {"final_result": "已驳回"}

# ── 路由函数 ──
def route_after_review(state: ReviewState) -> str:
    return "publish" if state["approved"] else "reject"

# ── 构建图 ──
checkpointer = MemorySaver()
graph = StateGraph(ReviewState)

graph.add_node("generate", generate_content)
graph.add_node("review", review_node)
graph.add_node("publish", publish_node)
graph.add_node("reject", reject_node)

graph.add_edge(START, "generate")
graph.add_edge("generate", "review")
graph.add_conditional_edges(
    "review", route_after_review,
    {"publish": "publish", "reject": "reject"}
)
graph.add_edge("publish", END)
graph.add_edge("reject", END)

app = graph.compile(checkpointer=checkpointer)

# ── 执行流程 ──
config = {"configurable": {"thread_id": "review-demo-001"}}

print("===== 第一次调用：执行到 interrupt 处暂停 =====")
# 第一次 invoke：会执行到 review_node 的 interrupt 处暂停
# 注意：这是一个耗时的操作，在实际应用中需要用异步方式处理
try:
    result = app.invoke(
        {"content": "人工智能正在改变我们的生活方式...", "approved": False, "final_result": ""},
        config=config
    )
    print(f"调用完成：{result}")
except Exception as e:
    print(f"⏸️  流程已暂停在 interrupt 处：{e}")

# 检查当前状态
state = app.get_state(config)
print(f"\n当前状态：")
print(f"  下一个待执行的节点：{state.next}")
print(f"  当前 State 的值：{state.values}")

print("\n===== 人工做出决策后，恢复执行 =====")
# 人类做出决策
human_decision = {"decision": "approve", "comment": "内容质量不错，可以发布"}

# ⚠️ update_state：注入人类决策，恢复图执行
app.update_state(
    config,
    {"approved": human_decision["decision"] == "approve"}
)

# 继续执行（从 review 节点之后继续）
result = app.invoke(None, config=config)
print(f"\n最终结果：{result['final_result']}")
```

### 4.4 update_state 的关键作用

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  app.update_state(config, values) 做了什么？          │
│                                                     │
│  1. 接收人类或外部系统提供的决策数据                    │
│  2. 将数据更新到当前 Thread 的 State 中               │
│  3. 解除 interrupt 的暂停状态                         │
│  4. 让图从暂停的节点继续执行                           │
│                                                     │
│  ⚠️ 关键提醒：                                         │
│  config 中必须包含 thread_id，                         │
│  这样才能定位到正确的暂停线程                           │
│                                                     │
│  生产环境中的典型模式：                                  │
│  1. invoke → 运行到 interrupt 暂停                    │
│  2. 记录 thread_id 到数据库                            │
│  3. 人类审核完成 → 从数据库取出 thread_id               │
│  4. update_state + invoke → 继续执行                  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 五、时间旅行——回溯历史与探索分支

### 5.1 概述

> **时间旅行（Time Travel）**：查看图执行的历史记录，回溯到任意历史状态，甚至从历史状态出发创建新的执行分支。

时间旅行赋予 LangGraph 三大能力：

```
能力一：历史查看（History）
    └── 查看每次执行的完整状态 → 调试排查、审计追溯

能力二：状态回溯（Rewind）
    └── 恢复到过去任意时间点 → 出错后回到正确状态重新执行

能力三：分支探索（Branching）
    └── 从历史节点出发，探索新的可能 → 对比不同决策的结果

LangGraph 的图不是死流程图——它是可以在时间轴上任意穿梭的动态系统！
```

### 5.2 查看执行历史——get_state_history

```python
# ── 完整示例：时间旅行 ──
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

# ── 定义 State ──
class CounterState(TypedDict):
    count: int          # 计数器
    history_list: Annotated[list, lambda x, y: (x or []) + (y or [])]  # 累加列表

# ── 三个节点，每个节点 count+1 ──
def step1(state: CounterState) -> CounterState:
    print(f"📍 Step1: count 从 {state['count']} → {state['count'] + 1}")
    return {
        "count": state["count"] + 1,
        "history_list": [f"step1完成(count={state['count']+1})"]
    }

def step2(state: CounterState) -> CounterState:
    print(f"📍 Step2: count 从 {state['count']} → {state['count'] + 1}")
    return {
        "count": state["count"] + 1,
        "history_list": [f"step2完成(count={state['count']+1})"]
    }

def step3(state: CounterState) -> CounterState:
    print(f"📍 Step3: count 从 {state['count']} → {state['count'] + 1}")
    return {
        "count": state["count"] + 1,
        "history_list": [f"step3完成(count={state['count']+1})"]
    }

# ── 构建图 ──
checkpointer = MemorySaver()
graph = StateGraph(CounterState)

graph.add_node("step1", step1)
graph.add_node("step2", step2)
graph.add_node("step3", step3)

graph.add_edge(START, "step1")
graph.add_edge("step1", "step2")
graph.add_edge("step2", "step3")
graph.add_edge("step3", END)

app = graph.compile(checkpointer=checkpointer)

# ── 执行 ──
config = {"configurable": {"thread_id": "time-travel-demo"}}
result = app.invoke({"count": 0, "history_list": []}, config=config)
print(f"\n执行完成，最终 count = {result['count']}")

# ── 查看执行历史 ──
print("\n===== 执行历史 =====")
# get_state_history 返回所有 Checkpoint，按时间倒序
# 最近的在前面，最古早的在后面
all_history = list(app.get_state_history(config))
print(f"总共 {len(all_history)} 个 checkpoint\n")

for i, checkpoint in enumerate(all_history):
    print(f"[{i}] checkpoint_id: {checkpoint.config['configurable']['checkpoint_id'][:8]}...")
    print(f"    count = {checkpoint.values.get('count', 'N/A')}")
    print(f"    history_list = {checkpoint.values.get('history_list', [])}")
    print()
```

**输出效果**：

```
执行完成，最终 count = 3

===== 执行历史 =====
总共 5 个 checkpoint

[0] checkpoint_id: 1a2b3c4d...  ← 最近：step3 完成后
    count = 3
    history_list = ['step1完成(count=1)', 'step2完成(count=2)', 'step3完成(count=3)']

[1] checkpoint_id: 2b3c4d5e...  ← step2 完成后
    count = 2
    history_list = ['step1完成(count=1)', 'step2完成(count=2)']

[2] checkpoint_id: 3c4d5e6f...  ← step1 完成后
    count = 1
    history_list = ['step1完成(count=1)']

[3] checkpoint_id: 4d5e6f7g...  ← 初始状态
    count = 0
    history_list = []

[4] checkpoint_id: 5e6f7g8h...  ← 更早的 checkpoint
```

### 5.3 回溯到历史状态

> **通过指定 checkpoint_id，可以回到任意历史时间点继续执行。**

```python
# ── 回溯到 count=1 的历史状态 ──
all_history = list(app.get_state_history(config))

# 选择倒数第三个 checkpoint（count=1 的状态）
target_checkpoint = all_history[-3]  # 索引从大到小 = 时间从新到旧
target_checkpoint_id = target_checkpoint.config["configurable"]["checkpoint_id"]

print(f"🎯 目标 checkpoint：{target_checkpoint_id[:8]}...")
print(f"   历史状态 count = {target_checkpoint.values['count']}")

# ── 从历史状态重新执行 ──
# 在 config 中同时指定 thread_id 和 checkpoint_id
replay_config = {
    "configurable": {
        "thread_id": "time-travel-demo",          # 同一个 thread
        "checkpoint_id": target_checkpoint_id,     # 历史 checkpoint
    }
}

# 从 count=1 的状态重新执行，相当于"回到过去，重新出发"
result = app.invoke(None, config=replay_config)
print(f"\n从 count=1 回溯后重新执行完毕，最终 count = {result['count']}")
# 输出：count = 3（重新走完了 step2 和 step3）
```

### 5.4 从历史状态创建新分支

```
同一个 Thread 的时间线：

  原始路径： START → step1 → step2 → step3 → END
                                             ↑
              checkpoint[4]                   ↑
              count=1                         ↑
                  │                           ↑
                  ├── 原始继续：step2 → step3 → END
                  │
                  └── 🆕 新分支（可以走不同路线！）
                       在 step1 后修改状态
                       → 走不同的 path
                       → 得到不同结果
```

```python
# ── 从历史状态创建新分支 ──
# 先回溯到 count=1 的 checkpoint
branch_config = {
    "configurable": {
        "thread_id": "time-travel-demo",
        "checkpoint_id": target_checkpoint_id,
    }
}

# 修改状态后再继续（例如手动修改 count 的初始值）
app.update_state(branch_config, {"count": 100})

# 从修改后的状态继续执行
result = app.invoke(None, config=branch_config)
print(f"新分支执行结果：count = {result['count']}")  # 输出：count = 103
```

### 5.5 时间旅行的应用场景

| 场景 | 操作 | 价值 |
|------|------|------|
| **调试排查** | `get_state_history` 查看每一步的状态 | 定位哪一步出了问题 |
| **错误恢复** | 回溯到出错前的 checkpoint，修正后继续 | 避免从头重跑 |
| **对比分析** | 从同一 checkpoint 出发，注入不同数据 | 对比不同决策路径的结果 |
| **审计合规** | 保留完整执行历史 | 满足监管审计要求 |
| **迭代实验** | 反复从某个 checkpoint 出发尝试不同方案 | 快速验证不同策略的效果 |

---

## 六、综合实战——交互式内容审核工作流

### 6.1 实战概述

我们将本节课四个知识点——**动态路由、Streaming、Human-in-the-Loop、时间旅行**——全部整合到一个实战项目中：

> **交互式内容审核工作流**：一个具备 AI 自动分析、多级人工审核、流式进度展示、历史追溯和可撤销决策的完整内容审核系统。

#### 功能清单

```
✅ 内容自动分析（毒性检测、垃圾信息检测、质量评分）
✅ AI 智能路由（自动通过 / 自动拒绝 / 转人工）
✅ 流式进度展示（实时看每一步的分析进展）
✅ 多级人工审核（一级审核 → 二级审核（升级））
✅ 历史追溯（查看每一步的完整状态）
✅ 可撤销决策（回溯到审核前重新判断）
```

### 6.2 流程图

```
                          ┌──────────┐
                          │   START  │
                          └────┬─────┘
                               ↓
                     ┌─────────────────┐
                     │ analyze_toxicity │  ← AI 分析毒性
                     └────────┬────────┘
                              ↓
                     ┌─────────────────┐
                     │ analyze_spam     │  ← AI 分析垃圾信息
                     └────────┬────────┘
                              ↓
                     ┌─────────────────┐
                     │ analyze_quality  │  ← AI 分析内容质量
                     └────────┬────────┘
                              ↓
                     ┌─────────────────┐
                     │ ai_recommendation│  ← AI 综合决策路由
                     └──┬──┬──┬────┬───┘
                        ↓  ↓  ↓    ↓
                   auto_   auto_   need_
                   approve reject human
                      ↓     ↓       ↓
                    END    END  ┌─────────────┐
                                │ level1_review│ ← ⏸️ 一级人工审核
                                └──┬──┬──┬────┘
                                   ↓  ↓  ↓
                               approve reject escalate
                                  ↓     ↓     ↓
                                 END   END  ┌─────────────┐
                                            │ level2_review│ ← ⏸️ 二级人工审核
                                            └──┬──┬──┬────┘
                                               ↓  ↓  ↓
                                           approve reject flag
                                              ↓     ↓     ↓
                                             END   END   END
```

### 6.3 完整代码

```python
# ════════════════════════════════════════════════════════════
#  综合实战：交互式内容审核工作流
#  知识点：动态路由 + Streaming + Human-in-the-Loop + 时间旅行
# ════════════════════════════════════════════════════════════

# ── 依赖导入 ──
import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import interrupt
from langchain_openai import ChatOpenAI

# ── 环境设置 ──
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

llm = ChatOpenAI(
    model="Qwen/Qwen2.5-7B-Instruct",
    base_url="https://api.siliconflow.cn/v1",
    api_key="your-api-key"
)

# ── State 定义 ──
class ContentReviewState(TypedDict):
    content: str                # 待审核的原始内容
    toxicity_score: float       # 毒性得分（0-1）
    spam_score: float           # 垃圾信息得分（0-1）
    quality_score: float        # 内容质量得分（0-1）
    ai_decision: str            # AI 决策：auto_approve / auto_reject / need_human
    level1_decision: str        # 一级审核：approve / reject / escalate
    level2_decision: str        # 二级审核：approve / reject / flag
    final_result: str           # 最终结果

# ── 节点1：毒性分析 ──
def analyze_toxicity(state: ContentReviewState) -> ContentReviewState:
    """分析内容的毒性程度"""
    print("🔬 正在分析内容毒性...")
    prompt = f"""请分析以下内容的毒性程度，给出 0-1 之间的分数。
0 = 完全无害，1 = 极端有害。
只输出数字，不要包含任何其他文字。

内容：{state['content']}

毒性得分："""
    response = llm.invoke(prompt)
    try:
        score = float(response.content.strip())
    except ValueError:
        score = 0.0
    print(f"   毒性得分：{score}")
    return {"toxicity_score": score}

# ── 节点2：垃圾信息分析 ──
def analyze_spam(state: ContentReviewState) -> ContentReviewState:
    """分析内容是否为垃圾信息"""
    print("📧 正在分析垃圾信息可能性...")
    prompt = f"""请分析以下内容是否为垃圾/营销信息，给出 0-1 之间的分数。
0 = 完全不是垃圾信息，1 = 绝对是垃圾信息。
只输出数字。

内容：{state['content']}

垃圾得分："""
    response = llm.invoke(prompt)
    try:
        score = float(response.content.strip())
    except ValueError:
        score = 0.0
    print(f"   垃圾得分：{score}")
    return {"spam_score": score}

# ── 节点3：内容质量分析 ──
def analyze_quality(state: ContentReviewState) -> ContentReviewState:
    """分析内容质量"""
    print("⭐ 正在分析内容质量...")
    prompt = f"""请分析以下内容的质量，给出 0-1 之间的分数。
0 = 极差质量，1 = 极高质量。
只输出数字。

内容：{state['content']}

质量得分："""
    response = llm.invoke(prompt)
    try:
        score = float(response.content.strip())
    except ValueError:
        score = 0.5
    print(f"   质量得分：{score}")
    return {"quality_score": score}

# ── 节点4：AI 综合决策 ──
def ai_recommendation(state: ContentReviewState) -> ContentReviewState:
    """AI 综合三个得分给出建议"""
    toxicity = state["toxicity_score"]
    spam = state["spam_score"]
    quality = state["quality_score"]

    print(f"\n📊 AI 综合分析：毒性={toxicity}, 垃圾={spam}, 质量={quality}")

    # 决策逻辑
    if toxicity > 0.7 or spam > 0.7:
        decision = "auto_reject"
        print("   🚫 AI 决策：自动拒绝（毒性或垃圾信息得分过高）")
    elif toxicity < 0.3 and spam < 0.3 and quality > 0.6:
        decision = "auto_approve"
        print("   ✅ AI 决策：自动通过（各项指标良好）")
    else:
        decision = "need_human"
        print("   👤 AI 决策：需要人工审核（指标处于灰色地带）")

    return {"ai_decision": decision}

# ── 节点5：一级人工审核 ──
def level1_review(state: ContentReviewState) -> ContentReviewState:
    """一级人工审核节点——含 interrupt"""
    print("\n📋 === 一级人工审核 ===")
    print(f"   毒性得分：{state['toxicity_score']}")
    print(f"   垃圾得分：{state['spam_score']}")
    print(f"   质量得分：{state['quality_score']}")
    print(f"   内容摘要：{state['content'][:80]}...")

    # ⚠️ interrupt：暂停等待人工决策
    decision_info = interrupt({
        "level": "一级审核",
        "message": "请审核此内容",
        "options": ["approve（通过）", "escalate（升级到二级）", "reject（拒绝）"],
        "content": state["content"],
        "scores": {
            "toxicity": state["toxicity_score"],
            "spam": state["spam_score"],
            "quality": state["quality_score"],
        }
    })

    # 人工决策后，代码从这里继续
    human_decision = decision_info.get("decision", "escalate")
    print(f"   👤 一级审核决策：{human_decision}")
    return {"level1_decision": human_decision}

# ── 节点6：二级人工审核 ──
def level2_review(state: ContentReviewState) -> ContentReviewState:
    """二级人工审核节点——含 interrupt（高级审核员）"""
    print("\n🔍 === 二级人工审核 ===")
    print(f"   一级审核决定：升级处理")
    print(f"   内容摘要：{state['content'][:80]}...")

    # ⚠️ interrupt：暂停等待高级审核员决策
    decision_info = interrupt({
        "level": "二级审核",
        "message": "请高级审核员做出最终决定",
        "options": ["approve（通过）", "reject（拒绝）", "flag（标记）"],
        "content": state["content"],
        "level1_decision": state["level1_decision"],
    })

    human_decision = decision_info.get("decision", "flag")
    print(f"   👤 二级审核决策：{human_decision}")
    return {"level2_decision": human_decision}

# ── 路由函数 ──
def route_ai_decision(state: ContentReviewState) -> str:
    """AI 决策后的路由"""
    return state["ai_decision"]

def route_level1(state: ContentReviewState) -> str:
    """一级审核后的路由"""
    return state["level1_decision"]

def route_level2(state: ContentReviewState) -> str:
    """二级审核后的路由"""
    return state["level2_decision"]

# ── 结果节点 ──
def final_approve(state: ContentReviewState) -> ContentReviewState:
    print("✅ 内容最终通过审核，已发布！")
    return {"final_result": "approved"}

def final_reject(state: ContentReviewState) -> ContentReviewState:
    print("❌ 内容被驳回")
    return {"final_result": "rejected"}

def final_flag(state: ContentReviewState) -> ContentReviewState:
    print("🏴 内容被标记，需要进一步跟踪")
    return {"final_result": "flagged"}

# ── 构建图 ──
# 使用 SqliteSaver 做持久化存储
checkpointer = SqliteSaver.from_conn_string("content_review.db")

graph = StateGraph(ContentReviewState)

# 添加所有节点
graph.add_node("analyze_toxicity", analyze_toxicity)
graph.add_node("analyze_spam", analyze_spam)
graph.add_node("analyze_quality", analyze_quality)
graph.add_node("ai_recommendation", ai_recommendation)
graph.add_node("level1_review", level1_review)
graph.add_node("level2_review", level2_review)
graph.add_node("final_approve", final_approve)
graph.add_node("final_reject", final_reject)
graph.add_node("final_flag", final_flag)

# 边定义
graph.add_edge(START, "analyze_toxicity")
graph.add_edge("analyze_toxicity", "analyze_spam")
graph.add_edge("analyze_spam", "analyze_quality")
graph.add_edge("analyze_quality", "ai_recommendation")

# AI 决策路由
graph.add_conditional_edges(
    "ai_recommendation", route_ai_decision,
    {
        "auto_approve": "final_approve",
        "auto_reject": "final_reject",
        "need_human": "level1_review",
    }
)

# 一级审核路由
graph.add_conditional_edges(
    "level1_review", route_level1,
    {
        "approve": "final_approve",
        "reject": "final_reject",
        "escalate": "level2_review",
    }
)

# 二级审核路由
graph.add_conditional_edges(
    "level2_review", route_level2,
    {
        "approve": "final_approve",
        "reject": "final_reject",
        "flag": "final_flag",
    }
)

for node in ["final_approve", "final_reject", "final_flag"]:
    graph.add_edge(node, END)

app = graph.compile(checkpointer=checkpointer)

# ════════════════════════════════════════════════════════════
#  执行演示
# ════════════════════════════════════════════════════════════

print("═" * 60)
print("  交互式内容审核工作流演示")
print("═" * 60)

# ── 测试内容 ──
test_content = "陈泽鹏"  # 无明显问题的内容
config = {"configurable": {"thread_id": "review-001"}}

initial_state = {
    "content": test_content,
    "toxicity_score": 0.0,
    "spam_score": 0.0,
    "quality_score": 0.0,
    "ai_decision": "",
    "level1_decision": "",
    "level2_decision": "",
    "final_result": "",
}

# ── 第一阶段：AI 分析 + 路由 ──
print("\n【阶段1】AI 分析和路由...")
print("使用 streaming mode: updates\n")

for chunk in app.stream(initial_state, config=config, stream_mode="updates"):
    print(f"📡 {list(chunk.keys())[0]} 完成")

# ── 检查流程状态 ──
state = app.get_state(config)
print(f"\n当前流程状态：")
print(f"  下一个节点：{state.next}")
print(f"  AI 决策：{state.values.get('ai_decision')}")

# ── 第二阶段：模拟人工审核 ──
if state.values.get("ai_decision") == "need_human":
    print("\n【阶段2】模拟人工审核...")

    # 从等待的节点名称判断当前在第几级审核
    next_nodes = state.next
    print(f"  等待审核的节点：{next_nodes}")

    # 模拟一级审核决策：升级到二级
    print("  👤 一级审核员决定：升级到二级审核")
    app.update_state(
        config,
        {"level1_decision": "escalate"}
    )

    # 继续执行
    print("\n  继续执行到二级审核...")
    for chunk in app.stream(None, config=config, stream_mode="updates"):
        print(f"📡 {list(chunk.keys())[0]} 完成")

    # 查看最新状态
    state = app.get_state(config)
    print(f"\n  当前节点：{state.next}")
    print(f"  等待审核的节点：{state.next}")

    # 模拟二级审核决策
    print("  👤 二级审核员决定：标记内容")
    app.update_state(
        config,
        {"level2_decision": "flag"}
    )

    # 继续执行到结束
    print("\n  最终执行...")
    final_result = app.invoke(None, config=config)
    print(f"\n🎯 最终结果：{final_result['final_result']}")

# ── 第三阶段：时间旅行——查看历史 ──
print("\n【阶段3】时间旅行——查看执行历史...")
history = list(app.get_state_history(config))
print(f"总共 {len(history)} 个 checkpoint（展示最近5个）：\n")
for i, cp in enumerate(history[:5]):
    vals = cp.values
    print(f"[{i}] checkpoint: {cp.config['configurable']['checkpoint_id'][:8]}...")
    print(f"    content: {vals.get('content', 'N/A')[:30]}...")
    print(f"    ai_decision: {vals.get('ai_decision')}")
    print(f"    level1_decision: {vals.get('level1_decision')}")
    print(f"    level2_decision: {vals.get('level2_decision')}")
    print(f"    final_result: {vals.get('final_result')}")
    print()
```

### 6.4 执行效果演示

```
══════════════════════════════════════════════
  交互式内容审核工作流演示
══════════════════════════════════════════════

【阶段1】AI 分析和路由...
使用 streaming mode: updates

🔬 正在分析内容毒性...
   毒性得分：0.0
📡 analyze_toxicity 完成
📧 正在分析垃圾信息可能性...
   垃圾得分：0.5
📡 analyze_spam 完成
⭐ 正在分析内容质量...
   质量得分：0.8
📡 analyze_quality 完成

📊 AI 综合分析：毒性=0.0, 垃圾=0.5, 质量=0.8
   👤 AI 决策：需要人工审核（指标处于灰色地带）
📡 ai_recommendation 完成

当前流程状态：
  下一个节点：('level1_review',)
  AI 决策：need_human

【阶段2】模拟人工审核...
  等待审核的节点：('level1_review',)
  👤 一级审核员决定：升级到二级审核

  继续执行到二级审核...

📋 === 一级人工审核 ===
   毒性得分：0.0
   垃圾得分：0.5
   质量得分：0.8
   内容摘要：陈泽鹏...

📡 level1_review 完成
🔍 === 二级人工审核 ===
   一级审核决定：升级处理
   内容摘要：陈泽鹏...
📡 level2_review 完成

  当前节点：('level2_review',)

  👤 二级审核员决定：标记内容
🏴 内容被标记，需要进一步跟踪

🎯 最终结果：flagged

【阶段3】时间旅行——查看执行历史...
总共 9 个 checkpoint（展示最近5个）：...
```

### 6.5 实战中的知识点映射

| 实战功能 | 对应知识点 | 代码位置 |
|----------|-----------|----------|
| AI 自动决策路由 | 动态流程控制（条件路由 + LLM 路由） | `ai_recommendation` + `route_ai_decision` |
| 多级审核路由 | 多级路由（漏斗式） | `route_level1` → `level2_review` → `route_level2` |
| Streaming 进度展示 | Streaming（updates 模式） | `app.stream(stream_mode="updates")` |
| 人工审核暂停 | Human-in-the-Loop（interrupt） | `level1_review` / `level2_review` 中的 `interrupt()` |
| 人工审核恢复 | Human-in-the-Loop（update_state） | `app.update_state(config, values)` |
| 历史回溯 | 时间旅行（get_state_history） | `app.get_state_history(config)` |
| 可撤销决策 | 时间旅行（checkpoint 回溯） | 指定 `checkpoint_id` 重新 invoke |

---

## 七、Streaming + Checkpoint 进阶组合

### 7.1 带进度条的 Streaming

```python
# ── 场景：处理 100 条数据，实时显示进度 ──
from typing import TypedDict
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

class ProgressState(TypedDict):
    items: list[str]        # 待处理的数据列表
    processed: int          # 已处理数量
    total: int              # 总数量
    progress_pct: float     # 进度百分比

def process_batch(state: ProgressState) -> ProgressState:
    """模拟处理一批数据"""
    processed = min(state["processed"] + 20, state["total"])
    pct = round(processed / state["total"] * 100, 1)
    print(f"   ⏳ 进度：{processed}/{state['total']} ({pct}%)")
    return {"processed": processed, "progress_pct": pct}

def final_report(state: ProgressState) -> ProgressState:
    print(f"✅ 全部处理完成！共处理 {state['processed']} 条")
    return state

# ── 构建图 ──
checkpointer = MemorySaver()
graph = StateGraph(ProgressState)

graph.add_node("process", process_batch)
graph.add_node("report", final_report)

graph.add_edge(START, "process")
graph.add_edge("process", "report")
graph.add_edge("report", END)

app = graph.compile(checkpointer=checkpointer)

# ── 使用 values 模式展示进度条 ──
config = {"configurable": {"thread_id": "progress-demo"}}
initial = {"items": ["data"] * 100, "processed": 0, "total": 100, "progress_pct": 0.0}

print("📊 实时进度展示（stream_mode='values'）：\n")
for chunk in app.stream(initial, config=config, stream_mode="values"):
    pct = chunk.get("progress_pct", 0)
    bar_len = 30
    filled = int(bar_len * pct / 100)
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"   [{bar}] {pct}%")
```

### 7.2 Streaming + Checkpoint 的组合使用

```python
# ── 使用 updates 模式 + SqliteSaver ──
# ⚠️ 关键：使用 Checkpoint 时必须带上 config

from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string("streaming_demo.db")

# ... 图定义 ...

app = graph.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "stream-checkpoint-demo"}}

# ⚠️ stream 时必须传入 config
for chunk in app.stream(
    initial_state,
    config=config,          # ← 必须！否则报错
    stream_mode="updates"
):
    node_name = list(chunk.keys())[0]
    print(f"📡 节点 [{node_name}] 更新了状态")

# ⚠️ 注意：如果不传 config，会抛出错误
# 因为 LangGraph 需要一个 thread_id 来定位 Checkpoint
```

---

## 八、interrupt 完整参数详解

```python
from langgraph.types import interrupt

# ── interrupt 的完整签名 ──
interrupt(
    value: Any,       # 暂停时返回给调用方的提示信息
    id: str = None,   # 可选：给这个中断点一个唯一 ID
    label: str = None,     # 可选：给这个中断点一个显示标签
    description: str = None  # 可选：给这个中断点一个描述
)

# ── 带完整参数的示例 ──
def review_node(state: ReviewState) -> ReviewState:
    decision = interrupt(
        value={
            "message": "请审核此内容",
            "options": ["approve", "reject"],
            "content": state["content"],
        },
        id="content_review_check",          # 唯一 ID
        label="内容审核确认点",               # 显示标签
        description="在此节点暂停，等待人工审核员确认或驳回内容"  # 描述
    )
    return {"approved": decision["decision"] == "approve"}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|:---:|------|
| `value` | `Any` | ✅ | 暂停时返回给调用方的信息，可以是字符串、字典等任意类型 |
| `id` | `str` | 可选 | 中断点的唯一标识符，用于在多个 interrupt 中区分 |
| `label` | `str` | 可选 | 中断点的显示标签，便于调试和 UI 展示 |
| `description` | `str` | 可选 | 中断点的详细描述，说明为什么要在此处暂停 |

---

## 九、三种 Streaming 模式深度对比

### 9.1 全维度对比

| 对比维度 | values | updates | messages |
|----------|:------:|:-------:|:--------:|
| **返回内容** | 全量 State 快照 | 仅变化部分 | Token 级文本 |
| **数据大小** | 大（所有字段） | 中（变化字段） | 小（逐 Token） |
| **带宽消耗** | 🔴 高 | 🟡 中 | 🟢 低 |
| **能看到"谁在执行"** | ❌ 只有结果 | ✅ 节点名+输出 | ❌ 只有文本 |
| **打字机效果** | ❌ | ❌ | ✅ |
| **适合前端全量刷新** | ✅ | ❌ | ❌ |
| **适合前端增量追加** | ❌ | ✅ | ✅ |
| **适合进度条展示** | ✅ | ⚠️ 需要自己累加 | ❌ |
| **适合多 Agent 追踪** | ❌ | ✅ 最佳 | ❌ |
| **调试友好度** | ✅ 完整快照 | ⚠️ 需要拼接 | ❌ |

### 9.2 场景选择决策树

```
你需要什么效果？
    │
    ├── 前端要展示完整上下文，每次刷新整个页面
    │   └── → values
    │
    ├── 多 Agent 协作，想知道每个 Agent 做了什么
    │   └── → updates
    │
    ├── 聊天界面，需要打字机效果
    │   └── → messages
    │
    ├── 打字机效果 + 也想追踪哪个 Agent 在工作
    │   └── → ["updates", "messages"] 组合模式
    │
    └── 进度条展示（基于 State 中的计数字段）
        └── → values
```

---

## 十、路由模式决策指南

### 10.1 选择合适路由模式的决策树

```
你的路由场景是什么？
    │
    ├── 条件明确，可以写 if-else 规则
    │   └── → 基于条件的路由（模式一）
    │       优点：快速、确定、零成本
    │       例子：得分>0.8 → 通过，得分<0.3 → 拒绝
    │
    ├── 输入模糊多变，需要 AI 理解判断
    │   └── → 基于大模型的路由（模式二）
    │       优点：灵活、能处理复杂语义
    │       代价：API 调用延迟 + 成本
    │       例子：用户问"咋整啊这是？" → 需要澄清意图
    │
    ├── 先大类后小类，逐步细化
    │   └── → 多级路由（模式三）
    │       优点：逻辑清晰，每级职责单一
    │       例子：客服系统 → 先分业务线，再分优先级
    │
    └── Agent 需要自主推理 + 工具调用 + 循环迭代
        └── → Agent 行动循环 / ReAct（模式四）
            优点：能处理未知的复杂任务
            注意：一定要设 max_iterations 上限！
            例子：数据分析助手 → 思考→查询→分析→再思考...
```

### 10.2 路由模式的组合使用

> 四种路由模式不是互斥的——在一个复杂的 LangGraph 图中，可以组合使用：

```
                    ┌─────────────┐
                    │  用户输入    │
                    └──────┬──────┘
                           ↓
                    模式二：LLM路由
                    （判断大类）
                           ↓
                ┌──────────┼──────────┐
                ↓          ↓          ↓
            客服处理    技术支持     其他
                ↓          ↓
                     模式三：多级路由
                     （紧急？常规？）
                         ↓
                    ┌────┴────┐
                    ↓         ↓
                  紧急       常规
                    ↓         ↓
                模式一：   模式一：
                条件路由   条件路由
                    ↓         ↓
                 专人处理   工单队列
                    ↓         ↓
                 模式四：    END
                 ReAct循环
                 （排查问题）
```

---

## 十一、常见问题与排错指南

### 11.1 错误速查表

| 错误信息 | 原因 | 解决方法 | 优先级 |
|----------|------|----------|:------:|
| `ValueError: Unknown edge label 'xxx'` | 路由函数返回的分支名不在 `add_conditional_edges` 的映射表中 | 检查路由函数的返回值是否在映射字典中；添加兜底逻辑 | 🔴 高 |
| `RecursionError: maximum recursion depth exceeded` | Agent 循环没有正确配置上限，造成无限递归 | 设置 `max_iterations` 并检查 `should_continue` 逻辑 | 🔴 高 |
| `stream() missing required argument: config` | 使用了 Checkpoint，但 `stream()` 没有传入 config | 在 `stream()` 中添加 `config` 参数 | 🔴 高 |
| `interrupt 后无法恢复执行` | 没有调用 `update_state`，或 `thread_id` 不匹配 | 确认 `thread_id` 一致，确认调用了 `update_state` | 🟡 中 |
| LLM 路由返回的意图不在预期列表中 | LLM 输出格式不稳定 | 在路由函数中加入防御代码 + 降低 LLM temperature | 🟡 中 |
| `get_state_history` 返回空列表 | 没有使用 Checkpointer 或没有执行过 | 确认 `compile(checkpointer=...)` 且已至少执行一次 | 🟡 中 |
| Streaming `values` 模式数据量太大 | State 字段过多，全量传输浪费 | 改用 `updates` 模式；或精简 State 字段 | 🟢 低 |
| 时间旅行回溯后状态不正确 | `checkpoint_id` 指定错误或使用了不同的 `thread_id` | 确认 `thread_id` 和 `checkpoint_id` 对应正确 | 🟡 中 |

### 11.2 排查流程

```
遇到问题时的排查顺序：

Step 1: 确认图定义是否正确
    └── 用 graph.get_graph().draw_mermaid_png() 画出流程图
        检查节点和边的连接是否符合预期

Step 2: 确认路由函数的返回值
    └── 在路由函数中加 print(state) 看 state 的值
        加 print(f"路由到: {return_value}") 看返回了什么

Step 3: 检查 checkpoint 配置
    └── 确认 compile 时传入了 checkpointer
        确认 config 中包含了 thread_id

Step 4: 检查 streaming 模式
    └── 先用 "values" 调试（看完整状态）
        上线后再切换为 "updates" 或 "messages"

Step 5: 检查 interrupt 流程
    └── get_state(config) 查看当前暂停在哪个节点
        确认 update_state 和 invoke 的顺序正确
```

### 11.3 常见陷阱

**陷阱一：忘记设置 max_iterations**

```python
# ❌ 错误：没有上限，死循环风险
class State(TypedDict):
    messages: Annotated[list, add_messages]
    iterations: int  # 只记录，不限制

# ✅ 正确：硬性限制循环次数
class State(TypedDict):
    messages: Annotated[list, add_messages]
    iterations: int
    max_iterations: int  # 上限！

def should_continue(state):
    if state["iterations"] >= state["max_iterations"]:
        return "end"  # 强制结束
    ...
```

**陷阱二：interrupt 后忘记 update_state**

```python
# ❌ 错误：interrupt 暂停后直接再次 invoke
app.invoke(input, config)        # 停在 interrupt
app.invoke(None, config)         # 还是停在 interrupt！（状态没变）

# ✅ 正确：先 update_state 注入数据，再 invoke
app.invoke(input, config)        # 停在 interrupt
app.update_state(config, values) # 注入人类决策
app.invoke(None, config)         # 继续执行 ✅
```

**陷阱三：stream() 不带 config 使用 Checkpoint**

```python
# ❌ 错误
app = graph.compile(checkpointer=MemorySaver())
for chunk in app.stream(input, stream_mode="values"):
    # 报错！没有 config

# ✅ 正确
app = graph.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "demo-1"}}
for chunk in app.stream(input, config=config, stream_mode="values"):
    # 正常运行
```

---

## 十二、课后练习

### 练习一：基础路由（⭐）

**目标**：实现一个简单的基于条件的路由

**场景**：一个年龄分类系统，输入人的年龄，输出所属阶段。

**要求**：
- State 包含 `age: int` 和 `stage: str`
- 路由规则：`age < 18 → "minor"`, `18 <= age < 60 → "adult"`, `age >= 60 → "senior"`
- 每个分支输出对应的阶段描述

**验收标准**：
- 输入 `age=15`，输出 `minor`
- 输入 `age=30`，输出 `adult`
- 输入 `age=65`，输出 `senior`

### 练习二：LLM 路由（⭐⭐）

**目标**：实现一个 LLM 驱动的客服分流系统

**场景**：用户输入一句话，LLM 判断应该分到哪个部门。

**要求**：
- 四个部门：`tech_support`（技术支持）、`billing`（账单/费用）、`complaint`（投诉）、`general`（一般咨询）
- 使用 LLM 判断意图
- 添加防御代码，处理 LLM 返回异常值的情况

**验收标准**：
- "我的电脑蓝屏了" → `tech_support`
- "为什么多扣了我 50 块钱？" → `billing`
- "我要投诉你们的客服态度" → `complaint`
- "今天天气真好" → `general`

### 练习三：Human-in-the-Loop（⭐⭐⭐）

**目标**：实现一个带人工审批的消息发送系统

**场景**：AI 生成消息内容 → 暂停等待人工确认 → 确认后发送。

**要求**：
- 使用 `interrupt` 在发送前暂停
- 人工可以选择 `approve`（发送）或 `reject`（不发送）或 `edit`（编辑后发送）
- 使用 `update_state` 注入人工决策后继续执行

**验收标准**：
- approve → 输出"消息已发送"
- reject → 输出"消息已取消"
- edit → 输出"消息已编辑并发送：{新内容}"

### 练习四：时间旅行（⭐⭐⭐）

**目标**：实现一个可回溯的计算流程

**场景**：一个三步计算流程（step1: +1, step2: ×2, step3: -1），要求能从任意 checkpoint 回溯。

**要求**：
- 使用 `MemorySaver` 保存状态
- 使用 `get_state_history` 查看所有 checkpoint
- 回溯到 step1 完成后，修改初始值重新执行

**验收标准**：
- 执行完三次后 `get_state_history` 能看到完整历史
- 回溯到第一个 checkpoint 并修改值后，后续步骤使用新值

### 练习五：综合实战（⭐⭐⭐⭐）

**目标**：构建一个简化版交互式合同审核系统

**场景**：
1. AI 分析合同文本（风险评分、合规评分）
2. AI 路由：高分自动通过，低分自动拒绝，中等需要人工
3. 人工审核（interrupt）：通过 / 拒绝 / 要求修改
4. Streaming 展示分析进度
5. 支持时间旅行回溯

**框架代码**：

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt
from langchain_openai import ChatOpenAI

class ContractState(TypedDict):
    contract_text: str
    risk_score: float
    compliance_score: float
    ai_decision: str
    human_decision: str
    final_result: str

# TODO: 实现以下节点
def analyze_risk(state): ...
def analyze_compliance(state): ...
def ai_route(state): ...
def human_review(state): ...  # 含 interrupt
def approve(state): ...
def reject(state): ...
def revise(state): ...

# TODO: 构建图并测试
```

**验收标准**：
- 能正确处理三种 AI 判决结果
- 人工审核能正常暂停和恢复
- Streaming 能展示每一步的进度
- 能查看完整执行历史

---

## 十三、课程小结

### 13.1 核心知识图谱

```
┌──────────────────────────────────────────────────────────────┐
│          LangGraph 03——人机协作与时间旅行 核心知识体系          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1️⃣  动态流程控制——路由的四种模式                               │
│      ├── 基于条件的路由：代码规则驱动，明确、高效、零成本          │
│      ├── 基于大模型的路由：LLM 判断意图，灵活、智能               │
│      ├── 多级路由：先粗筛后细分，漏斗式决策                       │
│      └── Agent 行动循环（ReAct）：思考→行动→观察→再思考           │
│          ⚠️ 必须设置 max_iterations 防止死循环                  │
│                                                              │
│  2️⃣  Streaming——流式输出的三种模式                              │
│      ├── values：全量 State 快照 → 调试、进度条                  │
│      ├── updates：仅变化部分 → 多 Agent 追踪、增量更新            │
│      └── messages：Token 级打字机效果 → 聊天 UI                  │
│      可组合使用：stream_mode=["updates", "messages"]            │
│                                                              │
│  3️⃣  Human-in-the-Loop——人机协作                                │
│      ├── interrupt(value)：在节点中暂停流程                       │
│      ├── app.update_state(config, values)：注入人类决策          │
│      ├── app.get_state(config)：查看当前暂停状态                  │
│      └── 生产模式：记录 thread_id → 审核 → update_state → 继续   │
│                                                              │
│  4️⃣  时间旅行——回溯历史与探索分支                                 │
│      ├── get_state_history(config)：查看完整执行历史（倒序）       │
│      ├── 回溯：指定 checkpoint_id + invoke → 回到过去重新出发    │
│      └── 新分支：update_state 修改历史状态 → 探索不同可能          │
│                                                              │
│  5️⃣  综合实战                                                    │
│      ├── 交互式内容审核工作流                                      │
│      ├── 整合四大知识点                                           │
│      ├── AI 分析 → 路由 → 一级审核 → 二级审核                    │
│      └── Streaming 进度 + interrupt 暂停 + 时间旅行              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 13.2 一句话总结

> **LangGraph 03 教你驾驭 Agent 的"方向盘"和"时光机"**——通过四种路由模式灵活控制流程走向，通过 Streaming 实时观察执行过程，通过 interrupt/update_state 实现人机协作，通过时间旅行回溯任意历史状态并探索新的分支，最终构建出一个 AI 自动分析 + 多级人工审核 + 可审计追溯的生产级内容审核系统。

### 13.3 关键 API 速查

| API | 用途 | 所属知识点 |
|-----|------|-----------|
| `add_conditional_edges(src, fn, map)` | 定义条件路由 | 动态流程控制 |
| `graph.add_edge("act", "think")` | 创建循环边（ReAct 的关键） | Agent 行动循环 |
| `app.stream(input, stream_mode="values")` | 全量状态流式输出 | Streaming |
| `app.stream(input, stream_mode="updates")` | 增量状态流式输出 | Streaming |
| `app.stream(input, stream_mode="messages")` | Token 级流式输出 | Streaming |
| `interrupt(value)` | 暂停流程等待人类介入 | Human-in-the-Loop |
| `app.update_state(config, values)` | 注入数据恢复执行 | Human-in-the-Loop |
| `app.get_state(config)` | 查看当前状态/暂停在哪个节点 | Human-in-the-Loop |
| `app.get_state_history(config)` | 查看完整执行历史（倒序） | 时间旅行 |
| `config["configurable"]["checkpoint_id"]` | 指定历史 checkpoint 回溯 | 时间旅行 |

### 13.4 与前两课的对比

| 维度 | 01 入门和组件 | 02 可记忆可恢复 | 03 人机协作与时间旅行（本课） |
|------|:-----------:|:-------------:|:------------------------:|
| **核心关注** | 图怎么搭？ | 状态怎么存？ | 流程怎么控？ |
| **关键 API** | `StateGraph`, `add_node`, `add_edge` | `MemorySaver`, `SqliteSaver`, Thread | `interrupt`, `update_state`, `get_state_history` |
| **解决的问题** | 能跑起来 | 断电能恢复 | 人能参与决策 |
| **复杂度** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

### 13.5 系列课程定位

```
LangChain 系列（18课）→ 模型调用、提示词、链式调用、Agent 基础
                          ↓
LangGraph 系列（6课）  → Agent 编排、状态持久化、多智能体、生产部署
    ├── 00 开篇                 ✅
    ├── 01 核心概念与入门         ✅
    ├── 02 状态持久化与记忆       ✅
    ├── 03 人机协作与时间旅行     ✅ 🆕  ← 你在这里
    ├── 04 外部工具集成与 API 调用   ⬜ 待续
    ├── 05 多智能体构建             ⬜ 待续
    └── 06 生产部署上线             ⬜ 待续

本节课是 LangGraph 系列的"交互操作性"课程——弥补了前两课
在"人机交互"和"流程回溯"方面的空白。从下一课开始，
我们将进入"工具集成"和"多智能体"的进阶领域。
```

---

*本教学文档基于陈泽鹏老师视频课程整理编写。*
*本文档涵盖 LangGraph v1.0.5 中的动态路由控制、Streaming 流式输出、Human-in-the-Loop 人机协作、时间旅行四大核心特性，并以交互式内容审核工作流为综合实战案例。*
