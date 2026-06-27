# LangChain 环境搭建与首次接入大语言模型（通义）

> 基于陈泽鹏老师视频课程整理编写 · 2026年6月

---

## 目录

- [一、课程背景与目标](#一课程背景与目标)
- [二、什么是 LangChain](#二什么是-langchain)
- [三、为什么需要 API Key——理解大语言模型的服务模式](#三为什么需要-api-key理解大语言模型的服务模式)
- [四、开发环境准备](#四开发环境准备)
- [五、虚拟环境详解](#五虚拟环境详解)
- [六、安装 LangChain 及依赖包](#六安装-langchain-及依赖包)
- [七、获取通义 API Key](#七获取通义-api-key)
- [八、编写第一个 LangChain 应用](#八编写第一个-langchain-应用)
- [九、运行与调试](#九运行与调试)
- [十、理解模型的响应时间](#十理解模型的响应时间)
- [十一、完整流程回顾](#十一完整流程回顾)
- [十二、常见问题与排错指南](#十二常见问题与排错指南)
- [十三、课后练习](#十三课后练习)
- [十四、课程小结](#十四课程小结)

---

## 一、课程背景与目标

### 1.1 本课定位

这是 LangChain 系列课程的**第一课**，从零开始，搭建环境，完成首个大语言模型应用的开发。

> 在网上有很多大语言模型可供选择。本节课我们以**通义（Tongyi）**为例，演示 LangChain 的环境搭建以及接入大语言模型的完整流程。

### 1.2 本节课要掌握的两个核心目标

```
┌─────────────────────────────────────────────┐
│                                             │
│   目标一：了解如何配置 LangChain 开发环境       │
│          ├── 创建虚拟环境                     │
│          ├── 安装 LangChain 及依赖包           │
│          └── 理解各包之间的关系                │
│                                             │
│   目标二：掌握接入大语言模型的流程              │
│          ├── 获取 API Key                    │
│          ├── 导入模型类                       │
│          ├── 创建模型实例                     │
│          ├── 调用模型获取回复                  │
│          └── 理解整个调用链路                  │
│                                             │
└─────────────────────────────────────────────┘
```

### 1.3 学完本课你能做什么

```
用户提问："夏天适合吃什么水果？"
                ↓
    你的 Python 代码（LangChain 封装）
                ↓
           通义大模型处理
                ↓
    返回结果："西瓜、桃子、哈密瓜、葡萄..."
```

**从零到成功调用，全程在本课中完成。**

---

## 二、什么是 LangChain

### 2.1 一句话理解

> **LangChain 是一个用于构建大语言模型（LLM）应用的开发框架。**

它帮你把「调用大模型」这件看似复杂的事情，简化成了几行 Python 代码。

### 2.2 没有 LangChain vs 有 LangChain

**没有 LangChain（直接调用 API）：**

```python
# 你需要自己处理：
# 1. HTTP 请求的构建
# 2. 请求头的设置
# 3. 认证签名的计算
# 4. JSON 数据的序列化/反序列化
# 5. 错误处理
# 6. 流式响应的拼接
# ... 很繁琐

import requests
import json

url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "model": "qwen-turbo",
    "input": {
        "messages": [
            {"role": "user", "content": "夏天适合吃什么水果？"}
        ]
    }
}
response = requests.post(url, headers=headers, json=payload)
result = response.json()
print(result["output"]["text"])
# 还要处理各种可能的异常...
```

**有 LangChain：**

```python
# LangChain 帮你封装了以上所有细节
from langchain_community.chat_models import ChatTongyi

chat = ChatTongyi(api_key="你的Key", model="qwen-turbo")
response = chat.invoke("夏天适合吃什么水果？")
print(response.content)
# 干净、简洁、不易出错
```

### 2.3 LangChain 帮你做了什么

```
┌──────────────────────────────────────────────────┐
│                  LangChain 框架                    │
│                                                   │
│  你的代码（3-5行）                                 │
│       ↓                                          │
│  LangChain 内部处理：                              │
│  ├── 消息格式化（SystemMessage / HumanMessage）     │
│  ├── HTTP 请求构建                                 │
│  ├── 认证鉴权                                      │
│  ├── 错误重试                                      │
│  ├── 响应解析                                      │
│  └── 返回统一格式的 AIMessage                      │
│       ↓                                          │
│  通义 / OpenAI / 智谱AI / ...（任意模型）           │
│                                                   │
└──────────────────────────────────────────────────┘
```

---

## 三、为什么需要 API Key——理解大语言模型的服务模式

### 3.1 大语言模型的本质

先理解一个关键概念：**大语言模型本质上是一个（或一组）巨大的文件**。

```
大语言模型 = 通过海量数据训练得到的模型文件
              ↓
        这个文件本身没有"服务"功能
              ↓
        它需要被"加载"并"提供服务"才能使用
```

### 3.2 使用大语言模型的两种方式

```
方式一：自己搭建（学习成本高、硬件要求高）
┌──────────────────────────────────────────┐
│ 1. 下载模型文件（几十到几百 GB）            │
│ 2. 准备 GPU 服务器（显卡很贵）              │
│ 3. 自己写代码加载模型                      │
│ 4. 自己搭建 API 服务                       │
│ 5. 维护和更新                             │
│                                           │
│ 😰 太复杂了，不适合快速上手                  │
└──────────────────────────────────────────┘

方式二：使用云平台提供的服务（推荐 ✅）
┌──────────────────────────────────────────┐
│ 1. 去云平台注册账号                        │
│ 2. 获取一个 API Key                       │
│ 3. 写几行代码调用 API                      │
│ 4. 平台帮你处理模型加载、推理、扩容…         │
│                                           │
│ 🎉 简单快速，适合学习和开发                  │
└──────────────────────────────────────────┘
```

本课程采用**方式二**——使用阿里云平台提供的通义模型服务。

### 3.3 为什么云平台不能免费使用？

> 大语言模型的运行需要消耗**电力和算力**（GPU 服务器），这些都是有成本的。

| 成本项 | 说明 |
|--------|------|
| 电力 | GPU 服务器功耗大，电费不菲 |
| 算力 | GPU 显卡价格昂贵，且有使用寿命 |
| 带宽 | 传输数据需要网络带宽 |
| 运维 | 需要工程师维护系统稳定 |

所以云平台需要**收费**，而收费的前提是**知道谁在用**。

### 3.4 API Key 的作用

> **API Key = 你的身份证明**

```
我发起一个请求 → 携带 API Key → 平台识别"这是张三的请求"
                                 ↓
                           记录用量、计算费用
                                 ↓
                           从张三的账户扣费
```

```
┌──────────────────────────────────────────────┐
│                                              │
│  没有 API Key：                               │
│  平台："你是谁？我不能免费让你用。"              │
│                                              │
│  有 API Key：                                 │
│  平台："好的，你是张三，你的账户余额充足，        │
│         这是你要的回复，费用已从你账户扣除。"      │
│                                              │
└──────────────────────────────────────────────┘
```

### 3.5 不同平台的 Key 获取方式

Key 是由**模型供应商**（而非 LangChain）发放的。因为本节课用的是**通义**，所以要去**阿里云的平台**获取。

| 模型 | 获取 Key 的平台 |
|------|----------------|
| 通义（Qwen） | 阿里云百炼平台 |
| 智谱AI（GLM） | 智谱AI 开放平台 |
| OpenAI（GPT） | OpenAI 官网 |
| 百度千帆 | 百度智能云 |
| Google Gemini | Google AI Studio |

> 📌 原则：**用哪家的模型，就去哪家的平台注册、获取 Key。**

---

## 四、开发环境准备

### 4.1 需要的工具

| 工具 | 用途 | 是否必须 |
|------|------|:--------:|
| **VS Code** | 编写代码的编辑器 | ✅ |
| **Conda** | 管理虚拟环境 | ✅（也可以用 venv） |
| **Python 3.9+** | 运行环境 | ✅ |
| **终端（Terminal）** | 执行命令 | ✅ |

> 视频中老师使用的是 VS Code + Conda + Python 3.11。

### 4.2 文件组织

建议创建一个专门的项目文件夹来存放代码：

```
agent-demo/                    ← 项目根文件夹
    ├── 01-llm-应用.ipynb      ← 第一个应用（Jupyter Notebook）
    ├── .env                   ← 存放 API Key（不提交到 Git）
    └── .gitignore             ← 忽略敏感文件
```

视频中老师创建了一个 `agent-demo` 文件夹，所有代码都放在里面，文件命名为 `01-llm-应用.ipynb`（`.ipynb` 是 Jupyter Notebook 的交互式文件格式）。

---

## 五、虚拟环境详解

### 5.1 为什么要创建虚拟环境？

> 在开发一个新的 Python 应用时，**强烈建议创建一个全新的虚拟环境**。

**核心原因：应用之间互相隔离，互不影响。**

```
没有虚拟环境（不推荐）：
┌─────────────────────────────────────┐
│         全局 Python 环境              │
│                                     │
│  项目A 需要 langchain==0.3.27       │
│  项目B 需要 langchain==0.2.0        │
│  项目C 需要 numpy==1.24             │
│  项目D 需要 numpy==2.0              │
│                                     │
│  😱 版本冲突！互相覆盖！              │
└─────────────────────────────────────┘

使用虚拟环境（推荐 ✅）：
┌──────────┐ ┌──────────┐ ┌──────────┐
│ 环境A     │ │ 环境B     │ │ 环境C     │
│          │ │          │ │          │
│ langchain│ │ langchain│ │ langchain│
│ 0.3.27   │ │ 0.2.0    │ │ 0.3.27   │
│ numpy    │ │ numpy    │ │ numpy    │
│ 1.24     │ │ 1.24     │ │ 2.0      │
│          │ │          │ │          │
│ 互不干扰 ✅│ │ 互不干扰 ✅│ │ 互不干扰 ✅│
└──────────┘ └──────────┘ └──────────┘
```

### 5.2 创建虚拟环境的方法

网上有多种创建虚拟环境的方式，本课使用 **Conda**：

| 方式 | 命令 | 特点 |
|------|------|------|
| Conda | `conda create -n 环境名 python=版本` | 功能强，能管理 Python 版本 |
| venv | `python -m venv 环境名` | Python 自带，轻量 |

### 5.3 实操步骤

**步骤一：创建虚拟环境**

```bash
conda create -n agent python=3.11
```

命令分解：

| 部分 | 含义 |
|------|------|
| `conda create` | 创建一个新的 Conda 环境 |
| `-n agent` | 环境名称叫 `agent`（可以自定义） |
| `python=3.11` | 指定 Python 版本为 3.11 |

执行后，Conda 会列出将要安装的包，输入 `y` 确认：

```
Proceed ([y]/n)? y

Downloading and Extracting Packages:
...
Preparing transaction: done
Verifying transaction: done
Executing transaction: done
#
# To activate this environment, use
#
#     $ conda activate agent
#
```

> ⚠️ 如果提示环境已存在（之前创建过），可以先删除再重建：
> ```bash
> conda remove -n agent --all
> conda create -n agent python=3.11
> ```

**步骤二：激活虚拟环境**

```bash
conda activate agent
```

激活后，终端提示符前面会出现环境名称：

```
(agent) $    ← 表示当前在 agent 环境中
```

**步骤三：验证环境**

```bash
which python
# 应该输出 agent 环境中的 Python 路径
# 例如：/Users/xxx/anaconda3/envs/agent/bin/python

python --version
# 应该输出：Python 3.11.x
```

### 5.4 虚拟环境管理常用命令

| 命令 | 作用 |
|------|------|
| `conda create -n 名称 python=3.11` | 创建新环境 |
| `conda activate 名称` | 激活（进入）环境 |
| `conda deactivate` | 退出当前环境 |
| `conda env list` | 查看所有环境 |
| `conda remove -n 名称 --all` | 删除环境 |
| `conda list` | 查看当前环境已安装的包 |

---

## 六、安装 LangChain 及依赖包

### 6.1 包之间的关系（重要！）

在安装之前，先理解这几个包的关系，避免蒙着头瞎装：

```
LangChain 生态系统的包层次：

langchain（主包）
    ├── 提供框架基础功能
    ├── 文档中说它是"合理起点"
    └── 但核心价值在生态集成中，主包本身功能不全

langchain-core（核心包）          ← 不需要手动安装
    ├── 提供统一接口和类型定义
    └── 安装 langchain 时自动附带

langchain-community（社区集成包）  ← 我们需要安装的！
    ├── 包含各种第三方模型和工具的集成
    ├── ChatTongyi 就在这里面
    └── 安装 langchain-community 时也会自动安装 langchain-core

dashscope（阿里云 SDK）           ← 通义专用底层依赖
    └── 通义模型实际通信时需要的阿里云 SDK
```

**关系总结：**

```
我们需要手动安装的：
├── langchain-community  ← 包含 ChatTongyi
└── dashscope            ← 通义底层通信需要

会自动附带安装的（不用管）：
├── langchain
├── langchain-core
└── 其他依赖...
```

### 6.2 安装命令

```bash
# 确保已激活虚拟环境
conda activate agent

# 安装 langchain-community
pip install langchain-community

# 安装阿里云 dashscope SDK（通义依赖）
pip install dashscope
```

**关于版本锁定：**

视频中老师安装的版本是 `langchain-community==0.3.27`。建议指定版本以保持一致性：

```bash
pip install langchain-community==0.3.27 dashscope
```

> ⚠️ **注意**：`langchain-community` 这个包名中有一个连字符（`-`），在某些终端中如果不加引号可能报错。如果遇到问题，可以这样写：
> ```bash
> pip install "langchain-community==0.3.27"
> ```

### 6.3 为什么通义没有像 OpenAI 那样的独立包？

在官方文档中可以看到：

```
使用 OpenAI → pip install langchain-openai（有独立包）
使用 Google → pip install langchain-google-genai（有独立包）
使用通义    → pip install langchain-community（通过社区集成包）
```

这是因为：
- OpenAI、Google 等是 LangChain 官方**重点维护**的，有独立的专门包
- 通义等模型通过社区集成包（`langchain-community`）来支持
- **不影响使用**，只是安装的包名不同

### 6.4 安装后的验证

```bash
# 确认包已安装
pip list | grep langchain
# 预期输出：
# langchain            0.3.27
# langchain-community  0.3.27
# langchain-core       0.3.x

pip list | grep dashscope
# 预期输出：
# dashscope            1.x.x
```

也可以用 Python 验证导入：

```bash
python -c "from langchain_community.chat_models import ChatTongyi; print('导入成功！')"
```

---

## 七、获取通义 API Key

### 7.1 去哪里获取？

通义模型的 Key 从**阿里云百炼平台**获取。

> 📎 地址：阿里云百炼平台（具体 URL 可能会有变化，搜索「阿里云百炼」即可）

### 7.2 完整操作步骤

**第一步：打开阿里云百炼平台，登录**

```
打开网站 → 点击「登录」
         → 选择登录方式：
            ├── 支付宝扫码
            ├── 淘宝账号
            ├── 阿里云账号
            └── 其他方式
         → 完成登录
```

登录成功后，页面右上角会显示你的账号信息。

**第二步：进入模型页面**

```
登录后 → 在页面上找到「模型」或「模型中心」入口 → 点击进入
```

这里会展示通义提供的多个模型（qwen-turbo、qwen-plus、qwen-max 等），这些都是可以使用的。不过我们**当前关注的不是模型本身，而是获取 API Key**。

**第三步：进入 API Key 管理页面**

```
在模型页面的左侧导航栏 → 找到最下面的「API Key」选项 → 点击进入
```

这样就来到了 API Key 管理页面。

**第四步：创建新的 API Key**

```
点击「创建 API Key」按钮
    ↓
弹出创建窗口
    ↓
空间选择：默认空间即可（不用改）
描述：可以留空（不用管）
    ↓
点击「确定」
    ↓
Key 创建成功！
```

**第五步：查看并复制 Key**

> ⚠️ API Key 创建后默认是**隐藏状态**的。

```
在 Key 列表中 → 找到刚创建的 Key
             → 点击「查看」
             → Key 显示出来
             → 点击「复制」按钮
             → 保存到安全的地方
```

**全过程图示（模拟）：**

```
┌─────────────────────────────────────────────────┐
│              阿里云百炼平台                        │
│                                                 │
│  顶部导航：[模型] [应用] [数据] ... [头像]         │
│                                                 │
│  左侧菜单：                          │ 右侧内容： │
│  ├── 模型中心                        │           │
│  ├── 应用中心                        │  API Key  │
│  ├── 数据中心                        │  管理页面  │
│  ├── ...                            │           │
│  └── API Key  ← 点这里               │ [创建Key] │
│                                                 │
│  ┌─────────────────────────────────────────┐    │
│  │ 创建 API Key                             │    │
│  │                                         │    │
│  │ 空间： [默认空间 ▼]                       │    │
│  │ 描述： [_______________]                  │    │
│  │                                         │    │
│  │         [取消]    [确定]                  │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  创建成功后：                                    │
│  ┌─────────────────────────────────────────┐    │
│  │ Key 名称    │ Key 值          │ 操作     │    │
│  │ my-key      │ sk-****隐藏**** │ [查看]   │    │
│  │             │                 │ [复制]   │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 7.3 登录方式

阿里云支持多种登录方式：

| 登录方式 | 说明 |
|----------|------|
| 支付宝扫码 | 最方便，视频中老师用的这种方式 |
| 淘宝账号 | 如果你有淘宝账号 |
| 阿里云账号 | 如果你之前注册过阿里云 |
| 手机号 | 常规注册方式 |

> 💡 没有账号的话，注册一个即可，流程简单。

### 7.4 可用模型一览

获取 Key 后，你可以在平台看到通义提供的多个模型：

| 模型名称 | 级别 | 适用场景 |
|----------|:----:|----------|
| `qwen-turbo` | 快速版 | 简单对话、快速响应、成本低 |
| `qwen-plus` | 增强版 | 日常使用，能力与速度均衡 |
| `qwen-max` | 旗舰版 | 复杂推理、高质量回答 |
| `qwen-long` | 长文本版 | 超长上下文处理 |

本课使用 `qwen-turbo` 进行演示。

---

## 八、编写第一个 LangChain 应用

### 8.1 文件格式说明

视频中使用 `.ipynb`（Jupyter Notebook）格式。这是一种**交互式**文件格式：

```
.ipynb 的优势：
├── 写完代码可以逐块运行
├── 运行结果直接显示在代码下方
├── 方便调试和实验
└── 适合教学演示

.py 的优势：
├── 适合正式项目
└── 方便版本管理和部署
```

本课跟着视频用 `.ipynb`，后续课程可以切换到 `.py`。

### 8.2 配置 VS Code 的 Python 内核

在 VS Code 中打开 `.ipynb` 文件后，需要选择正确的 Python 内核：

```
打开 .ipynb 文件
    ↓
右上角或右下角找到内核选择器
    ↓
点击「选择内核」
    ↓
选择「Python 环境...」
    ↓
找到并选择 agent（我们创建的虚拟环境）
    ↓
内核就绪 ✅
```

> ⚠️ 如果列表中没有 `agent` 环境，说明 VS Code 还没有识别到。可以先在终端中激活一次环境，或者重启 VS Code。

### 8.3 完整代码

```python
# ============================================================
# 第一个 LangChain 应用 —— 接入通义大语言模型
# ============================================================

# 1. 导入通义聊天模型类
from langchain_community.chat_models import ChatTongyi

# 2. 设置 API Key
api_key = "sk-你的通义API_Key粘贴到这里"

# 3. 创建模型实例
llm = ChatTongyi(
    api_key=api_key,
    model="qwen-turbo"       # 使用通义快速版模型
)

# 4. 调用模型（两种写法）
# 写法一：直接提问（简洁）
response = llm.invoke("夏天适合吃什么水果？请只回复几个水果名称。")
print(response.content)

# 写法二：先接收再打印（便于后续处理）
# info = llm.invoke("夏天适合吃什么水果？请只回复几个水果名称。")
# print(info.content)
```

### 8.4 代码逐行解析

#### 第 1 步：导入

```python
from langchain_community.chat_models import ChatTongyi
```

| 路径段 | 含义 |
|--------|------|
| `langchain_community` | 社区集成包（我们已经安装的） |
| `chat_models` | 聊天模型子模块 |
| `ChatTongyi` | 通义千问的聊天模型类 |

> 💡 初次编写时，如果你记不住完整的导入路径，在 VS Code 中可以先写 `from langchain_community.`，编辑器会自动补全提示后续路径。这也是视频中老师说的「可以自动提出来」的含义。

#### 第 2 步：设置 API Key

```python
api_key = "sk-你的通义API_Key粘贴到这里"
```

把上一节在阿里云百炼平台复制的 Key 粘贴过来。Key 通常以 `sk-` 开头。

> ⚠️ 这只是演示写法，生产环境中不要硬编码 Key。学完本课后，建议改为使用环境变量或 `.env` 文件管理。

#### 第 3 步：创建模型实例

```python
llm = ChatTongyi(
    api_key=api_key,
    model="qwen-turbo"
)
```

**ChatTongyi 类**就是一个「通义模型的客户端」。创建它的时候，告诉它两件事：

| 参数 | 值 | 含义 |
|------|-----|------|
| `api_key` | 你的 Key | 「我是谁，我有权限使用」 |
| `model` | `"qwen-turbo"` | 「用哪个模型来处理我的请求」 |

如果鼠标悬停在 `ChatTongyi` 上，VS Code 会显示这个类的文档，告诉你它需要哪些参数——这就是视频中老师说的「提示」。

#### 第 4 步：调用模型

```python
response = llm.invoke("夏天适合吃什么水果？请只回复几个水果名称。")
```

- `invoke()` 是 LangChain 中**调用模型的标准方法**
- 括号里放你要问的问题（一个字符串）
- 返回的是一个 `AIMessage` 对象
- `response.content` 是模型回复的**纯文本内容**

**为什么加了"请只回复几个水果名称"？**

> 如果不加这个限制，模型可能会生成很长的回复（介绍每种水果的特点、功效、注意事项……），生成需要较长时间。加上限制可以让回复更简短，方便快速看到效果。

### 8.5 代码变体——使用消息系统

上面的写法是最简形式。LangChain 还支持更规范的写法，使用消息列表：

```python
from langchain_community.chat_models import ChatTongyi
from langchain.schema import HumanMessage

llm = ChatTongyi(api_key="你的Key", model="qwen-turbo")

# 使用 HumanMessage 构建消息
messages = [HumanMessage(content="夏天适合吃什么水果？请只回复几个水果名称。")]
response = llm.invoke(messages)
print(response.content)
```

两种写法效果相同，第一种更简单，适合快速实验。

---

## 九、运行与调试

### 9.1 首次运行——ipykernel 安装

如果你使用的是 `.ipynb` 文件，**首次运行**时可能会提示：

```
Running cells with 'agent' requires ipykernel package.
```

这是因为 Jupyter Notebook 的交互式运行需要 `ipykernel` 包。安装即可：

```bash
# 确保在 agent 环境中
conda activate agent
pip install ipykernel
```

安装一次即可，后续不用再装。安装过程可能需要一两分钟（会下载一些依赖）。

### 9.2 第二次运行——dashscope 缺失

安装完 `ipykernel` 后再次运行，可能会遇到新的报错：

```
ModuleNotFoundError: No module named 'dashscope'
```

**这就是视频中老师遇到的报错！** 意思是：缺少 `dashscope` 这个包。`dashscope` 是阿里云通义模型的底层 SDK，`ChatTongyi` 内部实际通信时需要它。

```bash
# 解决：安装 dashscope
conda activate agent
pip install dashscope
```

> 📌 **为什么会出现这个问题？** 因为 `langchain-community` 包含了 `ChatTongyi` 这个类（可以导入成功），但 `ChatTongyi` 的底层实现依赖 `dashscope` 这个阿里云 SDK。`dashscope` 不是 `langchain-community` 的自动依赖，需要手动安装。
>
> **这也就是为什么视频中老师提前在文档中注明了需要安装 `dashscope`。**

### 9.3 第三次运行——终于成功了！

安装 `dashscope` 后再次运行，就能看到模型的回复了：

```
西瓜、桃子、葡萄、哈密瓜
```

或者如果不加限制（去掉"只回复几个水果名称"），回复会更详细：

```
夏天炎热，人体容易出汗，流失大量水分和矿物质。
以下是夏天适合吃的水果推荐：

1. 西瓜 —— 含水量高达90%以上，能有效清热解暑、补充水分
2. 哈密瓜 —— 含有丰富的维生素A和C，清甜爽口
3. 桃子 —— 富含维生素C和膳食纤维，甜美多汁
4. 葡萄 —— 含有丰富的抗氧化物质，有助于保护心血管健康
5. 荔枝 —— 甜美可口，含有丰富的葡萄糖和维生素
...
```

### 9.4 完整运行流程总结

```
第一步：激活环境
    conda activate agent

第二步：首次运行前确保依赖完整
    pip install langchain-community==0.3.27
    pip install dashscope
    pip install ipykernel        ← 如果用 .ipynb 文件

第三步：在 VS Code 中打开 .ipynb 文件
    选择内核 → agent 环境

第四步：粘贴代码 + 替换 API Key

第五步：点击运行 ▶
    期待看到模型的回复 🎉
```

---

## 十、理解模型的响应时间

### 10.1 为什么有时候等待很久？

视频中老师演示了一个现象：

```
提问："夏天适合吃什么水果？"
         ↓
    等待 1 秒... 2 秒... 3 秒...
         ↓
    一次性返回大段内容
```

> 「并不是说人家没给我们回复，而是它要生成的内容比较多，需要等待它生成完成。」

### 10.2 模型是怎么生成回复的？

大语言模型生成回复的过程是**逐字逐句**的：

```
输入："夏天适合吃什么水果？"
  ↓
模型开始生成（一个字一个字地）：
  "夏" → "天" → "炎" → "热" → "，" → "人" → "体" → ...
  ↓
全部生成完毕后
  ↓
一次性返回完整结果
```

### 10.3 影响响应时间的因素

| 因素 | 说明 | 举例 |
|------|------|------|
| **回复长度** | 越长越慢 | "回复几个水果名" vs "详细介绍每种水果" |
| **模型规模** | 越大越慢 | qwen-max 比 qwen-turbo 慢 |
| **服务器负载** | 高峰期慢 | 工作日白天 vs 深夜 |
| **网络延迟** | 国内快、国外慢 | 通义（快）vs OpenAI 无代理（连不上） |

### 10.4 实际演示中的对比

```python
# 快速回复（< 1 秒）
llm.invoke("夏天适合吃什么水果？只回复水果名称，不要解释。")
# → "西瓜、葡萄、桃子、哈密瓜"

# 较慢回复（3-5 秒或更长）
llm.invoke("夏天适合吃什么水果？请详细介绍每种水果的特点和功效。")
# → 大段详细文字...
```

---

## 十一、完整流程回顾

经过以上各节的学习，我们用一张图回顾**从零到成功调用**的完整流程：

```
┌─────────────────────────────────────────────────────────────┐
│              LangChain 接入大语言模型——完整流程               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Step 1: 创建虚拟环境                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ conda create -n agent python=3.11                     │   │
│  │ conda activate agent                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                  │
│  Step 2: 安装依赖包                                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ pip install langchain-community==0.3.27               │   │
│  │ pip install dashscope                                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                  │
│  Step 3: 获取 API Key                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 阿里云百炼平台 → 注册/登录 → API Key 管理 → 创建Key    │   │
│  │ → 查看 → 复制 Key                                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                  │
│  Step 4: 编写代码                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ from langchain_community.chat_models import ChatTongyi│   │
│  │                                                       │   │
│  │ llm = ChatTongyi(api_key="你的Key", model="qwen-turbo")│   │
│  │ response = llm.invoke("你的问题")                       │   │
│  │ print(response.content)                                │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                  │
│  Step 5: 运行 & 排错                                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 首次运行 → 安装 ipykernel（如果用 .ipynb）              │   │
│  │ 二次运行 → 安装 dashscope（如果报 ModuleNotFoundError） │   │
│  │ 三次运行 → 🎉 成功！                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 十二、常见问题与排错指南

### 12.1 错误速查表

| 错误信息 | 原因 | 解决方法 | 出现阶段 |
|----------|------|----------|:--------:|
| `conda: command not found` | 未安装 Conda | 安装 Anaconda 或 Miniconda | 环境搭建 |
| `Environment already exists` | 环境名已被使用 | 换个名字，或 `conda remove -n agent --all` 后重建 | 环境搭建 |
| `Running cells requires ipykernel` | Jupyter 缺少内核包 | `pip install ipykernel` | 首次运行 |
| `ModuleNotFoundError: No module named 'dashscope'` | 缺阿里云 SDK | `pip install dashscope` | 运行时 |
| `ModuleNotFoundError: No module named 'langchain_community'` | 缺社区集成包 | `pip install langchain-community` | 运行时 |
| `No module named 'langchain_community.chat_models'` | 版本不对或安装不完整 | 重装：`pip install langchain-community==0.3.27` | 运行时 |
| `ImportError: cannot import name 'ChatTongyi'` | 类名拼写错误或包版本低 | 检查拼写：`ChatTongyi`（不是 `ChatTongYi`） | 导入时 |
| 内核选择列表中没有 agent 环境 | VS Code 未识别 | 在终端激活一次 agent 环境，或重启 VS Code | 配置时 |
| `ConnectionError` / `Timeout` | 网络不通（通义是国内的一般不会） | 检查是否误开了代理、检查网络连接 | 运行时 |

### 12.2 排查流程图

```
代码运行报错
    ↓
错误类型是 ModuleNotFoundError？
    ↓ 是
缺少什么模块？
    ├── dashscope → pip install dashscope
    ├── langchain_community → pip install langchain-community
    ├── ipykernel → pip install ipykernel
    └── 其他 → 照着缺失的模块名 pip install
    ↓
重新运行 → 🎉
```

### 12.3 为什么版本号很重要？

```
pip install langchain-community        ← 不指定版本：安装最新的
pip install langchain-community==0.3.27 ← 指定版本：安装固定的

区别：
├── 不指定版本：你和别人安装的可能不一样，运行效果可能不同
└── 指定版本：  所有人装同一个版本，效果一致，方便排查问题
```

视频中老师安装的是 `0.3.27`，建议保持一致。

---

## 十三、课后练习

### 练习一：环境搭建（实操）

> 从零开始，创建一个全新的虚拟环境，安装 LangChain 及依赖，完成首次调用通义模型。

**验收标准：**
- [ ] 成功创建并激活一个新的虚拟环境
- [ ] `langchain-community` 和 `dashscope` 安装成功
- [ ] 在阿里云百炼平台获取了 API Key
- [ ] 代码运行成功，打印出通义模型的回复

### 练习二：更换模型

> 在上面的代码中，将 `model="qwen-turbo"` 分别改为 `"qwen-plus"` 和 `"qwen-max"`，用**同一个问题**测试三个模型，对比回复质量。

| 模型 | 回复内容（摘要） | 响应速度 | 回复质量评价 |
|------|-----------------|:--------:|:------------:|
| qwen-turbo | | | |
| qwen-plus | | | |
| qwen-max | | | |

### 练习三：理解 API Key

> 用自己的话回答以下问题：
>
> 1. 为什么调用大语言模型需要 API Key？
> 2. 如果别人拿到了你的 API Key，可能发生什么？
> 3. API Key 是 LangChain 发的还是模型供应商（阿里云）发的？

### 练习四：提问策略实验

> 用**同一个模型**，对同一个话题，分别用不同的提问方式测试，观察回复长度和质量的差异：

```python
# 提问方式一：简短提问（不加限制）
"夏天适合吃什么水果？"

# 提问方式二：加长度限制
"夏天适合吃什么水果？请只回复水果名称，不要解释。"

# 提问方式三：加角色和格式要求
"你是一个营养师。夏天适合吃什么水果？请分点列举，每种水果说明一个主要功效。"
```

| 提问方式 | 回复长度（大约） | 响应时间 | 是否符合预期 |
|:--------:|:---------------:|:--------:|:------------:|
| 方式一 | | | |
| 方式二 | | | |
| 方式三 | | | |

---

## 十四、课程小结

### 14.1 本课知识图谱

```
┌────────────────────────────────────────────────────────────┐
│             第一课核心知识体系                               │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  大语言模型的服务模式                                    │
│      ├── 模型文件本身不提供服务                               │
│      ├── 需要平台来加载模型 + 提供 API                         │
│      └── 我们用 API Key 证明身份，使用平台的云服务              │
│                                                            │
│  2️⃣  虚拟环境的作用                                         │
│      ├── 隔离不同项目的依赖                                   │
│      └── conda create -n 环境名 python=3.11                  │
│                                                            │
│  3️⃣  LangChain 的包结构                                     │
│      ├── langchain-community（社区集成，需手动安装）           │
│      ├── langchain-core（核心，自动附带）                     │
│      └── dashscope（通义底层SDK，需手动安装）                  │
│                                                            │
│  4️⃣  API Key 的获取流程                                     │
│      阿里云百炼平台 → 注册登录 → API Key 管理 → 创建 → 复制    │
│                                                            │
│  5️⃣  第一个应用的代码结构                                    │
│      导入 → 设置Key → 创建模型实例 → invoke() → 打印结果       │
│                                                            │
│  6️⃣  常见报错的处理                                         │
│      ModuleNotFoundError → pip install 对应包               │
│      ipykernel 缺失 → pip install ipykernel                 │
│      dashscope 缺失 → pip install dashscope                 │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 14.2 一句话总结

> 创建虚拟环境 → 安装 `langchain-community` 和 `dashscope` → 去阿里云获取 API Key → 写三行代码调用通义模型 → 完成第一个大语言模型应用。

### 14.3 下一步

学会了接入通义之后，后续课程将学习：

- 🔄 **如何更换其他模型**（从通义到智谱AI、OpenAI 等）——参考《LangChain 模型选型与平台调研指南》
- 💬 **消息系统**（SystemMessage / HumanMessage / AIMessage 的深入使用）
- 🌡️ **模型参数调优**（temperature 等参数的深入理解）
- 🔐 **API Key 安全管理**（`.env` 文件、环境变量的最佳实践）

---

*本教学文档基于陈泽鹏老师视频课程（第一课·环境搭建与首次接入）整理编写。*  
*本文档为入门基础篇，后续课程请参考配套文档。*
