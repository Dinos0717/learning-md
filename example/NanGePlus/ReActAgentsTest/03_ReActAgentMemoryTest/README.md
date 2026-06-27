# 1、项目介绍                  
## 1.1、主要内容
本期视频为大家分享如何在LangGraph提供的ReAct架构的Agent中使用Memory                
(1)Short-Term Memory(短期记忆)              
也称为线程级记忆，在LangGraph中与特定对话线程（thread）或会话（session）绑定的临时状态信息                
这种记忆仅在当前会话或线程的生命周期内有效，适合处理短时间内需要快速访问的上下文信息                      
(2)Long-Term Memory(长期记忆)                 
也称为跨线程记忆，在LangGraph中能够在不同会话或线程之间持久化存储和检索的信息              
这种记忆允许Agent记住用户的历史交互、偏好或关键信息，从而支持更个性化和智能化的交互                    
与短期记忆不同，长期记忆可以在多个会话或线程之间共享和访问，适合存储需要长期保留的信息，如用户偏好、历史行为或学习到的知识                 
关于Memory部分的介绍，大家可以参考官方文档链接如下所示:                      
https://langchain-ai.github.io/langgraph/agents/memory/                      
https://langchain-ai.github.io/langgraph/how-tos/create-react-agent-manage-message-history/                             

## 1.2 LangGraph介绍 
LangGraph 是由 LangChain 团队开发的一个开源框架，旨在帮助开发者构建基于大型语言模型（LLM）的复杂、有状态、多主体的应用            
官方文档:https://langchain-ai.github.io/langgraph/            
关于LangGraph大家可以参考如下项目，里面有详细的源码资料和视频分享:               
https://github.com/NanGePlus/LangGraphChatBot                        

## 1.3 自定义工具
使用python实现的一个模拟酒店预订的工具book_hotel                                    
其需传入的参数为:{hotel_name}                        


# 2、前期准备工作
## 2.1 集成开发环境搭建  
anaconda提供python虚拟环境,pycharm提供集成开发环境                                              
**具体参考如下视频:**                        
【大模型应用开发-入门系列】03 集成开发环境搭建-开发前准备工作                         
https://youtu.be/KyfGduq5d7w                     

## 2.2 大模型LLM服务接口调用方案
(1)gpt大模型等国外大模型使用方案                  
国内无法直接访问，可以使用代理的方式，具体代理方案自己选择                        
这里推荐大家使用:https://nangeai.top/register?aff=Vxlp                        
(2)非gpt大模型方案 OneAPI方式或大模型厂商原生接口                                              
(3)本地开源大模型方案(Ollama方式)                                              
**具体参考如下视频:**                                           
【大模型应用开发-入门系列】04 大模型LLM服务接口调用方案                    
https://youtu.be/mTrgVllUl7Y                           


# 3、项目初始化
## 3.1 下载源码
GitHub或Gitee中下载工程文件到本地，下载地址如下：                
https://github.com/NanGePlus/ReActAgentsTest                                                                                 
https://gitee.com/NanGePlus/ReActAgentsTest                                                                                     

## 3.2 构建项目 
使用pycharm构建一个项目，为项目配置虚拟python环境                          
项目名称：ReActAgentsTest                                                         
虚拟环境名称保持与项目名称一致                             

## 3.3 将相关代码拷贝到项目工程中           
将下载的代码文件夹中的文件全部拷贝到新建的项目根目录下                             

## 3.4 安装项目依赖                                  
新建命令行终端，在终端中运行如下指令进行安装                        
pip install langgraph==0.4.5                               
pip install langchain==0.3.25                                    
pip install langchain-openai==0.3.17                                                                 
pip install langchain-mcp-adapters==0.1.0                                       
**注意:** 建议先使用要求的对应版本进行本项目测试，避免因版本升级造成的代码不兼容。测试通过后，可进行升级测试                               


# 4、功能测试 
## (1)使用Docker的方式运行PostgreSQL数据库                   
进入官网 https://www.docker.com/ 下载安装Docker Desktop软件并安装，安装完成后打开软件                
打开命令行终端，cd 03_ReActAgentMemoryTest文件夹下，PostgreSQL的docker配置文件为docker-compose.yml             
运行 docker-compose up -d 命令后台启动PostgreSQL数据库服务。运行成功后可在Docker Desktop软件中进行管理操作或使用命令行操作或使用指令        
使用数据库客户端软件远程登陆进行可视化操作，这里使用Navicat客户端软件                           

## (2)功能测试      
进入03_ReActAgentMemoryTest文件夹下中运行脚本进行测试，在运行脚本之前先安装如下依赖                       
pip install langgraph-checkpoint-postgres==2.0.21                                


                   

         
 