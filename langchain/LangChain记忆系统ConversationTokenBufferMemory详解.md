# LangChain 记忆系统——ConversationTokenBufferMemory 详解

> 基于陈泽鹏老师视频课程整理编写 · 2026年6月

---

## 目录

- [一、课程背景与目标](#一课程背景与目标)
- [二、三种记忆策略的演进](#二三种记忆策略的演进)
- [三、Token 驱动的记忆机制详解](#三token-驱动的记忆机制详解)
- [四、TokenBuffer 的四大特点](#四tokenbuffer-的四大特点)
- [五、优点与缺点深度分析](#五优点与缺点深度分析)
- [六、代码实战——手动测试 Token 限制效果](#六代码实战手动测试-token-限制效果)
- [七、代码实战——通过模型验证记忆效果](#七代码实战通过模型验证记忆效果)
- [八、⚠️ 关键踩坑：需要安装 transformers](#八️-关键踩坑需要安装-transformers)
- [九、三种记忆类型全面对比](#九三种记忆类型全面对比)
- [十、如何选择 max_token_limit](#十如何选择-max_token_limit)
- [十一、常见问题与排错指南](#十一常见问题与排错指南)
- [十二、课后练习](#十二课后练习)
- [十三、课程小结](#十三课程小结)

---

## 一、课程背景与目标

### 1.1 前情回顾

我们已经学习了 LangChain 的两种记忆类型：

| 记忆类型 | 限制方式 | 核心问题 |
|----------|:--------:|----------|
| **ConversationBufferMemory** | 不限制（全量存储） | Token 线性增长，费用不可控 |
| **ConversationBufferWindowMemory** | 按**轮数**限制（K 轮） | 每轮对话长度差异大时不可控 |

### 1.2 轮数限制的问题

`ConversationBufferWindowMemory` 按轮数限制，但有一个关键问题：

```
场景：K=2（保留最近 2 轮）

情况 A：两轮都很短
第1轮："你好" → "你好！"                           （5 tokens）
第2轮："天气？" → "晴天"                           （5 tokens）
总计：10 tokens ✅ 很少

情况 B：第二轮特别长
第1轮："你好" → "你好！"                           （5 tokens）
第2轮："请详细介绍深度学习的历史..." → 长篇回答      （500 tokens）
总计：505 tokens ⚠️ 突然暴增！
```

> **问题**：按轮数限制时，Token 消耗不均衡。短对话浪费了额度，长对话突然超标。可控性差。

### 1.3 本节课的核心问题

> **能不能直接按 Token 数量来限制记忆？** 不管聊了多少轮，只保证总 Token 数不超过我设置的上限。

```
轮数限制（WindowMemory）：          Token 限制（TokenBufferMemory）：
"最多记 3 轮"                       "最多记 300 个 Token"
├── 短对话时：浪费了 Token 额度       ├── 短对话：可以记很多轮
└── 长对话时：Token 超标             └── 长对话：自动减少保留轮数
                                     → 精准控制！
```

### 1.4 本课要掌握的目标

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  目标一：了解 ConversationTokenBufferMemory       │
│         ├── 理解 Token 驱动 vs 轮数驱动的区别       │
│         ├── 理解它的四大特点                       │
│         └── 理解它的优点和缺点                     │
│                                                 │
│  目标二：掌握它的使用方法                          │
│         ├── 安装 transformers 依赖                │
│         ├── 设置 max_token_limit 参数             │
│         ├── 用 save_context 手动验证               │
│         └── 用 ConversationChain 实际对话验证       │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 二、三种记忆策略的演进

### 2.1 记忆系统的进化路径

```
┌─────────────────────────────────────────────────────────────┐
│                    三种记忆策略的进化                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  第一代：ConversationBufferMemory                            │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ 策略：全量存储，不限制                                   │    │
│  │ 优点：完整保留所有细节                                  │    │
│  │ 缺点：Token 线性增长，不可控                            │    │
│  └──────────────────────────────────────────────────────┘    │
│                          ↓ 改进                              │
│  第二代：ConversationBufferWindowMemory                       │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ 策略：按轮数限制（只保留最近 K 轮）                       │    │
│  │ 优点：Token 封顶，可控                                  │    │
│  │ 缺点：每轮长短不一，控制不够精准                         │    │
│  └──────────────────────────────────────────────────────┘    │
│                          ↓ 再改进                             │
│  第三代：ConversationTokenBufferMemory（本课）                 │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ 策略：按 Token 数量限制（不超过 max_token_limit）        │    │
│  │ 优点：精准控制 Token 使用量                             │    │
│  │ 缺点：依赖 LLM 计算 Token，设置值需要权衡               │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 三种策略的核心差异一句话

| 记忆类型 | 一句话 | 限制的是什么 |
|----------|--------|:----------:|
| BufferMemory | "全记住" | 无限制 |
| WindowMemory | "只记最近 3 轮" | **轮数** |
| **TokenBufferMemory** | "只记最近 300 Token" | **Token 数** |

---

## 三、Token 驱动的记忆机制详解

### 3.1 定义

> **ConversationTokenBufferMemory** 是 LangChain 提供的一种记忆机制，它根据 **Token 数量**来限制存储的对话历史。用户指定一个最大的 Token 数（`max_token_limit`），系统保留不超过该限制的最近对话内容。当新对话加入导致 Token 总数超过限制时，最早的对话记录会被自动移除。

### 3.2 Token 计数的含义

在深入之前，先理解"Token"这个概念在此处的含义：

```
一段文本 → LLM 的 Tokenizer 处理 → N 个 Token

例如（以某个模型为例）：
"你好"           → 2 个 Token
"Hello, world!"  → 4 个 Token
"我是程序员"       → 4 个 Token（取决于模型的分词方式）
```

> ⚠️ **关键认知**：不同的模型 Token 计算方式不同。同样的文字，智谱AI 可能算 5 个 Token，OpenAI 可能算 3 个。这也是为什么 `ConversationTokenBufferMemory` 需要传入 `llm` 参数。

### 3.3 max_token_limit=300 的工作演示

```
max_token_limit = 300（最多保留 300 Token 的历史）

第 1 轮对话（短）：
"你好，我是程序员" → "你好！很高兴认识你"          → 共 15 Token
累计：15/300  ✅ 保留

第 2 轮对话（短）：
"你叫什么？" → "我是AI助手"                       → 共 10 Token
累计：25/300  ✅ 保留

...中间若干轮...

第 10 轮对话（长）：
"请详细介绍..." → 长篇回答                         → 共 100 Token
累计：280/300  ✅ 还在限制内

第 11 轮对话：
"再问一个问题..." → "回答..."                      → 共 30 Token
累计：310/300  ⚠️ 超出限制！
→ 最早的第 1 轮被移除（15 Token 被释放）
→ 新的累计：295/300  ✅ 回到限制内
```

### 3.4 与轮数限制的关键区别

```
同一个对话序列，两种限制方式的表现：

对话序列：
第1轮：短（10 Token）    第4轮：短（10 Token）
第2轮：短（10 Token）    第5轮：短（10 Token）
第3轮：长（200 Token）   第6轮：短（10 Token）

WindowMemory（K=3）：
保留：[第4轮, 第5轮, 第6轮]  → 只 3 轮，共 30 Token
问题：第3轮虽然很长，但在 K 范围内 → 200 Token 照存不误

TokenBufferMemory（max=100）：
保留：[第5轮, 第6轮]       → 按 Token 数，共 20 Token
      第3轮（200 Token）超出限制，保留不下 → 被移出
问题：长对话被精准限制，不会突然超标
```

---

## 四、TokenBuffer 的四大特点

### 4.1 Token 驱动的截断

> 按照指定的 Token 数来限制保存多少会话。**不关心轮数，只关心 Token 总量。**

```
# ── WindowMemory：关心轮数 ──
memory = ConversationBufferWindowMemory(k=3)
# "不管每轮多长，我只记 3 轮"
# 可能 3 轮就 500 Token，也可能才 15 Token

# ── TokenBufferMemory：关心 Token ──
memory = ConversationTokenBufferMemory(llm=llm, max_token_limit=300)
# "不管多少轮，Token 总数不超过 300"
# 短对话可以记很多轮，长对话自动少记几轮
```

### 4.2 模型的适配性

> 不同的大语言模型计算 Token 的方式**不一样**。同一个文本，不同模型算出的 Token 数量可能不同。

```
同一句话 "你好，我是程序员"：

模型 A（通义）：算出来 6 个 Token
模型 B（智谱）：算出来 5 个 Token
模型 C（OpenAI）：算出来 4 个 Token

→ 同样的 max_token_limit=300
→ 使用不同模型时，实际能保留的对话量不同
→ 因此必须传入 llm 参数，让记忆系统用正确的模型计算 Token
```

### 4.3 动态窗口

> 窗口大小是**动态变化**的——不是固定的轮数，而是根据每轮对话的 Token 数灵活变化。

```
max_token_limit = 300，假设每轮对话的 Token 数不同：

对话 1-5 轮（每轮 20 Token）→ 窗口 = 15 轮（300÷20）
对话 6-10 轮（每轮 60 Token）→ 窗口 = 5 轮（300÷60）
对话 11-15 轮（每轮 100 Token）→ 窗口 = 3 轮（300÷100）

→ 同样的限制，长对话保留少，短对话保留多
→ 窗口随内容自动调整
```

### 4.4 高效的存储

> 仅保存不超过指定 Token 数的内容，内存和计算资源更可控。

**对比轮数限制的精准性差异**：

```
WindowMemory（K=2）：         TokenBufferMemory（max=100）：

┌─────────────────┐          ┌─────────────────┐
│ 第1轮: 10 Token  │          │ 第1轮: 10 Token  │
│ 第2轮: 200 Token │          │ 第2轮: 200 Token │
│ 总计: 210 Token  │          │ 总计: 110 Token  │
│                 │          │                 │
│ ⚠️ 超标了！      │          │ ✅ 超出100的限制   │
│ 但按轮数还在K=2  │          │ 最旧记录被移除    │
│ 所以照存不误    │          │ 严格控制！       │
└─────────────────┘          └─────────────────┘
```

> Token 限制比轮数限制**更精准**——能真正控制每一次调用消耗的 Token 量。

---

## 五、优点与缺点深度分析

### 5.1 优点

| 优点 | 说明 |
|------|------|
| **精准控制 Token** | 直接限制 Token 数，费用可控，预算明确 |
| **灵活自适应** | 短对话自动记更多轮，长对话自动减少保留 |
| **高效内存** | Token 封顶，内存使用可预期 |
| **跨模型一致** | 不管用什么模型，Token 上限是一致的策略 |

### 5.2 缺点

**缺点一：依赖大语言模型**

> 必须传入 `llm` 参数。不同模型计算 Token 的方式不同，如果用错模型，Token 计数也会错误。且无法脱离 LLM 独立计算 Token。

**缺点二：可能丢失早期信息**

> 和 WindowMemory 一样，超出限制后早期数据会被移出。但如果 max_token_limit 设得足够大，可以缓解这个问题。

**缺点三：设置复杂性**

> `max_token_limit` 到底设多少？设少了信息不够，设多了浪费 Token。需要结合实际场景测试调优。

**缺点四：不适合需要完整历史的场景**

> 法律咨询、长篇故事创作等需要完整记录的场景不适合。这种场景应该用 BufferMemory 或后面要学的 SummaryMemory。

### 5.3 适合 vs 不适合的场景

| 场景 | 适合度 | 原因 |
|------|:------:|------|
| 客服对话（3-5轮） | ✅ 很适合 | Token 限制精准，成本可控 |
| 闲聊机器人 | ✅ 很适合 | 近期上下文足够 |
| 短期问题诊断 | ✅ 适合 | 只需最近的交互历史 |
| 法律咨询 | ❌ 不适合 | 需要完整记录 |
| 长篇创作 | ❌ 不适合 | 早期设定可能被遗忘 |
| 复杂代码调试 | ⚠️ 谨慎 | 如果 max 值设得足够大，可以用 |

---

## 六、代码实战——手动测试 Token 限制效果

### 6.1 完整代码

```python
import os
from langchain_community.chat_models import ChatZhipuAI
from langchain.memory import ConversationTokenBufferMemory

# ============================================================
# 1. 准备模型
# ============================================================
os.environ["ZHIPUAI_API_KEY"] = "你的Key"
llm = ChatZhipuAI(model="glm-4", temperature=0.5)

# ============================================================
# 2. 创建 TokenBufferMemory
#    max_token_limit：限制最多保留多少 Token 的历史
# ============================================================
memory = ConversationTokenBufferMemory(
    llm=llm,                # 必须传！用于计算 Token 数
    max_token_limit=30       # 只保留最多 30 个 Token
)

# ============================================================
# 3. 手动添加对话历史（不通过模型，直接模拟）
# ============================================================
memory.save_context(
    {"input": "你好"},
    {"output": "你好！有什么可以帮助您的？"}
)
memory.save_context(
    {"input": "我喜欢编程"},
    {"output": "太棒了！你喜欢哪种语言？"}
)
memory.save_context(
    {"input": "Python 是我的最爱"},
    {"output": "Python 很强大！你用它做什么项目？"}
)
memory.save_context(
    {"input": "我想做一个聊天机器人"},
    {"output": "酷！像我这样的吗？"}
)

# ============================================================
# 4. 查看记忆内容
# ============================================================
print("=== memory.buffer ===")
print(memory.buffer)
print()

print("=== memory.load_memory_variables({}) ===")
print(memory.load_memory_variables({}))
```

### 6.2 不同 max_token_limit 的效果对比

以下用同一段对话历史，测试三种不同的限制值：

**max_token_limit=30：**

```
=== memory.buffer ===
Human: 我想做一个聊天机器人
AI: 酷！像我这样的吗？

↑ 只保留了最后一轮！前面的都超出了 30 Token 的限制
```

**max_token_limit=100：**

```
=== memory.buffer ===
Human: Python 是我的最爱
AI: Python 很强大！你用它做什么项目？
Human: 我想做一个聊天机器人
AI: 酷！像我这样的吗？

↑ 保留了两轮，但更早的内容还是丢了
```

**max_token_limit=300：**

```
=== memory.buffer ===
Human: 你好
AI: 你好！有什么可以帮助您的？
Human: 我喜欢编程
AI: 太棒了！你喜欢哪种语言？
Human: Python 是我的最爱
AI: Python 很强大！你用它做什么项目？
Human: 我想做一个聊天机器人
AI: 酷！像我这样的吗？

↑ 四轮全部保留！
```

### 6.3 效果对比表

```
┌─────────────────────────────────────────────────────────┐
│          同一段对话，不同 max_token_limit 的效果            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  max_token_limit=30： 只保留 1 轮  █░░░░░░░  最少       │
│  max_token_limit=100：保留 2 轮    ████░░░░  中等       │
│  max_token_limit=300：保留全部 4 轮 ████████  完整       │
│                                                         │
│  结论：max_token_limit 越大 → 保留的历史越多 → 越接近     │
│        BufferMemory 的效果                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 七、代码实战——通过模型验证记忆效果

### 7.1 使用 ConversationChain

```python
import os
from langchain_community.chat_models import ChatZhipuAI
from langchain.memory import ConversationTokenBufferMemory
from langchain.chains import ConversationChain

# ============================================================
# 1. 准备模型
# ============================================================
os.environ["ZHIPUAI_API_KEY"] = "你的Key"
llm = ChatZhipuAI(model="glm-4", temperature=0.5)

# ============================================================
# 2. 创建 TokenBufferMemory
# ============================================================
memory = ConversationTokenBufferMemory(
    llm=llm,
    max_token_limit=100     # 限制在 100 Token 以内
)

# ============================================================
# 3. 创建会话链
# ============================================================
conversation = ConversationChain(
    llm=llm,
    memory=memory
)

# ============================================================
# 4. 多轮对话
# ============================================================
# 第 1 轮：告知身份
r1 = conversation.invoke({"input": "你好，我的名字是小明，我是一名程序员，喜欢用 Python。"})
print(f"[第1轮] {r1['response']}")

# 第 2 轮：扩展话题（增加更多内容，逐渐逼近 Token 限制）
r2 = conversation.invoke({"input": "我目前在做一个人工智能项目，非常有趣。"})
print(f"[第2轮] {r2['response']}")

# 第 3 轮：关键测试——第1轮的信息还在吗？
r3 = conversation.invoke({"input": "你还记得我的名字和职业吗？"})
print(f"[第3轮] {r3['response']}")
```

### 7.2 运行结果

```
[第1轮] 你好小明！很高兴认识你。作为一名Python程序员，有什么可以帮你的？
[第2轮] 人工智能项目确实很有趣！能跟我说说具体在做什么吗？
[第3轮] 根据我们之前的对话，我记得你的名字是...（可能记不住，取决于 Token 是否超出限制）
```

### 7.3 查看当前记忆状态

```python
# 在任意时刻查看记忆保存了哪些内容
print(memory.load_memory_variables({}))
```

---

## 八、⚠️ 关键踩坑：需要安装 transformers

### 8.1 错误现象

首次使用 `ConversationTokenBufferMemory` 时，如果直接运行：

```
ImportError: cannot import transformers python package.
Please install transformers with `pip install transformers`.
```

### 8.2 原因

> `ConversationTokenBufferMemory` 需要**计算 Token 数量**，而这个计算依赖 `transformers` 库中的 Tokenizer 功能。`transformers` 不是 LangChain 的自动依赖，需要单独安装。

### 8.3 解决方法

```bash
# 确保在正确的虚拟环境中
conda activate agent

# 安装 transformers
pip install transformers
```

> 💡 建议锁定版本，避免不同版本导致的行为差异。视频中老师也强调了版本一致的重要性。

### 8.4 验证安装

```python
# 测试是否安装成功
from transformers import AutoTokenizer
print("transformers 安装成功！")
```

---

## 九、三种记忆类型全面对比

### 9.1 核心差异表

| 对比维度 | BufferMemory | WindowMemory | **TokenBufferMemory** |
|----------|:-----------:|:-----------:|:---------------------:|
| **限制方式** | 无限制 | 按**轮数**（K） | 按 **Token 数**（max） |
| **参数** | 无 | `k=整数` | `max_token_limit=整数` |
| **Token 增长** | 线性增长 | 封顶（但有波动） | **精准封顶** |
| **需传 llm** | ❌ | ❌ | **✅ 必须**（计算Token用） |
| **额外依赖** | 无 | 无 | **transformers** |
| **精度** | — | ⭐⭐ 近似控制 | ⭐⭐⭐⭐⭐ **精准控制** |
| **灵活性** | — | ⭐⭐⭐ | ⭐⭐⭐⭐ **动态窗口** |
| **早期上下文** | ✅ 永久 | ❌ 丢失 | ❌ 丢失（可设大值缓解） |

### 9.2 代码差异——三行对比

```python
# ── BufferMemory ──
from langchain.memory import ConversationBufferMemory
memory = ConversationBufferMemory()

# ── WindowMemory ──
from langchain.memory import ConversationBufferWindowMemory
memory = ConversationBufferWindowMemory(k=3)

# ── TokenBufferMemory ──
from langchain.memory import ConversationTokenBufferMemory
memory = ConversationTokenBufferMemory(llm=llm, max_token_limit=300)

# ── 其余代码完全一样！──
conversation = ConversationChain(llm=llm, memory=memory)
```

### 9.3 选择决策树

```
你需要记忆系统吗？
    ↓ 需要
你的核心诉求是什么？

├── 需要完整的历史记录（法律、创作...）
│   → ConversationBufferMemory
│      ⚠️ Token 会持续增长，注意预算
│
├── 只需近期上下文，想简单控制
│   → ConversationBufferWindowMemory
│      设 K=3~5 适用于大多数场景
│
└── 需要精准控制 Token 用量
    → ConversationTokenBufferMemory
       根据 Token 预算设定 max_token_limit
```

---

## 十、如何选择 max_token_limit

### 10.1 Token 数参考

| 中文文本长度 | 大约 Token 数 |
|:-----------:|:------------:|
| 10 个字 | ~15-20 Token |
| 50 个字 | ~70-100 Token |
| 100 个字 | ~150-200 Token |
| 500 个字 | ~700-900 Token |

> ⚠️ 以上为参考值，实际 Token 数因模型而异。

### 10.2 设定策略

```
步骤一：估算每轮对话的平均 Token 数
    用户问题：平均 20 Token
    模型回复：平均 50 Token
    一轮 ≈ 70 Token

步骤二：确定需要保留几轮上下文
    通常 3-5 轮足够
    5 轮 × 70 Token = 350 Token

步骤三：加上当前问题的 Token
    当前问题：20 Token
    总计：350 + 20 = 370 Token
    
步骤四：根据预算调整
    预算紧张 → 设 200（保留约 2-3 轮）
    预算宽松 → 设 500（保留约 6-7 轮）
```

### 10.3 建议值速查

| 使用场景 | 建议 max_token_limit | 大约保留轮数 |
|----------|:--------------------:|:-----------:|
| 简单客服 | 100-200 | 2-3轮 |
| 日常对话 | 200-500 | 3-6轮 |
| 详细咨询 | 500-1000 | 5-10轮 |
| 复杂调试 | 1000-2000 | 10-20轮 |

---

## 十一、常见问题与排错指南

### 11.1 错误速查表

| 错误/问题 | 原因 | 解决方法 | 优先级 |
|-----------|------|----------|:------:|
| `ImportError: cannot import transformers` | 未安装 transformers | `pip install transformers` | 🔴高 |
| `TypeError: __init__() missing required argument: 'llm'` | 没传 llm 参数 | `ConversationTokenBufferMemory(llm=llm, max_token_limit=300)` | 🔴高 |
| Token 限制似乎不生效 | Token 计算方式与预期不同 | 不同模型 Token 计算不同，检查 max_token_limit 是否设得太小 | 🟡中 |
| 记住的内容比预期少很多 | max_token_limit 设置太小 | 增大 max_token_limit（如从 50 改到 200） | 🟡中 |
| `NameError: name 'chat' is not defined` | 前面代码块未执行 | Jupyter 中按顺序执行，确保 llm 变量已定义 | 🟡中 |
| 跟 WindowMemory 效果差不多 | max_token_limit 设得太大 | 最大时等于 BufferMemory，适当调小 | 🟢低 |

### 11.2 排查流程

```
TokenBufferMemory 不按预期工作？
    ↓
第一步：检查 transformers 是否安装
    pip list | grep transformers
    ↓ 已安装
第二步：检查是否传了 llm 参数
    memory = ConversationTokenBufferMemory(llm=llm, max_token_limit=300)
                                             ↑ 这个必须有！
    ↓ 有
第三步：检查 max_token_limit 是否合理
    ├── 太小（< 50）→ 几乎记不住什么
    ├── 太大（> 10000）→ 接近 BufferMemory
    └── 适中（100-500）→ 正常
    ↓
第四步：用 memory.buffer 直接查看实际保存了多少
    print(memory.buffer)  → 实际验证
```

---

## 十二、课后练习

### 练习一：Token 限制效果对比

> 创建 `ConversationTokenBufferMemory`，分别设置 `max_token_limit=50`、`max_token_limit=150`、`max_token_limit=500`。用相同的 5 轮对话测试，每轮后打印 `memory.buffer`，对比保留的对话轮数。

| max_token_limit | 保留了哪几轮？ | 保留轮数 |
|:---------------:|---------------|:--------:|
| 50 | | |
| 150 | | |
| 500 | | |

### 练习二：三种记忆类型对比

> 用**同一段 5 轮对话**，分别测试 BufferMemory、WindowMemory(K=2)、TokenBufferMemory(max=200)。记录：
>
> 1. 第 5 轮时各保留了什么内容
> 2. 第 5 轮时 memory.buffer 的字符长度（代表 Token 消耗）

| 记忆类型 | 保留内容摘要 | buffer 长度 | 评价 |
|----------|-------------|:----------:|------|
| BufferMemory | | | |
| WindowMemory(K=2) | | | |
| TokenBufferMemory(200) | | | |

### 练习三：通过模型验证记忆

> 用 `ConversationTokenBufferMemory` + `ConversationChain`，进行以下实验：
>
> 1. 第 1 轮告诉模型姓名、年龄、职业
> 2. 第 2-5 轮聊其他话题（不断填充 Token）
> 3. 第 6 轮问"我的职业和年龄是什么？"
>
> 分别测试 `max_token_limit=100` 和 `max_token_limit=300` 两种情况。

| max_token_limit | 第 6 轮能记住职业吗？ | 第 6 轮能记住年龄吗？ |
|:---------------:|:--------------------:|:--------------------:|
| 100 | | |
| 300 | | |

### 练习四：精准控制场景

> 你正在开发一个客服机器人，Token 预算非常紧张——每次调用总 Token 不能超过 200。你需要保证对话历史 + 当前问题 + 模型回复的总 Token 在预算内。当前问题约 20 Token，模型回复约 50 Token。请计算合适的 `max_token_limit`，并解释你的计算过程。

```
你的计算过程：
max_token_limit = ______
理由：______
```

### 练习五：Token 与轮数的关系探索

> 设计两组对话，每组对话都有 4 轮，但：
> - 组 A：每轮都非常短（"你好"、"好的"等）
> - 组 B：每轮都非常长（详细的技术问答）
>
> 用 `max_token_limit=100` 运行两组，对比各自保留了哪些轮。

| 组别 | 保留的轮次 | 保留轮数 | 结论 |
|:----:|-----------|:--------:|------|
| A（短对话） | | | |
| B（长对话） | | | |

---

## 十三、课程小结

### 13.1 本课核心知识图谱

```
┌────────────────────────────────────────────────────────────┐
│              TokenBufferMemory 核心知识体系                   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  三种记忆策略的演进                                       │
│      ├── Buffer：全量存储 → Token 不可控                     │
│      ├── Window：按轮数限制 → 每轮长短不一，不够精准           │
│      └── TokenBuffer：按 Token 限制 → 精准控制 ✅             │
│                                                            │
│  2️⃣  核心机制                                               │
│      ├── 用户指定 max_token_limit（最大 Token 数）            │
│      ├── 系统保留不超过限制的最近对话内容                      │
│      ├── 超出限制时最早的记录自动移出（滑动窗口）               │
│      └── 必须传入 llm（不同模型 Token 计算方式不同）           │
│                                                            │
│  3️⃣  四大特点                                               │
│      ├── Token 驱动截断：不关心轮数，只关心 Token 量           │
│      ├── 模型适配性：不同模型 Token 计数不同                  │
│      ├── 动态窗口：短对话多保留，长对话自动少保留              │
│      └── 高效存储：Token 封顶，资源可预期                     │
│                                                            │
│  4️⃣  关键依赖                                               │
│      └── 必须安装 transformers：pip install transformers    │
│                                                            │
│  5️⃣  代码公式                                               │
│      memory = ConversationTokenBufferMemory(               │
│          llm=llm, max_token_limit=300                     │
│      )                                                    │
│      conversation = ConversationChain(llm=llm, memory=memory)│
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 13.2 一句话总结

> **ConversationTokenBufferMemory = 按 Token 数精确控制记忆量。** 不再按轮数，而是按 Token 数限制——短对话自动多记几轮，长对话自动少记几轮。比 WindowMemory 更精准，但需要传 `llm` 参数并安装 `transformers`。

### 13.3 练习题答案

> **问**：ConversationTokenBufferMemory 与 ConversationBufferWindowMemory 的主要区别是什么？
>
> - A. 前者保存完整历史对话，后者按轮数限制 ❌（TokenBuffer 也不完整保存）
> - **B. 前者根据 Token 数量来限制，后者根据固定的轮数来限制 ✅**
> - C. 前者通过总结早期对话来减少 Token ❌（TokenBuffer 不总结，是直接丢弃）
> - D. 前者无需指定大语言模型 ❌（必须指定 llm 用于计算 Token）
>
> **答案：B**

### 13.4 系列课程定位

```
第一课：环境搭建              第七课：链式调用
第二课：模型选型              第八课：流式输出
第三课：切换模型              第九课：记忆系统—BufferMemory
第四课：Ollama 本地           第十课：记忆系统—WindowMemory
第五课：提示词模板            第十一课：记忆系统—TokenBufferMemory 🆕
第六课：输出解析器            后续：SummaryMemory / RAG / Agent
```

---

*本教学文档基于陈泽鹏老师视频课程（记忆系统—ConversationTokenBufferMemory）整理编写。*  
*本文档涵盖 Token 驱动机制详解、三种 max_token_limit 效果对比、transformers 依赖安装、与 WindowMemory 的核心差异分析及三种记忆策略的全面对比。*
