# LangChain 输出解析器（Output Parser）详解

> 基于陈泽鹏老师视频课程整理编写 · 2026年6月

---

## 目录

- [一、课程背景与目标](#一课程背景与目标)
- [二、为什么需要输出解析器](#二为什么需要输出解析器)
- [三、什么是输出解析器](#三什么是输出解析器)
- [四、StructuredOutputParser——结构化字典输出](#四structuredoutputparser结构化字典输出)
- [五、PydanticOutputParser——Python 对象输出](#五pydanticoutputparserpython-对象输出)
- [六、两种解析器的对比与选择](#六两种解析器的对比与选择)
- [七、LangChain 中的其他输出解析器](#七langchain-中的其他输出解析器)
- [八、完整实战：从模板到解析的全流程](#八完整实战从模板到解析的全流程)
- [九、关键踩坑点与注意事项](#九关键踩坑点与注意事项)
- [十、常见问题与排错指南](#十常见问题与排错指南)
- [十一、课后练习](#十一课后练习)
- [十二、课程小结](#十二课程小结)

---

## 一、课程背景与目标

### 1.1 前情回顾

在前面几节课中，我们已经学会了：

- 使用 LangChain 接入大语言模型（通义、智谱AI、Ollama 本地模型）
- 使用提示词模板（PromptTemplate / ChatPromptTemplate）简化输入
- 模型返回的通常是**文本字符串**（或 AIMessage 对象）

```python
# 典型的调用流程
response = llm.invoke("张三今年25岁，请提取他的姓名和年龄")
print(response.content)
# 输出："姓名：张三，年龄：25岁"
#        ↑ 这是一个字符串，不是结构化的数据
```

### 1.2 问题场景：字符串不够用

考虑以下实际需求：

```
场景一：存数据库
"我叫张三，今年25岁，来自北京"
→ 要存入数据库的 name、age、city 三个字段
→ 字符串没法直接存 😰

场景二：调用其他API
模型返回了一段文字，需要提取其中的关键信息传给另一个API
→ 字符串需要手动解析 😰

场景三：前端展示
前端需要 JSON 格式的数据来渲染页面
→ 字符串无法直接渲染 😰
```

**核心矛盾**：

> 模型输出的是**非结构化文本**，而实际应用需要的是**结构化数据**（JSON、字典、对象）。

### 1.3 本课要掌握的两个核心目标

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  目标一：了解输出格式化有什么用                            │
│         ├── 它解决什么问题？                              │
│         ├── 什么场景下需要它？                             │
│         └── 它有哪些类型？                                │
│                                                         │
│  目标二：掌握输出格式化的使用方法                           │
│         ├── StructuredOutputParser（结构化字典输出）      │
│         ├── PydanticOutputParser（Python 对象输出）       │
│         ├── 完整流程：定义→创建→填充→调用→解析            │
│         └── 能独立编写输出解析代码                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 二、为什么需要输出解析器

### 2.1 一个直观的问题

```python
# 假设我们用提示词模板让模型提取信息
response = llm.invoke("""
从以下文本中提取姓名和年龄，以 JSON 格式返回：
"张三今年25岁，来自北京"
""")

print(response.content)
# 模型返回：
# '{"name": "张三", "age": 25}'
#
# 看起来是 JSON，但实际上它是... 一个字符串！
# type(response.content) → <class 'str'>
```

**问题**：虽然内容看起来像 JSON，但它**本质上还是一个字符串**。你不能直接：

```python
# ❌ 这样不行！
data = response.content
print(data["name"])   # TypeError: string indices must be integers
print(data.name)      # AttributeError: 'str' object has no attribute 'name'

# 必须手动解析
import json
data = json.loads(response.content)
print(data["name"])   # 现在才能用 → "张三"
```

> **输出解析器就是帮你自动完成这个「手动解析」步骤的工具。**

### 2.2 没有解析器 vs 有解析器

**没有解析器（手动处理）：**

```python
# 步骤繁琐，容易出错
response = llm.invoke(prompt)
raw_text = response.content

# 手动提取 → 各种字符串处理
import json
import re

try:
    data = json.loads(raw_text)
    name = data.get("name", "未知")
    age = data.get("age", 0)
except json.JSONDecodeError:
    # JSON 解析失败，尝试正则提取
    name_match = re.search(r"姓名[：:]\s*(.+?)[，,]", raw_text)
    age_match = re.search(r"年龄[：:]\s*(\d+)", raw_text)
    name = name_match.group(1) if name_match else "未知"
    age = int(age_match.group(1)) if age_match else 0

print(f"姓名：{name}，年龄：{age}")
# 😰 太复杂了！
```

**有解析器（LangChain 自动处理）：**

```python
# 定义好输出结构 → 解析器自动处理
output_parser = StructuredOutputParser.from_response_schemas([
    ResponseSchema(name="name", description="人的姓名"),
    ResponseSchema(name="age", description="人的年龄", type="integer")
])

# 调用 → 自动解析 → 直接得到字典
response = llm.invoke(prompt)
data = output_parser.parse(response.content)

print(f"姓名：{data['name']}，年龄：{data['age']}")
# 🎉 简洁、可靠！
```

### 2.3 输出解析器的三大好处

```
┌──────────────────────────────────────────────────────────┐
│                输出解析器的三大好处                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1️⃣  自动结构化                                            │
│      模型返回的原始字符串 → 自动转为 dict / JSON / 对象       │
│      不需要手写正则或 json.loads()                          │
│                                                          │
│  2️⃣  方便后续处理                                           │
│      提取出的结构化数据可以直接：                             │
│      ├── 存入数据库（对应字段）                              │
│      ├── 传给下一个 API                                    │
│      ├── 在前端渲染展示                                     │
│      └── 用 key 直接取值（data["name"]）                    │
│                                                          │
│  3️⃣  提升一致性和可读性                                      │
│      通过 format_instructions 告诉模型输出格式，              │
│      模型会按约定格式输出，每次结果结构一致                     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 三、什么是输出解析器

### 3.1 官方定义

> **输出解析器（Output Parser）** 是 LangChain 的关键功能之一，使用频率高，用于将大语言模型的原始输出解析为结构化的数据格式——可以是 JSON、字典类型或者自定义的 Python 对象。

### 3.2 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│                    输出解析器工作流程                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  第一步：定义输出结构（你想让模型返回什么格式？）                │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ name: 字符串   ← 人的姓名                             │    │
│  │ age:  整数     ← 人的年龄                             │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  第二步：创建解析器对象                                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ parser = StructuredOutputParser.from_response_schemas│    │
│  │ 解析器会自动生成 format_instructions                  │    │
│  │ 告诉模型"你要按这个格式输出"                            │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  第三步：将 format_instructions 嵌入提示词模板                │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ "请从以下文本提取信息，按以下格式返回：                   │    │
│  │  {format_instructions}                              │    │
│  │  文本：{input_text}"                                 │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  第四步：调用模型 → 获取原始字符串响应                         │
│                          ↓                                  │
│  第五步：解析器自动解析                                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 原始字符串: '{"name": "张三", "age": 25}'              │    │
│  │        ↓ parser.parse()                             │    │
│  │ 结构化字典: {"name": "张三", "age": 25}               │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 LangChain 提供的解析器类型

在 LangChain 的 `output_parsers` 模块中，提供了多种解析器：

```
langchain.output_parsers
├── StructuredOutputParser    ← 结构化字典/JSON 输出（本课重点）
├── PydanticOutputParser      ← Python 对象输出（本课重点）
├── ListOutputParser          ← 列表输出
├── CommaSeparatedListOutputParser ← 逗号分隔列表
├── NumberedListOutputParser  ← 编号列表
├── MarkdownListOutputParser  ← Markdown 列表
├── JsonOutputParser          ← JSON 输出
├── DatetimeOutputParser      ← 日期时间输出
├── EnumOutputParser          ← 枚举值输出
└── ...更多
```

> 📌 本节课重点学习最常用的两种：**StructuredOutputParser** 和 **PydanticOutputParser**。

---

## 四、StructuredOutputParser——结构化字典输出

### 4.1 什么时候用它？

适合**将模型输出解析为字典（dict）**的场景。

```
适用场景：
├── 信息提取（从文本中抽取姓名、年龄、地址等）
├── 结构化问答（返回多个字段）
├── 需要 JSON 格式输出的场景
└── 后续处理需要 key-value 数据
```

### 4.2 核心组件

`StructuredOutputParser` 依赖两个东西：

| 组件 | 类名 | 作用 |
|------|------|------|
| **字段定义** | `ResponseSchema` | 定义每个输出字段的名称、描述、类型 |
| **解析器** | `StructuredOutputParser` | 根据字段定义创建解析器，解析模型输出 |

### 4.3 完整代码流程

#### 第一步：导入

```python
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
```

| 导入 | 用途 |
|------|------|
| `StructuredOutputParser` | 创建结构化输出解析器 |
| `ResponseSchema` | 定义输出的每个字段 |

#### 第二步：定义输出结构

```python
# 用 ResponseSchema 定义每个字段
response_schemas = [
    ResponseSchema(name="name", description="人的姓名", type="string"),
    ResponseSchema(name="age", description="人的年龄", type="integer"),
]
```

**`ResponseSchema` 的参数：**

| 参数 | 必填 | 说明 | 示例 |
|------|:----:|------|------|
| `name` | ✅ | 字段名（输出字典中的 key） | `"name"`、`"age"` |
| `description` | ✅ | 字段描述（告诉模型这个字段是什么） | `"人的姓名"` |
| `type` | 否 | 数据类型 | `"string"`、`"integer"`、`"number"` |

> 💡 `type` 参数会影响模型输出的格式。`"integer"` 会让模型输出数字而不是字符串 `"25"`。

#### 第三步：创建解析器

```python
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
```

此时解析器会自动生成 **`format_instructions`**（格式化指令），它告诉模型应该按照什么格式输出：

```python
print(output_parser.get_format_instructions())
```

输出类似于：

```
The output should be a markdown code snippet formatted in the following schema:

```json
{
    "name": string  // 人的姓名
    "age": integer  // 人的年龄
}
```
```

#### 第四步：创建提示词模板（注意和普通模板的区别！）

这是使用输出解析器时**和普通 PromptTemplate 最大的不同**——需要用 `partial_variables` 预先填充 `format_instructions`：

```python
from langchain.prompts import PromptTemplate

# 定义模板字符串
template_string = """
你是一个信息提取助手。
请从以下文本中提取出姓名和年龄，并按照指定格式返回。

{format_instructions}

文本内容：{input_text}
"""

# ⚠️ 注意：不是直接 from_template，而是用 partial_variables
prompt_template = PromptTemplate(
    template=template_string,
    input_variables=["input_text"],
    partial_variables={
        "format_instructions": output_parser.get_format_instructions()
    }
)
```

**为什么不能直接用 `.from_template()`？**

```
普通 PromptTemplate 的流程：
    template = PromptTemplate.from_template("你是{role}")
    template.format(role="老师")           # 用户自己填所有变量

带解析器的 PromptTemplate 的流程：
    template = PromptTemplate(
        template="...",
        input_variables=["input_text"],       # 用户只填这些
        partial_variables={                   # format_instructions 自动填充
            "format_instructions": "..."      # 由解析器生成，用户不需要管
        }
    )
    template.format(input_text="张三今年25岁")  # 用户只需填 input_text
```

**关键概念——`partial_variables`：**

> `partial_variables` = **部分变量**。这些变量在模板创建时就已经填充好了，用户后续调用时**不需要也不应该**再传这些变量。用户只需要填充 `input_variables` 中声明的变量。

#### 第五步：填充模板 + 调用模型

```python
# 准备输入文本
input_text = "张三今年25岁，来自北京"

# 填充模板（只需填 input_text，format_instructions 已经自动填好了）
filled_prompt = prompt_template.format(input_text=input_text)

# 调用模型
response = llm.invoke(filled_prompt)

# 查看原始输出
print("原始输出：", response.content)
# → '```json\n{\n    "name": "张三",\n    "age": 25\n}\n```'
```

#### 第六步：解析输出

```python
# 用解析器将原始字符串解析为字典
parsed_output = output_parser.parse(response.content)

print("解析后：", parsed_output)
# → {"name": "张三", "age": 25}

print(f"姓名：{parsed_output['name']}，年龄：{parsed_output['age']}")
# → 姓名：张三，年龄：25

print(type(parsed_output))
# → <class 'dict'>
```

### 4.4 完整代码（可运行）

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
    ResponseSchema(name="name", description="人的姓名", type="string"),
    ResponseSchema(name="age", description="人的年龄", type="integer"),
]

# ============================================================
# 3. 创建解析器
# ============================================================
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

# ============================================================
# 4. 创建提示词模板（使用 partial_variables）
# ============================================================
prompt_template = PromptTemplate(
    template="""
你是一个信息提取助手。
请从以下文本中提取出姓名和年龄，并按照指定格式返回。

{format_instructions}

文本内容：{input_text}
""",
    input_variables=["input_text"],
    partial_variables={
        "format_instructions": output_parser.get_format_instructions()
    }
)

# ============================================================
# 5. 填充模板 + 调用模型
# ============================================================
input_text = "张三今年25岁，来自北京"
filled_prompt = prompt_template.format(input_text=input_text)
response = llm.invoke(filled_prompt)

# ============================================================
# 6. 解析输出
# ============================================================
parsed_output = output_parser.parse(response.content)

print("解析后的结构化数据：", parsed_output)
print(f"姓名：{parsed_output['name']}, 年龄：{parsed_output['age']}")
```

**运行结果：**

```
解析后的结构化数据： {'name': '张三', 'age': 25}
姓名：张三, 年龄：25
```

---

## 五、PydanticOutputParser——Python 对象输出

### 5.1 什么时候用它？

适合**将模型输出解析为 Python 对象**的场景。

```
适用场景：
├── 需要类型安全（name 一定是 str，age 一定是 int）
├── 有复杂的数据验证需求
├── 面向对象编程风格
├── 需要对象方法和属性
└── 用 Pydantic 做自动数据校验
```

### 5.2 和 StructuredOutputParser 的本质区别

| 对比 | StructuredOutputParser | PydanticOutputParser |
|------|:----------------------:|:--------------------:|
| 输出类型 | `dict`（字典） | 自定义 Python 对象 |
| 取值方式 | `data["name"]` | `data.name` |
| 类型校验 | 弱 | **强**（Pydantic 自动校验） |
| 适用风格 | 函数式 | **面向对象** |
| 额外依赖 | 无 | `pydantic`（通常已安装） |

### 5.3 完整代码流程

#### 第一步：导入

```python
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
```

| 导入 | 用途 |
|------|------|
| `PydanticOutputParser` | 创建 Pydantic 输出解析器 |
| `BaseModel` | Pydantic 基类，用于定义数据模型 |
| `Field` | 定义字段的描述和约束 |

#### 第二步：定义数据模型

```python
class Person(BaseModel):
    """人员信息模型"""
    name: str = Field(description="人的姓名")
    age: int = Field(description="人的年龄")
```

**Pydantic 模型的要素：**

| 要素 | 说明 | 示例 |
|------|------|------|
| `class Person(BaseModel)` | 继承 BaseModel | 定义一个数据模型类 |
| `name: str` | 字段名 + 类型注解 | `str`、`int`、`float`、`bool` |
| `Field(description="...")` | 字段描述（告诉模型含义） | 帮助模型理解这个字段 |

#### 第三步：创建解析器

```python
output_parser = PydanticOutputParser(pydantic_object=Person)
```

此时解析器同样会自动生成 `format_instructions`。

#### 第四步：创建提示词模板

```python
from langchain.prompts import PromptTemplate

prompt_template = PromptTemplate(
    template="""
你是一个信息提取助手。
请从以下文本中提取出姓名和年龄，并按照指定格式返回。

{format_instructions}

文本内容：{input_text}
""",
    input_variables=["input_text"],
    partial_variables={
        "format_instructions": output_parser.get_format_instructions()
    }
)
```

#### 第五步：填充 + 调用

```python
input_text = "李四今年30岁，住在上海"
filled_prompt = prompt_template.format(input_text=input_text)
response = llm.invoke(filled_prompt)
```

#### 第六步：解析为 Python 对象

```python
parsed_output = output_parser.parse(response.content)

print("解析后的对象：", parsed_output)
# → name='李四' age=30

print(f"姓名：{parsed_output.name}，年龄：{parsed_output.age}")
# → 姓名：李四，年龄：30

print(type(parsed_output))
# → <class '__main__.Person'>

# 🎉 可以用 . 语法取值，IDE 还会自动补全！
```

### 5.4 完整代码（可运行）

```python
import os
from langchain_community.chat_models import ChatZhipuAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field

# ============================================================
# 1. 准备模型
# ============================================================
os.environ["ZHIPUAI_API_KEY"] = "你的Key"
llm = ChatZhipuAI(model="glm-4", temperature=0.5)

# ============================================================
# 2. 定义数据模型
# ============================================================
class Person(BaseModel):
    """人员信息"""
    name: str = Field(description="人的姓名")
    age: int = Field(description="人的年龄")

# ============================================================
# 3. 创建解析器
# ============================================================
output_parser = PydanticOutputParser(pydantic_object=Person)

# ============================================================
# 4. 创建提示词模板
# ============================================================
prompt_template = PromptTemplate(
    template="""
你是一个信息提取助手。
请从以下文本中提取出姓名和年龄，并按照指定格式返回。

{format_instructions}

文本内容：{input_text}
""",
    input_variables=["input_text"],
    partial_variables={
        "format_instructions": output_parser.get_format_instructions()
    }
)

# ============================================================
# 5. 调用模型
# ============================================================
input_text = "李四今年30岁，住在上海"
filled_prompt = prompt_template.format(input_text=input_text)
response = llm.invoke(filled_prompt)

# ============================================================
# 6. 解析为 Python 对象
# ============================================================
person = output_parser.parse(response.content)

print(f"类型：{type(person).__name__}")
print(f"姓名：{person.name}，年龄：{person.age}")
```

**运行结果：**

```
类型：Person
姓名：李四，年龄：30
```

---

## 六、两种解析器的对比与选择

### 6.1 完整对比表

| 对比维度 | StructuredOutputParser | PydanticOutputParser |
|----------|:----------------------:|:--------------------:|
| **导入** | `langchain.output_parsers` | `langchain.output_parsers` |
| **定义方式** | `ResponseSchema` 列表 | Pydantic `BaseModel` 类 |
| **输出类型** | `dict` | 自定义 Python 对象 |
| **取值方式** | `data["name"]` | `person.name` |
| **IDE 补全** | ❌ 字典 key 无自动补全 | ✅ 对象属性有自动补全 |
| **类型校验** | ⭐⭐ 弱校验 | ⭐⭐⭐⭐⭐ Pydantic 强校验 |
| **代码量** | 较少 | 稍多（需定义类） |
| **复杂度** | ⭐ 简单 | ⭐⭐ 适中 |
| **适用场景** | 快速开发、简单提取 | 类型安全、复杂数据模型 |

### 6.2 选择决策树

```
需要输出解析器？

第一步：输出数据结构简单吗？
    ├── 简单（2-3个字段）→ StructuredOutputParser
    └── 复杂（嵌套、多类型）→ 往下看

第二步：需要严格的类型校验吗？
    ├── 需要（name 必须是 str，age 必须是 int）→ PydanticOutputParser
    └── 不需要 → StructuredOutputParser

第三步：喜欢哪种编程风格？
    ├── 字典风格 data["key"] → StructuredOutputParser
    └── 对象风格 data.key → PydanticOutputParser
```

### 6.3 代码对比

```python
# ──────────────────────────────────────
# StructuredOutputParser → 字典
# ──────────────────────────────────────
response_schemas = [
    ResponseSchema(name="name", description="姓名"),
    ResponseSchema(name="age", description="年龄")
]
parser = StructuredOutputParser.from_response_schemas(response_schemas)
result = parser.parse(response.content)
print(result["name"])  # 字典取值

# ──────────────────────────────────────
# PydanticOutputParser → 对象
# ──────────────────────────────────────
class Person(BaseModel):
    name: str = Field(description="姓名")
    age: int = Field(description="年龄")

parser = PydanticOutputParser(pydantic_object=Person)
result = parser.parse(response.content)
print(result.name)    # 对象取值
```

---

## 七、LangChain 中的其他输出解析器

### 7.1 解析器家族速览

视频中老师提到，点进 `langchain.output_parsers` 模块可以看到更多解析器：

| 解析器 | 输入 → 输出 | 使用场景 |
|--------|------------|----------|
| `StructuredOutputParser` | 文本 → `dict` | 结构化信息提取 |
| `PydanticOutputParser` | 文本 → `Python对象` | 类型安全的数据提取 |
| `JsonOutputParser` | 文本 → `dict` | JSON 输出解析 |
| `ListOutputParser` | 文本 → `list` | 列表型输出 |
| `CommaSeparatedListOutputParser` | 文本 → `list` | 逗号分隔列表 |
| `NumberedListOutputParser` | 文本 → `list` | 编号列表 |
| `DatetimeOutputParser` | 文本 → `datetime` | 日期时间提取 |
| `EnumOutputParser` | 文本 → `Enum` | 分类/标签输出 |

### 7.2 CommaSeparatedListOutputParser 示例

```python
from langchain.output_parsers import CommaSeparatedListOutputParser

parser = CommaSeparatedListOutputParser()

# 配合模板
prompt = PromptTemplate(
    template="列出5种{category}，用逗号分隔。\n{format_instructions}",
    input_variables=["category"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

response = llm.invoke(prompt.format(category="夏天的水果"))
result = parser.parse(response.content)
# → ['西瓜', '桃子', '葡萄', '哈密瓜', '荔枝']
```

### 7.3 如何自己探索其他解析器

```python
# 在 VS Code 中查看所有可用的解析器
from langchain.output_parsers import ...

# 或者查看官方文档：
# LangChain 官网 → Integrations → Output Parsers
#
# 或者让 AI 工具帮忙：
# "请给我一个 LangChain DatetimeOutputParser 的使用示例"
```

---

## 八、完整实战：从模板到解析的全流程

### 8.1 实战场景

构建一个**餐厅评论信息提取器**，从用户的评论文字中自动提取：
- 餐厅名称
- 评分（1-5）
- 推荐菜品
- 人均消费

### 8.2 StructuredOutputParser 版

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
    ResponseSchema(name="restaurant", description="餐厅名称", type="string"),
    ResponseSchema(name="rating", description="评分，1-5分", type="integer"),
    ResponseSchema(name="recommended_dish", description="推荐的菜品", type="string"),
    ResponseSchema(name="avg_price", description="人均消费（元）", type="integer"),
]

# ── 创建解析器 ──
parser = StructuredOutputParser.from_response_schemas(response_schemas)

# ── 创建模板 ──
prompt_template = PromptTemplate(
    template="""
你是一个餐厅评论分析助手。
请从以下用户评论中提取关键信息。

{format_instructions}

用户评论：{review}
""",
    input_variables=["review"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# ── 封装为函数 ──
def extract_restaurant_info(review_text):
    """从评论中提取餐厅信息"""
    prompt = prompt_template.format(review=review_text)
    response = llm.invoke(prompt)
    return parser.parse(response.content)

# ── 测试 ──
review = """
昨天去了朝阳区的"老张涮肉"，太赞了！点了他们的招牌手切羊肉，
肉质鲜嫩，蘸料也特别香。两个人花了180块，人均90左右吧。
我给他打4.5分，扣0.5分是因为等位太久。
"""

result = extract_restaurant_info(review)
print(f"餐厅：{result['restaurant']}")
print(f"评分：{result['rating']}分")
print(f"推荐菜：{result['recommended_dish']}")
print(f"人均：{result['avg_price']}元")
```

### 8.3 PydanticOutputParser 版

```python
import os
from langchain_community.chat_models import ChatZhipuAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field

# ── 准备模型 ──
os.environ["ZHIPUAI_API_KEY"] = "你的Key"
llm = ChatZhipuAI(model="glm-4", temperature=0.5)

# ── 定义数据模型 ──
class RestaurantInfo(BaseModel):
    """餐厅信息"""
    restaurant: str = Field(description="餐厅名称")
    rating: int = Field(description="评分，1-5分")
    recommended_dish: str = Field(description="推荐的菜品")
    avg_price: int = Field(description="人均消费（元）")

# ── 创建解析器 ──
parser = PydanticOutputParser(pydantic_object=RestaurantInfo)

# ── 创建模板 ──
prompt_template = PromptTemplate(
    template="""
你是一个餐厅评论分析助手。
请从以下用户评论中提取关键信息。

{format_instructions}

用户评论：{review}
""",
    input_variables=["review"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# ── 封装为函数 ──
def extract_restaurant_info(review_text):
    """从评论中提取餐厅信息"""
    prompt = prompt_template.format(review=review_text)
    response = llm.invoke(prompt)
    return parser.parse(response.content)

# ── 测试 ──
review = """
昨天去了朝阳区的"老张涮肉"，太赞了！点了他们的招牌手切羊肉，
两个人花了180块，人均90左右。我给他打4.5分。
"""

info = extract_restaurant_info(review)
print(f"餐厅：{info.restaurant}")
print(f"评分：{info.rating}分")
print(f"推荐菜：{info.recommended_dish}")
print(f"人均：{info.avg_price}元")
print(f"数据类型：{type(info).__name__}")
```

---

## 九、关键踩坑点与注意事项

### 9.1 ⚠️ 模板构建必须用 `partial_variables`

这是视频中老师反复强调的**最重要**的注意点！

```python
# ❌ 错误写法：普通的 from_template
# 这样 format_instructions 也需要用户手动填，失去了自动化的意义
template = PromptTemplate.from_template("""
{format_instructions}
文本：{input_text}
""")
filled = template.format(
    format_instructions="...",  # 😰 每次都要手动写格式说明
    input_text="张三今年25岁"
)

# ✅ 正确写法：用 partial_variables
# format_instructions 在创建模板时就自动填好了
template = PromptTemplate(
    template="""
{format_instructions}
文本：{input_text}
""",
    input_variables=["input_text"],            # 用户只需要填这个
    partial_variables={
        "format_instructions": parser.get_format_instructions()  # 自动填充
    }
)
filled = template.format(input_text="张三今年25岁")  # 🎉 只需填一个变量
```

### 9.2 ⚠️ `partial_variables` 中的 key 名必须和模板中一致

```python
# 模板中变量名
template = PromptTemplate(
    template="{format_instructions}\n文本：{input_text}",
    input_variables=["input_text"],
    partial_variables={
        "format_instructions": parser.get_format_instructions()  # ← 这个 key
    }
)

# 模板中的 {format_instructions} 和 partial_variables 中的 "format_instructions"
# 必须完全一致！
```

### 9.3 ⚠️ 解析结果的处理差异

```python
# StructuredOutputParser 返回 dict
result = parser.parse(response.content)
print(result["name"])    # ✅ 字典取值
print(result.name)       # ❌ 字典没有 .name 属性

# PydanticOutputParser 返回对象
result = parser.parse(response.content)
print(result.name)       # ✅ 对象属性取值
print(result["name"])    # ❌ Pydantic 对象不是字典（除非调用 .dict()）
```

### 9.4 ⚠️ 模型可能不按格式输出

有时模型输出不符合预期的 JSON 格式，解析器会报错。解决方案：

```python
# 方案一：降低 temperature（让模型更"听话"）
llm = ChatZhipuAI(model="glm-4", temperature=0.1)  # 更低的温度

# 方案二：在提示词中强调格式
template = """
你必须严格按照以下格式输出，不要添加任何额外的文字：

{format_instructions}

文本：{input_text}
"""

# 方案三：加 try-except 兜底
try:
    result = parser.parse(response.content)
except Exception as e:
    print(f"解析失败：{e}")
    print(f"原始输出：{response.content}")
    result = {"error": "解析失败"}
```

### 9.5 ⚠️ 调用流程总结

```
完整调用链路的每一步：

1. response_schemas  → 定义输出结构
        ↓
2. output_parser     → 创建解析器（自动生成 format_instructions）
        ↓
3. prompt_template   → 用 partial_variables 嵌入 format_instructions
        ↓
4. .format()         → 用户填 input_variables
        ↓
5. llm.invoke()      → 调用模型，得到原始 response
        ↓
6. parser.parse()    → 将原始字符串解析为结构化数据
        ↓
7. 🎉 得到 dict 或 Python 对象！
```

---

## 十、常见问题与排错指南

### 10.1 错误速查表

| 错误信息 | 原因 | 解决方法 |
|----------|------|----------|
| `KeyError: 'format_instructions'` | 模板中有 `{format_instructions}` 但没用 `partial_variables` | 改用 `partial_variables` 方式创建模板 |
| `OutputParserException: Failed to parse` | 模型输出格式不符合预期 | ①降低 temperature ②在提示词中强调格式 ③加 try-except |
| `AttributeError: 'dict' object has no attribute 'xxx'` | 把 StructuredOutputParser 的结果当成了对象 | 字典用 `result["xxx"]`，不是 `result.xxx` |
| `TypeError: 'Person' object is not subscriptable` | 把 PydanticOutputParser 的结果当成了字典 | 对象用 `result.xxx`，不是 `result["xxx"]` |
| `json.decoder.JSONDecodeError` | 模型输出的 JSON 格式错误 | 检查提示词中是否强调"只输出 JSON，不要其他文字" |
| `ImportError: No module named 'pydantic'` | 未安装 pydantic | `pip install pydantic` |
| 解析结果为空 | 模型没按要求返回 | 打印 response.content 查看原始输出，调整提示词 |
| 字段值类型不对（age 是字符串 "25" 而非数字 25） | ResponseSchema 没指定 type | 加上 `type="integer"` |

### 10.2 调试技巧

**技巧一：先看原始输出**

```python
response = llm.invoke(prompt)
print("=" * 50)
print("原始输出：")
print(response.content)
print("=" * 50)

# 确认原始输出格式正确后，再交给解析器
result = parser.parse(response.content)
```

**技巧二：打印 format_instructions**

```python
# 看看解析器给模型发了什么格式指令
print(parser.get_format_instructions())

# 确认指令清晰、合理
```

**技巧三：用简单文本先测试**

```python
# 先用最简单的文本测试，确保流程跑通
input_text = "张三今年25岁"  # 简单明了
# 跑通后再换更复杂的文本
```

---

## 十一、课后练习

### 练习一：StructuredOutputParser 基础

> 创建一个能提取以下信息的解析器：书名（book_name）、作者（author）、出版年份（year）。
> 用以下文本测试：
> "《三体》是刘慈欣创作的科幻小说，于2008年首次出版。"

**验收标准：**
- [ ] 能正确提取 book_name="三体"、author="刘慈欣"、year=2008
- [ ] year 的类型是整数，不是字符串

### 练习二：PydanticOutputParser 基础

> 用 PydanticOutputParser 实现练习一中同样的功能，但输出为 Python 对象。
> 对比两种方式的代码差异和取值体验。

### 练习三：对比实验

> 用同一个文本，分别测试**有输出解析器**和**无输出解析器**的效果：

```python
# 无解析器：直接问
response1 = llm.invoke("从'张三25岁'中提取姓名和年龄，用JSON返回")

# 有解析器：用 StructuredOutputParser
# ... (按本课流程)
```

| 方式 | 手动处理工作量 | 结果可靠性 | 代码行数 |
|------|:-------------:|:---------:|:--------:|
| 无解析器 | | | |
| 有解析器 | | | |

### 练习四：综合实战

> 构建一个**简历信息提取器**，从一段简历文字中提取：
> - 姓名（name）
> - 年龄（age）
> - 学历（education）
> - 工作年限（work_years）
> - 技能列表（skills）
>
> 要求：
> - 用 PydanticOutputParser
> - `skills` 字段是一个字符串列表 `List[str]`
> - 封装为函数 `extract_resume(text)`，传入简历文本，返回 Resume 对象

**提示：Pydantic 中列表类型写法：**

```python
from typing import List

class Resume(BaseModel):
    name: str = Field(description="姓名")
    age: int = Field(description="年龄")
    education: str = Field(description="最高学历")
    work_years: int = Field(description="工作年限")
    skills: List[str] = Field(description="技能列表")
```

### 练习五：解析器探索

> 在 LangChain 的 `output_parsers` 模块中，找到本节课未讲解的其他 3 种解析器，各写一个简单的使用示例。

| 解析器名称 | 用途 | 输入示例 | 输出示例 |
|------------|------|----------|----------|
| | | | |
| | | | |
| | | | |

---

## 十二、课程小结

### 12.1 本课知识图谱

```
┌────────────────────────────────────────────────────────────┐
│               输出解析器核心知识体系                          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  为什么需要输出解析器？                                 │
│      ├── 模型输出是非结构化文本（字符串）                     │
│      ├── 实际应用需要结构化数据（存数据库、调API、前端渲染）   │
│      └── 输出解析器自动完成文本→结构化数据的转换              │
│                                                            │
│  2️⃣  两种核心解析器                                         │
│      ├── StructuredOutputParser → 输出 dict                │
│      │   ├── ResponseSchema 定义字段                        │
│      │   ├── .from_response_schemas() 创建                  │
│      │   └── .parse(raw_text) → dict                       │
│      │                                                    │
│      └── PydanticOutputParser → 输出 Python 对象            │
│          ├── BaseModel + Field 定义数据模型                  │
│          ├── PydanticOutputParser(pydantic_object=...) 创建 │
│          └── .parse(raw_text) → 对象                        │
│                                                            │
│  3️⃣  关键步骤：partial_variables                            │
│       format_instructions 在创建模板时就自动填充              │
│       用户只需填 input_variables，无需关心格式指令            │
│                                                            │
│  4️⃣  完整调用链路                                           │
│       ResponseSchema → Parser → partial_variables           │
│       → .format() → invoke() → .parse() → 结构化数据        │
│                                                            │
│  5️⃣  其他解析器                                             │
│      ListOutputParser / CommaSeparatedList / Datetime /    │
│      JsonOutputParser / EnumOutputParser...                │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 12.2 一句话总结

> **输出解析器 = 文本 → 结构化数据的自动转换器。** 定义好输出结构，创建解析器，通过 `partial_variables` 将格式指令嵌入模板，模型按格式输出，解析器自动解析——最终得到可以直接使用的字典或 Python 对象。

### 12.3 练习题答案

> 视频最后的练习题：
>
> **问**：使用输出格式化的主要好处是什么？
>
> - A. 它允许语言模型生成更标准的输出 ❌（这只是附带效果，不是主要好处）
> - B. 它减少了语言模型的训练时间 ❌（LangChain 不涉及训练）
> - **C. 它将语言模型原始的输出转换为结构化的数据格式，便于后续处理 ✅**
> - D. 它提高了语言模型的性能和速度 ❌（解析器只是做格式转换，不影响模型性能）
>
> **答案：C**

### 12.4 系列课程定位

```
第一课：LangChain 环境搭建 + 通义（云端）入门
第二课：LangChain 模型选型与平台调研（理论）
第三课：切换大语言模型（智谱AI 等实战）
第四课：使用 Ollama 部署本地大语言模型
第五课：提示词模板（Prompt Template）
第六课（本课）：输出解析器（Output Parser）  ← 你在这里
后续：Chain / Memory / RAG / Agent 等高级主题
```

---

*本教学文档基于陈泽鹏老师视频课程（输出解析器）整理编写。*  
*本文档涵盖 StructuredOutputParser 和 PydanticOutputParser 两种核心解析器，从定义、创建到解析的完整流程。*
