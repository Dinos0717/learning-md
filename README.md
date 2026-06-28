# Learning-MD

> AI Agent 开发与 Git/GitHub 学习笔记仓库，整理个人学习路线、教学文档及开源项目实战代码。

---

## 📂 仓库结构

```
learning-md/
├── github/       # Git & GitHub 教学文档（15 篇）
├── langchain/    # LangChain & Agent 开发教学文档（38 篇）
└── example/      # 17 个开源项目实战代码
```

---

## 🗂️ github/ — Git & GitHub 从入门到精通

按学习顺序编号，从创建仓库到命令行进阶：

| 序号 | 文档 | 简介 |
|:---:|------|------|
| 01 | 装修 Github 个人主页 | GitHub 个人主页美化与配置 |
| 02 | 创建自己的第一个仓库 | 从零创建并管理 GitHub 仓库 |
| 03 | Github 是如何工作的 | Git 工作流程与核心原理 |
| 04 | GitHub 开源协作全流程实战 | Fork、PR、Code Review 全流程 |
| 05 | GitHub 仓库附属功能详解 | Issues、Wiki、Projects、Actions |
| 06 | GitHub-Desktop 安装配置 | GUI 工具安装与基本配置 |
| 07 | Git 四个分区的概念 | 工作区、暂存区、本地仓库、远程仓库 |
| 08 | GitHub-Desktop 进阶操作 | 分支管理、冲突解决、历史回溯 |
| 09 | 分支合并 | merge、rebase 策略与最佳实践 |
| 10 | 解决合并冲突 | 冲突场景分析与实战解决 |
| 11 | Github 做开源贡献的基本流程 | 从 Issue 到 PR 的完整贡献流程 |
| 12 | IDEA 里面使用 Git | IntelliJ IDEA 集成 Git 操作 |
| 13 | IDEA 里面使用 Git 进阶 | IDEA 高级 Git 功能与技巧 |
| 14 | Git 命令行 1 | 基础命令：clone、add、commit、push |
| 15 | Git 命令行 2 | 进阶命令：stash、cherry-pick、reflog |

---

## 🤖 langchain/ — LangChain & Agent 开发体系

按学习路线编号，覆盖从环境搭建到多 Agent 协作的完整链路：

### 基础篇（01-04）

| 序号 | 文档 | 简介 |
|:---:|------|------|
| 01 | 切换大语言模型教学文档 | 多模型切换方案与环境准备 |
| 02 | LangChain 模型选型与平台调研指南 | GPT、文心、通义千问等模型对比 |
| 03 | LangChain 环境搭建与首次接入大语言模型 | 开发环境配置与 Hello World |
| 04 | 使用 Ollama 部署本地大语言模型 | 本地模型部署与接入 |

### LangChain 核心篇（05-18）

| 序号 | 文档 | 简介 |
|:---:|------|------|
| 05 | LangChain 提示词模板详解 | Prompt Template 设计与工程化 |
| 06 | LangChain 输出解析器详解 | Structured Output 与解析策略 |
| 07 | LangChain 链式调用详解 | Chain 与 LCEL 表达式语言 |
| 08 | LangChain 流式输出详解 | Streaming 与 SSE 实时推送 |
| 09-12 | LangChain 记忆系统详解（4 篇） | BufferMemory / Window / Token / Summary |
| 13-14 | LangChain 文本嵌入模型详解（2 篇） | 云端 + 本地 Embedding 方案 |
| 15 | LangChain 语义搜索实战 | RAG 文档问答匹配全流程 |
| 16-17 | LangChain 工具封装详解（2 篇） | 工具定义、注册与天气查询实战 |
| 18 | LangChain 智能体 Agent 创建 | 多工具调用 Agent 完整实现 |

### LangGraph 实战篇（19-25）

| 序号 | 文档 | 简介 |
|:---:|------|------|
| 19 | LangGraph 实战 00 开篇 | 图式工作流思想与框架定位 |
| 20 | LangGraph 实战 01 入门和组件 | Node、Edge、State 核心概念 |
| 21 | LangGraph 实战 02 可记忆可恢复智能体 | Checkpoint 与状态持久化 |
| 22 | LangGraph 实战 03 人机协作与时间旅行 | HITL 与状态回溯 |
| 23 | LangGraph 实战 04 多智能体协作系统 | 多 Agent 编排与通信 |
| 24 | LangGraph 实战 05 生产环境 | 部署、监控与工程化实践 |
| 25 | LangGraph 终极实战-AI 辅助投资工具 | 完整项目：投资分析 Agent 系统 |

### Agent 进阶篇（26-37）

| 序号 | 文档 | 简介 |
|:---:|------|------|
| 26 | 为什么现在必须学 Agent 开发 | AI 开发新范式与行业趋势 |
| 27 | 多 Agent 项目架构总览 | 完整系统架构设计 |
| 28 | LangGraph 多 Agent 开发实战 | 从零到工程化落地 |
| 29 | Core 模块精讲 | Agent 系统基石与核心抽象 |
| 30 | Schema 模块 | 数据结构决定 Agent 规范 |
| 31 | Memory 模块 | 让 Agent 真正记住上下文 |
| 32 | Session 模块 | 多用户会话管理实战 |
| 33 | Agents 模块 | 多智能体业务开发逻辑 |
| 34 | 多 Agent 开发路线图与未来方向 | 技术演进与学习路径 |
| 35 | 2026 十大 Agent 框架到底选哪个 | LangGraph、AutoGen、CrewAI 等横评 |
| 36 | Agent 应用案例 1 | CrewAI + FastAPI 多 Agent 协作 |
| 37 | Agent 应用案例 2 | 技术研究员智能体案例 |
| 38 | Agent 应用案例 3 | 健康档案助手智能体案例（RAG + CrewAI） |

---

## 💻 example/ — 开源项目实战代码

收录 [NanGePlus](https://github.com/NanGePlus) 作者的 17 个开源项目，覆盖主流 Agent 框架：

| 框架/领域 | 项目 | 说明 |
|-----------|------|------|
| **LangChain** | LangChain_V1_Test | V1.x 全体系实战（16 章节） |
| | PromptLangChainTest | Prompt 工程用例合集 |
| | RagLangChainTest | 健康档案 RAG 知识库系统 |
| **LangGraph** | LangGraphChatBot | 带记忆的智能客服 Web 应用 |
| **CrewAI** | CrewAITest | 多 Agent 协作 + FastAPI 服务 |
| | CrewAIToolsTest | 内置工具测试系列 |
| | CrewAIKnowledgeTest | Knowledge 知识库功能测试 |
| | CrewAIFullstackTest | Flask + Vue.js 全栈项目 |
| | CrewAIFlowsFullStack | Flows 工作流 + MySQL 持久化 |
| **AutoGen** | AutoGenTest | 微软 AutoGen 框架测试 |
| | AutoGenV04Test | AutoGen v0.4 新架构测试 |
| **其他框架** | MetaGPTTest | 软件公司隐喻多 Agent 框架 |
| | SwarmTest | OpenAI 轻量级编排框架 |
| | OpenAIAgentsSDKTest | OpenAI Agents SDK 测试 |
| **MCP** | MCPTest | 模型上下文协议功能测试 |
| | MCPServerTest | MCP Server 搭建与配置 |
| **Agent 综合** | ReActAgentsTest | Agent 相关资源合集 |

---

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| **LLM 框架** | LangChain V1.x、LangGraph |
| **多 Agent** | CrewAI、AutoGen、MetaGPT、Swarm |
| **协议** | MCP（Model Context Protocol） |
| **后端** | FastAPI、Flask、Uvicorn |
| **前端** | Gradio、Vue.js |
| **数据库** | PostgreSQL、MySQL、Chroma、Milvus |
| **向量检索** | RAG、Embedding、向量数据库 |
| **模型部署** | Ollama、OneAPI |
| **工具链** | Git、GitHub Desktop、IntelliJ IDEA |

---

## 📅 更新记录

- **2026-06-28**：整理 example 目录，移除嵌套 git 仓库；统一所有 README 排版格式
- **2026-06-27**：按创建时间给 github、langchain 文件添加序号
- **2026-06-17 ~ 06-27**：完成 LangChain & Agent 开发全系列教学文档

---

> 📌 本项目仅供个人学习整理使用。example/ 目录下代码版权归原作者 [NanGePlus](https://github.com/NanGePlus) 所有。
