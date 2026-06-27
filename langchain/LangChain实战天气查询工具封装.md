# LangChain 实战——封装天气查询工具

> 基于陈泽鹏老师视频课程整理编写 · 2026年6月

---

## 目录

- [一、课程背景与目标](#一课程背景与目标)
- [二、回顾：@tool 装饰器快速复习](#二回顾tool-装饰器快速复习)
- [三、实战目标——封装一个天气查询工具](#三实战目标封装一个天气查询工具)
- [四、第一步：设计工具函数](#四第一步设计工具函数)
- [五、第二步：用 @tool 装饰](#五第二步用-tool-装饰)
- [六、第三步：验证 Schema 自动生成](#六第三步验证-schema-自动生成)
- [七、第四步：模拟 API 调用](#七第四步模拟-api-调用)
- [八、第五步：集成真实天气 API](#八第五步集成真实天气-api)
- [九、完整代码汇总](#九完整代码汇总)
- [十、工具验证清单](#十工具验证清单)
- [十一、常见问题与排错指南](#十一常见问题与排错指南)
- [十二、课后练习](#十二课后练习)
- [十三、课程小结](#十三课程小结)

---

## 一、课程背景与目标

### 1.1 前情回顾

上一节课我们学习了 LangChain 工具封装的核心概念和 `@tool` 装饰器的基本用法：

```python
from langchain.tools import tool

@tool
def multiply(a: int, b: int) -> int:
    """两个数的乘法，返回乘积"""
    return a * b
```

我们知道了：
- **为什么**需要工具：LLM 拿不到实时数据、无法调用三方 API、存在幻觉问题
- **怎么**封装工具：用 `@tool` 装饰器 + 写全类型注解 + 写清楚注释
- `@tool` 会自动生成 Schema（名称、描述、参数类型），供 LLM 理解和使用

### 1.2 本节课的核心任务

> **从概念到实践：亲手封装一个完整的天气查询工具。**

上一课我们了解了"是什么"和"为什么"，本课我们要亲自动手，从零开始构建一个**真实可用的工具**：

```
用户："今天北京天气怎么样？"
    ↓
Agent 自动选择「天气查询工具」
    ↓
工具调用天气 API → 获取真实数据
    ↓
返回："北京今天晴天，25°C，适合外出。"
```

### 1.3 本课要掌握的目标

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  目标：独立完成一个外部 API 工具的封装全过程        │
│        ├── 从需求分析到函数设计                    │
│        ├── @tool 装饰器的规范使用                  │
│        ├── 模拟数据 → 真实 API 的渐进式开发         │
│        ├── Schema 验证和工具信息查看               │
│        └── 掌握工具封装的完整开发流程               │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 二、回顾：@tool 装饰器快速复习

### 2.1 核心公式

```python
from langchain.tools import tool

@tool                    # 步骤1: 加装饰器
def function_name(        # 步骤2: 清晰的函数名
    param: type,          # 步骤3: 类型注解
) -> return_type:         # 步骤4: 返回值类型
    """详细的描述"""       # 步骤5: docstring
    # ... 业务逻辑 ...
    return result
```

### 2.2 @tool 自动生成的三要素

| 要素 | 对应代码 | LLM 理解 |
|------|----------|----------|
| `name` | 函数名 | "这个工具叫什么" |
| `description` | docstring | "这个工具能干什么" |
| `args_schema` | 类型注解 | "调用这个工具需要传什么参数" |

### 2.3 为什么需要工具？——快速回顾

```
LLM 的三大局限：
├── ❌ 获取不到实时数据（今天天气、股票价格…）
├── ❌ 无法交互三方应用（查订单、发邮件、读数据库…）
└── ❌ 幻觉问题（遇到不知道的会瞎编）

工具解决什么：
├── ✅ 提供实时数据访问能力
├── ✅ 桥接三方应用和 API
├── ✅ 基于真实数据回答，减少幻觉
└── ✅ 模块化设计，方便维护和复用
```

---

## 三、实战目标——封装一个天气查询工具

### 3.1 需求分析

| 需求项 | 详细说明 |
|--------|----------|
| **功能** | 根据城市名称查询天气情况 |
| **输入** | 城市名称（如"北京"）、可选日期 |
| **输出** | 天气描述（如"晴天，25°C"） |
| **数据源** | 先模拟数据，再接入真实天气 API |

### 3.2 用户使用场景

```
场景一：简单查询
用户："今天杭州天气怎么样？"
工具：get_weather("杭州") → "杭州今天多云，28°C"

场景二：Agent 自动调用
用户向 Agent 提问 → Agent 分析需要天气数据 
→ Agent 自动调用 get_weather 工具 → Agent 基于真实数据回答

场景三：指定日期查询
用户："下周一北京天气？"
工具：get_weather("北京", date="2026-06-23") → 返回指定日期的天气
```

### 3.3 开发策略

> **先模拟，再接入**——先写一个返回假数据的版本跑通流程，确认 Schema 正确，再替换为真实 API 调用。

```
开发流程：
Step 1: 设计函数签名（参数、返回值）
Step 2: @tool 装饰，验证 Schema
Step 3: 用模拟数据跑通流程
Step 4: 替换为真实 API（如高德天气 API、和风天气 API）
Step 5: 添加错误处理（网络超时、城市不存在等）
```

---

## 四、第一步：设计工具函数

### 4.1 函数签名设计

```python
def get_weather(city: str, date: Optional[str] = None) -> str:
    """查询指定城市的天气情况。
    
    参数:
        city: 城市名称，如"北京"、"上海"、"深圳"
        date: 日期，格式YYYY-MM-DD。不传则查询今天
        
    返回:
        天气信息字符串，包含温度、天气状况等
    """
    pass
```

### 4.2 设计决策说明

| 设计决策 | 选择 | 理由 |
|----------|:----:|------|
| `city: str` | 必填，无默认值 | 查询天气城市必须指定 |
| `date: Optional[str] = None` | 可选，有默认值 | 不传日期默认查今天 |
| 返回值 `-> str` | 字符串 | Agent 拿到的就是天气描述文本 |
| docstring 包含参数说明 | 详细写 | LLM 能准确理解每个参数的用途 |

### 4.3 为什么要让 date 可选？

```python
# 不传日期 → 默认查今天（最常见的场景）
get_weather("北京")
# → Schema 中 date 不是 required

# 传日期 → 查指定日期（扩展场景）
get_weather("北京", date="2026-06-23")
# → Schema 中 date 是可选的
```

> 💡 有默认值的参数 → `@tool` 的 Schema 中不会标记为 `required`。

---

## 五、第二步：用 @tool 装饰

### 5.1 核心代码

```python
from langchain.tools import tool
from typing import Optional

@tool
def get_weather(city: str, date: Optional[str] = None) -> str:
    """查询指定城市的天气情况。
    
    参数:
        city: 城市名称，如"北京"、"上海"、"深圳"
        date: 日期，格式YYYY-MM-DD。不传则查询今天
        
    返回:
        天气信息字符串
    """
    # 先用模拟数据（后续替换为真实 API）
    weather_data = {
        "北京": "晴天，25°C，微风",
        "上海": "多云，28°C，东南风3级",
        "深圳": "阵雨，30°C，湿度较大",
        "杭州": "晴转多云，26°C",
    }
    
    result = weather_data.get(city, f"暂无{city}的天气数据")
    
    if date:
        return f"{city}在{date}的天气：{result}"
    else:
        return f"{city}今天天气：{result}"
```

### 5.2 代码对比——装饰前后

```python
# ── 装饰前：普通 Python 函数 ──
def get_weather(city: str) -> str:
    return f"{city}天气：晴天"

# 只是一个函数，LLM 不知道它的存在
# 没有 name, description, args_schema

# ── 装饰后：LangChain 工具 ──
@tool
def get_weather(city: str, date: Optional[str] = None) -> str:
    """查询指定城市的天气情况。..."""
    # ...实现...

# 变成了 LangChain Tool 对象！
# get_weather.name         → "get_weather"
# get_weather.description  → "查询指定城市的天气情况。..."
# get_weather.args_schema  → 自动生成的 JSON Schema
```

---

## 六、第三步：验证 Schema 自动生成

### 6.1 查看工具信息

```python
# ── 1. 查看基本属性 ──
print("=== 工具基本信息 ===")
print(f"工具名称：{get_weather.name}")
print(f"工具描述：{get_weather.description}")
print()

# ── 2. 查看参数 Schema ──
print("=== 参数 Schema ===")
print(get_weather.args_schema.model_json_schema())
print()

# ── 3. 查看完整模型信息 ──
print("=== 完整模型信息 ===")
print(get_weather.model_dump())
```

### 6.2 预期输出

```
=== 工具基本信息 ===
工具名称：get_weather
工具描述：查询指定城市的天气情况。

    参数:
        city: 城市名称，如"北京"、"上海"、"深圳"
        date: 日期，格式YYYY-MM-DD。不传则查询今天
        
    返回:
        天气信息字符串

=== 参数 Schema ===
{
    'title': 'get_weatherSchema',
    'type': 'object',
    'properties': {
        'city': {
            'title': 'City',
            'type': 'string'
        },
        'date': {
            'title': 'Date',
            'type': 'string',
            'default': None
        }
    },
    'required': ['city']     ← 只有 city 是必填！
}                             date 有默认值所以不是 required
```

### 6.3 Schema 解读

| Schema 信息 | 含义 | LLM 的推理 |
|-----------|------|-----------|
| `name: "get_weather"` | 工具名称 | "这个工具叫 get_weather" |
| `description: "查询指定城市..."` | 工具描述 | "它是用来查天气的" |
| `city: string, required` | 城市参数，必填 | "调用时必须告诉我查哪个城市" |
| `date: string, not required` | 日期参数，可选 | "可以指定日期，不指定就默认今天" |

---

## 七、第四步：模拟 API 调用

### 7.1 为什么要先模拟？

```
真实 API 开发的问题：
├── 需要注册账号、获取 API Key
├── 有调用次数限制
├── 网络不稳定时无法调试
└── 开发阶段频繁测试 = 浪费额度

模拟数据的优势：
├── 零依赖，写几行字典就行
├── 即时返回，不依赖网络
├── 可以快速验证 Schema 是否正确
├── 跑通流程后再换成真实 API
└── 方便单元测试
```

### 7.2 扩展模拟数据

```python
@tool
def get_weather(city: str, date: Optional[str] = None) -> str:
    """查询指定城市的天气情况。
    
    参数:
        city: 城市名称，如"北京"、"上海"、"深圳"
        date: 日期，格式YYYY-MM-DD。不传则查询今天
    """
    # ── 模拟天气数据库 ──
    weather_db = {
        "北京": {"condition": "晴天", "temp": "25°C", "wind": "微风"},
        "上海": {"condition": "多云", "temp": "28°C", "wind": "东南风3级"},
        "深圳": {"condition": "阵雨", "temp": "30°C", "wind": "南风2级"},
        "杭州": {"condition": "晴转多云", "temp": "26°C", "wind": "东风1级"},
        "成都": {"condition": "阴天", "temp": "22°C", "wind": "北风2级"},
        "广州": {"condition": "雷阵雨", "temp": "32°C", "wind": "西南风3级"},
    }
    
    weather = weather_db.get(city)
    
    if not weather:
        return f"抱歉，暂无{city}的天气数据。请检查城市名称是否正确。"
    
    result = f"{city}：{weather['condition']}，{weather['temp']}，{weather['wind']}"
    
    if date:
        return f"{date} {result}"
    else:
        return f"今日 {result}"
```

### 7.3 测试调用

```python
# ── 测试脚本 ──
print("=== 天气查询工具测试 ===\n")

# 测试1：正常查询
print(get_weather("北京"))
# → 今日 北京：晴天，25°C，微风

# 测试2：指定日期
print(get_weather("上海", date="2026-06-20"))
# → 2026-06-20 上海：多云，28°C，东南风3级

# 测试3：不存在的城市
print(get_weather("火星"))
# → 抱歉，暂无火星的天气数据。请检查城市名称是否正确。

# 测试4：只传城市（利用默认值）
print(get_weather("深圳"))
# → 今日 深圳：阵雨，30°C，南风2级
```

---

## 八、第五步：集成真实天气 API

### 8.1 接入思路

模拟数据跑通后，替换为真实 API：

```python
@tool
def get_weather(city: str, date: Optional[str] = None) -> str:
    """查询指定城市的天气情况。..."""
    
    # ── 方式一：使用高德天气 API ──
    # import requests
    # API_KEY = "你的高德API_Key"
    # url = f"https://restapi.amap.com/v3/weather/weatherInfo"
    # params = {"key": API_KEY, "city": city, "extensions": "base"}
    # response = requests.get(url, params=params)
    # data = response.json()
    # ...
    
    # ── 方式二：使用和风天气 API ──
    # import requests
    # API_KEY = "你的和风API_Key"
    # ...
    
    # ── 方式三：使用 OpenWeatherMap API ──
    # ...
    
    pass  # 具体实现取决于你选择哪个天气 API
```

### 8.2 真实 API 接入模板

```python
import requests
from langchain.tools import tool
from typing import Optional

@tool
def get_weather(city: str, date: Optional[str] = None) -> str:
    """查询指定城市的天气情况。
    
    参数:
        city: 城市名称
        date: 日期，格式YYYY-MM-DD
    """
    try:
        # ── 调用真实天气 API ──
        API_KEY = "你的API_Key"
        url = "https://api.weather.com/v1/current"
        params = {
            "key": API_KEY,
            "city": city,
            "lang": "zh"
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # ── 提取关键信息 ──
        condition = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        
        result = f"{city}：{condition}，{temp}°C"
        
        if date:
            result = f"{date} {result}"
        
        return result
        
    except requests.exceptions.Timeout:
        return f"查询{city}天气超时，请稍后重试。"
    except requests.exceptions.RequestException as e:
        return f"查询{city}天气失败：{str(e)}"
    except KeyError:
        return f"抱歉，未找到{city}的天气信息。"
```

### 8.3 模拟 vs 真实——切换策略

```python
# ── 开发/测试阶段：使用模拟数据 ──
USE_REAL_API = False

@tool
def get_weather(city: str, date: Optional[str] = None) -> str:
    """查询指定城市的天气情况。"""
    
    if USE_REAL_API:
        return _get_weather_from_api(city, date)
    else:
        return _get_weather_from_mock(city, date)


def _get_weather_from_mock(city: str, date: Optional[str] = None) -> str:
    """模拟数据版本"""
    mock_data = {"北京": "晴天，25°C", "上海": "多云，28°C"}
    result = mock_data.get(city, f"暂无{city}的数据")
    return f"{date + ' ' if date else ''}{city}：{result}"


def _get_weather_from_api(city: str, date: Optional[str] = None) -> str:
    """真实 API 版本"""
    # ... 真实 API 调用代码 ...
    pass
```

> 💡 `USE_REAL_API = False` 切换到 `True` 即可从模拟切换到真实 API，无需修改工具接口。

---

## 九、完整代码汇总

```python
from langchain.tools import tool
from typing import Optional

# ============================================================
# 天气查询工具
# ============================================================
@tool
def get_weather(city: str, date: Optional[str] = None) -> str:
    """查询指定城市的天气情况。
    
    参数:
        city: 城市名称，如"北京"、"上海"、"深圳"
        date: 日期，格式YYYY-MM-DD。不传则查询今天
        
    返回:
        天气信息字符串，包含天气状况、温度、风力等
    """
    # ── 天气数据库（后续可替换为真实 API）──
    weather_db = {
        "北京": {"condition": "晴天", "temp": "25°C", "wind": "微风"},
        "上海": {"condition": "多云", "temp": "28°C", "wind": "东南风3级"},
        "深圳": {"condition": "阵雨", "temp": "30°C", "wind": "南风2级"},
        "杭州": {"condition": "晴转多云", "temp": "26°C", "wind": "东风1级"},
        "成都": {"condition": "阴天", "temp": "22°C", "wind": "北风2级"},
        "广州": {"condition": "雷阵雨", "temp": "32°C", "wind": "西南风3级"},
        "武汉": {"condition": "晴天", "temp": "27°C", "wind": "南风1级"},
        "南京": {"condition": "多云转晴", "temp": "24°C", "wind": "西北风2级"},
    }
    
    weather = weather_db.get(city)
    
    if not weather:
        return f"抱歉，暂无「{city}」的天气数据。请检查城市名称是否正确。"
    
    result = f"{city}：{weather['condition']}，{weather['temp']}，{weather['wind']}"
    
    if date:
        return f"{date} {result}"
    else:
        return f"今日 {result}"


# ============================================================
# 验证工具
# ============================================================
if __name__ == "__main__":
    print("=== 工具信息 ===")
    print(f"名称：{get_weather.name}")
    print(f"描述：{get_weather.description.strip()[:50]}...")
    print(f"参数：{get_weather.args_schema.model_json_schema()}")
    
    print("\n=== 功能测试 ===")
    print(get_weather("北京"))
    print(get_weather("上海", date="2026-06-20"))
    print(get_weather("火星"))
```

---

## 十、工具验证清单

封装完工具后，用以下清单逐项检查：

```
□ 函数名清晰描述了功能（如 get_weather，不是 f 或 func1）
□ docstring 详细说明了工具用途和每个参数的含意
□ 所有参数都有类型注解（city: str, date: Optional[str]）
□ 返回值有类型注解（-> str）
□ @tool 装饰器放在函数定义正上方
□ tool.name 能正确打印
□ tool.description 完整正确
□ tool.args_schema 包含所有参数，类型正确
□ required 列表正确（无默认值 = required）
□ 函数可以被正常调用
□ 异常情况有处理（城市不存在、网络错误等）
□ 模拟数据和真实 API 可以方便切换
```

---

## 十一、常见问题与排错指南

### 11.1 错误速查表

| 错误/问题 | 原因 | 解决方法 | 优先级 |
|-----------|------|----------|:------:|
| `ImportError: cannot import name 'tool'` | 导入路径错误 | `from langchain.tools import tool` | 🔴高 |
| Schema 中 date 被标记为 required | 没有指定默认值 | 给 date 加上 `= None` 作为默认值 | 🟡中 |
| LLM 不调用天气工具 | description 不够清晰 | 在 docstring 中明确写"查询天气" | 🟡中 |
| API 调用超时 | 网络问题或 API 服务不稳定 | 添加 try-except + timeout 参数 | 🟡中 |
| 返回结果格式混乱 | 没有统一返回值格式 | 统一返回 `f"{城市}：{天气}，{温度}"` 格式 | 🟢低 |

### 11.2 开发流程建议

```
第 1 步：设计函数签名 → 确认参数和返回值类型
第 2 步：写 docstring → 描述越详细越好
第 3 步：加 @tool → 验证 Schema 生成正确
第 4 步：写模拟数据 → 快速测试功能
第 5 步：注册真实 API → 获取 API Key
第 6 步：替换为真实 API → 添加错误处理
第 7 步：端到端测试 → 确认 LLM + 工具整个链路通畅
```

---

## 十二、课后练习

### 练习一：基础天气工具

> 参照本课代码，封装一个 `get_weather` 工具，要求：
> - 至少包含 5 个城市的模拟数据
> - city 必填，date 可选
> - 打印 tool.name、tool.description、tool.args_schema

### 练习二：扩展工具——空气质量查询

> 扩展天气工具，增加空气质量查询功能。新增一个 `get_air_quality(city: str) -> str` 工具。

```python
@tool
def get_air_quality(city: str) -> str:
    """查询指定城市的空气质量指数（AQI）。
    
    参数:
        city: 城市名称
    """
    # 模拟数据
    aqi_data = {
        "北京": "AQI 85，良",
        "上海": "AQI 55，优",
        "深圳": "AQI 42，优",
    }
    return aqi_data.get(city, f"暂无{city}的空气质量数据")
```

### 练习三：多工具组合

> 同时封装以下三个工具，打印每个工具的 Schema 信息：

| 工具名 | 功能 | 参数 |
|--------|------|------|
| `get_weather` | 天气查询 | city(str), date(可选) |
| `get_air_quality` | 空气质量 | city(str) |
| `get_temperature` | 温度查询 | city(str), unit(str)="celsius" |

### 练习四：接入真实 API

> 选择一个免费的天气 API 服务（如高德天气 API、和风天气 API），注册获取 API Key，将模拟数据替换为真实 API 调用。注意添加错误处理。

### 练习五：工具对比与分析

> 对比模拟版和真实 API 版的 `get_weather`：

| 对比维度 | 模拟版 | 真实 API 版 |
|----------|:----:|:---------:|
| 开发速度 | | |
| 数据真实性 | | |
| 网络依赖 | | |
| 费用 | | |
| 适用阶段 | | |

---

## 十三、课程小结

### 13.1 本课核心知识图谱

```
┌────────────────────────────────────────────────────────────┐
│              天气查询工具封装核心知识体系                       │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  工具设计五要素                                          │
│      ├── 函数名：清晰描述功能（get_weather）                  │
│      ├── 类型注解：每个参数 + 返回值                         │
│      ├── docstring：详细描述用途和参数                       │
│      ├── 默认值：可选参数设默认值（= None）                   │
│      └── @tool 装饰器：放在函数正上方                        │
│                                                            │
│  2️⃣  开发策略：先模拟，再接入                                 │
│      ├── 开发阶段：用字典模拟数据，快速跑通                   │
│      └── 上线阶段：替换为真实 API，加错误处理                │
│                                                            │
│  3️⃣  Schema 自动生成                                         │
│      ├── 无默认值 → required = True                         │
│      ├── 有默认值 → not required                            │
│      └── LLM 通过 Schema 理解工具的功能和调用方式             │
│                                                            │
│  4️⃣  完整流程                                                │
│      设计签名 → @tool装饰 → 验证Schema → 模拟测试 → API接入  │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 13.2 一句话总结

> **封装天气查询工具 = 写好函数签名（类型+注释） + @tool 装饰 + 模拟数据跑通 + 替换真实 API。** 核心公式：`@tool` + 完整类型注解 + 详细 docstring = LLM 可理解可调用的工具。

### 13.3 速记卡

```
┌───────────────────────────────────────────────────────┐
│            天气查询工具速记卡                            │
├───────────────────────────────────────────────────────┤
│                                                       │
│  导入：                                                │
│  from langchain.tools import tool                    │
│  from typing import Optional                         │
│                                                       │
│  封装：                                                │
│  @tool                                                │
│  def get_weather(city: str, date=None) -> str:       │
│      """查询指定城市的天气情况。                        │
│      参数: city城市名, date日期(可选)"""               │
│      return f"{city}天气：晴天"                       │
│                                                       │
│  验证：                                                │
│  get_weather.name / .description / .args_schema      │
│                                                       │
│  策略：模拟 → 跑通 → 换真实 API                        │
│                                                       │
└───────────────────────────────────────────────────────┘
```

### 13.4 练习题答案

> **问**：哪一个**不是**工具调用的主要功能？
>
> - A. 解决大语言模型幻觉问题 ✅ 是
> - B. 扩展 Agent 实时数据访问能力 ✅ 是
> - C. **直接提高语言模型生成质量** ❌ 工具不改变模型本身质量
> - D. 模块化设计便于维护复用 ✅ 是
>
> **答案：C**

### 13.5 系列课程定位

```
第十五课：语义搜索实战（文档问答匹配）
第十六课：工具封装概念（@tool 基础）
第十七课（本课）：天气查询工具实战 🆕
后续：Agent 智能体（自动选择并调用工具）
```

---

*本教学文档基于陈泽鹏老师视频课程（天气查询工具实战练习）整理编写。*  
*本文档涵盖从工具设计、@tool 封装、Schema 验证、模拟开发到真实 API 接入的完整实战流程。*
