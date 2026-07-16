# Core 模块精讲——整个 Agent 系统的基石

> 基于教学视频课程整理编写 · 2026年6月

---

## 目录

- [一、本节概述与学习目标](#一本节概述与学习目标)
- [二、Core 模块在架构中的位置](#二core-模块在架构中的位置)
- [三、config.py——统一配置管理中心](#三configpy统一配置管理中心)
- [四、llm_driver.py——大模型实例化工��](#四llm_driverpy大模型实例化工厂)
- [五、多厂商支持的映射设计](#五多厂商支持的映射设计)
- [六、测试驱动——验证 Core 模块](#六测试驱动验证-core-模块)
- [七、使用指南——日常怎么用 Core 模块](#七使用指南日常怎么用-core-模块)
- [八、扩展指南——加新厂商只需三步](#八扩展指南加新厂商只需三步)
- [九、常见问题与排错指南](#九常见问题与排错指南)
- [十、课后练习](#十课后练习)
- [十一、本节小结](#十一本节小结)

---

## 一、本节概述与学习目标

### 1.1 本节定位

> 这是「多 Agent 开发实战」系列的**第三课**——也是我们第一次深入到具体代码。Core 模块是整个系统的**最底层**，几乎所有其他模块都依赖它。它管两件事：**配置从哪里来**（config.py）和**大模型怎么调**（llm_driver.py）。

```
┌─────────────────────────────────────────┐
│           本系列课程体系                   │
├─────────────────────────────────────────┤
│                                         │
│  开篇：课程总览                           │
│  第1课：为什么学 + 范式转变                │
│  第2课：架构总览                          │
│  第3课（本节）：Core 模块精讲  ← 你在这里   │
│  后续课程：Schemas → Memory → Agent      │
│                                         │
│  本课是第一个"动手写代码"的课               │
│                                         │
└─────────────────────────────────────────┘
```

### 1.2 本课要掌握的目标

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  目标一：理解 Core 模块的两大职责                          │
│         ├── config.py：统一管理所有配置                    │
│         └── llm_driver.py：封装大模型实例化                │
│                                                         │
│  目标二：掌握 pydantic-settings 的配置管理模式             │
│         ├── BaseSettings 自动从 .env 加载                 │
│         ├── 优先级：.env > 默认值                         │
│         ├── 大小写不敏感                                  │
│         └── 类型校验 + 默认值设定                          │
│                                                         │
│  目标三：掌握多厂商支持的映射设计                           │
│         ├── Provider → URL → Model 的映射关系             │
│         ├── 切换厂商只需改一个参数                         │
│         └── 加新厂商只需三步                              │
│                                                         │
│  目标四：掌握缓存机制和工厂模式                            │
│         ├── @lru_cache 避免重复读取 .env                  │
│         ├── 实例缓存避免重复创建 LLM 对象                  │
│         └── get_llm() 一行代码创建模型实例                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 二、Core 模块在架构中的位置

### 2.1 依赖关系中的"地基"

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
│  Schemas 层 (数据结构定义)                                    │
│      ↑ 依赖                                                  │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Core 层（本课）  ← 最底层，地基！                 │       │
│  │  • config.py：配置管理                            │       │
│  │  • llm_driver.py：大模型调用                      │       │
│  │                                                  │       │
│  │  依赖：几乎为 0                                    │       │
│  │  → 只需要 API Key 就能独立测试                     │       │
│  └──────────────────────────────────────────────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Core 模块的两个文件

```
src/core/
├── __init__.py
├── config.py          # 配置管理中心
│   ├── Settings       # 全局配置（从 .env 加载）
│   ├── ModelConfig    # 大模型默认配置
│   ├── PROVIDER_MAP   # 厂商 → URL 映射
│   ├── MODEL_MAP      # 厂商 → 默认模型映射
│   └── get_settings() # 配置单例（缓存）
│
└── llm_driver.py      # 大模型实例化工厂
    ├── get_llm()      # 一行代码创建 LLM 实例
    └── _llm_cache     # 实例缓存
```

---

## 三、config.py——统一配置管理中心

### 3.1 为什么需要统一配置管理

```
没有统一配置管理时：                        有统一配置管理时：

# agent_a.py                              # .env
api_key = "sk-xxx"                        LLM_PROVIDER=deepseek
                                          DEEPSEEK_API_KEY=sk-xxx
# agent_b.py
api_key = "sk-xxx"                        # config.py 自动加载
                                          settings = get_settings()
# tools.py                                api_key = settings.deepseek_api_key
base_url = "https://..."                  # → 所有模块从 settings 读取

😰 问题：                                   ✅ 好处：
• API Key 散落在各处，改了要改 N 个文件        • 一处配置，全局生效
• 切换模型要全局搜索替换                      • 切模型只改 .env 一行
• 容易把 Key 提交到 Git                     • .env 在 .gitignore 中
• 没有默认值，漏配就崩溃                      • 有默认值兜底
```

### 3.2 BaseSettings——自动从 .env 加载

> Pydantic 的 `BaseSettings` 是本模块的核心基类。它比传统 JSON/YAML 配置文件有几个关键优势。

```python
# ── config.py: Settings 类 ──
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """
    全局配置类。
    继承 BaseSettings → 自动从 .env 文件加载配置。

    优先级：
    .env 文件中的值  >  代码中的默认值

    大小写不敏感：
    .env 中写 LLM_PROVIDER 或 llm_provider 都能正确加载
    """

    # ── LLM 厂商配置 ──
    llm_provider: str = Field(
        default="deepseek",
        description="默认大模型厂商。可选：deepseek / openai / kimi / qwen / ..."
    )

    # ── 各厂商 API Key ──
    deepseek_api_key: str = Field(default="", description="DeepSeek API Key")
    openai_api_key: str = Field(default="", description="OpenAI API Key")
    kimi_api_key: str = Field(default="", description="Kimi(Moonshot) API Key")
    qwen_api_key: str = Field(default="", description="千问 API Key")
    zhipu_api_key: str = Field(default="", description="智谱AI API Key")

    # ── 模型调用参数 ──
    temperature: float = Field(default=0.7, description="模型随机性 0-1")
    max_tokens: int = Field(default=4096, description="最大输出 Token 数")

    # ── HTTP 服务配置 ──
    api_host: str = Field(default="0.0.0.0", description="API 监听地址")
    api_port: int = Field(default=8000, description="API 监听端口")

    class Config:
        # ⚠️ 关键：告诉 BaseSettings 从 .env 文件加载
        env_file = ".env"
        env_file_encoding = "utf-8"
        # 大小写不敏感
        case_sensitive = False
```

```
BaseSettings 的四大优势：

1️⃣  自动映射
    配置好 env_file = ".env" 之后，
    .env 中的 LLM_PROVIDER=deepseek
    → 自动填充到 Settings.llm_provider
    不需要手动写任何读取和映射代码！

2️⃣  类型校验
    api_port: int = Field(default=8000)
    → 如果 .env 中写了 API_PORT=abc
    → 启动时直接报错，而不是运行时才发现

3️⃣  默认值兜底
    每个字段都有 default 值
    → .env 中没配？没关系，用默认值
    → 不影响系统启动

4️⃣  大小写不敏感
    .env 中写 LLM_PROVIDER 或 llm_provider
    → Settings.llm_provider 都能正确读到
```

### 3.3 厂商映射表

```python
# ── config.py: 厂商映射 ──

# 厂商 → API 端点 URL 映射
PROVIDER_URL_MAP: dict[str, str] = {
    "deepseek": "https://api.deepseek.com/v1",
    "openai": "https://api.openai.com/v1",
    "kimi": "https://api.moonshot.cn/v1",
    "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "zhipu": "https://open.bigmodel.cn/api/paas/v4",
    "doubao": "https://ark.cn-beijing.volces.com/api/v3",
}

# 厂商 → 默认模型映射
MODEL_MAP: dict[str, str] = {
    "deepseek": "deepseek-chat",
    "openai": "gpt-4o",
    "kimi": "kimi-k2.5",
    "qwen": "qwen-turbo",
    "zhipu": "glm-4",
    "doubao": "doubao-pro-32k",
}
```

```
为什么需要这些映射表？

场景：用户把 provider 从 deepseek 切成 kimi

如果没有映射表：
    → 用户不仅要改 provider
    → 还要手动去查 Kimi 的 URL 是什么
    → 还要查 Kimi 有哪些模型可用

有了映射表：
    → 用户只改 provider="kimi"
    → URL 自动取 PROVIDER_URL_MAP["kimi"]
    → 模型自动取 MODEL_MAP["kimi"]
    → 一键切换！
```

### 3.4 ModelConfig——模型默认配置

```python
# ── config.py: ModelConfig ──
from functools import lru_cache
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """
    大模型调用的默认配置。
    根据 provider 自动匹配 URL 和模型名。
    """
    provider: str
    api_key: str
    base_url: str
    model_name: str
    temperature: float = 0.7

    @classmethod
    def from_settings(
        cls,
        settings: Settings,
        provider: str | None = None
    ) -> "ModelConfig":
        """
        从全局配置创建 ModelConfig。

        Args:
            settings: 全局 Settings 实例
            provider: 指定的厂商。如果为 None，使用全局默认
        """
        # 如果没指定 provider，用全局默认
        actual_provider = provider or settings.llm_provider

        # 根据厂商名获取对应的 API Key
        # 例如 provider="deepseek" → settings.deepseek_api_key
        api_key = getattr(settings, f"{actual_provider}_api_key", "")

        # 从映射表获取 URL 和模型名
        base_url = PROVIDER_URL_MAP.get(actual_provider, "")
        model_name = MODEL_MAP.get(actual_provider, "")

        return cls(
            provider=actual_provider,
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            temperature=settings.temperature,
        )


# ── 缓存机制：避免重复读取 .env ──
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    获取全局配置的单例。
    使用 lru_cache 装饰器 → 只在第一次调用时读取 .env 文件，
    后续调用直接返回缓存的实例。

    为什么需要缓存？
    → 避免每次调用都去读磁盘上的 .env 文件
    → 在多处使用时保持配置一致性
    → 相当于一个全局单例
    """
    return Settings()
```

```
get_settings() 的缓存机制：

第一次调用 get_settings()：
    → 读取 .env 文件
    → 创建 Settings 实例
    → 缓存起来

第二次调用 get_settings()：
    → 直接返回缓存的实例 ✅
    → 不再读磁盘

第三次、第四次……：
    → 同上，直接返回缓存

结果：整个应用生命周期内，.env 只被读取一次！
```

---

## 四、llm_driver.py——大模型实例化工厂

### 4.1 为什么需要封装

```python
# ── ❌ 没有封装时 ──
# 每次调用都要写一堆参数

# agent_a.py
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    model="deepseek-chat",
    base_url="https://api.deepseek.com/v1",
    api_key="sk-xxxxxxxxxxxxx",
    temperature=0.7
)

# agent_b.py
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(  # 又写一遍！
    model="deepseek-chat",
    base_url="https://api.deepseek.com/v1",
    api_key="sk-xxxxxxxxxxxxx",
    temperature=0.7
)

# 切模型时 → 两个文件都要改 → 漏改一个就出 bug

# ── ✅ 有封装后 ──
# agent_a.py
from src.core.llm_driver import get_llm
llm = get_llm()  # 一行搞定！

# agent_b.py
from src.core.llm_driver import get_llm
llm = get_llm()  # 同样一行！

# 切模型时 → 改 .env 一行 → 全局生效！
```

### 4.2 get_llm() 完整实现

```python
# ── llm_driver.py ──
"""
大模型实例化工厂。
提供 get_llm() 函数，一行代码创建配置好的 LLM 实例。
"""
from functools import lru_cache
from langchain_openai import ChatOpenAI
from .config import ModelConfig, get_settings

@lru_cache(maxsize=32)
def get_llm(
    provider: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
) -> ChatOpenAI:
    """
    创建大模型实例的工厂函数。

    Args:
        provider: 厂商名。None=使用全局默认（.env 中的 LLM_PROVIDER）
        model: 模型名。None=使用该厂商的默认模型
        temperature: 随机性。None=使用全局默认（0.7）

    Returns:
        已配置好的 ChatOpenAI 实例

    Examples:
        # 使用默认配置（.env 中的设置）
        llm = get_llm()

        # 切换到千问
        llm = get_llm(provider="qwen")

        # 使用千问的最新模型，调低随机性
        llm = get_llm(provider="qwen", model="qwen-max", temperature=0.3)

        # 只用默认厂商，但换个模型
        llm = get_llm(model="deepseek-reasoner")
    """

    # 加载全局配置
    settings = get_settings()

    # 确定最终的参数值
    actual_provider = provider or settings.llm_provider
    actual_temperature = temperature if temperature is not None else settings.temperature

    # 获取该厂商的配置
    model_config = ModelConfig.from_settings(settings, actual_provider)

    # 确定模型名
    actual_model = model or model_config.model_name

    # ── 创建 ChatOpenAI 实例 ──
    return ChatOpenAI(
        model=actual_model,
        base_url=model_config.base_url,
        api_key=model_config.api_key,
        temperature=actual_temperature,
    )
```

### 4.3 实例缓存机制

```python
# ── @lru_cache 的作用 ──

# maxsize=32 → 最多缓存 32 个不同的 LLM 实例

# 场景1：多次调用相同参数
llm1 = get_llm()                    # 创建实例 → 缓存
llm2 = get_llm()                    # 命中缓存 → 直接返回
# llm1 is llm2 → True ✅ （同一个对象！）

# 场景2：不同参数创建不同实例
llm_deepseek = get_llm(provider="deepseek")   # 实例A → 缓存
llm_qwen = get_llm(provider="qwen")           # 实例B → 缓存
llm_kimi = get_llm(provider="kimi")           # 实例C → 缓存
# 三个不同的实例，各自缓存

# 为什么需要缓存？
# → 节省内存（同一个 provider 共用一个实例）
# → 避免重复创建对象
# → 相同参数 = 相同实例，方便在不同模块间传递
```

### 4.4 使用方式总结

```python
# ── 各种使用姿势 ──

from src.core.llm_driver import get_llm

# 1. 最简用法：用 .env 中的默认配置
llm = get_llm()

# 2. 切换厂商
llm = get_llm(provider="kimi")

# 3. 换模型
llm = get_llm(model="deepseek-reasoner")

# 4. 调整随机性
llm = get_llm(temperature=0.1)  # 更确定性
llm = get_llm(temperature=1.0)  # 更有创造性

# 5. 全部自定义
llm = get_llm(
    provider="qwen",
    model="qwen-max",
    temperature=0.3,
)

# 6. 绑定工具
from langchain_core.tools import tool

@tool
def my_tool(query: str) -> str:
    """工具描述"""
    return f"结果: {query}"

llm_with_tools = get_llm().bind_tools([my_tool])

# 7. 绑定结构化输出
from pydantic import BaseModel

class MyOutput(BaseModel):
    answer: str
    confidence: float

llm_structured = get_llm().with_structured_output(MyOutput)
```

---

## 五、多厂商支持的映射设计

### 5.1 完整映射关系

```
用户指定 provider="kimi"
    ↓
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Step 1: 获取 API Key                                       │
│      getattr(settings, "kimi_api_key")                      │
│      → 从 .env 中的 KIMI_API_KEY=sk-xxx 读取                │
│                                                             │
│  Step 2: 获取 Base URL                                      │
│      PROVIDER_URL_MAP["kimi"]                               │
│      → "https://api.moonshot.cn/v1"                         │
│                                                             │
│  Step 3: 获取默认模型                                        │
│      MODEL_MAP["kimi"]                                      │
│      → "kimi-k2.5"                                          │
│                                                             │
│  Step 4: 组装 ChatOpenAI                                    │
│      ChatOpenAI(                                            │
│          model="kimi-k2.5",                                 │
│          base_url="https://api.moonshot.cn/v1",             │
│          api_key="sk-xxx",                                  │
│          temperature=0.7,                                   │
│      )                                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 厂商参数获取优先级

```
每个配置参数的优先级：

1. API Key：
   优先从 .env 读 → 没有就用 default=""（空字符串）
   建议：至少配一个厂商的 API Key

2. Base URL：
   优先从 PROVIDER_URL_MAP 读 → 如果厂商不在映射表 → 空字符串
   建议：新厂商先在映射表注册

3. Model Name：
   优先从 MODEL_MAP 读 → 如果厂商不在映射表 → 空字符串
   可以通过 get_llm(model="xxx") 在调用时覆盖

4. Temperature：
   优先用 get_llm(temperature=...) 指定的值
   → 没指定就用 Settings.temperature（.env 或默认 0.7）
```

---

## 六、测试驱动——验证 Core 模块

### 6.1 测试 config.py

```python
# ── tests/test_core.py: test_config ──
"""
测试 config.py 的配置加载功能。
"""
import pytest
from src.core.config import Settings, ModelConfig, get_settings, PROVIDER_URL_MAP, MODEL_MAP


class TestSettings:
    """测试全局配置类"""

    def test_default_provider(self):
        """测试默认厂商为 deepseek"""
        settings = Settings()
        assert settings.llm_provider == "deepseek"

    def test_set_provider(self):
        """测试手动设置厂商"""
        settings = Settings()
        settings.llm_provider = "kimi"
        assert settings.llm_provider == "kimi"

    def test_temperature_range(self):
        """测试 temperature 在合理范围内"""
        settings = Settings()
        settings.temperature = 0.7
        assert 0 <= settings.temperature <= 1

    def test_default_api_port(self):
        """测试默认端口"""
        settings = Settings()
        assert settings.api_port == 8000


class TestModelConfig:
    """测试模型默认配置"""

    def test_deepseek_config(self):
        """测试 DeepSeek 的配置"""
        settings = Settings()
        config = ModelConfig.from_settings(settings, "deepseek")

        assert config.provider == "deepseek"
        assert "deepseek.com" in config.base_url
        assert config.model_name == "deepseek-chat"

    def test_kimi_config(self):
        """测试 Kimi 的配置"""
        settings = Settings()
        config = ModelConfig.from_settings(settings, "kimi")

        assert config.provider == "kimi"
        assert "moonshot.cn" in config.base_url
        assert config.model_name == "kimi-k2.5"

    def test_fallback_to_default_provider(self):
        """测试不指定 provider 时使用默认值"""
        settings = Settings()
        config = ModelConfig.from_settings(settings, None)

        # 应该使用全局默认 provider
        assert config.provider == settings.llm_provider

    def test_unknown_provider(self):
        """测试未注册的厂商"""
        settings = Settings()
        config = ModelConfig.from_settings(settings, "unknown_provider")

        # URL 和 Model 为空，但不应报错
        assert config.base_url == ""
        assert config.model_name == ""


class TestProviderMaps:
    """测试厂商映射表"""

    def test_known_providers_have_url(self):
        """测试已知厂商都有 URL 和 Model"""
        for provider in ["deepseek", "openai", "kimi", "qwen", "zhipu"]:
            assert provider in PROVIDER_URL_MAP, f"{provider} 缺少 URL 映射"
            assert provider in MODEL_MAP, f"{provider} 缺少 Model 映射"

    def test_url_format(self):
        """测试 URL 格式正确（以 https:// 开头）"""
        for provider, url in PROVIDER_URL_MAP.items():
            assert url.startswith("https://"), f"{provider} 的 URL 格式错误: {url}"
```

### 6.2 测试 llm_driver.py

```python
# ── tests/test_core.py: test_llm ──
"""
测试 llm_driver.py 的大模型实例化功能。
使用 mock 避免真正调用外部 API。
"""
import pytest
from unittest.mock import patch, MagicMock
from src.core.llm_driver import get_llm


class TestGetLLM:
    """测试 get_llm 工厂函数"""

    @patch("src.core.llm_driver.ChatOpenAI")
    def test_default_llm_creation(self, mock_chat_openai):
        """测试用默认配置创建 LLM"""
        # Mock ChatOpenAI 避免真正创建连接
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance

        llm = get_llm()

        # 验证 ChatOpenAI 被调用了
        mock_chat_openai.assert_called_once()

        # 验证返回的是 mock 实例
        assert llm == mock_instance

    @patch("src.core.llm_driver.ChatOpenAI")
    def test_custom_provider(self, mock_chat_openai):
        """测试指定 provider 创建 LLM"""
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance

        llm = get_llm(provider="kimi")

        # 验证传入的参数中包含 kimi 的 URL
        call_kwargs = mock_chat_openai.call_args.kwargs
        assert "moonshot.cn" in call_kwargs.get("base_url", "")

    @patch("src.core.llm_driver.ChatOpenAI")
    def test_custom_temperature(self, mock_chat_openai):
        """测试自定义 temperature"""
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance

        llm = get_llm(temperature=0.3)

        call_kwargs = mock_chat_openai.call_args.kwargs
        assert call_kwargs.get("temperature") == 0.3

    @patch("src.core.llm_driver.ChatOpenAI")
    def test_custom_model(self, mock_chat_openai):
        """测试自定义 model"""
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance

        llm = get_llm(model="custom-model-name")

        call_kwargs = mock_chat_openai.call_args.kwargs
        assert call_kwargs.get("model") == "custom-model-name"

    def test_multiple_calls_use_cache(self):
        """测试缓存：多次调用返回同一个实例"""
        llm1 = get_llm()
        llm2 = get_llm()

        # 相同参数应该返回同一个缓存的实例
        assert llm1 is llm2
```

### 6.3 运行测试

```bash
# ── 运行 Core 模块的所有测试 ──
$ uv run pytest tests/test_core.py -v

# 预期输出：
# test_default_provider ................... PASSED ✅
# test_set_provider ....................... PASSED ✅
# test_temperature_range .................. PASSED ✅
# test_default_api_port ................... PASSED ✅
# test_deepseek_config .................... PASSED ✅
# test_kimi_config ........................ PASSED ✅
# test_fallback_to_default_provider ....... PASSED ✅
# test_known_providers_have_url ........... PASSED ✅
# test_default_llm_creation ............... PASSED ✅
# test_custom_provider .................... PASSED ✅
# test_custom_temperature ................. PASSED ✅
# test_custom_model ....................... PASSED ✅
#
# ========== 12 passed in 0.85s ==========
```

---

## 七、使用指南——日常怎么用 Core 模块

### 7.1 初次配置（只需做一次）

```bash
# Step 1: 复制环境变量模板
cp .env.example .env

# Step 2: 编辑 .env，至少填一个厂商的 API Key
# .env 内容：
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-your-real-key-here

# Step 3: 验证配置是否生效
uv run python -c "
from src.core.config import get_settings
s = get_settings()
print(f'Provider: {s.llm_provider}')
print(f'API Key 已配置: {bool(s.deepseek_api_key)}')
"
```

### 7.2 日常切换模型

```bash
# ── 方式一：改 .env（推荐，全局生效）──
# 编辑 .env：
LLM_PROVIDER=kimi
# 保存 → 所有模块自动切换为 Kimi

# ── 方式二：代码中临时指定 ──
from src.core.llm_driver import get_llm
llm = get_llm(provider="qwen")  # 只用千问这一次
```

### 7.3 在 Agent 中使用

```python
# ── 典型用法：在 Agent 模块中调用 ──
from src.core.llm_driver import get_llm

class ChatAgent:
    def __init__(self):
        # 一行创建 LLM 实例
        self.llm = get_llm()

        # 或者绑定工具
        self.llm_with_tools = get_llm().bind_tools([...])

        # 或者使用结构化输出
        self.llm_structured = get_llm().with_structured_output(...)
```

---

## 八、扩展指南——加新厂商只需三步

### 8.1 以添加"豆包（Doubao）"为例

```
Step 1: 在 config.py 的映射表中注册
────────────────────────────────────

# 添加 URL 映射
PROVIDER_URL_MAP["doubao"] = "https://ark.cn-beijing.volces.com/api/v3"

# 添加默认模型映射
MODEL_MAP["doubao"] = "doubao-pro-32k"

Step 2: 在 Settings 中添加 API Key 字段
────────────────────────────────────

class Settings(BaseSettings):
    ...
    doubao_api_key: str = Field(default="", description="豆包 API Key")

Step 3: 在 .env 中配置
────────────────────────────────────

DOUBAO_API_KEY=your-doubao-api-key

✅ 完成！现在可以使用了：
llm = get_llm(provider="doubao")
```

### 8.2 扩展清单

```
加新厂商检查清单：

□ PROVIDER_URL_MAP 中添加了 URL
□ MODEL_MAP 中添加了默认模型
□ Settings 类中添加了 {provider}_api_key 字段
□ .env 或 .env.example 中添加了对应的 API Key 占位
□ 测试中添加了新厂商的验证用例
□ test_known_providers_have_url 测试通过
```

---

## 九、常见问题与排错指南

### 9.1 错误速查表

| 错误现象 | 原因 | 解决方法 |
|----------|------|----------|
| `Settings 读取不到 .env 中的值` | .env 文件不在项目根目录 | 确认 .env 在运行目录下；或指定 `env_file` 的绝对路径 |
| `API Key 为空` | .env 中没配或 key 名称不对 | 检查 .env 中的 key 名是否与 Settings 中的字段名对应（大小写不敏感） |
| `ChatOpenAI 连接超时` | base_url 不正确或网络问题 | 检查 PROVIDER_URL_MAP 中的 URL；确认能访问对应厂商 |
| `Model not found` | 模型名错误 | 检查 MODEL_MAP 或手动指定正确的 model 名 |
| `测试中 api_key 验证失败` | 测试环境没有配对应厂商的 Key | 使用 mock 避免真实调用；或在 CI 中注入环境变量 |
| `切了 .env 的 provider 但没生效` | 缓存问题，Settings 只加载了一次 | 重启应用；或清除 lru_cache |

### 9.2 排查流程

```
Core 模块问题排查：

Step 1: 确认 .env 文件存在且格式正确
    $ cat .env
    LLM_PROVIDER=deepseek
    DEEPSEEK_API_KEY=sk-xxx

Step 2: 确认配置能正常加载
    $ python -c "from src.core.config import get_settings; print(get_settings().llm_provider)"
    → 应该输出: deepseek

Step 3: 确认 LLM 能正常创建
    $ python -c "from src.core.llm_driver import get_llm; llm=get_llm(); print(llm.model_name)"
    → 应该输出: deepseek-chat

Step 4: 确认 LLM 能正常调用
    $ python -c "
    from src.core.llm_driver import get_llm
    llm = get_llm()
    print(llm.invoke('你好'))
    "
    → 应该输出 AI 的回复

Step 5: 运行测试验证
    $ uv run pytest tests/test_core.py -v
```

### 9.3 常见陷阱

**陷阱一：.env 文件没放在正确位置**

```bash
# ❌ 错误：.env 在 src/ 子目录下
src/.env         # BaseSettings 默认从当前工作目录读取

# ✅ 正确：.env 在项目根目录
.env             # 与 pyproject.toml 同级
```

**陷阱二：不同厂商的 API Key 名称搞混**

```bash
# ❌ 错误：用错了 Key
LLM_PROVIDER=deepseek
# Settings 会找 deepseek_api_key
# 但 .env 中写的是：
DEEPSEEK_KEY=sk-xxx    # 字段名不对！

# ✅ 正确：
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxx  # 格式: {PROVIDER}_API_KEY
```

**陷阱三：改完 .env 后没有重启**

```python
# ❌ 改了 .env 但没重启
# get_settings() 有缓存 → 还是旧的配置

# ✅ 要么重启应用，要么开发时清除缓存
from src.core.config import get_settings
get_settings.cache_clear()  # 手动清缓存
```

---

## 十、课后练习

### 练习一：验证配置（⭐）

**目标**：配置 .env 并验证加载成功

**要求**：
- 创建 .env 文件
- 至少配置一个厂商的 API Key
- 用 Python 代码验证配置加载成功

**验收标准**：
- `get_settings().llm_provider` 输出正确的厂商名
- `get_settings().{provider}_api_key` 不为空字符串

### 练习二：多厂商切换测试（⭐⭐）

**目标**：体验一键切换模型的便利

**要求**：
- 配置两个不同厂商的 API Key（如 DeepSeek + Kimi）
- 分别用两个厂商调用模型，回答同一个问题
- 对比两个厂商的回答风格和速度

**验收标准**：
- 两个厂商都能正常返回结果
- 能说出两个厂商回答的差异

### 练习三：添加新厂商（⭐⭐⭐）

**目标**：实践扩展新厂商

**要求**：
- 在映射表中添加一个新厂商（如 SiliconFlow 硅基流动）
- 在 Settings 中添加对应的 API Key 字段
- 用新厂商成功调用模型并验证

**验收标准**：
- `get_llm(provider="siliconflow")` 能正常创建实例
- 能成功调用并返回结果

### 练习四：写一个缺少 API Key 的测试（⭐⭐⭐）

**目标**：完善测试覆盖

**要求**：
- 写一个测试用例，模拟"缺少 API Key"的场景
- 验证系统在缺少 Key 时的行为是否符合预期（报错 or 空字符串？）

**验收标准**：
- 测试能正常运行
- 覆盖了边界情况

### 练习五：绑定工具的结构化输出（⭐⭐⭐⭐）

**目标**：在 Core 层之上验证 LLM 的工具调用能力

**要求**：
- 用 `get_llm()` 创建 LLM 实例
- 绑定一个自定义工具（如计算器工具）
- 验证 LLM 能否正确判断何时需要调用工具

**验收标准**：
- LLM 在需要计算时会调用工具
- 工具调用后 LLM 能正确整合结果

---

## 十一、本节小结

### 11.1 核心知识图谱

```
┌──────────────────────────────────────────────────────────────┐
│          Core 模块精讲——核心知识体系                             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1️⃣  Core 模块的定位                                          │
│      ├── 最底层：几乎不依赖任何其他模块                          │
│      ├── 两个文件：config.py（配置） + llm_driver.py（调用）    │
│      └── 整个系统的地基：所有上层模块都依赖它                    │
│                                                              │
│  2️⃣  config.py——配置管理                                      │
│      ├── BaseSettings：自动从 .env 加载，大小写不敏感           │
│      ├── 优先级：.env > 默认值                                 │
│      ├── PROVIDER_URL_MAP：厂商 → URL 映射                     │
│      ├── MODEL_MAP：厂商 → 默认模型映射                        │
│      └── @lru_cache：全局单例，只加载一次 .env                  │
│                                                              │
│  3️⃣  llm_driver.py——LLM 实例化                                │
│      ├── get_llm()：一行代码创建 LLM 实例                      │
│      ├── 可选参数：provider / model / temperature              │
│      ├── 默认用全局配置，参数可覆盖                             │
│      └── @lru_cache(32)：实例缓存，节省资源                     │
│                                                              │
│  4️⃣  多厂商支持                                               │
│      ├── 切换厂商：改 .env 一行 或 get_llm(provider="xxx")     │
│      ├── 映射表自动匹配 URL + Model                            │
│      └── 加新厂商只需三步：注册 URL + 注册 Model + 加 API Key   │
│                                                              │
│  5️⃣  测试驱动                                                 │
│      ├── test_config：验证配置加载和默认值                      │
│      ├── test_llm：用 mock 验证 LLM 实例化                     │
│      └── 12 个测试用例全部通过 ✅                               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 11.2 一句话总结

> **Core 模块是整个 Agent 系统的"电源开关"和"发动机"**——config.py 通过 pydantic-settings 统一管理所有配置（一键从 .env 加载，大小写不敏感，有默认值兜底），llm_driver.py 通过 get_llm() 工厂函数一行代码创建任意厂商的大模型实例（自动匹配 URL 和 Model，支持缓存），两者配合让你切换模型只需改一行 .env，加新厂商只需三步，所有上层 Agent 模块只依赖于这两个简单接口。

### 11.3 关键 API 速查

| API | 用途 | 示例 |
|-----|------|------|
| `get_settings()` | 获取全局配置 | `s = get_settings(); s.llm_provider` |
| `get_llm()` | 默认配置创建 LLM | `llm = get_llm()` |
| `get_llm(provider="kimi")` | 切换厂商 | `llm = get_llm(provider="kimi")` |
| `get_llm(model="xxx")` | 切换模型 | `llm = get_llm(model="gpt-4o")` |
| `get_llm(temperature=0.3)` | 调整随机性 | `llm = get_llm(temperature=0.3)` |
| `get_llm().bind_tools([...])` | 绑定工具 | `llm = get_llm().bind_tools(tools)` |
| `get_llm().with_structured_output(...)` | 结构化输出 | `llm = get_llm().with_structured_output(Schema)` |

### 11.4 下节预告

```
下一课：Schemas 层——数据结构定义

内容预告：
├── 请求/响应的 Pydantic 模型定义
├── RouterDecision 路由决策结构
├── MeetingSummary 会议纪要结构
├── 为什么要做数据结构分层
└── 测试：test_schemas.py
```

---

*本教学文档基于陈泽鹏老师视频课程整理编写。*
*本文档为 LangGraph 多 Agent 开发实战系列的第三课，涵盖 Core 模块的两大核心文件（config.py 的 pydantic-settings 配置管理模式和 llm_driver.py 的大模型工厂模式）、多厂商映射设计、缓存机制以及测试驱动验证方法。*
