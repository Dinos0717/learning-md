# 17_多Agent协作与任务分发回收

> 📅 生成日期: 2026-07-13 | 🎯 级别: XL 级 | ⏱️ 录音时长: ~99 分钟 | 📏 文档规模: 6,166+ 行
> 🏷️ 标签: `ACP` `多Agent协作` `DAG编排` `任务分发` `Agent Client Protocol` `Adapter模式` `并发调度`

---

## 📑 目录

- [一、16课回顾：Skills 执行流程与 DAG 规划](#一16课回顾skills-执行流程与-dag-规划)
- [二、多 Agent 协作概念与 ACP 协议引入](#二多-agent-协作概念与-acp-协议引入)
- [三、ACP Agent 注册与配置体系](#三acp-agent-注册与配置体系)
- [四、ACP 生命周期与最小 Demo Agent](#四acp-生命周期与最小-demo-agent)
- [五、ACP Client 与任务分发运行](#五acp-client-与任务分发运行)
- [六、DAG + ACP 编排实战](#六dag--acp-编排实战)
- [七、并发执行与异步调度](#七并发执行与异步调度)
- [八、自建 Agent 适配器（Adapter 模式）](#八自建-agent-适配器adapter-模式)
- [九、Q&A 答疑与架构总结](#九qa-答疑与架构总结)

---

## 一、16课回顾：Skills 执行流程与 DAG 规划

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 画出 Skills 执行的完整流程图（渐进式披露 → DAG 规划 → 执行 → 校验）
> - [ ] 解释渐进式披露的三层递进机制，以及为什么不能一次性加载所有资源
> - [ ] 理解 capability/block 作为可编排最小执行单元的设计思想
> - [ ] 写出 DAG 执行器 MVP 的拓扑排序 + 队列调度逻辑
> - [ ] 理解 Validate/Verify 校验如何与 Loop 机制配合实现质量闭环
> - [ ] 解释为什么代码注释不会影响模型输出

---

### 1.1 Skills 执行全流程回顾

#### 🧠 直观理解

如果把一个 Skill 比作一道菜谱，那么 Skills 执行流程就是"看懂菜谱 → 确认厨房装备 → 拆成步骤 → 一步步做 → 尝味道 → 不行重来"的完整闭环。模型不是一口气把所有菜谱都背下来——它先看简介，需要什么再翻什么，这叫渐进式披露。然后它根据自己的能力（有没有烤箱、能不能炒菜）来规划一个有序的执行步骤图，最后做完还要检查结果是否达标。

#### 📖 详细解释

整个 Skills 执行的完整流程可以分为五个阶段：

```
用户请求
    │
    ▼
┌──────────────────────────────────────────────────┐
│ 阶段一：渐进式披露（Progressive Disclosure）       │
│ skill.md → 按需加载 resource/scripts/reference    │
│ 为什么？一次性传所有资源 token 爆炸且无关信息干扰   │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│ 阶段二：能力门控（Capability Gating）              │
│ 检查 Host 提供的可用能力 vs Skill 所需能力         │
│ 为什么？提前发现"能力缺失"，避免执行到一半报错      │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│ 阶段三：DAG 规划（DAG Planning）                   │
│ 模型根据可用 capability 生成有向无环执行计划        │
│ 为什么？复杂任务需要有序步骤，依赖关系决定执行顺序   │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│ 阶段四：DAG 执行（DAG Execution）                  │
│ 拓扑排序 → 找无依赖节点 → 入队 → 遍历执行 → 解锁下游│
│ 为什么？保证依赖先于被依赖者执行，不出现死锁         │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│ 阶段五：Validate / Verify 校验                    │
│ 检查执行结果是否达标 → 不达标触发 Loop 重做         │
│ 为什么？LLM 输出不稳定，需要质量把关形成闭环         │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
                    最终输出
```

> 💡 **核心洞见**：这五个阶段构成了一个完整的"感知 → 规划 → 行动 → 校验"智能体闭环。DAG 是中间的骨架——它将模型的规划能力（生成步骤）与执行器的调度能力（按依赖执行）桥接在一起。

> 🔗 **关联知识**：本模块中 DAG 的每个节点是 capability/block（如 web_search），在后续内容中，这些节点将被替换为"外部 Agent 任务"，从而实现多 Agent 协作编排。

#### 💻 代码示例

老师在第 16 课中搭建了一个完整的 demo，下面展示的是 DAG 规划阶段的核心 Prompt 结构：

```python
# 文件名: dag_planner.py
# 功能: 根据 skill 本体和可用能力，让模型生成 DAG 执行计划

# 构建传给模型的完整 Prompt
prompt = f"""
## Skill 本体（经过渐进式披露后选定的资源）
{skill_md_content}

## 追加的 Resource 信息（上一阶段圈定的资源）
{selected_resources}

## 允许使用的能力（Capabilities）
- web_search: 执行网络搜索
- model_request: 调用大模型进行推理/生成

## 可查询的主题（Mock 数据，真实场景中应为开放 query）
{available_topics}
"""

# 要求模型输出结构化 DAG 计划
output_schema = """
请将执行拆分为有向无环步骤（DAG），输出 JSON 格式：
{
  "steps": [
    {
      "id": "step_1",
      "capability": "web_search",
      "query": "搜索关键词",
      "depends_on": []
    },
    ...
  ]
}
"""
# 模型返回的 steps 列表即为可执行的 DAG 计划
```

> ⚠️ **注意事项**：在 demo 中，web_search 使用的是 mock 数据和预定义的 `available_topics`（如 "weather", "price", "traffic"）。在真实场景中，这一项应该被替换为开放式的搜索 query，模型自由生成搜索关键词。

---

### 1.2 渐进式披露机制详解

#### 🧠 直观理解

渐进式披露就像你去图书馆查资料——你不会把整栋楼的书全部搬到桌上。你先看书目卡（skill.md），确定这本书跟你的问题有关，然后翻目录（resource 列表），再挑需要的章节仔细读（按需加载具体 resource）。这样既不浪费时间，也不会被无关信息干扰。

#### 📖 详细解释

渐进式披露（Progressive Disclosure）是 Skills 架构中控制信息加载节奏的核心机制。它分为三层递进：

```
第一层：Skill 本体（skill.md）
    │  包含：名称、描述、能力声明、可引用资源列表
    │  大小：通常几十到几百行
    │  作用：让模型判断"这个 Skill 能做什么"
    │
    ▼
第二层：资源圈定（Resource Selection）
    │  模型根据任务需求，从第一层暴露的资源列表中
    │  选择性加载所需的 scripts / reference / assets
    │  为什么这一步必要？实际项目可能包含几十个资源文件，
    │  全部加载会导致 token 爆炸和注意力稀释
    │
    ▼
第三层：按需深度加载
    │  对于已选定的资源，进一步读取其内容
    │  例如：选定了 scripts/web_search.py 后
    │  读取该脚本的完整代码和文档
    │
    ▼
最终：模型拥有足够且聚焦的上下文来规划执行
```

**推导链：为什么不能一次性加载所有信息？**

```
起点: 假设一个 Skill 包含 20 个 resource 文件、5 个 scripts、10 个 reference 文档
  │
  ├── 第1步: 将所有内容拼接成一个 Prompt
  │   为什么不能这样做？假设每个文件平均 500 行，总行数 = 35 × 500 = 17,500 行。
  │   换算成 token：约 70,000+ tokens。虽然大部分模型的上下文窗口足够大，
  │   但模型对长上下文中部的信息注意力会衰减（Lost in the Middle 效应），
  │   关键信息可能被淹没在无关内容中。
  │
  ├── 第2步: 大量无关信息干扰模型决策
  │   为什么这是问题？如果任务只需要 web_search 能力，但 Prompt 中包含了
  │   database_query、image_generation、file_io 等 15 个不相关 resource，
  │   模型会在无关内容上浪费"注意力预算"，导致核心任务规划质量下降。
  │
  ├── 第3步: Token 成本线性增长
  │   为什么在意成本？每次 Skill 调用都要把全量信息传给模型，
  │   一天数百次调用下来，无关信息消耗的 token 费用非常可观。
  │
  └── 结论: 渐进式披露 = 用少量"索引级"信息让模型自己做选择，
      以最小 token 成本获得最大任务相关信息密度。
```

> 💡 **核心洞见**：渐进式披露的本质是**让模型成为信息筛选的主体**——不给它所有信息，而是给它一个"菜单"，让它根据任务自己点菜。这比人类预先写死加载规则更灵活，因为模型能理解任务语义并做出上下文相关的选择。

#### 💻 代码示例

```python
# 文件名: progressive_disclosure.py
# 功能: 实现渐进式披露的资源选择逻辑

# 第一层：加载 Skill 本体（skill.md）
skill_md = load_file("skills/travel_planner/skill.md")
# skill.md 内容示例：
# ---
# name: travel_planner
# description: 规划旅行行程，提供景点、天气、交通等信息
# resources:
#   - scripts/web_search.py
#   - scripts/model_request.py
#   - reference/attractions.md
#   - reference/weather_api.md
#   - reference/traffic_data.md
#   - reference/price_guide.md
#   - reference/group_meal.md
# ---

# 第二层：让模型根据任务选择需要的资源
resource_selection_prompt = f"""
## Skill 信息
{skill_md}

## 用户任务
{user_task}

## 可用资源列表
1. reference/attractions.md — 景点介绍数据
2. reference/weather_api.md — 天气查询 API 文档
3. reference/traffic_data.md — 交通数据参考
4. reference/price_guide.md — 门票价格指南
5. reference/group_meal.md — 团餐信息
6. scripts/web_search.py — 网络搜索脚本
7. scripts/model_request.py — 模型调用脚本

请根据用户任务，列出本次需要加载的资源编号。
"""

# 模型返回：需要加载资源 [1, 4, 5, 6]
# 排除了 2（天气 API）、3（交通数据）、7（model_request）
# 因为本次任务可能不需要这些

# 第三层：只加载选定的资源
selected_resources_content = ""
for resource_id in model_selected_ids:
    selected_resources_content += load_resource(resource_id)
# 最终传给 DAG 规划阶段的上下文 = skill.md + selected_resources_content
```

> 🔗 **关联知识**：渐进式披露选择的资源最终会与 capability 列表一起传入 DAG 规划阶段。详见 [1.4 DAG 规划机制](#14-dag-规划机制)。

---

### 1.3 能力门控与 capability/block 概念

#### 🧠 直观理解

想象你要组装一台电脑。能力门控就是先检查工具箱——你有螺丝刀吗？有硅脂吗？如果缺少关键工具（能力），那就别开始组装，先想办法补齐工具。capability/block 就是工具箱里的每一件工具：螺丝刀（web_search）、电钻（model_request）、水平仪（verify）、备份还原（replay）。

#### 📖 详细解释

**capability（能力）** 和 **block（执行块）** 本质上是同一个概念的两个视角：

| 维度 | Capability | Block |
|---|---|---|
| 定义角度 | "我能做什么"——面向声明 | "我去做什么"——面向执行 |
| 使用阶段 | DAG 规划阶段：模型根据可用 capability 编排步骤 | DAG 执行阶段：执行器根据 block 类型调用对应函数 |
| 类比 | 工具箱清单 | 实际拿起工具干活 |
| 在框架中的称谓 | 老师的 demo 中称为 capability | Agentic 等成熟框架中称为 block |

常见的 capability/block 类型：

| Block 类型 | 功能 | 类比 |
|---|---|---|
| `web_search` | 执行网络搜索，获取外部信息 | 上网查资料 |
| `model_request` | 调用大模型进行推理、总结、生成 | 动脑思考 |
| `verify` | 验证执行结果是否符合预期 | 检查作业 |
| `replay` | 重新执行某个步骤（用于纠错） | 重做一遍 |

**能力门控（Capability Gating）的定位与争议**：

老师在第 16 课中明确指出，**在当前 demo 的场景中，能力门控的意义有限**。原因如下：

```
推导链：为什么能力门控在本地框架中显得多余？

起点: 当前 demo 中，所有能力都由 Host 在代码中显式提供
  │
  ├── 第1步: Host 代码中已经写死了可用的 capability 列表
  │   例如：HOST_CAPABILITIES = {"web_search": ..., "model_request": ...}
  │
  ├── 第2步: 开发者自己知道写了哪些能力
  │   为什么多余？因为能力是你在代码里定义的，
  │   有没有你自己最清楚，不需要运行时再检查一遍。
  │
  └── 结论: 在 Host 能力固定的场景中，能力门控是冗余的。
      但它仍然作为流程中的一个"概念节点"存在，代表一种设计意图。
```

**能力门控真正有价值的场景**：Skills 的 scripts 目录中动态注册能力。例如，一个 `ls.sh` 脚本在 Skill 加载时被解析，动态注册为 `list_directory` 能力。此时 Host 并不知道这个能力的存在，需要通过能力门控来发现和注册。

> 💡 **核心洞见**：能力门控的本质不是"检查我知道什么"，而是"发现我不知道什么"。当 Skill 可以动态注入能力时，能力门控从冗余变为必需。

> ❓ **常见误解**：很多学员认为 capability 和 block 是两个完全不同的东西。实际上，它们的区别是**阶段不同、视角不同**——capability 用于规划阶段告诉模型"你可以用什么"，block 用于执行阶段告诉执行器"现在该调用哪个函数"。两者指向的是同一个可执行单元。

#### 💻 代码示例

```python
# 文件名: capability_gating.py
# 功能: 演示能力门控和能力注册

# ====== 场景 A：固定能力（能力门控意义不大）======
# Host 写死的能力列表
HOST_CAPABILITIES = {
    "web_search": WebSearchExecutor(),
    "model_request": ModelRequestExecutor(),
}

# Skill 声明自己需要的能力
skill_required_capabilities = ["web_search", "model_request"]

# 能力门控检查——在这个场景下是冗余的
# 因为 HOST_CAPABILITIES 是开发者自己写的，不会漏掉
for cap in skill_required_capabilities:
    if cap not in HOST_CAPABILITIES:
        raise CapabilityMissingError(f"缺少能力: {cap}")
```

```python
# ====== 场景 B：动态能力注册（能力门控有意义）======
import os

# Skill 目录下可能包含未知脚本，它们会动态注册为新能力
SKILL_SCRIPTS_DIR = "skills/my_skill/scripts"
DYNAMIC_CAPABILITIES = {}

# 遍历 scripts 目录，发现并动态注册能力
for script_file in os.listdir(SKILL_SCRIPTS_DIR):
    if script_file.endswith(".sh"):
        # 提取脚本名作为能力名——例如 ls.sh → list_directory
        capability_name = script_file.replace(".sh", "")
        with open(os.path.join(SKILL_SCRIPTS_DIR, script_file)) as f:
            script_content = f.read()
        DYNAMIC_CAPABILITIES[capability_name] = ScriptExecutor(script_content)

# 合并静态能力 + 动态能力
ALL_CAPABILITIES = {**HOST_CAPABILITIES, **DYNAMIC_CAPABILITIES}

# 此时能力门控变得有意义——检查动态能力是否成功加载
for cap in skill_required_capabilities:
    if cap not in ALL_CAPABILITIES:
        raise CapabilityMissingError(
            f"能力 {cap} 未找到。"
            f"可用能力: {list(ALL_CAPABILITIES.keys())}"
        )
# 如果 scripts 目录中有 ls.sh，它会被自动注册为 list_directory 能力
```

---

### 1.4 DAG 规划机制

#### 🧠 直观理解

DAG（有向无环图）规划就像是制定旅行攻略——不是随便把"订机票、订酒店、查景点、写计划"乱序执行，而是要理清依赖关系：先查天气（决定带什么衣服），再查景点（决定去哪里），最后汇总所有信息写出一份完整的旅行计划。DAG 中的每个节点是一个动作（capability 调用），箭头表示"我必须等前面做完才能开始"。

#### 📖 详细解释

**DAG（Directed Acyclic Graph，有向无环图）** 在 Skills 执行中的角色是：**将模型的规划能力结构化为可执行的有序步骤图**。

```
推导链：为什么需要 DAG 而不是线性步骤列表？

起点: Skills 通常涉及多个可并发操作，如同步搜索天气、价格、交通、团餐
  │
  ├── 第1步: 简单顺序执行（Step1 → Step2 → Step3 → Step4 → Step5）
  │   为什么不合适？四个搜索之间没有依赖关系，它们完全可以并行。
  │   顺序执行浪费了大量时间——串行耗时 T_total = T1 + T2 + T3 + T4 + T5
  │
  ├── 第2步: 引入 DAG 表达依赖关系
  │   为什么更好？天气搜索、价格搜索、交通搜索、团餐搜索之间无依赖，
  │   它们可以并行执行。只有最后的"生成计划"（model_request）依赖所有搜索结果。
  │   并行耗时 T_total ≈ max(T1, T2, T3, T4) + T5
  │
  ├── 第3步: DAG 的"无环"约束防止死锁
  │   为什么必须无环？如果 A 依赖 B，B 依赖 C，C 又依赖 A，
  │   三个节点互相等待，永远无法开始执行。无环保证总有一个拓扑序。
  │
  └── 结论: DAG 用有向边表达"依赖"，用无环约束保证"不出现循环等待"，
      既保证了正确的执行顺序，又为并行优化留下了空间。
```

**DAG 的数据结构**：

```python
# DAG 计划的核心数据结构
dag_plan = {
    "steps": [
        {
            "id": "search_weather",       # 节点唯一标识
            "capability": "web_search",   # 该节点使用的能力
            "query": "杭州户外景点天气预报", # 能力执行的参数
            "depends_on": []              # 依赖的前置节点（空 = 根节点，可立即执行）
        },
        {
            "id": "search_price",
            "capability": "web_search",
            "query": "杭州景点门票价格",
            "depends_on": []
        },
        {
            "id": "search_traffic",
            "capability": "web_search",
            "query": "杭州景点公交交通情况",
            "depends_on": []
        },
        {
            "id": "search_meal",
            "capability": "web_search",
            "query": "杭州团餐推荐",
            "depends_on": []
        },
        {
            "id": "generate_plan",
            "capability": "model_request",
            "task": "根据以上搜索结果生成一日游计划",
            "depends_on": [
                "search_weather",
                "search_price",
                "search_traffic",
                "search_meal"
            ]
        }
    ]
}
```

对应的 DAG 图结构：

```
    ┌───────────────┐
    │ search_weather │──────────────────────────────┐
    └───────────────┘                                │
                                                     │
    ┌───────────────┐                                │
    │ search_price   │──────────────────────────┐     │
    └───────────────┘                            │     │
                                                  │     │
    ┌───────────────┐                            │     │
    │ search_traffic │──────────────────────┐     │     │
    └───────────────┘                        │     │     │
                                              │     │     │
    ┌───────────────┐                        │     │     │
    │ search_meal    │──────────────────┐     │     │     │
    └───────────────┘                    │     │     │     │
                                          ▼     ▼     ▼     ▼
                                    ┌─────────────────────────┐
                                    │    generate_plan         │
                                    │  (model_request)         │
                                    │  depends_on: [全部四个]   │
                                    └─────────────────────────┘
```

**depends_on 字段的关键设计语义**：

| 场景 | depends_on 值 | 含义 | 执行时机 |
|---|---|---|---|
| 根节点（无依赖） | `[]` | 不依赖任何其他节点，可立即启动 | 初始化时直接入队 |
| 单依赖节点 | `["search_weather"]` | 仅依赖一个节点 | 等 search_weather 完成后入队 |
| 多依赖节点（汇聚） | `["step_a", "step_b", "step_c"]` | 依赖多个节点**全部**完成 | 等所有依赖节点都完成后才入队 |
| 汇聚 + 发散（菱形依赖） | 取决于拓扑位置 | 典型的 map-reduce 模式 | 先并发执行所有 map 节点，再汇聚执行 reduce |

> ⚠️ **注意事项**：老师特别强调，在 demo 中使用的是 `topic` 字段而非 `query` 字段，因为 mock 搜索只能查预定义的主题。在真实网络搜索场景中，`topic` 应替换为 `query`，由模型自由生成搜索关键词。

#### 💻 代码示例

```python
# 文件名: dag_planner_full.py
# 功能: 完整的 DAG 规划流程——从 Prompt 构建到模型输出解析

import json

def generate_dag_plan(skill_md, selected_resources, capabilities, user_task):
    """
    将 skill 信息和任务交给模型，生成 DAG 执行计划。
    
    参数:
        skill_md: skill.md 文件内容（渐进式披露第一阶段）
        selected_resources: 经过资源选择后的具体资源内容（第二阶段）
        capabilities: 可用能力列表
        user_task: 用户任务描述
    返回:
        dag_plan: 包含 steps 列表的 DAG 计划字典
    """
    # 构建传给模型的 Prompt
    prompt = f"""
你是一个任务规划器。请根据以下信息，将任务分解为有向无环图（DAG）执行计划。

## Skill 描述
{skill_md}

## 可用资源信息
{selected_resources}

## 可用能力（只能使用以下能力）
{json.dumps(capabilities, ensure_ascii=False)}

## 用户任务
{user_task}

## 输出要求
请输出严格的 JSON 格式，结构如下：
{{
    "steps": [
        {{
            "id": "步骤唯一标识（如 step_1）",
            "capability": "使用的能力名称（必须是上面列出的能力之一）",
            "query": "搜索查询词或任务参数",
            "depends_on": ["依赖的前置步骤 id 列表，根节点为空数组 []"]
        }}
    ]
}}

注意：
- depends_on 中的 id 必须在 steps 中已定义
- 不能形成循环依赖
- 根节点（无前置依赖）的 depends_on 为空数组
"""
    # 调用模型生成计划
    response = model.generate(prompt)
    # 解析模型返回的 JSON
    dag_plan = json.loads(response)
    return dag_plan


# 运行示例
dag_plan = generate_dag_plan(
    skill_md=skill_content,
    selected_resources=resource_content,
    capabilities=["web_search", "model_request"],
    user_task="规划杭州一日游行程，需要天气、价格、交通、团餐信息"
)

print("=" * 50)
print("DAG 执行计划:")
print("=" * 50)
for step in dag_plan["steps"]:
    print(f"\n节点 ID: {step['id']}")
    print(f"  能力: {step['capability']}")
    print(f"  参数: {step.get('query', step.get('task', 'N/A'))}")
    print(f"  依赖: {step['depends_on']}")
```

输出示例：

```
==================================================
DAG 执行计划:
==================================================

节点 ID: search_weather
  能力: web_search
  参数: 杭州户外景点天气预报
  依赖: []

节点 ID: search_price
  能力: web_search
  参数: 杭州景点门票价格
  依赖: []

节点 ID: search_traffic
  能力: web_search
  参数: 杭州景点公交交通情况
  依赖: []

节点 ID: search_meal
  能力: web_search
  参数: 杭州团餐推荐
  依赖: []

节点 ID: generate_plan
  能力: model_request
  参数: 根据以上搜索结果生成一日游计划
  依赖: ['search_weather', 'search_price', 'search_traffic', 'search_meal']
```

> 💡 **核心洞见**：DAG 规划的核心价值不是"模型能想出步骤"——任何 LLM 都能分步思考。DAG 的真正价值在于**用结构化数据（depends_on）显式表达步骤间的依赖关系**，使得执行器可以根据依赖关系实现拓扑排序和并行调度，而不是盲目地按数组顺序执行。

---

### 1.5 DAG 执行器 MVP 原型

#### 🧠 直观理解

DAG 执行器就像工地上的工程调度员。他看着施工图（DAG），先找出所有不依赖其他工序的活（挖地基），派工人去干。干完一个就看看哪些后续工序的前置条件满足了，把满足条件的派下去。这样一圈一圈地调度，直到所有活都干完。

#### 📖 详细解释

老师在第 16 课中给出了一个 DAG 执行器的 MVP（最小可行原型）。它的核心算法是**拓扑排序 + 队列调度**，分为以下步骤：

**执行器工作流程**：

```
            ┌──────────────────────┐
            │ 输入：DAG 计划 (steps) │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ Step 1: 提取所有节点 ID │
            │ - 建立 id → step 的映射 │
            │ - 建立 id → children 的映射│
            │ - 计算每个节点的入度     │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ Step 2: 找根节点入队     │
            │ 遍历所有节点，将        │
            │ depends_on=[] 的节点   │
            │ 放入执行队列 queue       │
            └──────────┬───────────┘
                       │
                       ▼
         ╔══════════════════════════════╗
         ║  Step 3: 循环调度执行        ║
         ║                              ║
         ║  while queue 不为空:          ║
         ║    ① 从队列取出一个节点       ║
         ║    ② 根据 capability 类型     ║
         ║       执行对应的动作          ║
         ║    ③ 记录执行结果             ║
         ║    ④ 解锁下游节点：           ║
         ║       - 遍历当前节点的 children│
         ║       - 每个 child 的入度减 1 │
         ║       - 入度归零的 child 入队  │
         ╚══════════════════════════════╝
                       │
                       ▼
            ┌──────────────────────┐
            │ Step 4: 返回所有结果   │
            └──────────────────────┘
```

**推导链：MVP 为什么是串行的？**

```
起点: MVP 使用单队列 while 循环，每次只取一个节点执行
  │
  ├── 第1步: 观察执行器代码——每次 popleft() 取一个
  │   为什么一次只取一个？因为 MVP 的目的是演示 DAG 的调度逻辑，
  │   不涉及并发编程的复杂性。使用单线程/单协程简化实现。
  │
  ├── 第2步: 判断依赖是否满足——检查入度计数
  │   为什么需要入度计数？因为 DAG 可能出现"扇形汇聚"——
  │   节点 C 依赖 A 和 B，但 A 和 B 完成时间不同。
  │   执行器需要确保两者都完成才将 C 入队，而不是谁先完成谁就触发。
  │   入度计数器（dependency_count）完美地跟踪了"还剩几个前置未完成"。
  │
  ├── 第3步: 串行执行 vs 并行执行的差异
  │   串行（MVP）: queue 一次出一个，总耗时 = 所有节点耗时之和
  │   并行（优化）: 无依赖节点同时执行，总耗时 = 关键路径长度
  │   为什么 MVP 选串行？教学目的——先理解调度逻辑，
  │   后续课程中会引入并发改造（asyncio、触发流 TriggerFlow 等）。
  │
  └── 结论: MVP 的串行实现是刻意为之的教学简化。
      在实际工程中，可以使用 asyncio、线程池、或框架内置的
      task_dag 来实现真正的并行 DAG 执行。
```

> ⚠️ **注意事项**：MVP 中的执行器只处理了两种 capability（用 `if/elif` 判断），这在教学演示中是够用的。在真实场景中，执行器需要维护一个 `capability → executor_function` 的注册表，根据节点声明的 capability 动态分发到对应的执行函数。

#### 💻 代码示例

```python
# 文件名: dag_executor_mvp.py
# 功能: DAG 执行器 MVP 原型——拓扑排序 + 队列调度

from collections import deque
import json

class DAGExecutor:
    """DAG 执行器 MVP：串行拓扑排序执行"""
    
    def __init__(self, dag_plan):
        """
        初始化执行器。
        
        参数:
            dag_plan: DAG 计划，包含 steps 列表
        """
        self.steps = dag_plan["steps"]
        self.results = {}                         # id → 执行结果
        self.step_map = {}                        # id → step 对象（正向索引）
        self.children_map = {}                    # id → 下游节点 id 列表（反向索引）
        self.dependency_count = {}                # id → 剩余未完成的前置依赖数（入度）
        self.queue = deque()                      # 就绪执行队列
        
        # 构建索引结构
        self._build_indexes()
    
    def _build_indexes(self):
        """构建三大索引结构：step_map、children_map、dependency_count"""
        # Step 1: 建立正向索引和初始化
        for step in self.steps:
            self.step_map[step["id"]] = step
            self.children_map[step["id"]] = []
            # 计算每个节点的入度（尚未完成的前置依赖数量）
            self.dependency_count[step["id"]] = len(step.get("depends_on", []))
        
        # Step 2: 建立反向索引（parent → children）
        # 为什么需要反向索引？因为执行完一个节点后，需要快速找到
        # "哪些节点在等它完成"——这就是 children_map 的作用。
        for step in self.steps:
            for dep_id in step.get("depends_on", []):
                # dep_id 是当前 step 的前置节点（parent）
                # 所以当前 step 是 dep_id 的下游节点（child）
                self.children_map[dep_id].append(step["id"])
        
        # Step 3: 找到所有入度为零的节点（根节点），入队
        for step in self.steps:
            if self.dependency_count[step["id"]] == 0:
                self.queue.append(step["id"])
        
        print(f"[执行器] 初始化完成")
        print(f"[执行器] 总节点数: {len(self.steps)}")
        print(f"[执行器] 根节点数: {len(self.queue)}")
        print(f"[执行器] 初始队列: {list(self.queue)}")
    
    def _execute_node(self, node_id):
        """
        执行单个节点。
        
        为什么 MVP 用 if/elif 而非注册表？
        因为 MVP 只演示两种能力，使用 if/elif 简化代码提高可读性。
        真实场景应使用注册表模式实现开放-封闭原则。
        """
        step = self.step_map[node_id]
        capability = step["capability"]
        query = step.get("query", step.get("task", ""))
        
        print(f"\n[执行] 节点: {node_id}")
        print(f"[执行] 能力: {capability}")
        print(f"[执行] 参数: {query}")
        
        # 能力分发：根据 capability 类型执行不同动作
        if capability == "web_search":
            result = self._mock_web_search(query)
        elif capability == "model_request":
            # 汇聚节点：需要收集所有前置依赖的执行结果作为证据
            evidence = self._collect_dependency_results(node_id)
            result = self._mock_model_request(query, evidence)
        else:
            result = f"[错误] 未知能力: {capability}"
        
        # 记录执行结果
        self.results[node_id] = result
        print(f"[执行] 结果摘要: {str(result)[:100]}...")
    
    def _unlock_children(self, node_id):
        """
        解锁下游节点：当前节点执行完毕后，检查它的所有下游节点。
        
        核心逻辑（入度递减法）：
        - 每个 child 节点的 dependency_count 代表"还剩几个前置未完成"
        - 当前节点完成 → 所有 child 的 dependency_count 减 1
        - 减到 0 → 所有前置依赖已完成 → child 获得执行资格 → 入队
        
        为什么叫"解锁"？DAG 中每个节点都有一个"前置依赖锁"，
        锁数 = depends_on 数组长度。每完成一个前置节点，锁数减一。
        锁数归零时节点解锁。
        """
        for child_id in self.children_map[node_id]:
            self.dependency_count[child_id] -= 1
            remaining = self.dependency_count[child_id]
            print(f"[解锁] {node_id} 完成 → {child_id} 剩余依赖: {remaining}")
            
            if remaining == 0:
                self.queue.append(child_id)
                print(f"[入队] {child_id} 所有前置依赖已完成，加入执行队列")
    
    def _collect_dependency_results(self, node_id):
        """收集某个节点所有前置依赖的执行结果，作为 model_request 的证据"""
        step = self.step_map[node_id]
        evidence = {}
        for dep_id in step.get("depends_on", []):
            evidence[dep_id] = self.results.get(dep_id, "未找到结果")
        return evidence
    
    def _mock_web_search(self, query):
        """Mock 网络搜索——真实场景中替换为实际 API 调用"""
        mock_data = {
            "杭州户外景点天气预报": "晴天，22-28°C，适合户外活动",
            "杭州景点门票价格": "西湖免费，灵隐寺 45 元，宋城 300 元",
            "杭州景点公交交通情况": "地铁 1 号线可达西湖，公交 7 路达灵隐",
            "杭州团餐推荐": "楼外楼人均 150，知味观人均 80",
        }
        return mock_data.get(query, f"[Mock] 搜索'{query}'的结果")
    
    def _mock_model_request(self, task, evidence):
        """Mock 模型请求——真实场景中调用 LLM 进行总结/生成"""
        return f"[模型生成] 基于证据 {json.dumps(evidence, ensure_ascii=False)} 完成任务: {task}"
    
    def run(self):
        """
        主执行循环。
        
        为什么使用 while 循环而非递归？
        ① 队列天然支持拓扑顺序的逐层执行
        ② while 循环便于控制执行进度和错误处理
        ③ 避免递归深度过大导致栈溢出的问题
        """
        print("\n" + "=" * 50)
        print("开始执行 DAG")
        print("=" * 50)
        
        step_count = 0
        while self.queue:
            # 从队列中取出下一个待执行节点（FIFO 顺序）
            node_id = self.queue.popleft()
            step_count += 1
            print(f"\n--- 第 {step_count} 步 ---")
            
            # 执行该节点
            self._execute_node(node_id)
            
            # 执行完成后，解锁所有依赖它的下游节点
            self._unlock_children(node_id)
        
        print("\n" + "=" * 50)
        print(f"DAG 执行完成，共执行 {step_count} 个节点")
        print("=" * 50)
        
        return self.results


# ====== 使用示例 ======
if __name__ == "__main__":
    # 假设这是模型生成的 DAG 计划
    dag_plan = {
        "steps": [
            {"id": "s1", "capability": "web_search", "query": "杭州户外景点天气预报", "depends_on": []},
            {"id": "s2", "capability": "web_search", "query": "杭州景点门票价格", "depends_on": []},
            {"id": "s3", "capability": "web_search", "query": "杭州景点公交交通情况", "depends_on": []},
            {"id": "s4", "capability": "web_search", "query": "杭州团餐推荐", "depends_on": []},
            {"id": "s5", "capability": "model_request", "task": "生成一日游计划", "depends_on": ["s1", "s2", "s3", "s4"]},
        ]
    }
    
    executor = DAGExecutor(dag_plan)
    results = executor.run()
    
    print("\n最终结果汇总:")
    for node_id, result in results.items():
        print(f"  {node_id}: {str(result)[:80]}...")
```

| 行号范围 | 关键代码 | 解释 |
|---|---|---|
| `__init__` | 三个映射表 + 入度计数 + 队列 | 初始化所有索引结构，为调度算法做准备 |
| `_build_indexes` | 正向映射 + 反向 children 映射 | 为什么需要两个映射？正向用于执行时查找 step 详情，反向用于执行后快速找到下游节点 |
| `dependency_count` | `len(depends_on)` | 每个节点的"锁数"——前置依赖数量。归零即可入队，这是拓扑排序的核心状态变量 |
| `_execute_node` | `if capability == "web_search"` | MVP 用 if/elif 做能力分发，真实场景应使用注册表模式 |
| `_unlock_children` | `dependency_count[child] -= 1` | 关键步骤：解锁下游。减到零时 child 入队——这是整个调度算法的核心 |
| `run` | `while self.queue:` + `popleft()` | 串行执行循环。每次取一个，执行，解锁，循环直到队列空 |

---

### 1.6 执行校验与 Loop 机制

#### 🧠 直观理解

DAG 执行完了不等于任务完成了。就像一个学生交作业——老师要批改（Validate），检查每道题是否真的做对了（Verify 溯源），如果分数不达标，打回去重做（Loop）。这个"批改-重做"循环确保最终交付质量。

#### 📖 详细解释

老师在第 16 课末尾介绍了 Skills 执行的质量保障闭环，包含三个关键层次：

**校验体系三层结构**：

```
┌─────────────────────────────────────────────┐
│ 第一层：Validate（执行校验）                  │
│ 检查 DAG 执行结果是否达标                     │
│ - 每个 step 是否有实际产出？                  │
│ - 产出内容是否与声明相符？                    │
│ - 是否有"说了搜索但实际没搜"的情况？           │
│ 为什么需要？LLM 可能产生幻觉——声称搜了但没搜    │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│ 第二层：Verify（溯源验证）                    │
│ 检查结果中的每一条信息是否能追溯到证据          │
│ - "门票 45 元"这句话的出处在哪里？             │
│ - 模型生成的内容是否引用了不存在的搜索结果？    │
│ 为什么需要？防止模型"编造"数据来源             │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│ 第三层：Quality Check + Loop（质量闭环）       │
│ 模型自评输出质量 → 不合格 → 重新执行           │
│ - 模型判断每个 step 的结果是否达标             │
│ - 如：某些景点未提供使用提示 → 质量不合格       │
│ - 不合格时触发 Loop：将结果带回，重新执行 Skill │
│ 为什么需要？单次执行的结果可能不完美，          │
│ 多次迭代可以逼近更高质量                       │
└─────────────────────────────────────────────┘
```

**推导链：为什么需要 Loop 机制？**

```
起点: DAG 执行完成，得到了一个"旅行计划"
  │
  ├── 第1步: 直接交付给用户
  │   为什么不行？LLM 生成的结果具有随机性和不稳定性。
  │   这次可能漏掉"团餐建议"，下次可能漏掉"交通提示"。
  │   用户收到的质量忽高忽低，不可靠。
  │
  ├── 第2步: 引入 Validate 和 Verify 检查
  │   为什么还不够？校验只能发现问题，不能自动修复。
  │   发现"质量不合格"后如果只是告诉用户"有问题"，
  │   用户还是得不到好的结果。
  │
  ├── 第3步: 引入 Loop 机制——不合格就重做
  │   为什么有效？将上一次的执行结果和不合格原因传回 Skill，
  │   让模型知道"上次哪里做得不好"，针对性地改进。
  │   这类似于强化学习中的"反馈 → 优化 → 再评估"循环。
  │
  ├── 第4步: 设置最大重试次数
  │   为什么不能无限循环？模型可能永远无法达到完美（能力天花板），
  │   需要设置重试上限（如 3 次）防止死循环。同时也是 token 成本控制。
  │
  └── 结论: Validate + Verify + Loop 构成一个质量反馈闭环。
      它不是一次性的判断，而是持续改进的机制。
```

> 💡 **核心洞见**：Validate 和 Verify 的区别很容易混淆。简单记——**Validate 检查"你做没做"**（是否有产出、产出是否完整），**Verify 检查"你做得对不对"**（产出是否可溯源、是否引用了真实数据）。前者是完整性校验，后者是正确性校验。两者结合才能全面评估执行质量。

#### 💻 代码示例

```python
# 文件名: validate_and_loop.py
# 功能: 演示执行后的校验与 Loop 重做机制

def validate_execution_results(dag_results, dag_plan):
    """
    Validate 环节：检查 DAG 执行结果是否达标。
    
    为什么需要显式的 Validate 而不仅仅相信执行器返回？
    因为执行器只保证"调用了"，不保证"调用成功了"。
    模型可能在 web_search 中返回空结果或幻觉结果。
    """
    issues = []
    
    for step in dag_plan["steps"]:
        step_id = step["id"]
        result = dag_results.get(step_id)
        
        # 检查 1: 是否有产出
        if result is None:
            issues.append(f"[{step_id}] 未找到执行结果")
            continue
        
        # 检查 2: 产出是否有实质内容
        if len(str(result)) < 20:
            issues.append(f"[{step_id}] 执行结果内容过短，可能无效")
        
        # 检查 3: 是否包含 Mock 标记（说明没有真正执行）
        if "[Mock]" in str(result):
            issues.append(f"[{step_id}] 使用了 Mock 数据而非真实结果")
    
    return issues


def verify_evidence(final_output, dag_results):
    """
    Verify 环节：溯源验证——检查最终输出中的每条信息是否能追溯到证据。
    
    为什么叫"溯源"？因为是从最终结论出发，反向查找支撑这个结论的
    原始证据是否存在。就像学术论文中的"参考文献"——每个论断都应该有出处。
    """
    verification_results = []
    
    # 检查 1: 最终输出是否引用了所有搜索结果
    for step_id, result in dag_results.items():
        if step_id not in str(final_output):
            verification_results.append(
                f"缺失溯源: 最终输出未引用 {step_id} 的结果"
            )
    
    # 检查 2: 最终输出中是否有"凭空出现"的信息
    # 实际实现中需要更复杂的语义匹配，这里简化为示例
    # 例如：最终输出提到"门票 100 元"，但在所有 dag_results 中找不到这个数字
    
    return verification_results


def model_evaluate_quality(dag_results):
    """
    让模型自评输出质量。
    
    为什么让模型自评而非用纯规则判断？
    因为质量是一个语义概念——"旅行计划是否实用"，
    很难用纯规则（如字数、关键词匹配）来衡量。
    模型自评更适合捕捉语义层面的质量缺陷。
    """
    # 示意：实际调用模型进行自评
    # prompt = f"请评估以下执行结果的质量（0-1 分），并指出不足之处：{dag_results}"
    # score, feedback = model.generate(prompt)
    return 0.6, "某些景点未提供使用提示和注意事项"


def quality_check_and_loop(skill_executor, max_retries=3):
    """
    质量检查 + Loop 重做机制。
    
    为什么是 max_retries 而非无限循环？
    因为模型可能永远无法达到完美（能力天花板），
    需要设置重试上限防止死循环。同时也是 token 成本控制。
    """
    for attempt in range(1, max_retries + 1):
        print(f"\n{'='*50}")
        print(f"第 {attempt} 次执行尝试")
        print(f"{'='*50}")
        
        # 1. 执行 Skill 的完整流程
        dag_results = skill_executor.run()
        
        # 2. Validate：检查结果是否完整
        issues = validate_execution_results(dag_results, skill_executor.dag_plan)
        
        # 3. 模型自评质量
        quality_score, feedback = model_evaluate_quality(dag_results)
        
        if not issues and quality_score >= 0.8:
            print(f"质量达标（评分: {quality_score}），交付结果")
            return dag_results
        else:
            print(f"质量不合格（评分: {quality_score}），问题: {issues}")
            if attempt < max_retries:
                print(f"触发 Loop 重做（第 {attempt}/{max_retries} 次）...")
                # 将不合格原因和反馈传回，让模型知道哪里需要改进
                skill_executor.add_feedback({
                    "previous_issues": issues,
                    "quality_score": quality_score,
                    "model_feedback": feedback,
                    "improvement_hints": "需要为每个景点提供使用提示和注意事项"
                })
            else:
                print(f"已达最大重试次数 ({max_retries})，返回当前最佳结果")
                return dag_results
```

**Loop 机制的完整流程图**：

```
        ┌─────────────┐
        │  用户请求     │
        └──────┬──────┘
               │
               ▼
        ┌─────────────┐
        │ Skill 执行   │◄──────────────────────┐
        │（渐进式披露   │                        │
        │ → DAG 规划   │                        │
        │ → DAG 执行） │                        │
        └──────┬──────┘                        │
               │                                │
               ▼                                │
        ┌─────────────┐                        │
        │  Validate    │                        │
        │  结果完整性   │                        │
        └──────┬──────┘                        │
               │                                │
               ▼                                │
        ┌─────────────┐                        │
        │   Verify     │                        │
        │  证据溯源     │                        │
        └──────┬──────┘                        │
               │                                │
               ▼                                │
        ┌─────────────┐    不合格               │
        │ 质量检查      │────────────────────────┘
        │（模型自评）   │    （Loop 重做——将反馈传回 Skill）
        └──────┬──────┘
               │ 合格
               ▼
        ┌─────────────┐
        │  最终交付     │
        └─────────────┘
```

> 🔗 **延伸阅读**：本文中 Validate 环节的具体 block 实现（详见 [第四章：ACP 生命周期与最小 Demo Agent](#四acp-生命周期与最小-demo-agent)）有更详细的讨论。

---

### 1.7 答疑：代码注释会影响模型结果吗？

---

**🙋 问题**（榕树同学提问）：在代码后面增加注释会影响模型结果吗？

> 📖 **背景**：老师在第 16 课中展示了大量的 Python 代码，包括 DAG 规划、执行器逻辑等。学员在跟练时可能会在代码中添加注释以帮助自己理解，但不确定这些注释是否会被模型"读到"并影响 Prompt 的内容。

**💬 老师回答**：

**不会影响。** 模型只会读取通过 `input`/`prompt` 参数显式传给它的信息，不会读取代码注释。原因如下：

1. **模型的"视野"仅限于 API 调用时传入的参数**。在 Python 代码中，当你调用 `model.generate(prompt)` 时，模型只能看到 `prompt` 这个变量中存储的字符串内容。它看不到你代码中其他位置的注释、变量名、函数名或其他任何未被传入的文本。

2. **代码注释是写给人的，不是写给模型的**。注释存在于源代码文件中，在程序运行时被 Python 解释器完全忽略。而模型 API 调用是运行时行为，模型收到的只有你通过 HTTP 请求体发送的 `messages` 或 `prompt` 字段内容。

3. **一个具体的例子**：

```python
# 这段代码注释模型完全看不到
# 因为我们传给模型的是 prompt_text 变量的值，而不是整个 .py 文件
prompt_text = "请帮我规划旅行"  # 这个行内注释模型也看不到
response = model.generate(prompt_text)
# 模型只收到 "请帮我规划旅行" 这 7 个字符
```

但如果注释**出现在你主动拼接进 prompt 的文本中**，它就会被读到：

```python
# 这段注释会传给模型，因为它被拼接进了 prompt 变量
code_with_comment = """
def search():
    # 这是一个搜索函数   ← 模型会读到这一行！
    pass
"""
prompt = f"请解释以下代码:\n{code_with_comment}"
response = model.generate(prompt)
# 模型会读到 "# 这是一个搜索函数" 这行注释
```

**总结**：区分的关键在于——你的文本是否被放入了传给模型 API 的参数中。代码文件中的注释（未被拼接到 prompt 里的）永远不会被模型读到。**模型只读取你主动喂给它的内容，不会"偷看"你的源代码。**

> 💡 **延伸**：这个问题的本质是理解"模型能访问什么"这个边界。模型的输入仅限于你通过 API 传入的文本内容（messages / prompt / system 等字段）。它不能访问你的文件系统、不能读取你的源码、不能看到你的环境变量——除非你主动把这些信息拼接进 prompt。这也解释了为什么渐进式披露是必要的：你需要**主动选择**把哪些信息传给模型，而不是担心模型会"自己读到"什么。

---

## 📋 课程小结

### 🗺️ 知识图谱

```
                    ┌─────────────────────────┐
                    │    Skills 执行全流程     │
                    └────────────┬────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                         ▼
┌───────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ 渐进式披露      │      │   DAG 规划与执行  │      │  校验与 Loop     │
│               │      │                 │      │                 │
│ skill.md      │      │ capability注册   │      │ Validate        │
│ → 资源选择     │      │ → 模型生成steps  │      │ → Verify        │
│ → 按需加载     │      │ → depends_on     │      │ → 质量检查       │
│               │      │ → 拓扑排序       │      │ → Loop 重做      │
│               │      │ → 队列调度       │      │                 │
│               │      │ → 解锁下游       │      │                 │
└───────────────┘      └─────────────────┘      └─────────────────┘
        │                        │                         │
        └────────────────────────┼─────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   感知 → 规划 → 行动       │
                    │   → 校验 的智能体闭环       │
                    └─────────────────────────┘
```

### 💡 一句话总结

> Skills 执行是一个"渐进式加载信息 → 模型生成 DAG 执行计划 → 拓扑排序调度执行 → 校验反馈形成闭环"的完整流程，其中 DAG 用 `depends_on` 显式表达步骤间依赖，执行器通过"锁计数归零即入队"的拓扑机制保证正确的执行顺序。

### 📍 系列定位

> 📍 **系列定位**：本文是「Agent架构师企业级智能体系统构建」系列的第 16 课回顾篇。
> - 上一篇：第 16 课正文 — Skills 执行环境与 DAG 设计
> - 下一篇：[M02：多Agent协作概念与ACP协议引入] — 从单Agent执行过渡到多Agent协同

---

## 📝 课后练习

### 练习 1: 画出 DAG 图并写出执行计划 JSON

**题目**：给定以下任务——"分析竞争对手的产品定价策略"，需要执行：
1. 爬取竞品 A 的定价页
2. 爬取竞品 B 的定价页
3. 爬取竞品 C 的定价页
4. 综合三家数据生成分析报告

请画出对应的 DAG 图，并为每个节点写出完整的 JSON 结构（包含 `id`、`capability`、`depends_on` 字段）。

**验收标准**：
- [ ] DAG 图清晰表达节点和依赖关系
- [ ] 根节点的 `depends_on` 为空数组
- [ ] 汇聚节点正确依赖所有根节点
- [ ] 不存在循环依赖

### 练习 2: 手写拓扑排序过程

**题目**：基于练习 1 的 DAG 图，模拟 DAG 执行器的拓扑排序过程。写出每一轮循环中：
- 当前队列中有哪些节点
- 执行了哪个节点
- 解锁了哪些下游节点
- 更新后的队列状态

**验收标准**：
- [ ] 初始队列中的节点都是 `depends_on` 为空的节点
- [ ] 下游节点的解锁条件正确（所有前置依赖完成后才解锁）
- [ ] 最终所有节点都被执行
- [ ] 执行顺序符合 DAG 的拓扑序

### 练习 3: 代码注释实验

**题目**：编写一个简单的 Python 脚本，在函数内部添加注释，然后调用 LLM API 传入该函数的返回值（而非源代码），验证注释是否影响模型输出。

**验收标准**：
- [ ] 脚本包含带有注释的函数定义
- [ ] API 调用传入的是函数的返回值而非源代码
- [ ] 实验结果证明注释不影响模型输出
- [ ] 总结"模型能看到什么"的边界

---

> 🤖 由 transcript-to-doc v4.1 生成

## 二、多 Agent 协作概念与 ACP 协议引入

---

### 2.1 为什么需要多 Agent 协作

#### 🧠 直观理解

想象你要组织公司 50 个人去杭州玩。你需要搜索交通方案、对比酒店价格、找团餐餐厅、整理所有人的时间表、制定行程路线。如果所有事情都由你一个人来做，你会累垮，而且每个环节的专业度也很难保证——你不一定最擅长找酒店，也不一定最了解杭州的美食。

最自然的做法是什么？**把任务拆开，分给不同的人去做**。让行政同事负责交通和酒店，让爱吃的同事负责团餐，让细心的人负责行程表。你只需要统筹全局、回收结果、做最终决策。

Agent 的世界也是这样。当我们面对一个复杂任务时，与其让一个 Agent 硬扛所有执行细节，不如把任务拆解后分发出去，让不同的 Agent 各司其职。

#### 📖 详细解释

**第一层：单 Skill 执行的局限性**

回顾前面的课程，我们花了三节课深入学习了 Skills 的执行机制。Skills 已经是一套很完整的方案了——它提供了任务描述、工具清单、执行回路的编排、校验与重做。但大家会发现，Skills 本身的复杂度就已经很高了。老师在设计课程时特意把 Skills 往后移，就是因为它的理解门槛和执行复杂度都远超前面的内容。

当一个任务真的变得非常复杂时，即使我们精心设计了一个 Skill，执行起来依然会遇到几个问题：

1. **执行器复杂度爆炸**：Validation、Replay、React loop、结果校验——每一个环节都需要精细的代码来处理，执行器的代码量和维护成本直线上升。
2. **单节点的能力上限**：一个 Agent 即使配置了丰富的 tools，它的能力也是有边界的。比如我们的 Agent 可能擅长信息检索，但在代码生成方面，就不如专门做代码的 Claude Code。
3. **上下文膨胀**：所有子任务挤在一个会话里，上下文越来越长，模型的注意力会被稀释，执行质量下降。

**第二层：DAG 拆解后的新问题**

我们用 DAG 解决了"如何把复杂任务拆开"的问题。DAG 能把一个任务拆成多个有依赖关系的执行节点——搜索方案、模型总结、生成文档等等。

但拆完之后，我们面临一个选择：**这些节点一定要由我们自己的执行器来跑吗？**

老师在 15 课就提过这个问题。一个复杂任务，我们可以从业务执行逻辑的层面先进行拆解。拆解完之后，把每个节点直接放进一个 Skill 执行器里跑，只是其中一种做法。

**第三层：从"自己执行"到"代理分发"的思想跃迁**

还有另一种做法——把拆解后的任务**分发出去**。

你的本机上可能装了 Claude Code，装了 Codex，装了各种不同能力的 Agent。你能不能把"写代码"这个子任务直接丢给 Claude Code？把"搜索整理信息"丢给另一个 Agent？

这个思想跃迁就是：**我们不一定要自己做所有的执行。我们可以变成一个调度者，把任务委托给其他更擅长这件事的 Agent。**

> 💡 **核心洞见**：Skill 执行器很复杂，执行成功率也不一定能保证。但如果你本机已经装了 Claude Code 或 Codex 这种专业的 Agent 服务，直接分发任务给它们，让它们用自己的 tools、skills、memory 去完成，往往比你自己写一个 Skill 执行器来跑更高效、更可靠。

---

#### 🔗 完整类比：「组织公司 50 人去杭州玩」

老师用了一个非常贴切的类比来展开这个思想，我们完整保留这个类比的起承转合。

**起：问题的提出**

假设你要组织公司 50 个人去杭州旅游。这是一个典型的复杂任务。你不可能一个人把所有事情都做完——订机票、订酒店、安排团餐、规划景点路线、收集每个人的饮食禁忌、制定预算方案。任何一个环节出错，整个行程都会受影响。

**承：自然的拆解方式**

你会怎么做？你会先把任务拆开：
- 有人负责搜索交通方案（北京到杭州的高铁和飞机，比较价格和时间）
- 有人负责搜索酒店（50 人的住宿，预算控制，位置方便）
- 有人负责搜索团餐（人均 50 元，杭帮菜，能容纳 50 人）
- 有人负责整理汇总（把所有搜索结果整合成一份完整的行程方案）

这就是 DAG 在做的事情——**分解**。你把一个"组织杭州游"的复杂任务，拆成了四个相对独立的子任务。

**转：拆完后谁来执行？**

拆完之后，你面临一个选择：这四个子任务，由谁来执行？

方案 A：全部自己干。你自己去搜交通、搜酒店、搜团餐、汇总整理。但这样做效率低，而且你不一定在每个方面都最擅长。你可能搜酒店很厉害，但找团餐不太行。

方案 B：分给不同的人。行政部门的同事负责交通和酒店（他们天天订票订酒店，最专业），热爱美食的同事负责团餐（他们知道哪里好吃又实惠），你自己负责最后汇总。每个人做自己最擅长的事，效率和质量都最高。

**合：映射到 Agent 世界**

回到我们的 Agent 架构：
- "搜索交通方案"这个节点，不一定要写成 `web_search(query="北京到杭州高铁")` 这样去调用一个工具。你完全可以把它变成一个**任务描述**，分发给一个专业的 Agent——比如 Claude Code，对它说："帮我搜索从北京到杭州的最佳交通方案，考虑 50 人出行，比较高铁和飞机的价格、时间、舒适度。"
- "搜索团餐"这个节点，同样可以分发给 Codex 或另一个 Agent，让它利用自己的搜索能力去完成。
- 你（流程总控方）只需要把这些任务发出去，等结果回来，然后做最终的汇总和决策。

> 🔗 **思想转变**：这里有一个关键的思想转变——我们不再把 DAG 的节点看作是"调用一个工具（web_search）"，而是看作"分配一个任务给一个 Agent"。节点从「函数调用」变成了「任务委托」。这是我们进入多 Agent 协作世界的钥匙。

---

### 2.2 多 Agent 协作四步模型

#### 🧠 直观理解

多 Agent 协作的本质可以归结为四个字：**拆、发、做、收**。就像你组织杭州游一样——先拆任务，再发给大家，大家各自做，最后你把结果收回来汇总。

#### 📖 详细解释

```
                           ┌─────────────────────┐
                           │     复杂任务输入       │
                           │ "组织50人杭州游"       │
                           └──────────┬──────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Step 1: 分解 (Decompose)                         │
│                                                                     │
│  职责：将复杂任务拆解为多个可独立执行的子任务节点                       │
│  工具：DAG（有向无环图）规划                                          │
│  产出：一组带有依赖关系的任务节点，明确哪些可以并行、哪些需要串行等待    │
│                                                                     │
│  示例拆解：                                                          │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐             │
│  │ 搜索交通方案   │   │ 搜索酒店信息   │   │ 搜索团餐方案   │             │
│  │ (task_1)     │   │ (task_2)     │   │ (task_3)     │             │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘             │
│         └──────────────────┼──────────────────┘                     │
│                            ▼                                        │
│                    ┌──────────────┐                                  │
│                    │  汇总整理方案  │                                  │
│                    │  (task_4)     │                                  │
│                    └──────────────┘                                  │
│                   ↑ 依赖 task_1, task_2, task_3 全部完成              │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Step 2: 分发 (Dispatch)                          │
│                                                                     │
│  职责：将分解后的子任务通过统一协议发送给执行 Agent                      │
│  通道：ACP（Agent Client Protocol）                                  │
│  每个分发包包含：任务描述 + 上下文 + 预期输出格式                       │
│                                                                     │
│  分发决策（Agent 选择）：                                            │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐             │
│  │ task_1 →     │   │ task_2 →     │   │ task_3 →     │             │
│  │ Claude Code  │   │ Codex        │   │ 自定义Agent   │             │
│  │ (擅长搜索推理) │   │ (擅长研究分析) │   │ (擅长餐饮推荐) │             │
│  └──────────────┘   └──────────────┘   └──────────────┘             │
│                                                                     │
│  关键：ACP 只负责"怎么发"，不负责"发给谁"——发给谁由编排层决定          │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          ▼                       ▼                       ▼
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│   Claude Code     │   │     Codex        │   │   自定义Agent     │
│   [执行 task_1]   │   │   [执行 task_2]   │   │   [执行 task_3]   │
│                  │   │                  │   │                  │
│ 使用自己的：      │   │ 使用自己的：      │   │ 使用自己的：      │
│ · tools          │   │ · tools          │   │ · tools          │
│ · skills         │   │ · skills         │   │ · skills         │
│ · memory         │   │ · memory         │   │ · memory         │
│ · 工作区          │   │ · 工作区          │   │ · 工作区          │
└────────┬─────────┘   └────────┬─────────┘   └────────┬─────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Step 3: 执行 (Execute)                           │
│                                                                     │
│  各 Agent 在自己的独立上下文中完成分配的任务                           │
│  内部执行回路：模型调用 → 工具使用 → 记忆管理 → 结果生成               │
│  不同 Agent 之间完全隔离，互不干扰                                    │
│                                                                     │
│  可并行执行：task_1, task_2, task_3 没有互相依赖 → 三者同时跑          │
│  串行等待：task_4 必须在 task_1, task_2, task_3 全部完成后才启动       │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Step 4: 回收 (Collect)                           │
│                                                                     │
│  职责：通过 ACP 协议回收各 Agent 的执行结果                            │
│  动作：结果校验 → 汇总合并 → 触发下游任务（如有依赖）                   │
│                                                                     │
│  回收逻辑：                                                          │
│  1. 等待 task_1, task_2, task_3 全部完成                             │
│  2. 收集三个 Agent 返回的结果                                         │
│  3. 将结果汇总为 task_4 的输入上下文                                   │
│  4. 启动 task_4（可由模型总结完成，或再分发给某个 Agent）               │
│  5. 最终输出：一份完整的「杭州游行程方案」                              │
└─────────────────────────────────────────────────────────────────────┘
```

#### 🔀 四步模型中的关键设计决策

| 步骤 | 谁说了算 | 核心工具/协议 | 为什么是它 |
|---|---|---|---|
| 分解 | 流程总控方 | DAG / TriggerFlow | 需要理解任务语义、规划执行路径 |
| 分发 | 流程总控方 | ACP | 需要统一的通信标准才能连接异构 Agent |
| 执行 | 具体执行方 | 各 Agent 自己的 tools/skills | 专业的人做专业的事，总控方不应干预内部细节 |
| 回收 | 流程总控方 | ACP | 需要统一的结果格式才能汇总和触发下游 |

> ⚠️ **注意事项**：四步模型中，步骤 3（执行）发生在各个 Agent 的内部，总控方**不参与也不应该参与**。总控方只需要关心"任务发出去了没有"和"结果回来了没有"，不需要关心 Claude Code 内部是怎么调用工具、怎么管理记忆的。这种边界意识是架构分层的基础。

---

### 2.3 ACP 协议详解

#### 🧠 直观理解

ACP 就像一套**标准化快递系统**。

你是一个调度中心，需要把包裹发给不同的收件人。如果没有快递系统，你需要自己开车把包裹送到每个人家里——而且每个人的门牌号格式不一样、收件时间不一样、签收方式不一样。这太累了。

有了快递系统之后，你只需要按照统一的标准填写运单号、贴好面单、交给快递员。至于包裹是走卡车、飞机还是火车，你不需要关心。你只需要知道：东西发出去了，对方收到了，结果会以统一的方式返回给你。

**ACP 就是这个快递系统**。它让所有 Agent 都遵循同一套收发标准，你不需要关心每个 Agent 内部的实现细节。

#### 📖 详细解释

**ACP 全称与定位**

ACP 全称是 **Agent Client Protocol**（Agent 客户端协议）。它是一个**轻量级、本地化**的 Agent 通信协议，核心目标是让同一台机器（或同一局域网）上的不同 Agent 之间能够以统一的方式进行通信。

老师特别强调：ACP 在解决的**本质问题**是——如果你的机器上装了不同的 Agent 服务（Claude Code、Codex、你自己写的全能助手），它们之间的调用接口各不相同。ACP 希望把这些 Agent 都按照统一的协议连接起来，让你的调度指令可以用一种标准方式发出去，执行结果也可以用一种标准方式收回来。

**ACP 的核心价值**

| 价值维度 | 没有 ACP 时 | 有 ACP 时 |
|---|---|---|
| 异构 Agent 互通 | 每个 Agent 有自己的调用方式，需要写 N 套对接代码 | 统一标准协议，一套对接代码适配所有 Agent |
| 任务分发 | 手动切换到不同 Agent 客户端，逐个操作 | 程序化分发，一个指令同时发给多个 Agent |
| 结果回收 | 各 Agent 返回格式不统一，需手动整理 | 统一的返回格式，自动汇总 |
| 扩展性 | 新增一个 Agent 需要写一套新的对接代码 | 新 Agent 只需实现 ACP 接口即可接入 |
| 上下文隔离 | 所有任务混在一个会话里，容易互相污染 | 每个 Agent 独立会话，天然隔离 |

**ACP 标准化了什么？**

老师提到，ACP 标准化的核心在于将不同 Agent 的行为抽象为一个**统一的接口层**。主要包括：

1. **`run`（启动执行）**：统一的执行入口，接收任务描述，返回执行结果。不管底层是 Claude Code 还是 Codex，对外的调用方式都是一样的。
2. **Prompt 生成**：将任务描述转化为各 Agent 能理解的指令格式。不同 Agent 的 prompt 格式不同，但 ACP 的适配层会统一处理。
3. **Memory 管理**：标准化会话上下文的传递和管理方式，确保上下文不会在不同 Agent 之间泄漏。

> 💡 **核心洞见**：ACP 的核心价值有两个维度。**维度一**：统一异构 Agent 的交互逻辑，让调度方能以相同的方式调用 Claude Code、Codex 和自定义 Agent。**维度二**：跨 Agent 信息传递的同时保持隔离——信息可以通过 ACP 安全地发给目标 Agent，但不同 Agent 的会话空间是独立的。

---

#### 🔀 对比辨析：ACP vs A2A

这是学员反复追问的问题，老师做了详细解答。

| 维度 | ACP (Agent Client Protocol) | A2A (Agent-to-Agent) |
|---|---|---|
| **协议层级** | 本地通信层（Local） | 网络通信层（Network） |
| **设计目标** | 本机上不同 Agent 之间的统一调用 | 跨网络、跨服务商的 Agent 互相发现与协作 |
| **核心能力** | 标准化的客户端调用接口（一收一发） | 服务发现 + 能力声明 + 身份认证 |
| **复杂度** | 轻量，侧重通道连接 | 较重，需要处理服务注册、发现、路由 |
| **身份机制** | 无需复杂的身份声明（本地可信环境） | 需要「我是谁」「我提供什么服务」「我有什么能力」 |
| **典型场景** | 调度方在本机把任务分发给 Claude Code / Codex | 互联网上不同公司/组织的 Agent 服务市场 |
| **类比** | 公司内部的**内线电话系统**：拿起电话拨分机号就能找到人，不需要自我介绍 | 公开的**黄页电话簿 + 交换机**：你需要先查到对方的号码和服务，再拨过去 |

> ❓ **常见误解**：ACP 是不是就是简化版的 A2A？
>
> **不是。**两者的设计目标完全不同。ACP 解决的是「本机异构 Agent 如何统一调用」的问题，它是一个**通道协议**，假设所有 Agent 都在你的控制之下，不需要服务发现。A2A 解决的是「互联网上不同服务商的 Agent 如何互相发现和协作」的问题，它是一个**市场协议**，需要服务注册与发现机制。两者的关系不是「简化版 vs 完整版」，而是「本地通道 vs 网络市场」——解决不同层次的问题。

#### 🔀 对比辨析：ACP vs MCP

由于本课程也涉及 MCP，这里做一个简要区分：

| 维度 | ACP | MCP |
|---|---|---|
| **标准化对象** | Agent 的调用接口 | Tool / Resource 的暴露接口 |
| **解决的问题** | 不同 Agent 之间如何通信、如何分发任务 | Agent 如何发现和调用外部工具 |
| **协议角色** | 调度层协议（Agent 到 Agent） | 工具层协议（Agent 到 Tool） |
| **类比** | 分机电话系统（怎么联系到另一个 Agent） | 工具插座标准（怎么插上各种工具） |

---

### 2.4 ACP 在架构中的角色定位

#### 🧠 直观理解

回到杭州游的类比。你是组织者（流程总控方），你负责把事情拆开、分配给不同的人、最后汇总结果。但你不需要亲自跑到每个人的工位上去盯着他们做事——你只需要一个统一的通知方式（比如群消息），把任务发出去、把结果收回来。

ACP 就是那个**统一的通知方式**。它不关心任务内容是什么，它只负责传。至于「什么事该谁做、什么顺序做」——那是你这个组织者在拆解任务时就已经定好的。

#### 📖 详细解释：编排 vs 通道的分离

这是本模块最核心的一个概念区分，老师反复强调：「**ACP 只决定通道连接，不决定编排。**」

```
┌─────────────────────────────────────────────────────────────────┐
│                        编排层 (Orchestration)                     │
│                                                                 │
│  ┌──────────────────────┐        ┌──────────────────────┐       │
│  │        DAG            │  或    │     TriggerFlow       │       │
│  │  (声明式任务依赖图)    │        │  (自主可控的编排引擎)   │       │
│  └──────────┬───────────┘        └──────────┬───────────┘       │
│             └───────────────────────────────┘                   │
│                         │                                       │
│              决定：任务怎么拆、谁来做、什么顺序                     │
│              可替换：今天用 DAG，明天可以换 TriggerFlow            │
└─────────────────────────┼───────────────────────────────────────┘
                          │
                          │  调用 ACP 接口分发任务
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                        通道层 (Transport)                        │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐       │
│  │                       ACP                             │       │
│  │              Agent Client Protocol                    │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                 │
│              决定：任务怎么传过去、结果怎么收回来                    │
│              固定：标准协议，不随编排方式改变                       │
│              只负责：一收一发，不关心任务内容                        │
└─────────────────────────────────────────────────────────────────┘
```

| 职责 | 负责者 | 具体做什么 | 可替换性 |
|---|---|---|---|
| **编排** | DAG / TriggerFlow | 拆解任务、确定依赖关系、决定执行顺序、选择执行 Agent | 高（可以换编排引擎） |
| **通道** | ACP | 把任务描述发给目标 Agent、把执行结果收回来 | 低（协议标准，不轻易变） |

> ⚠️ **注意事项**：很多同学刚开始会把 ACP 和 DAG 混在一起想，觉得既然 DAG 能拆任务、能管依赖，那还要 ACP 干什么？答案是：DAG 告诉你「先做什么后做什么」，ACP 告诉你「怎么把任务送出去」。一个是规划地图，一个是交通工具——两个都需要，但职责完全不重叠。

#### 📖 详细解释：流程总控方 vs 具体执行方

这是架构分层的另一个关键维度：

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│   流程总控方 (Orchestrator)                  你 —— 组织者         │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐                        │
│   │ 任务拆解  │ │ Agent选择 │ │ 结果回收  │   关心：全局流程        │
│   │ 用 DAG    │ │ 匹配能力  │ │ 汇总合并  │   不关心：内部怎么执行   │
│   └──────────┘ └──────────┘ └──────────┘                        │
│         │             │             ▲                            │
│         └─────────────┼─────────────┘                            │
│                       │                                          │
│               ACP 通道 │                              ACP 通道    │
│              (分发任务) │                             (回收结果)   │
│                       ▼                              │           │
│   ┌──────────────────────────────────────────────────┴─────────┐ │
│   │                                                              │
│   │   具体执行方 (Executors)              行政 / 美食达人 / 细心同事 │
│   │                                                              │
│   │   ┌──────────┐   ┌──────────┐   ┌──────────┐               │
│   │   │Claude Code│   │  Codex   │   │自定义Agent│               │
│   │   │           │   │          │   │          │               │
│   │   │ 自己的:   │   │ 自己的:   │   │ 自己的:   │  关心：把自己   │
│   │   │ · tools   │   │ · tools  │   │ · tools  │  的任务做好     │
│   │   │ · skills  │   │ · skills │   │ · skills │  不关心：全局    │
│   │   │ · memory  │   │ · memory │   │ · memory │  流程          │
│   │   │ · 工作区   │   │ · 工作区  │   │ · 工作区  │               │
│   │   └──────────┘   └──────────┘   └──────────┘               │
│   │                                                              │
│   └──────────────────────────────────────────────────────────────┘
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

| 维度 | 流程总控方 | 具体执行方 |
|---|---|---|
| **关心的事** | 任务拆得对不对、分给谁最合适、结果能不能汇总 | 分配给我的任务怎么做好 |
| **不关心的事** | 内部怎么调用工具、怎么管理记忆 | 整体流程走到哪了、其他 Agent 在做什么 |
| **核心能力** | 编排逻辑、Agent 选择策略、结果校验规则 | 专业领域的执行能力（代码、搜索、分析） |
| **可替换性** | 高（换编排引擎不影响执行方） | 高（换执行 Agent 不影响编排） |

> 💡 **核心洞见**：这种分离的本质是**关注点分离**（Separation of Concerns）。总控方关心「What to do」和「Who does it」，执行方关心「How to do it」。一旦分开，两边的复杂度都降低了——总控方不需要知道 Claude Code 怎么工作，Claude Code 也不需要知道自己是整个流程的第几步。

#### 📖 详细解释：上下文隔离的价值

多 Agent 架构带来的一个隐性的、但非常重要的好处是**上下文隔离**。

在单 Agent 执行复杂任务的场景中，所有子任务都在同一个会话里跑。上下文不断累积，模型的注意力被稀释，前面的错误可能影响后面的判断，不同子任务的信息互相干扰。

在多 Agent 架构中：

1. **每个 Agent 有自己的独立会话空间**。Claude Code 处理交通搜索的上下文和 Codex 处理团餐搜索的上下文是完全隔离的。
2. **即使把多个任务发给同一个 Agent**（比如先后两次发给 Claude Code），每次分发也是独立的会话。前一次执行不会污染后一次。
3. **总控方的上下文保持干净**。总控方只收到汇总后的结果，不需要承受所有执行细节的上下文爆炸。

```
单 Agent 模式（上下文膨胀）：

  ┌──────────────────────────────────────────────────────┐
  │              同一个会话 (Single Session)               │
  │                                                      │
  │  交通搜索上下文 → 酒店搜索上下文 → 团餐搜索上下文 → 汇总 │
  │  [██████████████████████████████████████████████████] │
  │                    上下文越来越长，质量下降              │
  └──────────────────────────────────────────────────────┘

多 Agent 模式（上下文隔离）：

  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
  │  Agent A 会话    │ │  Agent B 会话    │ │  Agent C 会话    │
  │  交通搜索        │ │  酒店搜索        │ │  团餐搜索        │
  │  [████████]      │ │  [████████]      │ │  [████████]      │
  │  独立、精简       │ │  独立、精简       │ │  独立、精简       │
  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
           │                   │                   │
           └───────────────────┼───────────────────┘
                               │
                               ▼
           ┌──────────────────────────────────────┐
           │        总控方上下文 (干净、精简)        │
           │  只收到各 Agent 的汇总结果             │
           │  [████] 上下文不会爆炸                 │
           └──────────────────────────────────────┘
```

---

#### 💻 思想转变：从 web_search 块到 agent 任务

老师用了一个非常具象的例子来说明从单 Agent 到多 Agent 的思维转变，我们保留这个推演过程。

**转变前：把 DAG 节点当作工具调用**

在 DAG 执行器中，我们拿到规划结果后，每个节点是一个具体的执行动作。比如搜索任务，我们通常会写成：

```
DAG 节点:
  ├── 节点 1: web_search(query="北京到杭州高铁方案")
  ├── 节点 2: web_search(query="杭州 50 人住宿 团建酒店")
  ├── 节点 3: web_search(query="杭州团餐 人均 50 元")
  └── 节点 4: 模型总结(依赖: 节点1, 节点2, 节点3)
```

每个节点是一个**工具调用**（web_search）。执行器拿到这个规划，逐个调用 web_search 工具，拿到结果，最后汇总。

**转变后：把 DAG 节点当作任务委托**

现在换一个思路。我们把 `web_search(query=...)` 改成 `agent_task(agent=..., description=...)`：

```
DAG 规划:
  ├── 节点 1: agent_task(
  │     agent="claude_code",
  │     description="搜索从北京到杭州的最佳交通方案，考虑 50 人团队出行，
  │                  比较高铁和飞机的时间、价格、舒适度"
  │   )
  ├── 节点 2: agent_task(
  │     agent="codex",
  │     description="搜索杭州适合 50 人团建的酒店，预算适中，位置方便，
  │                  含早餐，有会议室"
  │   )
  ├── 节点 3: agent_task(
  │     agent="custom_agent",
  │     description="搜索杭州适合 50 人聚餐的杭帮菜餐厅，人均预算 50 元，
  │                  需有包间或大桌"
  │   )
  └── 节点 4: 模型总结(依赖: 节点1, 节点2, 节点3)
```

关键变化：**节点不再是调用一个简单的工具，而是把整个子任务委托给一个有完整执行能力的 Agent。**Claude Code 拿到「搜索交通方案」这个任务描述后，它内部可以自己决定怎么搜、搜什么关键词、怎么整理结果——它在自己的执行回路中拥有完整的自主权。

> 💡 **核心洞见**：这个转变的精髓在于——**从「我说怎么做」变成了「我说做什么，你决定怎么做」**。`web_search` 是你告诉执行器「调用搜索工具」，`agent_task` 是你告诉 Agent「我需要这个结果，你怎么做我不管」。前者是指令式的，后者是目标式的。这就是单 Agent 工具调用和多 Agent 任务委托之间的本质差异。

**这个转变的关键前提**

之所以能做这样的转变，是因为：

1. **DAG 已经完成了任务拆解**：我们已经知道有哪些子任务、它们之间的依赖关系是什么。把 `web_search` 替换成 `agent_task`，只是改变了执行方式，不改变规划结构。
2. **ACP 提供了统一的分发通道**：不管目标是 Claude Code 还是 Codex，分发的方式是一样的。没有统一的通道，这种替换就无法规模化。
3. **每个 Agent 自带完整的执行能力**：Claude Code 有自己的 tools、skills、memory，它不是被动地执行一个工具调用，而是主动地去完成一个目标。这种能力是简单的工具调用所不具备的。

---

### 🗺️ 本模块知识图谱

```
                        ┌─────────────────────────────┐
                        │   多 Agent 协作的核心理念       │
                        │   "拆解后不一定自己执行"         │
                        └─────────────┬───────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │   四步协作模型     │    │    ACP 协议       │    │   架构角色分离     │
    │                 │    │                 │    │                 │
    │ 分解→分发→执行→回收│    │ Agent Client    │    │ 编排 ≠ 通道       │
    │                 │    │ Protocol        │    │ 总控 ≠ 执行       │
    └────────┬────────┘    └────────┬────────┘    └────────┬────────┘
             │                      │                      │
             ▼                      ▼                      ▼
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │ DAG = 编排工具    │    │ vs A2A: 本地轻量  │    │ 上下文隔离        │
    │ ACP = 通信通道    │    │ vs MCP: 调度层    │    │ 各Agent独立会话   │
    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 💡 本模块一句话总结

> 多 Agent 协作的本质不是让一个 Agent 变强，而是把复杂任务拆解后，通过 ACP 这个统一的本地通信协议，将子任务委托给不同的专业 Agent 执行，总控方只负责编排与回收——实现「专业的人做专业的事，调度的人只管调度」。

> 🔗 **前置知识**：本模块承接 [第 1 章：Skills 执行流程与 DAG 规划回顾]，你需要理解 DAG 如何将复杂任务拆解为可执行节点，以及单个 Skill 的执行回路。
>
> 🔗 **延伸阅读**：下一章 [第 3 章：ACP Agent 注册与配置体系] 将具体讲解如何注册不同的 Agent、如何配置它们的连接参数，将本模块的概念落地到代码层面。

## 三、ACP Agent 注册与配置体系

> 🔗 **前置知识**：详见 [第二章：多Agent协作概念与ACP协议引入]

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 用 pip 安装 ACP Python 包并验证版本
> - [ ] 解释 AgentSpec 五个字段的设计意图
> - [ ] 区分自建 Agent、外部适配器 Agent、网关桥接 Agent 三种注册方式
> - [ ] 理解 npx 命令"下载+安装+启动"的一体化机制
> - [ ] 使用 launcher_available() 验证本机 Agent 可用性
> - [ ] 独立撰写 AgentSpec 配置文件，注册你自己的 Agent

---

### 3.1 🏗️ 环境准备

#### 安装 ACP Python 包

在 Python 环境中安装 `agent-client-protocol` 包，推荐版本 `0.10.1`。该包提供了 ACP 协议的 Python 客户端能力，包括后续会使用的 `run_acp_task` 等核心函数。

```bash
pip install agent-client-protocol==0.10.1
```

或者将版本写入 `requirements.txt` 后批量安装：

```python
# 文件名: requirements.txt
agent-client-protocol==0.10.1
```

```bash
pip install -r requirements.txt
```

安装成功后可在 Python 中验证：

```python
import agent_client_protocol
print(agent_client_protocol.__version__)  # 预期输出: 0.10.1
```

#### ⚠️ 前提条件：各 Agent 对宿主机的要求

ACP 协议负责"桥接"不同类型的 Agent。要让注册表中的 Agent 真正可用，你的本机还需满足以下条件：

| Agent 名称 | 本机前提 | 验证命令 |
|---|---|---|
| `company-policy` | Python 3.10+ | `python --version` |
| `demo-reviewer` | Python 3.10+（共用 demo_acp_agent.py） | 同上 |
| `demo-reporter` | Python 3.10+（共用 demo_acp_agent.py） | 同上 |
| `claude-agent` | 安装 Claude CLI 并已登录（`claude login`） | `which claude` |
| `codex` | Node.js 运行环境（npx 随 npm 自带） | `which npx` |
| `openclaw` | 安装 OpenClaw Gateway CLI | `which openclaw` |

> ⚠️ **注意事项**：`launcher_available()` 只检查启动器命令是否在系统 PATH 中，不检查账号登录状态、网络连通性或认证令牌是否有效。即使返回 `True`，claude-agent 可能因未登录而无法正常执行任务，codex 可能因 API key 过期而报错。`launcher_available()` 是**必要条件**，不是**充分条件**。

---

### 3.2 💻 AgentSpec 数据结构逐字段解析

#### 🧠 直观理解

**AgentSpec 就是一张"Agent 身份证"**。要启动一个 Agent，操作系统需要知道用哪个命令、传什么参数、这个 Agent 做什么用。AgentSpec 把这五项信息封装成一个**不可变的数据结构**，供调度器随时查阅。

就好比外卖平台上的"店铺信息卡"——店名（name）、后厨位置与启动指令（command + args）、品类（kind）、备注说明（note）。调度器（主流程）根据这张卡就知道该调用谁、怎么调用。

#### 📖 完整源码与行级解析

以下展示 `agent_registry.py` 的数据结构定义部分。这是整个 Agent 注册体系的基石——后续的 AGENT_MATRIX 字典、acp_client 调度逻辑、DAG 编排层都依赖这个数据结构。

```python
# 文件名: agent_registry.py（数据结构定义片段，第 1-20 行）
# 功能: 定义 AgentSpec 不可变数据类，作为所有 Agent 配置的统一格式

from __future__ import annotations      # 行 1: PEP 563 延迟求值注解

import shutil                            # 行 3: shell 工具，用于 which 命令查找
import sys                               # 行 4: 获取当前 Python 解释器路径
from dataclasses import dataclass        # 行 5: 数据类装饰器
from pathlib import Path                 # 行 6: 面向对象路径处理


SCRIPT_DIR = Path(__file__).resolve().parent  # 行 9: 脚本目录绝对路径


@dataclass(frozen=True)                  # 行 12: frozen=True → 不可变实例
class AgentSpec:                         # 行 13: Agent 规格数据类
    """一个 ACP Agent 的启动配置。"""     # 行 14: docstring

    name: str                            # 行 16: Agent 唯一标识符
    command: str                         # 行 17: 启动命令（python/npx/openclaw）
    args: tuple[str, ...]                # 行 18: 命令参数（不可变元组）
    kind: str                            # 行 19: Agent 分类标签
    note: str                            # 行 20: 备注说明（人类可读）
```

#### 行级解析表

下表对每一行关键代码进行逐行解释，覆盖设计意图、技术选型和工程考量：

| 行号 | 代码 | 解释 |
|---|---|---|
| 1 | `from __future__ import annotations` | 启用 PEP 563「延迟求值类型注解」。让所有类型注解以字符串形式存储，避免循环引用问题，同时提升类定义时的导入性能。若不写这行，`tuple[str, ...]` 这类泛型写法在 Python 3.9 之前会直接报 `TypeError`。写这行之后，Python 不会在定义时求值注解，而是在需要时（如 `get_type_hints()`）才解析 |
| 3 | `import shutil` | 导入 shell 工具模块。本节仅使用 `shutil.which()` 一个函数，用于在系统 PATH 中查找可执行文件。`shutil.which("npx")` 返回 `/usr/local/bin/npx` 或 `None` |
| 4 | `import sys` | 获取当前 Python 解释器的绝对路径（`sys.executable`），用于自建 Agent 的启动命令。当用户使用虚拟环境时，`sys.executable` 自动指向虚拟环境内的 Python（如 `.venv/bin/python`），确保子进程使用相同的依赖环境 |
| 5 | `from dataclasses import dataclass` | 导入数据类装饰器。`@dataclass` 会自动生成 `__init__`、`__repr__`、`__eq__` 等样板方法。选择 dataclass 而非 namedtuple 的原因：支持类型注解、支持方法定义、支持 property |
| 6 | `from pathlib import Path` | 面向对象的文件路径处理库，跨平台兼容（Windows/Linux/macOS）。`Path` 比 `os.path` 更直观：`SCRIPT_DIR / "demo_acp_agent.py"` 用 `/` 运算符拼接路径，代码可读性更好 |
| 9 | `SCRIPT_DIR = Path(__file__).resolve().parent` | **关键常量**。三步操作：`__file__` 取当前脚本路径（可能为相对路径），`.resolve()` 转为绝对路径（解析所有符号链接），`.parent` 取父目录。这确保了无论从哪个工作目录执行脚本，都能正确定位同目录下的 adapter 文件 |
| 12 | `@dataclass(frozen=True)` | `frozen=True` 使实例**不可变**——创建后不能修改任何字段。这是一种防御性编程策略：AGENT_MATRIX 中的 AgentSpec 一旦注册就不应被意外修改。如果代码尝试 `spec.name = "xxx"`，Python 会抛出 `FrozenInstanceError` |
| 16 | `name: str` | Agent 的**唯一标识符**。这个值同时作为 AGENT_MATRIX 字典的 key，调度器通过名称查找对应的启动配置。命名使用小写字母加连字符（kebab-case），如 `"company-policy"`，保持与 npm 包命名风格一致 |
| 17 | `command: str` | **启动命令**。根据 Agent 类型不同，取值也不同：自建 Agent 用 `sys.executable`（Python 解释器的绝对路径），外部适配器用 `"npx"`，网关桥接用 `"openclaw"`。这个字段直接传给 `asyncio.create_subprocess_exec` 作为可执行文件路径 |
| 18 | `args: tuple[str, ...]` | **命令参数元组**。类型为 `tuple[str, ...]`，表示不定长但元素类型固定为 str 的**不可变**序列。`...` 是 Python 3.9+ 的类型语法，等价于 `Tuple[str, ...]`。使用 tuple 而非 list，确保参数序列不会被意外 append/remove |
| 19 | `kind: str` | Agent **分类标签**。本课程中使用 4 种值：`"自建 Agent"`、`"本地演示 Agent"`、`"外部 Agent 适配器"`、`"网关桥接 Agent"`。这个字段用于日志分组、UI 展示、和运行时按类型批量过滤（如"只启动所有自建 Agent"） |
| 20 | `note: str` | **备注说明**，纯粹供开发者阅读，不影响运行时行为。内容包含：功能描述（"差旅制度核查"）、版本号说明（"课程固定 0.0.46"）、注意事项（"升级前需重新验证"）。属于"可读性优先"的设计 |

#### 💡 SCRIPT_DIR 与绝对路径的重要性：工程决策分析

`SCRIPT_DIR = Path(__file__).resolve().parent` 这一行承载了一个重要的工程假设：**所有 ACP adapter 脚本与 `agent_registry.py` 放在同一目录下**。

```
scripts/
├── agent_registry.py          ← SCRIPT_DIR 指向此目录
├── policy_acp_adapter.py      ← 被 company-policy 引用
└── demo_acp_agent.py          ← 被 demo-reviewer / demo-reporter 引用
```

为什么必须使用 `.resolve()` 取绝对路径？考虑以下场景：

```
# 用户从项目根目录启动
$ pwd
/Users/dinoschen/AI-Application-Development-Lessons/lessons/17_多Agent协作与任务分发回收

$ python scripts/acp_client.py
```

此时如果 args 中使用了相对路径 `"policy_acp_adapter.py"`，Python 子进程会从**当前工作目录**（项目根目录）查找该文件，而不是从 `scripts/` 目录查找。文件找不到 → `FileNotFoundError`。

使用 `SCRIPT_DIR / "policy_acp_adapter.py"` 后，路径变为绝对路径：

```python
# SCRIPT_DIR = /Users/.../lessons/17_多Agent协作与任务分发回收/scripts
args = (str(SCRIPT_DIR / "policy_acp_adapter.py"),)
# 结果: ("/Users/.../lessons/17_多Agent协作与任务分发回收/scripts/policy_acp_adapter.py",)
```

无论从哪个工作目录启动，路径始终正确。

> 🐞 **常见坑**：用 `os.getcwd()` 代替 `SCRIPT_DIR`。`getcwd()` 返回的是**执行命令时的当前工作目录**，而非脚本所在目录。当从项目根目录执行 `python scripts/acp_client.py` 时，`getcwd()` 是项目根目录，而不是 `scripts/`。此时拼接的相对路径必然错误。**永远使用 `Path(__file__).resolve().parent` 定位脚本目录，不要依赖 `getcwd()`**。

---

### 3.3 💻 AGENT_MATRIX 注册表详解 —— 六种 Agent 逐一分析

#### 🧠 直观理解

**AGENT_MATRIX 就是一个"Agent 花名册"**。它是一个字典（`dict[str, AgentSpec]`），key 是 Agent 的唯一名称，value 是该 Agent 的完整启动配置。主调度器拿到一个任务后，从花名册中按名查找 AgentSpec，提取 command 和 args 就能启动对应的 Agent 进程。

这种设计模式称为**注册表模式（Registry Pattern）**——将"定义"和"使用"分离。新增 Agent 只需在 AGENT_MATRIX 中加一条 entry，调度逻辑无需修改。这符合开闭原则（对扩展开放，对修改关闭）。

#### 注册表完整源码

```python
# 文件名: agent_registry.py（注册表部分，第 39-82 行）
# 功能: 统一注册 6 种 ACP Agent，按三种启动类型分类

AGENT_MATRIX: dict[str, AgentSpec] = {                 # 行 39

    # ═══════════ 第一类：自建 Agent（python 启动）═══════════
    "company-policy": AgentSpec(                        # 行 40
        name="company-policy",
        command=sys.executable,                        # 行 42: 当前 Python 解释器绝对路径
        args=(str(SCRIPT_DIR / "policy_acp_adapter.py"),),  # 行 43: adapter 脚本绝对路径
        kind="自建 Agent",
        note="差旅制度核查：把已有业务模块包成 ACP Agent",
    ),
    "demo-reviewer": AgentSpec(                        # 行 47
        name="demo-reviewer",
        command=sys.executable,
        args=(str(SCRIPT_DIR / "demo_acp_agent.py"), "--role", "reviewer"),
        kind="本地演示 Agent",
        note="信息核实：规则化输出，不调用模型",
    ),
    "demo-reporter": AgentSpec(                        # 行 54
        name="demo-reporter",
        command=sys.executable,
        args=(str(SCRIPT_DIR / "demo_acp_agent.py"), "--role", "reporter"),
        kind="本地演示 Agent",
        note="出差方案汇总：规则化输出，不调用模型",
    ),

    # ═══════════ 第二类：外部 Agent 适配器（npx 启动）═══════════
    "claude-agent": AgentSpec(                         # 行 61
        name="claude-agent",
        command="npx",                                 # 行 63: Node 包执行器
        args=("-y", "@agentclientprotocol/claude-agent-acp@0.49.0"),
        kind="外部 Agent 适配器",
        note="Claude Agent SDK 适配器；认证、模型和计费由 Agent 自身配置",
    ),
    "codex": AgentSpec(                                # 行 68
        name="codex",
        command="npx",
        args=("-y", "@agentclientprotocol/codex-acp@0.0.46"),
        kind="外部 Agent 适配器",
        note="课程固定 0.0.46；npm 当日已发布 1.0.0，升级前需重新验证",
    ),

    # ═══════════ 第三类：网关桥接 Agent（openclaw 启动）═══════════
    "openclaw": AgentSpec(                             # 行 75
        name="openclaw",
        command="openclaw",                            # 行 77: OpenClaw 网关 CLI
        args=("acp",),                                 # 行 78: 子命令，启动 ACP 模式
        kind="网关桥接 Agent",
        note="通过 OpenClaw Gateway 承接 ACP 会话",
    ),
}                                                      # 行 82
```

#### 类型一：自建 Agent —— python 启动，你写的 adapter

**共同特征：`command = sys.executable`，`args` 的第一个元素是 adapter 脚本的绝对路径。**

这三者是**你亲手编写的 adapter 脚本**，直接用 Python 启动，不依赖任何外部工具。它们的特点是：你完全控制内部逻辑，可以调用已有业务模块、数据库、内部 API。

| 维度 | `company-policy` | `demo-reviewer` | `demo-reporter` |
|---|---|---|---|
| adapter 脚本 | `policy_acp_adapter.py` | `demo_acp_agent.py` | `demo_acp_agent.py` |
| 额外参数 | 无 | `--role reviewer` | `--role reporter` |
| 核心功能 | 调用差旅制度模块，核查报销是否符合公司政策 | 规则化输出信息核实结果 | 规则化汇总出差方案 |
| 是否调用 LLM | 内部业务逻辑中可能调用 | 否（纯规则引擎） | 否（纯规则引擎） |
| kind 标签 | `"自建 Agent"` | `"本地演示 Agent"` | `"本地演示 Agent"` |

> 💡 **核心洞见：一脚本多角色复用**
>
> `demo-reviewer` 和 `demo-reporter` 共用同一个脚本 `demo_acp_agent.py`，通过 `--role` 参数区分行为：
>
> ```
> python scripts/demo_acp_agent.py --role reviewer   → 执行信息核实逻辑
> python scripts/demo_acp_agent.py --role reporter   → 执行方案汇总逻辑
> ```
>
> 这种设计降低了维护成本——修改 demo agent 的公共逻辑（如 ACP 协议消息解析）只需改一处。这是 ACP 自建 Agent 的推荐模式：**一个脚本 + 参数驱动 = 多个逻辑角色**。

**为什么 `command = sys.executable` 而不是硬编码 `"python3"`？**

用户机器上的 Python 可能叫 `python`、`python3`、`python3.11`，或在虚拟环境中。`sys.executable` 始终指向**当前正在运行的 Python 解释器的绝对路径**：

```python
# 系统 Python
>>> sys.executable
'/usr/local/bin/python3'

# 虚拟环境
>>> sys.executable
'/Users/dinoschen/.venv/bin/python'
```

使用 `sys.executable` 确保启动子进程时使用**相同的 Python 环境和依赖**——虚拟环境中的包（如 `agent-client-protocol==0.10.1`）在子进程中也可见。如果硬编码 `"python3"`，可能启动系统 Python 而非虚拟环境 Python，导致 `ModuleNotFoundError`。

#### 类型二：外部 Agent 适配器 —— npx 启动，社区维护

**共同特征：`command = "npx"`，`args = ("-y", "@agentclientprotocol/<适配器名>@<版本号>")`。**

这两者是**第三方（社区/厂商）维护的 ACP 适配器**，以 npm 包形式发布在 npm registry 上，通过 `npx` 运行时自动下载安装。

| 维度 | `claude-agent` | `codex` |
|---|---|---|
| npm 包名 | `@agentclientprotocol/claude-agent-acp` | `@agentclientprotocol/codex-acp` |
| 固定版本 | `0.49.0` | `0.0.46` |
| 对应产品 | Claude Agent SDK（Anthropic） | Codex CLI（OpenAI） |
| 实际启动命令 | `npx -y @agentclientprotocol/claude-agent-acp@0.49.0` | `npx -y @agentclientprotocol/codex-acp@0.0.46` |
| 认证方式 | 依赖 Claude CLI 的登录状态 | 依赖 Codex CLI 的登录状态 |
| 模型与计费 | 由 Claude Agent 自身配置管理 | 由 Codex 自身配置管理 |

> ⚠️ **版本号讨论：codex 0.0.46 vs 1.0.0**
>
> 课堂上使用 `codex-acp@0.0.46` 作为固定版本。老师指出，npm 上当日已有 `1.0.0` 版本发布，但**升级前必须重新验证**。以下是原因：
>
> | 考虑因素 | 说明 |
> |---|---|
> | **语义化版本** | `0.0.46 → 1.0.0` 是主版本号跳跃，意味着 API 可能不向后兼容 |
> | **启动方式** | 1.0.0 的命令行参数格式可能与 0.0.46 不同，args 元组需重新确认 |
> | **环境要求** | 新版本可能要求更高版本的 Node.js 或新的系统依赖 |
> | **行为变化** | 默认行为、超时策略、错误处理方式可能改变 |
>
> 在教学中固定版本号（而非使用 `@latest`）是生产环境的正确做法——避免随上游自动更新而引入不可预期的行为变化。如果要升级，正确流程是：**在新分支上测试 → 验证全部 agent 可用 → 更新 AgentSpec 中的版本号 → 合并**。决不直接在主干改版本号。

#### 类型三：网关桥接 Agent —— openclaw 启动，嵌套代理

**特征：`command = "openclaw"`，`args = ("acp",)`。**

与 npx 类型的适配器不同，**OpenClaw 本身就是一套完整的多 Agent 网关调度系统**。当它以 `openclaw acp` 启动时，OpenClaw Gateway 作为一个 ACP Agent 端，监听来自主调度器的任务。

| 字段 | 值 | 解释 |
|---|---|---|
| `command` | `"openclaw"` | OpenClaw Gateway 的 CLI 入口。需预先安装 OpenClaw |
| `args` | `("acp",)` | `acp` 是子命令，表示以 ACP 协议模式启动。OpenClaw 支持多种协议模式，`acp` 是其中之一 |
| `kind` | `"网关桥接 Agent"` | 与"外部 Agent 适配器"的区别：适配器只桥接单个外部 Agent；网关可以桥接其管辖下的**多个 Agent**，并在内部做二次调度 |
| `note` | `"通过 OpenClaw Gateway 承接 ACP 会话"` | 强调 OpenClaw 是任务接收方——它收到 ACP 任务后可以继续分发给内部的子 Agent |

这形成了一种**嵌套代理（Nested Delegation）**架构：

```
┌──────────────────────────────────────┐
│         主调度器（acp_client.py）       │
│         run_acp_task("openclaw",...)   │
└────────────────┬─────────────────────┘
                 │ ACP 协议
                 ▼
┌──────────────────────────────────────┐
│    OpenClaw Gateway（ACP Agent 端）    │
│    command: openclaw acp              │
│    ┌──────────┐  ┌──────────┐        │
│    │ 子Agent A │  │ 子Agent B │  ...   │
│    └──────────┘  └──────────┘        │
└──────────────────────────────────────┘
```

> 💡 **核心洞见**：ACP 协议的设计不关心 Agent 端的内部结构。Agent 端可以是一个单体 Agent，也可以是一个完整的 Agent 调度系统。这种**分层抽象**是 ACP 被 Amazon 和 OpenClaw 内部采用的核心原因——你可以把一整个 Agent 集群当作一个 ACP endpoint 暴露出去，调用方完全不需要知道内部有多少个子 Agent。

---

### 3.4 🔀 npx 启动机制与 MCP 类比

#### npx 是什么

`npx` 是 npm（Node Package Manager）自带的包执行器。它的核心价值在于**不需要全局安装就能直接运行 npm 包**。这在 ACP 生态中至关重要——你不需要先 `npm install -g @agentclientprotocol/claude-agent-acp`，一行命令即可启动。

```
npx -y @agentclientprotocol/claude-agent-acp@0.49.0
 │   │  │
 │   │  └── npm 包名 + 精确版本号（@scope/package-name@version）
 │   └── -y 标志：自动确认（--yes），跳过"是否安装?"的交互式提示
 └── npx 命令：Node Package Execute
```

#### 📖 三步一体：下载 → 安装 → 启动

老师特别强调"装完它就给你启动了"——npx 的一体化执行流程是整个 ACP 外部适配器设计的基础。当执行 `npx -y @agentclientprotocol/claude-agent-acp@0.49.0` 时：

```
┌─────────────────────────────────────────────────────┐
│  Step 1: 检查本地 npx 缓存                            │
│  npx 检查 ~/.npm/_npx/ 目录下是否已有此版本的包         │
│  ├── 缓存命中 → 跳过下载，直接使用缓存版本               │
│  └── 缓存未命中 → 进入 Step 2                          │
├─────────────────────────────────────────────────────┤
│  Step 2: 从 npm registry 下载指定版本的包               │
│  向 registry.npmjs.org 发送请求                        │
│  下载 .tgz 压缩包并解压到临时目录                        │
│  安装包的依赖（dependencies）                           │
├─────────────────────────────────────────────────────┤
│  Step 3: 执行包的入口文件                              │
│  读取 package.json 的 "bin" 字段确定入口脚本            │
│  启动 Node.js 进程，执行 ACP adapter                   │
│  adapter 开始监听 stdin/stdout 上的 ACP 协议消息        │
│  adapter 持续运行，直到父进程关闭连接或发送 cancel        │
└─────────────────────────────────────────────────────┘
```

> 💡 **核心洞见**：npx 的"一体化"特性正是 ACP 生态选择它作为分发渠道的原因。开发者只需在 AgentSpec 中配置一行 `args=("-y", "@agentclientprotocol/codex-acp@0.0.46")`，调度器启动时自动完成下载、安装、启动全过程。这是**零配置部署**在 Agent 生态中的应用。

#### 🔀 command + args 设计模式类比 MCP stdio transport

如果你学过 MCP（Model Context Protocol），会发现 AgentSpec 的 `command + args` 模式与 MCP 的 stdio transport 结构几乎完全一致：

| 维度 | MCP stdio transport | ACP AgentSpec |
|---|---|---|
| 启动命令字段 | `command`（如 `"npx"`、`"uvx"`、`"python"`） | `command`（如 `"npx"`、`sys.executable`、`"openclaw"`） |
| 启动参数字段 | `args`（如 `["-y", "@modelcontextprotocol/server-filesystem"]`） | `args`（如 `("-y", "@agentclientprotocol/codex-acp@0.0.46")`） |
| 通信通道 | 子进程的 stdin/stdout 传输 JSON-RPC 消息 | 子进程的 stdin/stdout 传输 ACP 协议消息 |
| 进程生命周期 | 父进程 spawn 子进程 → 通信 → 父进程关闭时终止子进程 | 完全相同的模式 |
| 注册配置 | MCP server 配置 JSON → Host 启动时读取 | AGENT_MATRIX 字典 → 调度器运行时读取 |
| 语言无关性 | Server 可用任何语言实现，只要遵守 stdio 协议 | Agent 可用任何语言实现，只要遵守 ACP 协议 |

这不是巧合。ACP 和 MCP 都遵循了** Unix 哲学中的"管道"思想**——通过子进程的标准输入输出进行结构化的消息传递。这使得协议实现方可以用任何编程语言编写 adapter，只要遵循协议的消息格式即可。对于调度器来说，启动一个 Python 写的自建 Agent 和启动一个 Node.js 写的 npx 适配器，底层都是 `asyncio.create_subprocess_exec(command, *args)`，完全透明。

> 🔗 **前置知识**：MCP stdio transport 的详细讨论见 [第 10-11 章：MCP协议与生态探讨]

---

### 3.5 ✅ launcher_available() 验证与 launch_line 展示

#### launcher_available() 方法：检查启动器是否已安装

```python
def launcher_available(self) -> bool:                    # 行 22
    """只检查启动器是否可见，不代表账号、网络和认证已经就绪。"""  # 行 23
    if Path(self.command).is_file():                     # 行 24
        return True                                      # 行 25
    return shutil.which(self.command) is not None        # 行 26
```

| 行号 | 代码 | 解释 |
|---|---|---|
| 22 | `def launcher_available(self) -> bool:` | 方法签名，返回布尔值。方法名用 `launcher_available` 而非 `is_available`，强调检查的是"启动器"而非"Agent 整体" |
| 23 | `"""只检查启动器是否可见..."""` | **关键 disclaimer**：明确告知调用方，返回 `True` 不代表 Agent 一定能正常工作。认证过期、网络不通、API key 无效都不会被检测到 |
| 24 | `if Path(self.command).is_file():` | 先判断 command 是否为文件路径。自建 Agent 的 command 是 `sys.executable`（如 `/usr/local/bin/python3`），这是一个文件路径，直接用 `Path.is_file()` 检查 |
| 25 | `return True` | 文件存在 → 启动器可用。注意这里不检查文件是否可执行——Python 解释器路径默认总是可执行的 |
| 26 | `return shutil.which(self.command) is not None` | 兜底逻辑：对于 `"npx"`、`"openclaw"` 这类在 PATH 中的命令名，使用 `shutil.which` 搜索。`which` 遍历 PATH 环境变量的所有目录，找到第一个匹配的可执行文件，返回其绝对路径；找不到返回 `None` |

**检查逻辑决策树：**

```
launcher_available() 被调用
    │
    ├── self.command 是一个存在的文件？
    │   ├── 是 → return True
    │   │   适用：自建 Agent（command = /usr/local/bin/python3）
    │   │         Python 是操作系统的一部分或通过包管理器安装
    │   │
    │   └── 否 → 进入 shutil.which 检查
    │
    └── shutil.which(self.command) 在 PATH 中找到？
        ├── 是 → return True
        │   适用：claude-agent（command = npx）、codex（command = npx）、openclaw（command = openclaw）
        │
        └── 否 → return False
            命令未安装或未加入 PATH
```

> 🐞 **常见坑**：用户安装了 claude CLI 但 `launcher_available()` 返回 `False`。原因通常是安装路径未加入 PATH 环境变量。
>
> **排查步骤**：
> ```bash
> # 1. 直接在终端验证
> which claude        # 预期输出: /usr/local/bin/claude 或类似路径
> which npx           # 预期输出: /usr/local/bin/npx
> which openclaw      # 预期输出: /path/to/openclaw
>
> # 2. 如果找不到，查找安装位置
> find / -name "claude" -type f 2>/dev/null
>
> # 3. 将安装目录加入 PATH（添加到 ~/.zshrc 或 ~/.bashrc）
> export PATH="/path/to/claude/bin:$PATH"
> source ~/.zshrc
> ```

#### launch_line property：生成可移植的命令展示

```python
@property                                               # 行 28
def launch_line(self) -> str:                           # 行 29
    """用于讲义展示的可移植命令，不暴露当前机器的绝对路径。"""  # 行 30
    if self.command == sys.executable and self.args:    # 行 31
        script = Path(self.args[0])                     # 行 32
        if script.parent == SCRIPT_DIR:                 # 行 33
            display_args = (f"scripts/{script.name}", *self.args[1:])  # 行 34
            return " ".join(("python", *display_args))  # 行 35
    return " ".join((self.command, *self.args))         # 行 36
```

| 行号 | 代码 | 解释 |
|---|---|---|
| 28 | `@property` | 装饰器将方法转为属性访问。调用方写 `spec.launch_line` 而非 `spec.launch_line()`。语义上，launch_line 更像"Agent 的一个属性"而非"需计算的操作" |
| 29 | `def launch_line(self) -> str:` | 返回一个可直接在终端执行的命令字符串 |
| 30 | `"""...不暴露当前机器的绝对路径。"""` | **设计意图**：教学文档中的命令应该可移植——展示 `python scripts/xxx.py` 而非 `python /Users/dinoschen/.../scripts/xxx.py`，后者暴露了作者机器的用户名和路径结构 |
| 31 | `if self.command == sys.executable and self.args:` | 两个条件：command 是当前 Python 解释器（即自建 Agent），且 args 非空。外部适配器（npx）和网关（openclaw）走兜底逻辑 |
| 32 | `script = Path(self.args[0])` | 提取 args 的第一个元素（adapter 脚本的绝对路径），包装为 Path 对象以便后续操作 |
| 33 | `if script.parent == SCRIPT_DIR:` | **防御性检查**：确认脚本确实在 `agent_registry.py` 的同一目录下。如果不在此目录，说明 args 配置可能有问题，不进行美化 |
| 34 | `display_args = (f"scripts/{script.name}", *self.args[1:])` | 将绝对路径 `"/Users/.../scripts/demo_acp_agent.py"` 替换为可移植格式 `"scripts/demo_acp_agent.py"`，然后用 `*self.args[1:]` 展开后续参数（如 `"--role"`, `"reviewer"`） |
| 35 | `return " ".join(("python", *display_args))` | 最终拼接：`"python scripts/demo_acp_agent.py --role reviewer"`。注意这里用的是 `"python"` 而非 `sys.executable`，因为讲义读者可能用不同 Python 版本，`python` 是通用命令名 |
| 36 | `return " ".join((self.command, *self.args))` | 兜底：外部 Agent（npx）和网关（openclaw）的 command 本身就是可移植的命令名，直接拼接输出即可 |

**各 Agent 的 launch_line 实际输出：**

| Agent | launch_line 输出 | 说明 |
|---|---|---|
| `company-policy` | `python scripts/policy_acp_adapter.py` | 绝对路径被替换为 `scripts/xxx.py` |
| `demo-reviewer` | `python scripts/demo_acp_agent.py --role reviewer` | 路径替换 + 保留额外参数 |
| `demo-reporter` | `python scripts/demo_acp_agent.py --role reporter` | 同上，仅 `--role` 值不同 |
| `claude-agent` | `npx -y @agentclientprotocol/claude-agent-acp@0.49.0` | 直接拼接，本身就是可移植的 |
| `codex` | `npx -y @agentclientprotocol/codex-acp@0.0.46` | 直接拼接 |
| `openclaw` | `openclaw acp` | 直接拼接 |

> 💡 **核心洞见**：`launch_line` 的设计体现了"文档即代码"的理念。教学文档中展示的命令和实际执行的命令是同一个来源——AgentSpec。如果未来版本号变化，只需改 AgentSpec 的 `args`，文档中展示的命令自动同步更新，避免文档与实际代码脱节。

---

### 3.6 📝 本节小结

#### 🗺️ 知识图谱

```
                    ┌─────────────────────────────┐
                    │     AgentSpec（数据基石）      │
                    │  name / command / args       │
                    │  kind / note                 │
                    │  launcher_available()        │
                    │  launch_line                 │
                    └─────────────┬───────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │   自建 Agent      │ │  外部适配器       │ │  网关桥接         │
    │ command=python   │ │ command=npx      │ │ command=openclaw │
    ├─────────────────┤ ├─────────────────┤ ├─────────────────┤
    │ company-policy   │ │ claude-agent    │ │ openclaw        │
    │ demo-reviewer    │ │ codex           │ │                 │
    │ demo-reporter    │ │                 │ │                 │
    └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
             │                   │                   │
             └───────────────────┼───────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────────┐
                    │       AGENT_MATRIX           │
                    │  dict[str, AgentSpec]        │
                    │  注册表模式：定义与使用分离       │
                    └─────────────────────────────┘
```

#### 💡 一句话总结

> AgentSpec 五字段不可变数据类是 ACP Agent 的统一配置格式；AGENT_MATRIX 注册表将自建、外部适配器、网关桥接三种 Agent 类型集中管理；npx 的下载-安装-启动一体化机制让外部适配器的部署成本降为零；command+args 设计与 MCP stdio transport 同源，遵循 Unix 管道哲学。

#### 关键概念速查表

| 概念 | 一句话 | 出现位置 |
|---|---|---|
| `AgentSpec` | 五字段不可变数据类，Agent 配置的统一格式 | `@dataclass(frozen=True)` |
| `sys.executable` | 当前 Python 解释器绝对路径，用于自建 Agent 的 command | `command=sys.executable` |
| `SCRIPT_DIR` | 脚本目录绝对路径，确保跨工作目录引用 adapter | `Path(__file__).resolve().parent` |
| `AGENT_MATRIX` | 注册表字典，6 种 Agent 按三种类型分类 | `dict[str, AgentSpec]` |
| `npx -y` | npm 包执行器 + 自动确认，下载-安装-启动一体化 | `command="npx"` |
| `launcher_available()` | 检查启动器命令是否可用，不检查认证 | `shutil.which()` |
| `launch_line` | 生成可移植命令字符串，隐藏机器特定路径 | `@property` |
| 固定版本号 | 教学/生产环境锁定版本，避免上游更新引入意外 | `@0.0.46`、`@0.49.0` |

> 📍 **系列定位**：本文是「Agent 架构师企业级智能体系统构建」第 3 篇。
> - 上一篇：多Agent协作概念与ACP协议引入 — 理解 ACP 是什么、为什么需要它
> - 下一篇：ACP 生命周期与最小 Demo Agent — 深入 adapter 内部实现，手写第一个 ACP Agent

> 🔗 **延伸阅读**：本文注册的 AgentSpec 配置将在 [第 5 章：ACP Client 任务分发实现] 中被 `run_acp_task()` 函数消费，在 [第 6 章：DAG 编排与任务委托] 中被 DAG 调度引擎引用

---

> 🤖 由 transcript-to-doc v4.1 生成 — M03-ACP-Agent注册与配置体系

## 四、ACP 生命周期与最小 Demo Agent

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 画出 ACP 一次委派的完整生命周期时序图（4 个阶段）
> - [ ] 逐行理解 `demo_acp_agent.py` 的每一段代码
> - [ ] 说出 `initialize` / `new_session` / `prompt` 三个方法的职责与返回值
> - [ ] 阐明 `PromptBlock` 联合类型的 5 种子类型及其设计意图
> - [ ] 解释 `session_id` 如何实现多轮对话持久化
> - [ ] 区分 `reviewer` 与 `reporter` 两种角色的 `render_reply` 输出逻辑

---

### 4.1 ACP 生命周期概览

#### 🧠 直观理解

一次 ACP 委派就像你去柜台办事：先确认柜台有人在（Initialize），再开一个工单（New Session），然后提交你的需求（Prompt），最后拿到结果（Response）。如果中途反悔，可以随时取消工单（Cancel）。整个过程是有状态的——同一个工单号（session_id）下你可以追加补充材料，柜员记得之前你说了什么。

#### 📖 详细解释

ACP（Agent Communication Protocol）是 Claude Code 生态中 Client 与 Agent 之间的通信协议。一次完整的委派经历四个阶段：

| 阶段 | 方法 | 谁发起 | 作用 | 返回值 |
|---|---|---|---|---|
| 1. 握手协商 | `initialize()` | Client → Agent | 确认 Agent 存在，交换能力和版本信息 | `InitializeResponse` |
| 2. 创建会话 | `new_session()` | Client → Agent（可选） | 创建一个新的上下文容器，返回 session_id | `NewSessionResponse` |
| 3. 任务发送 | `prompt()` | Client → Agent | 将用户任务以 PromptBlock 列表形式发送 | `PromptResponse` |
| 4. 中断取消 | `cancel()` | Client → Agent（可选） | 中止当前正在执行的任务 | — |

> 💡 **核心洞见**：老师强调"主流程就是一发送任务，然后这边直接给你返回一个任务结果"。权限请求（permission request）和中断（interrupt）只是中间过程，理解整体骨架时可以先忽略。

#### 🔄 执行流程（ASCII 时序图）

```
Client (Host)                              Agent (DemoAcpAgent)
    │                                            │
    │  ① initialize(protocol_version,            │
    │     client_capabilities, client_info)       │
    │ ─────────────────────────────────────────▶ │
    │                                            │ 验证自身存在，返回能力信息
    │         InitializeResponse(                │
    │           protocol_version,                 │
    │           agent_info=Implementation(...)     │
    │         )                                   │
    │ ◀───────────────────────────────────────── │
    │                                            │
    │  ② new_session(cwd,                        │
    │     additional_directories, mcp_servers)    │
    │ ─────────────────────────────────────────▶ │
    │                                            │ 创建新会话容器
    │         NewSessionResponse(                 │
    │           session_id="a3f2b1c4..."          │
    │         )                                   │
    │ ◀───────────────────────────────────────── │
    │                                            │
    │  ③ prompt(                                 │
    │     prompt=[TextContentBlock(...), ...],    │
    │     session_id="a3f2b1c4..."                │
    │     )                                      │
    │ ─────────────────────────────────────────▶ │
    │                                            │ 处理 prompt → session_update
    │                                            │ → 生成回复
    │         PromptResponse(                     │
    │           stop_reason="end_turn"            │
    │         )                                   │
    │ ◀───────────────────────────────────────── │
    │                                            │
    │  【多轮对话：复用同一个 session_id          │
    │   再次调用 prompt()，Agent 能回想上文】      │
    │                                            │
    │  ④ cancel(session_id=...)  ← 可选           │
    │ ─────────────────────────────────────────▶ │
    │                                            │ 中止当前任务
    │ ◀───────────────────────────────────────── │
    │                                            │
```

> ⚠️ **注意事项**：`new_session()` 是可选的——Client 可以多次调用 `prompt()` 并向同一个 `session_id` 追加任务。但如果选择了 `new_session()`，就会启动一个全新的上下文。这与 Claude Code 侧边栏中每个对话拥有独立 session 的机制完全一致。

> 🔗 **与多轮对话的关系**：有同学在课中提问"持续多轮交互可以维持这种有状态的多轮交互吗？"——答案就在于 `session_id`。同一个 `session_id` 下的所有 `prompt()` 调用共享同一段会话历史，Agent 可以通过 `session_update` 持久化每一轮的对话记录。（详见 [4.5 Session 与多轮对话机制](#45-session-与多轮对话机制)）

---

### 4.2 DemoAcpAgent 实现逐方法详解

#### 🎯 目标

逐行解析 `demo_acp_agent.py` 的完整实现，这是 ACP 协议下**最简原型 Agent**。它不调用真实大模型，而是通过规则化输出演示协议骨架。理解它之后，你就可以替换其中的 `render_reply()` 为真正的 LLM 调用逻辑。

#### 🏗️ 前置准备

- Python 3.10+
- `acp` 包已安装（通过 `pip install acp` 或课程环境预装）
- 理解 ACP 协议的基本概念（见 [4.1 ACP 生命周期概览](#41-acp-生命周期概览)）

#### 💻 Step-by-Step

**完整代码一览：**

```python
# 文件名: demo_acp_agent.py
# 功能: ACP 最小原型 Agent — 规则化回复，不调用大模型

from __future__ import annotations

import argparse
import asyncio
import re
from typing import Any, cast
from uuid import uuid4

from acp import (
    Agent,
    InitializeResponse,
    NewSessionResponse,
    PromptResponse,
    run_agent,
    text_block,
    update_agent_message,
)
from acp.interfaces import Client
from acp.schema import (
    AudioContentBlock,
    ClientCapabilities,
    EmbeddedResourceContentBlock,
    HttpMcpServer,
    ImageContentBlock,
    Implementation,
    McpServerStdio,
    ResourceContentBlock,
    SseMcpServer,
    TextContentBlock,
)

PromptBlock = (
    TextContentBlock
    | ImageContentBlock
    | AudioContentBlock
    | ResourceContentBlock
    | EmbeddedResourceContentBlock
)
McpServer = HttpMcpServer | SseMcpServer | McpServerStdio


def render_reply(role: str, prompt: str) -> str:
    if role == "reviewer":
        return (
            "信息核实结果：\n"
            "- 出行日期与目的地已记录\n"
            "- 天气、景区开放时间、市内交通方式需由实时检索核实\n"
            "- 仍缺：精确到当天的开放时间和票价\n"
            f"- 本次收到的任务摘要：{prompt[:100]}"
        )
    node_ids = list(dict.fromkeys(re.findall(r"\[(n\d+_[^\]]+)\]", prompt)))
    received = "、".join(node_ids) if node_ids else "未提供"
    policy_status = "已收到" if "制度核查" in prompt else "未收到"
    facts_status = "已收到" if "信息核实" in prompt else "未收到"
    return (
        "出差方案复核摘要：行程与预算可进入人工确认；正式提交前需落实"
        "交通限额、餐补标准和审批人。\n"
        f"已接收上游节点：{received}\n"
        f"汇总检查：差旅制度={policy_status}；信息核实={facts_status}"
    )


class DemoAcpAgent:
    _client: Client

    def __init__(self, role: str) -> None:
        self._role = role

    def on_connect(self, conn: Client) -> None:
        self._client = conn

    async def initialize(
        self,
        protocol_version: int,
        client_capabilities: ClientCapabilities | None = None,
        client_info: Implementation | None = None,
        **kwargs: Any,
    ) -> InitializeResponse:
        return InitializeResponse(
            protocol_version=protocol_version,
            agent_info=Implementation(
                name=f"demo-{self._role}",
                title=f"本地演示 Agent（{self._role}）",
                version="0.1.0",
            ),
        )

    async def new_session(
        self,
        cwd: str,
        additional_directories: list[str] | None = None,
        mcp_servers: list[McpServer] | None = None,
        **kwargs: Any,
    ) -> NewSessionResponse:
        return NewSessionResponse(session_id=uuid4().hex)

    async def prompt(
        self,
        prompt: list[PromptBlock],
        session_id: str,
        **kwargs: Any,
    ) -> PromptResponse:
        prompt_text = "\n".join(
            block.text for block in prompt if isinstance(block, TextContentBlock)
        )
        await self._client.session_update(
            session_id=session_id,
            update=update_agent_message(text_block(render_reply(self._role, prompt_text))),
        )
        return PromptResponse(stop_reason="end_turn")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=("reviewer", "reporter"), required=True)
    args = parser.parse_args()
    await run_agent(cast(Agent, DemoAcpAgent(args.role)))


if __name__ == "__main__":
    asyncio.run(main())
```

---

**Step 1: 导入与类型定义（第 1-39 行）**

```python
from __future__ import annotations          # 启用 PEP 604 联合类型语法 X | Y

import argparse                             # 命令行参数解析
import asyncio                              # 异步 I/O 事件循环
import re                                   # 正则表达式（用于 render_reply 中提取节点 ID）
from typing import Any, cast                # 类型标注工具
from uuid import uuid4                      # 生成唯一 session_id

from acp import (                           # ACP 协议核心 API
    Agent,                                  # Agent 的接口基类（类型标注用）
    InitializeResponse,                     # initialize() 的返回类型
    NewSessionResponse,                     # new_session() 的返回类型
    PromptResponse,                         # prompt() 的返回类型
    run_agent,                              # 启动 Agent 事件循环的入口函数
    text_block,                             # 构造文本内容块的工厂函数
    update_agent_message,                   # 构造会话更新的工厂函数
)
from acp.interfaces import Client           # Client 连接对象，用于推送 session_update
from acp.schema import (                    # ACP 协议的 Schema 定义
    AudioContentBlock,                      # 音频内容块
    ClientCapabilities,                     # 客户端能力声明
    EmbeddedResourceContentBlock,           # 内嵌资源内容块
    HttpMcpServer,                          # MCP Server（HTTP 传输）
    ImageContentBlock,                      # 图片内容块
    Implementation,                         # Agent/Client 的元信息描述
    McpServerStdio,                         # MCP Server（stdio 传输）
    ResourceContentBlock,                   # 资源引用内容块
    SseMcpServer,                           # MCP Server（SSE 传输）
    TextContentBlock,                       # 文本内容块（最常用）
)
```

**联合类型定义（第 32-39 行）：**

```python
PromptBlock = (
    TextContentBlock
    | ImageContentBlock
    | AudioContentBlock
    | ResourceContentBlock
    | EmbeddedResourceContentBlock
)
McpServer = HttpMcpServer | SseMcpServer | McpServerStdio
```

> 💡 **核心洞见**：`PromptBlock` 是一个**联合类型（Union Type）**，这意味着 `prompt()` 方法接收的 `prompt` 参数是一个列表，列表中每个元素可以是 5 种内容块之一。ACP 协议从设计之初就不仅仅支持纯文本传输——音频、图片、内嵌资源都可以作为 prompt 的一部分。这是 ACP 区别于传统纯文本协议的关键设计。

| 行号 | 代码 | 解释 |
|---|---|---|
| 1 | `from __future__ import annotations` | 启用延迟求值注解，允许使用 `X \| Y` 语法替代 `Union[X, Y]` |
| 9-17 | `from acp import ...` | 导入 ACP 协议核心 API：Agent 接口、三种 Response 类型、启动函数、内容块工厂函数 |
| 18 | `from acp.interfaces import Client` | Client 是 Agent 与外部通信的桥梁，Agent 通过它向 Client 推送 session_update |
| 19-30 | `from acp.schema import ...` | 导入所有 Schema 类型——这些是 ACP 协议的数据结构定义 |
| 32-38 | `PromptBlock = ...` | 定义 PromptBlock 联合类型，描述 prompt 可以包含的 5 种内容块 |
| 39 | `McpServer = ...` | 定义 MCP Server 联合类型，描述支持的 3 种 MCP 传输方式 |

---

**Step 2: DemoAcpAgent 类结构与 on_connect()（第 63-70 行）**

```python
class DemoAcpAgent:
    _client: Client                          # 持有 Client 连接对象的引用

    def __init__(self, role: str) -> None:   # 构造时传入角色：reviewer 或 reporter
        self._role = role

    def on_connect(self, conn: Client) -> None:  # Client 连接建立时回调
        self._client = conn                      # 保存 Client 引用，后续用于 session_update
```

> 🧠 **直观理解**：`on_connect()` 就像电话接通的那一瞬间——Agent 拿到了与 Client 通信的"话筒"（`self._client`）。之后 Agent 想要向 Client 推送消息（比如会话更新），就必须通过这个话筒。

> 📖 **详细解释**：`on_connect()` 是 ACP 协议中 Client 与 Agent 连接建立后触发的第一个回调。在这个方法中，Agent 必须保存 `conn: Client` 引用，因为后续的 `prompt()` 方法需要通过 `self._client.session_update()` 主动向 Client 推送会话状态变更。这是 Agent 作为服务端向 Client 推送数据的唯一通道。

| 行号 | 代码 | 解释 |
|---|---|---|
| 63 | `class DemoAcpAgent:` | Agent 主类，隐含实现了 ACP 的 Agent 协议接口（通过鸭子类型） |
| 64 | `_client: Client` | 类属性类型标注，存储 Client 连接对象的引用 |
| 66 | `def __init__(self, role: str) -> None:` | 构造函数，`role` 参数决定 Agent 的行为角色（reviewer 或 reporter） |
| 69 | `def on_connect(self, conn: Client) -> None:` | 连接建立回调，ACP 框架在 Client 连接建立后自动调用 |
| 70 | `self._client = conn` | 保存 Client 引用——这是 Agent 后续向 Client 推送消息的唯一途径 |

---

**Step 3: initialize() 握手协商（第 72-86 行）**

```python
    async def initialize(
        self,
        protocol_version: int,                              # Client 提议的协议版本号
        client_capabilities: ClientCapabilities | None = None,  # Client 能力声明
        client_info: Implementation | None = None,              # Client 身份信息
        **kwargs: Any,                                      # 兼容未来扩展参数
    ) -> InitializeResponse:
        return InitializeResponse(
            protocol_version=protocol_version,              # 回显 Client 的协议版本（表示兼容）
            agent_info=Implementation(                      # 构造 Agent 身份信息
                name=f"demo-{self._role}",                  # Agent 的唯一标识名
                title=f"本地演示 Agent（{self._role}）",     # Agent 的人类可读标题
                version="0.1.0",                            # Agent 的语义版本号
            ),
        )
```

> 🧠 **直观理解**：`initialize()` 就是 Client 和 Agent 的"握手"阶段。Client 说"我是谁、我能做什么、我用哪个协议版本"，Agent 回复"好的，我存在，我是谁，我也用这个版本"。

> 📖 **详细解释**：`initialize()` 方法有三个入参，但在这个最小原型中，Agent 只使用了 `protocol_version` 来原样回传（表示与 Client 使用同一协议版本），并忽略 `client_capabilities` 和 `client_info`。实际生产级 Agent 应该根据 `client_capabilities` 来决定启用哪些高级特性。

`Implementation` 对象有三个关键字段：

| 字段 | 示例值 | 含义 |
|---|---|---|
| `name` | `"demo-reviewer"` | Agent 的唯一标识名，用于注册和查找（对应 M03 中 AgenticSpec 的 name） |
| `title` | `"本地演示 Agent（reviewer）"` | 人类可读的标题，用于 UI 展示 |
| `version` | `"0.1.0"` | 语义版本号，用于版本兼容性检查 |

| 行号 | 代码 | 解释 |
|---|---|---|
| 72 | `async def initialize(self, ...)` | 异步方法，ACP 框架在 Client 连接后自动调用 |
| 73 | `protocol_version: int` | Client 提议的协议版本号（如版本 1） |
| 74 | `client_capabilities: ClientCapabilities \| None = None` | Client 的功能声明（如是否支持流式、是否支持图片等） |
| 79 | `return InitializeResponse(...)` | 返回初始化响应——这是握手的关键 |
| 80 | `protocol_version=protocol_version` | 直接回传 Client 版本号，表示"我兼容你的版本" |
| 81-85 | `agent_info=Implementation(...)` | 构造 Agent 的元信息，三个字段均为必填 |

---

**Step 4: new_session() 创建会话（第 88-95 行）**

```python
    async def new_session(
        self,
        cwd: str,                                               # Client 的当前工作目录
        additional_directories: list[str] | None = None,        # 额外授权目录列表
        mcp_servers: list[McpServer] | None = None,             # 可用的 MCP Server 列表
        **kwargs: Any,
    ) -> NewSessionResponse:
        return NewSessionResponse(session_id=uuid4().hex)        # 生成一个 32 位十六进制 session_id
```

> 🧠 **直观理解**：`new_session()` 就是开一张"工单"——返回一个唯一的工单号（session_id），后续所有操作都挂在同一个工单号下面。

> 📖 **详细解释**：这是 ACP 最简 prototype 的 `new_session()` 实现——它完全忽略 `cwd`、`additional_directories`、`mcp_servers` 这三个参数，只做一件事：生成一个全局唯一的 session_id 并返回。

`uuid4().hex` 生成的是一个 32 位十六进制字符串（如 `"a3f2b1c4d5e6f7a8b9c0d1e2f3a4b5c6"`），基于随机数生成，碰撞概率极低。在生产环境中，Agent 需要在此时创建对应的会话存储结构（内存字典、文件、数据库），将 `session_id` 映射到实际的会话上下文。

> ⚠️ **注意事项**：在这个最小原型的 `new_session()` 中，并没有任何"创建会话存储"的逻辑——它只是生成了一个 ID 并返回。这是因为该 demo 的所有会话更新都直接推送给 Client 侧维护，Agent 侧不需要持久化。在实际工程中，你需要在此方法中创建 `self._sessions[session_id] = {...}` 这样的数据结构。

| 行号 | 代码 | 解释 |
|---|---|---|
| 88 | `async def new_session(self, ...)` | 异步方法，Client 请求创建新会话时调用 |
| 89 | `cwd: str` | 当前工作目录——为了安全，Agent 只应该在这个目录下操作文件 |
| 90 | `additional_directories: list[str] \| None = None` | 额外授权的目录列表，扩展 Agent 的文件访问范围 |
| 91 | `mcp_servers: list[McpServer] \| None = None` | 会话可用的 MCP Server 列表 |
| 95 | `return NewSessionResponse(session_id=uuid4().hex)` | 最简实现：生成唯一 ID，不做其他任何事 |

---

**Step 5: prompt() 核心执行方法（第 97-110 行）**

```python
    async def prompt(
        self,
        prompt: list[PromptBlock],          # 接收到的用户任务，以内容块列表形式
        session_id: str,                    # 当前会话的唯一标识
        **kwargs: Any,
    ) -> PromptResponse:
        prompt_text = "\n".join(            # 提取所有文本块的内容
            block.text for block in prompt
            if isinstance(block, TextContentBlock)  # 类型收窄：只取文本块
        )
        await self._client.session_update(  # 向 Client 推送会话更新
            session_id=session_id,          # 指定更新哪个会话
            update=update_agent_message(    # 构造一条 Agent 消息更新
                text_block(                 # 构造一个文本内容块
                    render_reply(self._role, prompt_text)  # 调用角色分发函数生成回复
                )
            ),
        )
        return PromptResponse(stop_reason="end_turn")  # 声明本轮处理正常结束
```

> 🧠 **直观理解**：`prompt()` 是 Agent 的心脏。它接收用户消息（可能是文本、图片、音频的混合），从文本部分提取纯文本，生成一条回复，更新到会话里，最后告诉 Client"我这轮处理完了"。

> 📖 **详细解释**：这 14 行代码完成了三个关键动作：

**动作一：提取文本内容（第 103-105 行）**

```python
prompt_text = "\n".join(
    block.text for block in prompt
    if isinstance(block, TextContentBlock)
)
```

`prompt` 参数是一个 `list[PromptBlock]`，其中每个元素可能是文本、图片、音频等 5 种类型之一。这里通过 `isinstance(block, TextContentBlock)` 进行**类型收窄（type narrowing）**，只提取 `TextContentBlock` 的 `.text` 属性，用换行符连接。这是最简 Demo 的做法——真实 Agent 应该处理所有类型的块。

**动作二：更新会话（第 106-109 行）**

```python
await self._client.session_update(
    session_id=session_id,
    update=update_agent_message(text_block(render_reply(self._role, prompt_text))),
)
```

这里有三层嵌套调用，从内到外依次是：
1. `render_reply(self._role, prompt_text)` — 根据角色生成回复文本（纯 Python 函数，见 4.3 节）
2. `text_block(...)` — 将文本包装为 `TextContentBlock`（ACP 的标准内容块格式）
3. `update_agent_message(...)` — 将内容块包装为"Agent 消息更新"（指定这条消息的角色为 agent）
4. `self._client.session_update(...)` — 通过 Client 连接将更新推送到 Client 侧的会话存储

> 💡 **核心洞见**：`session_update` 是 Agent **主动推送**给 Client 的机制。这意味着 Agent 不是被动等待 Client 拉取结果，而是**推式（push-based）**通知 Client"会话有更新"。这使得 Agent 可以在一次 `prompt()` 调用中多次推送更新（如流式输出 token by token）。

**动作三：返回响应（第 110 行）**

```python
return PromptResponse(stop_reason="end_turn")
```

`stop_reason` 告诉 Client 本轮处理结束的原因：

| stop_reason 值 | 含义 | 场景 |
|---|---|---|
| `"end_turn"` | 正常结束 | Agent 完成了本轮推理，等待下一轮 prompt |
| `"max_tokens"` | 达到 Token 上限 | 输出被截断，可能需要 Client 追加 prompt 继续 |
| `"tool_use"` | 需要执行工具 | Agent 在回复中包含了 tool_use 块，等待工具执行结果 |
| `"interrupt"` | 被中断 | Agent 需要用户介入（如权限确认） |

在本 Demo 中，由于没有工具调用且没有 Token 限制，"end_turn" 是唯一合理的返回值。

| 行号 | 代码 | 解释 |
|---|---|---|
| 97 | `async def prompt(self, ...)` | 核心执行方法，由 Client 在发送任务时调用 |
| 98 | `prompt: list[PromptBlock]` | 入参：内容块列表（联合类型），支持多模态 |
| 99 | `session_id: str` | 入参：当前会话 ID |
| 103-105 | `prompt_text = "\n".join(...)` | 从 PromptBlock 列表中提取所有文本块并拼接 |
| 106 | `await self._client.session_update(...)` | 向 Client 推送会话更新（异步 I/O） |
| 107 | `session_id=session_id` | 指定更新的目标会话 |
| 108 | `update=update_agent_message(...)` | 构造 Agent 消息更新对象 |
| 108 | `text_block(render_reply(...))` | 将文本回复包装为 ACP 标准内容块 |
| 110 | `return PromptResponse(stop_reason="end_turn")` | 返回提示响应，声明本轮处理正常结束 |

---

**Step 6: main() 与 run_agent() 启动事件循环（第 113-121 行）**

```python
async def main() -> None:
    parser = argparse.ArgumentParser()                      # 命令行参数解析器
    parser.add_argument("--role", choices=("reviewer", "reporter"), required=True)
    args = parser.parse_args()                              # 解析命令行参数
    await run_agent(cast(Agent, DemoAcpAgent(args.role)))   # 启动 Agent 事件循环

if __name__ == "__main__":
    asyncio.run(main())                                     # 运行异步主函数
```

> 📖 **详细解释**：`run_agent()` 是 ACP 框架提供的入口函数。它接收一个实现了 Agent 协议的对象（通过鸭子类型——只要有 `on_connect`、`initialize`、`new_session`、`prompt` 四个方法即可），然后在内部创建事件循环、监听 Client 连接、分派协议调用。`cast(Agent, ...)` 是类型标注的妥协——`DemoAcpAgent` 并不显式继承 `Agent` 类，但通过 `cast` 告诉类型检查器它满足 `Agent` 接口。

命令行启动示例：

```bash
# 启动 reviewer 角色
python demo_acp_agent.py --role reviewer

# 启动 reporter 角色
python demo_acp_agent.py --role reporter
```

| 行号 | 代码 | 解释 |
|---|---|---|
| 113 | `async def main() -> None:` | 异步主函数 |
| 114 | `parser = argparse.ArgumentParser()` | 创建命令行参数解析器 |
| 115 | `parser.add_argument("--role", ...)` | 定义 --role 参数，仅接受 reviewer 或 reporter |
| 117 | `await run_agent(cast(Agent, DemoAcpAgent(args.role)))` | 核心：启动 Agent 事件循环 |
| 120-121 | `asyncio.run(main())` | Python 异步入口，创建事件循环并运行 main() |

#### ✅ 验证结果

一个最简的 ACP Agent 只需要实现 **4 个方法 + 1 个回调**：

```
DemoAcpAgent
    ├── on_connect(conn)          ← 保存 Client 引用
    ├── initialize(...)            ← 返回协议版本 + Agent 身份
    ├── new_session(...)           ← 返回新 session_id
    └── prompt(...)               ← 提取文本 → 生成回复 → session_update → 返回 end_turn
```

> 💡 **核心洞见**：老师反复强调"最小的原型"——这个 demo agent 不调用真实模型，只用简单的规则化函数（`render_reply`）生成输出。**它的价值在于展示 ACP 协议的骨架**：你需要什么样的方法签名、返回什么样的数据结构、如何通过 `session_update` 推送消息。学会这个骨架之后，把 `render_reply` 替换为真正的 LLM 调用就是一步之遥。

---

### 4.3 render_reply 角色分发逻辑

#### 🧠 直观理解

同一个 Agent 类，通过构造时传入不同的 `role` 参数，展现出完全不同的行为。这就像同一个演员（Agent），拿到不同的剧本（role），演出不同的角色。在 ACP 中，这体现了**一个 Agent 实现可以服务多种业务角色**的灵活性。

#### 📖 详细解释

`render_reply(role, prompt)` 是一个纯函数（无副作用），根据 `role` 参数分发到两种不同的输出模板：

**角色一：reviewer（信息核实员）**

```python
if role == "reviewer":
    return (
        "信息核实结果：\n"
        "- 出行日期与目的地已记录\n"
        "- 天气、景区开放时间、市内交通方式需由实时检索核实\n"
        "- 仍缺：精确到当天的开放时间和票价\n"
        f"- 本次收到的任务摘要：{prompt[:100]}"
    )
```

reviewer 的输出是一个**结构化的核实清单**——它不是在回答用户的问题，而是在告诉用户"我收到了什么信息、我还需要什么信息"。这种模式常见于多 Agent 协作中的"前置审查"角色。

**角色二：reporter（汇总报告员，默认）**

```python
node_ids = list(dict.fromkeys(re.findall(r"\[(n\d+_[^\]]+)\]", prompt)))
received = "、".join(node_ids) if node_ids else "未提供"
policy_status = "已收到" if "制度核查" in prompt else "未收到"
facts_status = "已收到" if "信息核实" in prompt else "未收到"
return (
    "出差方案复核摘要：行程与预算可进入人工确认；正式提交前需落实"
    "交通限额、餐补标准和审批人。\n"
    f"已接收上游节点：{received}\n"
    f"汇总检查：差旅制度={policy_status}；信息核实={facts_status}"
)
```

reporter 的输出更复杂——它会：
1. 使用正则 `r"\[(n\d+_[^\]]+)\]"` 从 prompt 中提取上游节点 ID（格式如 `[n01_xxx]`）
2. 用 `dict.fromkeys()` 去重（保留了插入顺序）
3. 检查 prompt 中是否包含"制度核查"和"信息核实"关键词
4. 生成一个包含"已接收节点"和"汇总检查"的完整报告

> 💡 **核心洞见**：这种以 key 词匹配 + 正则提取为核心的规则化 Agent 设计，在工作流编排场景中非常实用。它不需要大模型推理，运行速度快、结果确定、零成本——尤其适合作为多 Agent 流水线中的"质检节点"或"汇总节点"。

#### 🔀 reviewer vs reporter 对比表

| 维度 | reviewer（核实员） | reporter（报告员，默认） |
|---|---|---|
| 触发条件 | `role == "reviewer"` | `role != "reviewer"`（即 reporter） |
| 输出风格 | 清单式核实结果 | 结构化汇总报告 |
| 正则提取 | 无 | 提取 `[n01_xxx]` 格式的上游节点 ID |
| 关键词检测 | 无 | 检测"制度核查"和"信息核实" |
| 业务语义 | "我收到了什么，我还缺什么" | "已接收哪些节点，各模块状态如何" |
| 适用场景 | 前置校验、信息完整性检查 | 多节点结果汇总、终审报告生成 |

---

### 4.4 PromptBlock 信息结构

#### 🧠 直观理解

ACP 不假设用户只发文本。PromptBlock 是一个"万能信封"——可以装文本、图片、音频，甚至内嵌资源引用。就像快递包裹可以是文件、衣服、食品，但都装在同一个快递系统里传输。

#### 📖 详细解释

`PromptBlock` 是一个**联合类型（Union Type / Discriminated Union）**，在代码中定义为：

```python
PromptBlock = (
    TextContentBlock            # 纯文本内容
    | ImageContentBlock         # 图片内容（支持 base64 和 URL）
    | AudioContentBlock         # 音频内容
    | ResourceContentBlock      # 资源引用（如文件路径、URI）
    | EmbeddedResourceContentBlock  # 内嵌资源（如 PDF 正文）
)
```

五种类型的详细说明：

| 类型 | 主要属性 | 使用场景 | 在本 Demo 中的处理 |
|---|---|---|---|
| `TextContentBlock` | `.text: str` | 最常用——用户输入的文本 prompt | `isinstance(block, TextContentBlock)` 提取 `.text` |
| `ImageContentBlock` | `.source: ImageSource` (base64 或 url) | 包含图片的任务——截图问 Bug、设计稿转代码 | **本 Demo 忽略** |
| `AudioContentBlock` | `.source: AudioSource` | 语音输入——语音助手场景 | **本 Demo 忽略** |
| `ResourceContentBlock` | `.resource: Resource` (URI + mimeType) | 引用外部资源——"分析这个 PDF" | **本 Demo 忽略** |
| `EmbeddedResourceContentBlock` | `.resource: EmbeddedResource` (URI + blob) | 资源内容直接嵌入——离线场景 | **本 Demo 忽略** |

> ⚠️ **注意事项**：本 Demo 通过 `isinstance(block, TextContentBlock)` 只处理了文本——但这恰恰说明了协议的**可扩展性**。你能想象一个场景：用户发来一张机票截图，Agent 收到的是 `ImageContentBlock`，然后调用视觉模型 OCR 提取航班号。这一切都发生在**同一个 `prompt()` 方法中**，不需要额外的协议扩展。

> 💡 **核心洞见**：PromptBlock 的联合类型设计是 ACP 区别于传统文本协议（如 OpenAI Chat Completions API 的纯 JSON 文本）的关键差异。它让多模态输入成为了协议的**一等公民**，而非框架层的"附加上下文"。

---

### 4.5 Session 与多轮对话机制

#### 🧠 直观理解

`session_id` 就像一个聊天窗口的"房间号"。你和 Agent 在同一房间里的对话，Agent 都记得。换个房间（`new_session`），Agent 就从头开始。这和你使用 Claude Code 时，左侧边栏的每个对话都是一个独立 session 完全一样。

#### 📖 详细解释

##### Session 的创建

```python
async def new_session(self, ...) -> NewSessionResponse:
    return NewSessionResponse(session_id=uuid4().hex)
```

`uuid4().hex` 生成 32 位随机十六进制字符串。由于使用随机数生成（而非时间戳），session_id 无法被猜测或枚举，天然具备一定的安全属性。

##### Session 的更新

```python
await self._client.session_update(
    session_id=session_id,
    update=update_agent_message(text_block(render_reply(self._role, prompt_text))),
)
```

每次 `prompt()` 调用时，Agent 通过 `session_update` 将新生成的 Agent 消息追加到指定 `session_id` 的会话历史中。这个更新是**增量式**的——每次只追加一条消息，而非覆盖整个会话。

##### Session 的回想（Recall / Resume）

这是课中 Q&A 的核心问题。有同学问："持续多轮交互可以维持有状态的多轮交互吗？"

答案：**可以，关键在于复用同一个 session_id。**

```
第一轮：
  Client: prompt(prompt=[TextContentBlock("帮我查北京的天气")], session_id="abc123")
  Agent:  session_update(session_id="abc123", ...) → 回复天气信息
  → 会话 "abc123" 中现在有 2 条消息：user 的询问 + agent 的回复

第二轮（同一会话）：
  Client: prompt(prompt=[TextContentBlock("那明天呢？")], session_id="abc123")
  Agent:  从 session_id="abc123" 的会话历史中可知上文是"北京天气"
          → 正确理解"那明天呢"指的是"明天北京的天气"
  → 会话 "abc123" 中现在有 4 条消息
```

而在本 Demo 的最简实现中，Agent 侧**并没有**自己维护会话存储——它完全依赖 Client 侧来管理会话历史。Agent 所做的只是将新消息推送给 Client，然后 Client 负责将消息追加到会话中。这是一种**Client 侧管理会话状态**的架构模式。

> ⚠️ **注意事项**：本 Demo 的 `new_session()` 没有创建任何内部数据结构来存储会话。在生产级 Agent 中，你通常需要在此创建 `self._sessions[session_id] = []`，并在 `prompt()` 中读取历史消息来构造 LLM 的上下文。

#### 🔀 会话管理方式对比

| 管理方式 | 会话存储位置 | 优点 | 缺点 | 适用场景 |
|---|---|---|---|---|
| Client 侧管理（本 Demo 模式） | Client（Host） | Agent 无状态、易水平扩展 | Client 必须在线且可靠 | 简单 Demo、无状态 Agent |
| Agent 内存管理 | Agent 进程内存 | 低延迟、实现简单 | 进程重启丢失、不支持分布式 | 单机 Agent、开发环境 |
| 外部存储管理 | Redis / DB / 文件 | 持久化、支持分布式 | 额外依赖、网络延迟 | 生产级 Agent 服务 |

---

### 📋 本节小结

#### 🗺️ 知识图谱

```
            ┌───────────────────────────┐
            │   ACP 最小 Demo Agent     │
            │   (demo_acp_agent.py)     │
            └────────────┬──────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
  ┌──────────┐   ┌──────────────┐   ┌──────────┐
  │ 生命周期  │   │  核心方法      │   │ 关键概念  │
  └────┬─────┘   └──────┬───────┘   └────┬─────┘
       │                │                │
  ┌────┴────┐    ┌──────┴──────┐   ┌────┴─────┐
  │Initialize│    │ on_connect  │   │PromptBlock│
  │Session   │    │ initialize  │   │session_id │
  │Prompt    │    │ new_session │   │end_turn   │
  │Response  │    │ prompt      │   │session_up │
  │Cancel    │    │ run_agent   │   │-date      │
  └─────────┘    └─────────────┘   └───────────┘
```

#### 💡 一句话总结

> 一个生产可用的 ACP Agent 只需要 4 个方法（on_connect、initialize、new_session、prompt）——其中前 3 个在大多数场景下可以用固定模板，你真正需要定制的只有 `prompt()` 中的 LLM 调用逻辑。而本文解析的 Demo 证明：即使不接入大模型，用规则函数也能让 Agent 跑起来，关键是把协议骨架搭对。

#### 🔗 延伸关联

- **前置内容**：`AgenticSpec` 中 `name` 字段（如 `"demo-reviewer"`）正是本 Demo 中 `initialize()` 返回的 `Implementation.name`——两者必须一致，否则 Client 无法找到对应的 Agent 实现。
- **后继内容**：M08 的 Adapter 实现中，`initialize` / `new_session` / `prompt` 三个方法的签名将被直接复用为模板。
- **工程启示**：如果不需要 LLM，规则化 Agent 是极低成本的多节点编排方案（参考 `render_reply` 的 reviewer/reporter 设计）。

---

> 🤖 由 transcript-to-doc v4.1 生成

## 五、ACP Client 与任务分发运行

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 理解 `AcpTaskResult` dataclass 中 6 个字段的含义与用途
> - [ ] 实现一个最小可用的 ACP Client（`CollectingClient`），理解其能力边界
> - [ ] 掌握 `run_acp_task()` 的四步执行流程：spawn → initialize → new_session → prompt
> - [ ] 理解 `asyncio.wait_for()` 的超时保护机制和 `text_block()` 的协议转换作用
> - [ ] 诊断并解决 ACP Client 端常见的 `npx` 找不到问题
> - [ ] 理解 DAG 任务回收后的汇总模型处理流程

---

### 5.1 AcpTaskResult 数据结构

#### 🧠 直观理解

`AcpTaskResult` 是 ACP Client 执行完一次任务后返回的结构化结果包。你可以把它想象成一个快递包裹：发件人（agent_name）、快递单（agent_info）、包裹内容（text）、物流状态（stop_reason、update_kinds），所有信息一目了然。有了它，上层 DAG 编排器无需关心底层 ACP 协议细节，直接读取字段即可拿到任务执行的完整信息。

#### 📖 详细解释

`AcpTaskResult` 是一个 `@dataclass(frozen=True)` 的不可变数据结构。使用 `frozen=True` 意味着实例创建后字段不可修改——这是函数式编程中的"值对象"模式，确保任务结果一旦生成就不会被意外篡改，在多任务回收汇总时特别重要。

每一个字段都对应 ACP 协议中的一个关键信息点：

| 字段 | 类型 | 含义 | 来源 |
|---|---|---|---|
| `agent_name` | `str` | 执行任务的 Agent 名称 | 从 `AgentSpec.name` 传入 |
| `agent_info` | `str` | Agent 端宣告的身份信息 | `connection.initialize()` 返回的 `init.agent_info.name` |
| `session_id` | `str` | 本次会话的唯一标识 | `connection.new_session()` 返回的 `session.session_id` |
| `stop_reason` | `str` | 对话结束原因（如 `"end_turn"` 表示自然完成） | `connection.prompt()` 返回的 `response.stop_reason` |
| `update_kinds` | `tuple[str, ...]` | 会话过程中收到的更新类型列表 | `CollectingClient.session_update()` 收集 |
| `text` | `str` | Agent 返回的全部文本内容（拼接所有 text chunks） | `CollectingClient.text` 属性 |
| `permission_decisions` | `tuple[str, ...]` | 权限请求的决策记录 | `CollectingClient.request_permission()` 收集 |

#### 💻 代码定义

```python
# 文件名: acp_client.py（片段）
# 功能: 定义 ACP 任务执行结果的数据结构

from dataclasses import dataclass

@dataclass(frozen=True)
class AcpTaskResult:
    agent_name: str          # 来自 AgentSpec，标识是哪个 Agent 执行的任务
    agent_info: str          # ACP 握手时 agent 端宣告的自身信息（Implementation.name）
    session_id: str          # ACP 会话 ID，可用于后续 resume 继续对话
    stop_reason: str         # 对话停止原因："end_turn"（正常完成）、"max_turns"（达到上限）等
    update_kinds: tuple[str, ...]   # 会话期间收到的所有 update 类型，用于调试和审计
    text: str                # Agent 最终输出的完整文本，由所有 text chunks 拼接而成
    permission_decisions: tuple[str, ...]  # 每次权限请求的决策记录，用于安全审计
```

行级解析表：

| 行号 | 代码 | 解释 |
|---|---|---|
| 24 | `@dataclass(frozen=True)` | 声明为不可变数据类；frozen=True 保证实例创建后只读 |
| 25 | `class AcpTaskResult:` | 结果载体类，不包含任何行为逻辑（纯数据） |
| 26-32 | 7 个字段 | 每个字段都用类型标注，构成完整的任务执行回执 |

---

### 5.2 CollectingClient 能力边界详解

#### 🧠 直观理解

`CollectingClient` 是 ACP Client 的最小化实现。想象你去参加一个会议，你只需要做三件事：听别人说话（收集 text chunks）、表示"这个操作我不批准"（默认拒绝权限）、承认自己不会做某些事（RuntimeError）。这就是 `CollectingClient` 的全部职责——它是"只读监听器"，不主动执行任何有副作用的操作。

#### 📖 详细解释

ACP 协议要求 Client 端声明自己的"能力"（capabilities）。一个功能完备的 Client 应当实现文件读写、终端操作、权限管理等多种能力。但在 DAG 任务分发场景中，Client 的角色是"调度器"而非"执行器"——它只需把 prompt 发给 Agent，把结果收回来即可。因此，`CollectingClient` 通过显式抛出 `RuntimeError` 来声明自己没有某种能力，这是一种**最小化设计模式**：代码清楚地表达了"我故意不实现这个功能"，而不是默默忽略。

#### 💻 Step-by-Step

**Step 1: 初始化与连接 — `__init__()` + `on_connect()`**

```python
# 文件名: acp_client.py —— CollectingClient 类初始化部分

class CollectingClient:
    """最小 ACP Client：收消息，默认拒绝有副作用的权限请求。"""

    def __init__(self) -> None:
        self._text_chunks: list[str] = []      # 收集所有来自 Agent 的文本片段
        self.update_kinds: list[str] = []      # 记录每次 update 的类型（如 "message"）
        self.permission_decisions: list[str] = []  # 记录每次权限决策

    def on_connect(self, conn: Any) -> None:
        self._connection = conn                 # 保存连接对象，以备后续操作使用
```

> 初始化时创建三个空列表，分别负责**文本收集**、**事件记录**和**安全审计**。`_text_chunks` 以下划线开头，暗示外部应通过 `text` 属性而非直接访问该列表。

---

**Step 2: 收集文本更新 — `session_update()`**

```python
    async def session_update(self, session_id: str, update: Any, **kwargs: Any) -> None:
        self.update_kinds.append(str(update.session_update))  # 记录本次 update 的类型
        content = getattr(update, "content", None)            # 尝试获取 content 字段
        text = getattr(content, "text", None)                  # 从 content 中提取 text
        if getattr(content, "type", None) == "text" and isinstance(text, str):
            self._text_chunks.append(text)                     # 只收集 type="text" 的文本块
```

> `session_update()` 是 Client 接收 Agent 消息的主入口。每次 Agent 产生新内容时 ACP 协议层会调用此方法。这里做了两层防御性提取：先用 `getattr` 安全获取 `content`，再从中提取 `text`，同时校验 `content.type == "text"`——确保只收集真正的文本更新，过滤掉工具调用结果等其他类型的更新。

---

**Step 3: 默认拒绝权限 — `request_permission()`**

```python
    async def request_permission(
        self,
        options: list[PermissionOption],
        session_id: str,
        tool_call: ToolCallUpdate,
        **kwargs: Any,
    ) -> RequestPermissionResponse:
        # 在所有选项中找第一个以 "reject" 开头的选项
        reject = next((item for item in options if item.kind.startswith("reject")), None)
        if reject is None:
            self.permission_decisions.append("cancelled")
            return RequestPermissionResponse(outcome=DeniedOutcome(outcome="cancelled"))
        self.permission_decisions.append(reject.option_id)
        return RequestPermissionResponse(
            outcome=AllowedOutcome(outcome="selected", option_id=reject.option_id)
        )
```

> ⚠️ **注意事项**：`CollectingClient` 的安全策略是"默认拒绝"——对所有有副作用的权限请求（如文件写入、执行命令）一律选择拒绝。这在 DAG 任务分发场景中是合理的，因为我们只需要 Agent 做"纯文本推理"，不需要它操作文件系统或执行终端命令。

---

**Step 4: 未实现的能力声明 — RuntimeError 设计模式**

```python
    async def write_text_file(self, **kwargs: Any) -> None:
        raise RuntimeError("这个示例 Client 没有声明文件写入能力")

    async def read_text_file(self, **kwargs: Any) -> ReadTextFileResponse:
        raise RuntimeError("这个示例 Client 没有声明文件读取能力")

    async def create_terminal(self, **kwargs: Any) -> Any:
        raise RuntimeError("这个示例 Client 没有声明终端能力")

    async def terminal_output(self, **kwargs: Any) -> Any:
        raise RuntimeError("这个示例 Client 没有声明终端能力")

    async def release_terminal(self, **kwargs: Any) -> None:
        raise RuntimeError("这个示例 Client 没有声明终端能力")

    async def wait_for_terminal_exit(self, **kwargs: Any) -> Any:
        raise RuntimeError("这个示例 Client 没有声明终端能力")

    async def kill_terminal(self, **kwargs: Any) -> None:
        raise RuntimeError("这个示例 Client 没有声明终端能力")
```

> 💡 **核心洞见**：抛出 `RuntimeError` 而非静默返回 `None` 是刻意为之。如果 DAG 编排器错误地把一个需要文件写入权限的任务派发给了一个没有声明该能力的 Client，运行时异常会立即暴露问题，而不是默默丢失数据。这是一种 **fail-fast（快速失败）** 的设计哲学。

---

**Step 5: 扩展方法占位 — `ext_method()` + `ext_notification()`**

```python
    async def ext_method(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError(f"未实现扩展方法：{method}")

    async def ext_notification(self, method: str, params: dict[str, Any]) -> None:
        return None   # 通知类消息可以安全忽略，不抛异常
```

> `ext_method` 用于处理 Agent 发来的自定义方法调用（请求-响应模式），未实现时抛异常告知调用方。`ext_notification` 用于接收 Agent 发来的单向通知，因为通知不需要回复，所以静默忽略即可——这是两种不同的通信模式的正确处理方式。

---

**Step 6: `text` 属性 — 拼接所有 text chunks**

```python
    @property
    def text(self) -> str:
        return "".join(self._text_chunks)
```

> 使用 `@property` 将 `text` 暴露为只读属性，外部访问 `client.text` 即可拿到完整的文本结果。内部高效地用 `"".join()` 拼接——因为 chunks 按接收顺序追加，`join` 可以保持正确的文本顺序。

---

### 5.3 `run_acp_task()` 核心函数逐行解析

#### 🧠 直观理解

`run_acp_task()` 是整个 ACP Client 侧的核心函数——给定一个 Agent 规格描述（`AgentSpec`）和一段 prompt 文本，启动对应的 Agent 子进程、完成协议握手、建立会话、发送 prompt、等待结果，最后把结果打包成 `AcpTaskResult` 返回。整个过程就像点外卖：选商家（AgentSpec）、下单（prompt）、等待配送（asyncio.wait_for 超时保护）、收货确认（AcpTaskResult）。

#### 🔄 执行流程

```
run_acp_task(spec, prompt_text)
    │
    ├── 1. 创建 CollectingClient 实例（收件箱）
    │
    ├── 2. spawn_agent_process() 启动 Agent 子进程
    │       │
    │       ▼
    │   ┌──────────────────────────────────────┐
    │   │  connection.initialize()             │
    │   │  握手交换：Client 能力 ↔ Agent 信息   │
    │   │  得到：agent_info（Agent 身份信息）   │
    │   └──────────────────────────────────────┘
    │       │
    │       ▼
    │   ┌──────────────────────────────────────┐
    │   │  connection.new_session()            │
    │   │  创建新会话，获得 session_id          │
    │   │  参数：cwd（工作目录）、mcp_servers   │
    │   └──────────────────────────────────────┘
    │       │
    │       ▼
    │   ┌──────────────────────────────────────┐
    │   │  connection.prompt()                 │
    │   │  发送 prompt block，获得 stop_reason  │
    │   │  期间：session_update() 持续收集文本  │
    │   └──────────────────────────────────────┘
    │
    ├── 3. asyncio.wait_for() 超时保护（默认 60 秒）
    │
    └── 4. 组装 AcpTaskResult 返回
```

#### 💻 Step-by-Step 完整代码解析

**函数签名与参数**

```python
async def run_acp_task(
    spec: AgentSpec,           # 来自 agent_registry 的 Agent 规格
    prompt_text: str,          # 要发送给 Agent 的纯文本 prompt
    *,
    cwd: str | Path | None = None,   # Keyword-only：指定 Agent 的工作目录
    timeout: float = 60.0,           # Keyword-only：超时秒数，默认 60 秒
) -> AcpTaskResult:
```

> `*` 后的参数是 keyword-only 参数，调用者必须使用 `cwd=...` 或 `timeout=...` 的形式传入，提高可读性和安全性。

---

**Step 1: 初始化 Client 和工作目录**

```python
    client = CollectingClient()
    workdir = Path(cwd or Path.cwd()).resolve()
```

> `Path(cwd or Path.cwd())` 提供了灵活的工作目录设置：如果调用者传了 `cwd` 就用指定路径，否则用当前工作目录。`.resolve()` 将路径解析为绝对路径——这在启动子进程时非常重要，因为子进程的工作目录独立于父进程，相对路径可能导致文件找不到。

---

**Step 2: spawn_agent_process() —— 启动 Agent 子进程**

```python
    async def execute() -> tuple[Any, Any, Any]:
        async with spawn_agent_process(
            cast(Client, client),   # 将 CollectingClient 声明为 ACP Client 协议类型
            spec.command,            # Agent 的启动命令（如 "npx"）
            *spec.args,              # 命令参数（如 "@anthropic-ai/claude-code"）
            cwd=workdir,             # 子进程工作目录
        ) as (connection, _process):
```

> `spawn_agent_process()` 是 ACP SDK 提供的核心函数，它创建一个子进程来运行 Agent。`async with` 上下文管理器确保函数退出时自动清理子进程。`cast(Client, client)` 是类型转换——`CollectingClient` 虽然没有显式继承 `Client`，但它实现了 `Client` 要求的全部方法（鸭子类型），`cast` 告知类型检查器这是合法的。

---

**Step 3: connection.initialize() —— 握手获得 agent_info**

```python
            init = await connection.initialize(
                protocol_version=PROTOCOL_VERSION,   # ACP 协议版本号
                client_capabilities=ClientCapabilities(),  # 声明 Client 能力（此处为空）
                client_info=Implementation(
                    name="course-acp-orchestrator",   # Client 端的标识名称
                    title="课程 ACP 编排器",
                    version="0.1.0",
                ),
            )
```

> `initialize()` 是 ACP 协议的第一步握手。Client 向 Agent 宣告自己的身份和协议版本，Agent 回复自己的身份信息（`init.agent_info`）。`ClientCapabilities()` 传空对象意味着我们没有声明任何特殊能力——这与 `CollectingClient` 的"最小化"设计一致，如果 Agent 尝试使用我们未声明的能力，ACP 协议层会提前拦截并报错。

---

**Step 4: connection.new_session() —— 建会话**

```python
            session = await connection.new_session(
                cwd=str(workdir),    # 告知 Agent 本次会话的工作目录
                mcp_servers=[]       # 不附加任何 MCP 服务器
            )
```

> `new_session()` 在握手的连接上创建一次对话会话。`session.session_id` 是这个会话的全局唯一标识——后续 `connection.prompt()` 必须带上这个 ID 来指定向哪个会话发送消息。`mcp_servers=[]` 表示本次会话不连接任何外部 MCP 服务器，保持环境纯净。

---

**Step 5: connection.prompt() —— 发送 prompt**

```python
            response = await connection.prompt(
                prompt=[text_block(prompt_text)],   # 纯文本 → ACP PromptBlock 列表
                session_id=session.session_id,       # 指定目标会话
            )
            return init, session, response
```

> `prompt()` 将 prompt 发送给 Agent 并等待响应。传入的 `prompt` 是 `PromptBlock` 列表——因为 ACP 协议支持多模态 prompt（文本块 + 图片块 + 工具调用块等）。`text_block(prompt_text)` 这个工具函数将纯文本字符串包装成符合 ACP 协议的 `PromptBlock` 对象，是字符串与协议格式之间的桥梁。

> ⚠️ **注意事项**：在 Agent 处理 prompt 期间，ACP 协议层会不断调用 `CollectingClient.session_update()` 推送增量文本。所以当 `prompt()` 返回时，`client.text` 已经包含了完整的响应文本。

---

**Step 6: asyncio.wait_for() —— 超时保护**

```python
    init, session, response = await asyncio.wait_for(execute(), timeout=timeout)
```

> `asyncio.wait_for()` 给 `execute()` 协程设置了硬性时间上限。如果 Agent 在超时时间内没有完成响应，协程会被 `TimeoutError` 中断。这在实际生产中非常重要——Agent 可能因为模型 API 延迟、网络问题或死循环而无响应，超时机制保证调度器不会无限等待。默认 60 秒为大多数推理任务留出了足够余量。

---

**Step 7: 组装 AcpTaskResult 返回**

```python
    info = init.agent_info
    agent_info = info.name if info is not None else "(未提供 agentInfo)"
    return AcpTaskResult(
        agent_name=spec.name,                    # 从 AgentSpec 传入
        agent_info=agent_info,                    # 握手时获得
        session_id=session.session_id,            # 建会话时获得
        stop_reason=response.stop_reason,          # prompt 返回时获得
        update_kinds=tuple(client.update_kinds),   # session_update 收集
        text=client.text,                          # 全部 text chunks 拼接
        permission_decisions=tuple(client.permission_decisions),  # 权限决策记录
    )
```

> `agent_info` 做了防御性处理：如果 Agent 端没有提供 `agentInfo`，用 `"(未提供 agentInfo)"` 作为占位字符串，避免 `None.name` 抛出 `AttributeError`。所有从 `client` 收集的列表被转为 `tuple`——不可变类型适合在多线程/多协程间安全传递。

---

#### 📖 `text_block()` 工具函数解析

`text_block(prompt_text)` 是 ACP SDK 提供的辅助函数，它将一段纯文本字符串转换为 ACP 协议中标准的 `PromptBlock` 对象：

```
用户传入 "请帮我核实出差相关信息..."
        │
        ▼  text_block()
┌─────────────────────────────────────┐
│ PromptBlock(                        │
│   type="text",                      │
│   content=TextContent(              │
│     text="请帮我核实出差相关信息..."  │
│   )                                 │
│ )                                   │
└─────────────────────────────────────┘
```

> 💡 **核心洞见**：调用方只需要关心"我要发什么文本"，不需要关心 ACP 协议的数据结构细节。`text_block()` 隐藏了协议转换的复杂性，起到了适配器的作用。这也解释了为什么 `run_acp_task` 接收的是 `prompt_text: str` 而不是 `list[PromptBlock]`——对外接口越简单越好。

---

### 5.4 🐛 排错实录：npx 找不到

#### 🐛 排错实录：npx 无法正确找到导致 ACP Client 启动失败

> 此问题是老师在课堂上现场遇到的，耗时约 4 分钟排查。以下按 template.md Rule 1 格式完整还原踩坑与修复全过程。

---

**❌ 错误现象**

在 Jupyter Notebook 环境中，执行 `run_acp_task()` 启动 claude-code Agent 时，`spawn_agent_process()` 调用 `npx` 命令失败，Agent 子进程无法正常启动。`which npx` 在终端中返回的路径不正确——显示了一个过期的或不可用的 npx 位置。

**🚨 报错信息**

```
# 在 Notebook cell 中执行时：
找不到 npx

# 终端排查时：
$ which npx
/Users/xxx/.nvm/versions/node/vXX.XX.X/bin/npx  # 这个路径实际上不对或已过期

# ACP 子进程启动时报错：
Error: spawn npx ENOENT
# 或者 ACP 连接超时/connect 时报 connection error
```

**🔍 原因分析**

问题经历了三轮排查：

| 轮次 | 排查动作 | 观察结果 | 推论 |
|---|---|---|---|
| 第 1 轮 | `which npx` | 返回了一个路径，但不正确 | 不是 PATH 环境变量的问题（否则连路径都找不到） |
| 第 2 轮 | 提供绝对路径 `which npx` 的结果给代码 | 替换后仍然不行 | 不是路径问题——是 npx 二进制或它的缓存有问题 |
| 第 3 轮 | 重启环境（关闭并重新打开终端/Notebook） | npx 恢复正常 | 根本原因：**Node.js 服务缓存未处理好** |

**根本原因**：在 Mac 环境下使用 `nvm` 管理 Node.js 版本时，`npx` 的实际二进制文件位置和运行时缓存可能不同步。当 nvm 切换版本或环境变量被部分刷新后，`npx` 命令虽然可以被 `which` 找到，但其内部依赖的缓存文件（如 `.npm/_npx/` 目录下的缓存）可能已过时或损坏，导致实际执行时失败。

**额外的适配性问题**：即使 npx 问题修复后，在 Jupyter Notebook 中运行 ACP 相关代码时仍出现了 `connection error`。老师特别强调：**"这不是 ACP 的问题，是 notebook 执行环境跟 ACP 的适配性不是特别高"**。Notebook 的事件循环模型与 `asyncio` 的 `spawn_agent_process()` 有时会冲突——Notebook 自身也运行在一个 asyncio 事件循环中，嵌套启动子进程可能导致连接状态异常。

**✅ 正确修复**

```bash
# 方案 1：重启终端/IDE 环境（最简单有效）
# 关闭当前终端窗口/Notebook kernel → 重新打开 → 问题解决

# 方案 2：手动清理 npm/npx 缓存（如果重启无效）
$ npm cache clean --force
$ rm -rf ~/.npm/_npx

# 方案 3：使用 npx 的绝对路径作为临时替代（不推荐长期使用）
# 在 AgentSpec 中：
# command="/usr/local/bin/npx"  # 硬编码绝对路径
# 但这样换机器就会出问题，不如重启环境干净
```

**📝 经验总结**

1. **环境工具的缓存问题排查优先级**：先怀疑"缓存"再怀疑"安装"——`which` 能找到 ≠ 能正常运行。Node.js 生态（nvm + npm + npx）的缓存层数多，出问题概率不低。

2. **Notebook 环境下运行 ACP 的注意事项**：
   - ACP 的 `spawn_agent_process()` 需要独立的事件循环管理，Notebook 自带的事件循环可能造成干扰
   - 如果 Notebook 中 ACP 连接异常，优先考虑在独立 Python 脚本中测试
   - 老师最终为了演示效果，切换到直接在终端/脚本中运行 ACP 代码，而非执着于在 Notebook 中跑通

3. **防御性编程建议**：在生产环境的 `AgentSpec` 中，可以使用 `shutil.which("npx")` 来动态查找命令路径，并在找不到时给出明确错误提示，而不是依赖环境变量：

```python
import shutil

npx_path = shutil.which("npx")
if npx_path is None:
    raise RuntimeError(
        "未找到 npx 命令。请确认 Node.js 已正确安装且 npx 在 PATH 中。"
    )
```

---

### 5.5 结果回收与后续处理

#### 📖 DAG 回收后的汇总模型环节

`run_acp_task()` 返回的 `AcpTaskResult` 包含了 Agent 执行的完整结果。在 DAG 编排的完整流程中，任务分发不是终点——**任务的回收处理和汇总才是最后的关键步骤**。

整个数据流如下：

```
DAG 规划器
    │
    ├── 拆出任务 A ──▶ run_acp_task(codex_spec, travel_prompt)
    │                      │
    │                      ▼  AcpTaskResult(text="适合 1 日游的景点: ...")
    │
    ├── 拆出任务 B ──▶ run_acp_task(claude_spec, budget_prompt)
    │                      │
    │                      ▼  AcpTaskResult(text="50 元团餐推荐: ...")
    │
    └── 所有结果回收 ──▶ 汇总模型（大语言模型）
                            │
                            ▼
                       最终综合报告
```

> 💡 **核心洞见**：DAG 编排的精髓在于"拆任务 + 派任务 + 收结果 + 二次汇总"四步循环。`run_acp_task()` 解决了"派任务"和"收结果"两步。拿到所有结果后，你可以把它们作为上下文喂给一个大语言模型，让它做最终的整合与润色——这就是"Agent 协作"的真正价值：每个 Agent 各司其职，主模型做最后的信息融合。

#### 💻 代码示例

```python
# 文件名: dag_delegate.py（概念演示）
# 功能: 展示回收多个 AcpTaskResult 后进行汇总处理

async def orchestrate_travel_plan():
    # 第一步：并行分发任务给不同的 Agent
    tasks = [
        run_acp_task(codex_spec, "帮我查一下杭州 1 日游的推荐路线"),
        run_acp_task(claude_spec, "杭州西湖周边 50 元以内的团餐有什么推荐？"),
    ]
    results: list[AcpTaskResult] = await asyncio.gather(*tasks)

    # 第二步：回收所有结果，拼成汇总 prompt
    context_parts = []
    for r in results:
        context_parts.append(f"【{r.agent_name}】的结果：\n{r.text}\n")
        # 可以同时检查 stop_reason，确认任务是否正常完成
        if r.stop_reason != "end_turn":
            print(f"⚠️ {r.agent_name} 未正常完成，stop_reason={r.stop_reason}")

    summary_prompt = (
        "请根据以下各 Agent 的分析结果，整合出一份完整的杭州一日游计划：\n\n"
        + "\n".join(context_parts)
    )

    # 第三步：发给汇总模型做最终整合
    final_result = await run_acp_task(
        summary_spec,    # 一个专门做文本汇总的 Agent
        summary_prompt,
        timeout=120.0,   # 汇总可能需要更多 token，给更长超时
    )

    return final_result.text
```

> ⚠️ **注意事项**：回收结果时建议检查 `stop_reason`——如果某个 Agent 因为超时、被拒绝权限等原因异常退出，你需要决定是重试、跳过、还是降级处理。不能盲目信任所有返回结果。

---

### 5.6 💬 Q&A 答疑

---

**🙋 问题 1**：调用 ACP 得到结果以后，Agent 进程还在运行吗？如果 CLI 退出了，会话还存在吗？

> 📖 **背景**：学员关心 ACP Client 调用完成后 Agent 子进程的生命周期和会话持久性问题。

**💬 老师回答**：

- **Agent 进程**：`spawn_agent_process()` 使用 `async with` 上下文管理器，当 `execute()` 函数退出时，子进程自动被清理。所以 `run_acp_task()` 返回后，对应的 Agent 子进程就已经终止了。
- **会话持久化**：CLI 退出后，虽然 Agent 进程终止了，但**会话记录是持久化的**。以 claude-code 的 CLI 为例：

```
$ claude
> how are you?
... 对话 ...
> /exit
  📋 会话已保存，下次可通过 resume 恢复

$ claude --resume <session_id>
> （之前的对话历史都在，可以继续）
```

> 对于 ACP 也是如此：`session.session_id` 是持久化标识。你可以保存这个 ID，之后用 `connection.resume_session(session_id)` 恢复之前的对话上下文继续执行。这对于需要多轮对话的任务（如"先查数据 → 分析 → 再提问"）至关重要。

> 💡 **延伸**：理解 CLI exit 和 session 持久化的关系很重要——exit 关掉的是"进程"，但 session 的"状态"存在文件系统中。这就像你关掉浏览器但书签还在，下次打开可以继续浏览。

---

**🙋 问题 2**：如果我把 skills 放在 `.agent` 文件夹下面，不同的 Agent（codex、claude-code）能共享这些 skills 吗？

> 📖 **背景**：学员希望了解是否可以通过一个公共目录实现多个 Agent 之间的 skills 共享。

**💬 老师回答**：

原则上可以，但有优先级差异：

1. **`.agent/skills/`** 是一个通用目录，codex 和 claude-code 理论上都会去这个目录下查找 skills
2. 但是，**特定 Agent 的专属目录优先级更高**：
   - codex 优先查找 `.codex/skills/`
   - claude-code 优先查找 `.claude/skills/`
3. 因此 **不能 100% 保证** Agent 一定会使用 `.agent/` 下的 skills——如果同名的 skill 同时存在于 `.codex/skills/` 和 `.agent/skills/`，Agent 会优先用自己专属目录的版本

> 💡 **延伸**：如果你想确保 skills 在不同 Agent 间完全一致，最简单的方式是**在每个 Agent 的专属目录下放置符号链接**，指向同一个 skill 文件，而不是依赖 `.agent/` 的隐式查找机制。

---

**🙋 问题 3**：可以在发送 prompt 的时候追加 skills 指令吗？

> 💬 **老师回答**：可以。本质上是把技能指令直接拼到 prompt 文本中发给 Agent，比如在 `prompt_text` 中加入：

```
请使用以下 skill 完成任务：
- skill: 代码审查

任务内容：请审查 app.py 中的以下函数...
```

> 这种方式相当于"内联 skill 分发"——不需要 Agent 端预先安装 skill 文件，只需要在 prompt 中给出明确的指令。它特别适合 DAG 编排场景，因为调度器可以在分发任务时动态决定哪些 skill 指令附加到哪个 Agent 的 prompt 中。

---

## 📋 本节小结

### 🗺️ 知识图谱

```
                    ┌──────────────────────────┐
                    │   run_acp_task()          │
                    │   核心调度函数              │
                    └────────────┬─────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
    ┌─────────────────┐ ┌───────────────┐ ┌──────────────────┐
    │ CollectingClient │ │ ACP Protocol  │ │ AcpTaskResult    │
    │ 最小化 Client    │ │ 四步握手      │ │ 结构化结果包      │
    │ · session_update │ │ · spawn       │ │ · agent_name     │
    │ · request_permit │ │ · initialize  │ │ · session_id     │
    │ · RuntimeError   │ │ · new_session │ │ · stop_reason    │
    │   (能力声明)      │ │ · prompt      │ │ · text           │
    └─────────────────┘ └───────────────┘ └──────────────────┘
              │                                       │
              ▼                                       ▼
    ┌─────────────────┐                   ┌──────────────────┐
    │ 排错：           │                   │ DAG 结果回收      │
    │ npx 缓存问题     │                   │ → 汇总模型处理    │
    │ Notebook 适配性  │                   │ → 最终报告        │
    └─────────────────┘                   └──────────────────┘
```

### 💡 一句话总结

> `run_acp_task()` 通过四步握手（spawn → initialize → new_session → prompt）完成一次 Agent 任务分发，`CollectingClient` 以最小化实现充当"只读监听器"，结果通过 `AcpTaskResult` 结构化返回供 DAG 编排器回收处理——整个过程的核心是"派得出去、收得回来、防得住超时"。

### 📍 系列定位

> 📍 **系列定位**：本文是「Agent架构师企业级智能体系统构建」第 5 篇。
> - 上一篇：ACP 生命周期与最小 Demo Agent — Agent 端如何响应 ACP 请求
> - 下一篇：DAG + ACP 编排实战 — 利用 run_acp_task 进行多 Agent 任务分发的完整实践

## 六、DAG + ACP 编排实战

> 🏷️ 标签: `DAG` `ACP` `多Agent协同` `Planner` `拓扑排序` `编排` `TaskNode`

---

### 📑 目录

- [6.1 旅行规划案例 — DAG + ACP 编排全景](#61-旅行规划案例--dag--acp-编排全景)
- [6.2 dag_delegate.py 源码逐行解析](#62-dag_delegatepy-源码逐行解析)
- [6.3 Planner 的工作原理](#63-planner-的工作原理)
- [6.4 执行流程走读](#64-执行流程走读)
- [6.5 编排策略选择](#65-编排策略选择)

---

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 使用 `TaskNode` 构建带依赖关系的 DAG 任务图
> - [ ] 实现拓扑排序算法确定执行顺序
> - [ ] 利用 ACP 将 DAG 节点分发给不同 Agent 执行
> - [ ] 理解 Planner（LLM 驱动）如何从可选行动项中规划出合流
> - [ ] 在实际项目中选择合适的编排策略（DAG Planner / 手动编排 / TriggerFlow）

---

### 6.1 旅行规划案例 — DAG + ACP 编排全景

#### 📋 背景

假设我们接到一个出差规划任务：需要为一次从北京到杭州的出差做好行程准备。这涉及到三个子任务：

1. **差旅制度核查**：杭州出差的市内交通限额、餐补标准、住宿报销上限是什么？
2. **实地信息核实**：杭州本周天气如何？西湖景区是否开放？当地有哪些市内交通方式？
3. **出差方案汇总**：结合制度要求和实况信息，生成一份完整的行程与预算复核摘要。

这三个子任务并不是孤立的——任务 3 需要依赖任务 1 和任务 2 的结果才能产出有效摘要。这就是典型的有向无环图（DAG）结构。

#### ⚠️ 问题

在第 16 课中，我们使用的方案是：用 DAG Planner 将任务拆为三个 `web_search` 执行块，搜索完成后由一个 `model_request` 块汇总结果。但 `web_search` 的能力有限——它只能返回网页片段，无法做深度推理、无法调用企业内部制度、无法结合上下文做专业判断。

**核心转变**：当我们将三个 `web_search` 块替换为三个专门的 Agent（通过 ACP 协议调用），整个流程就从"单模型的工具调用"升级为"多 Agent 的协同作战"。

#### 🔍 全景架构

```
                          ┌─────────────────────────┐
                          │     DAG Planner         │
                          │   (DeepSeek 驱动)        │
                          │                         │
                          │  左边：可选行动项          │
                          │  ┌─────────────────┐     │
                          │  │ agent: codex    │     │
                          │  │ agent: claude   │     │
                          │  │ agent: openclaw │     │
                          │  │ model_request   │     │
                          │  │   → deepseek    │     │
                          │  │   → qwen2.5:7b  │     │
                          │  └─────────────────┘     │
                          │         │               │
                          │         ▼               │
                          │  右边：编排好的合流         │
                          └────────┬────────────────┘
                                   │
                                   ▼
          ┌────────────────────────────────────────────────┐
          │              DAG 任务图 (TRAVEL_DAG)             │
          │                                                │
          │  ┌─────────────────┐                           │
          │  │ n1_policy       │  差旅制度核查              │
          │  │ agent: company- │  ───────────────────┐     │
          │  │   policy        │                     │     │
          │  └────────┬────────┘                     │     │
          │           │                              │     │
          │           │              ┌─────────────────┐   │
          │  ┌────────┴────────┐    │ n3_brief        │   │
          │  │ n2_facts        │    │ agent: demo-    │   │
          │  │ agent: demo-    │    │   reporter      │   │
          │  │   reviewer      │    │ depends_on:     │   │
          │  │                 │    │ n1_policy,      │   │
          │  │ 杭州天气/交通      │    │ n2_facts        │   │
          │  └────────┬────────┘    └────────┬────────┘   │
          │           │                      │            │
          └───────────┼──────────────────────┼────────────┘
                      │                      │
                      ▼                      ▼
          ┌────────────────────────────────────────────────┐
          │              ACP 分发层                        │
          │                                                │
          │  n1_policy ─▶ run_acp_task(company-policy)     │
          │  n2_facts  ─▶ run_acp_task(demo-reviewer)      │
          │  n3_brief  ─▶ run_acp_task(demo-reporter)      │
          │              ↑ 上游结果注入 prompt               │
          └─────────────────────┬──────────────────────────┘
                                │
                                ▼
          ┌────────────────────────────────────────────────┐
          │              任务回收 & 汇总                     │
          │                                                │
          │  results = {                                   │
          │    "n1_policy": "杭州差旅制度：交通限额..."      │
          │    "n2_facts":  "杭州本周多云，西湖开放..."      │
          │    "n3_brief":  "出差行程摘要：建议高铁..."      │
          │  }                                             │
          │                    │                           │
          │                    ▼                           │
          │           model_request (汇总模型)              │
          │           如：qwen2.5:7b 本地低成本模型           │
          └────────────────────────────────────────────────┘
```

> 💡 **核心洞见**：编排是核心，ACP 是通道。Planner 决定"谁做什么、以什么顺序做"，ACP 负责"把任务准确地传给对应的 Agent 并取回结果"。

#### 🔀 对比：第 16 课方案 vs 第 17 课方案

| 维度 | ❌ 第 16 课：web_search 块 | ✅ 第 17 课：Agent 任务 |
|---|---|---|
| 执行单元 | web_search 工具调用（返回网页片段） | 完整 Agent（Codex / Claude / OpenClaw） |
| 推理深度 | 仅靠搜索结果的摘要 | Agent 可深度推理、可调用自身工具链 |
| 企业数据 | 无法访问内部制度 | Agent 可读取本地文件、调用内部 API |
| 能力边界 | 搜索引擎决定上限 | Agent 自身的模型+工具决定上限 |
| 通信协议 | 无（函数调用） | ACP（Agent Communication Protocol） |
| 可扩展性 | 受限于搜索接口 | 任意 ACP 兼容 Agent 即插即用 |

---

### 6.2 dag_delegate.py 源码逐行解析

#### 🎯 目标

完整理解 DAG 编排的核心代码——从一个 `TaskNode` 的定义到一次旅行规划 DAG 的全自动执行。

#### 🧠 直观理解

把 DAG 编排想象成"项目管理"：`TaskNode` 是任务卡片（写明做什么、谁负责、等谁先做完），`topological_order()` 是项目经理排期（确保先决任务完成后再启动依赖任务），`run_travel_dag()` 是自动化执行引擎（按排期逐个委派并传递上游成果）。

#### 💻 完整代码与行级解析

```python
# 文件名: dag_delegate.py
# 功能: 构建旅行规划 DAG，按拓扑序委派给 ACP Agent，并注入上游结果

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from acp_client import AcpTaskResult, run_acp_task
from agent_registry import AGENT_MATRIX
```

| 行号 | 代码 | 解释 |
|---|---|---|
| 1 | `from __future__ import annotations` | 启用延迟注解求值，允许在 dataclass 中自引用类型（如 `tuple[str, ...]`）而不必用字符串 |
| 3 | `from dataclasses import dataclass` | 导入 dataclass 装饰器，用于创建不可变的数据容器 |
| 4 | `from pathlib import Path` | 导入路径处理工具，用于 `cwd` 参数的类型标注 |
| 6 | `from acp_client import AcpTaskResult, run_acp_task` | 从第 17 课的 ACP 客户端模块引入核心函数——这是 DAG 与 ACP 的"化学键" |
| 7 | `from agent_registry import AGENT_MATRIX` | 引入第 17 课的 Agent 注册表，通过 agent name 查找对应的 AgentSpec |

```python
@dataclass(frozen=True)
class TaskNode:
    node_id: str
    purpose: str
    assigned_agent: str
    depends_on: tuple[str, ...] = ()
```

| 行号 | 代码 | 解释 |
|---|---|---|
| 10 | `@dataclass(frozen=True)` | 冻结 dataclass，实例创建后不可修改——DAG 节点一旦定义就不该被改动，保证图的稳定性 |
| 11 | `class TaskNode:` | DAG 的核心数据结构：一个任务节点 |
| 12 | `node_id: str` | 节点唯一标识符，如 `"n1_policy"`，在整个 DAG 中不可重复 |
| 13 | `purpose: str` | 任务目的描述，即发给 Agent 的 prompt 主体内容 |
| 14 | `assigned_agent: str` | 指定执行此任务的 Agent 名称，对应 `AGENT_MATRIX` 的 key |
| 15 | `depends_on: tuple[str, ...] = ()` | 前置依赖的 node_id 元组。空元组（默认值）表示无依赖，可以最先执行。使用 `tuple` 而非 `list` 以确保不可变性 |

```python
TRAVEL_DAG: tuple[TaskNode, ...] = (
    TaskNode(
        node_id="n1_policy",
        purpose="核对杭州出差的差旅制度：市内交通限额、餐补和住宿标准",
        assigned_agent="company-policy",
    ),
    TaskNode(
        node_id="n2_facts",
        purpose="核实杭州本周天气、西湖景区开放时间和市内交通方式，列出仍缺的信息",
        assigned_agent="demo-reviewer",
    ),
    TaskNode(
        node_id="n3_brief",
        purpose="结合差旅制度和核实信息，生成出差行程与预算复核摘要",
        assigned_agent="demo-reporter",
        depends_on=("n1_policy", "n2_facts"),
    ),
)
```

| 行号 | 代码 | 解释 |
|---|---|---|
| 18 | `TRAVEL_DAG: tuple[TaskNode, ...] = (` | 用元组而非列表定义 DAG，强调"图结构建好后不应增删节点"。类型标注 `tuple[TaskNode, ...]` 表示可变长度的 TaskNode 元组 |
| 19-23 | `TaskNode(node_id="n1_policy", ...)` | 节点 1：差旅制度核查。`depends_on` 取默认值空元组——无前置依赖，可最先执行。分配给 `company-policy` Agent |
| 24-28 | `TaskNode(node_id="n2_facts", ...)` | 节点 2：实地信息核实。同样无前置依赖，与 n1 无直接依赖关系——二者可并发执行。分配给 `demo-reviewer` Agent |
| 29-34 | `TaskNode(node_id="n3_brief", depends_on=("n1_policy", "n2_facts"), ...)` | 节点 3：方案汇总。**依赖 n1 和 n2**——这是 DAG "有向无环图" 结构的核心体现。只有 n1 和 n2 都完成后，n3 才能执行。分配给 `demo-reporter` Agent |

> 💡 **核心洞见**：`TRAVEL_DAG` 的依赖关系 `n3 → {n1, n2}` 是 DAG 的典型结构——两个独立任务并行产出中间结果，下游节点接收并整合。这种"分-合"模式是多 Agent 编排中最常见也最实用的范式。

```python
def topological_order(nodes: tuple[TaskNode, ...]) -> list[TaskNode]:
    by_id = {node.node_id: node for node in nodes}
    pending = set(by_id)
    completed: set[str] = set()
    ordered: list[TaskNode] = []

    while pending:
        ready = sorted(
            node_id
            for node_id in pending
            if set(by_id[node_id].depends_on) <= completed
        )
        if not ready:
            raise ValueError("DAG 中存在循环依赖或缺失节点")
        for node_id in ready:
            ordered.append(by_id[node_id])
            completed.add(node_id)
            pending.remove(node_id)
    return ordered
```

| 行号 | 代码 | 解释 |
|---|---|---|
| 38 | `def topological_order(...)` | 拓扑排序函数：输入节点元组，返回按依赖关系排好序的节点列表 |
| 39 | `by_id = {node.node_id: node for node in nodes}` | 构建 `node_id → TaskNode` 的索引字典，O(1) 快速查找 |
| 40 | `pending = set(by_id)` | 待处理节点集合，初始包含所有节点 |
| 41 | `completed: set[str] = set()` | 已完成节点集合，用于判断依赖是否满足 |
| 42 | `ordered: list[TaskNode] = []` | 排好序的结果列表 |
| 44-49 | `while pending:` 循环体 | **核心算法**：每轮找出所有依赖已满足的节点（`depends_on ⊆ completed`），加入就绪队列 |
| 46-48 | `set(by_id[node_id].depends_on) <= completed` | **关键判定**：集合子集运算。节点的所有依赖都在 `completed` 中时，该节点就绪。对于 `depends_on=()` 的节点，空集是任何集合的子集，因此第一轮就可执行 |
| 49 | `sorted(...)` | 按 node_id 字母序排序，保证相同条件下执行顺序可复现 |
| 50-51 | `if not ready: raise ValueError(...)` | 若某一轮找不到任何就绪节点，说明图中存在循环依赖或引用了不存在的 node_id。这是防御性编程 |
| 52-55 | `for node_id in ready:` | 将就绪节点依次加入结果列表，标记为完成，移出待处理集合 |
| 56 | `return ordered` | 返回拓扑序排列的节点列表。对 TRAVEL_DAG 而言，结果顺序为 `[n1_policy, n2_facts, n3_brief]`（n1 和 n2 的顺序取决于字母序，n3 最后） |

> ⚠️ **注意事项**：`sorted()` 保证的是 `n1_policy` 在 `n2_facts` 之前（字母序 `p` < `r`），但这两个节点并无实际依赖。在生产环境中，同层无依赖节点应该**并发执行**而非串行。这里为了教学简洁性采用了串行写法，真正的并发执行将在第 19 课展开。

```python
async def run_travel_dag(
    nodes: tuple[TaskNode, ...] = TRAVEL_DAG,
    *,
    cwd: str | Path | None = None,
) -> dict[str, AcpTaskResult]:
    """按拓扑序委派；默认全部连接课程内置的本地 ACP Agent。"""
    results: dict[str, AcpTaskResult] = {}
    for node in topological_order(nodes):
        upstream = "\n\n".join(
            f"[{dep}]\n{results[dep].text}" for dep in node.depends_on
        )
        prompt = node.purpose
        if upstream:
            prompt += f"\n\n上游产出：\n{upstream}"
        results[node.node_id] = await run_acp_task(
            AGENT_MATRIX[node.assigned_agent],
            prompt,
            cwd=cwd,
        )
    return results
```

| 行号 | 代码 | 解释 |
|---|---|---|
| 59-63 | 函数签名 | `run_travel_dag` 是整个模块的入口函数。`nodes` 默认使用 `TRAVEL_DAG`。`*` 强制后续参数为仅关键字参数。`cwd` 指定 Agent 的工作目录 |
| 65 | `results: dict[str, AcpTaskResult] = {}` | 缓存所有节点的执行结果，key 为 `node_id`，用于上游结果注入下游 |
| 66 | `for node in topological_order(nodes):` | **主循环**：按拓扑序逐个处理节点。拓扑序保证了处理当前节点时，其所有依赖已经完成且结果在 `results` 中可用 |
| 67-69 | `upstream = "\n\n".join(...)` | **上游产出注入机制的核心**：对当前节点的每个依赖，从 `results` 中取出对应文本，格式化为 `[node_id]\n{文本内容}`。多个上游结果用两个换行分隔 |
| 70 | `prompt = node.purpose` | prompt 基础部分就是节点的 `purpose` 字段 |
| 71-72 | `if upstream: prompt += f"\n\n上游产出：\n{upstream}"` | **关键操作**：如果有上游结果，将它们追加到 prompt 末尾。这样 Agent 在执行时就能"看见"前置任务的完整输出 |
| 73-77 | `results[node.node_id] = await run_acp_task(...)` | 通过 ACP 将组装好的 prompt 发送给对应 Agent，等待结果并存入 `results`。`AGENT_MATRIX[node.assigned_agent]` 将 agent name 映射为 `AgentSpec` |
| 78 | `return results` | 返回完整的执行结果字典，供调用方进行后续汇总 |

---

### 6.3 Planner 的工作原理

#### 🧠 直观理解

Planner 就像一位项目经理，手里有一份"能力清单"（哪些 Agent 可用、各擅长什么）和一份"任务描述"（需要达成什么目标），它需要画出一张"工作流程图"——谁先做、谁后做、谁等谁。

#### 📖 详细解释

##### 左右图对照：从可选项到合流

```
  左侧：可选行动项（给 Planner 的输入）          右侧：编排好的合流（Planner 的输出）
  ┌──────────────────────────────┐            ┌──────────────────────────────┐
  │                              │            │                              │
  │  ┌────────────────────┐      │            │  ┌────────────────────┐      │
  │  │ Agent: codex       │      │            │  │ 北京→杭州方案        │      │
  │  │ 擅长代码分析/搜索   │──────┤  Planner   │  │ → codex            │      │
  │  └────────────────────┘      │   (LLM)    │  └─────────┬──────────┘      │
  │                              │            │            │                 │
  │  ┌────────────────────┐      │            │  ┌─────────┴──────────┐      │
  │  │ Agent: claude code  │      │            │  │ 1日游方案           │      │
  │  │ 擅长多步推理        │──────┤    ───▶    │  │ → claude code      │      │
  │  └────────────────────┘      │            │  └─────────┬──────────┘      │
  │                              │            │            │                 │
  │  ┌────────────────────┐      │            │  ┌─────────┴──────────┐      │
  │  │ Agent: openclaw    │      │            │  │ 50元团餐            │      │
  │  │ 擅长网络信息检索    │──────┤            │  │ → openclaw         │      │
  │  └────────────────────┘      │            │  └─────────┬──────────┘      │
  │                              │            │            │                 │
  │  ┌────────────────────┐      │            │  ┌─────────┴──────────┐      │
  │  │ model_request      │      │            │  │ 模型汇总            │      │
  │  │ → deepseek /       │──────┤            │  │ → qwen2.5:7b       │      │
  │  │   qwen2.5:7b       │      │            │  └────────────────────┘      │
  │  └────────────────────┘      │            │                              │
  │                              │            │                              │
  └──────────────────────────────┘            └──────────────────────────────┘
```

##### Planner 给模型提供的信息

Planner（背后的 LLM，如 DeepSeek）需要三类信息才能做出正确的编排决策：

1. **allowed capabilities**：可选的能力块。在第 16 课中是 `model_request` 和 `web_search` 二选一；在第 17 课中升级为 `agent: codex`、`agent: claude code`、`agent: openclaw`、`model_request` 四种可选块。

2. **agent 能力描述**：每个 Agent 擅长什么。例如：
   - `codex`：擅长代码分析，能从大量文档中提炼方案
   - `claude code`：擅长多步推理，适合做一日游这种需要综合考虑的规划
   - `openclaw`：擅长网络信息检索，适合查找具体的价格和商家信息
   - `qwen2.5:7b`：本地模型，成本低，适合做最终的文字汇总

3. **任务目标**：自然语言描述的整体目标。"为北京到杭州的出差做全套行程规划，包括交通方案、一日游建议、以及人均 50 元的团餐推荐"。

> 💡 **核心洞见**：Planner 背后的模型就像一个聪明的调度员——它不需要自己执行任务，只需要理解"谁适合做什么"并画出任务图。因此 Planner 模型可以选择成本较低但推理能力足够的模型（如 DeepSeek），而真正执行任务的 Agent 可以使用最强的模型。

##### 从 web_search 块到 agent 任务的思维转变

| 第 16 课（web_search 时代） | 第 17 课（agent 时代） |
|---|---|
| Planner 选：`web_search(query="北京到杭州方案")` | Planner 选：`agent: codex, task="北京到杭州方案"` |
| 执行方式：调用搜索引擎 API | 执行方式：通过 ACP 连接 codex Agent |
| 结果：网页链接 + 摘要片段 | 结果：Agent 深度推理后的结构化方案 |
| Planner 选：`web_search(query="杭州1日游")` | Planner 选：`agent: claude code, task="杭州1日游方案"` |
| Planner 选：`web_search(query="杭州50元团餐")` | Planner 选：`agent: openclaw, task="杭州50元团餐"` |
| 汇总：`model_request` 接收三个搜索结果 | 汇总：`model_request` 接收三个 Agent 的专业产出 |

> 🔗 **关联知识**：这里 Planner 的实现代码在第 16 课「Skills 执行与校验」中详细讲解。本课的重点是：**Planner 的选择对象从"工具"变成了"Agent"**，而 Agent 的执行通道正是我们第 17 课搭建的 ACP 层。

---

### 6.4 执行流程走读

#### 🔄 完整执行流程

```
                        ┌──────────────┐
                        │  run_travel   │
                        │  _dag()      │
                        └──────┬───────┘
                               │
                               ▼
                        ┌──────────────┐
                        │ topological  │
                        │ _order()     │  返回: [n1_policy, n2_facts, n3_brief]
                        └──────┬───────┘
                               │
                               ▼
              ┌────────────────────────────────────┐
              │        遍历拓扑序节点                 │
              └────────────────┬───────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
   │ n1_policy   │     │ n2_facts    │     │ n3_brief    │
   │ depends_on  │     │ depends_on  │     │ depends_on  │
   │   = ()      │     │   = ()      │     │ = (n1, n2)  │
   │ upstream="" │     │ upstream="" │     │ upstream=   │
   └──────┬──────┘     └──────┬──────┘     │ n1.text +   │
          │                   │            │ n2.text     │
          │                   │            └──────┬──────┘
          ▼                   ▼                   │
   ┌─────────────┐     ┌─────────────┐            │
   │ ACP →       │     │ ACP →       │            │
   │ company-    │     │ demo-       │            │
   │ policy      │     │ reviewer    │            │
   └──────┬──────┘     └──────┬──────┘            │
          │                   │                   │
          ▼                   ▼                   ▼
   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
   │ 结果存入     │     │ 结果存入     │     │ ACP →       │
   │ results     │     │ results     │     │ demo-       │
   │ ["n1_       │     │ ["n2_       │     │ reporter    │
   │  policy"]   │     │  facts"]    │     └──────┬──────┘
   └─────────────┘     └─────────────┘            │
                                                  ▼
          ┌──────────────────────────────────────────────┐
          │            results 完整字典                    │
          │                                              │
          │  {                                           │
          │    "n1_policy": AcpTaskResult(text="..."),   │
          │    "n2_facts":  AcpTaskResult(text="..."),   │
          │    "n3_brief":  AcpTaskResult(text="..."),   │
          │  }                                           │
          └──────────────────────┬───────────────────────┘
                                 │
                                 ▼
          ┌──────────────────────────────────────────────┐
          │           汇总模型（可选）                      │
          │                                              │
          │  将所有 results 拼接为 prompt                │
          │  发送给 model（如 qwen2.5:7b）                 │
          │  生成最终的出差行程报告                        │
          └──────────────────────────────────────────────┘
```

#### 📖 执行器两步走

执行器（即 `run_travel_dag` 中的主循环）的实际工作可以抽象为两个阶段：

**阶段 1：找 depends_on 为空的节点入队**

拓扑排序算法在每一轮迭代中，扫描所有未完成节点，找出那些所有依赖都已满足的节点。对于第一轮来说，`depends_on=()` 的节点（n1_policy 和 n2_facts）会被立即选中，放入就绪队列。这两个节点之间没有依赖关系，因此在理论上可以并发执行。

**阶段 2：执行 + 解锁下游**

就绪节点执行完毕后，将其 node_id 加入 `completed` 集合。下一轮迭代时，拓扑排序会重新扫描，此时 n3_brief 的依赖 `{"n1_policy", "n2_facts"}` 已经是 `completed` 的子集，n3_brief 得以"解锁"，进入执行队列。n3_brief 的 prompt 中已经包含了 n1 和 n2 的完整输出文本。

```python
# 上游产出注入的核心代码
upstream = "\n\n".join(
    f"[{dep}]\n{results[dep].text}" for dep in node.depends_on
)
prompt = node.purpose
if upstream:
    prompt += f"\n\n上游产出：\n{upstream}"
```

这段代码的含义：
- `node.depends_on` 对 n3_brief 来说是 `("n1_policy", "n2_facts")`
- `results["n1_policy"].text` 是 company-policy Agent 返回的完整文本（如"杭州差旅制度：市内交通日报销上限 100 元..."）
- `results["n2_facts"].text` 是 demo-reviewer Agent 返回的完整文本（如"杭州本周多云，气温 28-35°C，西湖全天开放..."）
- 拼接后 n3_brief 收到的 prompt 变成：`"结合差旅制度和核实信息，生成出差行程与预算复核摘要\n\n上游产出：\n[n1_policy]\n杭州差旅制度：市内交通日报销上限 100 元...\n\n[n2_facts]\n杭州本周多云，气温 28-35°C，西湖全天开放..."`

> 💡 **核心洞见**：上游产出的注入不是简单的字符串拼接——它模拟了人类协作中的"工作交接"：下游人员拿到上游的完整报告，在此基础上继续工作。Agent 看到的不只是"前面的任务做完了"，而是"前面的任务具体产出了什么"。

#### 📊 任务回收与汇总模型

所有节点执行完毕后，`run_travel_dag` 返回一个完整的 `dict[str, AcpTaskResult]`。调用方可以选择：

1. **直接使用**：如果 n3_brief 已经是一份完整的摘要，那么它的结果就可以直接作为最终输出。
2. **汇总模型加工**：将所有结果拼接为一个 prompt，发送给一个专门负责汇总的模型（如 qwen2.5:7b）进行最终润色和格式整理。

```python
# 汇总阶段伪代码
results = await run_travel_dag()
all_outputs = "\n\n---\n\n".join(
    f"## {node_id}\n{r.text}" for node_id, r in results.items()
)
summary_prompt = f"以下是出差规划的各项产出，请整合为一份完整的出差报告：\n\n{all_outputs}"
final_report = await model_request(summary_prompt, model="qwen2.5:7b")
```

> 💡 **核心洞见**：汇总模型和 Planner 模型可以是不同的模型。Planner 需要较强的推理能力做任务拆解和编排决策（用 DeepSeek），而汇总模型只需要做文本整合（用成本更低的本地模型 qwen2.5:7b）。这种"分模型、分角色"的策略是成本优化的关键手段。

---

### 6.5 编排策略选择

#### 🤔 Q&A：编排是模型控制还是人控制？

> **🙋 学员问题（五八同学）**：多 Agent 协作中，编排是模型控制的还是人控制的？谁决定哪个任务给哪个 Agent？

**💬 老师回答**：

编排的决策者是 **Planner**，而 Planner 的背后可以是一个 LLM（如 DeepSeek）。所以答案是：**编排由模型控制**，但模型的能力边界由人设定。

具体来说：
- **人设定"可选范围"**：在 `allowed capabilities` 中，人规定了 Planner 可以从哪些能力块中选择。例如"你可以选 codex、claude code 或 openclaw 这三种 Agent，也可以选 model_request 直接调模型"。Planner 不能超出这个范围。
- **模型做"决策"**：Planner（DeepSeek）根据任务描述和每个能力块的描述，自主决定"北京到杭州方案给 codex，1 日游给 claude code，50 元团餐给 openclaw"。

这种模式可以类比为：老板（人）给了项目经理（Planner/LLM）一份"可用人员名单及其技能描述"，项目经理根据项目需求自主分配任务。老板不干涉具体分配，但控制了谁能上项目。

---

#### 🤔 编排策略选择：DAG Planner vs 手动编排 vs TriggerFlow

```
遇到 多 Agent 协同任务 时：
    │
    ├── 任务之间存在明确的依赖关系？
    │   ├── 是 → 任务组合是固定的？
    │   │   ├── 是 → 使用【手动编排】
    │   │   │       直接写死 TaskNode 和 depends_on，如 TRAVEL_DAG
    │   │   │       优点：简单、可预测、无 LLM 成本
    │   │   │       缺点：无法适应任务变化
    │   │   │
    │   │   └── 否（任务组合每次不同）→ 使用【DAG Planner】
    │   │           由 LLM 动态编排任务图
    │   │           优点：灵活、适应性强
    │   │           缺点：依赖 LLM 质量、有额外成本
    │   │
    │   └── 否 → 任务需要事件驱动？
    │       ├── 是 → 使用【TriggerFlow】
    │       │       当某个条件触发时启动对应 Agent
    │       │       优点：松耦合、响应式
    │       │       缺点：调试复杂、流程不可见
    │       │
    │       └── 否 → 使用【简单并发】
    │               所有 Agent 同时启动，各自独立完成任务
```

| 编排策略 | 适用场景 | 核心机制 | 优点 | 缺点 |
|---|---|---|---|---|
| **DAG Planner** | 任务组合不固定、依赖关系复杂 | LLM 动态生成任务图 | 灵活、可处理未知任务 | 依赖模型质量、有 token 成本 |
| **手动编排** | 任务组合固定、依赖关系明确 | 人工写死 TaskNode | 简单可靠、零推理成本 | 无法适应变化 |
| **TriggerFlow** | 事件驱动的响应式场景 | 事件触发 Agent 启动 | 松耦合、实时响应 | 调试困难、流程不透明 |
| **简单并发** | 任务无依赖、各自独立 | 所有 Agent 同时启动 | 速度最快 | 无法处理有依赖的任务 |

> ⚠️ **注意事项**：本课程展示的 `TRAVEL_DAG` 是手动编排的示例——三个节点的依赖关系是人工设计的。但在实际企业场景中，如果每天要处理的出差目的地、任务类型都不同，就需要 DAG Planner（LLM 驱动）来动态编排。两种方式不是互斥的，可以在同一个系统中混合使用。

---

### 📋 课程小结

#### 🗺️ 知识图谱

```
                    ┌──────────────────────────┐
                    │    DAG + ACP 编排实战      │
                    └────────────┬─────────────┘
                                 │
            ┌────────────────────┼────────────────────┐
            │                    │                    │
            ▼                    ▼                    ▼
    ┌───────────────┐    ┌──────────────┐    ┌──────────────┐
    │  TaskNode     │    │  Planner     │    │  编排策略     │
    │  ▸ node_id    │    │  ▸ LLM驱动   │    │  ▸ DAG       │
    │  ▸ purpose    │    │  ▸ 可选块    │    │    Planner   │
    │  ▸ agent      │    │  ▸ 编排合流  │    │  ▸ 手动编排   │
    │  ▸ depends_on │    │              │    │  ▸ Trigger   │
    └───────┬───────┘    └──────┬───────┘    │    Flow     │
            │                   │            └──────────────┘
            ▼                   ▼
    ┌───────────────┐    ┌──────────────┐
    │ 拓扑排序       │    │  执行引擎     │
    │ ▸ 入度法       │    │  ▸ ACP分发   │
    │ ▸ 循环检测     │    │  ▸ 上游注入   │
    │ ▸ 并发就绪检测 │    │  ▸ 结果回收   │
    └───────────────┘    └──────────────┘
```

#### 💡 一句话总结

> DAG 解决"按什么顺序做什么"，ACP 解决"怎么把任务传给 Agent"——二者组合，构成了多 Agent 协同编排的完整解决方案。Planner（LLM）决定任务图，执行器按拓扑序驱动 ACP 分发，上游产出自动注入下游，最终由汇总模型整合为完整输出。

#### 📍 系列定位

> 📍 **系列定位**：本文是「Agent架构师企业级智能体系统构建」第 6 篇（共 17+ 篇）。
> - 上一篇：M05-ACP Client 与任务分发运行 — run_acp_task 函数就绪，ACP 通道已通
> - 下一篇：M07-并发执行与异步调度 — 编排完成后，如何让无依赖节点真正并发执行

---

> 🤖 由 transcript-to-doc 生成

## 七、并发执行与异步调度

### 7.1 为什么需要并发 —— 串行 MVP 的问题分析

#### 🧠 直观理解

想象你去餐厅点了三道菜：清蒸鱼、红烧肉、炒青菜。厨房里有三个灶台，但如果按串行模式，厨师只能用一口锅，炒完青菜才能做红烧肉，做完红烧肉才能蒸鱼——明明可以三口锅同时开工，却白白等着。串行执行器的问题一模一样：DAG 里多个互不依赖的任务明明可以同时跑，却被串行的 `for` 循环一个个阻塞等待。

#### 📖 详细解释

回顾 M06 中 `dag_delegate.py` 的 `run_travel_dag` 函数——这是执行器的串行 MVP 版本：

```python
# dag_delegate.py 中的串行执行（简化展示）
async def run_travel_dag(nodes):
    results = {}
    for node in topological_order(nodes):
        # 每个节点必须等上一个节点完全执行完
        results[node.node_id] = await run_acp_task(...)
    return results
```

这段代码先通过 `topological_order()` 算出拓扑排序，然后**逐一出队**。问题出在哪里？以 `TRAVEL_DAG` 为例：

```
n1_policy (查差旅制度) ──┐
                         ├──▶ n3_brief (复核摘要)
n2_facts (核实天气交通) ──┘
```

`n1_policy` 和 `n2_facts` 之间**没有任何依赖关系**。但串行代码会先 `await n1_policy`，等它返回后才 `await n2_facts`。如果每个任务耗时 3 秒，总耗时为 3 + 3 + 3 = 9 秒——而并发执行的理想耗时为 max(3, 3) + 3 = 6 秒，节省 33%。

当 DAG 规模扩大——比如去查 5 个城市的天气——串行会把 5 个并行任务变成 5 倍的时间开销，这是不可接受的。

#### 🔗 推导链：从串行到并发

```
起点: 串行 for loop —— 每个节点 await 到底才进入下一个
  │
  ├── 第1步: 识别并行机会
  │   为什么？DAG 中节点之间的依赖是有向无环的，同一层级
  │   互不依赖的节点天然可以并行
  │
  ├── 第2步: 把所有"没有前置依赖"的节点找出来
  │   为什么？这些节点不等待任何人，是 DAG 的"入口层"——
  │   这就是 go_list 的来源
  │
  ├── 第3步: 用 asyncio.create_task() 把它们同时启动
  │   为什么？create_task 创建协程任务后立即开始执行，不阻塞
  │   调用者——这就是"同时启动"的实现机制
  │
  ├── 第4步: 用 asyncio.gather() 等待这一批全部完成
  │   为什么？下游节点需要上游结果，必须等上游全到位
  │
  └── 结论: 把 go_list 的节点并发启动后，解锁依赖它们的下游节点
      —— 循环此过程直到 DAG 全部执行完毕
```

#### 前后对比

| 维度 | 串行 MVP | 并发版本 |
|---|---|---|
| 执行方式 | `for node in ordered: await task` | `golist → create_task → gather` |
| 并行节点耗时 | T1 + T2 + ... + Tn（累加） | max(T1, T2, ..., Tn)（取最长） |
| 代码复杂度 | 低（一个 for 循环） | 中（需要管理 task 引用和依赖解锁） |
| 适用场景 | 节点少、无并行需求 | IO 密集型多节点 DAG |
| 核心机制 | 顺序 await | asyncio 协程并发 |

> ⚠️ **注意事项**：串行 MVP 不是"错的"——它是一个正确的、可工作的起点。产品开发中先跑通串行再改造并发，是符合敏捷原则的做法。不要跳过 MVP 直接写并发版本，因为并发引入的状态管理复杂度会掩盖业务逻辑的 bug。

---

### 7.2 DAG 并发执行器设计

#### 🧠 直观理解 —— go_list 模式

把 DAG 想象成一个施工项目。每天开工前，工头看一眼施工图："哪些工序的**前置工序全都完成了**？"这些就是今天可以开工的活儿。把它们全部分派给工人同时干，干完了再检查下一批。每天可以开工的活就是当天的 **go_list**。

在 DAG 里，go_list 的定义更简单：**depends_on 为空的节点**就是可以立刻执行的节点。这里"为空"有两层含义：
1. 节点天生没有依赖（DAG 的入口节点）——第一轮的 go_list
2. 节点的所有依赖都已执行完毕——后续轮的 go_list

#### 📖 详细解释 —— DAG 任务图数据结构

老师在设计并发执行器时，首先定义了统一的任务图数据结构。注意这里采用了轻量的 dict 方案，而非上节课 `dag_delegate.py` 中的 `dataclass`，因为教学中更侧重展示并发逻辑本身，避免多余的类定义开销。

```python
# DAG 任务图的数据结构
# 每个节点包含三个字段：
#   id         - 唯一标识符
#   script     - 要执行的异步函数（即 target）
#   depends_on - 前置依赖的节点 id 列表

tasks_graph = [
    {
        "id": "task_1",
        "script": first_task,     # 异步函数引用
        "depends_on": [],         # 空 = 无前置依赖 = 可立即执行
    },
    {
        "id": "task_2",
        "script": first_task,
        "depends_on": [],
    },
    {
        "id": "task_3",
        "script": first_task,
        "depends_on": [],
    },
    {
        "id": "final",
        "script": final_task,
        "depends_on": ["task_1", "task_2", "task_3"],  # 等三个上游都完成
    },
]
```

对应的 DAG 拓扑结构：

```
  task_1 ──┐
           │
  task_2 ──┼──▶ final
           │
  task_3 ──┘
```

三个入口节点（task_1/2/3）共同指向一个汇总节点（final），这是典型的 fan-out → fan-in 模式。

#### go_list 模式详解

go_list 的提取逻辑极其简洁——一行列表推导式即可完成：

```python
# 找出所有 depends_on 为空的节点
go_list = [t for t in tasks_graph if not t["depends_on"]]
# 结果: [task_1, task_2, task_3]
```

老师特别强调：go_list 不是一个一次性的概念。在实际的 DAG 执行器中，go_list 需要**动态更新**——每完成一批任务，就要检查是否有新的节点满足了"所有 depends_on 已完成"的条件，把新就绪的节点加入 go_list，形成一个循环。这与 `dag_delegate.py` 中 `topological_order()` 的 `while pending` 循环思路一致，但把串行的出队改成了并发的启动 + gather。

> 💡 **核心洞见**：go_list 本质上是对拓扑排序每一层的**批量并发**。拓扑排序告诉你"这些节点可以放在同一层"，go_list 让你"把这一层全部同时启动"。这就是串行拓扑向并发执行的跃迁点。

---

### 7.3 💻 并发改造 Step-by-Step

#### 🎯 目标

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 用 `asyncio.create_task()` 同时启动多个协程
> - [ ] 用 `asyncio.gather()` 等待并收集所有任务的结果
> - [ ] 实现 go_list 模式：找出 depends_on 为空的节点并并发执行
> - [ ] 将串行 DAG 执行器改造为并发版本

#### 🏗️ 前置准备

- Python 3.7+（asyncio 标准库）
- 理解 DAG 有向无环图的依赖关系（详见 M06）
- 理解 `async/await` 语法基础

#### Step 1: 定义模拟任务函数

老师用 `random.sleep` 模拟不同任务的不同执行耗时，这是教学中的经典手法——"用 sleep 让等待变得可见"。

```python
import asyncio
import random

# ---------- 模拟任务函数 ----------
async def first_task(task_id: str) -> dict:
    """
    模拟一个独立的前置任务。
    每个任务随机等待 0.5~3.0 秒后返回结果。
    三个 first_task 共享同一个函数体，但通过 task_id 区分身份。
    """
    delay = random.uniform(0.5, 3.0)
    print(f"  [{task_id}] 启动，预计耗时 {delay:.2f}s")
    await asyncio.sleep(delay)
    print(f"  [{task_id}] 完成 ✅")
    return {"task_id": task_id, "delay": round(delay, 2)}
```

> 老师的设计选择：三个 first_task 使用**同一个函数**，通过参数 `task_id` 区分。这是教学场景的简化——生产代码中每个节点可能指向完全不同的异步函数，但 create_task / gather 的调度逻辑完全一致。

```python
async def final_task(results: list[dict]) -> dict:
    """
    汇总所有上游 first_task 的结果。
    只有当三个 first_task 全部完成后才会被调用。
    """
    print(f"\n  [final_task] 收到 {len(results)} 个上游结果，开始汇总...")
    task_ids = [r["task_id"] for r in results]
    total_delay = sum(r.get("delay", 0) for r in results)
    return {
        "status": "汇总完成",
        "上游任务": task_ids,
        "上游总耗时": round(total_delay, 2),
    }
```

#### Step 2: 构建 DAG 任务图

```python
# ---------- DAG 任务图 ----------
# 课程的核心数据结构：id 标识节点，script 指向执行函数，depends_on 定义依赖
tasks_graph = [
    {"id": "task_1", "script": first_task, "depends_on": []},
    {"id": "task_2", "script": first_task, "depends_on": []},
    {"id": "task_3", "script": first_task, "depends_on": []},
    {"id": "final",  "script": final_task, "depends_on": ["task_1", "task_2", "task_3"]},
]
```

#### Step 3: 找 go_list —— 并发入口

```python
# 所有 depends_on 为空的节点 = 可以立即执行
go_list = [t for t in tasks_graph if not t["depends_on"]]
print(f"go_list: {[t['id'] for t in go_list]}")
# 输出: go_list: ['task_1', 'task_2', 'task_3']
```

这一步是整个并发改造的"开关"。串行版本里所有节点排成一个队列逐一执行；并发版本区分了"现在就绪"和"等待上游"两类节点。

#### Step 4: asyncio.create_task() 并发启动

```python
# ---------- 并发调度逻辑 ----------
task_futures: list[asyncio.Task] = []

for task_def in go_list:
    # task_def["script"] 是 first_task 函数的引用
    # 传入 task_id 作为首次调用的参数
    coro = task_def["script"](task_def["id"])
    # create_task：将协程包装为 Task 对象，立即开始执行（不阻塞）
    future = asyncio.create_task(coro)
    task_futures.append(future)

print(f"已创建 {len(task_futures)} 个并发任务，等待完成...")
```

> `asyncio.create_task(coro)` 是关键的并发转折点。它把协程注册到事件循环中，立即开始执行——不等待返回。如果你写成 `await task_def["script"](...)`，那就退化回串行了：第二个任务必须等第一个结束才能开始。**create_task 的区别就是：不 await，先启动，回头再收结果。**

#### Step 5: asyncio.gather() 等待回收

```python
# gather：等待 task_futures 列表中的所有 Task 全部完成
# 返回值按入参顺序排列（不是按完成顺序）
first_results = await asyncio.gather(*task_futures)

print(f"\n>>> 第一批全部完成，结果: {first_results}")
```

`asyncio.gather()` 做了三件事：
1. **等待**所有传入的 Task 完成
2. **收集**返回值（保持传入顺序）
3. **传播异常**：如果任一 Task 抛异常，gather 会抛出

这里 `*task_futures` 解包将列表展开为 `gather(task1, task2, task3)` 的形式。

#### Step 6: 解锁下游 —— 执行 final_task

```python
# 找出依赖第一批任务的节点（depends_on 包含 task_1/2/3）
final = [t for t in tasks_graph if t["id"] == "final"][0]
final_result = await final["script"](list(first_results))
print(f">>> 汇总结果: {final_result}")
```

> 在这个简化的教学演示中，final_task 不通过 create_task 启动，而是直接 await，因为它是唯一的、没有并行需求的汇总节点。**完整的 DAG 并发执行器则需要把"解锁下游→加入 go_list→create_task→gather"形成循环**，这样可以处理多层级的复杂依赖。这是留给后续扩展的练习。

#### ✅ 完整可运行代码

```python
# 文件名: concurrent_dag.py
# 功能: DAG 并发执行器教学演示 —— 三个并行 first_task → 汇总 final_task

import asyncio
import random
import time


# ============================================================
# 任务函数定义
# ============================================================
async def first_task(task_id: str) -> dict:
    """模拟独立前置任务，随机耗时 0.5~3.0 秒"""
    delay = random.uniform(0.5, 3.0)
    t0 = time.time()
    print(f"  [{task_id}] 启动 @ {time.strftime('%H:%M:%S')}")
    await asyncio.sleep(delay)
    print(f"  [{task_id}] 完成 ✅ 耗时 {delay:.2f}s")
    return {"task_id": task_id, "delay": round(delay, 2)}


async def final_task(results: list[dict]) -> dict:
    """汇总所有上游结果"""
    print(f"\n  [final_task] 开始汇总 {len(results)} 个上游结果...")
    return {
        "status": "汇总完成",
        "上游任务": [r["task_id"] for r in results],
        "上游总耗时": round(sum(r.get("delay", 0) for r in results), 2),
    }


# ============================================================
# DAG 任务图
# ============================================================
TASKS_GRAPH = [
    {"id": "task_1", "script": first_task, "depends_on": []},
    {"id": "task_2", "script": first_task, "depends_on": []},
    {"id": "task_3", "script": first_task, "depends_on": []},
    {"id": "final",  "script": final_task, "depends_on": ["task_1", "task_2", "task_3"]},
]


# ============================================================
# 并发执行器
# ============================================================
async def run_concurrent():
    print("=" * 50)
    print("  DAG 并发执行器演示")
    print("=" * 50)

    total_start = time.time()

    # Step 1: 找 go_list
    go_list = [t for t in TASKS_GRAPH if not t["depends_on"]]
    print(f"\n📋 go_list: {[t['id'] for t in go_list]}")

    # Step 2: 并发启动
    task_futures = []
    for task_def in go_list:
        coro = task_def["script"](task_def["id"])
        task_futures.append(asyncio.create_task(coro))
    print(f"🚀 已创建 {len(task_futures)} 个并发任务\n")

    # Step 3: 等待第一批完成
    first_results = await asyncio.gather(*task_futures)
    print(f"\n📦 第一批全部完成")

    # Step 4: 解锁下游
    final = [t for t in TASKS_GRAPH if t["id"] == "final"][0]
    final_result = await final["script"](list(first_results))

    total_elapsed = time.time() - total_start
    print(f"\n{'=' * 50}")
    print(f"🏁 全部完成！总耗时 {total_elapsed:.2f}s")
    print(f"📊 最终结果: {final_result}")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    asyncio.run(run_concurrent())
```

---

### 7.4 运行效果验证 —— 并发时间线

将上面的代码保存为 `concurrent_dag.py` 并运行，你会看到类似如下的输出（因为随机数，每次运行的具体秒数不同，但**同时启动**的规律不变）：

```
==================================================
  DAG 并发执行器演示
==================================================

📋 go_list: ['task_1', 'task_2', 'task_3']
🚀 已创建 3 个并发任务

  [task_1] 启动 @ 09:40:05
  [task_2] 启动 @ 09:40:05
  [task_3] 启动 @ 09:40:05
  [task_3] 完成 ✅ 耗时 1.20s
  [task_1] 完成 ✅ 耗时 2.14s
  [task_2] 完成 ✅ 耗时 2.83s

📦 第一批全部完成

  [final_task] 开始汇总 3 个上游结果...

==================================================
🏁 全部完成！总耗时 2.85s
📊 最终结果: {'status': '汇总完成', '上游任务': ['task_1', 'task_2', 'task_3'], '上游总耗时': 6.17}
==================================================
```

**关键观察点**：

1. **同时启动**：三个 task 都在 `09:40:05` 启动——印证了 `create_task` 的"立即开始"语义
2. **完成顺序不等于启动顺序**：task_3（1.20s）先完成，task_2（2.83s）最后完成——谁的活儿先干完谁先报
3. **总耗时 = 最长耗时**：2.85s ≈ task_2 的 2.83s（+ 极小开销），而不是三个耗时的累加（1.20 + 2.14 + 2.83 = 6.17s）
4. **final_task 在 gather 后才执行**：等三个全部结束了才进入汇总

> 老师现场演示时把 `sleep` 时间拉长到 3 秒，让"同时启动→先后完成"的效果更加肉眼可见。他在课上特意指出："先完成三再完成一再完成——同时启动的时间是瞬间并发出去的，回来时间不一样。"

**如果改成串行**，同样的任务耗时顺序，事件线会变成：

```
  [task_1] 启动 → 完成 (2.14s)
  [task_2] 启动 → 完成 (2.83s)    ← 白白等了 2.14s
  [task_3] 启动 → 完成 (1.20s)    ← 白白等了 4.97s
  总耗时 ≈ 6.17s                   ← 比并发版慢 2.16 倍
```

这就是并发改造的核心收益：**把互不依赖的等待时间从累加变为取最大值**。

---

### 7.5 TriggerFlow 替代方案

课堂上老师提到，除了手写 `asyncio.create_task` + `gather`，还可以用 **TriggerFlow** 的声明式编排来实现同样的并发效果：

```python
# TriggerFlow 伪代码——声明式 DAG 并发
from triggerflow import Flow, start, when

flow = Flow("travel_dag")

# 无依赖的节点：直接从 start 事件触发
flow.add_node("task_1", target=first_task, trigger=start)
flow.add_node("task_2", target=first_task, trigger=start)
flow.add_node("task_3", target=first_task, trigger=start)

# 有依赖的节点：when(上游全部完成)
flow.add_node("final", target=final_task, trigger=when(
    depends_on=["task_1", "task_2", "task_3"]
))
```

TriggerFlow 的核心思路：**把依赖关系从代码逻辑中提取到声明配置里**。
- `start` 表示节点在流启动时立即执行（等价于 depends_on 为空）
- `when(depends_on=[...])` 表示等指定的上游节点全部完成后自动触发

| 维度 | asyncio 手写并发 | TriggerFlow |
|---|---|---|
| 依赖表达 | 代码中显式判断 depends_on | 声明式 `when()` |
| go_list 管理 | 手动遍历、创建 task、gather | 框架自动调度 |
| 学习成本 | 低（标准库） | 中（需了解框架 DSL） |
| 灵活性 | 高（完全控制调度细节） | 中（受框架 DSL 限制） |
| 可视化 / 监控 | 需自行实现 | 框架内置 DAG 可视化 |
| 错误处理 | 手动 try/except | 框架级重试与降级 |
| 适用规模 | 小型 DAG、教学、原型 | 大型生产级多节点编排 |

> 💡 **核心洞见**：TriggerFlow 的 `when(depends_on)` 本质上就是框架帮你做了"等上游完成→解锁下游"的循环。它没有创造新能力，而是把你在 `run_concurrent()` 里手写的 4 步变成了配置。选择哪个方案取决于你需要多精细的控制。

---

### 7.6 决策树：何时用 asyncio / TriggerFlow / 串行

```
你的 DAG 任务图需要执行器，选哪个方案？
    │
    ├── 所有节点互相依赖（链表式 DAG）？
    │   └── 是 → 串行（并发无收益，别加复杂度）
    │
    ├── 节点总数 < 5，层级深度 < 2？
    │   ├── 是 → asyncio 手写（轻量、无框架依赖）
    │   └── 否 → 继续
    │
    ├── 需要可视化监控、任务重试、超时控制？
    │   ├── 是 → TriggerFlow（框架级能力开箱即用）
    │   └── 否 → 继续
    │
    ├── 每个节点的执行逻辑高度定制（不同 agent、不同协议）？
    │   ├── 是 → asyncio 手写（完全控制每个节点的调用方式）
    │   └── 否 → TriggerFlow（统一的任务抽象足够）
    │
    └── 团队有 Python asyncio 经验但不想引入新框架？
        └── 是 → asyncio 手写（标准库，零依赖）
```

**协程 vs 多线程**：老师特别强调了这一点。

在 Python 中，`asyncio` 使用的是**协程（coroutine）模型**，而不是多线程。两者的关键区别：

| 维度 | asyncio 协程 | threading 多线程 |
|---|---|---|
| 并发模型 | 单线程，事件循环调度 | 多线程，操作系统调度 |
| 切换成本 | 极低（用户态，await 点切换） | 较高（内核态，GIL 争抢） |
| 适合场景 | IO 密集型（网络请求、文件读写） | CPU 密集型（计算） |
| Python 限制 | 不受 GIL 影响 | 受 GIL 限制，不能真正并行计算 |
| 调试复杂度 | 低（单线程，出问题容易追踪） | 高（竞态条件、死锁） |
| 本课程场景 | ✅ 所有 Agent 调用都是网络 IO | ❌ 多线程的 GIL 反而拖慢 IO 密集型任务 |

> ⚠️ **注意事项**：如果你在 `first_task` 里写的是 CPU 密集型计算（比如大矩阵运算），`asyncio.create_task` 不会让它更快——因为只有一个线程在跑。asyncio 的并发收益只体现在"大量时间花在等待上"的 IO 密集型任务中。好在 Agent 调用（ACP 协议、HTTP 请求）恰恰是典型的 IO 密集型场景。

---

### 7.7 从教学演示到生产代码 —— 与 dag_delegate.py 的对接

回到 `dag_delegate.py` 中的 `run_travel_dag`。它的串行本质在于：

```python
for node in topological_order(nodes):      # 串行出队
    results[node.node_id] = await run_acp_task(...)  # 等待每一个
```

而 `topological_order()` 已经帮我们按层级排好了顺序。要改造为并发版本，思路是：**同一拓扑层级的节点用 go_list 收集，create_task 并发启动，gather 等待，然后进入下一层**。

改造后的伪代码框架：

```python
async def run_travel_dag_concurrent(nodes):
    results = {}
    by_id = {n.node_id: n for n in nodes}

    # 建立反向索引：谁依赖我（用于解锁下游）
    children_of: dict[str, list[str]] = {n.node_id: [] for n in nodes}
    for n in nodes:
        for dep in n.depends_on:
            children_of[dep].append(n.node_id)

    pending = set(by_id)
    completed: set[str] = set()

    while pending:
        # 找当前可执行的节点（go_list）
        ready = [nid for nid in pending
                 if set(by_id[nid].depends_on) <= completed]

        if not ready:
            break  # 或报错：循环依赖

        # 并发启动
        tasks = {}
        for nid in ready:
            tasks[nid] = asyncio.create_task(
                run_acp_task(AGENT_MATRIX[by_id[nid].assigned_agent], ...)
            )

        # 等待这一层全部完成
        for nid, task in tasks.items():
            results[nid] = await task
            completed.add(nid)
            pending.remove(nid)

    return results
```

这和老师现场演示的 `run_concurrent()` 是同一个模式的完整版——循环 go_list→create_task→gather 直到 DAG 全部完成。层级越多，并发收益越大。

---

## 📋 课程小结

### 🗺️ 知识图谱

```
                  ┌─────────────────────────────┐
                  │       DAG 并发执行器          │
                  │  从串行 MVP 到并发 asyncio    │
                  └──────────────┬──────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          ▼                      ▼                      ▼
  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐
  │   go_list     │    │ create_task   │    │    gather     │
  │   找就绪节点   │    │ + gather      │    │   等待回收    │
  │ depends_on    │    │ 并发启动模式   │    │ 收集所有结果   │
  │ 为空的节点     │    │               │    │               │
  └───────────────┘    └───────────────┘    └───────────────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
            ┌──────────┐ ┌──────────┐ ┌──────────┐
            │ 串行 MVP │ │ asyncio  │ │TriggerFlow│
            │  for 循环│ │ 协程并发 │ │ 声明式编排│
            └──────────┘ └──────────┘ └──────────┘
```

### 💡 一句话总结

> 串行执行器的并发改造只有一个核心动作：把"所有 depends_on 为空的节点"收集为 go_list，用 `asyncio.create_task` 同时启动，用 `asyncio.gather` 统一回收——这个模式让 DAG 的耗时从"累加"变为"取最长"。

### 📍 系列定位

> 📍 **系列定位**：本文是「Agent架构师企业级智能体系统构建」第 7 篇。
> - 上一篇：DAG+ACP 编排实战 — 掌握了任务图的定义和拓扑排序
> - 下一篇：自建 Agent 适配器（Adapter 模式） — 执行器能力扩展到自定义 agent

---

### 📝 课后练习

#### 练习 1: 多层 DAG 并发

**题目**：修改 `run_concurrent()` 使其支持任意深度的 DAG（不仅仅是 2 层）。要求自动识别每一层的 go_list，逐层并发执行，直到所有节点完成。

**验收标准**：
- [ ] 支持 3 层以上依赖（如 task_A, task_B → task_C；task_C, task_D → task_E）
- [ ] 每一层的并发任务数正确（只启动 depends_on 全满足的节点）
- [ ] 总耗时 = 各层最大耗时的累加（而非所有节点耗时的累加）

#### 练习 2: 串行 vs 并发耗时对比

**题目**：用 `time.time()` 分别测量串行版本和并发版本的总耗时，计算加速比。使用 5 个模拟任务，每个随机 sleep 2~5 秒。

**验收标准**：
- [ ] 加速比 > 3x（5 个任务串行约 17.5s，并发约 5s）
- [ ] 输出包含每个方案的耗时和加速比
- [ ] 解释加速比没有达到理想值 5x 的原因（最长任务决定总耗时）

#### 练习 3: 对接 dag_delegate.py

**题目**：将 `dag_delegate.py` 中的 `run_travel_dag` 改造为并发版本，对于 `TRAVEL_DAG`（n1_policy 和 n2_facts 并行，然后 n3_brief），验证总耗时是否从 ~9s 降低到 ~6s。

**验收标准**：
- [ ] n1_policy 和 n2_facts 的输出时间戳相同（证明同时启动）
- [ ] n3_brief 在两者都完成后才启动
- [ ] 实际运行测量加速效果

---

> 🤖 由 transcript-to-doc v4.1 生成

## 八、自建 Agent 适配器（Adapter 模式）

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 理解 Adapter 模式在 ACP 生态中的核心价值：业务代码零修改即可接入协议
> - [ ] 掌握 `demo_acp_agent` 与 `policy_acp_adapter` 的结构异同
> - [ ] 将任意已有 Python 模块按标准模板包装为 ACP Agent
> - [ ] 在 `AGENT_MATRIX` 中注册自己的适配器 Agent

---

### 8.1 Adapter 模式的动机：为什么要加这一层

#### 🧠 直观理解

你已经有了一个能跑的 Python 模块——比如一套差旅制度核查逻辑。它可能已经在 FastAPI 里服务了半年，代码稳定、逻辑完备。现在，你想让它接入 ACP 协议，但**你绝对不想改它**——一改就可能引入 bug，而且这个模块的用户不止 ACP 一个（还有 HTTP 接口、定时任务、本地脚本）。

**Adapter 模式解决的就是这个问题：在已有模块外面包一层薄薄的 ACP 协议壳，模块本身一行不改。**

用生活类比：你有一台日规电器的插头（扁平两脚），但它要插进中国的三孔插座。你不会把电器的线剪了重接——你买一个转换插头（Adapter），一头适配电器，一头适配插座。电器完全不知道自己被"转换"了。

#### 📖 详细解释

在本课程的前几个模块中，我们用 `demo_acp_agent.py` 展示了如何从头构建一个 ACP Agent。当时 `render_reply()` 的回复逻辑就直接写在 Agent 类所在的同一个文件里。这是一种"内联"写法，适合原型和演示。

但在工程中，你通常面对的是"已有资产"——一个沉淀了领域知识的既有模块。强行把它的代码搬进 `prompt()` 方法会带来两个问题：

1. **耦合**：业务逻辑和 ACP 协议搅在一起，日后维护时改一处可能牵动另一处。
2. **复用受限**：如果这个模块还要被 HTTP 端点或命令行调用，你不得不在不同地方维护两套调用方式。

Adapter 模式的做法是三个层次：

```
┌──────────────────────────────────┐
│          ACP 协议层               │  ← 标准化接口（on_connect/initialize/new_session/prompt）
│  TravelPolicyAcpAdapter         │
│       │                          │
│       │ self._module =           │
│       │   TravelPolicyModule()   │
│       ▼                          │
│  ┌─────────────────────────────┐ │
│  │      业务模块层              │ │  ← 纯业务逻辑，完全不知道 ACP 存在
│  │  TravelPolicyModule         │ │
│  └─────────────────────────────┘ │
└──────────────────────────────────┘
```

> 💡 **核心洞见**：适配层只做一件事——把 ACP 协议语（`PromptResponse`、`session_update`）翻译成对业务模块的普通 Python 调用（`module.run(text).render()`）。

---

### 8.2 TravelPolicyModule：纯业务模块逐行解析

在讲适配器之前，先把被适配的"业务模块"看清楚。这是文件 `policy_module.py` 的完整内容，**它不 import 任何 ACP 相关的东西**。

```python
# 文件名: policy_module.py
# 功能: 差旅制度核查模块 —— 纯业务逻辑，与 ACP 无依赖

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyReply:
    decision: str
    checks: tuple[str, ...]

    def render(self) -> str:
        lines = [f"差旅制度核查结论：{self.decision}", "适用规则："]
        lines.extend(f"- {item}" for item in self.checks)
        return "\n".join(lines)
```

#### 8.2.1 PolicyReply：结构化的核查结果

这是一个 `@dataclass(frozen=True)`——冻结意味着不可变，保障线程安全和数据完整性。它有两个字段和一个 `render()` 方法：

| 字段 | 类型 | 含义 |
|---|---|---|
| `decision` | `str` | 最终结论，如"符合制度，可据此安排"或"存在超标项，需补充审批" |
| `checks` | `tuple[str, ...]` | 适用的制度条款列表，不可变元组 |

`render()` 方法把这两个字段格式化为人类可读的文本。它的输出长这样：

```
差旅制度核查结论：存在超标项，需补充审批
适用规则：
- 市内交通：按城市分级限额报销，需保留行程单据
- 餐补：按出差天数和城市标准计发，超标部分自理
- 住宿：不超过岗位对应的城市住宿上限
- 报销：需提供发票、行程和审批记录三项凭证
- 境外出差需提前换汇报备，并适用境外差旅标准
```

这个 `render()` 的输出会被适配器的 `prompt()` 方法直接用作对 Client 的回复文本。

#### 8.2.2 TravelPolicyModule.run()：关键词驱动的规则引擎

```python
class TravelPolicyModule:
    """已有的差旅制度核查模块；它本身不知道 ACP。

    给一段出差任务文本，返回结构化的制度核查结果。这是一个普通 Python 类，
    既可以被 ACP Adapter 调用，也可以继续被 FastAPI、定时任务或本地脚本调用。
    """

    def run(self, prompt: str) -> PolicyReply:
        normalized = prompt.lower()
        checks = [
            "市内交通：按城市分级限额报销，需保留行程单据",
            "餐补：按出差天数和城市标准计发，超标部分自理",
            "住宿：不超过岗位对应的城市住宿上限",
            "报销：需提供发票、行程和审批记录三项凭证",
        ]
        if "国际" in prompt or "境外" in prompt or "overseas" in normalized:
            checks.append("境外出差需提前换汇报备，并适用境外差旅标准")
        if "接待" in prompt or "宴请" in prompt:
            checks.append("接待与宴请走专项审批，不计入个人餐补")

        over_markers = ("超标", "超出限额", "超预算")
        decision = "存在超标项，需补充审批" if any(m in prompt for m in over_markers) else "符合制度，可据此安排"
        return PolicyReply(decision=decision, checks=tuple(checks))
```

`run()` 的核心逻辑分三步，每一步都不涉及模型调用——它是纯粹的**规则匹配**：

**Step 1: 构建基础规则清单。** 四条通用规则覆盖市内交通、餐补、住宿、报销，**人人都会遇到**。这是「基础制度底座」。

**Step 2: 关键词增量规则。** 遍历输入 `prompt` 文本，检测特定关键词：
- `"国际" / "境外" / "overseas"` → 追加「境外出差」条款；
- `"接待" / "宴请"` → 追加「专项审批」条款。

这里的英文 `"overseas"` 检测用 `normalized = prompt.lower()` 预处理后做统一匹配，避免大小写遗漏——虽然简单，但工程上很实用。

**Step 3: 超标判定。** 检查是否存在 `"超标"`、`"超出限额"`、`"超预算"` 中的任意一个。命中则 `decision` 设为"存在超标项"，否则默认为"符合制度"。

> ⚠️ **注意事项**：这个模块**故意不用模型**。老师的选择是：对于制度核查这种确定性场景，规则引擎比 LLM 更可靠（零幻觉风险）且零延迟。这也是为什么这个"Agent"不需要 `acp` 依赖——它甚至不需要知道自己在 ACP 的框架里运行。

---

### 8.3 TravelPolicyAcpAdapter：适配层逐行解析

现在看 `policy_acp_adapter.py`。这个文件就是那个「转换插头」——它实现了 ACP 的标准接口，内部把调用转发给 `TravelPolicyModule`。

#### 8.3.1 导入与类型定义

```python
# 文件名: policy_acp_adapter.py
# 功能: 将 TravelPolicyModule 包装为 ACP Agent

from __future__ import annotations
import asyncio
from typing import Any, cast
from uuid import uuid4

from acp import (
    Agent, InitializeResponse, NewSessionResponse, PromptResponse,
    run_agent, text_block, update_agent_message,
)
from acp.interfaces import Client
from acp.schema import (
    AudioContentBlock, ClientCapabilities, EmbeddedResourceContentBlock,
    HttpMcpServer, ImageContentBlock, Implementation, McpServerStdio,
    ResourceContentBlock, SseMcpServer, TextContentBlock,
)

from policy_module import TravelPolicyModule   # ← 唯一的外部业务依赖
```

注意 `from policy_module import TravelPolicyModule`——适配器**依赖**业务模块，但业务模块**不知道**适配器的存在。这是依赖方向的正确选择（依赖倒置的一种朴素实践）。

#### 8.3.2 __init__：持有业务模块

```python
class TravelPolicyAcpAdapter:
    _client: Client

    def __init__(self) -> None:
        self._module = TravelPolicyModule()
```

与 `DemoAcpAgent.__init__(self, role: str)` 对比：

| 对比维度 | `DemoAcpAgent` | `TravelPolicyAcpAdapter` |
|---|---|---|
| `__init__` 参数 | 接收 `role: str`（reviewer/reporter） | 无参数 |
| 内部持有 | `self._role`（字符串） | `self._module`（TravelPolicyModule 实例） |
| 本质 | 把行为逻辑内联在 `render_reply()` 中 | 把行为逻辑委托给外部模块 |

这是 Adapter 模式的第一个特征：**构造时就把业务模块挂载好**（组合优于继承）。

#### 8.3.3 on_connect：保存 Client 引用

```python
    def on_connect(self, conn: Client) -> None:
        self._client = conn
```

与 `demo_acp_agent.py` **完全相同**。每个 ACP Agent 都需要在连接时保存 `Client` 句柄，后续 `prompt()` 中用它推送回复。

#### 8.3.4 initialize：声明 Agent 身份

```python
    async def initialize(
        self, protocol_version: int,
        client_capabilities: ClientCapabilities | None = None,
        client_info: Implementation | None = None,
        **kwargs: Any,
    ) -> InitializeResponse:
        return InitializeResponse(
            protocol_version=protocol_version,
            agent_info=Implementation(
                name="company-travel-policy",
                title="差旅制度核查 Agent",
                version="0.1.0",
            ),
        )
```

与 `demo_acp_agent` 对比——**结构完全相同，只有 `name` / `title` 的值不同**：

| 字段 | `DemoAcpAgent` | `TravelPolicyAcpAdapter` |
|---|---|---|
| `name` | `f"demo-{self._role}"`（动态拼接） | `"company-travel-policy"`（固定字面量） |
| `title` | `f"本地演示 Agent（{self._role}）"` | `"差旅制度核查 Agent"` |
| `version` | `"0.1.0"` | `"0.1.0"` |

> 🔗 **前置知识**：`initialize` 方法的签名和返回类型在 [第 X 章：demo_acp_agent 的四个标准方法] 中有详细讲解。

#### 8.3.5 new_session：生成会话 ID

```python
    async def new_session(
        self, cwd: str,
        additional_directories: list[str] | None = None,
        mcp_servers: list[McpServer] | None = None,
        **kwargs: Any,
    ) -> NewSessionResponse:
        return NewSessionResponse(session_id=uuid4().hex)
```

与 `demo_acp_agent.py` **逐字完全相同**。这个方法只是用 `uuid4().hex` 生成一个唯一会话标识，无状态、无业务逻辑。它**就是模板代码，不需要改**。

#### 8.3.6 prompt：唯一要改的地方

这是两个文件**唯一不同的核心位置**：

```python
    async def prompt(
        self, prompt: list[PromptBlock], session_id: str, **kwargs: Any,
    ) -> PromptResponse:
        prompt_text = "\n".join(
            block.text for block in prompt if isinstance(block, TextContentBlock)
        )
        reply = self._module.run(prompt_text).render()   # ← 唯一差异
        await self._client.session_update(
            session_id=session_id,
            update=update_agent_message(text_block(reply)),
        )
        return PromptResponse(stop_reason="end_turn")
```

把它和 `demo_acp_agent.prompt()` 并排对比：

```
┌──────────────────────────────────────────────────────────────────┐
│        demo_acp_agent                      policy_acp_adapter    │
├──────────────────────────────────────────────────────────────────┤
│ prompt_text = "\n".join(...)             prompt_text = "\n".join(...)    │  ← 完全相同
│                                                                    │
│ reply = render_reply(                   reply = self._module      │  ← 不同！
│     self._role, prompt_text              .run(prompt_text)        │
│ )                                        .render()                │
│                                                                    │
│ await self._client.session_update(...)  await self._client.session_update(...) │  ← 完全相同
│ return PromptResponse(...)              return PromptResponse(...) │  ← 完全相同
└──────────────────────────────────────────────────────────────────┘
```

> 💡 **核心洞见**：老师反复强调 **"唯一要改的地方只有这儿"**。`prompt_text` 的提取逻辑不变，`session_update` + `PromptResponse` 的返回不变。你只替换 `reply` 这一行——从内联函数变成对业务模块的委托调用。

`self._module.run(prompt_text).render()` 这行做了三件事：

1. `.run(prompt_text)` → 调用业务模块的核心方法，传入用户文本，返回 `PolicyReply` 对象；
2. `.render()` → 把结构化结果格式化为可读字符串；
3. 字符串直接作为 `text_block(reply)` 传给 `session_update`——ACP Client 收到这条消息。

---

### 8.4 核心对比表：`demo_acp_agent` vs `policy_acp_adapter`

把两个文件的每一层放在一起对比，结构相同和核心不同一目了然：

| 对比维度 | `demo_acp_agent.py` | `policy_acp_adapter.py` | 异同 |
|---|---|---|---|
| **导入** | 含 `argparse`、`re` | 含 `policy_module.TravelPolicyModule` | 不同：一个引入命令行解析，一个引入业务模块 |
| **`__init__`** | `def __init__(self, role: str)` → `self._role = role` | `def __init__(self)` → `self._module = TravelPolicyModule()` | 不同：一个存角色字符串，一个存模块实例 |
| **`on_connect`** | `self._client = conn` | `self._client = conn` | ✅ **完全相同** |
| **`initialize`** | 返回 `Implementation(name=f"demo-{role}", ...)` | 返回 `Implementation(name="company-travel-policy", ...)` | 结构相同，`name`/`title` 不同 |
| **`new_session`** | `return NewSessionResponse(session_id=uuid4().hex)` | `return NewSessionResponse(session_id=uuid4().hex)` | ✅ **完全相同** |
| **`prompt` 方法签名** | `async def prompt(self, prompt, session_id, **kwargs) -> PromptResponse` | 完全相同 | ✅ **完全相同** |
| **提取 prompt_text** | `"\n".join(block.text for block in prompt if isinstance(block, TextContentBlock))` | 完全相同 | ✅ **完全相同** |
| **生成 reply** | `render_reply(self._role, prompt_text)` — 内联函数 | `self._module.run(prompt_text).render()` — 委托给业务模块 | ⚠️ **唯一不同** |
| **session_update** | `await self._client.session_update(session_id, update=update_agent_message(text_block(reply)))` | 完全相同 | ✅ **完全相同** |
| **返回值** | `return PromptResponse(stop_reason="end_turn")` | 完全相同 | ✅ **完全相同** |
| **`main()`** | 含 `argparse` 解析 `--role` | 直接 `run_agent(cast(Agent, TravelPolicyAcpAdapter()))` | 不同：一个需要命令行参数，一个不需要 |
| **业务逻辑位置** | 在同一个文件的 `render_reply()` 函数中 | 在独立文件 `policy_module.py` 的 `TravelPolicyModule` 类中 | 不同：Adapter 实现了业务与协议的彻底分离 |

**结论**：两个文件的 10 个关键位置中，**7 个完全相同**，2 个只有参数值不同，**只有 1 个位置（生成 `reply`）是真正需要你动脑子的**。其余全是标准模板。

---

### 8.5 注册到 AGENT_MATRIX

写完适配器后，要让 `TriggerFlow` 知道它的存在，需要把它注册到 `AGENT_MATRIX` 配置中。配置项含义如下：

```python
# AGENT_MATRIX 注册配置示例
AGENT_MATRIX = {
    "company-policy": {
        "command": [sys.executable, "/path/to/policy_acp_adapter.py"],
        "desc": "差旅制度核查 Agent —— 基于规则引擎，检查任务中的制度合规性",
    },
    # ... 其他 agent 注册项
}
```

| 配置键 | 含义 |
|---|---|
| `"company-policy"` | Agent 在矩阵中的唯一标识符（key） |
| `"command"` | 启动命令列表：`[Python 解释器路径, 脚本绝对路径]` |
| `"desc"` | 人类可读的描述，供调度时参考 |

> ⚠️ **注意事项**：`sys.executable` 确保使用的是当前 Python 环境的解释器路径。如果你的适配器依赖特定的虚拟环境，请确保 `sys.executable` 指向正确的 `python` 可执行文件。**脚本路径要写绝对路径**——ACP 运行时会切换工作目录，相对路径会找不到文件。

注册后，TriggerFlow 可以像调度 `demo-acp` 一样调度 `"company-policy"`。从调度层看，它们都是 ACP Agent，没有任何区别——**这正是 Adapter 模式的目标：协议统一，实现自由**。

---

### 8.6 Adapter 模式的通用模板

老师给出了适配器的"标准模板"——**你可以直接复制，只改三个地方**：

```python
# ============================================================
# ACP Adapter 通用模板
# 只需修改标记为 【改】 的三个位置，其余原样保留
# ============================================================

from acp import (
    Agent, InitializeResponse, NewSessionResponse, PromptResponse,
    run_agent, text_block, update_agent_message,
)
# ... (其余 imports 不变)

from your_module import YourBusinessModule   # 【改 1】导入你的业务模块

class YourAcpAdapter:
    _client: Client

    def __init__(self) -> None:
        self._module = YourBusinessModule()   # 【改 2】实例化你的业务类

    def on_connect(self, conn: Client) -> None:
        self._client = conn

    async def initialize(self, ...) -> InitializeResponse:
        return InitializeResponse(
            protocol_version=protocol_version,
            agent_info=Implementation(
                name="your-agent-name",        # 【改 3】起个名字
                title="你的 Agent 标题",        # 【改 3】写个描述
                version="0.1.0",
            ),
        )

    async def new_session(self, ...) -> NewSessionResponse:
        return NewSessionResponse(session_id=uuid4().hex)

    async def prompt(self, prompt, session_id, **kwargs) -> PromptResponse:
        prompt_text = "\n".join(
            block.text for block in prompt if isinstance(block, TextContentBlock)
        )
        reply = self._module.run(prompt_text).render()   # ← 你的业务逻辑
        await self._client.session_update(
            session_id=session_id,
            update=update_agent_message(text_block(reply)),
        )
        return PromptResponse(stop_reason="end_turn")


async def main() -> None:
    await run_agent(cast(Agent, YourAcpAdapter()))

if __name__ == "__main__":
    asyncio.run(main())
```

> 💡 **核心洞见**：整个 `on_connect`、`new_session`、`prompt` 方法体中除 `reply =` 那一行之外的内容，以及 `main()`、`if __name__ == "__main__"`，全是**不变模板**。你只需要关心：你的业务模块叫什么、它的执行入口是什么、它返回的字符串长什么样。

---

### 8.7 Adapter 模式的通用工程价值

Adapter 模式在 ACP 场景下的价值远不止"省几行代码"。将其提炼为三个层次：

#### 第一层：接入成本最低化

| 场景 | 不用 Adapter | 用 Adapter |
|---|---|---|
| 已有 FastAPI 端点要接入 ACP | 拆代码、重构、测试回归 | 复制模板、改 3 行、注册矩阵 |
| 已有定时任务脚本要接入 ACP | 同上 | 同上 |
| 已有命令行工具要接入 ACP | 同上 | 同上 |

接入一个新 Agent 的"心智负担"从「理解整个 ACP 协议」降低为「知道 `__init__`, `reply`, `name` 三个位置怎么填」。

#### 第二层：环境天然隔离

Adapter 模式的一个**隐含好处**是运行时隔离。因为 ACP 通过 `subprocess` 启动适配器脚本作为独立进程：

```
┌─────────────────┐      subprocess      ┌─────────────────┐
│   主流程         │ ──────────────────▶  │  Adapter 进程    │
│  (TriggerFlow)  │                      │  (独立 Python)   │
│                 │   ◀── session_update │                 │
│  自己的工作目录   │                      │  自己的工作目录   │
│  自己的依赖环境   │                      │  自己的依赖环境   │
└─────────────────┘                      └─────────────────┘
```

业务模块跑在独立的进程中，拥有独立的文件系统视图、内存空间和依赖环境。即使业务模块崩溃，也不会拖垮主流程。

#### 第三层：可扩展性

Adapter 模式让「可执行的 Agent 单元」可以无限扩展——任何 Python 模块，只要接受 `str` 输入、返回 `str` 输出，就可以用同一个模板接入 ACP：

```
                    ┌──────────────┐
                    │  ACP 协议层   │
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │ 制度核查    │   │ 信息核实    │   │ 报告生成    │   ← 任意已有模块
    │ Adapter   │   │ Adapter   │   │ Adapter   │
    └───────────┘   └───────────┘   └───────────┘
```

> 💡 **核心洞见**：AC协议定义的是「Agent 怎么说话」，而不是「Agent 说什么话」。Adapter 模式让你专注于「说什么话」，把「怎么说话」交给模板。

---

### 8.8 本节完整流程回顾

把本节所有知识点串成一条完整的执行链路：

```
TriggerFlow 检测到关键词 "制度核查"
    │
    ├── 查 AGENT_MATRIX["company-policy"]
    │   └── 获取 command: [sys.executable, "policy_acp_adapter.py"]
    │
    ├── subprocess 启动 policy_acp_adapter.py
    │   │
    │   ├── TravelPolicyAcpAdapter.__init__()
    │   │   └── self._module = TravelPolicyModule()
    │   │
    │   ├── on_connect(client)          ← 保存 Client 引用
    │   ├── initialize() → name="company-travel-policy"
    │   ├── new_session() → session_id
    │   │
    │   └── prompt(prompt_text, session_id)
    │       │
    │       ├── self._module.run(prompt_text)
    │       │   ├── 检测关键词 → 追加规则
    │       │   ├── 判断超标 → 确定 decision
    │       │   └── 返回 PolicyReply(decision, checks)
    │       │
    │       ├── .render()
    │       │   └── "差旅制度核查结论：...\n适用规则：\n- ..."
    │       │
    │       └── session_update(client, text_block(reply))
    │
    └── 主流程收到 session_update → 显示核查结果
```

---

### 🗺️ 本模块知识图谱

```
                          ┌────────────────────────────┐
                          │   Adapter 模式              │
                          │   业务代码零修改接入 ACP      │
                          └─────────────┬──────────────┘
                                        │
              ┌─────────────────────────┼─────────────────────────┐
              │                         │                         │
     ┌────────▼────────┐     ┌─────────▼─────────┐     ┌─────────▼─────────┐
     │  TravelPolicy   │     │  TravelPolicyAcp  │     │   AGENT_MATRIX    │
     │    Module       │     │     Adapter       │     │     注册          │
     │  (纯业务逻辑)    │     │  (ACP 协议壳)      │     │  (调度接入点)      │
     └────────┬────────┘     └─────────┬─────────┘     └─────────┬─────────┘
              │                        │                         │
     ┌────────▼────────┐     ┌─────────▼─────────┐               │
     │  PolicyReply    │     │ 4个标准方法:       │               │
     │  - decision     │     │ on_connect        │               │
     │  - checks       │     │ initialize  ← 模板 │               │
     │  - render()     │     │ new_session ← 模板 │               │
     └─────────────────┘     │ prompt ← 唯一要改  │               │
                             └───────────────────┘               │
                                                                  │
    ┌─────────────────────────────────────────────────────────────┘
    │
    ▼
    TriggerFlow → AGENT_MATRIX["company-policy"] → subprocess 启动适配器
```

### 💡 一句话总结

> ACP Adapter 模式让你用 3 行改动（导入模块、实例化对象、替换 reply 行）就把任意已有 Python 模块变成标准的 ACP Agent——其余全是复制粘贴的模板代码。

---

> 🤖 由 transcript-to-doc v4.1 生成

## 九、Q&A 答疑与架构总结

> 🎯 **本节定位**
>
> 本模块是课程的收尾章节，汇集了全部 8 个学员真实提问与老师的详细回答，同时对整套 Agent 架构进行了系统性回顾与高度总结。相对于前几讲的 Skills 内容，本讲的抽象难度更低——其本质只解决一个问题：**我本地有一个外部服务模块（或自建的 Agent 服务），如何把任务分发给它去处理**。学完本节后，你将对 DAG + ACP 协同、生产部署、并发策略、ACP 与 MCP 的根本区别形成完整的认知闭环。

---

### 9.1 课程架构全景图：DAG + ACP 完整链路

#### 🧠 直观理解

DAG（有向无环图）负责「决定做什么」——将一个复杂任务拆解为可执行的步骤图；ACP（Agent Communication Protocol）负责「连接谁来做」——将每一步指向具体的执行 Agent，完成跨异构智能体的任务分发与结果回传。二者组合，构成了多 Agent 协同的完整闭环。

#### 📖 详细解释

整个系统的运作流程可以用一条完整链路来描述。DAG 方案不仅能编排你自己框架内已有的行为（如 MCP 工具调用、Action 注入等），还可以通过 ACP 直接将行为指定为**外部 Agent**。DAG 的 Planner 负责把「指定 Agent 执行任务」这件事进行实际的编排——左边是行动项（可能性），右边才是真正的可执行方案。

这个可执行方案需要利用**执行器**真正触发执行，而 ACP 就在中间发挥关键的桥接作用：

1. **输入方案与执行对象绑定**：ACP 将 Planner 产出的执行方案与指向的具体 Agent 连接起来
2. **任务分发与结果回传**：连接完毕后，ACP 从执行对象获取结果并返回
3. **反向汇总**：所有子任务完成后，汇总器将各 Agent 的产出整合为最终结果

#### 🔄 完整协同链路（ASCII 图）

```
                          ┌─────────────────────────────────┐
                          │          用户复杂任务              │
                          │   "请帮我分析这份代码库的安全漏洞，  │
                          │    并生成修复建议报告"              │
                          └───────────────┬─────────────────┘
                                          │
                                          ▼
                          ┌─────────────────────────────────┐
                          │        DAG Planner（编排层）       │
                          │                                 │
                          │  将任务拆解为有向无环图执行方案:      │
                          │                                 │
                          │  Step 1: 静态代码扫描 ──────────┐  │
                          │  Step 2: 依赖漏洞分析 ──┐       │  │
                          │  Step 3: 安全模式检测 ──┤       │  │
                          │                        │       │  │
                          │            ┌───────────┼───────┘  │
                          │            │           │          │
                          │            ▼           ▼          │
                          │  Step 4: 结果汇总 + 报告生成       │
                          └───────────────┬─────────────────┘
                                          │
                     ┌────────────────────┼────────────────────┐
                     │                    │                    │
                     ▼                    ▼                    ▼
           ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
           │   ACP 通道 #1    │ │   ACP 通道 #2    │ │   ACP 通道 #3    │
           │  指向: Codex    │ │  指向: Codex    │ │  指向: Claude    │
           │  任务: 静态扫描  │ │  任务: 依赖分析  │ │  任务: 安全检测   │
           └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
                    │                    │                    │
                    ▼                    ▼                    ▼
           ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
           │   Codex Agent   │ │   Codex Agent   │ │  Claude Agent   │
           │  ┌───────────┐  │ │  ┌───────────┐  │ │  ┌───────────┐  │
           │  │ 隔离沙箱 1 │  │ │  │ 隔离沙箱 2 │  │ │  │ 隔离沙箱 3 │  │
           │  │ skills    │  │ │  │ skills    │  │ │  │ skills    │  │
           │  │ tools     │  │ │  │ tools     │  │ │  │ tools     │  │
           │  │ workspace │  │ │  │ workspace │  │ │  │ workspace │  │
           │  └───────────┘  │ │  └───────────┘  │ │  └───────────┘  │
           └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
                    │                    │                    │
                    │  扫描结果          │  依赖报告          │  安全报告
                    ▼                    ▼                    ▼
           ┌─────────────────────────────────────────────────┐
           │              结果汇总器（Aggregator）              │
           │  将各 Agent 产出合并，生成最终报告                  │
           │  可再用一个 LLM（如千问 7B）做摘要/去重/润色        │
           └───────────────────────┬─────────────────────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │   最终交付物      │
                          │  安全漏洞分析报告  │
                          └─────────────────┘
```

> 💡 **核心洞见**：DAG 决定「做什么」，ACP 决定「找谁做」，两者解耦。你可以在不改 DAG 编排逻辑的前提下，把某个步骤的执行者从 Codex 换成 Claude Code，甚至替换为一个自建的通用 Agent——这就是 ACP 统一异构交互带来的灵活性。

> 🔗 **关联知识**：DAG 编排的底层实现详见第 16 课代码中的 `plan_executor`；ACP 的 Adapter 模式实现详见第 13 课的通用智能体平台。

---

### 9.2 Q&A 答疑集

> 📌 以下 8 个问题来自课堂现场的真实提问，每一个都代表了学员在理解与实践中遇到的典型困惑。老师逐一做了详细解答，文档完整保留了问答原文、背景分析和延伸建议。

---

#### 9.2.1 如何让 Agent 在指定路径下建立会话？

**🙋 问题**（实验同学）：执行 Agent 有一个执行目录，直接 `npx` 就在当前目录下建立会话。如果想让 Agent 在其他路径下建立会话，能做到吗？

> 📖 **背景**：在使用 ACP 启动 Agent 时，Agent 默认会在当前工作目录下建立会话状态。但在实际工程中，我们往往希望将不同 Agent 或不同任务的会话隔离到独立的目录下，避免文件冲突和状态污染。

**💬 老师回答**：

可以做到。在注册 Agent 时，我们可以为它指定启动命令和参数。以 `npx` 启动方式为例，注册时不仅提供基础命令（如 `npx @anthropic-ai/claude-code-acp`），还可以在后面追加参数，通过 `--workspace` 或 `-w` 标志来指定目标工作目录。

```
npx @anthropic-ai/claude-code-acp --workspace /path/to/your/target
```

这样一来，Agent 的会话就会在指定的路径下创建和管理。这个参数化的方式本质上与本地直接调用命令行时传入路径参数是同一个原理——ACP 启动 Agent 进程时，启动命令会被原样传递给子进程。

> 💡 **延伸**：`--workspace` 参数的作用不仅仅是设置「会话目录」，它还决定了 Agent 的**操作边界**——Agent 在这个工作空间内读写文件、执行命令、存储中间结果。合理规划 workspace 路径是实现**单机多 Agent 隔离**的第一步。如果后续演进到 Docker 沙箱模式（见 9.3 和 9.4），每个 Docker 容器内部也会有独立的 workspace 路径，天然形成文件系统隔离。

---

#### 9.2.2 ACP 外部 Agent 需要注册到 Action Center 吗？

**🙋 问题**（newbug 同学）：之前 MCP tools 是注册到 Action Center 的，那 ACP 外部的 Agent 需要注册吗？

> 📖 **背景**：在前面的课程中，学员已经习惯了「所有可调用能力统一注册到 Action Center」的模式。接触到 ACP 这个新概念后，自然会产生疑问：ACP 指向的外部 Agent 是否也需要走同样的注册流程？

**💬 老师回答**：

**可以不注册，也可以注册——取决于你选择的编排方式。**

首先，如果你直接使用 DAG 编排，DAG 的编排对象并不一定是 Action。从第 16 课代码中可以看到，DAG Planner 的核心编排对象是 `capability`——这个 `capability` 是在 `plan_executor` 中提供给 Planner 的。你可以在这里提供 `write`、`read`、`bash` 等各种能力项，Planner 通过这个地方知道它可以编排什么。

如果你使用的是一个更完整的 Agentic 框架，那么 Planner 的编排对象就包括：
- 已注册到 Action Center 的 Action
- Workspace 中允许使用的基础能力（如 Bash 指令）
- 处理复杂任务时的内置流程能力（如 Redo、Replan、Verify）

**关键点在于：编排这个动作本身是你自己决定的**。你可以用 DAG Planner 来做编排，也可以直接写一个 TriggerFlow——编排什么、怎么编排，都是你自己控制的。

那么 ACP 到底应不应该注册到 Action Center？老师的建议是：**在 Agentic 框架给定的方向里，应该注册**。你可以把 ACP 当作一种特殊的 Action 注册进来——注册后，DAG Planner 在做任务规划时就可以将其纳入可编排对象。这样，当 Planner 判断某个子任务更适合由外部 Agent 处理时，它可以直接编排一个「调用 ACP Agent」的步骤。

```
编排方式决策树：

你如何做编排？
    │
    ├── 使用 DAG Planner（自动编排）
    │   └── 建议将 ACP Agent 注册为 Action
    │        → Planner 可自动发现并编排 ACP Agent
    │
    ├── 手写 TriggerFlow（手动编排）
    │   └── 不需要注册
    │        → 直接在 TriggerFlow 中硬编码 ACP 调用
    │
    └── 混合模式
        └── 核心流程手写 + 扩展步骤用 Planner
            → 注册 ACP Agent 为 Action，供 Planner 使用
```

> 💡 **延伸**：注册与不注册的本质区别在于**可发现性**。注册到 Action Center 意味着 Agentic 框架的 Planner 可以在运行时动态发现并编排这个 ACP Agent；不注册则意味着你只能在代码中硬编码调用它。如果你的系统需要处理开放性的、多变的任务（即任务类型不可预知），建议注册以增加灵活性；如果任务模式固定（比如每次都走同一个流程），硬编码调用反而更简单直接。

---

#### 9.2.3 Web 生产环境通过 ACP 调用 Claude Code 可行吗？

**🙋 问题**（陈哥同学）：在 Web 生产系统中，后端服务收到请求后，通过 ACP 调用 Claude Code 来处理一些任务，这可行吗？有没有安全性和并发方面的问题？

> 📖 **背景**：这是最贴近真实生产场景的问题。学员关心的是：从理论上的「可以做」到生产环境的「可以上线」，中间还隔着安全性、并发、资源管理等多道关卡。

**💬 老师回答**：

**可行，但需要做好隔离和并发架构。**

**可行性前提**：你的后端响应服务器上需要装有 Claude Code 和对应的 Skills。核心流程是：外部 HTTP 请求到达后端服务 → 后端通过 ACP 将任务分发给本机或远程的 Claude Code Agent → Agent 执行完毕 → 结果返回。

**安全性**：直接在生产服务器的宿主机上运行 Claude Code 是有风险的——Agent 可能误操作文件系统、执行危险命令、或消耗过多系统资源。因此，正确的做法是将 Claude Code 和 Skills 放在**安全的沙盒环境**（如 Docker 容器）中。请求通过一个「网络穿透」的方式进入 Docker 这一层，在 Docker 内部完成处理。你可以精确控制 Docker 的：
- 网络权限（是否允许联网）
- 文件系统读写权限（只读/读写/完全隔离）
- 资源配额（CPU、内存的上限）

**并发**：并发能力取决于本机能承载的 Claude Code 客户端并发数量。在单机场景下，老师实测并发 3 到 5 个任务没有问题。但如果需要更高并发（比如 50 个），就需要考虑扩展架构了——在一台机器上部署多个 Docker 沙箱，或者更进一步，采用分布式部署多个响应服务器，由主调度器通过 ACP 统一管理。

> 💡 **延伸**：关于生产环境部署的完整架构，详见 [9.4 生产环境部署架构](#94-生产环境部署架构)。其中包含了分布式路由、Docker 沙箱、Session 持久化的完整方案。

---

#### 9.2.4 编排是模型控制还是人控制？

**🙋 问题**（五八同学）：任务编排是由模型自动控制的，还是由人手动控制的？

> 📖 **背景**：在 DAG + ACP 的架构讲解中，Planner 承担了「将任务拆解为执行步骤」的职责。学员自然会问：这个 Planner 背后是 AI 在做决策，还是人类在写死流程？

**💬 老师回答**：

**Planner 背后可以是 LLM（如 DeepSeek），也可以是人——编排这个动作本身是你自己决定的。**

在实际工程中有三种编排层次：

1. **人工手动编排（最简单）**：你对任务的理解已经非常清晰，不需要 AI 帮你分解。比如「收到 review PR 请求后，同时发给 Codex 和 Claude Code，最后汇总」——这个流程在脑中是固定的，直接写一个 TriggerFlow 或一段编排代码即可。这种情况下编排出自人手，ACP 只是执行通道。

2. **AI 辅助编排（DAG Planner + LLM）**：任务模式多变，无法预先枚举所有可能。这时让 LLM 做 Planner，根据任务描述自动生成 DAG 执行图。Planner 可以是 DeepSeek、千问、Claude 等任何具备推理能力的模型。它产出的编排结果再交给执行器和 ACP 去实际执行。

3. **混合编排（人在回路）**：AI 先生成编排方案，人工审核/调整后再执行。这是生产环境中最推荐的模式——既能利用 LLM 的泛化能力处理未知任务，又保留了人类对关键决策的控制权。

```
编排层级对照表：

┌──────────┬──────────────────┬──────────────────┬──────────────┐
│ 层级     │ 决策者            │ 适用场景          │ 实现方式      │
├──────────┼──────────────────┼──────────────────┼──────────────┤
│ 手动编排 │ 人类              │ 任务模式固定       │ TriggerFlow  │
│ AI 编排  │ LLM (Planner)    │ 任务开放多变       │ DAG Planner  │
│ 混合编排 │ 人类 + LLM       │ 生产环境推荐       │ Planner +    │
│          │                  │                    │ 人工审核     │
└──────────┴──────────────────┴──────────────────┴──────────────┘
```

> 💡 **延伸**：这与 ACP 的设计哲学一致——ACP 不关心「是谁做的编排」，它只关心「把任务分发给谁」。无论编排方案来自 Planner（AI）还是 TriggerFlow（人类），到了 ACP 这一层，输入都是统一的：**用哪个 Agent + 任务是什么**。这种解耦设计使得你可以在不同场景下灵活切换编排策略，而不需要改动底层的 Agent 通信逻辑。

---

#### 9.2.5 如何测试服务器并发最大数量？

**🙋 问题**（红宇同学）：如何测试服务器的并发最大数量？用什么方法？

> 📖 **背景**：在讨论 ACP + Docker 沙箱的生产部署时，并发能力是一个必须量化的问题。学员想知道如何科学地测试自己服务器的并发上限。

**💬 老师回答**：

测试并发上限的核心方法论是**资源观测**，而非简单加请求数。关键在于区分两种本质不同的场景。

**IO 密集型场景**（如通过网络请求远端 LLM API）：

如果你的业务服务器主要通过协程处理网络请求——收发数据、等待远端 API 响应——那么并发上限由操作系统的协程调度能力和网络带宽决定。在这种场景下，并发量可以非常大。老师在自己的 M2 Pro 芯片上实测，跑三五千个协程没有问题。因为协程的核心工作只是等待网络 IO，CPU 大部分时间处于空闲状态。

**测试方法**：逐步增加并发请求数，同时监控：
- CPU 使用率（不超过 70% 为健康）
- 内存使用量（线性增长、无突发飙升）
- 网络带宽（是否接近上限）
- 请求延迟 P99（延迟突增说明接近瓶颈）

**计算密集型场景**（如本地运行千问模型做推理）：

如果你的服务器上运行着本地大模型，模型推理本身就是计算密集型任务。此时并发上限由硬件（GPU/CPU 算力）决定，与协程数量几乎无关。例如本地千问服务器可能只能同时支持 2 到 3 个并发推理请求——不管你写了多少异步代码，模型的处理能力是有硬上限的。

**测试方法**：
- 从 1 个并发开始，每次增加 1 个
- 观测 GPU 利用率或 CPU 占用是否打满
- 当模型推理延迟显著增加时（如从 2 秒变 10 秒），说明已到并发瓶颈

```
并发测试决策树：

你的 Agent 执行模式是？
    │
    ├── 远端 API 调用（IO 密集型）
    │   ├── 并发上限: 数千级（协程）
    │   ├── 瓶颈: 网络带宽、文件描述符、内存
    │   └── 测试: 逐步加压，观测 CPU/内存/延迟
    │
    └── 本地模型推理（计算密集型）
        ├── 并发上限: 2~3 个（硬件决定）
        ├── 瓶颈: GPU/CPU 算力
        └── 测试: 逐个增加，观测 GPU 利用率/推理延迟
```

> 💡 **延伸**：当单机计算密集型并发达上限时，解决方案不是优化代码，而是**横向扩展**——部署多台推理服务器，在前面加一个路由层做负载分发。这正是 [9.4 生产环境部署架构](#94-生产环境部署架构) 中讨论的分布式拓扑。

---

#### 9.2.6 ACP 可以完全不依赖模型吗？

**🙋 问题**（小白同学）：ACP 协议本身可以完全不依赖大模型吗？还是说它的运行必须绑定一个 LLM？

> 📖 **背景**：学员之前接触的 MCP 是一个纯工具协议，不涉及智能处理。ACP 的名字中带有「Agent」一词，容易让人误以为 ACP 本身也内置了 AI 能力。

**💬 老师回答**：

**可以完全不依赖模型。ACP 的 Demo 实现就是纯分词逻辑，没有调用任何 LLM。**

ACP 协议层本身只是一个通信标准——它定义了：
1. **如何描述一个 Agent**（用什么启动命令、配置在哪）
2. **如何向 Agent 发送任务**（任务描述、附加文件）
3. **如何从 Agent 获取结果**（返回格式、状态码）

这些环节不需要任何 AI 模型参与。ACP 的工作是**连接**和**传递**，而不是**理解**和**推理**。

「智能」不在 ACP 协议层，而在 ACP 所连接的 Agent 内部。Agent 自身可以是一个 LLM（如 Claude Code），也可以是纯规则引擎（如 Demo 中的分词逻辑），甚至可以是调用远端 API 的简单脚本。ACP 不关心也不限制 Agent 的内部实现——这正是它「统一异构交互」价值的体现。

```
ACP 协议分层：

┌─────────────────────────────────────┐
│          编排层（Planner）           │  ← 可选使用 LLM
│    DAG Planner / TriggerFlow       │
├─────────────────────────────────────┤
│          通信层（ACP）              │  ← 不依赖 LLM
│    Agent 注册 / 任务分发 / 结果回传  │     纯协议逻辑
├─────────────────────────────────────┤
│          执行层（Agent）            │  ← 可使用 LLM
│    Claude Code / Codex / 自建Agent │     也可不用
└─────────────────────────────────────┘
```

> 💡 **延伸**：这个设计哲学与 MCP 形成对比——MCP 的协议层也不依赖 AI，它只是工具的描述和调用标准。ACP 和 MCP 在「协议层不绑定 AI」这一点上是一致的，区别在于它们连接的对象不同（详见 [9.5 ACP vs MCP 终极对比表](#95-acp-vs-mcp-终极对比表)）。

---

#### 9.2.7 ACP 与 MCP 的终极区别是什么？

**🙋 问题**（榕树、杨林同学）：ACP 和 MCP 到底有什么区别？感觉它们都像是让外部能力和我的主流程通信？

> 📖 **背景**：这是本节课最核心的概念辨析问题。学员同时接触了 MCP 和 ACP 两个协议，容易混淆它们的设计目标和适用场景。

**💬 老师回答**：

**最核心的区别就一句话：层不一样。MCP 是提供工具，ACP 是指定智能模块。**

**MCP（Model Context Protocol）**：
- 目标：为 LLM 提供一组可调用的工具（Tools）
- 抽象层级：工具级——暴露的是 `function_name(params)` 这样的原子能力
- MCP 服务本身**没有智能处理能力**，它只是把工具的描述和能力暴露出来，由调用方（LLM）决定何时、如何调用
- 典型场景：让 Claude 可以查数据库、发邮件、读网页——这些是「工具」，不是「Agent」

**ACP（Agent Communication Protocol）**：
- 目标：连接一个完整的智能模块，把任务分派给它去自主完成
- 抽象层级：任务级——暴露的是「接收一个自然语言任务，返回处理结果」这样的完整接口
- ACP 指向的 Agent **本身已具备智能处理能力**，它内部封装了 Skills、MCP Tools、Prompt 配置、甚至是另一个 LLM
- 典型场景：让 Codex Agent 去 Review 一段代码，让 Claude Code Agent 去分析一个仓库——这些是「任务」，不是「工具调用」

```
                    抽象层级差异（ASCII 示意图）

    ACP 级别（任务分派）                    MCP 级别（工具调用）
    ┌──────────────────┐                  ┌──────────────────┐
    │ "帮我校验这 200   │                  │  check_syntax()   │
    │  个文件的安全漏洞" │                  │  search_cve()     │
    │        ↓          │                  │  analyze_dep()    │
    │  ┌────────────┐   │                  │        ↓          │
    │  │ Agent 内部  │   │                  │  调用方（LLM）    │
    │  │ 自主调用:   │   │                  │  自己组合这些     │
    │  │ · MCP 工具  │   │                  │  工具来完成      │
    │  │ · Skills    │   │                  │  安全校验任务    │
    │  │ · 代码执行  │   │                  └──────────────────┘
    │  └────────────┘   │
    └──────────────────┘

    一个任务                    vs          多个工具调用
    内部组合了多个工具                       需要外部编排
```

> 💡 **延伸**：有人会问「那我把一个 LLM 包装成 MCP 服务，不就跟 ACP 一样了吗？」——这是另一个问题，也确实可以做。但区别在于：**ACP 的设计初衷就是连接智能模块**，它假定连接的对象已经具备自主决策能力，因此协议只暴露两个核心信息：用哪个 Agent + 任务是什么。而 MCP 的设计初衷是提供原子工具，它假定连接的对象是被动执行者，因此协议暴露的是工具列表和调用接口。两者追求的目标从一开始就不同。

完整的对比见 [9.5 ACP vs MCP 终极对比表](#95-acp-vs-mcp-终极对比表)。

---

#### 9.2.8 Review PR 用多 Agent 对比可行吗？

**🙋 问题**（一方同学）：我想用 ACP 发请求让多个 Agent 同时 Review 同一个 PR，然后对比它们的 Review 结果，这可行吗？

> 📖 **背景**：这是 ACP 核心价值的一个典型应用场景。学员想知道的是：能否将同一个 Prompt 分发给不同 Agent，利用它们各自的优势，最后汇总得出更全面的结论？

**💬 老师回答**：

**完全可以，这是一个非常典型的编排场景。**

你的流程非常清晰：
1. 收到 Review PR 的请求
2. 将同一个 Prompt 通过 ACP 同时发给 Codex 和 Claude Code
3. 两个 Agent 各自独立完成 Review，产出各自的结论
4. 用一个汇总器（甚至可以用千问 7B 这样的轻量模型）将两份 Review 结果做摘要和去重
5. 输出最终的综合 Review 报告

这个流程中，**你甚至不需要 Planner**——因为编排逻辑在你的脑中已经非常清楚：就是两个 Agent 并行执行同一任务，然后汇总。你直接写一段编排代码即可。ACP 在这里的价值是：你**不需要关心 Codex 和 Claude Code 的内部差异**。它们的启动方式、配置路径、工具集可能完全不同，但 ACP 让你用统一的方式向它们发送任务、接收结果。

```
Review PR 多 Agent 对比流程：

    ┌─────────────────┐
    │  PR Review 请求  │
    │  同一 Prompt     │
    └────────┬────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐     ┌──────────┐
│Codex    │     │Claude    │
│Review   │     │Review    │
│独立沙箱  │     │独立沙箱  │
│互不串供  │     │互不串供  │
└────┬────┘     └────┬─────┘
     │               │
     │  各自产出      │  各自产出
     ▼               ▼
┌──────────────────────────┐
│      汇总 Agent           │
│  （如千问 7B / DeepSeek） │
│  摘要 + 去重 + 润色       │
└────────────┬─────────────┘
             │
             ▼
    ┌─────────────────┐
    │  综合 Review 报告 │
    └─────────────────┘
```

**一个关键优势：隔离性**。Codex 和 Claude Code 在各自的沙箱中独立工作，它们之间完全隔离——不知道对方的存在，不会串供。这意味着它们的 Review 结果是真正独立的视角。如果两个 Agent 的结论一致，可信度更高；如果有分歧，你也能获得多角度的参考。

> 💡 **延伸**：这个模式可以扩展到更多场景：
> - **代码生成对比**：同一需求发给多个 Agent，比较代码质量
> - **安全分析交叉验证**：两个 Agent 独立分析，降低漏报和误报
> - **翻译质量对比**：多个 Agent 各自翻译，人工或 AI 评选最佳版本
> - 核心思路始终一样：**同输入 → 多 Agent 独立处理 → 汇总对比**

---

### 9.3 ACP 两大核心价值（白板板书还原）

> 📌 以下内容是老师在白板上总结的 ACP 设计哲学本质，是理解整个 ACP 协议「为什么存在」的关键。

---

#### 🧠 直观理解

ACP 存在的理由不是「又多了一种通信协议」，而是解决了多 Agent 协同中的两个根本问题：**异构 Agent 之间如何统一对话**，以及**多个 Agent 之间如何安全隔离**。

#### 📖 详细解释

**核心价值一：解决 Agent 内部异构问题，统一核心交互逻辑**

不同的 Agent 产品的交互方式天差地别：
- Claude Code 的启动方式是 `claude` CLI 工具
- Codex 的启动方式是通过 OpenAI API
- 自建 Agent 可能是一个 HTTP 服务、一个 Python 脚本、甚至是一个 Docker 容器

如果没有 ACP，你的主流程需要针对每一种 Agent 写一套适配逻辑——这会导致系统复杂度爆炸。ACP 通过**统一的注册格式和标准化的通信接口**，将所有异构 Agent 抽象为同一种可调用对象。主流程只需要知道两件事：「用哪个 Agent」和「任务是什么」，不需要关心 Agent 内部如何实现。

**核心价值二：跨 Agent 信息传递，每个 Agent 拥有独立工作空间**

ACP 所指向的 Agent 不仅有独立的**工作空间**（workspace），还包括独立的：
- **Skills**：每个 Agent 可以配置自己的技能集
- **Tools**：每个 Agent 可以绑定自己的 MCP 工具
- **MCP 服务**：不同 Agent 可以连接不同外部服务
- **环境配置**：独立的 Prompt、独立的模型选择、独立的运行时

这种隔离意味着：主流程中的 Codex Agent 拥有 Internet Search 和 Agentic Skill，而另一个 Agent 拥有 AMap MCP 和 Bash——它们的能力集完全不同且互不干扰。这正是「行为隔离 + 能力隔离」的真正含义。

```
ACP 隔离架构示意：

┌──────────────────────────────────────────────────┐
│                   主流程                          │
│    ┌─────────────┐  ┌─────────────┐              │
│    │ ACP → Codex  │  │ ACP → 自建  │              │
│    └──────┬──────┘  └──────┬──────┘              │
│           │                │                      │
│    ┌──────┴──────┐  ┌──────┴──────┐              │
│    │ 主流程自己的  │  │ 主流程自己的 │              │
│    │ Workspace   │  │ Workspace   │   ← 互不干扰  │
│    └─────────────┘  └─────────────┘              │
└──────────────────────────────────────────────────┘
          │  ACP 通道              │  ACP 通道
          ▼                        ▼
┌──────────────────┐  ┌──────────────────┐
│  Codex Agent     │  │  自建 Agent      │
│ ┌──────────────┐ │  │ ┌──────────────┐ │
│ │ 独立沙箱      │ │  │ │ 独立沙箱      │ │
│ │ · Skills     │ │  │ │ · Skills     │ │
│ │ · Tools      │ │  │ │ · MCP: AMap  │ │
│ │ · MCP: Search│ │  │ │ · Bash       │ │
│ │ · Workspace1 │ │  │ │ · Workspace2 │ │
│ └──────────────┘ │  │ └──────────────┘ │
│   ← 行为隔离     │  │   ← 行为隔离     │
│   ← 能力隔离     │  │   ← 能力隔离     │
└──────────────────┘  └──────────────────┘
```

#### ⚠️ 何时不该用 ACP

> ❓ **常见误解**：「是不是所有跨模块调用都应该用 ACP？」

**不是。** 如果你不需要隔离——你希望所有 Agent 共享同一个工作空间、同一套 Skills、同一组 MCP 工具——那你**不应该使用 ACP**。ACP 的核心意义是**隔离**。如果你的设计目标就是信息流通和共享，那么直接在主流程中完成所有操作更合适，因为本质上你期望的就是所有信息在一个大流程里流通。ACP 是为「需要隔离的场景」而设计的，不是为所有跨模块调用而设计的。

| 场景 | 是否用 ACP | 理由 |
|---|---|---|
| 多个 Agent 各自独立完成不同子任务，结果互不干扰 | ✅ 用 ACP | 需要工作空间和能力的隔离 |
| 多个 Agent 需要共享同一组文件、工具、配置 | ❌ 不用 ACP | 隔离反而成为障碍 |
| 调用外部 SaaS 服务完成特定任务 | ✅ 用 ACP | 外部服务的环境天然隔离 |
| 同一 Agent 内部的多步操作 | ❌ 不用 ACP | 这是 Agent 内部编排，不需要外部通信协议 |

---

### 9.4 生产环境部署架构

#### 🧠 直观理解

从「单机跑通 Demo」到「生产环境可上线」，中间的核心工程问题是：**当请求量变大、任务变复杂时，如何保证系统的安全性、可扩展性和状态管理？**

#### 📖 详细解释：分布式拓扑

生产环境的部署架构是一个典型的**分层分布式系统**，包含四个关键层：

```
生产环境分布式架构拓扑：

                          ┌──────────────────────────┐
                          │      外部请求入口          │
                          │   HTTP / WebSocket / gRPC │
                          └─────────────┬────────────┘
                                        │
                                        ▼
                          ┌──────────────────────────┐
                          │      分发路由层            │
                          │                          │
                          │  · 负载均衡               │
                          │  · 请求路由               │
                          │  · Session 粘性（可选）    │
                          │  · 限流 & 熔断            │
                          └──┬────────┬────────┬─────┘
                             │        │        │
                    ┌────────┼────────┼────────┼────────┐
                    │        │        │        │        │
                    ▼        ▼        ▼        ▼        ▼
          ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
          │ 响应服务1 │ │ 响应服务2 │ │ 响应服务3 │ │ 响应服务N │  ← 可水平扩展
          │          │ │          │ │          │ │          │
          │ Docker 1 │ │ Docker 2 │ │ Docker 3 │ │ Docker N │
          │ ┌──────┐ │ │ ┌──────┐ │ │ ┌──────┐ │ │ ┌──────┐ │
          │ │ C.C  │ │ │ │ C.C  │ │ │ │ C.C  │ │ │ │ C.C  │ │
          │ │Skills│ │ │ │Skills│ │ │ │Skills│ │ │ │Skills│ │
          │ └──────┘ │ │ └──────┘ │ │ └──────┘ │ │ └──────┘ │
          │    ↓     │ │    ↓     │ │    ↓     │ │    ↓     │
          │   ACP    │ │   ACP    │ │   ACP    │ │   ACP    │  ← ACP 通信层
          └──────────┘ └──────────┘ └──────────┘ └──────────┘
                             │
                             ▼
                  ┌──────────────────┐
                  │  远端持久化存储    │
                  │  · Session 数据库 │
                  │  · Workspace 快照 │
                  │  · 用户/项目元数据 │
                  └──────────────────┘
```

#### 📖 详细解释：Session 持久化两种策略

ACP 有一个公共 Session 的概念——Session 可以被提取、序列化、持久化。基于这一点，有两种生产级的 Session 管理策略：

**策略一：远端持久化 + 注入（无状态）**

```
请求进入
    │
    ▼
分发路由从请求中提取 User ID / Session ID
    │
    ▼
从远端数据库查询对应 Session 数据
    │
    ▼
将 Session 数据注入到目标 Docker 的 local dir
    │
    ▼
Docker 中的 Agent 使用还原后的 Session 工作
    │
    ▼
任务完成后，将更新后的数据回传到远端数据库
    │
    ▼
销毁 Docker 容器和对应的 local dir
```

**策略二：路由粘性（有状态）**

```
请求首次进入 → 分发路由记录 Session 所在服务器
                │
                ▼
后续相同 Session 的请求 → 路由到同一台服务器
                         │
                         ▼
                       直接使用本地已有的状态
                （无需每次从远端注入）
```

| 维度 | 策略一：远端持久化 | 策略二：路由粘性 |
|---|---|---|
| **状态管理** | 无状态，任意服务器可处理 | 有状态，绑定特定服务器 |
| **扩展性** | 优秀，可任意扩缩容 | 一般，需考虑粘性失效 |
| **性能** | 每次需注入/回传，有额外开销 | 本地直接访问，性能最优 |
| **容错** | 服务器宕机无影响，换一台即可 | 服务器宕机会丢失会话 |
| **实现复杂度** | 需要持久化/注入机制 | 只需路由层记录映射 |
| **资源倾斜** | 不会倾斜，均匀分布 | 可能倾斜（长会话集中到某服务器） |
| **适用场景** | 大规模分布式、会话可中断 | 小规模、长会话频繁交互 |

> 💡 **核心洞见**：两种策略可以混合使用。例如：正常情况下用路由粘性保证性能，当检测到目标服务器负载过高或宕机时，切换到远端持久化 + 注入的方式迁移会话到其他服务器。

#### 📖 详细解释：远端数据库 + workspace 默认模式

如果你的数据库在远端，workspace 保持默认配置的一种实现方式：

1. 请求到达分发路由，携带 User ID 和 Project ID
2. 分发路由根据这些信息从远端数据库查询对应的持久化数据
3. 将持久化数据注入到目标 Docker 容器的 local dir
4. Docker 启动 Agent（此时 local dir 已有完整的上下文）
5. Agent 完成任务
6. 在 Docker 销毁前，将 local dir 中的变更数据回传到远端数据库
7. 销毁 Docker 和 local dir（此时数据已在远端安全存储）

这个模式的本质是：**Docker 是临时的执行环境，远端数据库是唯一的状态来源**。

---

### 9.5 ACP vs MCP 终极对比表

> 📌 这是全课程最核心的概念澄清。ACP 和 MCP 的设计目标「不是一个事」。

| 维度 | MCP（Model Context Protocol） | ACP（Agent Communication Protocol） |
|---|---|---|
| **全称** | Model Context Protocol | Agent Communication Protocol |
| **设计目标** | 为 LLM 提供统一的工具调用标准 | 为多 Agent 提供统一的通信和任务分发标准 |
| **抽象层级** | **工具级**：暴露原子能力 `function_name(params)` | **任务级**：暴露完整接口「用哪个 Agent + 任务是什么」 |
| **连接对象** | LLM ↔ 工具服务（数据库、API、文件系统） | 主流程 ↔ 智能 Agent（Claude Code、Codex、自建 Agent） |
| **谁做决策** | 调用方（LLM）决定何时调用哪个工具 | 被调用方（Agent）自主决定如何完成任务 |
| **智能属性** | 协议层无智能，工具服务被动执行 | 协议层无智能，Agent 内部具备自主处理能力 |
| **隔离性** | 不涉及隔离——工具是被动调用的 | 天然隔离——每个 Agent 有独立的 workspace、skills、tools |
| **暴露内容** | 工具列表（名称、参数、描述） | Agent 标识 + 任务输入 + 返回结果 |
| **典型输出** | 工具调用结果（JSON、文本） | 任务完成的报告/产物 |
| **可否不依赖 AI** | 可以（协议层纯标准化） | 可以（Demo 用纯分词逻辑） |
| **核心价值** | **统一工具生态**：一次编写，所有 LLM 可用 | **统一异构交互 + 独立工作空间隔离** |
| **代表实现** | Anthropic MCP Server / Client | Claude Code ACP / Codex ACP / 自建 ACP Adapter |

```
层不一样——用一个比喻来理解：

MCP 像是「工具箱」：
你（LLM）走进工作室，墙上挂满了工具——锤子（search_cve）、
螺丝刀（check_syntax）、扳手（analyze_dep）。
你看到问题 → 挑选工具 → 使用工具 → 完成工作。
工具本身没有「意识」，你才是决策者。

ACP 像是「分工协作」：
你是项目经理（主流程），你不需要自己动手。
你告诉张三（Codex Agent）「去检查代码安全」，
告诉李四（Claude Agent）「去分析依赖风险」。
张三和李四是完整的「人」——他们有自己的工具箱、
自己的工作台、自己的工作方式。
他们独立完成任务后把报告交给你。
你不需要知道他们用了哪些工具、怎么用——
你只需要信任他们的专业能力。
```

---

### 9.6 并发实践指南

#### 🧠 直观理解

并发不是「越多越好」——它是「场景决定上限，硬件决定边界」。在 Agent 系统中，区分 IO 密集型和计算密集型是并发策略设计的起点。

#### 📖 详细解释

**场景一：IO 密集型（远端 API 调用）**

当你的 Agent 主要通过协程处理远端 API 请求（如调用 Claude API、DeepSeek API、远端千问服务），并发上限由以下因素决定：
- 操作系统的协程调度能力
- 网络带宽
- 文件描述符数量限制
- 内存容量

在这种场景下，协程非常适合。因为协程在等待网络 IO 时会主动让出 CPU，所以单个进程可以承载大量协程。老师在自己的 M2 Pro 芯片上实测，**三五千个协程的并发量没有问题**——因为协程的核心工作只是收发网络数据，CPU 大部分时间处于空闲状态。

**场景二：计算密集型（本地模型推理）**

如果你的服务器上运行着本地大模型做推理（如千问 7B、DeepSeek 本地部署），此时：
- 模型推理本身是计算密集型任务，占用大量 CPU/GPU
- 并发上限由硬件算力决定
- 本地千问服务器可能只能同时支持 **2 到 3 个**并发推理请求
- 无论你写了多少异步代码，模型的处理能力有硬上限

**关键认知**：当计算密集型任务达到并发上限时，解决方案不是优化代码，而是**横向扩展**——让路由层将额外请求分发到其他服务器。

#### 📊 并发策略决策表

```
你的 Agent 主要在执行什么？

    ├── 远端 API 调用（IO 密集型）
    │   ├── 并发策略: 协程 / async-await
    │   ├── 单机上限: 数千级
    │   ├── 瓶颈监控: CPU、内存、网络带宽、P99 延迟
    │   └── 扩展方式: 先优化单机，再考虑水平扩展
    │
    └── 本地模型推理（计算密集型）
        ├── 并发策略: 线程池 / 进程池 + 队列
        ├── 单机上限: 2~3 个（取决于硬件）
        ├── 瓶颈监控: GPU 利用率、推理延迟
        └── 扩展方式: 必须水平扩展（多机 + 路由分发）
```

#### 💻 代码示例：协程并发请求模式

```python
# 文件名: concurrent_acp_caller.py
# 功能: 使用协程并发调用远端 Agent API

import asyncio
import aiohttp
from typing import Any

# ACP Agent 的远端地址（实际部署时指向路由层或直接指向 Agent 服务）
AGENT_ENDPOINTS = [
    "http://agent-node-1:8080/acp",
    "http://agent-node-2:8080/acp",
    "http://agent-node-3:8080/acp",
]

async def call_agent(
    session: aiohttp.ClientSession,
    endpoint: str,
    task: str,
    semaphore: asyncio.Semaphore,
) -> dict[str, Any]:
    """通过 ACP 向指定 Agent 发送任务并获取结果。

    Args:
        session: aiohttp 会话（复用连接池）
        endpoint: Agent 服务地址
        task: 任务描述（自然语言）
        semaphore: 并发控制信号量

    Returns:
        Agent 返回的结果字典
    """
    async with semaphore:  # 控制最大并发数
        async with session.post(
            f"{endpoint}/execute",
            json={"task": task},
            timeout=aiohttp.ClientTimeout(total=300),  # 5 分钟超时
        ) as resp:
            return await resp.json()


async def distribute_tasks(tasks: list[str], max_concurrency: int = 100) -> list[dict]:
    """将一批任务并发分发给多个 Agent 节点。

    Args:
        tasks: 任务列表
        max_concurrency: 最大并发协程数（根据压测结果设定）

    Returns:
        所有任务的执行结果列表
    """
    semaphore = asyncio.Semaphore(max_concurrency)  # 并发上限

    async with aiohttp.ClientSession() as session:
        # 为每个任务分配一个 Agent 节点（轮询）
        coroutines = [
            call_agent(
                session,
                AGENT_ENDPOINTS[i % len(AGENT_ENDPOINTS)],
                task,
                semaphore,
            )
            for i, task in enumerate(tasks)
        ]
        return await asyncio.gather(*coroutines)


# 使用示例
if __name__ == "__main__":
    tasks = [f"请分析代码段 {i} 的安全漏洞" for i in range(50)]
    results = asyncio.run(distribute_tasks(tasks, max_concurrency=50))
    print(f"完成 {len(results)} 个任务，成功 {sum(1 for r in results if r.get('ok'))} 个")
```

> ⚠️ **注意事项**：`max_concurrency` 的值需要根据压测结果设定。IO 密集型场景下，M2 Pro 上设置 50-100 通常安全；但如果是本地模型推理，应设为 2-3。生产环境中建议先做压测，从低值开始逐步上调，同时监控系统指标。

---

### 9.7 下节课预告

> 🔗 **下节课内容**：**IM 工具集成——如何让 Agent 与 Slack / 飞书等即时通讯工具连接**

本课程系列已完整覆盖了 Agent 构建的核心能力：
- Skills 的执行与校验（第 14-16 课）
- MCP 工具生态与 Host 构建（第 10-11 课）
- 自建 Agent 与 Adapter 模式（第 12-13 课）
- DAG 编排 + ACP 多 Agent 协同（第 17 课 → 本课）

现在你的 Agent 已经可以执行复杂的任务——通过 Skills 编排本地操作，通过 ACP 分派任务给其他 Agent。下一步的自然延伸是：**如何让 Agent 与真实世界的沟通工具连接？**

下节课将讨论：
- Agent 如何接收来自 IM 工具（Slack / 飞书）的任务
- OpenClaw 与飞书的集成模式
- 远端信息传输的最佳实践

---

## 📋 课程小结

### 🗺️ 知识图谱

```
                        ┌───────────────────────────────┐
                        │      DAG + ACP 多 Agent 协同    │
                        │   「编排决定做什么，ACP 决定找谁做」 │
                        └───────────────┬───────────────┘
                                        │
            ┌───────────────────────────┼───────────────────────────┐
            │                           │                           │
            ▼                           ▼                           ▼
    ┌───────────────┐          ┌───────────────┐          ┌───────────────┐
    │   DAG 编排层   │          │   ACP 通信层   │          │   Agent 执行层 │
    │               │          │               │          │               │
    │ · Planner     │    ──▶   │ · 异构统一     │    ──▶   │ · Claude Code │
    │ · TriggerFlow │          │ · 工作空间隔离  │          │ · Codex       │
    │ · 人工编排    │          │ · 任务分发     │          │ · 自建 Agent  │
    └───────────────┘          │ · 结果回传     │          └───────────────┘
                               └───────────────┘
                                       │
                        ┌──────────────┼──────────────┐
                        │              │              │
                        ▼              ▼              ▼
                  ┌──────────┐  ┌──────────┐  ┌──────────┐
                  │ 生产部署  │  │Session   │  │ 并发策略  │
                  │          │  │持久化    │  │          │
                  │ · Docker │  │ · 远端   │  │ · IO密集  │
                  │ · 路由   │  │ · 粘性   │  │ · 计算密集│
                  └──────────┘  └──────────┘  └──────────┘
```

### 💡 一句话总结

> ACP 的本质不是又一个通信协议——它是将「异构 Agent 的统一交互」和「多 Agent 的独立工作空间隔离」这两个核心价值，通过一个极简的「用哪个 Agent + 任务是什么」的接口封装起来，让 DAG 编排层可以像搭积木一样组合不同的智能模块，构建出复杂而安全的 Agent 协同系统。

### 📍 系列定位

> 📍 **系列定位**：本文是「Agent 架构师企业级智能体系统构建」第 9 篇（最终篇）。
> - 上一篇：第 8 篇「自建 Agent 适配器」——掌握 Adapter 模式，让任何外部服务都能接入 ACP
> - 全系列回顾：从 MCP 生态 → Skills 执行 → 沙盒设计 → ACP 多 Agent 协同 → Q&A 架构总结
> - 下节课：IM 工具集成——Slack & 飞书与 Agent 的连接

---

> 🤖 由 transcript-to-doc v4.1 生成

---

> 🤖 由 transcript-to-doc v4.2 生成 | 参考代码: lessons/17_多Agent协作与任务分发回收/scripts/
