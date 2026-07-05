# Agently Model Request 入门与最小任务执行器

> 基于陈泽鹏老师视频课程整理编写 · 2026年7月3日
> 生成方式：v4.1 五阶段流水线 · 6 子 Agent 并行撰写

---

## 目录

- [一、课前补充：OpenClaw 配置进阶](#一课前补充openclaw-配置进阶)
- [二、Agentic 框架安装与开发工具](#二agentic-框架安装与开发工具)
- [三、单次请求能解决什么——四个业务场景](#三单次请求能解决什么四个业务场景)
- [四、会议纪要——人能看懂，系统用不了](#四会议纪要人能看懂系统用不了)
- [五、裸调模型的困境——五种输出形态](#五裸调模型的困境五种输出形态)
- [六、结构化输出的五个层次](#六结构化输出的五个层次)
- [七、Schema 约束——为什么不能只靠接口](#七schema-约束为什么不能只靠接口)
- [八、Schema as Prompt——用代码思维定义输出结构](#八schema-as-prompt用代码思维定义输出结构)
- [九、七步确保——从 Prompt 到可靠输出的完整链路](#九七步确保从-prompt-到可靠输出的完整链路)
- [十、单次请求的适用边界与工程化扩展](#十单次请求的适用边界与工程化扩展)
- [十一、Q&A 答疑精选与课程小结](#十一qa-答疑精选与课程小结)

---

以下是整理后的教学文档章节内容：

---

## 一、课前补充：OpenClaw 配置进阶

上一节课我们完成了 OpenClaw 的基础安装和首次运行。但要让它在实际项目中稳定地工作，配置层面还需要更精细的打磨。本节就从「配置文件结构」「Memory/Embedding 配置」「Gateway 穿透」「新版本 HTTPS 问题」「WSL 环境注意事项」以及「任务执行慢的根因」六个维度，把进阶配置一次性讲透。

### 1.1 配置文件总览：你的钥匙在哪里

OpenClaw 的所有核心配置都落在 **`~/.openclaw/openclaw.json`**。注意不是项目目录下，是用户家目录下的隐藏文件夹。

打开后，你会看到类似这样的结构：

```json
{
  "version": "2.0",
  "agentic": {
    "default": {
      "provider": "openai",
      "model": "gpt-4o",
      "api_key": "sk-your-api-key-here",
      "memory_search": {
        "provider": "openai",
        "model": "text-embedding-3-small",
        "remote": "https://api.openai.com/v1"
      }
    }
  },
  "gateway": {
    "mode": "local",
    "bind": "custom",
    "custom_bind_host": "0.0.0.0",
    "bind_port": 8080,
    "allow_origin": "*"
  }
}
```

**关键提醒**：这个文件里明文存储着你的 API Key。上课共享屏幕、录屏、截图之前，务必先把配置文件关掉。如果录播需要演示配置文件内容，请提前把 `api_key` 字段的值替换为占位符，切勿暴露真实密钥。一个小疏忽 = 你的 key 被人拿走刷爆额度。

---

### 1.2 Memory / Embedding 配置：让 agent 拥有长期记忆

OpenClaw 的记忆系统依赖向量检索，底层需要一个 embedding 模型把文本转成向量。这部分配置在 `agentic.default` 节点下，关键字段是 `memory_search`。

**配置路径**：

```
agentic.default.memory_search
├── provider    // embedding 服务提供商，如 openai、ollama
├── model       // 具体的 embedding 模型名称
├── remote      // API 端点地址（含 /v1 后缀）
└── api_key     // 访问该服务的认证密钥（可选，如果和上层的 api_key 相同可以省略）
```

#### 1.2.1 线上 embedding 示例（以阿里云百炼为例）

很多同学用的是国内的 embedding 服务，比如阿里云百炼平台的「千问 3 embedding」。配置方式如下：

```json
{
  "agentic": {
    "default": {
      "memory_search": {
        "provider": "openai",
        "model": "qwen3-embedding",
        "remote": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "api_key": "sk-your-dashscope-key"
      }
    }
  }
}
```

几个容易踩坑的点：

1. **provider 还是写 `"openai"`**。因为绝大多数国产大模型平台的 embedding API 都兼容 OpenAI 的 `/v1/embeddings` 接口格式，OpenClaw 内部用 OpenAI 协议去请求，所以 provider 字段不需要改成 aliyun 或 dashscope — 写 `openai` 就行。
2. **model 写你供应商后台的实际模型名**。比如阿里云百炼后台复制出来的模型 ID 就是 `qwen3-embedding`，不要自己编一个。
3. **remote 写到 `/v1` 为止**，不要在后面再加 `/embeddings`。OpenClaw 会自动拼接完整路径。
4. **api_key 用你供应商给的 key**，这个 key 只在请求 embedding 接口时使用。

配置完成后，通过以下命令验证 embedding 是否生效：

```bash
openclaw memory state
```

如果输出中显示出向量存储的状态信息而非报错，说明 embedding 正常工作。如果报错，优先检查 `remote` 字段是否拼写正确，以及 api_key 是否有效。

---

### 1.3 Gateway 穿透：让外部设备也能访问你的 Agent

本地调试时 `localhost:8080` 用着很爽，但一旦需要在局域网内的手机、另一台电脑上测试，就涉及到 Gateway 的网络穿透配置。

#### 1.3.1 配置文件中的关键字段

```json
{
  "gateway": {
    "mode": "local",
    "bind": "custom",
    "custom_bind_host": "0.0.0.0",
    "bind_port": 8080,
    "allow_origin": "*",
    "os_token": "your-secret-token"
  }
}
```

逐字段说明：

| 字段 | 取值 | 含义 |
|------|------|------|
| `mode` | `"local"` | 本地模式运行 Gateway |
| `bind` | `"custom"` | 使用自定义绑定地址 |
| `custom_bind_host` | `"0.0.0.0"` | 监听所有网络接口（局域网可访问） |
| `bind_port` | `8080` | Gateway 监听端口，可按需修改 |
| `allow_origin` | `"*"` | 允许任意来源的跨域请求 |
| `os_token` | 自定义字符串 | 访问 Gateway 时必须携带的 token |

**极易踩坑**：新手常常会想当然地写成 `"host": "0.0.0.0"`，这是不行的。Gateway 配置里**没有 `host` 这个字段**，正确写法是 **`custom_bind_host`**。这个单词一个字母都不能错。

#### 1.3.2 访问 URL 格式

外部设备通过以下 URL 访问你的 Gateway：

```
http://<你的局域网IP>:<bind_port>?token=<os_token>
```

举例：你的电脑 IP 是 `192.168.1.100`，端口是 `8080`，token 设为 `abc123`，那么访问地址就是：

```
http://192.168.1.100:8080?token=abc123
```

**`os_token` 必须设置**。没有 token 的话任何人都能通过端口扫描找到你的 Gateway 并直接调用，这在公网或公司网络环境下非常危险。token 相当于一把简易的访问锁，虽然不能替代 HTTPS 的安全级别，但至少拦住了一大批随意的扫描请求。

---

### 1.4 新版本 HTTPS 强制问题与 SSH 穿透方案

**重要变化**：较新版本的 OpenClaw/Gateway 强制使用 HTTPS，浏览器在访问 HTTP 端口时可能会被拒绝。如果你只是局域网测试且没有签 SSL 证书，这会直接导致连不上。

**解决方案：SSH 本地端口转发**

利用 SSH 隧道，在你本机创建一个安全的本地监听端口，把流量加密转发到远端 Gateway：

```bash
ssh -L <本地端口>:<远端IP>:<远端端口> <用户名>@<远端IP>
```

参数拆解：

| 参数 | 含义 |
|------|------|
| `-L` | 指定本地端口转发 |
| 本地端口 | 你本机用来访问的端口，如 `9090` |
| 远端IP | Gateway 所在机器的 IP |
| 远端端口 | Gateway 监听的端口，如 `8080` |
| 用户名 | 远端机器的 SSH 用户名 |

**实际执行示例**：

```bash
ssh -L 9090:192.168.1.100:8080 root@192.168.1.100
```

执行后，保持 SSH 会话不关闭。然后你在本机浏览器访问：

```
https://localhost:9090?token=xxx
```

流量路径：`浏览器 → localhost:9090（SSH加密隧道）→ 远端 192.168.1.100:8080（Gateway）`。HTTPS 问题由此绕过。

---

### 1.5 WSL 环境的特殊性

很多同学在 Windows 上装了 WSL，然后在 WSL 里跑了 OpenClaw，接着试图从 Windows 的浏览器访问 `localhost:8080`，发现连不上。

**核心认知**：WSL 和宿主机 Windows 是**同一台物理机器上的两个相互隔离的 Linux 环境**。它们各自有独立的网络栈、独立的进程空间。你不能想当然地认为「我在这台电脑上装的，所以另一个程序就能直接调」。

**正确做法**：

1. **所有依赖装在 WSL 内部**。Node.js、Python、OpenClaw 本体，一律在 WSL 终端里安装，不要用 Windows 的安装包。
2. 如果确实需要从 Windows 访问 WSL 里的 Gateway：
   - 在 WSL 内执行 `ip addr show eth0` 查看 WSL 的 IP 地址
   - Gateway 配置 `custom_bind_host` 设为 `0.0.0.0`
   - 从 Windows 浏览器访问 `http://<WSL的IP>:<端口>?token=xxx`
3. 反过来，如果 WSL 里的程序要调 Windows 上跑的服务，用的是 `$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')` 拿到的那个 IP（通常是 Windows 宿主在 WSL 视角下的虚拟网关地址）。

**一句话总结**：把 WSL 当成一台独立的虚拟 Linux 服务器来对待，别把它和 Windows 混为一谈。

---

### 1.6 为什么任务跑得慢：理解 ReAct Loop

经常有同学问：「为什么我让 agent 帮我查个天气，它要转好几圈才回答？不是应该一次调用就返回吗？」

**原因在于 ReAct Loop（推理-行动循环）**。每次 agent 处理任务，它不是「接到问题 → 回答问题」的一条直线，而是一个循环迭代的过程：

```
步骤 1：理解 & 规划
  └── agent 解析你的指令，拆解成子任务，制定执行计划

步骤 2：工具选择
  └── 根据当前阶段需要，从工具集里选一个或多个工具

步骤 3：调用 & 执行
  └── 真正发起 API 调用 / 执行本地操作

步骤 4：结果查看 & 判断
  └── 检查工具返回的结果是否足以回答用户
  └── 如果不够 → 回到步骤 1，新一轮循环
  └── 如果够了 → 生成最终回复输出给用户
```

每一轮 Loop 都要走一次完整的大模型推理，耗时叠加起来，一个「简单」任务转个 3-5 轮是家常便饭。这就是你会感觉「明明问题很简单，怎么半天不回我」的根本原因。

#### 1.6.1 IM 通道看不到中间过程

另一个让人焦虑的点：在 IM 类通道（如微信公众号、飞书机器人）里，用户只能看到「最终回复」。中间那 3-5 轮的 ReAct Loop 过程全部在黑盒里运行，用户这边看起来就是「对方正在输入…」然后等了很久。

**解决办法**：打开 **Dashboard**，它能可视化展示每一轮 Loop 的中间输出——模型在想什么、调用了哪个工具、工具返回了什么。日常调试一定开着 Dashboard，这对理解 agent 行为至关重要。

#### 1.6.2 约束提示词：让用户感知进度

如果你在 IM 通道里使用 agent，可以在系统提示词中加入以下约束来改善体验：

**策略**：要求 agent 收到任务后先回复「收到，正在处理」，并且在每一轮中间处理时向用户报告当前进展。

```
当用户发送任务时，你必须：
1. 第一句话回复："收到，正在处理您的请求。"
2. 每完成一个中间步骤（工具调用、搜索、计算等），简要报告当前进度
   例如："正在查询天气数据..."、"已获取数据，正在分析中..."
3. 最终输出完整结果时，附上你执行的步骤摘要
```

这样即使整体耗时没变少，用户因为每隔几秒就能看到进展更新，等待焦虑会大幅降低。体验上就从一个「漫长的空白等待」变成了「能感知到的逐步推进」。

---

### 1.7 本节要点回顾

| 要点 | 一句话记忆 |
|------|-----------|
| 配置文件位置 | `~/.openclaw/openclaw.json`，明文存 key，录屏前关掉 |
| Memory embedding | 在 `agentic.default.memory_search` 下配置，provider 写 `openai` |
| 验证 embedding | `openclaw memory state` 看是否正常 |
| Gateway 穿透 | `custom_bind_host=0.0.0.0`，不是 `host`！ |
| 跨域 | `allow_origin: "*"` |
| 访问 token | 必设 `os_token`，URL 带 `?token=xxx` |
| 新版 HTTPS | 用 `ssh -L 本地端口:远端IP:远端端口 user@远端IP` 做端口转发 |
| WSL | 独立环境，别混用 Windows 的资源，所有依赖装 WSL 里 |
| 慢的原因 | ReAct Loop 四步迭代（理解→选择工具→调用→判断），IM 通道看不到过程 |
| 改善体验 | 提示词约束 agent 先回「收到」，每步报告进展；调试开 Dashboard |

下一节我们将进入编码实战，把这些配置能力应用到具体的 agent 开发场景中。

---

以上就是完整的教学文档章节，涵盖录音稿中全部 7 个要点，结构分 7 个小节，包含配置代码块、表格对照、命令行示例和关键踩坑提醒，总篇幅控制在合理范围内。可以直接粘贴使用。
---

# Agentic 框架安装与业务场景入门

> 基于陈泽鹏老师视频课程整理编写 · 2026年7月3日

---

## 目录

- [二、Agentic 框架安装与开发工具](#二agentic-框架安装与开发工具)
  - [2.1 Agentic 框架简介](#21-agentic-框架简介)
  - [2.2 安装 Agentic 核心库](#22-安装-agentic-核心库)
  - [2.3 验证安装是否成功](#23-验证安装是否成功)
  - [2.4 模型服务配置](#24-模型服务配置)
  - [2.5 Agentic Devtools 开发工具](#25-agentic-devtools-开发工具)
  - [2.6 Debug 模式与日志诊断](#26-debug-模式与日志诊断)
  - [2.7 Devtools 功能全景](#27-devtools-功能全景)
- [三、单次请求能解决什么——四个业务场景](#三单次请求能解决什么四个业务场景)
  - [3.1 场景一：会议纪要结构化](#31-场景一会谈纪要结构化)
  - [3.2 场景二：制度问答](#32-场景二制度问答)
  - [3.3 场景三：长文摘要](#33-场景三长文摘要)
  - [3.4 场景四：提单字段自动提取](#34-场景四提单字段自动提取)
  - [3.5 四场景的共同特征](#35-四场景的共同特征)
  - [3.6 万能公式：给上下文 + 给任务 = 拿结果](#36-万能公式给上下文--给任务--拿结果)
- [四、会议纪要——人能看懂，系统用不了](#四会议纪要我—人能看懂系统用不了)
  - [4.1 场景重演：从录音到结构化 To-Do](#41-场景重演从录音到结构化-to-do)
  - [4.2 给人看 OK，给系统看不行](#42-给人看-ok给系统看不行)
  - [4.3 ReAct Loop 对结构化输出的刚性需求](#43-react-loop-对结构化输出的刚性需求)
  - [4.4 下游系统期望的格式](#44-下游系统期望的格式)
  - [4.5 从"人能看懂"到"机器可解析"的跨越](#45-从人能看懂到机器可解析的跨越)

---

## 二、Agentic 框架安装与开发工具

### 2.1 Agentic 框架简介

Agentic 是一个 Python 语言的智能体（Agent）开发框架。它的核心设计理念是：**将大语言模型的能力包装成可编程、可编排、可观测的智能体**。开发者不需要从零实现 ReAct 循环、工具调用协议、流式输出处理等底层逻辑——Agentic 已经把这些能力封装好了，你只需要关注业务逻辑。

在开始之前，先厘清两个关键概念：

- **Agentic（核心库）**：提供 `create_agent`、`Runner`、工具装饰器等核心 API，版本号 4.1.0.1。
- **agentic-tools（工具集）**：预置的工具箱，包含文件读写、网络请求、代码执行等常用工具，版本号 0.1.1。

> 注意：agentic-tools 是可选依赖。如果你只使用 Agentic 的编排能力而不需要预置工具，可以只装核心库。

---

### 2.2 安装 Agentic 核心库

在安装之前，确保你已经完成以下前置步骤：
- Python 3.10+ 环境已配置（推荐 UV 或 Conda 管理）
- 项目虚拟环境已激活

```bash
# 安装核心库（当前最新版本 4.1.0.1）
pip install agentic

# 安装预置工具集（可选，版本 0.1.1）
pip install agentic-tools
```

如果你使用 UV 管理环境，安装命令相同：

```bash
uv pip install agentic agentic-tools
```

安装完成后，可以通过 `pip list` 确认版本：

```bash
pip list | grep agentic
```

期望输出：

```
agentic            4.1.0.1
agentic-tools      0.1.1
```

> 提示：如果你在团队协作中需要锁定版本，建议在 `requirements.txt` 中明确写出：
> ```
> agentic==4.1.0.1
> agentic-tools==0.1.1
> ```

---

### 2.3 验证安装是否成功

安装完成后，用以下代码快速验证核心功能是否可用：

```python
from agentic import create_agent

# 如果能正常导入且不报错，说明安装成功
print("Agentic 导入成功")

# 进一步验证：创建一个最小化的 Agent 实例
agent = create_agent(
    name="test_agent",
    instruction="你是一个测试助手，用中文回答问题。",
)
print(f"Agent 创建成功: {agent.name}")
```

运行这段代码，如果没有抛出 `ModuleNotFoundError` 或 `ImportError`，说明 Agentic 已正确安装。

**常见问题排查：**

| 错误信息 | 原因 | 解决方法 |
|---------|------|---------|
| `ModuleNotFoundError: No module named 'agentic'` | 未安装或未激活虚拟环境 | 确认虚拟环境已激活，重新 `pip install agentic` |
| `ImportError: cannot import name 'create_agent'` | 安装了旧版本 | `pip install --upgrade agentic` 升级到 4.1.0.1 |
| `AttributeError: ...` | 版本不兼容 | 检查 `pip list` 确认版本号 |

---

### 2.4 模型服务配置

Agentic 不绑定特定模型厂商——它通过 **OpenAI 兼容接口** 来对接任何支持该协议的大模型服务。这意味着你可以使用 OpenAI、MiniMax、DeepSeek、Ollama（本地）、任何自部署的 vLLM 服务等。

#### 2.4.1 配置方式一：环境变量（推荐）

```bash
# 设置模型服务的接口地址
export OPENAI_BASE_URL="https://api.minimax.chat/v1"

# 设置 API 密钥
export OPENAI_API_KEY="your-api-key-here"

# 设置默认模型名称
export OPENAI_MODEL="MiniMax-M1"
```

在代码中，Agentic 会自动读取这些环境变量：

```python
from agentic import create_agent

agent = create_agent(
    name="assistant",
    instruction="你是一个专业助手。",
    # 不传 model 参数时，自动使用 OPENAI_MODEL 环境变量的值
)
```

#### 2.4.2 配置方式二：代码内显式指定

如果不想依赖环境变量，或者需要在同一个脚本中切换到不同的模型服务，可以直接在创建 Agent 时传入配置：

```python
from agentic import create_agent
from agentic.models import OpenAIModel

model = OpenAIModel(
    base_url="https://api.minimax.chat/v1",
    api_key="your-api-key-here",
    model="MiniMax-M1",
)

agent = create_agent(
    name="assistant",
    instruction="你是一个专业助手。",
    model=model,
)
```

#### 2.4.3 多模型服务对照表

以下列出常见模型服务商的 OpenAI 兼容接口配置：

| 服务商 | BASE_URL | 典型 model 参数 |
|-------|----------|----------------|
| MiniMax | `https://api.minimax.chat/v1` | `MiniMax-M1` |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o` |
| Ollama（本地） | `http://localhost:11434/v1` | `qwen2.5:7b` |
| vLLM（自部署） | `http://your-server:8000/v1` | 按部署配置 |

> 核心原理：Agentic 内部使用标准的 OpenAI Chat Completions API 协议与模型通信。只要模型服务兼容该协议，就能无缝接入。这是当前大模型应用开发的事实标准。

---

### 2.5 Agentic Devtools 开发工具

在开发智能体应用时，你经常需要观察 Agent 的"思考过程"——它收到了什么 Prompt、模型返回了什么、工具调用了几次、每次调用花了多少 Token。Agentic 提供了一套 Devtools，让你可以在浏览器中实时查看 Agent 的完整请求生命周期。

#### 2.5.1 安装 Devtools 依赖

```bash
pip install observation-bridge
```

#### 2.5.2 注册并启动 Devtools

```python
from agentic import create_agent, Runner
from observation_bridge import bridge

# 第一步：将 Agentic 注册到观测桥接器
bridge.register("agentic")

# 第二步：创建 Agent
agent = create_agent(
    name="devtools_demo",
    instruction="你是一个智能助手，可以帮用户解答技术问题。",
)

# 第三步：运行 Agent
runner = Runner()
result = runner.run(agent, "请解释一下什么是 ReAct 模式？")
print(result.final_output)
```

当你运行这段代码时，终端会打印一行 Devtools 地址：

```
🔍 Devtools: http://localhost:9140
```

在浏览器中打开这个地址，你将看到一个仪表盘界面，展示当前 Agent 运行的全部细节。

#### 2.5.3 Devtools 仪表盘核心区域

Devtools 界面分为以下几个核心查看区域：

```
┌────────────────────────────────────────────────────────────┐
│                    Devtools 仪表盘                          │
├──────────────┬──────────────────────┬──────────────────────┤
│  请求列表     │   请求详情面板        │   Metadata 面板       │
│              │                      │                      │
│  ┌─ Request  │  ┌─ Prompt 快照      │  ┌─ model: MiniMax-M1│
│  │  1        │  │  (System + User)  │  │  tokens: 1,234    │
│  │  ✓ 200    │  │                   │  │  latency: 2.3s    │
│  ├─ Request  │  ├─ 模型原始响应      │  │  cost: $0.002     │
│  │  2        │  │  (含 reasoning)    │  └──────────────────│
│  │  ✓ 200    │  │                   │                      │
│  └─ Request  │  ├─ Streaming 实时流  │                      │
│     3        │  │  (逐 token 展示)   │                      │
│     ⏳ ...   │  │                   │                      │
│              │  ├─ 工具调用记录      │                      │
└──────────────┴──────────────────────┴──────────────────────┘
```

---

### 2.6 Debug 模式与日志诊断

当 Agent 行为不符合预期时，你需要更详细的日志来定位问题。Agentic 提供了全局 debug 开关：

```python
from agentic import set_statics

# 开启 debug 模式——输出详细日志
set_statics(debug=True)

# 创建并运行 Agent，此时终端会打印完整的请求/响应日志
agent = create_agent(
    name="debug_demo",
    instruction="你是一个数学助手，回答前先展示推理过程。",
)

runner = Runner()
result = runner.run(agent, "一个水池，进水管 3 小时注满，出水管 5 小时放完，两管同开，几小时注满？")
print(result.final_output)
```

开启 `debug=True` 后，终端会输出类似以下的详细日志：

```
[DEBUG] agentic.runner - Starting run for agent 'debug_demo'
[DEBUG] agentic.llm - Preparing request to model: MiniMax-M1
[DEBUG] agentic.llm - System prompt length: 156 chars
[DEBUG] agentic.llm - User message length: 42 chars
[DEBUG] agentic.llm - Sending request to https://api.minimax.chat/v1/chat/completions
[DEBUG] agentic.llm - Response received in 2.34s
[DEBUG] agentic.llm - Token usage: prompt=89, completion=312, total=401
[DEBUG] agentic.runner - Run completed successfully
[DEBUG] agentic.runner - Total turns: 1, Total tokens: 401
```

> 生产环境中请关闭 debug 模式（`set_statics(debug=False)`），避免日志泄露敏感信息。

---

### 2.7 Devtools 功能全景

下表汇总 Devtools 提供的全部观测能力，它们是后续课程中调试复杂 Agent 流程的核心工具：

| 功能模块 | 说明 | 典型使用场景 |
|---------|------|------------|
| **Prompt 快照** | 展示每次模型调用的完整 System Prompt 和 User Message | 检查 Prompt 模板是否正确渲染；排查变量注入问题 |
| **模型原始响应** | 展示模型返回的原始 JSON 响应（含 reasoning、tool_calls） | 验证模型输出格式是否符合预期；排查工具调用参数错误 |
| **Streaming 实时流** | 逐 token 展示模型输出，模拟终端打字效果 | 观察模型生成节奏；检查是否有中途截断或重复生成 |
| **生命周期事件** | 记录 Agent 从创建到运行结束的全部关键节点：`agent.created` → `run.started` → `llm.request` → `tool.call` → `run.completed` | 追踪多步推理流程；定位具体在哪个环节出错 |
| **Metadata / Usage** | 统计每次请求的模型名称、Token 消耗（prompt_tokens / completion_tokens / total_tokens）、响应延迟、预估费用 | 成本监控；比较不同模型的性价比 |
| **工具调用追踪** | 展示每次工具调用的函数名、传入参数、返回结果 | 确认 Agent 是否正确选择了工具；工具参数是否合理 |

---

## 三、单次请求能解决什么——四个业务场景

在深入 Agent 的复杂编排之前，先回答一个问题：**什么样的任务适合用大模型解决？** 答案是：大量任务其实不需要 Agent，只需要一次请求。

本章通过四个真实业务场景，展示大模型在"单次请求"模式下能做什么，以及它们的共同特征。

---

### 3.1 场景一：会议纪要结构化

**输入**：一段会议录音转文字后的原始文本。

```
今天产品评审会讨论了三个议题。第一，Q3 产品路线图，张三建议优先做用户权限模块，
预计需要两周开发时间。第二，用户反馈中提到的搜索速度问题，李四认为核心瓶颈在索引
重建频率上，建议改成增量索引方案。第三，需求文档规范化，王五提议引入 PRD 模板，
统一团队文档标准。会议决议：张三负责出具权限模块技术方案，下周三前完成；李四负责
索引优化调研，本周五给出数据对比。王五负责制定 PRD 模板，下周一前发团队评审。
```

**期望输出**：结构化的会议纪要和待办事项清单。

```python
from agentic import create_agent, Runner

agent = create_agent(
    name="meeting_minutes",
    instruction="""你是一个专业的会议纪要整理助手。
    
    请将输入的会议记录整理为以下格式：
    1. 会议摘要（一段话概括核心内容）
    2. 议题列表（每项议题简要说明）
    3. 待办事项清单（负责人、事项描述、截止日期）
    """,
)

runner = Runner()
result = runner.run(
    agent,
    """今天产品评审会讨论了三个议题。第一，Q3 产品路线图，张三建议优先做用户权限模块，"""
    """预计需要两周开发时间。第二，用户反馈中提到的搜索速度问题，李四认为核心瓶颈在索引"""
    """重建频率上，建议改成增量索引方案。第三，需求文档规范化，王五提议引入 PRD 模板，"""
    """统一团队文档标准。会议决议：张三负责出具权限模块技术方案，下周三前完成；李四负责"""
    """索引优化调研，本周五给出数据对比。王五负责制定 PRD 模板，下周一前发团队评审。""",
)
print(result.final_output)
```

**模型输出示例**：

```
一、会议摘要
本次产品评审会围绕 Q3 产品路线图、搜索性能优化、需求文档规范三个议题展开讨论，
形成了明确的责任分工和时间节点。

二、议题列表
1. Q3 产品路线图：张三建议优先做用户权限模块，预计两周开发时间。
2. 搜索速度优化：李四认为核心瓶颈在索引重建频率，建议改为增量索引方案。
3. 需求文档规范化：王五提议引入 PRD 模板，统一团队文档标准。

三、待办事项
- 张三：出具权限模块技术方案，截止下周三
- 李四：完成索引优化调研并给出数据对比，截止本周五
- 王五：制定 PRD 模板并发送团队评审，截止下周一
```

---

### 3.2 场景二：制度问答

**输入**：公司制度文档的全文 + 员工的具体问题。

```python
policy_document = """
《考勤管理制度》（2026 版）
第三条 工作时间：公司实行弹性工作制，核心工作时间为 10:00-16:00。
  员工每日工作时长不得少于 8 小时。
第八条 请假流程：员工请假需提前一个工作日通过 OA 系统提交申请。
  紧急情况可电话告知直属上级后补办手续。连续请假超过 3 天需部门负责人审批。
第十二条 加班管理：工作日加班按 1.5 倍工资计算，休息日加班按 2 倍计算，
  法定节假日加班按 3 倍计算。加班需提前报备，未经审批的加班不计入加班费。
第十五条 年假：入职满 1 年享 5 天年假，此后每增加 1 年增加 1 天，上限 15 天。
"""

question = "我刚入职 8 个月，今天突然发烧需要请假，应该怎么做？"

agent = create_agent(
    name="policy_qa",
    instruction=f"""你是一个公司制度问答助手。请依据以下制度文档回答员工的问题。
    引用制度的具体条款编号。如果文档中没有覆盖到的问题，诚实告知。

    制度文档：
    {policy_document}
    """,
)

runner = Runner()
result = runner.run(agent, question)
print(result.final_output)
```

**模型输出示例**：

```
根据《考勤管理制度》（2026 版）的相关条款，针对您的情况分析如下：

1. 请假流程（参考第八条）：您当前属于紧急情况（突发疾病），可以先电话告知直属上级，
   后续通过 OA 系统补办请假手续。

2. 审批权限（参考第八条）：是否需要部门负责人审批取决于请假天数。
   如果请假不超过 3 天，直属上级审批即可。

3. 年假（参考第十五条）：您入职 8 个月，尚未满 1 年，目前不享受年假。
   建议使用事假或病假类型提交申请。

总结：先给上级打电话说明情况，再去医院就诊。身体恢复后登录 OA 补办请假手续。
```

---

### 3.3 场景三：长文摘要

**输入**：一篇长文章或报告的全文。

```python
long_article = """
[此处省略一篇 5000 字的技术报告，内容涵盖：项目背景、技术选型论证、架构设计细节、
  性能测试数据、风险评估、上线计划等]
"""

agent = create_agent(
    name="summarizer",
    instruction="""你是一个专业的技术文档摘要助手。请对输入的长文执行以下操作：
    
    1. 写出 200 字以内的核心摘要
    2. 提炼 3-5 个关键发现或结论
    3. 提取文中明确提出的行动项或建议（如果有的话）
    """,
)

runner = Runner()
result = runner.run(agent, long_article)
print(result.final_output)
```

> 注意：摘要场景对模型上下文窗口有要求。如果文章过长（超过模型上下文限制），需要先做分段处理。Agentic 支持通过 `agentic-tools` 中的文件读取工具来分段加载大文本。

---

### 3.4 场景四：提单字段自动提取

**输入**：用户在聊天框中自由描述的出差需求。

**输出**：结构化的字段信息，可直接填入 OA 系统的出差申请单。

```python
user_input = "我下周三到周五要去上海参加 AI 技术峰会，需要订机票和酒店，预算大概 5000 块。"

agent = create_agent(
    name="form_extractor",
    instruction="""你是一个出差申请单自动填写助手。请从用户的自由描述中提取以下字段，
    以 JSON 格式输出。如果某个字段用户没有提及，填写 null。
    
    需要提取的字段：
    - depart_city: 出发城市
    - dest_city: 目的地城市
    - depart_date: 出发日期
    - return_date: 返回日期
    - purpose: 出差事由
    - needs_flight: 是否需要机票（true/false）
    - needs_hotel: 是否需要酒店（true/false）
    - budget: 预算金额（数字）
    """,
)

runner = Runner()
result = runner.run(agent, user_input)
print(result.final_output)
```

**模型输出示例**：

```json
{
  "depart_city": null,
  "dest_city": "上海",
  "depart_date": "下周三",
  "return_date": "下周五",
  "purpose": "参加 AI 技术峰会",
  "needs_flight": true,
  "needs_hotel": true,
  "budget": 5000
}
```

> 关键洞察：用户只说了一句自然语言，模型就能将隐含信息（"去上海"隐含"需要机票和酒店"）推断出来并结构化。这正是大模型在信息提取场景中的核心价值。

---

### 3.5 四场景的共同特征

回顾上面四个场景，它们共享以下特征：

1. **输入信息一次给齐**：你不是分多轮逐步提供信息，而是在第一轮就把所有上下文一次性交给模型。会议纪要场景，你给了会议全文；制度问答场景，你给了制度文档 + 员工问题；长文摘要场景，你给了全文；提单场景，你给了用户的整段描述。

2. **不需要查其他系统**：执行任务所需的全部信息已经包含在输入中。模型不需要连接数据库、不需要查询企业内部 API、不需要翻看历史记录——它只需要"理解"你给的文本，然后输出结果。

3. **单次请求即可完成**：不需要多轮对话，不需要多次推理。一个请求进去，一个结果出来。模型自身的能力足以覆盖整个任务。

这三条特征背后隐含了一个判断标准：**如果你的任务满足"信息充分 + 不依赖外部 + 单次请求"，那它就是一个 Prompt 工程问题，不需要引入 Agent 的复杂编排**。

---

### 3.6 万能公式：给上下文 + 给任务 = 拿结果

把四个场景抽象到极致，就是一句话：

> **给上下文 + 给任务 = 拿结果**

这个公式包含了三个角色：

```
给上下文 ────→  你提供什么信息给模型？
   +
给任务   ────→  你要求模型做什么？
   =
拿结果   ────→  模型输出什么？
```

用这个公式去套上面的四个场景：

| 场景 | 给上下文 | 给任务 | 拿结果 |
|------|--------|-------|-------|
| 会议纪要 | 会议转写原文 | 整理摘要 + 议题 + 待办 | 结构化会议纪要 |
| 制度问答 | 制度全文 + 员工问题 | 依据制度回答 | 带条款引用的答复 |
| 长文摘要 | 长文章全文 | 摘要 + 关键发现 + 行动项 | 精简摘要 |
| 提单提取 | 用户自由描述 | 提取结构化字段 | JSON |

这个公式看起来极其简单，但它揭示了一个重要事实：**大模型的应用起点不是 Agent，而是 Prompt**。当你遇到一个需求，先问自己：能不能用一次请求完成？如果答案是"能"，那就用一个 Prompt 搞定。只有当单次请求搞不定的时候，才需要引入 Agent 的循环推理和工具调用。

---

## 四、会议纪要——人能看懂，系统用不了

上一章我们展示了会议纪要的结构化输出。看起来模型完成任务了——它整理出了摘要、议题、待办事项。但这里隐藏着一个关键问题：**这个输出是给人看的，还是给系统用的？**

本章以会议纪要为例，深入剖析"人类可读"和"机器可解析"之间的鸿沟，以及为什么 ReAct Agent 对结构化输出有刚性需求。

---

### 4.1 场景重演：从录音到结构化 To-Do

把场景还原得更加真实一点。假设你有一段 30 分钟的会议录音，经过语音识别转成了文字：

```
陈总：好，那我们开始。今天主要对齐一下下周上线的几个问题。

小王：我先说吧。支付模块昨天压测发现一个问题，QPS 到 2000 的时候响应
时间会突然飙升到 5 秒以上，排查初步定位在数据库连接池的配置上。

陈总：这个问题要马上解决。小李，你是后端负责人，你来牵头。小王配合你，
把排查结果整理出来。

小李：好的。我这两天看了一下，目前连接池最大是 50，在高并发下确实不够。
建议调大到 200，同时加上连接超时自动回收机制。

陈总：可以。另外，前端那边进度怎么样？

小张：H5 页面基本完成，但 iOS 端有一个 WebView 兼容问题，已经提了 issue。

陈总：这个问题谁在跟？

小张：还没分配……我觉得阿杰比较熟悉 WebView。

陈总：那就阿杰。另外，上线前的回归测试，测试团队这边，小赵来负责统筹。
所有 P0 用例必须跑通，不允许有遗留。

小赵：收到。我需要一个完整的测试环境，目前 staging 环境的后台服务
还是旧版本。

陈总：小李，你那边部署完了通知小赵。

小李：没问题，明天下午部署。

陈总：好，那今天就到这里。大家确认一下自己的任务，明天站会同步进度。
```

你的目标是把这段文字变成**下游系统可以直接消费的结构化数据**。

---

### 4.2 给人看 OK，给系统看不行

如果只是"给人看"，你让模型做一个自然语言摘要就够了：

```
会议摘要：
本次会议主要对齐下周上线事项。小李负责数据库连接池优化（连接数从 50 调到 200，
增加超时自动回收），明天下午部署 staging 环境。阿杰负责修复 iOS WebView 兼容问题。
小赵统筹回归测试，所有 P0 用例必须跑通。小王配合小李完成排查整理。
```

这段文字，任何同事看了都明白什么意思。**但如果把它丢给一个自动化系统呢？**

设想你要把待办事项自动同步到飞书任务、Jira 或企业 OA。程序需要知道：

- 哪些文字属于"摘要"而不是"待办"？
- 有几个任务？每个任务分给了谁？
- 截止日期是哪天？（原文只说了"明天下午"，那"明天"到底是哪天？）
- 任务之间有没有依赖关系？

上面那段自然语言输出**完全回答不了这些问题**。原因是：

```
自然语言摘要
─────────────────────────────
"小李负责数据库连接池优化……"
   ↑
   人阅读时：大脑自动解析出"小李→连接池优化→明天下午"
   程序解析时：需要 NLP → 实体识别 → 关系抽取 → 规则匹配 → 仍然可能出错

结构化输出
─────────────────────────────
{
  "tasks": [
    {
      "assignee": "小李",
      "title": "数据库连接池优化",
      "deadline": "2026-07-04T15:00:00"
    }
  ]
}
   ↑
   程序解析时：json.loads() → 直接用
```

**给人看的东西和给系统用的东西，在格式要求上是两个量级**。

---

### 4.3 ReAct Loop 对结构化输出的刚性需求

这个"格式鸿沟"不仅仅影响下游消费方。在 Agentic 框架内部，ReAct 循环的每一步也对结构化输出有严格的依赖。

回顾 ReAct 模式的核心循环：

```
┌─────────┐     ┌──────────┐     ┌──────────────┐
│  PLAN   │ ──→ │  ACTION  │ ──→ │ OBSERVATION  │
│  计划   │     │  执行动作  │     │   观察结果    │
└─────────┘     └──────────┘     └──────────────┘
      ↑                                    │
      └────────────────────────────────────┘
             根据观察结果，更新计划，继续循环
```

在这个循环中，每一步都要求输出格式精确：

1. **Plan（计划）**：模型必须输出可执行的步骤列表，每一步要有明确的意图。
2. **Action（动作）**：模型输出的不是一个模糊的"我要查点什么"，而是一个精确的函数调用——函数名、参数名、参数值，一个字符都不能错。
3. **Observation（观察）**：工具调用的返回结果。如果上一步的 Action 格式不对，工具直接报错，Observation 就是错误信息，整个循环就此中断。

**错误格式 vs 正确格式对比：**

```
❌ 错误的 Action 输出（给人看）：
   "我接下来需要搜索一下数据库连接池的最佳实践"

✅ 正确的 Action 输出（给系统用）：
   {
     "tool_name": "web_search",
     "parameters": {
       "query": "PostgreSQL 连接池 高并发 最佳配置",
       "max_results": 5
     }
   }
```

左边的输出人看得懂，但 Agentic 框架不会把它当成一个工具调用。右边的 JSON 才是 Agent 的"语言"。

> **核心认知**：Agent 不是在对"你"说话，Agent 是在对"工具系统"说话。Agent 和工具系统之间的通信协议，就是结构化 JSON。未来最靠谱的 Agent 实现路径是以 Function Call 或 MCP 为标准，让 Agent 在一个可解析、可验证的协议下与工具和系统交互——这就是 **MCP（Model Context Protocol）** 等标准协议存在的根本原因。

---

### 4.4 下游系统期望的格式

回到会议纪要的场景。假设下游有一个"To-Do 生成器"，它期望收到这样的数据：

```json
{
  "meeting_id": "MT-2026-0703-001",
  "summary": "本次会议对齐下周上线事项，确认了数据库优化、前端兼容修复、回归测试三项任务的负责人和时间节点。",
  "tasks": [
    {
      "id": 1,
      "title": "数据库连接池优化",
      "description": "将连接池上限从 50 调整到 200，增加连接超时自动回收机制。完成后部署 staging 环境。",
      "assignee": "小李",
      "collaborators": ["小王"],
      "deadline": "2026-07-04T15:00:00",
      "priority": "P0",
      "status": "待开始"
    },
    {
      "id": 2,
      "title": "修复 iOS WebView 兼容问题",
      "description": "H5 页面在 iOS 端 WebView 中出现兼容性问题，已提 issue，需排查并修复。",
      "assignee": "阿杰",
      "collaborators": ["小张"],
      "deadline": null,
      "priority": "P1",
      "status": "待开始"
    },
    {
      "id": 3,
      "title": "统筹回归测试",
      "description": "上线前回归测试统筹，所有 P0 用例必须跑通，不允许遗留。需要 staging 环境支持。",
      "assignee": "小赵",
      "collaborators": [],
      "deadline": null,
      "priority": "P0",
      "status": "等待依赖（依赖任务1完成）"
    }
  ]
}
```

这个 JSON 结构的每一个字段都有明确的含义和类型：

| 字段 | 类型 | 说明 |
|------|------|------|
| `meeting_id` | string | 会议编号，用于关联 |
| `summary` | string | 一段话摘要 |
| `tasks[].id` | integer | 任务序号 |
| `tasks[].title` | string | 任务标题（简短） |
| `tasks[].description` | string | 任务详细描述 |
| `tasks[].assignee` | string | 主要负责人 |
| `tasks[].collaborators` | array | 协助人员列表 |
| `tasks[].deadline` | string / null | 截止时间（ISO 8601） |
| `tasks[].priority` | string | 优先级（P0/P1/P2） |
| `tasks[].status` | string | 当前状态 |

**下游系统的每一个微服务都依赖这些字段做决策**：
- 飞书机器人读 `assignee` 字段 → 给对应的人发消息
- Jira 同步服务读 `tasks` 数组 → 逐个创建 Issue
- 日报生成器读 `summary` + `tasks[].status` → 自动生成每日进度报告
- 告警系统读 `deadline` → 到期前自动提醒

如果模型输出的只是"小李负责数据库优化，明天下午完成"这样一句自然语言，上面这些系统全部瘫痪。

---

### 4.5 从"人能看懂"到"机器可解析"的跨越

那么问题来了：**怎样让模型稳定地输出结构化的 `tasks` 数组？**

这需要两步：

**第一步：明确输出格式约束**

在 Agent 的 `instruction` 或 `output_type` 中，非常具体地描述期望的 JSON Schema。不是泛泛地说"输出一个 JSON"，而是精确到每个字段的类型、必填/选填、枚举值范围。

```python
agent = create_agent(
    name="meeting_parser",
    instruction="""你是会议纪要结构化解析器。请将会议记录解析为以下 JSON 格式：
    
    {
      "meeting_id": "会议编号（字符串）",
      "summary": "会议核心摘要（字符串，不超过 200 字）",
      "tasks": [
        {
          "id": 1,
          "title": "任务标题",
          "description": "详细描述",
          "assignee": "主要负责人姓名",
          "collaborators": ["协助人员1", "协助人员2"],
          "deadline": "截止时间，格式 YYYY-MM-DDTHH:mm:ss，无法确定则填 null",
          "priority": "P0 / P1 / P2",
          "status": "待开始 / 进行中 / 等待依赖 / 已完成"
        }
      ]
    }
    
    规则：
    1. 每个 task 必须独立可解析
    2. 所有日期必须标准化为 YYYY-MM-DD 格式，时间用 HH:mm:ss
    3. priority 的判断标准：P0=阻塞上线，P1=重要但不阻塞，P2=一般
    4. 如果原文未提及某个字段，填 null（不要编造）
    """,
)
```

**第二步：验证输出是否合法**

拿到模型输出后，还需要加一层验证：

```python
import json

raw_output = result.final_output

try:
    parsed = json.loads(raw_output)
    # 验证顶层字段
    assert "tasks" in parsed, "缺少 tasks 字段"
    assert isinstance(parsed["tasks"], list), "tasks 必须是数组"
    
    # 验证每个任务
    for task in parsed["tasks"]:
        assert "assignee" in task, f"任务 {task.get('id')} 缺少 assignee"
        assert "title" in task, f"任务 {task.get('id')} 缺少 title"
    
    print("✅ 输出格式验证通过")
    # 现在可以安全地传给下游系统了
except (json.JSONDecodeError, AssertionError) as e:
    print(f"❌ 输出格式异常: {e}")
    print("原始输出:", raw_output)
```

> 把这两步串起来，就是 Agent 开发中最重要的一个闭环：**约束 → 生成 → 验证 → 重试**。先定义输出 Schema（约束），让模型按 Schema 生成（生成），解析并检查生成的 JSON（验证），如果验证失败就重新请求（重试）。这个闭环直接引出了下一章的主题——**如何让 Agent 输出稳定、可预期的结构化结果**，这是企业级智能体系统的核心挑战。

---

**本章小结**：单次请求能解决"信息齐备 + 不依赖外部"的任务，这是大模型应用的第一步。但"人能看懂"的输出和"机器能解析"的输出之间存在鸿沟——自然语言无法被下游系统直接消费，ReAct 循环也依赖精确的 Action 格式。填补这道鸿沟的方法，是在 Prompt 中约定严格的输出 Schema，并对输出做验证。下一章我们将深入到 Agent 的核心循环机制，看模型如何通过"思考-行动-观察"的循环来完成单次请求无法搞定的复杂任务。

---

## 五、裸调模型的困境——五种输出形态

在前面的章节中，我们学会了如何搭建环境、接入模型、安装工具链。从这一章开始，我们要面对一个所有 Agent 开发者都无法绕开的核心问题：**模型返回的内容是不确定的**。这不是某一个模型的质量问题，而是大语言模型作为概率性系统的本质属性。

在这一章里，我们用"裸调"的方式——即直接用 HTTP 请求调用模型 API，不借助任何框架的封装——来演示这个问题的真实面貌。你会看到，一个看似简单的"让模型返回 JSON"的需求，在实际工程中会演变成五种截然不同的输出形态。

---

### 5.1 起点：一切看起来很简单

假设我们正在构建一个天气查询 Agent。用户输入"今天上海天气怎么样"，我们需要模型将这句话解析为结构化的查询参数，然后交给工具函数去执行。最朴素的想法是：写一段 prompt，告诉模型"请返回 JSON"，然后 `json.loads()` 解析即可。

```python
import httpx
import json

# 最朴素的做法：直接请求，直接解析
async def naive_weather_query(user_input: str):
    prompt = f"""
    请将以下用户查询解析为JSON格式的天气查询参数。
    
    用户查询：{user_input}
    
    请返回如下格式的JSON：
    {{"city": "城市名", "date": "日期或null"}}
    只返回JSON，不要加任何其他文字。
    """

    response = await httpx.AsyncClient().post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={"Authorization": "Bearer sk-xxx"},
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30.0,
    )

    data = response.json()
    content = data["choices"][0]["message"]["content"]
    result = json.loads(content)  # ← 这里会爆炸
    return result
```

运行这段代码，你大概率会看到这样的错误：

```
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

发生了什么？模型返回的 `content` 长这样：

````
```json
{"city": "上海", "date": null}
```
````

模型很"贴心"地用 Markdown 代码块把 JSON 包了起来。这很符合人类的阅读习惯——在聊天界面里，代码块让 JSON 看起来更清晰。但对于 `json.loads()` 来说，第一行的三个反引号就是语法错误。

---

### 5.2 第一次修补：去掉 Markdown 包裹

发现这个问题后，你的第一反应大概率是：加一行 `replace` 把反引号去掉就行了。

```python
def parse_model_output(raw_content: str) -> dict:
    """第一次修补：去除 Markdown 代码块标记"""
    content = raw_content.strip()

    # 去掉开头的 ```json 或 ```
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]

    # 去掉结尾的 ```
    if content.endswith("```"):
        content = content[:-3]

    return json.loads(content.strip())
```

测试一下，DeepSeek 返回的内容现在能正确解析了。你满意地提交了代码，心想这个问题已经解决了。

但事情远没有这么简单。因为你只处理了**一种**输出形态。而在真实世界中，模型可能以至少**五种**完全不同的形态返回它的"JSON"。

---

### 5.3 五种输出形态全景

下面是一个系统性的分类。每一种我都给出了真实的代码示例——它们都来自模型实际返回的内容，不是虚构的边界情况。

---

#### 形态一：干净 JSON（最理想，但也最不可靠）

```
{"city": "上海", "date": null}
```

这是最理想的情况：模型严格遵循 prompt 指令，返回了纯净的 JSON 字符串。`json.loads()` 一次通过，没有任何额外处理。

**出现概率**：取决于模型和 prompt 质量。DeepSeek V3 在明确指令下大约 70%-80% 的概率返回干净 JSON。GPT-4 类似。但注意——即便是 80%，也意味着每五次调用就有一次不是你期望的形态。

---

#### 形态二：Markdown 代码块包裹

````
```json
{"city": "上海", "date": null}
```
````

这是最常见的"不干净"形态。模型为了在对话上下文中展示代码，会自动给输出加上 Markdown 代码块标记。

**出现概率**：在 DeepSeek 中约占 15%-20%，在 GPT-4 的系统指令不够明确时也常出现。国内模型如 Qwen（通义千问）在对话场景下尤其倾向于加代码块。

**处理方式**：

```python
import re

def extract_from_markdown(content: str) -> str:
    """从 Markdown 代码块中提取 JSON"""
    # 匹配 ```json ... ``` 或 ``` ... ```
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return content
```

---

#### 形态三：前后附加自然语言

```
好的，按照你的要求，我将用户查询解析为以下JSON格式的天气查询参数：

{"city": "上海", "date": null}

以上是整理结果，如果需要进一步处理请告诉我。
```

这是百度文心一言（ERNIE）的标志性行为，但 GPT-4 和 DeepSeek 在某些 prompt 下也会出现。模型在输出 JSON 之前和之后附加了礼貌性的自然语言——它在跟你"对话"，而不是在"返回数据"。

**出现概率**：文心一言中约占 30%-40%。其他模型在 prompt 不够强硬时约占 5%-10%。

**处理方式**：

```python
import re

def extract_json_from_text(content: str) -> str:
    """从混合了自然语言的文本中提取 JSON 对象"""
    # 尝试找到第一个 { 和最后一个 }
    first_brace = content.find("{")
    last_brace = content.rfind("}")

    if first_brace == -1 or last_brace == -1:
        raise ValueError("文本中未找到 JSON 对象")

    return content[first_brace:last_brace + 1]
```

这种方法看似简单有效，但它有一个隐含假设：**文本中只有一对花括号**。如果模型的自然语言中也包含了花括号（比如举例说明），提取逻辑就会出错。

---

#### 形态四：含有多余逗号或注释（合法 JSON5，非法 JSON）

```json
{
    "city": "上海",
    "date": null,        // 用户未指定日期
}
```

注意末尾的 `null,` 后面的逗号——在标准 JSON 中，对象最后一个属性后面不能有逗号。但模型经常"顺手"加上逗号，因为它在训练数据中见过大量 JavaScript/JSON5 风格的代码。更麻烦的是注释——`//` 和 `/* */` 在 JSON 中是非法的，但模型会"很自然地"添加注释来解释字段含义。

**出现概率**：约占 3%-8%。在使用过 JavaScript/TypeScript 训练数据的模型中更常见。

**处理方式**：

```python
import re

def sanitize_json_like(content: str) -> str:
    """清理 JSON 中的非法元素"""
    # 去除单行注释 //...
    content = re.sub(r"//.*", "", content)
    # 去除多行注释 /* ... */
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
    # 去除尾部逗号（对象和数组中的）
    content = re.sub(r",(\s*[}\]])", r"\1", content)
    return content
```

或者直接使用 `json5` 库（如果允许引入额外依赖）：

```python
import json5  # pip install json5

def parse_with_json5(content: str) -> dict:
    """使用 json5 解析宽松格式的 JSON"""
    return json5.loads(content)
```

---

#### 形态五：字段缺失或多余

```json
{"city": "上海"}
```

模型有时候会"遗忘" prompt 中指定的某些字段。在这个例子里，`date` 字段消失了——模型可能判断"用户没有提日期，所以不需要这个字段"。但也可能走向另一个极端，添加 prompt 中没有要求的字段：

```json
{"city": "上海", "date": null, "province": "上海市", "country": "中国", "language": "zh"}
```

模型"热心"地补充了省份、国家、语言信息。

**出现概率**：约占 5%-10%。在温度参数较高（>0.7）或 prompt 描述不精确时更常见。

**处理方式**：

```python
from typing import Any

REQUIRED_FIELDS = {"city", "date"}
ALLOWED_FIELDS = {"city", "date"}

def validate_fields(data: dict[str, Any]) -> dict[str, Any]:
    """验证字段完整性和合法性"""
    # 检查必填字段
    missing = REQUIRED_FIELDS - set(data.keys())
    if missing:
        raise ValueError(f"缺少必填字段: {missing}")

    # 过滤多余字段（可选策略：是丢弃还是保留取决于业务需求）
    extra = set(data.keys()) - ALLOWED_FIELDS
    if extra:
        print(f"警告：检测到多余字段 {extra}，已自动过滤")
        data = {k: v for k, v in data.items() if k in ALLOWED_FIELDS}

    return data
```

---

### 5.4 五种形态对比总览

```
+==================================================================================+
|                         五种模型输出形态对比总览                                    |
+==================================================================================+
|                                                                                  |
|  形态         |  示例特征                    |  出现概率   |  解析策略            |
|---------------|-----------------------------|------------|---------------------|
|  ① 干净JSON   |  {"city":"上海"}            |  70-80%    |  直接 json.loads    |
|  ② Markdown   |  ```json ... ```             |  15-20%    |  正则提取代码块      |
|  ③ 前后文字   |  好的，按照要求...{...}以上 |  5-40%     |  定位首尾花括号      |
|  ④ 宽松格式   |  尾逗号、注释、单引号       |  3-8%      |  json5 / 正则清理    |
|  ⑤ 字段异常   |  缺字段或多余字段           |  5-10%     |  字段校验+过滤       |
|                                                                                  |
|  ⚠️ 关键认知：这五种形态不是互斥的——一次输出可以同时具备多种特征。                |
|  例如：Markdown包裹 + 尾逗号 + 字段缺失，三种问题叠加在一次返回中。               |
|                                                                                  |
+==================================================================================+
```

---

### 5.5 核心论点：概率性问题，工程上不容许任何一次失败

现在我们来谈最关键的认知。上面的表格里有一个"出现概率"列。你可能会想：形态一占 70%-80%，大部分时候都是干净的，我针对形态二做点处理不就覆盖 95% 的情况了吗？

```
+============================================================================+
|                      为什么"95% 够了"是幻觉                                   |
+============================================================================+
|                                                                            |
|  假设你的 Agent 每天处理 1000 次请求，解析成功率 95%：                        |
|                                                                            |
|    1000 × 5% = 50 次失败/天                                                  |
|                                                                            |
|  50 次失败意味着：                                                          |
|  - 50 个用户看到错误信息而非天气结果                                        |
|  - 50 次可能的客服投诉                                                      |
|  - 如果这是支付场景，50 笔异常交易需要人工核查                               |
|                                                                            |
|  工程上有一条铁律：                                                          |
|                                                                            |
|    概率性失败 = 确定性失败                                                   |
|                                                                            |
|  只要失败有可能发生，它就一定会发生——而且你不知道它什么时候发生。             |
|  你不能跟产品经理说"大部分时候都能用"。                                      |
|  你不能跟用户说"再试一次就好了"。                                            |
|                                                                            |
|  一个生产级 Agent 对结构化输出的要求是：                                     |
|  100% 的调用都有确定的、可预期的解析结果——要么成功，要么有明确的错误信息。   |
|                                                                            |
+============================================================================+
```

这不是危言耸听。我们来看一个真实的例子。假设你写了这样一段"防御代码"：

```python
def flawed_parse(content: str) -> dict:
    """一个有缺陷的防御解析器——看似覆盖了各种情况，实则处处是漏洞"""
    content = content.strip()

    # 只处理了 Markdown 包裹的情况
    if content.startswith("```"):
        lines = content.split("\n")
        # 假设第一行是 ```json，最后一行是 ```
        json_lines = lines[1:-1]
        content = "\n".join(json_lines)

    # 直接 json.loads——碰到形态三、四、五都会炸
    return json.loads(content)
```

这段代码的问题在于：它只处理了形态二，对形态三、四、五完全没有防御。而当你试图用正则去覆盖更多情况时，又会引入新的问题。

---

### 5.6 正则的困境：解决问题同时也在制造问题

你可能会想：那我写一个强大的正则表达式，把五种形态全覆盖了不就行了？

```python
import re

def overly_aggressive_extract(content: str) -> dict:
    """一个过于激进的正则提取器——它可能破坏本已干净的 JSON"""

    # 尝试匹配 JSON 对象
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if not match:
        raise ValueError("未找到 JSON 对象")

    json_str = match.group(0)

    # 清理常见问题
    json_str = re.sub(r"//.*", "", json_str)           # 去注释
    json_str = re.sub(r",(\s*[}\]])", r"\1", json_str) # 去尾逗号

    return json.loads(json_str)
```

这段代码看起来覆盖了很多情况。但请考虑以下场景：

**场景一：模型返回了干净的 JSON**

```json
{"city": "上海", "description": "今天天气{很好}，适合出行"}
```

正则 `\{.*\}` 在 `re.DOTALL` 模式下是贪婪匹配。对于上面的输入，它可能会匹配到 `{"city": "上海", "description": "今天天气{很好}`，因为第一个 `}` 对应的是 `很好` 后面的右花括号——注意 JSON 值中包含了花括号字符。正则无法区分"JSON 结构的边界花括号"和"字符串值中的花括号"。

**场景二：模型返回了多层嵌套 JSON**

```json
{"city": "上海", "forecast": {"temp": 28, "condition": "多云"}}
```

正则的贪心/非贪心策略在嵌套结构面前天然脆弱。要正确解析嵌套 JSON，你需要一个真正的解析器，而不是正则表达式。

**核心矛盾**：

```
+============================================================================+
|                    正则 vs 解析器：核心矛盾                                   |
+============================================================================+
|                                                                            |
|  正则表达式处理的是"字符模式"（character pattern）。                         |
|  JSON 是一种"上下文无关文法"（context-free grammar）。                       |
|                                                                            |
|  用正则解析 JSON，等同于用扳手拧螺丝——能凑合用，但不能保证每次都对。         |
|                                                                            |
|  更致命的是：                                                              |
|  - 正则越"聪明"、覆盖情况越多，它对干净 JSON 的误伤概率越大                  |
|  - 正则越"保守"、只在特定情况下触发，对复杂异常（如形态三）的覆盖率越低      |
|                                                                            |
|  这是一个零和博弈。你无法用一个正则表达式同时做到"高覆盖"和"零误伤"。        |
|                                                                            |
+============================================================================+
```

---

### 5.7 Demo 与生产环境的差距

最后一个关键点：你调通的 Demo 和你需要交付的生产系统，面对的是完全不同的世界。

```
+============================================================================+
|                       Demo vs 生产环境                                       |
+============================================================================+
|                                                                            |
|  Demo 环境：                                                               |
|  ┌─────────────────────────────────────────────────────────────────┐       |
|  │  模型固定：DeepSeek V3，一个模型用到底                            │       |
|  │  调用频率：手动测试，偶尔跑一跑                                   │       |
|  │  失败处理：看到了就改一下代码，没看到就算了                        │       |
|  │  防御策略：针对 DeepSeek 的习性写几个 replace                     │       |
|  │  评审标准："看起来能跑"                                            │       |
|  └─────────────────────────────────────────────────────────────────┘       |
|                                                                            |
|  生产环境：                                                               |
|  ┌─────────────────────────────────────────────────────────────────┐       |
|  │  模型不固定：今天 DeepSeek，下个月可能换成 GLM-4、Qwen3、文心     │       |
|  │  调用频率：每天数千到数万次                                       │       |
|  │  失败处理：每一次失败都可能触发告警、影响用户体验、产生脏数据      │       |
|  │  防御策略：需要应对所有模型的所有输出习性                          │       |
|  │  评审标准："一次都不能挂"                                          │       |
|  └─────────────────────────────────────────────────────────────────┘       |
|                                                                            |
|  关键差距：                                                                 |
|  - 模型习性差异：DeepSeek 喜欢加 ```json```，文心喜欢加"好的，按照..."     |
|  - 每换一个模型，你为上一个模型写的 replace 逻辑可能就失效了               |
|  - 甚至同一个模型的不同版本（如 DeepSeek V2 → V3）行为也会改变             |
|  - 私有化部署的模型（如企业内部微调的 Llama）行为完全不可预测              |
|                                                                            |
+============================================================================+
```

一个真实的工程故事：某团队用 DeepSeek 开发了内部工具，针对 DeepSeek 的 Markdown 包裹习惯写了清理逻辑，测试一切正常。三个月后，出于成本考虑切换到 Qwen3-8B。切换当天，30% 的请求开始返回形态三（前后附加自然语言）和形态四（尾逗号），原有的清理逻辑全部失效。团队花了两周时间逐个修补，写了两百多行 if-else。

这不是 DeepSeek 的问题，也不是 Qwen 的问题。**这是"裸调"本身的问题——你把解析逻辑和特定模型的输出习性绑定了。**

---

### 5.8 小结：裸调的四个致命缺陷

通过上面的演示和分析，我们可以归纳出裸调的四个致命缺陷：

| 缺陷 | 具体表现 | 后果 |
|------|---------|------|
| **概率性** | 输出格式不固定，同一种 prompt 可能得到五种不同形态 | 无法保证 100% 可用 |
| **耦合性** | 解析逻辑依赖特定模型的输出习性 | 换模型就要改代码 |
| **不可观测** | 失败时不知道模型究竟返回了什么、为什么解析失败 | 排查困难，无法优化 |
| **不可维护** | 防御代码随模型增加而膨胀，regex/if-else 层层叠加 | 代码腐化，新人不敢动 |

这四个缺陷不是靠写更聪明的正则就能解决的。它们指向一个共同的需求：**我们需要一套系统性的方法，来处理"让模型输出结构化数据"这件事。** 这就是下一章要讨论的内容。

---

## 六、结构化输出的五个层次

在第五章中，我们看到了"裸调"的困境——模型的输出是不确定的，而工程系统要求绝对的可靠性。这两个需求之间存在根本性的张力。解决这个张力的方法，就是**结构化输出（Structured Output）**。

结构化输出不是一个"有"或"没有"的二元概念。它是一个从零到完备的渐进体系。理解这五个层次，你就能在任何场景下找到正确的解决方案——既不过度工程化（为一个 Demo 搭建完整链路），也不欠工程化（让一个支付系统靠 regex 来解析模型输出）。

---

### 6.1 第一层：毫无约束（自由文本 → 手动解析）

```
+============================================================================+
|                     第一层：毫无约束                                          |
+============================================================================+
|                                                                             |
|  模型输出：自由文本（任意格式）                                               |
|  解析方式：完全靠开发者手动写规则                                             |
|  工程可靠性：接近零                                                          |
|                                                                             |
|  典型代码：                                                                  |
|  ┌─────────────────────────────────────────────────────────────────────┐     |
|  │  response = model.chat("今天天气怎么样")                             │     |
|  │  # 模型返回："今天上海天气晴朗，气温28度，湿度65%，适合出行"          │     |
|  │  # 你怎么把 "28度" 提取成 temp=28？                                  │     |
|  │  temp = extract_temp_with_regex(response)  # 脆弱、不可靠            │     |
|  └─────────────────────────────────────────────────────────────────────┘     |
|                                                                             |
|  在这一层，开发者面对的是完全无结构的自然语言输出。要从中提取结构化信息，     |
|  只能靠正则表达式、关键词匹配、甚至 if-else 分支。这不是工程——这是猜谜。    |
|                                                                             |
+============================================================================+
```

第一层的典型场景是早期 NLP 项目或课程作业：用 `input()` 读一行文本，`if "天气" in text` 判断意图，`re.search(r"\d+度", text)` 提取温度。在 Agent 系统中，这一层意味着你放弃了对模型输出的任何结构性约束，把解析的负担完全转嫁给了手写的规则引擎。

**为什么还在用**：并非所有人都意识到还有更好的方法。很多初学者因为看到过"让 ChatGPT 输出 JSON"的教程，就以为在 prompt 里写一句"请返回 JSON"就够了。他们不知道——或者还没有被坑过——模型并不会总是乖乖听话。

---

### 6.2 第二层：Prompt 约束（口头约定）

```
+============================================================================+
|                     第二层：Prompt 约束                                      |
+============================================================================+
|                                                                             |
|  模型输出：期望是 JSON，实际上不确定                                         |
|  解析方式：先 json.loads()，失败了再说                                       |
|  工程可靠性：约 80-90%（取决于模型和 prompt 质量）                           |
|                                                                             |
|  典型代码：                                                                  |
|  ┌─────────────────────────────────────────────────────────────────────┐     |
|  │  prompt = """                                                       │     |
|  │  请将以下用户查询解析为JSON格式。                                     │     |
|  │  只返回JSON，不要加任何其他文字。                                     │     |
|  │  格式：{"city": "...", "date": "..."}                                │     |
|  │  """                                                               │     |
|  │  response = model.chat(prompt)                                      │     |
|  │  result = json.loads(response)  # 祈祷不要出错                       │     |
|  └─────────────────────────────────────────────────────────────────────┘     |
|                                                                             |
+============================================================================+
```

第二层是目前工业界最常见的做法。即便是大厂的 AI 产品，很多也停留在这个层次。开发者写了一段精心设计的 prompt，用强烈语气告诉模型"请返回 JSON，不要加多余文字"。然后直接 `json.loads()`。

**令人惊讶的事实**：很多月活千万的 AI 产品，其后台对模型输出的处理就是第二层。它们能工作是因为：

1. 选择了格式遵循度高的模型（GPT-4、Claude 在这方面表现很好）
2. 设置了较低的温度参数（`temperature=0` 或接近 0）
3. 做了充分的 prompt 工程（few-shot examples、详细格式说明）
4. 在产品层面容忍了偶发的失败（用户看到错误提示后可以重试）

但正如第五章详细展示的，第二层的可靠性是概率性的。你不知道哪一次调用会返回五种形态中的哪一种。对于关键业务场景——支付、医疗、法律——80-90% 的成功率是不可接受的。

**第二层的正确使用场景**：
- 内部工具和原型验证
- 用户容忍度高的 C 端产品（如聊天机器人、内容生成）
- 有重试机制兜底的场景（失败了让用户再试一次）
- 输出有二次人工审核的流程

---

### 6.3 第三层：Schema 注入（框架介入）

```
+============================================================================+
|                     第三层：Schema 注入                                      |
+============================================================================+
|                                                                             |
|  框架行为：                                                                  |
|  1. 接收开发者定义的 Schema（如 Pydantic 模型）                              |
|  2. 将 Schema 转换为结构化的 prompt 指令                                     |
|  3. 注入到发给模型的请求中                                                   |
|  4. 从模型返回中自动提取和解析 JSON                                          |
|                                                                             |
|  典型代码（以 LangChain 的 with_structured_output 为例）：                    |
|  ┌─────────────────────────────────────────────────────────────────────┐     |
|  │  from pydantic import BaseModel, Field                             │     |
|  │  from langchain_openai import ChatOpenAI                           │     |
|  │                                                                     │     |
|  │  class WeatherQuery(BaseModel):                                    │     |
|  │      city: str = Field(description="城市名称")                      │     |
|  │      date: str | None = Field(default=None, description="日期")     │     |
|  │                                                                     │     |
|  │  model = ChatOpenAI(model="gpt-4")                                 │     |
|  │  structured_model = model.with_structured_output(WeatherQuery)      │     |
|  │  result: WeatherQuery = structured_model.invoke("今天上海天气")      │     |
|  │  print(result.city)  # "上海" —— 已经是 WeatherQuery 对象           │     |
|  └─────────────────────────────────────────────────────────────────────┘     |
|                                                                             |
|  核心价值：                                                                  |
|  - Schema 定义即文档：字段名、类型、描述集中在一处                             |
|  - 自动生成 prompt 指令：框架负责把 Schema 翻译成模型能理解的格式              |
|  - 自动解析：框架负责处理 Markdown 包裹等常见问题                             |
|  - 类型安全：返回值是强类型的 Pydantic 对象，IDE 可以自动补全                  |
|                                                                             |
+============================================================================+
```

第三层的核心思想是：**将 Schema 定义作为系统与模型之间的契约**。开发者定义"我想要什么结构"，框架负责"让模型输出这个结构"和"把输出解析成这个结构"。

在第三层，框架做的事情大致包括：

1. **Schema 到 Prompt 的转换**：把 Pydantic 的字段名、类型、描述转换成模型能理解的格式指令。例如：
   ```
   你必须以 JSON 格式回复。你的回复必须严格遵循以下 JSON Schema：
   {
     "type": "object",
     "properties": {
       "city": {"type": "string", "description": "城市名称"},
       "date": {"type": ["string", "null"], "description": "日期"}
     },
     "required": ["city"]
   }
   ```

2. **输出提取**：框架内置了类似第五章中讨论的 JSON 提取逻辑，但经过了充分测试和社区验证，覆盖了大多数常见异常情况。

3. **类型转换**：自动将 JSON 中的字符串 `"28"` 转换为 Python 的 `int`，将 `null` 转换为 `None`，确保返回对象符合类型定义。

第三层的可靠性显著高于第二层，对于大多数业务场景来说已经足够。但它有一个盲区：**解析失败时怎么办？**

---

### 6.4 第四层：注入 + 验证 + 重试

```
+============================================================================+
|                     第四层：注入 + 验证 + 重试                                 |
+============================================================================+
|                                                                             |
|  在第三层的基础上增加：                                                       |
|  1. 字段级验证：检查必填字段是否存在、类型是否正确                             |
|  2. 业务规则验证：city 不能是空字符串、date 必须是合法日期                    |
|  3. 重试机制：解析失败时，将错误信息反馈给模型，让它重新生成                    |
|                                                                             |
|  典型代码：                                                                  |
|  ┌─────────────────────────────────────────────────────────────────────┐     |
|  │  from typing import Any                                            │     |
|  │  import json                                                       │     |
|  │                                                                     │     |
|  │  MAX_RETRIES = 3                                                   │     |
|  │                                                                     │     |
|  │  def structured_call_with_retry(model, schema, user_input):         │     |
|  │      """带重试机制的结构化调用"""                                     │     |
|  │      errors = []                                                   │     |
|  │                                                                     │     |
|  │      for attempt in range(MAX_RETRIES):                             │     |
|  │          try:                                                      │     |
|  │              raw_output = model.invoke(user_input)                 │     |
|  │              parsed = extract_and_parse(raw_output)                │     |
|  │              validated = schema.model_validate(parsed)             │     |
|  │              return validated  # 成功，返回                         │     |
|  │                                                                     │     |
|  │          except json.JSONDecodeError as e:                          │     |
|  │              errors.append(f"JSON解析失败: {e}")                    │     |
|  │          except ValidationError as e:                               │     |
|  │              errors.append(f"字段验证失败: {e.errors()}")           │     |
|  │                                                                     │     |
|  │          # 将错误信息反馈给模型，要求重新生成                         │     |
|  │          retry_prompt = f"""                                        │     |
|  │          你上次的输出有错误，请修正后重新输出。                        │     |
|  │          错误信息：{errors[-1]}                                      │     |
|  │          请严格按照要求的 JSON Schema 输出。                          │     |
|  │          """                                                       │     |
|  │          model = model.with_retry_context(retry_prompt)             │     |
|  │                                                                     │     |
|  │      raise RuntimeError(f"重试{MAX_RETRIES}次后仍然失败: {errors}")  │     |
|  └─────────────────────────────────────────────────────────────────────┘     |
|                                                                             |
+============================================================================+
```

第四层是生产级 Agent 系统的**最低标准**。核心逻辑很简单：

```
第一轮：模型输出 → 解析 → 验证 → 成功 ✓
                           → 失败 → 把错误信息传给模型 → 第二轮
第二轮：模型看到错误信息 → 重新输出 → 解析 → 验证 → 成功 ✓
                                           → 失败 → 第三轮
第三轮：最后一次尝试
```

这个模式之所以有效，是因为模型在收到"你上次的 JSON 格式不对"这样的反馈后，有很高的概率修正错误。模型比你更擅长生成正确的 JSON——它只是偶尔"手滑"。给它第二次、第三次机会，成功率会大幅提升。

**实践数据**：
- 某生产系统，单次解析成功率 ~92%
- 加入一次重试后，累积成功率 ~98%
- 加入两次重试后，累积成功率 ~99.5%

那剩下的 0.5% 怎么办？这就是第五层要解决的问题。

---

### 6.5 第五层：全链路可观测

```
+============================================================================+
|                     第五层：全链路可观测                                      |
+============================================================================+
|                                                                             |
|  记录每一次调用的完整上下文，用于问题排查和持续优化：                          |
|                                                                             |
|  记录内容：                                                                  |
|  ┌─────────────────────────────────────────────────────────────────────┐     |
|  │  1. 请求快照：发送给模型的完整 prompt（含系统指令、用户输入、历史）    │     |
|  │  2. 原始输出：模型返回的原始文本（解析前，一字不改）                    │     |
|  │  3. 解析过程：使用的解析策略、每一步的中间结果                          │     |
|  │  4. 失败原因：具体的异常类型、错误信息、发生在哪一步                     │     |
|  │  5. 重试记录：每次重试的 prompt 变化和输出变化                          │     |
|  │  6. 环境信息：模型名称、温度参数、时间戳、请求 ID                       │     |
|  └─────────────────────────────────────────────────────────────────────┘     |
|                                                                             |
|  典型代码：                                                                  |
|  ┌─────────────────────────────────────────────────────────────────────┐     |
|  │  import logging, json, time, uuid                                   │     |
|  │  from dataclasses import dataclass, field, asdict                   │     |
|  │                                                                     │     |
|  │  @dataclass                                                        │     |
|  │  class CallTrace:                                                  │     |
|  │      trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)│     |
|  │      timestamp: float = field(default_factory=time.time)            │     |
|  │      model: str = ""                                               │     |
|  │      temperature: float = 0.0                                       │     |
|  │      prompt_snapshot: str = ""                                     │     |
|  │      raw_output: str = ""                                          │     |
|  │      parse_strategy: str = ""                                      │     |
|  │      parse_success: bool = False                                   │     |
|  │      error_info: str | None = None                                 │     |
|  │      retry_count: int = 0                                          │     |
|  │      retry_details: list[dict] = field(default_factory=list)       │     |
|  │                                                                     │     |
|  │  # 每次调用都记录完整 trace                                         │     |
|  │  trace = CallTrace(                                                │     |
|  │      model="deepseek-chat",                                        │     |
|  │      prompt_snapshot=final_prompt,                                 │     |
|  │      raw_output=raw_response,                                      │     |
|  │  )                                                                 │     |
|  │  logger.info(json.dumps(asdict(trace), ensure_ascii=False))         │     |
|  └─────────────────────────────────────────────────────────────────────┘     |
|                                                                             |
+============================================================================+
```

第五层的价值不在于"让成功率从 99.5% 提升到 99.9%"，而在于**让你知道那 0.5% 的失败到底发生了什么**。

没有可观测性时，你的排查流程是这样的：

```
用户反馈："天气查询不好使"
开发者：打开代码 → 看了看解析逻辑 → "看起来没问题啊"
        → 猜测是某个特殊情况 → 加一行 if → 部署 → 等下次失败
        → 循环往复
```

有可观测性时：

```
系统告警：过去 1 小时内有 3 次结构化输出解析失败
开发者：打开日志平台 → 搜索 trace → 看到原始输出是形态三
        → 定位到 extract_json_from_text 函数中首尾花括号的定位逻辑
        → 发现在特定 prompt 下，模型的自然语言中也包含花括号 → 修复
        → 修复后可以回溯历史 trace，确认不会再触发 → 部署
```

**可观测性不是一次性的调试工具，而是一个持续运行的反馈循环**——它让你能够在模型行为发生变化时第一时间感知到，并有数据支撑你的优化决策。

---

### 6.6 五层总览与工程选型

```
+==================================================================================+
|                           结构化输出五层体系总览                                    |
+==================================================================================+
|                                                                                  |
|  层次  |  名称              |  可靠性      |  复杂度    |  典型场景               |
|--------|--------------------|-------------|-----------|------------------------|
|  第一层 |  毫无约束          |  ~0-50%     |  低        |  实验、课程作业          |
|  第二层 |  Prompt 约束       |  ~80-90%    |  低        |  内部工具、原型、C端     |
|  第三层 |  Schema 注入       |  ~95%       |  中        |  一般生产环境            |
|  第四层 |  注入+验证+重试    |  ~99.5%     |  中高      |  关键业务场景            |
|  第五层 |  全链路可观测      |  可优化至    |  高        |  长期维护的生产系统      |
|        |                    |  ~99.9%+     |           |                         |
|                                                                                  |
+==================================================================================+
```

**工程上的关键认知**：第二、三、四层不是"选一个"的关系，而是**都得做**。

- **第二层（Prompt 约束）**：不管你用了多高级的框架，prompt 永远是第一道防线。好的 prompt 能减少模型的异常输出概率，也就能减少后续层的处理负担。
- **第三层（Schema 注入）**：让框架替你处理常见的格式问题。它比手写正则可靠得多，因为有社区维护和测试覆盖。
- **第四层（验证+重试）**：在框架的自动解析之上再加一层业务验证，确保字段满足你的具体需求。重试机制为偶发失败提供了缓冲。
- **第五层（可观测）**：让你知道系统在发生什么，不会在出了问题之后两眼一抹黑。

这四层（二到五）形成了一条**纵深防御链**：prompt 让模型尽量输出正确格式 → 框架自动处理常见格式异常 → 验证确保业务字段完整 → 重试兜底偶发失败 → 可观测性让一切透明可控。

---

## 七、Schema 约束——为什么不能只靠接口

在前两章中，我们讨论了模型输出的五种不确定形态和结构化输出的五个层次。你可能会有一个疑问：**这些问题的根源是不是 API 层面就能解决？** 毕竟 OpenAI 提供了 `response_format: { type: "json_object" }` 参数，设置为 `"json_schema"` 模式后模型"应该"严格输出符合 Schema 的 JSON。

这个想法的前半句是对的——API 层面的约束确实存在。但后半句是想当然的。这一章我们要论证一个核心观点：**Schema 约束这一层控制必须做在工程层，不能依赖模型接口层。**

---

### 7.1 OpenAI 的 json_format：理想很丰满

OpenAI 从 2023 年开始提供 `response_format` 参数，API 层面保证模型输出合法的 JSON：

```python
from openai import OpenAI

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "今天上海天气怎么样"}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "weather_query",
            "schema": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "date": {"type": ["string", "null"]},
                },
                "required": ["city"],
            },
        },
    },
)

# response.choices[0].message.content 保证是合法的 JSON
result = json.loads(response.choices[0].message.content)
```

这个机制的工作原理是：OpenAI 在推理过程中做了约束解码（constrained decoding），在模型生成每个 token 时限制其只能选择符合 JSON Schema 的 token。这从数学上保证了输出是合法的 JSON。

**问题在于**：这个机制只在 OpenAI 的 API 中可用。而且即使是在 OpenAI 内部，`json_schema` 模式也只对部分模型开放（gpt-4o、gpt-4-turbo 及更新版本）。

---

### 7.2 现实一：国内模型大多不提供这个能力

当你把上面的代码从 `gpt-4o` 换成任意一个国内模型时：

```python
# 尝试在 DeepSeek 上使用 response_format
response = client.chat.completions.create(
    model="deepseek-chat",  # 换了模型
    messages=[{"role": "user", "content": "今天上海天气怎么样"}],
    response_format={"type": "json_object"},  # DeepSeek 不支持此参数
)
# 结果：
# openai.BadRequestError: Error code: 400 - {'error': {'message':
# 'response_format is not supported', 'type': 'invalid_request_error'}}
```

DeepSeek 的 API 兼容 OpenAI 的接口格式，但**不包含 response_format 功能**。同样的限制适用于：

| 模型提供商 | 是否支持 response_format | 备注 |
|-----------|------------------------|------|
| OpenAI (GPT-4o) | 支持 (json_schema) | 仅限新模型 |
| OpenAI (GPT-3.5) | 支持 (json_object) | 不含 Schema 约束 |
| Anthropic (Claude) | 不通过此参数 | 通过 tool_use 间接实现 |
| DeepSeek (V3/R1) | 不支持 | 完全依赖 prompt |
| 百度文心 (ERNIE) | 部分支持 | 仅在特定版本中可用 |
| 阿里通义 (Qwen) | 部分支持 | DashScope API 有独立实现 |
| 智谱 (GLM) | 不支持 | zhipuai SDK 无此参数 |
| 月之暗面 (Moonshot) | 不支持 | 依赖 prompt |
| Ollama 本地模型 | 不支持 | 原生不支持 |
| vLLM 私有部署 | 取决于配置 | 需要额外设置 guided decoding |

**这张表传递的信息很明确**：`response_format` 是 OpenAI 的专有特性，不是行业标准。你在开发 Agent 时，如果要对接多个模型或支持灵活切换，就不能假设这个能力一定存在。

---

### 7.3 现实二：LangChain 的 format 控制同样依赖底层接口

你可能会想：LangChain 的 `with_structured_output` 不是能自动处理这些吗？答案是——它在底层做的事情是：

```
LangChain with_structured_output
    │
    ├── 检测到 OpenAI 模型
    │   └── 使用 response_format 参数 → 可靠
    │
    ├── 检测到 Anthropic 模型
    │   └── 使用 tool_use 机制 → 较可靠
    │
    └── 检测到其他模型（DeepSeek、文心、GLM...）
        └── 回退到 prompt 注入模式 → 回到第五章的困境
```

LangChain 的 `with_structured_output` 在你使用 OpenAI 模型时调用的就是 `response_format`，可靠性很高。但当你把模型换成 DeepSeek 或文心一言时，LangChain 检测到这些模型不支持 API 级别的约束，会自动回退到**第二层（Prompt 约束）模式**——在 prompt 里加上"请返回 JSON"，然后尝试解析。

**在这种情况下，LangChain 给你的保障并不比你自己写 prompt 高多少**。它提供的价值是：
- 自动生成格式化的 prompt 指令（比手写更规范）
- 内置 JSON 提取逻辑（经过了社区测试）
- 统一的调用接口（换模型时不需要改业务代码）

但它**不能**像 OpenAI 的 `response_format` 那样从数学上保证输出是合法的 JSON。该出现五种形态还是会出现的。

---

### 7.4 现实三：私有化部署的推理框架不会提供这个

如果你的 Agent 需要部署在客户内网，使用客户自己的 GPU 集群跑模型（一个非常常见的 B2B 场景），你会面对这样的环境：

```
+============================================================================+
|                    私有化部署的典型技术栈                                      |
+============================================================================+
|                                                                            |
|  推理框架层：vLLM / TGI (Text Generation Inference) / llama.cpp             |
|      │                                                                     |
|      │  这些框架的核心职责：                                                |
|      │  - 高效加载模型权重并做推理                                          |
|      │  - 管理 KV Cache、批处理请求                                        |
|      │  - 提供 OpenAI 兼容的 API 端点（/v1/chat/completions）              |
|      │                                                                     |
|      │  它们通常不包含：                                                    |
|      │  ✗ response_format 约束解码                                         |
|      │  ✗ tool_use / function calling 原生支持                             |
|      │  ✗ JSON Schema 级别的 token 约束                                    |
|      │                                                                     |
|  模型层：客户的私有模型（如微调过的 Llama-3 / Qwen / ChatGLM）              |
|      │                                                                     |
|      │  这个模型：                                                         |
|      │  - 可能经过了客户自己的微调（fine-tuning）                           |
|      │  - 微调数据可能改变了模型对 JSON 指令的响应行为                      |
|      │  - 输出习性完全不可预测                                              |
|      │                                                                     |
+============================================================================+
```

在这种环境下，你连"换一个支持 response_format 的模型"这个选项都没有。客户只有一个模型，跑在他们自己的机器上，你必须适配它——而不是它来适配你。

---

### 7.5 核心结论：工程层控制不可替代

综合以上三个现实，我们可以得出一个明确的结论：

```
+============================================================================+
|                                                                            |
|         Schema 约束必须做在工程层，不能依赖模型接口层                          |
|                                                                            |
+============================================================================+
|                                                                            |
|  原因一：能力碎片化                                                         |
|  ┌─────────────────────────────────────────────────────────────────┐       |
|  │  response_format 是 OpenAI 专属的，不是通用的行业标准。           │       |
|  │  国内模型、开源模型、私有化部署的推理框架——都不保证提供。          │       |
|  │  如果你的架构假设"所有模型都支持 response_format"，               │       |
|  │  那你的可用模型列表只剩下 OpenAI 的少数几个。                     │       |
|  └─────────────────────────────────────────────────────────────────┘       |
|                                                                            |
|  原因二：模型与运行逻辑的分离                                               |
|  ┌─────────────────────────────────────────────────────────────────┐       |
|  │  模型驱动的运行逻辑（解析、验证、重试）与模型本身是分离的。        │       |
|  │  上游换模型时，你的防御逻辑不应该跟着改——它应该独立于模型存在。    │       |
|  │                                                                  │       |
|  │  正确的关系：                                                     │       |
|  │    业务代码 → 工程层结构化输出控制 → 任意模型                      │       |
|  │                                                                  │       |
|  │  错误的关系：                                                     │       |
|  │    业务代码 → 模型A（依赖A的response_format）                      │       |
|  │    换模型B → 修改业务代码（B没有response_format）  ← 耦合         │       |
|  └─────────────────────────────────────────────────────────────────┘       |
|                                                                            |
|  原因三：防御策略需要统一封装                                               |
|  ┌─────────────────────────────────────────────────────────────────┐       |
|  │  第五章讨论的五种输出形态，每一种都需要对应的处理逻辑。             │       |
|  │  如果每个业务模块都自己写一遍这些逻辑，代码重复、质量参差不齐。    │       |
|  │  如果把这些处理统一封装在工程层，所有业务模块共用同一套逻辑，      │       |
|  │  维护和优化只需要在一个地方进行。                                  │       |
|  └─────────────────────────────────────────────────────────────────┘       |
|                                                                            |
+============================================================================+
```

---

### 7.6 框架的价值：封装差异，屏蔽变化

理解了"工程层控制不可替代"之后，框架（如 LangChain）的真正价值就清晰了。框架不是在替你调用 API——你自己也能调用 API。框架的价值在于：

```
+============================================================================+
|                    框架在结构化输出中的真正价值                                 |
+============================================================================+
|                                                                            |
|  1. 统一入口，屏蔽模型差异                                                   |
|  ┌─────────────────────────────────────────────────────────────────┐       |
|  │  # 同样的代码，不同的模型                                         │       |
|  │  result = structured_model.invoke(user_input)                    │       |
|  │                                                                  │       |
|  │  # 底层自动适配：                                                │       |
|  │  # OpenAI  → 使用 response_format（最可靠）                       │       |
|  │  # DeepSeek → prompt 注入 + 输出提取                              │       |
|  │  # 文心     → prompt 注入 + 中文友好提取                           │       |
|  │  # 私有部署 → prompt 注入 + 可配置的提取策略                       │       |
|  └─────────────────────────────────────────────────────────────────┘       |
|                                                                            |
|  2. 内置防御逻辑，持续迭代                                                   |
|  ┌─────────────────────────────────────────────────────────────────┐       |
|  │  框架的 JSON 提取逻辑经过了：                                     │       |
|  │  - 数千个项目的实际使用验证                                       │       |
|  │  - 社区的 issue 反馈和 bug 修复                                   │       |
|  │  - 对新模型的持续适配                                             │       |
|  │                                                                  │       |
|  │  你自己写的 200 行 if-else 没有这些。                              │       |
|  └─────────────────────────────────────────────────────────────────┘       |
|                                                                            |
|  3. 让你专注业务逻辑，而非解析细节                                           |
|  ┌─────────────────────────────────────────────────────────────────┐       |
|  │  不用框架时，你的代码结构：                                       │       |
|  │    业务逻辑 (20%) + 模型调用 (30%) + 解析防御 (50%)               │       |
|  │                                                                  │       |
|  │  用框架后，你的代码结构：                                         │       |
|  │    业务逻辑 (80%) + 模型调用+解析 (20%)                           │       |
|  │                                                                  │       |
|  │  那 50% 的解析防御去哪儿了？框架替你做了。                         │       |
|  └─────────────────────────────────────────────────────────────────┘       |
|                                                                            |
|  4. 降低模型切换成本                                                         |
|  ┌─────────────────────────────────────────────────────────────────┐       |
|  │  场景：从 GPT-4 切换到 DeepSeek V3（成本考虑）                     │       |
|  │                                                                  │       |
|  │  裸调方式：                                                       │       |
|  │    改 API endpoint → 改认证方式 → 发现 response_format 不支持     │       |
|  │    → 删掉依赖 response_format 的代码 → 加 prompt 指令             │       |
|  │    → 发现 DeepSeek 的输出习性和 GPT-4 不一样 → 改写解析逻辑       │       |
|  │    → 测试 → 又发现新的边缘 case → 继续改 → 两周过去了              │       |
|  │                                                                  │       |
|  │  框架方式：                                                       │       |
|  │    改一行模型名称：model="gpt-4" → model="deepseek-chat"          │       |
|  │    框架自动适配所有下游差异。                                      │       |
|  └─────────────────────────────────────────────────────────────────┘       |
|                                                                            |
+============================================================================+
```

---

### 7.7 架构决策总结

回顾第五、六、七三章的内容，我们可以提炼出 Agent 系统在结构化输出方面的核心架构原则：

```
+==================================================================================+
|                       结构化输出的核心架构原则                                       |
+==================================================================================+
|                                                                                  |
|  原则一：永远不要假设模型的输出是干净的                                               |
|  ───────────────────────────────────────────                                       |
|  模型的输出有至少五种不同的形态。你的解析逻辑必须覆盖全部五种，                       |
|  并且做好"这五种形态可能以任意组合叠加出现"的准备。                                   |
|                                                                                  |
|  原则二：纵深防御，多层兜底                                                         |
|  ───────────────────────────────────────────                                       |
|  Prompt 约束（L2）→ Schema 注入（L3）→ 验证+重试（L4）→ 可观测（L5）                |
|  每一层都是上一层的补充，不是替代。                                                  |
|                                                                                  |
|  原则三：工程层控制，不依赖接口层                                                   |
|  ───────────────────────────────────────────                                       |
|  response_format 是奢侈品，不是标配。你的结构化输出控制逻辑必须独立于模型接口，        |
|  能够在任何模型（OpenAI / DeepSeek / 文心 / 私有部署）上正常工作。                    |
|                                                                                  |
|  原则四：模型与防御逻辑解耦                                                         |
|  ───────────────────────────────────────────                                       |
|  换模型不应该意味着改防御代码。框架通过抽象层将模型差异封装起来，                       |
|  让业务代码只关心"要什么结构"，不关心"这个模型怎么输出"。                              |
|                                                                                  |
|  原则五：失败必须可追溯                                                             |
|  ───────────────────────────────────────────                                       |
|  每一次解析失败都应该留下完整的调用轨迹。没有 trace 的失败就是黑箱，                   |
|  你永远不知道是 prompt 的问题、模型的问题、还是解析逻辑的问题。                        |
|                                                                                  |
+==================================================================================+
```

这三章组合在一起，回答了 Agent 开发中最核心的一个工程问题：**如何让一个本质上不确定的系统（大语言模型），产生确定的、可依赖的输出。** 答案不是"找到一个完美的模型"，而是"构建一套多层次的工程防护体系"。这套体系的核心思想——纵深防御、工程层控制、模型与逻辑解耦——将在后续章节中反复出现，因为它们贯穿了整个 Agent 系统的设计哲学。

---

# Agentic Schema 语法详解

> 基于教学视频课程整理编写 · 2026年7月

---

## 目录

- [八、Schema as Prompt——用代码思维定义输出结构](#八schema-as-prompt用代码思维定义输出结构)
- [8.1 Schema as Prompt 概念：所见即所得](#81-schema-as-prompt-概念所见即所得)
- [8.2 Schema 字典结构：外层结构到叶子节点](#82-schema-字典结构外层结构到叶子节点)
- [8.3 Tuple 三元组详解](#83-tuple-三元组详解)
- [8.4 ensure_keys 与 ensure_all](#84-ensure_keys-与-ensure_all)
- [8.5 max_retries：重试上限](#85-max_retries重试上限)
- [8.6 完整代码示例——会议纪要 Schema](#86-完整代码示例会议纪要-schema)
- [8.7 链式调用与分段构建](#87-链式调用与分段构建)
- [8.8 get_text 与 get_data](#88-get_text-与-get_data)
- [8.9 本章小结](#89-本章小结)

---

## 八、Schema as Prompt——用代码思维定义输出结构

### 8.1 Schema as Prompt 概念：所见即所得

在你已掌握的 Pydantic Schema 基础上，**Agentic Schema** 再往前迈了一步：它不只是数据校验层，而是把 Schema 本身当作 Prompt 的一部分——用代码逻辑构建业务诉求，框架自动生成高质量的提示词指令。

```
传统 Schema（Pydantic）          Agentic Schema（本课）
─────────────────────────       ────────────────────────
定义数据结构 → 配合                用字典+Tuple三元组定义结构
with_structured_output →       Schema 本身即 Prompt →
只做数据校验 → 出错抛异常          框架自动生成提示词+校验链 →
                                内置Locator+JSON5解析 →
                                出错自动重试（带错误上下文）

类比：                             类比：
盖房子前画一张图纸                  图纸里不但有结构，还写了每个房间
施工队照着图纸盖                    的用途说明，施工队看了图纸就自己
                                  知道怎么盖
```

**核心洞察**：你用三元组中写的描述性文字，最终会原样进入发给模型的 Prompt 中。定义 Schema 的过程本身就是 Prompt Engineering。你不需要手写冗长的 System Prompt 来描述输出格式——只用 Python 字典说清「我需要哪些字段、每个字段是什么类型、在业务上代表什么含义」，剩下全部交给框架。

这种设计哲学称为 **Schema as Prompt**——所见即所得，用代码的精确性替代自然语言的模糊性。

### 8.2 Schema 字典结构：外层结构到叶子节点

Agentic Schema 使用**嵌套字典 + 叶子节点 Tuple** 描述输出格式。语法规则只有两条：

- **规则一**：外层用 dict 组织，列表字段用 `[...]`，嵌套对象用 `{...}`
- **规则二**：叶子节点必须用 tuple 三元组定义，不能是裸 `str`/`int`/`list`

```
Schema 字典结构解剖：

schema = {
    "field_a": (str, "..."),        ← 叶子：tuple 三元组
    "field_b": [(str, "...")],      ← 列表叶子：list of tuple
    "field_c": {                    ← 嵌套对象
        "sub": (str, "...")         ← 叶子：tuple 三元组
    },
    "field_d": [{                   ← 对象数组
        "key": (str, "...")
    }]
}
```

### 8.3 Tuple 三元组详解

每个叶子节点由三元组 `(type, description, ensure)` 定义：

```
三元组结构：(type, description, ensure)

元素1 — 类型声明 (type)
  str     字符串
  int     整数
  bool    布尔
  float   浮点数
  list    列表（如 ["高","中","低"] 枚举）
  
  ⚠️ 必须是 Python 基本类型或可 JSON 序列化的简单集合
  ✅ str, int, float, bool, list, dict
  ❌ class, function, object, 自定义对象
  原因：类型声明最终被转换进 JSON Schema，JSON Schema 只理解基本类型

元素2 — 描述性声明 (description)
  业务语义，告诉模型这个字段是什么意思
  会原样进入最终 Prompt，成为提示词的一部分
  示例：
    "会议标题，简洁概括本次会议主题"
    "会议时间，格式 YYYY-MM-DD HH:MM"
    "优先级，可选值：高 / 中 / 低"
  技巧：描述越清楚，模型越准，重试越少

元素3 — 确保标记 (ensure)
  True  → 框架运行时检查该字段是否存在且类型正确
  False → 不参与确保检查
  核心：ensure 不出现于 Prompt 中，是框架运行时的检查指令
        在 start() 时，根据 ensure_keys 参数决定实际检查哪些字段
```

**实际使用示例：**

```python
schema = {
    "title":      (str, "会议标题，简洁概括本次会议主题", True),
    "time":       (str, "会议时间，格式 YYYY-MM-DD HH:MM", True),
    "duration":   (int, "会议时长（分钟）", False),
    "is_online":  (bool, "是否为线上会议", False),
    "priority":   (["高", "中", "低"], "会议优先级", True),
    "attendees":  [(str, "参会人员姓名")],
}
```

### 8.4 ensure_keys 与 ensure_all

框架提供两种确保策略，在 `start()` 时指定：

```
ensure_keys(["a", "b"])             ensure_all=True
─────────────────────────           ─────────────────
只确保指定的 key 出现                 确保所有 ensure=True 的 key 出现
阶段性校验 / 只需要部分字段            最终输出 / 需要完整数据结构

schema.start(                       schema.start(
    info=text,                          info=text,
    ensure_keys=["title","time"]        ensure_all=True,
)                                   )
```

**工作流程**：

```
模型输出解析完成
        │
        ▼
┌───────────────────┐
│ 检查 ensure_keys / │
│ ensure_all 指定的  │
│ 字段是否存在且类型  │
│ 正确              │
└────────┬──────────┘
         │
   ┌─────┼─────┐
   ▼     ▼     ▼
全部通过  部分缺失  严重缺失
   │     │     │
   ▼     ▼     ▼
返回dict 带错误信息 带错误信息
        重试请求   重试请求
```

关键设计：检查不通过时**不抛异常**，而是把缺失信息打包进下一次请求的 Prompt 上下文，告诉模型「你上次漏了字段 X」，模型修正概率大幅提升。

### 8.5 max_retries：重试上限

`max_retries` 是安全熔断器，决定校验失败时最多自动重试几次：

```
第1次请求 → 输出 → 校验失败（缺少字段X）
  ├─ 第2次（带错误信息"补充字段X"）→ 输出 → 校验失败（字段Y类型错误）
  │   ├─ 第3次（带"字段Y类型应为str"）→ 输出 → ✅ 通过 → 返回
  │   └─ 若 retries 耗尽 → ❌ 抛异常，业务层 catch 做容错
```

| 值 | 含义 | 场景 |
|---|---|---|
| 3（默认） | 最多重试3次 | 常规业务，平衡可靠性与成本 |
| 0 | 不重试，失败即抛 | 测试阶段 |
| 5+ | 更多重试 | 复杂输出结构 |
| -1 | 不支持 | 必须有限，防止打光系统资源 |

### 8.6 完整代码示例——会议纪要 Schema

```python
from agentic_schema import Schema

# ── Step 1: 定义 Schema ──
meeting_schema = Schema({
    "title":       (str, "会议标题，简洁概括本次会议主题", True),
    "time":        (str, "会议时间，格式 YYYY-MM-DD HH:MM", True),
    "duration":    (int, "会议时长（分钟）", False),
    "host":        (str, "主持人姓名", True),
    "attendees":   [(str, "参会人员姓名")],

    "agenda": [{
        "topic":   (str, "议题名称", True),
        "speaker": (str, "发言人", False),
        "duration": (int, "该议题讨论时长（分钟）", False),
        "summary": (str, "讨论摘要，50字以内", True),
    }],

    "decisions": [{
        "content":  (str, "决议内容", True),
        "owner":    (str, "负责人", True),
        "deadline": (str, "截止日期，格式 YYYY-MM-DD", True),
        "priority": (["高", "中", "低"], "优先级", True),
    }],

    "next_meeting": (str, "下次会议时间，如未确定填'待定'", False),
    "notes":        (str, "其他备注信息", False),
})

# ── Step 2: 准备输入 ──
meeting_info = """
产品周会会议记录（2026年7月1日 14:00-15:30）
主持人：张伟
参会人员：李明、王芳、赵强、刘丽

议题1（14:00-14:25）：Q2用户增长数据复盘
  发言人：李明。Q2新增用户50万，环比增长12%，主来源短视频渠道投放。
  
议题2（14:25-14:50）：海外版V2.0上线排期
  发言人：赵强。功能开发完成85%，UI多语言适配需2周，预计7月20日提测。

议题3（14:50-15:15）：客户投诉率上升问题
  发言人：王芳。6月投诉率1.8%（5月为1.2%），集中在物流和客服响应。
  决定：成立专项小组，王芳牵头，两周内出整改方案。

决议：
1. 李明负责Q3总体增长策略方案，7月10日前提交
2. 赵强每周三同步海外版开发进度
3. 王芳成立服务质量专项小组，两周内出整改方案

下次会议：7月8日（周三）14:00
"""

# ── Step 3: start 启动 ──
result = meeting_schema.start(
    info=meeting_info,
    ensure_all=True,
    max_retries=3,
)

# ── Step 4: 获取结果 ──
data = result.get_data()   # dict 结构化数据
text = result.get_text()   # str 原始输出

# ── Step 5: 使用数据 ──
print(f"会议标题：{data['title']}")
print(f"主持人：{data['host']}")
print(f"决议数量：{len(data['decisions'])} 条")
for i, d in enumerate(data['decisions'], 1):
    print(f"  决议{i}：{d['content']} | 负责人：{d['owner']} | 截止：{d['deadline']}")
```

**运行输出示例：**

```
会议标题：Q2用户增长复盘与海外版上线排期会议
主持人：张伟
决议数量：3 条
  决议1：制定Q3总体增长策略方案 | 负责人：李明 | 截止：2026-07-10
  决议2：每周三同步海外版开发进度 | 负责人：赵强 | 截止：持续进行
  决议3：成立服务质量专项小组并出整改方案 | 负责人：王芳 | 截止：两周内
```

### 8.7 链式调用与分段构建

框架支持 Builder Pattern 链式调用，不必一次性准备好所有信息：

```python
from agentic_schema import Schema

# ── 方式一：分段构建 ──
schema = Schema({
    "summary":    (str, "事件摘要", True),
    "sentiment":  (["积极", "消极", "中性"], "情感倾向", True),
    "key_points": [(str, "关键要点")],
    "action":     (str, "建议行动", False),
})

# 先堆砌信息
schema.set_info("这是一段关于新功能上线的用户反馈...")
schema.set_system_prompt("你是一位数据分析师")

# 中间做其他处理...
processed = some_other_function()
schema.set_info(processed)

# 最后再启动
result = schema.start(ensure_all=True, max_retries=3)

# ── 方式二：一次性链式写完 ──
result = (
    Schema({"name": (str, "用户姓名", True),
            "age":  (int, "用户年龄", False)})
    .set_info("张三今年25岁")
    .start(ensure_keys=["name"])
)

# ── 方式三：Schema 复用（每次 start 是独立调用）──
shared = Schema({"intent": (["查询","下单","投诉"], "用户意图", True)})
r1 = shared.start(info="我想查一下我的订单", ensure_keys=["intent"])
r2 = shared.start(info="我要投诉快递太慢了", ensure_keys=["intent"])
```

### 8.8 get_text 与 get_data

两种输出方式对应不同使用场景：

```
get_text()                    get_data()
───────────                   ──────────
• 返回 str                    • 返回 dict
• 模型原始输出                  • 解析后的结构化数据
• 用于：调试/日志/自定义解析      • 用于：业务逻辑/存库/前端展示

生产代码模式：
result = schema.start(info=input_text, ensure_all=True)
data = result.get_data()         # 业务处理用 data
logger.debug(result.get_text())  # 原始文本写日志
```

### 8.9 本章小结

```
┌─────────────────────────────────────────────────────────────┐
│              Agentic Schema 语法速查卡片                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  核心思想：Schema as Prompt —— 数据结构即提示词               │
│                                                             │
│  基础语法：dict 外层 → tuple 三元组叶子节点                    │
│                                                             │
│  三元组：(type, description, ensure)                         │
│    类型：str / int / bool / list / ...（必须可序列化）        │
│    描述：业务语义，进入 Prompt                                 │
│    确保：True/False，运行时检查，不进入 Prompt                 │
│                                                             │
│  确保策略：                                                  │
│    ensure_keys=["a","b"] → 只确保指定 key                    │
│    ensure_all=True        → 确保全部 ensure=True 的 key      │
│                                                             │
│  容错机制：max_retries=3（默认）→ 最多重试次数                │
│                                                             │
│  输出方式：                                                  │
│    get_text() → 原始文本（调试）                              │
│    get_data() → 结构化 dict（业务）                           │
│                                                             │
│  下一课：M09 七步确保机制                                     │
│    → Schema 在框架内部的完整转化、校验、确保链路               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

# 七步确保机制

> 基于教学视频课程整理编写 · 2026年7月

---

## 目录

- [九、七步确保——从 Prompt 到可靠输出的完整链路](#九七步确保从-prompt-到可靠输出的完整链路)
- [9.1 全景流程图](#91-全景流程图)
- [9.2 Step 1：Schema → Prompt Generator](#92-step-1schema--prompt-generator)
- [9.3 Step 2：模型生成文本](#93-step-2模型生成文本)
- [9.4 Step 3：Locator 状态机定位闭合 JSON（重点）](#94-step-3locator-状态机定位闭合-json重点)
- [9.5 Step 4：JSON5 宽松解析](#95-step-4json5-宽松解析)
- [9.6 Step 5：Pydantic 校验](#96-step-5pydantic-校验)
- [9.7 Step 6：Ensure Keys 检查](#97-step-6ensure-keys-检查)
- [9.8 Step 7：返回 dict / 抛出异常](#98-step-7返回-dict--抛出异常)
- [9.9 每步可独立使用](#99-每步可独立使用)
- [9.10 完整链路代码示例](#910-完整链路代码示例)
- [9.11 本章小结](#911-本章小结)

---

## 九、七步确保——从 Prompt 到可靠输出的完整链路

表面上看只是调了一次 `schema.start()`，背后实际经历了**七个串联的步骤**，每一步都有明确的职责和容错策略。理解这七步，才能真正掌握 Agentic Schema 的可靠性来源——它不是「赌模型会输出正确结果」，而是构建了一套完整的保障链路。

### 9.1 全景流程图

```
┌──────────────────────────────────────────────────────────────────┐
│                    七步确保——完整处理流程                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  用户代码：schema.start(info=text, ensure_all=True, max_retries=3)│
│                          │                                       │
│                          ▼                                       │
│  ╔════════════════════════════════════════════════════════════╗  │
│  ║ Step 1: Prompt Generator                                  ║  │
│  ║ Schema 字典 → 遍历 + 模板拼装 → 可执行的 Prompt 指令        ║  │
│  ╚════════════════════════╤═══════════════════════════════════╝  │
│                           │                                      │
│                           ▼                                      │
│  ╔════════════════════════════════════════════════════════════╗  │
│  ║ Step 2: 模型生成文本 → Prompt → LLM API → 原始文本响应      ║  │
│  ╚════════════════════════╤═══════════════════════════════════╝  │
│                           │                                      │
│                           ▼                                      │
│  ╔════════════════════════════════════════════════════════════╗  │
│  ║ Step 3: Locator（状态机）定位闭合 JSON  ← ⚠️ 核心技术       ║  │
│  ║ 原始文本 → 逐字符扫描状态机 → 精确定位 {} 闭合区间 O(n)      ║  │
│  ╚════════════════════════╤═══════════════════════════════════╝  │
│                           │                                      │
│                           ▼                                      │
│  ╔════════════════════════════════════════════════════════════╗  │
│  ║ Step 4: JSON5 宽松解析                                    ║  │
│  ║ JSON 字符串 → json5.loads() → Python dict                  ║  │
│  ║ 容忍：注释 // /* */、尾随逗号、单引号、无引号 key           ║  │
│  ╚════════════════════════╤═══════════════════════════════════╝  │
│                           │                                      │
│                           ▼                                      │
│  ╔════════════════════════════════════════════════════════════╗  │
│  ║ Step 5: Pydantic 校验                                     ║  │
│  ║ dict → Schema 自动转换 Pydantic Model → model_validate()   ║  │
│  ║ 校验：字段名是否存在、类型是否正确                          ║  │
│  ╚════════════════════════╤═══════════════════════════════════╝  │
│                           │                                      │
│                           ▼                                      │
│  ╔════════════════════════════════════════════════════════════╗  │
│  ║ Step 6: Ensure Keys 检查                                  ║  │
│  ║ 检查 ensure_keys/ensure_all 指定字段 → 缺失则带错误信息重试 ║  │
│  ║ 全部通过 → Step 7  |  有缺失 → 回 Step 1（计数器+1）       ║  │
│  ╚════════════════════════╤═══════════════════════════════════╝  │
│                           │                                      │
│               ┌───────────┼───────────┐                          │
│               ▼           ▼           ▼                          │
│           全通过      部分缺失     重试耗尽                         │
│               │           │           │                          │
│               │           ▼           ▼                          │
│               │     返回 Step 1   ╔══════════════════════════╗   │
│               │    (携带错误信息)  ║ Step 7: 返回 dict        ║   │
│               │                  ║ 全部通过 → Result 对象    ║   │
│               ▼                  ║ 重试耗尽 → 抛异常         ║   │
│  ╔══════════════════════════╗    ║ 业务层可 catch 做容错    ║   │
│  ║ Step 7: 返回 Result     ║    ╚══════════════════════════╝   │
│  ║ get_data() → dict       ║                                    │
│  ║ get_text() → str        ║                                    │
│  ╚══════════════════════════╝                                    │
│                                                                  │
│       重试环路（max_retries 控制上限）：Step 6 不满足 → Step 1     │
└──────────────────────────────────────────────────────────────────┘
```

### 9.2 Step 1：Schema → Prompt Generator

将用 Python 字典定义的 Schema 转化为模型能理解的自然语言指令。

```
输入（你的代码）                     输出（发给模型的 Prompt）
─────────────────                   ──────────────────────────
schema = {                          
  "title": (str, "会议标题", True),   "请根据以下信息，按 JSON 格式输出：
  "time":  (str, "会议时间", True),    
}                                    {                              │
        │                            "title": "会议标题(string) 必填",
        │                            "time" : "会议时间(string) 必填"
        ▼                            }
                                     
  Prompt Generator:                  只输出 JSON，不要包含其他解释性文字。"
  遍历 Schema 字典
  → 提取字段名、类型、描述
  → 组装成字段说明文本
  → 包装成系统指令
```

你可以通过 `schema.get_prompt_text()` 在 DevTools 中查看生成的完整 Prompt。

### 9.3 Step 2：模型生成文本

将 Prompt 发送给 LLM，获取原始文本响应——与普通 Chat Completion 调用完全一致。

> **关键问题**：模型输出的不一定是干净的 JSON。它可能在前后插入礼貌用语，或用 Markdown 代码块包裹。这正是 Step 3 要解决的。

### 9.4 Step 3：Locator 状态机定位闭合 JSON（重点）

**这是七步机制中最关键、也最具技术深度的一步。**

#### 为什么不能用正则？

正则有两个致命缺陷：

```
问题 1：无法判断闭合性
───────────────────────
输入：'{ "a": 1 }, { "b": 2 }'
正则贪婪匹配可能：把两个对象当成一个，或只匹配第一个 } 就停止
→ 无法精确确定 JSON 对象的边界

问题 2：嵌套结构无能为力
─────────────────────────
输入：'{"a": {"b": [{"c": 1}]}}'
正则无法区分嵌套层级，. * 可能匹配到内层 } 就停，也可能贪婪越过所有 }
→ 无法确定哪一个 } 才是主对象的闭合
```

#### Locator 状态机的解决方案

Locator 使用**类状态机逐字符扫描**文本，维护深度计数器判断闭合性：

```
┌───────────────────────────────────────────────────────────────┐
│                 Locator 状态机算法                             │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  核心数据结构：                                                │
│    depth = 0          ← 大括号嵌套深度                         │
│    in_string = False  ← 当前是否在字符串内部                    │
│    escape = False     ← 上一个字符是否是转义符 \                │
│    start_pos = -1     ← 最外层 { 的起始位置                    │
│    end_pos = -1       ← 最外层 } 的结束位置                    │
│                                                               │
│  扫描逻辑：                                                    │
│    遇到 { 且 !in_string → depth++, 若 ==1 记录 start_pos       │
│    遇到 } 且 !in_string → depth--, 若 ==0 记录 end_pos → break │
│    遇到 " 且 !escape  → 切换 in_string 状态                    │
│    遇到 \ 且 in_string → escape=True（跳过下一字符）            │
│    在 in_string 内部 → { 和 } 不参与 depth 计数               │
│                                                               │
│  时间复杂度：O(n)  单遍扫描，每字符访问一次                      │
│  空间复杂度：O(1)  只需数个整型变量                              │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

**处理的关键边界情况：**

```
情况 1：JSON 前后有自然语言
  "好的，这是结果：{"a":1}"  →  扫描"好的..." depth=0 跳过
  { depth=1 start=7  } depth=0 end=12  →  定位到 {"a":1}

情况 2：嵌套 JSON
  '{"a":{"b":2}}'  →  { depth=1  { depth=2  } depth=1  } depth=0
  start=0  end=12  →  正确识别最外层

情况 3：字符串内部含 } 字符
  '{"text":"a } b"}'  →  { depth=1  "进入字符串  }不计数 "退出  } depth=0
  →  字符串内的 } 不被误判为结束

情况 4：Markdown 代码块包裹
  '```json\n{"a":1}\n```'  →  ` { } 字符不干扰，正确定位 {"a":1}

情况 5：多个 JSON 对象（取第一个）
  '{"a":1} {"b":2}'  →  depth 第一次回到 0 时 break，返回 {"a":1}
```

**Locator 的 Python 核心实现：**

```python
def locate_json(text: str):
    """状态机定位第一个合法闭合的 JSON 对象。O(n) 时间，O(1) 空间。"""
    depth = 0
    in_string = False
    escape = False
    start_pos = -1
    end_pos = -1

    for i, ch in enumerate(text):
        if escape:
            escape = False
            continue
        if ch == '\\' and in_string:
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == '{':
            depth += 1
            if depth == 1:
                start_pos = i
        elif ch == '}':
            depth -= 1
            if depth == 0 and start_pos != -1:
                end_pos = i
                break

    if start_pos != -1 and end_pos != -1:
        return text[start_pos:end_pos + 1], start_pos, end_pos
    return None, -1, -1
```

### 9.5 Step 4：JSON5 宽松解析

使用 **JSON5** 而非标准 JSON 解析器。这是重要设计决策——模型输出的 JSON 常有不标准的写法：

```
标准 JSON 拒绝：             JSON5 容忍：
─────────────────           ──────────
❌ 注释 // /* */              ✅ 注释
❌ 尾随逗号 {"a":1,}          ✅ 尾随逗号
❌ 单引号 {'a':'b'}           ✅ 单引号
❌ 无引号 key {a:1}           ✅ 无引号 key
❌ 十六进制 0xFF              ✅ 十六进制
❌ NaN / Infinity            ✅ NaN / Infinity
```

宽松解析大幅降低了因格式微小偏差导致的不必要重试。

```python
import json5
model_output = '{ "title": "Q2复盘", /* 注释 */ "time": "07-01", }'
data = json5.loads(model_output)  # ✅ 解析成功
```

### 9.6 Step 5：Pydantic 校验

框架根据 Schema 字典**自动生成 Pydantic BaseModel**，用 `model_validate()` 校验：

```
Schema 字典                    自动生成的 Pydantic Model
───────────                    ──────────────────────────
{                              class AutoSchema(BaseModel):
  "title": (str, "...", True),     title: str
  "time":  (str, "...", True),     time: str
  "duration": (int, "...", False), duration: int | None = None
}                                  model_config = {"extra": "ignore"}
                                  
校验内容：
  1. 字段名是否存在（多余字段忽略，extra="ignore"）
  2. 类型是否正确（尝试类型强制转换，失败则校验失败）
  3. 列表元素类型是否正确
  4. 枚举值是否在允许范围
```

### 9.7 Step 6：Ensure Keys 检查

Pydantic 校验通过后，进行**业务层面的确保检查**：

```
Step 5 vs Step 6 分工：

Step 5 Pydantic          Step 6 Ensure Keys
─────────────────        ────────────────────
关注「结构合法性」         关注「业务完整性」
类型对不对？字段多了？      业务必须的字段有没有出现？
类比：身份证读卡器          类比：安检检查违禁品
```

检查逻辑：遍历 `ensure_keys` 或所有 `ensure=True` 的字段 → 检查是否存在且类型正确 → **有缺失则包装错误信息，回 Step 1 重试**（不是直接抛异常）。

```
重试 Prompt 对比：

第一次：                               重试时：
"请根据以下信息输出 JSON..."            "请根据以下信息输出 JSON...
                                      
                                       ⚠️ 上一次输出存在以下问题：
                                       - 字段 "title" 缺失（必填）
                                       - 字段 "priority" 类型错误：
                                         期望 str，实际为 int
                                       
                                       请修正后重新输出完整 JSON。"
```

### 9.8 Step 7：返回 dict / 抛出异常

```
路径 A：全部通过 ✅                 路径 B：重试耗尽 ❌
────────────────────               ───────────────────
返回 Result 对象：                   抛出 SchemaValidationError：
  .get_data()  → dict                .message      → 错误描述
  .get_text()  → str                 .missing_fields → 缺失字段
  .retry_count → 重试次数            .retry_count  → 总重试次数
                                     .last_response → 最后输出

                                    业务层容错：
                                    try:
                                        result = schema.start(...)
                                    except SchemaValidationError as e:
                                        logger.error(f"失败: {e.message}")
                                        return fallback_response()  # 降级
```

### 9.9 每步可独立使用

七步机制每步都可独立调用，赋予极大的灵活性：

```
需要的功能                调用方式
────────────             ────────
只要 Prompt              prompt = schema.get_prompt_text()
（自己调 API）              → 返回完整 Prompt 字符串

只要 Locator             json_str, start, end = locate_json(raw_text)
（从文本提取 JSON）         → 返回定位到的 JSON

只要 JSON5 解析           data = json5.loads(json_str)
（解析非标准 JSON）         → 返回 dict

只要 Pydantic 校验        result = validate_with_schema(data_dict, schema_dict)
（校验已有 dict）           → 返回校验结果

只要 Ensure 检查          result = check_ensure_keys(data_dict, ["title","time"])
（检查 key 完整性）         → 返回缺失字段列表

跑完整链路               result = schema.start(info=text, ensure_all=True)
（标准用法）                → 走完七步，返回 Result
```

### 9.10 完整链路代码示例

```python
from agentic_schema import Schema, SchemaValidationError, locate_json
import json5

# ── 定义 Schema ──
schema = Schema({
    "sentiment":       (["正面", "负面", "中性"], "客户情感倾向", True),
    "category":        (str, "反馈类别", True),
    "severity":        (["高", "中", "低"], "问题严重程度", True),
    "summary":         (str, "反馈摘要，100字以内", True),
    "key_words":       [(str, "关键词")],
    "need_followup":   (bool, "是否需要跟进", True),
    "suggested_action": (str, "建议跟进措施", False),
    "sentiment_score": (int, "情感评分 1-10", False),
})

# ── 输入 ──
feedback = """
我在你们平台买了个手机壳，下单三天了还没发货！
找客服问了好几次，每次都说"正在处理中"。
要不是产品质量确实不错，我早就退款了。
"""

# ── 方式一：完整七步 ──
try:
    result = schema.start(info=feedback, ensure_all=True, max_retries=3)
    data = result.get_data()
    print(f"情感：{data['sentiment']} | 类别：{data['category']} | 重试：{result.retry_count}")
except SchemaValidationError as e:
    print(f"校验失败（重试{e.retry_count}次）：{e.missing_fields}")
    data = {"sentiment": "未知", "category": "未知"}  # 降级

# ── 方式二：分段独立使用 ──
# 只看 Prompt
prompt = schema.get_prompt_text()
print(f"Prompt 长度：{len(prompt)}")

# 只定位 JSON
dirty = '好的，这是结果：\n{"sentiment": "负面", "category": "物流"}'
clean, _, _ = locate_json(dirty)

# 只解析 + 校验
parsed = json5.loads(clean)
from agentic_schema import validate_schema_dict
check = validate_schema_dict(parsed, schema.schema_dict, ensure_keys=["sentiment", "category"])
print(f"校验结果：{check}")

# ── 方式三：链式调用 ──
result = (
    Schema({"topic": (str, "话题", True), "standpoint": (["支持","反对","中立"], "立场", True)})
    .set_info("我认为远程办公能提高工作效率")
    .start(ensure_all=True, max_retries=2)
)
print(f"{result.get_data()['topic']} — {result.get_data()['standpoint']}")
```

### 9.11 本章小结

```
┌─────────────────────────────────────────────────────────────────┐
│                     七步确保 速查卡片                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: Prompt Generator    Schema 字典 → 自然语言 Prompt       │
│  Step 2: 模型生成文本          Prompt → LLM → 原始文本            │
│  Step 3: Locator 状态机       原始文本 → 逐字符扫描 → 闭合 JSON   │
│  Step 4: JSON5 宽松解析        JSON 字符串 → dict                │
│  Step 5: Pydantic 校验         dict → model_validate → 类型检查  │
│  Step 6: Ensure Keys 检查      检查必确保字段 → 缺失则重试        │
│  Step 7: 返回 / 抛异常         全部通过→Result | 耗尽→异常        │
│                                                                 │
│  ⚠️ Step 3 Locator 核心：                                       │
│     • 状态机逐字符扫描，不用正则                                  │
│     • 深度计数器判断 {} 闭合性                                    │
│     • 字符串内括号不参与计数                                      │
│     • O(n) 时间，O(1) 空间                                       │
│                                                                 │
│  设计原则：                                                      │
│     • 每步可独立 —— 完整工具箱                                   │
│     • 出错重试不抛异常 —— 带错误上下文                           │
│     • max_retries 限流 —— 防止无限循环                           │
│     • JSON5 宽松 —— 降低不必要失败率                              │
│     • 业务层可容错 —— 不锁死                                     │
│                                                                 │
│  上一课：M08 Agentic Schema 语法详解                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

# 十~十二、单次请求边界、变量拼装与课程小结

> 基于陈泽鹏老师视频课程整理编写 · 2026年7月3日

---

## 目录

- [十、单次请求的适用边界——什么时候够用，什么时候不够](#十单次请求的适用边界什么时候够用什么时候不够)
  - [10.1 单次请求的能力清单](#101-单次请求的能力清单)
  - [10.2 单次请求不够用的四类场景](#102-单次请求不够用的四类场景)
  - [10.3 关键认知：运行框架 vs 模型](#103-关键认知运行框架-vs-模型)
  - [10.4 工程封装：从脚本到可维护项目](#104-工程封装从脚本到可维护项目)
  - [10.5 下节课预告：FastAPI 包装](#105-下节课预告fastapi-包装)
- [十一、从脚本到工程——变量拼装与配置外部化](#十一从脚本到工程变量拼装与配置外部化)
  - [11.1 链式调用与变量传入](#111-链式调用与变量传入)
  - [11.2 system / info / input 分块表达](#112-system--info--input-分块表达)
  - [11.3 支持的数据类型与边界](#113-支持的数据类型与边界)
  - [11.4 配置外部化：从硬编码到导入](#114-配置外部化从硬编码到导入)
  - [11.5 工厂模式创建 Agent](#115-工厂模式创建-agent)
  - [11.6 环境变量管理：dotenv 加载 API Key](#116-环境变量管理dotenv-加载-api-key)
- [十二、Q&A 答疑精选与课程小结](#十二qa-答疑精选与课程小结)
  - [12.1 Q&A 答疑精选](#121-qa-答疑精选)
  - [12.2 课程小结](#122-课程小结)
  - [12.3 下节课预告](#123-下节课预告)

---

## 十、单次请求的适用边界——什么时候够用，什么时候不够

在前面几章中，我们学会了如何构造 Schema、如何让模型按我们指定的结构输出。现在我们需要退一步，问一个更根本的问题：**一次模型调用，到底能解决什么级别的任务？什么时候够用，什么时候一定不够？**

这个问题之所以重要，是因为它直接决定了你在架构设计时选择什么粒度的工作单元。如果所有问题都能用单次请求解决，那 Agent 系统根本就不需要存在——一个简单的 API 封装就够了。但现实显然不是这样。理解单次请求的边界，就是理解 Agent 系统为什么必须存在的底层逻辑。

### 10.1 单次请求的能力清单

先明确"单次请求"的定义：**一次完整的模型调用，给定上下文，给定任务指令，等待模型返回最终结果，中间不中断、不交互、不查询外部系统。**

在满足以下三个条件时，单次请求完全够用：

```
+============================================================================+
|                    单次请求的适用条件                                        |
+============================================================================+
|                                                                            |
|  条件一：信息齐备                                                           |
|  ┌─────────────────────────────────────────────────────────────────────┐   |
|  │ 完成任务所需的所有信息，在请求发出前已经全部就绪。                      │   |
|  │ 模型不需要"先查一下再回来"，不需要在推理过程中发现"缺了什么"。          │   |
|  │ 示例：给一段代码做代码审查 → 代码已经在 prompt 里。                   │   |
|  └─────────────────────────────────────────────────────────────────────┘   |
|                                                                            |
|  条件二：不需要查询外部系统                                                 |
|  ┌─────────────────────────────────────────────────────────────────────┐   |
|  │ 模型不需要从数据库、API、文件系统、网络等外部来源获取任何信息。         │   |
|  │ 示例：将一段英文翻译成中文 → 不依赖外部数据。                          │   |
|  └─────────────────────────────────────────────────────────────────────┘   |
|                                                                            |
|  条件三：不需要根据中间结果重新决策                                         |
|  ┌─────────────────────────────────────────────────────────────────────┐   |
|  │ 任务路径在发出请求时已完全确定，不存在"先做完 A，看结果再决定          │   |
|  │ 是做 B 还是 C"的分支逻辑。                                            │   |
|  │ 示例：给一份简历打分并给出理由 → 逻辑路径是线性的。                    │   |
|  └─────────────────────────────────────────────────────────────────────┘   |
|                                                                            |
+============================================================================+
```

单次请求的核心公式可以归纳为：

```
给上下文 + 给任务 → 拿结果
```

注意这个公式里没有任何中间步骤——没有"先查一下"、没有"如果 A 则 B 否则 C"、没有"执行完这步再看看"。它是一条直线。模型拿到所有信息，一次推理，直接产出。

**典型的单次请求场景**：

| 场景 | 上下文 | 任务 | 输出 |
|------|--------|------|------|
| 文本分类 | 一段用户评论 | 判断情感正面/负面 | `"positive"` |
| 内容生成 | 产品描述文本 | 写一份营销文案 | 营销文案文本 |
| 代码审查 | 一段 Python 代码 | 指出潜在 bug | bug 列表 |
| 结构化提取 | 一份合同 PDF 文本 | 提取关键字段 | 结构化 JSON |
| 翻译 | 一段中文 | 翻译成英文 | 英文文本 |
| 摘要 | 一篇长文章 | 300 字摘要 | 摘要文本 |

在这些场景中，单次请求是最优解——简单、高效、没有不必要的复杂度。你不需要为了翻译一段文字而启动一个 Agent 循环。**能用单次请求解决的问题，就不要上 Agent。这是工程上的一条铁律。**

这条铁律的背后是一个更根本的原则：**复杂度是有成本的。** 每多一层抽象、每多一次工具调用、每多一轮循环，都在增加系统的延迟、出错概率和调试难度。在工程上，我们永远追求"刚好够用的复杂度"——不多不少。

### 10.2 单次请求不够用的四类场景

但现实世界中的很多任务，天然就无法用单次请求完成。以下四类场景，每一类都在挑战单次请求的边界，也每一类都在为 Agent 系统的存在提供理由。

#### 10.2.1 场景一：需要根据第一步结果决定第二步（ReAct Loop）

这是最经典也是最核心的场景。任务不是线性的——你需要先做第一步，看结果，然后决定第二步做什么；第二步的结果可能又决定了第三步。这种"推理-行动-观察-再推理"的循环，就是前面章节讲过的 **ReAct Loop**。

```
+============================================================================+
|                    ReAct Loop 场景示意                                       |
+============================================================================+
|                                                                            |
|  用户："帮我分析这份销售数据，找出业绩最差的三个区域，                        |
|        然后分析原因，给出改进建议。"                                          |
|                                                                            |
|  ┌─────────────────────────────────────────────────────────────────────┐   |
|  │ 模型无法在推理时才"看到"数据——它需要在推理过程中先拿到数据，            │   |
|  │ 分析数据后才知道"最差的三个区域"是谁，然后才知道要去分析什么原因。        │   |
|  │                                                                       │   |
|  │  Step 1: 查询销售数据 → Observation: 拿到 30 个区域的数据              │   |
|  │  Step 2: 排序找出最差 3 个 → Observation: A 区、B 区、C 区              │   |
|  │  Step 3: 针对这 3 个区域深入分析 → Observation: 原因分析结果            │   |
|  │  Step 4: 基于分析生成建议 → 最终回复用户                                │   |
|  │                                                                       │   |
|  │ 每一步都依赖上一步的结果，单次请求无法承载这种动态决策路径。             │   |
|  └─────────────────────────────────────────────────────────────────────┘   |
|                                                                            |
|  工程启示：Codex 和 Claude Code 之所以强大，正是因为他们内部实现             |
|  了一个完整的 ReAct Loop 框架——它们本质上不是"一次模型调用"，                |
|  而是"多次模型调用 + 中间状态管理"。                                        |
|                                                                            |
+============================================================================+
```

在代码层面，单次请求的实现只需要一行 `.run()`：

```python
# 单次请求：一次性给齐所有信息
agent = Agent(model="gpt-4")
result = agent.run("审查这段代码: " + code_snippet, schema=CodeReviewSchema)
# 返回的就是最终结果，中间不中断
```

但如果有 ReAct Loop 需求，情况就完全不同了——你需要一个能管理多轮状态、在每轮之后决定"是否继续"的运行框架。这正是 agentic 框架要解决的核心问题之一。

#### 10.2.2 场景二：需要查询实时数据（工具调用场景）

模型的知识截止于训练数据，它不知道"现在上海天气多少度"、不知道"张三今天有没有发飞书消息"、不知道"这笔订单当前状态是什么"。当任务需要这些实时信息时，单次请求就断链了。

```
+============================================================================+
|                    工具调用场景示意                                          |
+============================================================================+
|                                                                            |
|  用户："帮我查一下张三负责的项目，最新一期周报写了什么。"                     |
|                                                                            |
|  ┌─────────────────────────────────────────────────────────────────────┐   |
|  │ 这个任务需要三个外部查询步骤：                                          │   |
|  │                                                                       │   |
|  │  1. 查 CRM 系统 → 张三负责哪些项目？                                   │   |
|  │  2. 查文档系统 → 这些项目的最新周报文档链接？                           │   |
|  │  3. 查文档内容 → 拉取周报内容 → 总结回复用户                           │   |
|  │                                                                       │   |
|  │ 每一个查询都需要实际调用外部 API。"把 CRM 数据塞进 prompt"不现实：      │   |
|  │ 你不知道张三负责哪些项目，所以你不知道该塞什么数据。                     │   |
|  │ 你需要工具——模型输出"我要查 CRM"，系统执行查询，结果返回模型，          │   |
|  │ 模型再决定下一步。这就是 Function Calling 的典型应用场景。              │   |
|  └─────────────────────────────────────────────────────────────────────┘   |
|                                                                            |
+============================================================================+
```

工具调用（Function Calling / Tool Use）让模型从"全知全能的推理引擎"变成了"会使用工具的推理引擎"。它不需要自己知道一切，它只需要知道"遇到这个问题时，该用什么工具去查"。

#### 10.2.3 场景三：需要执行代码或操作文件（沙盒场景）

有时候模型不仅要"知道"答案，还要"做出"点什么——执行一段 SQL、运行一个 Python 脚本、修改一个配置文件、提交一个表单。模型本身只是一个推理引擎，它不能直接执行代码。

```
+============================================================================+
|                    沙盒执行场景示意                                          |
+============================================================================+
|                                                                            |
|  用户："帮我统计这个 CSV 文件中 sales 列的总和。"                            |
|                                                                            |
|  ┌─────────────────────────────────────────────────────────────────────┐   |
|  │ 模型可以"推理"出算法逻辑：                                             │   |
|  │  "用 pandas 读 CSV，取 sales 列，调 .sum() 即可"                      │   |
|  │                                                                       │   |
|  │ 但它不能真的执行这段代码——模型没有 Python 运行时。                     │   |
|  │                                                                       │   |
|  │ 你需要一个"沙盒"（Sandbox）：                                          │   |
|  │  1. 模型生成代码                                                      │   |
|  │  2. 系统在沙盒中执行代码                                               │   |
|  │  3. 执行结果返回给模型                                                 │   |
|  │  4. 模型基于结果给出最终回复                                            │   |
|  │                                                                       │   |
|  │ 这就是 Claude Code / Codex 的核心工作模式——它们给模型配备了一个         │   |
|  │ 代码执行环境，模型可以"写代码并运行"，然后根据运行结果继续工作。         │   |
|  └─────────────────────────────────────────────────────────────────────┘   |
|                                                                            |
+============================================================================+
```

沙盒场景的本质是：模型需要**产生副作用**——修改文件系统、操作数据库、执行计算。这些"副作用"都需要一个外部的执行环境来完成。单次请求只能产生文本输出，不能产生副作用。

#### 10.2.4 场景四：需要跨多对话记住上文（状态管理场景）

这一点比较容易被忽略。假设你做了一个"旅行规划助手"：

- 第一次对话：你告诉它"我下个月去东京，预算 2 万，喜欢人文景点"
- 第二次对话（三天后）：你说"帮我把上次那个规划里的浅草寺换成明治神宫"

第二次对话时，模型怎么知道"上次那个规划"是什么？单次请求是无状态的——每次调用都是独立的世界。要解决这个问题，你需要一个**状态管理层**。

```
+============================================================================+
|                    状态管理场景示意                                          |
+============================================================================+
|                                                                            |
|  对话一（Day 1）：                                                          |
|  User:  "我下个月去东京，预算 2 万，喜欢人文，帮我规划行程"                  |
|  Agent: [生成了一份包含浅草寺、国立博物馆等景点的行程]                       |
|                                                                            |
|  对话二（Day 3）：                                                          |
|  User:  "把上次规划里的浅草寺换成明治神宫"                                  |
|                                                                            |
|  ┌─────────────────────────────────────────────────────────────────────┐   |
|  │ 新的一次模型调用，默认情况下不记得"上次规划"是什么。                     │   |
|  │ 你需要一个外部机制来解决"跨对话记忆"：                                  │   |
|  │                                                                       │   |
|  │  a) 会话回放：把上次对话的完整上下文重新灌入                            │   |
|  │  b) 记忆提取：把关键信息提取存到数据库                                  │   |
|  │  c) 会话管理：每次请求带 session_id，后端根据 ID 取历史                 │   |
|  └─────────────────────────────────────────────────────────────────────┘   |
|                                                                            |
+============================================================================+
```

这四类场景——ReAct 循环、工具调用、沙盒执行、状态管理——共同构成了 Agent 系统必须解决的核心问题域。它们不是互斥的，一个真实的生产级任务往往同时涉及其中多个。

### 10.3 关键认知：运行框架 vs 模型

在讨论完单次请求的边界之后，有一个关键认知必须建立：**Codex / Claude Code 不是模型，它们是运行框架。**

```
+============================================================================+
|                    模型 vs 运行框架                                          |
+============================================================================+
|                                                                            |
|  ┌─────────────────────────────────┐  ┌─────────────────────────────────┐  |
|  │           模型（Model）          │  │       运行框架（Runtime）         │  |
|  ├─────────────────────────────────┤  ├─────────────────────────────────┤  |
|  │  • 文本生成引擎                  │  │  • 包裹模型的"操作系统"          │  |
|  │  • 推理与语言能力                │  │  • 管理多轮对话状态              │  |
|  │  • 纯输入 → 输出                 │  │  • 调度工具调用                  │  |
|  │  • 无状态                        │  │  • 提供代码执行沙盒              │  |
|  │  • 不能执行代码                  │  │  • 管理文件和外部连接            │  |
|  │  • 不能查外部系统                │  │  • 处理用户交互                  │  |
|  │                                 │  │                                 │  |
|  │  代表：GPT-4, Claude, Gemini    │  │  代表：Codex, Claude Code,      │  |
|  │                                 │  │         OpenClaw, agentic        │  |
|  └─────────────────────────────────┘  └─────────────────────────────────┘  |
|                                                                            |
|  核心关系：                                                                 |
|  ┌─────────────────────────────────────────────────────────────────────┐   |
|  │   运行框架 = 模型 + 循环管理 + 工具调度 + 沙盒 + 状态 + 交互层         │   |
|  │   我们整个课程在做的事情 = 构建自己的运行框架                           │   |
|  └─────────────────────────────────────────────────────────────────────┘   |
|                                                                            |
+============================================================================+
```

这个认知为什么重要？因为它直接回答了"我们为什么要学 agentic，而不是直接用 Claude Code 就好"这个问题。**Claude Code 是别人的运行框架，agentic 是你自己的运行框架。** 当你理解了运行框架的底层原理，你就可以按自己的需求定制编排逻辑、接入任何模型、控制数据的流向和存储、嵌入自己的业务系统——而不是被某个产品的编排方式束缚。

你来 agentic 框架的角色，就是把 Schema 定义、结构化输出约束、消费概念、Skills vs Tool 这些"零件"有机地组装在一起，提供一套干净、可扩展的编排基础设施。

### 10.4 工程封装：从脚本到可维护项目

到目前为止，我们的代码可能还比较"脚本化"——一个文件里塞了模型配置、Schema 定义、业务逻辑。这在快速验证阶段可以接受，但随着功能增多会迅速失控。

#### 10.4.1 封装为类

把"创建 Agent → 定义 Schema → 执行任务 → 解析结果"收拢到一个类中：

```python
# agent_runner.py
from agentic import Agent
from pydantic import BaseModel
from typing import Optional

class DocumentAnalyzer:
    """文档分析 Agent 的封装类"""
    def __init__(self, model: str = "gpt-4", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key
        self._agent = None

    @property
    def agent(self):
        if self._agent is None:
            self._agent = Agent(model=self.model, api_key=self.api_key)
        return self._agent

    def analyze(self, document: str) -> dict:
        return self.agent.run(
            prompt=f"请分析以下文档内容：\n{document}",
            schema=AnalysisResult
        )

class AnalysisResult(BaseModel):
    summary: str
    keywords: list[str]
    sentiment: str
    confidence: float
```

调用方只需要 `analyzer.analyze(doc)` 这一行，内部细节完全隐藏。后续加日志、缓存、重试逻辑，改这一个类就行。

#### 10.4.2 配置外部化

把模型名称、API 地址、超时时间从代码中抽离：

```python
# config/models.py
import os
from dotenv import load_dotenv
load_dotenv()

MODEL_CONFIG = {
    "gpt4": {
        "model": "gpt-4",
        "api_key_env": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com/v1",
        "timeout": 60,
    },
    "qwen_local": {
        "model": "qwen2.5:7b",
        "api_key_env": "OLLAMA_KEY",
        "base_url": "http://localhost:11434/v1",
        "timeout": 120,
    },
    "deepseek": {
        "model": "deepseek-chat",
        "api_key_env": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com/v1",
    }
}
```

切换模型只需改一行 key：`config = MODEL_CONFIG["qwen_local"]`，业务代码不动。

配置外部化的意义不仅仅是"整洁"：**可扩展成配置界面**（字典结构直接序列化成前端 JSON，实现可视化模型切换，这是前后台逻辑分离的基础）；**可做版本管理**（配置变更走 Git）；**可做环境隔离**（开发用 Qwen、测试用 DeepSeek、生产用 GPT-4）。

#### 10.4.3 目录结构分离

按职责把文件分开，推荐的工程目录结构：

```
my_agent_project/
├── config/               # 模型配置、全局设置
│   ├── __init__.py
│   ├── models.py
│   └── settings.py
├── schemas/              # Schema 定义（输出长什么样）
│   ├── __init__.py
│   ├── code_review.py
│   └── doc_analysis.py
├── agents/               # Agent 封装（谁来执行）
│   ├── __init__.py
│   ├── base.py           # 基类/工厂方法
│   ├── code_reviewer.py
│   └── doc_analyzer.py
├── bridges/              # 外部系统桥接层（数据库、API）
│   ├── __init__.py
│   ├── db.py
│   └── api.py
├── business/             # 业务逻辑编排
│   ├── __init__.py
│   └── workflows.py
├── main.py               # 入口
├── .env                  # 环境变量（不提交 Git）
├── .env.example          # 模板（可提交 Git）
└── requirements.txt
```

关注点分离：config 管"用什么模型"、schemas 管"输出长什么样"、agents 管"谁来执行"、bridges 管"怎么连外部"、business 管"业务怎么编排"。每一层只关心自己的事。

### 10.5 下节课预告：FastAPI 包装

封装成类、配置外部化、目录分离——做完后代码是可维护的工程了，但还是命令行里的东西。下节课用 **FastAPI** 包装成 HTTP 服务，让它变成内网可访问的服务，可以被前端页面、飞书机器人、定时任务甚至是其他微服务调用。

```
脚本阶段          →    工程阶段          →    服务阶段
一个 .py 文件          封装+配置分离       FastAPI HTTP 包装
python demo.py        python main.py     http://localhost:8000/api
```

---

### 本节小结

1. **能用单次请求解决的问题就不要上 Agent**——复杂度有成本，永远追求"刚好够用的复杂度"。
2. **四类不够用的场景**——ReAct 循环决策、工具调用实时数据、沙盒执行代码/文件、跨对话状态管理——共同构成了 Agent 系统存在的底层逻辑。
3. **Codex / Claude Code 是运行框架，不是模型**——我们整个课程的目标是 build 自己的运行框架。从脚本到工程（封装类→配置外部化→目录分离），再到服务（FastAPI 包装），是落地的必然路径。

---

## 十一、从脚本到工程——变量拼装与配置外部化

上节讨论了单次请求的边界和工程封装的大方向。本节深入最关键的技术细节：**变量拼装**——也就是如何把动态数据注入 prompt，以及背后的设计哲学。

这个看似简单的问题，如果处理不好，会导致大量字符串拼接、难以测试的硬编码和混乱的职责划分。agentic 框架的设计者在这个问题上做了一个非常干净的取舍——理解这个取舍，你就能理解整个框架的数据流设计哲学。

### 11.1 链式调用与变量传入

在 agentic 中，构造一个请求不是通过一个巨大的参数字典，而是通过**链式调用**逐步注入不同层次的信息：

```python
from agentic import Agent

agent = Agent(model="gpt-4")

result = (
    agent
    .system("你是一名代码审查专家，擅长发现 Python 代码中的潜在问题。")
    .info({"doc": doc_content})       # 注入文档内容
    .input(task_str)                   # 注入任务指令
    .run(schema=CodeReviewSchema)      # 指定输出结构并执行
)
```

每一行链式调用的含义：

| 方法 | 作用 | 变量传入 | 典型内容 |
|------|------|----------|----------|
| `.system()` | 设定行为角色和约束 | 通常不需要 | "你是一名代码审查专家" |
| `.info()` | 注入任务所需的外部数据 | 动态数据主入口 | `{"doc": doc_content, "ctx": context}` |
| `.input()` | 注入用户的具体任务指令 | 每次请求不同 | `"请审查以下代码: " + code` |
| `.run()` | 指定输出结构并触发执行 | schema 参数 | `schema=MySchema` |

变量传入的核心方式是 `.info()` 和 `.input()`。它们接受 Python 中的任何可序列化数据，agentic 框架在内部负责正确拼装到模型上下文中。

### 11.2 system / info / input 分块表达

为什么要分成三个入口，而不是一个"大 prompt"参数？设计哲学是**各司其职**——不同性质的信息放在不同槽位，框架可以有针对性地处理。

```
+============================================================================+
|                    system / info / input 三元结构                            |
+============================================================================+
|                                                                            |
|  system（系统提示）：角色定义、行为约束、输出格式要求                         |
|  ├── 变化频率：低——一个 Agent 的系统提示通常在整个生命周期中不变             |
|  ├── 设计意图：影响模型行为"基调"，应该稳定可复用                            |
|  └── 框架优化：可做缓存优化、prompt 版本管理                                 |
|                                                                            |
|  info（上下文信息）：外部数据、参考文档、背景知识                             |
|  ├── 变化频率：高——每次请求的数据不同                                       |
|  ├── 设计意图："数据层"，承载事实信息                                        |
|  └── 框架优化：可做内容压缩、RAG 检索增强                                    |
|                                                                            |
|  input（用户指令）：具体任务、问题、指令                                      |
|  ├── 变化频率：最高——每次用户请求都不同                                      |
|  ├── 设计意图："意图层"，承载用户想要什么                                    |
|  └── 框架优化：可做任务路由、意图识别                                        |
|                                                                            |
|  如果只有一个"大 prompt"参数：                                               |
|  prompt = "你是XXX。数据:" + data + "。任务:" + task                         |
|  → 框架无法区分角色/数据/任务，所有后续优化都无法针对性地工作。               |
|                                                                            |
+============================================================================+
```

这种分块设计，和前面讲的 Schema 三元组（描述/类型/约束）一脉相承：**清晰的边界带来清晰的工程处理能力。** 混在一起时什么都难做；分开了，每一块都可以独立优化。

### 11.3 支持的数据类型与边界

一句话：**任何可 JSON 序列化的 Python 数据结构都可以传。**

```
✅ 可以传：dict、list、str、int、float、bool、None、嵌套结构（dict/list 互相嵌套）
❌ 不能传：函数/方法、类对象、文件句柄、数据库连接、循环引用结构

核心原则：能变成 JSON 的就能传。模型最终拿到的是文本化 JSON，
传进去的东西必须能无损变成文本。
```

这个约束有一个重要工程含义：**你不能把"能力"传给模型，只能把"数据"传给模型。** 如果模型需要用到某个自定义计算公式，你不能传函数本身，而是把函数的逻辑用文字描述出来，让模型理解后自己实现。

### 11.4 配置外部化：从硬编码到导入

配置外部化的完整演进路径：

**阶段一：硬编码（快速验证期）**
```python
agent = Agent(model="gpt-4", api_key="sk-xxxxxxxxxxxx")
```
问题：API Key 暴露在代码里（提交 Git 即安全事故），换模型要改代码。

**阶段二：环境变量（基础工程化）**
```python
import os
from dotenv import load_dotenv
load_dotenv()
agent = Agent(model=os.getenv("AGENT_MODEL", "gpt-4"), api_key=os.getenv("OPENAI_API_KEY"))
```
问题：多 Agent 多模型时，switch 逻辑散落在代码里。

**阶段三：配置模块导入（推荐方案）**
```python
from config.models import MODEL_CONFIG
import os

config = MODEL_CONFIG["gpt4"]  # 只改这个 key
agent = Agent(
    model=config["model"],
    api_key=os.getenv(config["api_key_env"]),
    base_url=config.get("base_url")
)
```

配置外部化的三大价值：
1. **可扩展成配置界面**：MODEL_CONFIG 字典可直接序列化给前端，实现可视化模型切换——前后台逻辑分离
2. **可做版本管理**：谁在什么时候把 gpt-4 改成了 gpt-4-turbo，Git 记录清清楚楚
3. **可做环境隔离**：开发用本地 Qwen、测试用 DeepSeek、生产用 GPT-4——同一代码库，不同配置

### 11.5 工厂模式创建 Agent

当系统中有多种 Agent（代码审查、文档分析、客服、翻译），每种需要不同模型和 system 提示——直接用 `Agent(...)` 构造的代码会散落得到处都是。工厂模式统一创建：

```python
# agents/factory.py
from agentic import Agent
from config.models import MODEL_CONFIG
from config.settings import get_api_key

class AgentFactory:
    """Agent 工厂：集中管理所有 Agent 的创建逻辑"""

    @classmethod
    def create(cls, agent_type: str, model_key=None) -> Agent:
        mk = model_key or cls._default_model_for(agent_type)
        cfg = MODEL_CONFIG[mk]
        agent = Agent(
            model=cfg["model"],
            api_key=get_api_key(cfg["api_key_env"]),
            base_url=cfg.get("base_url")
        )
        agent.system(cls._system_prompt_for(agent_type))
        return agent

    @classmethod
    def _default_model_for(cls, agent_type: str) -> str:
        return {
            "code_reviewer": "gpt4",
            "doc_analyzer": "gpt4",
            "translator": "qwen_local",  # 翻译本地模型足够
        }.get(agent_type, "gpt4")

    @classmethod
    def _system_prompt_for(cls, agent_type: str) -> str:
        return {
            "code_reviewer": "你是一名代码审查专家...",
            "doc_analyzer": "你是一名文档分析专家...",
            "translator": "你是一名专业翻译...",
        }.get(agent_type, "")

# 使用方：一行代码
reviewer = AgentFactory.create("code_reviewer")
analyzer = AgentFactory.create("doc_analyzer", model_key="deepseek")
```

工厂模式的好处：创建逻辑集中（改模型和 system 提示只改一处）、类型安全（通过 agent_type 枚举避免拼写错误）、可扩展（加新类型只需加一个 case）。

### 11.6 环境变量管理：dotenv 加载 API Key

环境变量是管理敏感信息的标准方式。Python 中用 `python-dotenv`：

```
# .env 文件（不提交到 Git）
OPENAI_API_KEY=sk-your-real-api-key-here
DEEPSEEK_API_KEY=sk-your-deepseek-key
OLLAMA_KEY=ollama

# .env.example 文件（可提交 Git，作为模板）
OPENAI_API_KEY=your-openai-api-key-here
DEEPSEEK_API_KEY=your-deepseek-api-key-here
```

```python
# config/settings.py
import os
from dotenv import load_dotenv
load_dotenv()

def get_api_key(env_var_name: str) -> str:
    key = os.getenv(env_var_name)
    if not key:
        raise ValueError(
            f"环境变量 {env_var_name} 未设置。"
            f"请检查 .env 文件是否存在于项目根目录。"
        )
    return key
```

三个重要工程习惯：
1. **`.env` 必须加 `.gitignore`**——API Key 泄露到公开仓库可能几分钟内就被自动化扫描脚本检测到并滥用
2. **提供 `.env.example` 模板**——新加入的开发者直接复制改名填真实值即可
3. **生产环境不要依赖 `.env` 文件**——应该通过 K8s Secrets 或 Docker 环境变量注入密钥

---

### 本节小结

```
+============================================================================+
|                    变量拼装与工程化扩展全景                                   |
+============================================================================+
|  链式调用                    配置外部化                   环境管理            |
|  system() — 角色定义         config/ — 模型配置           .env — API Keys    |
|  info()   — 数据注入         schemas/ — 输出结构          .env.example      |
|  input()  — 任务指令         agents/  — 工厂模式          .gitignore        |
|  run()    — 执行             bridges/ — 外部连接                              |
|                                                                             |
|  核心原则：                                                                 |
|  • system/info/input 各司其职——清晰边界带来清晰工程处理能力                   |
|  • 能 JSON 序列化的就能传——不能传函数/对象                                   |
|  • 配置集中管理——工厂模式统一创建 Agent                                      |
|  • 密钥不进代码——dotenv + .gitignore                                        |
+============================================================================+
```

---

## 十二、Q&A 答疑精选与课程小结

这是本节课程的最后一章。先回答课程直播和讨论群中高频出现的七个关键问题，然后系统性回顾串联整体内容，最后预告下节课方向。

### 12.1 Q&A 答疑精选

#### 12.1.1 输入是否也需要 schema 约束？

> "输出有 Schema 约束了，输入需不需要也定义一个结构？"

**回答：不需要在框架层面做输入 schema 约束。输入校验是业务逻辑层的事，用 Pydantic BaseModel 即可。**

原因：输出结构不可控（模型是黑盒），所以需要框架层"强行约束"——Schema 三元组和 7 步确保机制意义在此。输入结构在传给模型之前完全在你代码控制之下，用 Pydantic 做一次校验即可：

```python
from pydantic import BaseModel, ValidationError

class DocumentInput(BaseModel):
    title: str
    content: str
    author: str
    tags: list[str] = []

try:
    doc = DocumentInput(title=t, content=c, author=a, tags=tags)
    agent.info(doc.model_dump())  # 校验通过后再传入
except ValidationError as e:
    print(f"输入数据格式错误: {e}")
```

框架的边界很清楚：**帮你约束输出的结构，输入数据的校验交给开发者自己。**

#### 12.1.2 agentic 框架与其他框架的对比？

> "agentic 和 LangChain、AutoGPT、CrewAI 有什么区别？"

**回答：agentic 的定位是底层编排工具，不是"全家桶"。**

| 框架 | 定位 | 关键特点 | 与 agentic 关系 |
|------|------|----------|----------------|
| agentic | 底层编排引擎 | 全异步、信号驱动编排、极小体积 | -- |
| LangChain | 应用框架全家桶 | Chains、RAG、Memory，同步为主 | 可被 agentic 编排驱动 |
| AutoGPT | 自主 Agent | 全自动任务拆解与执行 | 理念同源 |
| CrewAI | 多 Agent 协作 | 角色扮演、任务分配 | 互补关系 |
| Dify/扣子 | 低代码平台 | 拖拽式工作流 | 不同赛道 |

agentic 的关键区别：
1. **全异步**（async/await）——天然支持高并发，不阻塞事件循环
2. **信号驱动编排**（下节课详讲）——不是固定的 ReAct Loop，而是通过事件信号（完成/错误/超时/状态变更）灵活调度
3. **极小体积**——纯脚本逻辑，不绑定数据库、不强制存储方案
4. **可嵌入性**——可以作为其他框架的底层引擎

特别注意：**auto_gen 的 group chat / meeting loop 本质上也是 ReAct 变体**——多个 Agent 轮流发言，每个根据前一个的发言决定自己的发言。同样是"需要根据中间结果决定下一步"。理解了这个本质，就不会被各种框架的新名词迷惑。

#### 12.1.3 框架有多大？

> "agentic 体量大吗？依赖多不多？"

**回答：很小。纯脚本逻辑，存储通过外部插件。** 不自带数据库、消息队列、向量存储——全部由开发者自行选择。只做一件事：编排模型调用。依赖极少，安装快，启动快。

#### 12.1.4 文档在哪？

> "官方文档地址是什么？"

**回答：agentic.cn/docs**。API 参考、Schema 说明、配置项详解、示例代码都在上面。

#### 12.1.5 Schema 确保机制是怎样的？

> "Schema 里填 True 之后，框架内部做了什么？"

**回答：填 `True` 等于告诉框架"这个字段你需要帮我保证"。**

框架执行流程：

```
模型输出 → 解析 JSON → Schema 校验（字段存在性 + 类型一致性 + 约束满足性）
    │
    ├── 校验通过 → 返回结果
    │
    └── 校验失败 → 构造错误提示（哪个字段、预期类型、实际值）
                     → 重新请求模型（注入错误信息帮助修正）
                     → 默认最多 3 次重试
                     → 仍失败则抛出异常，由上层业务代码处理
```

**填 True vs 不填 True 的区别**：

| | 不填 True | 填 True |
|---|---|---|
| 字段缺失 | 视为可选，不报错 | 框架重试，直至模型补全 |
| 类型错误 | 不强制转换 | 框架重试，要求正确类型 |
| 适用场景 | 辅助字段，可有可无 | 核心业务字段，必须正确 |

本质：把结构约束从 prompt 的自然语言层面提升为框架的程序化保障——让程序而不是提示词来保证输出质量。

#### 12.1.6 AUTO GPT 的历史地位？

> "AUTO GPT 在 Agent 发展史中是什么地位？"

**回答：AUTO GPT 是 ReAct Loop / Function Calling 的真正鼻祖。**

时间线：
- **2023 年 4 月**：AUTO GPT 发布，用"土办法"实现 Function Calling——让模型输出特定 JSON 格式，程序解析 JSON、执行函数、结果拼回 prompt、模型继续。这就是 ReAct Loop + 工具调用的原型。
- **2023 年 6 月**：OpenAI 发布 Agent 相关论文，系统讨论 Agent 设计模式。
- **2023 年下半年**：OpenAI 在 API 中原生支持 Function Calling——模型直接输出标准 function call 结构。

AUTO GPT 不是最早的 Agent 概念，但它是第一个把"ReAct Loop + 自动化工具调用"推向大众视野的项目。它证明了"让模型自己决定用什么工具、分几步完成"是可行的——整个现代 Agent 系统的认知基础都源于此。我们今天讨论 agentic、LangChain、CrewAI，底层逻辑都可以追溯到 AUTO GPT 在 2023 年 4 月展示的那个基本模式。

#### 12.1.7 agentic vs LangChain 定位对比？

> "能具体说说两者在使用场景上有什么不同？"

**回答：LangChain 是应用框架，agentic 是编排引擎。**

**LangChain**——"给你一套完整积木，快速搭出能用的 Agent 应用"。组件丰富（RAG、Memory、Chains、Agents）、文档齐全、社区大。限制：抽象层多、调试困难、同步调用为主、深度定制时"黑盒"感强。适合快速原型和标准场景。

**agentic**——"给你一个干净的执行引擎，你想怎么编排就怎么编排"。全异步、信号驱动、轻量可嵌入、执行流透明可控。限制：不自带 RAG/Memory 等高层组件。适合需要精细编排、高并发、深度定制的生产级系统。

**它们不是竞争关系，可以组合使用**：agentic（编排引擎）+ LangChain Tools（工具库）+ 自建 Memory 系统 = 高度可控的生产级系统。用 agentic 的异步编排能力调度 LangChain 的成熟工具链，配上自己的状态管理和记忆方案。

### 12.2 课程小结

#### 12.2.1 核心知识图谱

```
+============================================================================+
|                       本阶段课程 核心知识图谱                                 |
+============================================================================+
|                                                                             |
|   为什么需要结构化输出？                                                      |
|   ├── 模型是不可完全可预测的计算单元                                          |
|   ├── 软件工程需要可预测的结构                                                |
|   └── 下游消费者期望固定格式                                                  |
|                │                                                             |
|                v                                                             |
|   结构化输出 5 个层次：                                                       |
|   L1 纯自然语言 → L2 Markdown 约定 → L3 JSON 字符串                          |
|                → L4 JSON+Schema 校验 → L5 7步确保机制                        |
|                │                                                             |
|                v                                                             |
|   Schema 三元组：描述（面向模型）+ 类型（面向程序）+ 约束（面向系统）           |
|                │                                                             |
|                v                                                             |
|   单次请求适用边界 → 不够用 → 多次请求 → Agent 编排管理                        |
|                                                                             |
+============================================================================+
```

#### 12.2.2 五层结构化输出回顾

| 层次 | 名称 | 机制 | 可靠性 | 适用场景 |
|------|------|------|--------|----------|
| L1 | 纯自然语言 | 无结构约束 | 不可靠 | 闲聊、创意写作 |
| L2 | Markdown 约定 | prompt 中约定格式 | 低 | 简单格式化输出 |
| L3 | JSON 字符串 | 要求模型输出 JSON | 中 | 需要程序解析的场景 |
| L4 | JSON+Schema | 解析后代码校验 | 高 | 需要可靠结构化的场景 |
| L5 | 7步确保机制 | 框架自动校验+重试 | 极高 | 生产级、核心业务 |

五个层次代表可靠性与复杂度的递增。不是"越高越好"，选择取决于业务对可靠性的要求。写诗用 L1，处理财务数据必须用 L5。

#### 12.2.3 七步确保机制回顾

**定义 Schema → 注入 prompt → 模型生成 → 解析 → 校验 → 修复（重试）→ 返回或报错**

防御式编程闭环：不是"相信模型会输出正确"，而是"假设模型可能出错，用程序兜底"。

#### 12.2.4 Schema 三元组回顾

```
字段 = 描述（description）+ 类型（type）+ 约束（constraints）

示例：
"score": {
    "description": "评分，0 到 100 之间的整数",
    "type": int,
    "constraints": (True, lambda x: 0 <= x <= 100)
}
```

三个要素对应三个角色：描述告诉模型"这是什么"、类型告诉程序"应该是什么"、约束告诉系统"怎样才合格"。三者分离，各自独立优化。

#### 12.2.5 一句话总结

> **可控的结构化输出是所有模型工程化的基石。**

没有结构化输出，模型就是一个"能说会道的黑盒"——它说的可能是对的，也可能是在胡说八道。有了结构化输出，你才能把模型的推理能力变成系统可消费的数据，嵌入更大的工程体系。从 L1 到 L5，从三元组到 7 步机制，从单次请求边界到 Agent 编排——所有内容指向一个目标：**让不可完全可预测的模型输出，变得在工程上可靠可用。**

### 12.3 下节课预告

下节课完成从"单次请求"到"多次请求"的跨越——Agent 系统的质变点：

1. **编排管理工具**：任务注册、状态追踪、结果回调、超时处理——管理一组并发的 Agent 任务，让一个任务的结果触发另一个任务的启动
2. **信号驱动编排（Signal-Driven Orchestration）**：agentic 区别于其他框架的核心特性。不是固定"步骤 1→2→3"，而是"当 A 完成触发 B，B 出错触发 C，超时触发 D"。事件信号替代硬编码执行路径，让系统在不确定的模型行为面前展现出极强的弹性和适应能力
3. **FastAPI 包装成 HTTP 服务**：Agent 工程脱离命令行，变成内网可达的 REST API——从前端到飞书机器人，从定时任务到 CI/CD 流水线，任何能发 HTTP 请求的系统都能调用

```
单次请求  ──────────────────────────>  多次请求
agent.run(...)                     signal.on("task_done", next_step)
一次调用，一次结果                  事件驱动，动态链路
确定性路径                          自适应路径
```

---

## 全章小结

| 章节 | 核心问题 | 核心答案 |
|------|----------|----------|
| 十、单次请求边界 | 什么时候够用，什么时候不够？ | 信息齐备+不查外部+不需中间决策 → 单次请求。反之一律需要 Agent。 |
| 十一、变量拼装与工程化 | 怎么从脚本变成工程？ | 链式调用分块注入 → 配置外部化 → 工厂模式 → dotenv 管理密钥 |
| 十二、Q&A 与小结 | 学完了然后呢？ | 结构化输出是基石，编排管理是下一站——从单次到多次的跨越 |

> **如果你只记住一件事：可控的结构化输出，是所有模型工程化的基石。有了它，你才能把"黑盒推理"变成"系统组件"。而 agentic 框架，就是在帮你把这块基石之上的整个大厦搭起来。**
