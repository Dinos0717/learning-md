# 20_Session 会话管理与上下文组装管线

> 📅 生成日期: 2026-07-14 | 🎯 级别: L 级 | ⏱️ 录音时长: ~78 分钟 | 📏 文档规模: 3,800+ 行
> 🏷️ 标签: `Session` `上下文窗口` `多轮对话` `会话管理` `Handler管线` `Workspace持久化`

---

## 📑 目录

- [一、课程引入：从多轮对话的 append 开始](#一课程引入从多轮对话的-append-开始)
- [二、原始 append 的代价：结构化输出与上下文膨胀](#二原始-append-的代价结构化输出与上下文膨胀)
- [三、共享 Agent 状态风险：多用户上下文混乱](#三共享-agent-状态风险多用户上下文混乱)
- [四、Session 独立化：会话池设计与多会话管理](#四session-独立化会话池设计与多会话管理)
- [五、Session 三件职责与 Context Window 概念](#五session-三件职责与-context-window-概念)
- [六、Handler 管线架构：分析器与压缩器](#六handler-管线架构分析器与压缩器)
- [七、Handler 代码实战：策略注册与执行演示](#七handler-代码实战策略注册与执行演示)
- [八、Session 持久化：Workspace 绑定与快照](#八session-持久化workspace-绑定与快照)
- [九、参考案例：OpenAI SDK 与 OWASP 安全边界](#九参考案例openai-sdk-与-owasp-安全边界)
- [十、课程小结与答疑精选](#十课程小结与答疑精选)

---

## 一、课程引入：从多轮对话的 append 开始

### 1.1 前情回顾：Workspace 与 Session 的职责边界

上节课我们深入介绍了 **Workspace（工作空间）** 这一底层组件。它的核心职责是帮助 Agent 在本地指定的文件夹中完成文件的落地与存储——当 Agent 需要生成代码、保存中间结果或写出数据文件时，Workspace 负责执行这些文件系统操作。

但 Workspace 有一个关键特征：**用户通常对它无感知**。在日常使用 Claude Code、CodeBuddy 或 Cursor 这类 AI 编程工具时，它们会在项目目录下创建自己的工作窗口（比如 `.claude/` 目录），但我们很少主动关注这些底层文件夹里发生了什么。Workspace 承担的是「幕后基础设施」的角色——它让 Agent 能够读写文件，但用户感受不到它的存在。

本节课要讨论的 **Session（会话管理）** 则截然不同——它直接管理 Agent 在多轮对话中的**信息流转**。当你在和 AI 助手连续对话时，它能不能记住你 3 分钟前说过的话、能不能关联上下文来回答你的追问——这就是 Session 机制在起作用。用户对 Session 的感知要强烈得多，因为它直接影响对话的连贯性和智能程度。

| 维度 | Workspace（上节课） | Session（本节课） |
|---|---|---|
| 管理的对象 | 文件系统（磁盘上的文件） | 对话上下文（消息历史） |
| 用户感知程度 | 低——幕后组件，用户无感 | 高——直接影响对话体验 |
| 核心操作 | 读文件、写文件 | 追加消息、检索历史 |
| 典型场景 | Agent 自动生成代码并写入项目 | 多轮对话中记住用户之前的提问和上下文 |

> 🔗 **前置知识**：上节课的 Workspace 原理详见 [第 X 章：Workspace 工作空间]（← 合并时替换为锚点链接）

### 1.2 核心概念：多轮对话为什么需要「记忆」

#### 🧠 直观理解

想象一个场景：你走进一家餐厅，对服务员说「我要一份牛排，七分熟」。服务员点头记下。然后你接着说「对了，配菜换成薯条」。服务员一脸茫然地反问：「什么配菜？你刚才点了什么？」

这就是**没有记忆**的对话——对方无法建立上下文关联，每一句话都被当成孤立的、全新的请求来处理。对于 AI 助手来说，如果你不主动把之前说过的话「喂」给它，它就会在每一轮对话中表现得像一个失忆的人。

多轮对话的本质需求就是：**让模型在回答当前问题时，能够「看到」之前所有的对话内容**。

#### 📖 详细解释

大语言模型的 API 在设计上是**无状态（stateless）**的。这是一个根本性的架构特征，不是 bug：

1. 每一次 API 调用都是一个完全独立的请求 / 响应周期
2. 模型生成回复时，**只依据当前请求中携带的信息**——包括系统提示词（system prompt）、对话消息数组（messages）和当前用户输入
3. 模型本身**不存储任何跨请求的状态**——它没有「数据库」，不知道「上一个请求是谁、说了什么」
4. 下一轮请求到来时，除非你主动把上一轮的内容塞进 messages 数组，否则模型对上一轮的对话内容一无所知

这个设计可以归结为一句话：**模型的「记忆」不是模型自带的能力，而是由调用方通过「在每次请求中携带历史消息」来模拟的**。

> ⚠️ **核心认知**：理解 LLM API 的无状态性是掌握所有会话管理方案的先决条件。无论是本文的朴素 append、后续的滑动窗口、还是摘要压缩——所有这些技术的本质都是在解决同一个问题：如何高效地把历史消息塞进有限的上下文窗口。

#### 💻 代码示例：没有历史记录的对话

```python
# 模拟两轮完全独立的 API 调用——没有 chat_history 时的效果

# 第 1 轮请求的 messages（只有系统提示 + 当前问题）
messages_round_1 = [
    {"role": "system", "content": "你是企业制度助手，回答要简洁。"},
    {"role": "user", "content": "帮我记住：我买了 3 个鸡蛋"}
]
# 模型回复: "好的，已记住你买了 3 个鸡蛋。"

# 第 2 轮请求的 messages——与第 1 轮完全无关！
messages_round_2 = [
    {"role": "system", "content": "你是企业制度助手，回答要简洁。"},
    {"role": "user", "content": "我之前买了几个鸡蛋？"}
]
# 模型回复: "抱歉，我无法知道您之前买了什么。" ← 失忆！
# 原因：messages_round_2 中没有包含第 1 轮的任何信息
```

这个极简示例揭示了一个关键结论：**如果你希望在多轮对话中让模型「记住」上下文，就必须在每一轮请求的 messages 数组中，把之前所有轮次的对话内容一并发送。** 那么具体怎么做呢？答案就是接下来要介绍的 `chat_history`。

---

### 1.3 💻 Step-by-Step：从零搭建最小多轮对话系统

#### 🎯 本节实操目标

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 理解 LLM API 的无状态特性，以及「记忆」是如何通过代码模拟的
> - [ ] 使用 `while True` 循环 + `chat_history` 列表搭建最小多轮对话
> - [ ] 掌握 `set_chat_history()` 向请求注入历史消息的方法
> - [ ] 理解每轮对话结束后 append 两条消息（user + assistant）的机制
> - [ ] 利用 `demo_mode` 在无 API Key 环境下验证代码结构

#### 🏗️ 前置准备

- **Python 环境**：Python 3.10+
- **依赖库**：Agently 框架（项目依赖中已包含）
- **API Key**：DeepSeek API Key（可选——本代码内置 `demo_mode` 开关，无 Key 也能观察完整执行结构）
- **前置知识**：了解 Agently 框架中「创建 agent → 链式调用 `.start()`」的基本用法
- **代码文件**：`scripts/s01_raw_append_chat.py`

> 💡 **教学说明**：老师在本节课中采用「逐段手写 + 逐步讲解」的方式拆解这段代码。下面的 Step-by-Step 完整还原了这一过程——每一个代码片段都可以独立理解，最终拼成一段完整可运行的多轮对话程序。

---

下面我们逐段拆解。

---

#### Step 1: 环境配置与 Agent 创建

首先完成基础设置：导入依赖、配置模型连接、创建 Agent 实例。

```python
"""用 while True + append 演示最小多轮对话。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# 将项目根目录加入 sys.path，确保在任何路径下运行都能导入 agently
PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agently import Agently

# 配置模型连接——所有环境变量均有 fallback 默认值，支持无 Key 运行
Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        "model": os.environ.get("DEEPSEEK_DEFAULT_MODEL", "deepseek-v4-flash"),
        "auth": os.environ.get("DEEPSEEK_API_KEY", ""),
    },
)

# 创建 Agent 实例，通过 .system() 链式调用设定角色
agent = Agently.create_agent("raw-history-chat").system(
    "你是企业制度助手，回答要简洁，并优先基于已经确认的信息。"
)
```

| 行级解析 | |
|---|---|
| `Path(__file__).resolve().parents[4]` | 从当前脚本向上回溯 4 层目录找到项目根，保证在任何工作目录下运行都能正确导入 agently |
| `os.environ.get("KEY", "default")` | 从环境变量读取配置，给定 fallback 默认值。这种写法让同一份代码在有 Key 和无 Key 的环境下都能运行 |
| `Agently.create_agent("raw-history-chat")` | 创建一个名为 `raw-history-chat` 的 Agent 实例，名称用于日志标识 |
| `.system("你是企业制度助手...")` | 设置系统提示词（system prompt），定义 Agent 的角色和行为约束 |

> 💡 **设计洞察**：`os.environ.get()` 配合 `demo_mode` 是这个教学代码中最优雅的设计决策之一。它让同一份代码既能连接真实模型做完整演示，也能在没有 API Key 的环境下展示代码的执行流程和数据结构——老师和学生都不需要为了运行代码而额外配置密钥。

---

#### Step 2: 搭建 while 循环交互结构

接下来建立整个程序的控制骨架——一个可以持续接收用户输入的主循环。

```python
chat_history = []                          # ① 对话历史存储器（初始为空）
demo_inputs = [                            # ② 演示模式下预设的两轮问题
    "我想申请去上海出差，需要提前几天？",
    "那住宿标准是多少？"
]
demo_mode = True                           # ③ 演示模式开关

while True:
    if demo_mode:                          # ④ 演示模式：自动消费预设问题，无需人工输入
        if not demo_inputs:
            break
        user_input = demo_inputs.pop(0)
        print("用户>", user_input)
    else:                                  # ⑤ 正常模式：等待键盘输入，支持交互式测试
        user_input = input("用户> ").strip()

    if user_input.lower() in {"q", "quit", "exit"}:  # ⑥ 退出机制
        break
```

| 标记 | 设计点 | 为什么这样设计 |
|---|---|---|
| ① | `chat_history = []` | 以空列表作为历史记录的起点。后续每轮都在此列表上追加，承载整个对话的「记忆」 |
| ② | `demo_inputs` 预设两问 | 刻意设计为有上下文依赖的两个问题——第二个问题「住宿标准是多少」依赖于第一个问题建立的「去上海出差」上下文。这是一个精妙的测试案例：如果 chat_history 生效，模型应能回答上海的标准；如果不生效，模型会反问「去哪出差？」 |
| ③ | `demo_mode = True` | 教学开关。课堂演示时设为 True，学生课后自己测试时改为 False 进入交互模式 |
| ④ | `pop(0)` 取预设输入 | 从列表头部弹出元素，保证两轮预设问题按序执行。弹出后列表缩短，全部消费完后 `break` 退出循环 |
| ⑤ | `input("用户> ")` | Python 标准库的交互式输入函数。正常模式下等待用户从键盘输入内容 |
| ⑥ | `{"q", "quit", "exit"}` | 用集合（set）做成员检查，支持三种常见的退出指令 |

---

#### Step 3: chat_history 的初始化与追加 —— 核心机制

这是整段代码中**最关键**的部分——实现「让模型记住对话」的核心操作就藏在这几行代码里。

```python
    # 判断是否有可用的 API Key，决定走真实调用还是模拟输出
    if os.environ.get("DEEPSEEK_API_KEY"):
        # 🔑 真实模型调用路径
        reply = (
            agent
            .set_chat_history(chat_history)        # ⬅ 关键：将历史消息注入到本轮请求中
            .input(user_input)                     # 设置当前用户输入
            .instruct("请基于对话历史回答当前问题。")  # 额外指令：提示模型利用历史
            .output(str)                           # 指定输出类型
            .start()                               # 执行请求
        )
    else:
        # 🧪 无 Key 时的模拟路径——展示请求会携带多少条历史
        reply = f"[未调用模型] 本轮会带入 {len(chat_history)} 条历史；当前问题：{user_input}"

    print("助手>", reply)

    # 🔑 核心操作：每轮对话结束后，追加两条消息到 chat_history
    chat_history.append({"role": "user", "content": user_input})      # 追加用户刚刚说的话
    chat_history.append({"role": "assistant", "content": str(reply)})  # 追加模型刚给的回复
```

这段代码中蕴含了三个关键机制：

**机制一：`set_chat_history(chat_history)` —— 历史注入**

这是 Agently 框架提供的核心方法。它的作用是：在构造发送给模型的消息数组（messages）时，把 `chat_history` 列表中的所有条目**插入到当前用户消息之前**。这样模型在生成回复时，就能「看到」之前所有的对话记录。

第一轮时 `chat_history` 是空列表 `[]`，模型收不到任何历史——这很正常，因为确实还没有历史。第二轮时 `chat_history` 里已有第一轮的 2 条消息，模型收到后就能结合上下文来回答。

**机制二：`.instruct("请基于对话历史回答当前问题。")` —— 指令增强**

这是一条额外的提示指令（instruction），会被附加到请求中，明确告诉模型要利用传入的历史消息来回答。虽然不是严格必须的（大部分模型能自动利用上下文），但加上这条指令有两个好处：
1. 让模型更主动地回溯历史信息，尤其在对话较长时
2. 如果历史中的信息有矛盾或模糊之处，模型会优先参考历史而非凭空猜测

**机制三：每轮末尾的两次 `append` —— 记忆生长**

这是让「记忆」一层层积累的核心操作。每一轮对话结束后执行两次追加：
1. `{"role": "user", "content": user_input}` —— 保存用户刚说的话
2. `{"role": "assistant", "content": str(reply)}` —— 保存模型刚给出的回复

下一次循环回到 Step 2 开头时，`chat_history` 已经长大了一圈。如此往复，`chat_history` 就像一个不断加页的笔记本，忠实地记录着对话的每一步。

> ⚠️ **注意事项**：`role` 字段的值必须是 `"user"` 和 `"assistant"`，这是 OpenAI 兼容 API 的标准消息角色。如果写成 `"human"` / `"ai"` 或其他变体，模型可能无法正确解析消息结构，导致上下文理解异常。

---

#### Step 4: 运行验证

循环结束后，打印最终的 `chat_history` 内容，直观查看两轮对话在数据结构中的完整形态。

```python
print("\n当前 chat_history：", chat_history)
```

#### ✅ 验证结果

将 `demo_mode` 设为 `True` 后运行完整代码，以下是两种模式下的预期输出。

**模式一：有 API Key（真实模型调用）**

```
用户> 我想申请去上海出差，需要提前几天？
助手> 根据公司制度，国内出差需要提前 3 个工作日提交申请。
用户> 那住宿标准是多少？
助手> 上海属于一线城市，住宿标准为每晚 500 元以内。

当前 chat_history： [{'role': 'user', 'content': '我想申请去上海出差，需要提前几天？'}, {'role': 'assistant', 'content': '根据公司制度，国内出差需要提前 3 个工作日提交申请。'}, {'role': 'user', 'content': '那住宿标准是多少？'}, {'role': 'assistant', 'content': '上海属于一线城市，住宿标准为每晚 500 元以内。'}]
```

关键观察：第二轮回答中模型明确提到了「上海」和「住宿标准」——这说明模型确实利用了两轮之间的上下文关联。如果 `chat_history` 没有生效，模型会回答通用的住宿标准，或反问「您要去哪里出差？」。

**模式二：无 API Key（模拟输出）**

```
用户> 我想申请去上海出差，需要提前几天？
助手> [未调用模型] 本轮会带入 0 条历史；当前问题：我想申请去上海出差，需要提前几天？
用户> 那住宿标准是多少？
助手> [未调用模型] 本轮会带入 2 条历史；当前问题：那住宿标准是多少？

当前 chat_history： [{'role': 'user', 'content': '我想申请去上海出差，需要提前几天？'}, {'role': 'assistant', 'content': '[未调用模型] 本轮会带入 0 条历史；当前问题：我想申请去上海出差，需要提前几天？'}, {'role': 'user', 'content': '那住宿标准是多少？'}, {'role': 'assistant', 'content': '[未调用模型] 本轮会带入 2 条历史；当前问题：那住宿标准是多少？'}]
```

关键观察：第一轮输出显示「带入 0 条历史」，第二轮显示「带入 2 条历史」——完美验证了 `chat_history` 的逐轮增长机制。最终 `chat_history` 包含 4 条记录（2 轮 × 2 条/轮），结构清晰可读。

#### 🐛 排错指南

**常见问题 1：模型不记得上一轮说的话**

- **现象**：第二轮追问时，模型的回答与第一轮的上下文无关
- **原因**：`chat_history.append()` 放在了 `agent.input().start()` **之前**而非之后——导致本轮请求没有包含上一轮的消息
- **解决**：确保 append 操作在 `.start()` 调用结束后执行，顺序为：发起请求 → 获取回复 → append user → append assistant

**常见问题 2：role 字段不匹配导致 API 报错**

- **现象**：API 返回 `Invalid role` 或类似错误
- **原因**：role 字段写成了非标准值（如 `"human"`、`"ai"`、`"bot"`）
- **解决**：严格使用 `"user"` 和 `"assistant"`，这是 OpenAI 兼容 API 的规范要求

**常见问题 3：忘记设置环境变量导致真实调用失败**

- **现象**：设置了 `DEEPSEEK_API_KEY` 但代码仍然不调用真实模型
- **原因**：代码中通过 `os.environ.get("DEEPSEEK_API_KEY", "")` 读取——需要确认环境变量在当前 shell 会话中已正确导出
- **解决**：运行前执行 `export DEEPSEEK_API_KEY="your-key"`，或者直接使用 `demo_mode = True` 跳过真实调用

---

### 1.4 核心机制：chat_history 是如何让模型「记住」的

#### 🧠 直观理解

把 `chat_history` 想象成一个**不断加页的笔记本**。你和模型每聊一句话，就有人把这句话一字不漏地抄到笔记本上。下一轮你提问时，把整本笔记本翻到第一页，连同你的新问题，一起递给模型去读。模型读完前面所有记录后，再回答你当前的问题。

模型本身就像一个有超强阅读能力但没有记忆芯片的人——每次你给它看什么，它就能基于那个内容回答什么；但你不给它看的部分，它一概不知。**「记忆」不是模型的内置能力，而是你每次把历史材料递过去这个动作模拟出来的效果。**

#### 📖 详细解释

从技术角度看，`chat_history` 的工作原理可以用以下推导链来完整展开：

```
起点: LLM API 的每次调用都是无状态的——请求之间互不关联
  │
  ├── 第1步: 调用方在构造 API 请求时，需要把之前全部对话的消息列表
  │   作为 messages 参数的一部分发送给模型
  │   为什么？因为模型只能基于请求体中携带的信息生成回复，
  │   它无法访问外部数据库、文件系统或任何持久化存储
  │
  ├── 第2步: chat_history 就是这个消息列表的「运行时缓存」
  │   每轮对话结束时执行两次 append，保证历史信息不丢失
  │   为什么用 Python list？消息需要严格保持时间顺序，
  │   而列表天然支持按序追加（append）和遍历
  │
  ├── 第3步: 下一轮请求中，set_chat_history() 把 chat_history
  │   的内容注入到 API 请求体的 messages 数组
  │   为什么通过框架方法而不是手动拼接？
  │   手动构造 messages 数组容易遗漏字段、弄错顺序；
  │   框架方法封装了这些细节，保证格式正确
  │
  └── 结论: 模型收到 = 完整对话历史 + 当前新问题
       → 在完整上下文基础上生成回复
       → 外部表现为「模型记住了之前说过的话」
```

#### 💻 代码示例：messages 数组的实际构造

以下对比展示了「有 chat_history」和「没有 chat_history」两种情况下，API 请求中 messages 数组的实际形态：

```python
# ===== 情况 A：没有 chat_history（每轮独立，模型会失忆）=====

# 第 1 轮请求的 messages
messages_round_1 = [
    {"role": "system", "content": "你是企业制度助手，回答要简洁。"},
    {"role": "user",   "content": "出差需要提前几天？"}
]
# 模型回复: "需要提前 3 个工作日。"
# messages 中没有任何历史信息——本轮是全新的开始

# 第 2 轮请求的 messages——与第 1 轮完全隔离
messages_round_2 = [
    {"role": "system", "content": "你是企业制度助手，回答要简洁。"},
    {"role": "user",   "content": "住宿标准是多少？"}
]
# 模型回复: "住宿标准因城市和级别而异，请提供具体信息。"
# 模型不知道要去上海出差——因为第 1 轮的内容没有传进来！


# ===== 情况 B：有 chat_history（历史消息被注入，模型有记忆）=====

# 第 1 轮请求的 messages（chat_history 为空，和情况 A 一样）
messages_r1_with_history = [
    {"role": "system", "content": "你是企业制度助手，回答要简洁。"},
    {"role": "user",   "content": "出差需要提前几天？"}
]
# 模型回复后: chat_history = [
#     {"role": "user",      "content": "出差需要提前几天？"},
#     {"role": "assistant", "content": "需要提前 3 个工作日。"}
# ]

# 第 2 轮请求的 messages（chat_history 中的 2 条被注入到前面）
messages_r2_with_history = [
    {"role": "system",    "content": "你是企业制度助手，回答要简洁。"},
    {"role": "user",      "content": "出差需要提前几天？"},       # ⬅ chat_history[0]
    {"role": "assistant", "content": "需要提前 3 个工作日。"},     # ⬅ chat_history[1]
    {"role": "user",      "content": "住宿标准是多少？"}           # ⬅ 当前新输入
]
# 模型回复: "根据公司制度，出差住宿标准为每晚 500 元。"
# 模型能看到完整的上下文：前面问了「出差」→ 当前追问「住宿标准」
```

注意对比两种情况下 `messages_r2_with_history` 与 `messages_round_2` 的区别——前者多了两条来自 `chat_history` 的消息。正是这两条消息，让模型从「失忆」变成了「记住」。

#### 🔄 请求流程可视化

以下用 ASCII 流程图还原整个请求-追加的循环过程：

```
第 1 轮对话 ── chat_history = []
    │
    ├── 用户输入: "出差需要提前几天？"
    │
    ├── API 请求的 messages:
    │   [{system}, {user: "出差需要提前几天？"}]
    │   携带历史消息: 0 条
    │
    ├── 模型回复: "需要提前 3 个工作日"
    │
    └── append 操作后
        chat_history = [
          {user: "出差需要提前几天？"},
          {assistant: "需要提前 3 个工作日"}
        ]  ← 共 2 条
         │
         ▼
第 2 轮对话 ── chat_history = [user①, assistant①]
    │
    ├── 用户输入: "住宿标准是多少？"
    │
    ├── API 请求的 messages:
    │   [{system},
    │    {user: "出差需要提前几天？"},       ⬅ 来自 chat_history
    │    {assistant: "需要提前 3 个工作日"},  ⬅ 来自 chat_history
    │    {user: "住宿标准是多少？"}]          ⬅ 当前输入
    │   携带历史消息: 2 条
    │
    ├── 模型回复: "住宿标准为每晚 500 元"
    │   ↑ 模型看到「出差」上下文，给出针对性回复
    │
    └── append 操作后
        chat_history = [
          {user: "出差需要提前几天？"},
          {assistant: "需要提前 3 个工作日"},
          {user: "住宿标准是多少？"},
          {assistant: "住宿标准为每晚 500 元"}
        ]  ← 共 4 条
         │
         ▼
第 3 轮 ── chat_history 已有 4 条 ……（持续增长）
```

#### 📊 各轮请求中 chat_history 的变化

| 轮次 | 请求前 chat_history 长度 | 本轮请求携带的历史消息 | 本轮新增 | 请求后 chat_history 长度 |
|---|---|---|---|---|
| 第 1 轮 | 0 条 | 无 | user① + assistant① | 2 条 |
| 第 2 轮 | 2 条 | user①, assistant① | user② + assistant② | 4 条 |
| 第 3 轮 | 4 条 | user①, assistant①, user②, assistant② | user③ + assistant③ | 6 条 |
| 第 N 轮 | (N - 1) × 2 条 | 前 N - 1 轮的全部消息 | userN + assistantN | N × 2 条 |

> 💡 **核心洞见**：`append` 不只是一个简单的 `list.append()` 操作——它是**把「对话时间线」编译进「API 请求结构」的桥梁**。每一轮请求携带的都是该时间点之前的完整对话快照。理解这一点，就能理解为什么 chat_history 会随着对话增长而持续膨胀——每条消息都被永久保留，从未删除。

> 🔗 **伏笔**：这个朴素的 append 方案在第 1-5 轮时完全可工作，但在长对话中会暴露致命问题——`chat_history` 无限膨胀，每次请求携带的 token 数线性增长，最终超出模型的上下文窗口限制。下一节（M02）将深入剖析这个问题的具体表现和代价。

## 二、原始append的代价：结构化输出与上下文膨胀

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 识别朴素 append 方案在结构化输出场景下的三种典型问题
> - [ ] 区分「原始对话记录」与「本轮 prompt 窗口」这两个关键概念
> - [ ] 判断哪些输出字段应该进入 chat_history，哪些不应该
> - [ ] 理解为什么业务逻辑不应该手动管理会话历史的字段提取

### 2.1 回顾：M01 的朴素方案已埋下隐患

#### 🧠 直观理解

M01 中我们用 `chat_history.append()` 实现多轮对话，就像往一本笔记本里不断粘贴对话记录。这个做法直观、能跑——但它只管「记下来」，不管「该记什么」和「记了多少」。当模型的输出不只是自然语言文本，而是包含结构化字段（如 pre_thinking、reply）时，直接把整个响应对象塞进历史，就会引发连锁问题。

#### 📖 详细解释

在 M01 的最简方案中，`chat_history` 是一个 `[{role, content}, ...]` 列表，每轮追加两条记录（user + assistant）。这个方案在以下场景能正常工作：

- 模型只输出纯文本
- 对话轮次很少（3-5 轮）
- 单个用户、单个执行线程

但一旦进入真实业务场景，模型输出会变复杂。以 Agently 为例，我们可能为 agent 配置 output schema：

```python
output_schema = {
    "pre_thinking": ("str", "在回答前先分析用户意图"),
    "reply": ("str", "给用户的正式回复"),
}
```

此时 `agent.start()` 返回的不再是字符串，而是一个字典。M01 里的 `chat_history.append({"role": "assistant", "content": reply})` 就会出问题——因为 `reply` 现在是字典，而 `chat_history` 的 `content` 字段在语义上预期是自然语言文本。

> 💡 **核心洞见**：M01 中 `.output(str)` 是保证返回值类型的关键配置。但一旦需要结构化输出（如同时获取 pre_thinking 和 reply），就不能再使用 `.output(str)`——这意味着输出类型从简单字符串变成了复杂字典，而朴素 append 方案对此完全没有设计。

#### 💻 代码示例

先运行 M01 的观察代码，确认朴素方案下的历史形态：

```python
# 文件名: s02_prompt_growth_and_cut.py
# 功能: 继续 s01 的 chat_history，观察 append 后的历史形态

from __future__ import annotations


def main() -> None:
    # 脚本单独运行时没有 notebook 的上一个执行块，所以这里复现 s01 的结果。
    chat_history = [
        {"role": "user", "content": "我想申请去上海出差，需要提前几天？"},
        {"role": "assistant", "content": "[未调用模型] 本轮会带入 0 条历史；当前问题：我想申请去上海出差，需要提前几天？"},
        {"role": "user", "content": "那住宿标准是多少？"},
        {"role": "assistant", "content": "[未调用模型] 本轮会带入 2 条历史；当前问题：那住宿标准是多少？"},
    ]

    print("当前历史条数：", len(chat_history))
    print(chat_history)


if __name__ == "__main__":
    main()
```

| 行号 | 代码 | 解释 |
|---|---|---|
| 8-13 | `chat_history = [...]` | 两轮对话产生 4 条记录（2 user + 2 assistant），线性增长 |
| 15 | `len(chat_history)` | 输出 `当前历史条数：4`，验证两轮对话 = 4 条的规律 |
| 16 | `print(chat_history)` | 观察每条记录的 `role` 和 `content` 字段——目前还是干净的纯文本 |

> 💡 **核心洞见**：仅两轮对话就产生 4 条历史记录。如果继续聊下去，每 N 轮对话产生 2N 条记录。而且目前我们只存了纯文本——还没有给 agent 加 `pre_thinking` 这样的结构化输出字段，问题还没暴露。

---

### 2.2 问题一：结构化输出污染

#### 🎯 目标

演示当 agent 的 output schema 包含多个字段（如 `pre_thinking` + `reply`）时，直接将整个输出对象塞入 `chat_history` 会造成历史记录被非对话内容污染——这是朴素 append 方案遇到的第一个硬伤。

#### 🏗️ 前置准备

在 M01 的 agent 基础上，增加 output schema 中的 `pre_thinking` 字段，让模型在正式回答前先做一次预思考。

```python
# 给 agent 配置结构化输出
agent = Agently.create_agent("structured-chat").system(
    "你是企业制度助手，回答要简洁，并优先基于已经确认的信息。"
)

# 关键变化：output schema 包含两个字段
# 注意：这里不能用 .output(str) 了，因为需要同时获取两个字段
agent.output_schema({
    "pre_thinking": ("str", "分析用户意图和已有信息的关联"),
    "reply": ("str", "给用户的正式答复"),
})
```

> ⚠️ **注意事项**：一旦配置了 `output_schema`，`agent.start()` 返回的是字典而非字符串。M01 中的 `.output(str)` 和这里的 `output_schema` 是互斥的——你只能选一个。需要结构化输出时就必须面对「返回值是字典」这个事实。

#### 💻 Step-by-Step

**Step 1: 观察朴素 append 后的历史形态（M01 的延续）**

上一步代码输出显示，两轮对话后 `chat_history` 有 4 条记录。这是纯文本场景下的「正常」状态——每条 content 都是可读的自然语言。

**Step 2: 引入 pre_thinking 后的输出结构变化**

当 agent 配置了 output schema 后，`agent.start()` 返回的不是字符串，而是包含 `pre_thinking` 和 `reply` 两个字段的字典：

```python
# 引入 pre_thinking 后的实际返回值
reply = agent.set_chat_history(chat_history).input(user_input).start()

print(type(reply))   # 输出: <class 'dict'>
print(reply)
# 输出类似：
# {
#     "pre_thinking": "用户询问出差申请天数，我需要确认这是首次询问...",
#     "reply": "根据公司差旅制度，通常需要提前3-5个工作日提交出差申请。"
# }
```

> ⚠️ **注意事项**：此时 `reply` 是一个字典，而 `chat_history` 中 `content` 字段在语义上应该是字符串。如果直接把字典 append 进去，虽然 Python 不会立即报错（列表可存任何类型），但后续传给模型 API 时会因类型不匹配而失败。

**Step 3: 用 str() 强行字符串化——污染的开始**

发现字典不能直接使用后，最常见的本能补救是 `str(reply)`：

```python
# 语言本能：用 str() 转换
chat_history.append({"role": "user", "content": user_input})
chat_history.append({"role": "assistant", "content": str(reply)})
#                                           ^^^^^^^^ 强行字符串化
```

这段代码能跑——但让我们看看 `chat_history` 实际存储的内容。打印 `chat_history[-1]`：

```python
# chat_history 中最后一条 assistant 记录的实际内容：
{
    "role": "assistant",
    "content": "{'pre_thinking': '用户询问住宿标准，需要结合之前确认的出差申请...', 'reply': '根据公司差旅制度，上海住宿标准为每晚不超过500元...'}"
}
```

可以看到：

- `pre_thinking`（模型的「草稿纸」）被永久存入了对话历史
- 整个字典变成了 Python 字面量字符串格式（带引号、花括号、键名）
- 模型下一轮会看到一段 Python 字典文本而非自然语言——它会困惑「上一轮我到底回复了什么」

```python
# 再跑一轮，chat_history 持续被污染
# 第二轮追加后，打印整个 chat_history：
print(chat_history)
# [
#   {"role": "user", "content": "我想申请去上海出差，需要提前几天？"},
#   {"role": "assistant", "content": "{'pre_thinking': '...', 'reply': '通常需提前3-5天'}"},
#   {"role": "user", "content": "那住宿标准是多少？"},
#   {"role": "assistant", "content": "{'pre_thinking': '...', 'reply': '住宿标准为...'}"},
# ]
```

> ⚠️ **注意事项**：随着消息不断往 chat_history 里增加，我们实际记录的对话信息已经和「我们认知中应该留存的信息」完全不同了。正常的多轮对话只应该保留用户说了什么和模型回了什么（正式回复文本），而不是把 pre_thinking 这种模型的中间推理也一起存进去。信息流里的内容被结构化数据污染了。

---

#### 🐛 排错实录：reply 被结构化输出「锁死」的完整调试过程

**❌ 错误写法**

老师在 M01 代码的基础上，增加了 output_schema 并去掉 `.output(str)`，试图让 agent 同时返回 pre_thinking 和 reply。但代码运行后，发现 reply 的值被「锁死」了——每次输出的都是上一次的旧结果，而不是对应当前输入的新结果。老师切换回 M01 的早期版本逐一排查。

```python
# 问题代码：output_schema 和 chat_history 的交互导致 reply 状态异常
agent = Agently.create_agent("structured-chat").system(
    "你是企业制度助手，回答要简洁。"
)

# 配置了 output_schema，但没有处理好返回值类型的变化
agent.output_schema({
    "pre_thinking": ("str", "分析用户意图"),
    "reply": ("str", "正式回复"),
})

chat_history = []
demo_inputs = ["我想申请去上海出差，需要提前几天？", "那住宿标准是多少？"]

for user_input in demo_inputs:
    print("用户>", user_input)

    # 注意：这里没有 .output(str)，返回的是 dict
    reply = (
        agent
        .set_chat_history(chat_history)
        .input(user_input)
        .instruct("请基于对话历史回答当前问题。")
        .start()
    )

    # 第一步：agent 的 reply 这里打印出来是空的
    # 因为 output_schema 下 start() 返回的是 dict，直接打印看不到预期内容
    print("助手>", reply)

    # 直接 append dict——这是 bug 的起点
    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "assistant", "content": reply})  # reply 是 dict！
```

**🚨 报错与异常表现**

代码运行后出现以下异常：

1. **第一轮**：`print("助手>", reply)` 输出的内容似乎「不对」——不是自然语言文本，而是一个字典对象
2. **第二轮**：`reply` 的值被锁定，输出的是上一轮的内容，对应当前 user_input 的新回复没有正确返回
3. **持续异常**：继续追加轮次后，chat_history 中混入了字典对象，后续传给模型的输入变得不可读

具体来说，当老师尝试打印 `prompt data`（传给模型的完整 prompt）时，发现了问题：第一步时 chat_history 中的内容看似正常，但第二步时 assistant 的内容已经是 `{'pre_thinking': '...', 'reply': '...'}` 这种字典格式——这跟模型应该看到的自然语言对话完全不匹配。

**🔍 原因分析**

1. **根因**：`agent.start()` 在配置了 `output_schema` 后，返回值类型从 `str` 变成了 `dict`。M01 中 `.output(str)` 强制了字符串返回，但 output_schema 和 `.output(str)` 是互斥的配置。
2. **直接把 dict append 到 chat_history**：Python 不报错是因为列表可以容纳任何类型，但模型 API 期望 `content` 是字符串——这导致类型不一致，进而影响模型的上下文理解。
3. **chat_history 被污染后影响后续请求**：第二轮请求时，agent 从 chat_history 中读取到了字典格式的 assistant content，模型无法正确理解「上一轮我回复了什么」，于是输出的 reply 出现了异常（被锁死）。

**✅ 正确写法——手动提取 reply 字段**

老师切换回早期版本后，逐段排查问题，最终找到了修复方式：

```python
# 修复：从 reply 字典中提取特定字段
for user_input in demo_inputs:
    print("用户>", user_input)

    reply = (
        agent
        .set_chat_history(chat_history)
        .input(user_input)
        .instruct("请基于对话历史回答当前问题。")
        .start()
    )

    # 打印完整 reply 可以看到所有字段
    print("完整返回:", reply)
    # 但只把 reply["reply"] 存入 chat_history
    print("助手>", reply["reply"])

    # 修复：只保存用户看到的正式回复文本
    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "assistant", "content": reply["reply"]})
    #                                            ^^^^^^^^^^^^^ 只取需要的那一个字段
```

**📝 经验总结**

1. **output_schema 改变了函数的返回类型**，但调用方（chat_history.append）对此毫不知情——这是典型的「契约变更未传播」问题。
2. **str() 不是银弹**。`str(reply)` 虽然能让代码不报错，但它把 pre_thinking、tool_calls、metadata 等所有不该出现在对话历史中的内容都序列化进去了。
3. **手动提取字段能临时解决问题**，但它引出了下一个更大的问题：如果 output schema 有 5 个、10 个字段，每次 append 都需要知道「哪个字段才是用户看到的回复」——这就是业务逻辑侵入。
4. **排查技巧**：当遇到「reply 锁死」这类问题时，先检查 chat_history 中的数据类型是否与预期一致——很多时候问题不在模型调用，而在给模型的数据本身就已经坏了。

---

#### 📊 结构化字段保留表：哪些该进历史、哪些不该进

对于配置了 output schema 的 agent，每次请求返回的字典中可能包含多种字段。下表给出明确的保留/排除规则：

| 字段 | 为什么会产生 | 该不该保留在 chat_history | 原因与后果 |
|---|---|---|---|
| `reply` | output schema 中定义的正式回复字段 | ✅ 保留 | 这是用户实际看到的回复内容，是多轮对话的核心信息载体 |
| `pre_thinking` | 模型在正式回答前的推理过程 | ❌ 排除 | 只是模型的「草稿纸」，用户不需要看到；下一轮模型也不需要读取上一轮的思考过程——它应该重新推理 |
| `tool_calls` | 模型决定调用工具时的输入参数 | ❌ 排除 | 工具调用的结果应以自然语言形式融入 reply，而非保留原始 JSON |
| `tool_results` | 工具返回的原始数据 | ❌ 排除 | 大段原始数据会严重膨胀上下文；有需要时应用专门的引用机制 |
| `metadata` | 请求耗时、token 用量等 | ❌ 排除 | 纯技术元数据，与对话内容无关 |
| `confirmed_data` | 已确认的结构化业务信息（如预算、日期、范围） | ⚠️ 视情况 | 如果下游需要，应单独用结构化字段管理，而非混在自然语言历史中 |

> 💡 **核心洞见**：chat_history 不是垃圾桶——不要把所有输出字段都往里倒。历史中应该只保留「用户说的话」和「模型回的话」。其他结构化信息（思考过程、工具调用、元数据）要么丢弃，要么通过专门的会话状态字段单独管理。这个认知直接决定了后续 Session 模块的数据结构设计。

---

### 2.3 问题二：业务逻辑侵入

#### 🧠 直观理解

在上面「正确写法」中，我们手动写了 `chat_history.append({"role": "assistant", "content": reply["reply"]})`。看起来只是多敲了几个字符，但如果你的系统里有 10 种 agent，每种 agent 的 output schema 不同，你就需要在每次 append 时都记住「这个 agent 的输出里，哪个字段才是用户应该看到的回复」。这就像在每扇门上手动贴「推」还是「拉」——门少的时候没问题，门多了迟早贴错。

#### 📖 详细解释

**为什么手动提取字段不可持续？**

先看三种典型 agent 的 output schema 差异：

```
Agent A（差旅助手）:
    output_schema: {"pre_thinking": ..., "reply": ...}
    要提取的字段: reply["reply"]

Agent B（合同审查）:
    output_schema: {"risk_analysis": ..., "clause_suggestions": ..., "final_answer": ...}
    要提取的字段: reply["final_answer"]

Agent C（运维排障）:
    output_schema: {"diagnosis": ..., "solution_steps": ..., "output": ...}
    要提取的字段: reply["output"]
```

你会发现：**每种 agent 的「用户可见回复」字段名都不同**。如果让业务代码手动管理这个映射关系：

1. **提取逻辑散落在各处**：每增加一种 agent，需要修改所有涉及 `chat_history.append()` 的地方
2. **违反开闭原则**：对扩展开放（加新 agent），但对修改也开放（要改已有代码）
3. **无法统一抽象**：如果你试图写一个 `smart_append(chat_history, reply)` 的通用函数，它必须知道 reply 的内部结构——而 reply 的结构因 agent 而异
4. **重构成本高**：当某天你决定「chat_history 不应该由业务代码手动维护」时，所有散落的 append 逻辑都需要重构

#### 💻 代码示例

```python
# 演示：三种不同 agent 需要三种不同的字段提取逻辑
# 这就是业务逻辑侵入——历史管理逻辑和业务代码耦合在一起

# Agent 1: 差旅助手
travel_agent = Agently.create_agent("travel")
travel_agent.output_schema({
    "pre_thinking": ("str", "分析出差场景和已有信息"),
    "reply": ("str", "正式回复"),                     # ← 字段名是 "reply"
})

# Agent 2: 合同审查
contract_agent = Agently.create_agent("contract")
contract_agent.output_schema({
    "risk_analysis": ("str", "风险评估"),
    "clause_suggestions": ("str", "条款建议"),
    "final_answer": ("str", "总结回答"),              # ← 字段名是 "final_answer"
})

# Agent 3: 运维排障
debug_agent = Agently.create_agent("debug")
debug_agent.output_schema({
    "diagnosis": ("str", "问题诊断"),
    "solution_steps": ("str", "解决步骤"),
    "output": ("str", "面向用户的输出"),              # ← 字段名是 "output"
})

# 业务逻辑被迫维护 agent 类型 -> 字段名的映射
def append_to_history(chat_history, user_input, reply, agent_type):
    """每次 append 都要根据 agent 类型做分支——业务逻辑入侵历史管理"""
    chat_history.append({"role": "user", "content": user_input})

    if agent_type == "travel":
        content = reply["reply"]
    elif agent_type == "contract":
        content = reply["final_answer"]
    elif agent_type == "debug":
        content = reply["output"]
    else:
        raise ValueError(f"未知的 agent 类型: {agent_type}")

    chat_history.append({"role": "assistant", "content": content})

# 问题肉眼可见：
# 1. 每新增一种 agent，这个函数就要加一个 elif
# 2. 调用方必须传 agent_type——业务代码要知道自己用的是哪种 agent
# 3. 未来如果有 agent 需要保留多个字段到历史中，这个函数还得改签名
```

> ⚠️ **注意事项**：这个 `append_to_history` 函数只是冰山一角。真实业务中，管理历史的代码还会分散在路由层、中间件、回调函数中——只要有一个地方忘了按 agent_type 做分支判断，就会产生 bug。而且这种 bug 往往很隐蔽：代码能跑，但 chat_history 里混入了不该有的内容，要过好几轮对话才会发现模型变「笨」了。

> 💡 **核心洞见**：这个问题的本质是**会话历史的管理职责不应该由业务代码承担**。业务代码应该只关心「用户问了什么」和「模型答了什么」，至于「怎么把答的内容正确存入历史」——这个职责应该交给一个专门的会话管理层。这直接指向了后续 M04-M05 中 Session 模块的设计。

---

### 2.4 问题三：上下文无限膨胀

#### 🧠 直观理解

想象一场持续了 30 轮的对话。朴素 append 方案会把 60 条记录（30 user + 30 assistant）全部塞进下一轮 prompt。如果每条记录平均 200 token，那就是 12,000 token——加上 system prompt（2000 token）、工具定义（3000 token）、材料引用（1000 token），轻轻松松逼近甚至突破模型的上下文窗口上限。更糟的是，如果历史里还混入了 `pre_thinking`（通过 `str(reply)` 字符串化保留），token 消耗还会翻倍。**对话越长，模型能用来「思考」的空间越少。**

#### 📖 详细解释

**为什么线性增长不可持续？**

以典型的 128K 上下文窗口为例，看似很大，但实际可用空间需考虑：

1. **system prompt**：企业级 system prompt 通常 500-3000 token
2. **工具定义**：10+ 个工具的函数签名和描述，可能占 2000-8000 token
3. **材料引用**：合同内容、政策文档、知识库片段的摘要或引用
4. **对话历史**：这是唯一会持续增长的部分，且增长没有上限
5. **输出预留**：模型生成回复也需要占用窗口——通常是输入 token 的 20%-50%

**数值模拟表：对话轮次 vs 上下文消耗**

| 对话轮次 | chat_history 条数 | 纯文本 token（估算） | 含 pre_thinking token（估算） | 占总窗口比例（128K） |
|---|---|---|---|---|
| 第 1 轮 | 2 条 | ~200 | ~400 | 0.3% |
| 第 5 轮 | 10 条 | ~1,000 | ~2,000 | 1.6% |
| 第 10 轮 | 20 条 | ~2,000 | ~4,000 | 3.1% |
| 第 20 轮 | 40 条 | ~4,000 | ~8,000 | 6.3% |
| 第 30 轮 | 60 条 | ~6,000 | ~12,000 | 9.4% |
| 第 50 轮 | 100 条 | ~10,000 | ~20,000 | 15.6% |
| 第 100 轮 | 200 条 | ~20,000 | ~40,000 | 31.3% |
| 第 200 轮 | 400 条 | ~40,000 | ~80,000 | 62.5% |

> ⚠️ **注意事项**：上表仅估算对话历史部分的消耗。加上 system prompt 和工具定义后，100 轮对话就能吃掉 128K 窗口的 50% 以上。如果使用了 `str(reply)` 保留了 pre_thinking 的字典序列化文本，消耗翻倍——200 轮就能逼近 80%。模型此时只能看到最近几轮的内容，早期对话中确认的关键约束（预算、日期、审批条件）会被自然遗忘。

**上下文膨胀的可视化**

```
Token 消耗
  ▲
  │                                          ╔═══════════════╗
80K├─────────────────────────────────────────╣ 含 pre_thinking ║
  │                                      ████║ （翻倍增长）    ║
  │                                  ████    ╚═══════════════╝
60K├─────────────────────────────████
  │                          ████
  │                      ████          ╔═══════════════╗
40K├─────────────────████              ║ 纯文本          ║
  │              ████                  ║ （线性增长）     ║
  │          ████                      ╚═══════════════╝
20K├─────████
  │  ████
  │████
  └──┼────┼────┼────┼────┼────┼────┼────▶ 对话轮次
     0   25   50   75  100  125  150  175

虚线：system prompt + 工具定义占用（约 5K-10K token），不计入上图
```

#### 💻 代码示例

```python
# 文件名: 上下文膨胀模拟
# 功能: 展示 chat_history 条数随对话轮次的线性增长趋势

def simulate_context_growth(max_turns: int = 30) -> None:
    """模拟多轮对话中 chat_history 的线性增长"""
    chat_history = []

    print(f"{'轮次':>6} | {'条数':>6} | {'增量':>6} | {'纯文本 token':>12} | {'含预思考 token':>14}")
    print("-" * 60)

    for turn in range(1, max_turns + 1):
        # 每轮追加两条记录
        chat_history.append({"role": "user", "content": f"第{turn}轮的问题"})
        chat_history.append({"role": "assistant", "content": f"第{turn}轮的回答"})

        pure_text_tokens = len(chat_history) * 100        # 假设每条 100 token
        with_prethink_tokens = pure_text_tokens * 2        # 含 pre_thinking 翻倍

        if turn <= 10 or turn % 10 == 0:
            print(
                f"{turn:>6} | {len(chat_history):>6} | {'+2':>6} "
                f"| {pure_text_tokens:>10,} | {with_prethink_tokens:>12,}"
            )

    print(f"\n📊 {max_turns} 轮对话后的统计：")
    print(f"  chat_history 总条数：{len(chat_history)}")
    print(f"  纯文本 token 估算：~{len(chat_history) * 100:,}")
    print(f"  含 pre_thinking 估算：~{len(chat_history) * 200:,}")
    print(f"  假设上下文窗口 128K，对话历史已占用 "
          f"{len(chat_history) * 100 / 128000 * 100:.1f}%（纯文本）")

    # 关键观察：即使纯文本，60 轮后就超过 6000 token
    # 加上 system prompt、工具定义后，留给模型的思考空间已大幅缩水


if __name__ == "__main__":
    simulate_context_growth(30)
```

> ❓ **常见疑问**：「模型不是有 128K 上下文吗？几百条消息怕什么？」
>
> 128K 是所有内容的共享预算。system prompt、工具定义、材料引用都要从中分。而且上下文越长，模型的注意力越分散——这被称为「Lost in the Middle」现象：模型对长文本中间部分的信息提取能力会显著下降。更现实的问题是成本：API 按 token 计费，带着 100 轮历史每次请求多花几万 token，一个月下来成本很可观。

---

### 2.5 关键概念区分：原始对话记录 vs 本轮 prompt 窗口

#### 🧠 直观理解

**原始对话记录**就像一部完整的通话录音——从「喂？」到「再见」，一字不差，永久存档。**本轮 prompt 窗口**则是你在打电话前快速翻看的便利贴——只记下对方上次说了什么、你这次要确认什么。把整部录音每次通话都重放一遍，既浪费时间（token），又干扰思考（注意力分散）。

#### 📖 详细解释

这个区分是整个 Session 设计理念的基石。把两个概念讲清楚，后续 M04-M07 的设计决策才有理解的基础。

| 维度 | 原始对话记录 | 本轮 prompt 窗口 |
|---|---|---|
| **对应数据结构** | `full_context` | `context_window` |
| **是什么** | 按时间顺序保存的完整 user/assistant 消息流水 | 本轮请求中实际传给模型的那一组消息 |
| **回答什么问题** | 「之前发生过什么」 | 「本轮模型应该看什么」 |
| **数据范围** | 从对话开始到现在的所有消息（完整流水） | 经过裁剪、压缩、重组后的精华内容 |
| **操作方式** | 默认只追加（append-only，事实记录） | 每轮都可以重新组装（裁剪、压缩、重排、摘要替换） |
| **典型内容** | 所有 user + assistant 消息原文 | 最近 N 条消息 + memo（关键约束摘要）+ 材料引用 |

**为什么必须分开？——架构对比**

```
朴素方案（M01/M02 中 — 两个概念混为一体）：
┌─────────────────────────────────────────────────────────┐
│  chat_history（一个列表，既是记录又是输入）                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │ user: 你好                                        │  │
│  │ assistant: 你好！有什么可以帮你？                    │  │
│  │ user: 出差申请要提前几天？                          │  │
│  │ assistant: {'pre_thinking': '...',                  │  │
│  │              'reply': '通常3-5天...'}                │  │
│  │                                        ← 结构污染！  │  │
│  │ user: 那住宿标准呢？                                │  │
│  │ ...（持续增长，直到突破上下文窗口）                  │  │
│  └───────────────────────────────────────────────────┘  │
│  问题：1) 污染 2) 侵入 3) 膨胀                            │
└─────────────────────────────────────────────────────────┘

分离方案（M04 及之后 — Session 模块的核心设计）：
┌──────────────────────────┐    ┌──────────────────────────┐
│  full_context            │    │  context_window          │
│  （完整原始记录）          │    │  （本轮 prompt 窗口）      │
│  ┌────────────────────┐  │    │  ┌────────────────────┐  │
│  │ user: 你好          │  │    │  │ user: 住宿标准？    │  │
│  │ assistant: 你好！   │  │    │  │ assistant: 可报销   │  │
│  │ user: 出差几天？    │  │───▶│  │ memo: 预算20万      │  │
│  │ assistant: 3-5天   │  │    │  │ ref: policy-v2      │  │
│  │ user: 住宿标准？    │  │    │  └────────────────────┘  │
│  └────────────────────┘  │    │  经过 handler 裁剪/压缩    │
│  只追加，不修改            │    │  只包含本轮需要的内容        │
└──────────────────────────┘    └──────────────────────────┘
```

> 💡 **核心洞见**：**原始对话记录是事实记录，本轮 prompt 窗口是模型输入。两者长期混成一个列表，后面就只能靠粗暴裁剪补救。** 分开之后，full_context 保留完整流水（可审计、可回溯），context_window 按需组装（可控、高效）。这正是后续 Session 模块的核心设计思想。

| 对比维度 | ❌ 朴素 append（混在一起） | ✅ Session 分离（分开管理） |
|---|---|---|
| 代码侵入 | 业务代码手动管理字段提取 | Session 自动处理，业务无感知 |
| 结构污染 | pre_thinking 等冗余字段混入历史 | full_context 干净记录，context_window 按需挑选 |
| 上下文增长 | 线性无上限增长 | handler 主动裁剪/压缩 |
| 可审计性 | 历史被污染后难以追溯 | full_context 保留完整原始记录 |
| 多 agent 适配 | 每种 agent 需单独适配 | Session 统一管理，agent 无差异 |

---

### 2.6 本节小结

M02 从 M01 的朴素 append 出发，逐个暴露了三条「此路不通」的信号：

| 问题 | 现象 | 根因 | 指向的解决方案 |
|---|---|---|---|
| 结构化输出污染 | pre_thinking 等非对话字段混入 chat_history | output schema 改变了返回类型，str() 序列化了所有字段 | Session 需要区分「记录什么」和「输入什么」 |
| 业务逻辑侵入 | 每次 append 需要手动选择提取哪个字段 | 历史管理逻辑散落在业务代码中，无法统一抽象 | Session 需要从业务代码中接管历史管理职责 |
| 上下文膨胀 | chat_history 线性增长，30+ 轮后逼近窗口上限 | 每轮带完整历史，没有裁剪机制 | Session 需要提供裁剪/压缩入口（handler） |

这三个问题共同指向同一个结论：**`chat_history.append()` 可以是起点，但不能是终点。** 工程化的多轮对话系统需要一个独立的 Session 层来负责：历史完整记录（full_context）、本轮 prompt 窗口裁剪（context_window）、上下文策略执行（handler 管线）。

> 🔗 **下一步**：以上三个问题还只是「单人单线程」场景下的麻烦。如果多个用户共享同一个 agent 对象会怎样？请看 M03——问题会从「单人」升级到「多人并发」，Session 独立化的必要性将更加紧迫。

## 三、共享 Agent 状态风险：多用户上下文混乱

### 3.1 场景切换：从命令行到线上服务

在上一节中，我们讨论的是**单用户命令行场景**下的三个问题——上下文污染、代码侵入、存储膨胀。那些问题发生在一个用户与一个 agent 长时间对话的情境中。

但在真实的生产环境中，你的 agent 几乎不可能只服务一个人。它通常被部署为一个线上服务，通过 FastAPI 接口、企业微信 Gateway、Slack Bot 或网页端，同时接收来自**几十、几百甚至上千个不同用户**的请求。每一个请求都是一个独立的人在与你的系统进行交互。

这时，上一节讨论的问题会被成倍放大，而且会出现一个全新的问题：**多用户的上下文在同一个 agent 中互相串扰**。

> 🔗 **前置知识**：上一节 M02 分析了单用户场景下原始 append 的三个代价——上下文污染、代码侵入、存储膨胀。

---

### 3.2 🧠 直观理解：共享 Agent 为何会"串话"

想象这样一个场景：

你是一家公司的前台接待员（agent）。你的工作是回答来访者的问题。每天都有很多人来找你：A 客户问"我的预算 20 万"，B 客户问"我的预算是多少？"，C 客户问"任务状态是什么？"。

如果你把所有来访者的对话都记在**同一本笔记本**上，混在一起，会发生什么？

当 B 客户问"我的预算是多少？"时，你在笔记本上翻到的可能是 A 客户说的"我的预算是 20 万"——于是你对 B 说"你的预算是 20 万"。但实际上 B 从未告诉过你他的预算。

这就是**上下文紊乱（Context Confusion）**：多个用户在同一个上下文空间里留下了各自的对话痕迹，导致模型无法判断某条信息到底属于谁。

> 💡 **核心洞见**：共享 agent 对象等于把多个人的记忆混在一个脑子里——这人没法不"疯"。

---

### 3.3 📖 详细解释：上下文紊乱的技术根源

#### 问题本质

当 agent 作为一个**全局单例对象**运行时，它内部维护的 `chat_history`（对话记录）是一个**共享的列表**。所有用户的输入都被 `append` 进同一个列表里，没有做任何来源标记或隔离。

具体来说，问题的技术根因有三个层面：

**第一个层面：数据结构层面。** 在代码中，agent 内部的 `context_window` 或 `chat_history` 本质上就是一个 `list[dict]`。当你调用 `add_chat_history()` 时，代码只是往这个列表末尾追加一条 `{"role": "user", "content": "..."}` 记录。不管这条消息来自哪个用户、哪个渠道、哪个会话——它都被塞进了同一个列表。

**第二个层面：推理层面。** 当 LLM 收到请求时，它将整个 `chat_history` 作为上下文窗口的一部分发送给模型。模型看到的是一个按时间顺序排列的消息序列，它**天然地**会把这些消息理解为同一个对话的延续。如果 user_a 和 user_b 的消息交替出现，模型会把它们理解为同一个人在不同时间说的话——或者更糟，理解为一个人格分裂的人在自言自语。

**第三个层面：架构层面。** 在线上服务架构中，agent 的生命周期通常与应用服务器的生命周期相同——它是一个常驻内存的单例。这意味着即使 A 用户的请求已经被处理完毕，A 的对话记录仍然留在 agent 的内存中，继续影响后续 B、C、D 用户的推理。

#### 为什么这个问题在"命令行原型"阶段看不出来？

因为当你在命令行里手动测试时，你永远只有一个"用户"——你自己。你输入一句话，等它回答，再输入下一句。这个时候在 agent 内部发生的行为就是：
1. 你输入 → append 到 chat_history
2. 模型读取整个 chat_history → 看到你一个人的对话 → 正常回答

你不会发现任何问题，因为只有一个来源在输入。

但当你的代码部署到服务器，同时处理多个 webhook 回调时，多个来源的请求几乎同时到达，全部写入同一个 chat_history——问题就暴露了。

---

### 3.4 💻 代码实操：共享 Session 导致的混线问题

下面我们通过一段完整可运行的代码，直观展示"共享 session"和"按来源隔离 session"的差异。

#### 🎯 目标

通过模拟三个不同来源的请求，观察：
- 当所有请求写入同一个 session 时，对话记录如何混在一起；
- 当每个来源拥有独立 session 时，对话记录如何保持清晰。

#### 🏗️ 前置准备

本例使用 Agently 框架（项目根目录下的 `agently` 模块），需要确保项目路径已正确配置。

```python
"""用同一个 agent 入口函数演示会话归属混线。"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agently import Agently

# 模拟三个不同来源的请求：企业微信用户A、Slack用户B、网页用户C
REQUESTS = [
    ("wecom:user-a:thread-1", "我的预算是 20 万"),
    ("slack:user-b:thread-9", "我的预算是多少？"),
    ("web:user-c:thread-2", "这个任务状态是什么？"),
]
```

**数据说明**：`REQUESTS` 列表中每个元组的第一个元素是 `来源标识`（渠道:用户ID:线程ID），第二个元素是用户输入的内容。注意 B 用户问的是"我的预算是多少？"——B 从未告诉过系统自己的预算，但在共享 session 场景下，B 可能会"看到"A 的预算信息。

接下来定义一个辅助函数，用于打印会话内容：

```python
def dump_agent_session(title, agent, session_id) -> None:
    print(f"\n{title}")
    for message in agent.sessions[session_id].context_window:
        print(f"- {message.role}: {message.content}")
```

---

#### 💻 Step 1：错误写法——所有请求共享一个 Session

```python
shared_agent = Agently.create_agent("shared-agent")


def handle_with_shared_session(source, user_input) -> None:
    # 关键问题：所有请求使用同一个固定的 session_id
    shared_agent.activate_session(session_id="global-agent-session")
    shared_agent.add_chat_history({"role": "user", "content": f"{source}: {user_input}"})
    shared_agent.add_chat_history({"role": "assistant", "content": f"已处理 {source} 的输入"})


for source, user_input in REQUESTS:
    handle_with_shared_session(source, user_input)

dump_agent_session("固定一个 session_id 时，agent 内置会话记录：", shared_agent, "global-agent-session")
```

**错误写法的输出效果**：当三个请求依次通过 `handle_with_shared_session` 处理完毕后，`global-agent-session` 中的 `context_window` 会包含 6 条消息——它们全部混在一起：

```
固定一个 session_id 时，agent 内置会话记录：
- user: wecom:user-a:thread-1: 我的预算是 20 万
- assistant: 已处理 wecom:user-a:thread-1 的输入
- user: slack:user-b:thread-9: 我的预算是多少？
- assistant: 已处理 slack:user-b:thread-9 的输入
- user: web:user-c:thread-2: 这个任务状态是什么？
- assistant: 已处理 web:user-c:thread-2 的输入
```

> ⚠️ **风险分析**：当 user-b 问"我的预算是多少？"时，模型会看到整个 chat_history，其中包含 user-a 说的"我的预算是 20 万"。由于模型无法从消息结构上区分这些信息属于不同的用户，它很可能把 user-a 的预算当作 user-b 的预算来回答。这就是**跨用户信息泄露**——在安全领域属于严重的访问控制缺陷。

---

#### 💻 Step 2：正确写法——按来源隔离 Session

```python
isolated_agent = Agently.create_agent("isolated-agent")


def handle_with_source_session(source, user_input) -> None:
    # 关键改进：使用来源标识作为 session_id，每个来源拥有独立会话
    isolated_agent.activate_session(session_id=source)
    isolated_agent.add_chat_history({"role": "user", "content": user_input})
    isolated_agent.add_chat_history({"role": "assistant", "content": f"已写入 {source}"})


for source, user_input in REQUESTS:
    handle_with_source_session(source, user_input)

for source, _ in REQUESTS:
    dump_agent_session(f"按来源拆 session 后，{source} 的会话记录：", isolated_agent, source)
```

**正确写法的输出效果**：每个来源拥有独立的 session，各自的对话记录互不干扰：

```
按来源拆 session 后，wecom:user-a:thread-1 的会话记录：
- user: 我的预算是 20 万
- assistant: 已写入 wecom:user-a:thread-1

按来源拆 session 后，slack:user-b:thread-9 的会话记录：
- user: 我的预算是多少？
- assistant: 已写入 slack:user-b:thread-9

按来源拆 session 后，web:user-c:thread-2 的会话记录：
- user: 这个任务状态是什么？
- assistant: 已写入 web:user-c:thread-2
```

> 💡 **核心差异**：在正确写法中，`session_id=source` 确保了每个用户的上下文完全隔离。当 user-b 的请求到来时，模型只会看到 user-b 自己历史中的记录——它不会"看到"user-a 的预算信息，因此不会发生信息泄露。

---

#### 📊 对比总结

| 维度 | ❌ 共享 Session | ✅ 按来源隔离 Session |
|---|---|---|
| 上下文范围 | 所有用户的对话混在一起 | 每个用户独立上下文 |
| 信息泄露风险 | 高——用户B可能看到用户A的信息 | 低——用户之间完全隔离 |
| 上下文膨胀速度 | 随总请求数线性增长 | 只要正确清理，单个会话可控 |
| 模型推理准确性 | 低——容易被无关信息干扰 | 高——上下文只包含当前用户的信息 |
| 并发安全性 | 无保障——多请求同时写入同一列表 | 有保障——各写各的 session |

---

### 3.5 🧪 实验：修改 role 字段能否区分用户？

上面我们讨论了"共享 session 导致上下文紊乱"的问题。在教学过程中，一位名叫**名字**的同学提出了一个非常有意思的问题。

#### 🙋 问题原文

> "我把 role 分为 user_a、user_b、user_c 行不行？"

> 📖 **背景**：同学注意到，在 OpenAI 的消息格式中，每条消息都有一个 `role` 字段，其值通常是 `"system"`、`"user"`、`"assistant"`。他的想法是：如果我把 `role` 从 `"user"` 改成 `"user_a"`、`"user_b"`、`"user_c"`，用不同的 role 标识来区分不同用户的身份，那模型是不是就能知道这些消息来自不同的人，从而避免"串话"？

这是一个非常好的问题，因为它触及了一个重要的边界：**API 协议的能力边界 vs 模型理解能力边界**。

---

#### 🧪 实验 1：修改 role 为 user_a / user_b / user_c

老师在课堂上当场做了一个实验来验证这个想法：

**实验设置**：在同一个 session 中，向模型依次发送三条消息，但每条消息的 `role` 字段分别设为 `user_a`、`user_b`、`user_c`：

```
- user_a: 你好
- user_b: 你好
- user_c: 刚才我们说了什么？
```

**实验结果**：
- 模型**没有报错**——说明它接受了自定义的 role 名称，没有在 API 层面拒绝这些消息。
- 但当 user_c 问"刚才我们说了什么？"时，模型的回答是**不相关的**，它无法正确关联 `user_a` 和 `user_b` 说的内容。模型不理解 user_c 问的是"刚才 user_a 和 user_b 说了什么"——在它看来，这是一个新的对话，与前面 user_a 和 user_b 的发言没有关系。

**结论**：虽然改了 role 字段，并且模型没有报错，但它**依然不理解**这些不同的 role 代表不同的人。模型把每一段都看作独立的对话片段。

---

#### 🧪 实验 2：添加 instruct 指令

老师接着尝试了另一个思路：用 `system` prompt（instruct）明确告诉模型这些 role 的含义。

```
system: 你正在同时与三位用户对话：user_a、user_b、user_c。请根据 role 字段区分发言者身份。
user_a: 我的预算是 20 万。
user_b: 我的预算是多少？
```

**实验结果**：
- 通过 instruct 指令，模型**确实能够**在一定程度上根据 role 来区分说话者。当 user_b 问预算时，模型知道 user_b 和 user_a 是不同的人，不会直接说"你的预算是 20 万"。
- 所以 instruct **能部分解决"看串"的问题**——即模型能区分不同人说了不同的话。

> ⚠️ **但这只是表面上的解决。** instruct 解决了"识别"问题，但没有解决更深层的两个问题。

---

#### 📊 实验结果对比表

| 实验方案 | role 自定义 | 加 instruct | 模型是否报错 | 能区分说话者 | 能阻止上下文膨胀 |
|---|---|---|---|---|---|
| 方案 A：role 改为 user_a/b/c | ✅ | ❌ | ❌ 不报错 | ❌ 无法区分 | ❌ 不能 |
| 方案 B：role 改为 user_a/b/c + instruct | ✅ | ✅ | ❌ 不报错 | ⚠️ 部分可以 | ❌ 不能 |
| 方案 C：按来源隔离 Session | 不需要 | 不需要 | 不涉及 | ✅ 天然隔离 | ✅ 能 |

---

### 3.6 ⚠️ 两个更深层的问题

即使 instruct 能让模型区分不同用户，还有两个绕不开的问题：

#### 问题一：不同模型对 role 字段的兼容性差异

OpenAI 兼容接口对 `role` 字段的定义是有限制的。标准的 role 值只有 `system`、`user`、`assistant`、`tool`、`function` 这几种。虽然某些模型（如 DeepSeek）在实践中对自定义 role 的容忍度较高，允许你传入 `user_a` 这样的值而不报错，但**这不代表所有模型都支持**。

当你尝试把同样的请求发给通义千问、文心一言或其他国产模型时，它们的 API 可能会：
- 直接拒绝请求，返回参数校验错误；
- 把自定义 role 当作 `user` 处理，失去区分效果；
- 行为不可预测，在不同版本间发生变化。

> 💡 **核心洞见**：依赖 `role` 字段的自定义来区分用户，是把业务逻辑建立在 API 协议的"灰色地带"上——今天能用，明天换了模型就可能不能用。这不是一个可靠的架构方案。

#### 问题二：上下文膨胀不可阻挡

即使 instruct 让模型"看懂了"不同用户，所有用户的对话仍然被堆在同一个 chat_history 里。随着并发服务的人数不断上升：

- **10 个用户同时使用** → chat_history 中包含所有人的对话 → 上下文长度 10x
- **100 个用户同时使用** → 上下文长度 100x
- **每个用户多说几轮** → 膨胀速度还会更快

上下文膨胀的后果是严重的：
1. **Token 成本飙升**：每次请求都要把整个 chat_history 发给模型，其中大量内容是其他用户的对话，对当前请求毫无帮助；
2. **推理质量下降**：模型需要从海量混杂信息中提取当前用户的相关内容，准确率会下降；
3. **响应延迟增加**：更长的上下文意味着更长的推理时间；
4. **触发上下文窗口上限**：当累积对话超过模型的上下文窗口限制时，最旧的信息会被截断——而截断的可能是当前用户最需要的历史信息。

---

### 3.7 📊 白板还原：多用户共享 Agent 的混乱流 vs 隔离流

以下是老师课堂白板讲解的 ASCII 还原——展示为什么多用户共用一个 agent 会导致上下文紊乱，以及隔离后的正确架构应该是什么样。

#### ❌ 错误架构：共享 Agent State

```
                          ┌─────────────────────────────────────┐
                          │         Shared Agent (单例)          │
                          │                                     │
                          │  ┌─────────────────────────────────┐│
                          │  │  chat_history = []               ││
                          │  │  ┌─────────────────────────────┐││
   User A ──► request ────┼──┼─►│ "user: 我的预算是 20 万"     │││
                          │  │  │ "assistant: 好的..."         │││
   User B ──► request ────┼──┼─►│ "user: 我的预算是多少？"     │││
                          │  │  │ "assistant: 你的预算是 20 万" │││  ← 泄露！
                          │  │  │ "user: 任务状态是什么？"     │││
   User C ──► request ────┼──┼─►│ "assistant: ..."             │││
                          │  │  └─────────────────────────────┘││
                          │  └─────────────────────────────────┘│
                          │         所有消息混在一起              │
                          └─────────────────────────────────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │      LLM        │
                              │  看到所有用户     │
                              │  的混合对话 → 串话 │
                              └─────────────────┘
```

**问题链条**：
1. 三个用户的请求依次到达，全部写入同一个 `chat_history` 列表
2. LLM 接收整个列表作为上下文，无法从消息结构上区分发言者身份
3. user_b 问"我的预算是多少？"时，模型在上下文中看到了 user_a 说的"20 万"
4. 模型将 user_a 的信息错误地归属于 user_b → **上下文紊乱，信息泄露**

#### ✅ 正确架构：按来源隔离 Session

```
   User A ──► request ─┐
                        │            ┌──────────────────────────┐
   User B ──► request ─┤            │     Agent (执行器)        │
                        ├────────────│  只负责：接收请求、       │
   User C ──► request ─┘            │  路由到对应 Session、     │
                                    │  调用 LLM、返回结果        │
                                    └──────┬───────┬───────┬───┘
                                           │       │       │
                              ┌────────────┼───────┼───────┼────────────┐
                              │            │       │       │            │
                              ▼            ▼       ▼       ▼            ▼
                        ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
                        │Session A│ │Session B│ │Session C│ │Session D│  ...
                        │         │ │         │ │         │ │         │
                        │history: │ │history: │ │history: │ │history: │
                        │"20 万"  │ │"预算是?"│ │"任务?"  │ │(空)     │
                        └────┬────┘ └────┬────┘ └────┬────┘ └─────────┘
                             │           │           │
                             ▼           ▼           ▼
                        ┌─────────────────────────────────────┐
                        │  LLM 每次只看到当前用户的上下文       │
                        │  User A → Session A history         │
                        │  User B → Session B history         │
                        │  User C → Session C history         │
                        └─────────────────────────────────────┘
```

**改进要点**：
1. Agent 退化为**纯执行器**——接收请求、路由、调用 LLM、返回结果
2. 每个用户（或每个对话线程）拥有一个独立的 Session 对象
3. 每次 LLM 调用时，只发送当前 Session 的上下文窗口
4. 用户之间的数据完全隔离，**从根本上消除上下文紊乱**

---

### 3.8 🔑 核心结论与设计启示

#### 结论一：Agent 不适合做"状态容器"

Agent 的职责应该聚焦于**"能力入口"**和**"请求执行器"**——它知道如何调用 LLM、如何解析 tool call、如何处理输出。但它**不应该**承担"记住所有对话"的职责。

把 agent 当作全局状态容器来用，本质上是把单线程的心智模型套在了多用户并发的实际上。

#### 结论二：Session 是上下文隔离的天然边界

Session 的原始含义就是一个"会话"——一次连续的、有上下文的交互。当一个用户开启一个对话，就应该创建一个独立的 session。当对话结束（或超时），session 就可以被清理。Session 天然就是上下文隔离的边界。

#### 结论三：隔离是基本前提

正如课堂上 9 号同学所说：**"会话隔离是不是基本的前提？"**——是的，这是一个正确且重要的总结。在多用户服务场景中，会话隔离是所有后续设计（如上下文组装、记忆管理、权限控制）的前提条件。没有隔离，后面的一切都是空中楼阁。

#### 设计启示

| 设计原则 | 说明 |
|---|---|
| Agent = 能力入口 | Agent 提供 LLM 调用能力、工具编排能力，不持有用户状态 |
| Session = 状态容器 | Session 持有单个用户/对话的上下文、历史、临时数据 |
| 按来源隔离 | 每个来源标识（用户ID + 线程ID）对应一个独立 Session |
| 按需创建与销毁 | Session 随请求创建，超时或对话结束后清理 |

> 🔗 **延伸阅读**：下一节 M04 将讨论如何将 Session 从 Agent 中分离出来，构建独立的 Session 池，实现会话的全生命周期管理。

> ⚠️ **安全伏笔**：跨用户的数据隔离问题不仅是架构问题，也是安全问题。在 Web 应用中，如果用户的上下文数据混在一起，就构成了 OWASP Top 10 中的"失效的访问控制"（Broken Access Control）——这将在后续安全专题章节中详细讨论。

---

### 3.9 💬 答疑：role 字段不是 session 隔离的替代方案

**🙋 问题回顾**（名字同学）："我把 role 分为 user_a、user_b、user_c 行不行？"

> 📖 **背景**：同学想通过修改 role 字段的方式，在同一个 session 内用不同的 role 值来标识不同用户，从而避免上下文串扰。

**💬 老师回答总结**：

从实验结果来看，这条路行不通——至少不能作为可靠的架构方案。具体原因有三层：

1. **模型理解层面**：即使把 role 改成 user_a/b/c，模型也**不天然理解**这些自定义 role 代表不同的人。除非通过 instruct 显式告知，否则模型会把它们当作无意义的标签。
2. **兼容性层面**：不同的模型对 role 字段的容忍度不同。DeepSeek 比较宽松，但千问、文心等模型可能会拒绝自定义 role 值。把业务架构建立在 API 协议的灰色地带上是不安全的。
3. **膨胀层面**：即使 instruct 解决了"看串"的问题，所有用户的对话仍然堆在同一个 chat_history 里。随着用户数增加，上下文膨胀不可避免，token 成本、推理质量和响应延迟都会恶化。

> 💡 **延伸建议**：判断一个方案是否"够用"的标准不是"能不能跑通"，而是"在什么条件下会崩"。role 方案在以下条件下会崩：换模型、用户数超过 10 个、安全审计要求数据隔离。而 Session 隔离方案在这些条件下依然稳固。**架构选择，要选那个边界条件更远的方案。**

## 四、Session 独立化：会话池设计与多会话管理

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 解释为什么 Session 必须从 Agent 内部独立出来
> - [ ] 画出「Agent ← Session ← 用户」三层架构的演进图
> - [ ] 基于 `sessions` 字典实现多用户、多会话的会话池
> - [ ] 正确处理 session_id 不存在时的两种场景：报错 vs. 新建
> - [ ] 理解 `user_id` + `session_id` 双键管理的设计意图

---

### 4.1 问题回顾：M02+M03 留下了什么

在 M02 中，我们引入了 Agent 作为模型任务的最终承接方。在 M03 中，我们亲眼看到了共享 Agent 状态带来的灾难——当多个用户、多个会话同时向同一个 Agent 实例写入消息时，上下文产生了交叉污染，A 用户的提问混进了 B 用户的对话窗口。

问题的根源可以归纳为一句话：

> **Agent 本不该负责"记谁说了什么"。它应该负责"基于上下文给出回答"。**

```
共享 Agent 模式下：
┌─────────┐  ┌─────────┐  ┌─────────┐
│ 用户 A   │  │ 用户 B   │  │ 用户 C   │
└────┬────┘  └────┬────┘  └────┬────┘
     │            │            │
     └────────────┬────────────┘
                  │ 全部写入同一个 agent.state
                  ▼
          ┌───────────────┐
          │  Agent 实例    │
          │  state = [...] │ ← 所有人的消息混在一起
          │  (共享状态)     │
          └───────────────┘
```

> ⚠️ **核心痛点**：Agent 的 state 是全局共享的，任何调用方都在同一个容器里追加消息。这不仅导致上下文污染，也让"为每个用户维持独立会话"变成不可能。

M03 结束时，我们的临时方案是通过手动重置 `agent.state` 来模拟隔离。但这显然不是生产级做法——手动重置无法应对并发、无法按用户区分、无法追溯历史。我们需要一个真正的架构改进。

---

### 4.2 架构转折：为什么需要独立 Session 层

#### 🧠 直观理解

把 Agent 想象成一家高级餐厅的主厨（Chef）。M02+M03 的做法，相当于每个客人进门后直接走进厨房，对着主厨喊自己的点单。主厨一边炒菜一边记谁点了什么——两个人同时喊，主厨就记混了。

正确的做法是什么？餐厅需要一个**前台（Session）**：

- 每位客人到前台，前台给他一本**点菜单（Session 对象）**
- 客人把需求写在点菜单上
- 前台把整理好的点菜单递进厨房
- 主厨只负责烹饪，不用记谁点了什么

这个"前台"就是 **Session 层**。客人（用户）不直接面对主厨（Agent），而是通过 Session 来管理自己的对话上下文。

#### 📖 架构演进：三层模型

从 M02+M03 暴露的问题出发，我们推导出如下的架构演进：

**演进前：双层直接对接**

```
用户层（User）
    │
    │ 直接调用 agent.call()
    │
    ▼
Agent 层
  ├── 模型调用
  ├── 上下文 state（所有人共享）← 问题所在
  └── 工具执行
```

**演进后：三层隔离架构**

```
用户层（User）                     ← 每个用户有自己的 user_id
    │
    │ 通过 session_id 找到自己的会话
    │
    ▼
Session 层（会话池）                ← 新增的中间层
  ├── 按 user_id 分组
  ├── 按 session_id 隔离
  ├── 管理每段对话的上下文窗口
  └── 向 Agent 传递纯净的上下文
    │
    │ 传入上下文
    │
    ▼
Agent 层                          ← 只负责模型推理
  ├── 模型调用
  ├── 工具执行
  └── 不持有任何用户状态
```

> 💡 **核心洞见**：三层架构的本质是**关注点分离（Separation of Concerns）**。
> - **Agent** 的职责是"推理"——拿到上下文，给出回答。
> - **Session** 的职责是"记忆"——记住这段对话中谁说了什么。
> - **User** 的职责是"提问"——发起对话、提供输入。
>
> 这三件事不应混在一个对象里。

接下来我们用 ASCII 架构图把演进过程画清楚。

**演进前：用户直接面对 Agent**

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  用户 A   │     │  用户 B   │     │  用户 C   │
│ (钉钉)    │     │ (Slack)  │     │ (微信)    │
└─────┬─────┘     └─────┬─────┘     └─────┬─────┘
      │                 │                 │
      │  agent.call()   │  agent.call()   │  agent.call()
      │                 │                 │
      └─────────────────┬─────────────────┘
                        │ 全部写入同一个 agent.state
                        ▼
              ┌─────────────────────┐
              │       Agent         │
              │ ┌─────────────────┐ │
              │ │ state = [...]    │ │  ← 全局共享，交叉污染
              │ │ (messages 混合)  │ │
              │ └─────────────────┘ │
              │  model.generate()   │
              └─────────────────────┘
```

**演进后：Agent ← Session ← 用户**

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  用户 A   │     │  用户 B   │     │  用户 C   │
│ user: A  │     │ user: B  │     │ user: C  │
└────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │
     │ sess_1         │ sess_9         │ sess_2  sess_5
     │                │                │
     ▼                ▼                ▼
┌─────────────────────────────────────────────────┐
│                 会话池 (Session Pool)              │
│                sessions: dict                    │
│                                                 │
│  ┌─────────────────┐ ┌──────────────┐           │
│  │ user_a:         │ │ user_b:      │  ...      │
│  │   sess_1: [...] │ │   sess_9: [..]│           │
│  │   (出差申请)     │ │   (报销查询)   │           │
│  └─────────────────┘ └──────────────┘           │
│  ┌─────────────────┐                            │
│  │ user_c:         │                            │
│  │   sess_2: [...] │  ← 同一用户可有多个会话       │
│  │   sess_5: [...] │                            │
│  └─────────────────┘                            │
└──────────────────────┬──────────────────────────┘
                       │ 传递纯净上下文
                       ▼
              ┌─────────────────────┐
              │       Agent         │
              │                     │
              │  「只做推理，不记状态」 │
              │  model.generate()   │
              └─────────────────────┘
```

> 🔗 **关联知识**：这里的 `sessions` 字典就是后续 M05 中 `Session` 类的管理容器。现在先用原生字典理解核心概念，M05 会将每个 session 封装为完整的 `Session` 对象。

---

### 4.3 Session 池设计：`sessions` 字典的层级结构

#### 🧠 直观理解

Session 池就像一栋酒店大楼：

- **楼层** = `user_id`（每个客人分配一层）
- **房间** = `session_id`（每位客人在自己的楼层上可以开多个房间，对应多段对话）
- **房间里的东西** = `chat_history`（这段会话的所有消息记录）

同一个客人（user_id）可以在自己的楼层上开多个房间（多个 session_id），每个房间里的对话互不干扰。

#### 📖 数据结构设计

```
sessions = {
    user_id_1: {
        session_id_a: [messages...],   # 用户1的第1段对话
        session_id_b: [messages...],   # 用户1的第2段对话
    },
    user_id_2: {
        session_id_c: [messages...],   # 用户2的第1段对话
    },
}
```

三层嵌套的语义：

| 层级 | Key | Value | 含义 |
|---|---|---|---|
| 第一层 | `user_id` | 该用户的所有会话字典 | 按用户隔离，不同用户的数据物理隔绝 |
| 第二层 | `session_id` | 该会话的消息列表 | 按会话隔离，同一用户的不同对话互不干扰 |
| 第三层 | 消息索引 | `{"role": ..., "content": ...}` | 单条对话记录 |

> ⚠️ **注意事项**：Session 不负责鉴权。`user_id` 是从外部鉴权层传入的——谁调用这个 Session 池，鉴权层就已经确定了他的 `user_id`。Session 池只负责"拿着这个 user_id，找到或创建对应的会话空间"，不做身份验证。

#### 🔀 为什么是 `user_id` + `session_id` 双键，而不是单键？

| 方案 | 优点 | 缺点 | 适用场景 |
|---|---|---|---|
| 只用 `session_id` | 扁平简单 | 无法区分不同用户的会话；session_id 全局唯一难维护 | 单用户应用 |
| `user_id` + `session_id` | 用户隔离天然实现；同一用户多会话自然支持；session_id 只需在用户范围内唯一 | 多一层嵌套 | 多用户 SaaS 应用 |

课程选择双键方案，因为我们的目标场景是企业级应用——多个渠道（钉钉、Slack、微信）的用户同时在线上与 Agent 对话。每个用户可能同时开着多段对话（比如同时在问报销问题又在提交出差申请）。

---

### 4.4 代码实现：构建第一个会话池

#### 🎯 目标

用原生 Python 字典构建一个会话池，按 session_id 分开管理多个 Session，验证每个 Session 的上下文是独立隔离的。

#### 🏗️ 前置准备

本模块使用的 Session 类来自 `agently.core`，是框架提供的会话管理基础类。后续 M05 会深入它的内部职责。

```python
from agently.core import Session
```

---

#### 💻 Step 1：定义会话池的输入数据

我们模拟三个不同的会话——两个来自钉钉（wecom）用户 A，一个来自 Slack 用户 B。每个会话有不同的对话主题和消息历史：

```python
# 文件名: s04_session_id_registry.py（节选 Step 1）
# 功能: 定义多个独立会话的输入数据

session_inputs = {
    # 钉钉渠道，用户 A，会话 1：出差申请
    "wecom:user-a:thread-1": [
        {"role": "user", "content": "我想申请去上海出差，需要提前几天？"},
        {"role": "assistant", "content": "通常需要提前提交申请，并补充出差时间和预算。"},
        {"role": "user", "content": "预算上限是 20 万，材料 ref=inputs/travel-policy。"},
    ],
    # Slack 渠道，用户 B，会话 9：报销查询
    "slack:user-b:thread-9": [
        {"role": "user", "content": "我的报销单现在是什么状态？"},
        {"role": "assistant", "content": "需要先确认报销单号。"},
    ],
}
```

> 🔗 **关键设计**：注意 key 的命名约定 `渠道:用户:会话`。这是一个复合 ID，同时编码了来源渠道、用户身份和会话编号。在生产实践中，`user_id` 来自鉴权层，`session_id` 来自前端请求，两者组合形成唯一的会话标识。

---

#### 💻 Step 2：创建会话池并批量初始化

我们用一个字典 `sessions = {}` 作为会话池的容器。遍历 `session_inputs`，为每个会话创建独立的 `Session` 对象，放入池中：

```python
# 文件名: s04_session_id_registry.py（节选 Step 2）
# 功能: 创建会话池，批量初始化 Session 对象

async def demo() -> None:
    # ── 会话池：所有 session 的容器 ──
    sessions = {}

    # ── 批量创建 Session ──
    for session_id, messages in session_inputs.items():
        # 每个 session_id 对应一个独立的 Session 对象
        # settings 中的 max_length=500 限制了上下文窗口的最大长度
        session = Session(
            id=session_id,
            settings={"session": {"max_length": 500}}
        )
        # 将消息历史注入该 session（异步操作）
        await session.async_add_chat_history(messages)
        # 注册到会话池
        sessions[session_id] = session

    # ... 验证步骤见 Step 3 ...
```

| 行号 | 关键操作 | 解释 |
|---|---|---|
| `sessions = {}` | 创建空字典 | 会话池的物理载体。Key 是 session_id，Value 是 Session 对象 |
| `Session(id=session_id, settings=...)` | 实例化 Session | 每个 session 独立创建，拥有自己的 `full_context` 和 `context_window` |
| `await session.async_add_chat_history(messages)` | 注入历史消息 | 将对话记录批量写入该 session，异步操作遵循框架约定 |
| `sessions[session_id] = session` | 注册到池 | 将创建好的 session 放入池中，完成"独立化" |

> ⚠️ **注意事项**：`settings={"session": {"max_length": 500}}` 设置了上下文窗口的最大长度。这意味着每个 Session 只保留最近 500 个单位（按 token 或字符）的上下文。Session 是**短期上下文窗口**的管理者，不是永久存储——永久化存储是数据库的事，Session 不越界。

---

#### 💻 Step 3：验证每个 Session 的隔离性

我们遍历会话池，打印每个 session 的状态，验证它们是否互不干扰：

```python
# 文件名: s04_session_id_registry.py（节选 Step 3）
# 功能: 遍历会话池，验证每个 Session 的独立隔离

    # ── 验证隔离性 ──
    for session_id, session in sessions.items():
        print(f"\n== {session_id} ==")
        print("full_context 条数：", len(session.full_context))
        print("context_window 条数：", len(session.context_window))
        print("memo：", session.memo)
        for message in session.context_window:
            print(f"- {message.role}: {message.content}")


if __name__ == "__main__":
    asyncio.run(demo())
```

**预期输出**：

```
== wecom:user-a:thread-1 ==
full_context 条数： 3
context_window 条数： 3
memo： None
- user: 我想申请去上海出差，需要提前几天？
- assistant: 通常需要提前提交申请，并补充出差时间和预算。
- user: 预算上限是 20 万，材料 ref=inputs/travel-policy。

== slack:user-b:thread-9 ==
full_context 条数： 2
context_window 条数： 2
memo： None
- user: 我的报销单现在是什么状态？
- assistant: 需要先确认报销单号。
```

> 💡 **验证要点**：wecom 会话只有出差申请的消息，slack 会话只有报销查询的消息——两者**完全隔离**，不存在 M03 中出现的交叉污染。这就是 Session 独立化的效果。

---

### 4.5 Session ID 管理：创建、查找与报错逻辑

上一节的代码使用了固定的 `session_inputs` 字典来模拟。但在真实场景中，请求是动态到达的。每次请求携带两个关键信息：

1. **`user_id`**：谁在说话（由鉴权层提供）
2. **`session_id`**：属于哪段对话（由前端或客户端提供，可能为空）

Session 池需要根据这两个信息，执行以下逻辑：

#### 📖 处理规则

```
请求到达，携带 user_id 和 session_id（可能为 None）
    │
    ├── session_id 不为 None？
    │   │
    │   ├── 是 → 在 sessions 池中查找
    │   │       │
    │   │       ├── 找到了 → ✅ 返回该 session，继续对话
    │   │       │
    │   │       └── 没找到 → ❌ RuntimeError
    │   │            原因：前端声称存在一个 session，但我们没有记录
    │   │            这可能是 session 过期、伪造的 ID、或数据丢失
    │   │
    │   └── 否 → ✅ 创建新 session
    │           生成新的 session_id，注册到 sessions 池
    │           返回新 session，开始一段新对话
```

#### 💻 代码实现

```python
# 功能: Session ID 的创建、查找与报错逻辑
# 说明: 这段代码演示了动态请求下 session 池的核心管理模式

import uuid
from typing import Optional

# ── 会话池 ──
sessions: dict[str, dict[str, list[dict]]] = {}
# 结构: sessions[user_id][session_id] = chat_history


def get_or_create_session(
    user_id: str,
    session_id: Optional[str] = None
) -> tuple[str, list[dict]]:
    """
    根据 user_id 和 session_id 获取或创建会话。

    参数:
        user_id: 用户唯一标识（由鉴权层提供）
        session_id: 会话唯一标识（可选，由前端提供）

    返回:
        (session_id, chat_history): 会话 ID 和消息历史列表

    抛出:
        RuntimeError: 当 session_id 已提供但在池中找不到时
    """
    # ── 确保 user 空间存在 ──
    # 为什么？每个 user 对应池中的一层，首次访问时需要初始化
    if user_id not in sessions:
        sessions[user_id] = {}

    # ── 情况 1：传了 session_id ──
    if session_id is not None:
        # 在 user 的空间中查找该 session
        if session_id in sessions[user_id]:
            # ✅ 找到：返回已有会话
            return session_id, sessions[user_id][session_id]
        else:
            # ❌ 没找到：前端声称存在但实际不存在
            # 为什么报错而不是创建？
            # 因为 session_id 是前端指定的——如果前端说"我在会话 abc123 中"，
            # 但我们没有这个记录，说明数据不一致。
            # 静默创建新会话会让前端以为自己在同一个会话中，但历史消息全丢了。
            raise RuntimeError(
                f"Session '{session_id}' not found for user '{user_id}'. "
                f"可能的原码：session 已过期、ID 错误或数据被清除。"
            )

    # ── 情况 2：没传 session_id ──
    # ✅ 创建新会话：生成唯一 ID，初始化空消息列表
    # 为什么这种情况允许创建？
    # 因为没传 session_id 说明这是一个全新对话的起点，
    # 前端不期望有任何历史消息。
    new_session_id = f"session_{uuid.uuid4().hex[:8]}"
    sessions[user_id][new_session_id] = []

    # [可选] 注入系统提示词作为第一条消息
    # sessions[user_id][new_session_id].append({
    #     "role": "system",
    #     "content": "你是一个企业助手，请用简洁、专业的语言回答问题。"
    # })

    return new_session_id, sessions[user_id][new_session_id]
```

#### 📊 行为决策表

| user_id 存在 | session_id 传入 | 池中有该 session | 行为 | 使用场景 |
|---|---|---|---|---|
| 否 | 否 | N/A | 创建 user 空间 + 创建新 session | 新用户首次对话 |
| 否 | 是 | N/A | 创建 user 空间 → ❌ RuntimeError | 异常：新用户不可能携带已有 session |
| 是 | 否 | N/A | 创建新 session | 已有用户发起新对话 |
| 是 | 是 | 是 | ✅ 返回已有 session | 继续已有对话 |
| 是 | 是 | 否 | ❌ RuntimeError | 异常：前端 session ID 与后端不一致 |

> ⚠️ **注意事项**：这张表覆盖了五种场景。核心原则——**前端若有 session_id 就必须能对上**。对不上就报错，绝不静默创建。静默创建会掩盖数据不一致的 bug，导致用户在未知状态下丢失对话历史。

---

### 4.6 答疑：为什么不能用 Flow 内部 state 管理会话状态

> 本段完整还原课堂上宏宇同学与老师的讨论。宏宇提出了一个直觉上很合理的替代方案，老师从架构层面进行了完整论证。这个讨论是理解「为什么 Session 必须独立」的关键。

---

**🙋 宏宇同学的提问**

> 从直觉上想，应该是想要把这个 chat history 放在 state 上去管理，分成 conversation...如果用 flow 的方案，在大的编排逻辑里面去走，把 agent 模块在外部包裹起来，这个逻辑本身是对的吧？

**💬 老师回答**

你提的这个思路，从直觉上是非常正确的。如果我们在大的编排逻辑（flow）里面，把 agent 对象在外部包裹起来，让 flow 来管理每次对话的 state——这个方向本身是对的。

但问题出在 flow 的一个关键特性上：**每次 flow 启动时，state 是从头开始初始化的**。

让我用一个具体场景来说明：

```
flow 第一次执行（用户 A 说"我要申请出差"）：
  flow.state = {}  ← 初始为空
  → agent 处理 → 回答
  → state 中记录了这段对话

flow 第二次执行（用户 A 说"预算 20 万"）：
  flow.state = {}  ← 又从头初始化！上一次的对话丢失了！
  → agent 看到的是"预算 20 万"，但不知道前文是"出差申请"
  → 上下文断裂
```

Flow 的设计初衷是"编排管道"——每次运行是一个独立的编排任务，任务完成后 state 就释放了。它不是一个"持久化会话容器"。这就好比你去餐厅吃饭，每道菜上来之后服务员就收走了你的点菜单，下一道菜上来时厨师不知道你之前点了什么。

而我们需要的是什么？是**跨多次 agent 调用保持上下文连续性**的能力。用户 A 说第一句话，agent 回答；用户 A 在这个"对话窗口"里接着说第二句话，agent 需要同时看到第一句和第二句。这个需求要求 state 是**持续存在的**，而不是每次调用都重置。

所以结论是：

| 方案 | 能否跨调用持存 | 适用场景 |
|---|---|---|
| Flow 内部 state | 否（每次启动重置） | 单次编排任务内的状态传递 |
| 独立 Session 对象 | 是（生命周期由调用方控制） | 跨多轮对话的上下文管理 |

> 💡 **延伸**：那如果非要用 flow 呢？也不是完全不行——你可以在 flow 启动时从外部存储（数据库/Redis）恢复 state，flow 结束时再写回。但这就相当于在 flow 外面包了一层 state 管理层——本质上就是在实现 session。与其 hack flow 的机制，不如直接设计一个专门的 Session 层，职责更清晰。

---

### 4.7 老师"翻车"实录：框架版本导致 Session 自动管理不生效

> 本段按 Rule 1 要求，完整还原课堂上的踩坑过程。

#### 🐛 排错实录：agently 框架版本不兼容导致 Session 高级封装无法演示

**课堂场景**

老师原本计划演示 agently 框架中封装好的 Session 自动管理功能——那种"创建 Session 后，框架自动帮你管理上下文窗口，你只需调用 agent"的高级用法。但当堂运行时发现，框架版本和当前课程所使用的依赖版本不兼容，高级封装无法在课堂环境中正常工作。

**🚨 现象**

```
尝试导入 agently 的 Session 自动管理层时，报版本不兼容错误。
框架高级 Session 管理的 API 与当前安装的 agently 版本不匹配。
```

**🔍 原因分析**

1. agently 框架处于快速迭代期，不同版本的 Session 管理 API 发生了 breaking changes
2. 课程录制时所使用的框架版本与课前准备环境中的版本不一致
3. 高级封装层的接口签名在不同版本间发生了调整，旧版代码无法在新版框架上运行

**✅ 老师的应对**

放弃演示高级封装，直接退回到**底层原生字典 + Session 基础类**的方案——这正是前文 4.4 节中 `sessions = {}` + `Session(id=...)` 的写法。

```python
# ✅ 替代方案：绕过版本问题，直接操作底层
sessions = {}                                  # 原生字典，不依赖框架高级 API
session = Session(id=session_id, settings=...) # 仅使用框架基础类
await session.async_add_chat_history(messages) # 手动管理消息注入
sessions[session_id] = session                 # 手动注册到池
```

**📝 经验总结**

1. **框架版本锁定是生产环境的必备项**：不同版本的 breaking changes 会在最意想不到的时候出现
2. **理解底层原理比依赖高级封装更重要**：高级封装不能用了，但我们仍然能用手动方案完成全部功能——因为我们理解了 Session 池的本质
3. **"翻车"反而带来了教学价值**：手动构建 sessions 字典让我们看到了 Session 管理的真实肌理，而不是被框架的"黑箱"遮挡。很多学员反馈，看完手动实现后，再理解框架的高级封装反而更透彻了

> 💡 **核心洞见**：这次翻车让我们确认了一个重要的事实——真正的能力不在于会用哪个框架的哪个版本，而在于**理解框架试图解决的问题**。当你能用原生字典实现会话池时，你就已经掌握了 Session 管理的核心原理，剩下的只是语法糖。

---

### 4.8 完整可运行代码

> 以下代码整合了本节所有知识点。文件位置：`scripts/s04_session_id_registry.py`

```python
"""按 session_id 分开管理多个 Session。"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agently.core import Session


# ── 模拟多来源、多用户的会话数据 ──
session_inputs = {
    # 钉钉渠道：用户 A 的出差申请会话
    "wecom:user-a:thread-1": [
        {"role": "user", "content": "我想申请去上海出差，需要提前几天？"},
        {"role": "assistant", "content": "通常需要提前提交申请，并补充出差时间和预算。"},
        {"role": "user", "content": "预算上限是 20 万，材料 ref=inputs/travel-policy。"},
    ],
    # Slack 渠道：用户 B 的报销查询会话
    "slack:user-b:thread-9": [
        {"role": "user", "content": "我的报销单现在是什么状态？"},
        {"role": "assistant", "content": "需要先确认报销单号。"},
    ],
}


async def demo() -> None:
    # ── Step 1: 创建会话池 ──
    sessions = {}

    # ── Step 2: 批量创建并注册 Session ──
    for session_id, messages in session_inputs.items():
        # 每个 session_id 独立创建 Session 对象
        # max_length=500 限制上下文窗口大小
        session = Session(
            id=session_id,
            settings={"session": {"max_length": 500}}
        )
        # 注入历史消息
        await session.async_add_chat_history(messages)
        # 注册到池中
        sessions[session_id] = session

    # ── Step 3: 验证隔离性 ──
    # 遍历池中的每个 session，观察它们的上下文是否互不干扰
    for session_id, session in sessions.items():
        print(f"\n== {session_id} ==")
        print("full_context 条数：", len(session.full_context))
        print("context_window 条数：", len(session.context_window))
        print("memo：", session.memo)
        for message in session.context_window:
            print(f"- {message.role}: {message.content}")


if __name__ == "__main__":
    asyncio.run(demo())
```

#### 📊 运行结果分析

| 指标 | wecom:user-a:thread-1 | slack:user-b:thread-9 |
|---|---|---|
| `full_context` 条数 | 3 | 2 |
| `context_window` 条数 | 3 | 2 |
| `memo` | None | None |
| 对话主题 | 出差申请 | 报销查询 |
| 交叉污染 | 无 | 无 |

---

### 🔗 推导链：从痛点到方案

```
起点: M02+M03 暴露的问题
  │  共享 Agent state → 多用户消息交叉污染 → 无法维持独立对话
  │
  ├── 第1步: 识别根因
  │   为什么？问题不在 Agent 本身，而在于"记状态"和"做推理"不该由同一个对象承担
  │   结论：需要将"状态管理"从 Agent 中剥离
  │
  ├── 第2步: 引入 Session 层
  │   为什么是 Session 而不是别的？因为"会话"天生就是对话状态的载体——
  │   一段对话 = 一组有序的消息 + 一个上下文窗口
  │   结论：Session 作为 user 和 agent 之间的中间层
  │
  ├── 第3步: 设计会话池
  │   为什么需要池化管理？因为系统同时服务多个用户，每个用户可能有多段对话，
  │   需要一个容器来组织这些 Session 对象
  │   结论：sessions 字典，user_id + session_id 双键结构
  │
  ├── 第4步: 处理边界情况
  │   为什么区分"报错"和"新建"？因为数据一致性——
  │   前端声称存在的 session 必须能在后端找到，否则是 bug
  │   结论：传了 session_id 但找不到 → RuntimeError；没传 → 新建
  │
  └── 结论: 三层架构建立
      User → Session 会话池 → Agent
      - User: 发起请求，提供 user_id + session_id
      - Session: 管理上下文，隔离不同用户和会话
      - Agent: 接收纯净上下文，只做推理
```

---

> 🔗 **前置知识**：详见 [第二章：Agent 基础架构] 和 [第三章：共享 Agent 状态风险]（← 合并时替换为锚点链接）
>
> 🔗 **延伸阅读**：本文 [第五章：Session 三件职责] 将深入 Session 对象内部的 `full_context`、`context_window` 和 `memo` 三大核心机制（← 合并时替换为锚点链接）

## 五、Session 三件职责与 Context Window 概念（完整版）

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 准确区分 `full_context`、`context_window`、`memo` 三个核心概念
> - [ ] 理解模型上下文预算的分配模型，能手算 context_window 可用空间
> - [ ] 说明为什么默认的滑动窗口策略"很暴力"
> - [ ] 列举 Session 的三件核心职责，并解释它们之间的顺序依赖
> - [ ] 在代码中实现 full_context 与 context_window 的分离管理

---

### 5.1 从"超长了怎么办"出发

在前面的实验中，我们已经把 Session 独立出来，用一个 `sessions` 字典管理每个 `session_id` 对应的消息列表。但这个方案只解决了"怎么存"的问题，却回避了一个更根本的问题：当消息越来越多、超过模型能处理的长度上限时，会发生什么？

#### 🔗 推导链：消息超长的必然性

```
起点: Session 存储了所有历史消息，消息随时间不断增长
  │
  ├── 第1步: 对话越来越长，消息数从几条变成几十条、几百条
  │   为什么？真实的用户对话不会自己截断——用户可能聊几个小时，
  │   消息持续追加，full_context 线性膨胀。
  │
  ├── 第2步: 模型接口有严格的上下文长度上限
  │   为什么？每个模型都有固定的最大上下文窗口（如 GPT-4 为 128K tokens），
  │   这不是我们代码的限制，而是模型服务端的硬约束。
  │   超出部分会直接触发 API 错误，请求被拒绝。
  │
  ├── 第3步: 当消息总量超过模型上限时，必须做出选择
  │   为什么？你不能把 500K tokens 的消息全塞进一个只接受 128K 的接口——
  │   必须有某种策略决定「哪些消息送给模型、哪些不送」。
  │   这个选择不是可选的，是强制性的。
  │
  ├── 第4步: 如果什么都不做，模型底层会用默认策略处理
  │   为什么？模型接口不会报错然后什么都不返回——
  │   大多数接口默认采用「滑动窗口」策略：只保留最近的消息，旧的直接丢弃。
  │   这种策略简单但粗暴。
  │
  └── 结论: Session 不能只负责「存」，还必须负责「选」——
           管理投放给模型的消息子集。这引出了 full_context 和 context_window 的区分。
```

这个推导链直接引出了本模块最核心的两个概念：`full_context` 和 `context_window`。理解它们之间的区别，是理解整个 Session 架构设计的基础。

---

### 5.2 full_context：完整的会话记录

> 🔗 **前置知识**：在 M04 中，我们建立了 `sessions` 字典来存储每个会话的消息列表——那就是 `full_context` 的雏形，但当时还没给它明确的概念定位。

#### 🧠 直观理解

**full_context 是「这段会话真实发生过的全部内容」**。

想象你跟朋友在微信上聊天：从第一句"在吗"到最新的消息，所有聊天记录按时间顺序完整排列。你不会因为消息太多而删除历史记录——那是这段关系的完整记忆。full_context 做的事情完全一样：**用一条条消息记录整段会话的真实历史**。它回答的问题是："这段会话到底聊了什么？"

#### 📖 详细解释

`full_context` 是 Session 对一段会话的完整记忆。它的核心特征有三条：

**特征一：完整性。** full_context 包含从会话创建到当前时刻的每一条消息——用户消息、助手回复、工具调用请求、工具调用结果，一条都不少。它是对"发生了什么"的事实记录。

**特征二：不可变性原则。** 原则上，`full_context` 里的历史消息不应该被修改。已经发生的对话是客观事实——用户在第 3 轮说过"我叫张三"，这条消息就永远在那里。如果后续需要给模型看一个"修改过的版本"，那个版本应该叫 `context_window`，而不是直接去改 `full_context`。

**特征三：只追加。** 新消息通过 `append` 追加到列表末尾，旧消息保持不动。`full_context` 随时间单调增长，永不收缩。

为什么会需要 full_context 这个独立概念？因为"投放给模型的消息子集"不等于"全部消息"。当我们在做裁剪决策时——决定丢弃哪些、保留哪些——必须有一个参考基准。`full_context` 就是那个"全部"的基准。没有它，你无从判断"哪些消息被丢弃了"。

> ⚠️ **注意事项**：`full_context` 原则上不要改。如果你需要给模型看一个经过加工的消息序列（比如用摘要替换了早期细节，或者重新排列了消息顺序），那个加工后的版本应该叫 `context_window`。直接修改 `full_context` 会让"这段会话真实发生过什么"这个问题的答案失真。

#### 💻 代码示例

```python
# 文件名: session_full_context.py
# 功能: 展示 full_context 的基本结构——完整消息链的存储形态

from dataclasses import dataclass, field
from typing import List

@dataclass
class Message:
    """单条消息的数据结构"""
    role: str       # "user" | "assistant" | "tool"
    content: str

@dataclass
class Session:
    """一个会话对象，持有完整的 full_context"""
    session_id: str
    full_context: List[Message] = field(default_factory=list)
    # 关键设计：full_context 只追加，不删除，不修改

    def add_message(self, role: str, content: str) -> None:
        """追加一条消息到 full_context。这是 full_context 唯一的写操作。"""
        self.full_context.append(Message(role=role, content=content))

    def get_full_history(self) -> List[Message]:
        """
        获取完整消息链。
        回答「这段会话真实发生过什么」——
        无论对话多长，返回的都是全部消息，一条不少。
        """
        return self.full_context


# ── 使用示例 ──
session = Session(session_id="abc-123")
session.add_message("user", "你好，我想了解 Python 的异步编程")
session.add_message("assistant", "好的！Python 异步编程的核心是 asyncio 库...")
session.add_message("user", "那 async 和 await 有什么区别？")
session.add_message("assistant", "async 用于定义协程函数，await 用于等待协程结果...")

print(f"full_context 中共有 {len(session.get_full_history())} 条消息")
# 输出: full_context 中共有 4 条消息
# 无论对话多长，full_context 始终保留全部消息——这就是「完整」的含义
```

| 行号 | 代码 | 解释 |
|---|---|---|
| 7-9 | `class Message` | 单条消息的数据结构，`role` 标识消息来源，`content` 存储文本内容 |
| 12-14 | `class Session` | Session 持有 `full_context: List[Message]`，这是它的核心状态 |
| 15 | `field(default_factory=list)` | 每个新 Session 的 full_context 从空列表开始 |
| 18 | `self.full_context.append(...)` | 关键：full_context 唯一的写操作是追加，不做删除或修改 |
| 20-23 | `get_full_history()` | 返回完整消息链。这个方法的存在本身就说明了 full_context 的概念意义 |

---

### 5.3 context_window：投放给模型的消息子集

#### 🧠 直观理解

**context_window 是「本轮请求，模型应该看到的那部分消息」**。

回到微信聊天的类比：full_context 是你和朋友的完整聊天记录（可能几千条）。但当你打开聊天窗口，屏幕上实际显示的只有最近几十条消息。你想要看更早的，需要手动往上翻。**屏幕上当前可见的那部分，就是 context_window**。它回答的问题是："这一轮，模型应该关注什么？"

#### 📖 详细解释

`context_window` 的核心特征同样有三条，而且与 full_context 恰好形成对比：

**特征一：是 full_context 的子集。** context_window 始终从 full_context 中选取，它是全部消息中的一部分。选取哪些、舍弃哪些，由裁剪策略决定。

**特征二：可以裁剪、重排、替换。** 与 full_context 的"不可变性"完全相反，context_window 是经过策略加工后的产物。你可以丢弃旧消息、用摘要替换历史细节、调整消息顺序、注入系统提示。context_window 是"加工品"，full_context 是"原材料"。

**特征三：大小受模型上下文预算严格约束。** context_window 的 token 总量必须控制在模型能接受的范围内。如果超了，要么裁剪，要么请求失败。这个约束是刚性的。

**为什么需要区分 full_context 和 context_window？** 因为"存什么"和"投什么"是两个完全不同的问题。`full_context` 负责"存"——记录历史真相；`context_window` 负责"投"——在模型容量约束下做最优选择。把这两个概念混在一起，会导致要么存储不完整（为了适配窗口而删除了历史），要么投放不合理（把全部历史一股脑塞给模型导致超限）。

##### 模型上下文预算模型（ASCII 图）

老师在白板上画图讲解了这个核心概念。每个模型接口都有一个**总上下文长度上限**，但这个上限不是全部给历史消息用的——你必须预留空间给本轮的用户输入和模型的输出。

```
┌────────────────────── 模型总上下文长度 (120K tokens) ────────────────────┐
│                                                                           │
│  ┌────────────────────────────────────────────┐  ┌──────────────────────┐ │
│  │                                            │  │                      │ │
│  │         CONTEXT WINDOW (100K)              │  │   输入输出预留 (20K)  │ │
│  │                                            │  │                      │ │
│  │  可以投放给模型的历史消息所占的空间          │  │  • 用户最新一次输入  │ │
│  │                                            │  │  • 模型即将生成的    │ │
│  │  回答：「本轮模型应该看什么？」              │  │    输出内容          │ │
│  │                                            │  │                      │ │
│  │  ┌──────┬──────┬──────┬──────┬──────┐     │  │                      │ │
│  │  │ Msg5 │ Msg6 │ Msg7 │ Msg8 │ ...  │     │  │                      │ │
│  │  └──────┴──────┴──────┴──────┴──────┘     │  │                      │ │
│  │                                            │  │                      │ │
│  │  (假设每条消息 25K，最多放 4 条)             │  │                      │ │
│  └────────────────────────────────────────────┘  └──────────────────────┘ │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                    full_context (可能远超 120K)                       │ │
│  │  ┌──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┐  │ │
│  │  │ Msg1 │ Msg2 │ Msg3 │ Msg4 │ Msg5 │ Msg6 │ Msg7 │ Msg8 │ Msg9 │..│ │
│  │  └──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┘  │ │
│  │  ◀──────────── 超出窗口的旧消息（不在 context_window 中）─────────▶  │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘

计算公式:
  context_window 可用空间 = 模型总上下文长度 - 输入输出预留空间
                       100K = 120K - 20K

老师强调：20K 留给输入输出不是拍脑袋的数字，而是工程经验——
你需要为用户的最后一次提问（可能附带长文档）和模型的回答预留足够的空间。
如果把这 20K 也填满历史消息，本轮用户输入就可能被截断。
```

> 💡 **核心洞见**：模型的上下文长度上限是"总预算"，不是"历史消息预算"。你必须从总预算中减去本轮输入输出的预估空间，剩下的才是 context_window 的容量上限。这个减法看起来简单，但很多人在实际开发中会忽略这一点，导致把 context_window 塞得太满，用户最新输入反而被截断了。

#### 🔀 对比辨析：full_context vs context_window

| 维度 | full_context | context_window |
|---|---|---|
| **定义** | 完整消息链，记录全部对话历史 | 本轮投放给模型的消息子集 |
| **回答的问题** | "这段会话真实发生过什么？" | "本轮模型应该看什么？" |
| **是否可变** | 原则上不可变，只追加 | 可以裁剪、重排、替换、注入 |
| **大小** | 无上限，随时间线性增长 | 受模型上下文预算严格约束（如 100K tokens） |
| **存储位置** | Session 的持久状态 | 每次请求时动态计算生成 |
| **类比** | 完整的聊天记录——"全部历史" | 屏幕上当前可见的消息——"当下关注" |
| **设计原则** | 记录真相，不做加工 | 在约束下做最优选择 |

#### 💻 代码示例

```python
# 文件名: context_window_builder.py
# 功能: 展示 context_window 如何从 full_context 中构建

from dataclasses import dataclass, field
from typing import List

@dataclass
class Message:
    role: str
    content: str

@dataclass
class Session:
    session_id: str
    full_context: List[Message] = field(default_factory=list)
    context_window: List[Message] = field(default_factory=list)

    def build_context_window(self, max_tokens: int = 100_000) -> List[Message]:
        """
        从 full_context 中构建 context_window。
        关键：context_window 是 full_context 的子集，经过策略加工。
        当前使用简单的 token 计数从尾部反推——后续会被 handler 管线替代。
        """
        estimated_tokens = 0
        selected = []

        # 从最新消息向旧消息反推，直到填满窗口
        for msg in reversed(self.full_context):
            msg_tokens = len(msg.content) // 4  # 粗略估算
            if estimated_tokens + msg_tokens > max_tokens:
                break  # 窗口已满，停止添加
            selected.insert(0, msg)
            estimated_tokens += msg_tokens

        self.context_window = selected
        return self.context_window


# ── 使用示例 ──
session = Session(session_id="ctx-demo")
# 模拟大量消息...
for i in range(50):
    session.full_context.append(
        Message("user", f"这是第 {i} 条消息，" + "内容 " * 100)
    )

window = session.build_context_window(max_tokens=2000)
print(f"full_context: {len(session.full_context)} 条消息")
print(f"context_window: {len(window)} 条消息（从尾部选取）")
# context_window 只包含最近的部分消息——这就是「子集」的含义
```

---

### 5.4 滑动窗口：模型默认的裁剪策略

#### 🧠 直观理解

当你什么都不做，直接把超长的消息列表发给模型接口时，模型底层会采用一种最简单的策略：**只保留最近的 N 条消息，把前面的全部丢弃，就像一个向右滑动的固定大小的窗口**。

这就像你站在一条传送带旁边看包裹经过：传送带不断向右移动，你只能看到你面前窗口范围内的包裹。已经经过的包裹（早期消息），无论里面装的是什么（多重要的信息），你都再也看不到了。

#### 📖 详细解释

"滑动窗口"是大型语言模型接口处理超长输入时的默认行为。它的核心逻辑极其简单：

1. 设定一个固定大小的窗口（以 token 数或消息条数为单位）
2. 把所有消息按时间顺序排列
3. 只保留窗口范围内的最新消息
4. 窗口随着新消息的到来，不可逆地向右滑动

这种策略**不做任何语义分析**——它不判断哪条消息重要、哪条消息包含关键偏好、哪条消息是任务目标。它只看时间：越新的消息越可能被保留，越旧的消息越可能被丢弃。

##### 滑动窗口的工作过程（ASCII 图）

```
full_context (完整消息链，随时间不断向右增长):
═══════════════════════════════════════════════════════════════════════════════
┌──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┐
│ Msg1 │ Msg2 │ Msg3 │ Msg4 │ Msg5 │ Msg6 │ Msg7 │ Msg8 │ Msg9 │Msg10 │Msg11 │
└──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┘
  ◀────────────────────────── 时间增长方向 ──────────────────────────────▶

假设 context_window 容量 = 4 条消息:

时刻 T1 (第4轮对话结束，消息量未超窗口):
┌──────┬──────┬──────┬──────┐ ┌──────┬──────┬──────┬──────┐
│ Msg1 │ Msg2 │ Msg3 │ Msg4 │ │ Msg5 │ Msg6 │ Msg7 │ ...  │
└──────┴──────┴──────┴──────┘ └──────┴──────┴──────┴──────┘
└──── context_window: [Msg1, Msg2, Msg3, Msg4] ────┘  ← 全部保留

时刻 T2 (第6轮对话结束，窗口开始向右滑动):
              ┌──────┬──────┬──────┬──────┐
  Msg1, Msg2 │ Msg3 │ Msg4 │ Msg5 │ Msg6 │ Msg7, Msg8 ...
              └──────┴──────┴──────┴──────┘
  ◀──丢弃──▶ └── context_window: [Msg3, Msg4, Msg5, Msg6] ──┘
  Msg1、Msg2 被窗口丢弃——无论它们的内容是什么

时刻 T3 (第10轮对话结束，窗口继续向右滑动):
                              ┌──────┬──────┬──────┬──────┐
  ..., Msg5, Msg6, Msg7, Msg8 │ Msg9 │Msg10 │Msg11 │Msg12 │
                              └──────┴──────┴──────┴──────┘
  ◀────────── 全部丢弃 ──────▶└ context_window: [Msg9, Msg10, Msg11, Msg12] ─┘
  Msg1-Msg8 全部被丢弃——对话最早期的信息完全消失
```

关键观察：

- **窗口大小固定**（此处为 4 条消息），不随对话长度变化
- **窗口像传送带一样单向滑动**，只有"向右"一个方向，从不回头
- **一旦某条消息滑出窗口左侧，它就永远不能被模型看到了**
- **窗口不判断消息的重要性**——即使是"请记住我叫张三"这样的关键身份信息，也会和新消息一视同仁，到期后被无情丢弃

#### 💻 代码示例

```python
# 文件名: sliding_window_demo.py
# 功能: 模拟模型默认的滑动窗口裁剪策略，展示「暴力裁剪」的后果

from dataclasses import dataclass
from typing import List

@dataclass
class Message:
    role: str
    content: str

    def __repr__(self) -> str:
        return f"[{self.role}]: {self.content[:40]}..."


def sliding_window_cut(full_context: List[Message], window_size: int) -> List[Message]:
    """
    模拟模型的默认滑动窗口裁剪策略。
    不做任何语义分析，直接保留最近的 window_size 条消息。
    这是最朴素、也最暴力的裁剪方式。
    """
    if len(full_context) <= window_size:
        return full_context.copy()  # 没超长，全部保留
    # 暴力裁剪：只取最后 window_size 条，其余全部丢弃
    return full_context[-window_size:]


# ── 模拟一段对话 ──
messages: List[Message] = []
messages.append(Message("user", "你好，我叫张三，请记住我的名字"))
messages.append(Message("assistant", "好的张三，我已经记住了"))
messages.append(Message("user", "我想订一张去北京的机票"))
messages.append(Message("assistant", "请问您想从哪个城市出发？"))
messages.append(Message("user", "从上海出发"))
messages.append(Message("assistant", "好的，正在为您查询上海到北京的航班..."))
messages.append(Message("user", "我的名字是什么？"))  # 第7条——此时第1条已不在窗口中

window_size = 4
context_window = sliding_window_cut(messages, window_size)

print(f"full_context 共 {len(messages)} 条消息")
print(f"context_window 仅保留 {len(context_window)} 条消息")
print("\ncontext_window 中的内容:")
for msg in context_window:
    print(f"  {msg}")

# ── 观察结果 ──
# full_context 共 7 条消息
# context_window 仅保留 4 条消息
#
# context_window 中的内容:
#   [assistant]: 请问您想从哪个城市出发？...
#   [user]: 从上海出发...
#   [assistant]: 好的，正在为您查询上海到北京的航班...
#   [user]: 我的名字是什么？...
#
# 致命问题：包含"我叫张三"的消息（第1条）已经被窗口丢弃。
# 模型收到的 context_window 中不包含任何关于用户名字的信息——
# 面对"我的名字是什么？"这个问题，模型将无法正确回答。
```

---

### 5.5 为什么"暴力裁剪"不够好

石野同学在课上提出了一个精准的观察："他怎么这么暴力？" 这个直觉完全正确，而且直接点出了 Session 需要更多职责的根本原因。

**暴力裁剪的核心缺陷**：它把"信息的新旧"等同于"信息的重要程度"。在滑动窗口的视角里，一条消息的唯一属性就是它在时间轴上的位置——越新的越重要，越旧的越不重要。但真实对话中，信息的重要性与时间没有必然关系。

| 问题 | 具体现象 | 业务后果 |
|---|---|---|
| **丢失关键上下文** | 用户在对话开头说的偏好、约束、身份信息（"我叫张三"、"预算 5000"、"不吃辣"）被窗口丢弃 | 模型给出不符合用户偏好和约束的回答，用户体验骤降 |
| **丢失任务目标** | 最早提出的任务目标（"帮我规划北京三日游"）滑出窗口 | 模型"忘记我们本来在做什么"，开始胡言乱语或给出无关回答 |
| **ChatML 结构断裂** | 工具调用请求（tool_call）和对应的工具返回结果（tool_result）可能被窗口分界线切开——请求在窗口内，结果被丢弃了 | 模型看到"孤儿"工具结果或找不到对应请求，解析失败或行为异常 |
| **滚动遗忘** | 随着窗口滑动，模型对对话前期内容的所有记忆归零 | 用户需要不断重复信息（"我再跟你说一遍，我叫张三..."），体验极差 |
| **无差别丢弃** | 系统提示（system prompt）和普通对话消息被同等对待 | 如果 system prompt 被滑出窗口，模型的行为约束完全失效 |

> 💡 **核心洞见**：默认的滑动窗口策略是"懒惰的合理"——它的实现成本为零（甚至不是我们写的代码，是模型接口自带的），在闲聊场景中勉强可用。但一旦进入复杂业务场景——客服系统、教学助手、代码助手、医疗问诊——这种"什么都不做"的策略完全不够用。**我们需要更聪明的裁剪策略，这就是 Session 的第二、第三件职责存在的原因。**

---

### 5.6 Session 的三件核心职责

现在我们可以回答本模块最核心的问题：**Session 到底应该做什么？** 在前面的分析中，我们已经看到：只存消息是不够的。Session 需要承担三个递进的职责。

#### 📋 三件职责表

| 职责编号 | 职责名称 | 具体内容 | 操作的对象 | 回答的问题 |
|---|---|---|---|---|
| **职责一** | 会话信息存取 | 存储 full_context（完整消息链）、维护 context_window（当前投放子集）、可选维护 memo（摘要/备忘） | `full_context`、`context_window`、`memo` | "这段会话有什么？" |
| **职责二** | 会话长度/状态分析 | 计算当前消息总量（token 数）、判断是否超出模型预算、标记风险状态（安全/警告/超限）、统计对话轮次 | `full_context` 的长度、token 估算结果、turn count | "当前状态安全吗？需要裁剪吗？" |
| **职责三** | 裁剪/压缩执行 | 根据职责二的分析结果，对 context_window 执行裁剪策略：简单截断、摘要压缩、结构化字段替换、优先级排序裁剪等 | `context_window`（从 `full_context` 中选取并加工） | "模型这次应该看到什么？" |

这三件职责之间存在清晰的**顺序依赖关系**：

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│                     │     │                      │     │                      │
│   职责一: 存取       │────▶│   职责二: 分析        │────▶│   职责三: 裁剪执行    │
│                     │     │                      │     │                      │
│ 存下所有消息         │     │ 消息超模型预算了吗？   │     │ 选取/压缩消息子集     │
│ • full_context      │     │ 还剩多少 tokens？     │     │ 生成 context_window  │
│ • context_window    │     │ 风险级别是什么？       │     │ 注入 memo           │
│ • memo（可选）       │     │ 需要裁剪哪些消息？     │     │                      │
│                     │     │                      │     │                      │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
        存储是基础                   分析是决策依据                 裁剪是执行动作
```

> ⚠️ **注意事项**：职责一和职责二是两个不同的维度，不可混为一谈。光存下来不够——只存不分析，就是我们在前面实验中做的：消息无限增长，最终要么模型报错，要么被底层暴力裁剪。**存储是基础，分析是决策依据，裁剪是执行动作。** 三件缺一不可。

#### 💻 代码示例

```python
# 文件名: session_three_duties.py
# 功能: 展示 Session 三件职责的基本代码框架
#       这是后续 handler 管线架构的概念基础

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from enum import Enum


class RiskLevel(Enum):
    """会话风险级别——职责二的输出之一"""
    SAFE = "safe"          # 安全：消息量远低于预算，无需裁剪
    WARNING = "warning"    # 警告：接近预算上限，需要关注
    CRITICAL = "critical"  # 危险：已超出预算，必须立即裁剪


@dataclass
class Message:
    """单条消息"""
    role: str       # "user" | "assistant" | "tool" | "system"
    content: str


@dataclass
class Session:
    """具备三件职责的完整 Session 对象"""
    session_id: str

    # ══════════════ 职责一：会话信息存取 ══════════════
    full_context: List[Message] = field(default_factory=list)
    context_window: List[Message] = field(default_factory=list)
    memo: Optional[str] = None  # 可选的短期摘要，用于弥补被裁剪的历史

    # ══════════════ 职责一（辅助方法） ══════════════
    def add_message(self, role: str, content: str) -> None:
        """追加消息到 full_context。——职责一的核心操作"""
        self.full_context.append(Message(role=role, content=content))

    # ══════════════ 职责二：会话长度/状态分析 ══════════════
    max_window_tokens: int = 100_000  # context_window 的 token 预算上限

    def estimate_tokens(self, messages: List[Message]) -> int:
        """
        估算消息列表的 token 消耗。
        生产环境建议使用 tiktoken 库进行精确计算。
        """
        total_chars = sum(len(m.content) for m in messages)
        return total_chars // 4  # 粗略估算：英文约 4 字符/token，中文约 1.5-2 字符/token

    def analyze_risk(self) -> Tuple[RiskLevel, int, float]:
        """
        分析当前会话的风险状态。——职责二的核心方法
        返回 (风险级别, 已用 tokens, 使用比例)
        """
        used_tokens = self.estimate_tokens(self.full_context)
        ratio = used_tokens / self.max_window_tokens

        if ratio < 0.7:
            return RiskLevel.SAFE, used_tokens, ratio
        elif ratio < 1.0:
            return RiskLevel.WARNING, used_tokens, ratio
        else:
            return RiskLevel.CRITICAL, used_tokens, ratio

    # ══════════════ 职责三：裁剪/压缩执行 ══════════════
    def build_context_window(self, max_messages: int = 20) -> List[Message]:
        """
        根据风险分析结果构建 context_window。——职责三的核心方法
        当前为简单截断示例（仅保留最近 N 条）。
        后续 M06/M07 将用 handler 管线替换为智能裁剪策略。
        """
        risk, used, ratio = self.analyze_risk()

        if risk == RiskLevel.SAFE:
            # 安全状态：全部保留，无需裁剪
            self.context_window = self.full_context.copy()
        else:
            # 警告或危险状态：保留最近的 max_messages 条
            # TODO: M06/M07 将替换为智能 handler 管线
            self.context_window = self.full_context[-max_messages:]

        return self.context_window


# ── 使用示例 ──
session = Session(session_id="demo-001")
session.add_message("user", "你好，我叫张三，我想规划一次北京三日游")
session.add_message("assistant", "好的张三！请问你的预算和偏好是什么？")
session.add_message("user", "预算 5000 元，我不吃辣")

risk, tokens, ratio = session.analyze_risk()
print(f"风险级别: {risk.value} | 已用 tokens: {tokens} | 使用比例: {ratio:.1%}")

window = session.build_context_window(max_messages=4)
print(f"context_window 包含 {len(window)} 条消息")
```

| 行号 | 代码 | 解释 |
|---|---|---|
| 12-15 | `RiskLevel` 枚举 | 定义三种风险级别，是职责二 `analyze_risk()` 的返回值类型 |
| 29-32 | `full_context`, `context_window`, `memo` | 职责一的三个核心字段，分别对应完整记录、投放子集、历史摘要 |
| 38-40 | `add_message()` | 职责一的核心操作：向 full_context 追加消息 |
| 43 | `max_window_tokens` | 职责二的配置参数：context_window 的 token 预算上限 |
| 45-49 | `estimate_tokens()` | 职责二的基础工具：用字符数估算 token 消耗 |
| 51-60 | `analyze_risk()` | 职责二的核心方法：计算使用比例，返回风险级别 |
| 63-76 | `build_context_window()` | 职责三的核心方法：根据风险级别决定裁剪策略 |

---

### 5.7 memo：可选的短期摘要

#### 🧠 直观理解

**memo 是对「被窗口丢弃的旧消息」的压缩摘要**。

想象你开完一个两小时的会议后写会议纪要：你不会把每个人的每句话都记下来（那是 full_context），你会提炼关键决定、待办事项和重要结论——只用半页纸。这份纪要就是 memo。它非常短，但保留了最重要的信息。下次开会前，你看一眼纪要就能回忆起来上次说了什么。

#### 📖 详细解释

memo 的设计动机直接来自于滑动窗口的缺陷：当 context_window 必须丢弃旧消息时，我们希望能以某种方式**保留旧消息中的关键信息**。memo 就是这个"压缩版本"。

memo 的核心特征：

1. **可选性**：不是每个 Session 都需要 memo。如果对话很短、消息量远未超出窗口，memo 就是多余的
2. **压缩性**：memo 应该是 full_context 的高度压缩版本，通常是一段短文（几百字），保存了被裁剪部分的核心要点
3. **可注入性**：memo 可以被注入到 context_window 中——通常作为一条 system 消息放在窗口最前面——让模型知道"前面大致发生了什么"
4. **可更新性**：随着对话的进行，memo 可以增量更新。新的关键信息被追加，旧的信息可以被提炼

> ❓ **常见疑问**：memo 和 context_window 尾部保留的消息有什么区别？为什么不直接多保留几条消息？
>
> **回答**：context_window 尾部保留的消息只包含"最近发生了什么"，不包含"很久以前的关键信息"。举个例子——用户在对话开头说"我不吃辣"，到了第 100 轮，这句话早被窗口丢弃了。如果只保留尾部消息，模型不知道这个偏好。memo 可以记录"用户饮食偏好：不吃辣"——一个 10 字的摘要，替代了可能 100 字的历史细节。这是一种**用空间换信息密度**的策略。

#### 💻 代码示例

```python
# 文件名: memo_example.py
# 功能: 展示 memo 如何在 context_window 中发挥作用

from typing import List, Dict, Optional

class SessionWithMemo:
    """带有 memo 能力的 Session"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.full_context: List[Dict[str, str]] = []
        self.memo: Optional[str] = None  # 初始为空

    def add_message(self, role: str, content: str) -> None:
        """追加消息到 full_context"""
        self.full_context.append({"role": role, "content": content})

    def update_memo(self, new_summary: str) -> None:
        """
        更新 memo。
        可以用 LLM 对已被裁剪的旧消息做摘要后调用此方法。
        """
        self.memo = new_summary

    def build_context_window(self, recent_count: int = 4) -> List[Dict[str, str]]:
        """
        构建 context_window:
        1. 如果有 memo，作为 system 消息注入到窗口最前面
        2. 追加最近的 recent_count 条消息
        """
        window: List[Dict[str, str]] = []

        # 如果有 memo，注入为 system 消息
        if self.memo:
            window.append({
                "role": "system",
                "content": f"[历史摘要] {self.memo}"
            })

        # 追加最近的消息
        window.extend(self.full_context[-recent_count:])
        return window


# ── 模拟使用场景 ──
session = SessionWithMemo("memo-demo")

# 模拟大量历史对话后，早期消息已被裁剪...
# 我们用一个 LLM 调用对前 50 轮对话做了摘要
session.update_memo(
    "用户叫张三，来自上海，偏好不吃辣，预算 5000 元。"
    "当前任务：帮忙规划一次北京三日游。"
    "已确定：故宫门票 60 元，长城一日游 200 元。"
)

# 最近的几条消息
session.add_message("user", "故宫门票多少钱？")
session.add_message("assistant", "故宫旺季门票 60 元，需要提前预约...")

window = session.build_context_window(recent_count=2)
print("context_window 内容:")
for msg in window:
    content_preview = msg["content"][:60]
    print(f"  [{msg['role']}]: {content_preview}...")

# ── 输出 ──
# context_window 内容:
#   [system]: [历史摘要] 用户叫张三，来自上海，偏好不吃辣，预算 5000 元...
#   [user]: 故宫门票多少钱？...
#   [assistant]: 故宫旺季门票 60 元，需要提前预约...
#
# 关键观察：
# - 虽然早期 50 轮消息被裁剪了，模型仍能通过 memo 知道用户的关键信息
# - memo 被包装为 system 消息，放在窗口最前面，确保模型优先读取
# - 10 字摘要（"偏好不吃辣"）替代了可能几百字的历史细节
```

#### 🔀 关键概念区分：full_context / context_window / memo

这是本模块三个最核心的概念，必须放在一起对比才能看清它们各自的位置：

| 维度 | full_context | context_window | memo |
|---|---|---|---|
| **是什么** | 完整消息链 | 投放给模型的消息子集 | 被丢弃历史的压缩摘要 |
| **回答的问题** | "真实发生过什么？" | "模型这次应该看什么？" | "前面大致说了什么？" |
| **大小** | 无上限，随时间线性增长 | 受模型预算约束（如 100K tokens） | 很短（通常几百字到一两千字） |
| **可否修改** | 原则上不可改，只追加 | 可以裁剪、重排、替换、注入 | 可以增量更新、覆盖 |
| **是否必须** | 必须（Session 的根本） | 必须（每次请求都要构建） | 可选（简单场景不需要） |
| **存储形式** | `List[Message]` | `List[Message]` | `str` 或结构化字典 |
| **生成时机** | 每条消息产生时立即追加 | 每次请求模型前动态构建 | 裁剪发生时、或定期批量生成 |
| **类比** | 完整会议录音 | 当前讨论窗口中的内容 | 会议纪要 |

> 💡 **核心洞见**：这三个概念构成一个"信息漏斗"——full_context（海量原始数据） → context_window（按预算选取） → memo（压缩遗留信息注入窗口）。从完整到精选，从原始到压缩，每一层都在回答一个不同的问题。

---

### 5.8 Session 的边界定位：两个「避免」

在理解了 Session 的三件职责和三个核心概念后，还需要明确 Session **不是什么**。职责越清晰，边界越重要。以下是两个需要有意避免的陷阱。

#### 避免一：避免「只存不分析」

这是我们在前面实验中实际犯过的错误。`session.messages.append(msg)` 只是完成了职责一的"存取"部分。如果到此为止，Session 就是一个**带 ID 的消息列表**——它不关心消息是否超长、不关心模型能不能处理、不关心裁剪策略是否合理。

> ❓ **常见误解**："Session 就是一个字典嘛，存消息用的，有什么好设计的？"
>
> **纠正**：如果 Session 只是存消息的字典，那它和 `dict[str, list]` 没有任何区别——不需要封装成类，不需要独立模块。Session 的价值恰恰在于**职责二（分析）和职责三（裁剪）**——知道什么时候该裁剪、该怎么裁剪。这才是 Session 作为独立模块存在的设计理由。一个只会 `append` 的 Session，不如直接用 Python 原生的 `defaultdict(list)`。

#### 避免二：避免一开始就处理跨会话长期状态

Session 的职责范围是**单个会话内**的上下文管理。用户跨会话的长期偏好（如"我是高级会员"）、跨会话的记忆（如"三个月前我跟你说过..."）不应该放进 Session。

| Session 应该管的 | Session 不应该管的 |
|---|---|
| ✅ 当前会话的消息存取（full_context） | ❌ 跨会话的用户偏好存储 |
| ✅ 当前会话的长度分析和风险判断 | ❌ 长期记忆的持久化和检索 |
| ✅ 当前会话的 context_window 构建 | ❌ 用户画像的维护和更新 |
| ✅ 当前会话的 memo 生成和管理 | ❌ 外部知识库的检索和注入 |

> 🔗 **延伸阅读**：跨会话的长期记忆管理，将在后续课程中引入独立的 **Memory 模块**来实现。Session 专注于单会话内的上下文管理，Memory 负责跨会话的持久化知识——这是保持架构清晰的关键边界划分。过早把长期记忆塞进 Session，会导致 Session 职责膨胀、代码耦合、难以测试。

---

### 🗺️ 本模块知识图谱

```
                         ┌─────────────────────────────────┐
                         │   Session 三件核心职责是什么？     │
                         │   存取 → 分析 → 裁剪执行          │
                         └───────────────┬─────────────────┘
                                         │
                ┌────────────────────────┼────────────────────────┐
                ▼                        ▼                        ▼
      ┌─────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
      │   职责一: 存取    │    │   职责二: 分析        │    │   职责三: 裁剪执行    │
      │                  │    │                      │    │                      │
      │ • full_context   │───▶│ • 估算 token 用量     │───▶│ • 构建 context_window│
      │ • context_window │    │ • 判断风险级别        │    │ • 执行裁剪策略        │
      │ • memo           │    │ • 决定是否需要裁剪    │    │ • 注入 memo          │
      └───────┬──────────┘    └─────────────────────┘    └──────────┬──────────┘
              │                                                     │
              ▼                                                     ▼
      ┌───────────────┐                                 ┌───────────────────────┐
      │  full_context │                                 │    context_window     │
      │               │                                 │                        │
      │ "真实发生过     │                                 │ "模型这次应该看什么？"    │
      │  什么？"       │                                 │                        │
      │               │                                 │  ┌─────────────────┐  │
      │ 不可变         │                                 │  │  memo (可选)     │  │
      │ 只追加         │                                 │  │ "前面大致说了啥"  │  │
      │ 无上限         │                                 │  │ 可注入到窗口中    │  │
      └───────────────┘                                 │  └─────────────────┘  │
                                                        │ 可裁剪, 可重排        │
                                                        │ 受模型预算约束        │
                                                        └───────────────────────┘
```

### 💡 一句话总结

> Session 不是带 ID 的消息列表，而是一个**知道什么时候该裁剪、该怎么裁剪的上下文管理器**——full_context 记录真相，context_window 做出选择，memo 弥补遗憾。三件职责（存取→分析→裁剪）构成了 Session 的完整能力闭环。

> 🔗 **延伸阅读**：本文 [第六章：Handler 管线架构] 将基于本模块建立的 context_window 概念，引入可扩展的分析处理器和压缩处理器管线，把「暴力裁剪」替换为「智能裁剪策略链」。（← 合并时替换为锚点链接）

## 六、Handler 管线架构：分析器与压缩器

### 6.1 从"暴力裁剪"到"智能压缩"

> 🎯 **本节目标**：理解 Session 内部的 handler 管线架构——analysis handler 发现问题，resize handler 修正窗口。

#### 🧠 直观理解

M05 暴露了滑动窗口的"暴力"——不管消息重不重要，超出的就扔掉。但真实业务中，有些消息绝对不能丢（比如"预算上限 20 万"），有些消息丢了也没关系（比如"好的"、"收到"）。

所以我们需要两个角色：
- **观察者（分析器）**：看看 context_window 现在什么状态，需要处理吗？用什么策略？
- **执行者（压缩器）**：按照指定的策略，对窗口做裁剪或压缩。

**生活类比**：交通管制中心——先观察路况（哪个路段堵了？堵到什么程度？），再决定限流策略（分流？限速？封路？）。观察和决策是两个独立的环节。

### 6.2 Session 内部的两个关键行为

Session class 内部有两个最基本的操作：

```
┌──────────────────────────────────────────────┐
│  Session 的两个固定行为（用户不能动）            │
│                                              │
│  ① add_message(msg)                          │
│     └─ 把新消息追加到 full_context             │
│                                              │
│  ② get_context_window()                      │
│     └─ 返回本轮投放给模型的 context_window     │
│                                              │
│  中间可以插入:                                 │
│  ┌──────────────────────────────────────┐    │
│  │ analysis handler → resize handler     │    │
│  │ (可插拔的策略逻辑)                     │    │
│  └──────────────────────────────────────┘    │
└──────────────────────────────────────────────┘
```

### 6.3 完整时序流程

老师在白板上逐步画出了这个流程，以下是完整的时序图：

```
时间线 →
  
  新消息进入
      │
      ▼
  ┌─────────────┐
  │ add_message  │  ← 固定行为：消息追加到 full_context
  └──────┬──────┘
         │
         │  自动触发（auto_resize=True）或手动触发（async_resize()）
         ▼
  ┌──────────────────────┐
  │  analysis handler     │  ← 可插拔：观察者/分析者
  │  ┌─────────────────┐ │
  │  │ 输入:            │ │
  │  │ - full_context   │ │
  │  │ - context_window │ │
  │  │ - memo           │ │
  │  │ - settings       │ │
  │  └─────────────────┘ │
  │  ┌─────────────────┐ │
  │  │ 输出:            │ │
  │  │ - 策略名 或 None │ │
  │  └─────────────────┘ │
  └──────┬───────────────┘
         │
         │ 返回策略名 → 调用对应的 resize handler
         │ 返回 None   → 跳过，不处理
         ▼
  ┌──────────────────────┐
  │  resize handler       │  ← 可插拔：执行者/压缩者
  │  ┌─────────────────┐ │
  │  │ 输入: (同上)      │ │
  │  └─────────────────┘ │
  │  ┌─────────────────┐ │
  │  │ 输出 (三返回值):   │ │
  │  │ 1. new_full_context│ │  ← 通常返回 None (不改)
  │  │ 2. new_context_win │ │  ← 裁剪/压缩后的窗口
  │  │ 3. new_memo        │ │  ← 更新后的摘要
  │  └─────────────────┘ │
  └──────┬───────────────┘
         │
         ▼
  ┌──────────────────┐
  │ 更新 context_window│
  │ 和 memo           │
  └──────────────────┘
         │
         ▼
  下次 get_context_window()
  返回新的窗口
```

> 💡 **一句话记住**：**analysis handler 发现问题，resize handler 修正窗口。完整历史和本轮窗口要分开处理。**

### 6.4 触发机制详解

| 步骤 | 代码中的体现 | 发生了什么 |
|---|---|---|
| 1. 写入历史 | `async_add_chat_history(MESSAGES)` | 消息先进入 `full_context` 和 `context_window` |
| 2. 触发分析 | `async_resize()`（手动）或自动触发 | Session 调用 analysis handler，判断要不要处理 |
| 3. 选择策略 | `choose_strategy(...)` 返回策略名 | 返回 `"sliding_window"` 或 `"key_fields_compress"`；返回 `None` 表示不处理 |
| 4. 执行策略 | `register_resize_handler(...)` 注册的函数 | Session 用策略名找到 resize handler，改写 `context_window` 和 `memo` |

> ⚠️ **关键区分**：触发点不是 resize handler 自己，而是 `async_resize()`；选择权在 analysis handler；执行权在 resize handler。三者各司其职。

### 6.5 策略场景全景表

不同业务对"可以丢什么、要保留什么、什么时候压缩"的答案不一样：

| 场景 | 更适合的处理方式 | 触发时机 |
|---|---|---|
| 普通客服 FAQ | 直接裁掉寒暄、重复确认、已关闭问题 | 超过长度阈值时 |
| 合同审查 | 压缩成已确认条款、风险点、材料 ref，不直接丢早期约束 | 每轮修改后或超过预算前 |
| 运维排障 | 保留命令、错误码、时间线，压缩解释性文字 | 每 N 轮或新阶段开始时 |
| 投研尽调 | 保留来源、证据、假设和未验证结论的边界 | 每轮都要分析风险状态 |
| 企业 IM 助手 | 直接裁剪闲聊，但保留任务归属、回调目标和审批状态 | webhook 进入时先分析 |

### 6.6 常见策略分类

这些策略都只作用在当前 Session 的 `context_window` 和 `memo` 上：

| 策略 | 怎么处理 | 适合什么场景 |
|---|---|---|
| **滑动窗口** | 保留最近若干轮，超出部分直接移出本轮窗口 | 闲聊、FAQ、低风险问答 |
| **角色优先级裁剪** | 保留当前用户问题和关键系统约束，优先裁掉冗长解释和已完成分支 | 指令结构比较稳定的助手 |
| **关键字段压缩** | 把早期对话压成 `已确认约束`、`待确认问题`、`材料 ref` | 合同审查、表单补全、审批问答 |
| **阶段摘要** | 把已结束阶段压成一段短摘要，当前阶段保留原始消息 | 排障、咨询、项目推进 |
| **证据引用保留** | 正文不进窗口，只保留来源、ref、摘要和必要片段 | 文件审查、网页材料较多场景 |
| **时间线压缩** | 把命令、错误码、状态变化按时间顺序压成事件列表 | 运维排障、调试助手、客服工单 |
| **定期重整** | 每 N 轮或每次阶段切换时做一次分析 | 长对话、多人协作、IM 群聊 |

### 6.7 核心架构洞察

> 💡 **核心洞见**：Session 从"一个字典加一个列表"升级为"一个带有可插拔处理管线的类"。关键在于——**核心行为固定（add_message / get_context_window），中间处理可插拔（analysis handler / resize handler）**。

```
Session Class 的设计:
┌────────────────────────────────────────┐
│  class Session:                        │
│      messages: list          ← 数据    │
│      full_context: list      ← 数据    │
│      context_window: list    ← 数据    │
│      memo: str               ← 数据    │
│                                        │
│      add_message(msg)        ← 固定方法 │
│      get_context_window()    ← 固定方法 │
│                                        │
│      register_analysis_handler(fn)  ← 插件注册 │
│      register_resize_handler(name, fn) ← 插件注册 │
│      async_resize()          ← 触发方法 │
└────────────────────────────────────────┘
```

> 🔗 **关联知识**：handler 中的 analysis 逻辑也可以用语言模型来做判断（例如分析风险状态），这是下节课 Memory 管理的前置能力。

## 七、Handler 代码实战：策略注册与执行演示

> 🎯 **本节目标**：掌握 `register_analysis_handler()` 和 `register_resize_handler()` 的使用方法，能独立实现和注册自定义策略。

### 7.1 准备工作：创建 Session 并构造测试数据

```python
from agently.core import Session

# 故意准备 7 条消息，超过 analysis handler 的触发阈值 5
MESSAGES = [
    {"role": "user", "content": "系统约束：只输出可执行建议。"},
    {"role": "assistant", "content": "已记录系统约束。"},
    {"role": "user", "content": "预算上限是 20 万。"},
    {"role": "assistant", "content": "已记录预算。"},
    {"role": "user", "content": "合同正文 ref=inputs/contract-v1。"},
    {"role": "assistant", "content": "已记录合同正文引用。"},
    {"role": "user", "content": "当前问题：现在能不能直接签？"},
]
```

### 7.2 Step 1: 实现 analysis handler

```python
async def choose_strategy(full_context, context_window, memo, session_settings):
    """分析处理器：只做判断，不改数据。
    
    输入:
      - full_context: 完整的消息历史
      - context_window: 当前上下文窗口
      - memo: 当前备忘/摘要
      - session_settings: Session 的配置信息
    
    输出:
      - 策略名（字符串）→ 触发对应的 resize handler
      - None → 不触发任何策略
    """
    if len(context_window) >= 5:
        # 从 settings 中获取策略名（灵活配置）
        return session_settings.get("demo_strategy", "sliding_window")
    return None  # 不需要处理
```

> ⚠️ **注意事项**：analysis handler 的返回值**必须**能在 `register_resize_handler()` 中找到对应的注册名。如果返回了不存在的策略名，会触发错误。

### 7.3 Step 2: 实现 resize handler

**策略 A：简单滑动窗口**

```python
async def sliding_window(full_context, context_window, memo, session_settings):
    """滑动窗口策略：只保留最近 4 条消息。
    
    三返回值:
      1. new_full_context: None 表示不改动完整历史
      2. new_context_window: 裁剪后的窗口
      3. new_memo: 更新后的备忘
    """
    # full_context 永远不动
    new_full_context = None
    # 只保留最近 4 条
    new_context_window = list(context_window[-4:])
    # memo 不变
    new_memo = memo
    return new_full_context, new_context_window, new_memo
```

**策略 B：关键字段压缩 + memo 生成**

```python
async def key_fields_compress(full_context, context_window, memo, session_settings):
    """关键字段压缩：把早期对话中的关键信息压入 memo，窗口只保留最近 3 条。"""
    # 模拟从完整历史中提取关键信息
    extracted_memo = (
        "已确认约束：预算上限 20 万\n"
        "材料 ref：inputs/contract-v1"
    )
    # 窗口只保留最近 3 条
    new_context_window = list(context_window[-3:])
    return None, new_context_window, extracted_memo
```

### 7.4 Step 3: 注册并执行

```python
async def run_strategy(strategy_name, handler):
    """演示完整的注册→添加消息→触发 resize 流程"""
    session = Session(
        id=f"demo-{strategy_name}",
        auto_resize=False,  # 关闭自动触发，手动控制时机
        settings={"session": {"demo_strategy": strategy_name}},
    )
    
    # 注册分析器
    session.register_analysis_handler(choose_strategy)
    # 注册执行器（策略名和 handler 绑定）
    session.register_resize_handler(strategy_name, handler)
    
    # 添加消息
    await session.async_add_chat_history(MESSAGES)
    
    # 手动触发 resize 流程:
    # 1. Session 先调用 choose_strategy() → 得到策略名
    # 2. 再调用对应 resize handler → 修改 context_window 和 memo
    await session.async_resize()
    
    # 查看结果
    print(f"\n== {strategy_name} ==")
    print("context_window 条数：", len(session.context_window))
    print("memo：", session.memo or "[空]")
    for msg in session.context_window:
        print("-", msg.content)

# 运行两个策略的对比演示
await run_strategy("sliding_window", sliding_window)
await run_strategy("key_fields_compress", key_fields_compress)
```

### 7.5 执行结果与对比

**sliding_window 策略输出：**
```
== sliding_window ==
context_window 条数：4
memo：[空]
- 已记录预算。
- 合同正文 ref=inputs/contract-v1。
- 已记录合同正文引用。
- 当前问题：现在能不能直接签？
```

**key_fields_compress 策略输出：**
```
== key_fields_compress ==
context_window 条数：3
memo：已确认约束：预算上限 20 万
材料 ref：inputs/contract-v1
- 已记录合同正文引用。
- 当前问题：现在能不能直接签？
```

| 对比维度 | sliding_window | key_fields_compress |
|---|---|---|
| context_window 大小 | 4 条 | 3 条 |
| memo 使用 | 空 | 包含关键约束和引用 |
| 是否丢失早期约束 | ✅ 不丢失（仍在窗口中） | ✅ 不丢失（通过 memo 携带） |
| 适用场景 | 简单问答 | 需要追踪约束的审批/审查 |

### 7.6 auto_resize 的两种模式

| 模式 | 配置 | 触发方式 | 适用场景 |
|---|---|---|---|
| 自动模式 | `auto_resize=True`（默认） | 每次 `add_chat_history()` 后自动触发 | 大多数场景 |
| 手动模式 | `auto_resize=False` | 需要显式调用 `async_resize()` | 需要在特定时机控制 resize 的场景 |

> 💡 **核心洞见**：两种 handler 共享相同的输入签名，但扮演完全不同的角色。analysis handler 是"决策者"，resize handler 是"执行者"。这种分离让策略逻辑清晰且可测试。

### 7.7 排错指南

| 常见问题 | 原因 | 解决 |
|---|---|---|
| 策略不触发 | `auto_resize=False` 且忘记调用 `async_resize()` | 检查 auto_resize 配置或手动调用 |
| 策略名找不到 | analysis handler 返回的策略名未注册 | 确保 `register_resize_handler(name, fn)` 中的 name 与返回值一致 |
| context_window 没变化 | resize handler 返回值格式错误 | 检查是否返回了 3 个值的元组 |

## 八、Session 持久化：Workspace 绑定与快照

> 🎯 **本节目标**：理解 Session 如何通过 Workspace 实现持久化，区分 AgentlyMemory 和完整 Session 快照两种路径。

### 8.1 Session 为什么需要 Workspace

#### 🧠 直观理解

Session 在内存中管理对话历史，但服务重启后一切都丢失了。Workspace（第19课）提供了"外置存储底座"——Session 把需要持久化的数据交给 Workspace，由 Workspace 负责落盘和恢复。

**生活类比**：Session 是"工作记忆"——你在桌子上放的便签纸。Workspace 是"文件柜"——便签纸用完了归档到文件柜里。

### 8.2 两种持久化路径

```
┌──────────────────────────────────────────────────────┐
│  路径 A: AgentlyMemory（推荐）                         │
│  Agent → Session → AgentlyMemory → Workspace         │
│  自动在请求前后召回/写入 memory record                │
│                                                      │
│  路径 B: 完整 Session 快照（显式）                      │
│  Session → to_serializable_session_data() → Workspace │
│  需要手动调用，适合需要完整恢复的场景                    │
└──────────────────────────────────────────────────────┘
```

### 8.3 路径 A：AgentlyMemory 自动管理

```python
import tempfile
from agently import Agently

with tempfile.TemporaryDirectory() as tmpdir:
    agent = Agently.create_agent("workspace-backed-session-demo")
    agent.use_workspace(f"{tmpdir}/session-workspace")
    agent.activate_session(session_id="tenant-a:user-7:thread-3")
    agent.activated_session.use_memory(mode="AgentlyMemory")

    print("session_id：", agent.activated_session.id)
    print("memory_mode：", agent.activated_session.memory_mode)
    print("memory 已绑定 workspace：",
          agent.activated_session.memory.workspace is agent.workspace)
```

> ⚠️ **重要**：`AgentlyMemory` 持久化的是 **memory record**（从对话中抽取的关键记忆），不是完整的 Session 快照。memory record 存在 Workspace 的 `collection="memory"` 下。

### 8.4 路径 B：完整 Session 快照

```python
import json, tempfile
from agently import Agently
from agently.core import Session

with tempfile.TemporaryDirectory() as tmpdir:
    workspace = Agently.create_workspace(f"{tmpdir}/session-workspace")
    
    persistent_session = Session(id="tenant-a:user-7:thread-3")
    await persistent_session.async_add_chat_history([
        {"role": "user", "content": "请记住合同正文 ref=inputs/contract-v1。"},
        {"role": "assistant", "content": "已记录合同正文引用。"},
    ])
    
    # 序列化并存入 Workspace
    session_ref = await workspace.put(
        persistent_session.to_serializable_session_data(),
        collection="sessions",
        kind="session_snapshot",
        meta={"session_id": persistent_session.id},
    )
    
    # 恢复
    restored_data = await workspace.get_data(session_ref)
    restored_session = Session().load_json_session(
        json.dumps(restored_data, ensure_ascii=False))
    
    print("恢复后的 session_id：", restored_session.id)
    print("恢复后的 full_context 条数：", len(restored_session.full_context))
```

### 8.5 两种路径对比

| 维度 | AgentlyMemory（路径A） | 完整快照（路径B） |
|---|---|---|
| 持久化内容 | 抽取的 memory record | 完整 full_context + context_window + memo |
| 触发方式 | 自动（请求前后） | 手动调用 |
| 恢复能力 | 恢复关键记忆字段 | 完整恢复会话状态 |
| 存储量 | 小 | 较大 |
| 适用场景 | 日常使用 | 审计、导出、迁移 |

> 💡 **核心洞见**：真正进入模型请求的，不是 Workspace 里全部记录，而是 Session 管线分析后组装出来的一包上下文。

### 8.6 关键观察

- 实操路径：绑定 Workspace → 激活 Session → 按需启用 `AgentlyMemory`
- `AgentlyMemory` 持久化的是 memory record，不是完整 Session 快照
- 完整 Session 快照需要显式保存或由上层服务的恢复策略统一管理
- 第21课将基于 handler + Workspace 的组合，展开 Memory 的完整管理方案

## 九、参考案例：OpenAI SDK 与 OWASP 安全边界

> 🎯 **本节目标**：通过业界案例验证本课架构判断的正确性，理解 Session 层的安全价值。

> 💡 **阅读提示**：外部资料在这里不是"看起来有出处"，而是用来验证前面的架构判断——会话历史应该有独立状态层，状态层还要和用户、线程、权限边界绑定。

### 9.1 案例一：OpenAI Agents SDK Sessions

#### 📋 背景

OpenAI Agents SDK 的 Sessions 组件讨论了一个常见问题：多轮 Agent 运行时，开发者不想每轮手动把上一轮结果转成下一轮输入，也不想把所有历史管理逻辑散落在业务代码里。

#### ✅ 解决方案

把会话历史交给 session 对象：
- 一次 run 开始前，runner 从 session 取出已有历史并和当前输入合并
- 一次 run 结束后，runner 把本轮新增的 user/assistant/tool 条目写回 session
- 不同 `session_id` 对应不同对话
- 后端可从 SQLite、Redis、SQLAlchemy、MongoDB 中选择

#### 📊 与本课的关联

| 案例要点 | 本课对应 |
|---|---|
| 多轮历史有明确归属（session_id） | M04：按 user_id + session_id 隔离 |
| 历史存取独立于业务代码 | M04：Session 作为 Agent 和用户之间的中间层 |
| 请求前可定制历史合并方式 | M06-M07：analysis handler + resize handler |
| 不同 session 不会天然混到一起 | M03：共享 agent 状态的混乱演示 |

> ⚠️ **边界说明**：这个案例证明"会话历史管理应该模块化"，不等于证明所有业务都可以直接使用默认合并策略。

### 9.2 案例二：OWASP LLM Top 10 (2025)

#### 📋 背景

OWASP LLM 应用风险清单（2025版）中，有两个风险与 Session 设计直接相关：

- **Sensitive Information Disclosure**：LLM 应用把个人信息、财务信息、凭证、商业数据泄露出去
- **Excessive Agency**：LLM 系统被授予过多功能、权限或自主性，执行超出预期的动作

#### 📊 Session 层能提供什么支撑

| 风险入口 | 如果 Session 边界没拆清楚 | Session 层能提供的支撑 |
|---|---|---|
| 敏感信息泄露 | B 用户请求带入了 A 用户的原始对话、材料 ref、审批状态 | 用 tenant_id / user_id / thread_id / session_id 绑定窗口归属 |
| 权限扩大 | 同一个 agent 状态里混入不同用户可用工具或材料范围 | Session 快照只保存本归属边界下的上下文和 ref |
| 高影响动作 | 旧历史里的指令、工具输出或恶意输入影响下一轮动作 | analysis handler 在请求前检查风险状态和窗口内容 |
| 无界上下文 | 过多历史和材料进入 prompt，难以审计 | resize handler 控制本轮窗口，Workspace 保存可追溯快照 |

> ⚠️ **边界说明**：Session 不直接解决所有安全问题。权限校验、数据脱敏、人工审批仍然要由对应模块承担。但如果会话归属一开始就混乱，后面的安全策略很难补回来。

### 9.3 综合判断：Session 层要回答的四个问题

结合两个案例，一个设计合格的 Session 层必须回答：

```
1. 这段历史属于谁？
   → tenant_id + user_id + channel + thread_id + session_id 怎样绑定

2. 本轮要取哪些内容？
   → full_context / context_window / memo / 材料 ref 怎样进入 prompt

3. 超长或高风险时怎么处理？
   → 滑动窗口 / 字段压缩 / 阶段摘要 / 风险检查 由哪个 handler 执行

4. 服务重启后怎么恢复？
   → Session 快照 / 摘要 / 归属信息 怎样交给 Workspace
```

> 💡 **核心洞见**：Session 不是"把历史消息 append 到 prompt 里"的语法糖。回答了这四个问题，Session 才从"聊天记录列表"变成"一条上下文组装管线"。

## 十、课程小结与答疑精选

### 10.1 🗺️ 知识图谱

```
                        ┌──────────────────────┐
                        │    Session 会话管理     │
                        │  "短期上下文的模块边界"  │
                        └──────────┬───────────┘
                                   │
            ┌──────────────────────┼──────────────────────┐
            │                      │                      │
            ▼                      ▼                      ▼
   ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
   │  append 是起点  │   │ Session 是边界  │   │ handler 是策略  │
   │                │   │                │   │                │
   │ while + history │   │ full_context   │   │ analysis: 判断  │
   │ 最小多轮对话    │   │ context_window │   │ resize: 执行    │
   │ 直观但不足      │   │ memo           │   │ 可插拔可组合    │
   └───────┬────────┘   └───────┬────────┘   └───────┬────────┘
           │                    │                     │
           └────────────────────┼─────────────────────┘
                                │
                                ▼
                      ┌────────────────┐
                      │  Workspace 底座 │
                      │                │
                      │ AgentlyMemory  │
                      │ Session 快照    │
                      │ 持久化与恢复    │
                      └────────────────┘
```

### 10.2 💡 一句话总结

> Session 不是"把历史消息 append 到 prompt 里"的语法糖。它解决的是短期交互状态的模块边界：`full_context` 保留完整记录，`context_window` 表示本轮窗口，`memo` 承接摘要，analysis handler 发现问题，resize handler 修正窗口，Workspace 是持久化底座。

### 10.3 📍 系列定位

> 📍 **系列定位**：本文是「Agent 架构师」系列第 20 篇。
> - 上一篇：第19课 Workspace — Agent 的外置文件工作空间
> - 下一篇：第21课 Memory — 基于 Session handler 的中长期记忆管理

---

### 10.4 📝 答疑精选

**🙋 问题1**：群聊中有多个 agent 和多个用户，如何管理对话？

> 📖 **背景**：有同学问到企业微信群聊场景——多个用户通过 @ 符号触发不同的 agent，此时如何进行对话管理？

**💬 老师回答**：群聊场景本质上是协同的一种变种。群聊本身就是一个"命令分发控制器"——用户 @ 某个 agent 就相当于 human-in-the-loop 触发特定的 agent。群聊有自己的聊天记录，当通过 ACP 协议分发任务给具体 agent 时，由业务逻辑决定该 agent 是继承群聊上下文还是独立上下文。

> 💡 **延伸**：这种场景下，session_id 的设计需要包含 `channel_id + thread_id`，而不是简单的 `user_id`。

---

**🙋 问题2**：FDE（Forward Deployed Engineer）和 agent 开发工程师有什么区别？

**💬 老师回答**：FDE 本质上就是"AI 时代的实施工程师"。在欧美，SaaS 标品化程度高（如 Salesforce），实施工程师只需要远程勾选功能模块。但 AI 应用落地无法"标品化勾选"——必须有人坐到业务现场，理解业务需求，设计 AI 流程。FDE 解决的就是"最后 1 公里"的问题。

> 💡 **核心区别**：FDE 是"带咨询的实施"，不是"照单打勾的实施"。需要理解业务、设计流程、选择策略——和本课讲的 handler 策略设计是同一类能力。

---

### 10.5 📝 课后练习

#### 练习 1：实现自定义 analysis handler

**题目**：为一个客服 Session 实现 analysis handler，要求：
- 当 context_window 超过 10 条时触发压缩
- 使用"保留最近 5 条 + 生成 memo"的策略
- memo 内容为前 5 条的消息摘要

**验收标准**：
- [ ] analysis handler 正确判断触发条件
- [ ] resize handler 正确返回 (None, context_window[-5:], memo)
- [ ] memo 包含前 5 条消息的关键信息

#### 练习 2：设计多用户 Session 隔离方案

**题目**：为一个 FastAPI 服务设计 Session 管理方案：
- 支持 user_id + session_id 两级隔离
- 用户可以创建多个会话、恢复已有会话
- 考虑并发安全和持久化

**验收标准**：
- [ ] 画出 Session 池的字典结构
- [ ] 写出 `get_or_create_session(user_id, session_id)` 的核心逻辑
- [ ] 说明如何与 Workspace 集成实现持久化

---

> 📅 生成日期: 2026-07-14 | 🎯 级别: L 级 | ⏱️ 录音时长: ~78 分钟 | 📏 文档规模: 3,500+ 行
> 🤖 由 transcript-to-doc v4.2 生成

---

## 📋 课程小结

### 🗺️ 知识图谱

```
                        ┌──────────────────────────┐
                        │     Session 会话管理        │
                        │  "短期上下文的模块边界"      │
                        └────────────┬─────────────┘
                                     │
            ┌────────────────────────┼────────────────────────┐
            │                        │                        │
            ▼                        ▼                        ▼
   ┌────────────────┐    ┌────────────────────┐    ┌────────────────────┐
   │  append 是起点  │    │   Session 是边界    │    │   handler 是策略    │
   │  while+history │    │ full_context       │    │ analysis: 判断触发  │
   │  最小多轮对话   │    │ context_window     │    │ resize: 执行压缩    │
   │  直观但不足     │    │ memo               │    │ 可插拔、可组合      │
   └───────┬────────┘    └────────┬───────────┘    └────────┬───────────┘
           │                      │                          │
           └──────────────────────┼──────────────────────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │   Workspace 底座    │
                        │  AgentlyMemory 自动 │
                        │  Session快照 显式   │
                        │  持久化与恢复       │
                        └────────────────────┘
```

### 💡 一句话总结

> Session 不是"把历史消息 append 到 prompt 里"的语法糖。它解决的是短期交互状态的模块边界：`full_context` 保留完整会话记录，`context_window` 表示本轮模型能看到的短期窗口，`memo` 承接短期摘要或关键字段，analysis handler 判断是否需要处理，resize handler 执行裁剪或压缩，Workspace 是持久化底座。

### 📍 系列定位

> 📍 本文是「Agent 架构师」系列第 20 篇。上一篇：第19课 Workspace；下一篇：第21课 Memory。

---

## 📝 课后练习

### 练习 1：实现自定义滑动窗口策略
为客服 Session 实现 handler 管线：analysis 在 context_window >= 10 时触发，resize 保留最近 5 条并生成 memo。
**验收标准**：[ ] 正确判断触发 [ ] 返回正确三元组 [ ] 15条消息验证裁剪

### 练习 2：设计多用户 Session 隔离方案
为 FastAPI 服务设计：user_id + session_id 隔离、并发安全、Workspace 持久化。
**验收标准**：[ ] 数据结构图 [ ] 核心逻辑 [ ] 恢复流程

### 练习 3：策略场景匹配
为 IT 运维助手、合同审查助手、企业微信机器人选择上下文管理策略。
**验收标准**：[ ] 触发时机+策略 [ ] 选择理由 [ ] 边界情况

---

> 📅 生成日期: 2026-07-14 | 🎯 级别: L 级 | ⏱️ 录音时长: ~78 分钟 | 📏 文档规模: 3,800+ 行
> 🤖 由 transcript-to-doc v4.2 生成
