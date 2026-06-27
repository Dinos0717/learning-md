# LangChain 最新版本 V1.x 中 ReAct 风格 Agent API 接口服务（带 Skill 按需加载）

## 1、案例介绍

本期视频为大家分享的是在 **11_AgentAPIServer** 能力不变的前提下，实现「带 Skill 按需加载」的 Agent API 服务      

涉及到的源码、操作说明文档等全部资料都是开源分享给大家的，大家可以在本期视频置顶评论中获取免费资料链接进行下载                     

本期用例的核心功能包含：    

- Agent 按需加载 skill 技能，每个 skill 必包括 `SKILL.md` 、 可选可执行的脚本(*.py)       

### Skill设计思想

Skill 的设计思想可以概括为三句话：**按需加载、说明即能力、工具化接入**   

1. **按需加载（Progressive Disclosure）**
- **问题：** 如果把所有“摘要 / 翻译 / 写 SQL …”的详细说明都塞进系统提示，会占很多 token，成本高、上下文也容易乱
- **做法：** 系统提示里只告诉 Agent“你有 load_skill 工具，可用技能有 summarize、translate”。当用户真的问“总结一下这段话”或“翻译成英文”时，Agent 再调用 load_skill("summarize") 或 load_skill("translate")，把对应 SKILL.md 的全文拉进对话
- **效果：** 平时不占 token，只有用到某技能时才加载该技能的说明

2. **说明即能力（Prompt-Driven Specialization）**
- **思想：** 一个“技能”本质上是一段**专门说明**：在什么场景用、输入输出是什么、要遵循什么步骤和原则。Agent 不需要为“摘要”单独写死代码，只要按这段说明执行即可
- **实现：** 每个技能必须包括一个 SKILL.md：
    - Frontmatter：name、description（给 Agent 做“要不要用这个技能”的匹配）
    - 正文：步骤、原则、注意事项（给 Agent 做“怎么用”的执行指南）
- **好处：** 
    - 改能力 = 改文档，不必改 Python
    - 新技能 = 新目录 + 新 SKILL.md + 可选的可执行脚本，load_skill 自动发现，扩展简单

3. **工具化接入（Skill as a Tool）**
- **思想：** 不改变现有 Agent 架构（create_agent + tools + HITL），把“技能”当成一种**特殊工具**：
    - 工具名：load_skill
    - 输入：skill_name（如 summarize、translate）
    - 输出：该技能的完整说明文本（即 SKILL.md 内容）
- **效果：** 
    - Agent 的决策流程不变：先想“用户要摘要 → 我该用哪个工具？”→ 选 load_skill("summarize")，拿到说明后再按说明生成摘要


## 2、准备工作

### 2.1 集成开发环境搭建

anaconda提供python虚拟环境,pycharm提供集成开发环境          

具体参考如下视频:  
【大模型应用开发-入门系列】集成开发环境搭建-开发前准备工作  
[https://www.bilibili.com/video/BV1nvdpYCE33/](https://www.bilibili.com/video/BV1nvdpYCE33/)  
[https://youtu.be/KyfGduq5d7w](https://youtu.be/KyfGduq5d7w)                        

### 2.2 大模型LLM服务接口调用方案

(1)gpt大模型等国外大模型使用方案  
国内无法直接访问，可以使用Agent的方式，具体Agent方案自己选择  
这里推荐大家使用:[https://nangeai.top/register?aff=Vxlp](https://nangeai.top/register?aff=Vxlp)          

(2)非gpt大模型方案 OneAPI方式或大模型厂商原生接口          

(3)本地开源大模型方案(Ollama方式)            

具体参考如下视频:  
【大模型应用开发-入门系列】大模型LLM服务接口调用方案  
[https://www.bilibili.com/video/BV1BvduYKE75/](https://www.bilibili.com/video/BV1BvduYKE75/)  
[https://youtu.be/mTrgVllUl7Y](https://youtu.be/mTrgVllUl7Y)                           

## 3、项目初始化

关于本期视频的项目初始化请参考本系列的入门案例那期视频，视频链接地址如下:             

【EP01_快速入门用例】2026必学！LangChain最新V1.x版本全家桶LangChain+LangGraph+DeepAgents开发经验免费分享  
[https://youtu.be/0ixyKPE2kHQ](https://youtu.be/0ixyKPE2kHQ)  
[https://www.bilibili.com/video/BV1EZ62BhEbR/](https://www.bilibili.com/video/BV1EZ62BhEbR/)               

### 3.1 下载源码

大家可以在本期视频置顶评论中获取免费资料链接进行下载              

### 3.2 构建项目

使用pycharm构建一个项目，为项目配置虚拟python环境  
项目名称：LangChainV1xTest  
虚拟环境名称保持与项目名称一致                                                      

### 3.3 将相关代码拷贝到项目工程中

将下载的代码文件夹中的文件全部拷贝到新建的项目根目录下                             

### 3.4 安装项目依赖

新建命令行终端，在终端中运行如下指令进行安装               

```bash
pip install langchain==1.2.1
pip install langchain-openai==1.1.6   
pip install concurrent-log-handler==0.9.28     
pip install langgraph-checkpoint-postgres==3.0.2 
pip install langchain-text-splitters==1.1.0 
pip install langchain-community==0.4.1
pip install langchain-chroma==1.1.0
pip install pypdf==6.6.0
pip install mcp==1.25.0  
pip install langchain-mcp-adapters==0.2.1
pip install pymilvus==2.6.6
pip install fastapi==0.115.14
pip install gradio==6.5.1

```

**注意:** 建议先使用这里列出的对应版本进行本项目脚本的测试，避免因版本升级造成的代码不兼容。测试通过后，可进行升级测试                                 

## 4、功能测试

### 4.1 使用Docker方式运行PostgreSQL数据库和Milvus向量数据库

进入官网 [https://www.docker.com/](https://www.docker.com/) 下载安装Docker Desktop软件并安装，安装完成后打开软件                      

打开命令行终端，运行如下指令进行部署                     

- 进入到 postgresql 下执行 `docker-compose up -d` 运行 PostgreSQL 服务                             
- 进入到 milvus 下执行 `docker-compose up -d` 运行 Milvus 服务

运行成功后可在Docker Desktop软件中进行管理操作或使用命令行操作或使用指令                           

PostgreSQL数据库可使用数据库客户端软件远程登陆进行可视化操作，这里推荐使用免费的DBeaver客户端软件              

- DBeaver 客户端软件下载链接: [https://dbeaver.io/download/](https://dbeaver.io/download/)

### 4.2 功能测试

```bash
# 1、Milvus向量数据库测试
cd milvus
python 01_create_database.py
python 02_create_collection.py
python 03_insert_data.py
python 04_basic_earch.py
python 05_full_text_search.py
python 06_hybrid_search.py

# 2、MCP Server测试
cd rag_mcp
python mix_text_search.py
python mcp_start.py
python rag_mcp_server_test.py

# 3、Agent测试
python agent_api.py
python api_test.py
python gradio_ui.py

```     
