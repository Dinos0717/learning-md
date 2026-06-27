# LangChain 提示词模板（Prompt Template）详解

> 基于陈泽鹏老师视频课程整理编写 · 2026年6月

---

## 目录

- [一、课程背景与目标](#一课程背景与目标)
- [二、为什么需要提示词模板](#二为什么需要提示词模板)
- [三、什么是提示词模板](#三什么是提示词模板)
- [四、PromptTemplate——基础字符串模板](#四prompttemplate基础字符串模板)
- [五、ChatPromptTemplate——对话角色模板](#五chatprompttemplate对话角色模板)
- [六、两种模板的对比与选择](#六两种模板的对比与选择)
- [七、模板变量填充的多种方式](#七模板变量填充的多种方式)
- [八、完整代码实例](#八完整代码实例)
- [九、实战：从零搭建一个提示词模板应用](#九实战从零搭建一个提示词模板应用)
- [十、提示词工程最佳实践](#十提示词工程最佳实践)
- [十一、常见问题与排错指南](#十一常见问题与排错指南)
- [十二、课后练习](#十二课后练习)
- [十三、课程小结](#十三课程小结)

---

## 一、课程背景与目标

### 1.1 前情回顾

在前面几节课，我们已经学会了：

- 通过 LangChain 创建大语言模型应用
- 将自己的需求转换成文字 → 发送给模型 → 获取回复

基本调用模式：

```python
llm = ChatZhipuAI(model="glm-4")
response = llm.invoke("夏天适合吃什么水果？")
print(response.content)
```

### 1.2 问题场景：提示词越来越长

随着使用深入，我们会遇到以下几种情况：

| 场景 | 问题 | 举例 |
|------|------|------|
| **要求格式** | 想让模型按指定格式回复 | "请用 JSON 格式返回，包含 name、price、description 三个字段" |
| **要求准确** | 想让模型回复更精确 | "你是资深营养师，请从营养成分、适合人群、食用禁忌三个维度分析" |
| **需求复杂** | 需求本身就很复杂 | "以专业旅游专家的角色，根据本月天气情况，从预算、天数、适合人群三个角度推荐旅游目的地" |

这些情况下，提示词会写得很长：

```python
# 一个复杂需求的提示词可能长这样 😰
question = """
你是一个资深的旅游规划专家，拥有10年以上的行业经验。
请你以通俗易懂的语言，根据以下要求推荐旅游目的地：

1. 出发地：北京
2. 预算：每人5000元以内
3. 天数：3-5天
4. 季节：夏季
5. 偏好：自然风光，避开人多的景点
6. 请从以下几个维度分析：
   - 推荐目的地及理由
   - 大致费用明细
   - 最佳出行时间
   - 注意事项
"""
```

### 1.3 本节课的核心问题

> **能不能简化输入的提示词？**
>
> 不想每次输入一大堆文字，但又想让模型按照指定的格式、准确、有条理地回复，需求还很复杂——能不能两全其美？

**答案**：可以。使用 **提示词模板（Prompt Template）**。

### 1.4 本课要掌握的两个核心目标

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  目标一：了解提示词模板的作用                              │
│         ├── 它解决什么问题？                              │
│         ├── 它的工作原理是什么？                           │
│         └── 它能带来什么好处？                             │
│                                                         │
│  目标二：掌握提示词模板的使用方法                           │
│         ├── PromptTemplate（基础字符串模板）               │
│         ├── ChatPromptTemplate（对话角色模板）             │
│         ├── 两种变量填充方式                              │
│         └── 能独立编写模板代码                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 二、为什么需要提示词模板

### 2.1 一个直观的类比

想象你要让不同的学生写一篇作文。每次都从头开始给学生讲要求会很累。你可能会做一个**模板**：

```
模板：
"请以{角色}的身份，用{风格}的语言，围绕{主题}写一篇{字数}字的文章。"

使用时只需要填空：
"请以【记者】的身份，用【简洁客观】的语言，围绕【人工智能发展】写一篇【800】字的文章。"
"请以【诗人】的身份，用【浪漫抒情】的语言，围绕【春天】写一篇【200】字的文章。"
```

对于大语言模型，**提示词模板就是做这件事的**。

### 2.2 没有模板 vs 有模板

**没有模板（每次都重写完整提示词）：**

```python
# 用户A的提问
q1 = "你是数学老师，请用通俗易懂的风格，讲一下勾股定理是什么？"

# 用户B的提问（又要重写一遍角色和风格描述）
q2 = "你是历史老师，请用生动有趣的风格，讲一下鸦片战争是什么？"

# 用户C的提问（又双叒要重写...）
q3 = "你是物理老师，请用严谨专业的风格，讲一下相对论是什么？"
# 😰 每次都要写"你是XX老师，请用XX的风格，讲一下XX"
```

**有模板（一次定义，反复使用）：**

```python
# 定义模板（只写一次）
template = "你是{role}，请用{style}的风格，讲一下{question}是什么？"

# 用户A填空
prompt1 = template.format(role="数学老师", style="通俗易懂", question="勾股定理")

# 用户B填空
prompt2 = template.format(role="历史老师", style="生动有趣", question="鸦片战争")

# 用户C填空
prompt3 = template.format(role="物理老师", style="严谨专业", question="相对论")
# 🎉 只需要填三个空！
```

### 2.3 提示词模板的三大好处

```
┌──────────────────────────────────────────────────────────┐
│                提示词模板的三大好处                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1️⃣  简化用户输入                                          │
│     用户只需要填几个变量，不需要重复写大段文字               │
│                                                          │
│  2️⃣  提升输出准确性                                         │
│     模板预定义了回答的维度和结构，                          │
│     模型不容易跑偏或遗漏要点                                │
│                                                          │
│  3️⃣  保证一致性                                            │
│     同一模板生成的所有提示词结构相同，                       │
│     不同用户得到的回复风格和格式保持一致                     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 三、什么是提示词模板

### 3.1 官方定义

> **提示词模板（Prompt Template）**是 LangChain 的核心组件之一，主要用于构建和管理与大语言模型交互的提示词。

它的作用是：

```
用户输入（动态数据）
        +
预定义模板（固定结构）
        ↓
结构化的提示词（发给模型）
        ↓
模型输出更准确、更一致
```

### 3.2 工作原理图解

```
┌─────────────────────────────────────────────────────────────┐
│                    提示词模板工作流程                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  第一步：定义模板（由开发者预先写好，只写一次）                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ "你是{role}，请用{style}的风格，回答：{question}"      │    │
│  │        ↑         ↑                   ↑               │    │
│  │      变量1     变量2               变量3              │    │
│  │   （占位符，等待用户填充）                             │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  第二步：用户填空（填入具体内容）                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ role    = "资深营养师"                                │    │
│  │ style   = "通俗易懂"                                 │    │
│  │ question = "夏天应该怎么饮食？"                        │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  第三步：自动拼接（模板引擎完成）                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ "你是资深营养师，请用通俗易懂的风格，                   │    │
│  │  回答：夏天应该怎么饮食？"                             │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  第四步：发给模型 → 得到结构化回复                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 LangChain 中的两种提示词模板

LangChain 提供了两种主要的提示词模板类：

| 模板类型 | 类名 | 适用场景 | 导入路径 |
|----------|------|----------|----------|
| **基础字符串模板** | `PromptTemplate` | 简单的单角色提示词 | `from langchain.prompts import PromptTemplate` |
| **对话角色模板** | `ChatPromptTemplate` | 多角色对话（系统+用户） | `from langchain_core.prompts import ChatPromptTemplate` |

> 📌 视频中老师展示了这两种模板的用法。下面逐一详解。

---

## 四、PromptTemplate——基础字符串模板

### 4.1 什么时候用它？

适合**单人单次提问**的场景。提示词只有一个角色（没有区分系统消息和用户消息）。

```
适用场景：
├── 简单的问答
├── 翻译任务
├── 文本总结
└── 单轮格式化输出
```

### 4.2 完整语法

```python
from langchain.prompts import PromptTemplate

# 第一步：定义模板字符串
# 变量用 {变量名} 表示
template_string = "你是{role}，请用{style}的风格，回答问题：{question}"

# 第二步：创建模板对象
prompt_template = PromptTemplate.from_template(template_string)

# 第三步：填充变量（生成完整提示词）
filled_prompt = prompt_template.format(
    role="数学老师",
    style="通俗易懂",
    question="勾股定理是什么？"
)

# 第四步：发送给模型
response = llm.invoke(filled_prompt)
print(response.content)
```

### 4.3 代码详解

#### 4.3.1 导入

```python
from langchain.prompts import PromptTemplate
```

| 路径段 | 说明 |
|--------|------|
| `langchain` | LangChain 主包 |
| `prompts` | 提示词相关模块 |
| `PromptTemplate` | 基础字符串模板类 |

#### 4.3.2 定义模板字符串

```python
template_string = "你是{role}，请用{style}的风格，回答问题：{question}"
```

关键语法：
- `{变量名}` = **占位符**，花括号里的内容就是变量名
- 变量名可以自定义（`role`、`style`、`question` 都可以换成别的名字）
- 变量的**个数和名称**由你自己决定

```
模板中可以定义任意数量的变量：

1个变量： "翻译成{language}：{text}"
3个变量： "你是{role}，用{style}风格，回答：{question}"
5个变量： "{role}以{style}风格，从{dim1}、{dim2}、{dim3}三个角度分析{question}"
```

#### 4.3.3 创建模板对象

```python
prompt_template = PromptTemplate.from_template(template_string)
```

- `from_template()` 是 `PromptTemplate` 的**类方法**，接收一个字符串，返回模板对象
- 它会**自动识别**字符串中所有的 `{变量名}` 占位符
- 不需要手动声明有哪些变量

#### 4.3.4 填充变量——方式一：`.format()`

```python
filled_prompt = prompt_template.format(
    role="数学老师",
    style="通俗易懂",
    question="勾股定理是什么？"
)
```

`.format()` 方法将具体值填入占位符，生成完整的提示词字符串：

```
输入：  role="数学老师", style="通俗易懂", question="勾股定理是什么？"

输出：  "你是数学老师，请用通俗易懂的风格，回答问题：勾股定理是什么？"
```

#### 4.3.5 发送给模型

```python
response = llm.invoke(filled_prompt)
print(response.content)
```

模板填充完毕后，剩下的调用方式和之前完全一样，不需要任何改变。

### 4.4 完整代码示例

以智谱AI 为例的完整代码：

```python
import os
from langchain_community.chat_models import ChatZhipuAI
from langchain.prompts import PromptTemplate

# ============================================================
# 准备模型
# ============================================================
os.environ["ZHIPUAI_API_KEY"] = "你的API_Key"
llm = ChatZhipuAI(model="glm-4", temperature=0.5)

# ============================================================
# 定义模板
# ============================================================
template_string = "你是{role}，请用{style}的风格，回答问题：{question}"

prompt_template = PromptTemplate.from_template(template_string)

# ============================================================
# 用户只需填写这三个变量
# ============================================================
filled_prompt = prompt_template.format(
    role="数学老师",
    style="通俗易懂",
    question="勾股定理是什么？"
)

# ============================================================
# 发送给模型
# ============================================================
response = llm.invoke(filled_prompt)
print(response.content)
```

**可能的输出：**

> 勾股定理，简单来说就是直角三角形的一个基本规律：两条直角边的平方和等于斜边的平方。用公式表示就是 a² + b² = c²。比如一个直角三角形，两条直角边分别是3和4，那么斜边就是5，因为 3² + 4² = 9 + 16 = 25 = 5²……

---

## 五、ChatPromptTemplate——对话角色模板

### 5.1 什么时候用它？

适合**区分角色的多轮对话**场景。可以把系统设定（System）和用户提问（User）分开管理。

```
适用场景：
├── 需要给模型设定明确的角色和行为规则
├── 需要区分"系统指令"和"用户输入"
├── 多轮对话管理
└── 复杂应用（需要 SystemMessage + HumanMessage 分离）
```

### 5.2 为什么需要区分角色？

在前面的课程中我们学过，消息系统有三种类型：

| 消息类型 | 作用 | 谁写 |
|----------|------|------|
| `SystemMessage` | 角色设定、行为规则 | **开发者预定义**（固定在模板中） |
| `HumanMessage` | 用户的具体问题 | **用户输入**（动态变化） |
| `AIMessage` | 模型的回复 | 模型生成 |

`ChatPromptTemplate` 可以分别管理 System 和 Human 部分：

```
ChatPromptTemplate 帮你做的事：

SystemMessage 部分（固定结构）：
    "你是{role}，请用{style}的风格回答问题。"
    ↑ 这部分的框架是固定的，role和style是用户可填的变量

HumanMessage 部分（用户输入）：
    "{question}"
    ↑ 这是用户每次具体要问的问题
```

### 5.3 完整语法

```python
from langchain_core.prompts import ChatPromptTemplate

# 第一步：定义模板（区分 system 和 human 两个角色）
chat_template = ChatPromptTemplate.from_messages([
    ("system", "你是{role}，请用{style}的风格回答问题。"),
    ("human", "请{style}地解释：{question}")
])

# 第二步：填充变量
filled_messages = chat_template.invoke({
    "role": "数学老师",
    "style": "生动有趣",
    "question": "勾股定理是什么？"
})

# filled_messages 是一个消息列表，内容为：
# [
#     SystemMessage(content="你是数学老师，请用生动有趣的风格回答问题。"),
#     HumanMessage(content="请生动有趣地解释：勾股定理是什么？")
# ]

# 第三步：发送给模型
response = llm.invoke(filled_messages)
print(response.content)
```

### 5.4 代码详解

#### 5.4.1 导入

```python
from langchain_core.prompts import ChatPromptTemplate
```

注意这个导入路径是 `langchain_core.prompts`，不是 `langchain.prompts`。这是 LangChain 核心库中的类。

> 💡 记不住路径也没关系：在 VS Code 中输入 `from langchain_core.prompts import ` 后，编辑器会自动提示 `ChatPromptTemplate`。

#### 5.4.2 定义模板——`from_messages()`

```python
chat_template = ChatPromptTemplate.from_messages([
    ("system", "你是{role}，请用{style}的风格回答问题。"),
    ("human", "请{style}地解释：{question}")
])
```

**`from_messages()` 的参数是一个列表，列表中每个元素是一个元组：**

```
[("角色", "模板字符串"), ("角色", "模板字符串"), ...]

角色可以是：
├── "system"  → 系统消息（角色设定）
├── "human"   → 用户消息（具体问题）
├── "ai"      → AI消息（历史对话，不常用）
└── "placeholder" → 占位消息（高级用法）
```

**结构解读：**

```python
# 第1个元组：SystemMessage
("system", "你是{role}，请用{style}的风格回答问题。")
#          ↑ 模板中也可以包含变量

# 第2个元组：HumanMessage
("human", "请{style}地解释：{question}")
#         ↑ 用户消息中也可以包含变量
```

> 💡 注意：同一个变量（如 `style`）可以出现在多个消息中。填充时所有出现的地方都会被替换。

#### 5.4.3 填充变量

`ChatPromptTemplate` 支持两种填充方式：

**方式一：`.invoke()` 传入字典（视频中的方式）**

```python
filled_messages = chat_template.invoke({
    "role": "数学老师",
    "style": "生动有趣",
    "question": "勾股定理是什么？"
})
```

**方式二：`.format_messages()` 传入关键字参数**

```python
filled_messages = chat_template.format_messages(
    role="数学老师",
    style="生动有趣",
    question="勾股定理是什么？"
)
```

两种方式效果相同，`.invoke()` 使用字典更灵活，`.format_messages()` 使用关键字参数更直观。

### 5.5 完整代码示例

```python
import os
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.prompts import ChatPromptTemplate

# ============================================================
# 准备模型
# ============================================================
os.environ["ZHIPUAI_API_KEY"] = "你的API_Key"
llm = ChatZhipuAI(model="glm-4", temperature=0.5)

# ============================================================
# 定义对话模板（区分 system 和 human）
# ============================================================
chat_template = ChatPromptTemplate.from_messages([
    ("system", "你是{role}，请用{style}的风格回答问题。"),
    ("human", "请{style}地解释：{question}")
])

# ============================================================
# 用户填空（方式一：.invoke() + 字典）
# ============================================================
filled_messages = chat_template.invoke({
    "role": "数学老师",
    "style": "生动有趣",
    "question": "勾股定理是什么？"
})

# ============================================================
# 发送给模型
# ============================================================
response = llm.invoke(filled_messages)
print(response.content)
```

**可能的输出：**

> 嘿！勾股定理就像数学界的"黄金法则"！想象你有一个直角三角形，两条直角边就像两个好朋友，斜边就像他们手拉手。神奇的是：两个好朋友各自"平方"（就是乘以自己）再加起来，刚好等于那条斜边的平方！用公式就是 a² + b² = c²。古人几千年前就发现了这个秘密，现在你也能轻松掌握啦！😄

---

## 六、两种模板的对比与选择

### 6.1 区别对比表

| 对比维度 | `PromptTemplate` | `ChatPromptTemplate` |
|----------|:----------------:|:--------------------:|
| **导入路径** | `langchain.prompts` | `langchain_core.prompts` |
| **模板结构** | 单一字符串 | 多条消息（System + Human + …） |
| **角色支持** | 单角色 | **多角色**（system / human / ai） |
| **填充方式** | `.format(x=..., y=...)` | `.invoke({...})` 或 `.format_messages(...)` |
| **填充结果** | 一个**字符串** | 一个**消息列表** |
| **复杂度** | ⭐ 简单 | ⭐⭐ 稍复杂 |
| **适用场景** | 简单问答、单轮对话 | 带角色设定的复杂对话 |

### 6.2 什么时候用哪个？

```
只需要填空提问？
    ├── 是 → 用 PromptTemplate（简单直接）
    └── 否 → 需要区分"系统设定"和"用户输入"？
                ├── 是 → 用 ChatPromptTemplate（结构清晰）
                └── 否 → 用 PromptTemplate
```

**简单判断法则：**

```
模板中是否需要 SystemMessage？
    ├── 不需要 → PromptTemplate
    └── 需要   → ChatPromptTemplate
```

### 6.3 代码对比

```python
# ────────────────────────────────────────────
# PromptTemplate：生成一个字符串
# ────────────────────────────────────────────
from langchain.prompts import PromptTemplate

pt = PromptTemplate.from_template("你是{role}，回答：{q}")
result = pt.format(role="老师", q="1+1=?")
print(type(result))  # <class 'str'>
print(result)        # "你是老师，回答：1+1=?"

# ────────────────────────────────────────────
# ChatPromptTemplate：生成一个消息列表
# ────────────────────────────────────────────
from langchain_core.prompts import ChatPromptTemplate

ct = ChatPromptTemplate.from_messages([
    ("system", "你是{role}"),
    ("human", "{q}")
])
result = ct.invoke({"role": "老师", "q": "1+1=?"})
print(type(result))  # <class 'list'>  ← 注意是列表！
print(result)
# [
#     SystemMessage(content="你是老师"),
#     HumanMessage(content="1+1=?")
# ]
```

---

## 七、模板变量填充的多种方式

### 7.1 PromptTemplate 的填充方式

**方式一：`.format()` 关键字参数（视频中演示）**

```python
template = PromptTemplate.from_template("你是{role}，回答：{question}")

# 关键字参数方式
prompt = template.format(role="数学老师", question="勾股定理是什么？")
```

**方式二：`.invoke()` 字典方式**

```python
# 字典方式
prompt = template.invoke({"role": "数学老师", "question": "勾股定理是什么？"})
```

### 7.2 ChatPromptTemplate 的填充方式

**方式一：`.invoke()` 传入字典（视频中演示）**

```python
template = ChatPromptTemplate.from_messages([
    ("system", "你是{role}，用{style}风格回答问题。"),
    ("human", "{question}")
])

filled = template.invoke({
    "role": "数学老师",
    "style": "生动有趣",
    "question": "勾股定理是什么？"
})
```

**方式二：`.format_messages()` 关键字参数**

```python
filled = template.format_messages(
    role="数学老师",
    style="生动有趣",
    question="勾股定理是什么？"
)
```

### 7.3 填充方式速查表

| 模板类型 | 填充方法 | 参数形式 | 返回类型 |
|----------|----------|----------|----------|
| `PromptTemplate` | `.format(key=value, ...)` | 关键字参数 | `str` |
| `PromptTemplate` | `.invoke({"key": value})` | 字典 | `str` |
| `ChatPromptTemplate` | `.invoke({"key": value})` | 字典 | `list[Message]` |
| `ChatPromptTemplate` | `.format_messages(key=value)` | 关键字参数 | `list[Message]` |

### 7.4 ⚠️ 变量名必须完全匹配

这是视频中老师强调的一个重要点：

```python
# 模板中定义的变量名
template = PromptTemplate.from_template("你是{role}，用{style}风格回答：{question}")

# ✅ 正确：变量名完全匹配
template.format(role="数学老师", style="通俗易懂", question="勾股定理")
# ✅ 也可以多传（多余的会被忽略，但建议不要多传）

# ❌ 错误：变量名不匹配 → 报错！
template.format(role="数学老师", style="通俗易懂", q="勾股定理")
#                                                   ↑ 模板中是 question，这里写成了 q
# KeyError: 'question'
```

> 📌 **原则**：填充时使用的变量名必须和模板中 `{变量名}` 定义的**完全一致**，包括大小写。

---

## 八、完整代码实例

### 8.1 实例一：PromptTemplate 完整演示

```python
import os
from langchain_community.chat_models import ChatZhipuAI
from langchain.prompts import PromptTemplate

# ── 准备模型 ──
os.environ["ZHIPUAI_API_KEY"] = "你的Key"
llm = ChatZhipuAI(model="glm-4", temperature=0.5)

# ── 定义模板（只写一次）──
template = PromptTemplate.from_template(
    "你是{role}，请用{style}的风格，从{dim1}、{dim2}、{dim3}三个维度，"
    "回答以下问题：{question}"
)

# ── 测试1：数学问题 ──
prompt1 = template.format(
    role="大学数学教授",
    style="严谨学术",
    dim1="定义", dim2="推导过程", dim3="实际应用",
    question="什么是傅里叶变换？"
)
response1 = llm.invoke(prompt1)
print("=== 回答1 ===")
print(response1.content)
print()

# ── 测试2：历史问题（换几个变量值即可）──
prompt2 = template.format(
    role="中学历史老师",
    style="通俗易懂",
    dim1="时代背景", dim2="主要人物", dim3="历史影响",
    question="鸦片战争的起因是什么？"
)
response2 = llm.invoke(prompt2)
print("=== 回答2 ===")
print(response2.content)
```

### 8.2 实例二：ChatPromptTemplate 完整演示

```python
import os
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.prompts import ChatPromptTemplate

# ── 准备模型 ──
os.environ["ZHIPUAI_API_KEY"] = "你的Key"
llm = ChatZhipuAI(model="glm-4", temperature=0.5)

# ── 定义对话模板 ──
chat_template = ChatPromptTemplate.from_messages([
    ("system", "你是{role}。回答必须包含以下要素：{requirements}。"),
    ("human", "请用{style}的风格，回答：{question}")
])

# ── 测试：字典方式填充 ──
filled = chat_template.invoke({
    "role": "资深营养师",
    "requirements": "食物名称、主要营养成分、适合人群、食用建议",
    "style": "通俗易懂",
    "question": "夏天应该多吃什么？"
})

# ── 发送 ──
response = llm.invoke(filled)
print(response.content)
```

---

## 九、实战：从零搭建一个提示词模板应用

### 9.1 场景设计

我们要做一个**万能问答助手**，用户可以自定义：
- 角色（role）
- 回答风格（style）
- 需要从哪几个维度回答（dimensions）
- 具体问题（question）

### 9.2 完整代码

```python
import os
from langchain_community.chat_models import ChatZhipuAI
from langchain.prompts import PromptTemplate

# ============================================================
# Step 1: 初始化模型
# ============================================================
os.environ["ZHIPUAI_API_KEY"] = "你的Key"
llm = ChatZhipuAI(model="glm-4", temperature=0.5)

# ============================================================
# Step 2: 创建模板（这是开发者做的工作，只做一次）
# ============================================================
TEMPLATE = """
你是一位{role}。
请用{style}的风格回答问题。
回答时请包含以下要素：
{requirements}

问题：{question}
"""

prompt_template = PromptTemplate.from_template(TEMPLATE)

# ============================================================
# Step 3: 用户调用函数（封装后用户只需传4个参数）
# ============================================================
def ask_expert(role, style, requirements, question):
    """万能问答函数"""
    # 填充模板
    prompt = prompt_template.format(
        role=role,
        style=style,
        requirements=requirements,
        question=question
    )
    # 调用模型
    response = llm.invoke(prompt)
    return response.content

# ============================================================
# Step 4: 用户使用（只需一行！）
# ============================================================

# 场景A：问营养
answer1 = ask_expert(
    role="资深营养师",
    style="通俗易懂，像跟朋友聊天一样",
    requirements="1.推荐食物 2.主要营养 3.适合人群 4.注意事项",
    question="夏天适合吃什么水果？"
)
print(answer1)
print("\n" + "="*50 + "\n")

# 场景B：问编程
answer2 = ask_expert(
    role="资深Python工程师",
    style="简洁专业，附带代码示例",
    requirements="1.概念解释 2.代码示例 3.使用场景 4.常见误区",
    question="Python的装饰器是什么？"
)
print(answer2)
```

### 9.3 效果展示

```
用户A的调用：
ask_expert(role="资深营养师", style="通俗易懂...", requirements="...", question="夏天适合吃什么水果？")
                      ↓
生成的完整提示词（用户看不到，自动完成）：
"你是一位资深营养师。请用通俗易懂，像跟朋友聊天一样的风格。回答时请包含以下要素：
1.推荐食物 2.主要营养 3.适合人群 4.注意事项
问题：夏天适合吃什么水果？"
                      ↓
模型回复 → 结构化、有条理、符合要求

用户B的调用：
ask_expert(role="资深Python工程师", style="简洁专业...", requirements="...", question="Python的装饰器是什么？")
                      ↓
同样流程 → 得到编程相关的结构化回复
```

---

## 十、提示词工程最佳实践

### 10.1 模板设计的黄金法则

| 法则 | 说明 | 示例 |
|------|------|------|
| **角色先行** | 先告诉模型"你是谁" | "你是{role}" |
| **格式明确** | 告知回答的结构要求 | "请从以下3个维度回答：{dims}" |
| **风格指定** | 告知语言风格 | "请用{style}的风格" |
| **变量隔离** | 变化的部分用变量，不变的部分固化在模板中 | 角色→变量，结构→固定 |

### 10.2 好的模板 vs 差的模板

```python
# ❌ 差的模板：太简单，模型随意发挥
bad_template = "{question}"

# ❌ 差的模板：变量太少，每次都重复写
bad_template = "回答：{question}"
# 用户调用时：每次都要写"你是XX，请用XX风格..."

# ✅ 好的模板：结构完整，变量合理，一次定义反复使用
good_template = """
你是{role}。
请用{style}的风格回答问题。
回答必须包含以下内容：
1. {point1}
2. {point2}
3. {point3}

问题：{question}
"""
```

### 10.3 变量命名的建议

| 变量名 | 建议用途 | 示例值 |
|--------|----------|--------|
| `role` | 角色设定 | "数学老师"、"资深营养师" |
| `style` | 语言风格 | "通俗易懂"、"严谨学术"、"生动有趣" |
| `question` | 具体问题 | "勾股定理是什么？" |
| `requirements` | 格式要求 | "1.定义 2.举例 3.总结" |
| `language` | 输出语言 | "中文"、"英文" |
| `format` | 输出格式 | "JSON"、"Markdown"、"纯文本" |

### 10.4 模板管理与复用

在实际项目中，建议将模板集中管理：

```python
# templates.py —— 所有模板集中在一个文件中

# 翻译模板
TRANSLATE_TEMPLATE = "将以下内容翻译成{target_language}：\n{text}"

# 总结模板
SUMMARIZE_TEMPLATE = "请用{word_count}字以内总结以下内容，突出{key_points}：\n{text}"

# 代码审查模板
CODE_REVIEW_TEMPLATE = """
你是{role}，请从以下角度审查代码：
1. 正确性
2. 性能
3. 可读性

代码：
{code}
"""

# 使用时从 templates 模块导入
# from templates import TRANSLATE_TEMPLATE
```

---

## 十一、常见问题与排错指南

### 11.1 错误速查表

| 错误信息 | 原因 | 解决方法 |
|----------|------|----------|
| `KeyError: 'xxx'` | 模板中有 `{xxx}` 变量但填充时没传 | 检查 `.format()` 的参数名是否覆盖了所有模板变量 |
| `KeyError`（变量名不匹配） | 填参时变量名和模板中不一致 | 确保填参名和 `{变量名}` 完全一致（含大小写） |
| `AttributeError: 'str' object has no attribute 'content'` | 把 `PromptTemplate` 填充结果（字符串）当成了 AIMessage | `PromptTemplate` 返回字符串，直接使用即可 |
| `TypeError: format() got unexpected keyword argument` | `ChatPromptTemplate` 用了 `.format()` 而非 `.invoke()` | `ChatPromptTemplate` 用 `.invoke({...})` |
| 模板中 `{` 和 `}` 需要作为普通字符 | 花括号被识别为变量占位符 | 使用双花括号转义：`{{` 表示 `{`，`}}` 表示 `}` |
| `ImportError: cannot import name 'ChatPromptTemplate'` | 导入路径不对 | 从 `langchain_core.prompts` 导入 |
| 填充后提示词中变量没有被替换 | 变量名拼写不一致 | 仔细核对模板中的变量名和填空时的参数名 |

### 11.2 调试技巧

**技巧一：先打印看填充结果**

```python
template = PromptTemplate.from_template("你是{role}，回答：{q}")

# 填充后先打印看看，确认无误再发给模型
filled = template.format(role="老师", q="1+1=?")
print("生成的提示词：", filled)  # 👈 调试关键行！
# 确认无误后再发送
# response = llm.invoke(filled)
```

**技巧二：查看模板中的变量列表**

```python
template = PromptTemplate.from_template("你是{role}，{style}地回答：{question}")

# 查看模板自动识别了哪些变量
print(template.input_variables)
# 输出：['question', 'role', 'style']
# 确保你的 .format() 涵盖了这3个变量
```

**技巧三：检查 ChatPromptTemplate 的填充结果**

```python
chat_template = ChatPromptTemplate.from_messages([
    ("system", "你是{role}"),
    ("human", "{question}")
])

filled = chat_template.invoke({"role": "老师", "question": "1+1=?"})

# 看看生成的每条消息
for msg in filled:
    print(f"{type(msg).__name__}: {msg.content}")
# 输出：
# SystemMessage: 你是老师
# HumanMessage: 1+1=?
```

---

## 十二、课后练习

### 练习一：基础模板（PromptTemplate）

> 创建一个 PromptTemplate，包含 4 个变量：`role`、`style`、`format`、`question`。
> 分别用两组不同的变量值填充并发送给模型，对比回复。

```python
# 模板框架提示
template_string = """
你是{role}。
请用{style}的风格。
输出格式要求：{format}

问题：{question}
"""
```

| 测试组 | role | style | format | question | 回复摘要 |
|:------:|------|-------|--------|----------|----------|
| 1 | 营养师 | 通俗 | 分点列举 | 夏天吃什么？ | |
| 2 | 程序员 | 专业 | 代码示例 | 什么是递归？ | |

### 练习二：对话模板（ChatPromptTemplate）

> 使用 ChatPromptTemplate，创建包含 SystemMessage 和 HumanMessage 的模板。
> SystemMessage 包含 `role` 和 `style` 变量，HumanMessage 包含 `question` 变量。
> 分别用 `.invoke()` 字典方式和 `.format_messages()` 方式填充，验证两种方式结果是否相同。

### 练习三：封装复用函数

> 将练习一中的模板封装成一个函数 `ask(role, style, format_type, question)`，
> 调用该函数 3 次，每次用不同的 `role` 和 `question`，对比回复的差异。

### 练习四：模板对比实验

> 用同一个问题，分别测试**有模板**和**无模板**两种方式：

```python
# 无模板
response1 = llm.invoke("讲一下勾股定理")

# 有模板
template = PromptTemplate.from_template("你是{role}，从{aspect1}和{aspect2}两个角度详细解释{question}")
filled = template.format(role="数学教授", aspect1="历史背景", aspect2="实际应用", question="勾股定理")
response2 = llm.invoke(filled)
```

| 方式 | 回复长度 | 结构是否清晰 | 内容是否准确 | 评价 |
|------|:--------:|:------------:|:------------:|------|
| 无模板 | | | | |
| 有模板 | | | | |

### 练习五：模板库设计

> 设计 3 个常用的提示词模板，分别用于：
> 1. 代码解释（role=程序员, style=简洁, question=代码片段）
> 2. 文本翻译（target_language=目标语言, text=待翻译文本）
> 3. 学习助手（subject=学科, topic=知识点, level=难度级别）
>
> 每个模板至少包含 3 个变量，并编写测试代码验证。

---

## 十三、课程小结

### 13.1 本课知识图谱

```
┌────────────────────────────────────────────────────────────┐
│               提示词模板核心知识体系                          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  提示词模板是什么？                                     │
│      LangChain 的核心组件，用于构建和管理提示词              │
│      用户填空 + 预定义结构 → 结构化提示词 → 更准确一致的输出  │
│                                                            │
│  2️⃣  两种模板类型                                          │
│      ├── PromptTemplate（基础字符串模板）                    │
│      │   ├── 导入：langchain.prompts                       │
│      │   ├── 创建：PromptTemplate.from_template(字符串)     │
│      │   ├── 填充：.format(key=value, ...)                 │
│      │   └── 返回：字符串                                  │
│      │                                                    │
│      └── ChatPromptTemplate（对话角色模板）                  │
│          ├── 导入：langchain_core.prompts                  │
│          ├── 创建：ChatPromptTemplate.from_messages([...]) │
│          ├── 填充：.invoke({...}) 或 .format_messages(...)│
│          └── 返回：消息列表 [SystemMessage, HumanMessage]  │
│                                                            │
│  3️⃣  模板的三大好处                                         │
│      ├── 简化用户输入：只需填变量，不用重复写大段文字         │
│      ├── 提升准确性：预定义结构，模型不容易跑偏               │
│      └── 保证一致性：同一模板生成的结果风格统一               │
│                                                            │
│  4️⃣  关键注意事项                                           │
│      ├── 变量名必须完全匹配（模板和填充时）                   │
│      ├── ChatPromptTemplate 不能用 .format()，用 .invoke() │
│      └── 填充后先用 print 确认，再发给模型                   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 13.2 一句话总结

> **提示词模板 = 固定的结构 + 可变的填空。** 开发者定义好模板（只写一次），用户只需填几个变量就能获得结构化的回复。既简化了输入，又提升了准确性和一致性。

### 13.3 练习答案

> 视频最后的练习题：
>
> **问**：LangChain 里的提示词模板引擎主要的作用是什么？
>
> - A. 直接生成大语言模型的输出内容 ❌（模板生成的是提示词，不是输出）
> - **B. 将用户输入或动态数据结构化嵌入到预定义模板，提升模型输出的准确性和一致性 ✅**
> - C. 用于存储大语言模型的训练数据 ❌（LangChain 是调用框架，不涉及训练）
> - D. 优化大语言模型的训练过程 ❌（同上，不涉及训练）
>
> **答案：B**

### 13.4 系列课程定位

```
第一课：LangChain 环境搭建 + 通义（云端）入门
第二课：LangChain 模型选型与平台调研（理论）
第三课：切换大语言模型（智谱AI 等实战）
第四课：使用 Ollama 部署本地大语言模型
第五课（本课）：提示词模板（Prompt Template）  ← 你在这里
后续：Chain / Memory / RAG / Agent 等高级主题
```

---

*本教学文档基于陈泽鹏老师视频课程（提示词模板）整理编写。*  
*本文档涵盖 PromptTemplate 和 ChatPromptTemplate 两种模板的定义、填充、调试全流程。*
