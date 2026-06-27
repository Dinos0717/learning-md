# LangChain 智能体（Agent）创建与多工具调用详解

> 基于陈泽鹏老师视频课程整理编写 · 2026年6月

---

## 目录

- [一、课程背景与目标](#一课程背景与目标)
- [二、动态城市编码查询——从 CSV 读取数据](#二动态城市编码查询从-csv-读取数据)
- [三、get_city_code 函数——三级匹配策略](#三get_city_code-函数三级匹配策略)
- [四、优化天气工具——提取关键字段](#四优化天气工具提取关键字段)
- [五、Agent 工作流程——模型如何调用工具](#五agent-工作流程模型如何调用工具)
- [六、创建 Agent——完整代码实战](#六创建-agent完整代码实战)
- [七、多工具调用](#七多工具调用)
- [八、⚠️ 参数传递问题与修复](#八️-参数传递问题与修复)
- [九、多轮对话测试](#九多轮对话测试)
- [十、完整代码汇总](#十完整代码汇总)
- [十一、常见问题与排错指南](#十一常见问题与排错指南)
- [十二、课后练习](#十二课后练习)
- [十三、课程小结](#十三课程小结)

---

## 一、课程背景与目标

### 1.1 前情回顾

之前我们学习了 `@tool` 装饰器封装工具，但封装的天气工具有两个问题：

```python
@tool
def get_weather(city: str) -> str:
    # ❌ 问题1：城市编码写死了，只能查北京
    url = f"https://api.weather.com?city=101010100"
    
    # ❌ 问题2：返回了整个 JSON，数据太多
    return response.text  # 返回一大坨原始数据
```

| 问题 | 表现 | 影响 |
|------|------|------|
| 城市编码写死 | 无论传入什么城市，都查北京 | 工具不可用 |
| 返回数据冗余 | 返回完整 JSON，包含几十个字段 | Agent 难以提取关键信息 |

### 1.2 本节课的核心问题

> **如何让工具真正"动态"起来——传入任意城市都能查到正确的天气？**
> **如何让 Agent 自动选择并调用工具？多个工具时怎么处理？**

```
本课要解决的三个核心问题：

问题1：城市编码动态化
"北京" → get_city_code("北京") → 101010100
"上海" → get_city_code("上海") → 101020100
→ 不再写死！

问题2：Agent 创建与工具调用
用户提问 → Agent 自动判断 → 调用对应工具 → 返回结果

问题3：多工具共存 + 参数传递
多个工具时，Agent 如何正确选择并传递参数？
```

### 1.3 本课要掌握的目标

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  目标一：掌握动态城市编码查询的实现                 │
│         ├── pandas 读取 CSV 文件                 │
│         ├── 三级匹配策略（区县→市→省）            │
│         └── 模糊匹配 + 默认值兜底                 │
│                                                 │
│  目标二：掌握 Agent 的创建和工具调用流程           │
│         ├── create_react_agent 创建智能体         │
│         ├── AgentExecutor 执行智能体              │
│         ├── 从 langchain hub 加载提示词模板        │
│         └── 理解 Agent 的工作流程                 │
│                                                 │
│  目标三：掌握多工具调用和参数问题修复              │
│         ├── 多工具列表配置                       │
│         ├── 字符串参数解析（正则提取）             │
│         └── 多轮对话测试                        │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 二、动态城市编码查询——从 CSV 读取数据

### 2.1 问题分析

天气 API 使用的是**城市编码**而非城市名：

```
用户说："查一下北京的天气"
    ↓ 需要转换
"北京" → 城市编码 "101010100"
    ↓ 传给 API
API 返回北京天气数据
```

我们需要一个**城市名 → 编码**的映射表。这个映射表存储在一个 CSV 文件中，包含全国所有城市的编码。

### 2.2 CSV 文件结构（模拟）

```
city_code, city_name, province, district
101010100, 北京, 北京, 北京
101010200, 海淀, 北京, 海淀区
101010300, 朝阳, 北京, 朝阳区
101020100, 上海, 上海, 上海
101030100, 天津, 天津, 天津
...
```

### 2.3 安装依赖

```bash
pip install pandas==2.3
pip install requests
```

| 模块 | 用途 |
|------|------|
| `pandas` | 读取和操作 CSV 表格数据 |
| `requests` | 发送 HTTP 请求调用天气 API |

### 2.4 读取 CSV 文件

```python
import pandas as pd

# 读取城市编码 CSV 文件
city_df = pd.read_csv("city_code.csv")

# 查看前几行数据
print(city_df.head())
```

**输出示例：**

```
   city_code city_name province district
0  101010100      北京      北京      北京
1  101010200      海淀      北京     海淀区
2  101010300      朝阳      北京     朝阳区
3  101020100      上海      上海      上海
4  101030100      天津      天津      天津
```

---

## 三、get_city_code 函数——三级匹配策略

### 3.1 匹配策略设计

> 用户说的地名可能是**区县、城市或省份**——需要三级匹配。

```
用户问天气时的表达方式：

"今天北京天气怎么样？"        → "北京"     → 市级
"西青区今天冷不冷？"          → "西青区"   → 区县级
"河北今天下雨吗？"            → "河北"     → 省级
"南开区"                     → 可能只是一段话中的关键词
```

**策略**：优先精准匹配区县 → 其次匹配城市 → 最后模糊匹配省份 → 都不行默认北京。

```
匹配优先级：
1. 区县精准匹配（district == 用户输入）
    ↓ 没找到
2. 城市精准匹配（city_name == 用户输入）
    ↓ 没找到
3. 省份模糊匹配（city_name 包含用户输入）
    ↓ 没找到
4. 默认返回北京编码（兜底）
```

### 3.2 完整函数代码

```python
import pandas as pd

# ── 全局加载 CSV（只读一次）──
city_df = pd.read_csv("city_code.csv")

def get_city_code(city: str) -> str:
    """根据城市名称获取城市编码。
    
    匹配策略：区县精准 → 城市精准 → 省份模糊 → 默认北京
    
    参数:
        city: 城市名称（可以是区县、城市或省份）
    返回:
        城市编码字符串
    """
    
    # ── 第一步：优先匹配区县级 ──
    match = city_df[city_df["district"] == city]
    if not match.empty:
        return match.iloc[0]["city_code"]
    
    # ── 第二步：匹配城市级 ──
    match = city_df[city_df["city_name"] == city]
    if not match.empty:
        return match.iloc[0]["city_code"]
    
    # ── 第三步：模糊匹配省级 ──
    match = city_df[city_df["city_name"].str.contains(city, na=False)]
    if not match.empty:
        return match.iloc[0]["city_code"]
    
    # ── 第四步：默认返回北京 ──
    return "101010100"
```

### 3.3 代码逐行解析

#### 精准匹配

```python
match = city_df[city_df["district"] == city]
```

| 写法 | 含义 |
|------|------|
| `city_df["district"]` | 取出 district（区县）这一列 |
| `== city` | 判断每个值是否等于传入的 city |
| `city_df[...]` | 过滤出匹配的行 |
| `match.iloc[0]` | 取匹配结果的第一条 |
| `["city_code"]` | 取 city_code 列的值 |

#### 模糊匹配

```python
match = city_df[city_df["city_name"].str.contains(city, na=False)]
```

| 参数 | 含义 |
|------|------|
| `.str.contains(city)` | 判断字符串是否**包含** city |
| `na=False` | 遇到空值（NaN）时视为不匹配 |

#### 默认兜底

```python
return "101010100"  # 北京的编码
```

> 💡 宁可返回默认值，也不要让函数报错导致整个 Agent 崩溃。

### 3.4 不该省略重复代码

视频中老师特别强调：三段匹配代码看似重复，**不建议合并省略**。

```python
# ❌ 不推荐：强行合并
# 合并后逻辑不清晰，调试困难

# ✅ 推荐：保持三段独立
# 每一段职责明确：区县 → 城市 → 省份
# 层级分明，方便调试和维护
```

### 3.5 测试函数

```python
# 测试1：区县级
print(get_city_code("房山"))     # → 1200100（房山区编码）

# 测试2：城市级
print(get_city_code("上海"))     # → 101020100（上海市编码）

# 测试3：模糊省级
print(get_city_code("北京"))     # → 101010100
# "北京"在区县精准匹配中找不到（district是"北京"的只有市级），
# 城市精准匹配中找到 city_name=="北京"

# 测试4：乱写
print(get_city_code("火星"))     # → 101010100（默认北京）
```

---

## 四、优化天气工具——提取关键字段

### 4.1 问题

直接 `requests.get()` 返回的是完整 JSON，数据太多：

```json
{
  "code": 200,
  "result": {
    "real_time": {
      "temperature": 26,
      "weather": "多云",
      "wind": "东南风3级",
      "humidity": "65%",
      "pressure": "1012hPa",
      ...（还有很多字段）
    }
  }
}
```

Agent 拿到这么多数据，反而不好提取关键信息。

### 4.2 优化——只提取温度 + 天气

```python
import requests

def get_weather_from_api(city_code: str) -> str:
    """调用天气 API 并提取关键信息"""
    
    # ── 发请求 ──
    url = f"https://api.weather.com/v1?city={city_code}"
    response = requests.get(url)
    
    # ── 解析 JSON ──
    data = response.json()
    
    # ── 按层级提取关键字段 ──
    temperature = data.get("result", {}).get("real_time", {}).get("temperature", "未知")
    weather = data.get("result", {}).get("real_time", {}).get("weather", "未知")
    
    # ── 返回精简结果 ──
    return f"天气：{weather}，温度：{temperature}°C"
```

### 4.3 JSON 层层提取

```python
data.get("result", {})            # 第一层：取 result
    .get("real_time", {})         # 第二层：取 real_time
    .get("temperature", "未知")   # 第三层：取 temperature
```

| 层级 | 字段 | 含义 |
|:----:|------|------|
| 1 | `result` | API 返回的结果集 |
| 2 | `real_time` | 实时天气数据 |
| 3 | `temperature` / `weather` | 温度和天气状况 |

### 4.4 最终工具代码

```python
@tool
def get_weather(city: str) -> str:
    """查询指定城市的实时天气情况。
    
    参数:
        city: 城市名称，如"北京"、"上海"、"深圳"、"海淀区"等
    返回:
        天气和温度的简短描述
    """
    # 第一步：动态获取城市编码
    city_code = get_city_code(city)
    
    # 第二步：调用 API
    url = f"https://api.weather.com/v1?city={city_code}"
    response = requests.get(url)
    
    # 第三步：解析并提取关键字段
    data = response.json()
    temperature = data.get("result", {}).get("real_time", {}).get("temperature", "未知")
    weather = data.get("result", {}).get("real_time", {}).get("weather", "未知")
    
    # 第四步：返回精简结果
    return f"天气：{weather}，温度：{temperature}°C"
```

### 4.5 优化前后对比

```
优化前：
返回："{\"code\":200,\"result\":{\"real_time\":{\"temperature\":26,...}}}"
      → Agent 看到一坨 JSON，难以理解

优化后：
返回："天气：多云，温度：26°C"
      → Agent 一目了然，用户也能看懂
```

---

## 五、Agent 工作流程——模型如何调用工具

### 5.1 完整工作流程

```
┌─────────────────────────────────────────────────────────────┐
│                Agent 调用工具的完整流程                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ① 用户输入需求                                              │
│     "今天北京天气怎么样？"                                     │
│         ↓                                                   │
│  ② Agent 接收并解析意图                                      │
│     "用户想查天气，位置是北京"                                  │
│         ↓                                                   │
│  ③ Agent 匹配工具                                            │
│     遍历可用工具列表 → 找到 get_weather（描述匹配"天气"）        │
│         ↓                                                   │
│  ④ Agent 准备参数                                            │
│     从用户输入中提取参数 → city="北京"                          │
│         ↓                                                   │
│  ⑤ 执行工具函数                                              │
│     get_weather("北京") → "天气：晴，温度：25°C"               │
│         ↓                                                   │
│  ⑥ Agent 整合响应                                            │
│     工具返回原始结果 → Agent 组织成自然语言                     │
│         ↓                                                   │
│  ⑦ 返回给用户                                                │
│     "北京今天天气是晴天，温度25°C，适合外出。"                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 关键理解

> **Agent 不只是转发工具结果**——它会理解工具返回的内容，再用自己的语言组织成自然的回答。

```
工具返回：    "天气：晴，温度：25°C"
Agent 输出：  "根据最新数据，北京今天晴天，气温约25摄氏度，
              体感舒适，适合户外活动。"
              
→ Agent 在工具结果基础上做了润色和补充！
```

---

## 六、创建 Agent——完整代码实战

### 6.1 核心组件

| 组件 | 类/函数 | 作用 |
|------|---------|------|
| **LLM** | `ChatZhipuAI` | 大语言模型，Agent 的"大脑" |
| **工具列表** | `[tool1, tool2, ...]` | Agent 可调用的工具 |
| **提示词模板** | 从 hub 加载 | 告诉 Agent 何时用什么工具 |
| **Agent** | `create_react_agent` | 创建智能体 |
| **执行器** | `AgentExecutor` | 运行智能体，处理调用循环 |

### 6.2 第一步：导入

```python
import os
from langchain_community.chat_models import ChatZhipuAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
```

### 6.3 第二步：准备 LLM

```python
os.environ["ZHIPUAI_API_KEY"] = "你的Key"
llm = ChatZhipuAI(model="glm-4", temperature=0.5)
```

### 6.4 第三步：准备工具列表

```python
# 将封装好的工具放入列表
tools = [get_weather]
```

> ⚠️ 工具必须是列表形式。`create_react_agent` 的 `tools` 参数要求是一个序列。

### 6.5 第四步：加载提示词模板

> **不推荐自己手写**提示词模板——LangChain Hub 提供了经过验证的模板。

```python
# 从 LangChain Hub 拉取提示词模板
prompt = hub.pull("hwchase17/react")
```

这个模板会告诉 Agent：
- 你是一个智能助手
- 你可以使用以下工具
- 当需要实时数据时调用工具
- 工具返回结果后基于结果回答

### 6.6 第五步：创建 Agent + 执行器

```python
# 创建智能体
agent = create_react_agent(
    llm=llm,          # 大语言模型
    tools=tools,      # 工具列表
    prompt=prompt     # 提示词模板
)

# 创建执行器
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True       # 打印调试日志（可选但推荐）
)
```

### 6.7 第六步：调用

```python
# 调用 Agent
response = agent_executor.invoke({
    "input": "今天北京天气怎么样？"
})

print(response["output"])
```

### 6.8 verbose=True 的日志输出

设置 `verbose=True` 后，能看到 Agent 的完整思考过程：

```
> Entering new AgentExecutor chain...
I need to find out the weather in Beijing today.
Action: get_weather
Action Input: 北京
Observation: 天气：晴，温度：25°C
Thought: I now know the weather in Beijing.
Final Answer: 北京今天天气晴朗，气温25°C，适合外出活动。

> Finished chain.
```

| 日志标签 | 含义 |
|----------|------|
| `Action` | Agent 决定调用哪个工具 |
| `Action Input` | 传给工具的参数 |
| `Observation` | 工具返回的结果 |
| `Thought` | Agent 的推理过程 |
| `Final Answer` | 最终给用户的回答 |

---

## 七、多工具调用

### 7.1 添加第二个工具

```python
# ── 工具1：天气查询 ──
@tool
def get_weather(city: str) -> str:
    """查询指定城市的天气情况"""
    city_code = get_city_code(city)
    # ... API 调用 ...
    return f"天气：{weather}，温度：{temperature}°C"

# ── 工具2：乘法计算 ──
@tool
def multiply(a: int, b: int) -> int:
    """两个数的乘法，返回乘积"""
    return a * b

# ── 工具列表包含两个工具 ──
tools = [get_weather, multiply]
```

### 7.2 Agent 自动选择工具

Agent 会根据用户的输入**自动判断**使用哪个工具：

```
用户："今天北京天气怎么样？"     → Agent 选择 get_weather
用户："2×3等于几？"             → Agent 选择 multiply
用户："帮我修电脑"              → Agent 没有匹配的工具，直接用 LLM 回答
```

### 7.3 测试多工具

```python
test_inputs = [
    "今天北京天气怎么样？",    # → 应该调用 get_weather
    "2×3等于几？",            # → 应该调用 multiply
    "帮我修电脑",             # → 无法匹配工具，LLM 直接回答
]

for question in test_inputs:
    response = agent_executor.invoke({"input": question})
    print(f"问：{question}")
    print(f"答：{response['output']}")
    print("-" * 50)
```

**运行结果：**

```
问：今天北京天气怎么样？
答：北京今天小雨，温度20-25°C...
→ ✅ 调用了 get_weather

问：2×3等于几？
答：2×3等于6。
→ ✅ 调用了 multiply

问：帮我修电脑
答：抱歉，作为一个文本AI助手，我无法直接帮您修理电脑。
    不过我可以尝试提供一些故障排查建议...
→ ✅ 没有匹配工具，LLM 用自己的能力回答
```

---

## 八、⚠️ 参数传递问题与修复

### 8.1 问题现象

这是视频中老师**当场遇到并解决**的核心问题。当 Agent 调用 `multiply(a: int, b: int)` 时：

```
Agent 传参：Action Input: a=1 b=2
                            ↑ 传的是字符串 "a=1 b=2"
函数期望：multiply(a=1, b=2)
                    ↑ 期望的是两个独立的 int 参数

→ ❌ 报错：无法将 "a=1 b=2" 解析为两个整数
```

### 8.2 原因分析

> Agent 将参数合并成了一个字符串传给工具，而工具期望接收两个独立的整数参数。类型注解和 docstring 都无法完全解决这个问题。

### 8.3 解决方案——正则解析输入

修改 `multiply` 函数，让它能接受一个字符串参数并自行解析：

```python
import re

@tool
def multiply(input_str: str) -> int:
    """两个数的乘积。输入格式如 '2×3' 或 'a=2 b=3'"""
    
    # ── 用正则提取所有数字 ──
    numbers = re.findall(r'\d+', input_str)
    
    # ── 确保提取到两个数字 ──
    if len(numbers) == 2:
        a, b = map(int, numbers)  # 转为整数
        return a * b
    else:
        return "错误：请提供两个数字，如 '2×3'"
```

### 8.4 代码逐行解析

```python
numbers = re.findall(r'\d+', input_str)
```

| 写法 | 含义 |
|------|------|
| `re.findall()` | 在字符串中查找所有匹配的内容 |
| `r'\d+'` | 正则表达式：一个或多个数字 |
| 输入 `"a=1 b=2"` | 匹配结果：`['1', '2']` |

```python
a, b = map(int, numbers)
```

| 写法 | 含义 |
|------|------|
| `map(int, numbers)` | 将 `['1', '2']` 中的每个元素传给 `int()` |
| `a, b = ...` | 解包：`a=1, b=2`（已经是整数类型） |

> 💡 `map(int, numbers)` 将列表中的每个元素依次传给 `int` 函数进行类型转换——相当于 `[int('1'), int('2')]` → `[1, 2]`。

---

## 九、多轮对话测试

### 9.1 完整代码

```python
# ── 准备多个问题 ──
test_inputs = [
    "今天北京天气怎么样？",
    "2×3等于几？",
    "帮我修电脑",
]

# ── 逐个测试 ──
for question in test_inputs:
    print(f"\n{'='*50}")
    print(f"用户：{question}")
    response = agent_executor.invoke({"input": question})
    print(f"Agent：{response['output']}")
```

### 9.2 运行结果

```
==================================================
用户：今天北京天气怎么样？
Agent：根据查询结果，北京今天小雨，温度20-25°C，建议带伞出门。

==================================================
用户：2×3等于几？
Agent：2乘以3等于6。

==================================================
用户：帮我修电脑
Agent：抱歉，作为一个文本AI助手，我无法直接帮您修理电脑。
但您可以尝试以下步骤：1. 检查电源连接 2. 重启电脑 3. ...
```

> 🎉 两个工具有的被正确调用，没有工具时 LLM 也能合理应对。

---

## 十、完整代码汇总

```python
import os
import re
import requests
import pandas as pd
from langchain_community.chat_models import ChatZhipuAI
from langchain.tools import tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub

# ============================================================
# 1. 准备 LLM 和全局数据
# ============================================================
os.environ["ZHIPUAI_API_KEY"] = "你的Key"
llm = ChatZhipuAI(model="glm-4", temperature=0.5)
city_df = pd.read_csv("city_code.csv")

# ============================================================
# 2. 城市编码查询函数
# ============================================================
def get_city_code(city: str) -> str:
    """三级匹配：区县 → 城市 → 省份模糊 → 默认北京"""
    match = city_df[city_df["district"] == city]
    if not match.empty:
        return match.iloc[0]["city_code"]
    match = city_df[city_df["city_name"] == city]
    if not match.empty:
        return match.iloc[0]["city_code"]
    match = city_df[city_df["city_name"].str.contains(city, na=False)]
    if not match.empty:
        return match.iloc[0]["city_code"]
    return "101010100"  # 默认北京

# ============================================================
# 3. 工具1：天气查询
# ============================================================
@tool
def get_weather(city: str) -> str:
    """查询指定城市的实时天气情况。"""
    city_code = get_city_code(city)
    url = f"https://api.weather.com/v1?city={city_code}"
    response = requests.get(url)
    data = response.json()
    temp = data.get("result", {}).get("real_time", {}).get("temperature", "未知")
    weather = data.get("result", {}).get("real_time", {}).get("weather", "未知")
    return f"天气：{weather}，温度：{temp}°C"

# ============================================================
# 4. 工具2：乘法计算（含参数解析修复）
# ============================================================
@tool
def multiply(input_str: str) -> int:
    """两个数的乘积。输入如 '2×3' 或 'a=2 b=3'"""
    numbers = re.findall(r'\d+', input_str)
    if len(numbers) == 2:
        a, b = map(int, numbers)
        return a * b
    return "错误：请提供两个数字"

# ============================================================
# 5. 创建 Agent
# ============================================================
tools = [get_weather, multiply]
prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# ============================================================
# 6. 测试
# ============================================================
test_questions = [
    "今天北京天气怎么样？",
    "2×3等于几？",
    "帮我修电脑",
]

for q in test_questions:
    print(f"\n用户：{q}")
    result = agent_executor.invoke({"input": q})
    print(f"Agent：{result['output']}")
```

---

## 十一、常见问题与排错指南

### 11.1 错误速查表

| 错误/问题 | 原因 | 解决方法 | 优先级 |
|-----------|------|----------|:------:|
| `list index out of range` | invoke 参数格式不对 | 用 `{"input": "..."}` 而不是直接传字符串 | 🔴高 |
| `city_code is not defined` | 前面代码块未执行 | 确保 CSV 读取和 get_city_code 已运行 | 🔴高 |
| `requests is not defined` | 未导入 requests | `import requests` | 🔴高 |
| `ModuleNotFoundError: pandas` | 未安装 pandas | `pip install pandas` | 🔴高 |
| Agent 传递参数时类型错误 | Agent 把多个参数合并成字符串 | 用正则 `re.findall(r'\d+', s)` 解析 | 🟡中 |
| `IndexError: list index out of range` | 正则没匹配到足够数字 | 检查输入格式，添加 len 判断 | 🟡中 |
| Agent 不调用工具 | 工具描述不够清晰 | 优化 docstring，明确写出工具用途 | 🟡中 |

### 11.2 排查流程

```
Agent 不调用工具？
    ↓
第一步：开启 verbose
    agent_executor = AgentExecutor(..., verbose=True)
    → 看日志中 Action 是什么
    ↓
第二步：检查工具列表
    print(tools) → 确保工具有在列表中
    ↓
第三步：检查工具 Schema
    print(tool.name, tool.description) → 描述是否清晰？
    ↓
第四步：检查提示词模板
    print(prompt) → Agent 是否被正确告知工具有哪些？

Agent 调用工具但参数出错？
    ↓
    看日志中的 Action Input 是字符串还是多个参数
    → 如果是字符串 → 在工具函数中用正则解析
```

---

## 十二、课后练习

### 练习一：基础 Agent

> 用 `create_react_agent` + `AgentExecutor` 创建一个 Agent，只配备 `get_weather` 这一个工具，测试查询 3 个不同城市的天气。

### 练习二：多工具 Agent

> 创建包含 3 个工具的 Agent：`get_weather`、`multiply`、以及你自己封装的一个新工具（如 `get_time`——返回当前时间）。分别测试三个问题，验证 Agent 能正确选择工具。

| 测试问题 | 期望调用的工具 | 实际调用 |
|----------|:------------:|:--------:|
| 今天上海天气？ | get_weather | |
| 5×8等于几？ | multiply | |
| 现在几点了？ | get_time | |

### 练习三：参数解析修复

> 故意让工具需要两个独立参数（如 `add(a: int, b: int)`），观察 Agent 传参时的行为。然后用正则解析方式修复，验证修复后能正常运行。

### 练习四：三级匹配测试

> 用以下输入测试 `get_city_code` 的三级匹配策略：

| 输入 | 匹配层级 | 返回编码 | 是否正确？ |
|------|:------:|:------:|:--------:|
| "海淀" | 区县 | | |
| "上海" | 城市 | | |
| "广东" | 省份（模糊） | | |
| "xyz" | 默认 | | |

### 练习五：完整流程

> 从零开始：读取 CSV → 封装 get_city_code → 封装 get_weather + @tool → 创建 Agent → 多工具调用。以深圳、广州、杭州为例测试天气查询。

---

## 十三、课程小结

### 13.1 本课核心知识图谱

```
┌────────────────────────────────────────────────────────────┐
│              Agent 创建与多工具调用核心知识体系                 │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  动态城市编码查询                                        │
│      ├── pandas.read_csv → 加载编码表                       │
│      ├── 三级匹配：区县精准 → 城市精准 → 省份模糊            │
│      └── 默认兜底 → 返回北京编码（不怕出错）                  │
│                                                            │
│  2️⃣  Agent 创建五步走                                       │
│      ├── LLM：ChatZhipuAI(model="glm-4")                  │
│      ├── Tools：[weather, multiply, ...]                  │
│      ├── Prompt：hub.pull("hwchase17/react")              │
│      ├── Agent：create_react_agent(llm, tools, prompt)    │
│      └── Executor：AgentExecutor(agent, tools, verbose)  │
│                                                            │
│  3️⃣  Agent 工作流程                                         │
│      用户输入 → 解析意图 → 匹配工具 → 准备参数 →              │
│      执行函数 → 获取结果 → 整合响应 → 返回用户              │
│                                                            │
│  4️⃣  多工具共存                                             │
│      ├── tools = [tool1, tool2, tool3] → 列表             │
│      ├── Agent 根据用户输入自动选择                          │
│      └── 无匹配工具 → LLM 直接用自己的能力回答               │
│                                                            │
│  5️⃣  ⚠️ 参数传递修复                                        │
│      ├── 问题：Agent 将参数合并成字符串                      │
│      ├── 解决：re.findall(r'\d+', s) 正则提取              │
│      └── map(int, numbers) 类型转换                        │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 13.2 一句话总结

> **Agent = LLM + 工具 + 提示词。** `create_react_agent` 创建智能体 → `AgentExecutor` 执行调用 → Agent 自动解析意图、匹配工具、执行并返回结果。多工具共存时只需全部放入列表，Agent 会自动选择。参数传递出错时用正则解析修复。

### 13.3 速记卡

```
┌───────────────────────────────────────────────────────┐
│               Agent 创建速记卡                          │
├───────────────────────────────────────────────────────┤
│                                                       │
│  导入：                                                │
│  from langchain.agents import create_react_agent,     │
│      AgentExecutor                                   │
│  from langchain import hub                           │
│                                                       │
│  创建：                                                │
│  agent = create_react_agent(llm, tools, prompt)      │
│  executor = AgentExecutor(agent, tools, verbose=True)│
│                                                       │
│  调用：                                                │
│  result = executor.invoke({"input": "问题"})          │
│  print(result["output"])                             │
│                                                       │
│  多工具：                                              │
│  tools = [tool1, tool2, tool3]  → 放列表里就行         │
│                                                       │
└───────────────────────────────────────────────────────┘
```

### 13.4 系列课程定位

```
第十五课：语义搜索实战
第十六课：工具封装概念（@tool 基础）
第十七课：天气查询工具实战
第十八课（本课）：Agent 创建与多工具调用 🆕
后续：RAG（检索增强生成）
```

---

*本教学文档基于陈泽鹏老师视频课程（Agent 智能体创建与多工具调用）整理编写。*  
*本文档涵盖动态城市编码三级匹配、真实 API 结果优化、Agent 完整创建流程、多工具共存与自动选择、参数传递问题的正则修复方案。*
