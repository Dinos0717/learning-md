# 工具调用回路与 ReAct Loop

> 📅 生成日期: 2026-07-05 | 🎯 级别: XL 级 | ⏱️ 录音时长: ~101 分钟 | 📏 文档规模: 2,780+ 行
> 🏷️ 标签: `Function Calling` `ReAct Loop` `TriggerFlow` `Tool Calling` `Agent架构` `Agently` `工程化`

---

## 📑 目录

- [一、课程开场与前章回顾](#一课程开场与前章回顾)
  - [1.1 本章在系列中的位置](#11-本章在系列中的位置)
  - [1.2 前章核心回顾：三项基础能力](#12-前章核心回顾三项基础能力)
  - [1.3 编排系统的深层理解](#13-编排系统的深层理解)
  - [1.4 工程骨架的关键价值](#14-工程骨架的关键价值)
- [二、为什么模型需要工具调用](#二为什么模型需要工具调用)
  - [2.1 预训练模型的"知识截止日期"](#21-预训练模型的知识截止日期)
  - [2.2 模型的演进方向：从"知道"到"能问"](#22-模型的演进方向从知道到能问)
  - [2.3 两种典型的外部交互场景](#23-两种典型的外部交互场景)
  - [2.4 系统角色的扩展](#24-系统角色的扩展)
- [三、工具调用回路四节点](#三工具调用回路四节点)
  - [3.1 从 Codex 的现象出发](#31-从-codex-的现象出发)
  - [3.2 四个节点的完整拆解](#32-四个节点的完整拆解)
  - [3.3 关键边界：声明 vs 执行](#33-关键边界声明-vs-执行)
- [四、Tool Schema 深度解析](#四tool-schema-深度解析)
  - [4.1 OpenAI Function Calling 的历史地位](#41-openai-function-calling-的历史地位)
  - [4.2 Schema 三字段逐层拆解](#42-schema-三字段逐层拆解)
  - [4.3 工具注册的隐性机制](#43-工具注册的隐性机制)
- [五、多工具选择机制与工具池架构](#五多工具选择机制与工具池架构)
  - [5.1 多工具选择：语义匹配的本质](#51-多工具选择语义匹配的本质)
  - [5.2 四种场景推演](#52-四种场景推演)
  - [5.3 模型如何学会工具调用：两种训练路径](#53-模型如何学会工具调用两种训练路径)
- [六、单工具调用实战](#六单工具调用实战)
  - [6.1 环境准备](#61-环境准备)
  - [6.2 定义与注册工具](#62-定义与注册工具)
  - [6.3 触发完整回路](#63-触发完整回路)
  - [6.4 双工具注入验证](#64-双工具注入验证)
- [七、多工具选择实战与工具管理](#七多工具选择实战与工具管理)
  - [7.1 三工具注册与调用](#71-三工具注册与调用)
  - [7.2 模型自主选择验证](#72-模型自主选择验证)
  - [7.3 工具池三层管理架构](#73-工具池三层管理架构)
- [八、原生 Function Calling 手动实现](#八原生-function-calling-手动实现)
  - [8.1 构造 Tool Schema](#81-构造-tool-schema)
  - [8.2 四步手动走完原生 FC](#82-四步手动走完原生-fc)
  - [8.3 框架装饰器的本质](#83-框架装饰器的本质)
- [九、为什么要自己实现 Function Calling](#九为什么要自己实现-function-calling)
  - [9.1 原生 FC 的三大问题](#91-原生-fc-的三大问题)
  - [9.2 权限认证的两种路径](#92-权限认证的两种路径)
  - [9.3 动态工具加载](#93-动态工具加载)
  - [9.4 三条路径的选择决策](#94-三条路径的选择决策)
  - [9.5 TriggerFlow 方案概述](#95-triggerflow-方案概述)
- [十、TriggerFlow 实现工具调用](#十triggerflow-实现工具调用)
  - [10.1 TriggerFlow 核心概念](#101-triggerflow-核心概念)
  - [10.2 decide chunk：节点一的 TriggerFlow 版本](#102-decide-chunk节点一的-triggerflow-版本)
  - [10.3 execute_and_answer chunk](#103-execute_and_answer-chunk)
  - [10.4 信号路由与启动](#104-信号路由与启动)
- [十一、ReAct Loop 原理与 TriggerFlow 实现](#十一react-loop-原理与触发流实现)
  - [11.1 从翻车演示到 ReAct Loop](#111-从翻车演示到-react-loop)
  - [11.2 ReAct Loop 的概念模型](#112-react-loop-的概念模型)
  - [11.3 基础 ReAct Loop 代码实现](#113-基础-react-loop-代码实现)
  - [11.4 TriggerFlow 版 ReAct Loop](#114-triggerflow-版-react-loop)
  - [11.5 基础 ReAct 的缺陷分析](#115-基础-react-的缺陷分析)
- [十二、生产级框架优化对比](#十二生产级框架优化对比)
  - [12.1 三框架对比总览](#121-三框架对比总览)
  - [12.2 Hermes Agent：并行执行 + Grace Call](#122-hermes-agent并行执行--grace-call)
  - [12.3 OpenClaw：Hook 拦截机制](#123-openclawhook-拦截机制)
  - [12.4 Action 类型的扩展谱系](#124-action-类型的扩展谱系)
  - [12.5 异步 vs 多线程的选择](#125-异步-vs-多线程的选择)
- [十三、ReAct Loop v2 改进实现](#十三react-loop-v2-改进实现)
  - [13.1 改进 1：多工具并行执行](#131-改进-1多工具并行执行)
  - [13.2 改进 2：Grace Call](#132-改进-2grace-call)
  - [13.3 改进 3：错误捕获](#133-改进-3错误捕获)
  - [13.4 v1 vs v2 完整对比](#134-v1-vs-v2-完整对比)
- [十四、课程答疑精选](#十四课程答疑精选)
  - [14.1 工具与框架选择](#141-工具与框架选择)
  - [14.2 输入输出格式](#142-输入输出格式)
  - [14.3 工程落地实践](#143-工程落地实践)
  - [14.4 AI 能力与职业发展](#144-ai-能力与职业发展)

---

## 一、课程开场与前章回顾

### 1.1 本章在系列中的位置

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 清晰定位本章在系列课程中的位置
> - [ ] 复述前一章的三个核心能力
> - [ ] 理解编排系统的双重职责
> - [ ] 说明工程骨架的核心设计价值

本节是第二章节的开篇。在第一章中，我们完成了从「模型能说什么」到「工程能做什么」的基建工作。现在进入第二章，核心命题发生转换——从「模型输出文字」到「模型驱动外部动作」。

```
第一章：基础能力建设
├── 模型调起
├── 行为编排
└── 工程骨架
        │
        ▼
第二章：模型与外部世界的交互  ← 本章在此
├── 第06课：工具调用回路与 ReAct Loop  ← 当前课程
├── 第07课：（后续）
└── 第08课：工具管理专题
```

### 1.2 前章核心回顾：三项基础能力

上一章帮大家建立了三个最基本的能力，这些是所有模型应用工程的前提：

| 能力 | 做什么 | 为什么重要 |
|---|---|---|
| **模型调起** | 通过 API 调用大模型，管理请求和响应 | 所有 AI 应用的入口 |
| **行为编排** | 在多次模型请求之间构建起连接关系和数据传递 | 从「单次问答」到「多步任务」的关键跃迁 |
| **工程骨架** | 搭建标准化的项目文件结构，配置与代码分离 | 可维护、可扩展、可协作的基础 |

### 1.3 编排系统的深层理解

> 💡 **核心洞见**：编排系统不只是连接行为节点，更是为多次请求提供数据传递的基础环境。

很多同学会问：「编排到底在解决什么问题？我为什么不直接写代码？」

一个很简单的测试：如果不使用任何编排框架，让模型直接用 Python `while` 循环硬写 agent loop，会发生什么？

模型会为了帮你在多次请求之间串联信息，做大量额外工作——在外面包装很多东西，甚至为每个分支建专门的数据模型。这对于简单逻辑没问题，但一旦需求稍微复杂、要扩展，就会发现硬编码的方式存在严重的维护性和扩展性问题。

```
编排框架的核心价值：
┌──────────┐     ┌──────────┐     ┌──────────┐
│ 行为节点A │────▶│ 行为节点B │────▶│ 行为节点C │
└────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │
     ▼                ▼                ▼
┌─────────────────────────────────────────────┐
│          数据传递层（编排系统提供）              │
│    A的输出 → B的输入 → B的输出 → C的输入       │
└─────────────────────────────────────────────┘
```

这就是为什么我们要学习工程框架——框架分两层：我们自己有工程架子，开发工具又有它的框架。如果我们不建立自己的工程结构，当项目复杂度上升时，定位问题和修改代码的成本会急剧增加。

### 1.4 工程骨架的关键价值

上节课我们不只是搭了一个 FastAPI 服务，而是设计了一整套文件结构。关键收益不是「文件夹排列整齐」，而是**责任分离**：

| 模块 | 分离后的效果 |
|---|---|
| **模型配置** | 换模型只需改配置，不动代码 |
| **Prompt** | 对任一节点的 prompt 做微调，无需打开核心代码 |
| **Flow 行为块** | 每个行为节点独立维护，彼此解耦 |
| **API 接口** | 对外服务层与内部逻辑分离 |

> ⚠️ **注意事项**：工程骨架的核心意义在于「清楚地知道修改哪部分内容会带来什么影响」，而不仅仅是代码整洁。

有了这个基础之后，我们来思考一个新问题：目前为止，模型的能力边界在哪里？它只能「说话」，还不会「做事」——这就是本章要解决的问题。

---

## 二、为什么模型需要工具调用

### 2.1 预训练模型的"知识截止日期"

> 🧠 **直观理解**：预训练模型就像一本印刷好的百科全书——印刷完成的那一刻，里面的知识就定格了，再也不会自动更新。

2023 年 ChatGPT 刚出来时，大家觉得它很厉害：能理解模糊表达的意图，用自然语言回答问题，这是以前小冰、小黄鸭做不到的。但如果我拿着一个问题直接裸调模型 API——不给任何额外信息——问它"今天英伟达的股价是多少？"，大概率得到的回答是「我不知道」或过时信息。

原因很简单：**模型是预训练的**。模型文件一旦固化，任何人对它发起请求都不会再改变模型本身。

### 2.2 模型的演进方向：从"知道"到"能问"

那我们是不是只能等模型公司不断更新模型，来跟上问题复杂度的变化？观察 Anthropic 和 OpenAI 近年的发展方向会发现：**他们不是在一直给模型追加最新信息，而是越来越倾向于提升模型与外部系统交互的能力**。

```
模型的演进方向：

第一代：模型自身的知识（有截止日期，无法更新）
          │
          ▼
第二代：模型 + 外部工具（实时获取信息，执行动作）
          │
          ▼
第三代：模型 + 多工具编排 + 自主决策回路（本章主题）
```

### 2.3 两种典型的外部交互场景

真实世界中，模型需要外部工具的原因可以归纳为两类：

| 场景 | 例子 | 解决方案 |
|---|---|---|
| **获取实时信息** | 英伟达今天的股价、当前天气 | 模型发出查询指令 → 工具获取数据 → 模型基于数据回答 |
| **获取执行反馈** | 调 API 创建订单、执行数据库操作 | 模型发出操作指令 → 工具执行 → 结果返回给模型做后续判断 |

> ❓ **常见误解**：「模型输出的文字已经很好了，为什么要加工具？」——文字只能回答模型训练数据中已有的知识。对于实时信息、私有数据、需要执行动作的场景，文字无法替代工具。

### 2.4 系统角色的扩展

在之前的课程中，整个系统里只有两个关键角色：

```
原来的系统：
┌──────────┐         ┌──────────┐
│  工程模块  │────────▶│   模型    │
│（编排+指令）│◀────────│（回答问题）│
└──────────┘         └──────────┘
```

从这节课开始，系统角色扩展为：

```
新的系统：
┌──────────┐     ┌──────────┐     ┌──────────┐
│  工程模块  │────▶│   模型    │────▶│  外部模块  │
│（编排+指令）│◀────│（决策+生成）│◀────│（执行工具）│
└──────────┘     └──────────┘     └──────────┘
```

核心变化是：**模型能给出指令，工程把指令翻译成真正的行动，指向其他模块，获取返回结果，再由模型做进一步处理**。本质上就是「翻译处理」——把模型的意图翻译为系统行动。

> 📍 **系列定位**：本文是「AI 应用开发实战」系列第 06 篇。上一篇第 05 课完成了工程骨架搭建，本篇在此基础上引入工具调用能力。

---

## 三、工具调用回路四节点

### 3.1 从 Codex 的现象出发

> 🧠 **直观理解**：打开 Claude Code 或 Codex，让它读取一个文件。你会先看到它调用了 Read 工具，拿到文件内容，然后才开始回答。这个「工具调用→拿到结果→给出回答」的过程，背后是一套精密的四节点通信协议。

不管是 Codex 还是 Claude Code 的 agent 模式，都可以观察到一个共同现象：

当问题超出模型自身知识范围时，agent 会先形成一个基础规划 → 根据可用工具发起行动 → 从行动中拿到结果 → 给出下一步判断。单看中间这一段处理，就是**一个标准的 Function Calling**。

```
在 Codex 中观察到的工具调用过程：

  Tool: Bash
  Input: { "command": "which python3" }
  ────────────────────────
  [命令执行结果]
  
  → 基于结果判断下一步动作
```

```
在 Claude Code 中同样可见：
  
  Tool: Read
  Input: { "file_path": "README.md" }
  ────────────────────────
  [文件内容]
  
  → 基于内容生成回答
```

### 3.2 四个节点的完整拆解

工具调用不是一次请求，而是**四个标准动作的串行链路**：

```
用户输入
   │
   ▼
┌─────────────────────────────────────────────────┐
│  节点一：模型收到 prompt + 工具列表（schema）      │
│  输入：用户问题 + 可用工具的 schema 列表            │
│  输出：需要调用 get_weather，参数 city=北京        │
│  关键：模型在这里完成「问题与工具的匹配选择」        │
└──────────────────────────┬──────────────────────┘
                           │  结构化工具调用指令（JSON）
                           ▼
┌─────────────────────────────────────────────────┐
│  节点二：系统执行工具                             │
│  调用 get_weather(city="北京")                   │
│  返回：{"temp": 22, "condition": "晴"}           │
│  关键：发生在系统侧，模型完全不感知                │
└──────────────────────────┬──────────────────────┘
                           │  执行结果
                           ▼
┌─────────────────────────────────────────────────┐
│  节点三：结果回填到上下文                         │
│  工具结果追加到对话历史，作为后续模型请求的输入     │
│  关键：用户问题 + 工具调用指令 + 工具结果           │
│        共同构成第二轮请求的上下文                  │
└──────────────────────────┬──────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────┐
│  节点四：模型继续生成                             │
│  基于工具结果，输出最终回答                       │
│  关键：此时模型已经"看到"了工具返回的数据          │
└─────────────────────────────────────────────────┘
```

这张图是今天所有内容的基础框架，后续的 Agently tool_func、原生 Function Calling、TriggerFlow 实现、ReAct Loop，都是在这个四节点框架下的不同实现方式。

### 3.3 关键边界：声明 vs 执行

> 💡 **核心洞见**：模型只做「声明」——它说"我要调用这个工具"——但从不「执行」。执行发生在系统侧（你的代码或框架代码），模型对这个过程完全不感知。

这个「声明 vs 执行」的边界意味着什么？

```
节点一（模型侧）        节点二（系统侧）
┌─────────────┐       ┌─────────────┐
│ 模型输出：    │       │ 代码拿到 JSON │
│ {"type":    │──────▶│ 解析工具名和   │
│  "tool_use",│       │ 参数           │
│  "name":    │       │               │
│  "get_       │       │ 执行前可做：    │
│  weather",  │       │ • 权限检查     │
│  "input":   │       │ • 人工审批     │
│  {...}"}    │       │ • 审计日志     │
│             │       │ • 分发到远端    │
└─────────────┘       └─────────────┘
```

因为这个边界的存在，你可以：
- 在执行前做**权限检查**：当前用户有没有权限调用这个工具？
- 插入**人工审批**：涉及敏感操作时让管理员确认
- 记录**审计日志**：谁在什么时候调了什么工具
- **分发到另一台机器**：工具执行不一定发生在同一台服务器上

这也是为什么我们要理解原理——如果你用的是别人封装好的黑箱，这些定制的可能性就全被锁死了。

---

## 四、Tool Schema 深度解析

### 4.1 OpenAI Function Calling 的历史地位

2023 年，OpenAI 发布了 Function Calling，官网上的第一个案例就是查天气。从那之后，**这个模式基本没有变化**。

这不仅仅是一个 API 特性——它在模型与外界交互这件事上定义了**行业事实标准**：

| 平台 | 对 Function Calling 的支持 |
|---|---|
| **OpenAI** | 原生 `tools=` 参数 + `tool_calls` 返回字段 |
| **Anthropic Claude** | `tool_use` content block，结构类似 |
| **DeepSeek** | 兼容 OpenAI 的 `tools=` 参数格式 |
| **开源模型（Llama/Qwen）** | 视推理框架而定，部分支持 |

> 💡 **核心洞见**：不管你用哪个模型，tool schema 的结构（name + description + parameters）和返回结果的格式基本上是一致的。OpenAI 在这个领域起到了「标准协议推动者」的作用。

### 4.2 Schema 三字段逐层拆解

节点一里，模型收到的不仅是 prompt，还有工具列表（schema）。Schema 告诉模型「有哪些工具可用、每个工具能干什么、需要传什么参数」。三个核心字段各司其职：

```json
{
  "name": "get_weather",
  "description": "查询指定城市的当前天气状况，返回温度（摄氏度）、天气描述和湿度",
  "parameters": {
    "type": "object",
    "properties": {
      "city": { "type": "string", "description": "城市名称，如 '北京'、'上海'" }
    },
    "required": ["city"]
  }
}
```

| 字段 | 谁用它 | 用来做什么 | 写法要求 |
|---|---|---|---|
| `name` | **系统代码** | 路由到对应的函数 | 精确匹配函数名，是系统级的标识符 |
| `description` | **模型** | 判断「这个工具适不适合解决当前问题」 | 越具体越好，模糊的描述导致模型判断不准 |
| `parameters` | **模型 + 系统** | 模型据此生成参数值；系统据此做类型校验 | 参数名和描述都要有信息量 |

**`description` 是给模型读的，不是给人看的文档。** 写得模糊，模型就判断不准——选错工具、填错参数。写得具体，模型决策的准确率会显著提高。

> 🔗 **关联知识**：这和 Anthropic 的 Skills 撰写规范强调的是同一件事——Skills 不能写得太泛，要讲清楚最适用什么场景。本质都是在帮模型做更精准的「意图-能力」匹配。

**`parameters` 的信息量也容易被忽视。** 除了工具描述，参数列表本身也隐式地告诉模型这个工具的能力边界。就像有经验的工程师看 API 文档——一看接口命名，二看参数列表，大概就知道这个接口能处理什么范围的问题。

### 4.3 工具注册的隐性机制

刚才用 Codex 举例时，有同学问：「这里有没有提前注册工具？」

答案是**有**。工具注册隐藏在框架的运行环境里。

```
工具的注册入口可能是：

┌──────────────────────────────────────────┐
│  Codex / Claude Code 运行时              │
│                                          │
│  • MCP Server 配置 → 注册了浏览器、文件等工具│
│  • Plugin 系统 → 注册了第三方扩展工具       │
│  • Settings 面板 → 注册了内置工具           │
│  • Skills → 注册了自定义技能               │
└──────────────────────────────────────────┘
```

这解释了为什么你在 Coding Agent 里用工具时感觉是「理所当然」的——实际上工具列表早已注入了请求上下文。这也恰好说明了为什么这类产品的**可控性在企业落地场景中偏弱**——你无法看到中间过程，无法在关键环节插入自己的逻辑。

> ⚠️ **注意事项**：工具注册不是可有可无的，是必然发生的。区别只在于你是否能在工程代码中显性地控制它。

---

## 五、多工具选择机制与工具池架构

### 5.1 多工具选择：语义匹配的本质

> 🧠 **直观理解**：模型选择工具的过程，特别像你在搜索引擎里输入关键词——模型拿出你的问题和每个工具的 description 做「语义级别的匹配」，跟向量检索的原理非常相似。

如果只有一个天气工具，模型没有选择空间。但真实场景中我们往往有多个工具，甚至多个功能相近但精度不同的工具——模型怎么选？

关键影响因素是**问题与工具描述之间的匹配度**。匹配度高 → 选中；匹配度低 → 不选；两个工具的匹配度差不多 → 随机选。

### 5.2 四种场景推演

假设你有两个天气查询工具：

| 工具 | 覆盖范围 | 精度 |
|---|---|---|
| `cn_weather` | 中国 | 街道级 |
| `global_weather` | 全球 | 市级 |

来看四个不同问题下的模型选择行为：

```
场景 A：问"纽约天气怎么样？"
  匹配分析：cn_weather 只覆盖中国 → 不匹配
            global_weather 覆盖全球 → 匹配
  结果：→ global_weather ✅

场景 B：问"北京天气怎么样？"
  匹配分析：两个都能查北京
            cn_weather 精度更高 → 匹配度相近
  结果：→ 随机选择 ⚠️

场景 C：问"北京回龙观某条路的天气？"
  匹配分析：cn_weather 精度到街道 → 匹配
            global_weather 精度到市 → 不够精细
  结果：→ cn_weather ✅

场景 D：问"洛杉矶橡树路明天会下雨吗？"
  匹配分析：cn_weather 不覆盖美国 → 不匹配
            global_weather 覆盖但精度不够 → 部分匹配
  结果：→ 可能告诉用户"我只能查到市级，洛杉矶明天..."
       或直接回复"查不到这么细的信息"
```

> 💡 **核心洞见**：description 和 parameters 的质量是工具调用准确率的主要影响因素之一。描述越精确，模型判断越准。

### 5.3 模型如何学会工具调用：两种训练路径

有同学问：「模型到底怎么学会使用工具的？训练过程是什么样的？」

**路径一：模型原生训练（Function Calling 专用训练）**

在模型后训练（对齐）阶段，用特定的 QA 对告诉模型「面对这类问题，你应该输出这种格式的回答」。训练数据中会插入特殊的 tag，告诉模型 "这是一次 tool_calls 生成任务"。模型在大量 QA 对中学到：看到类似的问题格式 + tag → 输出结构化的工具调用指令。

```
训练数据格式（简化示意）：
Q: <tool_call_tag> 北京今天天气怎么样？
A: {"name": "get_weather", "parameters": {"city": "北京"}}
```

**路径二：结构化 JSON 输出 + 框架强约束（不依赖原生训练）**

模型不一定经过 Function Calling 的专门训练，但当今大部分模型都有**稳定的 JSON 输出能力**。我们可以在 prompt 层面告诉模型「请按这个格式输出」，再利用框架层做类型校验和重试，把成功率做到 99.9% 以上。

| 维度 | 路径一（原生训练） | 路径二（结构化 JSON 输出） |
|---|---|---|
| 依赖条件 | 模型厂商做了 FC 专用训练 | 模型有稳定 JSON 输出能力即可 |
| 跨模型兼容 | 不一定，看具体模型 | 任何能输出 JSON 的模型都能用 |
| 可控性 | 低 — 格式由 API 层控制 | 高 — 完全由你的代码控制 |
| 实现成本 | 低 — 一个参数搞定 | 中 — 需要自己搭回路 |

> 🔗 **推导链**：两种训练路径 → 两种实现方式 → 分别对应 M08 的「原生 FC 手动实现」和 M10 的「TriggerFlow 结构化输出」。理解了训练路径，就理解了为什么两条实现路径都存在且各有价值。

让我们进入代码实操阶段。

## 六、单工具调用实战

### 6.1 环境准备

> 🎯 **目标**：用 Agently 框架跑通单工具的完整四节点回路，观察 show_tool_logs 的输出。

在写代码之前，先做好环境配置：

```python
# 文件名: s01_single_tool.py
# 功能: 单工具完整调用回路演示

import os
import requests
from typing import Annotated
from dotenv import load_dotenv, find_dotenv
from agently import Agently

load_dotenv(find_dotenv())

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        "model": os.environ.get("DEEPSEEK_DEFAULT_MODEL", "deepseek-v4-flash"),
        "auth": os.environ.get("DEEPSEEK_API_KEY", ""),
    },
)
Agently.set_settings("runtime.show_tool_logs", True)
```

| 配置项 | 说明 |
|---|---|
| `base_url` | DeepSeek API 端点（兼容 OpenAI 协议） |
| `model` | 使用的模型版本 |
| `auth` | API 密钥 |
| `runtime.show_tool_logs` | **关键配置**：设为 True 后在控制台打印工具调用日志——这是节点一输出的直接证据 |

### 6.2 定义与注册工具

> 💡 **核心洞见**：工具的最基本形态就是一个函数——可以直接调用，也可以通过 agent 的装饰器注册后被模型调用。

```python
agent = Agently.create_agent()


@agent.tool_func
async def get_weather(
    city: Annotated[str, "城市名称，如 '北京'、'上海'、'Tokyo'"],
) -> dict:
    """查询指定城市的当前天气状况，返回温度（摄氏度）、天气描述和湿度"""
    r = requests.get(f"https://wttr.in/{city}?format=j1", timeout=10)
    cur = r.json()["current_condition"][0]
    return {
        "temp_c": int(cur["temp_C"]),
        "condition": cur["weatherDesc"][0]["value"],
        "humidity": int(cur["humidity"]),
    }
```

**`@agent.tool_func` 装饰器做了什么？**

| 代码元素 | 对应 Schema 字段 | 作用 |
|---|---|---|
| 函数名 `get_weather` | `name` | 系统代码路由到此函数 |
| docstring `"""查询指定城市..."""` | `description` | 模型判断是否调用此工具 |
| `city: Annotated[str, "城市名称..."]` | `parameters.city.description` | 模型据此生成城市参数值 |
| 返回类型 `-> dict` | 工具返回值的类型信息 | 系统校验 |

> 🔗 **关联知识**：回忆 M04 的 Schema 三字段表——装饰器的每个部分恰好对应 Schema 中的一个字段。框架帮你省去了手写 JSON Schema 的步骤。

**工具的有效性验证**：

get_weather 是一个真正的、可以独立调用的函数：

```python
# 人可以直接调用
result = get_weather("太原")
# → {"temp_c": 24, "condition": "晴", "humidity": 10}

# 工程代码也可以直接调用
# → 同样的结果
```

### 6.3 触发完整回路

```python
response = (
    agent
    .input("北京今天天气怎么样？适合出去跑步吗？")
    .use_tool(get_weather)
    .get_response()
)

print(response.get_data())
```

**这 4 行代码背后发生了什么？**

```
agent.input("北京今天天气怎么样？...")
    │  设置用户问题
    ▼
.use_tool(get_weather)
    │  将 get_weather 的 schema 注入请求数据
    │  （等同于告诉模型：你可以用这个工具）
    ▼
.get_response()
    │  触发完整的四节点回路：
    │  节点一 → 节点二 → 节点三 → 节点四
    ▼
response.get_data()
    │  获取模型最终回答（已包含天气数据）
```

### 6.4 双工具注入验证

为了验证模型确实在做「选择」而非「无脑调用」，我们注入一个计算工具：

```python
@agent.tool_func
async def add_calculate(
    a: Annotated[int, "整数A"],
    b: Annotated[int, "整数B"],
) -> int:
    """计算两个整数的加和，返回整数结果"""
    return a + b
```

| 输入问题 | 模型选择 | 说明 |
|---|---|---|
| "北京今天天气怎么样？适合跑步吗？" | `get_weather` | 天气问题和计算工具无关，模型正确选择 |
| "3 + 5 等于多少？" | `add_calculate` | 计算问题触发计算工具 |
| "今天天气怎么样？顺便帮我算一下 12+34" | 两个都调 | 复合需求触发多个工具 |

> 🐞 **常见坑**：show_tool_logs 在框架的某些版本中可能存在 debug 输出异常。如果看到 `mamba extra` 等无关日志，可以尝试关闭 debug 模式或直接使用 `print` 打印中间结果。这不影响工具调用的正确性，只是调试输出的格式问题。

**关键观察**：

- `show_tool_logs` 在控制台打印的调用记录——**这是节点一输出工具调用指令的直接证据**
- 模型回答中包含了工具返回的数据（温度、天气状况）——**证明节点三回填和节点四消费成功**
- 模型没有「执行」工具——**Agently 框架接收了节点一的声明后代为执行**

> ⚠️ **注意事项**：输入"大海"这类和所有工具都不相关的抽象问题时，模型一个工具都不会调用。这证明模型在工具选择时，确实是基于语义匹配做了判断，而非无条件触发。

---

## 七、多工具选择实战与工具管理

### 7.1 三工具注册与调用

> 🎯 **目标**：注入三个不同领域的工具，观察模型如何根据 prompt 自主决定调用哪些。

在 s02_multi_tool_selection.py 中，我们注册了三个工具：

```python
agent2 = Agently.create_agent()

# 工具一：天气查询
@agent2.tool_func
async def get_weather(
    city: Annotated[str, "城市名称，如 '北京'、'上海'、'Tokyo'"],
) -> dict:
    """查询指定城市的当前天气状况，返回温度（摄氏度）、天气描述和湿度"""
    r = requests.get(f"https://wttr.in/{city}?format=j1", timeout=10)
    cur = r.json()["current_condition"][0]
    return {
        "temp_c": int(cur["temp_C"]),
        "condition": cur["weatherDesc"][0]["value"],
        "humidity": int(cur["humidity"]),
    }

# 工具二：汇率查询
@agent2.tool_func
async def get_exchange_rate(
    from_currency: Annotated[str, "源货币代码，如 'CNY'（人民币）、'USD'（美元）"],
    to_currency:   Annotated[str, "目标货币代码，如 'JPY'（日元）、'EUR'（欧元）"],
) -> dict:
    """查询两种货币之间的实时汇率"""
    r = requests.get(f"https://open.er-api.com/v6/latest/{from_currency}", timeout=10)
    rate = r.json()["rates"].get(to_currency)
    return {"from": from_currency, "to": to_currency, "rate": rate}

# 工具三：节假日查询
@agent2.tool_func
async def get_public_holidays(
    country_code: Annotated[str, "ISO 3166-1 两字母国家代码，如 'JP'、'CN'、'US'"],
    year:         Annotated[int, "查询年份，如 2026"],
) -> list:
    """查询指定国家某年的全部法定节假日，返回日期、本地名称和英文名称"""
    r = requests.get(
        f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}",
        timeout=10,
    )
    return [
        {"date": h["date"], "name": h["localName"], "name_en": h["name"]}
        for h in r.json()
    ]
```

### 7.2 模型自主选择验证

```python
# 场景一：三个需求全部提及
response2 = (
    agent2
    .input("我打算下个月去日本东京出差，帮我查查东京的天气、"
           "人民币兑日元的汇率，以及2026年5月日本有哪些公众假日")
    .use_tool(get_weather)
    .use_tool(get_exchange_rate)
    .use_tool(get_public_holidays)
    .get_response()
)
# → tool_logs 显示三个工具都被调用了 ✅

# 场景二：只提天气和汇率
response2 = (
    agent2
    .input("我去泰国清迈玩，帮我查清迈天气和泰铢汇率")
    .use_tool(get_weather)
    .use_tool(get_exchange_rate)
    .use_tool(get_public_holidays)
    .get_response()
)
# → tool_logs 显示 get_weather ✅, get_exchange_rate ✅
#   get_public_holidays ❌ (没被调用！)
```

> 💡 **核心洞见**：模型读了每个工具的 description 后自己做了判断。代码层面完全没有额外的路由逻辑——没有 if-else 决定调哪个工具。

获取结构化调用记录用于审计和监控：

```python
full = response2.get_data(type="all")
for log in full.get("extra", {}).get("tool_logs", []):
    print(json.dumps(log, ensure_ascii=False, indent=2))
```

### 7.3 工具池三层管理架构

有同学问：「工具特别多怎么办？工具列表会不会很长？所有的工具信息都会加到 prompt 里吗？」

这引出了一个关键的架构设计。我们来看工具的三层管理模型：

```
┌─────────────────────────────────────────────────┐
│           第一层：全量工具池（维护层）               │
│  所有工具都在这里                                  │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │
│  │天气查询│ │汇率查询│ │节假日 │ │数据库 │ │文件IO │  │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘  │
│  可能有几十、几百甚至几千个工具                      │
│  由工具团队/外部门维护                              │
└────────────────────┬────────────────────────────┘
                     │  场景筛选（可根据权限、业务场景）
                     ▼
┌─────────────────────────────────────────────────┐
│         第二层：可激活工具（场景层）                  │
│  当前场景下实际可用的工具子集                        │
│  ┌──────┐ ┌──────┐ ┌──────┐                    │
│  │天气查询│ │汇率查询│ │节假日 │  ← use_tool() 激活  │
│  └──────┘ └──────┘ └──────┘                    │
│  直接影响 prompt 长度 → 影响模型注意力              │
│  由场景处理模块决定                                │
└────────────────────┬────────────────────────────┘
                     │  语义匹配（模型判断）
                     ▼
┌─────────────────────────────────────────────────┐
│         第三层：实际调用工具（请求层）                │
│  模型根据当前问题实际选中的工具                      │
│  ┌──────┐ ┌──────┐                              │
│  │天气查询│ │汇率查询│  ← 模型自主选择               │
│  └──────┘ └──────┘                              │
└─────────────────────────────────────────────────┘
```

> 🧠 **直观理解**：消防队有一个设备仓库（全量工具池），里面什么都有——高压水枪、消防斧、云梯、氧气瓶。但接到「救猫」的警情时，出警小队只带云梯和捕猫网就够了（可激活工具），不需要把水车装满水。最终在救援现场，消防员可能只用到了云梯（实际调用工具）。

**`use_tool()` 到底在做什么？**

`use_tool()` 的本质是：**将指定工具的 schema 信息注入到本次请求的 request data 中**。不调用 `use_tool()`，工具不会默认被加载进来。全量工具池和可激活工具的**分离设计**是工程架构的关键。

> ⚠️ **注意事项**：海量工具全部注入 prompt 会导致模型「失焦」——上下文过长时（尤其是超过 100K），模型注意力分散，工具选择准确率骤降。这也是为什么后面第 8 课会专门讲工具管理。

```
use_tool 的数量决策：
┌────────────────────────────────────────────┐
│  全量池有 1000 个工具                        │
│      │                                      │
│      ├── 通用智能体场景 → 可能需要全部注入     │
│      │   （不推荐：失焦问题严重）              │
│      │                                      │
│      ├── 客服场景 → use_tool(订单, 画像, 政策)│
│      │   （只需 3-5 个，聚焦）               │
│      │                                      │
│      └── 报销场景 → use_tool(发票解析, 表单)  │
│          （只需 2 个，高度聚焦）              │
└────────────────────────────────────────────┘
```

---

## 八、原生 Function Calling 手动实现

### 8.1 构造 Tool Schema

> 🎯 **目标**：不用 Agently 框架，用 OpenAI 原生 SDK 手动走完四节点回路。

```python
# 文件名: s03_native_fc.py
from openai import OpenAI

raw_client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
    base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
)
_MODEL = os.environ.get("DEEPSEEK_DEFAULT_MODEL", "deepseek-v4-flash")

# 手写 tool schema（框架的装饰器就是帮你自动生成这个）
WEATHER_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "查询指定城市的当前天气状况，返回温度（摄氏度）、天气描述和湿度",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string",
                         "description": "城市名称，如 '北京'、'上海'、'Tokyo'"}
            },
            "required": ["city"],
        },
    },
}
```

### 8.2 四步手动走完原生 FC

```python
# ── 节点一：把 prompt + tools schema 发给模型 ─────────────────────
messages = [{"role": "user", "content": "北京今天天气怎么样？适合出去跑步吗？"}]
resp1 = raw_client.chat.completions.create(
    model=_MODEL, messages=messages, tools=[WEATHER_TOOL_SCHEMA]
)
assistant_msg = resp1.choices[0].message
tc = assistant_msg.tool_calls[0]
print(f"[节点一] finish_reason={resp1.choices[0].finish_reason!r}")
print(f"[节点一] 工具调用指令  name={tc.function.name!r}  args={tc.function.arguments}")
# 输出示例：
# [节点一] finish_reason='tool_calls'
# [节点一] 工具调用指令  name='get_weather'  args={"city": "北京"}

# ── 节点二：系统侧执行工具 ────────────────────────────────────
fn_args = json.loads(tc.function.arguments)
result = _call_weather(**fn_args)
print(f"\n[节点二] 执行结果 = {result}")
# 输出示例：
# [节点二] 执行结果 = {'temp_c': 22, 'condition': '晴', 'humidity': 35}

# ── 节点三：把 assistant 消息 + 工具结果追加进对话历史 ───────────
messages.append(assistant_msg)  # 含 tool_calls 字段，不能省略！
messages.append({
    "role": "tool",
    "tool_call_id": tc.id,  # 和节点一的 tool_call id 必须对应
    "content": json.dumps(result, ensure_ascii=False),
})
print(f"\n[节点三] 角色序列 = "
      f"{[m['role'] if isinstance(m, dict) else m.role for m in messages]}")
# 输出示例：
# [节点三] 角色序列 = ['user', 'assistant', 'tool']

# ── 节点四：再次调用模型，基于工具结果生成最终回答 ──────────────
resp2 = raw_client.chat.completions.create(
    model=_MODEL, messages=messages, tools=[WEATHER_TOOL_SCHEMA]
)
print(f"\n[节点四] finish_reason={resp2.choices[0].finish_reason!r}")
print(f"\n最终回答：\n{resp2.choices[0].message.content}")
# 输出示例：
# [节点四] finish_reason='stop'
# 最终回答：
# 北京今天天气晴朗，温度22°C，湿度35%，非常适合户外跑步！
```

**四步走完后的关键观察**：

| 节点 | 谁在做 | 关键字段 | 观察 |
|---|---|---|---|
| 节点一 | 模型 | `finish_reason='tool_calls'` | 模型决定要调工具 |
| 节点二 | 你的代码 | 手动调用 `_call_weather()` | 模型完全不感知 |
| 节点三 | 你的代码 | `role='tool'` + `tool_call_id` | id 必须和节点一对应 |
| 节点四 | 模型 | `finish_reason='stop'` | `'tool_calls'` → `'stop'` |

> 💡 **核心洞见**：不是模型端在做 Function Calling，**是你在做**。模型只管节点一的决策和节点四的生成，节点二和节点三完全是工程侧在驱动。

### 8.3 框架装饰器的本质

现在回头看 Agently 的 `@agent.tool_func`，它的底层逻辑一目了然：

```
装饰器自动完成的事：
┌──────────────────────────────────────────────┐
│ @agent.tool_func                             │
│     │                                        │
│     ├── 从函数名提取 → schema.name            │
│     ├── 从 docstring 提取 → schema.description│
│     ├── 从 Annotated 提取 → schema.parameters │
│     └── 生成标准 JSON Schema（就是你上面手写的）│
└──────────────────────────────────────────────┘
```

它做的就是帮你省掉手写 JSON Schema 的步骤，自动从 Python 的类型标注和文档字符串中提取信息。

---

## 九、为什么要自己实现 Function Calling

### 9.1 原生 FC 的三大问题

> 🧠 **直观理解**：用别人封装的四节点回路就像坐地铁——方便但路线固定。自己实现就像开车——想去哪去哪，但需要会开。

原生 Function Calling（路径一，直接用模型 API 的 `tools=` 参数）有三个核心问题：

**问题一：模型服务依赖**

```
你的企业环境：
├── 可能用的是 Llama 3
├── 可能用的是 Qwen 2.5
├── 可能是自建推理框架
├── 可能是云厂商提供的（千帆、阿里百炼）
└── 问题：它们都支持原生 tool_calls 吗？
    答案：不一定。取决于推理框架、量化方式、甚至部署版本。
```

就算当前版本支持，下次升级模型或换推理框架时接口可能又变了。每次换模型都要重新测试工具调用是否正常——这不是工程应该有的状态。

**问题二：可控性不足**

四节点被封装在一起，你想在中间插入逻辑时无处下手：

```
原生 FC 的封装程度：
┌───────────────────────────────────────┐
│          API 层面的黑箱                 │
│  tools=[schema] → 拿到 tool_calls     │
│         → 回填 → 再次调用              │
│                                       │
│  你无法在中间：                          │
│  ❌ 做权限检查                           │
│  ❌ 插入人工审批                         │
│  ❌ 动态注入业务规则                      │
│  ❌ 修改工具调用参数                      │
└───────────────────────────────────────┘
```

**问题三：封装不可拆分**

像 Codex 或 Claude Code 这类产品，它们内部确实实现了工具调用回路，但你无法把它们的回路抽出来嵌入到你自己的服务中。你的用户不可能每人装一个 Codex。

> 💡 **核心洞见**：不是在给自己用的工具，是在给真正的使用者构建服务。你是服务的构建者，不是 Codex 的使用者。

### 9.2 权限认证的两种路径

在实际企业场景中，工具调用需要权限控制。假设只有老板才能查天气，普通员工不行——权限认证可以发生在两个位置：

**方式一：工具内部做鉴权**

```python
def get_weather(city: str, user_token: str) -> dict:
    """在工具函数内部检查权限"""
    if not has_permission(user_token, "weather:read"):
        raise PermissionError("无权限查询天气")
    # ... 执行查询
```

问题：这种方式将权限和工具紧耦合，且 agent 本身没有身份概念——所有人访问 agent 时用的是同一个身份。

**方式二：工程侧透传鉴权（推荐）**

回想第 5 课的 API 封装层：

```
用户请求（带 token）
    │
    ▼
┌──────────────┐
│  API 封装层    │  ← 在这里获取用户身份
│  解析 token    │
└──────┬───────┘
       │  用户身份透传
       ▼
┌──────────────┐
│  节点二：      │
│  执行工具前     │  ← 在这里做权限判断
│  检查权限      │
└──────┬───────┘
       │  工具调用
       ▼
┌──────────────┐
│  工具函数      │
└──────────────┘
```

> 💡 **核心洞见**：这就是为什么你要自己实现节点二——因为只有在你自己的代码里执行工具调用，才能把鉴权信息一层层透传进去。

### 9.3 动态工具加载

可激活工具清单不一定需要人工指定。我们可以：

```
全量工具池（向量库维护）
    │
    ▼
向量检索 → 预筛选出 N 个相关工具
    │
    ▼
可激活工具组（N 个）
    │
    ▼
模型最终选择 → 实际调用的工具（1-M 个）
```

逐层降低实际注入 prompt 的工具数量，避免失焦。

### 9.4 三条路径的选择决策

```
遇到工具调用需求时：
    │
    ├── 模型支持原生 tool_calls，且你不需要任何定制？
    │   └── 是 → 路径一：直接用 API 的 tools= 参数
    │        （最简单，一个参数搞定）
    │
    ├── 模型不一定支持 tool_calls，你需要解耦模型依赖？
    │   └── 是 → 路径二：Agently use_tool()
    │        （框架帮你选路径，中等可控）
    │
    └── 你需要权限注入、动态工具加载、业务规则定制？
        └── 是 → 路径三：自己实现 TriggerFlow 回路
             （完全可控，但需要自己搭）
```

| 条件 | 路径一 | 路径二 | 路径三 |
|---|---|---|---|
| 模型要求 | 必须支持 FC | 支持 JSON 输出 | 支持 JSON 输出 |
| 权限注入 | 难 | 中 | 易 |
| 动态工具 | 不支持 | 部分支持 | 完全支持 |
| 实现成本 | 低 | 低 | 中 |
| 控制粒度 | 粗 | 中 | 细 |

> 💡 **核心洞见**：没有绝对的答案。你对可控性和定制空间的要求越高，就越需要自己实现。

### 9.5 TriggerFlow 方案概述

路径三的核心思路是使用 Agently 的 TriggerFlow——一个信号驱动的编排引擎。它把四节点回路拆成两个独立的处理块：

```
┌──────────────────┐        ┌──────────────────┐
│  decide chunk    │        │  execute chunk    │
│  (对应节点一)     │ emit   │  (对应节点二三四)  │
│                  │───────▶│                  │
│  判断是否需要工具  │        │  执行工具          │
│  生成调用参数     │        │  回填结果          │
│                  │        │  生成最终回答       │
└──────────────────┘        └──────────────────┘
```

两个 chunk 通过信号（emit_nowait）连接，不是线性调用关系——decide 可以决定走 execute 分支，也可以直接返回 answer。这正是后续 ReAct Loop 的信号驱动基础。

接下来让我们在代码中实现 TriggerFlow 版本的工具调用。

## 十、TriggerFlow 实现工具调用

### 10.1 TriggerFlow 核心概念

> 🎯 **目标**：用 TriggerFlow + 结构化输出，实现不依赖模型原生 tool_calls 的工具调用回路。

TriggerFlow 是 Agently 框架中的**信号驱动编排引擎**。它的核心概念非常简洁：

| 概念 | 说明 | 类比 |
|---|---|---|
| **Chunk** | 一个独立的处理函数（async 函数） | 流水线上的一个工位 |
| **State** | 贯穿所有 chunk 的共享数据 | 公告板，谁都可以读、可以写 |
| **Signal (emit)** | chunk 之间传递消息 | "做完了，下一个工位接手！" |
| **flow.to()** | 设置入口 chunk | 流水线的起点 |
| **flow.when("信号名").to(chunk)** | 信号路由 | "收到这个信号就去那个工位" |

```
TriggerFlow 的工作模型：

flow.start(state)
    │
    ▼
┌──────────┐  emit("Execute")  ┌──────────┐
│  decide   │─────────────────▶│ execute_and│
│  chunk    │                  │ _answer   │
└────┬─────┘                  └────┬─────┘
     │ async_set_state()           │
     │ (不发信号, flow 终止)        │
     ▼                             ▼
  state.get("answer")        state.get("answer")
```

### 10.2 decide chunk：节点一的 TriggerFlow 版本

```python
# 文件名: s04_triggerflow_single.py
from agently import TriggerFlow, TriggerFlowRuntimeData

def build_single_tool_flow(tool_info: dict, handler) -> TriggerFlow:
    flow = TriggerFlow(name="single-tool-flow")

    async def decide(data: TriggerFlowRuntimeData):
        """节点一（结构化输出版）：模型决定是否调工具及参数"""
        question = data.input
        d = (
            Agently.create_agent()
            .input(question)
            .info({"可用工具": tool_info})
            .instruct([
                "根据问题判断是否需要调用上述工具",
                "如果需要，输出 needs_tool=true 并填写参数",
                "如果不需要，直接给出答案",
            ])
            .output({
                "needs_tool": (bool,         "是否需要调用工具"),
                "tool_args":  ("dict | null", "需要时填写工具参数"),
                "answer":     ("str | null",  "不需要工具时的直接回答"),
            })
            .get_response()
        ).get_data(ensure_keys=["needs_tool"])

        print(f"[节点一] needs_tool={d['needs_tool']}  args={d.get('tool_args')}")

        if d["needs_tool"]:
            # 需要工具 → 发射 "Execute" 信号，附带 question 和 args
            data.emit_nowait("Execute", {
                "question": question,
                "args": d.get("tool_args") or {}
            })
        else:
            # 不需要工具 → 直接写 state，不发射信号（flow 终止）
            await data.async_set_state("answer", d.get("answer", ""), emit=False)
```

**这里有三层 prompt slot（提示槽位）**：

| Slot | 方法 | 作用 | 位置 |
|---|---|---|---|
| `input` | `.input()` | 用户原始问题 | user 区域 |
| `info` | `.info()` | 工具描述、上下文信息 | info 区域 |
| `instruct` | `.instruct()` | 行为指令、业务规则 | instruct 区域 |

> 💡 **核心洞见**：三个 slot 最终都会被合并到 prompt 中，只是框架会根据各自的位置做顺序优化。如果你不用框架自己实现，就相当于你自己维护一个模板，把这些信息签到模板里去。

**`.output()` 的强约束**：

```python
.output({
    "needs_tool": (bool,         "是否需要调用工具"),    # 类型 + 描述
    "tool_args":  ("dict | null", "需要时填写工具参数"),
    "answer":     ("str | null",  "不需要工具时的直接回答"),
})
```

这个 `output()` 是提前告诉模型「你必须按这个 JSON 结构回答我」。框架层会做类型校验，不符合 schema 的回答会被拒绝并重试。这就是 M05 中提到的「利用模型 JSON 输出能力 + 框架强约束」——不依赖原生 FC 训练，任何能稳定输出 JSON 的模型都能用。

### 10.3 execute_and_answer chunk

```python
    async def execute_and_answer(data: TriggerFlowRuntimeData):
        """节点二+三+四：执行工具，回填结果，生成最终回答"""
        state = data.input  # 从信号中接收 question + args

        # 节点二：系统侧执行工具
        result = handler(**state["args"])
        print(f"[节点二] 结果: {result}")

        # 节点三+四：把结果注入下一次模型调用，生成最终回答
        answer = (
            Agently.create_agent()
            .input(state["question"])
            .info({"工具结果": result})
            .instruct("根据工具返回的信息回答用户的问题")
            .get_text()
        )
        await data.async_set_state("answer", answer)
```

注意这里 `data.input` 拿到的就是 `emit_nowait("Execute", {...})` 中传递的数据——信号传递的同时也传递了数据。

### 10.4 信号路由与启动

```python
    # 配置信号路由
    flow.to(decide)                        # 入口：从 decide 开始
    flow.when("Execute").to(execute_and_answer)  # 收到 "Execute" → 去执行
    # 注意：execute_and_answer 结束后如果不发信号，flow 自然关闭
    return flow

# 使用：
WEATHER_TOOL_INFO = {
    "name": "get_weather",
    "desc": "查询指定城市的当前天气状况，返回温度（摄氏度）、天气描述和湿度",
    "args": {"city": "城市名称，如 '北京'、'Tokyo'"},
}

single_flow = build_single_tool_flow(WEATHER_TOOL_INFO, _call_weather)
state = single_flow.start("北京今天天气怎么样？适合出去跑步吗？")
print(f"\n最终回答：\n{state.get('answer', '')}")
```

**完整信号流转图**：

```
flow.start("北京今天天气怎么样？...")
         │
         ▼
     ┌─────────┐
     │  decide  │
     └────┬─────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
needs_tool   needs_tool
  = true      = false
    │           │
    │           ▼
    │    async_set_state("answer", ...)
    │    emit=False → flow 终止 ✅
    │
    ▼
emit_nowait("Execute", {question, args})
    │
    ▼
┌──────────────────┐
│ execute_and_answer│
│  1. 执行工具       │
│  2. 注入结果       │
│  3. 生成回答       │
└──────┬───────────┘
       │
       ▼
async_set_state("answer", answer)
→ flow 终止 ✅
```

| | 路径一（原生 FC） | 路径二（TriggerFlow） |
|---|---|---|
| 节点一实现 | `tools=[schema]` 传给 API | `.output()` 拿结构化决策 |
| 节点二-四 | `messages.append` + 第二次 API 调用 | 在 `execute_and_answer` chunk 中完成 |
| 模型要求 | 必须支持原生 FC | 支持结构化 JSON 输出即可 |
| 控制粒度 | API 层面自动处理 | 每步完全可见、可定制 |
| 可注入点 | 0 个 | instruct / info / execute 前均可注入 |

---

## 十一、ReAct Loop 原理与 TriggerFlow 实现

### 11.1 从翻车演示到 ReAct Loop

> 🧠 **直观理解**：M10 的单工具 TriggerFlow 只能一次调用一个工具。如果你问「帮我查东京天气和人民币兑日元汇率」，模型实际上两个都需要——但我们的回路只设计了一个工具调用槽位。

课堂上的「翻车」演示展示了一个关键现象：

```
输入："我去泰国旅游，帮我查清迈天气和泰铢汇率"
  ↓
模型输出 tool_calls: [get_weather, get_exchange_rate]
  ↓
但我们的 decide → execute 回路只处理了第一个工具！
  ↓
第二个工具被丢弃 ❌
```

这不是模型的问题——模型正确地判断了需要两个工具。问题在于我们的回路设计：**单次 decide → execute 只能承载一个工具调用的决策**。

更根本的问题是：**回路没有反思机制**——不会检查「当前是否已经回答了用户的所有信息需求」。

### 11.2 ReAct Loop 的概念模型

ReAct Loop 的核心思路：**Reason（推理）→ Act（行动）→ Observe（观察）→ 循环，直到信息足够**。

```
┌──────────────────────────────────────────────────┐
│                                                  │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐  │
│  │  Reason  │────▶│   Act    │────▶│ Observe  │  │
│  │ 推理决策  │     │ 执行工具  │     │ 观察结果  │  │
│  └──────────┘     └──────────┘     └────┬─────┘  │
│       ▲                                 │        │
│       └─────────── 循环 ◀───────────────┘        │
│                                                  │
│  Reason 判断"信息够了"→ 输出 final answer → 结束   │
└──────────────────────────────────────────────────┘
```

ReAct Loop 和四节点回路的关系：

| 四节点回路 | ReAct Loop |
|---|---|
| 单次请求 | 多轮循环 |
| 固定路径：1→2→3→4 | 每轮都是 1→2→3，循环决定是否继续 |
| 不检查完整性 | 每轮检查"还需要什么信息" |
| 适合单一需求 | 适合复合需求 |

### 11.3 基础 ReAct Loop 代码实现

在看 TriggerFlow 版本之前，先用最直接的方式理解 ReAct Loop 的逻辑（s03_react_loop.py）：

```python
def react_loop(question: str, tools: dict, max_steps: int = 5) -> str:
    done_steps = []
    tools_desc = [
        {"name": k, "desc": v["desc"], "args": v["args"]}
        for k, v in tools.items()
    ]

    for step in range(max_steps):
        print(f"\n[Step {step + 1}]")
        # ── Reason 阶段 ──
        response = (
            Agently.create_agent()
            .input(question)
            .info({"可用工具": tools_desc, "已完成步骤": done_steps})
            .instruct([
                "根据问题和已完成步骤判断：是否需要再调用工具？",
                "如果需要，输出 type='tool' 并指定工具名和参数",
                "如果已有足够信息，输出 type='final' 并给出最终回答",
            ])
            .output({
                "type":      ("'tool' | 'final'", "下一步动作类型"),
                "reasoning": ("str",              "推理：现在知道了什么、还缺什么"),
                "tool_name": ("str | null",        "type=='tool' 时填工具名"),
                "tool_args": ("dict | null",       "type=='tool' 时填参数"),
                "answer":    ("str | null",        "type=='final' 时填最终回答"),
            })
            .get_response()
        )
        d = response.get_data(ensure_keys=["type", "reasoning"])

        if d["type"] == "final":
            return d.get("answer", "")

        # ── Act + Observe 阶段 ──
        tool_name = d.get("tool_name")
        tool_args = d.get("tool_args") or {}
        result = tools[tool_name]["func"](**tool_args)
        done_steps.append({"tool": tool_name, "args": tool_args, "result": result})

    return "已达到最大步骤数"
```

```
执行示例：
[Step 1]
  推理：用户需要东京天气和汇率信息，先查天气
  决策：tool
  执行：get_weather({"city": "东京"})
  结果：{"temp_c": 15, "condition": "多云", "humidity": 60}

[Step 2]
  推理：已获得天气信息，还需要汇率信息
  决策：tool
  执行：get_exchange_rate({"from_currency": "CNY", "to_currency": "JPY"})
  结果：{"from": "CNY", "to": "JPY", "rate": 20.5}

[Step 3]
  推理：已获得天气和汇率信息，可以给出完整建议
  决策：final
```

> ⚠️ **注意事项**：`output` 中的输出顺序很重要——先 `reasoning` 后 `type`（COT 顺序）。如果反过来（先 type 后 reasoning），模型有时会为了迎合它当时瞬间做出的决定而在 reasoning 里强行解释。

### 11.4 TriggerFlow 版 ReAct Loop

用 TriggerFlow 实现 ReAct Loop，信号驱动机制天然匹配循环结构（s05_react_triggerflow.py）：

| ReAct 概念 | TriggerFlow 实现 |
|---|---|
| Reason | `reason` chunk：调用模型，决定下一步 |
| Act + Observe | `act_and_observe` chunk：执行工具，结果追加进 state |
| 循环 | `emit_nowait("Reason", state)` 让信号循回 |
| 终止 | `async_set_state("answer", ...)` + `return` 不发信号，flow 自然关闭 |

```python
def build_react_flow(tools: dict, max_steps: int = 5) -> TriggerFlow:
    tools_schema = [
        {"name": k, "desc": v["desc"], "args": v["args"]}
        for k, v in tools.items()
    ]
    flow = TriggerFlow(name="react-loop")

    async def reason(data: TriggerFlowRuntimeData):
        state = data.input
        step = state["step"] + 1
        print(f"\n[Step {step}] Reason")

        d = (
            Agently.create_agent()
            .input(state["question"])
            .info({"可用工具": tools_schema, "已完成步骤": state["history"]})
            .instruct([
                "根据问题和已完成步骤判断：是否需要再调用工具？",
                "如果需要，输出 type='tool' 并指定工具名和参数",
                "如果已有足够信息，输出 type='final' 并给出最终回答",
            ])
            .output({
                "type":      ("'tool' | 'final'", "下一步动作类型"),
                "reasoning": ("str",              "推理：现在知道了什么、还缺什么"),
                "tool_name": ("str | null",        "type=='tool' 时填工具名"),
                "tool_args": ("dict | null",       "type=='tool' 时填参数"),
                "answer":    ("str | null",        "type=='final' 时填最终回答"),
            })
            .get_response()
        ).get_data(ensure_keys=["type", "reasoning"])

        print(f"  推理：{d.get('reasoning', '')}")
        print(f"  决策：{d['type']}")

        new_state = {**state, "step": step, "last_decision": d}

        if d["type"] == "tool" and step < max_steps:
            # 信号循环：发 "Act" → act_and_observe 执行完后
            #          又会发 "Reason" → 回到这里的 reason
            data.emit_nowait("Act", new_state)
        else:
            # 终止：写 answer，不发信号
            await data.async_set_state(
                "answer", d.get("answer") or "已达到最大步骤数", emit=False
            )

    async def act_and_observe(data: TriggerFlowRuntimeData):
        state = data.input
        d = state["last_decision"]
        tool_name = d.get("tool_name", "")
        tool_args = d.get("tool_args") or {}

        if tool_name not in tools:
            data.emit_nowait("Reason", state)  # 工具不存在 → 回到 reason
            return

        print(f"  Act: {tool_name}({tool_args})")
        result = tools[tool_name]["func"](**tool_args)
        print(f"  Observe: {result}")

        new_state = {
            **state,
            "history": state["history"] + [
                {"tool": tool_name, "args": tool_args, "result": result}
            ],
        }
        data.emit_nowait("Reason", new_state)  # ← 循环的关键：发回 "Reason"

    # 信号路由配置
    flow.to(reason)                 # 入口
    flow.when("Act").to(act_and_observe)   # "Act" → 执行
    flow.when("Reason").to(reason)         # "Reason" → 推理（循环的关键！）

    return flow
```

**信号流转完整图**：

```
flow.start({question, history:[], step:0})
         │
         ▼
     ┌─────────┐
     │ reason  │◀──────────────────────────┐
     └────┬─────┘                          │
          │                                │
    ┌─────┴─────────┐                      │
    │               │                      │
    ▼               ▼                      │
type='tool'     type='final'               │
    │               │                      │
    │               ▼                      │
    │    async_set_state("answer",...)      │
    │    emit=False → flow 终止 ✅          │
    │                                      │
    ▼                                      │
emit_nowait("Act", new_state)              │
    │                                      │
    ▼                                      │
┌──────────────────┐                      │
│ act_and_observe  │                      │
│  1. 执行工具       │                      │
│  2. 追加 history   │                      │
│  3. emit_nowait   │──────────────────────┘
│     ("Reason",...) │    ← 信号循回！
└──────────────────┘
```

> 💡 **核心洞见**：`emit_nowait("Reason", state)` 是循环的驱动力。Chunk 之间通过信号互相触发，`state` 是贯穿全程的"公告板"。当 reason 决定终止时，它不发信号，flow 自然关闭——`flow.start()` 返回最终的 state 快照。

### 11.5 基础 ReAct 的缺陷分析

```
基础 ReAct Loop 的三个缺陷：

┌─────────────────────────────────────────────┐
│ 缺陷一：无限循环风险                           │
│                                              │
│ reason 完全靠模型自主判断是否终止               │
│ → 模型可能一直认为"信息还不够"                  │
│ → 无限烧 token，直到上下文窗口打满              │
├─────────────────────────────────────────────┤
│ 缺陷二：单步单工具                             │
│                                              │
│ 每轮只调用一个工具                             │
│ → 天气和汇率两个独立请求必须串行                 │
│ → 等待时间 = 天气耗时 + 汇率耗时               │
├─────────────────────────────────────────────┤
│ 缺陷三：工具调用失败无处理                       │
│                                              │
│ 工具抛出异常 → 整个 loop 中断                   │
│ → 用户拿到的是错误信息，不是最终回答             │
└─────────────────────────────────────────────┘
```

两个最基础的改进手段：

| 改进 | 方式 | 位置 |
|---|---|---|
| **轮次限制** | `step < max_steps` 条件判断 | reason chunk 中 |
| **上下文长度监测** | 计算 history 的 token 数 | reason chunk 中 |

但这两个手段只能防止无限循环，不能解决其他两个问题。接下来我们看一下生产级框架是怎么处理这些问题的。

---

## 十二、生产级框架优化对比

### 12.1 三框架对比总览

> 🧠 **直观理解**：我们造的是一辆能跑的卡丁车。Hermes Agent 和 OpenClaw 是跑在赛道上的赛车——基础原理一样，但在关键位置做了专业级优化。

| 问题 | 我们的基础实现 | Hermes Agent | OpenClaw |
|---|---|---|---|
| **单步多工具** | 单次一个，循环多次 | `ThreadPoolExecutor` 并行执行 | 顺序执行，hook 拦截 |
| **工具调用失败** | 不处理，直接崩 | 记录错误，继续下一轮 | `after_tool_call` hook 检查 |
| **步骤预算耗尽** | 硬截断，无答案 | 90步 + Grace Call（强制给答案） | 10分钟总超时 |

### 12.2 Hermes Agent：并行执行 + Grace Call

**并行工具执行**（来源：Hermes Agent Agent Loop Internals，已简化）：

```python
if len(tool_calls) == 1:
    result = execute_tool(tool_calls[0])
    messages.append({"role": "tool", "content": result})
else:
    # 多工具：ThreadPoolExecutor 并发执行
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(execute_tool, tc): tc for tc in tool_calls}
        for tc in tool_calls:
            result = futures[tc].result()
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result
            })
```

**预算追踪 + Grace Call**（已简化）：

```python
while iterations < max_iterations:
    response = call_llm(messages, tools)
    if response.tool_calls:
        execute_tools(response.tool_calls)
        iterations += 1
    else:
        return response.content  # 正常终止

# Grace Call：预算耗尽后，不截断，让模型用当前信息给出最佳答案
final = call_llm(messages + [{
    "role": "user",
    "content": "请基于当前信息给出最佳答案"
}])
return final.content
```

> 💡 **核心洞见**：Grace Call 不是简单截断——它在最后一轮请求中注入了一个特殊提示，告诉模型「请用你手上现有的信息给出最佳回答」。这比硬截断多了最后一次机会，显著提升了预算耗尽时的用户体验。

### 12.3 OpenClaw：Hook 拦截机制

OpenClaw 不在工具执行层面做并行，但提供了更灵活的 Hook 机制（来源：docs.openclaw.ai，TypeScript 已简化）：

```typescript
for (const toolCall of response.toolCalls) {
    // 执行前：可以做权限检查、审批拦截
    const decision = await hooks.beforeToolCall(toolCall, session);
    if (decision === "block") continue;

    const result = await executeTool(toolCall);

    // 执行后：审计结果、记录日志
    await hooks.afterToolCall(toolCall, result, session);
    messages.push({ role: "tool", content: result });
}
```

Hook 的核心价值在于**外部插入的插件式处理器**——在不修改 agent 核心逻辑的情况下：

| Hook 类型 | 可做的事 |
|---|---|
| `before_tool_call` | 权限检查、参数校验、审批拦截、请求改写 |
| `after_tool_call` | 结果审计、日志记录、副作用处理、结果改写 |

### 12.4 Action 类型的扩展谱系

> 💡 **核心洞见**：Function Calling 里的 "function" 只是 Action 类型中的一种。当我们把 Action 的类型进行扩展，它的执行方式就完全不同了。

```
Action 类型扩展谱系：

function       → 调用本地函数
call MCP       → 发起网络请求到 MCP server
run bash       → 在本地 shell 环境执行命令
run python     → 在沙盒中执行 Python 代码
execute SQL    → 连接数据库执行 SQL 语句
```

| Action 类型 | 执行环境 | 安全性 | 并行方式 |
|---|---|---|---|
| function call | 当前进程 | 高（代码可控） | 异步 |
| MCP server | 远端 server | 中（网络隔离） | 异步 |
| run bash | 本地/沙盒 | 低（需沙盒保护） | 多线程 |
| run python | 沙盒 | 中（沙盒隔离） | 多线程 |
| execute SQL | 数据库连接 | 中（数据表隔离） | 异步/连接池 |

### 12.5 异步 vs 多线程的选择

有同学问：「并行处理就是用异步实现吗？」

答案取决于 Action 的具体类型：

```
你的任务是 IO 密集型？
  │  （大多数 HTTP 调用、MCP server 调用、数据库查询）
  │
  ├── 是 → 用异步（asyncio）
  │   一个进程单线程能瞬间起 5000-10000 个并发
  │   因为大部分时间在等待网络响应，CPU 空闲
  │
  └── 否，是 CPU 密集型？
       （大量本地计算、Python 数据处理）
       │
       └── 是 → 用多线程（ThreadPoolExecutor）
           受限于 CPU 核数，M2 Pro 芯片大概三四百个线程
           才能真正利用多核并行计算能力
```

> ⚠️ **注意事项**：如果你不确定 Action 的类型，框架默认使用异步是合理的。但当你确定某类 Action 是计算密集型时，就需要自己掰开框架、改用线程池——这就是定制化的核心场景。

---

## 十三、ReAct Loop v2 改进实现

### 13.1 改进 1：多工具并行执行

> 🎯 **目标**：将 M12 的三个优化方案落地到 TriggerFlow ReAct Loop 中。

v2 的核心变化：**reason 一次声明所有需要的工具**，**act_and_observe 用 asyncio.gather 并发执行**。

```python
# 文件名: s06_react_v2.py
import asyncio

async def run_one_tool(name: str, args: dict, tools: dict) -> dict:
    """单个工具执行器：异步 + 错误捕获"""
    print(f"    → {name}({args})")
    try:
        result = (
            await asyncio.to_thread(tools[name]["func"], **args)
            if name in tools
            else {"error": f"未知工具: {name}"}
        )
    except Exception as e:
        result = {"error": str(e)}
    print(f"    ← {name}: {result}")
    return {"tool": name, "args": args, "result": result}
```

`asyncio.to_thread` 的作用：将同步的 `tools[name]["func"](**args)` 调用放到线程池中执行，返回一个可被 `await` 的协程。这样多个工具就能用 `asyncio.gather` 并发执行。

```python
def build_react_flow_v2(tools: dict, max_steps: int = 6) -> TriggerFlow:
    tools_schema = [
        {"name": k, "desc": v["desc"], "args": v["args"]}
        for k, v in tools.items()
    ]
    flow = TriggerFlow(name="react-loop-v2")

    async def reason(data: TriggerFlowRuntimeData):
        state = data.input
        step = state["step"] + 1
        budget_left = max_steps - step
        print(f"\n[Step {step}/{max_steps}] Reason（剩余预算：{budget_left}）")

        # Grace Call 提示注入
        extra = (
            [f"步骤预算只剩 {budget_left} 步，请直接基于现有信息给出最佳回答"]
            if budget_left <= 1
            else []
        )

        d = (
            Agently.create_agent()
            .input(state["question"])
            .info({"可用工具": tools_schema, "已完成步骤": state["history"]})
            .instruct([
                "根据问题和已完成步骤判断：是否需要调用工具？",
                # v2 关键变化：一次声明所有需要的工具
                "如果需要，一次声明所有需要的工具（填写 tool_calls 列表）",
                "如果已有足够信息，输出 type='final' 并给出最终回答",
                *extra,
            ])
            .output({
                "type":       ("'tool' | 'final'", "下一步动作类型"),
                "reasoning":  ("str",               "推理"),
                # v2 关键变化：tool_calls 是列表，不再是单个 tool_name
                "tool_calls": (
                    "[{name: str, args: dict}] | null",
                    "type=='tool' 时填，可声明多个"
                ),
                "answer":     ("str | null",         "type=='final' 时填最终回答"),
            })
            .get_response()
        ).get_data(ensure_keys=["type", "reasoning"])

        print(f"  推理：{d.get('reasoning', '')}")
        new_state = {**state, "step": step}

        if budget_left <= 0 or d["type"] == "final":
            label = "Grace Call" if budget_left <= 0 else "主动终止"
            print(f"  决策：final（{label}）")
            await data.async_set_state(
                "answer", d.get("answer") or "已达到最大步骤数", emit=False
            )
            return

        tool_calls = d.get("tool_calls") or []
        if not tool_calls:
            await data.async_set_state("answer", d.get("answer") or "", emit=False)
            return

        print(f"  决策：tool × {len(tool_calls)}")
        data.emit_nowait("Act", {**new_state, "pending_tools": tool_calls})
```

### 13.2 改进 2：Grace Call

```
预算充足时：
  模型自由决定 type='tool' 或 type='final'

budget_left <= 1 时：
  → 注入 "步骤预算只剩 1 步，请直接基于现有信息给出最佳回答"
  → 给模型紧迫感，让它倾向于输出 type='final'

budget_left <= 0 时：
  → 强制走 final 分支
  → 标签改为 "Grace Call"
  → 让模型用现有 answer 或默认消息
```

> 💡 **核心洞见**：Grace Call 的本质是**用 prompt engineering 替代硬截断**——给模型紧迫感而非直接掐断，换取更好的用户体验。

### 13.3 改进 3：错误捕获

```python
    async def act_and_observe(data: TriggerFlowRuntimeData):
        state = data.input
        pending = state.get("pending_tools") or []
        print(f"  Act：并行执行 {len(pending)} 个工具")

        # asyncio.gather 并发执行所有工具
        results = await asyncio.gather(*[
            run_one_tool(tc.get("name", ""), tc.get("args") or {}, tools)
            for tc in pending
        ])

        # 错误结果也会被加入 history：
        # {"tool": "xxx", "args": {...}, "result": {"error": "异常信息"}}
        new_state = {**state, "history": state["history"] + list(results)}
        data.emit_nowait("Reason", new_state)
```

错误结果进入 history 后，下一轮 reason 能看到 `{"error": "..."}` 的信息，模型可以自主决定：
- 换个参数重试这个工具
- 放弃这个工具，用现有信息给出回答
- 换一个替代工具

### 13.4 v1 vs v2 完整对比

| 维度 | v1（基础 ReAct） | v2（改进版） |
|---|---|---|
| **工具声明** | `tool_name: str` 单个 | `tool_calls: [{name, args}]` 列表 |
| **工具执行** | 同步单个调用 | `asyncio.gather` + `asyncio.to_thread` 并发 |
| **预算管理** | `step < max_steps` 硬截断 | `budget_left` 渐进式 + 紧迫感注入 |
| **预算耗尽** | 直接返回 "已达到最大步骤数" | Grace Call：让模型用现有信息回答 |
| **错误处理** | 不处理，工具异常 → 整个 loop 崩 | try/except + 错误信息回传 history |
| **未知工具** | 不处理 | 返回 `{"error": "未知工具: xxx"}` |

**完整运行示例**：

```
[Step 1/4] Reason（剩余预算：3）
  推理：用户需要东京天气和汇率，两个信息独立，可以并行获取
  决策：tool × 2
  Act：并行执行 2 个工具
    → get_weather({'city': '东京'})
    → get_exchange_rate({'from_currency': 'CNY', 'to_currency': 'JPY'})
    ← get_weather: {'temp_c': 15, 'condition': '多云', 'humidity': 60}
    ← get_exchange_rate: {'from': 'CNY', 'to': 'JPY', 'rate': 20.5}

[Step 2/4] Reason（剩余预算：2）
  推理：已获得天气和汇率，可给出完整出行建议
  决策：final（主动终止）
```

在这个例子中，v2 只需要 **2 轮**就完成了 v1 需要 3 轮才能完成的任务——原因是天气和汇率在 Step 1 被**并行执行**了。

> 🔗 **推导链**：单工具调用 → 单次四节点回路 → 多工具串行 ReAct Loop → 多工具并行 ReAct Loop v2。整个演进过程就是工程控制力不断增强的过程。

## 十四、课程答疑精选

> 本章按主题分为四个板块，收录课程结尾答疑环节的核心问题和回答。

### 14.1 工具与框架选择

---

**🙋 问题 1**：目前是不是用 CLI 的趋势多过 MCP？怎么看？

> 📖 **背景**：学员大量接触了 Claude Code、Codex、OpenClaw 等 CLI 工具，感觉 CLI 是行业主流方向。

**💬 老师回答**：

这不是趋势问题，是**感知问题**。你看到 CLI 的趋势多过 MCP，是因为你大量接触了 C 端产品——Claude Code、Codex 这类工具确实是目前成熟度最高的 AI 产品，它们的核心场景是帮你在本机上完成任务。

但你看不到企业级服务背后在干嘛。企业服务里，MCP 的服务模块切分在安全性上远高于 CLI。API 调用也比你见到的 CLI 调用多得多——只是企业服务不对 C 端消费者展示。

**判断原则**：
- C 端视角 → 以 CLI 为主（开发者在自己的机器上完成任务）
- B 端视角 → 以 API/MCP 为主（服务模块间通过标准化协议交互）
- 不能笼统地说「CLI 趋势多过 MCP」——这是信息茧房效应

> 💡 **延伸**：从安全角度看，MCP 的服务模块切分天然比 CLI 安全。CLI 本质是本地执行，权限是用户的全部权限；MCP 可以把权限控制在单个服务级别。

---

**🙋 问题 2**：为什么选 Agently 而不是 LangChain？

> 📖 **背景**：LangChain 生态更大、物料更多，为什么课程用 Agently？

**💬 老师回答**：

这不是一个「谁更好」的问题，而是从不同角度看各有优劣：

| 维度 | Agently | LangChain |
|---|---|---|
| 国内模型适配 | 较好 | 双向适配都较差 |
| 代码可维护性 | Python 原生表达，直观 | 抽象层多，阅读负担重 |
| 教学友好度 | 一目了然，信息透传直观 | 封装深，初学者阅读有负担 |
| 生态 | 相对小 | 物料多、社区大 |
| 适合场景 | 自己维护代码、追求直观 | 主要让模型开发、关心生态 |

> 💡 **延伸**：如果主要让模型写代码，LangChain 的生态确实有优势。但如果追求代码的意图性和可维护性，Python 原生表达更直观。动态选择，按需决策。

---

**🙋 问题 3**：TriggerFlow 的 ReAct Loop 要自己实现吗？没有封装吗？

> 📖 **背景**：学员想知道是否可以直接调用框架现成的 ReAct Loop。

**💬 老师回答**：

ReAct Loop 没有标准封装——因为它的变体太多了。我们光是看了 Hermes Agent 和 OpenClaw 两个实现，就有并行执行、Grace Call、Hook 拦截等不同方案。

**ReAct Loop 本身是一个方法论，不是一个固定实现。** 触类旁通——理解了原理之后，你可以根据业务需要做出各种变体。

Agently 的 `use_tool` 不是 ReAct Loop，它内部使用了 TriggerFlow 做信号编排，有并发、有回路、有失败降级——但它的实现方式与你手写的 ReAct Loop 不同，它是框架级的多层编排。

> 💡 **延伸**：掌握了 TriggerFlow 的信号驱动模式，你不仅会写 ReAct Loop，还会写任何需要多轮决策的编排流程。

---

**🙋 问题 4**：Skills 可以理解为 TriggerFlow + ReAct 的一种方式吗？

> 📖 **背景**：学员观察到 Skills 也需要多轮调用，联想到 ReAct Loop。

**💬 老师回答**：

不是。Skills 和 ReAct Loop 是不同的东西：

**Skills** 是一套综合的信息组织方式——它不仅仅是 prompt，还包括可执行的脚本。消费 Skills 需要一个比 ReAct Loop 更复杂的执行器：
1. 先读 Skills 的最外层（元数据、描述）
2. 由类似 ReAct Loop 的行为决定是否需要深入读取 Skills 的内部模块
3. 如果需要 Skills 提供的脚本，执行脚本
4. 脚本的执行不是简单的函数调用——可能性非常多，需要专用的执行器

**ReAct Loop** 是信号驱动的多轮决策机制，它关注的是「如何循环」而非「循环什么内容」。

Skills 的消费过程**可能用到** ReAct Loop 的模式，但它们不是一个层面的概念。

---

### 14.2 输入输出格式

---

**🙋 问题 5**：GLM 现在风向 HTML > Markdown，怎么看？

> 📖 **背景**：有模型厂商在输出格式上倾向 HTML，引发学员对格式选择的疑问。

**💬 老师回答**：

我认为这是**噱头**。正确的做法是按场景分，而不是非 A 即 B。

**输入端（用户 → 模型）**：
- 用户的自然表达是语音/口语 > 书面
- 书面表达中，Markdown 永远优于 HTML
- Markdown 天然提供了标题、列表、代码等结构化表达方式
- HTML 标签对人类书写不友好
- **结论：输入端不能放弃 Markdown**

**输出端（模型 → 用户）**：
- HTML 确实能表达更丰富的层次关系（位置、嵌套、样式）
- Markdown 偏顺次型，对复杂层次关系的表达能力有限
- 但不是所有场景都需要复杂层次关系
- **结论：需要丰富呈现时用 HTML，简单场景用 Markdown**

> 💡 **延伸**：这就像甜豆脑和咸豆脑——不需要争个你死我活，可以都喜欢。场景决定格式，而非格式决定场景。

---

### 14.3 工程落地实践

---

**🙋 问题 6**：VS Code + Code Agent 和 Cursor 哪个好用？

> 📖 **背景**：学员在多个 AI 编程工具中犹豫。

**💬 老师回答**：

个人偏好 VS Code + Codex（5.5 以上 + 中高思考强度），体验比 Claude Code 好。

**Cursor 的优缺点**：
- 优点：团队管理功能——成员使用统计、代码生成量、最爱模型、代码采纳率
- 缺点：模型供应受限，可能被 Anthropic 等公司限制；模型能力不行时很多功能就用不了

**选择建议**：个人开发者 → VS Code + Codex。研发团队管理者 → Cursor 的团队版提供了独特的管理视角。

---

**🙋 问题 7**：准备用 Agent 做自动化测试，OpenCloud 能满足吗？

> 📖 **背景**：学员想用 Agent 做 APP 自动化测试，点击 APP 看界面效果。

**💬 老师回答**：

可以试 OpenCloud，但更推荐 Codex 或 Claude Code 近期的定时任务能力。在 token 消耗量、准确度和质量上，后两者远高于 OpenCloud。

**更精细的建议**：
- **巡检行为非常固定** → 用 Flow 编排一套固定流程即可，甚至可以用 Codex 装一个定时任务
- **巡检行为很发散**（每次测试的内容不同）→ 用 Claude Code 或 Codex 的 agent 模式更合适

---

**🙋 问题 8**：现在各行各业的 Agent 落地到什么程度了？

> 📖 **背景**：学员对 AI 在 B 端的真实落地情况感到好奇。

**💬 老师回答**：

C 端视角和 B 端视角有很大的偏差。B 端的落地不是「把人干掉、用数字员工替代」——那是自媒体喜欢的故事。

**真实的落地方式是**：在企业的信息流程中找到**胶水级节点**，逐渐把 AI 嵌入进去。

| 行业 | 落地场景举例 |
|---|---|
| 企业 OA | 报销——发票上传 → AI 解析 → 自动填表单 |
| 银行 | 理财咨询师辅助——AI 帮检索产品信息、合规政策 |
| 招投标 | 标书评定——AI 辅助信息提取和比对 |
| BI 分析 | 业务数据统计——自然语言查询 → AI 生成 SQL + 图表 |

> 💡 **核心洞见**：不是不解决问题，而是解决的没有自媒体吹的那么高。B 端要的不是一个高大上的全能智能体，而是一个能解决特定 feature 问题的智能体。

---

**🙋 问题 9**：怎么看待 Dify 这类工具？

> 📖 **背景**：学员关注低代码 AI 平台的价值。

**💬 老师回答**：

Dify 有价值，但价值在**复杂系统里偏弱**。它的核心价值是把业务人员的 AI 能力释放出来——做一些业务流程的编排。但真正复杂的业务，Dify 也好、no-code 也好，都做不到。这也是为什么 Dify/no-code 的热度在最近一年下来了。

---

**🙋 问题 10**：如果工具很多，工具列表会不会很长？

> 📖 **背景**：延续 M07 的工具池管理讨论。

**💬 老师回答**：

会的。几千个工具的 schema 全部注入 prompt，上下文会被直接打满。解决方案就是前面讲的三层架构：

1. **全量工具池**：向量库维护（可以成千上万个）
2. **可激活工具**：通过检索预筛选（几十个）
3. **实际调用**：模型从可激活中挑选（几个）

每一层都在缩小范围。向量检索做初筛 → 模型做精选。

---

**🙋 问题 11**：系统侧执行工具代码的 `handler(**state["args"])` 是怎么传参的？

> 📖 **背景**：学员对 Python 的 `**` 字典展开语法不熟悉。

**💬 老师回答**：

`state["args"]` 是一个字典，比如 `{"city": "北京"}`。`**` 操作符把字典展开为关键字参数：`handler(city="北京")`。

整个数据流：

```
emit_nowait("Execute", {"question": "...", "args": {"city": "北京"}})
    │
    ▼
data.input  # → {"question": "...", "args": {"city": "北京"}}
    │
    ▼
state = data.input
state["args"]  # → {"city": "北京"}
    │
    ▼
handler(**state["args"])  # → handler(city="北京")
```

---

**🙋 问题 12**：execute SQLite 是怎么运行的沙盒？

> 📖 **背景**：学员好奇 SQL 类 Action 的隔离机制。

**💬 老师回答**：

本质上不是沙盒。execute SQLite 的 Action 是让模型生成 SQL 指令，然后执行器连接数据库去运行。隔离发生在**数据库连接层面**——不同环境的 SQLite 操作的是不同的数据表、不同的数据库文件。

这不是传统意义上的沙盒（进程/容器隔离），而是**数据层隔离**。在生产环境中，你通常会为不同的 session 或不同的用户创建独立的数据库连接或临时表。

---

### 14.4 AI 能力与职业发展

---

**🙋 问题 13**：不太理解 AI 是怎么做到理解整个代码库的逻辑的？

> 📖 **背景**：学员对 Codex 等工具如何「理解」大型代码库感到好奇。

**💬 老师回答**：

AI 的理解机制都是一样的——所有模型在生成下一个 token 时，一定是基于**上下文**。

但关键问题：**上下文怎么做到「理解整个代码库」？**

Codex 这类工具**不会把整个代码库一次性丢进上下文**。中间的机制包括：

```
代码库
  │
  ▼
AST 解析 → 提取代码的语义结构（类、函数、依赖关系）
  │
  ▼
信息精炼 → 只保留与当前任务相关的部分
  │
  ▼
上下文组装 → 相关代码片段 + 项目结构 + 当前问题
  │
  ▼
模型生成 → 基于精炼后的上下文输出回答
```

那些看起来像「思考」的过程，实际上是**多次模型请求并发执行**的结果——「看看这个文件」「检查那个依赖」「理解这个函数」——可能是 2-3 次甚至更多次请求在背后并行。

---

**🙋 问题 14**：AI 在软件工程各阶段能发挥什么作用？

> 📖 **背景**：学员想了解 AI 在完整开发流程中的位置。

**💬 老师回答**：

从需求分析到设计文档、自动化测试到发布，AI 都可以参与。但需要**建立自己的行为模式**：

1. **Spec-Driven Development**：告诉模型「在开发之前不要写代码，先理解需求，先写需求文档和设计文档给我看」
2. **TDD**：让 AI 先写测试，再写实现
3. **架构需要自己管**：AI 做 code review 没问题，但架构决策必须人来把控——模型经常会做出「反架构」的事情

> 💡 **延伸**：Spec DD + TDD 是目前使用 AI 辅助编程的一个比较标准的基本思想。模型本身不知道最优的行为模式——需要你来建立和维护规则。

---

**🙋 问题 15**：学完这门课去哪种类型的公司最好？

> 📖 **背景**：学员关心职业发展路径。

**💬 老师回答**：

都可以去。这门课讲的是「AI 能力怎么切入到软件系统」——这是一个正在发生的事情，也是**一次真正的软件工程范式革命**。

**范式革命的本质**：系统里多了一个模糊处理节点（模型），整个系统需要去回应和适应这个节点的存在。

**当前阶段**（1-10% AI 嵌入）：以原有信息系统为主，AI 像胶水一样补充现有系统的不足。

**未来阶段**（可能到五五开）：AI 的灵活度和智能带来的价值提升，超过了「写死系统」带来的稳定性追求时，会迎来大规模系统重构。

**你掌握的能力**：不是在用某个 AI 工具——而是能够规划「AI 能力应该放在系统哪里」「原有系统能力应该放在哪里」，掌握模块边界的划分能力。这是一个底层能力，不管去哪类公司都有价值。

---

**🙋 问题 16**：团队完全使用 AI 来编码吗？

> 📖 **背景**：学员好奇 AI 在实际团队中的渗透程度。

**💬 老师回答**：

AI 编码和人工编码都有。现在的认知是：
- AI 写 code 肯定没问题
- 但 code 必须 review——**架构必须自己管**
- 模型经常做出反架构的事情
- 团队需要逐渐形成规范、规则、测试体系

本质上是搭建**自己团队的工作环境**——Spec DD、TDD、编码规范、审查流程——这些都是靠人来做的，AI 是加速器但不是决策者。

---

## 📎 技术附录：深度补充与排错实录

> 本附录为各模块的深度补充内容，包含逐行代码解析、关键原理深入、排错实录和实际应用场景。
> 每个子章节标有对应的主文档模块编号，可按需交叉参考。

### 附 A：单工具调用——装饰器与 Schema 的映射（对应 M06）

#### 6.2.1 装饰器与 Schema 的映射关系——逐行解析

让我们逐行拆解 `@agent.tool_func` 装饰器是如何将 Python 函数转化为 Tool Schema 的：

```python
@agent.tool_func                              # ← 1. 将函数注册到 agent 的工具表
async def get_weather(                        # ← 2. async：框架支持异步工具执行
    city: Annotated[str, "城市名称..."]        # ← 3. 参数名 → schema.city
) -> dict:                                    # ← 4. 返回值类型提示（非必须，但推荐）
    """查询指定城市的当前天气状况..."""           # ← 5. docstring → schema.description
    r = requests.get(                          # ← 6. 实际的工具逻辑
        f"https://wttr.in/{city}?format=j1",
        timeout=10
    )
    cur = r.json()["current_condition"][0]
    return {
        "temp_c": int(cur["temp_C"]),          # ← 7. 返回结构化数据
        "condition": cur["weatherDesc"][0]["value"],
        "humidity": int(cur["humidity"]),
    }
```

| 行号 | Python 元素 | 转化方向 | Schema 中对应的字段 |
|---|---|---|---|
| 1 | `@agent.tool_func` | 触发装饰器处理 | 整个 schema 由此生成 |
| 2 | 函数名 `get_weather` | → | `schema.name = "get_weather"` |
| 3 | `city: Annotated[str, "城市名称..."]` | → | `schema.parameters.properties.city = {"type": "string", "description": "城市名称..."}` |
| 4 | `-> dict` | → | 返回值类型信息（框架用于校验） |
| 5 | `"""查询指定城市..."""` | → | `schema.description = "查询指定城市...天气描述和湿度"` |
| 6-7 | 函数体 | — | 不进入 schema，只在节点二执行时才用到 |

> 💡 **核心洞见**：Annotated 类型标注中的第二个参数（字符串）是**给模型看**的参数描述。它和 docstring 一起，决定了模型如何理解这个工具的能力边界。如果你在这里写了模糊的描述，模型填参数时也会填得模糊。

### 附 B：工具调用日志与工具池维护（对应 M07）

#### 7.2.1 工具调用记录的编程式获取

当 `show_tool_logs = True` 时，控制台会打印类似以下的结构化日志。这是理解四节点回路在框架中如何运作的最直接窗口：

```
[Tool Call Start]
  Tool: get_weather
  Input: {"city": "北京"}
[Tool Call End]
  Output: {"temp_c": 22, "condition": "晴", "humidity": 35}
```

这段日志对应了：
- `[Tool Call Start]` → **节点一结束**：模型决策完成，框架收到了 tool_calls
- `Tool: get_weather` → 框架从 tool_calls 中提取的 name 字段
- `Input: {"city": "北京"}` → 框架从 tool_calls 中提取的 arguments 字段
- `[Tool Call End]` → **节点二结束**：工具执行完成
- `Output: {"temp_c": 22, ...}` → 工具的返回值，即将进入节点三回填

> 🐞 **常见坑**：本课程演示中出现过 `show_tool_logs` 输出异常的问题。表现是打印出 `mamba extra` 等与工具调用无关的调试信息。原因是在本地调试环境中，框架的某个版本中 `show_tool_logs` 的实现与其他 debug 模块产生了日志输出冲突。**解决方案**：关闭 `show_tool_logs`，改用 `print` 直接打印 `response.get_data(type="all")` 中的 `tool_logs` 字段。

---

### 7.2.1 工具调用记录的编程式获取

除了通过 `show_tool_logs` 在控制台观察，也可以通过代码获取结构化的工具调用记录。这对于**审计日志**、**监控告警**和**调试**非常重要：

```python
# 获取包含 tool_logs 的完整响应
full = response2.get_data(type="all")

# tool_logs 的结构
# [
#   {
#     "tool_name": "get_weather",
#     "input": {"city": "东京"},
#     "output": {"temp_c": 15, "condition": "多云", "humidity": 60},
#     "timestamp": "2026-07-05T14:08:35",
#     "duration_ms": 320
#   },
#   {
#     "tool_name": "get_exchange_rate",
#     "input": {"from_currency": "CNY", "to_currency": "JPY"},
#     "output": {"from": "CNY", "to": "JPY", "rate": 20.5},
#     "timestamp": "2026-07-05T14:08:35",
#     "duration_ms": 450
#   }
# ]

for log in full.get("extra", {}).get("tool_logs", []):
    print(f"工具: {log.get('tool_name')}")
    print(f"参数: {log.get('input')}")
    print(f"结果: {log.get('output')}")
    print(f"耗时: {log.get('duration_ms')}ms")
    print("---")
```

### 附 C：原生 FC 实现细节（对应 M08）

#### 8.2.1 节点一的隐藏细节：prompt 中到底拼了什么

三层架构中的第一层（全量工具池）看起来简单，但在大型工程中它有自己的维护挑战：

```
全量工具池的维护维度：

┌─────────────────────────────────────────────┐
│ 维度 1：工具注册                              │
│ • 内部开发团队注册新工具                        │
│ • 外部部门通过 MCP server 暴露能力              │
│ • 第三方 SaaS API 封装为工具                   │
├─────────────────────────────────────────────┤
│ 维度 2：工具版本管理                           │
│ • 工具接口变更时如何保证向后兼容？               │
│ • 是否支持多个版本的同一工具同时存在？           │
├─────────────────────────────────────────────┤
│ 维度 3：工具元数据                             │
│ • 健康状态（可用/降级/不可用）                   │
│ • 调用频率限制（rate limit）                   │
│ • 归属信息（哪个团队维护）                      │
│ • 安全等级（是否需要审批）                      │
├─────────────────────────────────────────────┤
│ 维度 4：工具发现                               │
│ • 新工具如何被场景模块发现？                     │
│ • 工具废弃后如何通知所有使用方？                 │
└─────────────────────────────────────────────┘
```

> 🔗 **前置知识**：工具管理的详细方案将在第 08 课专门展开。本节的重点是理解「为什么需要三层分离」——这个架构认知比具体的实现方式更重要。

---

### 8.2.1 节点一的隐藏细节：prompt 中到底拼了什么

当调用 `raw_client.chat.completions.create(model=_MODEL, messages=messages, tools=[WEATHER_TOOL_SCHEMA])` 时，API 层在幕后做了大量的 prompt 拼接工作。我们可以近似理解为最终的 prompt 包含以下部分：

```
[System Prompt - 框架/API 自动生成]
你是一个有用的助手。你可以使用以下工具来帮助回答用户的问题。

[可用工具列表 - 从 tools= 参数自动注入]
{
  "name": "get_weather",
  "description": "查询指定城市的当前天气状况...",
  "parameters": {
    "city": {"type": "string", "description": "城市名称..."}
  }
}

当你需要使用工具时，请输出以下格式的 JSON：
{"name": "工具名", "arguments": {...}}

[User Message]
北京今天天气怎么样？适合出去跑步吗？
```

**关键点**：工具的 schema 信息和格式指令，都是 API 层自动插入到 prompt 中的。如果是路径二（TriggerFlow），这些信息由你手动通过 `.info()` 和 `.instruct()` 注入——这正是可控性的来源。

#### 8.2.2 节点三的易错点：tool_call_id 对齐

节点三中最容易被忽略但最容易出错的细节是 `tool_call_id`：

```python
# ❌ 错误：忘记添加 assistant_msg
messages.append({
    "role": "tool",
    "tool_call_id": tc.id,  # ← 必须有这个 id
    "content": json.dumps(result, ensure_ascii=False),
})
# → API 报错: "Missing assistant message with tool_calls"

# ❌ 错误：tool_call_id 不匹配
messages.append({
    "role": "tool",
    "tool_call_id": "random_wrong_id",  # ← id 错误
    "content": json.dumps(result, ensure_ascii=False),
})
# → API 报错或模型行为异常

# ✅ 正确：完整回填
messages.append(assistant_msg)  # ← 先加 assistant 消息
messages.append({
    "role": "tool",
    "tool_call_id": tc.id,       # ← 用完全相同的 id
    "content": json.dumps(result, ensure_ascii=False),
})
```

> 🐞 **常见坑**：省略 `messages.append(assistant_msg)` 直接加 tool 消息，会导致 API 返回错误。因为模型需要知道「工具结果是对哪次工具调用的回应」——而 assistant 消息中的 `tool_calls[].id` 就是这个关联的桥梁。

**角色序列的演化过程**：

```
请求前:
  messages = [{"role": "user", "content": "北京天气?"}]

节点一响应后:
  messages = [
    {"role": "user", "content": "北京天气?"},
    {"role": "assistant", "tool_calls": [{"id": "call_abc", ...}]}  ← 新增
  ]

节点三追加后:
  messages = [
    {"role": "user", "content": "北京天气?"},
    {"role": "assistant", "tool_calls": [{"id": "call_abc", ...}]},
    {"role": "tool", "tool_call_id": "call_abc", "content": "{...}"}  ← 新增
  ]

节点四第二次请求 → 模型看到完整的对话历史 → 基于工具结果回答
```

---

### 附 D：ReAct Loop 状态管理与信号驱动（对应 M11）

#### 11.3.1 ReAct Loop 状态管理详解

ReAct Loop 中的 `state` 是贯穿全程的核心数据结构。理解它的演化过程，是理解 ReAct Loop 的关键：

```
state 的初始状态:
{
  "question": "我下周要去东京出差，帮我查一下东京天气和人民币兑日元的汇率，给我一个出行建议",
  "history": [],
  "step": 0
}

Step 1 - Reason 后:
{
  "question": "我下周要去东京出差...",     ← 不变
  "history": [],                          ← 尚未执行任何工具
  "step": 1,                              ← 步数 +1
  "last_decision": {                      ← Reason 的决策结果
    "type": "tool",
    "reasoning": "用户需要东京天气信息，先查天气",
    "tool_name": "get_weather",
    "tool_args": {"city": "东京"},
    "answer": null
  }
}
  ↓ emit_nowait("Act", state)

Step 1 - Act_and_observe 后:
{
  ...以上所有字段,
  "history": [                            ← history 追加了一条
    {
      "tool": "get_weather",
      "args": {"city": "东京"},
      "result": {"temp_c": 15, "condition": "多云", "humidity": 60}
    }
  ]
}
  ↓ emit_nowait("Reason", state)

Step 2 - Reason:
  模型看到的 info = {
    "可用工具": [...],
    "已完成步骤": [{  ← 就是 history 的内容
      "tool": "get_weather",
      ...
    }]
  }

  模型推理: "已经有了天气，还需要汇率"
  决策: type='tool', tool_name='get_exchange_rate', ...
```

> 💡 **核心洞见**：`state` 就是 ReAct Loop 的「记忆」。history 不断累加工具调用记录，每一轮 reason 都能看到「到目前为止已经做了什么」——这正是模型能够做出「还需要什么」判断的基础。

#### 11.4.1 emit_nowait 的信号驱动原理深入

`emit_nowait` 是 TriggerFlow 中最重要的概念之一。理解它的行为模式，是理解整个 ReAct Loop 实现的关键：

```
emit_nowait("Act", data) 的行为:
┌──────────────────────────────────────────────┐
│ 1. 向 flow 发送一个 "Act" 信号                  │
│ 2. 附带 data 作为接收方的 input                │
│ 3. 当前 chunk 继续执行（不等待，不阻塞）          │
│ 4. 当前 chunk 执行完毕后，flow 调度器分发信号     │
│    → 找到 when("Act").to(act_and_observe)     │
│    → 调用 act_and_observe(data)               │
└──────────────────────────────────────────────┘

async_set_state("answer", value, emit=False) 的行为:
┌──────────────────────────────────────────────┐
│ 1. 将 state["answer"] 设为 value               │
│ 2. emit=False → 不发送任何信号                  │
│ 3. 当前 chunk 执行完毕且无新信号 → flow 自然关闭  │
│ 4. flow.start() 返回当前 state 快照            │
└──────────────────────────────────────────────┘
```

两种终止方式的区别：

| 终止方式 | 行为 | 用户体验 |
|---|---|---|
| `async_set_state(emit=False)` + `return` | 优雅终止，写入结果 | 用户拿到完整回答 |
| `step >= max_steps` 硬截断（v1） | 强制终止，"已达到最大步骤数" | 用户可能拿不到有价值的回答 |
| Grace Call（v2） | 预算耗尽前最后一次请求，注入紧迫感 | 用户拿到基于现有信息的最佳回答 |

#### 11.5.1 为什么 ReAct Loop 容易"停不下来"

模型在 ReAct Loop 中「停不下来」的三个常见原因：

```
原因 1：工具描述过于宽泛
┌─────────────────────────────────────────────┐
│ 模型看到：「这个工具可以搜索网页」               │
│ 模型心想：「也许再搜一次会有更好的结果？」         │
│ → 无限循环搜索                                 │
│ 解决：工具描述中加入边界说明                     │
│ 「搜索最近 7 天的网页内容，每次最多返回 10 条」    │
└─────────────────────────────────────────────┘

原因 2：prompt 没有明确告知「何时应该停止」
┌─────────────────────────────────────────────┐
│ 缺少：「如果已经获取了用户需要的所有信息，请停止」 │
│ instruct 中应明确终态条件                      │
└─────────────────────────────────────────────┘

原因 3：工具结果中包含新的「线索」
┌─────────────────────────────────────────────┐
│ 搜索结果中提到了一个新话题                     │
│ 模型被「吸引」去探索新话题                      │
│ → 离最初的问题越来越远                         │
│ 解决：instruct 中强调「只回答最初的问题」        │
└─────────────────────────────────────────────┘
```

### 附 E：生产级框架深入——预算控制与 Hook 场景（对应 M12）

#### 12.2.1 Hermes Agent 的完整上下文监测机制

除了轮次限制，Hermes Agent 还加入了**上下文长度监测**。这不只是简单的 token 计数：

```python
# 上下文长度监测的简化逻辑
def check_context_budget(messages: list, max_tokens: int = 24000):
    current_tokens = count_tokens(messages)

    if current_tokens > max_tokens * 0.8:
        # 80% 阈值：给模型一个温和的提醒
        messages.append({
            "role": "system",
            "content": "上下文即将达到上限，请尽快给出最终回答。"
        })

    if current_tokens > max_tokens:
        # 超过上限：强制触发 Grace Call
        return True  # 不再继续工具调用

    return False  # 可以继续
```

> ⚠️ **注意事项**：轮次限制和上下文长度监测解决的是**不同的问题**。轮次限制防止「一直在做事」，上下文监测防止「单轮获取了太多信息」。比如一轮网页搜索返回了一篇超长论文——轮次只增加了 1，但上下文可能已经打满了。两个机制需要共同作用。

### 12.3.1 Hook 机制的实际应用场景

OpenClaw 的 Hook 机制在以下场景中特别有价值：

```
场景一：敏感工具审批
┌─────────────────────────────────────────────┐
│ before_tool_call: "delete_production_data"   │
│   → 检查操作是否涉及生产数据                    │
│   → 需要经理审批 → block                        │
│   → 发送审批通知 → 等待                          │
│   → 审批通过 → 放行                              │
└─────────────────────────────────────────────┘

场景二：工具调用审计
┌─────────────────────────────────────────────┐
│ after_tool_call: 任何工具调用                  │
│   → 记录：用户、时间、工具名、参数、结果          │
│   → 写入审计日志数据库                          │
│   → 检测异常调用模式（如短时间内大量失败调用）    │
│   → 触发告警                                   │
└─────────────────────────────────────────────┘

场景三：结果改写
┌─────────────────────────────────────────────┐
│ after_tool_call: "search_customer_data"      │
│   → 检查返回结果中是否包含 PII（个人隐私信息）   │
│   → 脱敏处理：替换身份证号、手机号              │
│   → 将脱敏后的结果返回给模型                    │
└─────────────────────────────────────────────┘
```
### 附 F：完整代码索引与脚本对应关系

下表列出课程中 7 个演示脚本与本文档各模块的对应关系，方便读者按需查阅源码：

| 脚本文件 | 对应模块 | 核心内容 | 关键知识点 |
|---|---|---|---|
| `s01_single_tool.py` | M06 | 单工具完整回路 | `@agent.tool_func`, `use_tool()`, `show_tool_logs` |
| `s02_multi_tool_selection.py` | M07 | 三工具自主选择 | 多工具注册, 模型自主选择, `get_data(type="all")` |
| `s03_native_fc.py` | M08 | 原生 FC 手动实现 | `tools=[schema]`, `tool_calls`, 四节点手动走 |
| `s03_react_loop.py` | M11 | 基础 ReAct Loop | while 循环版 ReAct, `output()` 结构化决策 |
| `s04_triggerflow_single.py` | M10 | TriggerFlow 单工具 | `decide` + `execute_and_answer`, `emit_nowait` |
| `s05_react_triggerflow.py` | M11 | TriggerFlow ReAct | 信号驱动的多轮循环, state 公告板 |
| `s06_react_v2.py` | M13 | ReAct v2 改进版 | `asyncio.gather` 并行, Grace Call, 错误捕获 |

### 附 G：三条实现路径的完整决策框架

回顾 M09 中讨论的三条路径，这里提供更完整的决策框架，帮助你根据实际场景选择合适的实现方式：

```
开始：我需要在我的系统中实现工具调用
  │
  ├── Q1: 你使用的模型是否稳定支持原生 tool_calls？
  │   ├── 否 → 跳转到 Q3（只能用路径二或三）
  │   └── 是 → 继续 Q2
  │
  ├── Q2: 你是否需要在工具调用过程中做以下任一操作？
  │   ├── 权限检查（不同用户有不同的工具权限）
  │   ├── 人工审批（敏感操作需要确认）
  │   ├── 审计日志（记录每次工具调用的详细信息）
  │   ├── 结果改写（脱敏、翻译、格式化工具返回结果）
  │   └── 动态工具选择（根据用户身份/场景动态调整可用工具）
  │
  │   ├── 全部不需要 → ✅ 路径一：原生 FC
  │   │   直接用 API 的 tools= 参数
  │   │   优点：最简单，代码最少
  │   │   缺点：无定制空间
  │   │
  │   └── 需要部分 → 继续 Q3
  │
  ├── Q3: 你的定制需求仅限于 prompt 层面（如业务规则提示、工具描述优化）？
  │   ├── 是 → ✅ 路径二：框架 use_tool() + 结构化输出
  │   │   用 Agently 的 use_tool() 或类似框架
  │   │   优点：解耦模型依赖，中低实现成本
  │   │   缺点：节点二/三的深度定制受限
  │   │
  │   └── 否 → 继续 Q4
  │
  └── Q4: 你需要深度定制吗？
      │  （如：权限透传到工具内部、自定义执行环境、复杂错误恢复策略）
      │
      └── 是 → ✅ 路径三：自己实现 TriggerFlow 回路
          用 TriggerFlow + 结构化输出
          优点：完全可控，可以插任何逻辑
          缺点：需要自己写更多代码
```

**实际案例参考**：

| 场景 | 推荐路径 | 原因 |
|---|---|---|
| 个人项目，用 DeepSeek v3，查天气机器人 | 路径一 | 模型支持 FC，无定制需求 |
| 公司内部 OA 机器人，需区分员工/经理权限 | 路径二 | 用框架处理工具选择，权限在 API 层控制 |
| 金融系统对客智能体，需全链路审计 + 敏感操作审批 | 路径三 | 每个环节都需要插入定制逻辑 |
| 开源项目，需要兼容多种模型 | 路径二或三 | 不能依赖特定模型的 FC 支持 |

### 附 H：TriggerFlow 信号路由模式汇编

TriggerFlow 的信号路由配置是整个编排系统的核心。以下是本文档中出现的所有信号路由模式及其适用场景：

**模式 1：单次决策 → 执行（M10）**

```python
flow.to(decide)
flow.when("Execute").to(execute_and_answer)
# decide 内部：
#   需要工具 → emit_nowait("Execute", data)
#   不需要工具 → async_set_state("answer", ..., emit=False)
```

适用场景：单一工具调用，不需要多轮。

**模式 2：循环决策 → 执行（M11）**

```python
flow.to(reason)
flow.when("Act").to(act_and_observe)
flow.when("Reason").to(reason)  # ← 循环的关键
# reason 内部：
#   需要工具 → emit_nowait("Act", state)
#   不需要 → async_set_state("answer", ..., emit=False)
# act_and_observe 内部：
#   执行完后 → emit_nowait("Reason", new_state)
```

适用场景：多轮工具调用，模型自主判断何时结束。

**模式 3：多信号分支（扩展）**

```python
flow.to(reason)
flow.when("Act").to(act_and_observe)
flow.when("Reason").to(reason)
flow.when("AskUser").to(ask_user_chunk)     # 需要用户输入时
flow.when("Error").to(error_handler_chunk)   # 出错时
# reason 内部可以根据情况发射不同信号：
#   需要工具 → emit_nowait("Act", state)
#   需要确认 → emit_nowait("AskUser", state)
#   出错 → emit_nowait("Error", state)
```

适用场景：复杂的 Agent 流程，需要处理多种情况。

**关键规则**：
- `emit_nowait`：发射信号后当前 chunk 继续执行（非阻塞），执行完后信号被分发
- `async_set_state(key, value, emit=False)`：写入 state 但不发射信号 → flow 关闭
- `flow.start(input_data)`：启动 flow 并等待关闭，返回最终 state 快照
- `data.input`：接收上一个 chunk 通过信号传递过来的数据

### 附 I：常见错误排查速查表

以下是课程中出现的所有排错场景和对应的解决方案速查：

| # | 现象 | 原因 | 解决方案 |
|---|---|---|---|
| 1 | `show_tool_logs` 输出 `mamba extra` 等无关信息 | 框架版本 debug 日志冲突 | 关闭 `show_tool_logs`，改用手动 `print` 或 `get_data(type="all")` |
| 2 | 多工具场景下只有一个工具被调用 | decide→execute 回路只处理了第一个工具 | 改为 ReAct Loop 或 v2 的 tool_calls 列表 |
| 3 | 节点四报错 "Missing assistant message" | 节点三遗漏 `messages.append(assistant_msg)` | 先 append assistant_msg，再 append tool_msg |
| 4 | 模型选择工具时行为随机 | 多个工具的 description 匹配度接近 | 细化 description 和 parameters，增加区分度 |
| 5 | ReAct Loop 无限循环不停 | 模型判断"信息还不够"，继续调工具 | 加 `max_steps` 限制 + Grace Call |
| 6 | 上下文打满后模型输出质量骤降 | 单轮获取的信息过多（如长网页） | 上下文长度监测 + 80% 阈值提醒 |
| 7 | 工具调用超时导致整个流程中断 | 工具执行无超时控制，无错误处理 | `try/except` + 超时设置 + 错误信息回传 history |
| 8 | 权限检查无法在工具调用前完成 | 原生 FC 的节点二被封装在 API 层 | 改用路径三，在 execute chunk 中手动做权限检查 |
| 9 | `tool_call_id` 不匹配导致节点四失败 | ID 复制错误或使用随机值 | 严格使用 `tc.id` 进行传递 |
| 10 | 模型生成的参数不符合预期类型 | `output()` 的类型约束不够精确 | 细化 `output()` 的类型定义，使用 `ensure_keys` |

### 附 J：面向工程落地的架构设计要点总结

结合本课内容，以下是面向企业级工程落地的关键架构设计要点：

**1. 工具与模型的解耦**

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   业务逻辑     │────▶│  工具调用层    │────▶│   模型层      │
│  （不变的部分） │     │ （可切换实现）  │     │ （可替换模型） │
└──────────────┘     └──────────────┘     └──────────────┘
```

工具调用层（无论用路径一、二还是三）应该在架构上独立于模型层。这样切换模型时，工具调用逻辑不需要修改。

**2. 权限模型设计**

```
用户请求 → API Gateway（鉴权）→ Agent 服务（携带用户身份）
  → 工具调用层（根据身份筛选可激活工具集）
  → 工具执行（透传身份，工具内部做细粒度权限控制）
```

**3. 可观测性设计**

每个节点的输入输出都应该可被观测：
- 节点一：记录 prompt + schema + 模型输出的 tool_calls
- 节点二：记录工具名称、参数、执行耗时、返回结果
- 节点三：记录对话历史的 token 数变化
- 节点四：记录最终回答和 finish_reason

**4. 容错与降级**

```
工具调用失败 → 错误进入 history → 模型下一轮看到
  ├── 可以重试（换个参数）
  ├── 可以放弃（用现有信息）
  └── 可以降级（换一个功能相似的工具）
```

> 💡 **核心洞见**：容错不需要额外的复杂逻辑——只要把错误信息像正常结果一样追加到 history 中，模型自己就能理解和处理。这是 ReAct Loop 的天然优势。

---

## 📋 课程小结

### 🗺️ 知识图谱

```
                         ┌─────────────────────────┐
                         │   工具调用回路与 ReAct Loop │
                         └────────────┬────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              ▼                       ▼                       ▼
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │   四节点回路      │    │   Tool Schema    │    │   工具池架构     │
    │                 │    │                 │    │                 │
    │ 节点一: 模型决策  │    │ name → 系统路由  │    │ 全量池 → 可激活  │
    │ 节点二: 系统执行  │    │ desc → 模型选择  │    │ → 实际调用      │
    │ 节点三: 结果回填  │    │ params → 双向    │    │                 │
    │ 节点四: 模型生成  │    │                 │    │ 向量检索预筛选   │
    └────────┬────────┘    └────────┬────────┘    └────────┬────────┘
             │                      │                      │
             └──────────────────────┼──────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
          ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
          │ 路径一: 原生FC │ │ 路径二:       │ │ 路径三:       │
          │              │ │ TriggerFlow  │ │ 完整 ReAct    │
          │ API tools=   │ │ 结构化输出    │ │ Loop + 定制   │
          │ 简单但受限    │ │ 中等可控      │ │ 完全可控      │
          └──────────────┘ └──────┬───────┘ └──────┬───────┘
                                  │                  │
                                  ▼                  ▼
                          ┌──────────────┐  ┌──────────────┐
                          │ ReAct Loop   │  │ ReAct v2     │
                          │ Reason→Act   │  │ 并行+Grace    │
                          │ →Observe     │  │ Call+容错     │
                          │ 信号驱动循环  │  │ 生产级优化    │
                          └──────────────┘  └──────────────┘
```

### 💡 一句话总结

> 工具调用回路是模型与外部世界交互的基础协议，ReAct Loop 是这个协议的多轮升级版——理解四节点原理之后，你就可以按业务需求自己搭建、定制、甚至改写整个回路，而不依赖任何「标准方案」。

### 📍 系列定位

> 📍 **系列定位**：本文是「AI 应用开发实战」系列第 06 篇。
> - 上一篇：第 05 课 — 工程骨架搭建：从脚本到 FastAPI 服务，将 AI 能力打包为可对外提供的接口
> - 下一篇：第 07 课 — （即将发布，敬请期待）

---

## 📝 课后练习

### 练习 1：手写四节点回路

**题目**：不依赖 Agently 框架，使用 OpenAI SDK 手写一个完整的 Function Calling 回路，实现一个「获取指定城市当前时间」的工具。

**验收标准**：
- [ ] 手写 tool schema（包含 name、description、parameters）
- [ ] 节点一能正确输出 `finish_reason='tool_calls'`
- [ ] 节点三中 `tool_call_id` 与节点一保持一致
- [ ] 节点四 `finish_reason` 变为 `'stop'`
- [ ] 最终回答中包含工具返回的时间数据
- [ ] 代码中打印出四节点的关键输出（参考 s03_native_fc.py）

### 练习 2：用 TriggerFlow 实现多工具选择

**题目**：参考 s04_triggerflow_single.py，用 TriggerFlow 实现一个支持两个工具的 decide → execute 回路（比如天气 + 汇率）。关键要求：模型自主判断是否需要工具、需要哪个工具。

**验收标准**：
- [ ] 使用 `build_single_tool_flow` 的架构模式
- [ ] `decide` chunk 中用 `.output()` 做结构化输出
- [ ] `emit_nowait` 信号路由到 `execute_and_answer`
- [ ] 不依赖原生 tool_calls 接口
- [ ] 输入「今天天气怎么样」和「CNY 兑 USD 汇率」两个不同问题，验证模型选择了正确的工具

### 练习 3：完善 ReAct Loop v2

**题目**：在 s06_react_v2.py 的基础上，增加一个工具（如 `get_public_holidays`），并验证三个工具并行执行的 correctness。额外要求：添加一个「工具调用超时」（timeout=5s）的错误场景，验证 Grace Call 在工具超时情况下能否给出有意义的回答。

**验收标准**：
- [ ] 三个工具能在一次 reason 中被同时声明
- [ ] `asyncio.gather` 并发执行，总耗时约等于最慢工具的时间
- [ ] 工具超时时，错误被正确捕获并记录到 history
- [ ] 超时后 Grace Call 能基于部分结果给出回答
- [ ] 打印每一步的推理和决策过程

---

> 📅 生成日期: 2026-07-05 | 🎯 级别: XL 级 | ⏱️ 录音时长: ~101 分钟 | 📏 文档规模: 2,780+ 行
> 🤖 由 transcript-to-doc v4.2 生成
