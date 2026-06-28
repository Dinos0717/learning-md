# Agent 应用案例 3（进阶）——健康档案助手智能体案例

> 基于陈泽鹏老师视频课程整理编写 · 2026年6月28日

---

## 目录

- [一、案例概述与学习目标](#一案例概述与学习目标)
- [二、RAG 速览——私有知识库的核心原理](#二rag-速览私有知识库的核心原理)
- [三、业务场景——健康档案助手](#三业务场景健康档案助手)
- [四、项目结构](#四项目结构)
- [五、离线步骤——文档入库](#五离线步骤文档入库)
  - [5.1 文档加载与切分](#51-文档加载与切分)
  - [5.2 Embedding 向量化](#52-embedding-向量化)
  - [5.3 存入 ChromaDB 向量数据库](#53-存入-chromadb-向量数据库)
  - [5.4 离线入库完整代码](#54-离线入库完整代码)
- [六、在线步骤——检索与生成](#六在线步骤检索与生成)
  - [6.1 RAG 检索工具封装](#61-rag-检索工具封装)
  - [6.2 Text-to-PDF 工具](#62-text-to-pdf-工具)
- [七、Agent 与 Task 配置](#七agent-与-task-配置)
- [八、Crew 封装类——工具分配与编排](#八crew-封装类工具分配与编排)
- [九、FastAPI 服务与测试](#九fastapi-服务与测试)
- [十、执行流程演示](#十执行流程演示)
- [十一、工具测试——先测试再集成](#十一工具测试先测试再集成)
- [十二、本案例相比案例 2 的核心突破](#十二本案例相比案例-2-的核心突破)
- [十三、完整代码清单](#十三完整代码清单)
- [十四、课后练习](#十四课后练习)
- [十五、课程小结](#十五课程小结)

---

## 一、案例概述与学习目标

### 1.1 本案例简介

> 本案例实现一个**健康档案助手智能体**——医生询问某个患者的健康问题，一个 Agent 从私有健康档案库中检索相关记录，另一个 Agent 分析数据并生成专业的健康建议报告（PDF）。

```
┌─────────────────────────────────────────────────────────┐
│          本案例 vs 前两个案例的区别                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  案例 1（基础）：CrewAI + FastAPI 入门                    │
│  ├── 研究员 + 分析师，输出 Markdown                       │
│  └── 纯 LLM 知识，无外部数据源                           │
│                                                         │
│  案例 2（进阶）：技术研究员                               │
│  ├── 自定义 Text-to-PDF 工具                             │
│  └── LangChain ChatOpenAI 模型注入                       │
│                                                         │
│  案例 3（本案例）：健康档案助手 ← 核心突破！               │
│  ├── 🆕 RAG 私有知识库集成（ChromaDB 向量数据库）         │
│  ├── 🆕 离线入库 + 在线检索 完整流程                      │
│  ├── 🆕 工具独立测试体系（unit test 文件夹）              │
│  └── Agent 能检索你自己文档里的内容！                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 1.2 本课要掌握的目标

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  目标一：理解 RAG 的两阶段流程                             │
│         ├── 离线阶段：文档→切片→向量化→入库              │
│         └── 在线阶段：问题→向量化→检索→Prompt→LLM→答案  │
│                                                         │
│  目标二：掌握 CrewAI 集成私有知识库的方法                  │
│         ├── 自定义 RAG 检索工具封装                       │
│         ├── ChromaDB 向量数据库集成                       │
│         └── 工具分配给特定 Agent 的策略                   │
│                                                         │
│  目标三：建立"先测试工具，再集成 Agent"的工作流            │
│         ├── unit test 文件夹：独立测试每个工具            │
│         └── 工具验证通过后再注册到 CrewAgent              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 二、RAG 速览——私有知识库的核心原理

### 2.1 什么是 RAG

> **RAG（Retrieval-Augmented Generation，检索增强生成）** 是让 LLM 能够回答"知识库中有但训练数据中不一定有"的问题的核心技术。

```
没有 RAG 的 LLM：
用户："张三最近头疼与之前的体检记录有关吗？"
LLM："抱歉，我没有张三的体检记录。" 😰

有 RAG 的 LLM：
用户："张三最近头疼与之前的体检记录有关吗？"
RAG 系统：先检索张三的健康档案 → 找到血压 135/85、血糖偏高等数据
LLM："根据张三的体检记录，血压 135/85 属轻度高血压，
      可能与头痛有关。建议..." ✅
```

### 2.2 RAG 的两阶段流程

```
┌─────────────────────────────────────────────────────────┐
│          RAG 完整流程                                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ═══════════ 离线阶段（数据入库） ═══════════            │
│                                                         │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────┐ │
│  │ 原始文档  │ → │  文档切分  │ → │ 向量化    │ → │向量DB│ │
│  │ (PDF/TXT)│   │ (Chunking)│   │(Embedding)│   │Chroma│ │
│  └──────────┘   └──────────┘   └──────────┘   └──────┘ │
│                                                         │
│  只需执行一次！（或文档更新时重新执行）                    │
│                                                         │
│  ═══════════ 在线阶段（问答） ═══════════                │
│                                                         │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────┐ │
│  │ 用户问题  │ → │ 向量化    │ → │ 相似检索  │ → │取TopK│ │
│  └──────────┘   └──────────┘   └──────────┘   └──────┘ │
│                                                         │
│  ┌──────────────────────────────────────────┐           │
│  │ 构建 Prompt：                              │           │
│  │ "根据以下资料回答问题：{检索到的文档}       │           │
│  │  问题：{用户问题}"                         │           │
│  └──────────────────────────────────────────┘           │
│         │                                                │
│         ▼                                                │
│  ┌──────────┐                                            │
│  │   LLM    │ → 生成最终答案                              │
│  └──────────┘                                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 三、业务场景——健康档案助手

```
医生询问：
"张三最近的头疼与之前的体检记录是否有关联？"

        │
        ▼
┌──────────────────────────────────┐
│  Agent 1: 健康档案检索专家        │
│  任务：从私有知识库检索张三的       │
│        健康档案相关记录            │
│  工具：RAG 检索工具 → ChromaDB   │
│  产出：张三的体检数据、病史等      │
│  ├── 血压 135/85                 │
│  ├── 心率 78 次/分钟             │
│  ├── 血糖偏高                     │
│  └── 睡眠时间不足                 │
└──────────────┬───────────────────┘
               │ 检索结果传递
               ▼
┌──────────────────────────────────┐
│  Agent 2: 健康报告撰写专家         │
│  任务：分析检索数据 + 医生问题     │
│        撰写专业健康建议报告        │
│  工具：Text-to-PDF 工具           │
│  产出：PDF 健康建议报告            │
│  ├── 头痛原因分析                 │
│  ├── 相关体检指标解读             │
│  ├── 生活方式影响评估             │
│  └── 个性化健康建议               │
└──────────────┬───────────────────┘
               │
               ▼
       📄 张三健康建议报告.pdf
```

---

## 四、项目结构

```
health-archive-crew/
├── main.py                      # FastAPI 服务入口
├── api_test.py                  # API 测试客户端
├── crew_runner.py               # Crew 封装类（编排 + 工具分配）
├── config/
│   ├── agents.yaml              # 2 个 Agent 定义
│   └── tasks.yaml               # 2 个 Task 定义
├── tools/
│   ├── text_to_pdf_tool.py      # 工具1：报告 → PDF 文件
│   └── health_search_tool.py    # 工具2：RAG 健康档案检索
├── unit_test/
│   ├── test_pdf_tool.py         # 测试 PDF 工具
│   └── test_rag_tool.py         # 测试 RAG 检索
├── utils/
│   ├── chinese_chunker.py       # 中文文档切分工具
│   └── english_chunker.py       # 英文文档切分工具
├── input/
│   └── 健康档案.pdf             # 原始健康档案文件
├── fonts/
│   └── SimHei.ttf               # 中文字体（PDF 防乱码）
├── output/                      # PDF 报告输出目录
├── chroma_db/                   # ChromaDB 向量数据库持久化目录
└── build_vectordb.py            # 离线入库脚本
```

---

## 五、离线步骤——文档入库

### 5.1 文档加载与切分

> 这是 RAG 的第一步：把 PDF 文档加载进来，切成一个个文本块（chunk）。

```python
# ── utils/chinese_chunker.py ──

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader


def load_and_split_chinese_pdf(
    pdf_path: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> list:
    """
    加载中文 PDF 并切分为文本块
    
    Args:
        pdf_path: PDF 文件路径
        chunk_size: 每个文本块的最大字符数
        chunk_overlap: 相邻文本块的重叠字符数
    
    Returns:
        list[Document]: 切分后的文档列表
    """
    # Step 1: 加载 PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    # Step 2: 中文文本切分
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    
    print(f"📄 文档加载完成：{len(documents)} 页")
    print(f"✂️  切分完成：{len(chunks)} 个文本块")
    
    return chunks
```

### 5.2 Embedding 向量化

> 把文本块转成向量（一串数字），这样才能进行语义搜索。

```python
# ── 常用的 Embedding 模型 ──

# 方式一：OpenAI Embedding
from langchain_openai import OpenAIEmbeddings
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
    base_url="https://your-proxy-url/v1",
    api_key="sk-your-key"
)

# 方式二：OneAPI / 国产模型
# 同样的接口，换成 OneAPI 地址即可
embedding_model = OpenAIEmbeddings(
    model="text-embedding-v2",  # 千问的 Embedding 模型
    base_url="http://localhost:3000/v1",
    api_key="sk-your-oneapi-token"
)
```

```
Embedding 的本质：

文本："张三血压135/85" 
  ↓ Embedding 模型
向量：[0.023, -0.451, 0.789, ..., 0.312]  ← 比如 1536 维的向量

相似的文本 → 向量距离近 → 检索时能匹配到
```

### 5.3 存入 ChromaDB 向量数据库

```python
# ── ChromaDB 封装类 ──

import chromadb
from chromadb.config import Settings
from typing import List
from langchain_core.documents import Document


class ChromaDBManager:
    """
    ChromaDB 向量数据库管理器
    
    负责：
    1. 初始化数据库和集合
    2. 批量添加文档向量
    3. 相似度检索
    """
    
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "demo01"
    ):
        """
        初始化 ChromaDB
        
        Args:
            persist_directory: 数据库持久化目录
            collection_name: 集合名称（相当于关系数据库的"表"）
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # ── 创建客户端（持久化模式）──
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # ── 获取或创建集合 ──
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )
        
        print(f"📦 ChromaDB 就绪：{persist_directory}/{collection_name}")
    
    def add_documents(
        self,
        documents: List[Document],
        embeddings: List,
        batch_size: int = 25
    ):
        """
        批量添加文档到向量数据库
        
        Args:
            documents: 文档列表
            embeddings: 对应的向量列表
            batch_size: 每批次处理的文档数
        """
        total = len(documents)
        
        for i in range(0, total, batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]
            
            self.collection.add(
                embeddings=batch_embeddings,
                documents=[doc.page_content for doc in batch_docs],
                metadatas=[doc.metadata for doc in batch_docs],
                ids=[f"doc_{j}" for j in range(i, i + len(batch_docs))]
            )
            
            print(f"  批次 {i//batch_size + 1}: {len(batch_docs)} 条已入库")
        
        print(f"✅ 入库完成：共 {total} 条记录")
    
    def search(self, query_embedding, top_k: int = 5) -> dict:
        """
        相似度检索
        
        Args:
            query_embedding: 查询文本的向量
            top_k: 返回最相似的 K 条结果
        
        Returns:
            dict: 检索结果
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        return results
```

### 5.4 离线入库完整代码

```python
# ── build_vectordb.py ──

import os
from langchain_openai import OpenAIEmbeddings
from utils.chinese_chunker import load_and_split_chinese_pdf
from chroma_db_manager import ChromaDBManager


# ══════════════════════════════════════════════════════
# 配置参数
# ══════════════════════════════════════════════════════

# ── Embedding 模型配置 ──
EMBEDDING_CONFIG = {
    "model": "text-embedding-3-small",
    "base_url": "https://your-proxy-url/v1",
    "api_key": "sk-your-key"
}

# ── 文档配置 ──
PDF_PATH = "input/健康档案.pdf"
LANGUAGE = "chinese"   # 文档语言：chinese / english

# ── 向量数据库配置 ──
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "demo01"

# ── 切分配置 ──
CHUNK_SIZE = 500       # 每个文本块最大字符数
CHUNK_OVERLAP = 50     # 重叠字符数
BATCH_SIZE = 25        # 每批次入库数量


def main():
    """执行离线文档入库"""
    
    print("=" * 50)
    print("🚀 开始离线文档入库...")
    print("=" * 50)
    
    # Step 1: 初始化 Embedding 模型
    print("\n1️⃣  初始化 Embedding 模型...")
    embedding_model = OpenAIEmbeddings(**EMBEDDING_CONFIG)
    
    # Step 2: 加载并切分文档
    print("\n2️⃣  加载并切分文档...")
    if LANGUAGE == "chinese":
        chunks = load_and_split_chinese_pdf(
            PDF_PATH,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
    else:
        # 英文用另一个切分器
        from utils.english_chunker import load_and_split_english_pdf
        chunks = load_and_split_english_pdf(PDF_PATH)
    
    # Step 3: 向量化（批量处理）
    print("\n3️⃣  向量化文本块...")
    texts = [chunk.page_content for chunk in chunks]
    
    all_embeddings = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i:i + BATCH_SIZE]
        batch_embeddings = embedding_model.embed_documents(batch_texts)
        all_embeddings.extend(batch_embeddings)
        print(f"  批次 {i//BATCH_SIZE + 1}: {len(batch_texts)} 条已向量化")
    
    # Step 4: 存入 ChromaDB
    print("\n4️⃣  存入向量数据库...")
    db_manager = ChromaDBManager(
        persist_directory=CHROMA_DIR,
        collection_name=COLLECTION_NAME
    )
    db_manager.add_documents(chunks, all_embeddings, batch_size=BATCH_SIZE)
    
    print(f"\n{'='*50}")
    print(f"🎉 离线入库完成！")
    print(f"   数据库路径：{CHROMA_DIR}")
    print(f"   集合名称：{COLLECTION_NAME}")
    print(f"   总记录数：{len(chunks)}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
```

```
执行效果：

$ python build_vectordb.py

==================================================
🚀 开始离线文档入库...
==================================================

1️⃣  初始化 Embedding 模型...
2️⃣  加载并切分文档...
📄 文档加载完成：5 页
✂️  切分完成：28 个文本块

3️⃣  向量化文本块...
  批次 1: 25 条已向量化
  批次 2: 3 条已向量化

4️⃣  存入向量数据库...
📦 ChromaDB 就绪：./chroma_db/demo01
  批次 1: 25 条已入库
  批次 2: 3 条已入库
✅ 入库完成：共 28 条记录

==================================================
🎉 离线入库完成！
   数据库路径：./chroma_db
   集合名称：demo01
   总记录数：28
==================================================
```

---

## 六、在线步骤——检索与生成

### 6.1 RAG 检索工具封装

> 这是本案例**最核心的工具**——让 Agent 能够从私有知识库中检索信息。

```python
# ── tools/health_search_tool.py ──

from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from langchain_openai import OpenAIEmbeddings
from chroma_db_manager import ChromaDBManager


class HealthSearchInput(BaseModel):
    """健康档案检索工具的输入参数"""
    query: str = Field(
        description="用户的健康问题，例如：'张三最近的头痛与之前的体检记录是否有关'"
    )


class HealthArchiveSearchTool(BaseTool):
    """
    健康档案 RAG 检索工具
    
    从私有健康档案向量数据库中检索与用户问题最相关的记录。
    
    ⚠️ 关键配置：chroma_dir 和 collection_name 必须与离线入库时一致！
    """
    
    name: str = "health_archive_search"
    
    description: str = (
        "从健康档案知识库中检索与用户健康问题相关的历史记录。"
        "当需要查询某个人的健康档案、体检记录、病史等信息时使用此工具。"
        "参数说明：query - 用户的健康问题（如'张三最近头痛是否与体检有关'）"
        "返回：检索到的相关健康档案内容"
    )
    
    args_schema: Type[BaseModel] = HealthSearchInput
    
    # ═══ 配置参数 ═══
    chroma_dir: str = "./chroma_db"       # ⚠️ 必须与离线入库路径一致！
    collection_name: str = "demo01"        # ⚠️ 必须与离线入库集合名一致！
    top_k: int = 5                         # 返回最相似的前 K 条
    
    def _run(self, query: str) -> str:
        """
        执行 RAG 检索
        
        Args:
            query: 用户健康问题
        
        Returns:
            str: 检索到的相关健康档案内容
        """
        try:
            # Step 1: 初始化 Embedding 模型
            embedding_model = OpenAIEmbeddings(
                model="text-embedding-3-small",
                base_url="https://your-proxy-url/v1",
                api_key="sk-your-key"
            )
            
            # Step 2: 将查询向量化
            query_embedding = embedding_model.embed_query(query)
            
            # Step 3: 在 ChromaDB 中相似检索
            db = ChromaDBManager(
                persist_directory=self.chroma_dir,
                collection_name=self.collection_name
            )
            results = db.search(query_embedding, top_k=self.top_k)
            
            # Step 4: 整理检索结果
            if not results or not results.get("documents"):
                return "未找到相关健康档案记录。"
            
            documents = results["documents"][0]  # 第一个查询的结果
            
            # 拼接结果
            output = "检索到的健康档案记录：\n\n"
            for i, doc in enumerate(documents, 1):
                output += f"--- 记录 {i} ---\n{doc}\n\n"
            
            return output
        
        except Exception as e:
            return f"❌ 健康档案检索失败：{str(e)}"
```

### 6.2 Text-to-PDF 工具

> 和案例 2 类似的 PDF 保存工具，本案例中分配给报告撰写 Agent 使用。

```python
# ── tools/text_to_pdf_tool.py ──

from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
import os
from datetime import datetime
from fpdf import FPDF


class TextToPDFInput(BaseModel):
    content: str = Field(description="要保存为 PDF 的报告内容")
    filename: Optional[str] = Field(
        default=None,
        description="输出 PDF 文件名（不含 .pdf 后缀）"
    )


class TextToPDFTool(BaseTool):
    """将健康报告保存为 PDF 文件"""
    
    name: str = "text_to_pdf"
    
    description: str = (
        "将健康分析报告内容保存为 PDF 文件到本地。"
        "当你完成健康分析和报告撰写后，使用此工具保存报告。"
        "参数：content（报告文本内容，必填）、"
        "filename（文件名不含后缀，选填）"
        "返回：PDF 文件的保存路径"
    )
    
    args_schema: Type[BaseModel] = TextToPDFInput
    output_dir: str = "output"
    
    def _run(self, content: str, filename: Optional[str] = None) -> str:
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"健康建议报告_{timestamp}"
            
            filepath = os.path.join(self.output_dir, f"{filename}.pdf")
            
            pdf = FPDF()
            pdf.add_page()
            
            # 加载中文字体
            font_path = os.path.join("fonts", "SimHei.ttf")
            if os.path.exists(font_path):
                pdf.add_font("SimHei", "", font_path, uni=True)
                pdf.set_font("SimHei", "", 12)
            
            pdf.set_font_size(18)
            pdf.cell(0, 10, "健康建议报告", ln=True, align="C")
            pdf.ln(10)
            
            pdf.set_font_size(12)
            for line in content.split("\n"):
                safe_line = line.encode("latin-1", "replace").decode("latin-1")
                pdf.multi_cell(0, 8, safe_line)
                pdf.ln(2)
            
            pdf.output(filepath)
            return f"✅ 健康报告已保存到: {filepath}"
        
        except Exception as e:
            return f"❌ 保存 PDF 失败: {str(e)}"
```

---

## 七、Agent 与 Task 配置

### 7.1 Agent 定义

```yaml
# ── config/agents.yaml ──

health_retriever:
  role: "健康档案检索专家"
  goal: >
    根据医生询问的健康问题，从私有健康档案库中
    检索出该患者的相关历史记录
  backstory: >
    你是一位专业的健康档案检索专家，
    擅长在庞大的健康档案中快速找到用户健康相关的历史记录。
    你对各种医学术语和体检指标有深入的理解。
  verbose: true
  allow_delegation: false

health_report_writer:
  role: "健康报告撰写专家"
  goal: >
    分析从健康档案中检索到的相关数据，
    结合医生的问题，撰写一份简明且富有医学依据的健康建议报告
  backstory: >
    你是一位具有医学背景的报告撰写专家，
    擅长分析健康档案并生成专业、易于医生理解的健康建议报告。
    你的报告内容简洁、逻辑清晰，且具有医学依据。
    你会分析用户的病史、体检数据、生活方式等因素，
    确保报告能够帮助医生做出科学决策。
  verbose: true
  allow_delegation: false
```

### 7.2 Task 定义

```yaml
# ── config/tasks.yaml ──

retrieval_task:
  description: >
    根据用户提供的健康问题：{query}
    使用健康档案检索工具，从私有健康档案库中
    检索与该问题相关的所有健康信息。
    确保检索结果全面、准确。
  expected_output: >
    与用户健康问题密切相关的档案记录，
    包括体检数据、病史、生活习惯等信息。
  agent: health_retriever

report_task:
  description: >
    根据健康档案检索专家返回的健康记录，
    再结合医生的问题：{query}
    撰写一份专业的健康建议报告。
    
    报告应包含以下内容：
    1. 健康状况概览
    2. 头痛可能的原因分析（结合体检数据）
    3. 相关指标解读（血压、血糖、心率等）
    4. 生活方式影响评估
    5. 个性化健康改善建议
    
    完成报告后，使用 PDF 工具将报告保存为文件。
  expected_output: >
    一份包含健康状况分析和健康建议的专业报告，
    语言简洁但具有医学依据。
  agent: health_report_writer
  context:
    - retrieval_task
```

---

## 八、Crew 封装类——工具分配与编排

> 本案例的关键设计：**不同工具分配给不同 Agent**。RAG 检索工具给检索 Agent，PDF 工具给报告 Agent。

```python
# ── crew_runner.py ──

import yaml
from typing import Any, Optional
from crewai import Agent, Task, Crew, Process

from tools.health_search_tool import HealthArchiveSearchTool
from tools.text_to_pdf_tool import TextToPDFTool


class HealthArchiveCrew:
    """
    健康档案助手 Crew
    
    核心设计：两个 Agent 分配不同的工具
    - Agent 1（检索专家）→ RAG 检索工具
    - Agent 2（报告专家）→ PDF 保存工具
    """
    
    def __init__(self, llm: Any = None, verbose: bool = True):
        self.llm = llm
        self.verbose = verbose
        
        # 加载配置
        self.agents_config = self._load_yaml("config/agents.yaml")
        self.tasks_config = self._load_yaml("config/tasks.yaml")
        
        # 创建 Agent
        self.retriever = self._create_agent("health_retriever")
        self.report_writer = self._create_agent("health_report_writer")
    
    def _load_yaml(self, path: str) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def _create_agent(self, key: str) -> Agent:
        config = self.agents_config[key]
        params = {
            "role": config["role"],
            "goal": config["goal"],
            "backstory": config["backstory"],
            "verbose": config.get("verbose", True),
            "allow_delegation": config.get("allow_delegation", False),
        }
        if self.llm:
            params["llm"] = self.llm
        return Agent(**params)
    
    def run(self, query: str) -> str:
        """
        执行健康档案查询和分析
        
        Args:
            query: 医生询问的健康问题
        
        Returns:
            str: 最终的健康分析报告
        """
        # ── 创建工具实例 ──
        search_tool = HealthArchiveSearchTool()
        pdf_tool = TextToPDFTool()
        
        # ── Task 1: 检索任务（绑定 RAG 工具）──
        retrieval_task = Task(
            description=self.tasks_config["retrieval_task"]["description"].format(
                query=query
            ),
            expected_output=self.tasks_config["retrieval_task"]["expected_output"],
            agent=self.retriever,
            tools=[search_tool]   # ═══ RAG 检索工具 → 检索 Agent ═══
        )
        
        # ── Task 2: 报告任务（绑定 PDF 工具）──
        report_task = Task(
            description=self.tasks_config["report_task"]["description"].format(
                query=query
            ),
            expected_output=self.tasks_config["report_task"]["expected_output"],
            agent=self.report_writer,
            tools=[pdf_tool],      # ═══ PDF 工具 → 报告 Agent ═══
            context=[retrieval_task]  # 引用检索结果
        )
        
        # ── 创建 Crew 并执行 ──
        crew = Crew(
            agents=[self.retriever, self.report_writer],
            tasks=[retrieval_task, report_task],
            process=Process.sequential,
            verbose=self.verbose
        )
        
        return str(crew.kickoff())
```

---

## 九、FastAPI 服务与测试

### 9.1 服务入口

```python
# ── main.py ──

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from crew_runner import HealthArchiveCrew

app = FastAPI(title="健康档案助手服务", version="3.0.0")

llm = None
health_crew = None

# ── 模型配置 ──
LLM_CONFIG = {
    "model": "gpt-4o-mini",
    "base_url": "https://your-proxy-url/v1",
    "api_key": "sk-your-key",
    "temperature": 0.7
}

class QueryRequest(BaseModel):
    query: str = Field(
        default="张三最近的头疼与之前的体检记录是否有关？",
        description="医生的健康询问"
    )

class QueryResponse(BaseModel):
    success: bool
    query: str
    report: str

@app.on_event("startup")
async def startup():
    global llm, health_crew
    llm = ChatOpenAI(**LLM_CONFIG)
    health_crew = HealthArchiveCrew(llm=llm)
    print("✅ 健康档案助手服务已就绪")

@app.post("/health-query", response_model=QueryResponse)
async def health_query(request: QueryRequest):
    if health_crew is None:
        raise HTTPException(status_code=503)
    try:
        report = health_crew.run(query=request.query)
        return QueryResponse(success=True, query=request.query, report=report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8028)
```

### 9.2 测试客户端

```python
# ── api_test.py ──

import requests

url = "http://localhost:8028/health-query"
payload = {
    "query": "张三最近的头疼与之前的体检记录是否有关？"
}

print(f"🚀 发送健康咨询...")
response = requests.post(url, json=payload, timeout=300)

if response.status_code == 200:
    data = response.json()
    print(f"✅ 咨询完成！\n")
    print(data["report"])
    print(f"\n📄 PDF 报告已保存到 output/ 目录")
else:
    print(f"❌ 请求失败：{response.status_code}")
```

---

## 十、执行流程演示

```
第一步：离线入库（只需执行一次）

$ python build_vectordb.py

🚀 开始离线文档入库...
📄 文档加载完成：5 页
✂️  切分完成：28 个文本块
✅ 入库完成：共 28 条记录

────────────────────────────────────────────────

第二步：启动服务

$ python main.py

✅ 健康档案助手服务已就绪
📡 端口: 8028

────────────────────────────────────────────────

第三步：发送请求

$ python api_test.py

🚀 发送健康咨询...

═══════════════════════════════════════════════
Agent 1: 健康档案检索专家 开始工作
═══════════════════════════════════════════════

任务：检索"张三最近头疼与体检记录是否有关"
→ 调用 health_archive_search 工具...
→ 从 ChromaDB demo01 集合检索...
→ 检索到 5 条相关记录：
  - 张三，血压 135/85，2024-08-15
  - 心率 78 次/分钟
  - 血糖偏高...
  - 睡眠时间不足...

═══════════════════════════════════════════════
Agent 2: 健康报告撰写专家 开始工作
═══════════════════════════════════════════════

任务：分析检索数据，撰写健康建议报告
→ 分析体检指标...
→ 结合头痛问题...
→ 撰写报告...
→ 调用 text_to_pdf 保存报告...

✅ 报告完成！
📄 健康建议报告已保存到: output/健康建议报告_20260628_091500.pdf
```

---

## 十一、工具测试——先测试再集成

> 本案例的一个重要工作流创新：**在 unit_test 文件夹中独立测试每个工具，验证通过后再注册到 Crew Agent 中。**

```
┌─────────────────────────────────────────────────────────┐
│          工具开发工作流                                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Step 1: 在 unit_test/ 中编写工具测试                    │
│          ├── 测试基本功能是否正常                         │
│          ├── 测试边界情况                                 │
│          └── 确保输出符合预期                             │
│                                                         │
│  Step 2: 测试通过后，封装为 CrewAI Tool                   │
│          ├── 继承 BaseTool                               │
│          ├── 添加 @tool 注解                             │
│          └── 写好 name 和 description                    │
│                                                         │
│  Step 3: 注册到 Crew 中                                  │
│          ├── 分配给对应的 Agent 或 Task                   │
│          └── 完整流程测试                                 │
│                                                         │
│  这个工作流避免了"工具有问题但不知道哪里有问题"的困境！    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 十二、本案例相比案例 2 的核心突破

| 维度 | 案例 2（技术研究员） | 案例 3（健康档案助手） |
|---|---|---|
| **数据来源** | 纯 LLM 知识 | **私有知识库（RAG）** 🆕 |
| **外部存储** | 无 | **ChromaDB 向量数据库** 🆕 |
| **核心工具** | Text-to-PDF | Text-to-PDF + **RAG 检索** 🆕 |
| **预处理** | 无 | **离线文档入库流程** 🆕 |
| **工具测试** | 无独立测试 | **unit_test 文件夹** 🆕 |
| **工具分配** | 一个 Task 绑定一个工具 | **不同 Agent 分配不同工具** |
| **Embedding** | 无需 | **需要 Embedding 模型** 🆕 |

---

## 十三、完整代码清单

```
health-archive-crew/
├── main.py                      # FastAPI 服务
├── api_test.py                  # 测试客户端
├── crew_runner.py               # Crew 封装（工具分配）
├── build_vectordb.py            # 离线入库脚本
├── config/
│   ├── agents.yaml              # 检索专家 + 报告专家
│   └── tasks.yaml               # 检索任务 + 报告任务
├── tools/
│   ├── health_search_tool.py    # RAG 检索工具（核心！）
│   └── text_to_pdf_tool.py      # PDF 保存工具
├── unit_test/
│   ├── test_pdf_tool.py         # 测试 PDF 工具
│   └── test_rag_tool.py         # 测试 RAG 检索
├── utils/
│   ├── chinese_chunker.py       # 中文文档切分
│   └── english_chunker.py       # 英文文档切分
├── input/
│   └── 健康档案.pdf             # 原始档案文件
├── fonts/
│   └── SimHei.ttf               # 中文字体
├── output/                      # PDF 输出目录
└── chroma_db/                   # ChromaDB 持久化目录
```

```txt
# requirements.txt
crewai>=0.80.0
fastapi>=0.115.0
uvicorn>=0.30.0
langchain>=0.3.0
langchain-openai>=0.2.0
langchain-community>=0.3.0
chromadb>=0.5.0
pypdf>=5.0.0
fpdf>=1.7.2
pyyaml>=6.0
```

---

## 十四、课后练习

### 练习一：基础——搭建自己的私有知识库

**题目**：准备一份你自己的 PDF 文档（可以是学习笔记、项目文档等），完成离线入库 + RAG 检索全流程。

**要求**：
1. 修改 `build_vectordb.py` 的配置参数
2. 执行离线入库，确认 ChromaDB 中有数据
3. 在 `unit_test/test_rag_tool.py` 中测试检索效果
4. 验证检索结果是否与你的问题相关

### 练习二：进阶——给 Agent 不同工具验证效果

**题目**：创建一个测试场景，验证"不同 Agent 分配不同工具"的效果。

**要求**：
1. 创建 3 个 Agent，分别分配 3 个不同工具
2. 观察每个 Agent 在执行任务时调用的工具
3. 验证：给 Agent A 的工具，Agent B 不会去调用
4. 对比"把工具分配给 Task"和"分配给 Agent"的区别

### 练习三：综合——改造为其他领域的知识库助手

**题目**：把健康档案换成其他领域（如法律文书、产品手册、课程笔记），适配 Agent 的角色和提示词。

**要求**：
1. 准备新领域的 PDF 文档
2. 修改 YAML 配置中的 Agent 角色/目标/背景
3. 修改 Task 描述，适配新领域
4. 运行并对比效果

---

## 十五、课程小结

### 15.1 核心知识图谱

```
┌────────────────────────────────────────────────────────────┐
│        健康档案助手智能体——核心知识体系                        │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  RAG 两阶段流程                                        │
│      ├── 离线：文档加载→切分→Embedding→ChromaDB            │
│      └── 在线：问题→向量化→相似检索→Prompt→LLM→答案       │
│                                                            │
│  2️⃣  Agent 角色定义                                         │
│      ├── Agent 1：健康档案检索专家（RAG 检索工具）          │
│      └── Agent 2：健康报告撰写专家（PDF 保存工具）          │
│                                                            │
│  3️⃣  工具分配策略                                           │
│      ├── RAG 检索工具 → 分配给检索 Agent                    │
│      └── PDF 保存工具 → 分配给报告 Agent                    │
│                                                            │
│  4️⃣  工具开发工作流                                         │
│      ├── unit_test 独立测试 → 验证通过                     │
│      ├── 封装为 CrewAI Tool                                 │
│      └── 注册到 Crew（分配给 Agent/Task）                  │
│                                                            │
│  5️⃣  关键配置一致性                                         │
│      ├── chroma_dir 和 collection_name                     │
│      ├── 离线入库 和 在线检索 必须一致！                    │
│      └── Embedding 模型配置也需要一致                       │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 15.2 一句话总结

> **健康档案助手案例的核心突破是 RAG 集成——Agent 不再只靠 LLM 的"记忆"回答问题，而是能真正检索你自己的私有文档。离线入库 + 在线检索的两阶段流程是 RAG 的标准范式，ChromaDB 是轻量级向量数据库的最佳入门选择。Prompt 仍然是整个系统最重要的部分——Agent 的角色描述和 Task 的期望输出直接决定了最终答案的质量。**

### 15.3 系列课程定位

```
┌─────────────────────────────────────────────────────────┐
│         Agent 应用案例系列                                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  案例 1：CrewAI + FastAPI 基础入门（研究员+分析师）       │
│  案例 2：技术研究员（自定义工具 + LLM 注入 + PDF）       │
│  案例 3（本课）：健康档案助手 ← 你在这里                  │
│         → RAG 私有知识库 + ChromaDB + 工具独立测试       │
│                                                         │
│  后续：                                                  │
│  └── 案例 4：多工具复杂编排 + Pipeline                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

*本教学文档基于陈泽鹏老师视频课程整理编写 · 2026年6月28日*
