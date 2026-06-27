# LangChain 流式输出（Streaming）详解

> 基于陈泽鹏老师视频课程整理编写 · 2026年6月

---

## 目录

- [一、课程背景与目标](#一课程背景与目标)
- [二、两种响应模式——短 vs 长](#二两种响应模式短-vs-长)
- [三、什么是流式输出](#三什么是流式输出)
- [四、非流式 vs 流式——全面对比](#四非流式-vs-流式全面对比)
- [五、代码实现：从 `.invoke()` 到 `.stream()`](#五代码实现从-invoke-到-stream)
- [六、`print()` 参数详解——`end` 和 `flush`](#六print-参数详解end-和-flush)
- [七、⚠️ 关键踩坑：输出解析器与流式输出冲突](#七️-关键踩坑输出解析器与流式输出冲突)
- [八、完整实战：从零构建流式输出应用](#八完整实战从零构建流式输出应用)
- [九、流式输出的其他用法](#九流式输出的其他用法)
- [十、常见问题与排错指南](#十常见问题与排错指南)
- [十一、课后练习](#十一课后练习)
- [十二、课程小结](#十二课程小结)

---

## 一、课程背景与目标

### 1.1 前情回顾

在前面几节课中，我们已经学会了：

- 使用 LangChain 创建大语言模型应用
- 将需求发送给模型 → 模型生成响应 → 返回结果
- 使用链式调用（Chain）简化代码

```python
# 前几节课的标准调用方式
chain = template | llm | parser
result = chain.invoke({"question": "勾股定理是什么？"})
print(result)
# 等待 3-5 秒... → 一次性输出完整结果
```

### 1.2 问题场景：长时间的沉默等待

使用过程中会遇到一个体验问题：

```
提问 → [沉默... 3秒... 5秒... 10秒... 30秒...] → 一次性输出大段回答
                  ↑
        这段时间用户看不到任何反馈
```

| 内容长度 | 等待时间 | 用户体验 |
|:--------:|:--------:|:--------:|
| 短（几个词） | < 1 秒 | ✅ 很好，秒回 |
| 中等（几段话） | 3 ~ 10 秒 | 😐 还可以接受 |
| 长（详细分析） | 10 ~ 60 秒 | 😰 **焦虑——"程序是不是卡死了？"** |
| 超长（报告级别） | 1 分钟以上 | 🤬 **"什么破程序，半天不理人"** |

> **核心矛盾**：模型需要时间思考，但用户在等待期间得不到任何反馈——就像问了一个问题，对方**半天不理你**，给人一种"爱搭不理"的感觉。

### 1.3 本课要掌握的目标

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  目标：掌握流式输出的使用方法                       │
│        ├── 理解流式输出解决什么问题                 │
│        ├── 掌握 .stream() 方法替代 .invoke()      │
│        ├── 理解 print() 的 end 和 flush 参数       │
│        └── 解决输出解析器与流式输出的冲突问题         │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 二、两种响应模式——短 vs 长

### 2.1 短内容——天生好体验

当用户问一个简单问题时，模型很快就能给出答案：

```python
chain.invoke({"question": "1+1等于几？"})
# 几乎瞬间返回： "1+1等于2"
# 用户：😊 体验不错！
```

这种情况下不需要流式输出——因为内容本身就短，等待时间几乎为零。

### 2.2 长内容——用户体验灾难

当问题需要模型深度思考并生成长篇回答时：

```python
chain.invoke({"question": "请详细介绍深度学习的發展歷史、核心原理和主要应用场景"})
```

用户体验时间线：

```
00:00  用户点击发送
00:01  [控制台一片空白]
00:03  [仍然一片空白]
00:05  [用户开始怀疑：是不是卡了？]
00:10  [用户想关掉重试...]
00:15  [仍然没有任何反馈]
00:20  [用户已经打开其他页面了]
00:25  [突然！一整篇回答弹出来]
       → 用户：😡 "终于出来了，但这体验太差了"
```

> 用户在等待时**完全不知道发生了什么**——模型是在思考？还是程序崩溃了？还是网络断了？没有任何信息反馈。

### 2.3 问题的本质

```
非流式输出的问题：

用户视角   [发送问题] ═══════等待═══════ [收到回答]
                          ↑
                   这段时间内：零反馈
                   用户心理：焦虑、困惑、不满

流式输出的解决：

用户视角   [发送问题] → 逐字输出中... → [全部显示完成]
            ↑           ↑    ↑    ↑
          立即响应     "勾" "股" "定" ... 
                   用户心理：满意，能看到进度
```

---

## 三、什么是流式输出

### 3.1 定义

> **流式输出（Streaming）**：用户在输入问题后，AI 模型**边生成边显示**响应的内容，逐步展示 AI 的思考过程，而不是等待所有内容生成完毕后再一次性返回完整答案。

### 3.2 直观理解

把模型想象成一个**正在写字的人**：

```
非流式（传统方式）：
┌─────────────────────────────────┐
│ 模型先把整篇文章在脑中写好         │
│ → 写完了 → 啪！一次性扔给你        │
│                                  │
│ 等待期间：你完全不知道他在干嘛      │
└─────────────────────────────────┘

流式输出：
┌─────────────────────────────────┐
│ 模型想到一个字 → 写一个字          │
│ "勾" → "股" → "定" → "理" →...  │
│                                  │
│ 你实时看到每个字的生成             │
│ 就像看直播打字一样                │
└─────────────────────────────────┘
```

### 3.3 流式输出的核心价值

```
┌──────────────────────────────────────────────────────────┐
│                   流式输出的三大价值                         │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1️⃣  即时反馈——消除用户焦虑                                  │
│      用户在几毫秒内就能看到第一个字，知道"程序在正常工作"        │
│                                                          │
│  2️⃣  逐步展示——用户可以边看边思考                              │
│      内容逐字出现，用户可以在全部生成完之前就开始阅读前几行       │
│                                                          │
│  3️⃣  感知速度——让等待"感觉"更短                               │
│      同样需要 10 秒生成，一帧一帧出现比 10 秒后一次性弹出         │
│      感觉快很多                                            │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 四、非流式 vs 流式——全面对比

### 4.1 行为对比表

| 对比维度 | 非流式输出（`.invoke()`） | 流式输出（`.stream()`） |
|----------|:----------------------:|:---------------------:|
| **响应时机** | 全部生成完毕后一次性返回 | **边生成边返回** |
| **用户第一眼看到内容** | 等待 N 秒后看到全文 | **毫秒级就看到第一个字** |
| **等待体验** | 😰 空白等待，焦虑 | 😊 逐字出现，安心 |
| **总耗时** | 相同（10秒） | 相同（10秒） |
| **感知耗时** | 感觉很慢 | **感觉很快** |
| **代码方法** | `.invoke()` | `.stream()` |
| **返回类型** | 完整结果（str / AIMessage / dict） | **迭代器**，逐块产出 |
| **适用场景** | 短文本、后台批处理 | **用户交互、聊天界面** |

### 4.2 同一场景的实际体验模拟

**非流式输出**：

```
用户输入："请介绍勾股定理"
[3 秒空白等待]
突然输出：
勾股定理是数学中的一个基本定理，它描述了直角三角形三边之间的关系。
在直角三角形中，两条直角边的平方和等于斜边的平方。
用公式表示为：a² + b² = c²...
```

**流式输出**：

```
用户输入："请介绍勾股定理"
勾股定理是数学中的一个基本定理，它描述了直角三角形三边之间的关系。在直角三角形中，两条直角边的平方和等于斜边的平方。用公式表示为：a² + b² = c²...
↑ 这些字一个一个地出现在屏幕上，用户可以边看边等
```

> 📌 **总耗时相同**，但是流式输出的**感知速度**好得多——就像进度条一样，让你知道"事情在推进"。

---

## 五、代码实现：从 `.invoke()` 到 `.stream()`

### 5.1 核心改动——只改一个方法名

流式输出的代码改动**非常小**：

```python
# ── 非流式（之前的写法）──
result = chain.invoke({"question": "勾股定理是什么？"})
print(result)
# 等待 3 秒... → 一次性输出完整结果

# ── 流式（只需改一个词！）──
for chunk in chain.stream({"question": "勾股定理是什么？"}):
    print(chunk, end="", flush=True)
# 逐字出现，实时的输出体验！
```

| 改动 | 非流式 | 流式 |
|------|--------|------|
| 方法名 | `.invoke()` | **`.stream()`** |
| 返回类型 | 完整结果（一次性） | **迭代器**（逐块产出） |
| 处理方式 | 直接使用 | **for 循环**逐块获取 |
| 打印方式 | `print(result)` | `print(chunk, end="", flush=True)` |

### 5.2 `.stream()` 方法详解

```python
# .stream() 返回一个迭代器
stream = chain.stream({"question": "勾股定理是什么？"})

# 每次迭代产出模型生成的一个"块"（chunk）
for chunk in stream:
    # chunk 可能是：
    #   - 几个字符："勾股"
    #   - 一个词："定理"
    #   - 一句话："是数学中..."
    #   - 或者一个 AIMessage 对象（取决于链的结构）
    print(chunk, end="", flush=True)
```

**`.stream()` 的工作方式：**

```
模型内部生成过程：   "勾" → "股" → "定" → "理" → "是" → ...
                         ↓       ↓       ↓       ↓
.stream() 产出的 chunk： chunk1  chunk2  chunk3  chunk4 ...
                         ↓       ↓       ↓       ↓
for 循环接收：          第1次    第2次    第3次    第4次  ...
                         ↓       ↓       ↓       ↓
print() 立即输出：      勾      股      定      理      ...
```

### 5.3 存储完整结果的同时流式显示

视频中老师提到了一个重要做法——**边显示边存储**：

```python
# 累积存储完整结果
full_response = ""

for chunk in chain.stream({"question": "勾股定理是什么？"}):
    # 提取文本内容（chunk 可能是对象）
    content = chunk.content if hasattr(chunk, 'content') else str(chunk)
    
    # 流式显示
    print(content, end="", flush=True)
    
    # 同时存储
    full_response += content

# 循环结束后，full_response 包含完整结果
print("\n\n--- 完整结果已保存 ---")
print(f"总字数：{len(full_response)}")
```

---

## 六、`print()` 参数详解——`end` 和 `flush`

### 6.1 为什么需要这些参数？

视频中老师强调了 `print()` 的两个关键参数。如果不加这两个参数，流式输出会"变形"——每个 chunk 独占一行：

```python
# ❌ 不加参数——输出惨不忍睹
for chunk in chain.stream({"question": "勾股定理是什么？"}):
    print(chunk)

# 输出效果：
# 勾股
# 定理
# 是数学
# 中的
# 一个基本定理
# ...
# → 每块内容独占一行，完全不是流式的效果
```

### 6.2 `end=""`——禁止自动换行

`print()` 函数默认在输出的末尾添加换行符 `\n`。这就是为什么每块内容会独占一行。

```python
# print() 的默认行为
print("勾股")     # 输出 "勾股\n"  → 自动换行
print("定理")     # 输出 "定理\n"  → 又换一行
# 结果：
# 勾股
# 定理

# end="" 禁止自动换行
print("勾股", end="")   # 输出 "勾股"  → 不换行
print("定理", end="")   # 输出 "定理"  → 紧接着上一条
# 结果：
# 勾股定理
```

| `end` 参数值 | 效果 |
|:-----------:|------|
| 默认（`\n`） | 每次 print 后**换行** ❌ |
| `end=""` | 每次 print 后**不换行**，内容连在一起 ✅ |
| `end=" "` | 每次 print 后加一个**空格** |
| `end=" | "` | 每次 print 后加**竖线分隔** |

### 6.3 `flush=True`——强制立即输出

Python 的 `print()` 有**输出缓冲**机制：内容会先存在缓冲区，攒够一批再输出到屏幕。这会导致流式输出"卡顿"——明明已经生成了内容，但屏幕上不显示。

```python
# ❌ 不加 flush——可能卡顿
for chunk in chain.stream({...}):
    print(chunk, end="")
# 可能出现：等了好几块内容才突然一起出现
# → 失去了流式的意义

# ✅ flush=True——强制立即刷新
for chunk in chain.stream({...}):
    print(chunk, end="", flush=True)
# 每生成一块，立刻显示在屏幕上
# → 真正的实时流式体验
```

### 6.4 三个参数的组合效果

```
┌─────────────────────────────────────────────────────────────┐
│                print(chunk, end="", flush=True)              │
│                         ↑       ↑         ↑                 │
│                      输出内容   不换行    立即刷新              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  效果：                                                     │
│  • 每个 chunk 紧接着上一个 chunk 输出（不换行）                │
│  • 不会在缓冲区等待（立即刷新）                                │
│  • 用户看到文字一个字一个字地在同一行出现                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 七、⚠️ 关键踩坑：输出解析器与流式输出冲突

### 7.1 问题现象

这是视频中老师**当场遇到并演示解决**的核心问题。当你把流式输出和输出解析器一起使用时：

```python
# 链中包含输出解析器
chain = template | llm | parser   # ← parser 在链中！

# 使用流式输出
for chunk in chain.stream({"question": "勾股定理是什么？"}):
    print(chunk, end="", flush=True)

# 运行结果：😰 等了好久，然后一次性全部输出！
# 完全没有流式效果！
```

### 7.2 原因分析

输出解析器（Output Parser）的工作原理是：**拿到完整结果 → 格式化解析 → 输出**。

```
链的数据流（含 parser）：

template → llm → [等待 llm 生成完整结果...] → parser → 输出
                                              ↑
                                     parser 必须等 llm 全部生成完
                                     才能开始工作！
                                     
→ 流式效果被 parser "卡"住了！
```

> **输出解析器需要完整结果才能格式化**。而流式输出的核心优势在于模型思考过程中的实时展示。**这两者天然冲突。**

### 7.3 解决方案——去掉解析器

视频中的解决方案：**从链中移除输出解析器**。

```python
# ❌ 有解析器的链——流式失效
chain = template | llm | parser
for chunk in chain.stream({...}):
    print(chunk, end="", flush=True)
# → 等很久，一次性输出（解析器"吃掉"了流式效果）

# ✅ 去掉解析器的链——真正的流式
chain = template | llm              # ← 没有 parser！
for chunk in chain.stream({...}):
    # chunk 现在是 AIMessage 对象，需要提取 .content
    print(chunk.content, end="", flush=True)
# → 逐字出现，完美的流式效果！
```

### 7.4 提取 `.content` 属性

去掉解析器后，`chunk` 是 `AIMessage` 对象，不是纯文本。需要提取 `.content`：

```python
# 去掉解析器后，chunk 是 AIMessage 对象
for chunk in chain.stream({"question": "勾股定理是什么？"}):
    # chunk 的类型：<class 'langchain.schema.AIMessage'>
    # 直接 print(chunk) → AIMessage(content='勾股', ...)  ← 不好看
    
    # 正确做法：提取 .content
    print(chunk.content, end="", flush=True)
    # → 纯文本流式输出，完美！
```

### 7.5 冲突总结

```
┌──────────────────────────────────────────────────────────┐
│         流式输出 + 输出解析器 = 不兼容 ⚠️                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  原因：解析器需要完整结果才能格式化                          │
│                                                          │
│  现象：加了 parser 的链用 .stream() = 还是等全部生成完才输出  │
│                                                          │
│  解决：从链中去掉 parser                                   │
│        chain = template | llm     ← 没有 parser           │
│        然后 for chunk 中访问 chunk.content                 │
│                                                          │
│  取舍：流式体验 vs 结构化输出                               │
│        ├── 要流式 → 去 parser，事后手动解析                 │
│        └── 要结构化 → 用 parser，但接受非流式输出            │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 八、完整实战：从零构建流式输出应用

### 8.1 完整代码（基于之前的链式调用改造）

```python
import os
from langchain_community.chat_models import ChatZhipuAI
from langchain.prompts import PromptTemplate

# ============================================================
# 1. 准备模型
# ============================================================
os.environ["ZHIPUAI_API_KEY"] = "你的Key"
llm = ChatZhipuAI(model="glm-4", temperature=0.5)

# ============================================================
# 2. 定义提示词模板（不需要解析器！）
# ============================================================
template = PromptTemplate.from_template("""
你是{role}，请用{style}的风格回答以下问题。

问题：{question}
""")

# ============================================================
# 3. 创建链（⚠️ 不加 parser！）
# ============================================================
chain = template | llm

# ============================================================
# 4. 流式调用
# ============================================================
print("🤖 AI 正在回答：\n")

for chunk in chain.stream({
    "role": "数学老师",
    "style": "通俗易懂",
    "question": "勾股定理是什么？请详细介绍。"
}):
    print(chunk.content, end="", flush=True)

print("\n\n✅ 回答完毕！")
```

### 8.2 边流式显示边存储完整结果

```python
import os
from langchain_community.chat_models import ChatZhipuAI
from langchain.prompts import PromptTemplate

# ── 准备 ──
os.environ["ZHIPUAI_API_KEY"] = "你的Key"
llm = ChatZhipuAI(model="glm-4", temperature=0.5)
chain = PromptTemplate.from_template(
    "你是{role}，用{style}风格回答：{question}"
) | llm

# ── 流式 + 存储 ──
def stream_and_save(role, style, question):
    """流式显示并返回完整结果"""
    full_text = ""
    
    for chunk in chain.stream({
        "role": role, "style": style, "question": question
    }):
        text = chunk.content
        print(text, end="", flush=True)   # 实时显示
        full_text += text                  # 累积存储
    
    return full_text

# ── 使用 ──
result = stream_and_save(
    role="历史老师",
    style="生动有趣",
    question="介绍一下唐朝的丝绸之路"
)

print(f"\n\n📊 统计：共 {len(result)} 字")
# 后续可以用 result 做进一步处理
```

### 8.3 对比：同一个链，两种调用方式

```python
# ── 同一个链 ──
chain = template | llm

# 方式一：非流式（快速获取完整结果）
result = chain.invoke({"role": "老师", "question": "1+1=?"})
print(result.content)
# → 几乎瞬间输出完整答案

# 方式二：流式（长篇回答时的好体验）
for chunk in chain.stream({"role": "老师", "question": "请详细解释..."}):
    print(chunk.content, end="", flush=True)
# → 逐字输出，用户不会焦虑
```

> 📌 **同一个链**既可以用 `.invoke()` 也可以用 `.stream()`，根据场景选择。

---

## 九、流式输出的其他用法

### 9.1 不使用链的流式输出

如果不用链，直接调用模型也可以流式输出：

```python
llm = ChatZhipuAI(model="glm-4", temperature=0.5)

# 直接流式调用模型
for chunk in llm.stream("请用中文介绍什么是机器学习？"):
    print(chunk.content, end="", flush=True)
```

### 9.2 异步流式输出（`.astream()`）

在高性能场景下，可以使用异步版本：

```python
import asyncio

async def async_stream():
    chain = template | llm
    async for chunk in chain.astream({"question": "什么是AI？"}):
        print(chunk.content, end="", flush=True)

asyncio.run(async_stream())
```

### 9.3 流式 + 后处理：折中方案

如果你既想要流式输出的体验，又想要结构化数据：

```python
import json

# ── 流式显示（不加 parser）──
chain = template | llm
full_text = ""

for chunk in chain.stream({"question": "..."}):
    print(chunk.content, end="", flush=True)
    full_text += chunk.content

# ── 流式结束后，手动解析（非流式部分）──
# 如果模型返回的是 JSON 格式
try:
    structured_data = json.loads(full_text)
    print(f"\n解析结果：{structured_data}")
except json.JSONDecodeError:
    print("\n无法解析为 JSON，使用原始文本")
```

---

## 十、常见问题与排错指南

### 10.1 错误速查表

| 错误/问题 | 原因 | 解决方法 | 优先级 |
|-----------|------|----------|:------:|
| 流式输出等了很久一次性出现 | 链中包含了 Output Parser | 从链中移除 parser：`chain = template \| llm` | 🔴高 |
| 每个 chunk 独占一行 | `print()` 默认 `end="\n"` | 加 `end=""` 禁止换行 | 🔴高 |
| 输出卡顿，几块内容一起出现 | 输出缓冲区未刷新 | 加 `flush=True` 强制立即输出 | 🟡中 |
| `AttributeError: 'str' object has no attribute 'content'` | chunk 本身就是字符串，不需要 `.content` | 直接 `print(chunk, ...)` | 🟡中 |
| 流式输出乱码或格式不对 | chunk 类型不确定 | 统一处理：`chunk.content if hasattr(chunk, 'content') else str(chunk)` | 🟡中 |
| `.stream()` 报错 `NotImplementedError` | 某个组件不支持流式 | 检查链中的每个组件是否都支持 streaming | 🟡中 |
| 流式输出完想用 parser 解析 | parser 需要完整结果 | 流式收集完整文本后，再传给 parser | 🟢低 |
| 异步报错 | 用了 `.stream()` 而非 `.astream()` | 异步环境用 `async for chunk in chain.astream(...)` | 🟢低 |

### 10.2 排查流程

```
流式输出不工作？
    ↓
第一步：确认链中是否包含 Output Parser？
    ├── 是 → parser 是罪魁祸首！去掉它
    │        chain = template | llm  （不加 parser）
    └── 否 → 往下看

第二步：确认 print() 参数是否正确？
    必须同时使用：
    ├── end=""     ← 不换行
    └── flush=True ← 立即刷新

第三步：确认如何提取内容？
    ├── chunk 有 .content 属性？ → chunk.content
    ├── chunk 是字符串？ → 直接使用
    └── 不确定？ → hasattr(chunk, 'content') 判断

第四步：确认所有组件都支持流式？
    大部分语言模型都支持 .stream()
    Custom 组件可能不支持
```

### 10.3 `.stream()` vs `.invoke()` 选择指南

```
是否需要流式输出？

    场景判断：
    ├── 内容是短文本（< 50字）？
    │   → .invoke() 就够了，差距不大
    │
    ├── 内容是长文本，用户需要实时看到？
    │   → .stream()，显著提升体验
    │
    ├── 后台批处理，用户不需要实时看？
    │   → .invoke()，代码更简单
    │
    └── 需要结构化解析输出？
        ├── 必须 parser → 建议 .invoke()
        └── 可以不要 parser → .stream() + 手动后处理
```

---

## 十一、课后练习

### 练习一：基础流式输出

> 创建一个链（不含 parser），使用 `.stream()` 方法实现流式输出。分别测试短问题和长问题，观察输出效果。

**验收标准：**
- [ ] 链中不包含 Output Parser
- [ ] 使用 `.stream()` 而不是 `.invoke()`
- [ ] `print()` 使用了 `end=""` 和 `flush=True`
- [ ] 短问题快速输出，长问题逐字出现

### 练习二：流式 + 存储

> 在练习一的基础上，实现"边流式显示边存储完整结果"。流式结束后打印统计信息（总字数、生成耗时）。

**提示**：

```python
import time

start = time.time()
full_text = ""

for chunk in chain.stream({...}):
    print(chunk.content, end="", flush=True)
    full_text += chunk.content

elapsed = time.time() - start
print(f"\n\n总字数：{len(full_text)}，耗时：{elapsed:.1f}秒")
```

### 练习三：对比实验

> 用**同一个链**和**同一个长问题**，分别用 `.invoke()` 和 `.stream()` 两种方式执行。记录：
>
> 1. 两种方式的**实际耗时**
> 2. 作为用户的**主观体验感受**（哪种更好？为什么？）

| 方式 | 实际耗时 | 第一个字出现时间 | 主观体验评分（1-5） |
|------|:--------:|:---------------:|:-------------------:|
| `.invoke()` | | | |
| `.stream()` | | | |

### 练习四：流式 + 解析器冲突验证

> 创建一个**包含 Output Parser 的链**，分别用 `.invoke()` 和 `.stream()` 执行，观察 `.stream()` 是否有流式效果。
>
> 然后**去掉 Parser**，再次用 `.stream()` 执行，对比两次的差异。

```python
# 链A：含 parser（流式失效）
chain_a = template | llm | parser

# 链B：不含 parser（流式正常）
chain_b = template | llm
```

| 链 | Parser | `.stream()` 效果 | 原因 |
|----|:------:|:----------------:|------|
| A | 有 | | |
| B | 无 | | |

### 练习五：综合实战

> 构建一个**可切换输出模式**的问答函数：
>
> - 参数 `streaming=True` → 流式输出
> - 参数 `streaming=False` → 一次性输出
>
> 封装为 `ask(question, role, style, streaming=True)` 函数。

**提示**：

```python
def ask(question, role="助手", style="简洁", streaming=True):
    chain = template | llm
    
    if streaming:
        for chunk in chain.stream({"role": role, "style": style, "question": question}):
            print(chunk.content, end="", flush=True)
    else:
        result = chain.invoke({"role": role, "style": style, "question": question})
        print(result.content)
```

---

## 十二、课程小结

### 12.1 本课核心知识图谱

```
┌────────────────────────────────────────────────────────────┐
│               流式输出核心知识体系                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  为什么需要流式输出？                                   │
│      ├── 长内容等待时用户没有任何反馈 → 体验极差              │
│      ├── 流式输出：边生成边显示 → 用户实时看到进度             │
│      └── 总耗时相同，但"感知速度"快得多                      │
│                                                            │
│  2️⃣  .invoke() → .stream()                                 │
│      ├── .invoke()：一次性返回完整结果                        │
│      └── .stream()：返回迭代器，逐块产出                      │
│          for chunk in chain.stream({...}):                 │
│              print(chunk.content, end="", flush=True)      │
│                                                            │
│  3️⃣  print() 两个关键参数                                   │
│      ├── end=""：禁止自动换行，chunk 连在一起                 │
│      └── flush=True：强制立即刷新缓冲区                       │
│                                                            │
│  4️⃣  ⚠️ 输出解析器与流式冲突                                 │
│      ├── 原因：Parser 需要完整结果才能格式化                  │
│      ├── 现象：链含 parser → .stream() 也等全部生成完         │
│      └── 解决：去掉 parser（chain = template | llm）         │
│                                                            │
│  5️⃣  实践模式                                               │
│      ├── 纯流式：template | llm → .stream()                │
│      ├── 流式+存储：for 循环中累积 full_text                 │
│      └── 流式+后处理：流式收集 → 手动解析                     │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 12.2 一句话总结

> **换一个方法，加两个参数**。将 `.invoke()` 换成 `.stream()`，`print()` 加上 `end=""` 和 `flush=True`，长回答从"半天不理人"变成"逐字实时输出"。⚠️ 记得：链里不能有输出解析器，否则流式失效。

### 12.3 速记卡

```
┌─────────────────────────────────────────────┐
│            流式输出速记卡                      │
├─────────────────────────────────────────────┤
│                                             │
│  非流式：                                    │
│  result = chain.invoke({...})               │
│  print(result)                              │
│                                             │
│  流式：                                      │
│  for chunk in chain.stream({...}):          │
│      print(chunk.content, end="", flush=True)│
│                                             │
│  ⚠️ 链中不要有 parser！                       │
│  chain = template | llm   ← 这样就够了        │
│                                             │
└─────────────────────────────────────────────┘
```

### 12.4 系列课程定位

```
第一课：LangChain 环境搭建 + 通义接入
第二课：模型选型与平台调研指南
第三课：切换大语言模型（智谱AI 实战）
第四课：使用 Ollama 部署本地大语言模型
第五课：提示词模板（Prompt Template）
第六课：输出解析器（Output Parser）
第七课：链式调用（Chain）
第八课（本课）：流式输出（Streaming）  ← 你在这里
后续：Memory / RAG / Tools & Agents 等高级主题
```

---

*本教学文档基于陈泽鹏老师视频课程（流式输出）整理编写。*  
*本文档涵盖非流式与流式输出的完整对比、`.stream()` 方法使用、print 参数详解，以及输出解析器冲突的解决方案。*
