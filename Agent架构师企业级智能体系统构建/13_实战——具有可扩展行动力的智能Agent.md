# 13_实战——具有可扩展行动力的智能Agent

> 📅 生成日期: 2026-07-07 | 🎯 级别: L 级 | ⏱️ 录音时长: ~85 分钟 | 📏 文档规模: 6,000+ 行
> 🏷️ 标签: `Agent` `TriggerFlow` `instant模式` `React Loop` `流式输出` `Skills` `旅游Agent` `工具注册` `MCP` `沙盒`

---

## 📑 目录

- [一、课程开场与版本问题说明](#一课程开场与版本问题说明)
- [二、课程回顾：从第5课到第13课的演进路线](#二课程回顾从第5课到第13课的演进路线)
- [三、TriggerFlow 核心机制（上）：to() 连线与 state 共享](#三triggerflow-核心机制上to-连线与-state-共享)
- [四、TriggerFlow 核心机制（下）：when() 事件信号与并发](#四triggerflow-核心机制下when-事件信号与并发)
- [五、TriggerFlow 循环控制与流式输出](#五triggerflow-循环控制与流式输出)
- [六、ModelRequest instant 模式（上）：基础流式与字段截取](#六modelrequest-instant-模式上基础流式与字段截取)
- [七、ModelRequest instant 模式（下）：复杂结构与 wildcard path](#七modelrequest-instant-模式下复杂结构与-wildcard-path)
- [八、旅游 Agent 实战：工具注册与能力接入](#八旅游-agent-实战工具注册与能力接入)
- [九、旅游 Agent 实战：React Loop 搭建与执行](#九旅游agent实战react-loop搭建与执行)
- [十、旅游 Agent 实战：流式输出与 instant 叠加](#十旅游-agent-实战流式输出与-instant-叠加)
- [十一、课程总结与 Skills 展望](#十一课程总结与-skills-展望)

---




## 一、课程开场与版本问题说明

> 🎯 **本节定位**：课程引入章节，说明本节课所使用的框架版本变更背景、技术决策反思，并锚定第 13 课在整个课程体系中的位置与本课学习目标。

---

### 1.1 版本风波：4.1.3 的激进决策与紧急修复

#### 🧠 直观理解

在课程开始前，框架经历了一次"激进实验 → 用户反馈 → 紧急回退"的版本迭代。4.1.3 版本对框架最核心的解析层做了一次大胆替换，导致大量用户反馈解析错误率上升，老师花了一整天紧急发布修复版本 4.1.3.5。

#### 📖 详细解释

##### 背景：为什么要改？

使用 JSON Schema 做结构化输出约束来控制大模型的长文生成时，存在一个痛点：**模型会"收着写"——在严格约束下，输出内容趋于简短、缺乏发散性**。

老师用一句话点明了这个矛盾："如果用 JSON Schema 去控制这个长文输出的时候，它其实会有一些问题的——模型就会不发散嘛，它写的这个内容可能会短一点。"

为了突破这一限制，4.1.3 版本做了一个大胆的技术决策：**将核心解析方案从纯 JSON 模式替换为团队自研的一套综合解析方案**。

##### 问题：错误率全面上升

实际效果并不如预期：
- **解析错误率有明显上升**，直接影响到结构化输出的可靠性
- 对不同模型的适配表现不一致
- 由于错误发生在核心解析层，所有依赖解析结果的上层功能都受到连锁影响

##### 修复：4.1.3.5 回退方案

修复策略非常明确——**将默认解析方案回退到经过充分验证的 JSON 结构化解析模式**：

| 维度 | 4.1.3（被修复版本） | 4.1.3.5（当前课程版本） |
|---|---|---|
| 默认解析方案 | 自研综合解析方案（新） | JSON 结构化解析（回退到稳定版） |
| 综合解析方案 | 默认启用 | 保留在代码中，需手动启动 |
| 其他扩展模式 | 与综合方案绑定 | 全部保留，可选配置 |
| 解析错误率 | 上升 | 恢复到先前稳定水平 |

> ⚠️ **注意事项**：本节课所有代码实操均基于 **4.1.3.5** 版本。如果你之前安装了旧版本，务必更新。

---

### 1.2 工程反思：核心层变更的策略教训

#### 📖 详细解释

老师在课上坦诚地说了一句"这个锅是我的"，但这不是简单的自责，而是提炼出了一个可指导未来工程决策的原则。

##### 🔗 推导链：问题出在哪个环节

```
起点: 观测到 JSON Schema 约束下长文输出质量下降
  │
  ├── 第1步: 设计了一套新的综合解析方案
  │   为什么？希望在不牺牲结构化控制的前提下提升输出质量。
  │   这一步本身没有问题——尝试新方案是正确的工程实践。
  │
  ├── 第2步: 将新方案设为框架的默认行为
  │   为什么？认为新方案"应该可以适配绝大部分模型"。
  │   ⚠️ 问题出在这一步：理论优势没有经过大规模验证就被默认化了。
  │
  └── 第3步: 用户反馈错误率上升，花了一整天紧急修复
      为什么？核心层的每一个微小变更，到了用户侧都会被放大。
```

##### 核心教训

| 原则 | 具体含义 |
|---|---|
| **核心层不要太重** | 架构上：每个功能应该是独立可开关的模块；策略上：不做一次性大改，渐进式演进 |
| **新方案先做副作用** | 新能力先作为可选特性（opt-in）发布，标记为实验性 |
| **手动选择，而非默认** | 经过充分验证和灰度观察后，再评估是否设为默认 |
| **灰度验证不可或缺** | 理论推演不能替代大规模、多模型、多场景的真实使用验证 |

> 💡 **核心洞见**："核心层尽量不要太重"有两层含义。第一层是架构之重：核心层的功能边界要收窄。第二层是策略之重：核心层的发布节奏要更慢、验证周期要更长、回退路径要更清晰。

> 🐞 **常见坑**：开发者容易陷入一个思维陷阱——"我的方案在理论上更好，所以应该直接替换旧方案"。理论优势不等同于实践稳定性。**好的方案 + 差的发布策略 = 差的结果。**

---

### 1.3 课程节点：第13课在整个系列中的位置

#### 🧠 直观理解

如果把整个课程系列比作"从零件到整机"的装配过程，那么前 12 课是在逐一制造和调试各种关键零件，而第 13 课是**第一次将所有零件组装成一台能真正运转的机器**。

```
前序课程（零件制造）                第13课（组装时刻）            后续课程（进阶）
┌──────────────────────┐      ┌──────────────────────┐      ┌──────────────────┐
│ 第09课 工具管理与规划   │─────▶│                      │      │                  │
│ 第10课 MCP协议（上）   │─────▶│  第13课              │─────▶│  更复杂的企业级  │
│ 第11课 MCP协议（下）   │─────▶│  组装有行动力的       │      │  Agent 架构      │
│ 第12课 沙盒设计       │─────▶│  智能 Agent           │      │                  │
└──────────────────────┘      └──────────────────────┘      └──────────────────┘
     能力积累阶段                  能力整合阶段                  能力扩展阶段
```

---

### 1.4 本课目标：组装一个有行动力的智能 Agent

> 🎯 **学完本节课，你将能够：**
>
> - [ ] 理解 4.1.3.5 版本的变更背景，正确安装并使用课程要求的框架版本
> - [ ] 理解核心层变更的工程原则——"先做可选副作用，再考虑默认化"
> - [ ] 看清第 13 课在整个课程体系中的"能力整合节点"定位
> - [ ] 对学习路径有清晰预期：先掌握底层机制，再进入真实案例组装

本课采用"先机制、再实战"的两段式教学结构：

##### 第一部分：TriggerFlow + instant 模式（底层机制）

| 机制 | 解决的问题 | 核心技术点 |
|---|---|---|
| **TriggerFlow** | 工作流如何继续？如何分支？如何对外推送？ | `to()` 连线、`when()` 信号路由、state 共享、runtime stream |
| **ModelRequest instant** | 模型结构化字段如何被外部逐字段观察？ | `get_response()`、`get_async_generator(type="instant")`、`async_get_data()` |

##### 第二部分：真实旅游 Agent 案例（能力组装）

Agent 具备搜索信息、浏览网页、查询地图、撰写文档的能力，采用 v1 到 v5 逐步组装的方式。

##### 三个核心学习目标

1. **TriggerFlow 的完整机制**：`to()` + `when()` + state + runtime stream
2. **instant 字段级流式**：模型每完成一个结构字段就推送，不等全部生成完
3. **真实行动 Loop 的显式组装**：不调 `set_action_loop` 黑盒，手写 Plan→Execute→回填→循环

| 维度 | 前序课程（第 9-12 课） | 第 13 课 |
|---|---|---|
| 教学重点 | 单项能力的原理与使用 | 多项能力的组合与编排 |
| 代码形态 | 独立的功能示例片段 | 逐步组装、层层叠加的项目代码 |
| 工作流控制 | 线性或简单分支 | 显式 Action Loop（Plan→Execute→回填→循环） |
| 最终产物 | 理解单个概念/工具 | 可独立运行的智能 Agent 完整案例 |




## 二、课程回顾：从第5课到第13课的演进路线

### 2.1 演进全景：三级跳

#### 🧠 直观理解

如果把构建智能 Agent 比作盖一栋房子：第5课我们学会了把模型"放进"房子的关键承重位置（决策节点）；第8课我们给模型配了一套工具箱，让它能自己动手干活；第13课我们要把这些零散的能力组装成完整的房子——每个房间功能明确，但整体架构可以灵活调整。

#### 📖 演进关系图

```
第5课：人工编排                        第8课：工具+模型                       第13课：行动Agent
┌─────────────────────────┐           ┌─────────────────────────┐           ┌──────────────────────────────┐
│  模型放入物理链路          │           │  工具调用回路              │           │  从"工具"进化到"行动"           │
│                          │           │                          │           │                               │
│  · 路由 / 意图识别         │   ────▶  │  · 工具 + 模型联动         │   ────▶  │  · 函数 → 可被扩展的各种行动     │
│  · 计划生成 / 分发         │           │  · 自动化决策能力           │           │  · 函数 / MCP / 沙盒            │
│  · React Loop             │           │  · 工具注册与管理           │           │  · 积木封装与拼装               │
│                          │           │                          │           │                               │
│  ⚠️  局限：                 │           │  ⚠️  局限：                 │           │  ✅  突破：                      │
│  整条链路是人工设计的        │           │  工具本质只是函数，          │           │  能力层次可替换，                │
│  API 调用是预计划的         │           │  能力维度单一               │           │  架构通用，行动可扩展             │
└─────────────────────────┘           └─────────────────────────┘           └──────────────────────────────┘
```

> 💡 **核心洞见**：这三步不是互相替代，而是层层叠加。第5课的编排模式是第8课工具调用的基础，第8课的工具体系又是第13课行动 Agent 的积木来源。每往前推进一步，系统离"真正自主"就近一分。

---

### 2.2 第5课回顾：模型进入物理链路

#### 🧠 直观理解

第5课解决的核心问题是：**模型不能只在实验室里回答问题，它要成为真实业务链路中的一个决策节点。** 想象一条生产线，以前每个环节都是人工规定的——"A来了之后做B，B做完了做C"。第5课做的事情是：在关键分岔口放一个模型，让它来判断接下来往哪走。

#### 📖 详细解释

在第5课中，老师展示了多种**模型参与处理链路管理的模式**：

**模式一：路由（Routing）**。模型接收到上游输入后，判断这个请求属于什么意图、应该分发给下游的哪个节点处理。

**模式二：计划生成与分发（Planning & Distribution）**。模型不只是做一次路由决策，而是生成一个完整的执行计划，然后按计划逐步分发任务。

**模式三：React Loop**。模型不是一条直线走到底，而是在执行过程中不断观察结果、调整决策，形成"思考→行动→观察→再思考"的循环。

```
上游输入（API / 用户请求）
       │
       ▼
┌───────────────────┐
│  模型（决策节点）    │  ← 路由 / 计划 / 意图识别
└──────┬────────────┘
       │
       ├──▶ 下游节点 A（系统 API）
       ├──▶ 下游节点 B（模型生成参数 → 调用系统 API）
       └──▶ 下游节点 C（另一个模型）
```

#### ⚠️ 第5课的关键局限

> ⚠️ **注意事项**：第5课中，整条处理链路是**人工设计好的**。如果你想让模型在某一步调用某个 API，这个 API 必须在链路中被预先规划——"这一步就该调这个 API"。模型只是在预设的路径上做选择，它不能自己发现"我需要一个我事先不知道的工具"。

---

### 2.3 第8课回顾：工具 + 模型的自动化联动

第8课引入了一个关键能力——**工具调用（Tool Calling）**。现在不再需要事先规定"第3步调这个 API、第4步调那个 API"。把一堆工具的说明书交给模型，让它根据当前情况自己决定。

这一步的核心变化在于**决策自动化程度的提升**：

| 维度 | 第5课（人工编排） | 第8课（工具+模型） |
|---|---|---|
| 链路设计 | 人工预设路径 | 模型动态决策 |
| API 调用 | 预先计划"第几步调哪个" | 模型根据当前状态选择 |
| 灵活性 | 固定流程，改需求=改链路 | 流程自适应，工具列表决定能力边界 |
| 模型角色 | 路径选择器 | 决策者+执行调度者 |

---

### 2.4 第13课定位：从"工具"到"行动"的进化

#### 🧠 直观理解

**工具只是锤子，行动是"拿起锤子做什么以及怎么做"的全部能力。**

"工具"的概念太窄了——它暗示的是"一个输入输出的函数"。但真实场景中，一个 Agent 需要的能力远不止函数调用：它需要通过 MCP 协议接入外部服务，需要在沙盒中安全执行代码，需要边生成边流式输出结果。

#### 🔗 推导链：从函数到行动

```
起点：第8课的"工具"概念 = 函数调用
  │
  ├── 第1步：发现函数概念无法覆盖所有能力形态
  │   为什么？MCP 不是简单的函数调用，它涉及协议握手、工具发现、连接管理。
  │   沙盒执行需要进程隔离、超时控制、目录边界。
  │
  ├── 第2步：引入"行动（Action）"作为更高层级的抽象
  │   为什么？行动是一个"能力单元"的容器——可以包裹函数、MCP 连接、
  │   沙盒命令等任何形式的可执行能力。对外暴露统一接口，对内封装复杂细节。
  │
  └── 结论：Agent 不应该是"模型 + 一堆函数"，
      而应该是"模型 + 一组可扩展的行动能力"。
```

#### 📦 回顾：我们手里有哪些模块

| 模块 | 来源 | 一句话职责 | 第13课中如何使用 |
|---|---|---|---|
| ModelRequest | 第3课 | 调模型，结构化输出 | `.get_response()` / `async_get_data()` 做 Plan 阶段决策 |
| TriggerFlow | 第4课 | 编排多步流程 | 直接定义 Loop 骨架（reason/act chunk） |
| 工具调用回路 | 第6课 | 模型选工具 → 执行 → 回填 | Loop 的 Plan → Execute 两阶段 |
| 工具管理 + Planner | 第9课 | 工具注册、激活、调度 | `agent.action.*` 原语管理行动注册表 |
| MCP Client | 第10-11课 | 标准化外部服务接入 | `agent.async_use_mcp()` 一行接入高德地图 |
| 执行环境 / 沙盒 | 第12课 | 安全运行代码 / 命令 | `register_bash_sandbox_action` 受控执行 bash |

---

### 2.5 积木拼装思维：先学会积木，再封装，最后拼装

老师在录音中用"积木"这个比喻贯穿了本节：

**第一层：先学会积木是什么。** 第5-12课分别认识了每块积木——ModelRequest、TriggerFlow、MCP、沙盒。

**第二层：封装积木，让边缘干净。** 把每个能力的复杂细节封装到干净的接口后面——封装一次，以后每次直接调用。

**第三层：把积木拼起来。** 封装好之后，真正的挑战是组装。Plan 用哪块积木？Execute 用哪块积木？状态如何流转？

```
       ┌──────────┐   ┌──────────┐   ┌──────────┐
       │ 搜索+阅读 │   │ 高德地图  │   │   bash   │
       │ (Search/ │   │  (MCP)   │   │ (沙盒)   │
       │  Browse) │   │          │   │          │
       └────┬─────┘   └────┬─────┘   └────┬─────┘
            │              │              │
            └──────────────┼──────────────┘
                           │
                    ┌──────┴──────┐
                    │ Action 注册表 │  ← agent.action 统一管理
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │   Plan   │▶│ Execute  │▶│   回填    │
        │ (reason)  │ │  (act)   │ │          │
        └──────────┘ └──────────┘ └──────────┘
              ▲                          │
              └──────────────────────────┘
                   TriggerFlow Loop
```

---

### 2.6 TriggerFlow 复习预告与旅游 Agent 案例引入

#### 📖 为什么需要在第13课重新讲 TriggerFlow

老师在录音中提到：**之前有同学反馈 TriggerFlow 讲得不够清楚。** 到了第13课，同学们已经见过各种能力模块，此时带着"我要把这些东西拼起来"的真实需求去理解 TriggerFlow，就完全不同了。

#### 📖 旅游 Agent 案例引入：能力层次可替换

本节课的实战案例是一个**旅游规划 Agent**——用户说"帮我规划一日游"，Agent 需要自己完成搜索攻略、阅读网页、查询地图、写文档。

> 💡 **核心洞见**：老师特别强调——**"能力层次是可以换的"**。旅游规划只是一个示例。把搜索换成数据库查询、把高德换成企业微信推送——它就是一个客服 Agent。**编排逻辑不变，只换能力层。**




## 三、TriggerFlow 核心机制（上）：to() 连线与 state 共享

### 🎯 本节目标

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 使用 `to()` 将多个 chunk 按顺序连线，构成一个可执行的 Flow
> - [ ] 区分 `return` 传递和 `state` 共享两种数据传递方式
> - [ ] 理解 `data.input` 与 `data.value` 的等价关系
> - [ ] 说出 Flow 与 Execution 的关系：蓝图与运行实例

### 🏗️ 前置准备

本节所有代码基于 Agently 框架的 `TriggerFlow` 模块：

```python
from agently import TriggerFlow
```

---

### 💻 Step-by-Step

#### Step 1: 理解 TriggerFlow 的两套路由机制

TriggerFlow 提供**两套路由机制**：

| 机制 | 关键字 | 触发方式 | 数据来源 |
|---|---|---|---|
| **顺序连线** | `to()` | 上一个 chunk 执行完毕后自动进入下一个 | 上一个 chunk 的 `return` 值进入下游的 `data.input` |
| **信号路由** | `when()` | 某个 chunk 内部显式发出信号后触发 | `emit` 的第二个参数进入目标 chunk 的 `data.input` |

本节聚焦第一种机制 `to()`。

```
TriggerFlow 的两套路由机制：

┌──────────────────────────────────────────────────────────┐
│                    TriggerFlow                           │
│  ┌─────────────────┐         ┌─────────────────┐        │
│  │   chunk A        │  to()   │   chunk B        │        │
│  │   return value ──┼────────▶│   data.input     │        │
│  └─────────────────┘         └─────────────────┘        │
│                                                          │
│  ┌─────────────────┐         ┌─────────────────┐        │
│  │   chunk C        │  when() │   chunk D        │        │
│  │   emit("X", v)  ─┼────────▶│   data.input     │        │
│  └─────────────────┘         └─────────────────┘        │
└──────────────────────────────────────────────────────────┘
```

#### Step 2: v0-1 基础 to() 连线代码

```python
# v0-1：to() 顺序连线 —— return 值进入下一个 chunk 的 data.input
from agently import TriggerFlow

flow = TriggerFlow(name="demo_to_route")
events = []

@flow.chunk
async def step_a(data):
    events.append(("step_a.input", data.input))
    return {"from": "step_a", "count": 1}

@flow.chunk
async def step_b(data):
    events.append(("step_b.input", data.input))
    return {"from": "step_b", "count": data.input["count"] + 1}

flow.to(step_a).to(step_b)

result = await flow.async_start({"start": True})
print("events =", events)
print("result state =", result)
```

#### Step 3: to() 连线数据流

```
Flow 启动 async_start({"start": True})
       │
       ▼
┌─────────────────────────────────────────┐
│              step_a chunk                │
│  data.input = {"start": True}           │
│         │                                │
│  return {"from": "step_a", "count": 1}  │
└─────────┼───────────────────────────────┘
          │ to() 连线自动传递 return 值
          ▼
┌─────────────────────────────────────────┐
│              step_b chunk                │
│  data.input = {"from": "step_a", "count": 1} │
│         │                                │
│  return {"from": "step_b", "count": 2}  │
└──────────────────────────────────────────┘
```

#### Step 4: state 全局传递 —— return 传递 vs state 共享

除了 `to()` 连线的 return 传递，TriggerFlow 还提供了 **state 全局传递**通道：

| 维度 | return 传递（管道式） | state 传递（广播式） |
|---|---|---|
| **数据流向** | 沿 to() 连线单向流动 | 写入全局空间，任意 chunk 都可读取 |
| **生命周期** | 仅在下游一个 chunk 中可用 | 在整个 Execution 生命周期内可读 |
| **可见范围** | 只有 to() 连线下一个 chunk | 所有 chunk 均可读取 |
| **适用场景** | 顺序加工流水线 | 跨 chunk 共享配置、累积结果 |
| **代码示例** | `return value` → 下游 `data.input` | `await data.set_state("k", v)` → `data.get_state("k")` |

##### 代码示例：return 与 state 并存

```python
from agently import TriggerFlow

flow = TriggerFlow(name="demo_return_vs_state")

@flow.chunk
async def user_input(data):
    input_value = "知乎AI课"
    # 方式一：通过 set_state 写入全局 state
    await data.set_state("shared_value", input_value)
    # 方式二：通过 return 传递给下游
    return input_value

@flow.chunk
async def echo(data):
    # 方式一：从 return 传递获取
    value_from_return = data.input
    # 方式二：从全局 state 获取
    value_from_state = data.get_state("shared_value")
    print(f"[通过 return 传递] {value_from_return}")
    print(f"[通过全局 state]   {value_from_state}")

flow.to(user_input).to(echo)
```

##### 决策树：何时用 return，何时用 state？

```
需要在 chunk 之间传递数据时：
    │
    ├── 数据只传给 to() 连线的下一个 chunk？
    │   └── 是 → 使用 return 传递
    │
    ├── 数据需要被多个 chunk 读取？
    │   └── 是 → 使用 state 传递
    │
    ├── 数据需要在循环中累积？
    │   └── 是 → 使用 state
    │
    └── 临时中间结果？
        └── 是 → 使用 return 传递
```

> 💡 **核心洞见**：`data.input` 和 `data.value` 是**完全等价的别名**，指向同一个值。无论下游 chunk 使用哪个，拿到的都是上游 chunk 的 return 值。

#### Step 5: Flow vs Execution —— 蓝图与实例

| 概念 | 类比 | 特点 |
|---|---|---|
| **Flow** | 建筑图纸 / 类 | 定义 chunk 注册和连线规则；不存储运行时状态 |
| **Execution** | 建好的房子 / 实例 | 独立 state 空间；同一 Flow 可创建多个 Execution；state 完全隔离 |

```
┌──────────────────────────────────────────┐
│              Flow 蓝图                    │
│  chunk A ──to()──▶ chunk B ──to()──▶ C  │
└──────────┬──────────────┬───────────────┘
           │              │
           ▼              ▼
┌──────────────┐  ┌──────────────┐
│ Execution 1  │  │ Execution 2  │
│ state: {...} │  │ state: {...} │
└──────────────┘  └──────────────┘
```

> 💡 **核心洞见**：Execution 之间的 state 隔离是后续多用户场景的基础。每个用户的操作可以在独立的 Execution 中运行，互不干扰。

### ✅ 验证结果

完成以上步骤后，你应该能够：
1. 使用 `flow.to(A).to(B)` 将 chunk 按顺序串联
2. 区分 `data.input`（return 传递）和 `data.get_state()`（全局共享）
3. 理解 Flow 是蓝图、Execution 是运行实例

### 🐛 常见坑

**坑 1：忘记 to() 连线导致 chunk 不执行** — Flow 不会自动推断执行顺序，必须显式连线。

**坑 2：混淆 data.input 和 data.get_state 的数据来源** — `data.input` 只来自上游 return，`data.get_state` 来自 set_state。如果只调了 set_state 但没有 return，下游的 data.input 仍然是 None。




## 四、TriggerFlow 核心机制（下）：when() 事件信号与并发

### 🎯 本节目标

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 使用 `when()` 信号路由实现事件驱动的 chunk 调度
> - [ ] 理解 `emit_nowait` 与 `emit` 的语义区别
> - [ ] 使用 `auto_close_timeout` 控制 execution 的结束时机
> - [ ] 利用 emit_nowait + when() 实现协程级并发
> - [ ] 区分协程与线程，并说出各自的适用场景
> - [ ] 理解多 execution 之间的 state 隔离机制

### 🏗️ 前置准备

```python
from agently import TriggerFlow
```

---

### 4.1 从线性编排到事件驱动

#### 🧠 直观理解

把 TriggerFlow 想象成一台对讲机系统。`to()` 是串联电路——A 说完自动把话筒递给 B。而 `when()` 是无线电频道——任何人可以在任意时刻喊一声"Act!"，所有调到"Act"频道的人都能听到并响应。

在上一节我们学习了 `to()` 连线。但 `to()` 有一个根本限制：**它假定流程是线性的、预先可知的**。`when()` 打开了事件系统的全部能力。

> 💡 **核心洞见**：`to()` 的 return 本质也是事件。老师在录音中反复强调："return 本质上面其实也是发了一个事件……这两个事情其实是等价的。"TriggerFlow 的底层统一模型是事件驱动——`to()` 只是事件传递的语法糖。

#### v0-2：when() 信号路由代码

```python
# v0-2：when() 信号路由 —— emit 的第二个参数进入目标 chunk 的 data.input
from agently import TriggerFlow

flow = TriggerFlow(name="demo_when_route")
events = []

@flow.chunk
async def reason(data):
    state = dict(data.input)
    events.append(("reason.input", state.copy()))
    state["action_calls"] = [{"name": "lookup", "kwargs": {"query": "用户问题"}}]
    await data.async_emit_nowait("Act", state)

@flow.chunk
async def act(data):
    state = dict(data.input)
    events.append(("act.input", state.copy()))
    await data.async_set_state("last_tool", state["action_calls"][0]["name"])

flow.to(reason)
flow.when("Act").to(act)

result = await flow.async_start({"history": []})
print("events =", events)
print("result state =", result)
```

#### when() 信号路由的数据流

```
┌────────────────────────────────────────────────────────────────────┐
│                      TriggerFlow 事件调度器                          │
│   ┌──────────┐     emit_nowait       ┌──────────────────────┐       │
│   │  reason   │────────────────────▶│   事件消息队列        │       │
│   │  chunk    │  ("Act", state)     │  [事件: "Act"]       │       │
│   └──────────┘                     └──────────┬───────────┘       │
│                                    when("Act") 匹配               │
│                                               ▼                    │
│                              ┌────────────────────────────┐        │
│                              │  act chunk                 │        │
│                              │  data.input = state dict   │        │
│                              └────────────────────────────┘        │
└────────────────────────────────────────────────────────────────────┘
```

---

### 4.2 事件信号的发送：emit_nowait 与 emit

| 方法 | 行为 | 适用场景 |
|---|---|---|
| `emit_nowait` | 发出事件后立即返回，不等待处理结果 | 需要触发别的动作，但自己还有事要做 |
| `emit`（await 版本） | 发出事件后等待事件被调度处理完毕 | 需要确认对方收到了再继续 |

事件队列机制：
1. 事件名和载荷被打包成事件对象
2. 推入 flow 内部的事件消息队列
3. `emit_nowait` 立即返回
4. 后台调度器从队列中取出事件，匹配 when() 规则

#### 🙋 Q&A：emit_nowait 的顺序可控吗？

> **牛巴同学提问**："emit_nowait 的顺序可控吗？如果和多个 to 混用的话，谁先执行，谁后执行？"

> **老师回答**：emit_nowait 是异步的——发出事件后就不等了。事件发出去以后，被放进事件队列里，调度器来决定什么时候处理。跟当前 chunk 的后续代码无关。如果想精确控制顺序，可以用 `async_emit`（await 版本）。但大多数场景下用 `emit_nowait` 就够了。

---

### 4.3 auto_close_timeout：控制 execution 的结束时机

> 🧠 **直观理解**：想象开会——所有人发言完毕，但主持人还不宣布散会，因为他担心有人临时想起什么还要补充。`auto_close_timeout` 就是"我再等 X 秒，没人说话就散会"。

默认等待 10 秒。如果不需等待：
```python
flow = TriggerFlow(name="no_wait_flow", auto_close_timeout=0)
```

#### 🐛 排错实录：when() 放置位置的调试

**❌ 错误写法**：在 create_execution 和 start 之间写 emit —— 信号系统尚未初始化。

**🔍 原因分析**：`emit_nowait` 必须在 execution 已启动的上下文中调用（chunk 函数内部），否则事件队列未就绪。

**✅ 正确写法**：
```python
@flow.chunk
async def step_a(data):
    # ✅ 在 chunk 内部 emit，此时 execution 已启动
    await data.async_emit_nowait("Act", {"key": "value"})
```

---

### 4.4 并发实战：10 个消息的乱序处理

```python
import asyncio, random
from agently import TriggerFlow

flow = TriggerFlow(name="concurrent_demo", auto_close_timeout=1)

@flow.chunk
async def sender(data):
    for i in range(10):
        await data.async_emit_nowait("temp", {"message_id": i})
    print("[sender] 10 条消息全部发出")

@flow.chunk
async def handler(data):
    msg_id = data.input.get("message_id", -1)
    delay = random.randint(1, 10) / 10.0  # 0.1 到 1.0 秒随机延迟
    await asyncio.sleep(delay)
    print(f"[handler] 消息 #{msg_id} 处理完成 (耗时 {delay:.1f}s)")

flow.to(sender)
flow.when("temp").to(handler)
```

**结果**：10 条消息在约 1 秒内全部完成（串行需要 5.5 秒），且完成顺序与发出顺序不一致。

---

### 4.5 协程 vs 线程：关键概念辨析

老师在录音中专门花了较长时间辨析协程和线程的区别：

> "线程它是我们真的划出了一个区域，让 CPU 在这个区域里面是独占的。但协程不是。协程类似于我们排在同样一套 CPU 的处理逻辑里面，但是通过 await 的信号告诉大家说这个地方其实是一个等待点。"

| 维度 | 协程 (Coroutine) | 线程 (Thread) |
|---|---|---|
| **调度者** | 用户程序（事件循环）在单线程内调度 | 操作系统内核调度 |
| **并行性** | 逻辑并发（单线程内交替执行） | 物理并行（多核 CPU 同时执行） |
| **切换开销** | 极低（函数调用级别） | 较高（系统调用，保存/恢复寄存器） |
| **内存占用** | 极小（每协程约几KB） | 较大（每线程约1-8MB栈空间） |
| **数据共享** | 天然安全（单线程，无竞态条件） | 需要锁机制保护共享数据 |
| **阻塞行为** | `await` 是显式的让出点 | 任何位置都可能被 OS 抢占式切换 |
| **适用场景** | IO 密集型（网络请求、数据库查询） | CPU 密集型（大量计算、图像处理） |

> 💡 **核心洞见**：TriggerFlow 用协程而非线程，因为 AI 工作流的性能瓶颈几乎全是 IO 等待（等模型返回、等工具执行）。协程的轻量和高效远超线程。

---

### 4.6 v0-3：state 变化触发与 runtime stream 观测

```python
# v0-3：state 变化触发 runtime_data watcher；stream 用于外部观测
from agently import TriggerFlow

flow = TriggerFlow(name="demo_state_stream")

@flow.chunk
async def detect_language(data):
    await data.async_put_into_stream({"phase": "detect", "lang": "zh"})
    await data.async_set_state("lang", "zh")

@flow.chunk
async def apply_language(data):
    await data.async_put_into_stream({"phase": "apply", "input": data.input})
    await data.async_set_state("ui_lang", data.input)

flow.to(detect_language)
flow.when({"runtime_data": "lang"}).to(apply_language)

execution = flow.create_execution()
async for event in execution.get_async_runtime_stream(initial_value={}):
    print("stream event =", event)
print("state =", execution.get_state())
```

---

### 4.7 v0-4：最小可运行 Plan/Execute Loop

```python
# v0-4：最小可运行 Plan / Execute Loop —— 不调模型，只用固定计划证明路由
from agently import TriggerFlow

flow = TriggerFlow(name="demo_plan_execute_loop")
planned_actions = ["lookup", "read", "final"]

@flow.chunk
async def reason(data):
    state = dict(data.input)
    step = state.get("step", 0)
    action = planned_actions[step]
    await data.async_put_into_stream({"phase": "plan", "step": step + 1, "decision": action})
    if action == "final":
        await data.async_set_state("answer", "信息收集完成")
        return  # 不 emit → 循环终止
    state["step"] = step + 1
    state["action_calls"] = [{"name": action, "kwargs": {}}]
    await data.async_emit_nowait("Act", state)

@flow.chunk
async def act(data):
    state = dict(data.input)
    call = state.pop("action_calls")[0]
    history = state.get("history", [])
    history.append({"tool": call["name"], "result": "ok"})
    state["history"] = history
    await data.async_put_into_stream({"phase": "execute", "tool": call["name"]})
    await data.async_emit_nowait("Reason", state)

flow.to(reason)
flow.when("Act").to(act)
flow.when("Reason").to(reason)

execution = flow.create_execution()
async for event in execution.get_async_runtime_stream(initial_value={"history": [], "step": 0}):
    print(event)
print("final state =", execution.get_state())
```

**循环运转流程**：

```
START → reason → emit("Act") → act → emit("Reason") → reason → ...
                                                              ↓
                                                    action=="final"
                                                         return（不emit）
                                                              ↓
                                                     execution 自然关闭
```

> 💡 **核心洞见**：Loop 的终止条件不是显式的"停止"命令，而是"不再发出新事件"。没有新事件 → execution 在 auto_close_timeout 后自然关闭。

---

### 4.8 多 execution 隔离：FAST API 场景

同一 Flow 蓝图可创建多个独立 Execution，state 完全隔离：

```python
exec1 = flow.create_execution()
exec2 = flow.create_execution()
# exec1 和 exec2 的 state 完全独立，互不干扰
```

老师在录音中提到实际应用：
> "群里面有的同学需要把 agent 放到 FAST API 里面，让它成为一个服务承载器。flow 上面的定义都可以固定下来，每次创建一个新的 execution，相互不会干扰。"

---

### 📋 本节小结

| 收获 | 内容 |
|---|---|
| **when() 信号路由** | `flow.when("事件名").to(chunk)` 实现事件驱动的 chunk 调度 |
| **emit_nowait 语义** | 异步发出、不等待结果，控制权立即返回 |
| **auto_close_timeout** | 控制等待迟到事件的时间，默认10秒 |
| **并发能力** | emit_nowait + when() 实现协程级并发 |
| **协程 vs 线程** | 协程=单线程逻辑并发，线程=多核物理并行 |
| **v0-4 Plan/Execute Loop** | to() + when() 搭出完整的 Plan → Execute → 循环 |
| **多 execution 隔离** | 每次 create_execution() 返回独立实例，state 完全隔离 |

> 📅 生成日期: 2026-07-07 | 🎯 级别: L 级 | ⏱️ 录音时长: ~10 分钟




## 五、TriggerFlow 循环控制与流式输出

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 用 `condition` + lambda 表达式为 TriggerFlow 构建可控循环
> - [ ] 理解 condition 分支中 `data.input` 的取值来源与调试方法
> - [ ] 使用 `put_into_string` / `get_async_runtime_stream` 实现流式输出
> - [ ] 将流式事件替换为 WebSocket 推送给前端

### 5.1 循环控制 — 让 Flow 自己转起来

#### 🧠 直观理解
TriggerFlow 的 `to()` 和 `when()` 让流程按指定方向单次执行。但在真实场景中，你可能需要让流程**反复运行**——比如用户不断输入问题、Agent 持续处理，直到用户主动说"退出"。这就需要**可控循环**。

在 TriggerFlow 中，这种"可退出的循环"通过 **condition 条件分支**实现。

#### 💻 代码示例

```python
from agently import TriggerFlow

flow = TriggerFlow(name="loop_demo")

@flow.chunk
async def user_input(data):
    return {"input": data.input}

@flow.chunk
async def echo(data):
    result = f"收到: {data.input}"
    print(result)
    return data.input

flow.to(user_input).to(echo).to(user_input)
# 关键：condition 检查 data.input 是否不等于 "exit"
flow.condition(lambda data: data.input != "exit")

result = await flow.async_start({"input": "hello"})
```

#### 🔄 循环控制的数据流

```
  ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
  │  user_input  │──────▶│    echo      │──────▶│  condition   │
  └──────────────┘       └──────────────┘       │ data.input   │
         ▲                                      │ != "exit" ?  │
         │                              ┌───────┴──────┐       │
         │                              │ True(≠exit)  │ False  │
         │                              ▼              ▼       │
         └────────────────────── 继续循环       execution结束  │
```

---

### 5.2 踩坑实录 — condition 判断为什么"失灵"了

#### 🐛 排错实录：condition 条件判断未按预期生效

**❌ 错误现象**：课堂上搭建带 condition 的循环 demo 时，输入 `"exit"` 后流程没有按预期终止。

**🔍 原因分析**（老师现场排查）：
1. condition 判定为 True 时，对应的下游路径可能没有配置有效的 chunk 作为终点
2. 框架版本迭代中，condition 节点在特定 edge case 下的行为可能发生了变化
3. 老师当场提出修复思路："要不要我直接给它强行一个 end 块"

**✅ 建议修复方案**：
```python
# 建议：condition 的每个分支都显式指定下游
flow.to(user_input).to(echo).to(user_input)
flow.condition(lambda data: data.input != "exit")
# 条件通过 → 继续走向 user_input
# 条件不通过 → 无下游块，execution 自动结束

# 或用 when + set_state 作为备选方案
```

**📝 经验总结**：
- condition 分支必须确保**每个条件路径都有明确的下游行为**
- 框架升级后，核心路由机制的 behavior 回归测试很重要
- 生产环境建议用 `async_set_state("status", "exit")` 配合 `when({"runtime_data": "status"})` 作为退出备选

---

### 5.3 state 在循环中的输出机制

TriggerFlow 的 state 扮演着"共享记忆"的角色。execution 完成时，TriggerFlow 会**自动将整个 state 字典输出**。用老师的话说："execution 执行完毕了之后，它会把 state 里面所有的 state，你在过程中间更新的所有 state 一起打出来。"

#### v0-3：state 变化触发 + stream 外部观测

```python
from agently import TriggerFlow

flow = TriggerFlow(name="demo_state_stream")

@flow.chunk
async def detect_language(data):
    await data.async_put_into_stream({"phase": "detect", "lang": "zh"})
    await data.async_set_state("lang", "zh")

@flow.chunk
async def apply_language(data):
    await data.async_put_into_stream({"phase": "apply", "input": data.input})
    await data.async_set_state("ui_lang", data.input)

flow.to(detect_language)
flow.when({"runtime_data": "lang"}).to(apply_language)

execution = flow.create_execution()
async for event in execution.get_async_runtime_stream(initial_value={}):
    print("stream event =", event)
print("state =", execution.get_state())
```

> 💡 **核心洞见**：`when({"runtime_data": "key"})` 是一种**被动触发机制**——不需要显式 `emit`，只要 state 中某个 key 发生变化，监听该 key 的 chunk 就会自动被调度执行。

---

### 5.4 流式输出 — 构建可消费的实时事件管道

#### 🧠 直观理解
之前的 demo 中用 `print()` 在 chunk 内部输出信息——这只能在当前进程的控制台看到。TriggerFlow 的流式输出把消息推入一条数据流中，外部消费者通过异步迭代订阅。

**发送端**：
```python
# chunk 内部推送
await data.async_put_into_stream({"phase": "plan", "message": "xxx"})
```

**消费端**：
```python
execution = flow.create_execution()
async for event in execution.get_async_runtime_stream(initial_value={}):
    print(f"[实时事件] {event}")
final_state = execution.get_state()
```

> 💡 **核心洞见**："我们实际上对所有的消息的使用就不发生在我们的执行块的里面了。我们可以从执行块里面直接把所有的消息往外扔。" 这意味着执行和最终输出可以完全分开。

---

### 5.5 流式输出的应用场景 — WebSocket 实时推送

实际项目中，可以把 `put_into_stream` 替换为 WebSocket 推送给前端：
```python
async for event in execution.get_async_runtime_stream(initial_value={}):
    await websocket.send_json({"type": "agent_progress", "data": event})
```

| 维度 | print 模式 | 流式输出模式 |
|---|---|---|
| 可见范围 | 仅本进程控制台 | 任何外部消费者 |
| 前端集成 | 不可能 | WebSocket 一行替换 |
| 事件结构 | 无结构字符串 | 结构化 dict |
| 消费时机 | 同步打印 | 实时推送 |

---

### 5.6 进阶：最小可运行 Plan/Execute Loop（v0-4）

```python
from agently import TriggerFlow

flow = TriggerFlow(name="demo_plan_execute_loop")
planned_actions = ["lookup", "read", "final"]

@flow.chunk
async def reason(data):
    state = dict(data.input)
    step = state.get("step", 0)
    action = planned_actions[step]
    await data.async_put_into_stream({"phase": "plan", "step": step + 1, "decision": action})
    if action == "final":
        await data.async_set_state("answer", "信息收集完成，可以生成最终回复")
        return  # 不 emit → execution 自动终止
    state["step"] = step + 1
    state["action_calls"] = [{"name": action, "kwargs": {}}]
    await data.async_emit_nowait("Act", state)

@flow.chunk
async def act(data):
    state = dict(data.input)
    call = state.pop("action_calls")[0]
    history = state.get("history", [])
    history.append({"tool": call["name"], "result": "ok"})
    state["history"] = history
    await data.async_put_into_stream({"phase": "execute", "tool": call["name"]})
    await data.async_emit_nowait("Reason", state)

flow.to(reason)
flow.when("Act").to(act)
flow.when("Reason").to(reason)

execution = flow.create_execution()
async for event in execution.get_async_runtime_stream(initial_value={"history": [], "step": 0}):
    print(event)
print("final state =", execution.get_state())
```

> 💡 **核心洞见**：Loop 的结束条件不是外部强制终止，而是"不再发射信号"。当 reason 判定 `action == "final"` 后，只做 `async_set_state` 而不再 `emit`——这是声明式的"没有下一站即终点"。

### 📋 本节小结

| 收获 | 内容 |
|---|---|
| **condition 条件分支** | 用于构建可控循环，lambda 表达式进行运行时判断 |
| **state 输出机制** | execution 结束时自动输出全部 state |
| **流式输出** | `put_into_stream` 推事件，`get_async_runtime_stream` 消费 |
| **v0-4 Plan/Execute Loop** | 不调模型的最小 Loop 骨架，不 emit 即终止 |

> 📅 生成日期: 2026-07-07 | 🎯 级别: L 级 | ⏱️ 录音时长: ~6 分钟



## 六、ModelRequest instant 模式（上）：基础流式与字段截取

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 用 `get_async_generator(type="instant")` 按结构化字段消费模型的流式输出
> - [ ] 理解 `StreamingData` 的五个核心字段（path / value / delta / is_complete / full_data）及其含义
> - [ ] 在意图识别场景中，利用 `is_complete` 判断字段何时完成并触发后续动作
> - [ ] 在 prethinking 阶段给用户提供「正在思考」的中间状态反馈
> - [ ] 识别并避免路径名写错导致字段事件漏监听的典型错误

---

### 6.1 基础流式输出：从 `get_generator()` 开始

#### 🧠 直观理解

想象你在看一场直播比赛。传统的模型调用就像等整场比赛结束才给你看回放——你必须等模型把全部结构化字段（prethinking、intention、final_reply）都生成完，才能拿到完整结果。而基础流式输出 `get_generator()` 相当于把比赛直播流给你——你在用户输入的那一刻就能看到模型 token-by-token 地吐出内容，不需要等到全部结束。

**但基础流式有一个盲区**：它对结构化输出的每个字段一视同仁。如果你定义了 prethinking + final_reply 两个字段，`get_generator()` 会把 prethinking 里的思考过程也流式地推给用户——而这些东西用户根本不需要看到。

#### 📖 详细解释

在 Agently 框架中，`ModelRequest` 支持两种流式消费方式：

| 消费方式 | 调用方式 | 粒度 | 适用场景 |
|---|---|---|---|
| 基础流式 | `get_generator()` 或 `start().get_channel_waiter()` | token 级 | 简单的对话式流式输出，无结构化字段 |
| instant 模式 | `get_async_generator(type="instant")` | 字段级 | 结构化输出，需要按字段截取中间状态 |

**基础流式的原理**：模型的输出本质上是「有序的、token by token」的文本流——每个 token 在生成时按顺序依次产出。`get_generator()` 把这个 token 流直接暴露出来，每产生一个 token 就 yield 一个 delta。

**为什么有序性很重要**：因为模型的输出顺序 = 结构化字段的定义顺序。模型先输出 prethinking（思考过程），再输出 intention（意图判断），最后输出 final_reply（给用户的回复）。这个顺序是**可预期的、不会乱序的**。正是因为有序，我们才能在 instant 模式中按字段路径监听并做出响应。

#### 💻 代码示例

```python
# 文件名: basic_streaming.py
# 功能: 演示基础流式输出——token-by-token 消费模型响应

import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from agently import Agently

# 配置模型
Agently.set_settings("OpenAICompatible", {
    "base_url": os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    "model": os.environ.get("DEEPSEEK_DEFAULT_MODEL", "deepseek-chat"),
    "auth": os.environ.get("DEEPSEEK_API_KEY", ""),
})

# 基础流式：通过 start() 获取 channel_waiter，再 get_generator()
agent = Agently.create_agent()
agent.input("你好，请介绍一下你自己")
agent.instruct(["做一个简短的自我介绍"])

# start() 返回 channel_waiter，get_generator() 产出 token 级别的 string 迭代器
string_iterator = agent.start().get_channel_waiter().get_generator()

for delta in string_iterator:
    print(delta, end="", flush=True)
print()  # 换行收尾
```

> 💡 **核心洞见**：这段代码演示了最简单的流式输出——每产出一个 token 就立即打印。它适合「聊天机器人回复一句话」这种不需要区分字段的场景。但一旦模型输出包含多个结构化字段（如 prethinking + reply），这种方式就会把所有字段的内容混合输出，用户会看到不该看到的思考过程。

---

### 6.2 结构化输出的流式困境

#### ⚠️ 问题：不该暴露的字段被用户看到了

在构建智能客服或 Agent 时，我们通常会让模型输出**三层结构**：

```
┌──────────────────────────────────────┐
│  prethinking  （内部推理过程）         │  ← 开发者关心，用户不应看到
├──────────────────────────────────────┤
│  intention    （意图分类结果）         │  ← 开发者用于路由，用户不应看到
├──────────────────────────────────────┤
│  final_reply  （给用户的直接回复）     │  ← 用户应该看到的唯一内容
└──────────────────────────────────────┘
```

**关键矛盾**：基础流式 `get_generator()` 把这个三层结构原封不动地 token-by-token 推出来。用户会在屏幕上看到模型的思考过程——这些内容对用户来说不仅无用，还会造成困惑。

#### 💻 问题演示

```python
# 文件名: structured_streaming_problem.py
# 功能: 演示结构化输出中基础流式暴露不该暴露的字段

from agently import Agently

agent = Agently.create_agent()
agent.input("我买的鞋子想退款，应该怎么处理？")
agent.instruct([
    "判断用户意图，并给出客服回复",
    "你需要先输出 prethinking（推理过程），再输出 intention（意图），最后输出 final_reply",
])
agent.output({
    "prethinking": ("str", "你的推理过程——用户不应看到这部分"),
    "intention": ("'咨询' | '退款' | '投诉' | '闲聊'", "用户意图分类"),
    "final_reply": ("str", "给用户的直接回复，友善且简洁"),
})

# 用基础流式输出——用户会看到 prethinking 和 intention
for delta in agent.start().get_channel_waiter().get_generator():
    print(delta, end="", flush=True)
# 问题：用户看到了 "prethinking: 用户提出了退款相关问题..." 这些内部字段
```

> 🐞 **常见坑**：很多同学第一次做结构化输出的流式消费时，直接用 `get_generator()`，然后发现用户端展示的内容里混入了 prethinking 和 intention，不得不手动在前端做字符串过滤——这既不可靠（字段分隔符可能出现在正文中），也不优雅。

---

### 6.3 instant 模式：字段级流式输出

#### 🧠 直观理解

如果说基础流式 `get_generator()` 是「给你一条完整的直播流，所有频道混在一起」，那 instant 模式就是「给你一份节目单，每个频道单独推送」。

instant 模式的核心能力是：**模型边生成结构化字段，你边按字段名称（path）接收事件**。你可以对不同字段做不同处理——prethinking 阶段给用户展示「正在思考…」，intention 字段完成时立即触发路由逻辑，final_reply 字段流式输出给用户。

#### 📖 StreamingData 结构详解

`get_async_generator(type="instant")` 产出的每一个事件都是一个 `StreamingData` 对象，包含以下五个核心字段：

| 字段 | 类型 | 含义 | 使用场景 |
|---|---|---|---|
| `path` | `str` | 当前事件对应的结构化输出字段名 | 判断「这个事件属于哪个字段」——例如 `"prethinking"`、`"intention"`、`"final_reply"` |
| `value` | `Any` | 该字段当前已生成的值 | 在 `is_complete=True` 时是完整的最终值；在 `is_complete=False` 时是部分值（如半个句子） |
| `delta` | `str` | 本次增量——新产出的 token 文本片段 | 用于流式逐字展示，每次只输出新增的那一小段 |
| `is_complete` | `bool` | 该字段是否已生成完毕 | **这是区分「过程值」和「完整值」的关键标志**。`True` 表示字段已完整，可以安全使用；`False` 表示仍在生成中 |
| `full_data` | `dict` | 所有字段的当前累积数据快照 | 快速获取当前所有字段的最新状态，不必手动拼装 |
| `event_type` | `str` | 事件类型标记 | 最常见的是 `"done"`，表示该字段生成完毕 |

> 💡 **核心洞见**：`is_complete` 是 instant 模式中最重要但最容易用错的概念。它的含义不是「整个模型输出是否完成」，而是「**这个 path 对应的字段是否已完成**」。你要在代码里区分两种场景：
> - **需要完整值才能做决策**（如 intention 分类）→ 用 `is_complete == True` 的时机
> - **需要展示过程给用户看**（如 final_reply 正文）→ 用 `is_complete == False` 期间的 `delta`

#### 💻 1.2-1 instant 调用模板

以下是第 13 课中定义的 instant 标准调用模板（有 DEEPSEEK_API_KEY 时可直接运行）：

```python
# 文件名: instant_template.py
# 功能: ModelRequest instant 标准调用模板——字段级流式消费
# 来源: 第13课 1.2-1

import os
from typing import Any
from agently import Agently

Agently.set_settings("OpenAICompatible", {
    "base_url": os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    "model": os.environ.get("DEEPSEEK_DEFAULT_MODEL", "deepseek-chat"),
    "auth": os.environ.get("DEEPSEEK_API_KEY", ""),
})

if not os.environ.get("DEEPSEEK_API_KEY"):
    print("跳过真实模型请求：未设置 DEEPSEEK_API_KEY")
else:
    # Step 1: 定义结构化输出并获取 response 对象
    response = (
        Agently.create_agent()
        .input("我买的鞋子想退款，应该怎么处理？")
        .instruct([
            "判断用户意图，并给出客服回复",
            "输出 intent、need_human、reply 三个字段",
            "reply 要简短、明确、可直接展示给用户",
        ])
        .output({
            "intent": ("'咨询' | '退款' | '投诉' | '闲聊'", "用户意图"),
            "need_human": ("bool", "是否需要人工客服介入"),
            "reply": ("str", "给用户的直接回复"),
        })
        .get_response()  # ★ 注意：这里用 get_response()，不是 start()
    )

    # Step 2: 用 instant 模式按字段消费
    data: dict[str, Any] = {}
    async for streaming_data in response.get_async_generator(type="instant"):
        if streaming_data.event_type == "done":
            data[streaming_data.path] = streaming_data.value
            print(f"field {streaming_data.path} = {streaming_data.value!r}")

    # Step 3: async_get_data() 兜底——补全 instant 可能遗漏的字段
    final = await response.async_get_data()
    for key, value in final.items():
        data.setdefault(key, value)

    print("data =", data)
```

| 行号 | 代码关键点 | 解释 |
|---|---|---|
| 26 | `.get_response()` | **关键**：获取同一次模型请求的 response 对象。不能替代为 `start()`，必须是 `get_response()` 才能拿到后续 instant 消费的入口 |
| 38 | `response.get_async_generator(type="instant")` | 启动 instant 模式，返回 `StreamingData` 事件的异步迭代器 |
| 39 | `streaming_data.event_type == "done"` | 只处理「字段完成」事件。每完成一个字段，该字段的最终值就在 `streaming_data.value` 中 |
| 40 | `streaming_data.path` | 字段名——与 `.output()` 中定义的 key 一一对应 |
| 43 | `await response.async_get_data()` | 兜底方案——instant 消费完毕后再调用，确保没有遗漏任何字段 |

> ⚠️ **注意事项**：`async_get_data()` 作为兜底调用是**必须的**，不能省略。因为在某些边缘情况下（如模型输出异常），instant 事件流可能没有覆盖所有字段。`async_get_data()` 保证你最终拿到的 `data` 字典包含全部定义的结构化字段。

#### 🔄 执行流程

```
用户输入 "鞋子退款"
    │
    ▼
┌─────────────────────┐
│  get_response()     │  同一次模型请求，不重复调用
│  发起模型请求        │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐      ┌─────────────────────┐
│ instant generator   │─────▶│ intent 字段完成       │
│ 按字段推送事件       │      │ event_type="done"    │
│                     │─────▶│ need_human 字段完成   │
│                     │─────▶│ reply 字段完成        │
└────────┬────────────┘      └─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ async_get_data()    │  兜底：确保所有字段都有值
│ 一次性拿完整结果      │
└─────────────────────┘
```

---

### 6.4 代码实操：意图识别场景下的 instant 完整应用

#### 🎯 实操目标

构建一个智能客服的意图识别 + 流式回复流程，用 instant 模式实现：
1. **prethinking 阶段**：不暴露给用户，展示「正在思考…」
2. **intention 字段完成时**：立即识别意图并做路由决策
3. **final_reply 字段**：逐字流式输出给用户

#### 🏗️ 前置准备

```python
# 前置：环境变量配置
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from agently import Agently

# 模型设置
Agently.set_settings("OpenAICompatible", {
    "base_url": os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    "model": os.environ.get("DEEPSEEK_DEFAULT_MODEL", "deepseek-chat"),
    "auth": os.environ.get("DEEPSEEK_API_KEY", ""),
})
```

#### 💻 Step 1: 定义结构化输出结构

我们用 `instruct()` 和 `output()` 定义三层结构：prethinking（推理过程）、intention（意图分类）、final_reply（用户可见回复）。

```python
# Step 1: 定义结构化输出——三层字段
agent = Agently.create_agent()
response = (
    agent
    .input("我买的鞋子想退款，请问怎么处理？")
    .instruct([
        "你是一个智能客服助手。收到用户问题后，请按以下顺序输出：",
        "1. prethinking：你的推理过程（用户不应看到）",
        "2. intention：判断用户意图，从 '闲聊' | '售前咨询' | '售后咨询' 中选择",
        "3. final_reply：给用户的直接回复。如果是闲聊则友好回应；",
        "   如果是售前/售后咨询，先用共情语句安抚用户并告知正在处理",
    ])
    .output({
        "prethinking": ("str", "推理过程——内部使用，不对用户展示"),
        "intention": ("'闲聊' | '售前咨询' | '售后咨询'", "用户意图分类"),
        "final_reply": ("str", "给用户的直接回复"),
    })
    .get_response()
)
```

#### 💻 Step 2: 用 instant 模式消费字段事件

消费 instant 事件的核心循环——遍历 `StreamingData` 事件，根据 `path` 和 `is_complete` 做不同处理。

```python
# Step 2: instant 模式消费——核心循环框架
async for streaming_data in response.get_async_generator(type="instant"):
    path = streaming_data.path
    is_complete = streaming_data.is_complete

    if path == "prethinking":
        # prethinking 字段：不展示内容，只给状态反馈
        pass

    elif path == "intention":
        # intention 字段：完整值到达时做路由决策
        pass

    elif path == "final_reply":
        # final_reply 字段：流式输出给用户
        pass
```

#### 💻 Step 3: 中间状态提示——prethinking 阶段

在 prethinking 阶段，我们用 `is_complete` 判断：当字段刚开始生成时（`is_complete == False`），向用户展示「正在思考中」的状态提示。这是一种**中间状态的感知反馈**——用户知道系统正在处理，不会误以为卡死了。

```python
# Step 3: prethinking 阶段的中间状态提示
show_thinking_tip = False  # 状态标记：是否已向用户展示过思考提示

async for streaming_data in response.get_async_generator(type="instant"):
    path = streaming_data.path
    is_complete = streaming_data.is_complete

    # prethinking 阶段：给用户「正在思考」的反馈
    if path == "prethinking":
        if not show_thinking_tip:
            print("\n🤔 正在思考如何回答...", end="", flush=True)
            show_thinking_tip = True
        # 当 prethinking 完成时，进入下一阶段
        if is_complete:
            print(" ✓")  # 思考完成标记
            continue
```

> 💡 **核心洞见**：这里用的 `show_thinking_tip` 是一个巧妙的防止重复打印的技巧。因为 instant 事件是**持续推送的**——即使我们只关心「prethinking 开始了」这个事件，在字段生成过程中也会持续收到 `is_complete=False` 的事件。如果不加这个标记，每一轮循环都会重复打印「正在思考…」，让用户看到一大堆重复提示。

#### 💻 Step 4: 字段完成后触发动作——intention 判断

**这是 instant 模式最核心的价值体现**：在 `intention` 字段完成的那一刻（`is_complete == True`），你**不需要等到整个模型输出结束**，就可以立即拿到意图分类结果，并触发后续的路由或处理逻辑。

```python
# Step 4: intention 字段完成时——立即做路由决策
intention = None

async for streaming_data in response.get_async_generator(type="instant"):
    path = streaming_data.path
    is_complete = streaming_data.is_complete

    # prethinking 状态提示（见 Step 3）
    if path == "prethinking":
        if not show_thinking_tip:
            print("\n🤔 正在思考如何回答...", end="", flush=True)
            show_thinking_tip = True
        if is_complete:
            print(" ✓")
            continue

    # intention 字段完成时——立即执行路由
    elif path == "intention" and is_complete:
        intention = streaming_data.value
        print(f"\n📌 已识别用户意图为：{intention}")

        # 根据意图做不同处理——在 TriggerFlow 中可以用 emit_nowait 分发
        if intention == "闲聊":
            print("   → 启动闲聊处理模块...")
            # await data.async_emit_nowait("chat", {...})  ← 在 TriggerFlow 中的用法
        elif intention in ("售前咨询", "售后咨询"):
            print(f"   → 启动{intention}处理模块...")
            # await data.async_emit_nowait("support", {...})
        continue
```

> 🔗 **关联知识**：在这个节点上结合 TriggerFlow 的 `async_emit_nowait()`，可以在 intention 识别完成的一瞬间就将事件分发到对应的处理 chunk——详见 [第 X 章：TriggerFlow 循环控制与流式输出]（← 合并时替换为锚点链接）。

#### 💻 Step 5: 流式输出 final_reply 给用户

对于 `final_reply` 字段，我们需要的是「过程值」——`is_complete == False` 时的 `delta` 增量。每一小段 delta 都直接展示给用户，实现逐字打字效果。

```python
# Step 5: final_reply 字段——流式打字效果输出
async for streaming_data in response.get_async_generator(type="instant"):
    path = streaming_data.path
    is_complete = streaming_data.is_complete

    # prethinking（见 Step 3）
    if path == "prethinking":
        if not show_thinking_tip:
            print("\n🤔 正在思考如何回答...", end="", flush=True)
            show_thinking_tip = True
        if is_complete:
            print(" ✓")
            continue

    # intention（见 Step 4）
    elif path == "intention" and is_complete:
        intention = streaming_data.value
        print(f"\n📌 已识别用户意图为：{intention}")
        if intention == "闲聊":
            print("   → 启动闲聊处理模块...")
        elif intention in ("售前咨询", "售后咨询"):
            print(f"   → 启动{intention}处理模块...")
        continue

    # ★ final_reply 流式输出——逐字展示给用户
    elif path == "final_reply":
        if not is_complete:
            # 过程中：只输出增量 delta
            print(streaming_data.delta, end="", flush=True)
        else:
            # 完成时：收尾处理
            print()  # 换行
            final_reply = streaming_data.value
            print(f"\n✅ 回复已完成，共 {len(final_reply)} 字")
        continue
```

#### ✅ 完整代码

将 Step 1 到 Step 5 整合为一份可运行的完整代码：

```python
# 文件名: intent_recognition_instant.py
# 功能: 意图识别场景下的 instant 模式完整实战——三层结构化字段的字段级流式消费

import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from agently import Agently

# 模型配置
Agently.set_settings("OpenAICompatible", {
    "base_url": os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    "model": os.environ.get("DEEPSEEK_DEFAULT_MODEL", "deepseek-chat"),
    "auth": os.environ.get("DEEPSEEK_API_KEY", ""),
})

# Step 1: 定义结构化输出
agent = Agently.create_agent()
response = (
    agent
    .input("我买的鞋子想退款，请问怎么处理？")
    .instruct([
        "你是一个智能客服助手。收到用户问题后，请按以下顺序输出：",
        "1. prethinking：你的推理过程（用户不应看到）",
        "2. intention：判断用户意图，从 '闲聊' | '售前咨询' | '售后咨询' 中选择",
        "3. final_reply：给用户的直接回复。如果是闲聊则友好回应；",
        "   如果是售前/售后咨询，先用共情语句安抚用户并告知正在处理",
    ])
    .output({
        "prethinking": ("str", "推理过程——内部使用，不对用户展示"),
        "intention": ("'闲聊' | '售前咨询' | '售后咨询'", "用户意图分类"),
        "final_reply": ("str", "给用户的直接回复"),
    })
    .get_response()
)

# Step 2-5: instant 模式按字段消费
print("=" * 50)
print("智能客服意图识别系统启动")
print("=" * 50)

show_thinking_tip = False
intention = None
final_reply = None

async for streaming_data in response.get_async_generator(type="instant"):
    path = streaming_data.path
    is_complete = streaming_data.is_complete

    if path == "prethinking":
        if not show_thinking_tip:
            print("\n🤔 正在思考如何回答...", end="", flush=True)
            show_thinking_tip = True
        if is_complete:
            print(" ✓")
            continue

    elif path == "intention" and is_complete:
        intention = streaming_data.value
        print(f"\n📌 已识别用户意图为：{intention}")
        if intention == "闲聊":
            print("   → 启动闲聊处理模块...")
        elif intention in ("售前咨询", "售后咨询"):
            print(f"   → 启动{intention}处理模块...")
        continue

    elif path == "final_reply":
        if not is_complete:
            print(streaming_data.delta, end="", flush=True)
        else:
            print()
            final_reply = streaming_data.value
            print(f"\n✅ 回复已完成，共 {len(final_reply)} 字")
        continue

# 兜底：async_get_data() 确保没有遗漏字段
data = await response.async_get_data()
print(f"\n📋 最终数据汇总：")
print(f"   意图: {data.get('intention', intention)}")
print(f"   回复: {data.get('final_reply', final_reply)[:50]}...")
```

#### ✅ 验证结果

运行上述代码后，预期的输出顺序和效果如下：

```
==================================================
智能客服意图识别系统启动
==================================================

🤔 正在思考如何回答... ✓

📌 已识别用户意图为：售后咨询
   → 启动售后咨询处理模块...
您好！非常抱歉给您带来了不便。我已经了解到您想要办理退款
，正在为您查询相关信息，请稍候片刻，我会尽快为您处理...

✅ 回复已完成，共 68 字

📋 最终数据汇总：
   意图: 售后咨询
   回复: 您好！非常抱歉给您带来了不便。我已经了解到您...
```

> 💡 **核心洞见**：注意输出顺序——先有「正在思考」的状态提示，然后是「意图识别完成」的通知，最后才是逐字输出的 final_reply。这个顺序对应的是模型结构化字段的**生成顺序**（prethinking → intention → final_reply），也体现了 instant 模式的价值：你不必等模型跑完所有字段才能给用户任何反馈。

---

### 6.5 🐛 排错实录：路径写错导致第三个字段没监听到

> 这是课堂现场真实发生的排错过程。老师在演示意图识别时，将 final_reply 的路径写错，导致第三个字段的事件完全没有被捕获。

**❌ 错误写法**

在 instant 事件循环中，老师为了监听 `final_reply` 字段的流式输出，写了如下判断逻辑：

```python
# 错误写法：路径名写错了
async for streaming_data in response.get_async_generator(type="instant"):
    path = streaming_data.path
    is_complete = streaming_data.is_complete

    if path == "prethinking":
        if not show_thinking_tip:
            print("\n🤔 正在思考...", end="", flush=True)
            show_thinking_tip = True
        if is_complete:
            print(" ✓")
        continue

    elif path == "intention" and is_complete:
        intention = streaming_data.value
        print(f"\n📌 意图: {intention}")
        continue

    # ★ 错误：将 final_reply 写成了 reply
    elif path == "reply":  # ← 这里写错了！output 中定义的是 "final_reply"
        if not is_complete:
            print(streaming_data.delta, end="", flush=True)
        continue
```

**🚨 报错信息**

这段代码**不会报错**——这正是问题的隐蔽之处。程序正常运行，但会出现以下现象：

```
🤔 正在思考... ✓
📌 意图: 售后咨询
        ← 这里本应有 final_reply 的流式输出，但什么都没有
```

控制台输出在 intention 之后就直接结束了。模型实际上已经生成了完整的 final_reply 内容，但代码中没有任何一条分支路径与 `"final_reply"` 匹配，导致该字段的所有事件被**静默跳过**。

**🔍 原因分析**

追溯问题的完整推导链：

```
起因: output() 中定义的字段名是 "final_reply"
  │
  ├── 第1步: 模型按 output 定义生成字段，StreamingData.path 的值是 "final_reply"
  │   为什么？因为 instant 的 path 严格对应 output 中定义的 key 名称
  │
  ├── 第2步: 代码中写的判断条件是 path == "reply"（少了 "final_" 前缀）
  │   为什么会出现这个差异？手动修改代码时凭记忆写了简化的路径名，忘记对齐
  │
  ├── 第3步: 所有 path 为 "final_reply" 的事件进入循环后，没有任何 elif 分支匹配
  │   为什么不会报错？因为 if-elif 结构只会在不匹配时静默跳过，Python 不会提示「未处理的事件」
  │
  └── 结论: final_reply 字段的所有 streaming_data 事件被静默丢弃，用户看不到任何回复内容
```

**✅ 正确写法**

将路径名与 `output()` 中定义的字段名严格对齐：

```python
# 正确写法：路径名必须与 output() 定义完全一致
async for streaming_data in response.get_async_generator(type="instant"):
    path = streaming_data.path
    is_complete = streaming_data.is_complete

    if path == "prethinking":
        if not show_thinking_tip:
            print("\n🤔 正在思考...", end="", flush=True)
            show_thinking_tip = True
        if is_complete:
            print(" ✓")
        continue

    elif path == "intention" and is_complete:
        intention = streaming_data.value
        print(f"\n📌 意图: {intention}")
        continue

    # ✅ 正确：路径名与 output() 中的 "final_reply" 一致
    elif path == "final_reply":  # ← 修正后的路径
        if not is_complete:
            print(streaming_data.delta, end="", flush=True)
        continue
```

**📝 经验总结**

从这个真实的踩坑经历中提炼三条核心教训：

1. **路径名是 instant 模式的第一道门**——如果路径匹配不上，整个字段的数据都不会被处理。不同于 JavaScript 的对象属性访问（写错了最多 `undefined`），这里的数据根本不会进入任何分支。
2. **静默失败是最危险的 bug**——没有报错、没有异常、没有任何可见的提示。唯一能发现的途径是观察输出结果是否完整。在开发阶段建议给 instant 循环加一个 `else` 兜底分支，打印未匹配的 path 用于调试。
3. **字段名以 `output()` 的定义为准**——不要凭记忆或猜测，要回过头去确认 `output()` 中定义的 key 到底是什么。建议在写 instant 处理逻辑时，先把 `output()` 中的 key 列在旁边做对照。

> 🐞 **预防建议**：在 instant 事件循环的开头加一行调试打印 `print(f"[DEBUG] path={path}, is_complete={is_complete}")`，能帮你快速发现哪些字段的事件正在产生、哪些被遗漏了。

---

### 6.6 结合 TriggerFlow emit：实时分发意图识别结果

instant 模式与 TriggerFlow 的结合，形成了一套完整的「识别 → 分发 → 处理」实时管道。

```
用户输入
    │
    ▼
┌─────────────────────────────────────────────┐
│  ModelRequest instant                       │
│                                             │
│  prethinking ──→ 给用户「正在思考」反馈       │
│       │                                     │
│       ▼                                     │
│  intention（complete）──→ emit_nowait("闲聊") │ ← 字段完成的瞬间就分发
│       │                  emit_nowait("售后") │
│       ▼                                     │
│  final_reply ──→ 逐字流式输出给用户           │
└─────────────────────────────────────────────┘
```

核心代码模式如下——在一个 TriggerFlow chunk 中，intention 字段完成时立即通过 `async_emit_nowait()` 将事件发出，后续处理 chunk 接收到信号后即可并行启动：

```python
@flow.chunk
async def reason(data):
    # ... 模型请求和 instant 消费代码 ...

    async for streaming_data in response.get_async_generator(type="instant"):
        path = streaming_data.path
        is_complete = streaming_data.is_complete

        if path == "intention" and is_complete:
            intention = streaming_data.value
            # ★ 在 intention 完成的一瞬间，emit 信号给对应的处理 chunk
            # emit_nowait 是非阻塞的——信号发出后继续处理 final_reply
            if intention == "闲聊":
                await data.async_emit_nowait("chat_flow", {
                    "intention": intention,
                    "user_input": user_input,
                })
            elif intention in ("售前咨询", "售后咨询"):
                await data.async_emit_nowait("support_flow", {
                    "intention": intention,
                    "user_input": user_input,
                })

        elif path == "final_reply" and not is_complete:
            # 同时继续流式输出回复——两者互不阻塞
            print(streaming_data.delta, end="", flush=True)
```

> 💡 **核心洞见**：`emit_nowait` 的非阻塞特性在这里至关重要——它发出信号后立即返回，不会等待下游处理完成。这意味着在 intention 字段完成、emit 信号发出之后，代码继续处理 final_reply 的流式输出，两者**并行进行**。用户在前台看到回复文字在逐字输出的同时，后台的售后处理模块已经在启动中了。

---

### 6.7 产品视角：中间状态提示的用户体验价值

instant 模式解决的不只是技术问题，它的设计背后有一套产品逻辑。

#### 📋 传统 UI 时代的「等待反馈」模式

在传统 Web 应用和移动端 UI 中，当后端处理需要时间时，设计师会使用以下模式给用户心理反馈：

| 模式 | 示例 | 用户感知 |
|---|---|---|
| 转圈圈（Spinner） | 加载中... 圆圈旋转动画 | 「系统在处理，请等待」 |
| 进度条（Progress Bar） | 已处理 60%... | 「系统在处理，大约还需要多久」 |
| 骨架屏（Skeleton） | 灰色方块占位，逐步替换为真实内容 | 「这里有内容，正在加载中」 |
| 状态文字 |「正在查询物流信息…」| 「系统在处理，具体在做什么」 |

**共同目标**：让用户感知到「系统活着，在为你工作」，避免用户因看不到任何反馈而焦虑、反复点击、甚至关掉页面。

#### 🔀 instant 模式在 AI 对话场景中的对应方案

在 AI 对话这种**非确定性延迟**的场景中，传统方案面临挑战——我们不知道模型要生成多长的文本，进度条和预估时间都不可靠。instant 模式提供了一种更细粒度的解决方案：

```
传统方案（一次性等待）：
  用户发消息 → [空白等待 5-10 秒] → 完整回复一次性显示
  ↑ 用户在这 5-10 秒里不知道发生了什么，体验差

instant 方案（分段反馈）：
  用户发消息 → 「正在思考…」（1-2秒）→ 「已识别意图：退款」（瞬间）
             → 逐字输出回复（3-5 秒）→ 回复完成
  ↑ 每一段都有反馈，用户知道系统在做什么、做到了哪一步
```

> 💡 **核心洞见**：在即时通讯式 AI 对话中，「系统有响应」比「系统响应得快」更重要。人类的等待耐心是有限的——如果 2 秒内没有任何反馈，用户就开始焦虑。instant 模式通过在 0.5-1 秒内给出第一个状态反馈（「正在思考…」），抢在用户焦虑之前建立了「系统活着」的心智模型。

#### 📊 instant 模式的双层价值总结

| 层级 | 价值 | 对应能力 |
|---|---|---|
| **技术层** | 字段截取——从结构化输出中按需提取字段 | `path` 过滤 + `is_complete` 判断 |
| **产品层** | 中间状态感知——用户在每个阶段都有可见反馈 | prethinking 提示 + intention 确认 + reply 流式 |
| **架构层** | 提前分发——字段完成后立即触发后续流程 | 结合 TriggerFlow `emit_nowait` 实现并行处理 |

这就是为什么 instant 模式不仅仅是一个「流式输出的变体」——它改变了 AI 应用与用户之间的**交互节奏**，让交互从「等→全量展示」变成了「分段感知→逐字输出」。

---

### 📋 课程小结

#### 🗺️ 知识图谱

```
                    ┌──────────────────────────┐
                    │   ModelRequest instant   │
                    │   字段级流式输出           │
                    └────────────┬─────────────┘
                                 │
            ┌────────────────────┼────────────────────┐
            ▼                    ▼                    ▼
   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
   │  StreamingData  │  │  is_complete   │  │     path       │
   │  事件结构        │  │  完整 vs 过程   │  │  字段定位       │
   └───────┬────────┘  └───────┬────────┘  └───────┬────────┘
           │                   │                   │
           ▼                   ▼                   ▼
   ┌────────────────────────────────────────────────────────┐
   │                    核心应用场景                          │
   ├──────────────┬──────────────────┬──────────────────────┤
   │ prethinking  │  intention        │  final_reply          │
   │ 中间状态提示  │ 字段完成→emit 分发 │ 逐字流式输出           │
   └──────────────┴──────────────────┴──────────────────────┘
```

#### 💡 一句话总结

> instant 模式在模型生成结构化字段的过程中，让你能够**按字段名称按需截取、按完成状态分阶段响应**——它将一次完整的模型输出拆解为多个可观测、可干预、可提前消费的字段级事件流。

#### 📍 系列定位

> 📍 **系列定位**：本文是「AI 应用开发实战」系列第 6 篇。
> - 上一篇：TriggerFlow 循环控制与流式输出 — 掌握工作流级别的阶段事件推送
> - 下一篇：ModelRequest instant 模式（下）— 复杂结构与 wildcard path — 处理嵌套结构、数组字段和通配符路径匹配

---

> 📅 生成日期: 2026-07-07 | 🎯 级别: 中级 | ⏱️ 录音时长: ~14 分钟 | 📏 文档规模: 450+ 行
> 🤖 由 transcript-to-doc v4.1 生成



## 七、ModelRequest instant 模式（下）：复杂结构与 wildcard path

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 使用 path 点语法精确定位嵌套结构中的任意字段
> - [ ] 根据 is_complete 状态机判断字段是否完成输出，在"完整值"和"过程值"之间做出正确选择
> - [ ] 使用 wildcard path（`*`）对数组类型字段进行模糊检索
> - [ ] 理解 output schema 三元组 `(类型, 说明, ensure)` 的含义和 ensure 的重跑机制
> - [ ] 在 instant 模式下消费复杂结构（嵌套字典 + 数组）的流式输出

> 🔗 **前置知识**：详见 [第 X 章：ModelRequest instant 模式（上）— 基础流式与字段截取]（← 合并时替换为锚点链接）

---

### 7.1 path 点语法：嵌套结构字段定位

#### 🧠 直观理解

想象你有一个多层抽屉的柜子。`path` 就是告诉你"现在打开的是第二层抽屉里的左边那个小格子"。在 instant 模式下，模型的结构化输出是一个嵌套的对象树，`path` 用点语法精确告诉你当前正在输出的是哪个叶子字段。

#### 📖 详细解释

当我们在 `.output()` 中定义复杂嵌套结构时——例如 `reply` 是一个包含 `role` 和 `content` 的字典——模型的输出不再是扁平的一层字段，而是一个有层级关系的数据结构。instant 模式的每个 `StreamingData` 事件携带一个 `path` 属性，用**点语法**指明当前数据属于哪个字段。

**点语法的规则**：

- 顶层字段直接用字段名：`"intent"`、`"reply"`
- 嵌套对象的子字段用 `.` 连接：`"reply.content"`、`"reply.role"`
- 数组元素用索引访问：`"reply[0].content"`
- 数组全部元素用通配符：`"reply[*].content"`（详见 7.3）

**为什么用 path 而不是直接给嵌套对象？**

因为模型是 token-by-token 流式输出的。模型一定是先输出完前面的字段才开始输出后面的字段，日志顺序是严格有序的。instant 解析器跟踪模型的输出 token 流，实时判断"当前正在输出哪个字段、处于该字段的什么位置"，然后通过 `path` 把这个位置信息暴露给外部消费者。这意味着你不需要等整个响应完成，就可以在 `reply.content` 只输出到一半时开始消费它的内容。

> ⚠️ **注意事项**：模型的输出一定是严格有序的——它不会在输出 `intent` 的同时交叉输出 `reply`。一定是 `intent` 先完成，`reply` 再开始。这个有序性保证是 path 追踪能够可靠工作的前提。

#### 🔀 为什么需要 path？—— 扁平输出 vs 嵌套输出

| 场景 | 扁平输出 | 嵌套输出（需要 path） |
|---|---|---|
| 字段结构 | `{"intent": "...", "reply": "..."}` | `{"intent": "...", "reply": {"role": "assistant", "content": "..."}}` |
| 事件携带 | `streaming_data.path = "reply"` | `streaming_data.path = "reply.content"` |
| 区分粒度 | 只能区分到 reply 整个字段 | 可以区分到 reply 内部的 role 和 content |
| 适用场景 | 简单分类 + 一句话回复 | 需要更精细控制回复结构（角色、内容分离） |

#### 💻 代码示例

```python
# 文件名: instant_path_demo.py
# 功能: 演示 path 点语法在嵌套结构中的字段定位

from agently import Agently

# 定义带嵌套结构的 output schema
# reply 是一个包含 role 和 content 的字典
response = (
    Agently.create_agent()
    .input("我想退货，流程是什么？")
    .instruct([
        "判断用户意图，并给出客服回复",
        "回复要包含角色和内容",
    ])
    .output({
        "intent": ("str", "用户意图，如'咨询'、'退款'、'投诉'"),
        "reply": ({
            "role": ("str", "回复角色，通常为'assistant'"),
            "content": ("str", "给用户的直接回复内容"),
        }, "客服回复结构体"),
    })
    .get_response()
)

# 消费 instant 流，观察 path 变化
async for streaming_data in response.get_async_generator(type="instant"):
    print(f"path={streaming_data.path!r:25s}  "
          f"is_complete={streaming_data.is_complete!r:6s}  "
          f"delta={streaming_data.delta!r}")
```

| 行号 | 关键点 | 解释 |
|---|---|---|
| 16-18 | `"reply": ({...}, "...")` | 将 reply 定义为一个嵌套字典，内部分 role 和 content 两个子字段 |
| 25 | `streaming_data.path` | 事件携带的 path 值可能是 `"intent"`、`"reply.role"`、`"reply.content"`，精确定位到叶子字段 |

> 🔗 **延伸阅读**：path 的本质是框架内部的 StreamingData 对象属性。详见本文 [7.6 踩坑实录]（← 合并时替换）中关于类型提示丢失的讨论。

---

### 7.2 is_complete：流式输出的完整状态机

#### 🧠 直观理解

把模型输出一个字段想象成用钢笔写一句话。`is_complete = false` 表示笔还在纸上移动，字还没写完——你看到的是"过程"。`is_complete = true` 表示这句话写完了，你拿到的是"完整的结果"。对于意图识别，你要等整句话写完（`true`）才知道到底是"退款"还是"咨询"；对于流式展示，你要在笔移动的过程中（`false`）就把每个新写的笔画显示给用户看。

#### 📖 状态机详解

模型在流式输出一个字段时，可能会分成 3~5 次事件才能把一个完整的字段值输出完毕。每次事件携带：

| 事件属性 | 含义 | 示例（字段 `intent`，值为 `"售前咨询"`） |
|---|---|---|
| `path` | 当前正在输出的字段路径 | `"intent"` |
| `value`（full_data） | 到当前为止该字段的累计完整值 | 第1次: `"售"` → 第2次: `"售前"` → 第3次: `"售前咨询"` |
| `delta` | 本次事件的新增内容 | 第1次: `"售"` → 第2次: `"前"` → 第3次: `"咨询"` |
| `is_complete` | 该字段是否已经输出完毕 | 第1次: `false` → 第2次: `false` → 第3次: `true` |
| `event_type` | 事件类型 | 一般为 `"delta"`（增量类型），完成时可能为 `"done"` |

**is_complete 的状态转换**：

```
字段开始输出
    │
    ▼
┌─────────────────┐
│ is_complete =   │  ← 模型正在输出该字段
│     false       │     每次 delta 事件触发
└────────┬────────┘     可以用 value 拿累计值，用 delta 拿增量值
         │
         │ 模型完成该字段的输出
         ▼
┌─────────────────┐
│ is_complete =   │  ← 字段值已完整，不会再变化
│     true        │     此时 value 即为最终值
└─────────────────┘     可以安全地基于此字段做决策
```

**两个典型消费场景**：

| 场景 | 关注的值 | is_complete 条件 | 原因 |
|---|---|---|---|
| **意图识别**（需要完整值） | `value`（累计结果） | `is_complete == True` | 不能拿着"售"或"售前"就做判断，必须等"售前咨询"完整输出 |
| **流式展示**（需要过程值） | `delta`（增量）、`value`（累计） | `is_complete == False` | 要实时把每个新增的字展示给用户，等完整了反而失去"边想边说"的效果 |

#### 💻 代码示例

```python
# 文件名: is_complete_usage.py
# 功能: 演示 is_complete 在意图识别和流式展示中的不同用法

intent = None          # 意图识别：等完整值
reply_display = ""     # 流式展示：逐字拼接

async for streaming_data in response.get_async_generator(type="instant"):
    # ── 场景一：意图识别 ── 必须等 complete == True ──
    if streaming_data.path == "intent" and streaming_data.is_complete:
        intent = streaming_data.value
        print(f"[决策] 意图识别完成: {intent}")
        # 此时才可以安全地基于 intent 做路由决策
        if intent == "退款":
            print("  → 转退款处理流程")
        elif intent == "投诉":
            print("  → 转投诉升级流程")

    # ── 场景二：流式展示 ── 消费 complete == False 的过程值 ──
    if streaming_data.path == "reply.content" and not streaming_data.is_complete:
        reply_display += streaming_data.delta
        # 这里可以做实时 UI 更新，例如：
        # print(streaming_data.delta, end="", flush=True)

print(f"\n[最终] 意图={intent}, 回复={reply_display}")
```

> ❓ **常见疑问**：为什么不用 `delta` 拼接 + `is_complete == true` 之后再做意图判断？因为如果你只在 `is_complete == true` 时才消费，就等价于 `await response.async_get_data()` 一次性拿结果——失去了 instant 模式"边输出边处理"的意义。

---

### 7.3 wildcard path（`*`）：数组模糊检索

#### 🧠 直观理解

精确 path 像是"请打开第 3 号柜子"。wildcard path 像是"把所有的柜子都打开，把里面的东西全部倒出来"。当你定义 `reply` 为一个列表（多行回复），而你不确定模型会生成几行时，用 `*` 通配所有元素。

#### 📖 语法规则

instant 模式中，path 支持两种数组访问方式：

| 方式 | 语法 | 含义 | 示例 |
|---|---|---|---|
| **精确索引** | `reply[0].content` | 只取列表第 1 个元素的 content 字段 | `path == "reply[0].content"` |
| **wildcard 通配** | `reply[*].content` | 取列表中所有元素的 content 字段，合并推送 | `path == "reply[*].content"` |

> ⚠️ **注意事项**：wildcard 会合并所有匹配字段的 delta 输出。如果你定义了 5 行 reply，`reply[*].content` 会把 5 行的内容串在一起推送——这意味着你拿到的是一行一行的内容连续输出的效果。如果你需要区分每一行，应当使用精确索引。

**老师课堂现场纠正**：录音中老师先说成了 "wild pass"，随后纠正为 "wildcard pass"——这是一个真实的笔误，也侧面说明了这个语法的特殊性和易混淆性。

#### 💻 代码示例

```python
# 文件名: wildcard_path_demo.py
# 功能: 对比精确 path 和 wildcard path 的数组访问方式

# 定义多行 reply 的 output schema
# reply 是一个列表，每个元素包含 content 字段
response = (
    Agently.create_agent()
    .input("昨天的麻辣鸡翅好像不太新鲜，这是怎么回事？")
    .instruct([
        "用多行回复用户的售后问题",
        "输出必须大于 5 行",
    ])
    .output({
        "intent": ("str", "用户意图"),
        "reply": ([
            {"content": ("str", "一行回复内容", True)},  # ensure=True
        ], "多行客服回复"),
    })
    .get_response()
)

# 方式一：精确索引 —— 只取第一行
async for streaming_data in response.get_async_generator(type="instant"):
    if streaming_data.path == "reply[0].content":
        print(f"[第1行] delta={streaming_data.delta!r}")

# 方式二：wildcard path —— 取所有行
all_lines = ""
async for streaming_data in response.get_async_generator(type="instant"):
    if streaming_data.path == "reply[*].content":
        all_lines += streaming_data.delta
        # 所有行的内容会合并输出
print(f"[所有行合并] {all_lines}")
```

> 💡 **核心洞见**：wildcard path 遵循和普通 path 完全相同的底层机制——都是基于模型的 token-by-token 有序输出来追踪位置。唯一的区别在于匹配范围：精确索引只匹配单个位置，`*` 匹配所有位置。`is_complete` 的判断逻辑在 wildcard 下同样适用：当所有匹配位置的字段都输出完毕后，`is_complete` 才变为 `true`。

---

### 7.4 output schema 元组结构：`(类型, 说明, ensure)`

#### 🧠 直观理解

output schema 中的每个叶子字段用一个三元组来表达：**类型**告诉模型你想要什么形状的数据，**说明**告诉模型这个字段是干什么的，**ensure** 告诉框架"这个字段很重要，如果模型没给我，你就让它重来一次"。就像一个三连问：是什么？为什么？完不完整？

#### 📖 三元组详解

在 `.output()` 定义的叶子字段中，当你需要精确控制时，可以用一个三元组 `(类型, 说明, ensure)` 来描述字段：

```
(类型, 说明, 是否确保)
```

| 位置 | 名称 | 必填 | 说明 | 示例 |
|---|---|---|---|---|
| 第1个值 | **类型** | 是 | 字段的数据类型描述，用于告诉模型期望的输出格式 | `"str"`、`"bool"`、`"'咨询' \| '退款' \| '投诉'"` |
| 第2个值 | **说明** | 是 | 字段的中文描述，帮助模型理解该字段的用途 | `"用户意图"`、`"是否需要人工介入"` |
| 第3个值 | **ensure** | 否（默认 `False`） | 是否要求框架确保该字段必须出现 | `True` / `False` |

**ensure 机制详解**：

`ensure=True` 的含义是：向框架声明"这个字段的内容必须至少有一条"。框架在收到模型的输出后，会检测该字段是否存在且满足条件。如果发现缺失或不满足要求（例如声明了 ensure 但模型没输出该字段），框架会**让整个模型请求重新执行一遍**——相当于告诉模型"你刚才漏了这个，重新来"。

```
模型输出
    │
    ▼
┌──────────────────────┐
│ 框架检查 ensure 字段   │
│ 是否全部满足？         │
└─────────┬────────────┘
          │
    ┌─────┴─────┐
    ▼           ▼
  满足        不满足
    │           │
    ▼           ▼
 正常返回    重新请求模型
             （重跑一遍）
```

> ⚠️ **注意事项**：ensure 是框架层面的检查和重试，不等同于提示词中的"请务必输出"。提示词层面的要求靠模型自觉，ensure 是框架兜底。但 ensure 也不是万能的——反复重跑会增加延迟和 token 消耗。

#### 🔀 "没有规范"——一个被反复强调的关键点

老师在课堂上被学员问到"output 有没有规范"时，反复强调：

> **"题没规范。题一直都没规范。这个前面我随便写的。这个纯粹的只是在告诉模型，我想输出一个什么东西而已。它就是一个 gemma 表达。"**

这意味着：

- output schema **不是**一个标准的、有严格语法定义的模式语言
- 它是一个**结构化的提示**——用 Python 数据结构（字典、元组）向模型描述你期望的输出形状
- 元组 `(类型, 说明, ensure)` 是这个框架内部的约定用法，不是行业标准
- 你怎么写类型描述都可以——`"str"`、`"'A' | 'B'"`、更复杂的描述——只要是模型能理解的自然语言或伪类型标注就行

> 🔗 **关联知识**：这个设计理念在前面课程（第 2 或第 3 课）中有完整的讲解——output schema 本质上是结构化提示词的一种表达形式，而不是强类型约束。

#### 💻 代码示例

```python
# 文件名: output_schema_demo.py
# 功能: 展示 output schema 三元组的各种写法

.output({
    # 写法一：最简单的二元组 (类型, 说明)，ensure 默认 False
    "intent": ("str", "用户意图"),

    # 写法二：枚举类型 —— 用字符串告诉模型可选范围
    "need_human": ("bool", "是否需要人工客服介入"),

    # 写法三：三元组 —— ensure=True，要求框架确保此字段必出
    "priority": ("'高' | '中' | '低'", "问题优先级", True),

    # 写法四：嵌套结构中的三元组
    "reply": ({
        "role": ("str", "回复角色"),
        "content": ("str", "给用户的回复内容", True),
        # content 使用了 ensure=True：确保回复内容必须生成
    }, "客服回复结构体"),
})
```

| 行号 | 写法 | ensure | 效果 |
|---|---|---|---|
| 5 | `("str", "用户意图")` | 默认 `False` | 模型可能不输出 intent，框架不干预 |
| 8 | `("bool", "是否需要人工客服介入")` | 默认 `False` | 同上 |
| 11 | `("'高' \| '中' \| '低'", "问题优先级", True)` | `True` | 框架检测 priority 是否输出且值合法，否则重跑 |
| 16 | `("str", "...", True)` | `True` | 嵌套字段也支持 ensure，框架递归检查 |

---

### 7.5 综合实战：复杂结构的完整流式消费

#### 🎯 目标

将 path 点语法、is_complete 状态机、wildcard path、output schema 三元组组合起来，实现一个完整的 instant 流式消费流程。场景：客服意图分流，既要识别意图做路由决策，又要实时展示回复内容。

#### 💻 Step-by-Step

**Step 1: 定义复杂的 output schema**

```python
# 文件名: complex_instant_demo.py
# 功能: 复杂嵌套结构 + 多行回复的 instant 流式消费完整示例

import asyncio
from agently import Agently

Agently.set_settings("OpenAICompatible", {
    "base_url": "https://api.deepseek.com",
    "model": "deepseek-chat",
    "auth": "your-api-key",
})

response = (
    Agently.create_agent()
    .input("我买的运动鞋穿了一天就开胶了，我要退款！")
    .instruct([
        "判断用户意图，识别是否需要人工介入",
        "先输出意图分析 pre_thinking，再输出结构化结果",
        "回复使用多行格式，至少 5 行，详细说明处理步骤",
    ])
    .output({
        # 分析过程 —— 流式展示用
        "pre_thinking": ("str", "分析推理过程"),
        # 意图 —— 决策用，需要完整值
        "intent": ("str", "用户意图", True),
        # 是否需要人工 —— 决策用
        "need_human": ("bool", "是否需要人工客服介入"),
        # 多行回复 —— 流式展示用
        "reply": ([
            {"content": ("str", "一行回复内容", True)},
        ], "多行客服回复，每行是一个步骤"),
    })
    .get_response()
)
```

**Step 2: 实现分类消费逻辑**

```python
# Step 2: 消费 instant 流 —— 三种不同的消费策略
intent = None
need_human = None
thinking_display = ""
reply_display = ""

async for streaming_data in response.get_async_generator(type="instant"):
    path = streaming_data.path
    is_complete = streaming_data.is_complete

    # 策略一：推理过程 —— 流式展示（要过程值，不要完整值）
    if path == "pre_thinking" and not is_complete:
        thinking_display += streaming_data.delta
        # 实时显示推理过程
        # print(streaming_data.delta, end="", flush=True)

    # 策略二：意图识别 —— 等完整值做决策
    if path == "intent" and is_complete:
        intent = streaming_data.value
        print(f"\n[路由决策] 意图={intent}")
        if "退款" in intent:
            print("  → 触发退款流程")

    # 策略三：多行回复 —— wildcard 取所有行，流式展示
    if path == "reply[*].content" and not is_complete:
        reply_display += streaming_data.delta

    # need_human 也可以用完整值
    if path == "need_human" and is_complete:
        need_human = streaming_data.value
        print(f"[决策] 需要人工: {need_human}")

# 兜底：用 async_get_data() 拿最终结果
final_data = await response.async_get_data()
print(f"\n[最终结果] intent={final_data.get('intent')}")
print(f"[最终结果] reply={final_data.get('reply')}")
```

**Step 3: Python flush 机制 —— 为什么流式输出看起来"卡顿"**

```python
# 如果没有 flush，Python 的行缓冲会导致输出"攒着一起出现"
# 解决方法：print 时指定 flush=True
import sys

async for streaming_data in response.get_async_generator(type="instant"):
    if streaming_data.path == "pre_thinking" and not streaming_data.is_complete:
        # ✅ 正确：强制刷新缓冲区
        print(streaming_data.delta, end="", flush=True)
        sys.stdout.flush()  # 双重保险

# ❌ 错误：没有 flush，Python 会缓冲直到遇到换行符
# print(streaming_data.delta, end="")  # 可能很久才看到输出
```

> 🐞 **常见坑**：Python 的 `print()` 在对 stdout 进行行缓冲时，如果输出内容不含换行符 `\n`，内容会一直留在缓冲区里，直到缓冲区满或遇到换行符才一次性输出。在流式场景下，每个 delta 通常不包含换行符，所以会出现"明明在输出但屏幕上看不到"的现象。解决方法就是加 `flush=True`。

#### ✅ 验证结果

运行上述代码后，你应该看到：
1. `pre_thinking` 的内容逐字出现在屏幕上（流式展示效果）
2. 当 `is_complete=True` 时，意图识别完成，路由决策被触发
3. 多行 reply 的内容通过 wildcard path 流式拼接
4. 最终通过 `async_get_data()` 可以拿到完整的结构化结果

#### 🔄 完整数据流示意图

```
模型 token-by-token 输出
    │
    ▼
┌──────────────────────────────────────────┐
│           instant 解析器                  │
│  追踪字段边界，构造 StreamingData 事件     │
└──────────────────┬───────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    ▼              ▼              ▼
 path="pre_    path="intent"   path="reply[*].
 thinking"     is_complete=    content"
 is_complete=  True            is_complete=
 False                         False
    │              │              │
    ▼              ▼              ▼
 流式展示       路由决策        流式展示
 (delta)       (value)        (delta)
```

---

### 7.6 Q&A 答疑

#### 🙋 问题 1：path 是什么属性？是怎么来的？

> 📖 **背景**：学员在课堂上看到 `streaming_data.path` 这个属性，不理解它的含义和来源。

**💬 老师回答**：

path 是 instant 模式下 `StreamingData` 对象上的一个属性。它本质上是一个**内部对象结构的地址描述**——框架在解析模型的 token 流时，实时跟踪当前处于 schema 定义的哪个嵌套位置，然后用点语法字符串告诉你这个位置。

它的设计灵感类似于 JavaScript 中的对象属性访问：`obj.reply.role`。框架把这个层级关系用 `.` 串联成字符串：`"reply.role"`。如果你访问的是数组，就是 `"reply[0].content"`，表示列表的第一个元素的 content 字段。

path 的核心价值在于：**在一个事件的回调中，你不需要自己去解析数据结构来猜"这是什么字段"——path 直接告诉你**。

> 💡 **延伸**：path 的设计也有利于未来的扩展。因为它是字符串表达能力，理论上可以支持任意深度的嵌套路径，而不需要为每种嵌套结构定义新的回调参数。

---

#### 🙋 问题 2：is_complete 到底是什么？我什么时候该用它？

> 📖 **背景**：学员看到 `is_complete` 在代码中既用于 `True` 判断也用于 `False` 判断，不清楚区别。

**💬 老师回答**：

`is_complete` 指的是**一个字段有没有完成输出**。模型是流式输出的，一个字段的值可能会分成 3~5 次事件才能全部推送完。在还没有完成的时候，`is_complete=False`；当这个字段的值已经完整了、不会再变化了，`is_complete=True`。

**什么时候用 `True`？**——需要完整值做决策的时候。

比如意图识别，你不能拿着"售"或"售前"就去判断意图。你需要等到"售前咨询"这四个字完整出来，才能确认意图类型。所以意图字段的消费条件必须是 `is_complete == True`。

**什么时候用 `False`？**——需要实现"边想边说"效果的时候。

比如回复内容的显示，你想要用户看到模型正在一字一字地组织语言，而不是等全部写完再一次性蹦出来。这时候你要的是 `is_complete == False` 时的 `delta`（增量值），每个新字出来就立即显示。

> 💡 **延伸**：同一个字段既可以在 `is_complete == False` 时做流式展示，也可以在 `is_complete == True` 时做最终确认——两者不冲突。你可以把 `delta` 推给 UI，同时在 `is_complete == True` 时记录日志或触发后续流程。

---

#### 🙋 问题 3：output schema 到底有没有规范？类型怎么写才算对？

> 📖 **背景**：学员看到 `.output()` 中的 `("str", "...")`、`("'A' | 'B'", "...")` 等写法，困惑是否有统一的类型规范。

**💬 老师回答**：

**没有规范。题没规范。** 这个在前面第 2 课或第 3 课的时候就专门讲过。output schema 不是一个有严格语法的模式定义语言，它纯粹是一个**结构化提示（gemma 表达）**——你只是在用 Python 的数据结构（字典、元组）向模型描述"我希望你输出一个长什么样的东西"。

类型那一栏你怎么写都可以——`"str"`、`"bool"`、`"'咨询' | '退款' | '投诉'"`——只要模型能看懂你的意思就行。这不是一个 type system，没有类型检查器会去验证你的类型描述是否合法。它就是一个提示，告诉模型"你在这个位置应该输出什么类型的东西"。

唯一有约束力的是第三个参数 `ensure`——但那是框架层面的检查机制，和类型描述的语法无关。框架只会检查字段是否存在、是否满足条件（比如列表是否为空），不会去验证输出值是否符合你写的类型描述。

> 💡 **延伸**：如果你想看底层到底发生了什么——模型收到的 prompt 是什么样的，可以用 `.get_response()` 之前的 agent 对象查看构造出来的提示词。老师课堂上也展示了查 prompt 的方法（通过 `tur` 或 `turn` 对象），但由于当天版本发布仓促，有些类型提示丢失了，导致查出来的结果不完整。

---

#### 🙋 问题 4：模型的输出顺序是确定的吗？path 追踪会不会乱？

> 📖 **背景**：学员担心流式输出中多个字段会不会乱序交叉，导致 path 追踪不准确。

**💬 老师回答**：

**模型的输出一定是严格有序的。** 模型是一个 token 一个 token 输出的，解析也是 token by token 的。模型绝对不会在输出 `intent` 的同时又交叉输出 `reply`。它一定是先把前面的字段（如 `intent`）完整输出完，再开始输出后面的字段（如 `reply`）。

正因为这个有序性保证，instant 解析器才能可靠地通过 path 追踪当前位置——只要 is_complete 还是 false，就说明这个字段还在输出中，所有新增的 token 都追加到这个字段的值上。顺序不会乱，所以 path 也不会跳。

---

#### 🙋 问题 5：wildcard path 和普通 path 一样吗？有什么限制？

> 📖 **背景**：学员看到 `reply[*].content` 这个写法，想知道它和 `reply[0].content` 的区别。

**💬 老师回答**：

wildcard path 和普通 path 在底层机制上**完全一样**——都是基于 token-by-token 有序输出来追踪位置。区别只在于匹配范围：

- 精确 path（如 `reply[0].content`）：只匹配一个位置，只消费那一个位置的字段输出。
- wildcard path（如 `reply[*].content`）：匹配数组中所有位置的同名字段，把它们的输出合并推送。

wildcard path 的一个限制是：如果你需要区分每一行的内容（比如要知道"第 1 行说了什么、第 2 行说了什么"），wildcard 就不适用了——它会把所有行的内容串在一起。这种情况需要用精确索引分别监听。

---

### 7.7 踩坑实录：版本更新导致类型提示丢失

#### 🐛 排错实录：类型提示丢失导致 path 信息不完整

**❌ 问题现象**

老师上课时想要查看 instant 模式下 `StreamingData` 的类型提示（通过 IDE 的自动补全或代码跳转查看 path、is_complete 等属性的定义），结果发现这些类型信息"丢了"——IDE 无法正常提示相关属性。

```python
# 期望：IDE 能提示 streaming_data.path、streaming_data.is_complete 等属性
async for streaming_data in response.get_async_generator(type="instant"):
    streaming_data.  # ← IDE 无法补全，类型提示丢失
```

**🚨 真实情况**

```
"不知道为什么这个 stream 今天拿到的这个结果它不对啊。感觉好像是某些东西丢了。"

"我知道为什么，因为我们追加这个 agent term 的时候，把一些类型的这个提示给丢了。"
```

**🔍 原因分析**

当天课程使用的框架版本是仓促发布的——在添加 `agent term` 功能的过程中，改动影响到了类型标注（type hints）文件，导致部分类型定义在发布时丢失。这属于**版本迭代中的回归问题**：新增功能时没有对现有类型标注做充分的回归测试。

**📝 经验总结**

1. **类型提示是"锦上添花"而非"必需品"**：即使 IDE 无法自动补全，代码仍然可以正常运行（Python 是动态类型语言）。老师课堂上依赖的是自己对 API 的记忆和理解，而不是 IDE 提示。
2. **版本发布节奏的把控很重要**：当天的发布"发得很急"，很多测试来不及做。这在教学场景中是真实存在的——框架在快速迭代，偶尔会遇到不稳定的版本。
3. **遇到问题先自己排查**：老师通过推理（"我们追加 agent term 的时候..."）快速定位了根因，这是一种工程直觉——改动哪里，问题大概率出在哪里。

> ⚠️ **注意事项**：老师课后会检查版本并修复这个问题。如果你在学习时遇到类似的情况（类型提示不完整），可以先对照文档中的属性名手动编写，或等待框架更新。

---

### 🗺️ 本节知识图谱

```
              ┌──────────────────────────────┐
              │     instant 复杂结构消费       │
              └──────────────┬───────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   path 定位    │   │  is_complete  │   │ output schema │
│               │   │   状态机       │   │   三元组       │
├───────────────┤   ├───────────────┤   ├───────────────┤
│ • 点语法       │   │ • true: 完整值 │   │ • (类型, 说明, │
│ • 精确索引     │   │ • false: 过程值│   │    ensure)    │
│ • wildcard *  │   │ • 有序性保证   │   │ • ensure 重跑  │
│ • 嵌套对象     │   │ • delta/      │   │ • 没有规范     │
│ • 数组元素     │   │   full_data   │   │ • gemma 表达   │
└───────────────┘   └───────────────┘   └───────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ 三种消费策略                   │
              ├──────────────────────────────┤
              │ 1. 意图识别 → is_complete=True │
              │ 2. 流式展示 → is_complete=False│
              │ 3. 数组通配 → wildcard path    │
              └──────────────────────────────┘
```

### 💡 一句话总结

> instant 模式下的复杂结构消费，本质上是三件事的组合：用 **path** 知道"现在在输出什么"，用 **is_complete** 判断"输出完了没"，用 **wildcard** 处理"不确定有几个"的数组——三者组合起来，你就能在模型还在"思考"的时候就精准拿到每个字段的变化。

### 📍 系列定位

> 📍 **系列定位**：本文是「AI 应用开发实战系列」第 13 课第二部分。
> - 前接：ModelRequest instant 模式（上）— 基础流式与字段截取
> - 后接：旅游 Agent 实战 — 工具注册与能力接入




## 八、旅游 Agent 实战：工具注册与能力接入

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 画出旅游 Agent 的四层架构图并解释每层职责
> - [ ] 清点手里已有的框架模块，知道每个模块的"一句话职责"
> - [ ] 理解封装的价值：为什么用框架模块比自己从头写要好
> - [ ] 独立完成三类能力的注册：Search + Browse、高德地图 MCP、Bash Sandbox
> - [ ] 理解 Action 行为控制中心的概念和职责
> - [ ] 解释"自己搭 Loop"相比 `set_action_loop` 的优势

---

### 8.1 整体架构：一个有行动力的 Agent 长什么样

```
┌──────────────────────────────────────────────────────────────────┐
│                    编排层（Action Loop）                            │
│     Plan（模型决策）────▶ Execute（工具执行）────▶ 回填 ────▶ 循环  │
│     使用 TriggerFlow 显式定义 reason / act 两阶段                  │
└───────────────────────────────┬──────────────────────────────────┘
                                │ 调用
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                    能力层（三类真实行动）                            │
│  ┌────────────────┐  ┌──────────────────┐  ┌────────────────┐   │
│  │  Search+Browse │  │  高德地图 MCP      │  │  Bash Sandbox  │   │
│  └───────┬────────┘  └────────┬─────────┘  └───────┬────────┘   │
│          └────────────────────┼─────────────────────┘             │
│              统一注册到 agent.action 行为控制中心                   │
└───────────────────────────────┬──────────────────────────────────┘
                                │ 依赖
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│              执行环境层（ExecutionEnvironment）                     │
│  · bash 沙盒的受控空间 / MCP 连接生命周期管理                       │
└───────────────────────────────┬──────────────────────────────────┘
                                │ 驱动
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                    模型层（ModelRequest）                          │
│  · 统一的模型请求接口 + 结构化输出                                 │
└──────────────────────────────────────────────────────────────────┘
```

---

### 8.2 回顾：我们手里有哪些模块

| 模块 | 来源 | 一句话职责 | 这节课用什么 |
|---|---|---|---|
| ModelRequest | 第3课 | 调模型，结构化输出 | `.get_response()` / `async_get_data()` |
| TriggerFlow | 第4课 | 编排多步流程 | 直接定义 Loop 骨架（reason/act chunk） |
| 工具调用回路 | 第6课 | 模型选工具 → 执行 → 回填 | Loop 的 Plan → Execute 两阶段 |
| 工具管理 + Planner | 第9课 | 工具注册、激活、调度 | `agent.action.*` 原语 |
| MCP Client | 第10-11课 | 标准化外部服务接入 | `agent.async_use_mcp()` 一行 |
| 执行环境 / 沙盒 | 第12课 | 安全运行代码 / 命令 | `register_bash_sandbox_action` |

---

### 8.3 封装的价值：自己实现 vs 框架模块

| 维度 | 自己实现 | 框架模块 |
|---|---|---|
| 代码量 | 每类能力数百行 | 每类 1-3 行 |
| 维护成本 | 每个 API 变动都要改 | 框架统一维护 |
| 出错概率 | 高（每个细节都可能踩坑） | 低（框架已经过验证） |
| 多后端切换 | 需要重写适配层 | 框架内部统一抽象 |
| 时间投入 | 基建占大部分精力 | 精力留给业务逻辑 |

> 💡 **核心洞见**：这些能力不是用一次就扔的。封装一次，以后每次用到都能直接调。

---

### 8.4 三类能力接入

#### 能力一：搜索与浏览网页（Search + Browse）

```python
from agently.builtins.actions import Browse, Search

# 反向注册：将搜索和浏览能力注册到 agent.action 行为控制中心
Search().register_actions(agent.action)
Browse().register_actions(agent.action)
```

#### 能力二：高德地图 MCP

```python
# 一行接入，地图工具自动进入注册表
await agent.async_use_mcp(
    f"https://mcp.amap.com/mcp?key={os.environ['AMAP_API_KEY']}"
)
```

#### 能力三：Bash Sandbox（受控 Shell）

```python
agent.action.register_bash_sandbox_action(
    expose_to_model=True,                              # 模型知道此能力
    allowed_cmd_prefixes=["bash", "echo", "cat", "ls", "mkdir"],
    allowed_workdir_roots=[workdir],                   # 限定工作目录
    timeout=15,                                        # 命令超时
)
```

| 参数 | 含义 | 为什么这样设置 |
|---|---|---|
| `expose_to_model` | 是否将沙盒的存在告知模型 | 必须为 True，模型才知道能执行命令 |
| `allowed_cmd_prefixes` | 允许执行的命令白名单 | 安全边界：只允许必要的命令 |
| `allowed_workdir_roots` | 允许访问的目录根路径 | 沙盒的"围墙" |
| `timeout` | 单次命令的超时时间（秒） | 防止命令挂死 |

> 💡 **核心洞见**：这个沙盒是"逻辑版沙盒"，不是 Docker 容器。它通过命令白名单 + 工作目录限制 + 超时控制来实现进程隔离。对于写行程文档这类场景，逻辑版沙盒足够安全。

---

### 8.5 Action 行为控制中心

`agent.action` 的核心职责：

1. **注册（Register）**：统一入口，让各种能力挂载到 agent 上
2. **管理（Manage）**：维护注册表（action_registry），记录所有已注册工具
3. **激活（Activate）**：通过 `use_actions()` 选择性地激活工具子集
4. **调度（Dispatch）**：提供 `async_execute_action(name, kwargs)` 统一接口

```
                            agent.action（行为控制中心）
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │  Search  │        │ 高德 MCP  │        │   Bash   │
    │  Browse  │        │  maps_*   │        │ Sandbox  │
    └──────────┘        └──────────┘        └──────────┘
```

### 8.6 为什么自己搭 Loop（而不是调 set_action_loop）

| 维度 | set_action_loop（黑盒） | 自己搭 Loop（显式） |
|---|---|---|
| 代码量 | 1 行 | ~50 行 |
| Plan 阶段可见性 | 不可见 | 完全可见 |
| 可插入人工鉴权 | 否 | 是 |
| 可自定义终止条件 | 有限 | 完全自由 |
| 适合场景 | 快速原型/简单需求 | 生产环境/需要精细控制 |

> 💡 **核心洞见**：自己搭 Loop 不是为了炫技，而是为了**可控性**。在实际的生产环境中，你可能需要在工具执行前做人工鉴权，或者在特定条件下跳过某些工具——这些在黑盒里是做不了的。

### 📋 本节小结

> 💡 **一句话总结**：工具注册是 agent "能动手"的前提——通过框架的三类注册原语，用几行代码把搜索、地图、shell 能力挂载到 `agent.action` 行为控制中心，为下一节的 Loop 搭建铺好路。

> 📅 生成日期: 2026-07-07 | 🎯 级别: 进阶级 | ⏱️ 录音时长: ~6 分钟




## 九、旅游Agent实战：React-Loop搭建与执行

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 用 TriggerFlow 的 `to()` 和 `when()` 搭出 Plan/Execute 两阶段 Loop 骨架
> - [ ] 在 Plan 阶段通过结构化输出让模型做出 type('tool'|'final') 决策
> - [ ] 在 Execute 阶段通过 `async_execute_action()` 归一化执行工具并回填结果
> - [ ] 理解「行为指导模板」设计模式

### 9.1 整体架构：Plan/Execute 两阶段循环

在上一节中，我们已经注册好了三类工具。但问题是：**谁来调用？以什么顺序调用？**

答案是：不写死顺序。让模型自己决定。

```
┌──────────────────────────────────────────────────────────┐
│                    旅游 Agent Loop                       │
│   ┌──────────────┐    Act信号   ┌──────────────┐        │
│   │ Plan (reason)│────────────▶│Execute (act) │        │
│   │ 模型决策       │◀───────────│ 归一化执行     │        │
│   │ type:tool/final│ Reason信号 │ 结果回填       │        │
│   └──────┬───────┘             └──────────────┘        │
│          │ final → set_state("answer") → Loop结束       │
└──────────────────────────────────────────────────────────┘
```

---

### 9.2 Plan 阶段详解：模型决策（Reason Chunk）

Plan 阶段的核心是一个 `@flow.chunk` 修饰的 `reason` 函数。它做五件事：
1. 获取当前状态（step、history）
2. 构建模型请求（用户需求 + 工具列表 + 已执行步骤）
3. 要求结构化输出（type/reasoning/tool_name/tool_args/answer）
4. 分支处理（tool→emit Act / final→写入answer / 超轮次→兜底）
5. 信号分发

```python
@flow.chunk
async def reason(data):
    state = data.input
    step = state.get("step", 0) + 1
    history = state.get("history", [])

    response = (
        Agently.create_agent()
        .input({"用户需求": user_request})
        .info({"可用工具": tools_desc, "已执行步骤": history})
        .instruct([
            "根据用户需求和已执行步骤判断：是否需要调用工具？",
            "搜索到网页结果后，至少调用一次 browse 阅读相关页面",
            "如果需要，输出 type='tool' 并指定工具名和参数",
            "如果已有足够信息，输出 type='final' 并给出最终回答",
        ])
        .output({
            "type": ("'tool' | 'final'", "下一步动作类型"),
            "reasoning": ("str", "推理过程"),
            "tool_name": ("str | null", "type=='tool' 时填工具名"),
            "tool_args": ("dict | null", "type=='tool' 时填参数"),
            "answer": ("str | null", "type=='final' 时填最终回答"),
        })
        .get_response()
    )
    decision = await response.async_get_data(ensure_keys=["type", "reasoning"])

    state["step"] = step
    if decision["type"] == "final":
        await data.async_set_state("answer", decision.get("answer", ""))
        return  # 不再 emit → execution 自动关闭
    if step >= max_rounds:
        await data.async_set_state("answer", "达到最大轮数")
        return
    if decision["type"] == "tool" and decision.get("tool_name"):
        state["action_calls"] = [{
            "name": decision["tool_name"],
            "kwargs": decision.get("tool_args") or {},
        }]
        await data.async_emit_nowait("Act", state)
```

| 字段 | 类型 | 含义 |
|---|---|---|
| `type` | `'tool' \| 'final'` | 本轮决策类型 |
| `reasoning` | `str` | 模型推理过程 |
| `tool_name` | `str \| null` | 要调用的工具名 |
| `tool_args` | `dict \| null` | 工具调用参数 |
| `answer` | `str \| null` | 最终回答文本 |

---

### 9.3 Execute 阶段详解：工具执行（Act Chunk）

Execute 阶段的核心：把 Plan 阶段产出的 `action_calls` 中的每一项，归一化执行，结果追加到 `history`。

```python
@flow.chunk
async def act(data):
    state = data.input
    results = []
    for call in state.pop("action_calls", []):
        name, kwargs = call["name"], call["kwargs"]
        # ★ 归一化执行：所有工具通过同一个入口调用
        result = await agent.action.async_execute_action(name, kwargs)
        results.append({"tool": name, "args": kwargs, "result": result})
    history = state.get("history", [])
    history.extend(results)
    state["history"] = history
    await data.async_emit_nowait("Reason", state)
```

> 💡 **核心洞见**：`async_execute_action()` 把 Search 的 API 调用、MCP 协议握手、bash 进程隔离，全部归一成同一种调用方式。

---

### 9.4 Loop 连线：三行代码让 Plan/Execute 转起来

```python
flow.to(reason)                 # 第一步：进入 Plan
flow.when("Act").to(act)        # Plan 决策为 tool → 进入 Execute
flow.when("Reason").to(reason)  # Execute 完成 → 回到 Plan（下一轮）
```

```
START → reason → type='tool' → emit("Act") → act → emit("Reason") → reason → ...
                                                      type='final' → set_state("answer") → END
```

---

### 9.5 行为指导模板：教模型如何输出

给模型一堆工具，说"你自由发挥"，模型可能会迷路。**你得教模型怎么输出。** 行为指导模板在用户原始需求之上套一层结构化行为指令：

```python
# 用户只讲需求，行为指令由开发者套用
BEHAVIOR_GUIDANCE = """
{user_original_request}

请自主完成信息的收集工作。
搜索后请至少 browse 一个相关网页，再查询地图和写文件。
最后必须用 bash_sandbox 执行 bash -c，把行程写成 markdown 存到 {workdir}/plan.md。
拿到信息后尽快进入写文件环节，不要反复搜索。
最后告诉我生成的报告文件地址在哪里。
"""
user_request = BEHAVIOR_GUIDANCE.format(
    user_original_request="帮我规划北京一日游（自然景点为主）",
    workdir=workdir
)
```

关键三要素：**终点行为**（写 plan.md）、**行为约束**（至少 browse 一次）、**完成确认**（告诉我文件地址）。

> 💡 **核心洞见**：强调终点不是怀疑模型找不到 bash 工具，而是确保模型知道**你期望的输出方式**。

---

### 9.6 串联运行：v3 完整执行与结果观察

一次真实运行（北京一日游）的典型输出：

```
[Plan · Step 1] tool: 用户要求搜索北京自然景点攻略...
[Execute] search → 返回 10 条候选网页链接
[Plan · Step 2] tool: 搜索已完成，browse 阅读正文...
[Execute] browse → 返回网页正文
[Plan · Step 3] tool: 查地图距离...
[Execute] maps_distance → 返回距离和交通时间
[Plan · Step 4] tool: 用 bash_sandbox 写 plan.md...
[Execute] bash_sandbox → {'ok': True, 'returncode': 0}
[Plan · Step 5] final: 信息足够，生成最终回答...
```

### 📋 本节小结

| 收获 | 内容 |
|---|---|
| **Plan/Execute 两阶段** | reason（模型决策）→ act（归一化执行）→ 回填 → 循环 |
| **结构化输出协议** | type/reasoning/tool_name/tool_args/answer 五个字段 |
| **归一化执行** | `async_execute_action()` 统一入口 |
| **行为指导模板** | 终点行为 + 行为约束 + 完成确认 |

> 💡 **一句话总结**：React Loop 的本质是两个阶段的交替——Plan 做决策（想），Execute 做执行（做）。三条连线、五个决策字段、一个归一化执行入口，就构成了一个能自主行动的 Agent。

> 📅 生成日期: 2026-07-07 | 🎯 级别: L 级 | ⏱️ 录音时长: ~6 分钟




## 十、旅游 Agent 实战：流式输出与 instant 叠加

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 用 `async_put_into_stream` 替代 `print` 实现阶段级流式输出
> - [ ] 通过 `get_async_runtime_stream` 在外部消费 runtime stream 事件
> - [ ] 理解 sandbox 命令白名单与模型之间的执行契约
> - [ ] 使用 instant 模式实现字段级流式输出，并与阶段级流式叠加

---

### 10.1 为什么需要流式输出：从 print 的问题说起

v3 版本已经能跑了，但观察 Loop 内部状态的方式是 `print()`。print 有两个致命问题：
1. **只能在本进程看**：前端和外部消费者拿不到
2. **不是结构化数据**：纯文本日志无法被程序化解析

TriggerFlow 内置了运行时观测通道：`async_put_into_stream`——不参与 to() 流转、不触发 when() 路由，只做一件事：把 chunk 内部的阶段事件推送到外部消费者。

| 维度 | v3（print） | v4（流式） |
|---|---|---|
| 数据出口 | 标准输出/日志 | runtime stream（结构化事件） |
| 消费方式 | 人眼看日志 | 程序异步迭代读取 |
| 数据类型 | 纯文本字符串 | 结构化 dict（含 phase/step 等字段） |
| 前端可用性 | 不可用 | 可直接渲染进度条、状态卡片 |
| Loop 骨架 | 不变 | 不变（只在 chunk 里加一行推送） |

---

### 10.2 v4 流式输出：async_put_into_stream 替代 print

**Plan 阶段推送**：
```python
# 在 reason chunk 拿到模型决策后推送
await data.async_put_into_stream({
    "phase": "plan", "step": step,
    "reasoning": decision.get("reasoning", ""),
    "decision": decision["type"],
})
```

**Execute 阶段推送**：
```python
# 每执行一个工具就推送一条事件
await data.async_put_into_stream({
    "phase": "execute",
    "tool": name,
    "result_preview": str(result)[:100],
})
```

**外部消费**：
```python
flow = await run_action_loop_streaming(agent, user_request)
execution = flow.create_execution()
async for event in execution.get_async_runtime_stream(
    initial_value={"history": [], "step": 0}, timeout=120
):
    phase = event.get("phase", "?")
    if phase == "plan":
        print(f"[Plan · Step {event['step']}] {event['decision']}")
    elif phase == "execute":
        print(f"[Execute] {event['tool']} → {event['result_preview'][:60]}")

result = execution.get_state()
```

**v4 真实运行效果**：
```
[Plan · Step 1] tool: 用户要求先搜索西湖周边自然景点攻略...
[Execute] search → {'ok': True, 'data': [...]}
[Plan · Step 2] tool: 搜索已完成，需要 browse 阅读网页正文...
[Execute] browse → {'ok': True, 'content': '...'}
[Plan · Step 3] tool: 已阅读攻略，需要查驾车距离...
[Execute] maps_distance → {'ok': True, 'data': {'results': [{'distance': '8223'}]}}
[Plan · Step 4] tool: 已有攻略和距离，进入写文档...
[Execute] bash_sandbox → {'ok': True, 'returncode': 0}
[Plan · Step 5] final: 四步全部完成...
```

---

### 10.3 sandbox 命令白名单与执行契约

当 `expose_to_model=True` 时，沙盒的约束信息（允许的命令、工作目录、超时时间）会通过工具描述传递给模型。模型知道自己只能用 `bash echo cat ls mkdir`，sandbox 知道要拦截越界操作——**这是模型与执行环境之间的双向执行契约**。

> ❓ **常见疑问**：`ls`、`mkdir` 这些命令的参数需要单独告诉模型吗？
>
> **答**：不需要。这些是最基本的文件操作命令，模型在训练时已有大量数据覆盖。参数含义是通用知识。

---

### 10.4 v5 instant 叠加：字段级 + 阶段级两层流式

v4 做到阶段级流式，但 Plan 阶段里模型生成字段的过程仍是黑盒。instant 打开这个黑盒：

```
v4（阶段级流式）：[Plan] ─⏳等待模型生成完整决策⏳─▶ 推送 Plan 事件

v5（字段级 + 阶段级流式）：
  ↳ field type = tool         ← 模型刚生成 type 字段就推送
  ↳ field tool_name = search  ← 模型刚生成 tool_name 就推送
  ↳ field reasoning = ...     ← 模型刚生成 reasoning 就推送
  [Plan] 完整决策 → 推送 Plan 事件
```

**v5 reason chunk 核心变更**：
```python
# ★ v5：instant 模式逐字段消费
decision: dict[str, Any] = {}
async for streaming_data in response.get_async_generator(type="instant"):
    if streaming_data.event_type == "done":
        path = streaming_data.path
        value = streaming_data.value
        decision[path] = value
        # 桥接到 TriggerFlow stream
        await data.async_put_into_stream({
            "phase": "plan_field", "step": step,
            "path": path, "value_preview": str(value)[:100],
        })

# 兜底补全
final = await response.async_get_data()
for k, v in final.items():
    if k not in decision:
        decision[k] = v

# 所有字段完成后推送 Plan 阶段汇总事件
await data.async_put_into_stream({
    "phase": "plan", "step": step,
    "reasoning": str(decision.get("reasoning", "")),
    "decision": str(decision.get("type", "")),
})
```

**两层流式的含义**：

| 层级 | 推送时机 | 事件类型 | 效果 |
|---|---|---|---|
| **字段级** (instant) | 模型每生成完一个字段 | `plan_field` | 细粒度，逐字段可见 |
| **阶段级** (TriggerFlow) | Plan 汇总 / Execute 完成 | `plan` / `execute` | 粗粒度，阶段边界清晰 |

---

### 10.5 v3 / v4 / v5 三版对比

| 维度 | v3（print） | v4（阶段级流式） | v5（字段级+阶段级） |
|---|---|---|---|
| **观察方式** | `print()` 打日志 | `async_put_into_stream` | `async_put_into_stream` + instant |
| **Plan 阶段可见性** | 决策完成后才看到 | 决策完成后推送 | 逐字段生成时推送 |
| **事件粒度** | 无结构化事件 | 阶段级 | 字段级 + 阶段级 |
| **Loop 骨架** | reason/act | 同 v3（加一行推送） | reason 改用 instant |
| **前端可用性** | 不可用 | 可渲染进度 | 更多细腻度 |

---

### 10.6 效果评价：已经非常接近 OpenAI

老师在课上做了一个关键观察：当运行 v5 时，用户看到的效果是一条一条状态不断滚动迭代——"先搜什么东西 → 我已经获得了什么东西 → 我要去做什么事情"。这个体验**已经非常接近** OpenAI 平台上 agent 完成任务的实时状态展示。

> 💡 **核心洞见**：流式输出不改变 Agent 的执行逻辑，但通过两层推送机制（字段级 instant + 阶段级 TriggerFlow stream），将 Loop 内部的每一个决策和执行步骤透明化，让用户体验达到 OpenAI 产品级别的水准。

### 📋 本节小结

| 收获 | 内容 |
|---|---|
| **v4 阶段级流式** | `async_put_into_stream` 替代 `print`，`get_async_runtime_stream` 逐条消费 |
| **sandbox 执行契约** | `expose_to_model=True` 将约束传递给模型，形成双向约束 |
| **v5 instant 字段级流式** | `get_async_generator(type="instant")` 按字段逐条推送 |
| **两层流式叠加** | 字段级 + 阶段级，全链路可观测 |
| **效果对标 OpenAI** | 状态滚动迭代体验已接近 OpenAI agent 产品水准 |

> 📅 生成日期: 2026-07-07 | 🎯 级别: 高级 | ⏱️ 录音时长: ~6 分钟




## 十一、课程总结与 Skills 展望

### 11.1 本课核心收获：三块积木拼出可行动 Agent

#### 🧠 直观理解
如果说前面的课程是在逐一制造零件，第13课就是把所有零件组装成一台能运转的机器。三块核心积木：**TriggerFlow**（工作流编排）、**instant 模式**（字段级流式）、**React Loop**（决策-执行循环）。

```
                    ┌─────────────────────────────────────┐
                    │        第13课：可行动旅游Agent        │
                    └────────────────┬────────────────────┘
                                     │
            ┌────────────────────────┼────────────────────────┐
            ▼                        ▼                        ▼
    ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
    │  TriggerFlow  │       │ instant 模式   │       │  React Loop   │
    │  工作流编排    │       │ 字段级流式输出  │       │  决策-执行循环 │
    │ to()/when()  │       │ get_response() │       │ Plan/Execute  │
    │ /stream      │       │ /async_get_data│       │ /回填         │
    └───────────────┘       └───────────────┘       └───────────────┘
```

#### 📊 课程收获总结表

| 收获 | 内容 |
|---|---|
| **行动 Loop 内部结构** | Plan（模型决策）→ Execute（工具执行）→ 回填 → 循环 |
| **三层工具接入** | Search+Browse / `async_use_mcp` 接高德 / `register_bash_sandbox_action` |
| **Loop 不调黑盒** | 不调 `set_action_loop`，reason/act 在代码里显式写出来 |
| **阶段级流式** | `async_put_into_stream` + `get_async_runtime_stream` |
| **字段级流式** | `get_async_generator(type="instant")` 逐字段推送 |
| **两层叠加** | 字段级 + 阶段级，全链路可观测 |

---

### 11.2 v4 vs v5 对比

老师回应学员提问时总结：**"v4 已经足够清晰了，但是 v5 可以把细节拆得更碎。"**

| 维度 | v4（流式输出） | v5（instant 流式） |
|---|---|---|
| **核心机制** | `async_put_into_stream` 推送阶段事件 | v4 基础上叠加 instant 逐字段推送 |
| **观察粒度** | 阶段级：Plan 完成 / Execute 完成 | 字段级：type完成/tool_name完成/reasoning完成... |
| **模型输出消费** | `async_get_data()` 一次性等待 | `async for ... get_async_generator(type="instant")` 逐字段 |

---

### 11.3 React Loop 的局限：Plan 阶段缺少外部指导

Agent 跑通了——会搜、会查地图、会写文档。但**模型每次都得从零开始想"规划一次旅行该怎么规划"吗？**

**模型缺的不是工具，也不是行动力，是领域行为指引。**

```
工具 + 编排：能动手 —— 会搜、会查、会写
      ↓                          还差一层
领域指引：  会想 —— 这类需求该关注什么、
                    按什么标准、
                    容易踩的坑在哪
```

> 💡 **核心洞见**：当前架构把"规划"这件事完全外包给了模型。框架给了模型"能做什么"（工具）和"怎么串起来"（编排），但没给"遇到这类需求该怎么想"。我们需要在 Plan 阶段注入结构化的领域行为指引——这就是 **Skills**。

---

### 11.4 Skills 对 Plan/Execute 架构的改变

老师在白板上画了两张对比图。以下是核心区别的 ASCII 还原：

**BEFORE：以 Action 为中心（当前 React Loop）**
```
┌───────────────────────────────────────────────┐
│                  PLAN 阶段                     │
│   ┌──────────┐          ┌──────────┐         │
│   │  用户信息  │          │ 工具信息  │         │
│   │  (绿色)   │          │  (橙色)   │         │
│   └─────┬────┘          └─────┬────┘         │
│         └──────────┬──────────┘               │
│                    ▼                          │
│            ┌──────────────┐                   │
│            │   模型自己做   │                   │
│            │   规划决策     │  ← 开发者没有插手   │
│            └──────────────┘                   │
└───────────────────────────────────────────────┘
```

**AFTER：Skills 引入后的架构**
```
┌───────────────────────────────────────────────┐
│                  PLAN 阶段                     │
│   ┌─────────────────────────────────┐         │
│   │         Skills 指导类信息        │         │
│   │  "当你在做 XX 事时，             │         │
│   │   你需要这样想、这样做"           │  ← ★   │
│   └───────────────┬─────────────────┘         │
│                   ▼                           │
│           ┌──────────────┐                    │
│           │ 模型做规划    │                    │
│           │ + 探索 Skills │                    │
│           └──────────────┘                    │
└──────────────────┬────────────────────────────┘
                   ▼
┌───────────────────────────────────────────────┐
│                EXECUTE 阶段                    │
│   ┌─────────────────────────────────┐         │
│   │       Skills 能力说明            │         │
│   │  "这个能力怎么安装？              │         │
│   │   这个能力怎么调用？"             │  ← ★   │
│   └───────────────┬─────────────────┘         │
│                   ▼                           │
│           ┌──────────────┐                    │
│           │  沙盒执行器   │ ← 承载脚本运行      │
│           └──────┬───────┘                    │
│                  ▼                            │
│           ┌──────────────┐                    │
│           │  Action 中心  │ ← 跳回工具循环      │
│           └──────────────┘                    │
└───────────────────────────────────────────────┘
```

> 💡 **核心区别**：Skills 在 Plan 阶段注入的不是"还有什么工具可用"，而是"遇到这类问题时该怎么思考"。在 Execute 阶段，Skills 不仅告诉你有什么能力，还告诉你这个能力怎么被运行——这需要一个执行器（沙盒）来承载。

---

### 11.5 Skills 是什么

老师打开 Anthropic 官方 Skills 仓库做现场演示，强调：**Skills 不是一个单独的 markdown 文本，更不是 plan.md。**

| 组成部分 | 内容 | 作用 |
|---|---|---|
| **指导文档** | Markdown 说明 | Plan 阶段的领域行为指引 |
| **可执行脚本** | 如 unpack 脚本 | Execute 阶段的具体执行能力 |
| **能力元信息** | 前置条件、调用方式 | 供规划器和执行器解析 |

---

### 11.6 Skills 的三组件架构

```
Skills 执行器（初级）的三大组件:

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   动态规划器     │────▶│   沙盒执行器     │────▶│   拼装集成       │
│   用户信息 +     │     │   安全运行脚本   │     │   规划器+执行器  │
│   Skills 指导   │     │   承载能力调用   │     │   + React Loop  │
│   → 具体行为    │     │                 │     │   = 可工作Agent  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

后续课程路线：第14课（Skills 是什么、怎么写）→ 第15课（规划器+执行器怎么造）→ 第16课（拼装成完整 Skill 执行器）。

---

### 11.7 Q&A 答疑汇总

**🙋 问题 1**：skill 和 plan.md 有什么区别？

> **老师回答**：plan.md 是模型执行后的**产出物**——是 Plan 阶段生成的具体执行计划文本。Skills 是 Plan 阶段的**输入物**——它告诉模型"当你在做某类事情时应该怎么做"。一个是输出，一个是输入，方向完全不同。

> **延伸**：Skills 包含的远不止文本——还有可执行脚本。如果把 Skills 内容简单灌进 system prompt，那只是在 Plan 阶段塞了一段文本。Skills 的核心价值在于 Execute 阶段的能力承载——模型看到了 "unpack 脚本" 但不能运行它，因为缺少沙盒执行器。

**🙋 问题 2**：流式输出校验失败，重试去了应该怎么办？

> **老师回答**：流式输出校验失败时，系统会抛出一个 **retry 事件**。你只需要在消费流的地方监听并消费这个 retry 事件即可。这个机制本质上是 TriggerFlow 事件体系的一部分——不只是 `Act`、`Reason` 这类业务流程信号，还可以有 `retry`、`error` 等异常流程信号。

**🙋 问题 3**：如果做亲子游这种专案，不写 skill，而是把 skill 里面的 markdown 内容全部喂给 system instruction，效果应该也不错吧？

> **老师回答**：不太行。第一，Skills 不只是文本——有可执行脚本，灌 prompt 灌不进去执行能力。第二，几百个 skill 的内容加起来可能是几百万字，全部塞进 prompt 不现实。第三，Skills 的执行有状态和生命周期，需要规划器和执行器管理。第四，亲子游、徒步游、商务差旅，用同一套工具但规划逻辑完全不同——Skills 让你把每种经验封装成独立 skill，按需动态加载。

---

### 📋 课程小结

> 💡 **一句话总结**：三块积木（TriggerFlow + instant + React Loop）拼出了能动手的 Agent；但要让 Agent 从"会动手"升级到"会想"，需要在 Plan 阶段注入结构化的领域行为指引——这就是 Skills 要解决的问题。

> 📍 **系列定位**：第13课最终模块。系列共26节课，13课恰好过半。
> - 下一篇：第14课 — Skills 基本结构与撰写方法

> 📅 生成日期: 2026-07-07 | 🎯 级别: L 级 | ⏱️ 录音时长: ~13 分钟



---

## 📋 课程小结

### 🗺️ 知识图谱

```
                    ┌─────────────────────────────────────────┐
                    │    第13课：具有可扩展行动力的智能Agent     │
                    │    TriggerFlow + instant + React Loop    │
                    └────────────────────┬────────────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
┌───────────────────┐          ┌───────────────────┐          ┌───────────────────┐
│   TriggerFlow     │          │   instant 模式     │          │   React Loop      │
│   工作流编排       │          │   字段级流式输出    │          │   决策-执行循环    │
│                   │          │                   │          │                   │
│ · to() 顺序连线   │          │ · get_response()  │          │ · Plan(模型决策)   │
│ · when() 信号路由 │          │ · get_async_      │          │ · Execute(工具执行)│
│ · state 全局共享  │          │   generator()     │          │ · 回填 → 循环      │
│ · stream 运行时   │          │ · async_get_data()│          │ · 行为指导模板     │
│   观测            │          │ · is_complete     │          │                   │
│                   │          │ · wildcard path   │          │                   │
│ · condition 循环  │          │ · 意图识别场景    │          │ · 归一化执行入口   │
│ · emit_nowait    │          │ · 两层流式叠加    │          │ · max_rounds      │
│   并发            │          │                   │          │   防无限循环       │
└───────────────────┘          └───────────────────┘          └───────────────────┘
         │                                │                                │
         └────────────────────────────────┼────────────────────────────────┘
                                          │
                          ┌───────────────┴───────────────┐
                          ▼                               ▼
              ┌───────────────────┐           ┌───────────────────┐
              │   旅游 Agent 实战  │           │   Skills 展望      │
              │   v1 → v5 渐进组装 │           │   Plan阶段注入     │
              │                   │           │   领域行为指引     │
              │ v1 工具注册       │           │                   │
              │ v2 Loop骨架       │           │ · 动态规划器       │
              │ v3 串联运行       │           │ · 沙盒执行器       │
              │ v4 阶段级流式     │           │ · 拼装集成         │
              │ v5 字段级流式     │           │                   │
              └───────────────────┘           └───────────────────┘
```

### 💡 一句话总结

> 三块积木（TriggerFlow 编排 + instant 字段流式 + React Loop 决策循环）拼出了能搜索、能阅读、能查地图、能写文档的可行动 Agent；v1→v5 的逐层组装证明了"观察方式"的升级（print → stream → instant）不需要改变 Loop 执行逻辑；而要突破"模型每次从零开始思考"的天花板，Skills 在 Plan 阶段注入结构化领域行为指引是下一层进化方向。

### 📍 系列定位

> 📍 **系列定位**：本文是「AI 应用开发实战课程」第 13 课。系列共 26 节课，本文恰好过半。
> - 上一篇：第 12 课 — 受控执行环境与沙盒设计
> - 下一篇：第 14 课 — Skills 基本结构与撰写方法（什么是 Skills、常见 Skills 类型、如何自己写一个 Skill）

---

## 📝 课后练习

### 练习 1: 搭建最小 React Loop

**题目**：用 TriggerFlow 搭建一个最小可运行的 Plan/Execute Loop。不调真实模型，使用固定计划步骤 `["lookup", "read", "final"]`。

**验收标准**：
- [ ] reason chunk 读取 state.step 决定下一步动作
- [ ] act chunk 模拟执行工具并回填结果
- [ ] reason 判断 action=="final" 后不再 emit 信号，execution 自动结束
- [ ] 最终 execution.get_state() 中 answer 不为空，history 包含所有执行记录

### 练习 2: 注册并验证工具

**题目**：使用 Agently 框架独立完成 Search、Browse 和 Bash Sandbox 三类工具的注册，并在 Agent 中验证注册表。

**验收标准**：
- [ ] Search().register_actions(agent.action) 成功注册搜索能力
- [ ] Browse().register_actions(agent.action) 成功注册浏览能力
- [ ] register_bash_sandbox_action 成功注册沙盒，且 allowed_cmd_prefixes 至少包含 3 个命令
- [ ] agent.action.get_tool_list() 能打印出所有已注册工具的名称和描述

### 练习 3: 对比实验 — 有无行为指导模板

**题目**：运行 v3 旅游 Agent 两次，一次带行为指导模板（终点行为、行为约束、完成确认），一次不带。对比两轮 Loop 的执行步骤数差异。

**验收标准**：
- [ ] 不带行为指导时 Agent 可能无限搜索/不写文件
- [ ] 带行为指导时 Agent 步骤更精简、更快到达 final
- [ ] 能总结出行为指导模板的"三要素"（终点 + 约束 + 确认）

---

> 📅 生成日期: 2026-07-07 | 🎯 级别: L 级 | ⏱️ 录音时长: ~85 分钟 | 📏 文档规模: 6,000+ 行
> 🤖 由 transcript-to-doc v4.2 生成
