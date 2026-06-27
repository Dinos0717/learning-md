# LangChain 语义搜索实战——文档问答匹配

> 基于陈泽鹏老师视频课程整理编写 · 2026年6月

---

## 目录

- [一、课程背景与目标](#一课程背景与目标)
- [二、案例场景——公司政策文档问答](#二案例场景公司政策文档问答)
- [三、第一步：加载文档——TextLoader](#三第一步加载文档textloader)
- [四、第二步：文本分块——CharacterTextSplitter](#四第二步文本分块characterttextsplitter)
- [五、第三步：向量化 + 持久化——ChromaDB](#五第三步向量化--持久化chromadb)
- [六、第四步：语义搜索——similarity_search](#六第四步语义搜索similarity_search)
- [七、⚠️ 关键踩坑——模型维度不匹配](#七️-关键踩坑模型维度不匹配)
- [八、完整代码汇总](#八完整代码汇总)
- [九、语义搜索的应用场景扩展](#九语义搜索的应用场景扩展)
- [十、常见问题与排错指南](#十常见问题与排错指南)
- [十一、课后练习](#十一课后练习)
- [十二、课程小结](#十二课程小结)

---

## 一、课程背景与目标

### 1.1 前情回顾

在前两节课中，我们已经学会了：

| 课程 | 内容 |
|------|------|
| 第十三课 | 文本嵌入模型原理 + 云端 Embedding（智谱AI） |
| 第十四课 | 本地 Embedding 模型（HuggingFace + bge-small-zh） |

我们已经能把文本变成向量了，但**向量化之后能做什么**？本课用一个完整的案例来回答这个问题。

### 1.2 本节课的核心问题

> **我有一份公司的政策文档，员工问"迟到怎么处罚"——怎么让程序自动从文档中找到最匹配的答案？**

```
传统做法（Ctrl+F）：
"迟到怎么处罚" → 搜索"迟到"关键词 → 只能匹配精确文字

语义搜索（本课）：
"迟到怎么处罚" → 转为向量 → 搜索相似向量 → 匹配到"迟到30分钟即为缺勤"
                                        ↑ 文字不完全一样，但语义匹配！
```

### 1.3 本课要掌握的目标

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  目标：掌握文本嵌入模型的完整实战流程                │
│        ├── 文档加载（TextLoader）                 │
│        ├── 文本分块（CharacterTextSplitter）      │
│        ├── 向量持久化（ChromaDB）                 │
│        ├── 语义搜索（similarity_search）          │
│        └── 理解并解决模型维度不匹配问题             │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 二、案例场景——公司政策文档问答

### 2.1 原始文档

准备好一份公司政策文档，内容如下：

```
公司的年假政策：
员工满一年可享用5天带薪休假。
年假的有效期是次年的3月31号。
部门经理审批完以后可以去使用。

考勤制度：
工作日的上班时间是9点-18点。
迟到30分钟即为缺勤。
```

### 2.2 期望效果

| 用户问 | 期望匹配到 |
|--------|-----------|
| "迟到怎么处罚？" | "迟到30分钟即为缺勤" |
| "年假有多少天？" | "员工满一年可享用5天带薪休假" |
| "年假什么时候过期？" | "年假的有效期是次年的3月31号" |
| "上班时间是几点？" | "工作日的上班时间是9点-18点" |

> **核心思路**：文档转向量存起来 → 用户问题转向量 → 在向量库中找最相似的文档片段。

---

## 三、第一步：加载文档——TextLoader

### 3.1 为什么用 LangChain 的加载器？

Python 原生的 `open()` 也能读文件，但 LangChain 的加载器提供了**统一格式**的输出，方便后续处理。

### 3.2 核心代码

```python
from langchain_community.document_loaders import TextLoader

# 加载文本文件
loader = TextLoader(
    "./政策文件.txt",        # 文件路径
    encoding="utf-8"         # 中文必须指定编码！
)

# 加载为 Document 对象
documents = loader.load()
```

### 3.3 代码逐行解析

| 代码 | 说明 |
|------|------|
| `TextLoader` | LangChain 提供的纯文本加载器 |
| `"./政策文件.txt"` | 文件路径（当前目录下） |
| `encoding="utf-8"` | ⚠️ 中文必须指定！否则乱码 |
| `.load()` | 加载文件，返回 Document 对象列表 |

### 3.4 Document 对象结构

```python
# 加载后 documents 是一个列表
# 每个元素是一个 Document 对象
print(documents[0])
# Document(
#     page_content="公司的年假政策：\n员工满一年可享用5天带薪休假。\n...",
#     metadata={"source": "./政策文件.txt"}
# )
```

| 属性 | 内容 |
|------|------|
| `.page_content` | 文档的文本内容 |
| `.metadata` | 元信息（来源文件等） |

---

## 四、第二步：文本分块——CharacterTextSplitter

### 4.1 为什么要分块？

```
不分块的问题：
一整段长文本 → 一个向量 → 搜索只能定位到整个文档
"迟到怎么处罚" → 匹配到整个政策文档 → 不精确！

分块后的好处：
文档切成多个小块 → 每块一个向量 → 搜索精确到具体段落
"迟到怎么处罚" → 匹配到"迟到30分钟即为缺勤"这一块 → 精确！
```

### 4.2 核心代码

```python
from langchain.text_splitter import CharacterTextSplitter

text_splitter = CharacterTextSplitter(
    chunk_size=100,           # 每块最多 100 个字符
    chunk_overlap=20,         # 相邻块重叠 20 个字符
    separator="\n\n"          # 优先按双换行分割
)

# 执行分块
split_docs = text_splitter.split_documents(documents)
```

### 4.3 参数详解

| 参数 | 含义 | 示例（chunk_size=100） |
|------|------|----------------------|
| `chunk_size` | 每块的**目标**大小（字符数） | 每块约 100 个字符 |
| `chunk_overlap` | 相邻块之间的**重叠**字符数 | 块1的第80-100字 = 块2的第1-20字 |
| `separator` | 分割的**优先级** | 先按 `\n\n` 分，再按 `\n`，再按标点… |

### 4.4 chunk_overlap 的关键作用

```
没有 overlap（chunk_overlap=0）：

块1: "员工的年假申请需要"     ← 在这断了！
块2: "部门经理审批通过后"

→ "需要" 和 "部门经理" 之间的关联丢失了！

有 overlap（chunk_overlap=20）：

块1: "员工的年假申请需要部门经理"
块2: "需要部门经理审批通过后方可使用"
      ↑ 重叠部分保留了上下文连续性

→ 不会因为切分导致信息断裂
```

### 4.5 separator 的中文适配

```python
# 针对中文文本的分隔符设置
separator = "\n\n"    # 双换行（段落分隔）
# 如果没有双换行，会依次尝试：
#   "\n"       → 单换行
#   "。"       → 句号
#   "！"       → 感叹号
#   "？"       → 问号
#   ...然后更小的分隔符

# ⚠️ 对于中文，推荐设置更细的分隔符：
text_splitter = CharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=20,
    separator="\n"
)
```

### 4.6 调整 chunk_size 的效果

```python
# chunk_size=100 → 大约分 2 块
# chunk_size=50  → 大约分 4-5 块（更细）

# 原则：
# 分太粗 → 匹配不够精确
# 分太细 → 每块信息太少，可能丢失上下文
# 100-500 是常用的范围
```

### 4.7 查看分块结果

```python
# 查看共分了多少块
print(f"共分成 {len(split_docs)} 块")

# 查看第一块的纯文本内容
print(split_docs[0].page_content)
```

---

## 五、第三步：向量化 + 持久化——ChromaDB

### 5.1 为什么要持久化？

```
内存存储：
├── 每次运行 → 重新向量化 → 慢
└── 数据量大时 → 内存不够

ChromaDB 持久化：
├── 向量化一次 → 存到硬盘
├── 下次直接读取 → 快
└── 支持大规模数据
```

### 5.2 安装 ChromaDB

```bash
pip install chromadb
```

> 📌 建议锁定版本，保持和课程一致。

### 5.3 核心代码

```python
from langchain_community.vectorstores import Chroma

# 将分块后的文档向量化并存入 ChromaDB
db = Chroma.from_documents(
    documents=split_docs,               # 分块后的文档列表
    embedding=embeddings,               # Embedding 模型（本地或云端）
    persist_directory="./chroma_db"     # 持久化目录
)
```

### 5.4 参数详解

| 参数 | 作用 | 说明 |
|------|------|------|
| `documents` | 要向量化的文档 | 就是上一步分好的 `split_docs` |
| `embedding` | 用什么模型做向量化 | 本地 `HuggingFaceEmbeddings` 或云端 `ZhipuAIEmbeddings` |
| `persist_directory` | 向量数据存哪里 | 指定一个文件夹路径 |

### 5.5 执行过程

```
Chroma.from_documents() 内部做的事：

split_docs（文本块列表）
    ↓
embedding 模型将每块文本转为向量
    ↓
向量 + 原始文本 → 存入 ChromaDB
    ↓
持久化到 ./chroma_db/ 文件夹
    ↓
后续可以直接加载使用
```

---

## 六、第四步：语义搜索——similarity_search

### 6.1 核心代码

```python
# 语义搜索
query = "迟到怎么处罚？"
results = db.similarity_search(
    query,    # 搜索的问题
    k=1       # 返回最相似的 1 个结果
)

# 查看结果
for doc in results:
    print(doc.page_content)
```

### 6.2 参数详解

| 参数 | 含义 | 常用值 |
|------|------|:------:|
| `query` | 搜索的问题（自然语言） | 用户的输入 |
| `k` | 返回几个最相似的结果 | 1-5（根据需求） |

### 6.3 运行结果

```
输入："迟到怎么处罚？"

匹配结果：
考勤制度：
工作日的上班时间是9点-18点。
迟到30分钟即为缺勤。

→ 虽然没有出现"处罚"二字，但语义匹配到了"迟到30分钟即为缺勤"！
```

### 6.4 整个搜索流程背后发生了什么

```
用户问题："迟到怎么处罚？"
    ↓ embedding 模型
问题向量：[0.023, -0.451, 0.782, ..., -0.567]  (512维或1024维)
    ↓
在 ChromaDB 中计算问题向量与所有文档向量的相似度
    ↓
文档向量1（年假政策）：相似度 0.32  ← 不相关
文档向量2（考勤制度）：相似度 0.89  ← 最高！
    ↓
返回文档向量2对应的原始文本："迟到30分钟即为缺勤"
    ↓
🎉 这就是语义搜索！
```

### 6.5 k 值的效果

```python
# k=1：只返回最匹配的那一条
db.similarity_search("迟到怎么处罚？", k=1)
# → "迟到30分钟即为缺勤"

# k=2：返回最匹配的两条
db.similarity_search("迟到怎么处罚？", k=2)
# → "迟到30分钟即为缺勤"（最匹配）
# → "部门经理审批完以后可以去使用"（次匹配，语义有点远但也被找出来了）
```

---

## 七、⚠️ 关键踩坑——模型维度不匹配

### 7.1 问题现象

这是视频中老师**当场遇到并演示解决**的核心问题。用本地模型创建了向量数据库后，切换到云端模型：

```python
# 第一次：用本地模型创建数据库
db = Chroma.from_documents(docs, local_embeddings, persist_directory="./db")
# → 本地模型 bge-small-zh：512 维

# 第二次：换成云端模型，尝试搜索
db = Chroma.from_documents(docs, cloud_embeddings, persist_directory="./db")
# → 云端模型 embedding-2：1024 维
# → ❌ 报错！维度不匹配！
```

**错误信息**：

```
ValueError: Expected embedding dimension 512, but got 1024
```

### 7.2 原因分析

```
ChromaDB 的工作机制：

创建数据库时：
├── 用模型 A → 生成 512 维向量 → 存入 ./db/ 文件夹
└── 数据库文件记录了"我是 512 维的"

再次加载时：
├── 用模型 B → 生成 1024 维向量 → 尝试匹配
└── 数据库说"我只有 512 维"→ 维度冲突 → 报错！
```

> ⚠️ **向量数据库创建好之后，维度就固定了。** 换了不同维度的 Embedding 模型，必须重新创建数据库。

### 7.3 解决方案

**方案一：删除旧数据库，重新创建**

```bash
# 删除旧的向量数据库文件夹
rm -rf ./chroma_db
```

然后重新运行 `Chroma.from_documents()`。

**方案二：使用不同的存储目录**

```python
# 本地模型 → 存到这个目录
db_local = Chroma.from_documents(docs, local_embeddings, 
                                  persist_directory="./chroma_db_local")

# 云端模型 → 存到另一个目录
db_cloud = Chroma.from_documents(docs, cloud_embeddings, 
                                  persist_directory="./chroma_db_cloud")
```

**方案三：用 try-except 自动处理**

```python
try:
    db = Chroma.from_documents(docs, new_embeddings, persist_directory="./db")
except Exception:
    # 维度不匹配时，删除旧数据重新创建
    import shutil
    shutil.rmtree("./db")
    db = Chroma.from_documents(docs, new_embeddings, persist_directory="./db")
```

### 7.4 维度速查表

| Embedding 模型 | 向量维度 |
|:--------------|:------:|
| 本地 `bge-small-zh` | **512** |
| 本地 `bge-base-zh` | **768** |
| 本地 `bge-large-zh` | **1024** |
| 云端 `embedding-2` | **1024** |
| 云端 `embedding-3` | 更高 |

> 📌 **记住**：创建数据库和搜索数据库必须用**维度相同**的模型。换模型 = 重建数据库。

---

## 八、完整代码汇总

### 8.1 完整流程代码

```python
import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# ============================================================
# Step 1: 加载文档
# ============================================================
loader = TextLoader("./政策文件.txt", encoding="utf-8")
documents = loader.load()
print(f"文档加载完成，共 {len(documents)} 个文档")

# ============================================================
# Step 2: 文本分块
# ============================================================
text_splitter = CharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=20,
    separator="\n"
)
split_docs = text_splitter.split_documents(documents)
print(f"分块完成，共 {len(split_docs)} 块")

# ============================================================
# Step 3: 加载 Embedding 模型
# ============================================================
embeddings = HuggingFaceEmbeddings(
    model_name="./bge-small-zh",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

# ============================================================
# Step 4: 向量化并持久化
# ============================================================
db = Chroma.from_documents(
    documents=split_docs,
    embedding=embeddings,
    persist_directory="./chroma_db"
)
print("向量化完成，数据已存入 chroma_db/")

# ============================================================
# Step 5: 语义搜索
# ============================================================
def search_policy(question, k=1):
    """搜索公司政策中与问题最匹配的内容"""
    results = db.similarity_search(question, k=k)
    return results

# ── 测试 ──
test_questions = [
    "迟到怎么处罚？",
    "年假有多少天？",
    "上班时间是几点？",
    "怎么申请年假？",
]

for q in test_questions:
    print(f"\n问：{q}")
    results = search_policy(q)
    for r in results:
        print(f"答：{r.page_content}")
```

### 8.2 云端 Embedding 版本

```python
import os
from langchain_community.embeddings import ZhipuAIEmbeddings

# ── 使用云端模型 ──
os.environ["ZHIPUAI_API_KEY"] = "你的Key"
embeddings = ZhipuAIEmbeddings(model="embedding-2")

# ⚠️ 注意：云端模型是 1024 维，本地是 512 维
# 必须使用不同的 persist_directory
db = Chroma.from_documents(
    documents=split_docs,
    embedding=embeddings,                     # ← 云端模型
    persist_directory="./chroma_db_cloud"     # ← 不同目录
)
```

---

## 九、语义搜索的应用场景扩展

### 9.1 用户意图解析

视频中老师提到了一个重要的应用场景：

> 用户发送请求 → 用语义搜索匹配到预定义的操作 → 决定执行哪个功能

```
操作列表：
├── "查询余额"  → 向量A
├── "转账汇款"  → 向量B
├── "修改密码"  → 向量C
└── ...

用户说："我想看看卡里还有多少钱"
    ↓ 语义搜索
匹配到 → "查询余额"（语义最接近）
    ↓
系统执行查询余额功能
```

### 9.2 内容精准过滤

> 模型生成长篇回答 → 用语义搜索从回答中提取最相关的段落 → 只返回核心信息

```
模型生成完整的回答（5000字）
    ↓
用户关心的其实只是其中一段
    ↓
语义搜索匹配 → 只返回最相关的 200 字
    ↓
返回精简但有价值的信息
```

### 9.3 构建知识库问答

这是本课案例的扩展——也就是后续课程要讲的 RAG：

```
文档库（数百个文件）
    ↓ 向量化
向量数据库
    ↓ 用户提问 → 语义搜索
找到相关文档片段
    ↓ 塞给 LLM
LLM 基于片段生成准确答案
    ↓
用户得到有据可查的回答
```

---

## 十、常见问题与排错指南

### 10.1 错误速查表

| 错误/问题 | 原因 | 解决方法 | 优先级 |
|-----------|------|----------|:------:|
| 中文乱码 | TextLoader 未指定编码 | `TextLoader(path, encoding="utf-8")` | 🔴高 |
| `ValueError: dimension mismatch` | Embedding 模型维度与数据库不一致 | 删除旧数据库或用不同 persist_directory | 🔴高 |
| `ModuleNotFoundError: No module named 'chromadb'` | 未安装 chromadb | `pip install chromadb` | 🔴高 |
| 搜索返回的结果不相关 | chunk_size 太大 | 减小 chunk_size（如 50-100） | 🟡中 |
| 搜索结果语义不太对 | Embedding 模型不适合中文 | 换用中文模型（bge-small-zh） | 🟡中 |
| 分块后信息断裂 | chunk_overlap 太小 | 增大 chunk_overlap（如 20-50） | 🟢低 |
| `HuggingFaceEmbeddings not defined` | 前面代码块没运行 | Jupyter 中确保按顺序执行全部代码块 | 🟡中 |

### 10.2 排查流程

```
语义搜索效果不佳？
    ↓
第一步：检查分块是否合理
    打印 split_docs[i].page_content → 内容是否完整连续？
    ├── 信息断裂 → 增大 chunk_overlap
    └── 每块太长 → 减小 chunk_size
    ↓
第二步：检查 Embedding 模型
    是否用的是中文模型？→ 用 bge-small-zh 或 embedding-2
    ↓
第三步：检查搜索参数
    k 值是否够？→ 问题复杂时可增大 k
    ↓
第四步：检查数据库维度
    切换过模型？→ 维度变了 → 重建数据库
```

---

## 十一、课后练习

### 练习一：基础流程

> 准备一份自己的文本文件（如产品说明、课程大纲等），完成完整的文档问答流程：加载 → 分块 → 向量化 → 语义搜索。

**验收标准：**
- [ ] 文档成功加载且中文无乱码
- [ ] 分块数量在 2-10 块之间
- [ ] 语义搜索能返回相关的内容

### 练习二：分块参数实验

> 用同一份文档，分别设置 `chunk_size=50`、`chunk_size=100`、`chunk_size=200`，用同一个问题做语义搜索。对比不同设置下的搜索结果。

| chunk_size | 分块数 | 搜索返回的内容 | 评价 |
|:----------:|:-----:|-------------|------|
| 50 | | | |
| 100 | | | |
| 200 | | | |

### 练习三：k 值实验

> 用同一个问题，分别设置 `k=1`、`k=2`、`k=3`，对比返回结果。

| k 值 | 返回内容（摘要） | 是否有冗余信息？ |
|:----:|---------------|:---------------:|
| 1 | | |
| 2 | | |
| 3 | | |

### 练习四：模型维度验证

> 分别用本地模型（512维）和云端模型（1024维）创建向量数据库（用不同的 persist_directory），用同一个问题搜索。对比：
>
> 1. 搜索结果是否有差异？
> 2. 如果交叉使用（本地搜索云端的数据库，或反过来），会报什么错？

| 创建数据库的模型 | 搜索的模型 | 结果 |
|:-------------:|:---------:|------|
| 本地（512维） | 本地 | |
| 本地（512维） | 云端 | |
| 云端（1024维） | 云端 | |
| 云端（1024维） | 本地 | |

### 练习五：应用场景设计

> 设计一个你自己的语义搜索应用场景，说明：
>
> 1. 数据来源是什么？（如产品文档、FAQ、法律条款）
> 2. 用户会问什么问题？
> 3. 期望返回什么答案？

---

## 十二、课程小结

### 12.1 本课核心知识图谱

```
┌────────────────────────────────────────────────────────────┐
│              语义搜索实战核心知识体系                          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  完整流程（四步走）                                      │
│      TextLoader → CharacterTextSplitter → ChromaDB →       │
│      similarity_search                                    │
│                                                            │
│  2️⃣  TextLoader                                            │
│      ├── 加载纯文本文件                                      │
│      └── encoding="utf-8" ← 中文必须！                     │
│                                                            │
│  3️⃣  CharacterTextSplitter                                 │
│      ├── chunk_size：每块多大（100字符）                     │
│      ├── chunk_overlap：相邻重叠（20字符，防断裂）            │
│      └── separator：按什么符号分割（\n、。、！、？）          │
│                                                            │
│  4️⃣  ChromaDB                                              │
│      ├── 向量数据库：存储文本+向量                           │
│      ├── from_documents：向量化 + 持久化                    │
│      └── persist_directory：数据存到哪个文件夹               │
│                                                            │
│  5️⃣  语义搜索                                               │
│      ├── db.similarity_search(query, k=1)                  │
│      ├── query：自然语言问题                                │
│      └── k：返回几个最相似结果                               │
│                                                            │
│  6️⃣  ⚠️ 维度陷阱                                           │
│      ├── 本地 bge-small-zh = 512 维                        │
│      ├── 云端 embedding-2 = 1024 维                        │
│      ├── 换模型 → 维度变了 → 必须重建数据库                  │
│      └── 解决：删旧数据库 或 用不同 persist_directory        │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 12.2 一句话总结

> **文档转向量存 ChromaDB → 用户问题转向量 → 搜最相似的文档片段。** 四步走：`TextLoader` 加载 → `CharacterTextSplitter` 分块 → `Chroma.from_documents` 向量化 → `db.similarity_search` 语义搜索。⚠️ 换 Embedding 模型必须重建数据库。

### 12.3 速记卡

```
┌───────────────────────────────────────────────────────┐
│              语义搜索速记卡                              │
├───────────────────────────────────────────────────────┤
│                                                       │
│  加载：                                                │
│  loader = TextLoader("文件.txt", encoding="utf-8")    │
│  docs = loader.load()                                │
│                                                       │
│  分块：                                                │
│  splitter = CharacterTextSplitter(                   │
│      chunk_size=100, chunk_overlap=20               │
│  )                                                    │
│  split_docs = splitter.split_documents(docs)         │
│                                                       │
│  向量化+存储：                                          │
│  db = Chroma.from_documents(                         │
│      split_docs, embeddings,                        │
│      persist_directory="./db"                        │
│  )                                                    │
│                                                       │
│  搜索：                                                │
│  results = db.similarity_search("问题", k=1)          │
│                                                       │
│  ⚠️ 换模型 = 换目录（或删旧库）                          │
│                                                       │
└───────────────────────────────────────────────────────┘
```

### 12.4 系列课程定位

```
第一~十二课：环境搭建 ~ SummaryBufferMemory
第十三课：文本嵌入（云端·智谱AI）
第十四课：文本嵌入（本地·HuggingFace）
第十五课（本课）：语义搜索实战 🆕
后续：RAG（检索增强生成）
```

---

*本教学文档基于陈泽鹏老师视频课程（语义搜索实战案例）整理编写。*  
*本文档涵盖从文档加载、文本分块、向量持久化到语义搜索的完整流程，以及 Embedding 模型维度不匹配问题的深度解析。*
