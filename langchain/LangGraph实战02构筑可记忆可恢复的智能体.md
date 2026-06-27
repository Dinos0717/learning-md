# LangGraph 实战——02 构筑可记忆、可恢复的智能体

> 基于教学视频课程整理编写 · 2026年6月

---

## 目录

- [一、课程背景与目标](#一课程背景与目标)
- [二、复杂 AI 应用的四大痛点](#二复杂-ai-应用的四大痛点)
- [三、State 设计最佳实践](#三state-设计最佳实践)
- [四、Reducer——状态的更新机制](#四reducer状态的更新机制)
- [五、Checkpoint 机制——状态的持久化存储](#五checkpoint-机制状态的持久化存储)
- [六、Thread——独立的执行上下文](#六thread独立的执行上下文)
- [七、Durable Execution——持久化执行](#七durable-execution持久化执行)
- [八、实战一——可恢复的数据管道](#八实战一可恢复的数据管道)
- [九、记忆管理——短期记忆与长期记忆](#九记忆管理短期记忆与长期记忆)
- [十、记忆管理策略——重要性评分与时间衰减](#十记忆管理策略重要性评分与时间衰减)
- [十一、实战二——有记忆的个人助理](#十一实战二有记忆的个人助理)
- [十二、常见问题与排错指南](#十二常见问题与排错指南)
- [十三、课程小结](#十三课程小结)

---

## 一、课程背景与目标

### 1.1 前情回顾

在上一课中，我们学习了 LangGraph 的三大核心组件——State（状态）、Node（节点）、Edge（边），并完成了第一个内容审核 Agent 的构建。

### 1.2 本节课的核心问题

> **Agent 运行到一半崩溃了怎么办？怎么让 Agent 记住用户的偏好和习惯？**

```
本课要解决的关键问题：

问题1：状态丢失
    Agent 执行中断 → 之前所有结果全没了 → 从头再来 😰
    
问题2：无法恢复
    服务器重启 → Agent 不知道之前做到哪了 → 完全失忆
    
问题3：记不住用户
    每次对话都是"第一次认识" → 用户体验差
    
问题4：数据流混乱
    State 字段越来越多 → 难以维护和扩展
```

### 1.3 本课要掌握的目标

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  目标一：掌握 State 设计和 Checkpoint 持久化        │
│         ├── State 设计的四大原则                   │
│         ├── Reducer 更新机制（add/自定义）         │
│         ├── MemorySaver / SqliteSaver            │
│         └── Thread 独立执行上下文                 │
│                                                 │
│  目标二：理解 Durable Execution 持久化执行          │
│         ├── Checkpoint 的工作原理                 │
│         ├── 断点续传的实现                        │
│         └── 故障恢复的完整流程                     │
│                                                 │
│  目标三：掌握记忆管理                              │
│         ├── 短期记忆 vs 长期记忆                   │
│         ├── 事实提取与存储                        │
│         └── 重要性评分 + 时间衰减策略              │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 二、复杂 AI 应用的四大痛点

### 2.1 痛点全景

```
┌─────────────────────────────────────────────────────────────┐
│                复杂 AI 应用的四大痛点                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1️⃣  状态丢失                                                │
│      执行中断 → 所有进度清零 → 从头再来                        │
│      例：处理100条数据，处理到第67条时崩溃 → 66条白做           │
│                                                             │
│  2️⃣  执行中断                                                │
│      Agent 长时间运行 → 莫名其妙中断 → 无法定位原因             │
│                                                             │
│  3️⃣  长期记忆缺失                                            │
│      每次对话都是"第一次认识" → 不知道用户偏好和习惯            │
│                                                             │
│  4️⃣  可维护性差                                              │
│      字段越来越多 → State 结构混乱 → 难以扩展                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 LangGraph 的解决方案

| 痛点 | LangGraph 方案 | 核心机制 |
|------|---------------|----------|
| 状态丢失 | Checkpoint 持久化 | 每节点执行后自动存档 |
| 执行中断 | Durable Execution | 从断点无缝恢复 |
| 记忆缺失 | 长期记忆管理 | 事实提取 + 持久化存储 |
| 可维护性差 | State 设计原则 | 最小化、清晰命名、类型安全、分层 |

---

## 三、State 设计最佳实践

### 3.1 State 的核心地位

> **State 是 LangGraph 应用的核心数据，类似于企业级应用中的业务表设计。** 表结构贯穿业务始终，字段设计决定系统的可用性和可扩展性。

### 3.2 四大设计原则

#### 原则一：最小化——只存必要数据

```python
from typing import TypedDict

# ❌ 不好的设计：数据冗余
class BadState(TypedDict):
    messages: list           # ✅ 对话记录，必要
    last_message: str        # ❌ 冗余！messages[-1] 就是 last_message
    message_count: int       # ❌ 冗余！len(messages) 就是 message_count

# ✅ 好的设计：最小化
class GoodState(TypedDict):
    messages: list           # 对话记录 → 就够了！
    # last_message = messages[-1]
    # message_count = len(messages)
    # → 需要时动态计算，不存储冗余数据
```

#### 原则二：清晰命名——见名知意

```python
# ❌ 命名不清晰
class BadState(TypedDict):
    data: str          # 什么数据？
    temp: int          # 什么温度？临时变量？
    flag: bool         # 什么标志？

# ✅ 命名清晰
class GoodState(TypedDict):
    user_input: str          # 用户输入内容
    session_temperature: int # 会话温度参数
    requires_review: bool    # 是否需要人工审核
```

#### 原则三：类型安全

```python
from typing import Annotated, Optional, Literal

class SafeState(TypedDict):
    # 使用 Literal 限制枚举值
    status: Literal["active", "paused", "completed", "failed"]
    
    # 使用 Optional 标识可选字段
    error_message: Optional[str]     # 可能没有错误
    
    # 使用明确类型而非 Any
    confidence: float                # ✅ 明确是 float
    # confidence: Any                # ❌ 不要用 Any
```

#### 原则四：分层设计

```python
from typing import TypedDict

# ── 子对象定义 ──
class UserProfile(TypedDict):
    name: str
    age: int
    city: str

class SessionInfo(TypedDict):
    session_id: str
    started_at: str
    message_count: int

# ── 主 State 引用子对象 ──
class ComplexState(TypedDict):
    user: UserProfile        # 用户画像（嵌套对象）
    session: SessionInfo     # 会话信息（嵌套对象）
    messages: list           # 对话记录
```

### 3.3 最简单的 State 示例

```python
class SimpleState(TypedDict):
    """最简单的 State 设计"""
    user_input: str          # 用户输入
    response: str            # AI 响应
    conversation_count: int  # 对话次数统计
```

---

## 四、Reducer——状态的更新机制

### 4.1 什么是 Reducer？

> **Reducer** 定义了 State 中每个字段**如何被更新**。在 LangGraph 中，节点返回的字典会更新 State——Reducer 决定了是**替换**还是**累加**。

```
默认行为（无 Reducer）：
State: {"count": 10}
Node 返回: {"count": 5}
结果: {"count": 5}    ← 直接替换

有 Reducer（add）：
State: {"count": 10}
Node 返回: {"count": 5}
结果: {"count": 15}    ← 累加！
```

### 4.2 Annotated + Reducer 的完整示例

```python
from typing import TypedDict, Annotated
from operator import add
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # 简单替换：没有 Reducer → 节点返回什么就替换成什么
    username: str
    session_id: str
    
    # 累加更新：使用 add reducer → 每次累加
    total_tokens: Annotated[int, add]
    
    # 消息追加：使用 add_messages → 自动去重 + 保持顺序
    messages: Annotated[list, add_messages]
```

### 4.3 累加效果演示

```python
# 初始 State
state = {
    "total_tokens": 100,     # 初始 100 tokens
    "messages": ["msg1", "msg2"]
}

# 第一次更新
update_1 = {
    "total_tokens": 50,      # 新增 50
    "messages": ["msg3"]      # 新增 msg3
}
# 结果: total_tokens = 150 (100+50), messages = ["msg1","msg2","msg3"]

# 第二次更新
update_2 = {
    "total_tokens": 30,      # 再新增 30
    "messages": ["msg4"]
}
# 结果: total_tokens = 180 (150+30), messages = ["msg1","msg2","msg3","msg4"]
```

### 4.4 自定义 Reducer

```python
def custom_list_reducer(old: list, new: list) -> list:
    """自定义 Reducer：合并 + 去重"""
    combined = old + new
    seen = set()
    result = []
    for item in combined:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

# 使用自定义 Reducer
class CustomState(TypedDict):
    unique_items: Annotated[list, custom_list_reducer]
```

### 4.5 add_messages 的内置特性

```python
# add_messages 是 LangGraph 内置的消息 Reducer
# 特性1：自动去重
# 特性2：保持消息顺序
# 特性3：支持 Message 对象

from langgraph.graph import MessagesState  # 已经包装好的消息 State

# 等价于：
class MyState(TypedDict):
    messages: Annotated[list, add_messages]
```

---

## 五、Checkpoint 机制——状态的持久化存储

### 5.1 什么是 Checkpoint？

> **Checkpoint** 是 LangGraph 的状态存档机制。每执行完一个节点，自动保存当前 State 的完整快照。

```
执行过程：
START → [Node A] → 💾存档 → [Node B] → 💾存档 → [Node C] → 💾存档 → END
                ↑           ↑           ↑
            Checkpoint1  Checkpoint2  Checkpoint3

每个 Checkpoint 包含：
├── 完整的 State 快照（所有变量的当前值）
├── 节点执行历史
├── 时间戳
└── 父 Checkpoint 的引用
```

### 5.2 三种存储方式

| 存储方式 | 类 | 位置 | 特点 | 适用场景 |
|----------|----|------|------|----------|
| **Memory** | `MemorySaver` | 内存 | 快，不需外部依赖 | 开发测试 |
| **SQLite** | `SqliteSaver` | 本地磁盘文件 | 重启后仍存在 | 本地持久化 |
| **PostgreSQL** | `PostgresSaver` | 数据库 | 向量存储，生产级 | 生产环境 |

### 5.3 MemorySaver 示例

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class CounterState(TypedDict):
    count: int

def increment(state: CounterState) -> dict:
    """每次执行 count + 1"""
    return {"count": state.get("count", 0) + 1}

# ── 构建图 ──
graph = StateGraph(CounterState)
graph.add_node("increment", increment)
graph.add_edge(START, "increment")
graph.add_edge("increment", END)

# ── 使用 MemorySaver ──
memory = MemorySaver()
app = graph.compile(checkpointer=memory)

# ── 线程1：执行两次 ──
config_1 = {"configurable": {"thread_id": "thread-1"}}
result = app.invoke({"count": 0}, config_1)      # count = 1
result = app.invoke(None, config_1)               # count = 2（累加！）

# ── 线程2：独立执行 ──
config_2 = {"configurable": {"thread_id": "thread-2"}}
result = app.invoke({"count": 100}, config_2)     # count = 101（独立！）

print(result["count"])  # → 101
```

### 5.4 SqliteSaver 示例

```python
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

# 使用 SQLite 文件持久化
conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)

app = graph.compile(checkpointer=checkpointer)

# 执行后，checkpoints.db 文件会持久保存状态
result = app.invoke({"count": 0}, config_1)
# 即使程序重启，从同一个 thread_id 调用，状态仍在！
```

---

## 六、Thread——独立的执行上下文

### 6.1 什么是 Thread？

> **Thread** 是 LangGraph 中的**独立执行上下文**。每个 Thread 有独立的 State 和 Checkpoint 列表。通常**一个 Thread 对应一次用户会话**。

```
用户A的会话：  thread_id = "user-a-session-1"
    ├── 第1轮对话：State = {..., messages: [...2条]}
    ├── 第2轮对话：State = {..., messages: [...4条]}  ← 基于第1轮继续
    └── ...

用户B的会话：  thread_id = "user-b-session-1"
    ├── 第1轮对话：State = {..., messages: [...2条]}  ← 全新的！
    └── ...
```

> ⚠️ **Thread 对应的是会话（session），不是用户（user）。** 同一个用户的不同会话应该用不同的 thread_id。

### 6.2 查看历史状态

```python
# 遍历某个 thread 的所有 checkpoint 历史
for checkpoint in app.get_state_history(config_1):
    print(f"Checkpoint ID: {checkpoint.config['configurable']['checkpoint_id']}")
    print(f"State: {checkpoint.values}")
    print(f"下一步: {checkpoint.next}")
    print("---")
```

---

## 七、Durable Execution——持久化执行

### 7.1 核心概念

> **Durable Execution** 是 LangGraph 的"超能力"——它能在任务失败后从断点无缝恢复，确保长时间运行的任务永不丢失进度。

```
没有 Durable Execution：
Node A ✅ → Node B ✅ → Node C ✅ → Node D ❌ 崩溃！
                                  ↓
                          全部进度丢失！
                          从头开始 → 😰

有 Durable Execution：
Node A ✅ → 💾 → Node B ✅ → 💾 → Node C ✅ → 💾 → Node D ❌ 崩溃！
                                                    ↓
                                          自动从 Node D 恢复！
                                          前三步结果保留 → 🎉
```

### 7.2 工作原理（伪代码）

```python
def execute_with_durable_execution(graph, config):
    """Durable Execution 的执行流程（伪代码）"""
    
    # Step 1: 从 checkpoint 恢复 State
    state = checkpoint.load(config)
    
    # Step 2: 确定下一个要执行的节点
    next_node = determine_next_node(state)
    
    # Step 3: 执行节点（带上恢复的 State）
    new_state = graph.nodes[next_node](state)
    
    # Step 4: 创建新的 checkpoint 并保存
    checkpoint.save(config, new_state)
    
    # Step 5: 继续执行下一个节点
    # ...循环直到 END
```

### 7.3 适用场景

| 场景 | 说明 |
|------|------|
| **长时间运行任务** | 数小时甚至数天的自动化流程 |
| **数据迁移** | A 数据库数据拷贝到 B 数据库，中间崩溃不需要重来 |
| **Human-in-the-Loop** | 等待人工输入时暂停，输入完成后恢复 |
| **故障恢复** | 任何原因导致的崩溃都能从断点继续 |

---

## 八、实战一——可恢复的数据管道

### 8.1 场景

模拟一个数据处理管道：获取数据 → 分三批处理 → 完成。在第二批处理时**故意触发失败**，验证断点恢复。

### 8.2 State 定义

```python
from typing import TypedDict

class PipelineState(TypedDict):
    total_items: int          # 总数据条数
    processed_items: int      # 已处理条数
    failed_items: int         # 失败条数
    results: list             # 处理结果
```

### 8.3 节点函数

```python
def fetch_data(state: PipelineState) -> dict:
    """获取数据：设置总量"""
    return {"total_items": 100}

def batch1_process(state: PipelineState) -> dict:
    """第一批处理：处理 33 条"""
    return {
        "processed_items": 33,
        "results": ["batch1_result"]
    }

def batch2_process(state: PipelineState) -> dict:
    """第二批处理：模拟失败！"""
    if state.get("processed_items", 0) == 33:
        raise Exception("模拟第二批处理失败！")
    return {
        "processed_items": state["processed_items"] + 33,
        "results": state.get("results", []) + ["batch2_result"]
    }

def batch3_process(state: PipelineState) -> dict:
    """第三批处理：处理剩余"""
    return {
        "processed_items": state["processed_items"] + 34,
        "results": state.get("results", []) + ["batch3_result"]
    }

def finalize(state: PipelineState) -> dict:
    """完成处理"""
    return {
        "results": state.get("results", []) + [f"完成！共处理{state['processed_items']}条"]
    }
```

### 8.4 构建图并测试

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

# ── 构建线性图 ──
graph = StateGraph(PipelineState)
graph.add_node("fetch", fetch_data)
graph.add_node("batch1", batch1_process)
graph.add_node("batch2", batch2_process)
graph.add_node("batch3", batch3_process)
graph.add_node("finalize", finalize)

graph.add_edge(START, "fetch")
graph.add_edge("fetch", "batch1")
graph.add_edge("batch1", "batch2")
graph.add_edge("batch2", "batch3")
graph.add_edge("batch3", "finalize")
graph.add_edge("finalize", END)

# ── 使用 SqliteSaver ──
conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)
app = graph.compile(checkpointer=checkpointer)

# ── 第一次运行 → batch2 会失败 ──
config = {"configurable": {"thread_id": "pipeline-1"}}
try:
    result = app.invoke({}, config)
except Exception as e:
    print(f"失败：{e}")
    print("但 batch1 的进度已保存！")

# ── 修复 batch2 后重新运行 → 从断点继续 ──
# （实际场景中修复代码后重新执行）
result = app.invoke(None, config)
print(f"完成：共处理 {result['processed_items']} 条")
# → 完成：共处理 100 条
```

**运行效果**：

```
第一次运行：
fetch ✅ → batch1 ✅ (processed=33) → batch2 ❌ 崩溃！
    状态已存档：processed_items=33

修复后重新运行：
从 checkpoint 恢复 processed_items=33 → batch2 ✅ → batch3 ✅ → finalize ✅
完成：共处理 100 条
```

---

## 九、记忆管理——短期记忆与长期记忆

### 9.1 两种记忆的区别

```
┌─────────────────────────────────────────────────────────────┐
│              短期记忆 vs 长期记忆                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  短期记忆（Short-term Memory）                                 │
│  ├── 来源：最近 N 条聊天记录                                   │
│  ├── 内容：当前会话的上下文                                     │
│  ├── 生命周期：单次会话内                                       │
│  └── 实现：取 messages[-10:] 作为上下文窗口                    │
│                                                             │
│  长期记忆（Long-term Memory）                                   │
│  ├── 来源：从对话中提取的客观事实                                │
│  ├── 内容：用户名、偏好、习惯、住址...                           │
│  ├── 生命周期：永久 / 长期                                     │
│  └── 实现：LLM 提取 → 持久化存储 → 下次对话作为上下文注入        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 9.2 长期记忆的 State 设计

```python
class MemoryState(TypedDict):
    # ── 短期记忆 ──
    messages: Annotated[list, add_messages]   # 对话记录
    
    # ── 长期记忆 ──
    user_name: str                            # 用户姓名
    user_preferences: dict                    # 用户偏好（语言、风格等）
    facts: list                               # 提取到的客观事实
    # 例: ["用户喜欢喝咖啡", "用户在北京", "用户是程序员"]
```

### 9.3 记忆管理架构

```
用户对话
    ↓
[Chat Node] ← 用长期记忆作为上下文
    ↓
[Extract Node] ← 分析最近2轮对话，提取新事实
    ↓
更新 facts → 持久化存储
    ↓
下次对话时 → facts 注入上下文 → 更懂用户
```

---

## 十、记忆管理策略——重要性评分与时间衰减

### 10.1 为什么需要管理策略？

> 对话越来越多 → 提取的事实越来越多 → 全部放入上下文 → **Token 膨胀，超出模型限制**

需要策略来**筛选最重要的记忆**放入上下文。

### 10.2 策略一：重要性评分

```
流程：
每条记忆 → LLM 评分（0-1） → 按分数排序 → 取 Top-N 放入上下文

示例：
"用户叫张三"            → 重要性 0.9 ← 很重要！
"用户喜欢喝美式咖啡"     → 重要性 0.7
"用户上周去了上海出差"   → 重要性 0.3 ← 不太重要
"用户昨天吃了火锅"      → 重要性 0.1 ← 可以忽略

→ 只取 Top 2 条放入上下文
```

### 10.3 策略二：时间衰减

> 近期的记忆比久远的记忆更重要。使用 **30 天半衰期**计算权重。

```python
import math
from datetime import datetime

def calculate_memory_weight(created_at: datetime, half_life_days: int = 30) -> float:
    """计算记忆的权重（时间衰减）"""
    days_passed = (datetime.now() - created_at).days
    decay_factor = math.exp(-math.log(2) * days_passed / half_life_days)
    return decay_factor

# 示例
memory_1 = {"content": "用户喜欢咖啡", "created_at": datetime(2026, 6, 20)}  # 3天前
memory_2 = {"content": "用户叫张三", "created_at": datetime(2026, 1, 1)}    # 170天前

print(calculate_memory_weight(memory_1["created_at"]))  # → 0.93（高权重）
print(calculate_memory_weight(memory_2["created_at"]))  # → 0.02（近乎忽略）
```

---

## 十一、实战二——有记忆的个人助理

### 11.1 State 定义

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class PersonalAssistantState(TypedDict):
    """个人助理的完整 State"""
    
    # 短期记忆
    messages: Annotated[list, add_messages]
    
    # 长期记忆
    user_name: str                        # 用户名
    user_id: str                          # 用户ID
    facts: list                           # 学到的客观事实
    user_preferences: dict                # 用户偏好
    metadata: dict                        # 元数据
```

### 11.2 图结构

```
              START
                ↓
           [chat] ← 用 facts + preferences 作为上下文
                ↓
          需要提取新信息？
         ┌──────┴──────┐
         ↓              ↓
     [extract]        END
    提取新事实           │
         ↓              │
    更新 facts          │
         ↓              │
         └──────┬──────┘
                ↓
          回到 [chat]（继续对话）
```

### 11.3 Chat Node

```python
def chat_node(state: PersonalAssistantState) -> dict:
    """与用户聊天的节点"""
    
    # ── 短期记忆：取最近 10 条消息 ──
    recent_messages = state["messages"][-10:]
    
    # ── 长期记忆：构建上下文 ──
    facts_context = "\n".join(state.get("facts", []))
    preferences_context = str(state.get("user_preferences", {}))
    
    # ── 构建系统提示词 ──
    system_prompt = f"""你是一个贴心的个人助理。

关于用户的信息：
{facts_context}

用户偏好：
{preferences_context}

请基于以上信息，自然地与用户交流。"""
    
    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        *recent_messages
    ])
    
    return {"messages": [response]}
```

### 11.4 Extract Node

```python
import json

def extract_info_node(state: PersonalAssistantState) -> dict:
    """从最近的对话中提取用户信息"""
    
    # ── 只分析最近的 2 轮对话 ──
    recent_messages = state["messages"][-4:]  # 最近2轮 = 4条消息
    
    system_prompt = """从以下对话中提取关于用户的客观事实。
只提取确定的信息，不确定的不要提取。

以 JSON 格式返回：
{
    "new_facts": ["事实1", "事实2", ...],
    "preferences_update": {"key": "value", ...}
}
如果没有新信息，返回空数组。"""
    
    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        *recent_messages
    ])
    
    try:
        result = json.loads(response.content)
        new_facts = result.get("new_facts", [])
        
        # 合并到已有 facts
        existing_facts = state.get("facts", [])
        updated_facts = list(set(existing_facts + new_facts))
        
        return {"facts": updated_facts}
    except json.JSONDecodeError:
        return {}  # 解析失败，不更新
```

### 11.5 完整图构建

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

graph = StateGraph(PersonalAssistantState)

graph.add_node("chat", chat_node)
graph.add_node("extract", extract_info_node)

graph.add_edge(START, "chat")

# 条件路由：对话后判断是否需要提取信息
def should_extract(state: PersonalAssistantState) -> str:
    """判断是否需要提取新信息"""
    # 如果最近的消息是用户发的，尝试提取
    last_message = state["messages"][-1]
    if hasattr(last_message, 'type') and last_message.type == 'human':
        return "extract"
    return "end"

graph.add_conditional_edges("chat", should_extract, {
    "extract": "extract",
    "end": END
})
graph.add_edge("extract", "chat")  # 提取后回到聊天

# ── 持久化 ──
conn = sqlite3.connect("assistant_memory.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)
app = graph.compile(checkpointer=checkpointer)

# ── 使用 ──
config = {"configurable": {"thread_id": "alice-session-1"}}

# 第1轮
result = app.invoke({
    "messages": [{"role": "user", "content": "你好！我喜欢喝咖啡，尤其是美式咖啡。"}]
}, config)
print(result["messages"][-1].content)

# 第2轮（几天后）
result = app.invoke({
    "messages": [{"role": "user", "content": "嘿，我又回来了！最近工作很忙，需要提神。"}]
}, config)
# → AI 会记住用户喜欢咖啡，回复中可能提到"要不要来杯美式咖啡？"
print(result["messages"][-1].content)
```

**运行效果**：

```
第1轮：
用户: "我喜欢喝咖啡，尤其是美式咖啡。"
    ↓ extract_node 提取事实
facts: ["用户喜欢喝咖啡，尤其是美式咖啡"]
AI: "好的，我记住了！咖啡爱好者，美式是你的最爱。"

第2轮（几天后）：
用户: "嘿，我又回来了！最近工作很忙，需要提神。"
AI: "欢迎回来！工作辛苦了。记得你喜欢美式咖啡，要不要来一杯提提神？☕"
    ↑ AI 记住了用户的偏好！
```

---

## 十二、常见问题与排错指南

### 12.1 错误速查表

| 错误/问题 | 原因 | 解决方法 | 优先级 |
|-----------|------|----------|:------:|
| Checkpoint 不生效 | 编译时没传 checkpointer | `graph.compile(checkpointer=MemorySaver())` | 🔴高 |
| 两个 Thread 状态串了 | thread_id 相同 | 确保不同会话用不同的 thread_id | 🔴高 |
| SQLite 文件没有生成 | 路径问题或权限问题 | 检查路径，确保有写入权限 | 🟡中 |
| Reducer 行为不符合预期 | 没使用 Annotated | `total: Annotated[int, add]` | 🟡中 |
| 长期记忆不更新 | extract_node 没被触发 | 检查条件路由是否正确 | 🟡中 |
| 上下文 Token 超限 | 记忆太多 | 使用重要性评分 + Top-N 筛选 | 🟢低 |

### 12.2 排查流程

```
断点恢复不工作？
    ↓
第一步：确认 checkpointer 已传入
    graph.compile(checkpointer=...) ← 有这个吗？
    ↓ 有
第二步：确认 thread_id 一致
    第一次 invoke 和恢复时的 thread_id 相同吗？
    ↓ 相同
第三步：查看 checkpoint 历史
    for cp in app.get_state_history(config):
        print(cp.values)  → 看状态是否正确存档
    ↓
第四步：确认 State 类型与 Checkpoint 兼容
    所有字段都可以被序列化吗？
```

---

## 十三、课程小结

### 13.1 本课核心知识图谱

```
┌────────────────────────────────────────────────────────────┐
│          可记忆、可恢复智能体核心知识体系                       │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  State 设计四大原则                                     │
│      ├── 最小化：只存储必要数据，去冗余                       │
│      ├── 清晰命名：见名知意                                 │
│      ├── 类型安全：Annotated + Literal + Optional           │
│      └── 分层设计：结构化嵌套                                │
│                                                            │
│  2️⃣  Reducer 更新机制                                       │
│      ├── 默认：直接替换                                      │
│      ├── add：累加（适合计数、Token）                        │
│      ├── add_messages：消息追加（去重+保序）                  │
│      └── 自定义：合并去重 / 字典合并                         │
│                                                            │
│  3️⃣  Checkpoint 持久化                                      │
│      ├── MemorySaver：内存，开发测试用                       │
│      ├── SqliteSaver：本地文件，持久化                       │
│      ├── PostgresSaver：向量数据库，生产环境                  │
│      └── Thread：独立执行上下文，一个会话一个 thread_id       │
│                                                            │
│  4️⃣  Durable Execution                                     │
│      存档 → 执行 → 崩溃 → 恢复 → 从断点继续 ✅               │
│      永远不会丢失进度                                        │
│                                                            │
│  5️⃣  记忆管理                                               │
│      ├── 短期记忆：最近 N 条消息作为上下文窗口                │
│      ├── 长期记忆：提取 + 存储 + 注入                        │
│      ├── 重要性评分：LLM 打分 → Top-N 筛选                   │
│      └── 时间衰减：30天半衰期，近期优先                      │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 13.2 一句话总结

> **LangGraph 通过 Checkpoint + Reducer + Memory 实现了可记忆、可恢复的智能体。** State 设计遵循四原则，Reducer 控制更新方式，Checkpoint 实现断点续传，长期记忆通过 LLM 提取 + 重要性评分 + 时间衰减来高效管理。

### 13.3 速记卡

```
┌───────────────────────────────────────────────────────────┐
│           可记忆可恢复智能体速记卡                            │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  State 设计：最小化 / 清晰命名 / 类型安全 / 分层             │
│                                                           │
│  Reducer：                                                │
│  total: Annotated[int, add]            ← 累加              │
│  messages: Annotated[list, add_messages] ← 消息追加        │
│                                                           │
│  Checkpoint：                                             │
│  checkpointer = SqliteSaver(conn)                         │
│  app = graph.compile(checkpointer=checkpointer)           │
│  config = {"configurable": {"thread_id": "xxx"}}          │
│                                                           │
│  记忆管理：                                                │
│  └── 重要性评分(LLM打分→Top-N) + 时间衰减(30天半衰期)       │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### 13.4 系列课程定位

```
LangGraph 系列（6课）：
├── 00 开篇：框架定位与课程体系
├── 01 入门和组件：State / Node / Edge + 条件分支
├── 02 可记忆可恢复智能体（本课）🆕
├── 03 流式输出、中断与时间旅行（待续）
├── 04 外部工具集成与 API 调用
├── 05 多智能体构建
└── 06 生产部署上线
```

---

*本教学文档基于 LangGraph 系列课程第二讲视频整理编写。*  
*本文档涵盖 State 设计四大原则、Reducer 更新机制、Checkpoint 持久化（Memory/SQLite）、Thread 执行上下文、Durable Execution 故障恢复、长期记忆管理及两个完整实战案例。*
