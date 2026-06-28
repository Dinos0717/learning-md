# NanGePlus 开源仓库合集

> 作者 GitHub: [https://github.com/NanGePlus](https://github.com/NanGePlus)
>
> 本文件夹收录了 NanGePlus 作者与 **LangChain**、**LangGraph** 及 **智能体（Agent）** 相关的全部开源仓库，共计 17 个项目。

---

## 📚 目录

- [LangChain 生态](#langchain-生态)
- [LangGraph](#langgraph)
- [CrewAI 多 Agent 框架](#crewai-多-agent-框架)
- [其他多 Agent 框架](#其他多-agent-框架)
- [MCP 协议](#mcp-协议)
- [Agent 综合](#agent-综合)

---

## LangChain 生态

### [LangChain_V1_Test](./LangChain_V1_Test/)

从零基础理解 LangChain V1.x 及其相关生态（包括 LangGraph、DeepAgents 等）在当前主流智能体开发中的定位与核心能力。涵盖：

- 基础环境准备、依赖安装
- LLM 调用、Prompt 工程实战
- Agent 类自动化流程构建
- 知识库（RAG）、向量检索
- 结构化/非结构化数据处理
- 多模态与插件集成

### [PromptLangChainTest](./PromptLangChainTest/)

Prompt 工程相关用例合集，包括：

- 模拟智能推荐客服系统构建和问答
- 思维链（Chain of Thought）
- 自洽性（Self-Consistency）
- 思维树（Tree of Thoughts）等进阶 Demo
- 支持多种大模型（OpenAI、阿里通义千问等）
- 使用 FastAPI 对应用进行 API 封装

### [RagLangChainTest](./RagLangChainTest/)

模拟健康档案私有知识库构建和检索全流程，实现 RAG（检索增强生成）功能：

- **离线步骤**：文档加载 → 文档切分 → 向量化 → 灌入向量数据库
- **在线步骤**：获取用户问题 → 问题向量化 → 检索向量数据库 → 填入 Prompt 模版 → 调用 LLM 生成回复
- 一份代码同时支持多种大模型（OpenAI、阿里通义千问等）

---

## LangGraph

### [LangGraphChatBot](./LangGraphChatBot/)

使用 LangGraph + DeepSeek-R1 + FastAPI + Gradio 实现带有记忆功能的流量包推荐智能客服 Web 端用例。支持多种大模型：

- GPT 大模型
- 国产大模型（OneApi 方式）
- Ollama 本地开源大模型
- 阿里通义千问大模型

---

## CrewAI 多 Agent 框架

### [CrewAITest](./CrewAITest/)

使用 CrewAI + FastAPI 搭建多 Agent 协作应用并对外提供 API 服务。支持：

- GPT 大模型
- 国产大模型
- Ollama 本地大模型

### [CrewAIToolsTest](./CrewAIToolsTest/)

CrewAI 官方提供的 Tools 测试系列，涵盖各种内置工具的用法与实战案例。

### [CrewAIKnowledgeTest](./CrewAIKnowledgeTest/)

CrewAI 新版本 Knowledge 属性测试，支持将多种数据格式内容作为知识增强知识库提供给 Agent 使用：

- txt、PDF、CSV、Excel、JSON
- 多文件混合知识库

### [CrewAIFullstackTest](./CrewAIFullstackTest/)

完整的 AI 应用全栈项目：Flask + Vue.js + CrewAI，从前端到后端的完整闭环。

### [CrewAIFlowsFullStack](./CrewAIFlowsFullStack/)

使用 FastAPI 后端框架 + CrewAI 实现 AI Agent 复杂工作流：

- CrewAI Flows 功能实现
- Flow 运行中间结果持久化存储和查询（MySQL）
- 多 Flow 并行（Celery 异步任务队列）

---

## 其他多 Agent 框架

### [AutoGenTest](./AutoGenTest/)

微软开源多 Agent 智能体协作框架 **AutoGen** 全新改版核心概念介绍及相关案例测试。

### [AutoGenV04Test](./AutoGenV04Test/)

AutoGen v0.4 最新架构测试。v0.4 是对 AutoGen 的一次从头重写，旨在构建更健壮、可扩展、更易用的跨语言 Agent 库，采用分层架构设计满足不同场景需求。

### [MetaGPTTest](./MetaGPTTest/)

开源多 Agent 智能体协作框架 **MetaGPT** 核心概念介绍及相关案例测试。MetaGPT 以软件公司为隐喻，为 GPT 分配不同角色（产品经理、架构师、工程师等）协作完成复杂任务。

### [SwarmTest](./SwarmTest/)

OpenAI 开源多 Agent 智能体协作框架 **Swarm** 核心概念介绍及相关案例测试。Swarm 是 OpenAI 的实验性轻量级多 Agent 编排框架。

### [OpenAIAgentsSDKTest](./OpenAIAgentsSDKTest/)

OpenAI 于 2025 年 3 月正式发布的开源 **OpenAI Agents SDK** 测试。这是一个专为构建智能代理的轻量级且生产就绪的开发工具包，是 Swarm 的升级版本，支持更轻松地创建、编排和管理多代理系统。

---

## MCP 协议

### [MCPTest](./MCPTest/)

**MCP（Model Context Protocol，模型上下文协议）** 功能测试。MCP 是 Anthropic（Claude）开源的一种开放协议，可实现 LLM 应用程序与外部数据源和工具之间的无缝集成。本项目编写 LLM 应用程序调用 MCP。

### [MCPServerTest](./MCPServerTest/)

MCP Server 测试系列，涵盖多种 MCP Server 的搭建、配置与使用场景。

---

## Agent 综合

### [ReActAgentsTest](./ReActAgentsTest/)

AI Agent 相关分享合集，包含 YouTube 频道和 B 站频道的所有 Agent 相关开源资源，全部免费开源。

---

## 🏷️ 技术栈总览

| 技术                        | 涉及项目                                                                                       |
|-----------------------------|----------------------------------------------------------------------------------------------|
| **LangChain**               | LangChain_V1_Test, PromptLangChainTest, RagLangChainTest                                     |
| **LangGraph**               | LangGraphChatBot, LangChain_V1_Test                                                          |
| **CrewAI**                  | CrewAITest, CrewAIToolsTest, CrewAIKnowledgeTest, CrewAIFullstackTest, CrewAIFlowsFullStack  |
| **AutoGen**                 | AutoGenTest, AutoGenV04Test                                                                  |
| **MetaGPT**                 | MetaGPTTest                                                                                  |
| **Swarm / OpenAI Agents SDK** | SwarmTest, OpenAIAgentsSDKTest                                                             |
| **MCP**                     | MCPTest, MCPServerTest                                                                       |
| **FastAPI**                 | CrewAITest, CrewAIFlowsFullStack, LangGraphChatBot, PromptLangChainTest                      |
| **RAG**                     | RagLangChainTest, LangChain_V1_Test                                                          |
| **向量数据库**              | RagLangChainTest                                                                             |

---

> 📅 克隆日期：2026-06-28
>
> 所有仓库版权归原作者 [NanGePlus](https://github.com/NanGePlus) 所有。本合集仅供学习参考。
