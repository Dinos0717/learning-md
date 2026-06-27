# LangChain 链式调用（Chain）详解

> 基于陈泽鹏老师视频课程整理编写 · 2026年6月

---

## 目录

- [一、课程背景与目标](#一课程背景与目标)
- [二、什么是链式调用](#二什么是链式调用)
- [三、没有链 vs 有链——代码量对比](#三没有链-vs-有链代码量对比)
- [四、旧版方式：LLMChain（已废弃）](#四旧版方式llmchain已废弃)
- [五、新版方式：管道运算符 `|`（推荐）](#五新版方式管道运算符-推荐)
- [六、旧版 vs 新版完整对比](#六旧版-vs-新版完整对比)
- [七、链式调用的完整工作流程](#七链式调用的完整工作流程)
- [八、实战：从零构建一个链式调用应用](#八实战从零构建一个链式调用应用)
- [九、Chain 的未来——可集成的更多组件](#九chain-的未来可集成的更多组件)
- [十、常见问题与排错指南](#十常见问题与排错指南)
- [十一、课后练习](#十一课后练习)
- [十二、课程小结](#十二课程小结)

---

## 一、课程背景与目标

### 1.1 前情回顾

在前面几节课中，我们已经学会了 LangChain 的三个核心组件：

| 组件 | 类 | 作用 |
|------|-----|------|
| **提示词模板** | `PromptTemplate` | 管理提示词，用户填空，自动生成完整提示词 |
| **大语言模型** | `ChatZhipuAI` / `ChatTongyi` / `ChatOllama` | 接收提示词，返回回复 |
| **输出解析器** | `StructuredOutputParser` / `PydanticOutputParser` | 将模型原始输出转为结构化数据 |

目前我们使用这三个组件的方式是**手动串联**：

```python
# 当前的手动流程（每一步都要自己写）
prompt = template.format(style="通俗易懂", question="勾股定理是什么？")  # 1. 填模板
response = llm.invoke(prompt)                                       # 2. 调模型
result = parser.parse(response.content)                             # 3. 解析结果
```

### 1.2 本节课的核心问题

> **每次都要手动写三步，能不能把它们串在一起，一键执行？**

```
手动方式：
    填模板 → 调模型 → 解析结果  （三步，每次都要写）

链式调用：
    chain.invoke({"style": "...", "question": "..."})  （一步搞定！）
```

### 1.3 本课要掌握的目标

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  目标一：了解什么是链式调用                         │
│         ├── 链式调用的定义                         │
│         ├── 链式调用解决了什么问题                  │
│         └── 链可以串联哪些组件                      │
│                                                 │
│  目标二：掌握链式调用的使用方法                      │
│         ├── 旧版 LLMChain（了解即可，已废弃）       │
│         ├── 新版管道运算符 | （重点掌握）            │
│         └── 用 invoke() 替代废弃的 run()          │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 二、什么是链式调用

### 2.1 直观理解

想象一条**流水线**：

```
┌─────────────────────────────────────────────────────────────┐
│                     链式调用 = 流水线                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  原材料（用户输入）                                            │
│      ↓                                                      │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐             │
│  │ 提示词模板 │ ──→ │ 语言模型  │ ──→ │ 输出解析器│             │
│  │(格式化问题)│     │(生成答案) │     │(结构化输出)│             │
│  └──────────┘     └──────────┘     └──────────┘             │
│      ↓                                                      │
│  最终产品（结构化数据）                                         │
│                                                             │
│  用户只需：扔进原材料 → 坐等成品出来                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

> **链（Chain）**就是将多个组件串在一起。调用时，数据自动依次流过每个组件，无需手动干预。

### 2.2 官方定义

在 LangChain 中，**LLM Chain（大语言模型链）**是一个核心对象：

- 它将**提示词模板**、**语言模型**和**可选的输出解析器**组合在一起
- 形成一个**可重复执行的流程**
- **简化**了与大语言模型的交互

### 2.3 Chain 可以串联的组件

根据课程内容，Chain 目前可以串联的核心组件：

```
当前已学的三大组件：
┌────────────┐    ┌────────────┐    ┌────────────┐
│ 提示词模板  │ ←→ │  语言模型   │ ←→ │ 输出解析器  │
│ Prompt     │    │ ChatModel  │    │ Output     │
│ Template   │    │            │    │ Parser     │
└────────────┘    └────────────┘    └────────────┘

未来还可以加入：
┌────────────┐
│ 记忆组件    │  ← 让模型记住之前的对话历史
│ Memory     │
└────────────┘

以及更多：
├── Tools（工具调用）
├── Retrievers（检索器）
└── ...更多组件
```

> 📌 **Chain 不是必须的**——你可以不用它，手动一步步写也能工作。但用上之后，**代码更简洁、更易维护**。推荐使用。

---

## 三、没有链 vs 有链——代码量对比

### 3.1 手动方式（繁琐）

下面是没有链式调用时的完整代码。注意：每一步都必须**手动执行**。

```python
import os
from langchain_community.chat_models import ChatZhipuAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate

# ── 准备模型 ──
os.environ["ZHIPUAI_API_KEY"] = "你的Key"
llm = ChatZhipuAI(model="glm-4", temperature=0.5)

# ── 定义输出结构 ──
response_schemas = [
    ResponseSchema(name="answer", description="问题的答案"),
    ResponseSchema(name="confidence", description="答案的确信度，0-100的整数"),
]
parser = StructuredOutputParser.from_response_schemas(response_schemas)

# ── 定义提示词模板 ──
template = PromptTemplate(
    template="""
你是{role}，请用{style}的风格回答以下问题。
{format_instructions}

问题：{question}
""",
    input_variables=["role", "style", "question"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# ── 手动执行 ──
# 第1步：填充模板
prompt = template.format(role="数学老师", style="通俗易懂", question="勾股定理是什么？")

# 第2步：调用模型
response = llm.invoke(prompt)

# 第3步：解析结果
result = parser.parse(response.content)

# 第4步：使用结果
print(f"答案：{result['answer']}")
print(f"确信度：{result['confidence']}")
```

**问题**：每次都要写 4 步。而且 `prompt` → `response` → `result` 这些中间变量都暴露在外，代码越写越长。

### 3.2 链式调用方式（简洁）

使用管道运算符 `|`（新版推荐方式）：

```python
# ── 创建链（一次性定义）──
chain = template | llm | parser

# ── 执行链（只需一行！）──
result = chain.invoke({
    "role": "数学老师",
    "style": "通俗易懂",
    "question": "勾股定理是什么？"
})

print(f"答案：{result['answer']}")
print(f"确信度：{result['confidence']}")
```

**效果对比**：

| 方式 | 执行步骤 | 代码行数 | 中间变量 | 维护难度 |
|------|:--------:|:--------:|:--------:|:--------:|
| 手动 | 3-4 步 | ~8 行 | 3 个（prompt, response, result） | 高 |
| **链式** | **1 步** | **3 行** | **0 个** | ⭐ 低 |

---

## 四、旧版方式：LLMChain（已废弃）

### 4.1 旧版代码

在 LangChain 早期版本中，链式调用是通过 `LLMChain` 类实现的：

```python
from langchain.chains import LLMChain

# 创建 LLMChain 对象
chain = LLMChain(
    llm=llm,            # 语言模型
    prompt=template,    # 提示词模板
    output_parser=parser  # 输出解析器（可选）
)

# 用 .run() 执行
result = chain.run(style="通俗易懂", question="勾股定理是什么？")
print(result)
```

### 4.2 ⚠️ 警告信息解读

运行上面的代码后，虽然能正常出结果，但会看到**弃用警告（Deprecation Warning）**：

```
LangChainDeprecationWarning: The class `LLMChain` was deprecated in
LangChain 0.1.7 and will be removed in 1.0. Use RunnableSequence,
e.g., `prompt | llm` instead.

LangChainDeprecationWarning: The method `Chain.run` was deprecated
in LangChain 0.1.0 and will be removed in 1.0. Use `.invoke()` instead.
```

**警告关键信息解读：**

| 废弃项 | 废弃版本 | 删除版本 | 替代方案 |
|--------|:--------:|:--------:|----------|
| `LLMChain` 类 | 0.1.7 | **1.0** | `prompt \| llm \| parser`（管道语法） |
| `.run()` 方法 | 0.1.0 | **1.0** | `.invoke()` |

> 🚨 **重要**：代码能运行 ≠ 没有隐患。`LLMChain` 和 `.run()` 在 LangChain 1.0 版本中会被**彻底删除**。如果你的代码依赖它们，升级 LangChain 版本后会直接报错。**现在就改用新版写法！**

### 4.3 旧版代码能跑但需要立即修改

视频中老师现场演示了这个问题：

```python
# ❌ 旧版写法 —— 现在能跑，但不推荐
chain = LLMChain(llm=llm, prompt=template, output_parser=parser)
result = chain.run(style="通俗易懂", question="勾股定理")

# 能拿到结果，但控制台会出现：
# ⚠️ LangChainDeprecationWarning: ...
# 以后升级到 1.0 就彻底不能用了
```

---

## 五、新版方式：管道运算符 `|`（推荐）

### 5.1 核心语法

新版链式调用使用 Python 的**管道运算符 `|`** 来串联组件：

```python
chain = 组件1 | 组件2 | 组件3
```

- `|` 在这里就是 **"管道"** 的意思——数据从左到右依次流过
- 它是 `RunnableSequence` 的简洁语法
- **不需要**导入 `LLMChain`，直接用 `|` 连接

### 5.2 管道运算符的直观理解

```
template | llm | parser

  ↓         ↓       ↓
模板格式化  →  模型推理  →  解析输出

数据流向：
{"style": "...", "question": "..."}
    ↓ (进入 template → 生成完整提示词字符串)
"你是数学老师，请用通俗易懂的风格..."
    ↓ (进入 llm → 模型推理)
AIMessage(content='{"answer": "...", "confidence": 90}')
    ↓ (进入 parser → 解析)
{"answer": "勾股定理是...", "confidence": 90}
```

### 5.3 完整代码（新版推荐写法）

```python
import os
from langchain_community.chat_models import ChatZhipuAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate

# ============================================================
# 1. 准备模型
# ============================================================
os.environ["ZHIPUAI_API_KEY"] = "你的Key"
llm = ChatZhipuAI(model="glm-4", temperature=0.5)

# ============================================================
# 2. 定义输出结构
# ============================================================
response_schemas = [
    ResponseSchema(name="answer", description="问题的答案"),
    ResponseSchema(name="confidence", description="答案的确信度，0-100的整数"),
]
parser = StructuredOutputParser.from_response_schemas(response_schemas)

# ============================================================
# 3. 定义提示词模板
# ============================================================
template = PromptTemplate(
    template="""
你是{role}，请用{style}的风格回答以下问题。
{format_instructions}

问题：{question}
""",
    input_variables=["role", "style", "question"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# ============================================================
# 4. 创建链（管道语法——新版推荐！）
# ============================================================
chain = template | llm | parser

# ============================================================
# 5. 执行链（用 .invoke()，不用 .run()！）
# ============================================================
result = chain.invoke({
    "role": "数学老师",
    "style": "通俗易懂",
    "question": "勾股定理是什么？"
})

# ============================================================
# 6. 使用结果
# ============================================================
print(f"答案：{result['answer']}")
print(f"确信度：{result['confidence']}")
print(f"数据类型：{type(result)}")  # <class 'dict'>
```

### 5.4 `.invoke()` vs `.run()`——为什么必须改

| 方法 | 状态 | 原因 |
|------|:----:|------|
| `.run()` | ❌ 已废弃（0.1.0起）| 旧的设计，不支持流式、回调等高级特性 |
| **`.invoke()`** | ✅ 推荐 | 新版统一接口，所有 Runnable 对象通用 |

```python
# ❌ 废弃写法
result = chain.run(style="通俗易懂", question="勾股定理")
# → 警告：LangChainDeprecationWarning

# ✅ 推荐写法
result = chain.invoke({
    "role": "数学老师",
    "style": "通俗易懂",
    "question": "勾股定理是什么？"
})
# → 无警告，干净利落
```

### 5.5 管道链的更多写法

```python
# 写法一：三件套（模板 + 模型 + 解析器）—— 最常用
chain = template | llm | parser

# 写法二：只串联模板和模型（不需要解析器时）
chain = template | llm
result = chain.invoke({"role": "老师", "question": "1+1=?"})
# result 是 AIMessage 对象

# 写法三：分步串联，更清晰
step1 = template | llm       # 先串联模板和模型
chain = step1 | parser        # 再串联解析器
# 效果和一步到位完全一样

# 写法四：更多组件
# chain = template | llm | parser | some_other_component
```

---

## 六、旧版 vs 新版完整对比

### 6.1 代码对比

```python
# ╔══════════════════════════════════════════════════════════╗
# ║              旧版写法（LLMChain）—— 已废弃                ║
# ╚══════════════════════════════════════════════════════════╝

from langchain.chains import LLMChain      # ← 需要额外导入

chain = LLMChain(
    llm=llm,
    prompt=template,
    output_parser=parser
)

result = chain.run(                        # ← .run() 已废弃
    style="通俗易懂",
    question="勾股定理是什么？"
)

# ╔══════════════════════════════════════════════════════════╗
# ║              新版写法（管道 |）—— 推荐                     ║
# ╚══════════════════════════════════════════════════════════╝

# 无需额外导入！直接用 | 连接

chain = template | llm | parser            # ← 简洁的管道语法

result = chain.invoke({                    # ← .invoke() 统一接口
    "role": "数学老师",
    "style": "通俗易懂",
    "question": "勾股定理是什么？"
})
```

### 6.2 六维对比表

| 对比维度 | 旧版 LLMChain | 新版管道 `\|` |
|----------|:-------------:|:-------------:|
| **导入** | `from langchain.chains import LLMChain` | **无需额外导入** |
| **创建方式** | `LLMChain(llm=, prompt=, output_parser=)` | `template \| llm \| parser` |
| **执行方法** | `.run()` ❌ 已废弃 | **`.invoke()`** ✅ |
| **参数传递** | `.run(key=value, ...)` 关键字参数 | `.invoke({"key": value})` 字典 |
| **代码行数** | ~6 行 | **~3 行** |
| **当前状态** | ⚠️ 废弃中，1.0 删除 | ✅ 推荐使用 |
| **扩展性** | 有限 | **强**：可以无限 `\|` 连接更多组件 |

### 6.3 何时会遇到旧版代码？

如果在网上搜索 LangChain 教程，你可能会遇到以下**旧版代码**：

```python
# ⚠️ 这些都是旧版写法，不要照抄！

from langchain.chains import LLMChain
chain = LLMChain(llm=llm, prompt=template)
chain.run(question="...")

from langchain.chains import SimpleSequentialChain
from langchain.chains import ConversationChain
# 等等...
```

**识别旧版代码的方法**：
- 看到 `LLMChain` → 旧版
- 看到 `.run()` → 旧版
- 看到 `from langchain.chains import ...` → 需要警惕

**遇到旧版代码怎么办**：
- 理解它的逻辑（和链式调用一样）
- 改成 `|` + `.invoke()` 的新版写法
- 效果完全一样，但不会有过期警告

---

## 七、链式调用的完整工作流程

### 7.1 数据在链中的流转

以 `chain = template | llm | parser` 为例，当调用 `chain.invoke({...})` 时：

```
┌─────────────────────────────────────────────────────────────┐
│                  chain.invoke() 内部执行流程                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  invoke({"role": "数学老师", "style": "通俗易懂",              │
│          "question": "勾股定理是什么？"})                     │
│       ↓                                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 第1步：template 处理                                  │    │
│  │                                                      │    │
│  │ 输入：{"role": "数学老师", "style": "通俗易懂",         │    │
│  │        "question": "勾股定理是什么？"}                 │    │
│  │        + format_instructions（partial_variables 自动补）│    │
│  │                                                      │    │
│  │ 输出："你是数学老师，请用通俗易懂的风格回答以下问题。      │    │
│  │        [format_instructions]                         │    │
│  │        问题：勾股定理是什么？"                           │    │
│  └─────────────────────────────────────────────────────┘    │
│       ↓ 自动传递给下一步                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 第2步：llm 处理                                       │    │
│  │                                                      │    │
│  │ 输入：格式化后的提示词字符串                              │    │
│  │                                                      │    │
│  │ 输出：AIMessage(content='{"answer": "...",            │    │
│  │                          "confidence": 90}')         │    │
│  └─────────────────────────────────────────────────────┘    │
│       ↓ 自动传递给下一步                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 第3步：parser 处理                                    │    │
│  │                                                      │    │
│  │ 输入：AIMessage 对象（自动提取 .content）               │    │
│  │                                                      │    │
│  │ 输出：{"answer": "勾股定理是直角三角形中...",           │    │
│  │        "confidence": 90}                             │    │
│  └─────────────────────────────────────────────────────┘    │
│       ↓                                                     │
│  返回给用户：result = {"answer": "...", "confidence": 90}     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 关键认知

> **链的核心价值**：你只需要定义链的结构（有哪些组件、什么顺序），然后调用 `.invoke()`。中间的数据传递、格式转换、错误处理，LangChain 全部自动完成。

---

## 八、实战：从零构建一个链式调用应用

### 8.1 场景

构建一个**智能问答分析器**，输入角色、风格和问题，输出：
- 答案内容（answer）
- 确信度评分（confidence）

### 8.2 完整代码（新版推荐）

```python
import os
from langchain_community.chat_models import ChatZhipuAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate

# ============================================================
# Step 1: 准备模型
# ============================================================
os.environ["ZHIPUAI_API_KEY"] = "你的Key"
llm = ChatZhipuAI(model="glm-4", temperature=0.5)

# ============================================================
# Step 2: 定义输出结构
# ============================================================
response_schemas = [
    ResponseSchema(name="answer", description="问题的答案"),
    ResponseSchema(name="confidence", description="答案的确信度，0-100的整数"),
]
parser = StructuredOutputParser.from_response_schemas(response_schemas)

# ============================================================
# Step 3: 定义提示词模板
# ============================================================
template = PromptTemplate(
    template="""
你是{role}，请用{style}的风格回答以下问题。

{format_instructions}

问题：{question}
""",
    input_variables=["role", "style", "question"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# ============================================================
# Step 4: 创建链
# ============================================================
chain = template | llm | parser

# ============================================================
# Step 5: 封装为函数（方便复用）
# ============================================================
def ask_with_confidence(role, style, question):
    """执行链式调用，返回答案和确信度"""
    return chain.invoke({
        "role": role,
        "style": style,
        "question": question
    })

# ============================================================
# Step 6: 测试
# ============================================================
# 测试一
result1 = ask_with_confidence(
    role="数学老师",
    style="通俗易懂",
    question="勾股定理是什么？"
)
print(f"【测试一】答案：{result1['answer']}")
print(f"         确信度：{result1['confidence']}%")
print()

# 测试二
result2 = ask_with_confidence(
    role="历史老师",
    style="生动有趣",
    question="鸦片战争的起因是什么？"
)
print(f"【测试二】答案：{result2['answer']}")
print(f"         确信度：{result2['confidence']}%")
print()

# 测试三：同一个链，完全不同的参数
result3 = ask_with_confidence(
    role="资深Python工程师",
    style="简洁专业，附带代码示例",
    question="什么是装饰器？"
)
print(f"【测试三】答案：{result3['answer']}")
print(f"         确信度：{result3['confidence']}%")
```

### 8.3 效果展示

```
【测试一】答案：勾股定理是直角三角形中的一个基本定理...
         确信度：95%

【测试二】答案：鸦片战争，简单来说就是19世纪中期...
         确信度：90%

【测试三】答案：装饰器是Python中一种特殊的语法...
         确信度：92%
```

> 🎉 **一个链，三个完全不同的问题，全部自动完成——模板填充 → 模型推理 → 结果解析。**

---

## 九、Chain 的未来——可集成的更多组件

### 9.1 当前已学的组件组合

```
template | llm | parser
    ↑       ↑       ↑
  提示词   模型    解析器
```

### 9.2 未来可以加入的组件

视频中老师预告了 Chain 可以串联更多组件：

```
┌──────────────────────────────────────────────────────────┐
│              未来更强大的链                                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  memory | template | llm | parser | ...                  │
│     ↑                                              │
│  记忆组件：让模型记住对话历史                           │
│  • 自动保存之前的问答                                   │
│  • 在后续对话中引用上下文                               │
│  • 实现真正的"多轮对话"                                 │
│                                                          │
│  还有更多：                                              │
│  ├── Retriever（检索器）：从文档库中检索相关内容           │
│  ├── Tools（工具）：让模型调用外部API                    │
│  └── Router（路由器）：根据输入自动选择不同的处理链        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

> 📌 Memory 组件将在后续课程中详细讲解。核心思想就是：**任何 LangChain 组件都可以用 `|` 串进链里**。

---

## 十、常见问题与排错指南

### 10.1 错误速查表

| 错误/警告 | 原因 | 解决方法 | 优先级 |
|-----------|------|----------|:------:|
| `LangChainDeprecationWarning: LLMChain was deprecated` | 用了旧版 `LLMChain` 类 | 改用 `template \| llm \| parser` | 🔴高 |
| `LangChainDeprecationWarning: Chain.run was deprecated` | 用了 `.run()` 方法 | 改用 `.invoke({...})` | 🔴高 |
| `ImportError: cannot import name 'LLMChain'` | LangChain 新版本已删除 LLMChain | 改用管道语法 `\|` | 🔴高 |
| `KeyError: 'format_instructions'` | 模板有 `{format_instructions}` 但没在 `partial_variables` 中指定 | 在 `PromptTemplate` 中设置 `partial_variables` | 🟡中 |
| `TypeError: invoke() missing 1 required positional argument` | `.invoke()` 没传参 | `.invoke()` 需要一个字典参数 | 🟡中 |
| 链创建成功但 `.invoke()` 返回的不是预期格式 | 漏了 parser 组件 | 链末尾加上 `\| parser` | 🟡中 |
| `AttributeError: 'str' object has no attribute 'content'` | 把字典直接传给 llm 而不是链 | 确保是 `chain.invoke({...})` 而不是 `llm.invoke({...})` | 🟡中 |
| 管道符号语法错误 | Python 版本太低 | Python 3.9+ 才支持 `\|` 运算符重载 | 🟢低 |

### 10.2 排查流程

```
链式调用出问题？

第一步：确认用的是新版还是旧版？
    ├── 代码中有 LLMChain？ → 立即改用 template | llm | parser
    └── 已经用 | 语法？ → 往下看

第二步：检查链的组件顺序
    chain = template | llm | parser
            ↑ 先格式化  ↑ 再推理  ↑ 最后解析
    顺序不能乱！

第三步：检查 .invoke() 的参数
    chain.invoke({"key": "value"})  ← 必须是字典
    字典的 key 必须和 input_variables 一致

第四步：检查输出
    有 parser：返回 dict
    无 parser：返回 AIMessage（需要 .content 提取）
```

### 10.3 版本兼容性说明

| LangChain 版本 | LLMChain | `.run()` | 管道 `\|` | `.invoke()` |
|:-------------:|:--------:|:--------:|:---------:|:-----------:|
| < 0.1.0 | ✅ 可用 | ✅ 可用 | ❌ | ❌ |
| 0.1.0 ~ 0.1.7 | ⚠️ 可用但有警告 | ⚠️ 废弃警告 | ✅ | ✅ |
| 0.1.7 ~ 0.3.x | ⚠️ 废弃警告 | ❌ 可能报错 | ✅ | ✅ |
| >= 1.0（未来） | ❌ 已删除 | ❌ 已删除 | ✅ | ✅ |

> 📌 **建议**：现在就全部改用 `|` + `.invoke()`，避免将来升级版本时批量修改代码。

---

## 十一、课后练习

### 练习一：基础链式调用

> 用管道语法 `|` 创建一个链，包含：PromptTemplate + ChatZhipuAI + StructuredOutputParser。输出结构包含 `summary`（总结）和 `keywords`（关键词列表）。

**验收标准：**
- [ ] 使用 `|` 语法创建链，不使用 `LLMChain`
- [ ] 使用 `.invoke()` 执行，不使用 `.run()`
- [ ] 无 DeprecationWarning 警告
- [ ] 正确输出结构化的 dict

### 练习二：旧版代码迁移

> 下面是一段旧版代码，请将其改写为新版写法：

```python
# 旧版代码（请改写）
from langchain.chains import LLMChain

chain = LLMChain(llm=llm, prompt=template, output_parser=parser)
result = chain.run(topic="人工智能", length="简短")
```

| 对比维度 | 旧版 | 你的新版 |
|----------|------|----------|
| 导入语句 | | |
| 创建链 | | |
| 执行链 | | |

### 练习三：有无链对比

> 用同一个场景（翻译助手），分别用**手动方式**和**链式调用方式**实现：
>
> 输入：`text`（待翻译文本）、`target_lang`（目标语言）
> 输出：`original`（原文）、`translated`（翻译结果）、`confidence`（翻译质量评分）

**要求：**
- 手动方式：写满 3 步（填模板 → 调模型 → 解析结果）
- 链式方式：用 `|` 语法一步完成
- 统计两种方式的代码行数，填入下表：

| 方式 | 创建代码行数 | 每次调用行数 | 总可读性（1-5） |
|------|:-----------:|:-----------:|:---------------:|
| 手动 | | | |
| 链式 | | | |

### 练习四：多链复用

> 创建两个不同的链（共享同一个 llm）：
>
> **链A（问答链）**：回答问题时，输出 `answer` + `confidence`
> **链B（翻译链）**：翻译文本时，输出 `original` + `translated`
>
> 分别调用两个链，验证它们互不干扰。

**提示**：

```python
# 共享同一个 llm
llm = ChatZhipuAI(model="glm-4", temperature=0.5)

# 链A：问答
qa_chain = qa_template | llm | qa_parser

# 链B：翻译
translate_chain = translate_template | llm | translate_parser

# 分别调用
result_a = qa_chain.invoke({...})
result_b = translate_chain.invoke({...})
```

### 练习五：探索废弃类的替代方案

> 在网上搜索 LangChain 教程时，你可能会遇到以下旧版类。请查找它们的新版替代方案：

| 旧版类/方法 | 状态 | 新版替代 |
|------------|:----:|----------|
| `LLMChain` | 废弃 | |
| `SimpleSequentialChain` | 废弃 | |
| `ConversationChain` | 废弃 | |
| `.run()` | 废弃 | |
| `.arun()` | 废弃 | |

---

## 十二、课程小结

### 12.1 本课核心知识图谱

```
┌────────────────────────────────────────────────────────────┐
│               链式调用核心知识体系                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  什么是链式调用？                                       │
│      ├── 将多个组件串在一起，自动依次执行                      │
│      ├── 核心组件：提示词模板 + 语言模型 + 输出解析器          │
│      ├── 未来可扩展：Memory、Tools、Retriever...              │
│      └── 不是必须的，但强烈推荐使用                           │
│                                                            │
│  2️⃣  旧版 vs 新版                                           │
│      ├── 旧版 LLMChain：0.1.7 废弃，1.0 删除               │
│      │   chain = LLMChain(llm=, prompt=, output_parser=)   │
│      │   chain.run(key=value)                              │
│      │                                                    │
│      └── 新版管道 |：当前推荐 ✅                              │
│          chain = template | llm | parser                   │
│          chain.invoke({"key": "value"})                    │
│                                                            │
│  3️⃣  管道运算符 | 的本质                                    │
│      ├── Python 语法，数据从左到右流动                        │
│      ├── 等价于 RunnableSequence                           │
│      └── 可以无限串联：a | b | c | d | ...                 │
│                                                            │
│  4️⃣  invoke() 替代 run()                                    │
│      ├── .run() 在 0.1.0 废弃                              │
│      ├── .invoke({"key": "value"}) 统一接口                 │
│      └── 传字典而不是关键字参数                              │
│                                                            │
│  5️⃣  链的核心价值                                            │
│      定义一次，反复使用                                       │
│      一个 .invoke() 替代三步手动操作                          │
│      代码更简洁、更易维护、更不容易出错                         │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 12.2 一句话总结

> **链式调用 = 用 `|` 把组件串起来，用 `.invoke()` 一键执行。** 旧版的 `LLMChain` 和 `.run()` 已经废弃，新的管道语法更简洁、更现代。记住：`template | llm | parser` → `chain.invoke({...})`。

### 12.3 新旧写法速记卡

```
┌─────────────────────────────────────────┐
│          链式调用速记卡                    │
├─────────────────────────────────────────┤
│                                         │
│  旧版（❌ 不要用了）：                    │
│  chain = LLMChain(llm, prompt, parser)  │
│  result = chain.run(x=1, y=2)          │
│                                         │
│  新版（✅ 用这个）：                      │
│  chain = template | llm | parser        │
│  result = chain.invoke({"x": 1, "y": 2})│
│                                         │
└─────────────────────────────────────────┘
```

### 12.4 系列课程定位

```
第一课：LangChain 环境搭建 + 通义接入
第二课：模型选型与平台调研指南
第三课：切换大语言模型（智谱AI 实战）
第四课：使用 Ollama 部署本地大语言模型
第五课：提示词模板（Prompt Template）
第六课：输出解析器（Output Parser）
第七课（本课）：链式调用（Chain）  ← 你在这里
后续：Memory / RAG / Tools & Agents 等高级主题
```

---

*本教学文档基于陈泽鹏老师视频课程（链式调用）整理编写。*  
*本文档涵盖旧版 LLMChain 与新版管道语法的完整对比、迁移指南及实战代码。*
