# LangGraph 终极实战——LangChain + LangGraph 构建 AI 辅助投研工具

> 基于教学视频课程整理编写 · 2026年6月

---

> ⚠️ **免责声明**：本文档仅为 LangChain 与 LangGraph 技术教学案例，所有分析结果仅供学习参考，**不构成任何投资建议**。市场有风险，投资需谨慎。

---

## 目录

- [一、项目背景与目标](#一项目背景与目标)
- [二、系统架构全景](#二系统架构全景)
- [三、四大 Agent 专家详解](#三四大-agent-专家详解)
- [四、LangGraph 流程图与状态管理](#四langgraph-流程图与状态管理)
- [五、技术栈与工具链](#五技术栈与工具链)
- [六、环境配置](#六环境配置)
- [七、核心代码详解](#七核心代码详解)
- [八、运行效果演示](#八运行效果演示)
- [九、设计亮点与技术要点](#九设计亮点与技术要点)
- [十、常见问题与排错指南](#十常见问题与排错指南)
- [十一、课后练习](#十一课后练习)
- [十二、项目小结](#十二项目小结)

---

## 一、项目背景与目标

### 1.1 为什么选这个选题

在 LangChain 系列（18 课）和 LangGraph 系列（5 课）之后，我们终于迎来了**终极综合实战**。这个项目历经多次选题打磨，最终选定了一个**大家都会感兴趣的方向**——用 AI 辅助投研分析。

> 这个项目的目标不是让你用 AI 去自动交易，而是展示：**如何用 LangChain + LangGraph 将多个专业 AI Agent 组织成一个协作团队，从不同维度分析复杂问题，最终给出综合决策建议**。

### 1.2 纯大模型的局限

如果直接用大模型去分析某个投资标的，会遇到几个典型问题：

```
直接问大模型"帮我分析 002600 这只股票"：

问题1：数据过时
    ├── 大模型的知识截止日期可能是几个月前
    └── 不知道最新的行情数据 → 分析脱离实际

问题2：幻觉严重
    ├── 可能把股票 A 的数据安到股票 B 上
    └── 代码和数据对不上 → 张冠李戴

问题3：不会看图
    ├── 老手会看 K 线图做技术分析
    └── 纯文本模型看不懂图表中的形态和信号

问题4：线性思维
    ├── 单一推理链路 → 容易遗漏关键因素
    └── 没有多角度交叉验证 → 结论片面

问题5：不懂市场特性
    ├── 不同市场的分析逻辑完全不同
    └── 比如需要关注主力资金流向这个关键指标
```

### 1.3 本项目的解决方案

```
LangGraph 多 Agent 协作投研系统：

  纯大模型（单一视角）          →    多 Agent 协作（多维度 + 交叉验证）

  "我觉得可以买"               →    量化分析师："技术面呈上升趋势"
                                    图表分析师："K线出现金叉信号"
                                    舆情分析师："近期正面消息居多"
                                    CIO："综合置信度 65%，建议持有"
                                         ↓
                                    附带：短线/中线/长线策略 + 风险提示
```

### 1.4 本课要掌握的目标

```
┌───────────────────────────────────────────────────────┐
│                                                       │
│  目标一：掌握 LangChain + LangGraph 综合架构设计         │
│         ├── 如何将复杂业务拆分为多个专业 Agent            │
│         ├── 并行分支 + 汇总的图结构设计                  │
│         └── Structured Output 在 Agent 中的应用         │
│                                                       │
│  目标二：掌握多模态 Agent 的构建方法                     │
│         ├── 用代码生成图表（K线图）                      │
│         ├── 将图表传给 Vision 模型分析                   │
│         └── 图表分析结果与其他 Agent 结果融合             │
│                                                       │
│  目标三：掌握外部数据源的集成                            │
│         ├── 金融数据 API（akshare）集成                 │
│         ├── 联网舆情检索（Tavily Search）               │
│         └── 时序预测工具（Prophet）的桥接               │
│                                                       │
│  目标四：理解生产级 Agent 的输出规范                     │
│         ├── Structured Output 定义结构化报告             │
│         ├── Markdown 格式的专业投研报告                   │
│         └── 置信度 + 多时间维度策略输出                   │
│                                                       │
└───────────────────────────────────────────────────────┘
```

---

## 二、系统架构全景

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI 辅助投研系统 整体架构                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   用户输入（股票代码）                                             │
│        ↓                                                        │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    LangGraph 编排层                       │   │
│   │                                                         │   │
│   │   ┌──────────┐                                          │   │
│   │   │  Fetch   │ ← 数据采集节点                             │   │
│   │   │ 数据获取  │    • akshare API：历史行情 + 资金流向       │   │
│   │   └────┬─────┘    • Tavily Search：舆情搜索               │   │
│   │        │                                                │   │
│   │   ┌────┼──────────────────────────┐                      │   │
│   │   ↓    ↓                          ↓                      │   │
│   │ ┌────┐ ┌──────────┐  ┌──────────────────┐               │   │
│   │ │量化│ │图表分析   │  │   舆情分析          │ ← 三个专家     │   │
│   │ │专家│ │(Vision)  │  │   (News Agent)    │   并行执行     │   │
│   │ └──┬─┘ └────┬─────┘  └────────┬─────────┘               │   │
│   │    │         │                │                          │   │
│   │    └─────────┼────────────────┘                          │   │
│   │              ↓                                           │   │
│   │   ┌──────────────────┐                                   │   │
│   │   │   CIO Agent      │ ← 综合决策                         │   │
│   │   │   首席投资官       │   汇总三份报告                     │   │
│   │   └────────┬─────────┘   给出最终建议                      │   │
│   │            ↓                                             │   │
│   │   结构化输出报告（Markdown）                                 │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   外部依赖：                                                      │
│   ├── akshare（金融数据）     ├── Prophet（时序预测）              │
│   ├── Plotly（K线图生成）     ├── ZhipuAI Vision（图表识别）       │
│   └── Tavily Search（舆情）   └── 硅基流动千问（文本推理）         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流全景

```
输入：股票代码 "002600"
  │
  ├──→ akshare API ──→ 历史行情数据 ──→ 资金流向数据
  │                                       │
  │                          ┌────────────┼────────────┐
  │                          ↓            ↓            ↓
  │                     ┌─────────┐ ┌─────────┐ ┌─────────┐
  │                     │ 量化分析 │ │ K线图    │ │ 舆情搜索 │
  │                     │ Prophet │ │ Plotly  │ │ Tavily  │
  │                     │ 时序预测 │ │ 画图     │ │ 搜索     │
  │                     └────┬────┘ └────┬────┘ └────┬────┘
  │                          ↓            ↓            ↓
  │                     LLM 分析    图片→base64    LLM 分析
  │                     (文本模型)   →智谱Vision   (文本模型)
  │                          ↓            ↓            ↓
  │                     量化报告     图表报告      舆情报告
  │                          │            │            │
  │                          └────────────┼────────────┘
  │                                       ↓
  │                              ┌──────────────┐
  │                              │  CIO Agent   │
  │                              │  综合决策      │
  │                              │  LLM 汇总     │
  │                              └──────┬───────┘
  │                                     ↓
  │                          结构化输出（Markdown）
  │                          ├── 投资建议：buy/sell/hold
  │                          ├── 置信度：65%
  │                          ├── 核心逻辑
  │                          ├── 短线/中线/长线策略
  │                          └── 风险提示
  ↓
输出：专业投研分析报告
```

### 2.3 LangGraph 图结构

```
                     ┌──────────┐
                     │  START   │
                     └────┬─────┘
                          ↓
                   ┌─────────────┐
                   │   fetch     │
                   │  数据采集    │
                   │ akshare +   │
                   │ Tavily      │
                   └──┬──┬──┬───┘
                      ↓  ↓  ↓
          ┌───────────┘  │  └───────────┐
          ↓              ↓              ↓
   ┌─────────────┐ ┌───────────┐ ┌───────────┐
   │ quant_agent │ │vega_agent │ │news_agent │
   │ 量化分析     │ │ 图表识别   │ │ 舆情分析   │
   │ (时序+LLM)  │ │(K线+Vision)│ │(搜索+LLM) │
   └──────┬──────┘ └─────┬─────┘ └─────┬─────┘
          ↓              ↓              ↓
          └──────────────┼──────────────┘
                         ↓
                  ┌─────────────┐
                  │ cio_agent   │
                  │ 综合分析     │
                  │ 生成报告     │
                  └──────┬──────┘
                         ↓
                  ┌─────────────┐
                  │ 结构化输出   │
                  │ Markdown报告 │
                  └──────┬──────┘
                         ↓
                       END
```

---

## 三、四大 Agent 专家详解

### 3.1 专家总览

```
┌──────────────────────────────────────────────────────────────┐
│                     四大 Agent 专家                            │
├──────────────┬────────────────┬──────────┬──────────────────┤
│   专家名称    │    分析维度      │  输入     │    核心技术       │
├──────────────┼────────────────┼──────────┼──────────────────┤
│ Quant Agent  │ 技术面量化分析   │ 历史行情  │ Prophet 时序预测   │
│ 量化分析师    │                │ 资金流向  │ + LLM 文本推理    │
├──────────────┼────────────────┼──────────┼──────────────────┤
│ Vega Agent   │ K线图视觉分析   │ K线图    │ Plotly 画图       │
│ 图表分析师    │                │ (PNG)    │ + ZhipuAI Vision │
├──────────────┼────────────────┼──────────┼──────────────────┤
│ News Agent   │ 舆情情感分析     │ 搜索关键词│ Tavily Search    │
│ 舆情分析师    │                │          │ + LLM 文本推理    │
├──────────────┼────────────────┼──────────┼──────────────────┤
│ CIO Agent    │ 综合决策         │ 三份报告  │ LLM 综合推理      │
│ 首席投资官    │                │          │ + Structured     │
│              │                │          │   Output         │
└──────────────┴────────────────┴──────────┴──────────────────┘
```

### 3.2 Agent 一：Quant Agent（量化分析师）

> **纯技术面分析专家**，负责从数据维度判断走势。

```
┌─────────────────────────────────────────────────────────────┐
│  Quant Agent 工作流                                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  输入：历史行情数据（近2年）+ 资金流向数据                      │
│                                                             │
│  Step 1: 时序预测（Prophet）                                  │
│      ├── 输入：日期 + 收盘价时间序列                           │
│      ├── 模型：Facebook Prophet                              │
│      └── 输出：未来趋势预测 + 置信区间                         │
│                                                             │
│  Step 2: 资金流向分析                                         │
│      ├── 主力资金净流入/流出                                   │
│      ├── 超大单/大单/中单/小单分布                              │
│      └── 输出：资金面判断（吸筹/出货/观望）                     │
│                                                             │
│  Step 3: LLM 综合推理                                        │
│      ├── 输入：时序预测结果 + 资金流向数据                      │
│      ├── + 技术指标（均线/成交量/换手率…）                      │
│      ├── Structured Output（结构化输出）                      │
│      └── 输出：量化分析报告（趋势判断 + 支撑位/压力位）          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 量化分析报告结构化输出示例

```python
# ── Quant Agent 的结构化输出 Schema ──
from pydantic import BaseModel, Field

class QuantReport(BaseModel):
    """量化分析报告的结构化输出"""
    trend: str = Field(
        description="趋势判断：bullish(看涨) / bearish(看跌) / sideways(横盘)"
    )
    confidence: float = Field(
        description="置信度 0-1，例如 0.65 表示 65%"
    )
    key_findings: list[str] = Field(
        description="关键发现列表，每项不超过50字"
    )
    technical_signals: str = Field(
        description="技术指标信号总结，如 MACD金叉、均线多头排列等"
    )
    capital_flow_analysis: str = Field(
        description="资金流向分析：主力资金动向及解读"
    )
    support_level: str = Field(
        description="支撑位分析"
    )
    resistance_level: str = Field(
        description="压力位分析"
    )
```

### 3.3 Agent 二：Vega Agent（图表分析师）

> **多模态分析专家**，负责从 K 线图视觉维度判断走势。这是本项目最有特色的 Agent。

```
┌─────────────────────────────────────────────────────────────┐
│  Vega Agent 工作流                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  输入：历史行情数据                                            │
│                                                             │
│  Step 1: 生成 K 线图（Plotly）                                │
│      ├── 数据：OHLC（开盘/最高/最低/收盘）                      │
│      ├── 指标叠加：MA5/MA10/MA20（移动均线）                    │
│      ├── 成交量柱状图（副图）                                  │
│      └── 输出：PNG 图片文件 → 保存到 temp_charts/ 目录          │
│                                                             │
│  Step 2: 图片转 base64                                       │
│      └── 读取 PNG → 编码为 base64 字符串                       │
│                                                             │
│  Step 3: 调用 Vision 模型（ZhipuAI GLM-4V）                   │
│      ├── 将 base64 图片传给多模态模型                          │
│      ├── 提示词：分析 K 线形态、均线位置、成交量变化            │
│      └── 输出：图表技术分析（MACD 金叉/死叉、形态识别……）        │
│                                                             │
│  Step 4: 结构化输出                                           │
│      └── 输出：Vega 分析报告                                  │
│                                                             │
│  核心价值：AI 像老手一样"看图"，识别肉眼可辨的形态和信号         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Vega Agent 核心代码示意

```python
# ── 生成 K 线图 ──
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64

def generate_kline_chart(df, symbol, save_path):
    """
    生成带均线和成交量的 K 线图。

    Args:
        df: DataFrame，包含 Date/Open/High/Low/Close/Volume 列
        symbol: 股票代码
        save_path: 图片保存路径
    """
    # 计算均线
    df['MA5'] = df['Close'].rolling(5).mean()
    df['MA10'] = df['Close'].rolling(10).mean()
    df['MA20'] = df['Close'].rolling(20).mean()

    # 创建双子图：K线（上）+ 成交量（下）
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
    )

    # K 线图
    fig.add_trace(
        go.Candlestick(
            x=df['Date'],
            open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'],
            name='K线'
        ),
        row=1, col=1
    )

    # 均线叠加
    for ma, color in [('MA5', 'blue'), ('MA10', 'orange'), ('MA20', 'purple')]:
        fig.add_trace(
            go.Scatter(x=df['Date'], y=df[ma], name=ma,
                       line=dict(color=color, width=1)),
            row=1, col=1
        )

    # 成交量柱状图（红涨绿跌）
    colors = ['red' if close >= open else 'green'
              for close, open in zip(df['Close'], df['Open'])]
    fig.add_trace(
        go.Bar(x=df['Date'], y=df['Volume'], name='成交量',
               marker_color=colors),
        row=2, col=1
    )

    fig.update_layout(
        title=f'{symbol} K线图',
        xaxis_rangeslider_visible=False,
        height=800,
    )

    fig.write_image(save_path)
    return save_path

# ── 调用 Vision 模型分析图表 ──
def analyze_chart_with_vision(image_path: str, model_client) -> str:
    """
    用 Vision 模型分析 K 线图。

    Args:
        image_path: K 线图 PNG 文件路径
        model_client: ZhipuAI 客户端

    Returns:
        Vision 模型的分析结果
    """
    # 读取图片 → base64
    with open(image_path, 'rb') as f:
        image_base64 = base64.b64encode(f.read()).decode('utf-8')

    # Vision 模型分析提示词
    chart_prompt = """请分析这张股票K线图，从以下角度给出你的判断：

1. **K线形态**：最近出现什么经典形态？（如锤子线、吞没形态、十字星等）
2. **均线关系**：MA5/MA10/MA20 的排列方式？（多头排列/空头排列/缠绕）
3. **成交量变化**：最近成交量是放大还是缩小？这意味什么？
4. **MACD 信号**：是否能观察到金叉或死叉信号？
5. **支撑与压力**：图中能看到哪些关键的支撑位和压力位？
6. **综合判断**：基于以上分析，短期走势偏多还是偏空？

请给出结构化的分析结论。"""

    response = model_client.chat.completions.create(
        model="glm-4v",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
                {"type": "text", "text": chart_prompt},
            ]
        }]
    )

    return response.choices[0].message.content
```

### 3.4 Agent 三：News Agent（舆情分析师）

> **舆情情感分析专家**，负责从互联网信息维度判断市场情绪。

```
┌─────────────────────────────────────────────────────────────┐
│  News Agent 工作流                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  输入：股票代码 + 公司名称                                      │
│                                                             │
│  Step 1: 联网检索（Tavily Search）                            │
│      ├── 搜索关键词："{股票名称} 最新消息"                      │
│      ├── 搜索关键词："{股票名称} 利好 利空"                     │
│      └── 返回：相关新闻标题和摘要                              │
│                                                             │
│  Step 2: LLM 舆情分析                                         │
│      ├── 输入：搜索到的所有新闻摘要                             │
│      ├── 分析维度：                                            │
│      │   ├── 正面消息占比                                     │
│      │   ├── 负面消息占比                                     │
│      │   ├── 市场关注度（新闻数量）                             │
│      │   └── 关键事件（财报/政策/行业变动）                      │
│      └── 输出：舆情分析报告                                    │
│                                                             │
│  Step 3: 结构化输出                                           │
│      └── 输出：News 分析报告                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.5 Agent 四：CIO Agent（首席投资官）

> **综合决策专家**，负责汇总三个专家的报告，给出最终投资建议。

```
┌─────────────────────────────────────────────────────────────┐
│  CIO Agent 工作流                                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  输入：三份专家报告（量化 + 图表 + 舆情）                        │
│                                                             │
│  处理流程：                                                   │
│  Step 1: 阅读理解三份报告                                     │
│      ├── 提取每份报告的核心结论                                 │
│      ├── 交叉验证：三份报告结论是否一致？                        │
│      └── 识别矛盾点：不一致的地方需要重点分析                    │
│                                                             │
│  Step 2: 权重综合                                            │
│      ├── 量化分析权重：30%                                    │
│      ├── 图表分析权重：20%                                    │
│      ├── 舆情分析权重：20%                                    │
│      └── 资金流向权重：30%（在本市场环境下最重要）              │
│                                                             │
│  Step 3: 结构化输出（Markdown 报告）                           │
│      ├── 最终建议：buy / sell / hold                          │
│      ├── 置信度：0-100%                                      │
│      ├── 核心逻辑：为什么给出这个建议                           │
│      ├── 短线策略（1-5天）                                    │
│      ├── 中线策略（1-4周）                                    │
│      ├── 长线策略（1-3月）                                    │
│      └── 风险提示                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### CIO 结构化输出示例

```markdown
# 📊 002600 投资分析报告

## 🎯 最终建议
**HOLD（持有观望）** —— 置信度 65%

## 📈 核心逻辑

当前标的主要处于**洗盘吸筹阶段**，主力资金呈现明显的"边拉边洗"特征：

1. **主力资金动向**（权重 30%）：近5日主力净流入约1.2亿，
   超大单买入占比持续上升 → 偏多信号
2. **技术面**（权重 30%）：MACD 在零轴附近金叉，
   均线呈多头排列，短期偏多
3. **图表形态**（权重 20%）：K线在MA20上方整理，
   成交量温和放大，属健康走势
4. **舆情面**（权重 20%）：近期消息面偏正面，
   行业政策利好频出

## 📋 实战策略

| 周期 | 策略 | 操作建议 |
|------|------|----------|
| 短线（1-5天） | 逢低吸纳 | 回调至 MA10 附近可轻仓试多 |
| 中线（1-4周） | 持有待涨 | 若放量突破前高可加仓 |
| 长线（1-3月） | 逢高减仓 | 到达目标位后分批止盈 |

## ⚠️ 风险提示

- 市场整体波动风险
- 行业政策变化风险
- 主力资金突然撤离风险
- 本报告仅为 AI 辅助分析，不构成投资建议
```

---

## 四、LangGraph 流程图与状态管理

### 4.1 State 完整定义

```python
# ── src/agent/state.py ──
"""
投研系统的 State 定义。
由于涉及多个 Agent 的数据交换，State 字段较多。
每个字段有明确的职责和归属。
"""
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class InvestmentResearchState(TypedDict):
    # ── 输入层 ──
    symbol: str                     # 股票代码（如 "002600"）

    # ── 数据采集层（fetch 节点填充）──
    stock_data: str                 # akshare 获取的原始行情数据（JSON 字符串）
    chart_paths: str                # K线图保存路径（temp_charts/ 目录）
    news_data: str                  # Tavily 搜索的舆情数据
    capital_flow_data: str          # 主力资金流向数据
    profile: str                    # 标的基本信息（名称/板块/是否龙头…）

    # ── 时序预测层 ──
    prophet_result: str             # Prophet 时序预测结果

    # ── Agent 报告层（三个分支填充）──
    quant_report: str               # 量化分析师报告
    vega_report: str                # 图表分析师报告（Vision）
    news_report: str                # 舆情分析师报告

    # ── 综合决策层 ──
    final_report: str               # CIO 综合报告（Markdown）
    recommendation: str             # 最终建议：buy / sell / hold
    confidence: float               # 置信度 0-1
```

### 4.2 图定义（链式 API）

```python
# ── src/agent/graph.py ──
"""
投研系统 Graph 定义。
LangGraph 1.2 链式 API 写法。
"""
from langgraph.graph import StateGraph, END, START
from .state import InvestmentResearchState
from .nodes import (
    fetch_data,
    quant_analysis,
    vega_analysis,
    news_analysis,
    cio_decision,
)

# ── 创建 StateGraph ──
workflow = StateGraph(InvestmentResearchState)

# ── 添加节点 ──
workflow.add_node("fetch", fetch_data)         # 数据采集
workflow.add_node("quant", quant_analysis)      # 量化分析
workflow.add_node("vega", vega_analysis)        # 图表分析
workflow.add_node("news", news_analysis)        # 舆情分析
workflow.add_node("cio", cio_decision)          # 综合决策

# ── 边定义 ──
# 入口 → 数据采集
workflow.add_edge(START, "fetch")

# 数据采集 → 三个专家（并行分支）
# 从 fetch 同时发往三个 Agent
workflow.add_edge("fetch", "quant")
workflow.add_edge("fetch", "vega")
workflow.add_edge("fetch", "news")

# 三个专家 → CIO 汇总
workflow.add_edge("quant", "cio")
workflow.add_edge("vega", "cio")
workflow.add_edge("news", "cio")

# CIO → 结束
workflow.add_edge("cio", END)

# ── 编译 ──
app = workflow.compile()
```

### 4.3 节点职责矩阵

| 节点 | 调用模型 | 外部依赖 | 输出字段 |
|------|:------:|------|------|
| **fetch** | 无 | akshare, Tavily | `stock_data`, `chart_paths`, `news_data`, `capital_flow_data`, `profile` |
| **quant** | 千问（文本） | Prophet | `quant_report`, `prophet_result` |
| **vega** | 智谱 GLM-4V（视觉） | Plotly | `chart_paths`, `vega_report` |
| **news** | 千问（文本） | Tavily（由 fetch 预取） | `news_report` |
| **cio** | 千问（文本） | 无（纯推理） | `final_report`, `recommendation`, `confidence` |

---

## 五、技术栈与工具链

### 5.1 完整技术栈

```
┌─────────────────────────────────────────────────────────────┐
│                     技术栈全景                                │
├─────────────────┬───────────────────────────────────────────┤
│     层级         │               技术选型                     │
├─────────────────┼───────────────────────────────────────────┤
│ 编排框架         │ LangGraph 1.2（最新版）                     │
│ 模型调用         │ LangChain 1.2.0                            │
│ 文本模型         │ 硅基流动 Qwen 2.5 3B/7B Instruct（免费）    │
│ 视觉模型         │ 智谱AI GLM-4V（免费，图表识别）              │
│ 结构化输出       │ LangChain StructuredOutput + Pydantic      │
├─────────────────┼───────────────────────────────────────────┤
│ 金融数据         │ akshare（A股开源数据接口）                   │
│ 时序预测         │ Prophet（Facebook 时序预测）                │
│ K线图生成       │ Plotly（交互式图表）                        │
│ 联网搜索         │ Tavily Search（免费额度/天）                │
├─────────────────┼───────────────────────────────────────────┤
│ 依赖管理         │ UV（Python 包管理器）                       │
│ 运行入口         │ main.py（命令行交互）                       │
└─────────────────┴───────────────────────────────────────────┘
```

### 5.2 各工具的角色

| 工具 | 用途 | 为什么选它 |
|------|------|-----------|
| **akshare** | 获取 A 股历史行情、资金流向、基本信息 | 免费、数据全、纯 Python |
| **Prophet** | 收盘价时序趋势预测 | 开源、易用、自动处理季节性和趋势 |
| **Plotly** | 生成专业 K 线图（含均线+成交量） | Python 原生、图片输出质量高 |
| **Tavily Search** | 搜索互联网上的舆情和新闻 | 专为 AI Agent 设计、免费额度 |
| **ZhipuAI GLM-4V** | 多模态识别 K 线图形态 | 免费、中文理解好、图片分析能力强 |
| **Qwen 2.5** | 文本推理（量化分析、舆情分析、CIO 汇总） | 免费、中文能力强、支持工具调用 |

---

## 六、环境配置

### 6.1 .env 文件

```bash
# ═══════════════════════════════════════════
#  AI 辅助投研系统 - 环境变量配置
# ═══════════════════════════════════════════

# ── 硅基流动（文本模型）──
SILICONFLOW_API_KEY=sk-your-key-here
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
# 可选模型：Qwen/Qwen2.5-3B-Instruct、Qwen/Qwen2.5-7B-Instruct

# ── 智谱AI（视觉模型 - 图表识别）──
ZHIPUAI_API_KEY=your-zhipuai-api-key-here
# 免费模型：glm-4v

# ── Tavily Search（联网舆情搜索）──
TAVILY_API_KEY=tvly-your-key-here
# 免费额度：每天固定次数

# ── LangSmith（可选 - 追踪调试）──
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=lsv2_pt_your_key_here
LANGSMITH_PROJECT=investment-research
```

### 6.2 依赖安装

```bash
# ── pyproject.toml 核心依赖 ──
# 使用 UV 管理

# 安装所有依赖
uv sync

# 或手动安装核心依赖
uv add langchain langchain-openai langgraph
uv add akshare prophet plotly
uv add tavily-python zhipuai
uv add kaleido  # Plotly 导出静态图片需要
```

---

## 七、核心代码详解

### 7.1 fetch 节点——数据采集

```python
# ── nodes.py: fetch_data ──
import akshare as ak
from tavily import TavilyClient
import json

def fetch_data(state: InvestmentResearchState) -> InvestmentResearchState:
    """
    数据采集节点：获取行情数据 + 资金流向 + 基本信息 + 舆情搜索。

    这个节点是纯数据操作，不涉及 LLM 调用。
    所有数据准备好后，分发给三个 Agent 做推理。
    """
    symbol = state["symbol"]
    print(f"📡 正在采集 {symbol} 的数据...")

    # ── 1. 获取历史行情（近2年日线）──
    df = ak.stock_zh_a_hist(
        symbol=symbol,
        period="daily",
        start_date="20240601",
        end_date="20260624",
        adjust="qfq"  # 前复权
    )
    stock_data_json = df.to_json(orient="records", force_ascii=False)
    print(f"   ✅ 历史行情：{len(df)} 条日线数据")

    # ── 2. 获取资金流向 ──
    try:
        flow_df = ak.stock_individual_fund_flow(
            stock=symbol,
            market="sz" if symbol.startswith("0") else "sh"
        )
        capital_flow = flow_df.to_json(orient="records", force_ascii=False)
        print(f"   ✅ 资金流向数据已获取")
    except Exception:
        capital_flow = "{}"
        print(f"   ⚠️  资金流向数据获取失败")

    # ── 3. 获取基本信息 ──
    try:
        info = ak.stock_individual_info_em(symbol=symbol)
        profile = info.to_json(orient="records", force_ascii=False)
    except Exception:
        profile = "{}"

    # ── 4. 舆情搜索（Tavily）──
    # 从基本信息中提取公司名称用于搜索
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    search_results = tavily.search(
        query=f"{symbol} 最新消息 利好 利空",
        search_depth="basic",
        max_results=5
    )
    news_data = json.dumps(search_results, ensure_ascii=False)
    print(f"   ✅ 舆情搜索完成：{len(search_results.get('results', []))} 条")

    print(f"📡 数据采集完成！\n")

    return {
        "stock_data": stock_data_json,
        "capital_flow_data": capital_flow,
        "profile": profile,
        "news_data": news_data,
    }
```

### 7.2 quant 节点——量化分析

```python
# ── nodes.py: quant_analysis ──
from prophet import Prophet
import pandas as pd
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .models import QuantReport  # Pydantic 结构化输出模型

def quant_analysis(state: InvestmentResearchState) -> InvestmentResearchState:
    """
    量化分析节点：
    1. 用 Prophet 做时序预测
    2. 分析资金流向
    3. 用 LLM 综合推理 → 结构化输出
    """
    print("📊 [Quant Agent] 开始量化分析...")

    # ── Step 1: Prophet 时序预测 ──
    df = pd.read_json(state["stock_data"])
    # Prophet 需要 ds(日期) 和 y(值) 两列
    prophet_df = pd.DataFrame({
        "ds": pd.to_datetime(df["日期"]),
        "y": df["收盘"].astype(float),
    })

    model = Prophet(
        daily_seasonality=True,
        yearly_seasonality=True,
    )
    model.fit(prophet_df)

    # 预测未来 30 天
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    # 提取预测趋势
    trend_direction = "上升" if forecast["trend"].iloc[-1] > forecast["trend"].iloc[-31] else "下降"
    prophet_summary = (
        f"Prophet 时序预测：未来30日趋势→{trend_direction}，"
        f"预测区间：{forecast['yhat_lower'].iloc[-1]:.2f} ~ "
        f"{forecast['yhat_upper'].iloc[-1]:.2f}"
    )

    # ── Step 2: LLM 综合推理（结构��输出）──
    llm = ChatOpenAI(
        model="Qwen/Qwen2.5-7B-Instruct",
        base_url=os.getenv("SILICONFLOW_BASE_URL"),
        api_key=os.getenv("SILICONFLOW_API_KEY"),
    )

    # 使用结构化输出
    structured_llm = llm.with_structured_output(QuantReport)

    prompt = f"""你是一个专业的量化分析师。请根据以下数据进行技术分析：

## Prophet 时序预测
{prophet_summary}

## 资金流向数据
{state['capital_flow_data'][:2000]}

## 历史行情（最近30条）
{state['stock_data'][:3000]}

请从趋势、技术指标、资金面三个维度进行分析。"""

    report: QuantReport = structured_llm.invoke(prompt)
    print(f"   ✅ 量化分析完成：趋势={report.trend}，置信度={report.confidence}")

    return {
        "prophet_result": prophet_summary,
        "quant_report": json.dumps(report.model_dump(), ensure_ascii=False),
    }
```

### 7.3 vega 节点——图表分析（多模态）

```python
# ── nodes.py: vega_analysis ──
import base64
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from zhipuai import ZhipuAI
import pandas as pd

def vega_analysis(state: InvestmentResearchState) -> InvestmentResearchState:
    """
    图表分析节点：
    1. 用 Plotly 生成 K 线图（含均线+成交量）
    2. 保存为 PNG
    3. 传给智谱 GLM-4V 做视觉分析
    4. 结构化输出图表分析报告
    """
    print("📈 [Vega Agent] 开始图表分析...")

    symbol = state["symbol"]

    # ── Step 1: 解析数据并生成 K 线图 ──
    df = pd.read_json(state["stock_data"])
    df["日期"] = pd.to_datetime(df["日期"])

    # 计算均线
    df['MA5'] = df['收盘'].rolling(5).mean()
    df['MA10'] = df['收盘'].rolling(10).mean()
    df['MA20'] = df['收盘'].rolling(20).mean()

    # 创建 K 线图
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
    )

    # 上��：K线 + 均线
    fig.add_trace(
        go.Candlestick(
            x=df["日期"],
            open=df["开盘"], high=df["最高"],
            low=df["最低"], close=df["收盘"],
            name="K线",
            increasing_line_color='red',
            decreasing_line_color='green',
        ),
        row=1, col=1
    )
    for ma, color in [('MA5', 'blue'), ('MA10', 'orange'), ('MA20', 'purple')]:
        fig.add_trace(
            go.Scatter(x=df["日期"], y=df[ma], name=ma,
                       line=dict(color=color, width=1.5)),
            row=1, col=1
        )

    # 下图：成交量
    colors = ['red' if c >= o else 'green'
              for c, o in zip(df['收盘'], df['开盘'])]
    fig.add_trace(
        go.Bar(x=df["日期"], y=df['成交量'], name='成交量',
               marker_color=colors, opacity=0.5),
        row=2, col=1
    )

    fig.update_layout(
        title=f'{symbol} K线图（近3个月）',
        xaxis_rangeslider_visible=False,
        height=800,
        template='plotly_white',
    )

    # 保存图片
    import os
    os.makedirs("temp_charts", exist_ok=True)
    chart_path = f"temp_charts/{symbol}_kline.png"
    fig.write_image(chart_path)
    print(f"   📸 K线图已保存：{chart_path}")

    # ── Step 2: 读取图片 → base64 → Vision 模型 ──
    with open(chart_path, 'rb') as f:
        image_base64 = base64.b64encode(f.read()).decode('utf-8')

    zhipu_client = ZhipuAI(api_key=os.getenv("ZHIPUAI_API_KEY"))

    chart_prompt = """请分析这张股票K线图（含MA5/MA10/MA20均线和成交量），回答以下问题：

1. K线形态：最近一周出现什么重要形态？（如十字星、吞没、锤子线等）
2. 均线关系：MA5/MA10/MA20 的排列方式？是多头还是空头排列？
3. 成交量：最近成交量变化趋势？放量还是缩量？
4. 技术信号：是否能看到明显的金叉或死叉信号？
5. 支撑压力：关键的支撑位和压力位在哪里？
6. 综合判断：短期（1-2周）走势偏多还是偏空？

请给出结构化的分析结论。"""

    response = zhipu_client.chat.completions.create(
        model="glm-4v",
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_base64}"}
                },
                {"type": "text", "text": chart_prompt},
            ]
        }],
        temperature=0.3,
    )

    vega_result = response.choices[0].message.content
    print(f"   ✅ 图表分析完成")

    return {
        "chart_paths": chart_path,
        "vega_report": vega_result,
    }
```

### 7.4 news 节点——舆情分析

```python
# ── nodes.py: news_analysis ──
from langchain_openai import ChatOpenAI
from .models import NewsReport  # Pydantic 结构化输出

def news_analysis(state: InvestmentResearchState) -> InvestmentResearchState:
    """
    舆情分析节点：
    基于 fetch 节点预取的新闻数据，用 LLM 做情感分析和影响评估。
    """
    print("📰 [News Agent] 开始舆情分析...")

    llm = ChatOpenAI(
        model="Qwen/Qwen2.5-7B-Instruct",
        base_url=os.getenv("SILICONFLOW_BASE_URL"),
        api_key=os.getenv("SILICONFLOW_API_KEY"),
    )
    structured_llm = llm.with_structured_output(NewsReport)

    prompt = f"""你是一个金融舆情分析师。请分析以下关于股票的新闻和消息。

## 搜索到的新闻数据
{state['news_data'][:3000]}

## 标的基本信息
{state['profile']}

请从以下角度分析：
1. 正面消息和负面消息各占比多少？
2. 是否有重大利好或利空事件？
3. 市场整体情绪如何？
4. 这些消息对短期股价的可能影响？"""

    report: NewsReport = structured_llm.invoke(prompt)
    print(f"   ✅ 舆情分析完成：正面占比={report.positive_ratio}")

    return {
        "news_report": json.dumps(report.model_dump(), ensure_ascii=False),
    }
```

### 7.5 cio 节点——综合决策

```python
# ── nodes.py: cio_decision ──
from langchain_openai import ChatOpenAI
from .models import CIOReport  # Pydantic 结构化输出

def cio_decision(state: InvestmentResearchState) -> InvestmentResearchState:
    """
    CIO 综合决策节点：
    汇总三份专家报告，给出最终投资建议。
    """
    print("🎯 [CIO Agent] 开始综合决策...")

    llm = ChatOpenAI(
        model="Qwen/Qwen2.5-7B-Instruct",
        base_url=os.getenv("SILICONFLOW_BASE_URL"),
        api_key=os.getenv("SILICONFLOW_API_KEY"),
    )
    structured_llm = llm.with_structured_output(CIOReport)

    prompt = f"""你是一个经验丰富的首席投资官（CIO）。你需要综合分析以下三份专家报告，
给出最终的投资建议。

## 量化分析报告
{state['quant_report']}

## 技术图表分析报告（基于K线图的视觉识别）
{state['vega_report']}

## 舆情分析报告
{state['news_report']}

## 分析要求

请综合考虑，注意以下权重：
- 资金流向分析：30%（最关键）
- 技术面分析：30%
- 图表形态分析：20%
- 舆情分析：20%

## 输出要求

1. **投资建议**：必须是 buy（买入）、sell（卖出）或 hold（持有观望）之一
2. **置信度**：0-100% 的数字
3. **核心逻辑**：为什么给出这个建议（3-5点）
4. **短线策略**（1-5天）
5. **中线策略**（1-4周）
6. **长线策略**（1-3月）
7. **风险提示**（至少3条）

用 Markdown 格式输出完整报告。"""

    report: CIOReport = structured_llm.invoke(prompt)
    print(f"   ✅ 综合决策完成：建议={report.recommendation}，置信度={report.confidence}%")

    return {
        "final_report": report.model_dump().get("markdown_report", ""),
        "recommendation": report.recommendation,
        "confidence": report.confidence / 100.0,
    }
```

### 7.6 结构化输出模型定义（models.py）

```python
# ── src/agent/models.py ──
"""所有 Agent 的结构化输出 Pydantic 模型"""
from pydantic import BaseModel, Field
from typing import Optional

# ── Quant Agent 输出 ──
class QuantReport(BaseModel):
    trend: str = Field(description="bullish / bearish / sideways")
    confidence: float = Field(description="置信度 0-1")
    key_findings: list[str] = Field(description="关键发现")
    technical_signals: str = Field(description="技术指标信号")
    capital_flow_analysis: str = Field(description="资金流向分析")
    support_level: str = Field(description="支撑位")
    resistance_level: str = Field(description="压力位")

# ── News Agent 输出 ──
class NewsReport(BaseModel):
    positive_ratio: float = Field(description="正面消息占比 0-1")
    negative_ratio: float = Field(description="负面消息占比 0-1")
    sentiment: str = Field(description="整体情绪：positive / neutral / negative")
    key_events: list[str] = Field(description="关键事件列表")
    market_attention: str = Field(description="市场关注度：high / medium / low")
    impact_assessment: str = Field(description="对股价的可能影响")

# ── CIO Agent 输出 ──
class CIOReport(BaseModel):
    recommendation: str = Field(description="buy / sell / hold")
    confidence: float = Field(description="置信度百分比 0-100")
    core_logic: list[str] = Field(description="核心逻辑，3-5条")
    short_term_strategy: str = Field(description="短线策略 1-5天")
    medium_term_strategy: str = Field(description="中线策略 1-4周")
    long_term_strategy: str = Field(description="长线策略 1-3月")
    risk_warnings: list[str] = Field(description="风险提示，至少3条")
    markdown_report: str = Field(description="完整的 Markdown 格式报告")
```

### 7.7 命令行入口（main.py）

```python
# ── main.py ──
"""
AI 辅助投研系统 - 命令行入口。
输入股票代码，获取完整分析报告。
"""
import sys
import os
from dotenv import load_dotenv
from src.agent.graph import app

# 加载环境变量
load_dotenv()

def main():
    print("=" * 60)
    print("  📊 AI 辅助投研分析系统")
    print("  Powered by LangChain + LangGraph")
    print("=" * 60)
    print()
    print("  ⚠️  免责声明：分析结果仅供参考，不构成投资建议")
    print()

    # 输入股票代码
    symbol = input("🔍 请输入股票代码（如 002600）：").strip()

    if not symbol:
        print("❌ 请输入有效的股票代码")
        sys.exit(1)

    print(f"\n⏳ 正在分析 {symbol}，请稍候...\n")

    # 调用 LangGraph
    result = app.invoke({
        "symbol": symbol,
        "stock_data": "",
        "chart_paths": "",
        "news_data": "",
        "capital_flow_data": "",
        "profile": "",
        "prophet_result": "",
        "quant_report": "",
        "vega_report": "",
        "news_report": "",
        "final_report": "",
        "recommendation": "",
        "confidence": 0.0,
    })

    # 输出结果
    print("\n" + "=" * 60)
    print(f"  📊 {symbol} 投资分析报告")
    print("=" * 60)

    print(f"\n🎯 最终建议：{result['recommendation'].upper()}")
    print(f"📈 置信度：{result['confidence']*100:.0f}%")
    print()

    if result.get("final_report"):
        print(result["final_report"])
    else:
        print("❌ 未能生成完整报告，请检查网络连接和 API Key 配置")

    print("\n" + "=" * 60)
    print("  ⚠️  以上分析由 AI 生成，仅供参考，不构成投资建议")
    print("  ⚠️  市场有风险，投资需谨慎")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

---

## 八、运行效果演示

### 8.1 运行命令

```bash
# ── 使用 UV 运行 ──
uv run python main.py
```

### 8.2 执行过程

```
══════════════════════════════════════
  📊 AI 辅助投研分析系统
  Powered by LangChain + LangGraph
══════════════════════════════════════

🔍 请输入股票代码（如 002600）：002080

⏳ 正在分析 002080，请稍候...

📡 正在采集 002080 的数据...
   ✅ 历史行情：487 条日线数据
   ✅ 资金流向数据已获取
   ✅ 舆情搜索完成：5 条

📊 [Quant Agent] 开始量化分析...
   ✅ 量化分析完成：趋势=sideways，置信度=0.72

📈 [Vega Agent] 开始图表分析...
   📸 K线图已保存：temp_charts/002080_kline.png
   ✅ 图表分析完成

📰 [News Agent] 开始舆情分析...
   ✅ 舆情分析完成：正面占比=0.45

🎯 [CIO Agent] 开始综合决策...
   ✅ 综合决策完成：建议=hold，置信度=65%

══════════════════════════════════════
  📊 002080 投资分析报告
══════════════════════════════════════

🎯 最终建议：HOLD
📈 置信度：65%

# 📊 002080 投资分析报告

## 🎯 最终建议
**HOLD（持有观望）** —— 置信度 65%

## 📈 核心逻辑

1. **主力资金动向**：近5日主力净流入约8,500万，
   超大单买入占比持续上升，显示主力吸筹迹象
2. **技术面**：MACD 在零轴附近有金叉趋势，
   MA5 上穿 MA10，短期偏多
3. **图表形态**：K线在 MA20 上方整理，
   成交量温和放大，属健康整理形态
4. **舆情面**：近期消息面中性偏正面，
   行业景气度回升

## 📋 实战策略

| 周期 | 策略 | 操作建议 |
|------|------|----------|
| 短线 | 逢低吸纳 | 回调至 MA10(约¥12.80) 附近可轻仓 |
| 中线 | 持有待涨 | 若放量突破 ¥14.50 可适度加仓 |
| 长线 | 分批止盈 | 目标位 ¥16.00-17.50 区间分批减仓 |

## ⚠️ 风险提示
- 市场系统性风险：大盘波动可能拖累个股
- 主力资金撤离风险：若主力突然转向出货
- 行业政策风险：相关政策变动可能影响基本面
- **本报告仅供学习参考，不构成投资建议**

══════════════════════════════════════
  ⚠️  以上分析由 AI 生成，仅供参考
  ⚠️  市场有风险，投资需谨慎
══════════════════════════════════════
```

### 8.3 不同标的的对比分析

```
示例1：002600 → HOLD（持有），置信度 65%
   原因：洗盘吸筹阶段，主力资金持续流入
   策略：逢低吸纳，等待突破

示例2：002080 → HOLD（持有），置信度 60%
   原因：横盘整理，均线缠绕，方向待确认
   策略：观望为主，等待方向选择

示例3：（强势标的）→ BUY，置信度 75%
   原因：多头排列 + 放量突破 + 利好消息
   策略：积极做多，设好止损
```

---

## 九、设计亮点与技术要点

### 9.1 架构设计亮点

```
┌─────────────────────────────────────────────────────────────┐
│                    项目设计亮点                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1️⃣  数据采集与分析分离                                       │
│      fetch 节点统一采集数据 → 三个 Agent 只做推理不拿数据        │
│      好处：避免每个 Agent 重复调 API，节省时间和额度             │
│                                                             │
│  2️⃣  并行三专家 + 汇总                                        │
│      三个 Agent 同时分析 → CIO 统一决策                        │
│      好处：多维度交叉验证，比单一视角更可靠                     │
│                                                             │
│  3️⃣  多模态融合                                              │
│      文本推理（千问） + 视觉识别（智谱GLM-4V）                  │
│      好处：不仅分析数据，还能"看懂"图表                         │
│                                                             │
│  4️⃣  结构化输出全链路                                         │
│      每个 Agent 使用 Pydantic 模型约束输出                     │
│      好处：输出格式稳定，下游 CIO 能可靠地解析                   │
│                                                             │
│  5️⃣  时序预测 + LLM 推理                                      │
│      Prophet 做数据预测 → LLM 做语义解读                        │
│      好处：数据分析与语义理解分工明确                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 9.2 关键设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| **数据采集放一个节点 vs 分散** | 集中到 fetch | 避免重复 API 调用；三个 Agent 只做推理 |
| **Vision 模型选择** | ZhipuAI GLM-4V | 免费、中文好、图片分析效果好 |
| **文本模型选择** | 硅基流动 Qwen 2.5 7B | 免费、推理能力强、支持结构化输出 |
| **时序预测工具** | Prophet | 开源、易用、自动处理趋势和季节性 |
| **结构化输出** | Pydantic + with_structured_output | LangChain 原生支持，格式稳定 |
| **CIO 权重设置** | 资金流向 30% | 适应当前市场环境的分析逻辑 |

### 9.3 可扩展方向

```
未来可以扩展的方向：

1. 更多数据源
   ├── 财报数据（季报/年报）
   ├── 行业对比数据
   └── 宏观经济指标

2. 更多 Agent
   ├── 财务分析 Agent（PE/PB/ROE…）
   ├── 行业分析 Agent（对标竞品）
   └── 宏观经济 Agent（利率/政策…）

3. 更丰富的输出
   ├── 可视化报告（自动生成图表嵌入Markdown）
   ├── 历史回溯验证（回测准确率）
   └── 多标的对比分析

4. 生产化部署
   ├── LangSmith Deploy（API 端点）
   ├── 定时任务（每日自动分析）
   └── Web 前端（输入代码 → 查看报告）
```

---

## 十、常见问题与排错指南

### 10.1 错误速查表

| 错误信息 | 原因 | 解决方法 | 优先级 |
|----------|------|----------|:------:|
| `akshare 数据获取失败` | 网络问题或接口变动 | 检查 akshare 版本；尝试升级 `pip install akshare --upgrade` | 🔴 高 |
| `Prophet 安装失败` | 依赖编译问题（Windows常见） | Windows 用 `conda install prophet`；Mac/Linux 先装 `pystan` | 🔴 高 |
| `Plotly 图片导出失败` | 缺少 kaleido 引擎 | `uv add kaleido` 或 `pip install kaleido` | 🔴 高 |
| `智谱AI 调用报错` | API Key 无效或余额不足 | 检查 `ZHIPUAI_API_KEY`；确认有免费额度 | 🟡 中 |
| `Structured Output 解析失败` | LLM 返回的格式不符合 Pydantic 模型 | 调低 temperature；简化模型字段约束 | 🟡 中 |
| `资金流向数据为空` | 某些股票不支持此接口 | 加 try/except 容错；降级为跳过资金分析 | 🟡 中 |
| `K线图生成后 Vision 模型看不懂` | 图片信息不够或提示词不清晰 | 调整图表时间范围（建议近3个月）；优化提示词 | 🟢 低 |
| `Tavily 搜索额度用完` | 免费额度有限 | 注册多个账号轮换；或改用其他搜索 API | 🟢 低 |

### 10.2 排查流程

```
投研系统问题排查：

Step 1: 检查数据采集
    └── 单独运行 fetch 节点，看 akshare 是否正常返回
        import akshare as ak
        df = ak.stock_zh_a_hist(symbol="002600", period="daily",
                                  start_date="20240601", end_date="20260624")
        print(df.head())  # 应该有数据

Step 2: 检查模型调用
    └── 单独测试三个模型是否能正常调用
        # 文本模型
        llm.invoke("你好")
        # Vision 模型
        zhipu_client.chat.completions.create(...)

Step 3: 检查结构化输出
    └── 先用普通 LLM 调用（不用 structured output）
        确认 prompt 能产生合理的回答后，再加上 structured output

Step 4: 检查 LangGraph 图
    └── 用最简状态 invoke 一次
        观察每个节点的打印输出，确认执行顺序正确

Step 5: 端到端验证
    └── 用一个熟悉的股票代码跑完整流程
        手动检查三份报告的内容是否合理
```

### 10.3 常见陷阱

**陷阱一：Stock 代码格式错误**

```python
# ❌ 错误：代码格式不对导致 akshare 查不到
symbol = "2600"  # 缺少前导零

# ✅ 正确
symbol = "002600"  # 6位标准代码
# 深圳主板：000xxx, 001xxx, 002xxx
# 上海主板：600xxx, 601xxx, 603xxx
# 创业板：300xxx
# 科创板：688xxx
```

**陷阱二：Prophet 数据格式要求**

```python
# ❌ 错误：列名不匹配
prophet_df = pd.DataFrame({
    "date": dates,    # Prophet 要求列名为 "ds"
    "price": prices,  # Prophet 要求列名为 "y"
})

# ✅ 正确
prophet_df = pd.DataFrame({
    "ds": dates,  # 日期列
    "y": values,  # 数值列
})
```

**陷阱三：Vision 模型图片太大**

```python
# ❌ 错误：极高分辨率 K 线图 → base64 编码后超大
# 可能导致 API 请求超时或超过 Token 限制

# ✅ 正确：控制图片尺寸
fig.update_layout(height=800)  # 不要超过 1200
# 或导出时降低 DPI
fig.write_image(path, width=1200, height=800, scale=1)
```

---

## 十一、课后练习

### 练习一：基础数据采集（⭐）

**目标**：独立使用 akshare 获取数据

**要求**：
- 用 akshare 获取任意一只股票近1年的日线数据
- 打印数据的基本信息（行数、列名、日期范围）
- 计算并打印该股票近1年的最高价、最低价、平均收盘价

**验收标准**：
- 能成功获取数据
- 打印的信息准确

### 练习二：结构化输出实战（⭐⭐）

**目标**：为单个 Agent 设计并实现结构化输出

**要求**：
- 选择一个分析维度（技术面/基本面/舆情面）
- 用 Pydantic 定义结构化输出模型（至少5个字段）
- 用 `with_structured_output` 让 LLM 输出结构化结果
- 验证输出格式的稳定性（同一问题测试3次）

**验收标准**：
- 3次测试中至少2次输出格式完全正确
- Pydantic 模型解析不报错

### 练习三：K线图生成与Vision分析（⭐⭐⭐）

**目标**：独立实现图表生成 + Vision 分析流程

**要求**：
- 用 Plotly 生成一只股票的 K 线图（含均线 + 成交量）
- 保存为 PNG 文件
- 用智谱 GLM-4V 分析图片
- 输出结构化分析结果

**验收标准**：
- K 线图清晰可读
- Vision 模型能正确识别图表中的基本形态
- 分析结果至少包含3个技术观察

### 练习四：简化版投研系统（⭐⭐⭐⭐）

**目标**：构建一个简化版的两专家投研系统

**场景**：只有技术分析 + 舆情分析两个专家（不含图表分析），CIO 汇总。

**要求**：
- 使用 LangGraph 图结构（fetch → 并行 → 汇总）
- 两个 Agent 使用结构化输出
- CIO 输出 Markdown 格式报告
- 可以只在本地运行（不需要 LangSmith）

**验收标准**：
- 输入股票代码能正常输出完整报告
- 两个专家的输出互不干扰
- CIO 能正确引用两个专家的结论

### 练习五：扩展自己的专家 Agent（⭐⭐⭐⭐⭐）

**目标**：为投研系统新增一个自定义专家 Agent

**场景**：在当前四专家基础上，增加一个"财务分析 Agent"，分析 PE/PB/ROE 等基本面指标。

**要求**：
- 设计新的 Pydantic 结构化输出模型
- 实现财务数据采集逻辑
- 将新 Agent 加入 LangGraph 图（与其他专家并行）
- CIO 的 prompt 中加入对新专家报告的分析权重
- 端到端测试完整流程

**验收标准**：
- 新 Agent 能独立产出分析报告
- 五专家并行执行不互相阻塞
- CIO 报告中包含财务分析的结论

---

## 十二、项目小结

### 12.1 核心知识图谱

```
┌──────────────────────────────────────────────────────────────┐
│   LangGraph 终极实战——AI 辅助投研工具 核心知识体系               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1️⃣  系统架构设计                                              │
│      ├── fetch 集中采集 → 三个 Agent 并行推理 → CIO 综合决策    │
│      ├── 数据层与推理层分离（fetch 只拿数据，Agent 只做推理）    │
│      └── LangGraph 并行分支 + 汇聚的标准模式                    │
│                                                              │
│  2️⃣  多模态 Agent                                              │
│      ├── Plotly 生成 K 线图 → base64 编码                     │
│      ├── ZhipuAI GLM-4V 视觉模型分析图表                       │
│      └── 图表分析结果与文本分析结果融合                          │
│                                                              │
│  3️⃣  结构化输出全链路                                          │
│      ├── Pydantic 定义每个 Agent 的输出 Schema                 │
│      ├── LangChain with_structured_output 约束 LLM 输出       │
│      └── 确保下游 CIO 能可靠地解析上游报告                      │
│                                                              │
│  4️⃣  多工具集成                                                │
│      ├── akshare：A股行情/资金流向/基本信息                     │
│      ├── Prophet：时间序列趋势预测                              │
│      ├── Tavily Search：互联网舆情搜索                         │
│      ├── Plotly：专业 K 线图生成                               │
│      └── ZhipuAI Vision：图表多模态识别                        │
│                                                              │
│  5️⃣  工程实践                                                  │
│      ├── .env 环境变量管理所有 API Key                          │
│      ├── Pydantic models.py 集中管理输出结构                   │
│      ├── main.py CLI 命令行入口                                │
│      └── 容错设计（try/except 处理外部 API 失败）               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 12.2 一句话总结

> **LangGraph 终极实战展示了 LangChain + LangGraph 构建复杂 AI 系统的完整范式**——将一个大问题拆解为多个专业 Agent（量化/图表/舆情/CIO），通过 LangGraph 的并行分支实现多维度并发分析，通过多模态技术让 AI "看懂"图表，通过结构化输出确保上下游 Agent 的数据契约，最终产出比单一 LLM 更专业、更可靠的综合决策建议。

### 12.3 技能点清单

| 技能点 | 掌握程度 | 体现位置 |
|--------|:------:|------|
| LangGraph 并行分支 | ⭐⭐⭐⭐⭐ | fetch → 3 Agents 并行 |
| Structured Output | ⭐⭐⭐⭐⭐ | 每个 Agent 的 Pydantic 模型 |
| 多模态 Agent | ⭐⭐⭐⭐ | Vega Agent（Plotly + Vision） |
| 外部 API 集成 | ⭐⭐⭐⭐⭐ | akshare + Tavily + ZhipuAI |
| 时序预测集成 | ⭐⭐⭐ | Prophet 桥接 |
| 工程化目录结构 | ⭐⭐⭐⭐ | models.py / nodes.py / graph.py |
| CLI 交互 | ⭐⭐⭐ | main.py |

### 12.4 完整课程体系总结

```
LangChain 系列（18课）
   模型调用 → 提示词 → 链式调用 → 记忆系统 → 嵌入 → Agent 基础
                          ↓
LangGraph 系列（5课）
   图的搭建 → 状态持久化 → 人机协作 → 多智能体 → 生产部署
                          ↓
终极综合实战（本课）
   LangChain + LangGraph 完整融合
   多 Agent 协作 + 多模态 + 结构化输出 + 外部工具集成
   从数据采集 → 多维度分析 → 综合决策 → 专业报告

整个学习路径：从"Hello World"到"企业级 AI 系统"
```

---

*本教学文档基于陈泽鹏老师视频课程整理编写。*
*本文档为 LangChain + LangGraph 系列课程的终极综合实战项目，涵盖多 Agent 协作架构设计、多模态图表分析（Vision Model）、Structured Output 全链路、akshare/Prophet/Plotly/Tavily/ZhipuAI 等多工具集成，以及从数据采集到综合决策的完整 AI 投研辅助系统构建。*

> ⚠️ **再次声明**：本文档为技术教学目的而编写。分析结果仅供学习参考，不构成任何投资建议。市场有风险，投资需谨慎。
