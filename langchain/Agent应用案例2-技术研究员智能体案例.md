# Agent 应用案例 2——技术研究员智能体案例

> 基于陈泽鹏老师视频课程整理编写 · 2026年6月27日

---

## 目录

- [一、案例概述与学习目标](#一案例概述与学习目标)
- [二、业务场景——技术趋势研究员](#二业务场景技术趋势研究员)
- [三、项目结构](#三项目结构)
- [四、Agent 与 Task 的 YAML 配置](#四agent-与-task-的-yaml-配置)
  - [4.1 研究员 Agent](#41-研究员-agent)
  - [4.2 报告撰写 Agent](#42-报告撰写-agent)
  - [4.3 研究任务](#43-研究任务)
  - [4.4 报告撰写任务](#44-报告撰写任务)
- [五、自定义工具——Text to PDF](#五自定义工具text-to-pdf)
  - [5.1 工具实现](#51-工具实现)
  - [5.2 工具描述的重要性](#52-工具描述的重要性)
- [六、Crew 封装类——核心执行逻辑](#六crew-封装类核心执行逻辑)
- [七、FastAPI 服务——对外暴露接口](#七fastapi-服务对外暴露接口)
- [八、API 测试客户端](#八api-测试客户端)
- [九、本案例相比案例 1 的三大改进](#九本案例相比案例-1-的三大改进)
  - [9.1 改进一：使用 LangChain ChatOpenAI 定义模型](#91-改进一使用-langchain-chatopenai-定义模型)
  - [9.2 改进二：模型通过参数传入 Crew 类](#92-改进二模型通过参数传入-crew-类)
  - [9.3 改进三：集成自定义外部工具](#93-改进三集成自定义外部工具)
- [十、执行流程演示](#十执行流程演示)
- [十一、模型效果对比](#十一模型效果对比)
- [十二、完整代码清单](#十二完整代码清单)
- [十三、课后练习](#十三课后练习)
- [十四、课程小结](#十四课程小结)

---

## 一、案例概述与学习目标

### 1.1 本案例简介

> 本案例实现一个**技术研究员智能体**——你输入一个技术领域（如"人工智能"），两个 Agent 协作研究该领域的最新技术趋势，分析其优缺点和潜在影响，最终调用外部工具将报告保存为 **PDF 文件**到本地。

```
┌─────────────────────────────────────────────────────────┐
│          本案例 vs 案例 1 的区别                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  案例 1（基础）：                                        │
│  ├── 研究员 + 报告分析师                                 │
│  ├── 输出 Markdown 文件                                  │
│  └── 使用环境变量配置模型                                │
│                                                         │
│  案例 2（本案例）：                                      │
│  ├── 高级技术研究员 + 专业技术作家                       │
│  ├── 调用外部工具 → 输出 PDF 文件                        │
│  ├── 使用 LangChain ChatOpenAI 定义模型（更灵活）        │
│  └── 模型通过参数传入 Crew 类（可分配不同模型）          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 1.2 本课要掌握的目标

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  目标一：掌握使用 LangChain ChatOpenAI 灵活定义模型       │
│         ├── 不依赖环境变量，代码中直接配置               │
│         └── 可以调整 temperature 等参数控制输出效果      │
│                                                         │
│  目标二：掌握自定义 CrewAI 外部工具的方法                 │
│         ├── @tool 装饰器 + BaseTool 基类                 │
│         └── 工具描述对 Agent 行为的关键影响              │
│                                                         │
│  目标三：掌握模型通过参数传递给 Crew 的模式               │
│         ├── 不同 Agent 可以使用不同模型                  │
│         └── 构造函数注入模式                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 二、业务场景——技术趋势研究员

```
用户输入：一个技术领域名称（例如"人工智能"）

        │
        ▼
┌──────────────────────────────┐
│  Agent 1: 高级技术研究员      │
│  角色：领域专家               │
│  任务：研究该领域的最新技术趋势 │
│  产出：5 个要点清单           │
│  ├── 当前趋势                 │
│  ├── 技术利弊                 │
│  └── 潜在影响                 │
└──────────────┬───────────────┘
               │ 上下文传递
               ▼
┌──────────────────────────────┐
│  Agent 2: 专业技术作家        │
│  角色：技术文档撰写专家       │
│  任务：根据研究结果撰写报告    │
│  产出：结构化 PDF 报告         │
│  ├── 引言                     │
│  ├── 当前趋势                 │
│  ├── 技术利弊                 │
│  ├── 潜在影响                 │
│  └── 结论                     │
└──────────────┬───────────────┘
               │ 调用外部工具
               ▼
┌──────────────────────────────┐
│  外部工具: text_to_pdf        │
│  将报告内容 → PDF 文件         │
│  保存到本地磁盘               │
└──────────────────────────────┘
```

---

## 三、项目结构

```
tech-researcher-crew/
├── main.py                      # FastAPI 服务主入口
├── api_test.py                  # API 测试客户端
├── config/
│   ├── agents.yaml              # Agent 角色/目标/背景 配置
│   └── tasks.yaml               # Task 描述/输出/分配 配置
├── crew_runner.py               # Crew 封装类（核心执行逻辑）
├── custom/
│   └── text_to_pdf_tool.py      # 自定义工具：报告→PDF
├── fonts/
│   └── SimHei.ttf               # 中文字体文件（防乱码）
└── output/                      # PDF 输出目录
    └── .gitkeep
```

---

## 四、Agent 与 Task 的 YAML 配置

### 4.1 研究员 Agent

```yaml
# ── config/agents.yaml ──

tech_researcher:
  role: "高级技术研究员"
  goal: "研究 {topic} 领域或行业的最新技术趋势并进行深入分析"
  backstory: >
    你是该领域的资深专家，擅长探索技术前沿动态，
    深入挖掘技术发展趋势。你能够以敏锐的洞察力
    撰写全面报告，确保分析具有深度和专业性。
  verbose: true
  allow_delegation: false

tech_writer:
  role: "专业技术作家"
  goal: "根据研究结果撰写专业、清晰的技术趋势报告"
  backstory: >
    你是一名擅长专业技术的作家，能够将复杂的技术概念
    用简单易懂的语言解释清楚，同时确保报告具有深度和
    可读性。你撰写的研究报告适合行业读者阅读。
  verbose: true
  allow_delegation: false
```

### 4.2 报告撰写 Agent

> 两个 Agent 的分工非常明确：研究员负责"找信息、做分析"，作家负责"写成文、可阅读"。这种角色分工让每个 Agent 专注自己的强项。

### 4.3 研究任务

```yaml
# ── config/tasks.yaml ──

research_task:
  description: >
    研究 {topic} 行业或领域的最新技术趋势。
    请关注最新的技术进展，评估它们的优缺点，并提供详细的分析。
    
    研究内容请至少包括以下三个方面的内容：
    1. 当前技术趋势概述
    2. 技术的利与弊分析
    3. 潜在的影响展望
    
    最终给出 5 个核心要点。
  
  expected_output: >
    一份包含 5 个核心要点的清单，介绍 {topic} 领域的
    技术前沿动态和最新技术发展趋势，每个要点附带简要说明。
  
  agent: tech_researcher
```

### 4.4 报告撰写任务

```yaml
report_task:
  description: >
    根据研究任务获得的最新技术内容，撰写一份关于 {topic}
    技术趋势的专业报告。
    
    报告要求：
    1. 结构清晰，包含引言、分析、结论
    2. 内容有洞察力，阐述技术的影响
    3. 语言专业但通俗易懂，适合行业读者阅读
    4. 最终调用可用的工具将报告保存为文件
  
  expected_output: >
    一份详细的专业报告，解释 {topic} 的技术趋势及其影响，
    适合行业读者阅读。
  
  agent: tech_writer
  
  context:
    - research_task    # 引用研究任务的输出作为上下文
```

---

## 五、自定义工具——Text to PDF

### 5.1 工具实现

> 本案例的关键创新：Agent 不只是"说"出报告内容，还能调用外部工具把报告**保存为 PDF 文件**。

```python
# ── custom/text_to_pdf_tool.py ──

from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
import os
from datetime import datetime


class TextToPDFInput(BaseModel):
    """工具的输入参数定义"""
    content: str = Field(
        description="要保存为 PDF 的报告文本内容"
    )
    filename: Optional[str] = Field(
        default=None,
        description="输出文件名（不含后缀），默认自动生成"
    )


class TextToPDFTool(BaseTool):
    """
    将文本内容保存为 PDF 文件的工具
    
    这是 CrewAI 自定义工具的标准写法：
    1. 继承 BaseTool
    2. 定义 name 和 description
    3. 定义 args_schema（输入参数）
    4. 实现 _run 方法
    
    ⚠️ 工具的 description 极其重要！
    它是 Agent 决定"什么时候用这个工具"的唯一依据。
    """
    
    name: str = "text_to_pdf"
    
    description: str = (
        "将给定的文本内容保存为 PDF 文件到本地磁盘。"
        "当你需要保存任务输出的报告、文档或任何文本内容时，"
        "使用此工具。"
        "参数：content（要保存的文本内容，必填）、"
        "filename（文件名不含后缀，选填，默认使用时间戳）"
    )
    
    args_schema: Type[BaseModel] = TextToPDFInput
    
    # ── 输出目录 ──
    output_dir: str = "output"
    
    def _run(
        self,
        content: str,
        filename: Optional[str] = None
    ) -> str:
        """
        执行：将文本内容保存为 PDF
        
        Args:
            content: 要保存的报告文本
            filename: 文件名（不含.pdf后缀），默认自动生成
        
        Returns:
            str: 保存成功的消息
        """
        try:
            # ── 确保输出目录存在 ──
            os.makedirs(self.output_dir, exist_ok=True)
            
            # ── 生成文件名 ──
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"tech_report_{timestamp}"
            
            filepath = os.path.join(self.output_dir, f"{filename}.pdf")
            
            # ── 写入 PDF ──
            self._write_pdf(content, filepath)
            
            return f"✅ 报告已成功保存到: {filepath}"
        
        except Exception as e:
            return f"❌ 保存 PDF 失败: {str(e)}"
    
    def _write_pdf(self, content: str, filepath: str):
        """
        将文本内容写入 PDF 文件
        
        使用 reportlab 或 fpdf 库生成 PDF
        - 支持中文（需要中文字体文件）
        - 自动分页
        """
        from fpdf import FPDF
        
        pdf = FPDF()
        pdf.add_page()
        
        # ── 设置中文字体 ──
        # 关键！不使用中文字体会导致乱码
        font_path = os.path.join("fonts", "SimHei.ttf")
        if os.path.exists(font_path):
            pdf.add_font("SimHei", "", font_path, uni=True)
            pdf.set_font("SimHei", "", 12)
        else:
            pdf.set_font("Helvetica", "", 12)
        
        # ── 写入标题 ──
        pdf.set_font_size(18)
        pdf.cell(0, 10, "技术趋势研究报告", ln=True, align="C")
        pdf.ln(10)
        
        # ── 写入正文 ──
        pdf.set_font_size(12)
        # 处理多字节字符的换行
        for line in content.split("\n"):
            # 清理不可编码字符
            safe_line = line.encode("latin-1", "replace").decode("latin-1")
            pdf.multi_cell(0, 8, safe_line)
            pdf.ln(2)
        
        # ── 保存文件 ──
        pdf.output(filepath)
```

### 5.2 工具描述的重要性

```
┌─────────────────────────────────────────────────────────┐
│  ⚠️ 工具的描述（description）是 Agent 找到工具的关键！    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Agent 在执行任务时，会阅读所有可用工具的 description     │
│  来判断"我该用哪个工具？"                                │
│                                                         │
│  好的 description：                                      │
│  "当你需要保存任务输出的报告、文档或任何文本内容时，     │
│   使用此工具。"                                          │
│  → 明确告诉 Agent 什么场景用这个工具 ✅                   │
│                                                         │
│  不好的 description：                                    │
│  "保存文件。"                                            │
│  → 太模糊，Agent 不知道什么时候该用它 ❌                  │
│                                                         │
│  写好描述 = Agent 能准确调用工具                         │
│  描述写差 = Agent 不知道有这个工具，永远不会用           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 六、Crew 封装类——核心执行逻辑

> 本案例的 Crew 封装类相比案例 1 做了两个重要改进：**通过参数接收模型**和**集成外部工具**。

```python
# ── crew_runner.py ──

import yaml
from typing import Optional, Any
from crewai import Agent, Task, Crew, Process
from custom.text_to_pdf_tool import TextToPDFTool


class TechResearcherCrew:
    """
    技术研究员 Crew 封装类
    
    改进点：
    1. 通过构造函数接收 LLM 模型（而非从环境变量读取）
    2. 集成外部工具 text_to_pdf
    3. 不同 Agent 可以分配不同模型
    
    使用方式：
        llm = ChatOpenAI(model="gpt-4o-mini", ...)
        crew = TechResearcherCrew(llm=llm)
        result = crew.run(topic="人工智能")
    """
    
    def __init__(
        self,
        llm: Any = None,
        verbose: bool = True
    ):
        """
        初始化 Crew
        
        Args:
            llm: LangChain ChatOpenAI 实例（或其他兼容 LLM）
                 如果不传，CrewAI 会使用默认环境变量
            verbose: 是否输出详细执行日志
        """
        self.llm = llm
        self.verbose = verbose
        
        # ── 加载 YAML 配置 ──
        self.agents_config = self._load_yaml("config/agents.yaml")
        self.tasks_config = self._load_yaml("config/tasks.yaml")
        
        # ── 创建 Agent ──
        self.researcher = self._create_agent("tech_researcher")
        self.writer = self._create_agent("tech_writer")
    
    def _load_yaml(self, filepath: str) -> dict:
        """加载 YAML 配置文件"""
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def _create_agent(self, agent_key: str) -> Agent:
        """
        创建 Agent
        
        关键改进：把 llm 传入 Agent
        如果不传 llm，CrewAI 会使用默认环境变量
        """
        config = self.agents_config[agent_key]
        
        # ── 构建 Agent 参数 ──
        agent_params = {
            "role": config["role"],
            "goal": config["goal"],
            "backstory": config["backstory"],
            "verbose": config.get("verbose", True),
            "allow_delegation": config.get("allow_delegation", False),
        }
        
        # ═══ 关键改进：把 LLM 模型传给 Agent ═══
        if self.llm is not None:
            agent_params["llm"] = self.llm
        
        return Agent(**agent_params)
    
    def run(self, topic: str) -> str:
        """
        执行技术趋势研究
        
        Args:
            topic: 要研究的技术领域（如"人工智能"、"区块链"）
        
        Returns:
            str: 最终的报告内容
        """
        # ── 创建自定义工具实例 ──
        pdf_tool = TextToPDFTool()
        
        # ── 创建研究任务 ──
        research_task = Task(
            description=self.tasks_config["research_task"]["description"].format(
                topic=topic
            ),
            expected_output=self.tasks_config["research_task"]["expected_output"].format(
                topic=topic
            ),
            agent=self.researcher
        )
        
        # ── 创建报告撰写任务（绑定 PDF 工具）──
        report_task = Task(
            description=self.tasks_config["report_task"]["description"].format(
                topic=topic
            ),
            expected_output=self.tasks_config["report_task"]["expected_output"].format(
                topic=topic
            ),
            agent=self.writer,
            tools=[pdf_tool],           # ═══ 关键：工具绑定给这个 Task ═══
            context=[research_task]      # 引用研究结果
        )
        
        # ── 创建 Crew 并执行 ──
        crew = Crew(
            agents=[self.researcher, self.writer],
            tasks=[research_task, report_task],
            process=Process.sequential,
            verbose=self.verbose
        )
        
        result = crew.kickoff()
        return str(result)
```

---

## 七、FastAPI 服务——对外暴露接口

```python
# ── main.py ──

import uvicorn
import argparse
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

# ══════════════════════════════════════════════════════
# LangChain ChatOpenAI —— 灵活定义模型
# ══════════════════════════════════════════════════════

from langchain_openai import ChatOpenAI
from crew_runner import TechResearcherCrew

# ══════════════════════════════════════════════════════
# 全局配置
# ══════════════════════════════════════════════════════

# ── 大模型配置（三选一）──

# 方案一：GPT 代理
GPT_CONFIG = {
    "model": "gpt-4o-mini",
    "base_url": "https://your-proxy-url/v1",
    "api_key": "sk-your-api-key",
    "temperature": 0.7,      # 可以调整温度参数！
}

# 方案二：OneAPI（千问）
ONAPI_CONFIG = {
    "model": "qwen-max",
    "base_url": "http://localhost:3000/v1",
    "api_key": "sk-your-oneapi-token",
    "temperature": 0.7,
}

# 方案三：Ollama 本地
OLLAMA_CONFIG = {
    "model": "llama3.1:8b",
    "base_url": "http://localhost:11434/v1",
    "api_key": "ollama",
    "temperature": 0.7,
}

# ══════════════════════════════════════════════════════
# 选择当前使用的模型
# ══════════════════════════════════════════════════════

MODEL_TYPE = "openai"      # 可选: "openai" / "oneapi" / "ollama"
SERVICE_PORT = 8028

if MODEL_TYPE == "openai":
    ACTIVE_CONFIG = GPT_CONFIG
elif MODEL_TYPE == "oneapi":
    ACTIVE_CONFIG = ONAPI_CONFIG
else:
    ACTIVE_CONFIG = OLLAMA_CONFIG

# ══════════════════════════════════════════════════════
# FastAPI 应用
# ══════════════════════════════════════════════════════

app = FastAPI(
    title="技术研究员智能体服务",
    description="使用 CrewAI 构建的技术趋势研究多 Agent 协作服务",
    version="2.0.0"
)

# 全局模型和 Crew 实例
llm: Optional[ChatOpenAI] = None
tech_crew: Optional[TechResearcherCrew] = None


class ResearchRequest(BaseModel):
    """研究请求"""
    topic: str = Field(
        default="人工智能",
        description="要研究的技术领域或行业"
    )


class ResearchResponse(BaseModel):
    """研究响应"""
    success: bool
    topic: str
    report: str


@app.on_event("startup")
async def startup():
    """
    服务启动初始化
    
    关键改进：使用 LangChain ChatOpenAI 定义模型
    - 不依赖环境变量
    - 可以自由调整 temperature 等参数
    - 模型参数完全可控
    """
    global llm, tech_crew
    
    print("🤖 初始化大模型...")
    
    # ═══ 使用 LangChain ChatOpenAI 创建模型 ═══
    llm = ChatOpenAI(
        model=ACTIVE_CONFIG["model"],
        base_url=ACTIVE_CONFIG["base_url"],
        api_key=ACTIVE_CONFIG["api_key"],
        temperature=ACTIVE_CONFIG["temperature"],  # 可调参数！
    )
    
    print(f"   模型: {ACTIVE_CONFIG['model']}")
    print(f"   地址: {ACTIVE_CONFIG['base_url']}")
    print(f"   温度: {ACTIVE_CONFIG['temperature']}")
    
    # ═══ 把模型传给 Crew ═══
    tech_crew = TechResearcherCrew(llm=llm, verbose=True)
    
    print(f"✅ 技术研究员智能体服务已就绪")
    print(f"📡 端口: {SERVICE_PORT}")


@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """
    技术趋势研究接口
    
    接收一个技术领域，两个 Agent 协作完成研究并生成 PDF 报告
    """
    if tech_crew is None:
        raise HTTPException(status_code=503, detail="服务未就绪")
    
    try:
        report = tech_crew.run(topic=request.topic)
        
        return ResearchResponse(
            success=True,
            topic=request.topic,
            report=report
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"研究过程出错: {str(e)}"
        )


@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "model": ACTIVE_CONFIG["model"],
        "crew_ready": tech_crew is not None
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
```

---

## 八、API 测试客户端

```python
# ── api_test.py ──

import requests
import json


def test_research(topic: str = "人工智能"):
    """
    测试技术研究员 API
    
    Args:
        topic: 要研究的技术领域
    """
    url = "http://localhost:8028/research"
    
    payload = {
        "topic": topic
    }
    
    print(f"🚀 研究主题：{topic}")
    print(f"📡 请求地址：{url}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=payload, timeout=300)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 研究完成！")
            print(f"\n{'='*50}")
            print(f"📄 技术趋势研究报告：")
            print(f"{'='*50}")
            print(data["report"])
            print(f"\n{'='*50}")
            print(f"💾 PDF 报告已保存到 output/ 目录")
        else:
            print(f"❌ 请求失败：{response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ 连接失败: {e}")


if __name__ == "__main__":
    # ── 测试 ──
    test_research("人工智能")
    
    # ── 测试其他领域 ──
    # test_research("区块链")
    # test_research("量子计算")
    # test_research("新能源汽车")
```

---

## 九、本案例相比案例 1 的三大改进

### 9.1 改进一：使用 LangChain ChatOpenAI 定义模型

```
案例 1 的方式（环境变量）：
┌─────────────────────────────────────────────────────────┐
│  os.environ["OPENAI_API_BASE"] = "..."                  │
│  os.environ["OPENAI_API_KEY"] = "..."                   │
│  → 依赖全局环境变量，不灵活                              │
│  → 无法调整 temperature 等细粒度参数                    │
└─────────────────────────────────────────────────────────┘

案例 2 的方式（LangChain ChatOpenAI）：
┌─────────────────────────────────────────────────────────┐
│  llm = ChatOpenAI(                                      │
│      model="gpt-4o-mini",                               │
│      base_url="...",                                    │
│      api_key="...",                                     │
│      temperature=0.7    ← 可以调整！                    │
│  )                                                      │
│  → 代码中直接配置，灵活可控                              │
│  → temperature 等参数自由调整                            │
│  → 可以同时创建多个不同配置的模型                        │
└─────────────────────────────────────────────────────────┘
```

### 9.2 改进二：模型通过参数传入 Crew 类

```python
# ── 案例 1：Crew 自己从环境变量读模型 ──
class TopicResearchCrew:
    def __init__(self):
        # Agent 创建时不传 llm → CrewAI 从环境变量读
        self.agent = Agent(role="...", goal="...")

# ── 案例 2：模型从外部传入 ──
class TechResearcherCrew:
    def __init__(self, llm=None):   # ← 接收外部模型
        self.llm = llm
    
    def _create_agent(self, key):
        params = {...}
        if self.llm is not None:
            params["llm"] = self.llm  # ← 显式传入
        return Agent(**params)
```

```
这种改进的好处：

1️⃣  不同 Agent 可以用不同模型
    researcher = Agent(llm=gpt4, ...)   # 研究员用 GPT-4
    writer = Agent(llm=gpt4o_mini, ...)  # 写手用便宜的 GPT-4o-mini
    
2️⃣  方便切换模型做对比测试
    传入 ChatOpenAI(model="gpt-4o-mini") → 测试 GPT
    传入 ChatOpenAI(model="qwen-max")    → 测试千问
    代码逻辑零改动！

3️⃣  解耦模型配置和业务逻辑
    模型配置集中在 main.py
    Crew 类只关心业务
```

### 9.3 改进三：集成自定义外部工具

```
案例 1：没有自定义工具
    Task 只做文本生成，输出存为 Markdown 文件

案例 2：集成 text_to_pdf 工具
    Agent 可以调用工具把报告保存为 PDF
    
    工具集成方式：
    ┌─────────────────────────────────────────────┐
    │  # 创建工具                                  │
    │  pdf_tool = TextToPDFTool()                 │
    │                                             │
    │  # 绑定到 Task（也可以绑定到 Agent）          │
    │  report_task = Task(                        │
    │      ...,                                   │
    │      tools=[pdf_tool]  ← 这个任务可以用它   │
    │  )                                          │
    └─────────────────────────────────────────────┘

工具分配的两种方式：
├── 绑定给 Agent → 该 Agent 的所有 Task 都能用
└── 绑定给 Task → 只有这个 Task 能用
```

---

## 十、执行流程演示

```
启动服务 → 发送请求 → 观察执行过程

$ python main.py

🤖 初始化大模型...
   模型: gpt-4o-mini
   地址: https://your-proxy-url/v1
   温度: 0.7
✅ 技术研究员智能体服务已就绪
📡 端口: 8028

────────────────────────────────────────────────

$ python api_test.py

🚀 研究主题：人工智能
📡 请求地址：http://localhost:8028/research

═══════════════════════════════════════════════
Agent 1: 高级技术研究员 开始工作
═══════════════════════════════════════════════

任务：研究人工智能的最新技术趋势
→ 分析当前趋势...
→ 评估技术利弊...
→ 展望潜在影响...
→ 输出 5 个核心要点 ✅

═══════════════════════════════════════════════
Agent 2: 专业技术作家 开始工作
═══════════════════════════════════════════════

任务：根据研究结果撰写专业报告
→ 组织报告结构...
→ 撰写各章节内容...
→ 调用 text_to_pdf 工具保存报告...
→ ✅ 报告已保存到: output/tech_report_20260627_215000.pdf

✅ 研究完成！
```

---

## 十一、模型效果对比

| 维度 | **GPT-4o-mini** | **千问 Max** | **Llama 3.1 8B** |
|---|---|---|---|
| **速度** | ⚡ 快 | 🐢 较慢 | 🐢 慢（依赖硬件） |
| **推理质量** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **报告完整性** | ✅ 5 点完整 | ⚠️ 有时不完整 | ❌ 不满足要求 |
| **PDF 输出** | ✅ 正常 | ✅ 正常 | ⚠️ 中文可能乱码 |
| **推荐场景** | 生产环境首选 | 备选 | 不建议（需更大参数） |

> 💡 **结论**：GPT-4o-mini 在本案例中表现最佳。千问 Max 推理速度和完整性稍逊。本地 Llama 3.1 8B 参数太小，无法胜任这种需要深度推理的任务，建议至少使用 70B 以上参数的本地模型。

---

## 十二、完整代码清单

```
tech-researcher-crew/
├── main.py                      # FastAPI 服务（模型配置 + 路由 + 生命周期）
├── api_test.py                  # API 测试客户端
├── crew_runner.py               # Crew 封装类（LLM 注入 + 工具集成）
├── config/
│   ├── agents.yaml              # 2 个 Agent 定义
│   └── tasks.yaml               # 2 个 Task 定义（含 context 引用）
├── custom/
│   └── text_to_pdf_tool.py      # TextToPDFTool 自定义工具
├── fonts/
│   └── SimHei.ttf               # 中文字体（PDF 防乱码）
└── output/                      # PDF 输出目录
```

```txt
# ── requirements.txt ──
crewai>=0.80.0
crewai-tools>=0.16.0
fastapi>=0.115.0
uvicorn>=0.30.0
langchain-openai>=0.2.0
pyyaml>=6.0
fpdf>=1.7.2
pydantic>=2.0.0
```

---

## 十三、课后练习

### 练习一：基础——跑通技术研究员案例

**题目**：下载源码，配置 GPT-4o-mini（或其他可用模型），成功生成一份 PDF 技术报告。

**要求**：
- 修改 main.py 中的模型配置
- 启动服务，发送 POST 请求
- 验证 output/ 目录中是否生成了 PDF 文件
- 打开 PDF 确认内容完整（5 个要点 + 中文正常显示）

### 练习二：进阶——新增 Excel 导出工具

**题目**：模仿 `TextToPDFTool`，新增一个 `TextToExcelTool`，把研究报告的数据部分导出为 Excel 表格。

**要求**：
- 在 `custom/` 下创建 `text_to_excel_tool.py`
- 继承 `BaseTool`，定义 name、description、args_schema
- 实现 `_run` 方法（使用 openpyxl 或 pandas）
- 在 `crew_runner.py` 中注册新工具
- 修改 Task 的 tools 列表，让 Agent 可以使用

<details>
<summary>参考框架</summary>

```python
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import pandas as pd

class TextToExcelInput(BaseModel):
    content: str = Field(description="报告文本内容")
    filename: str = Field(default="tech_report", description="文件名")

class TextToExcelTool(BaseTool):
    name: str = "text_to_excel"
    description: str = (
        "将报告内容保存为 Excel 文件。"
        "当你需要以表格形式保存数据时使用此工具。"
    )
    args_schema: Type[BaseModel] = TextToExcelInput
    
    def _run(self, content: str, filename: str = "tech_report") -> str:
        df = pd.DataFrame({"报告内容": [content]})
        filepath = f"output/{filename}.xlsx"
        df.to_excel(filepath, index=False)
        return f"✅ Excel 已保存到: {filepath}"
```
</details>

### 练习三：综合实战——分配不同模型给不同 Agent

**题目**：修改代码，让研究员使用 GPT-4o-mini，写手使用更便宜的模型（如 GPT-3.5 或千问），实现"强模型研究 + 弱模型写作"的成本优化策略。

**要求**：
- 创建两个不同的 LLM 实例
- 修改 `crew_runner.py`，支持为每个 Agent 传入不同 llm
- 测试对比：两个 Agent 用同一模型 vs 用不同模型的成本和效果

---

## 十四、课程小结

### 14.1 核心知识图谱

```
┌────────────────────────────────────────────────────────────┐
│        技术研究员智能体案例——核心知识体系                      │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  业务场景                                              │
│      ├── Agent1（研究员）：研究趋势 → 5 个要点              │
│      ├── Agent2（作家）：撰写报告 → 调用工具 → PDF         │
│      └── 顺序执行：研究 → 写作（上下文传递）                │
│                                                            │
│  2️⃣  三大改进（相比案例 1）                                 │
│      ├── 改进1：LangChain ChatOpenAI 定义模型              │
│      │   └── 不依赖环境变量，temperature 可调               │
│      ├── 改进2：模型通过参数传入 Crew 类                    │
│      │   └── 不同 Agent 可用不同模型，解耦配置              │
│      └── 改进3：集成自定义外部工具 TextToPDFTool            │
│          └── @tool + BaseTool + 描述 = Agent 找到工具      │
│                                                            │
│  3️⃣  自定义工具规范                                        │
│      ├── 继承 BaseTool                                     │
│      ├── name + description（决定 Agent 是否找到它）       │
│      ├── args_schema（Pydantic 输入定义）                  │
│      └── _run 方法（实际执行逻辑）                          │
│                                                            │
│  4️⃣  模型效果                                              │
│      ├── GPT-4o-mini：最佳（推荐生产使用）                  │
│      ├── 千问 Max：可用（速度稍慢）                         │
│      └── Llama 8B：不足（需要更大参数模型）                 │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 14.2 一句话总结

> **技术研究员案例在案例 1 的基础上做了三大升级：用 LangChain ChatOpenAI 替代环境变量（更灵活）、用参数注入替代隐式读取（支持不同 Agent 不同模型）、用自定义工具替代纯文本输出（Agent 能生成 PDF 文件）。这让多 Agent 系统从"能跑"进化到"好用"。**

### 14.3 系列课程定位

```
┌─────────────────────────────────────────────────────────┐
│         Agent 应用案例系列                                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  案例 1：CrewAI + FastAPI 基础入门                        │
│         → 官方模板 + FastAPI 封装                         │
│                                                         │
│  案例 2（本课）：技术研究员智能体                          │
│         → 自定义工具 + LLM 注入 + PDF 输出                │
│         ← 你在这里                                       │
│                                                         │
│  后续案例：                                              │
│  ├── 案例 3：多工具复杂编排                               │
│  └── 案例 4：生产部署与企业级方案                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

*本教学文档基于陈泽鹏老师视频课程整理编写 · 2026年6月27日*
