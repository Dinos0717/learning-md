# LangChain 本地文本嵌入模型详解（HuggingFace）

> 基于陈泽鹏老师视频课程整理编写 · 2026年6月

---

## 目录

- [一、课程背景与目标](#一课程背景与目标)
- [二、云端 vs 本地——什么时候需要本地模型](#二云端-vs-本地什么时候需要本地模型)
- [三、模型下载——两大平台详解](#三模型下载两大平台详解)
- [四、选择模型的关键指标](#四选择模型的关键指标)
- [五、环境搭建——依赖安装](#五环境搭建依赖安装)
- [六、代码实战——加载并使用本地 Embedding](#六代码实战加载并使用本地-embedding)
- [七、CPU vs GPU——设备选择详解](#七cpu-vs-gpu设备选择详解)
- [八、完整流程回顾](#八完整流程回顾)
- [九、云端 Embedding vs 本地 Embedding——全面对比](#九云端-embedding-vs-本地-embedding全面对比)
- [十、常见问题与排错指南](#十常见问题与排错指南)
- [十一、课后练习](#十一课后练习)
- [十二、课程小结](#十二课程小结)

---

## 一、课程背景与目标

### 1.1 前情回顾

上一节课我们学习了**云端文本嵌入模型**——使用智谱AI 平台提供的 Embedding API：

```python
# 上一课：云端方式
from langchain_community.embeddings import ZhipuAIEmbeddings
embeddings = ZhipuAIEmbeddings(model="embedding-2")
vectors = embeddings.embed_documents(["产品太棒了！"])
# → 文本通过 API 发送到智谱服务器 → 返回 1024 维向量
```

| 云端方式的特征 | |
|------|------|
| 模型运行位置 | 智谱AI 的服务器 |
| 需要什么 | API Key + 网络 |
| 优点 | 方便快捷，不需要本地算力 |
| 缺点 | 依赖网络、依赖平台、有费用 |

### 1.2 本节课的核心问题

> **云端模型不能满足需求怎么办？**
>
> 我想在本地跑 Embedding 模型——不需要网络，不需要 API Key，完全自己控制。怎么做到？

```
云端方式：                    本地方式：
文本 → API发送 → 云端服务器    文本 → 本地模型文件 → 本地CPU/GPU
         ↓                              ↓
      等待返回                          即时返回
         ↓                              ↓
      1024维向量                       512维向量

依赖：网络 + API Key + 平台         依赖：模型文件 + PyTorch
```

### 1.3 本课要掌握的目标

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  目标一：了解如何搭建本地文本嵌入模型的环境          │
│         ├── 从哪下载模型（HuggingFace / 魔搭）     │
│         ├── 如何下载模型（git clone / SDK）        │
│         ├── 安装哪些依赖（langchain-huggingface）  │
│         └── 理解 CPU vs GPU 的选择                │
│                                                 │
│  目标二：掌握本地文本嵌入模型的使用方法              │
│         ├── 加载本地模型（HuggingFaceEmbeddings）  │
│         ├── 设置 device 和 encode_kwargs 参数      │
│         ├── 使用 embed_query 将文本转为向量         │
│         └── 查看向量维度和内容                     │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 二、云端 vs 本地——什么时候需要本地模型

### 2.1 为什么需要本地 Embedding？

| 场景 | 云端是否可行 | 本地方案 |
|------|:----------:|------|
| 数据敏感，不能上传到第三方 | ❌ 不行 | ✅ **本地处理** |
| 没有网络或网络不稳定 | ❌ 不行 | ✅ **离线可用** |
| 高频调用，API 费用高 | ⚠️ 费用问题 | ✅ **一次下载，免费使用** |
| 需要定制化的 Embedding 效果 | ⚠️ 受限于平台 | ✅ **可选不同模型** |
| 学习研究 Embedding 原理 | ⚠️ 黑盒 | ✅ **完全透明** |

### 2.2 本地 Embedding 的核心思路

> 不需要自己从头训练模型。网络上已经有大量**现成可用的开源 Embedding 模型**，直接下载到本地使用即可。

```
本地 Embedding 三步走：

第1步：下载模型文件（从 HuggingFace 或魔搭）
    ↓
第2步：安装运行环境（langchain-huggingface + sentence-transformers）
    ↓
第3步：加载模型 → 传入文本 → 得到向量
```

---

## 三、模型下载——两大平台详解

### 3.1 本节课使用的模型

> **bge-small-zh**（BAAI General Embedding - Small - Chinese）
>
> 由 BAAI（北京智源人工智能研究院）开发的中文文本嵌入模型，体积小、效果好，适合本地使用。

### 3.2 平台一：Hugging Face

**网址**：huggingface.co

| 特点 | 说明 |
|------|------|
| 模型数量 | 最多最全 |
| 更新速度 | 最快 |
| 访问要求 | ⚠️ **需要科学上网** |
| 下载方式 | git clone / transformers 库 / 网页下载 |

**搜索模型**：在 HuggingFace 首页搜索 `bge-small-zh`，进入模型页面。

**下载方式一：git clone（推荐）**

```bash
# 直接克隆整个模型仓库
git clone https://huggingface.co/BAAI/bge-small-zh
```

```bash
# 克隆后的目录结构
bge-small-zh/
├── config.json           # 模型配置
├── model.safetensors     # 模型权重文件
├── tokenizer.json        # 分词器
├── special_tokens_map.json
├── tokenizer_config.json
└── ...其他文件
```

**下载方式二：使用 Transformers 库**

模型页面点击「Use this model」→ 选择「Transformers」→ 会显示 Python 下载代码。

### 3.3 平台二：魔搭（ModelScope）

**网址**：modelscope.cn

| 特点 | 说明 |
|------|------|
| 模型数量 | 丰富（中文模型尤其多） |
| 访问要求 | ✅ **不需要科学上网** |
| 语言 | 中文界面 |
| 下载方式 | SDK / CLI 工具 / git clone |

**搜索模型**：在魔搭首页搜索 `bge-small-zh`。

**下载方式一：SDK 方式**

```bash
pip install modelscope
```

```python
from modelscope import snapshot_download
model_dir = snapshot_download('BAAI/bge-small-zh')
```

**下载方式二：git clone**

```bash
git clone https://www.modelscope.cn/BAAI/bge-small-zh.git
```

### 3.4 两大平台对比

| 对比维度 | Hugging Face | 魔搭（ModelScope） |
|----------|:-----------:|:-----------------:|
| 模型数量 | ⭐⭐⭐⭐⭐ 最多 | ⭐⭐⭐⭐ 丰富 |
| 更新频率 | ⭐⭐⭐⭐⭐ 最快 | ⭐⭐⭐⭐ 快（可能同步） |
| 访问速度 | ⚠️ 需科学上网 | ✅ 国内直接访问 |
| 中文友好 | ⭐⭐⭐ 英文为主 | ⭐⭐⭐⭐⭐ 中文界面 |
| 下载方式 | git / transformers / 网页 | git / SDK / CLI |

> 📌 **选择建议**：能科学上网 → HuggingFace（模型最新最全）。不能科学上网 → 魔搭（国内直连，中文友好）。两个平台都看看，选最快最方便的。

---

## 四、选择模型的关键指标

### 4.1 需要关注的参数

在模型页面向下翻，会看到模型的详细参数。以 `bge-small-zh` 为例：

| 参数 | 值 | 含义 |
|------|-----|------|
| **维度（Dimension）** | 512 | 向量有多少个数字 |
| **序列长度（Max Sequence Length）** | 512 | 一次最多处理多少个 Token |
| **模型大小** | ~100MB | 下载需要多少磁盘空间 |

> ⚠️ 维度在后续数据匹配时非常关键——不同维度的向量不能直接比较。

### 4.2 常见的中文 Embedding 模型

| 模型 | 维度 | 大小 | 特点 |
|------|:---:|:----:|------|
| `bge-small-zh` | 512 | ~100MB | 小体积，快速 |
| `bge-base-zh` | 768 | ~400MB | 中等，平衡 |
| `bge-large-zh` | 1024 | ~1.3GB | 大体积，精度最高 |
| `text2vec-base-chinese` | 768 | ~400MB | 老牌中文模型 |

### 4.3 模型维度速查

```
bge-small-zh  → 512 维（每句话变成 512 个数字）
bge-base-zh   → 768 维（每句话变成 768 个数字）
bge-large-zh  → 1024 维（每句话变成 1024 个数字）

维度越大 → 信息越丰富 → 模型越大 → 推理越慢
```

---

## 五、环境搭建——依赖安装

### 5.1 核心依赖

本地 Embedding 需要以下依赖：

```bash
# 1. LangChain 的 HuggingFace 集成包
pip install langchain-huggingface

# 2. sentence-transformers（会同时安装 torch）
pip install sentence-transformers
```

> 📌 安装 `sentence-transformers` 时会**自动安装 PyTorch（torch）**——这是深度学习框架，默认安装 CPU 版本。

### 5.2 依赖关系图

```
langchain-huggingface
    └── HuggingFaceEmbeddings 类（用来加载模型）

sentence-transformers
    └── torch (PyTorch)
         ├── CPU 版本（默认）
         └── GPU 版本（需手动安装 CUDA 版本）
```

### 5.3 安装后验证

```bash
# 验证 langchain-huggingface
pip show langchain-huggingface

# 验证 sentence-transformers
pip show sentence-transformers

# 验证 torch
python -c "import torch; print(torch.__version__)"

# 验证是否可以用 GPU
python -c "import torch; print(torch.cuda.is_available())"
# → True = GPU 可用，False = 只有 CPU
```

---

## 六、代码实战——加载并使用本地 Embedding

### 6.1 完整代码

```python
# ============================================================
# 1. 导入
# ============================================================
from langchain_huggingface import HuggingFaceEmbeddings

# ============================================================
# 2. 加载本地模型
# ============================================================
embeddings = HuggingFaceEmbeddings(
    # 模型路径（已下载的文件夹路径）
    model_name="./bge-small-zh",
    
    # 模型运行参数
    model_kwargs={
        "device": "cpu"    # "cpu" 或 "cuda"（GPU）
    },
    
    # 编码参数（提升精度的可选配置）
    encode_kwargs={
        "normalize_embeddings": True   # 归一化向量，提升相似度精度
    }
)

# ============================================================
# 3. 测试：将文本转为向量
# ============================================================
query = "如何使用Python？"

# embed_query：将单条文本转为向量
query_vector = embeddings.embed_query(query)

# ============================================================
# 4. 查看结果
# ============================================================
print(f"输入文本：{query}")
print(f"向量维度：{len(query_vector)}")      # → 512（bge-small-zh）
print(f"向量内容（前10个）：{query_vector[:10]}")
```

### 6.2 运行结果

```
输入文本：如何使用Python？
向量维度：512
向量内容（前10个）：[0.0234, -0.0451, 0.0067, -0.0123, 0.0345, 0.0012, -0.0567, 0.0432, -0.0089, 0.0178]

→ 512 个浮点数组成的向量！
→ 计算机可以对这些数字进行计算（比较相似度等）
```

### 6.3 代码逐行解析

#### 导入

```python
from langchain_huggingface import HuggingFaceEmbeddings
```

| 对比 | 云端（上一课） | 本地（本课） |
|------|-------------|------------|
| 导入 | `from langchain_community.embeddings import ZhipuAIEmbeddings` | `from langchain_huggingface import HuggingFaceEmbeddings` |
| 包名 | `langchain-community` | `langchain-huggingface` |
| 需要 API Key | ✅ | ❌ |

#### model_name

```python
model_name="./bge-small-zh"
```

| 参数 | 含义 |
|------|------|
| `"./bge-small-zh"` | 当前目录下的 `bge-small-zh` 文件夹 |
| 也可以是绝对路径 | `/Users/xxx/models/bge-small-zh` |
| 也可以是 HuggingFace 上的模型名 | `"BAAI/bge-small-zh"`（会自动下载） |

#### model_kwargs

```python
model_kwargs={"device": "cpu"}
```

| 参数 | 值 | 含义 |
|------|-----|------|
| `device` | `"cpu"` | 使用 CPU 运算（默认） |
| `device` | `"cuda"` | 使用 GPU（需要 CUDA 版 PyTorch） |

#### encode_kwargs

```python
encode_kwargs={"normalize_embeddings": True}
```

| 参数 | 作用 |
|------|------|
| `normalize_embeddings` | 对向量做归一化处理，提升相似度计算精度 |

> 💡 推荐开启 `normalize_embeddings`，能让向量相似度的计算更准确。

#### embed_query vs embed_documents

```python
# 单条文本 → 单个向量
query_vector = embeddings.embed_query("如何使用Python？")

# 多条文本 → 多个向量（批量）
doc_vectors = embeddings.embed_documents([
    "Python是流行的编程语言",
    "Java是企业级开发语言"
])
```

| 方法 | 参数 | 返回 | 用途 |
|------|------|------|------|
| `.embed_query()` | 一条字符串 | 一个向量（列表） | 查询时使用 |
| `.embed_documents()` | 字符串列表 | 向量列表 | 批量处理文档 |

---

## 七、CPU vs GPU——设备选择详解

### 7.1 默认是 CPU

> 安装 `sentence-transformers` 时**自动安装的 PyTorch 是 CPU 版本**。

```
pip install sentence-transformers
    ↓ 自动安装
torch (CPU 版本)
    ↓
model_kwargs={"device": "cpu"}  ← 默认就是这个
```

### 7.2 何时需要 GPU？

| 场景 | CPU 够用吗？ |
|------|:----------:|
| 少量文本（< 100 条） | ✅ CPU 完全够用 |
| 中等量（100 ~ 1000 条） | ⚠️ CPU 稍慢但可用 |
| 大量文本（> 1000 条） | ❌ CPU 太慢，建议 GPU |
| 生产环境高吞吐 | ❌ 必须 GPU |

> 📌 本课使用 `bge-small-zh` 模型，体积小，CPU 跑并不慢。日常使用 CPU 版本足够了。

### 7.3 如何切换到 GPU

```bash
# 先卸载 CPU 版本的 torch
pip uninstall torch

# 安装 CUDA 版本的 torch（以 CUDA 11.8 为例）
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

```python
# 代码中指定 device
embeddings = HuggingFaceEmbeddings(
    model_name="./bge-small-zh",
    model_kwargs={"device": "cuda"},   # ← 改用 cuda
    encode_kwargs={"normalize_embeddings": True}
)
```

---

## 八、完整流程回顾

```
┌─────────────────────────────────────────────────────────────┐
│              本地文本嵌入模型——完整流程                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Step 1: 下载模型                                            │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ 选平台：HuggingFace（需科学上网）或 魔搭（国内直连）      │    │
│  │ 选模型：bge-small-zh（512维，~100MB）                  │    │
│  │ 下载：git clone 或 SDK                                │    │
│  └──────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  Step 2: 安装依赖                                            │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ pip install langchain-huggingface                    │    │
│  │ pip install sentence-transformers                   │    │
│  └──────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  Step 3: 加载模型                                            │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ embeddings = HuggingFaceEmbeddings(                  │    │
│  │     model_name="./bge-small-zh",                     │    │
│  │     model_kwargs={"device": "cpu"},                  │    │
│  │     encode_kwargs={"normalize_embeddings": True}     │    │
│  │ )                                                    │    │
│  └──────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  Step 4: 使用                                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ vec = embeddings.embed_query("如何使用Python？")       │    │
│  │ print(len(vec))  → 512                               │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 九、云端 Embedding vs 本地 Embedding——全面对比

| 对比维度 | 云端（智谱AI Embedding） | 本地（HuggingFace Embedding） |
|----------|:----------------------:|:----------------------------:|
| **模型位置** | 远程服务器 | **本地文件** |
| **网络依赖** | ✅ 必须有网络 | ❌ **离线可用** |
| **API Key** | ✅ 需要 | ❌ **不需要** |
| **费用** | 按量付费 | **完全免费** |
| **速度** | ⭐⭐⭐⭐ 专用服务器 | ⭐⭐⭐ 取决于本地硬件 |
| **维度** | 1024（embedding-2） | **512（bge-small-zh）** / 768 / 1024 |
| **模型选择** | 平台提供什么用什么 | **开源模型随便选** |
| **数据隐私** | 数据上传到云端 | ⭐⭐⭐⭐⭐ **数据完全在本地** |
| **安装复杂度** | ⭐ 简单（pip install） | ⭐⭐⭐ 需要下载模型+安装框架 |
| **硬件要求** | 几乎无 | 需要 CPU/GPU |
| **适用场景** | 快速开发、常规使用 | **隐私敏感、离线、高频** |

### 9.1 选择决策

```
选择 Embedding 方案？

第一步：数据是否涉及隐私？
    ├── 是 → 本地 Embedding
    └── 否 → 往下看

第二步：是否需要离线使用？
    ├── 是 → 本地 Embedding
    └── 否 → 往下看

第三步：调用量多大？
    ├── 低频（< 100次/天）→ 云端（简单方便）
    └── 高频（> 1000次/天）→ 本地（避免 API 费用）

第四步：需要多高的精度？
    ├── 精度优先 → 云端（1024维或更高）
    └── 速度优先 → 本地 + 小模型（512维）
```

---

## 十、常见问题与排错指南

### 10.1 错误速查表

| 错误/问题 | 原因 | 解决方法 | 优先级 |
|-----------|------|----------|:------:|
| `ModuleNotFoundError: No module named 'langchain_huggingface'` | 未安装包 | `pip install langchain-huggingface` | 🔴高 |
| `ModuleNotFoundError: No module named 'sentence_transformers'` | 未安装 sentence-transformers | `pip install sentence-transformers` | 🔴高 |
| 模型加载时找不到文件 | model_name 路径不对 | 检查模型文件夹是否存在，路径是否正确 | 🔴高 |
| git clone 速度极慢或失败 | HuggingFace 被墙 | 换用魔搭（modelscope.cn）无需科学上网 | 🟡中 |
| `CUDA out of memory` | GPU 显存不够 | 换用 CPU (`device="cpu"`) 或更大显存的 GPU | 🟡中 |
| 向量维度与预期不符 | 加载了不同版本的模型 | 检查 model_name 指向的文件夹是否正确 | 🟡中 |
| CPU 推理太慢 | 模型太大或文本太多 | 换小模型（如 bge-small-zh 512维）或切换 GPU | 🟢低 |

### 10.2 排查流程

```
本地 Embedding 不工作？
    ↓
第一步：检查依赖
    pip list | grep langchain-huggingface
    pip list | grep sentence-transformers
    ↓ 已安装
第二步：检查模型文件
    ls ./bge-small-zh/
    → 能看到 config.json, model.safetensors 等文件？
    ↓ 有
第三步：检查 model_name 路径
    model_name="./bge-small-zh"  ← 路径是否正确？
    可以用绝对路径：model_name="/Users/xxx/models/bge-small-zh"
    ↓ 正确
第四步：检查 device
    GPU 不可用但写了 "cuda"？
    → 改为 "cpu" 试试
```

---

## 十一、课后练习

### 练习一：模型下载

> 从魔搭（modelscope.cn）或 HuggingFace 下载 `bge-small-zh` 模型到本地。

**验收标准：**
- [ ] 模型文件夹存在
- [ ] 文件夹中包含 `config.json` 和 `model.safetensors`
- [ ] 记录下载耗时和模型大小

### 练习二：基础使用

> 加载本地 `bge-small-zh` 模型，将以下 3 句话分别转为向量，记录每条向量的维度：

| 文本 | 向量维度 | 前5个数字（示例） |
|------|:------:|------|
| "人工智能是未来的趋势" | | |
| "今天天气很好" | | |
| "Python是一门优秀的语言" | | |

### 练习三：语义相似度计算

> 将以下 4 句话转为向量，用余弦相似度（可手算或写代码）判断哪两句最接近：

| 编号 | 文本 |
|:----:|------|
| A | "这个产品非常好用" |
| B | "垃圾东西，太差了" |
| C | "质量很棒，推荐购买" |
| D | "一点都不好用" |

**你的预测**：
- A 和 ___ 应该最接近（语义相近）
- B 和 ___ 应该最接近（语义相近）

### 练习四：device 参数实验

> 分别用 `device="cpu"` 和 `device="cuda"`（如果可用）加载模型，用同一段文本转换 100 次，记录平均耗时。

| device | 单次平均耗时 | 100次总耗时 |
|:------:|:----------:|:----------:|
| cpu | | |
| cuda | | |

### 练习五：云端 vs 本地对比

> 用**同一段文本**，分别用云端 Embedding（ZhipuAIEmbeddings, embedding-2）和本地 Embedding（bge-small-zh）生成向量。对比：

| 对比维度 | 云端（智谱） | 本地（bge-small-zh） |
|----------|:----------:|:-------------------:|
| 向量维度 | | |
| 是否需要网络 | | |
| 是否需要 API Key | | |
| 生成耗时 | | |
| 适用场景 | | |

---

## 十二、课程小结

### 12.1 本课核心知识图谱

```
┌────────────────────────────────────────────────────────────┐
│              本地文本嵌入核心知识体系                          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  为什么需要本地 Embedding？                              │
│      ├── 数据隐私：不上传第三方                               │
│      ├── 离线可用：不需要网络                                 │
│      ├── 完全免费：不需要 API 费用                            │
│      └── 自主可控：模型和数据都在本地                          │
│                                                            │
│  2️⃣  两大模型下载平台                                         │
│      ├── HuggingFace：模型最多，需科学上网                     │
│      └── 魔搭 ModelScope：国内直连，中文友好                   │
│         下载方式：git clone / SDK / CLI                      │
│                                                            │
│  3️⃣  选择模型的关键指标                                       │
│      ├── 维度（512/768/1024）：决定向量信息量                  │
│      └── 序列长度（512）：一次处理的最大 Token 数              │
│                                                            │
│  4️⃣  环境搭建                                                │
│      ├── pip install langchain-huggingface                 │
│      └── pip install sentence-transformers（自动装 torch）   │
│                                                            │
│  5️⃣  代码三步走                                              │
│      ├── embeddings = HuggingFaceEmbeddings(model_name=...)│
│      ├── model_kwargs={"device": "cpu"}                   │
│      ├── encode_kwargs={"normalize_embeddings": True}      │
│      └── vec = embeddings.embed_query("文本")               │
│                                                            │
│  6️⃣  CPU vs GPU                                             │
│      ├── pip install 默认装 CPU 版 torch                     │
│      ├── 小模型 + 少量文本 → CPU 够用                         │
│      └── 大模型 + 大量文本 → 需要 GPU（CUDA 版 torch）        │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 12.2 一句话总结

> **本地 Embedding = 下载模型文件 + 安装 langchain-huggingface + 用 HuggingFaceEmbeddings 加载。** 不需要网络，不需要 API Key，数据完全在本地。核心代码就三行：创建 embeddings、指定 device、调用 embed_query。

### 12.3 速记卡

```
┌───────────────────────────────────────────────────────┐
│              本地 Embedding 速记卡                      │
├───────────────────────────────────────────────────────┤
│                                                       │
│  下载模型（二选一）：                                    │
│  git clone https://huggingface.co/BAAI/bge-small-zh   │
│  git clone https://www.modelscope.cn/BAAI/bge-small-zh│
│                                                       │
│  安装依赖：                                             │
│  pip install langchain-huggingface                    │
│  pip install sentence-transformers                   │
│                                                       │
│  使用模型：                                             │
│  embeddings = HuggingFaceEmbeddings(                  │
│      model_name="./bge-small-zh",                    │
│      model_kwargs={"device": "cpu"},                 │
│      encode_kwargs={"normalize_embeddings": True}    │
│  )                                                    │
│  vec = embeddings.embed_query("文本")                  │
│  # → 512 维向量                                        │
│                                                       │
└───────────────────────────────────────────────────────┘
```

### 12.4 系列课程定位

```
第一课：环境搭建              第九课：BufferMemory
第二课：模型选型              第十课：WindowMemory
第三课：切换模型              第十一课：TokenBufferMemory
第四课：Ollama 本地           第十二课：SummaryBufferMemory
第五课：提示词模板            第十三课：文本嵌入（云端）
第六课：输出解析器            第十四课：文本嵌入（本地）🆕
第七课：链式调用              后续：向量数据库 / RAG
第八课：流式输出
```

---

*本教学文档基于陈泽鹏老师视频课程（本地文本嵌入模型）整理编写。*  
*本文档涵盖 HuggingFace/魔搭双平台模型下载、langchain-huggingface 环境搭建、本地模型加载、CPU/GPU 设备选择及与云端 Embedding 的全面对比。*
