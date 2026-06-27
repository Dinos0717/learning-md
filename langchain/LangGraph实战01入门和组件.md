# LangGraph 实战——01 入门和组件

> 基于教学视频课程整理编写 · 2026年6月

---

## 目录

- [一、课程背景与目标](#一课程背景与目标)
- [二、LangGraph 的设计哲学——低层级控制](#二langgraph-的设计哲学低层级控制)
- [三、Workflow vs Agent——两种编排模式](#三workflow-vs-agent两种编排模式)
- [四、核心组件详解——State / Node / Edge](#四核心组件详解state--node--edge)
- [五、Hello World——第一个 LangGraph 应用](#五hello-world第一个-langgraph-应用)
- [六、条件分支——图的分流控制](#六条件分支图的分流控制)
- [七、实战——智能内容审核系统](#七实战智能内容审核系统)
- [八、完整代码汇总](#八完整代码汇总)
- [九、常见问题与排错指南](#九常见问题与排错指南)
- [十、课后练习](#十课后练习)
- [十一、课程小结](#十一课程小结)

---

## 一、课程背景与目标

### 1.1 前情回顾

在开篇中我们了解了 LangGraph 是一个面向持久化智能体的低层级编排框架。本节课开始真正动手，学习 LangGraph 的核心概念并搭建第一个应用。

### 1.2 本节课的核心问题

> **LangGraph 里的 State、Node、Edge 分别是什么？怎么用它们搭建一个有分支决策能力的 Agent？**

```
本课三个关键输出：
├── 理解 Workflow 和 Agent 两种编排模式的区别
├── 掌握 State / Node / Edge 三个核心组件
└── 实战：构建一个智能内容审核系统（Agent 模式）
```

### 1.3 本课要掌握的目标

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  目标一：理解 LangGraph 的设计哲学和核心组件        │
│         ├── State：状态的记录、传递和更新          │
│         ├── Node：单一职责的函数节点               │
│         ├── Edge：普通边 + 条件边                 │
│         └── Reducer：状态的安全原子化更新           │
│                                                 │
│  目标二：掌握 Workflow 和 Agent 两种模式的实现      │
│         ├── Workflow：代码逻辑驱动的流程控制        │
│         ├── Agent：LLM 推理驱动的流程控制           │
│         └── 实战：智能内容审核系统                  │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 二、LangGraph 的设计哲学——低层级控制

### 2.1 高层级 vs 低层级

```
高层级抽象（LangChain）：
┌─────────────────────────────────────────┐
│  封装好的功能，几行代码实现一个 Agent      │
│  agent = create_react_agent(llm, tools) │
│  ↑ 方便，但底层细节不可控                │
└─────────────────────────────────────────┘

低层级控制（LangGraph）：
┌─────────────────────────────────────────┐
│  每个节点、每条边、每个条件都自己定义      │
│  graph.add_node("analyze", analyze_fn)  │
│  graph.add_edge("start", "analyze")     │
│  ↑ 完全的控制权，更大的自由度            │
└─────────────────────────────────────────┘
```

### 2.2 LangGraph 的四大设计优势

| 优势 | 说明 | 对比 LangChain |
|------|------|:------------:|
| **完全控制** | 直接编写 Prompt，不被抽象层遮蔽 | LangChain 对 Prompt 做了多层封装 |
| **显式状态** | State 控制整个 Agent 的流程运转 | LangChain 中状态是隐式的 |
| **图状结构** | Agent 最终呈现为可视化的流程图 | LangChain Agent 的内部流程不可见 |
| **生产级可靠** | 专为复杂生产场景设计 | LangChain 更偏向快速原型 |

### 2.3 适用的典型场景

| 场景 | 说明 | 为什么需要 LangGraph |
|------|------|---------------------|
| **多步复杂推理** | 需要多个推理步骤，步骤间有依赖关系 | 图结构天然支持多步流程 |
| **长时间运行任务** | 数小时甚至数天的自动化任务 | Durable Execution 保证不中断 |
| **Human-in-the-Loop** | 关键节点需要人工确认审核 | 中断机制支持人工介入 |
| **生产级稳定性** | 需要故障恢复和状态持久化 | 状态持久化 + 断点恢复 |

---

## 三、Workflow vs Agent——两种编排模式

### 3.1 本质区别

两种模式都是用 LangGraph 的图结构来编排，区别在于**谁来决定流程走向**：

```
Workflow 模式：                       Agent 模式：
┌──────────────────────┐        ┌──────────────────────┐
│   代码逻辑决定走向      │        │   LLM 推理决定走向     │
│                      │        │                      │
│  if temp < 15:       │        │  LLM分析内容          │
│      → cold节点       │        │  → 风险高？           │
│  elif temp < 25:     │        │  → 需要人工审核？      │
│      → warm节点       │        │  → 直接通过？         │
│  else:               │        │                      │
│      → hot节点        │        │  由模型推理结果决定     │
└──────────────────────┘        └──────────────────────┘
    确定性，可预测                     不确定性，有随机性
```

| 对比维度 | Workflow | Agent |
|----------|:--------:|:-----:|
| **决策者** | 代码逻辑 | LLM 推理 |
| **确定性** | ✅ 确定，可预测 | ⚠️ 有随机性 |
| **灵活性** | ⭐⭐ 受限于预设规则 | ⭐⭐⭐⭐⭐ 模型自主判断 |
| **适用场景** | 规则明确的流程 | 需要语义理解的任务 |
| **实现复杂度** | ⭐ 简单 | ⭐⭐⭐ 需要设计 Prompt |

### 3.2 混合模式——最佳实践

> 实际项目中推荐**两种模式结合使用**：某些节点用代码判断，某些节点用 LLM 推理。

```
混合模式示例：
用户输入 → LLM 分析意图（Agent）
              ↓
         ┌────┴────┐
         ↓         ↓
      查天气    查订单（Workflow：根据意图路由）
         ↓         ↓
         └────┬────┘
              ↓
         LLM 综合回答（Agent）
              ↓
         返回用户
```

---

## 四、核心组件详解——State / Node / Edge

### 4.1 State——状态的记录与传递

> **State** 是 LangGraph 中**最核心**的概念。它记录了 Agent 运行过程中的所有变量，这些变量会在节点之间**传递和更新**。

```python
from typing import TypedDict

class HelloState(TypedDict):
    """LangGraph 的状态定义——本质是一个 JSON 对象"""
    name: str           # 用户名
    greeting: str       # 问候语
```

| 特性 | 说明 |
|------|------|
| 本质 | 一个 JSON 对象，用 TypedDict 定义 |
| 作用 | 记录所有变量，在节点间传递和更新 |
| 生命周期 | 一次 Graph 调用（invoke）的完整生命周期 |
| 持久化 | 可配置持久化，实现故障恢复（后续课程） |

**State 的传递过程**：

```
invoke({"name": "张三"})
    ↓
State = {"name": "张三", "greeting": ""}
    ↓ 传入节点1
节点1: greeting = "你好，张三"
    ↓ State 更新为 {"name": "张三", "greeting": "你好，张三"}
    ↓ 传入节点2
节点2: greeting = "你好，张三 👋"
    ↓ State 更新为 {"name": "张三", "greeting": "你好，张三 👋"}
    ↓
输出 State
```

### 4.2 Node——单一职责的执行单元

> **Node** 是图中的节点，每个节点负责**单一的职责**。最佳实践是**函数优先**——每个节点就是一个 Python 函数。

```python
# ✅ 好的节点设计：单一职责
def greet_node(state: HelloState) -> dict:
    """只负责生成问候语"""
    return {"greeting": f"你好，{state['name']}"}

def add_emoji_node(state: HelloState) -> dict:
    """只负责添加表情"""
    return {"greeting": state["greeting"] + " 👋"}
```

| 最佳实践 | 说明 |
|----------|------|
| **单一职责** | 每个节点只做一件事 |
| **函数优先** | 用纯函数实现，方便测试 |
| **返回字典** | 返回要更新的 State 字段 |
| **常见用途** | LLM 调用、工具调用、数据转换 |

### 4.3 Edge——节点之间的连接

> **Edge** 定义了节点之间的流转方向。有两种类型：

#### 普通边（Normal Edge）

```
节点A ────→ 节点B
     固定方向，无条件
```

```python
graph.add_edge("greet", "add_emoji")  # greet → add_emoji
```

#### 条件边（Conditional Edge）

```
           ┌→ 节点B（条件1）
节点A ──→ 路由函数 ──→ 节点C（条件2）
           └→ 节点D（条件3）
```

```python
graph.add_conditional_edges(
    "check",              # 从哪个节点出发
    route_function,       # 路由函数：决定去哪个节点
    {                     # 路由映射
        "cold": "cold_node",
        "warm": "warm_node", 
        "hot": "hot_node"
    }
)
```

### 4.4 Reducer——状态的安全更新

> **Reducer** 定义了状态如何被**原子化地安全更新**。在并发或多节点同时修改同一字段时，Reducer 确保数据一致性。

```python
# 使用内置 Reducer：追加消息到列表
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # 使用 add_messages reducer
```

---

## 五、Hello World——第一个 LangGraph 应用

### 5.1 安装依赖

```bash
pip install langchain              # 已包含 langgraph
pip install langchain-openai       # OpenAI 兼容的模型调用
pip install graphviz               # 流程图可视化
```

### 5.2 完整代码

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# ============================================================
# Step 1: 定义 State
# ============================================================
class HelloState(TypedDict):
    """记录 LangGraph 中所有状态的 JSON 对象"""
    name: str           # 用户名
    greeting: str       # 问候语（在节点间传递和更新）

# ============================================================
# Step 2: 定义 Node（函数优先，单一职责）
# ============================================================
def greet_node(state: HelloState) -> dict:
    """节点1：生成问候语"""
    name = state.get("name", "朋友")
    return {"greeting": f"你好，{name}"}

def add_emoji_node(state: HelloState) -> dict:
    """节点2：在问候语后添加表情"""
    return {"greeting": state["greeting"] + " 👋"}

# ============================================================
# Step 3: 构建图
# ============================================================
# 创建 StateGraph 对象
graph = StateGraph(HelloState)

# 添加节点
graph.add_node("greet", greet_node)
graph.add_node("add_emoji", add_emoji_node)

# 添加边（控制流程走向）
graph.add_edge(START, "greet")        # 开始 → 问候节点
graph.add_edge("greet", "add_emoji")  # 问候节点 → 表情节点
graph.add_edge("add_emoji", END)      # 表情节点 → 结束

# 编译图
app = graph.compile()

# ============================================================
# Step 4: 运行
# ============================================================
result = app.invoke({"name": "张三"})
print(result["greeting"])  # → "你好，张三 👋"
```

### 5.3 图结构可视化

```
   START
     ↓
 [greet]  ← 节点1：生成"你好，张三"
     ↓
[add_emoji] ← 节点2：追加"👋"
     ↓
   END
```

### 5.4 State 的流转过程

```
invoke({"name": "张三"})
        ↓
┌──────────────────────────────────────────────┐
│ State 初始值：{"name": "张三", "greeting": ""} │
└──────────────────────────────────────────────┘
        ↓ 进入 greet_node
┌──────────────────────────────────────────────────┐
│ State 更新：{"name": "张三", "greeting": "你好，张三"}│
└──────────────────────────────────────────────────┘
        ↓ 进入 add_emoji_node
┌──────────────────────────────────────────────────────────┐
│ State 更新：{"name": "张三", "greeting": "你好，张三 👋"}   │
└──────────────────────────────────────────────────────────┘
        ↓
最终输出："你好，张三 👋"
```

---

## 六、条件分支——图的分流控制

### 6.1 场景

根据温度给出穿衣建议：<15°穿棉袄，<25°穿夹克，≥25°穿短袖。

### 6.2 完整代码

```python
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

# ============================================================
# Step 1: 定义 State
# ============================================================
class WeatherState(TypedDict):
    temperature: int             # 温度
    recommendation: str          # 穿衣建议

# ============================================================
# Step 2: 定义节点
# ============================================================
def check_temperature(state: WeatherState) -> dict:
    """检查温度，设置 temperature 值"""
    return {"temperature": 25}

def recommend_cold(state: WeatherState) -> dict:
    """冷（<15°）：穿棉袄"""
    return {"recommendation": "建议穿棉袄，注意保暖"}

def recommend_warm(state: WeatherState) -> dict:
    """温暖（15-25°）：穿夹克"""
    return {"recommendation": "建议穿夹克，温度适中"}

def recommend_hot(state: WeatherState) -> dict:
    """热（≥25°）：穿短袖"""
    return {"recommendation": "穿短袖，记得防晒"}

# ============================================================
# Step 3: 定义路由函数（条件判断）
# ============================================================
def route_by_temperature(state: WeatherState) -> Literal["cold", "warm", "hot"]:
    """根据温度决定下一步走向哪个节点"""
    temp = state["temperature"]
    if temp < 15:
        return "cold"
    elif temp < 25:
        return "warm"
    else:
        return "hot"

# ============================================================
# Step 4: 构建带条件分支的图
# ============================================================
graph = StateGraph(WeatherState)

# 添加节点
graph.add_node("check", check_temperature)
graph.add_node("cold", recommend_cold)
graph.add_node("warm", recommend_warm)
graph.add_node("hot", recommend_hot)

# 添加边
graph.add_edge(START, "check")              # 开始 → 检查温度
graph.add_conditional_edges(                 # 条件分支！
    "check",                                 # 从 check 节点出发
    route_by_temperature,                    # 路由函数
    {                                        # 路由映射
        "cold": "cold",
        "warm": "warm",
        "hot": "hot"
    }
)
graph.add_edge("cold", END)
graph.add_edge("warm", END)
graph.add_edge("hot", END)

app = graph.compile()

# ============================================================
# Step 5: 运行
# ============================================================
result = app.invoke({})
print(f"温度: {result['temperature']}°C")
print(f"建议: {result['recommendation']}")
# → 温度: 25°C
# → 建议: 穿短袖，记得防晒
```

### 6.3 图结构可视化

```
              START
                ↓
             [check]  ← 设置 temperature=25
                ↓
         路由函数判断
         ┌───┼───┐
         ↓   ↓   ↓
       cold warm hot
       (<15)(15-25)(≥25)
         ↓   ↓   ↓
         └───┴───┘
              ↓
            END
```

---

## 七、实战——智能内容审核系统

### 7.1 场景设计

构建一个内容审核 Agent，自动判断用户提交的内容是否合规：

| 内容类型 | 风险等级 | 处理方式 |
|----------|:------:|:--------:|
| 正常评论 | Low | 自动通过 |
| 刷单评论 | Low | 自动通过 |
| 包含脏话 | **High** | 需人工审核 |
| 政治敏感 | **High** | 需人工审核 |

### 7.2 State 定义

```python
from typing import TypedDict

class ModerationState(TypedDict):
    """内容审核的状态"""
    input_text: str         # 用户输入的内容
    analysis: str           # LLM 的分析结果（JSON字符串）
    decision: str           # 审核决策：approve / reject / review
    reason: str             # 决策理由
    confidence: float       # 置信度 0-1
```

### 7.3 模型声明

```python
from langchain_openai import ChatOpenAI

# 使用 OpenAI 兼容接口，可以对接国内模型
llm = ChatOpenAI(
    model="qwen-3b",              # 千问 3B 模型
    api_key="你的API_Key",         # API Key
    base_url="你的API地址",         # 兼容 OpenAI 协议的地址
    temperature=0
)
```

### 7.4 节点函数

```python
import json

# ── 节点1：分析内容 ──
def analyze_content(state: ModerationState) -> dict:
    """调用 LLM 分析内容的风险等级"""
    
    system_prompt = """你是一个专业的内容审核助手。
请分析以下内容的合规性，并以 JSON 格式返回：
{
    "has_issue": true/false,        // 是否有问题
    "issue_type": ["脏话", "敏感话题", "欺诈", ...],  // 问题类型
    "risk_level": "low/medium/high",  // 风险等级
    "confidence": 0.0-1.0            // 置信度
}"""
    
    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": state["input_text"]}
    ])
    
    return {"analysis": response.content}


# ── 节点2：自动决策 ──
def decide_node(state: ModerationState) -> dict:
    """基于 LLM 分析结果，由 LLM 自动做出审核决策"""
    
    system_prompt = """基于以下审核分析结果，做出最终决策。
你有三个选项：
- approve: 内容合规，直接通过
- reject: 内容违规，直接拒绝
- review: 需要人工进一步审核

请以 JSON 格式返回：
{
    "decision": "approve/reject/review",
    "reason": "决策理由"
}"""
    
    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": state["analysis"]}
    ])
    
    result = json.loads(response.content)
    return {
        "decision": result.get("decision", "review"),
        "reason": result.get("reason", "")
    }


# ── 节点3：人工审核 ──
def human_review_node(state: ModerationState) -> dict:
    """标记需要人工审核"""
    return {
        "decision": "review",
        "reason": "风险等级为 high，需要人工审核"
    }
```

### 7.5 路由函数

```python
import json

def should_auto_review(state: ModerationState) -> str:
    """判断是否需要转入人工审核
    
    从 analysis 中提取 risk_level：
    - high → 走人工审核
    - low/medium → 走自动决策
    """
    try:
        analysis = json.loads(state["analysis"])
        risk_level = analysis.get("risk_level", "low")
        if risk_level == "high":
            return "review"       # 高风险 → 人工审核
        else:
            return "decide"       # 低/中风险 → 自动决策
    except json.JSONDecodeError:
        return "decide"           # 解析失败 → 默认自动决策
```

### 7.6 构建图

```python
from langgraph.graph import StateGraph, START, END

# ── 创建图 ──
graph = StateGraph(ModerationState)

# ── 添加节点 ──
graph.add_node("analyze", analyze_content)       # 分析内容
graph.add_node("decide", decide_node)            # 自动决策
graph.add_node("human_review", human_review_node) # 人工审核

# ── 添加边 ──
graph.add_edge(START, "analyze")                 # 开始 → 分析

# 条件分支：根据风险等级决定去向
graph.add_conditional_edges(
    "analyze",                    # 从分析节点出发
    should_auto_review,           # 条件判断函数
    {
        "review": "human_review", # high → 人工审核
        "decide": "decide"        # low/medium → 自动决策
    }
)

graph.add_edge("human_review", END)
graph.add_edge("decide", END)

app = graph.compile()
```

### 7.7 图结构可视化

```
              START
                ↓
           [analyze]  ← LLM 分析内容
                ↓
        should_auto_review
         ┌──────┴──────┐
         ↓              ↓
    risk=high       risk=low/medium
         ↓              ↓
  [human_review]    [decide]  ← LLM 做决策
         ↓              ↓
         └──────┬──────┘
                ↓
              END
```

### 7.8 运行测试

```python
# ── 测试数据 ──
test_contents = [
    "这是一条正常的评论，产品质量很好，值得购买。",                  # → approve
    "你这个傻X，东西烂得要死！！！",                              # → review
    "搞活动的时候买的，价格实惠，物流也快，下次还来。",              # → approve
    "我们应该讨论一下最近的XX政策，大家怎么看？",                   # → review
]

for content in test_contents:
    result = app.invoke({"input_text": content})
    print(f"内容: {content[:30]}...")
    print(f"决策: {result['decision']}")
    print(f"理由: {result['reason']}")
    print("-" * 50)
```

**预期输出：**

```
内容: 这是一条正常的评论，产品质量很好，值得购买。...
决策: approve
理由: 内容合规，无违规内容
--------------------------------------------------
内容: 你这个傻X，东西烂得要死！！！...
决策: review
理由: 风险等级为 high，需要人工审核
--------------------------------------------------
内容: 搞活动的时候买的，价格实惠，物流也快，下次还来。...
决策: approve
理由: 正常表达购物体验
--------------------------------------------------
内容: 我们应该讨论一下最近的XX政策，大家怎么看？...
决策: review
理由: 风险等级为 high，需要人工审核
--------------------------------------------------
```

---

## 八、完整代码汇总

```python
import json
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

# ============================================================
# 1. 初始化 LLM
# ============================================================
llm = ChatOpenAI(
    model="qwen-3b",
    api_key="你的Key",
    base_url="你的地址",
    temperature=0
)

# ============================================================
# 2. 定义 State
# ============================================================
class ModerationState(TypedDict):
    input_text: str
    analysis: str
    decision: str
    reason: str
    confidence: float

# ============================================================
# 3. 定义 Node
# ============================================================
def analyze_content(state: ModerationState) -> dict:
    system_prompt = """分析内容的合规性，返回JSON：{
        "has_issue": true/false,
        "issue_type": [...],
        "risk_level": "low/medium/high",
        "confidence": 0.0-1.0
    }"""
    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": state["input_text"]}
    ])
    return {"analysis": response.content}

def decide_node(state: ModerationState) -> dict:
    system_prompt = """基于分析结果做出决策（approve/reject/review），返回JSON：{
        "decision": "...",
        "reason": "..."
    }"""
    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": state["analysis"]}
    ])
    result = json.loads(response.content)
    return {"decision": result["decision"], "reason": result["reason"]}

def human_review_node(state: ModerationState) -> dict:
    return {"decision": "review", "reason": "需人工审核"}

# ============================================================
# 4. 路由函数
# ============================================================
def should_auto_review(state: ModerationState) -> Literal["review", "decide"]:
    try:
        analysis = json.loads(state["analysis"])
        return "review" if analysis.get("risk_level") == "high" else "decide"
    except:
        return "decide"

# ============================================================
# 5. 构建图
# ============================================================
graph = StateGraph(ModerationState)
graph.add_node("analyze", analyze_content)
graph.add_node("decide", decide_node)
graph.add_node("human_review", human_review_node)
graph.add_edge(START, "analyze")
graph.add_conditional_edges("analyze", should_auto_review, {
    "review": "human_review", "decide": "decide"
})
graph.add_edge("human_review", END)
graph.add_edge("decide", END)
app = graph.compile()

# ============================================================
# 6. 测试
# ============================================================
tests = [
    "产品很好，值得购买",
    "你这个傻X，烂东西",
]
for t in tests:
    r = app.invoke({"input_text": t})
    print(f"{t[:20]}... → {r['decision']}")
```

---

## 九、常见问题与排错指南

### 9.1 错误速查表

| 错误/问题 | 原因 | 解决方法 | 优先级 |
|-----------|------|----------|:------:|
| `AttributeError: 'dict' object has no attribute` | State 类型不匹配 | 确保 TypedDict 定义的字段在节点中都返回了 | 🔴高 |
| 条件边不生效 | 路由函数返回值与映射 key 不匹配 | 路由返回值和 `add_conditional_edges` 的字典 key 要一致 | 🔴高 |
| `json.JSONDecodeError` | LLM 返回的不是合法 JSON | ①降低 temperature ②在 Prompt 中强调格式 ③加 try-except | 🟡中 |
| 图编译报错 | 节点或边的连接有遗漏 | 检查每个节点是否有入口边和出口边 | 🟡中 |
| graphviz 渲染失败 | graphviz 未正确安装 | `pip install graphviz` + 安装系统级 graphviz | 🟢低 |
| LLM 返回结果不一致 | Agent 模式的固有特性 | 降低 temperature，优化 Prompt | 🟢低 |

### 9.2 排查流程

```
图不按预期执行？
    ↓
第一步：打印 State
    在每个节点函数开头加 print(state) → 看 State 是否正确传递
    ↓
第二步：检查路由函数
    print(state) 在路由函数中 → 看条件判断的输入是否正确
    ↓
第三步：检查 LLM 返回
    print(response.content) → 看 LLM 返回的 JSON 是否合法
    ↓
第四步：可视化图
    print(app.get_graph().draw_ascii()) → 确认图结构
```

---

## 十、课后练习

### 练习一：Hello World 改造

> 在 Hello World 示例基础上增加一个 `to_upper` 节点，将最终 greeting 转为大写。

```
改造后的图：
START → greet → add_emoji → to_upper → END
```

### 练习二：条件分支扩展

> 在温度示例中增加 `freezing` 分支（<0°），返回"建议穿羽绒服，极寒天气"。

| 温度范围 | 路由 | 建议 |
|:------:|:----:|------|
| <0 | freezing | 穿羽绒服 |
| 0-15 | cold | 穿棉袄 |
| 15-25 | warm | 穿夹克 |
| ≥25 | hot | 穿短袖 |

### 练习三：Workflow vs Agent

> 将内容审核系统改写为纯 Workflow 模式（不用 LLM）：

```python
# Workflow 模式的路由函数
def should_review_by_keywords(state):
    keywords = ["傻X", "烂", "政策", "敏感词"]  # 关键词黑名单
    for kw in keywords:
        if kw in state["input_text"]:
            return "review"
    return "decide"
```

对比两种模式的效果：

| 测试内容 | Workflow 决策 | Agent 决策 | 差异分析 |
|----------|:-----------:|:---------:|------|
| "产品很好" | | | |
| "傻X烂东西" | | | |
| "刷单评论" | | | |

### 练习四：完整 Agent 定制

> 基于课上的审核系统，增加以下功能：
> 1. 增加 `spam` 类别（垃圾广告），直接 reject
> 2. 在 `decide_node` 中增加置信度低于 0.6 时走人工审核的逻辑

---

## 十一、课程小结

### 11.1 本课核心知识图谱

```
┌────────────────────────────────────────────────────────────┐
│              LangGraph 入门核心知识体系                       │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  三大核心组件                                           │
│      ├── State：TypedDict 定义，记录和传递所有变量            │
│      ├── Node：函数优先，单一职责，返回要更新的字段           │
│      └── Edge：普通边（add_edge）+ 条件边（add_conditional）│
│                                                            │
│  2️⃣  两种编排模式                                           │
│      ├── Workflow：代码逻辑驱动，确定性，可预测               │
│      └── Agent：LLM 推理驱动，灵活性高，有随机性              │
│          实际项目推荐混合使用                                │
│                                                            │
│  3️⃣  构建 LangGraph 应用五步走                              │
│      定义 State → 定义 Node → 构建 Graph → 编译 → invoke   │
│                                                            │
│  4️⃣  条件分支                                               │
│      ├── add_conditional_edges(source, router, mapping)   │
│      ├── router 函数返回字符串 → 映射到具体节点              │
│      └── 返回 Literal 类型确保类型安全                      │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 11.2 一句话总结

> **LangGraph = StateGraph + Node + Edge。** State 记录一切，Node 执行逻辑，Edge 控制流转。通过 `add_conditional_edges` 实现条件分支，让 Agent 能根据 LLM 推理结果自主决定下一步。Workflow 和 Agent 两种模式各有所长，实际项目推荐混合使用。

### 11.3 速记卡

```
┌───────────────────────────────────────────────────────┐
│            LangGraph 速记卡                             │
├───────────────────────────────────────────────────────┤
│                                                       │
│  定义 State：class State(TypedDict): ...              │
│  添加节点：graph.add_node("name", node_fn)            │
│  添加边：  graph.add_edge(A, B)                       │
│  条件边：  graph.add_conditional_edges(               │
│               A, router_fn, {"a": nodeA, "b": nodeB}) │
│  编译：    app = graph.compile()                      │
│  运行：    result = app.invoke({"key": "value"})      │
│                                                       │
└───────────────────────────────────────────────────────┘
```

### 11.4 系列课程定位

```
LangGraph 系列（6课）：
├── 00 开篇：框架定位、五大特性、课程体系
├── 01 入门和组件（本课）🆕
├── 02 状态持久化与记忆（待续）
├── 03 流式输出、中断与时间旅行
├── 04 外部工具集成与 API 调用
├── 05 多智能体构建
└── 06 生产部署上线
```

---

*本教学文档基于 LangGraph 系列课程第一讲视频整理编写。*  
*本文档涵盖 State/Node/Edge 核心组件、Workflow vs Agent 双模式对比、Hello World 入门示例、条件分支实现及智能内容审核系统完整实战。*
