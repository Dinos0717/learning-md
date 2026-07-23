# 📂 learning-md 文件系统规划

> 基于「资深程序员知识体系全景图」六大支柱设计 | 2026-07-19

---

## 🎯 设计原则

1. **二层深度** — 大类 + 子类，最多三层，再深就没法日常用了
2. **与框架对齐** — 目录名直译框架编号，一眼能对上
3. **兼容现有内容** — 不破坏已有的 AGENT/ GITHUB/ example/，平滑迁移
4. **留白优先** — 现在空的目录没关系，框架需要生长空间

---

## 📁 完整目录树

```
learning-md/
│
├── README.md                          ← 总索引（更新为框架六大支柱版）
├── FILE-SYSTEM-PLAN.md                ← 你在这里
│
├── 00-math/                           ← 📐 2.0 数学基础
│   ├── linear-algebra/                ← 线性代数
│   ├── probability-statistics/        ← 概率论与统计
│   ├── calculus/                      ← 微积分
│   └── discrete-math/                 ← 离散数学
│
├── 01-industry/                       ← 🏭 一、行业认知
│   ├── tech-trends/                   ← 技术趋势判断
│   ├── business-models/               ← 商业模式与成本
│   └── compliance-security/           ← 合规与安全
│
├── 02-backend/                        ← 2.1 后端工程
│   ├── distributed-systems/           ← 分布式系统
│   ├── databases/                     ← 数据库
│   └── high-concurrency/              ← 高并发
│
├── 03-frontend/                       ← 2.2 前端工程
│   ├── rendering-performance/         ← 渲染性能
│   ├── state-management/              ← 状态管理
│   └── web-standards/                 ← Web 标准
│
├── 04-data/                           ← 2.3 数据工程
│   ├── batch-processing/              ← 批处理
│   ├── stream-processing/             ← 流处理
│   └── data-warehouse/                ← 数据仓库
│
├── 05-ai-agent/                       ← 🤖 2.4 AI / Agent  ★ 现有 AGENT/ 迁移至此
│   ├── prompt-engineering/            ← 提示工程
│   ├── rag/                           ← RAG 检索增强生成
│   ├── agent-frameworks/              ← Agent 框架 (LangChain/CrewAI/AutoGen)
│   ├── model-finetuning/              ← 模型微调 (LoRA/QLoRA)
│   ├── model-deployment/              ← 模型部署 (vLLM/Ollama)
│   ├── mcp-protocol/                  ← MCP 协议
│   └── courses/                       ← 课程笔记
│       ├── agent-architect-01/        ← Agent架构师第一期
│       ├── agent-architect-02/        ← Agent架构师第二期
│       └── llm-fullstack-08/          ← AI大模型全栈第八期
│
├── 06-embedded/                       ← 🔌 2.5 嵌入式系统
│   ├── mcu/                           ← MCU 开发 (STM32/ESP32)
│   ├── rtos/                          ← RTOS (FreeRTOS/Zephyr)
│   └── linux-embedded/                ← Linux 嵌入式
│
├── 07-robotics/                       ← 🤖 2.6 机器人工程
│   ├── perception/                    ← 感知 (SLAM/CV)
│   ├── planning/                      ← 规划 (A*/RRT)
│   ├── control/                       ← 控制 (PID/MPC)
│   └── ros/                           ← ROS 2
│
├── 08-design/                         ← 🎨 2.7 设计工具
│   ├── figma/                         ← UI 设计
│   └── blender/                       ← 3D 建模
│
├── 09-gamedev/                        ← 🎮 2.8 游戏开发
│   ├── game-engines/                  ← 游戏引擎 (Unity/Unreal/Godot)
│   ├── rendering/                     ← 渲染 (Shader/GPU)
│   ├── physics/                       ← 物理模拟
│   └── networking/                    ← 网络同步
│
├── 10-aerospace/                      ← 🚀 2.9 航天工程
│   ├── orbital-mechanics/             ← 轨道力学
│   ├── gnc/                           ← 制导导航控制
│   └── flight-software/               ← 飞行软件
│
├── 11-languages/                      ← 3.1 编程语言
│   ├── python/                        ← Python
│   ├── go/                            ← Go
│   ├── rust/                          ← Rust
│   ├── typescript/                    ← TypeScript
│   └── cpp/                           ← C/C++
│
├── 12-network/                        ← 🔗 3.2 网络协议
│   ├── tcp-udp-quic/                  ← TCP/UDP/QUIC
│   ├── tls-https/                     ← TLS/HTTPS
│   ├── dns/                           ← DNS
│   └── vpn/                           ← ★ VPN 专题（隧道/代理/GFW对抗）
│
├── 13-infra/                          ← 3.3 基础设施
│   ├── docker/                        ← Docker
│   ├── kubernetes/                    ← Kubernetes
│   ├── terraform/                     ← IaC
│   └── observability/                 ← 可观测性
│
├── 14-architecture/                   ← 4.1 架构设计
│   ├── patterns/                      ← 架构模式
│   ├── design-principles/             ← 设计原则
│   └── system-design/                 ← 系统设计面试
│
├── 15-quality/                        ← 4.2 质量保障
│   ├── testing/                       ← 测试
│   ├── performance/                   ← 性能优化
│   └── code-review/                   ← 代码审查
│
├── 16-devops/                         ← 4.3 DevOps
│   ├── ci-cd/                         ← CI/CD
│   ├── sre/                           ← SRE
│   └── incident-management/           ← 事故管理
│
├── 17-github/                         ← 🐙 4.4 GitHub 协作  ★ 现有 GITHUB/ 保留
│   ├── git-basics/                    ← Git 基础
│   ├── github-workflow/               ← 工作流
│   └── github-actions/                ← Actions
│
├── 18-soft-skills/                    ← 🤝 五、软技能
│   ├── technical-writing/             ← 技术写作
│   ├── communication/                 ← 沟通协作
│   └── career/                        ← 职业发展
│
├── 19-projects/                       ← 💼 六、实战经验  ★ 现有 example/ 迁移至此
│   ├── my-projects/                   ← 自己的项目
│   └── open-source/                   ← 开源项目代码（现有 NanGePlus 系列）
│
├── config-file/                       ← ★ 保留，配置文件参考
│
└── .claude/                           ← Claude Code 配置（不变）
```

---

## 🔄 现有内容迁移映射

| 现有路径 | → | 新路径 | 说明 |
|----------|---|--------|------|
| `AGENT/langchain/` | → | `05-ai-agent/agent-frameworks/langchain/` | LangChain 系列 38 篇 |
| `AGENT/AI大模型全栈工程师培养计划第八期/` | → | `05-ai-agent/courses/llm-fullstack-08/` | 课程笔记 |
| `AGENT/Agent架构师企业级智能体系统构建第一期/` | → | `05-ai-agent/courses/agent-architect-01/` | 课程笔记 |
| `AGENT/Agent架构师企业级智能体系统构建第二期/` | → | `05-ai-agent/courses/agent-architect-02/` | 课程笔记 |
| `AGENT/AGENT-ENGINEERING.md` | → | `05-ai-agent/AGENT-ENGINEERING.md` | Agent 工程总览 |
| `GITHUB/` (全部) | → | `17-github/` | Git/GitHub 教程 16 篇 |
| `example/NanGePlus/` | → | `19-projects/open-source/NanGePlus/` | 开源项目代码 |
| `config-file/` | → | `config-file/` (保留) | 配置文件参考 |
| `README.md` | → | `README.md` (重写) | 更新为框架版索引 |

---

## 📐 编号体系

```
编号规则：{支柱序号}-{子领域序号}

00  = 数学基础（前置知识）
01  = 行业认知
02  = 后端      ┐
03  = 前端      │
04  = 数据      │
05  = AI/Agent  ├─ 领域专精（02-10）
06  = 嵌入式     │
07  = 机器人     │
08  = 设计      │
09  = 游戏      │
10  = 航天      ┘
11  = 编程语言   ┐
12  = 网络协议   ├─ 技术栈（11-13）
13  = 基础设施   ┘
14  = 架构设计   ┐
15  = 质量保障   ├─ 工程能力（14-17）
16  = DevOps    │
17  = GitHub    ┘
18  = 软技能
19  = 实战项目
```

---

## 🚀 迁移步骤（建议）

```
Phase 1 — 建骨架（5 min）
  mkdir -p 各个空目录，但不移动任何现有内容

Phase 2 — 移内容（10 min）
  把 AGENT/ → 05-ai-agent/
  把 GITHUB/ → 17-github/
  把 example/ → 19-projects/open-source/

Phase 3 — 写索引（15 min）
  重写 README.md，按六大支柱分类展示
  每个目录下加一个 .gitkeep 或小的 README

Phase 4 — 日常填充
  学到新东西 → 放进对应目录
  空目录 → 激励自己拓展新领域
```

---

## 💡 日常使用约定

| 约定 | 说明 |
|------|------|
| **一个知识点一个 .md** | 不要一个文件塞 10 个主题 |
| **目录下放 README.md** | 该领域的知识图谱和学习进度 |
| **用序号前缀** | `01-xxx.md` `02-xxx.md` 保证阅读顺序 |
| **空目录留 .gitkeep** | 标记"计划学习但还没开始" |
| **projects/ 只放代码** | 不放文档，文档归入对应领域目录 |
