# LangChain 记忆系统——ConversationBufferWindowMemory 详解

> 基于陈泽鹏老师视频课程整理编写 · 2026年6月

---

## 目录

- [一、课程背景与目标](#一课程背景与目标)
- [二、从 Buffer 到 Window——记忆策略的进化](#二从-buffer-到-window记忆策略的进化)
- [三、滑动窗口机制详解](#三滑动窗口机制详解)
- [四、WindowMemory 的三大特点](#四windowmemory-的三大特点)
- [五、优点与缺点深度分析](#五优点与缺点深度分析)
- [六、代码实战——K=1 vs K=2 对比实验](#六代码实战k1-vs-k2-对比实验)
- [七、如何查看和测试记忆内容](#七如何查看和测试记忆内容)
- [八、手动操作记忆——不通过模型直接操作](#八手动操作记忆不通过模型直接操作)
- [九、BufferMemory vs WindowMemory——全面对比](#九buffermemory-vs-windowmemory全面对比)
- [十、如何选择 K 值](#十如何选择-k-值)
- [十一、常见问题与排错指南](#十一常见问题与排错指南)
- [十二、课后练习](#十二课后练习)
- [十三、课程小结](#十三课程小结)

---

## 一、课程背景与目标

### 1.1 前情回顾

上一节课我们学习了 LangChain 的第一种记忆类型——**ConversationBufferMemory**：

```python
# 上节课的核心代码
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory)
```

| ConversationBufferMemory | 特点 |
|:------------------------:|------|
| 存储方式 | **完整存储**所有历史对话，不做任何压缩和筛选 |
| Token 增长 | **线性增长**——每增加一轮对话，Token 就增加一轮 |
| 核心问题 | 对话越长 → Token 越多 → **费用越来越高** |

### 1.2 本节课的核心问题

> **BufferMemory 太费 Token 了，有没有办法控制 Token 的消耗？**
>
> 我不需要记住所有的历史，只需要记住**最近几轮**就够了——怎么做到？

```
BufferMemory（全量记忆）：
[第1轮] [第2轮] [第3轮] ... [第98轮] [第99轮] [第100轮]
 ↑                                                      ↑
全部记住（Token 不断增加）                            全部记住

WindowMemory（窗口记忆）：
[第1轮] [第2轮] ... [第97轮] [第98轮] [第99轮] [第100轮]
   ↑ 丢弃                  ↑                        ↑
 超出窗口                  只保留最近 K 轮
```

### 1.3 本课要掌握的目标

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  目标一：了解 ConversationBufferWindowMemory      │
│         ├── 理解滑动窗口的机制（K 的含义）          │
│         ├── 理解它的三大特点                       │
│         └── 理解它的优点和缺点                     │
│                                                 │
│  目标二：掌握它的使用方法                          │
│         ├── 代码实现（与 BufferMemory 的差异）     │
│         ├── 验证窗口效果（K=1 vs K=2 实验）        │
│         ├── 查看记忆内容的方法                     │
│         └── 手动操作记忆（add/save context）       │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 二、从 Buffer 到 Window——记忆策略的进化

### 2.1 问题回顾：Buffer 的 Token 膨胀

`ConversationBufferMemory` 最核心的问题：

```
对话进行中，每次发给模型的内容：

第 1 轮：["你好，我是程序员"]                                    → 10 tokens
第 5 轮：["你好，我是程序员", "你好!", "你叫什么?", ...共10条消息] → 100 tokens
第 20 轮：[20轮的完整历史...]                                    → 500 tokens
第 50 轮：[50轮的完整历史...]                                    → 1500 tokens
...

每次调用，模型收到的消息都在变多 → Token 持续增长 → 费用持续上涨
```

### 2.2 解决思路：不需要记住全部

很多场景下，**最近几轮对话**就足够维持上下文了，不需要完整的历史：

```
场景一：客服对话
"我想退货" → "订单号是多少？" → "12345" → "好的，已处理"
第 4 轮时，第 1 轮的"我想退货"可能已经不再需要了

场景二：闲聊
"今天天气真好" → "是啊" → "适合出去玩" → "去哪里？"
第 4 轮时，第 1 轮的"今天天气真好"已经不太重要了
```

**思路**：只保留最近 K 轮对话，超过窗口的自动丢弃。

### 2.3 ConversationBufferWindowMemory 的定义

> **ConversationBufferWindowMemory** 是 LangChain 提供的一种记忆机制，它**只存储最近的 K 轮对话记录**。K 是用户指定的**窗口大小**，代表保留多少轮会话。当新对话发生时，最旧的对话会被移出窗口，从而确保内存使用和 Token 消耗在可控范围内。

| 要素 | 说明 |
|------|------|
| 对话记录 | 包括用户输入（HumanMessage）和模型输出（AIMessage） |
| K（窗口大小） | 用户指定的保留轮数，如 K=2 则保留最近 2 轮 |
| 滑动逻辑 | 新对话进来 → 如果超出 K → 最旧的被移除 |

---

## 三、滑动窗口机制详解

### 3.1 什么是"一轮"对话？

在 WindowMemory 中，**一轮 = 一次用户提问 + 一次模型回答**：

```
一轮对话 = HumanMessage + AIMessage

例如：
用户："你好，我是程序员"       ← HumanMessage
模型："你好！很高兴认识你"      ← AIMessage
                                ↑ 这是一轮
```

### 3.2 K=2 的滑动窗口演示

以 K=2（保留 2 轮）为例，观察窗口如何滑动：

```
初始状态（窗口为空）：
[                              ]
窗口大小：0/2

第 1 轮对话后：
[ 第1轮: "我是程序员" → "你好"  ]
窗口大小：1/2  ✅ 还能装

第 2 轮对话后：
[ 第1轮: "我是程序员" → "你好"  |  第2轮: "我叫张三" → "好的" ]
窗口大小：2/2  ✅ 刚好装满

第 3 轮对话后（关键！）：
[ 第2轮: "我叫张三" → "好的"    |  第3轮: "我的职业是?" → "程序员" ]
窗口大小：2/2  ⚠️ 第1轮被移出了！
                ↑
         "我是程序员"这条信息已经丢失！
```

### 3.3 完整图解

```
K = 2 的滑动窗口：

        ┌────────────── 窗口（K=2）──────────────┐
        │                                       │
第1轮   │  第1轮    第2轮    第3轮    第4轮    第5轮 │
        │                                       │
        │  [A1]     [A1]    [B1]    [C1]    [D1] │
        │  [B1]     [B2]    [C2]    [D2]    [E2] │
        │                                       │
        └───────────────────────────────────────┘
           ↑                     ↑
        第1轮被丢弃           只保留第4、5轮

图例：字母 = 轮次，数字 = 消息序号（1=用户, 2=模型）
      A=第1轮, B=第2轮, C=第3轮, D=第4轮, E=第5轮
```

### 3.4 窗口滑动的本质

```
新对话 → 追加到窗口末尾
         ↓
    窗口是否已满（达到 K 轮）？
    ├── 未满 → 保留所有
    └── 已满 → 移除最旧的一轮，为新对话腾出空间

→ 窗口始终只保留最新的 K 轮对话
→ 就像"滑动窗口"，永远只看到最近 K 个
```

---

## 四、WindowMemory 的三大特点

视频中老师总结了 `ConversationBufferWindowMemory` 的三个核心特点：

### 4.1 滑动窗口机制

> 只保留最近的 K 轮对话，新的对话会覆盖（移出）最早的对话记录。

```
特点：自动滑动，无需手动管理
效果：就像传送带，新的上来，旧的下去
```

### 4.2 固定的内存占用

> 无论进行了多少轮对话，内存中始终只保留固定轮数（K 轮）的会话。Token 消耗不会线性增长。

```
BufferMemory（线性增长）：          WindowMemory（固定上限）：
Token ↑                            Token ↑
     │        ╱                         │
     │     ╱                            │  ──────────（到达 K 后持平）
     │  ╱                               │ ╱
     │╱                                 │╱
     └──────────→ 轮数                   └──────────→ 轮数
     (持续增长)                          (到达 K 后封顶)
```

### 4.3 可配置性

> K 的大小可以自定义。期望保存少一点就设小 K，期望保存多一点就设大 K，相对灵活。

| K 值 | 效果 | 适用场景 |
|:----:|------|----------|
| K=1 | 只记最近 1 轮 | 简单的一问一答，不需要多轮上下文 |
| K=3 | 记最近 3 轮 | 普通对话，需要短期连贯性 |
| K=5 | 记最近 5 轮 | 稍微复杂的多轮交互 |
| K=10 | 记最近 10 轮 | 需要较长上下文的场景 |
| K=50+ | 记很多轮 | 接近 BufferMemory 的效果 |

---

## 五、优点与缺点深度分析

### 5.1 优点

| 优点 | 说明 |
|------|------|
| **Token 可控** | 到达 K 轮后封顶，不会线性增长 |
| **内存固定** | 无论多少轮对话，内存占用基本恒定 |
| **灵活配置** | K 值可以按需调整 |
| **代码简单** | 和 BufferMemory 几乎一模一样的写法 |
| **自动管理** | 不需要手动删除旧对话，窗口自动滑动 |

### 5.2 缺点一：丢失早期上下文

> 这是 WindowMemory **最关键的缺点**，视频中老师用了一个非常形象的例子：

```
场景：第一个问题是总纲，后续问题是细化

第 1 轮（总纲）："我想开发一个电商系统，包含用户管理、商品管理、订单管理"
第 2 轮（细化）："用户管理模块应该怎么设计？"
第 3 轮（细化）："登录功能用什么方案？"
...
第 10 轮（细化）："支付接口怎么对接？"

如果 K=5：
├── 第 1-5 轮 → ❌ 已被移出窗口
└── 第 6-10 轮 → ✅ 在窗口中

→ 总纲（第1轮）丢失了！
→ 模型不知道你最初的完整需求是什么
→ 后续回答可能偏离总体方向
```

> ⚠️ **关键认知**：在某些场景下，早期上下文不是"旧信息"，而是"总方向"。丢失总纲可能导致整个对话偏离预期。

### 5.3 缺点二：不适合需要完整历史的复杂场景

| 场景 | 可行性 | 原因 |
|------|:------:|------|
| 法律咨询 | ❌ 不适合 | 需要完整记录每一条信息 |
| 长篇故事创作 | ❌ 不适合 | 需要记住早期的情节设定 |
| 代码调试（多轮） | ⚠️ 谨慎 | 第1个bug的修复方案可能在第5轮还需要 |
| 客服对话 | ✅ 适合 | 通常只需近期上下文 |
| 闲聊 | ✅ 适合 | 聊到哪算哪，早期内容不重要 |

### 5.4 缺点三：K 值难以确定

视频中老师特别强调了这一点：

> **K 值到底设多少？5？10？100？说实话不好确定。**

设太小的后果：
```
K=2 → 用户说了3轮后，第1轮丢失 → 回答不准确
```

设太大的后果：
```
K=100 → 和 BufferMemory 差不多 → Token 控制失效
```

**确定 K 值需要综合考虑**：

| 考虑因素 | 影响方向 |
|----------|:--------:|
| 业务需求（需要多长的上下文） | 决定 K 的下限 |
| Token 使用量（预算限制） | 决定 K 的上限 |
| 内存占用（服务器资源） | 决定 K 的上限 |
| 每次对话的平均长度 | 同样的 K，长对话 Token 更多 |

---

## 六、代码实战——K=1 vs K=2 对比实验

### 6.1 完整代码

```python
import os
from langchain_community.chat_models import ChatZhipuAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain

# ============================================================
# 1. 准备模型
# ============================================================
os.environ["ZHIPUAI_API_KEY"] = "你的Key"
llm = ChatZhipuAI(model="glm-4", temperature=0.5)

# ============================================================
# 2. 创建 WindowMemory（K=1：只记最近1轮）
# ============================================================
memory = ConversationBufferWindowMemory(k=1)

# ============================================================
# 3. 创建会话链
# ============================================================
conversation = ConversationChain(
    llm=llm,
    memory=memory
)

# ============================================================
# 4. 多轮对话测试
# ============================================================

# 第 1 轮：告知身份
response1 = conversation.invoke({"input": "你好，我是一名程序员"})
print(f"[第1轮] {response1['response']}")

# 第 2 轮：告知姓名
response2 = conversation.invoke({"input": "你好，我的名字是张三"})
print(f"[第2轮] {response2['response']}")

# 第 3 轮：关键测试——问职业
# K=1 时，第1轮（告知职业）已被移出窗口！
response3 = conversation.invoke({"input": "我的职业是什么？"})
print(f"[第3轮] {response3['response']}")
```

### 6.2 实验一：K=1 运行结果

```
[第1轮] 你好！很高兴认识你，程序员朋友。有什么可以帮你的？
[第2轮] 你好，张三！有什么我可以帮你的吗？
[第3轮] 你好！根据之前的对话，你的名字是张三，但我没有关于你职业的信息。
        ↑ 😰 第1轮"我是程序员"已经被窗口移出了！模型不记得你的职业！
```

```
K=1 时的窗口状态：

第1轮后：[第1轮: "我是程序员"→"..."]
第2轮后：[第2轮: "我叫张三"→"..."]        ← 第1轮被移出！
第3轮时：[第2轮: "我叫张三"→"..."]        ← 窗口只有这一轮
         ↑ 问职业时，窗口里没有第1轮的信息！
```

### 6.3 实验二：K=2 运行结果

把 `k=1` 改成 `k=2`，重新运行：

```python
memory = ConversationBufferWindowMemory(k=2)  # ← 改成 K=2
```

```
[第1轮] 你好！很高兴认识你，程序员朋友。有什么可以帮你的？
[第2轮] 你好，张三！有什么我可以帮你的吗？
[第3轮] 根据我们之前的对话，你是一名程序员，名字叫张三。
        ↑ 🎉 K=2 时，第1轮和第2轮都在窗口中，模型记住了全部信息！
```

```
K=2 时的窗口状态：

第1轮后：[第1轮]
第2轮后：[第1轮, 第2轮]                   ← 都在
第3轮时：[第1轮, 第2轮]                   ← 都在（K=2刚好装下）
         ↑ 问职业时，窗口里有第1轮的"我是程序员"！
```

### 6.4 对比总结

```
┌─────────────────────────────────────────────────────────┐
│             K=1 vs K=2 —— 第3轮回复对比                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  K=1："我没有关于你职业的信息。"                             │
│       ↑ 只记住了第2轮（名字），第1轮（职业）丢了              │
│                                                         │
│  K=2："你是一名程序员，名字叫张三。"                         │
│       ↑ 记住了第1轮和第2轮，完整信息都在                     │
│                                                         │
│  结论：K 值决定了模型能"记住"多少轮之前的信息                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 6.5 代码差异——WindowMemory vs BufferMemory

```python
# ── BufferMemory（上节课）──
from langchain.memory import ConversationBufferMemory
memory = ConversationBufferMemory()                    # 无参数，全量存储

# ── WindowMemory（本节课）──
from langchain.memory import ConversationBufferWindowMemory
memory = ConversationBufferWindowMemory(k=2)           # 多了一个 k 参数！
```

> **会了一个，其余的差不多都会了——无非换个类名，加个参数。**

---

## 七、如何查看和测试记忆内容

### 7.1 为什么需要查看记忆？

视频中老师提出了一个重要的问题：

> 我们验证记忆是否有效，每次都要发送给模型吗？有没有更直接的方法？

**答案**：有。`memory` 对象本身就存储了对话历史，可以直接查看，不需要通过模型。

### 7.2 方法一：`memory.buffer`

```python
# 直接访问 buffer 属性
print(memory.buffer)
```

**输出示例：**

```
Human: 你好，我是一名程序员
AI: 你好！很高兴认识你，程序员朋友。
Human: 你好，我的名字是张三
AI: 你好，张三！有什么可以帮你的？
```

> 💡 用 `print()` 而不是直接输出，是因为 buffer 中包含 `\n` 换行符，`print()` 会自动解析。

### 7.3 方法二：`memory.load_memory_variables({})`

```python
# 调用 load_memory_variables 方法
history = memory.load_memory_variables({})
print(history)
```

**输出示例：**

```
{'history': 'Human: 你好，我是一名程序员\nAI: 你好！很高兴认识你...\nHuman: 你好，我的名字是张三\nAI: 你好，张三！...'}
```

返回一个字典，`history` 键对应的值就是格式化的对话历史字符串。

### 7.4 两种查看方式对比

| 方式 | 语法 | 返回类型 | 用途 |
|------|------|:--------:|------|
| `memory.buffer` | 直接访问属性 | `str` | 快速查看原始历史 |
| `memory.load_memory_variables({})` | 调用方法 | `dict` | 获取结构化的历史数据 |

### 7.5 验证窗口效果

通过查看 `memory.buffer`，可以直观验证窗口的滑动效果：

```python
memory = ConversationBufferWindowMemory(k=2)

# 第 1 轮
memory.save_context({"input": "第一条"}, {"output": "回复1"})
print(f"1轮后 buffer: {memory.buffer}")  # → 只有第1轮

# 第 2 轮
memory.save_context({"input": "第二条"}, {"output": "回复2"})
print(f"2轮后 buffer: {memory.buffer}")  # → 第1轮 + 第2轮

# 第 3 轮（超出窗口！）
memory.save_context({"input": "第三条"}, {"output": "回复3"})
print(f"3轮后 buffer: {memory.buffer}")  # → 只有第2轮 + 第3轮！
                                          #    第1轮被移出了！
```

---

## 八、手动操作记忆——不通过模型直接操作

### 8.1 为什么要手动操作？

视频中老师展示了一个重要的测试技巧：

> 不通过模型调用，直接往 memory 里添加对话历史。这样可以**快速验证**记忆系统是否正确工作，不需要等待模型响应。

### 8.2 方法一：`save_context()`

```python
from langchain.memory import ConversationBufferWindowMemory

# 创建 K=2 的 WindowMemory
memory = ConversationBufferWindowMemory(k=2)

# 手动添加一轮对话
memory.save_context(
    {"input": "你好"},           # 用户输入
    {"output": "你好！有什么可以帮你的？"}  # 模型输出
)

# 再添加一轮
memory.save_context(
    {"input": "今天天气怎么样？"},
    {"output": "今天天气不错！"}
)

# 查看结果
print(memory.buffer)
```

### 8.3 方法二：`chat_memory.add_user_message()` + `add_ai_message()`

```python
# 另一种添加方式——分别添加用户消息和AI消息
memory.chat_memory.add_user_message("你好")
memory.chat_memory.add_ai_message("你好！")

memory.chat_memory.add_user_message("今天天气怎么样？")
memory.chat_memory.add_ai_message("今天天气不错！")
```

### 8.4 完整的手动测试流程

视频中老师演示了直接用 `save_context` 来测试窗口滑动效果：

```python
from langchain.memory import ConversationBufferWindowMemory

# ── 创建 K=2 的 WindowMemory ──
memory = ConversationBufferWindowMemory(k=2)

# ── 添加 3 轮对话 ──
memory.save_context({"input": "第1轮用户消息"}, {"output": "第1轮AI回复"})
print("第1轮后:\n", memory.buffer, "\n")

memory.save_context({"input": "第2轮用户消息"}, {"output": "第2轮AI回复"})
print("第2轮后:\n", memory.buffer, "\n")

memory.save_context({"input": "第3轮用户消息"}, {"output": "第3轮AI回复"})
print("第3轮后:\n", memory.buffer, "\n")
# ↑ K=2，所以只显示第2轮和第3轮！第1轮已被移出
```

**运行结果：**

```
第1轮后:
 Human: 第1轮用户消息
AI: 第1轮AI回复

第2轮后:
 Human: 第1轮用户消息
AI: 第1轮AI回复
Human: 第2轮用户消息
AI: 第2轮AI回复

第3轮后:
 Human: 第2轮用户消息
AI: 第2轮AI回复
Human: 第3轮用户消息
AI: 第3轮AI回复
                                    ← 第1轮消失了！
```

### 8.5 手动操作 vs 通过模型

```
┌─────────────────────────────────────────────────────────┐
│              手动操作记忆的价值                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  通过模型：                                              │
│  conversation.invoke(...) → 等待模型响应 → 才能验证       │
│  缺点：需要网络、需要等待、消耗 Token                      │
│                                                         │
│  手动操作：                                              │
│  memory.save_context(...) → 立即查看 buffer               │
│  优点：不需要模型、不需要网络、不消耗 Token、瞬间完成        │
│                                                         │
│  💡 开发调试时首选手动操作，最终运行时再用模型              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 九、BufferMemory vs WindowMemory——全面对比

### 9.1 核心差异

| 对比维度 | ConversationBufferMemory | ConversationBufferWindowMemory |
|----------|:------------------------:|:------------------------------:|
| **存储策略** | 存储**全部**历史 | 只存储**最近 K 轮** |
| **Token 增长** | 线性增长（∞） | **固定上限**（到达 K 后封顶） |
| **内存占用** | 持续增长 | **固定** |
| **早期上下文** | ✅ 永久保留 | ⚠️ 超出 K 后丢弃 |
| **代码参数** | 无 | `k=整数` |
| **适用场景** | 需要完整历史的场景 | 只需近期上下文的场景 |
| **费用控制** | ❌ 无法控制 | ✅ 可控 |
| **长对话适应性** | ⚠️ Token 会爆 | ✅ Token 固定 |

### 9.2 代码对比

```python
# ── BufferMemory ──
from langchain.memory import ConversationBufferMemory
memory = ConversationBufferMemory()
# 全量存储，无限制

# ── WindowMemory ──
from langchain.memory import ConversationBufferWindowMemory
memory = ConversationBufferWindowMemory(k=3)
# 只保留最近 3 轮

# ── 其余代码完全一样！──
conversation = ConversationChain(llm=llm, memory=memory)
response = conversation.invoke({"input": "..."})
```

### 9.3 选择决策树

```
你的应用需要记忆系统吗？
    ↓ 需要
对话历史需要完整保留吗？
    ├── 需要（法律咨询、故事创作、详细记录）
    │   → ConversationBufferMemory
    │      ⚠️ 注意 Token 增长，适时考虑 Summary 型记忆
    │
    └── 不需要完整保留，近期上下文即可
        → ConversationBufferWindowMemory
           ↓
        确定合适的 K 值：
        ├── K=1-3：简单对话、客服
        ├── K=5-10：中等复杂度对话
        └── K=10+：需要较长上下文的场景
```

---

## 十、如何选择 K 值

### 10.1 K 值的影响

| K 值 | 记住的对话 | Token 消耗 | 推荐场景 |
|:----:|-----------|:----------:|----------|
| **1-2** | 最少 | 最低 | 简单一问一答，不需要多轮上下文 |
| **3-5** | 近期几轮 | 较低 | 普通对话、客服场景 |
| **5-10** | 近期多轮 | 中等 | 稍微复杂的多轮交互 |
| **10-20** | 较完整 | 较高 | 需要较长上下文的专业场景 |
| **50+** | 很多轮 | 接近 Buffer | 接近全量记忆（此时不如直接用 Buffer） |

### 10.2 选择 K 值的实践建议

```
步骤一：分析业务需求
    "用户通常几轮对话后会引用到前面的信息？"
    例如：客服场景通常 3-5 轮内解决问题 → K=3~5 即可

步骤二：评估 Token 预算
    "每轮对话平均多少 Token？"
    平均 50 Token/轮 × K 轮 = 历史消息的 Token 数
    加上当前问题的 Token = 一次调用的总 Token
    
步骤三：测试并调优
    ├── Token 消耗太高 → 减小 K
    ├── 回答经常缺少上下文 → 增大 K
    └── 两者平衡 → 这就是合适的 K 值
```

---

## 十一、常见问题与排错指南

### 11.1 错误速查表

| 错误/问题 | 原因 | 解决方法 | 优先级 |
|-----------|------|----------|:------:|
| 模型不记得 K 轮之前的信息 | WindowMemory 正常行为 | 增大 K 值，或切换到 BufferMemory | 🟡中 |
| `ImportError: cannot import ConversationBufferWindowMemory` | 导入路径错误 | `from langchain.memory import ConversationBufferWindowMemory` | 🔴高 |
| 设置了 K=5 但好像记住了很多轮 | `ConversationChain` 内部可能有额外的 Prompt 模板影响 | 用 `memory.buffer` 直接查看实际存储的轮数 | 🟡中 |
| K=0 报错 | K 值至少为 1 | 设置 K>=1 | 🟡中 |
| 窗口内容用 `print(memory)` 看不清楚 | buffer 中有 `\n`，直接输出不解析 | 使用 `print(memory.buffer)` | 🟢低 |
| `save_context` 后 buffer 没更新 | 忘记调用或调用方式不对 | 确保 `save_context({"input": ...}, {"output": ...})` 格式正确 | 🟡中 |

### 11.2 排查流程

```
WindowMemory 表现不符合预期？
    ↓
第一步：直接查看 buffer
    print(memory.buffer)
    → 看实际存储了几轮对话，验证窗口效果
    ↓
第二步：检查 K 值
    memory.k 的值是多少？
    是否与预期一致？
    ↓
第三步：如需要调整
    ├── 经常丢失重要上下文 → 增大 K
    ├── Token 消耗太高 → 减小 K
    └── 需要完整历史 → 换用 BufferMemory
```

---

## 十二、课后练习

### 练习一：K 值效果验证

> 创建 `ConversationBufferWindowMemory`，K 分别设为 1、2、3。每一种 K 值都进行 4 轮对话（依次告知姓名、年龄、职业、爱好），然后问模型"我的姓名和职业是什么？"。对比三种 K 值下的回复。

| K 值 | 第 5 轮回复 | 记住了哪些信息？ | 丢失了哪些信息？ |
|:----:|-----------|-----------------|-----------------|
| K=1 | | | |
| K=2 | | | |
| K=3 | | | |

### 练习二：手动操作记忆

> 不通过模型，仅用 `save_context()` 手动向 `ConversationBufferWindowMemory`（K=2）添加 5 轮对话。每添加一轮后打印 `memory.buffer`，观察窗口的滑动过程。

**验收标准：**
- [ ] 第 1-2 轮后，buffer 显示所有对话
- [ ] 第 3 轮后，buffer 中第 1 轮消失
- [ ] 第 5 轮后，buffer 只保留第 4 和第 5 轮

### 练习三：Token 消耗对比

> 创建 BufferMemory 和 WindowMemory（K=3），各进行 10 轮相同内容的对话。每轮后记录 `load_memory_variables({})` 返回的 history 字符串长度，绘制对比。

| 轮次 | BufferMemory 历史长度 | WindowMemory(K=3) 历史长度 |
|:----:|:---------------------:|:--------------------------:|
| 1 | | |
| 3 | | |
| 5 | | |
| 7 | | |
| 10 | | |

### 练习四：场景匹配

> 判断以下场景最适合用 BufferMemory 还是 WindowMemory：

| 场景 | 推荐记忆类型 | 理由 |
|------|:-----------:|------|
| 法律咨询，需要完整的对话记录 | | |
| 客服机器人，通常 3 轮内解决问题 | | |
| 多轮代码调试，需要完整的历史修改记录 | | |
| 闲聊机器人，聊到哪算哪 | | |
| 面试模拟，需要记住候选人的所有回答 | | |

### 练习五：确定最佳 K 值

> 设计一个 10 轮的测试对话（模拟客服场景），分别用 K=1 到 K=5 运行。在第 10 轮问一个需要引用第 1 轮信息的问题（如"根据我最开始说的问题，现在的解决方案完整吗？"）。找出"能正确回答"的最小 K 值。

```
你的测试结论：
最小可用的 K = ______
```

---

## 十三、课程小结

### 13.1 本课核心知识图谱

```
┌────────────────────────────────────────────────────────────┐
│              WindowMemory 核心知识体系                       │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  从 Buffer 到 Window                                    │
│      ├── Buffer：全量存储 → Token 线性增长 → 浪费            │
│      └── Window：只存最近 K 轮 → Token 封顶 → 可控           │
│                                                            │
│  2️⃣  滑动窗口机制                                           │
│      ├── K = 窗口大小（保留几轮对话）                        │
│      ├── 一轮 = HumanMessage + AIMessage                    │
│      ├── 新对话 → 超出 K → 最旧的被移出                     │
│      └── 像传送带：新上来，旧下去                            │
│                                                            │
│  3️⃣  三大特点                                               │
│      ├── 滑动窗口机制：自动丢弃旧对话                        │
│      ├── 固定内存占用：Token 到达 K 后封顶                  │
│      └── 可配置性：K 值可调                                 │
│                                                            │
│  4️⃣  三个缺点                                               │
│      ├── 丢失早期上下文（总纲可能被丢弃）                    │
│      ├── 不适合需要完整历史的复杂场景                        │
│      └── K 值难确定（需要综合考虑业务+Token+内存）           │
│                                                            │
│  5️⃣  代码公式（和 BufferMemory 几乎一样）                    │
│      memory = ConversationBufferWindowMemory(k=2)          │
│      conversation = ConversationChain(llm=llm, memory=memory)│
│                                                            │
│  6️⃣  查看和测试记忆                                         │
│      ├── memory.buffer → 直接查看字符串历史                 │
│      ├── memory.load_memory_variables({}) → 结构化查看      │
│      └── memory.save_context(input, output) → 手动添加      │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 13.2 一句话总结

> **ConversationBufferWindowMemory = 带窗口限制的 BufferMemory。** 只保留最近 K 轮对话，超出自动丢弃。代码和 BufferMemory 几乎一模一样（只多一个 `k` 参数），但能有效控制 Token 消耗。代价是早期的上下文可能丢失。

### 13.3 练习题答案

> **以下哪种场景最适合使用 ConversationBufferWindowMemory？**
>
> - A. 需要保留完整的对话历史（法律咨询场景）❌ → 应该用 BufferMemory
> - B. 对 Token 消耗要求极高，需要精准控制 Token ❌ → WindowMemory 不能精准控制（某轮对话特别长的话仍会多用 Token）
> - C. 长对话需要总结早期内容以节省 Token ❌ → WindowMemory 没有总结功能，是直接丢弃
> - **D. 短时对话，只需记住最近几轮交互 ✅**
>
> **答案：D**

### 13.4 系列课程定位

```
第一课：环境搭建          第六课：输出解析器
第二课：模型选型          第七课：链式调用
第三课：切换模型          第八课：流式输出
第四课：Ollama 本地       第九课：记忆系统—BufferMemory
第五课：提示词模板        第十课：记忆系统—WindowMemory 🆕
                         后续：SummaryMemory / RAG / Agent
```

---

*本教学文档基于陈泽鹏老师视频课程（记忆系统—ConversationBufferWindowMemory）整理编写。*  
*本文档涵盖滑动窗口机制详解、K 值效果实验、手动操作记忆方法、与 BufferMemory 的全面对比及 K 值选择策略。*
