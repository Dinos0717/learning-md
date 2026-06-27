# LangGraph 实战——04 构筑多智能体协作系统

> 基于教学视频课程整理编写 · 2026年6月

---

## 目录

- [一、课程背景与目标](#一课程背景与目标)
- [二、单一 Agent 的局限与多 Agent 的价值](#二单一-agent-的局限与多-agent-的价值)
- [三、Subgraph——多 Agent 协作的基石](#三subgraph多-agent-协作的基石)
- [四、主图与子图的 State 数据传递](#四主图与子图的-state-数据传递)
- [五、多 Agent 协作的四种模式](#五多-agent-协作的四种模式)
- [六、综合实战——旅行规划助手](#六综合实战旅行规划助手)
- [七、协作模式决策指南](#七协作模式决策指南)
- [八、Subgraph 设计最佳实践](#八subgraph-设计最佳实践)
- [九、常见问题与排错指南](#九常见问题与排错指南)
- [十、课后练习](#十课后练习)
- [十一、课程小结](#十一课程小结)

---

## 一、课程背景与目标

### 1.1 前情回顾

在前三课中，我们掌握了 LangGraph 的基础能力：

| 课程 | 核心能力 | 关键 API |
|------|----------|----------|
| **01 入门和组件** | 搭建图结构 | `StateGraph`, `add_node`, `add_edge`, `add_conditional_edges` |
| **02 可记忆可恢复** | 状态持久化与断点恢复 | `MemorySaver`, `SqliteSaver`, `Thread`, `Durable Execution` |
| **03 人机协作与时间旅行** | 流程控制与回溯 | `interrupt`, `update_state`, `stream`, `get_state_history` |

**前三课的共同特点**：所有 Agent 都是**单一的**。一个图 = 一个 Agent = 一个职责。

> 从本课开始，我们进入**多 Agent** 的世界——如何让多个 Agent 像团队一样协作？

### 1.2 本节课的核心问题

> **当任务太复杂，一个 Agent 搞不定的时候，怎么把多个专业 Agent 组织成一个协作团队？**

```
本课要解决的关键问题：

问题1：单一 Agent 撑不住了
	    让一个 Agent 同时查机票、订酒店、推荐活动、管预算
	    → 提示词数千字，大模型开始"犯迷糊" 😵‍💫

问题2：没法独立调试
	    一个超大 Agent，改一行提示词可能影响全局
	    → 每次修改都要全链路测试，效率极低

问题3：模块无法复用
	    在这个项目里写好的"酒店查询"逻辑，另一个项目没法直接用
	    → 同样的代码到处复制粘贴

问题4：不知道怎么分工
	    多个 Agent 之间，应该串行还是并行？谁指挥谁？
	    → 协作模式选错，效果大打折扣
```

### 1.3 本课要掌握的目标

```
┌───────────────────────────────────────────────────────┐
│                                                       │
│  目标一：理解多 Agent 的价值与适用场景                   │
│         ├── 单一 Agent 的四大局限                       │
│         ├── 多 Agent 的三大优势（专业/独立/可复用）      │
│         └── 何时用单 Agent、何时用多 Agent              │
│                                                       │
│  目标二：掌握 Subgraph——多 Agent 的基石                 │
│         ├── Subgraph 的概念与独立性                     │
│         ├── 主图调用子图的方式                          │
│         └── 子图嵌套子图的层级结构                       │
│                                                       │
│  目标三：掌握主图与子图的数据传递                        │
│         ├── State 映射函数的编写                        │
│         ├── 主图 → 子图 的数据传入                      │
│         └── 子图 → 主图 的数据传出                      │
│                                                       │
│  目标四：掌握四种协作模式                                │
│         ├── 顺序协作（串行管道）                         │
│         ├── 并行协作（同时执行）                         │
│         ├── 主控专家（Supervisor 调度）                  │
│         └── 协商模式（投票决策）                         │
│                                                       │
└───────────────────────────────────────────────────────┘
```

---

## 二、单一 Agent 的局限与多 Agent 的价值

### 2.1 单一 Agent 的四大局限

```
单一 Agent 的问题全景图：

                         ┌─────────────────────────────┐
                         │    单一 Agent（一个图包揽一切）│
                         ├─────────────────────────────┤
                         │                             │
                         │  提示词：                     │
                         │  "你是一个助手，你需要：        │
                         │   1. 分析用户意图              │
                         │   2. 查询机票信息              │
                         │   3. 查询酒店信息              │
                         │   4. 推荐当地活动              │
                         │   5. 做预算规划               │
                         │   6. 生成完整旅行报告          │
                         │   7. 注意……                  │
                         │   8. 还有……"                 │
                         │                             │
                         │  问题：                       │
                         │  • 职责不清 → 什么都管，什么    │
                         │    都管不好                    │
                         │  • 提示词膨胀 → 越来越长，     │
                         │    模型开始"遗忘"前面的指令     │
                         │  • 难以维护 → 改一处可能       │
                         │    影响全局                    │
                         │  • 无法复用 → 这个"酒店查询"   │
                         │    逻辑只能在这个 agent 里用   │
                         │                             │
                         └─────────────────────────────┘
```

| 局限 | 表现 | 后果 |
|------|------|------|
| **职责不清** | 一个 Agent 承担所有任务，没有明确的专业边界 | 大模型容易混淆上下文，输出质量不稳定 |
| **难以维护** | 提示词数百行，步骤几十个 | 改一处可能触发连锁反应，定位问题困难 |
| **无法专业化** | Agent 什么都要会，但什么都做不到极致 | 没有深度，缺乏领域专业知识 |
| **难以复用** | 逻辑全部耦合在一个图里 | 同样的"酒店查询"无法直接给别的项目用 |

### 2.2 多 Agent 的优势

> **让每个 Agent 只做好一件事，然后像团队一样协作。**

```
单一 Agent 模式：
┌─────────────────────────────────────────────┐
│              万能 Agent                       │
│  (机票+酒店+活动+预算+规划…全在一身)            │
│  提示词：5000字 😱                            │
│  调试：牵一发动全身                           │
└─────────────────────────────────────────────┘

                    ↓ 拆分 ↓

多 Agent 模式：
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ 机票专家  │  │ 酒店专家  │  │ 活动专家  │  │ 预算专家  │
│ Agent     │  │ Agent     │  │ Agent     │  │ Agent     │
│           │  │           │  │           │  │           │
│ 只关注    │  │ 只关注    │  │ 只关注    │  │ 只关注    │
│ 航班查询  │  │ 住宿推荐  │  │ 游玩活动  │  │ 费用计算  │
│           │  │           │  │           │  │           │
│ 提示词:   │  │ 提示词:   │  │ 提示词:   │  │ 提示词:   │
│ 200字 ✅  │  │ 200字 ✅  │  │ 200字 ✅  │  │ 150字 ✅  │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
     │              │              │              │
     └──────────────┴──────────────┴──────────────┘
                    │
            ┌───────┴───────┐
            │   规划师 Agent  │ ← 汇总协调
            │   整合结果      │
            │   生成最终报告  │
            └───────────────┘
```

| 优势 | 说明 | 实际效果 |
|------|------|----------|
| **专业分工** | 每个 Agent 专注一个领域 | 提示词简单清晰，模型理解准确 |
| **独立开发测试** | 每个 Agent 可以单独跑、单独调 | 修改"酒店 Agent"时不影响"机票 Agent" |
| **可复用组合** | Agent 像乐高积木，拆下来可以装到别的项目 | "酒店查询"这个子图可以给多个主图使用 |

### 2.3 单 Agent vs 多 Agent 决策表

| 判断维度 | 适合单 Agent | 适合多 Agent |
|----------|:-----------:|:-----------:|
| **任务数量** | 1-3 个简单任务 | 4 个以上独立任务 |
| **领域跨度** | 同一领域 | 跨领域（机票/酒店/活动） |
| **提示词长度** | < 500 字 | 每个领域都有大量专业指令 |
| **团队协作** | 单人开发 | 多人并行开发不同的 Agent |
| **复用需求** | 一次性使用 | 多个项目需要用到 |
| **调试粒度** | 整体调试即可 | 需要逐模块隔离调试 |

---

## 三、Subgraph——多 Agent 协作的基石

### 3.1 Subgraph 的概念

> **Subgraph（子图）是嵌在主图中的一个完整的 LangGraph 图。它是多 Agent 协作的最小单元。**

```
Subgraph 的本质：

一个 Subgraph = 一个完整的 LangGraph 图
    ├── 有自己的 State
    ├── 有自己的 Node
    ├── 有自己的 Edge
    ├── 可以独立编译和执行
    └── 也可以作为"节点"被主图调用

在主图看来，整个 Subgraph 就是一个节点！
但在流程图渲染时，Subgraph 会被框起来显示其内部结构。
```

```
┌──────────────────────────────────────────────┐
│                   主图 (Main Graph)           │
│                                              │
│  ┌─────────┐    ┌─────────────────┐          │
│  │ 节点A   │───→│  ┌───────────┐  │          │
│  └─────────┘    │  │ Subgraph  │  │          │
│                 │  │ ┌───────┐ │  │          │
│                 │  │ │ 子节点1 │ │  │          │
│                 │  │ └───┬───┘ │  │          │
│                 │  │     ↓     │  │          │
│                 │  │ ┌───────┐ │  │          │
│                 │  │ │ 子节点2 │ │  │          │
│                 │  │ └───────┘ │  │          │
│                 │  └───────────┘  │          │
│                 └────────┬────────┘          │
│                          ↓                   │
│                    ┌─────────┐               │
│                    │ 节点B   │               │
│                    └─────────┘               │
│                                              │
└──────────────────────────────────────────────┘
```

### 3.2 为什么 Subgraph 是构建复杂系统的关键

| 价值 | 说明 |
|------|------|
| **模块化** | 将复杂逻辑封装成独立的、可管理的子图，主图保持简洁 |
| **可复用** | 同一个子图可以用在这个主图，也可以用在别的主图中 |
| **清晰性** | 业务细节藏在子图内部，主图逻辑一目了然 |
| **独立测试** | 可以先对子图单独做测试，再对整合后的主图做测试 |

### 3.3 一个最简单的 Subgraph 示例

> 子图做"数学变换"（输入×2 + 10），主图调用它。

#### 子图定义

```python
# ── 子图的 State ──
from typing import TypedDict

class SubState(TypedDict):
    input_value: int     # 子图的输入
    doubled: int         # 乘2后的值
    result: int          # 子图的最终结果

# ── 子图的节点 ──
def double_node(state: SubState) -> SubState:
    """第一步：将输入乘以2"""
    doubled = state["input_value"] * 2
    print(f"   [子图] double: {state['input_value']} × 2 = {doubled}")
    return {"doubled": doubled}

def add_ten_node(state: SubState) -> SubState:
    """第二步：再加上10"""
    result = state["doubled"] + 10
    print(f"   [子图] add_ten: {state['doubled']} + 10 = {result}")
    return {"result": result}

# ── 构建子图 ──
from langgraph.graph import StateGraph, END, START

subgraph = StateGraph(SubState)
subgraph.add_node("double", double_node)
subgraph.add_node("add_ten", add_ten_node)

subgraph.add_edge(START, "double")
subgraph.add_edge("double", "add_ten")
subgraph.add_edge("add_ten", END)

subgraph_app = subgraph.compile()  # 子图可以独立编译！
```

#### 主图定义（调用子图）

```python
# ── 主图的 State ──
class MainState(TypedDict):
    number: int       # 用户的输入数字
    result: int       # 经子图处理后的最终结果

# ── 主图的节点 ──
def prepare_node(state: MainState) -> MainState:
    """主图准备工作"""
    print(f"[主图] 准备处理数字：{state['number']}")
    return state

def call_subgraph_node(state: MainState) -> MainState:
    """
    调用子图！
    将主图的 number 传入子图的 input_value，
    将子图的 result 传回主图的 result。
    """
    print("[主图] 正在调用子图...")
    # ⚠️ 关键：subgraph_app.invoke() 调用子图
    sub_result = subgraph_app.invoke({
        "input_value": state["number"],  # 主→子：number → input_value
        "doubled": 0,
        "result": 0,
    })
    print(f"[主图] 子图返回结果：{sub_result}")
    return {"result": sub_result["result"]}  # 子→主：result → result

# ── 构建主图 ──
main_graph = StateGraph(MainState)
main_graph.add_node("prepare", prepare_node)
main_graph.add_node("call_subgraph", call_subgraph_node)

main_graph.add_edge(START, "prepare")
main_graph.add_edge("prepare", "call_subgraph")
main_graph.add_edge("call_subgraph", END)

main_app = main_graph.compile()

# ── 执行 ──
result = main_app.invoke({"number": 5, "result": 0})
print(f"\n最终结果：输入 5 → 输出 {result['result']}")

"""
输出：
[主图] 准备处理数字：5
[主图] 正在调用子图...
   [子图] double: 5 × 2 = 10
   [子图] add_ten: 10 + 10 = 20
[主图] 子图返回结果：{'input_value': 5, 'doubled': 10, 'result': 20}

最终结果：输入 5 → 输出 20
"""
```

#### 流程图渲染效果

```
主图（Main Graph）：
    START → prepare → ┌──────────────────┐ → END
                       │   Subgraph (框)   │
                       │ START → double   │
                       │   ↓               │
                       │ add_ten           │
                       │   ↓               │
                       │ END               │
                       └──────────────────┘
```

> 💡 在 Graphviz 渲染图中，Subgraph 会用一个**虚线框**框住，内部节点清晰可见。

---

## 四、主图与子图的 State 数据传递

### 4.1 核心问题

主图和子图的 State 结构**通常不一样**——怎么把数据从主图传进子图，怎么把子图的结果传回主图？

```
主图 State                   子图 State
┌────────────────┐          ┌────────────────┐
│ user_query      │   主→子  │ query          │
│ search_results  │ ──────→ │ result         │
│ final_answer    │          └────────────────┘
│                │   子→主
│ search_results ←────── result
└────────────────┘
```

### 4.2 State 映射函数的编写

> 通过 **return 语句中的 key 名称** 来决定数据流向：用主图的 key = 传到主图，用子图的 key = 传到子图。

```python
# ── 场景：主图做搜索，子图做搜索执行 ──

# 主图 State
class MainState(TypedDict):
    user_query: str          # 用户的搜索问题
    search_results: str      # 搜索结果（由于子图填充）
    final_answer: str        # 最终答案

# 子图 State
class SearchSubState(TypedDict):
    query: str               # 搜索关键词（从主图 user_query 传入）
    result: str              # 搜索结果（回传到主图 search_results）

# ── 主图 → 子图：映射函数 ──
def map_main_to_sub(main_state: MainState) -> SearchSubState:
    """
    将主图 State 的数据映射到子图 State。
    return 中使用子图的 key 名称。
    """
    print(f"[映射] 主→子: user_query='{main_state['user_query']}' → query")
    return {
        "query": main_state["user_query"],  # 子图的 key
        "result": "",                        # 子图的 key（初始为空）
    }

# ── 子图节点 ──
def search_node(state: SearchSubState) -> SearchSubState:
    """执行搜索（模拟）"""
    print(f"[子图] 搜索: '{state['query']}'")
    # 实际中调搜索 API
    return {"result": f"关于'{state['query']}'的搜索结果..."}

# ── 子图 → 主图：映射函数 ──
def map_sub_to_main(sub_state: SearchSubState) -> MainState:
    """
    将子图 State 的数据映射回主图 State。
    return 中使用主图的 key 名称。
    """
    print(f"[映射] 子→主: result → search_results")
    return {
        "search_results": sub_state["result"],  # 主图的 key
    }
```

### 4.3 推荐的 State 映射模式

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  模式一：直接对称映射（最常用）                         │
│  主图 key: user_name     ←→ 子图 key: name           │
│  主图 key: query_text    ←→ 子图 key: query          │
│  适用：字段含义相同，仅名称不同                         │
│                                                     │
│  模式二：计算映射                                      │
│  主图 key: budget_per_person                         │
│  子图 key: total_budget = state["budget_per_person"] │
│           * state["person_count"]                    │
│  适用：子图需要经过计算后的数据                         │
│                                                     │
│  模式三：多对一映射                                    │
│  主图 key: departure + destination + date            │
│  子图 key: query = f"从{departure}到{destination}    │
│           {date}的航班"                              │
│  适用：子图需要组合多个主图字段                         │
│                                                     │
│  模式四：一对多映射                                    │
│  主图 key: search_results（大段文本）                  │
│  子图 key: flights / hotels / activities             │
│  适用：子图需要拆解主图的一个大字段                     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 4.4 完整的数据传递示例

```python
# ════════════════════════════════════════════════════════════
#  完整示例：主图 + 子图数据传递全流程
# ════════════════════════════════════════════════════════════

from typing import TypedDict
from langgraph.graph import StateGraph, END, START

# ── 子图：搜索执行器 ──
class SearchSubState(TypedDict):
    query: str
    result: str

def execute_search(state: SearchSubState) -> SearchSubState:
    print(f"   [搜索子图] 正在搜索：{state['query']}")
    # 模拟搜索结果
    return {"result": f"🔍 搜索结果：{state['query']} → 发现 42 条相关信息"}

search_subgraph = StateGraph(SearchSubState)
search_subgraph.add_node("search", execute_search)
search_subgraph.add_edge(START, "search")
search_subgraph.add_edge("search", END)
search_app = search_subgraph.compile()

# ── 主图：智能问答 ──
class MainState(TypedDict):
    user_query: str
    search_results: str
    final_answer: str

def analyze_intent(state: MainState) -> MainState:
    print(f"[主图] 分析用户意图：{state['user_query'][:30]}...")
    return state

def call_search_subgraph(state: MainState) -> MainState:
    """调用搜索子图，完成主→子→主的数据传递"""
    print("[主图] 调用搜索子图...")

    # 主→子：通过子图的 State key 传入数据
    sub_result = search_app.invoke({
        "query": state["user_query"],   # 主图的 key → 子图的 query
        "result": "",
    })

    # 子→主：通过主图的 State key 传出数据
    return {"search_results": sub_result["result"]}  # 子图的 result → 主图的 search_results

def generate_answer(state: MainState) -> MainState:
    print(f"[主图] 基于搜索结果生成答案...")
    return {"final_answer": f"回答：基于 {state['search_results']}，我得出以下结论..."}

# ── 构建主图 ──
main_graph = StateGraph(MainState)
main_graph.add_node("analyze", analyze_intent)
main_graph.add_node("search_subgraph", call_search_subgraph)
main_graph.add_node("answer", generate_answer)

main_graph.add_edge(START, "analyze")
main_graph.add_edge("analyze", "search_subgraph")
main_graph.add_edge("search_subgraph", "answer")
main_graph.add_edge("answer", END)

main_app = main_graph.compile()

# ── 执行 ──
result = main_app.invoke({
    "user_query": "2026年夏季日本旅游攻略",
    "search_results": "",
    "final_answer": "",
})
print(f"\n最终答案：{result['final_answer']}")
```

#### ⚠️ 数据传递的关键规则

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  State 数据传递规则（一次性掌握）：                      │
│                                                     │
│  规则1：invoke 时传什么 key，取决于子图的 State 定义    │
│         subgraph_app.invoke({                        │
│             "子图State字段名": 值,                     │
│         })                                          │
│                                                     │
│  规则2：子图返回后取什么 key，来自子图 State 的实际字段  │
│         sub_result["子图State字段名"]                 │
│                                                     │
│  规则3：返回主图时用主图 State 的 key                  │
│         return {"主图State字段名": 值}                │
│                                                     │
│  规则4：字段名相同的，可以无感传递                      │
│         如主图和子图都有 messages，直接传不需要映射      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 五、多 Agent 协作的四种模式

### 5.1 概述

在 LangGraph 中，多个 Agent（子图）的协作方式可以分为四种经典模式：

```
┌─────────────────────────────────────────────────────────────────┐
│                      多 Agent 协作模式的定位                       │
├──────────┬──────────┬────────────────┬───────────┬──────────────┤
│  顺序     │  并行     │  主控专家        │  协商      │              │
│  Serial  │ Parallel │ Supervisor     │ Voting    │              │
│          │          │                │           │              │
│ A→B→C    │ A↘       │     Supervisor │ A↘        │              │
│          │ B→汇总    │      / | \     │ B→投票统计  │              │
│          │ C↗       │     A  B  C    │ C↗        │              │
│          │          │                │           │              │
│ 简单线性  │ 多角度    │ 智能调度         │ 民主决策    │              │
│ 事务处理  │ 并行分析  │ 专家系统         │ 高鲁棒决策  │              │
└──────────┴──────────┴────────────────┴───────────┴──────────────┘
```

| 模式 | 图结构 | 决策方式 | 适用场景 |
|------|:------:|----------|----------|
| **顺序协作** | 链式（A→B→C） | 事先定好顺序 | 步骤有依赖关系的流水线 |
| **并行协作** | 扇形分支汇总 | 同时执行，事后汇总 | 多角度分析、并行数据采集 |
| **主控专家** | Supervisor 调度 | 由主控 LLM 动态分配 | 复杂任务需智能分派 |
| **协商模式** | 并行投票 | 少数服从多数 | 需要高鲁棒性的决策系统 |

### 5.2 模式一：顺序协作（Serial Pipeline）

> **Agent A 做完 → Agent B 做 → Agent C 做**。最简单的协作方式，类似工厂流水线。

#### 流程图

```
START
  ↓
┌──────────┐
│ Agent A  │ ← 分析用户意图
│ (意图分析)│
└────┬─────┘
     ↓
┌──────────┐
│ Agent B  │ ← 查询相关信息
│ (信息检索)│
└────┬─────┘
     ↓
┌──────────┐
│ Agent C  │ ← 生成最终回复
│ (答案生成)│
└────┬─────┘
     ↓
    END
```

#### 代码示例

```python
# ── 顺序协作：意图分析 → 信息检索 → 答案生成 ──
from typing import TypedDict
from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="Qwen/Qwen2.5-3B-Instruct",
    base_url="https://api.siliconflow.cn/v1",
    api_key="your-api-key"
)

class PipelineState(TypedDict):
    user_input: str
    intent: str
    search_result: str
    final_answer: str

# Agent A: 意图分析
def agent_analyze_intent(state: PipelineState) -> PipelineState:
    print("[Agent A] 分析用户意图...")
    response = llm.invoke(f"分析意图，只输出一个词：{state['user_input']}")
    return {"intent": response.content.strip()}

# Agent B: 信息检索
def agent_search(state: PipelineState) -> PipelineState:
    print(f"[Agent B] 根据意图「{state['intent']}」检索信息...")
    # 模拟检索
    return {"search_result": f"关于{state['intent']}的相关信息..."}

# Agent C: 生成答案
def agent_generate(state: PipelineState) -> PipelineState:
    print("[Agent C] 生成最终答案...")
    response = llm.invoke(
        f"基于以下信息回答用户问题：\n信息：{state['search_result']}\n问题：{state['user_input']}"
    )
    return {"final_answer": response.content}

# 构建顺序协作图
graph = StateGraph(PipelineState)
graph.add_node("agent_a", agent_analyze_intent)
graph.add_node("agent_b", agent_search)
graph.add_node("agent_c", agent_generate)

graph.add_edge(START, "agent_a")
graph.add_edge("agent_a", "agent_b")
graph.add_edge("agent_b", "agent_c")
graph.add_edge("agent_c", END)

app = graph.compile()

result = app.invoke({"user_input": "我想了解量子计算的最新进展", "intent": "", "search_result": "", "final_answer": ""})
print(f"\n最终答案：{result['final_answer']}")
```

### 5.3 模式二：并行协作（Parallel Fan-out）

> **多个 Agent 同时开工，各干各的，最后汇总结果。** 适用于任务之间互不依赖的场景。

#### 流程图

```
                    START
                      ↓
                  ┌─────────┐
                  │ 任务分发  │
                  └──┬───┬──┘
                     ↓   ↓   ↓
              ┌──────┐ ┌──────┐ ┌──────┐
              │Agent A│ │Agent B│ │Agent C│ ← 并行执行！
              │情绪分析│ │主题分析│ │实体提取│
              └──┬───┘ └──┬───┘ └──┬───┘
                 ↓        ↓        ↓
                 └────────┼────────┘
                          ↓
                    ┌──────────┐
                    │  汇总节点  │
                    │  整合结果  │
                    └─────┬────┘
                          ↓
                         END
```

#### 代码示例

```python
# ── 并行协作：情绪分析 + 主题分析 + 实体提取 ──
from typing import TypedDict
from langgraph.graph import StateGraph, END, START

class ParallelState(TypedDict):
    text: str               # 输入文本
    sentiment: str          # 情绪分析结果
    topic: str              # 主题分析结果
    entities: str           # 实体提取结果
    summary: str            # 汇总结果

# Agent A: 情绪分析
def agent_sentiment(state: ParallelState) -> ParallelState:
    print("[Agent A] 分析情绪...")
    return {"sentiment": "正面情绪（高兴、期待）"}

# Agent B: 主题分析
def agent_topic(state: ParallelState) -> ParallelState:
    print("[Agent B] 分析主题...")
    return {"topic": "科技/AI"}

# Agent C: 实体提取
def agent_entities(state: ParallelState) -> ParallelState:
    print("[Agent C] 提取实体...")
    return {"entities": "LangGraph, Agent, 多智能体"}

# 并行分发的关键：路由函数返回列表
def fan_out(state: ParallelState) -> list[str]:
    """返回多个目标节点名 → LangGraph 会并行执行！"""
    return ["sentiment", "topic", "entities"]

# 汇总节点
def aggregate(state: ParallelState) -> ParallelState:
    summary = (
        f"情绪：{state['sentiment']}\n"
        f"主题：{state['topic']}\n"
        f"实体：{state['entities']}"
    )
    print(f"[汇总] {summary}")
    return {"summary": summary}

# 构建并行协作图
graph = StateGraph(ParallelState)

graph.add_node("start_distribute", lambda s: s)  # 分发起点
graph.add_node("sentiment", agent_sentiment)
graph.add_node("topic", agent_topic)
graph.add_node("entities", agent_entities)
graph.add_node("aggregate", aggregate)

graph.add_edge(START, "start_distribute")
# 并行分发：一个节点 → 多个目标
graph.add_edge("start_distribute", "sentiment")
graph.add_edge("start_distribute", "topic")
graph.add_edge("start_distribute", "entities")
# 汇总
graph.add_edge("sentiment", "aggregate")
graph.add_edge("topic", "aggregate")
graph.add_edge("entities", "aggregate")
graph.add_edge("aggregate", END)

app = graph.compile()

result = app.invoke({
    "text": "LangGraph 的多智能体功能太强大了！",
    "sentiment": "", "topic": "", "entities": "", "summary": ""
})
print(f"\n汇总结果：\n{result['summary']}")
```

> ⚠️ **并行 vs 条件分支**：并行模式中，从 start_distribute 出发的边是**实线**，表示全部并行执行。而 Supervisor 模式中，从 Supervisor 出发的边是**虚线**（条件路由），一次只走一条。

### 5.4 模式三：主控专家模式（Supervisor）

> **核心 Agent（Supervisor）分析任务后，动态决定交给哪个专家 Agent 处理。** 这是最经典的多 Agent 架构。

#### 架构全景

```
                        用户输入
                           ↓
                  ┌────────────────┐
                  │  Supervisor    │ ← 主控 Agent
                  │  (LLM 决策)     │   分析任务 → 决定分配给谁
                  │                │   接收结果 → 决定是否继续
                  └───┬───┬───┬───┘
              ┌───────┘   │   └───────┘
              ↓           ↓           ↓
        ┌─────────┐ ┌─────────┐ ┌─────────┐
        │ 退款专家  │ │ 物流专家  │ │ 产品专家  │ ← 专家 Agent
        │ (Refund) │ │(Shipping)│ │(Product) │   各自专注一个领域
        └────┬────┘ └────┬────┘ └────┬────┘
             ↓           ↓           ↓
             └───────────┼───────────┘
                         ↓
                  ┌────────────────┐
                  │  Supervisor    │ ← 再次判断
                  │  需要继续吗？   │    【循环】
                  └───────┬────────┘
                          ↓
                         END
```

#### 流程图（Graphviz 渲染效果）

```
START
  ↓
┌──────────────┐
│  supervisor  │ ← 虚线分叉（条件路由，走单条）
└──┬───┬───┬──┘
   ↓   ↓   ↓
 refund shipping product  ← 根据用户输入选一个
   ↓       ↓       ↓
   └───────┼───────┘
           ↓
      ┌──────────┐
      │ supervisor│ ← 循环回来
      └────┬─────┘
           ↓
          END
```

#### 完整代码

```python
# ── 主控专家模式：客服 Supervisor ──
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

llm = ChatOpenAI(
    model="Qwen/Qwen2.5-3B-Instruct",
    base_url="https://api.siliconflow.cn/v1",
    api_key="your-api-key"
)

# ── State ──
class SupervisorState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    next_agent: str         # Supervisor 决定的下一个 Agent
    refund_result: str      # 退款专家的结果
    shipping_result: str    # 物流专家的结果
    product_result: str     # 产品专家的结果

# ── Supervisor 节点 ──
def supervisor_node(state: SupervisorState) -> SupervisorState:
    """
    主控节点：分析用户输入，决定分配给哪个专家。
    实际应用中由 LLM 做决策，这里用关键词模拟演示。
    """
    last_message = state["messages"][-1].content if state["messages"] else ""

    # LLM 驱动的决策（实际应用）
    prompt = f"""分析以下用户消息，判断应交给哪个专家处理。只输出以下之一：
- refund：涉及退款、退货、账单问题
- shipping：涉及物流、配送、快递查询
- product：涉及产品功能、使用方法、规格参数
- finish：问题已解决，可以结束

用户消息：{last_message}

决策："""
    response = llm.invoke(prompt)
    decision = response.content.strip().lower()
    print(f"[Supervisor] 决策 → {decision}")
    return {"next_agent": decision}

# ── 退款专家 ──
def refund_expert(state: SupervisorState) -> SupervisorState:
    print("[退款专家] 处理退款请求...")
    # 实际中调退款系统 API
    return {
        "refund_result": "已为您查询退款进度：预计3-5个工作日到账",
        "messages": [AIMessage(content="已为您查询退款进度：预计3-5个工作日到账")]
    }

# ── 物流专家 ──
def shipping_expert(state: SupervisorState) -> SupervisorState:
    print("[物流专家] 查询物流信息...")
    return {
        "shipping_result": "您的包裹已到达北京分拣中心，预计明天送达",
        "messages": [AIMessage(content="您的包裹已到达北京分拣中心，预计明天送达")]
    }

# ── 产品专家 ──
def product_expert(state: SupervisorState) -> SupervisorState:
    print("[产品专家] 查询产品信息...")
    return {
        "product_result": "该产品支持蓝牙5.3，续航12小时，防水等级IPX5",
        "messages": [AIMessage(content="该产品支持蓝牙5.3，续航12小时，防水等级IPX5")]
    }

# ── 路由函数 ──
def route_by_supervisor(state: SupervisorState) -> str:
    """根据 Supervisor 的决策进行路由"""
    decision = state["next_agent"]
    valid_routes = ["refund", "shipping", "product", "finish"]
    return decision if decision in valid_routes else "finish"

def route_after_expert(state: SupervisorState) -> str:
    """专家处理完后，回到 Supervisor 判断是否需要继续"""
    return "supervisor"  # 始终回到 Supervisor 再判断

# ── 构建图 ──
graph = StateGraph(SupervisorState)

graph.add_node("supervisor", supervisor_node)
graph.add_node("refund", refund_expert)
graph.add_node("shipping", shipping_expert)
graph.add_node("product", product_expert)

graph.add_edge(START, "supervisor")
graph.add_conditional_edges(
    "supervisor", route_by_supervisor,
    {
        "refund": "refund",
        "shipping": "shipping",
        "product": "product",
        "finish": END,
    }
)
# 专家处理完 → 回到 Supervisor
graph.add_edge("refund", "supervisor")
graph.add_edge("shipping", "supervisor")
graph.add_edge("product", "supervisor")

app = graph.compile()

# ── 执行 ──
result = app.invoke({
    "messages": [HumanMessage(content="我上周买的商品还没到货，能帮我查一下吗？")],
    "next_agent": "",
    "refund_result": "", "shipping_result": "", "product_result": ""
})
print(f"\n最终对话：\n{result['messages'][-1].content}")
```

#### Supervisor 模式的执行流程

```
invoke("包裹到哪了？")
    ↓
Supervisor 分析 → "shipping（物流）"
    ↓
Shipping Expert 处理 → "您的包裹在……"
    ↓
回到 Supervisor 再判断 → "finish（问题已解决）"
    ↓
END
```

### 5.5 模式四：协商模式（Voting/Consensus）

> **多个 Agent 各自独立判断，然后投票，少数服从多数。** 适用于需要高鲁棒性和多视角验证的决策场景。

#### 流程图

```
                    START
                      ↓
            ┌─────────┼─────────┐
            ↓         ↓         ↓
       ┌────────┐ ┌────────┐ ┌────────┐
       │ 评审A   │ │ 评审B   │ │ 评审C   │ ← 各自独立判断
       │ (投票)  │ │ (投票)  │ │ (投票)  │
       └───┬────┘ └───┬────┘ └───┬────┘
           ↓          ↓          ↓
           └──────────┼──────────┘
                      ↓
               ┌─────────────┐
               │  投票统计     │ ← 统计票数
               │  多数通过？   │
               └──┬──────┬───┘
                  ↓      ↓
               通过    否决
                  ↓      ↓
                 END    END
```

#### 完整代码

```python
# ── 协商模式：多 Agent 投票决定是否通过 ──
from typing import TypedDict
from langgraph.graph import StateGraph, END, START

class VotingState(TypedDict):
    proposal: str           # 待表决的提案
    vote_a: str             # Agent A 的投票
    vote_b: str             # Agent B 的投票
    vote_c: str             # Agent C 的投票
    result: str             # 最终表决结果

# ── 三个投票 Agent ──
def reviewer_a(state: VotingState) -> VotingState:
    """评审A：基于关键词判断"""
    proposal = state["proposal"]
    # 实际场景中由 LLM 判断
    if "安全" in proposal or "风险" in proposal:
        vote = "approve"  # 涉及安全→通过
    else:
        vote = "reject"
    print(f"   [评审A] 投票：{vote}")
    return {"vote_a": vote}

def reviewer_b(state: VotingState) -> VotingState:
    """评审B：不同的判断逻辑"""
    proposal = state["proposal"]
    if "预算" in proposal or "成本" in proposal:
        vote = "approve"
    else:
        vote = "reject"
    print(f"   [评审B] 投票：{vote}")
    return {"vote_b": vote}

def reviewer_c(state: VotingState) -> VotingState:
    """评审C：LLM 驱动的判断"""
    # 实际中用 LLM 判断；这里用简单规则演示
    if len(state["proposal"]) > 10:
        vote = "approve"
    else:
        vote = "reject"
    print(f"   [评审C] 投票：{vote}")
    return {"vote_c": vote}

# ── 投票统计节点 ──
def tally_votes(state: VotingState) -> VotingState:
    """统计投票结果，多数通过"""
    votes = [state["vote_a"], state["vote_b"], state["vote_c"]]
    approve_count = votes.count("approve")
    reject_count = votes.count("reject")

    print(f"\n   📊 投票统计：通过 {approve_count} 票，否决 {reject_count} 票")

    if approve_count > reject_count:
        result = "通过 ✅"
    elif reject_count > approve_count:
        result = "否决 ❌"
    else:
        result = "平局，需复议 ⚠️"

    print(f"   🎯 最终结果：{result}")
    return {"result": result}

# ── 构建协商图 ──
graph = StateGraph(VotingState)

graph.add_node("reviewer_a", reviewer_a)
graph.add_node("reviewer_b", reviewer_b)
graph.add_node("reviewer_c", reviewer_c)
graph.add_node("tally", tally_votes)

# 三个并行分支
graph.add_edge(START, "reviewer_a")
graph.add_edge(START, "reviewer_b")
graph.add_edge(START, "reviewer_c")

# 汇总到一个节点
graph.add_edge("reviewer_a", "tally")
graph.add_edge("reviewer_b", "tally")
graph.add_edge("reviewer_c", "tally")

graph.add_edge("tally", END)

app = graph.compile()

# ── 执行：测试一个涉及安全和预算的提案 ──
result = app.invoke({
    "proposal": "增加系统安全防护预算",
    "vote_a": "", "vote_b": "", "vote_c": "", "result": ""
})
print(f"\n表决「{result['proposal']}」→ {result['result']}")

"""
输出：
   [评审A] 投票：approve
   [评审B] 投票：approve
   [评审C] 投票：approve

   📊 投票统计：通过 3 票，否决 0 票
   🎯 最终结果：通过 ✅

表决「增加系统安全防护预算」→ 通过 ✅
"""
```

### 5.6 四种模式的对比总结

| 维度 | 顺序协作 | 并行协作 | 主控专家 | 协商模式 |
|------|:-------:|:-------:|:-------:|:-------:|
| **执行方式** | A→B→C 串行 | A/B/C 同时 | Supervisor 动态分派 | 并行投票 |
| **是否有依赖** | 后一步依赖前一步 | 互不依赖 | 由 Supervisor 判断 | 互不依赖 |
| **决策者** | 流程图预定 | 流程图预定 | LLM（Supervisor） | 少数服从多数 |
| **复杂度** | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **适用场景** | 管道式处理 | 多角度分析 | 智能客服 | 内容审核、评审 |
| **延迟** | 累加（A+B+C） | 取决于最慢的 | 取决于最慢的那个专家 | 取决于最慢的评审 |
| **容错性** | 任一失败全失败 | 部分失败不影响其他 | 专家失败可换另一个 | 一票错误不影响整体 |
| **可扩展性** | 加节点改顺序 | 加并行分支 | 加专家+注册路由 | 加投票 Agent |

---

## 六、综合实战——旅行规划助手

### 6.1 实战概述

> 整合 Subgraph + 并行协作 + 预算计算 → 构建一个完整的旅行规划多 Agent 系统。

#### 架构全景

```
                        ┌──────────────┐
                        │   用户输入    │
                        │ 目的地/日期/  │
                        │ 人数/预算     │
                        └──────┬───────┘
                               ↓
            ┌──────────────────┼──────────────────┐
            ↓                  ↓                  ↓
   ┌────────────────┐ ┌───────────────┐ ┌────────────────┐
   │  机票 Subgraph  │ │ 酒店 Subgraph │ │  活动 Subgraph  │
   │  (并行执行)      │ │ (并行执行)     │ │  (并行执行)      │
   │                │ │               │ │                │
   │ START          │ │ START         │ │ START          │
   │   ↓            │ │   ↓           │ │   ↓            │
   │ search_flights │ │ search_hotels │ │search_activities│
   │   ↓            │ │   ↓           │ │   ↓            │
   │ END            │ │ END           │ │ END            │
   └───────┬────────┘ └──────┬────────┘ └───────┬────────┘
           ↓                 ↓                  ↓
           └─────────────────┼──────────────────┘
                             ↓
                   ┌─────────────────┐
                   │   预算计算节点   │
                   │  budget_calc    │
                   └────────┬────────┘
                            ↓
                   ┌─────────────────┐
                   │   规划生成节点   │
                   │  generate_plan  │
                   └────────┬────────┘
                            ↓
                           END
```

#### 功能清单

```
✅ 机票查询 Subgraph（航班推荐、价格对比）
✅ 酒店预订 Subgraph（种类推荐、备选方案）
✅ 活动推荐 Subgraph（当地游玩建议）
✅ 预算计算节点（总费用拆解）
✅ 规划生成节点（完整旅行报告）
```

### 6.2 完整代码

```python
# ════════════════════════════════════════════════════════════
#  综合实战：旅行规划助手（多 Agent 协作系统）
#  知识点：Subgraph + 并行协作 + 预算计算 + 规划生成
# ════════════════════════════════════════════════════════════

# ── 依赖导入 ──
import os
from typing import TypedDict
from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI

# ── 环境设置 ──
llm = ChatOpenAI(
    model="Qwen/Qwen2.5-3B-Instruct",
    base_url="https://api.siliconflow.cn/v1",
    api_key="your-api-key"
)

# ════════════════════════════════════════════════════════════
#  Part 1: 子图 State 定义
# ════════════════════════════════════════════════════════════

# ── 子图1：机票查询 State ──
class FlightSubState(TypedDict):
    destination: str        # 目的地
    departure_date: str     # 出发日期
    return_date: str        # 返回日期
    passengers: int         # 乘客人数
    flight_suggestion: str  # 航班推荐结果

# ── 子图2：酒店查询 State ──
class HotelSubState(TypedDict):
    destination: str
    check_in: str
    check_out: str
    guests: int
    hotel_suggestion: str   # 酒店推荐结果

# ── 子图3：活动推荐 State ──
class ActivitySubState(TypedDict):
    destination: str
    travel_dates: str
    interests: str          # 兴趣偏好（可选）
    activity_suggestion: str # 活动推荐结果

# ── 主图 State ──
class TravelPlanState(TypedDict):
    # 用户输入
    destination: str            # 目的地
    departure_date: str         # 出发日期
    return_date: str            # 返回日期
    passengers: int             # 旅客人数
    budget: float               # 总预算

    # 各专家输出（由子图填充）
    flight_suggestion: str      # 机票建议
    hotel_suggestion: str       # 酒店建议
    activity_suggestion: str    # 活动建议

    # 预算分析
    budget_breakdown: str       # 预算拆解

    # 最终规划
    final_plan: str             # 完整旅行规划报告

# ════════════════════════════════════════════════════════════
#  Part 2: 机票查询 Subgraph
# ════════════════════════════════════════════════════════════

def search_flights(state: FlightSubState) -> FlightSubState:
    """查询航班信息（实际应用中调真实航班 API）"""
    print(f"   ✈️  [机票子图] 查询 {state['departure_date']} → {state['destination']} 的航班...")

    # 模拟航班数据
    suggestion = f"""
航班推荐（{state['destination']}，{state['passengers']}人）：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✈️ 推荐航班：
   航空公司 A：{state['departure_date']} 08:00-11:30，经济舱 ¥2,800/人
   航空公司 B：{state['departure_date']} 14:00-17:30，经济舱 ¥2,400/人
   航空公司 C：{state['departure_date']} 20:00-23:30，经济舱 ¥2,100/人

返程航班（{state['return_date']}）：
   航空公司 A：{state['return_date']} 10:00-13:30，经济舱 ¥2,600/人
   航空公司 B：{state['return_date']} 16:00-19:30，经济舱 ¥2,200/人

💰 推荐方案：往返均选航空公司 B
   单人往返：¥2,400 + ¥2,200 = ¥4,600
   总计（{state['passengers']}人）：¥{4600 * state['passengers']:,}
"""
    return {"flight_suggestion": suggestion}

# 构建机票子图
flight_subgraph = StateGraph(FlightSubState)
flight_subgraph.add_node("search_flights", search_flights)
flight_subgraph.add_edge(START, "search_flights")
flight_subgraph.add_edge("search_flights", END)
flight_app = flight_subgraph.compile()

# ════════════════════════════════════════════════════════════
#  Part 3: 酒店查询 Subgraph
# ════════════════════════════════════════════════════════════

def search_hotels(state: HotelSubState) -> HotelSubState:
    """查询酒店信息（实际应用中调真实酒店 API）"""
    print(f"   🏨 [酒店子图] 查询 {state['destination']} 的酒店...")

    suggestion = f"""
酒店推荐（{state['destination']}，{state['guests']}位住客）：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏨 推荐酒店：
   🌟🌟🌟🌟🌟 五星级：东京帝国酒店
       价格：¥3,500/晚（含早餐）
       位置：市中心，距地铁站步行3分钟
       评分：4.8/5.0

   🌟🌟🌟🌟 四星级：东京湾喜来登
       价格：¥1,800/晚
       位置：滨海区域，距迪士尼15分钟
       评分：4.5/5.0

   🌟🌟🌟 经济型：东横INN 新宿店
       价格：¥600/晚（含简单早餐）
       位置：新宿区，交通便利
       评分：4.2/5.0

💰 推荐方案：四星级酒店（性价比）
   4晚（{state['check_in']} - {state['check_out']}）：¥1,800 × 4 = ¥7,200
"""
    return {"hotel_suggestion": suggestion}

# 构建酒店子图
hotel_subgraph = StateGraph(HotelSubState)
hotel_subgraph.add_node("search_hotels", search_hotels)
hotel_subgraph.add_edge(START, "search_hotels")
hotel_subgraph.add_edge("search_hotels", END)
hotel_app = hotel_subgraph.compile()

# ════════════════════════════════════════════════════════════
#  Part 4: 活动推荐 Subgraph
# ════════════════════════════════════════════════════════════

def search_activities(state: ActivitySubState) -> ActivitySubState:
    """查询当地活动（实际应用中调旅游推荐 API）"""
    print(f"   🎯 [活动子图] 查询 {state['destination']} 的推荐活动...")

    suggestion = f"""
活动推荐（{state['destination']}，{state['travel_dates']}）：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 推荐活动：
   Day 1：浅草寺 → 天空树（晴空塔）→ 浅草美食街
   Day 2：明治神宫 → 原宿/表参道购物 → 涩谷十字路口
   Day 3：筑地市场（早市海鲜）→ 银座 → 秋叶原
   Day 4：上野公园/博物馆 → 东京塔 → 六本木夜景

🎫 门票预算：
   天空树：¥2,100/人
   东京塔：¥1,200/人
   上野博物馆：¥620/人

💰 预估活动总费用（{state.get('passengers', 1)}人）：
   景点 + 交通 + 餐饮 ≈ ¥3,000/人
"""
    return {"activity_suggestion": suggestion}

# 构建活动子图
activity_subgraph = StateGraph(ActivitySubState)
activity_subgraph.add_node("search_activities", search_activities)
activity_subgraph.add_edge(START, "search_activities")
activity_subgraph.add_edge("search_activities", END)
activity_app = activity_subgraph.compile()

# ════════════════════════════════════════════════════════════
#  Part 5: 主图节点（协调 + 汇总）
# ════════════════════════════════════════════════════════════

# ── 并行调度节点：同时调用三个子图 ──
def call_flight_subgraph(state: TravelPlanState) -> TravelPlanState:
    """调用机票子图"""
    print("[主图] 正在调用机票子图...")
    sub_result = flight_app.invoke({
        "destination": state["destination"],
        "departure_date": state["departure_date"],
        "return_date": state["return_date"],
        "passengers": state["passengers"],
        "flight_suggestion": "",
    })
    return {"flight_suggestion": sub_result["flight_suggestion"]}

def call_hotel_subgraph(state: TravelPlanState) -> TravelPlanState:
    """调用酒店子图"""
    print("[主图] 正在调用酒店子图...")
    sub_result = hotel_app.invoke({
        "destination": state["destination"],
        "check_in": state["departure_date"],
        "check_out": state["return_date"],
        "guests": state["passengers"],
        "hotel_suggestion": "",
    })
    return {"hotel_suggestion": sub_result["hotel_suggestion"]}

def call_activity_subgraph(state: TravelPlanState) -> TravelPlanState:
    """调用活动子图"""
    print("[主图] 正在调用活动子图...")
    sub_result = activity_app.invoke({
        "destination": state["destination"],
        "travel_dates": f"{state['departure_date']} - {state['return_date']}",
        "interests": "文化、美食、购物",
        "activity_suggestion": "",
    })
    return {"activity_suggestion": sub_result["activity_suggestion"]}

# ── 预算计算节点 ──
def budget_calculator(state: TravelPlanState) -> TravelPlanState:
    """综合三个子图的结果，计算总费用并拆解预算"""
    print("\n[主图] 💰 正在计算预算...")
    total_budget = state["budget"]

    # 从各子图结果中提取关键数字（实际中用正则或 LLM 提取）
    passengers = state["passengers"]

    # 预算拆解
    flight_cost = 4600 * passengers       # 机票
    hotel_cost = 7200                      # 酒店（4晚）
    activity_cost = 3000 * passengers     # 活动和餐饮
    reserve = total_budget - flight_cost - hotel_cost - activity_cost  # 剩余

    breakdown = f"""
预算拆解（总预算 ¥{total_budget:,}）：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✈️  机票费用：    ¥{flight_cost:,}      ({flight_cost/total_budget*100:.0f}%)
🏨 酒店费用：    ¥{hotel_cost:,}       ({hotel_cost/total_budget*100:.0f}%)
🎯 活动/餐饮：   ¥{activity_cost:,}       ({activity_cost/total_budget*100:.0f}%)
📦 预留/其他：   ¥{reserve:,}        ({reserve/total_budget*100:.0f}%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 合计：        ¥{total_budget:,}     (100%)

{'✅ 预算充足' if reserve >= 0 else '❌ 超出预算！请调整方案'}
"""
    return {"budget_breakdown": breakdown}

# ── 规划生成节点 ──
def generate_final_plan(state: TravelPlanState) -> TravelPlanState:
    """汇总所有信息，生成完整的旅行规划报告"""
    print("[主图] 📝 正在生成完整旅行规划...")

    # 用 LLM 汇总生成完整报告
    prompt = f"""你是一个专业的旅行规划师。请根据以下信息，生成一份完整的旅行规划报告。

目的地：{state['destination']}
日期：{state['departure_date']} - {state['return_date']}
人数：{state['passengers']}人
总预算：¥{state['budget']:,}

【机票方案】
{state['flight_suggestion']}

【酒店方案】
{state['hotel_suggestion']}

【活动方案】
{state['activity_suggestion']}

【预算拆解】
{state['budget_breakdown']}

请用中文生成一份详细的旅行规划报告，包含：
1. 行程概览
2. 推荐理由
3. 详细日程安排（每一天）
4. 预算说明
5. 备选方案（经济型）
6. 注意事项（交通、语言、天气、安全、饮食等）

格式要求：使用标题、列表和表格来组织内容。"""

    response = llm.invoke(prompt)
    print("   ✅ 旅行规划报告生成完成！")
    return {"final_plan": response.content}

# ── 分发节点（并行起点）──
def distribute(_: TravelPlanState) -> TravelPlanState:
    """分发起点，不修改状态"""
    return {}

# ════════════════════════════════════════════════════════════
#  Part 6: 构建主图
# ════════════════════════════════════════════════════════════

main_graph = StateGraph(TravelPlanState)

# 添加所有节点
main_graph.add_node("distribute", distribute)
main_graph.add_node("flight_subgraph", call_flight_subgraph)
main_graph.add_node("hotel_subgraph", call_hotel_subgraph)
main_graph.add_node("activity_subgraph", call_activity_subgraph)
main_graph.add_node("budget_calc", budget_calculator)
main_graph.add_node("generate_plan", generate_final_plan)

# 边定义
main_graph.add_edge(START, "distribute")

# 并行分发：三个子图同时执行
main_graph.add_edge("distribute", "flight_subgraph")
main_graph.add_edge("distribute", "hotel_subgraph")
main_graph.add_edge("distribute", "activity_subgraph")

# 三个子图的结果汇总到预算计算节点
main_graph.add_edge("flight_subgraph", "budget_calc")
main_graph.add_edge("hotel_subgraph", "budget_calc")
main_graph.add_edge("activity_subgraph", "budget_calc")

# 预算计算 → 规划生成 → 结束
main_graph.add_edge("budget_calc", "generate_plan")
main_graph.add_edge("generate_plan", END)

travel_app = main_graph.compile()

# ════════════════════════════════════════════════════════════
#  Part 7: 执行演示
# ════════════════════════════════════════════════════════════

print("═" * 60)
print("  旅行规划助手 —— 多 Agent 协作演示")
print("═" * 60)

# 用户输入
user_request = {
    "destination": "日本东京",
    "departure_date": "2026-06-01",
    "return_date": "2026-06-05",
    "passengers": 2,
    "budget": 20000,
    "flight_suggestion": "",
    "hotel_suggestion": "",
    "activity_suggestion": "",
    "budget_breakdown": "",
    "final_plan": "",
}

print(f"\n📋 旅行需求：")
print(f"   目的地：{user_request['destination']}")
print(f"   日期：{user_request['departure_date']} → {user_request['return_date']}")
print(f"   人数：{user_request['passengers']}人")
print(f"   预算：¥{user_request['budget']:,}")
print()

# 执行
result = travel_app.invoke(user_request)

# 输出结果摘要
print("\n" + "═" * 60)
print("  📊 规划结果摘要")
print("═" * 60)

print(f"\n{result['flight_suggestion']}")
print(f"\n{result['hotel_suggestion']}")
print(f"\n{result['activity_suggestion']}")
print(f"\n{result['budget_breakdown']}")

print("\n" + "═" * 60)
print("  📝 完整旅行规划报告")
print("═" * 60)
print(f"\n{result['final_plan']}")
```

### 6.3 执行效果演示

```
══════════════════════════════════════
  旅行规划助手 —— 多 Agent 协作演示
══════════════════════════════════════

📋 旅行需求：
   目的地：日本东京
   日期：2026-06-01 → 2026-06-05
   人数：2人
   预算：¥20,000

[主图] 正在调用机票子图...
   ✈️  [机票子图] 查询 2026-06-01 → 日本东京 的航班...
[主图] 正在调用酒店子图...
   🏨 [酒店子图] 查询 日本东京 的酒店...
[主图] 正在调用活动子图...
   🎯 [活动子图] 查询 日本东京 的推荐活动...

[主图] 💰 正在计算预算...
[主图] 📝 正在生成完整旅行规划...

══════════════════════════════════════
  📊 规划结果摘要
══════════════════════════════════════

✈️ 航班推荐（日本东京，2人）：
   推荐方案：往返均选航空公司 B
   单人往返：¥4,600
   总计（2人）：¥9,200

🏨 酒店推荐（日本东京，2位住客）：
   推荐方案：四星级酒店
   4晚：¥7,200

🎯 活动推荐（日本东京，6月1日-5日）：
   预估活动总费用：¥6,000

💰 预算拆解（总预算 ¥20,000）：
   机票 ¥9,200 (46%) | 酒店 ¥7,200 (36%) | 活动 ¥6,000 (15%)
   预留 ¥-2,400  ← 超预算！(实际场景中会调整)

══════════════════════════════════════
  📝 完整旅行规划报告
══════════════════════════════════════

【行程概览】
【推荐理由】
【Day 1-5 详细日程】
【预算说明】
【备选方案（经济型）】
【注意事项】
  - 交通：购买 Suica 卡，地铁出行便捷
  - 语言：下载翻译 App，备基础日语
  - 天气：6月东京 22-28°C，梅雨季备伞
  - 安全：日本治安良好，注意地震预警
  - 饮食：备现金，部分小店只收现金
```

### 6.4 实战中的知识点映射

| 实战功能 | 对应知识点 | 代码位置 |
|----------|-----------|----------|
| 三个独立子图 | Subgraph 概念 | `FlightSubState` / `HotelSubState` / `ActivitySubState` |
| 主图并行调用三个子图 | 并行协作模式 | `distribute` → `flight/hotel/activity` 三个边 |
| 子图返回数据到主图 | State 数据传递 | `sub_result["flight_suggestion"]` → 主图 State |
| 预算节点汇总三个子图结果 | 汇总逻辑 | `budget_calculator` 提取三个子图的数据计算 |
| LLM 生成完整规划报告 | LLM 整合 | `generate_final_plan` 用 LLM 汇总所有信息 |
| 每个子图可独立测试 | 独立测试 | `flight_app.invoke(...)` 可直接调 |

---

## 七、协作模式决策指南

### 7.1 选择协作模式的决策树

```
你的任务有什么特点？
    │
    ├── 步骤之间有严格顺序依赖
    │   例：先分析意图 → 再查资料 → 再写回答
    │   └── → 顺序协作
    │
    ├── 多个独立维度需要同时分析
    │   例：情感分析 + 主题提取 + 实体识别
    │   └── → 并行协作
    │
    ├── 任务类型多样，需要智能分配
    │   例：客服咨询（退款/物流/产品/投诉...）
    │   不清楚用户会问什么
    │   └── → 主控专家（Supervisor）
    │
    └── 需要高可靠性的决策
       例：内容发布审批、金融风控决策
       不能由单个 Agent 说了算
       └── → 协商模式（投票）
```

### 7.2 模式组合使用

> 四种模式可以在一个复杂系统中**组合使用**。例如：

```
Supervisor 模式的专家节点本身也可以是 Subgraph：

                    Supervisor
                    /    |    \
              退款专家  物流专家  产品专家
              (子图)    (子图)    (子图)
                │         │         │
                ↓         ↓         ↓
              内部使用顺序协作或并行协作
```

```python
# ── 专家节点内部是顺序协作的 Subgraph ──
# 退款专家子图：验证身份 → 查询订单 → 计算退款金额 → 发起退款
refund_subgraph = StateGraph(RefundState)
refund_subgraph.add_node("verify_identity", verify_identity)
refund_subgraph.add_node("query_order", query_order)
refund_subgraph.add_node("calculate_refund", calculate_refund)
refund_subgraph.add_node("process_refund", process_refund)
# 顺序协作
refund_subgraph.add_edge(START, "verify_identity")
refund_subgraph.add_edge("verify_identity", "query_order")
refund_subgraph.add_edge("query_order", "calculate_refund")
refund_subgraph.add_edge("calculate_refund", "process_refund")
refund_subgraph.add_edge("process_refund", END)
refund_app = refund_subgraph.compile()

# 然后在 Supervisor 图中，退款专家节点直接调用 refund_app
```

---

## 八、Subgraph 设计最佳实践

### 8.1 设计原则

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Subgraph 设计四大原则：                                       │
│                                                             │
│  1️⃣  单一职责                                                 │
│      一个子图只做一件事（机票查询 ≠ 酒店预订 ≠ 活动推荐）         │
│                                                             │
│  2️⃣  明确接口                                                 │
│      子图的 State 就是它的"API"——输入什么字段，输出什么字段      │
│      团队协作时，定了 State 就定了接口                           │
│                                                             │
│  3️⃣  可独立运行                                               │
│      子图必须能脱离主图单独 invoke 和测试                       │
│      subgraph_app.invoke({...}) 应该能正常返回                 │
│                                                             │
│  4️⃣  无副作用                                                 │
│      子图不应修改外部的全局状态                                  │
│      所有的输入输出都通过 State 传递                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 命名规范建议

| 类型 | 命名规范 | 示例 |
|------|----------|------|
| 子图 State | `{功能}SubState` | `FlightSubState`, `HotelSubState` |
| 子图 app | `{功能}_app` | `flight_app`, `hotel_app` |
| 子图变量 | `{功能}_subgraph` | `flight_subgraph`, `hotel_subgraph` |
| 节点函数 | `{动词}_{名词}` | `search_flights`, `calculate_budget` |
| 路由函数 | `route_by_{条件}` | `route_by_supervisor`, `route_by_urgency` |

### 8.3 子图版本管理

> 子图的独立性带来的一个重要好处：**可以独立升级**。

```python
# ── 版本化子图 ──
# flight_subgraph_v1: 返回静态模拟数据
# flight_subgraph_v2: 接入真实航班 API
# flight_subgraph_v3: 增加价格预测和推荐算法

# 主图不需要改动！只要子图的 State 接口不变，
# 子图内部怎么实现都可以自由升级。

# 唯一的约束：State 的字段名和类型必须保持兼容
class FlightSubState(TypedDict):
    destination: str       # ← 接口字段，保持稳定
    flight_suggestion: str # ← 接口字段，保持稳定
    # 内部实现可以随意加字段
```

### 8.4 何时不需要子图

```
以下情况不建议使用子图，直接用普通节点即可：

❌ 只有 2-3 个简单步骤
   例：分析情绪（一个 LLM 调用）→ 直接放主图节点

❌ 不会被复用的逻辑
   例：某个业务特有的数据转换 → 不需要抽成子图

❌ 过度设计
   例：为了"看起来高级"而把 2 步操作封成子图 → 增加理解成本
```

---

## 九、常见问题与排错指南

### 9.1 错误速查表

| 错误信息 | 原因 | 解决方法 | 优先级 |
|----------|------|----------|:------:|
| `KeyError: 'xxx'` | 子图 State 需要的字段在主图调用时没有传入 | 检查 `subgraph_app.invoke()` 中是否传入了所有必需字段 | 🔴 高 |
| 子图结果没有回传到主图 | `return` 时用了子图的 key 而不是主图的 key | `return {"主图key": 子图结果["子图key"]}` | 🔴 高 |
| 并行执行结果互相覆盖 | 多个并行节点修改了同一个 State 字段 | 每个并行节点写**不同字段**；或用 `Reducer` 合并 | 🔴 高 |
| Supervisor 无限循环 | `route_after_expert` 始终返回 `"supervisor"`，没有结束条件 | 在 Supervisor 中增加 `finish` 判断逻辑 | 🟡 中 |
| 子图编译后 state key 不一致 | 主图编译时找不到子图引用的字段 | 确保子图先编译，且 State 定义在所有节点之前 | 🟡 中 |
| 并行分支数超过限制 | 一个节点出边太多 | 使用中间分发节点分组 | 🟢 低 |
| 子图嵌套层数太多 | 子图套子图套子图 → 调试困难 | 最多嵌套 2 层（主图→子图→子子图） | 🟢 低 |

### 9.2 排查流程

```
多 Agent 系统调试流程：

Step 1: 逐个子图单独测试
    └── 每个 subgraph_app.invoke({测试数据})，确保独立运行正常
        如果子图单独跑就有问题 → 修复子图内部逻辑

Step 2: 检查 State 数据传递
    └── 在主图调用子图的节点中加 print
        print(f"传入子图的数据：{...}")
        print(f"子图返回的数据：{sub_result}")
        确认字段名一一对应

Step 3: 测试单条路径
    └── 把并行协作暂时改成顺序协作
        一条一条路径验证通过后，再改回并行

Step 4: 端到端测试
    └── 用真实输入跑完整流程
        用 get_state_history 查看每一步的状态变化

Step 5: 性能优化
    └── 并行模式确认各子图延迟
        优先优化最慢的子图
```

### 9.3 常见陷阱

**陷阱一：并行节点写入同一个 State 字段**

```python
# ❌ 错误：flight 和 hotel 都写 suggestion 字段 → 互相覆盖
def call_flight(state):
    return {"suggestion": "航班建议..."}  # ← 会被 hotel 覆盖！

def call_hotel(state):
    return {"suggestion": "酒店建议..."}  # ← 覆盖了 flight 的结果！

# ✅ 正确：每个子图写不同的字段
class TravelPlanState(TypedDict):
    flight_suggestion: str    # 机票专用字段
    hotel_suggestion: str     # 酒店专用字段
    activity_suggestion: str  # 活动专用字段
```

**陷阱二：子图返回后忘记映射字段名**

```python
# ❌ 错误：直接返回子图的 State（字段名不匹配）
def call_flight(state: MainState) -> MainState:
    sub_result = flight_app.invoke({...})
    return sub_result  # ← sub_result 的 key 是 flight_suggestion，
                       #    但如果主图 State 的 key 叫 flight_result
                       #    数据就丢了！

# ✅ 正确：显式映射
def call_flight(state: MainState) -> MainState:
    sub_result = flight_app.invoke({...})
    return {"flight_result": sub_result["flight_suggestion"]}
                       # ↑ 主图 key     ↑ 子图 key
```

**陷阱三：Supervisor 缺少结束条件**

```python
# ❌ 错误：永远回到 supervisor → 无限循环
def route_after_expert(state):
    return "supervisor"  # ← 永远不结束！

# ✅ 正确：Supervisor 判断问题是否已解决
def supervisor_node(state):
    # ...分析...
    if 问题已解决:
        return {"next_agent": "finish"}
    else:
        return {"next_agent": 某个专家}
```

---

## 十、课后练习

### 练习一：基础 Subgraph（⭐）

**目标**：创建并调用一个简单的子图

**场景**：一个"字符串处理"子图，包含两个步骤——反转字符串 + 转大写。

**要求**：
- 子图 State：`input_str: str`, `reversed: str`, `result: str`
- 节点1 `reverse_node`：反转字符串
- 节点2 `uppercase_node`：转大写
- 主图调用子图，输入 `"hello"`，期望输出 `"OLLEH"`

**验收标准**：
- 子图能独立编译和测试
- 主图调用子图能正确传递数据
- 输入 `"hello"` → 输出 `"OLLEH"`

### 练习二：并行协作（⭐⭐）

**目标**：实现一个三路并行分析系统

**场景**：输入一段文本，三个 Agent 并行分析——关键词提取、情感分析、语言检测。

**要求**：
- 三个分析节点并行执行
- 每个节点写入不同的 State 字段
- 汇总节点整合三个分析结果

**验收标准**：
- 并行节点不会互相覆盖结果
- 汇总节点能读取到所有三个分析结果

### 练习三：Supervisor 模式（⭐⭐⭐）

**目标**：实现一个智能客服 Supervisor

**场景**：用户输入问题，Supervisor（LLM）判断分给哪个部门。

**要求**：
- Supervisor 用 LLM 分析意图
- 四个专家 Agent：退款、物流、产品、投诉
- 专家处理后回到 Supervisor 判断是否结束
- 设置循环上限（防止死循环）

**验收标准**：
- "我要退款" → 退款专家处理 → 结束
- "包裹在哪" → 物流专家处理 → 结束
- "产品怎么用" → 产品专家处理 → 结束
- 连续对话不超过 max_iterations 次

### 练习四：协商模式（⭐⭐⭐）

**目标**：实现一个多角度内容评审系统

**场景**：三个评审 Agent 从安全性、合规性、用户体验三个角度独立评审，投票决定是否通过。

**要求**：
- Agent A：安全性评审（用 LLM 判断）
- Agent B：合规性评审（用 LLM 判断）
- Agent C：用户体验评审（用 LLM 判断）
- 投票统计节点：至少 2 票通过才算通过

**验收标准**：
- 三个评审各自独立输出 vote
- 投票统计正确（多数通过/否决/平局）
- 每个评审的角度有明显差异

### 练习五：综合实战——电影推荐系统（⭐⭐⭐⭐）

**目标**：构建一个完整的多 Agent 电影推荐系统

**场景**：用户输入偏好（类型、年代、语言等），系统并行查询多个数据源，汇总后生成个性化推荐。

**要求**：
1. **三个 Subgraph**：热门电影查询子图、评分查询子图、相似用户推荐子图
2. **并行执行**：三个子图同时查询
3. **汇总节点**：综合三个源的结果，去重并排序
4. **LLM 生成**：用 LLM 生成推荐理由
5. 支持 State 映射（主图 State 与三个子图 State 不同）

**框架代码**：

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END, START

# 主图 State
class RecommendState(TypedDict):
    genre: str              # 偏好类型
    year_range: str         # 年代范围
    hot_movies: str         # 热门子图结果
    rated_movies: str       # 评分子图结果
    similar_users: str      # 相似用户子图结果
    final_recommendation: str  # 最终推荐

# TODO: 实现三个子图
class HotSubState(TypedDict):
    genre: str
    result: str

class RatingSubState(TypedDict):
    genre: str
    min_rating: float
    result: str

class SimilarSubState(TypedDict):
    genre: str
    result: str

# TODO: 构建三个子图
# TODO: 构建主图（并行调用 + 汇总 + LLM 生成推荐）
# TODO: 测试
```

**验收标准**：
- 三个子图并行执行
- 汇总节点正确整合三个数据源
- 最终推荐包含电影名称、评分、推荐理由
- 多组输入产生不同的推荐结果

---

## 十一、课程小结

### 11.1 核心知识图谱

```
┌──────────────────────────────────────────────────────────────┐
│        LangGraph 04——构筑多智能体协作系统 核心知识体系           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1️⃣  单一 Agent vs 多 Agent                                    │
│      ├── 单一 Agent 局限：职责不清、难以维护、无专业化、难复用    │
│      ├── 多 Agent 优势：专业分工、独立测试、可复用组合            │
│      └── 决策：任务>4 个或跨多领域时，选多 Agent                │
│                                                              │
│  2️⃣  Subgraph——多 Agent 的基石                                  │
│      ├── 子图是独立的 LangGraph 图（有自己的 State/Node/Edge）   │
│      ├── 子图可以作为节点被主图调用                              │
│      ├── 模块化 + 可复用 + 可独立测试                           │
│      └── 设计原则：单一职责、明确接口、可独立运行、无副作用        │
│                                                              │
│  3️⃣  State 数据传递（主图 ↔ 子图）                               │
│      ├── 主→子：invoke 时用子图的 State key 传入                 │
│      ├── 子→主：return 时用主图的 State key 传出                 │
│      ├── 四种映射模式：直接对称 / 计算 / 多对一 / 一对多          │
│      └── 关键：字段名相同的可以无感传递                           │
│                                                              │
│  4️⃣  四种协作模式                                               │
│      ├── 顺序协作：A→B→C，有依赖关系的流水线                     │
│      ├── 并行协作：同时执行互不依赖的任务，最后汇总               │
│      ├── 主控专家：Supervisor 智能分派 + 循环，最经典的架构       │
│      └── 协商模式：多 Agent 投票，少数服从多数，高鲁棒性          │
│                                                              │
│  5️⃣  综合实战——旅行规划助手                                       │
│      ├── 三个子图：机票查询 + 酒店预订 + 活动推荐                 │
│      ├── 并行调用三个子图                                       │
│      ├── 预算计算节点汇总分析                                    │
│      ├── LLM 生成完整旅行规划报告                                │
│      └── 包含每日行程、预算拆解、注意事项                         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 11.2 一句话总结

> **LangGraph 04 教你如何把多个单兵 Agent 组织成一支高效的团队**——通过 Subgraph 封装专业能力（每个 Agent 只做好一件事），通过四种协作模式灵活调配（顺序/并行/Supervisor/投票），通过 State 映射精确控制数据流（主图 ↔ 子图透明传递），最终构建出像旅行规划助手这样多引擎并行、智能协调、结果整合的生产级多 Agent 系统。

### 11.3 关键 API 速查

| API | 用途 | 所属知识点 |
|-----|------|-----------|
| `subgraph = StateGraph(SubState)` | 定义子图 | Subgraph |
| `subgraph_app = subgraph.compile()` | 独立编译子图 | Subgraph |
| `subgraph_app.invoke({子图key: 值})` | 主图调用子图 | State 传递 |
| `return {"主图key": sub_result["子图key"]}` | 子图结果回传主图 | State 传递 |
| `graph.add_edge("distribute", "sub_a")` | 并行分发 | 并行协作 |
| `graph.add_edge("distribute", "sub_b")` | （同上） | 并行协作 |
| `add_conditional_edges(supervisor, fn, map)` | Supervisor 动态路由 | 主控专家 |
| `graph.add_edge("expert", "supervisor")` | 专家→回 Supervisor 循环 | 主控专家 |

### 11.4 与前几课的对比

| 维度 | 01 入门组件 | 02 记忆恢复 | 03 人机时间旅行 | 04 多智能体（本课） |
|------|:----------:|:----------:|:-------------:|:-----------------:|
| **核心关注** | 图怎么搭 | 状态怎么存 | 流程怎么控 | **团队怎么协作** |
| **关键 API** | `StateGraph`, `add_node` | `MemorySaver`, `Thread` | `interrupt`, `stream` | **`Subgraph`, `invoke`** |
| **解决的问题** | 能跑起来 | 断电能恢复 | 人能参与 | **多引擎协同** |
| **开发模式** | 单人单图 | 单人单图 | 单人单图 | **多人多图并行开发** |
| **复杂度** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | **⭐⭐⭐⭐** |

### 11.5 系列课程定位

```
LangChain 系列（18课）→ 模型调用、提示词、链式调用、Agent 基础
                          ↓
LangGraph 系列（6课）  → Agent 编排、状态持久化、多智能体、生产部署
    ├── 00 开篇                   ✅
    ├── 01 核心概念与入门            ✅
    ├── 02 状态持久化与记忆          ✅
    ├── 03 人机协作与时间旅行        ✅
    ├── 04 构筑多智能体协作系统      ✅ 🆕  ← 你在这里
    ├── 05 外部工具集成与 API 调用   ⬜ 待续
    └── 06 生产部署上线             ⬜ 待续

本节课是 LangGraph 系列的"架构升级"课程——
从单兵作战进入团队协作的新阶段。
掌握 Subgraph 和四种协作模式后，
你已经具备了构建复杂生产级 Agent 系统的核心能力。

下一课将进入"工具集成"——如何让 Agent 调用外部 API 和数据库，
让多智能体系统真正落地。
```

---

*本教学文档基于陈泽鹏老师视频课程整理编写。*
*本文档涵盖 LangGraph v1.2.0 中的 Subgraph 概念、主图与子图 State 数据传递、四种多 Agent 协作模式（顺序/并行/主控专家/协商），并以旅行规划助手为综合实战案例。*
