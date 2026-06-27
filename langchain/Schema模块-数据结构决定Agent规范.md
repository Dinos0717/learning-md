# Schema 模块——数据结构决定 Agent 规范

> 基于陈泽鹏老师视频课程整理编写 · 2026年6月25日

---

## 目录

- [一、本节概述与学习目标](#一本节概述与学习目标)
- [二、为什么要定义 Agent 的输出格式](#二为什么要定义-agent-的输出格式)
- [三、系统中的三种 Agent 及其 Schema](#三系统中的三种-agent-及其-schema)
- [四、Router Schema——意图识别的数据结构](#四router-schema意图识别的数据结构)
- [五、Meeting Schema——会议纪要的数据结构](#五meeting-schema会议纪要的数据结构)
- [六、Chat Schema——HTTP 对话的数据结构](#六chat-schemahttp-对话的数据结构)
- [七、Pydantic 字段约束速查](#七pydantic-字段约束速查)
- [八、结构化输出实战——LLM 如何按 Schema 回复](#八结构化输出实战llm-如何按-schema-回复)
- [九、Schema 的测试方法](#九schema-的测试方法)
- [十、常见问题与排错指南](#十常见问题与排错指南)
- [十一、课后练习](#十一课后练习)
- [十二、本节小结](#十二本节小结)

---

## 一、本节概述与学习目标

### 1.1 本节定位

> 这是「多 Agent 开发实战」系列的**Schema 模块课**。在前面课程中我们已经讲完了 Core 模块（配置管理和大模型驱动），现在往上走一层——**Schema 层**。这一层负责定义 Agent 之间交互的数据结构规范，是整个系统「通信协议」的制定者。

```
┌─────────────────────────────────────────┐
│           本系列课程体系                   │
├─────────────────────────────────────────┤
│                                         │
│  开篇：课程总览                           │
│  第1课：为什么学 + 范式转变                │
│  第2课：架构总览                          │
│  第3课：Core 模块精讲                     │
│  第4课（本节）：Schema 模块  ← 你在这里     │
│  后续课程：Memory → Agent → Service       │
│                                         │
│  Schema 是 Agent 之间的"通信协议"          │
│                                         │
└─────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────────┐
│                    架构层级（从下往上）                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  入口层 (run_agent.py / run_service.py)                      │
│      ↑ 依赖                                                  │
│  Agent 层 (router / chat / meeting)                          │
│      ↑ 依赖                                                  │
│  Memory 层 (记忆管理 + Session)                               │
│      ↑ 依赖                                                  │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Schemas 层（本课）  ← Agent 之间的通信协议         │       │
│  │  • router_schema.py：路由数据结构                  │       │
│  │  • meeting_schema.py：会议纪要数据结构              │       │
│  │  • chat_schema.py：对话请求/响应数据结构            │       │
│  │                                                  │       │
│  │  依赖：几乎为 0（只依赖 pydantic）                  │       │
│  │  → 纯数据结构，独立可测                             │       │
│  └──────────────────────────────────────────────────┘       │
│      ↑ 依赖                                                  │
│  Core 层 (config.py + llm_driver.py)                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 本课要掌握的目标

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  目标一：理解为什么要定义 Agent 的输出结构                 │
│         ├── 大模型回复的"啰嗦"问题                       │
│         ├── 下游处理只需要关键字段                        │
│         └── 数据合法性校验的必要性                        │
│                                                         │
│  目标二：掌握系统中三种 Agent 的 Schema 设计               │
│         ├── Router Schema：意图识别（Intent 枚举）       │
│         ├── Meeting Schema：会议纪要结构化                │
│         └── Chat Schema：HTTP 请求/响应格式              │
│                                                         │
│  目标三：掌握 Pydantic BaseModel 的字段约束语法            │
│         ├── 必填字段（...）vs 可选字段（default）         │
│         ├── 数值范围约束（ge / le）                      │
│         └── 字符串长度约束（min_length / max_length）    │
│                                                         │
│  目标四：掌握 structured_output 的使用方法                │
│         ├── llm.with_structured_output(Schema)           │
│         └── 大模型如何自动填充结构化字段                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 二、为什么要定义 Agent 的输出格式

### 2.1 大模型回复的特点

用过 ChatGPT 或其他大语言模型的人都有这个感受：大模型的回复**很像人在聊天**——它会把前因后果都说清楚，内容很长，有些信息并不是你当前最需要的。

```
┌─────────────────────────────────────────────────────────┐
│              大模型回复的典型特征                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  😅 回复很长 —— 像人在聊天，铺垫多                       │
│  😅 重点不突出 —— 关键信息淹没在大段文字中               │
│  😅 格式不统一 —— 每次回复的结构可能不一样               │
│  😅 包含冗余信息 —— "好的，我来帮您分析一下..." 这类     │
│                                                         │
│  这对人类阅读来说没问题，但对程序处理来说是灾难！          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Agent 系统的核心场景：大模型是流水线的一个环节

在 Agent 系统中，大模型的输出**不是终点**，而是处理流程中的**一个中间环节**。它的输出要被下游模块继续消费：

```
用户输入 "帮我整理一下上周的项目会议记录"
    │
    ▼
┌──────────────┐
│  路由 Agent   │  ← 判断这是什么意图
└──────┬───────┘
       │ 输出：{"intent": "meeting_notes", "confidence": 0.95}
       ▼
┌──────────────┐
│ 会议纪要Agent │  ← 提取会议关键信息
└──────┬───────┘
       │ 输出：{"title": "...", "date": "...", "attendees": [...], ...}
       ▼
┌──────────────┐
│  存储/展示层  │  ← 存入数据库，或渲染成 Markdown
└──────────────┘
```

> ⚠️ **关键洞察**：如果每个 Agent 输出的都是一大段自然语言文本，下游模块就不得不自己做"阅读理解"来提取关键字段。这不仅浪费 token，还容易出错。

### 2.3 Before / After：有没有 Schema 的区别

**❌ 没有 Schema 时：**

```python
# 路由 Agent 的原始回复（一大段文本）
response = """
根据用户的问题分析，我认为这次对话的意图应该是会议纪要相关的。
用户提到了"整理会议记录"这样的关键词，结合上下文来看，
置信度大约在95%左右。我的推理过程是：首先识别了关键词"会议"，
然后判断用户想要的是结构化的会议纪要输出...
"""

# 下游代码要自己从这段文字里提取意图 —— 非常脆弱！
if "会议" in response:
    intent = "meeting_notes"
elif "聊天" in response or "对话" in response:
    intent = "chat"
# 这种方式极其不可靠！
```

**✅ 有 Schema 时：**

```python
# 路由 Agent 的结构化回复（精确定义）
class RouterResponse(BaseModel):
    intent: Intent          # chat | meeting_notes | unknown
    confidence: float       # 0.0 ~ 1.0
    reasoning: str = ""     # 推理过程（可选）

# 下游代码直接访问字段 —— 精确、高效！
if response.intent == Intent.MEETING_NOTES:
    call_meeting_agent()
elif response.intent == Intent.CHAT:
    call_chat_agent()
```

```
┌─────────────────────────────────────────────────────────┐
│           Schema 带来的四大收益                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1️⃣  精准提取 —— 只取需要的字段，不浪费 token            │
│                                                         │
│  2️⃣  数据校验 —— 必填字段自动检查，不合规的数据直接拒绝    │
│                                                         │
│  3️⃣  类型安全 —— 字段有明确类型，IDE 有自动补全           │
│                                                         │
│  4️⃣  格式一致 —— 每次输出结构统一，下游处理逻辑稳定        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.4 重要澄清：Schema ≠ 项目中所有的数据结构

> ⚠️ **关键概念**：Schema 模块定义的格式，**仅仅是 Agent 之间交互的数据结构**，不是你项目代码框架中所有的数据结构。比如你的数据库模型、内部配置类这些，不放在 Schema 模块中。

```
Schema 模块的范围：
├── ✅ Agent 的输入输出格式（如路由结果、会议纪要结构）
├── ✅ Agent 之间的通信协议（如 HTTP 请求/响应格式）
├── ❌ 数据库 ORM 模型
├── ❌ 内部配置数据结构
└── ❌ 工具函数的参数/返回值类型
```

---

## 三、系统中的三种 Agent 及其 Schema

### 3.1 三种 Agent 概览

在我们的系统中，一共有三种 Agent，每种对应一个 Schema 文件：

```
SRC/schemas/
├── router_schema.py    ← 路由 Agent 的数据结构
├── meeting_schema.py   ← 会议纪要 Agent 的数据结构
└── chat_schema.py      ← 对话 Agent 的请求/响应结构
```

| Agent 类型 | Schema 文件 | 核心职责 | 关键输出字段 |
|---|---|---|---|
| **路由 Agent** | `router_schema.py` | 意图识别：判断用户问题该分给哪个子 Agent | `intent`（枚举）、`confidence`（置信度） |
| **会议纪要 Agent** | `meeting_schema.py` | 从对话中提取结构化的会议纪要 | `title`、`date`、`attendees`、`content`、`actions` |
| **对话 Agent** | `chat_schema.py` | 处理 HTTP API 的请求和响应 | `message`（请求）、`response`（响应）、`session_id` |

```
用户的输入
    │
    ▼
┌─────────────────────────────────────┐
│          路由 Agent (Router)         │
│  职责：意图识别                       │
│  输出：Intent 枚举 + 置信度           │
│  Schema：router_schema.py            │
└──────────┬──────────────┬───────────┘
           │              │
    intent=chat     intent=meeting_notes
           │              │
           ▼              ▼
┌──────────────────┐  ┌──────────────────────┐
│  对话 Agent       │  │  会议纪要 Agent       │
│  职责：自由对话    │  │  职责：结构化会议记录  │
│  Schema:          │  │  Schema:             │
│  chat_schema.py   │  │  meeting_schema.py   │
└──────────────────┘  └──────────────────────┘
```

### 3.2 三种 Agent 的定位差异

| 维度 | 路由 Agent | 会议纪要 Agent | 对话 Agent |
|---|---|---|---|
| **是否需要记忆** | ❌ 不需要 | ❌ 不需要（单次调用） | ✅ 需要（多轮对话） |
| **输出结构复杂度** | 简单（3个字段） | 复杂（7+ 字段 + 嵌套模型） | 中等（请求+响应） |
| **核心设计挑战** | 意图枚举的穷举性 | 必选/可选字段的取舍 | 请求长度校验 |
| **依赖外部** | 子 Agent 列表 | 无 | Session 管理 |

---

## 四、Router Schema——意图识别的数据结构

### 4.1 路由 Agent 的核心任务

路由 Agent 只有一件事要做：**意图识别**。它接收用户的一句话，判断该把这句话分给哪个子 Agent 来处理。

```
"今天天气怎么样？"
        │
        ▼
┌──────────────────┐
│   路由 Agent      │
│   意图识别        │
└──────┬───────────┘
       │
       ├── chat（闲聊类问题）
       ├── meeting_notes（会议纪要类问题）
       └── unknown（无法识别）
```

> ⚠️ **设计原则**：意图的取值不是无限的，而是由你的**子 Agent 数量**决定的。你有几个子 Agent，意图的可选值就有几个（再加上一个 `unknown` 兜底）。

### 4.2 Intent 枚举定义

```python
# ── router_schema.py ──

from enum import Enum
from pydantic import BaseModel, Field


class Intent(str, Enum):
    """
    意图枚举：定义路由 Agent 所有可能的识别结果
    
    设计原则：
    - 意图的数量 = 子 Agent 的数量 + 1（unknown 兜底）
    - 当前系统有 2 个子 Agent，所以 Intent 有 3 个值
    - 如果后续加了新 Agent，在这里新增一个枚举值即可
    """
    CHAT = "chat"                    # 闲聊/对话类
    MEETING_NOTES = "meeting_notes"  # 会议纪要类
    UNKNOWN = "unknown"              # 无法识别（兜底）
```

**Intent 枚举的设计原则详解：**

```
┌─────────────────────────────────────────────────────────┐
│              Intent 枚举设计三原则                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1️⃣  穷举性：每个子 Agent 对应一个枚举值                  │
│     ├── chat → 对话 Agent                                │
│     └── meeting_notes → 会议纪要 Agent                   │
│                                                         │
│  2️⃣  兜底机制：unknown 处理所有无法识别的情况              │
│     └── 确保系统不会因为未知意图而崩溃                     │
│                                                         │
│  3️⃣  可扩展性：加新 Agent 时只需新增枚举值                 │
│     └── 例如加一个 summary Agent → 加 SUMMARY = "summary" │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 4.3 RouterResponse 完整定义

```python
# ── router_schema.py（续） ──

class RouterResponse(BaseModel):
    """
    路由 Agent 的结构化输出
    
    这是路由 Agent 回复时必须遵循的数据格式。
    大模型会按照这个结构填充各个字段的值。
    """
    
    intent: Intent = Field(
        default=...,
        description="识别出的用户意图，用于决定调用哪个子 Agent"
    )
    # ... = 必填字段！没有默认值，大模型必须给出一个意图
    
    confidence: float = Field(
        default=...,
        ge=0.0,
        le=1.0,
        description="意图识别的置信度，取值范围 0.0 ~ 1.0"
    )
    # ge=0.0, le=1.0 约束了数值范围，超出范围会校验失败
    
    reasoning: str = Field(
        default="",
        description="推理过程：大模型是如何得出结论的，用于调试和可解释性"
    )
    # default="" 表示这是可选字段，不填也不会报错
```

### 4.4 字段详解

| 字段 | 类型 | 必填 | 约束 | 说明 |
|---|---|---|---|---|
| `intent` | `Intent`（枚举） | ✅ 必填 | 只能是 `chat` / `meeting_notes` / `unknown` | 核心字段。路由 Agent 存在的意义就是输出这个值 |
| `confidence` | `float` | ✅ 必填 | `0.0 ≤ value ≤ 1.0` | 这次意图识别的把握有多大。例如识别为 `chat` 的置信度是 0.92 |
| `reasoning` | `str` | ❌ 可选 | 无 | 大模型的推理过程记录。比如"识别到关键词'会议'，判断为 meeting_notes 意图"。可用于调试和审计 |

### 4.5 RouterResponse 使用示例

```python
# ── 使用示例 ──

# 创建一个路由结果：识别为"会议纪要"意图，置信度 0.95
result = RouterResponse(
    intent=Intent.MEETING_NOTES,
    confidence=0.95,
    reasoning="用户输入中包含'整理会议记录'、'项目周会'等关键词"
)

# 下游代码直接使用字段
if result.intent == Intent.MEETING_NOTES:
    print(f"✅ 意图：会议纪要（置信度：{result.confidence:.0%}）")
    # 调用会议纪要 Agent
    meeting_agent.invoke(user_input)

# 查看推理过程（调试用）
print(f"推理过程：{result.reasoning}")
```

**输出效果：**

```
✅ 意图：会议纪要（置信度：95%）
推理过程：用户输入中包含'整理会议记录'、'项目周会'等关键词
```

---

## 五、Meeting Schema——会议纪要的数据结构

### 5.1 会议纪要 Agent 的核心任务

会议纪要 Agent 负责从对话内容中**提取结构化的会议信息**。和路由 Agent 不同，它的输出字段更多、结构更复杂，因为一次会议包含的信息维度很多。

```
原始对话内容（可能是几十分钟的会议记录）
        │
        ▼
┌──────────────────────┐
│  会议纪要 Agent       │
│  提取关键信息        │
└──────┬───────────────┘
       │
       ▼
结构化会议纪要（MeetingSummary 对象）
├── title: "Q3产品规划讨论会"
├── date: "2026-06-25"
├── attendees: ["张三", "李四", "王五"]
├── content: "本次会议主要讨论了Q3的产品路线图..."
├── resolutions: ["确定Q3上线3个新功能", "组建专项技术攻坚组"]
├── actions: [
│     MeetingAction(description="调研竞品功能", person="张三", deadline="2026-07-10"),
│     MeetingAction(description="完成技术方案", person="李四", deadline="2026-07-05")
│   ]
└── notes: "下次会议定于7月15日"
```

### 5.2 必选字段 vs 可选字段的设计思路

在设计会议纪要的 Schema 时，需要做一个关键决策：**哪些字段是必选的，哪些是可选的？**

```
┌─────────────────────────────────────────────────────────┐
│          会议纪要字段的"必选/可选"决策逻辑                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  必选字段（每场会议一定有）：                              │
│  ├── title       → 会议总得有个主题吧？                   │
│  ├── date        → 会议总有个日期吧？                     │
│  ├── attendees   → 总得知道谁参加了吧？                   │
│  └── content     → 会议总得谈了些什么吧？                 │
│                                                         │
│  可选字段（不一定每场会议都有）：                          │
│  ├── resolutions → 有些会是纯讨论，不产生决议             │
│  ├── actions     → 有些会可能没有明确的行动项             │
│  └── notes       → 额外的备注，有就填，没有不强求         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 5.3 MeetingAction 子模型

会议中的**行动项**（谁要做什么、什么时候完成）本身也有结构，所以我们先定义一个子模型：

```python
# ── meeting_schema.py ──

from typing import Optional, List
from pydantic import BaseModel, Field


class MeetingAction(BaseModel):
    """
    会议行动项
    
    当会议确定了后续要执行的任务时，每个任务就是一个 MeetingAction。
    这是一个嵌套的子模型，被 MeetingSummary 引用。
    """
    
    description: str = Field(
        default=...,
        description="行动描述：具体要做什么"
    )
    # 必填 —— 一个行动项至少要知道"做什么"
    
    responsible_person: str = Field(
        default=...,
        description="负责人：这个行动由谁来执行"
    )
    # 必填 —— 没人负责的行动等于没安排
    
    deadline: Optional[str] = Field(
        default=None,
        description="截止日期：什么时候要完成（可选，不是每个任务都有硬性截止）"
    )
    # 可选 —— 有些任务可能没有明确的截止日期
```

> 💡 **设计思路**：只要是"行动"，就一定有"做什么"和"谁来做"这两个维度，所以 `description` 和 `responsible_person` 是必填的。而截止日期不一定每个任务都有，所以用 `Optional` 标记为可选。

### 5.4 MeetingSummary 完整定义

```python
# ── meeting_schema.py（续） ──

class MeetingSummary(BaseModel):
    """
    会议纪要的完整数据结构
    
    这是会议纪要 Agent 输出的标准格式。
    大模型会把对话内容按照这个结构提取并填充。
    """
    
    # ═══ 必选字段 ═══
    title: str = Field(
        default=...,
        description="会议标题/主题"
    )
    
    date: str = Field(
        default=...,
        description="会议日期"
    )
    
    attendees: List[str] = Field(
        default=...,
        description="参会人员列表"
    )
    
    content: str = Field(
        default=...,
        description="会议内容摘要：本次会议主要讨论了什么"
    )
    
    # ═══ 可选字段 ═══
    resolutions: Optional[List[str]] = Field(
        default=None,
        description="会议决议列表（可选，不是每次会议都有正式决议）"
    )
    
    actions: Optional[List[MeetingAction]] = Field(
        default=None,
        description="会议行动项列表（可选，嵌套 MeetingAction 模型）"
    )
    
    notes: Optional[str] = Field(
        default=None,
        description="备注信息（可选）"
    )
```

### 5.5 to_markdown() 方法——从结构化到可读

有了结构化的字段之后，我们还需要把它**呈现出来**。`to_markdown()` 方法就是把结构化数据转换成人类可读的 Markdown 格式：

```python
    # ── meeting_schema.py ── MeetingSummary 类内部的方法 ──
    
    def to_markdown(self) -> str:
        """
        将结构化的会议纪要按照 Markdown 格式排版输出
        
        格式层级设计：
        - # 一级标题：会议标题
        - ## 二级标题：日期、参会人员、摘要、决议、行动项、备注
        - 行动项内部使用表格展示
        """
        lines = []
        
        # 一级标题：会议主题
        lines.append(f"# {self.title}")
        lines.append("")
        
        # 日期
        lines.append(f"## 日期")
        lines.append(f"{self.date}")
        lines.append("")
        
        # 参会人员
        lines.append(f"## 参会人员")
        lines.append("、".join(self.attendees))
        lines.append("")
        
        # 会议摘要
        lines.append(f"## 摘要")
        lines.append(f"{self.content}")
        lines.append("")
        
        # 会议决议（如果有）
        if self.resolutions:
            lines.append(f"## 决议")
            for i, r in enumerate(self.resolutions, 1):
                lines.append(f"{i}. {r}")
            lines.append("")
        
        # 行动项（如果有）—— 用表格展示
        if self.actions:
            lines.append(f"## 行动项")
            lines.append("| 序号 | 行动描述 | 负责人 | 截止日期 |")
            lines.append("|------|---------|--------|---------|")
            for i, action in enumerate(self.actions, 1):
                deadline = action.deadline or "待定"
                lines.append(f"| {i} | {action.description} | {action.responsible_person} | {deadline} |")
            lines.append("")
        
        # 备注（如果有）
        if self.notes:
            lines.append(f"## 备注")
            lines.append(f"{self.notes}")
            lines.append("")
        
        return "\n".join(lines)
```

#### to_markdown() 输出效果演示

假设我们用以下数据填充了 `MeetingSummary`：

```python
summary = MeetingSummary(
    title="Q3产品规划讨论会",
    date="2026-06-25",
    attendees=["张三", "李四", "王五", "赵六"],
    content="本次会议主要讨论了Q3的产品路线图，确定了三个重点功能方向。"
            "团队一致认为应该在用户体验方面投入更多资源。",
    resolutions=[
        "确定Q3上线3个新功能：智能搜索、批量操作、数据导出",
        "组建专项技术攻坚组，由李四担任组长"
    ],
    actions=[
        MeetingAction(
            description="完成智能搜索的技术方案设计",
            responsible_person="李四",
            deadline="2026-07-05"
        ),
        MeetingAction(
            description="调研竞品的数据导出功能",
            responsible_person="张三",
            deadline="2026-07-10"
        ),
        MeetingAction(
            description="准备Q3产品规划的材料",
            responsible_person="王五",
            deadline=None  # 没有明确截止日期
        )
    ],
    notes="下次会议暂定7月15日，具体时间待确认。"
)

print(summary.to_markdown())
```

**实际输出：**

```markdown
# Q3产品规划讨论会

## 日期
2026-06-25

## 参会人员
张三、李四、王五、赵六

## 摘要
本次会议主要讨论了Q3的产品路线图，确定了三个重点功能方向。团队一致认为应该在用户体验方面投入更多资源。

## 决议
1. 确定Q3上线3个新功能：智能搜索、批量操作、数据导出
2. 组建专项技术攻坚组，由李四担任组长

## 行动项
| 序号 | 行动描述 | 负责人 | 截止日期 |
|------|---------|--------|---------|
| 1 | 完成智能搜索的技术方案设计 | 李四 | 2026-07-05 |
| 2 | 调研竞品的数据导出功能 | 张三 | 2026-07-10 |
| 3 | 准备Q3产品规划的材料 | 王五 | 待定 |

## 备注
下次会议暂定7月15日，具体时间待确认。
```

> 💡 **设计灵感**：`to_markdown()` 的格式完全由你决定。你可以改成 JSON 格式、纯文本、HTML 甚至 PDF——取决于你的下游需要什么。核心思想是**数据归数据，呈现归呈现**，两者分离。

### 5.6 MeetingSummary 字段一览

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `title` | `str` | ✅ | 会议标题/主题 |
| `date` | `str` | ✅ | 会议日期 |
| `attendees` | `List[str]` | ✅ | 参会人员列表 |
| `content` | `str` | ✅ | 会议内容摘要 |
| `resolutions` | `Optional[List[str]]` | ❌ | 会议决议列表 |
| `actions` | `Optional[List[MeetingAction]]` | ❌ | 行动项列表（嵌套子模型） |
| `notes` | `Optional[str]` | ❌ | 额外备注 |

---

## 六、Chat Schema——HTTP 对话的数据结构

### 6.1 对话 Agent 的定位

对话 Agent 处理的是**通过 HTTP API 进行的自由对话**。和前面两个 Agent 不同，它需要考虑**请求和响应**两个方向的数据格式。

```
客户端（浏览器 / 移动端）
    │  POST /chat
    │  Body: {"message": "帮我写一首诗", "session_id": "abc123"}
    ▼
┌──────────────────┐
│  对话 Agent       │
│  处理用户消息     │
└──────┬───────────┘
       │ Response: {"response": "春风拂面万物新...", "session_id": "abc123", "intent": "chat"}
       ▼
客户端收到 AI 的回复
```

### 6.2 ChatRequest——请求格式

```python
# ── chat_schema.py ──

from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    HTTP 对话请求的数据结构
    
    用户在客户端发送消息时，需要遵循这个格式。
    """
    
    message: str = Field(
        default=...,
        min_length=1,
        max_length=8000,
        description="用户发送的消息内容。最短1个字符（不能为空），最长8000个字符"
    )
    # 必填 + 长度限制：既不能为空，也不能无限制地长
    
    session_id: Optional[str] = Field(
        default=None,
        description="会话ID，用于标识同一个对话窗口。"
                    "如果上游不传，系统会自动生成一个新的 session_id"
    )
    # 可选字段 —— 第一次请求可以不传，系统会自动生成
```

#### 请求字段的校验逻辑

```
用户发送请求
    │
    ├── message 为空？
    │   └── ❌ 校验失败："message 至少需要 1 个字符"
    │
    ├── message 超过 8000 字符？
    │   └── ❌ 校验失败："message 不能超过 8000 字符"
    │       → 设计师意图：长文章可以做结构化的提取预处理，不必全量传给 Agent
    │
    ├── session_id 为空（None）？
    │   └── ✅ 通过，系统自动生成一个新的 session_id 并返回给客户端
    │       → 客户端后续请求带上这个 session_id，就能维持同一对话窗口
    │
    └── 一切正常 → ✅ 进入 Agent 处理
```

### 6.3 ChatResponse——响应格式

```python
# ── chat_schema.py（续） ──

class ChatResponse(BaseModel):
    """
    HTTP 对话响应的数据结构
    
    Agent 处理完用户消息后，按照这个格式返回给客户端。
    """
    
    response: str = Field(
        default=...,
        description="AI 的回复内容。这是 Agent 对用户消息的主要回应"
    )
    # 必填 —— 没有回复内容的响应没有意义
    
    session_id: Optional[str] = Field(
        default=None,
        description="会话ID。返回给客户端，客户端后续请求可以带上它来保持对话连续性"
    )
    
    intent: Optional[str] = Field(
        default=None,
        description="意图识别结果。路由 Agent 识别出的意图会透传到这里，"
                    "方便客户端了解这次对话被归类为什么类型"
    )
```

#### 响应字段说明

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `response` | `str` | ✅ | AI 的回复内容，核心字段 |
| `session_id` | `Optional[str]` | ❌ | 会话窗口标识，用于多轮对话的连续性 |
| `intent` | `Optional[str]` | ❌ | 意图透传，让客户端知道这次对话被归为什么类型 |

### 6.4 Session ID 的流转机制

```
第一次请求（客户端不知道 session_id）：
┌──────────────────────────────────────────────────────────┐
│  客户端 → 服务器：                                        │
│  {"message": "你好", "session_id": null}                  │
│                                                          │
│  服务器处理：                                             │
│  session_id 为 null → 系统自动生成 uuid                   │
│  例如：session_id = "a1b2c3d4-..."                       │
│                                                          │
│  服务器 → 客户端：                                        │
│  {"response": "你好！有什么可以帮你？",                     │
│   "session_id": "a1b2c3d4-...",                          │
│   "intent": "chat"}                                      │
└──────────────────────────────────────────────────────────┘

第二次请求（客户端带上 session_id）：
┌──────────────────────────────────────────────────────────┐
│  客户端 → 服务器：                                        │
│  {"message": "刚才说到哪了？",                             │
│   "session_id": "a1b2c3d4-..."}                          │
│                                                          │
│  服务器处理：                                             │
│  session_id 匹配！→ 加载之前的对话历史 → 上下文连贯        │
│                                                          │
│  服务器 → 客户端：                                        │
│  {"response": "我们刚才在聊...",                           │
│   "session_id": "a1b2c3d4-...",                          │
│   "intent": "chat"}                                      │
└──────────────────────────────────────────────────────────┘
```

> ⚠️ **关键设计**：`session_id` 是由**上游控制**的——如果上游想维持同一个会话窗口，就传同一个 `session_id`；如果上游想开启一个新窗口，就不传（或传一个新的）。这个灵活性是 HTTP API 设计中很重要的一点。

---

## 七、Pydantic 字段约束速查

### 7.1 约束语法速查表

所有 Schema 类都继承自 Pydantic 的 `BaseModel`。以下是本项目中用到的所有约束语法：

| 语法 | 含义 | 示例 |
|---|---|---|
| `...`（Ellipsis） | **必填字段** | `name: str = Field(default=...)` |
| `default=值` | **可选字段**，给定默认值 | `notes: str = Field(default="")` |
| `description="..."` | 字段说明（给大模型看的提示） | `Field(description="用户意图")` |
| `ge=值` | 数值的**最小值**（≥） | `Field(ge=0.0)` — 不能小于 0 |
| `le=值` | 数值的**最大值**（≤） | `Field(le=1.0)` — 不能大于 1 |
| `min_length=值` | 字符串的**最小长度** | `Field(min_length=1)` — 不能为空 |
| `max_length=值` | 字符串的**最大长度** | `Field(max_length=8000)` — 不能超过 8000 字符 |

### 7.2 必填 vs 可选：`...` 和 `default` 的本质区别

```python
from pydantic import BaseModel, Field

class Example(BaseModel):
    # ✅ 必填字段：用 ... (Ellipsis) 表示
    required_field: str = Field(default=...)
    
    # ✅ 可选字段：用 default=值 表示
    optional_field: str = Field(default="这是默认值")
    
    # ✅ 可选字段：也可以用 Optional 类型标注
    maybe_field: Optional[str] = Field(default=None)

# 使用效果
# 必填字段缺失 → 抛出 ValidationError
Example()  
# ❌ pydantic.error_wrappers.ValidationError: 
#    field "required_field" is required

# 可选字段不填 → 使用默认值
obj = Example(required_field="hello")
print(obj.optional_field)  # "这是默认值"
print(obj.maybe_field)     # None
```

### 7.3 约束的组合使用

```python
class ValidatedExample(BaseModel):
    """
    展示各种约束的组合使用
    """
    
    # 数值约束：范围 + 必填
    score: float = Field(
        default=...,
        ge=0.0,       # 不能低于 0
        le=100.0,     # 不能超过 100
        description="评分，取值范围 0~100"
    )
    
    # 字符串约束：长度范围 + 可选
    username: str = Field(
        default="匿名用户",
        min_length=1,    # 至少 1 个字符
        max_length=50,   # 最多 50 个字符
        description="用户名"
    )
    
    # 只约束最小值（不约束最大值）
    positive_number: int = Field(
        default=...,
        ge=1,
        description="正整数"
    )
    
    # 只约束最大值
    percentage: float = Field(
        default=...,
        le=100.0,
        description="百分比"
    )
```

---

## 八、结构化输出实战——LLM 如何按 Schema 回复

### 8.1 核心方法：`with_structured_output()`

这是整个 Schema 模块最关键的用法。一行代码就能让大模型**按照你定义的数据结构来回复**：

```python
# ── 不使用结构化输出（传统方式） ──
from src.core.llm_driver import get_llm

llm = get_llm()
response = llm.invoke("用户说：帮我整理一下上周的会议记录")

# response 是一个普通的字符串，例如：
# "好的，根据您的描述，这次会议的意图是整理会议纪要，
#  主题是关于上周的项目进展讨论，参会人员有张三、李四、王五。
#  会议主要内容包括..."
# → 你需要自己用正则或其他手段去解析这段文字！


# ── 使用结构化输出（Schema 方式） ──
from src.core.llm_driver import get_llm
from src.schemas.meeting_schema import MeetingSummary

llm = get_llm()
structured_llm = llm.with_structured_output(MeetingSummary)

# invoke 的返回值直接就是 MeetingSummary 对象！
summary: MeetingSummary = structured_llm.invoke(
    "帮我整理：上周五张三、李四、王五开了项目进展讨论会，"
    "讨论了Q3的需求排期，决定下周先做用户调研..."
)

# 直接访问结构化字段！
print(summary.title)        # "项目进展讨论会"
print(summary.date)         # "上周五"
print(summary.attendees)    # ["张三", "李四", "王五"]
print(summary.to_markdown())  # 直接生成 Markdown 格式
```

### 8.2 工作原理解析

```
┌─────────────────────────────────────────────────────────┐
│          with_structured_output 的工作原理               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1️⃣  你把 Schema 类传给 llm.with_structured_output()     │
│      └── Pydantic 模型被转换成 JSON Schema               │
│                                                         │
│  2️⃣  LLM 收到你的输入 + JSON Schema 的描述               │
│      └── Schema 中的 description 就是给 LLM 的提示       │
│                                                         │
│  3️⃣  LLM 按照 JSON Schema 输出结构化的 JSON              │
│      └── 大模型自动把内容填充到对应字段                   │
│                                                         │
│  4️⃣  Pydantic 验证 JSON 是否符合 Schema 定义             │
│      ├── 必填字段都有值吗？                               │
│      ├── 数值范围符合吗？                                 │
│      ├── 枚举值合法吗？                                   │
│      └── 类型正确吗？                                     │
│                                                         │
│  5️⃣  验证通过 → 返回 Pydantic 对象给你                   │
│      验证失败 → 抛出 ValidationError                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 8.3 三种 Agent 的结构化调用示例

```python
# ── 示例1：路由 Agent 的结构化调用 ──
from src.schemas.router_schema import RouterResponse, Intent

llm = get_llm()
router_llm = llm.with_structured_output(RouterResponse)

result: RouterResponse = router_llm.invoke(
    "帮我整理上个月的会议记录，生成会议纪要"
)

print(result.intent)       # Intent.MEETING_NOTES
print(result.confidence)   # 0.96
print(result.reasoning)    # "用户明确提到了'会议记录'和'会议纪要'关键词"


# ── 示例2：会议纪要 Agent 的结构化调用 ──
from src.schemas.meeting_schema import MeetingSummary

meeting_llm = llm.with_structured_output(MeetingSummary)

summary: MeetingSummary = meeting_llm.invoke(
    """
    会议记录：2026年6月20日，产品组周会。
    参会：张三（产品经理）、李四（开发）、王五（测试）。
    讨论了3个事项：
    1. 用户反馈搜索功能太慢 → 决定优化索引，李四负责，7月5日前完成
    2. Q3要不要做移动端适配 → 决议先做一版，张三负责调研，7月10日给出方案
    3. 测试环境不稳定 → 王五负责排查，明天之前解决
    """
)

print(summary.title)           # "产品组周会"
print(summary.date)            # "2026-06-20"
print(summary.attendees)       # ["张三", "李四", "王五"]
print(len(summary.actions))    # 3
print(summary.actions[0].description)  # "优化搜索索引"


# ── 示例3：对话 Agent 的结构化调用 ──
from src.schemas.chat_schema import ChatRequest, ChatResponse

chat_llm = llm.with_structured_output(ChatResponse)

request = ChatRequest(
    message="写一首关于夏天的五言诗",
    session_id="user-abc-123"
)

response: ChatResponse = chat_llm.invoke(request.message)

print(response.response)      # "夏日炎炎热，蝉鸣绿树间..."
print(response.session_id)    # "user-abc-123"
print(response.intent)        # "chat"
```

### 8.4 对比：有没有结构化输出的巨大差异

```
┌─────────────────────────────────────────────────────────┐
│              传统方式 vs 结构化输出                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  传统方式：                                              │
│  llm.invoke(input)                                       │
│  → 返回一段自然语言文本                                   │
│  → 你需要自己写正则/解析逻辑来抽取字段                     │
│  → 抽取逻辑容易出错，每次格式变化都要改代码                │
│  → 没有类型检查，运行时才发现问题                          │
│                                                         │
│  结构化输出：                                            │
│  llm.with_structured_output(Schema).invoke(input)        │
│  → 返回一个严格类型化的 Pydantic 对象                      │
│  → 字段直接访问，IDE 有自动补全                            │
│  → Pydantic 自动校验，不合规的数据直接拒绝                 │
│  → 大模型自动适配 Schema，不需要手写解析                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 九、Schema 的测试方法

### 9.1 数据结构测试的特点

Schema 类的测试非常简单——它们只是数据结构，不依赖外部服务，不需要网络连接，不需要 API Key。测试的核心思路就是：

> **创建一个对象，验证字段值是否正确存取。**

### 9.2 RouterResponse 测试示例

```python
# ── test_router_schema.py ──

import pytest
from src.schemas.router_schema import RouterResponse, Intent


class TestRouterResponse:
    """路由响应数据结构的测试"""
    
    def test_create_with_chat_intent(self):
        """测试：创建一个 chat 意图的路由响应"""
        response = RouterResponse(
            intent=Intent.CHAT,
            confidence=0.92,
            reasoning="用户询问天气，属于闲聊类问题"
        )
        
        # 验证字段存取正确
        assert response.intent == Intent.CHAT
        assert response.confidence == 0.92
        assert response.reasoning == "用户询问天气，属于闲聊类问题"
    
    def test_intent_is_enum_value(self):
        """测试：intent 字段确实是枚举值"""
        response = RouterResponse(
            intent=Intent.MEETING_NOTES,
            confidence=0.85
        )
        
        # 验证 intent 的类型和值
        assert isinstance(response.intent, Intent)
        assert response.intent.value == "meeting_notes"
    
    def test_confidence_boundary(self):
        """测试：confidence 边界值校验"""
        # 边界值 0.0 应该通过
        r1 = RouterResponse(intent=Intent.CHAT, confidence=0.0)
        assert r1.confidence == 0.0
        
        # 边界值 1.0 应该通过
        r2 = RouterResponse(intent=Intent.CHAT, confidence=1.0)
        assert r2.confidence == 1.0
        
        # 超出范围应该抛出 ValidationError
        with pytest.raises(Exception):
            RouterResponse(intent=Intent.CHAT, confidence=1.5)
        
        with pytest.raises(Exception):
            RouterResponse(intent=Intent.CHAT, confidence=-0.1)
    
    def test_reasoning_is_optional(self):
        """测试：reasoning 是可选字段，不填也不会报错"""
        response = RouterResponse(
            intent=Intent.UNKNOWN,
            confidence=0.5
        )
        # 不填 reasoning 也应该能正常创建
        assert response.reasoning == ""  # 默认值
```

### 9.3 ChatRequest 测试示例

```python
# ── test_chat_schema.py ──

import pytest
from src.schemas.chat_schema import ChatRequest, ChatResponse


class TestChatRequest:
    """对话请求数据结构的测试"""
    
    def test_create_valid_request(self):
        """测试：创建合法的请求"""
        request = ChatRequest(
            message="你好，帮我查一下天气",
            session_id="abc-123"
        )
        
        assert request.message == "你好，帮我查一下天气"
        assert request.session_id == "abc-123"
    
    def test_session_id_is_optional(self):
        """测试：session_id 是可选的，不传也没关系"""
        request = ChatRequest(message="你好")
        
        assert request.message == "你好"
        assert request.session_id is None  # 默认值
    
    def test_message_cannot_be_empty(self):
        """测试：message 不能为空"""
        with pytest.raises(Exception):
            ChatRequest(message="")  # 空字符串，min_length=1 会拒绝
    
    def test_message_cannot_exceed_max_length(self):
        """测试：message 不能超过 8000 字符"""
        too_long = "x" * 8001
        with pytest.raises(Exception):
            ChatRequest(message=too_long)
    
    def test_message_at_max_length_is_ok(self):
        """测试：刚好 8000 字符是可以通过的"""
        at_limit = "x" * 8000
        request = ChatRequest(message=at_limit)
        assert len(request.message) == 8000


class TestChatResponse:
    """对话响应数据结构的测试"""
    
    def test_create_valid_response(self):
        """测试：创建合法的响应"""
        response = ChatResponse(
            response="你好！有什么可以帮你的吗？",
            session_id="abc-123",
            intent="chat"
        )
        
        assert response.response == "你好！有什么可以帮你的吗？"
        assert response.session_id == "abc-123"
        assert response.intent == "chat"
```

### 9.4 MeetingSummary 测试示例

```python
# ── test_meeting_schema.py ──

import pytest
from src.schemas.meeting_schema import MeetingSummary, MeetingAction


class TestMeetingAction:
    """会议行动项数据结构的测试"""
    
    def test_create_action(self):
        """测试：创建一个行动项"""
        action = MeetingAction(
            description="完成用户调研报告",
            responsible_person="张三",
            deadline="2026-07-01"
        )
        
        assert action.description == "完成用户调研报告"
        assert action.responsible_person == "张三"
        assert action.deadline == "2026-07-01"
    
    def test_deadline_is_optional(self):
        """测试：deadline 是可选的"""
        action = MeetingAction(
            description="维护服务器",
            responsible_person="运维组"
        )
        
        assert action.deadline is None


class TestMeetingSummary:
    """会议纪要数据结构的测试"""
    
    def test_create_basic_summary(self):
        """测试：创建一个仅含必填字段的会议纪要"""
        summary = MeetingSummary(
            title="项目周会",
            date="2026-06-25",
            attendees=["张三", "李四"],
            content="讨论了本周项目进展"
        )
        
        assert summary.title == "项目周会"
        assert summary.date == "2026-06-25"
        assert summary.attendees == ["张三", "李四"]
        assert summary.resolutions is None   # 可选字段，未填
        assert summary.actions is None       # 可选字段，未填
    
    def test_to_markdown(self):
        """测试：to_markdown 方法能正常运行"""
        summary = MeetingSummary(
            title="测试会议",
            date="2026-06-25",
            attendees=["张三"],
            content="测试内容"
        )
        
        md = summary.to_markdown()
        
        # 验证 Markdown 包含关键内容
        assert "# 测试会议" in md
        assert "2026-06-25" in md
        assert "张三" in md
        assert "测试内容" in md
    
    def test_to_markdown_with_actions(self):
        """测试：包含行动项时 to_markdown 生成表格"""
        summary = MeetingSummary(
            title="测试会议",
            date="2026-06-25",
            attendees=["张三"],
            content="测试内容",
            actions=[
                MeetingAction(
                    description="做某事",
                    responsible_person="张三",
                    deadline="2026-07-01"
                )
            ]
        )
        
        md = summary.to_markdown()
        
        assert "## 行动项" in md
        assert "做某事" in md
        assert "2026-07-01" in md
```

### 9.5 测试要点总结

```
┌─────────────────────────────────────────────────────────┐
│            Schema 测试的核心关注点                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1️⃣  正常创建 —— 填入合法值，能正确存取                    │
│                                                         │
│  2️⃣  必填字段 —— 不填必填字段时抛出异常                    │
│                                                         │
│  3️⃣  可选字段 —— 不填可选字段时使用默认值                  │
│                                                         │
│  4️⃣  约束边界 —— 测试 ge/le/min_length/max_length 的边界  │
│      ├── 刚好在边界内 → 通过                              │
│      ├── 刚好在边界上 → 通过                              │
│      └── 超出边界 → 抛出异常                              │
│                                                         │
│  5️⃣  枚举值 —— 只能填入枚举定义中的值                      │
│                                                         │
│  6️⃣  方法测试 —— to_markdown() 等转换方法输出正确         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 十、常见问题与排错指南

### 10.1 错误速查表

| 错误信息 | 原因 | 解决方法 | 优先级 |
|---|---|---|---|
| `field required` | 必填字段（`default=...`）没有传值 | 检查创建对象时是否遗漏了必填字段 | 🔴 高 |
| `ensure this value is greater than or equal to X` | 数值小于最小约束（`ge`） | 检查传入的数值是否在合法范围内 | 🔴 高 |
| `ensure this value is less than or equal to X` | 数值大于最大约束（`le`） | 检查传入的数值是否在合法范围内 | 🔴 高 |
| `ensure this value has at least X characters` | 字符串太短 | 确保字符串长度满足 `min_length` 要求 | 🟡 中 |
| `ensure this value has at most X characters` | 字符串太长（如 message 超过 8000） | 缩短字符串，或对超长内容做预处理截断 | 🟡 中 |
| `value is not a valid enumeration member` | 枚举字段传了不在枚举定义中的值 | 检查枚举类定义了哪些值，使用 `Intent.CHAT` 而非裸字符串 `"chat"` | 🟡 中 |
| `LLM 返回的字段和 Schema 不匹配` | 大模型输出的 JSON 格式有误 | 在 `description` 里更清晰地描述字段含义；考虑换模型 | 🟢 低 |
| `model_dump() 得到的字典缺少某些字段` | 可选字段值为 `None`，默认不导出 | 使用 `model_dump(exclude_none=True)` 或 `exclude_none=False` | 🟢 低 |

### 10.2 `...` vs `default` 的正确用法

这是一个非常容易搞混的点：

```python
# ❌ 错误：想表示可选字段，但用了 ...
# 这会让 Pydantic 认为它是必填的
class Wrong(BaseModel):
    name: str = Field(default=...)  # 必填！

# ✅ 正确：可选字段用 default=值
class Correct(BaseModel):
    name: str = Field(default="未命名")  # 可选，默认"未命名"
```

```
记忆口诀：
  ...（三个点）= 三个字"必须填"
  default     = 四个字"可以不填"
```

### 10.3 枚举值的使用注意

```python
from src.schemas.router_schema import Intent, RouterResponse

# ✅ 正确：使用枚举成员
response = RouterResponse(
    intent=Intent.CHAT,  # 枚举成员
    confidence=0.9
)

# ⚠️ 也可以：直接用字符串值（Pydantic 会自动转换）
response = RouterResponse(
    intent="chat",       # 字符串
    confidence=0.9
)

# ❌ 错误：不在枚举定义中的值
response = RouterResponse(
    intent="translate",  # 枚举里没有这个值！
    confidence=0.9
)
# → ValidationError: value is not a valid enumeration member
```

### 10.4 Optional 字段的 model_dump 行为

```python
summary = MeetingSummary(
    title="测试",
    date="2026-06-25",
    attendees=["张三"],
    content="测试内容"
    # resolutions 和 actions 没有传 → 值为 None
)

# exclude_none=True（默认行为的一部分）→ None 字段不出现
d = summary.model_dump()
# {"title": "测试", "date": "2026-06-25", "attendees": ["张三"], "content": "测试内容"}
# 注意：resolutions, actions, notes 都不在结果中

# 如果想把 None 也输出：
d = summary.model_dump(exclude_none=False)
# 会包含 "resolutions": null, "actions": null, "notes": null
```

---

## 十一、课后练习

### 练习一：基础——补全 Schema 定义

**题目**：请为系统新增一个"翻译 Agent"（Translate Agent），并定义它的 Schema。翻译 Agent 接收一段文本和源语言/目标语言，返回翻译结果和置信度。

**要求**：
- 定义一个 `TranslateRequest`，包含 `text`（必填）、`source_lang`（必填）、`target_lang`（必填）
- 定义一个 `TranslateResponse`，包含 `translated_text`（必填）、`confidence`（必填，0~1）、`alternatives`（可选，备选翻译列表）
- 为置信度字段添加数值范围约束

**验收标准**：
- 创建对象时，必填字段缺失会抛出异常
- 置信度超出 0~1 范围会抛出异常
- `alternatives` 不传时默认值为空列表

<details>
<summary>参考答案（点击展开）</summary>

```python
from typing import Optional, List
from pydantic import BaseModel, Field


class TranslateRequest(BaseModel):
    text: str = Field(
        default=...,
        min_length=1,
        description="待翻译的文本"
    )
    source_lang: str = Field(
        default=...,
        description="源语言，如 'zh'、'en'"
    )
    target_lang: str = Field(
        default=...,
        description="目标语言，如 'en'、'fr'"
    )


class TranslateResponse(BaseModel):
    translated_text: str = Field(
        default=...,
        description="翻译结果"
    )
    confidence: float = Field(
        default=...,
        ge=0.0,
        le=1.0,
        description="翻译置信度"
    )
    alternatives: Optional[List[str]] = Field(
        default=None,
        description="备选翻译列表（可选）"
    )
```
</details>

### 练习二：进阶——给 RouterResponse 添加 to_dict 方法

**题目**：参考 `MeetingSummary.to_markdown()` 的设计思路，给 `RouterResponse` 添加一个 `to_dict()` 方法，返回一个适合下游调用的字典。

**要求**：
- 返回格式：`{"intent": "chat", "confidence": 0.92, "reasoning": "..."}`
- 如果 `reasoning` 为空字符串，则字典中不包含 `reasoning` 字段
- 补充对应的测试用例

<details>
<summary>参考答案（点击展开）</summary>

```python
class RouterResponse(BaseModel):
    intent: Intent = Field(default=..., description="识别出的用户意图")
    confidence: float = Field(default=..., ge=0.0, le=1.0, description="置信度")
    reasoning: str = Field(default="", description="推理过程")
    
    def to_dict(self) -> dict:
        """转换为下游可用的字典，空字段自动排除"""
        result = {
            "intent": self.intent.value,
            "confidence": self.confidence,
        }
        if self.reasoning:
            result["reasoning"] = self.reasoning
        return result
```
</details>

### 练习三：综合实战——为 MeetingAction 添加状态字段

**题目**：当前 `MeetingAction` 只有 `description`、`responsible_person`、`deadline` 三个字段。请新增一个 `status` 字段来表示行动项的执行状态。

**要求**：
- 定义一个 `ActionStatus` 枚举：`PENDING`（待执行）、`IN_PROGRESS`（执行中）、`COMPLETED`（已完成）、`CANCELLED`（已取消）
- `status` 字段为可选，默认值为 `PENDING`
- 为 `to_markdown()` 方法中的行动项表格新增"状态"列
- 写测试验证枚举值约束和默认值行为

<details>
<summary>参考答案（点击展开）</summary>

```python
from enum import Enum

class ActionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MeetingAction(BaseModel):
    description: str = Field(default=..., description="行动描述")
    responsible_person: str = Field(default=..., description="负责人")
    deadline: Optional[str] = Field(default=None, description="截止日期")
    status: ActionStatus = Field(
        default=ActionStatus.PENDING,
        description="执行状态"
    )


# to_markdown() 中行动项表格对应的修改：
# lines.append("| 序号 | 行动描述 | 负责人 | 截止日期 | 状态 |")
# ...
# lines.append(f"| {i} | {action.description} | {action.responsible_person} | {deadline} | {action.status.value} |")
```
</details>

---

## 十二、本节小结

### 12.1 核心知识图谱

```
┌────────────────────────────────────────────────────────────┐
│              Schema 模块核心知识体系                          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  为什么需要 Schema                                      │
│      ├── 大模型回复啰嗦 → 需要提取关键字段                    │
│      ├── 下游只需要部分信息 → 结构化输出避免浪费 token         │
│      └── 数据合法性校验 → 必填/类型/范围约束自动检查          │
│                                                            │
│  2️⃣  三种 Agent 的 Schema 设计                              │
│      ├── RouterResponse：intent（枚举）+ confidence + reasoning│
│      ├── MeetingSummary：7个字段 + MeetingAction 子模型 +    │
│      │   to_markdown()                                      │
│      └── ChatRequest/Response：message + session_id + intent │
│                                                            │
│  3️⃣  Pydantic BaseModel 字段约束                             │
│      ├── default=... → 必填                                 │
│      ├── default=值 → 可选（带默认值）                       │
│      ├── ge / le → 数值范围                                  │
│      ├── min_length / max_length → 字符串长度               │
│      └── description → 字段说明（给 LLM 看的）               │
│                                                            │
│  4️⃣  structured_output 使用                                 │
│      ├── llm.with_structured_output(Schema)                 │
│      ├── .invoke(input) → 直接返回 Schema 对象               │
│      └── 大模型自动填充 → Pydantic 自动校验                   │
│                                                            │
│  5️⃣  Schema 测试要点                                        │
│      ├── 字段创建与存取验证                                  │
│      ├── 边界值/约束校验                                     │
│      ├── 可选字段默认值验证                                  │
│      └── 转换方法（to_markdown/to_dict）验证                 │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 12.2 Schema 模块与其他模块的关系

```
┌─────────────────────────────────────────────────────────┐
│              Schema 模块的依赖关系                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Schema 层（本课）                                       │
│  ├── 只依赖 pydantic（几乎没有业务依赖）                   │
│  ├── 被 Agent 层引用（Agent 用它定义 I/O 格式）           │
│  └── 被测试直接使用（数据结构独立可测）                    │
│                                                         │
│  往上看 → Agent 层使用 Schema 定义的行为契约               │
│  往下看 → Core 层完全不依赖 Schema（单向依赖）             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 12.3 一句话总结

> **Schema 模块的本质是：把 Agent 之间的"通信协议"从模糊的自然语言，变成精确的类型约束。它让大模型这个"黑盒"的输出变得可预测、可校验、可编程。**

### 12.4 系列课程定位

```
┌─────────────────────────────────────────────────────────┐
│              多 Agent 开发实战 · 系列课程                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  开篇：课程总览                                           │
│  第1课：为什么现在必须学 Agent 开发                         │
│  第2课：多 Agent 项目架构总览                              │
│  第3课：Core 模块精讲——配置管理 + 大模型驱动                │
│  第4课（本课）：Schema 模块——数据结构决定 Agent 规范        │
│        ← 你在这里                                         │
│  后续课程：Memory 模块 → 各 Agent 实现 → Service 部署      │
│                                                         │
│  本课是从"基础架构"到"Agent 实现"的关键过渡！               │
│  学完本课后，你将能够：                                    │
│  ✅ 为任何 Agent 定义结构化的输入输出格式                   │
│  ✅ 在大模型调用中使用 structured_output                    │
│  ✅ 编写 Schema 的单元测试                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

*本教学文档基于陈泽鹏老师视频课程整理编写 · 2026年6月25日*
