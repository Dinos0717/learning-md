# 27_28 Action 辅助使用 Docker 与 GitHub Package

> 📅 生成日期: 2026-07-18 | 🎯 级别: M 级 | ⏱️ 录音时长: ~18 分钟 | 📏 文档规模: 2,960+ 行
> 🏷️ 标签: `GitHub Action` `Docker` `镜像拉取` `阿里云ACR` `GitHub Package` `npm` `包管理`

---

## 📑 目录

### 第一部分：Action 辅助使用 Docker

- [一、课程引入与 Docker Linux 安装](#一课程引入与-docker-linux-安装)
  - [1.1 课程背景与核心问题](#11-课程背景与核心问题)
  - [1.2 解决方案：GitHub Action 助力国内 Docker 使用](#12-解决方案github-action-助力国内-docker-使用)
  - [1.3 Docker Linux 安装 Step-by-Step](#13-docker-linux-安装-step-by-step)
  - [1.4 本节小结](#14-本节小结)
- [二、Docker Windows 与 Mac 安装](#二docker-windows-与-mac-安装)
  - [2.1 Windows 安装前提：WSL 2 与虚拟机平台](#21-windows-安装前提wsl-2-与虚拟机平台)
  - [2.2 WSL 2 安装与配置](#22-wsl-2-安装与配置)
  - [2.3 Docker Desktop 安装（Windows）](#23-docker-desktop-安装windows)
  - [2.4 Mac Docker Desktop 安装](#24-mac-docker-desktop-安装)
  - [2.5 安装后验证](#25-安装后验证)
- [三、方案一：阿里云私有仓库镜像转存](#三方案一阿里云私有仓库镜像转存)
  - [3.1 方案概述与设计思路](#31-方案概述与设计思路)
  - [3.2 本节目标](#32-本节目标)
  - [3.3 前置准备](#33-前置准备)
  - [3.4 Step-by-Step：完整配置流程](#34-step-by-step完整配置流程)
  - [3.5 验证结果：阿里云控制台确认](#35-验证结果阿里云控制台确认)
  - [3.6 国内服务器拉取镜像](#36-国内服务器拉取镜像)
  - [3.7 排错指南](#37-排错指南)
  - [3.8 实际项目应用案例：RSS 项目改造](#38-实际项目应用案例rss-项目改造)
  - [3.9 方案总结](#39-方案总结)
- [四、方案二至五：镜像站、离线下载、一键脚本、Cloudflare Worker](#四方案二至五镜像站离线下载一键脚本cloudflare-worker)
  - [4.1 方案二：配置镜像站](#41-方案二配置镜像站)
  - [4.2 方案三：GitHub Action 离线镜像下载](#42-方案三github-action-离线镜像下载)
  - [4.3 方案四：一键脚本自动测速下载](#43-方案四一键脚本自动测速下载)
  - [4.4 方案五：Cloudflare Worker 自建镜像加速](#44-方案五cloudflare-worker-自建镜像加速)
  - [4.5 方案对比与选择](#45-方案对比与选择)
- [五、Docker 镜像搜索与第一部分收尾](#五docker-镜像搜索与第一部分收尾)
  - [5.1 Docker 镜像搜索网站](#51-docker-镜像搜索网站)
  - [5.2 Docker 第一部分内容回顾](#52-docker-第一部分内容回顾)
  - [5.3 课程过渡：进入 GitHub Package](#53-课程过渡进入-github-package)

### 第二部分：GitHub Package

- [六、GitHub Package 概述与项目初始化](#六github-package-概述与项目初始化)
  - [6.1 GitHub Package 是什么](#61-github-package-是什么)
  - [6.2 免费额度详解](#62-免费额度详解)
  - [6.3 项目初始化 Step-by-Step](#63-项目初始化-step-by-step)
  - [6.4 本节知识图谱](#64-本节知识图谱)
- [七、发布包到 GitHub Package](#七发布包到-github-package)
  - [7.1 发布流程概述](#71-发布流程概述)
  - [7.2 创建 Workflow 文件](#72-创建-workflow-文件)
  - [7.3 配置 package.json](#73-配置-packagejson)
  - [7.4 提交代码并创建 Release](#74-提交代码并创建-release)
  - [7.5 验证发布结果](#75-验证发布结果)
- [八、使用 GitHub Package 的包与课程总结](#八使用-github-package-的包与课程总结)
  - [8.1 使用 GitHub Package 的两步配置概览](#81-使用-github-package-的两步配置概览)
  - [8.2 Step 1：配置 package.json 的 dependencies](#82-step-1配置-packagejson-的-dependencies)
  - [8.3 Step 2：创建 .npmrc 文件 — 仓库地址声明](#83-step-2创建-npmrc-文件--仓库地址声明)
  - [8.4 Step 3：创建 Personal Access Token](#84-step-3创建-personal-access-token)
  - [8.5 Step 4：npm install 验证](#85-step-4npm-install-验证)
  - [8.6 排错指南](#86-排错指南)
  - [8.7 两步配置总结](#87-两步配置总结)
- [全课程回顾总结](#全课程回顾总结)
- [课后练习](#课后练习)

---

## 一、课程引入与 Docker Linux 安装

### 1.1 课程背景与核心问题

#### 📖 背景

2024 年以来，国内多家知名 Docker 镜像加速站点——如中科大镜像站、阿里云容器镜像服务、DaoCloud 加速器等——相继宣布下架或停止对公提供服务。对于国内开发者而言，这不仅仅是"下载速度变慢"的问题，而是 `docker pull` 直接报错、镜像根本无法拉取的问题。

面对这一困境，传统的"换镜像源"方案已不再可靠。我们需要一套新的方法论来解决 Docker 在国内的使用问题，而 GitHub Action 正是破局的关键——通过 Action 的自动化能力，我们可以在境外的 GitHub Runner 上完成下载和打包，再将结果通过 Release 页面分发给国内用户。

> ⚠️ **注意事项**：如果你当前的 Docker `pull`/`push` 还能正常使用，也不代表高枕无忧。镜像站下架是大趋势，提早掌握本课程的方案，才能在服务彻底中断时从容应对。

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 理解国内 Docker 使用的三大核心痛点（安装、拉取、搜索）
> - [ ] 掌握通过 GitHub Action 项目在 Linux 上一键安装 Docker 的完整流程
> - [ ] 区分 GitHub 与 Gitee 双地址方案，在网络受限时灵活切换
> - [ ] 成功启动 Docker 服务并验证安装结果

#### 📋 课程的三大核心问题

本期课程围绕三个大家最关心的问题展开：

| 序号 | 核心问题 | 痛点描述 | 解决思路 |
|---|---|---|---|
| 1 | **如何安装 Docker？** | 官网下载慢或无法访问，镜像站已不可用 | GitHub Action 每日同步官方安装脚本，国内用户通过 Release 下载 |
| 2 | **如何拉取镜像（pull）？** | `docker pull` 直接失败，镜像无法下载 | 后续章节详解 |
| 3 | **如何查找镜像名称？** | 不知道需要的镜像叫什么、去哪里搜索 | 后续章节详解 |

> 💡 **核心洞见**：这三个问题恰好构成了一条完整的 Docker 使用链条——先装好 Docker，然后找到需要的镜像，最后拉取到本地。任何一个环节卡住，整个流程都走不通。本课程将逐一打通这三个环节。

### 1.2 解决方案：GitHub Action 助力国内 Docker 使用

#### 🧠 直观理解

传统的"改镜像源"方案相当于在国内找一条"近路"去 Docker Hub。现在这条"近路"被封了，我们的新思路是：让一台在海外的机器（GitHub Action 的 Runner）帮我们跑腿，把我们需要的东西下载好，再通过 GitHub 仓库或 Release 页面传回国内。

简而言之：**让 GitHub Action 做你的海外代理**。

#### 🔄 工作流程

```
┌──────────────────────────────────────────────────────────────────┐
│                     GitHub Action 工作流                           │
│                                                                  │
│  ┌────────────────┐   定时触发 (cron)    ┌──────────────────┐    │
│  │   schedule      │───────────────────▶│ 下载最新官方脚本   │    │
│  │  (每天执行)      │                    │ get.docker.com    │    │
│  └────────────────┘                    └────────┬─────────┘    │
│                                                 │               │
│                                                 ▼               │
│                                        ┌──────────────────┐     │
│                                        │  保存到 Release    │     │
│                                        │  linux.sh         │     │
│                                        └────────┬─────────┘     │
│                                                 │               │
│                   ┌─────────────────────────────┼─────────┐     │
│                   │                             │         │     │
│                   ▼                             ▼         │     │
│          ┌────────────────┐           ┌────────────────┐  │     │
│          │  GitHub 地址    │           │  Gitee 地址     │  │     │
│          │ (境外稳定访问)   │           │ (国内备选加速)  │  │     │
│          └───────┬────────┘           └───────┬────────┘  │     │
│                  │                            │           │     │
└──────────────────┼────────────────────────────┼───────────┘     │
                   │                            │                 │
                   └─────────────┬──────────────┘                 │
                                 ▼                                │
                      ┌──────────────────┐                       │
                      │  国内用户执行安装   │                       │
                      │  curl script | sh │                       │
                      └──────────────────┘                       │
```

#### 📖 详细解释

这个方案的核心在于 **GitHub Action 的定时触发器（schedule）**。下面按步骤分析整个流程的设计思路：

1. **定时执行**：在项目仓库中配置一个 GitHub Action workflow，使用 `schedule` 事件（cron 表达式）让它每天自动运行一次。**为什么每天执行？** 因为 Docker 官方安装脚本 `get.docker.com` 会不定期更新（例如新增对某个 Linux 发行版的支持、修复安全漏洞），每天同步一次可以保证仓库中的脚本始终与官方最新版本一致。

2. **境外下载**：GitHub Action 的 Runner 运行在境外的服务器上，可以直接访问 `get.docker.com`，不受国内网络限制。**为什么 Runner 能直接访问？** 因为 Runner 位于 GitHub 的全球基础设施中，不会被国内的 DNS 污染或 IP 屏蔽所影响。Action 将官方的一键安装脚本下载下来，保存为 `linux.sh`。

3. **发布到 Release**：脚本被上传到仓库的 Release 页面。**为什么用 Release 而不是直接放仓库里？** Release 提供了固定的下载链接和版本管理，用户可以通过 `/releases/latest/download/linux.sh` 这样的链接始终拿到最新版本，而不需要记住具体的版本号。

4. **用户安装**：国内用户只需要执行一条 `curl` 命令，从 Release 页面下载脚本并通过管道传给 `sh`，即可完成 Docker 的一键安装。整个过程对用户来说只有一行命令。

> 💡 **核心洞见**：这是 GitHub Action "解决实际问题"的一个完美案例。Action 不只是用来做 CI/CD（持续集成/持续部署）的——它本质上是一个**免费的、可编程的境外服务器**，拥有 2000-3000 分钟/月的免费执行额度（公开仓库无限制）。当你遇到"国内无法访问某个海外资源"的问题时，可以优先思考：能不能用 Action 帮你下载？

> 🔗 **关联知识**：本课程后续章节中，同样的思路还会用于"拉取 Docker 镜像"和"搜索镜像名称"——用 Action 在境外帮你完成，再传递回国内。整个课程的方法论一以贯之。

### 1.3 Docker Linux 安装 Step-by-Step

#### 🎯 目标

在 Linux 服务器上通过一键命令完成 Docker 的安装、启动与完整验证。

#### 🏗️ 前置准备

| 条件 | 说明 |
|---|---|
| 操作系统 | Linux（CentOS 7+、Ubuntu 18.04+、Debian 10+ 等主流发行版均可） |
| 用户权限 | 具有 `sudo` 权限的普通用户或 `root` 用户 |
| 网络 | 能访问 GitHub 或 Gitee（至少其一） |
| 终端 | SSH 连接到服务器，或直接在服务器本地终端操作 |

#### 💻 Step-by-Step

**Step 1: 执行 Docker 一键安装命令**

将以下命令复制到终端中执行。该命令会自动完成 Docker CE（社区版）及其依赖的安装，整个过程约 1-3 分钟。

```bash
# 方式一：通过 GitHub 地址安装（推荐首选）
# 从 GitHub Release 页面下载官方安装脚本并执行
curl -fsSL https://github.com/<项目地址>/releases/latest/download/linux.sh | sudo sh
```

> 这条命令拆解如下：
> - `curl -fsSL`：`-f` 遇到 HTTP 错误直接失败返回非 0 退出码；`-s` 静默模式不输出进度条；`-S` 配合 `-s` 使用时出错仍显示错误信息；`-L` 跟随 HTTP 重定向。
> - `|`：将下载的脚本内容通过管道传递给右侧命令。
> - `sudo sh`：以管理员权限执行脚本。脚本内部会自动检测你的 Linux 发行版并执行对应的安装步骤。

> ❓ **常见疑问**：为什么不用 `wget`？`curl` 和 `wget` 都能下载文件，但 `curl` 在大多数 Linux 发行版中预装率更高。此外 `curl -fsSL` 的参数组合能提供更精细的静默+错误处理，在管道场景中更可靠。

如果因为网络问题无法访问 GitHub，可以使用 Gitee（码云）上的镜像地址，两者下载的脚本内容完全一致：

```bash
# 方式二：通过 Gitee 地址安装（国内网络备选）
# 脚本内容与方式一完全相同，仅下载源地址不同
curl -fsSL https://gitee.com/<项目地址>/releases/latest/download/linux.sh | sudo sh
```

> ⚠️ **注意事项**：GitHub 与 Gitee 两个地址下载的脚本**内容完全一致**（都是官方 `get.docker.com` 脚本的定时同步版本），唯一的区别在于**下载源**。Gitee 是国内 Git 托管平台，从国内访问延迟更低、更稳定。优先尝试 GitHub 地址，遇到超时或连接失败就立即切换 Gitee。

**Step 2: 启动 Docker 服务**

安装脚本执行完毕后，Docker 已安装到系统中，但 Docker 守护进程不会自动启动，需要手动启动。

```bash
# 启动 Docker 守护进程
sudo systemctl start docker

# 设置 Docker 开机自启（强烈推荐，避免每次重启服务器后手动启动）
sudo systemctl enable docker
```

> 如果你的 Linux 发行版不使用 `systemd`（如较老的 CentOS 6 或某些精简版系统），可改用 `service` 命令：
> ```bash
> sudo service docker start
> ```

**Step 3: 验证安装结果**

通过以下三步递进验证，确保 Docker 已完整安装并可正常使用。

```bash
# 验证 1：查看 Docker 版本信息
docker --version
# 预期输出类似：Docker version 24.0.7, build afdd53b

# 验证 2：确认 Docker 服务运行状态
sudo systemctl status docker
# 预期输出中包含：Active: active (running) — 表示服务正在运行

# 验证 3：运行 Hello World 容器（端到端验证）
sudo docker run hello-world
```

`hello-world` 容器的预期输出如下：

```
Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
 3. The Docker daemon created a new container from that image...
 4. The Docker daemon streamed that output to the Docker client...

For more examples and ideas, visit:
 https://docs.docker.com/get-started/
```

> 💡 **核心洞见**：`docker run hello-world` 是一个**端到端**的验证——它不仅检查 Docker 是否安装，还验证了 Docker 能否从镜像仓库拉取镜像、能否创建并启动容器、能否将容器输出传回客户端。四个步骤全部通过，才说明 Docker 安装完全成功。如果这一步卡在 "Unable to find image" 或 "pull access denied"，说明安装成功但网络拉取仍有问题——这正是课程后续章节要解决的核心问题之二。

#### 🐛 排错指南

---

**🐞 问题 1：执行安装脚本时提示网络连接失败**

**🚨 现象**
```
curl: (7) Failed to connect to github.com port 443: Connection timed out
```

**🔍 原因分析**

`curl` 无法连接到 GitHub 服务器。在国内网络环境下，GitHub 的某些 IP 可能被间歇性阻断或 DNS 解析异常，导致连接超时。

**✅ 解决方案**

立即切换到 Gitee 备选地址。两种方式的脚本内容完全一致，功能上没有任何差异。

```bash
# 切换到 Gitee 地址重新执行
curl -fsSL https://gitee.com/<项目地址>/releases/latest/download/linux.sh | sudo sh
```

**📝 经验总结**

在国内开发环境下，**GitHub 为主、Gitee 为备**是贯穿整个课程的核心理念。每次遇到 GitHub 不可达时，第一反应就是切 Gitee。老师特意维护了两个地址版本，就是为了应对国内网络不稳定的实际场景。

---

**🐞 问题 2：执行 `docker` 命令时提示权限不足**

**🚨 现象**
```
Got permission denied while trying to connect to the Docker daemon socket
at unix:///var/run/docker.sock
```

**🔍 原因分析**

安装 Docker 后，默认只有 `root` 用户和 `docker` 用户组的成员才能与 Docker 守护进程（通过 Unix socket `/var/run/docker.sock`）通信。当前普通用户不在 `docker` 组中，因此被拒绝访问。

**✅ 解决方案**

将当前用户添加到 `docker` 用户组，然后刷新用户组权限使其生效。

```bash
# 将当前用户加入 docker 组
sudo usermod -aG docker $USER

# 刷新当前 shell 的用户组权限（无需退出重登）
newgrp docker

# 再次验证——这次不需要 sudo
docker run hello-world
```

**📝 经验总结**

`Permission denied` 是 Linux 初装 Docker 后几乎必遇的问题。记住一行命令即可：`sudo usermod -aG docker $USER`。注意 `-aG` 是追加（append）到附加组，如果误写成 `-G`（覆盖），用户会从原有组（如 `sudo`）中被移除，可能造成更严重的问题。

---

**🐞 问题 3：Docker 守护进程无法启动**

**🚨 现象**
```
Job for docker.service failed because the control process exited with error code.
See "systemctl status docker.service" and "journalctl -xe" for details.
```

**🔍 原因分析**

常见原因包括：服务器上之前通过 `yum`/`apt` 安装过旧版 Docker（发行版自带版本），残留的配置文件或依赖与新版本冲突，导致新版 Docker 守护进程无法正常启动。

**✅ 解决方案**

先彻底移除旧版本残留，再重新安装。

```bash
# 移除旧版 Docker（Ubuntu/Debian）
sudo apt-get remove docker docker-engine docker.io containerd runc 2>/dev/null

# 移除旧版 Docker（CentOS/RHEL）
# sudo yum remove docker docker-client docker-client-latest docker-common 2>/dev/null

# 重新执行一键安装脚本
curl -fsSL https://gitee.com/<项目地址>/releases/latest/download/linux.sh | sudo sh

# 再次启动
sudo systemctl start docker
sudo systemctl status docker
```

**📝 经验总结**

新装 Docker 前，建议先在服务器上执行一次旧版本清理。特别是通过云服务商模板创建的服务器，可能预装了旧版 Docker。`docker --version` 能正常输出版本号并不意味着服务可以正常启动——版本冲突通常体现在守护进程启动阶段。

### 1.4 本节小结

> 💡 **一句话总结**：面对国内 Docker 镜像站纷纷下架的困境，我们通过 GitHub Action 定时从官方同步安装脚本，配合 GitHub + Gitee 双地址策略，使国内用户也能通过一行命令完成 Docker 的完整安装与验证。

> 🔗 **下一步**：本节我们完成了 Linux 系统上的 Docker 安装。对于使用 Windows 和 macOS 的开发者，下一章将介绍对应操作系统的安装方法（← 合并时替换为锚点链接）。

## 二、Docker Windows 与 Mac 安装

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 理解 WSL 2 和虚拟机平台在 Windows Docker 中的角色
> - [ ] 在 Windows 上完成 WSL 2 的安装与配置
> - [ ] 在 Windows 上安装 Docker Desktop
> - [ ] 区分 Mac 的 Apple Silicon (arm64) 和 Intel (x86) 架构并安装对应版本
> - [ ] 独立完成安装后验证

### 2.1 Windows 安装前提：WSL 2 与虚拟机平台

#### 🧠 直观理解

Docker 最初是为 Linux 内核设计的——它依赖 Linux 的 cgroup 和 namespace 等内核特性来实现容器隔离。Windows 本身没有这些 Linux 内核能力，因此需要一个"翻译层"：**WSL 2（Windows Subsystem for Linux 2）** 提供了一个完整的 Linux 内核运行在 Windows 之上，让 Docker 以为自己在 Linux 上工作。

可以这样类比：Docker 是一辆燃油车（需要 Linux 内核），Windows 是一条没有加油站的道路。WSL 2 就是在这条路上专门为这辆车建造的一个加油站——它提供一个微型的完整 Linux 内核，让 Docker 能正常"加油"运行。而**虚拟机平台**则是建造这个加油站的土地许可证——没有它，WSL 2 就无法使用 Hyper-V 虚拟化架构来运行 Linux 内核。

> 💡 **核心洞见**：Docker Desktop for Windows 不直接运行容器，而是借助 WSL 2 提供的轻量级 Linux 虚拟机来运行。容器实际上跑在 WSL 2 里面的 Linux 内核上，而不是 Windows 内核上。这解释了为什么必须先装 WSL 2。

#### 📖 详细解释

Docker Desktop for Windows 的技术栈层次：

```
┌──────────────────────────────────┐
│          Docker Desktop           │  ← 你看到的 GUI 应用
├──────────────────────────────────┤
│          Docker Engine            │  ← 容器运行时（Linux 原生）
├──────────────────────────────────┤
│      WSL 2 (Linux 内核)           │  ← 完整 Linux 内核，轻量级 VM
├──────────────────────────────────┤
│    虚拟机平台 / Hyper-V           │  ← Windows 虚拟化底层
├──────────────────────────────────┤
│         Windows 10/11             │  ← 宿主机操作系统
└──────────────────────────────────┘
```

两个必要组件的职责：

| 组件 | 角色 | 为什么需要它 |
|---|---|---|
| **Windows Subsystem for Linux (WSL 2)** | 提供完整 Linux 内核 | Docker 依赖 Linux 内核的 cgroup、namespace、OverlayFS 等特性，Windows 内核不支持 |
| **虚拟机平台** | 启用 Hyper-V 虚拟化架构 | WSL 2 本质是一个轻量级 Hyper-V 虚拟机；没有虚拟化平台，WSL 2 无法启动 |

> ❓ **常见疑问**：为什么 Docker Desktop 不直接像 Linux 那样运行容器？
>
> 因为容器不是真正的"虚拟化"，它只是进程隔离。Linux 容器的隔离依赖于 Linux 内核自身的 cgroup 和 namespace 机制。Windows 内核没有这些接口，所以必须借助 WSL 2 提供的 Linux 内核来运行容器。

#### 💻 第一步：启用 Windows 必要功能

**操作步骤**：

1. 在任务栏搜索框中输入"启用或关闭 Windows 功能"，点击打开
2. 在列表中向下滚动到底部
3. 勾选以下两项：
   - **适用于 Linux 的 Windows 子系统**（Windows Subsystem for Linux）
   - **虚拟机平台**（Virtual Machine Platform）
4. 点击"确定"，系统会自动安装所需组件
5. 按照提示**重新启动电脑**

```
Windows 功能对话框：
┌──────────────────────────────────────────┐
│  启用或关闭 Windows 功能                   │
│                                           │
│  ☑ Hyper-V                                │
│  ☑ Windows 虚拟机监控程序平台               │
│  ☑ 适用于 Linux 的 Windows 子系统    ← 勾选 │
│  ☑ 虚拟机平台                       ← 勾选 │
│  ☐ Telnet Client                          │
│  ...                                      │
│                                           │
│            [确定]  [取消]                  │
└──────────────────────────────────────────┘
```

> ⚠️ **注意事项**：重启是必须的——这两个功能涉及内核级组件的加载，不重启无法生效。确认重启前请保存好所有工作。

> 🔗 **前置知识**：本课程使用 Docker Desktop 的安装包来自项目的 GitHub Release，由 GitHub Action 定时从 Docker 官网下载并验证校验和，确保版本的可靠性和一致性。详见 [第 X 章：GitHub Action 定时同步 Release]（← 合并时替换为锚点链接）。

---

### 2.2 WSL 2 安装与配置

> 🔗 **关联知识**：`wsl --set-default-version 2` 的作用是将 WSL 的默认版本设为 2。WSL 有版本 1 和版本 2，其中版本 2 才包含完整 Linux 内核，版本 1 只是系统调用翻译层。Docker Desktop 要求 WSL 2。详见 [第 X 章：WSL 版本差异详解]（← 合并时替换）。

#### 🎯 目标

安装 WSL 2 内核更新包，并将 WSL 默认版本设置为 2，使 Docker Desktop 能够正常启动。

#### 🏗️ 前置准备

- 已完成 2.1 的功能启用和电脑重启
- 确认 Windows 版本为 Windows 10 2004+ 或 Windows 11

#### 💻 Step-by-Step

**Step 1：以管理员身份打开命令提示符**

在任务栏搜索框中输入 `CMD`，右键点击"命令提示符"，选择"**以管理员身份运行**"。

> ⚠️ **注意事项**：后续 WSL 安装命令需要管理员权限（涉及系统级修改），必须右键"以管理员身份打开"，直接双击打开的命令提示符权限不足会导致命令执行失败。

**Step 2：设置 WSL 默认版本为 2**

```powershell
# 将 WSL 的默认版本设为 2（Docker Desktop 要求 WSL 2）
wsl --set-default-version 2
```

> 这条命令告诉 Windows：以后通过 `wsl --install` 安装任何新 Linux 发行版时，默认使用 WSL 2 架构而不是 WSL 1。WSL 2 提供完整的 Linux 内核和更好的 I/O 性能，是 Docker 运行的必要条件。

**Step 3：安装/更新 WSL 内核**

```powershell
# 安装或更新 WSL 2 内核包
wsl --update
```

> 💡 **核心洞见**：`wsl --update` 并不是安装某个 Linux 发行版，而是更新 WSL 2 使用的 Linux 内核本身。Docker Desktop 使用 `docker-desktop` 和 `docker-desktop-data` 这两个特殊的 WSL 发行版来管理容器运行时和数据存储，它们都运行在这个共同的 WSL 2 内核之上。

**国内网络优化**：

```powershell
# 如果在国内网络，加上 --web-download 参数避免下载失败
wsl --update --web-download
```

> 💡 **核心洞见**：`--web-download` 参数强制 WSL 通过 HTTPS 直接下载内核包，而不是使用 Windows Update 渠道分发。在国内网络环境下，Windows Update 的 CDN 节点可能连接缓慢或超时，走 Web 直连 GitHub 的 CDN 反而更稳定。

| 下载模式 | 默认（无参数） | `--web-download` |
|---|---|---|
| 下载渠道 | Windows Update | GitHub Release CDN |
| 国内速度 | 可能极慢或超时 | 通常较快 |
| 适用场景 | 海外网络 | 国内网络 |
| 是否影响结果 | 不影响，最终安装的内核包相同 | 不影响 |

> 🐞 **常见坑**：国内用户不加 `--web-download` 时，下载进度条可能长时间卡在某个百分比不动（常见于 50%-70%），这不是安装失败，只是网络慢。如果等待超过 10 分钟，按 `Ctrl+C` 取消后加上 `--web-download` 重试即可。

**预期输出**：

执行成功后，终端会显示类似以下的内容：

```
正在下载: WSL 内核
正在安装: WSL 内核
请求的操作成功。直到重新启动系统前更改均不会生效。
```

> ⚠️ **注意事项**：如果输出提示需要重启，照做即可。WSL 内核更新涉及内核模块替换，不重启会让新旧模块混用，可能导致 WSL 启动报错。

---

### 2.3 Docker Desktop 安装（Windows）

#### 🎯 目标

下载并安装 Docker Desktop for Windows，使其与已配置的 WSL 2 后端对接。

#### 🏗️ 前置准备

- WSL 2 已成功安装并设默认版本为 2
- 电脑已按需重启

#### 💻 Step-by-Step

**Step 1：下载 Docker Desktop 安装包**

从项目 GitHub Release 页面下载 Windows 版 Docker Desktop：

```
访问项目的 GitHub 仓库 → Releases → 找到最新版本 → 下载 docker-desktop-windows.exe
```

> 🔗 **关联知识**：本项目 Release 中的 Docker Desktop 安装包由 GitHub Action 定时从 Docker 官网自动下载，确保安装包版本始终为 Docker 官方发布的最新稳定版，并附带校验和验证。详见 [第 X 章：GitHub Action 自动化 Release 发布]（← 合并时替换）。

**Step 2：安装 Docker Desktop**

**方式一：图形化安装（推荐）**

直接双击下载的 `.exe` 安装文件，按默认提示完成安装。安装程序会自动检测 WSL 2 环境并配置后端。

**方式二：命令行安装（可指定安装目录）**

```powershell
# 默认安装路径（C 盘）方式：直接双击 exe 即可

# 如果想将 Docker Desktop 安装到其他盘（如 D 盘），使用命令行参数 --installation-dir
# 注意：需要以管理员身份运行命令提示符
start /wait "" "Docker Desktop Installer.exe" install --installation-dir=D:\Docker\Docker
```

> 💡 **核心洞见**：`--installation-dir` 参数允许将 Docker Desktop 的二进制文件安装到指定路径。但请注意，Docker 镜像和容器的数据存储位置是另外管理的（由 WSL 2 的 `docker-desktop-data` 发行版控制），这个参数只决定 Docker Desktop 应用程序自身的安装位置。如果需要调整镜像数据存储位置，可以在 Docker Desktop 启动后在 Settings → Resources → Advanced 中修改 disk image location。

> ⚠️ **注意事项**：指定安装目录时，目录名中**不要包含中文**，否则 Docker Desktop 可能因路径编码问题无法正常启动或出现异常报错。

**Step 3：启动 Docker Desktop**

安装完成后，可以在开始菜单中找到 "Docker Desktop" 图标，点击启动。首次启动可能需要接受服务协议，并等待 Docker Engine 初始化（系统托盘中 Docker 图标变为稳定状态即表示成功）。

---

### 2.4 Mac Docker Desktop 安装

#### 🧠 直观理解

Mac 的情况和 Windows 不同——macOS 本身就基于 Darwin 内核（类 Unix），但没有 Linux 内核的 cgroup 等容器特性。Docker Desktop for Mac 的做法是在后台运行一个**轻量级 Linux 虚拟机**（使用 Apple 的 Hypervisor 框架），Docker Engine 跑在这个虚拟机里，而非直接运行在 macOS 上。

#### 📖 详细解释：芯片架构区分

Mac 的硬件在 2020 年后发生了根本性变化，不同芯片需要不同的 Docker 版本：

| 芯片类型 | 架构标识 | Docker 安装包 | 代表机型 |
|---|---|---|---|
| **Apple Silicon** (M1/M2/M3/M4) | `arm64` / `aarch64` | `Docker.dmg` (Apple Chip 版) | MacBook Air/Pro 2020+, Mac mini 2020+, iMac 2021+, Mac Studio |
| **Intel** | `x86_64` / `amd64` | `Docker.dmg` (Intel Chip 版) | MacBook 2020 及更早的 Intel 机型 |

> ❓ **常见疑问**：Apple Silicon Mac 能不能装 Intel 版 Docker？
>
> 可以通过 Rosetta 2 转译运行，但**强烈不推荐**。转译会有性能损耗（约 20%-40%），且运行 x86 容器时会出现双层转译（Mac 转译 Docker + Docker 内转译容器），性能更差。Apple Silicon Mac 请一定安装 arm64 版。

#### 💻 Step-by-Step

**Step 1：确认你的 Mac 芯片类型**

在终端中执行以下命令确认芯片型号：

```bash
# 查看当前 Mac 的处理器架构
uname -m
```

如果输出 `arm64`，说明是 Apple Silicon 芯片；如果输出 `x86_64`，说明是 Intel 芯片。

**Step 2：下载对应的安装包**

从项目 GitHub Release 页面选择对应架构的安装包：

```
Apple Silicon (M1/M2/M3/M4)：选择文件名为 *.arm64.dmg 的安装包
Intel 芯片：选择文件名为 *.x86_64.dmg（或 *.amd64.dmg）的安装包
```

> ⚠️ **注意事项**：务必下载与芯片匹配的版本。如果不小心下载了错误的架构版本，安装时 macOS 会弹出兼容性提示或安装后 Docker Engine 无法启动。

**Step 3：安装 Docker Desktop**

1. 双击下载的 `.dmg` 文件，挂载磁盘映像
2. 将 `Docker.app` 拖入 `Applications` 文件夹
3. 在 Launchpad 或应用程序文件夹中找到 Docker 图标，双击启动
4. 首次启动时，系统会弹窗要求授予权限——必须点击"**确定**"允许 Docker 安装必要的网络和系统扩展

> 💡 **核心洞见**：Mac 版 Docker Desktop 安装极其简单，不需要像 Windows 那样手动配置 WSL——macOS 的 Hypervisor 框架内置在系统中，Docker Desktop 会自动利用它创建 Linux 虚拟机。

---

### 2.5 安装后验证

安装完成并启动 Docker Desktop 后，通过以下步骤验证安装是否成功：

**Step 1：检查系统托盘图标**

```
Windows：系统托盘（右下角）出现 Docker 鲸鱼图标，鼠标悬停显示 "Docker Desktop is running"
Mac：菜单栏（右上角）出现 Docker 鲸鱼图标，点击显示 "Docker Desktop is running"
```

**Step 2：在终端/命令提示符中验证**

```bash
# 查看 Docker 版本信息，确认安装成功
docker --version

# 查看更详细的 Docker 系统信息
docker info

# 运行官方 hello-world 测试容器
docker run hello-world
```

预期输出中 `hello-world` 容器应打印欢迎信息：

```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

> 🐞 **常见坑**：如果 `docker run hello-world` 报错 `Cannot connect to the Docker daemon`，说明 Docker 桌面应用还没有完全启动。请等待系统托盘/菜单栏图标稳定（不再旋转动画），再重新执行命令。

> ❓ **常见疑问**：`docker info` 和 `docker --version` 有什么区别？
>
> `docker --version` 只显示客户端版本号；`docker info` 会显示 Docker Daemon 的运行状态、存储驱动、镜像数、容器数等详细信息。后者能更全面地判断 Docker 是否正常工作。在排查安装问题时，`docker info` 提供的信息更有价值。

---

### 🔄 Windows 安装完整流程总览

```
开始
  │
  ▼
┌─────────────────────────────────┐
│ Step 1：启用 Windows 功能        │
│ ☑ 适用于 Linux 的 Windows 子系统 │
│ ☑ 虚拟机平台                     │
└──────────────┬──────────────────┘
               │ 重启电脑
               ▼
┌─────────────────────────────────┐
│ Step 2：安装 WSL 2 内核          │
│ $ wsl --set-default-version 2   │
│ $ wsl --update --web-download   │
└──────────────┬──────────────────┘
               │（按需重启）
               ▼
┌─────────────────────────────────┐
│ Step 3：安装 Docker Desktop      │
│ 下载 Release 中的 exe 安装包     │
│ 双击安装（或命令行指定目录）      │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│ Step 4：验证安装                 │
│ $ docker --version              │
│ $ docker run hello-world        │
└─────────────────────────────────┘
```

---


## 三、方案一：阿里云私有仓库镜像转存

### 3.1 方案概述与设计思路

#### 🧠 直观理解

在国内拉取 Docker Hub 镜像，就像从海外直邮买东西——速度慢、经常被拦截、甚至完全收不到。阿里云私有仓库镜像转存方案，相当于在阿里云（国内）建了一个「个人转运仓」：先把 Docker Hub 的镜像自动下载到你的阿里云私有仓库，再从阿里云拉取，速度快且稳定。

#### 📖 为什么选择阿里云？

> 💡 **核心洞见**：2024 年以来，国内几乎所有 Docker Hub 公共镜像加速站都陆续下架或停止服务。但阿里云容器镜像服务（ACR，Alibaba Cloud Container Registry）个人版依然可用，且提供完全免费的个人仓库。

老师特别指出该方案的五个关键优势：

| 维度 | 说明 |
|---|---|
| **费用** | 阿里云个人版完全免费，GitHub Actions 对公开仓库也免费 |
| **镜像大小** | 支持高达 **40GB** 的大型镜像，远超一般公共镜像站的限制 |
| **网络线路** | 走阿里云官方骨干网线路，国内服务器下载速度极快 |
| **稳定性** | 阿里云作为国内头部云厂商，服务 SLA 有保障，不会像小镜像站那样随时关停 |
| **镜像来源** | 支持任意 Docker 镜像仓库（Docker Hub、GHCR、Quay.io 等），不限于 Docker Hub |

> 🔗 **关联知识**：本方案延续了 01 章中使用 GitHub Action 实现自动化的思路——利用 GitHub 提供的免费 CI 计算资源（每月 2000 分钟起），完成原本需要手动操作的镜像下载和上传任务。

#### 🔗 推导链：为什么这个方案这样设计

```
起点: Docker Hub 镜像在国内无法正常拉取
  │
  ├── 第1步: 尝试使用国内公共镜像站 / 加速器
  │   为什么？这是最直觉的替代方案
  │   发现：绝大多数国内 Docker 镜像站已陆续下架，
  │         仍存活的也极不稳定
  │
  ├── 第2步: 考虑云厂商的容器镜像服务
  │   为什么？云厂商有基础设施和合规资质，不会轻易关停
  │   候选：阿里云 ACR、腾讯云 TCR、华为云 SWR
  │   选择阿里云 ACR 的原因：个人版完全免费，无需企业认证
  │
  ├── 第3步: 需要一个自动化的中转工具
  │   为什么？手动执行 docker pull → docker tag → docker push
  │         太繁琐，每次新增镜像都要重复操作
  │   约束：中转机器必须能访问 Docker Hub（需要海外网络）
  │   方案：GitHub Action 运行在海外机房，天然能访问 Docker Hub，
  │         且对公开仓库完全免费
  │
  └── 结论: GitHub Action + 阿里云 ACR 个人版
            = 零成本、自动化、持续可用的镜像转存方案
```

#### 🔄 整体架构流程

```
                         GitHub Actions（海外机房）
┌─────────────┐         ┌─────────────────────────┐         ┌─────────────────────┐
│  Docker Hub  │──拉取──▶│  docker pull（自动）      │──推送──▶│  阿里云 ACR 私有仓库  │
│  (镜像源头)   │         │  docker tag（自动）       │         │  (国内高速下载)       │
└─────────────┘         │  docker push（自动）      │         └──────────┬──────────┘
                        └─────────────────────────┘                    │
                                                                       │ docker pull
                                                                       │ （高速）
                                                                       ▼
                                                            ┌─────────────────────┐
                                                            │  你的国内服务器       │
                                                            │  （百度云/阿里云/自建）│
                                                            └─────────────────────┘
```

老师撰写的这个 GitHub Action 项目已在开源社区获得 **3.5k+ Fork**，说明大量国内开发者面临着同样的镜像拉取困境，这个方案经过了广泛的社区验证。

---

### 3.2 🎯 本节目标

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 在阿里云创建个人版容器镜像服务，并正确配置命名空间
> - [ ] 准确获取并理解四个关键环境变量的含义和用途
> - [ ] Fork GitHub 项目并正确配置仓库 Secrets
> - [ ] 编辑 `images.txt` 文件添加需要转存的镜像
> - [ ] 触发 GitHub Action 并确认镜像转存成功
> - [ ] 在国内服务器上从阿里云私有仓库拉取转存后的镜像
> - [ ] 将现有项目（docker-compose、Shell 脚本）中的 Docker Hub 地址替换为阿里云地址

---

### 3.3 🏗️ 前置准备

在开始操作之前，请确保具备以下条件：

| 准备项 | 说明 | 是否必须 |
|---|---|---|
| **阿里云账号** | 需完成实名认证，个人版不需要企业认证 | 是 |
| **GitHub 账号** | 用于 Fork 项目、配置 Secrets、触发 Action | 是 |
| **目标镜像清单** | 列出你需要转存的 Docker 镜像名称和 tag | 是 |
| **一台国内服务器** | 用于验证最终拉取效果（也可在本地 Docker 环境验证） | 否 |

---

### 3.4 💻 Step-by-Step：完整配置流程

---

#### Step 1: 注册并配置阿里云容器镜像服务

首先访问阿里云容器镜像服务控制台：

```
https://cr.console.aliyun.com/
```

如果没有阿里云账号，注册并完成实名认证。进入控制台后，按以下步骤操作：

**1.1 选择个人版**

在页面提示中选择「**个人版**」，点击「**创建个人版**」按钮。系统会弹出确认对话框，点击「**确定**」完成创建。

> 💡 **核心洞见**：阿里云容器镜像服务分为「个人版」和「企业版」。个人版完全免费，提供 300 个仓库配额，足够个人和小团队使用。企业版按量付费，适合有合规审计需求的正式生产环境。本方案使用个人版即可。

**1.2 设置登录密码**

进入个人版实例后，点击左侧菜单的「**访问凭证**」，在页面中点击「**设置固定密码**」。这个密码后续用于 Docker CLI 登录阿里云仓库。

```bash
# 设置固定密码（示例，请使用你自己的强密码）
# 密码: techramp123
```

> ⚠️ **注意事项**：这里的「固定密码」与阿里云账号的登录密码是**两个独立的密码**。「固定密码」专门用于 `docker login` 命令，即使泄露也只影响容器镜像仓库，不会波及阿里云账号本身。

**1.3 创建命名空间**

在左侧菜单中点击「**命名空间**」，然后点击「**创建命名空间**」按钮。

```bash
# 命名空间名称示例
# 命名空间: shrimp-images
```

输入命名空间名称，点击「**确定**」完成创建。

> 💡 **核心洞见**：命名空间（Namespace）在阿里云镜像仓库中的作用类似于文件系统中的**文件夹**——它是一个逻辑分组容器。你的所有转存镜像都会归类到这个命名空间下面。命名空间名称会在最终的镜像拉取地址中出现，所以建议使用有意义的名称（如 `my-project`、`team-images`）。

命名空间创建完成后，控制台中会显示该命名空间条目。此时尚未产生任何镜像仓库——镜像仓库会在后续 GitHub Action 执行推送时自动创建。

---

#### Step 2: 获取四个关键环境变量

在阿里云控制台中，需要获取以下四个配置值，它们将作为 GitHub Action 连接阿里云仓库的凭证：

| 序号 | 环境变量名 | 获取位置 | 说明 | 示例值 |
|---|---|---|---|---|
| ① | `ALIYUN_NAME_SPACE` | 「命名空间」页面 | 你在 Step 1.3 创建的命名空间名称 | `shrimp-images` |
| ② | `ALIYUN_REGISTRY_USER` | 「访问凭证」页面 | 阿里云分配给个人版的用户名 | 一串自动生成的字符串 |
| ③ | `ALIYUN_REGISTRY_PASSWORD` | 「访问凭证」页面 | 你在 Step 1.2 设置的固定密码 | `techramp123` |
| ④ | `ALIYUN_REGISTRY` | 控制台顶部/概览页 | 仓库地址（绿色高亮显示） | `registry.cn-hangzhou.aliyuncs.com` |

**逐一详解**：

- **① 命名空间 (`ALIYUN_NAME_SPACE`)**：就是你在 Step 1.3 创建的名称。这个值直接决定了镜像推送目标路径：`<仓库地址>/<命名空间>/<镜像名>`。
- **② 用户名 (`ALIYUN_REGISTRY_USER`)**：在「访问凭证」页面，看到「固定密码」区域，上方显示的「用户名」即是。这是一串由阿里云自动生成的字符串（不是你的阿里云账号或手机号）。
- **③ 密码 (`ALIYUN_REGISTRY_PASSWORD`)**：同一个「访问凭证」页面中你设置的固定密码。如果忘记了，可以点击「重置密码」重新设置。
- **④ 仓库地址 (`ALIYUN_REGISTRY`)**：在控制台顶部或「概览」页面，仓库地址通常以**绿色**高亮显示。格式为 `registry.<地域标识>.aliyuncs.com`。

> ⚠️ **注意事项**：仓库地址中的**地域标识**（如 `cn-hangzhou`、`cn-shanghai`、`cn-beijing`）取决于你创建个人版时选择的地域。不同地域的仓库地址不同，镜像存储的物理位置也不同，但对国内服务器的下载速度差异不明显，选择默认地域即可。

---

#### Step 3: Fork 项目到自己的 GitHub

打开老师提供的 GitHub 项目页面，点击页面右上角的 **Fork** 按钮：

```
项目页面 → 右上角 Fork 按钮 → Create fork
```

Fork 的作用是将项目**完整复制一份**到你自己的 GitHub 账号下。Fork 完成后，你会在自己的 GitHub 仓库列表中看到该项目（仓库名保持不变）。

> 💡 **核心洞见**：Fork 不是简单的下载或 clone，而是在 GitHub 服务器上创建了一个**属于你的独立仓库副本**。这意味着：
> - 你可以自由修改代码和配置，不影响原始项目
> - 原始项目更新时，你可以选择同步（Sync fork）
> - 你可以向原始项目提交 Pull Request 贡献代码
> - 这是 GitHub 上开源协作的标准模式

---

#### Step 4: 配置 GitHub Secrets

进入你自己 Fork 后的项目仓库，按以下路径配置 Secrets：

```
仓库首页 → Settings → Secrets and variables → Actions
```

在 **Actions secrets and variables** 页面中，点击绿色按钮 **「New repository secret」**，逐个添加 Step 2 中获取的四个环境变量：

```bash
# ┌──────────────────────────────────────────────────┐
# │         GitHub Secrets 配置清单                   │
# ├──────────────────────────────────────────────────┤
# │                                                  │
# │  ① Name:  ALIYUN_NAME_SPACE                      │
# │     Value: shrimp-images                         │
# │                                                  │
# │  ② Name:  ALIYUN_REGISTRY_USER                   │
# │     Value: （你的阿里云个人版用户名）               │
# │                                                  │
# │  ③ Name:  ALIYUN_REGISTRY_PASSWORD               │
# │     Value: （你设置的固定密码）                     │
# │                                                  │
# │  ④ Name:  ALIYUN_REGISTRY                        │
# │     Value: registry.cn-hangzhou.aliyuncs.com     │
# │                                                  │
# └──────────────────────────────────────────────────┘
```

每次点击 **Add secret** 保存一个变量。全部完成后，你的 Actions secrets 列表应显示 4 个配置项：

```
Repository secrets:
  ALIYUN_NAME_SPACE        *** (已配置)
  ALIYUN_REGISTRY          *** (已配置)
  ALIYUN_REGISTRY_PASSWORD *** (已配置)
  ALIYUN_REGISTRY_USER     *** (已配置)
```

> ⚠️ **注意事项**：
> - Secret 的 **Name 必须与项目工作流文件中引用的名称完全一致**（区分大小写、区分下划线），否则 Action 运行时找不到对应值
> - Secret 的值保存后**无法在 GitHub 页面上再次查看**，只能「更新」或「删除」。请务必在添加前确认值正确
> - 如果你的项目仓库是**公开的**（Public），Secrets 仍然安全——GitHub 不会在任何日志或输出中暴露 Secret 值

---

#### Step 5: 启用 GitHub Actions 并编辑 images.txt

**5.1 启用 Actions**

回到项目仓库首页，点击顶部的 **Actions** 标签页。由于 Fork 的项目默认不启用 GitHub Actions（安全策略），你会看到提示信息。点击页面中的绿色按钮：

```
I understand my workflows, go ahead and enable them
```

启用后，工作流文件（`.github/workflows/` 目录下的 `.yml` 文件）才会生效。

**5.2 编辑 images.txt**

回到 **Code** 标签页，在仓库根目录找到 `images.txt` 文件。点击文件名进入预览页面，然后点击右上角的**小铅笔图标**（✏️ Edit this file）进入编辑模式。

`images.txt` 是镜像转存的核心配置文件，格式规则如下：

```text
# ========================================
# images.txt - 镜像转存清单
# ========================================
# 格式规则：
#   1. 每行一个镜像
#   2. 格式: 镜像名[:tag]
#   3. tag 可以省略，省略时默认使用 latest
#   4. 以 # 开头的行为注释，不会被执行
# ========================================

# 示例：常用基础镜像
alpine
python:alpine3.19
nginx:1.25
redis
node:20-alpine
```

> 💡 **核心洞见**：`images.txt` 的格式细节：
> - **带 tag**：`镜像名:tag` —— 指定具体版本，如 `python:alpine3.19`。生产环境**强烈建议**写明具体 tag，避免 `latest` 漂移导致的不一致
> - **不带 tag**：只写镜像名，如 `redis` —— 此时默认拉取 `latest` 标签
> - **每行一个镜像**：不支持 `alpine python nginx` 这种写法
> - **注释行**：以 `#` 开头，可以用来记录分组或备注，不会被处理

编辑完成后，点击右上角绿色按钮 **「Commit changes...」**，在弹出的对话框中直接点击 **「Commit changes」** 提交。

> ⚠️ **注意事项**：提交 `images.txt` 时，确保提交到**默认分支**（通常是 `main` 或 `master`）。GitHub Action 工作流通常监听默认分支的 push 事件，如果提交到其他分支可能不会触发。

---

#### Step 6: 查看 Action 执行结果

提交 `images.txt` 后，GitHub Action 工作流会**自动触发**。进入 **Actions** 标签页查看执行状态：

```
仓库首页 → Actions → 最新的 Workflow Run → 点击查看详情
```

你会看到类似如下的执行日志：

```
┌──────────────────────────────────────────────────────────┐
│              GitHub Action 工作流执行流程                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Step 1 ── 检出仓库代码                                   │
│  │   actions/checkout，读取 images.txt                   │
│  │                                                       │
│  Step 2 ── 登录阿里云 ACR                                 │
│  │   docker login ${{ secrets.ALIYUN_REGISTRY }}         │
│  │   使用 Secrets 中的用户名和密码                         │
│  │                                                       │
│  Step 3 ── 逐行处理 images.txt 中的镜像                   │
│  │  ┌─────────────────────────────────┐                  │
│  │  │ 对每一个镜像名：                  │                  │
│  │  │  ① docker pull <镜像名>          │  (从 Docker Hub 拉取)     │
│  │  │  ② docker tag <原镜像> <ACR地址> │  (标记为 ACR 地址)       │
│  │  │  ③ docker push <ACR地址>        │  (推送到 ACR)            │
│  │  └─────────────────────────────────┘                  │
│  │                                                       │
│  Step 4 ── 完成                                         │
│  │   输出执行摘要，列出成功/失败的镜像                      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

每一步的日志都可以在 Action 详情页中展开查看。执行完成后，状态标记为绿色的 ✅，表示所有镜像都已成功转存。

> 🐞 **常见坑**：如果 Action 显示红色 ❌，展开日志定位失败原因：
> - `Error: ALIYUN_REGISTRY is not set` → Secrets 名称拼写错误
> - `Error: Cannot login to registry` → 用户名或密码不正确
> - `Error: pull access denied` → 镜像名写错或 Docker Hub 中不存在该镜像
> - `Timeout` → Docker Hub 拉取超时，点击「Re-run jobs」重新运行即可

---

### 3.5 ✅ 验证结果：阿里云控制台确认

Action 执行成功后，回到阿里云容器镜像服务控制台，点击「**镜像仓库**」：

```
阿里云控制台 → 容器镜像服务 → 镜像仓库
```

你应该能看到 `images.txt` 中填写的所有镜像，每个镜像对应一个独立的仓库：

```
┌───────────────────────────────────────────────────────────┐
│                  阿里云镜像仓库列表                          │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────────────────────────────────────┐      │
│  │ 📦 alpine                                         │      │
│  │    仓库地址: registry.cn-hangzhou.aliyuncs.com     │      │
│  │             /shrimp-images/alpine                  │      │
│  │    标签: latest                                    │      │
│  │    类型: 私有（可切换为公开）                       │      │
│  └─────────────────────────────────────────────────┘      │
│                                                           │
│  ┌─────────────────────────────────────────────────┐      │
│  │ 📦 python                                         │      │
│  │    仓库地址: .../shrimp-images/python              │      │
│  │    标签: alpine3.19                                │      │
│  │    类型: 私有                                      │      │
│  └─────────────────────────────────────────────────┘      │
│                                                           │
│  ┌─────────────────────────────────────────────────┐      │
│  │ 📦 nginx                                          │      │
│  │    仓库地址: .../shrimp-images/nginx               │      │
│  │    标签: 1.25                                      │      │
│  │    类型: 私有                                      │      │
│  └─────────────────────────────────────────────────┘      │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

点击任意仓库进入详情页，可以查看：

| 标签页 | 内容 |
|---|---|
| **镜像版本** | 列出该仓库所有已推送的 tag，以及每个 tag 的大小和推送时间 |
| **使用指南** | 自动生成完整的 `docker login` 和 `docker pull` 命令，可直接复制使用 |
| **基本信息** | 仓库类型（公开/私有）、创建时间、所属命名空间 |

> 💡 **核心洞见**：关于镜像仓库类型的设置：
> - **私有**（默认）：仅你自己可以拉取，其他人即使知道地址也无法访问。适合个人或公司内部使用，安全性最高
> - **公开**：任何人都能直接拉取，无需登录，适合团队协作或对外分享。切换方式：仓库详情页点击「基本信息」旁的「编辑」即可修改

---

### 3.6 💻 国内服务器拉取镜像

#### 拉取命令格式

在阿里云镜像仓库详情页的「使用指南」标签页中，可以直接复制为你生成好的命令。完整格式如下：

```bash
# ┌────────────────────────────────────────────────────────┐
# │ 拉取命令通用格式                                        │
# │ docker pull <仓库地址>/<命名空间>/<镜像名>:<tag>         │
# └────────────────────────────────────────────────────────┘

# Step 1: 登录阿里云 Docker 仓库（仅私有镜像需要）
docker login --username=<你的用户名> registry.cn-hangzhou.aliyuncs.com
# 输入密码后看到 Login Succeeded 表示登录成功

# Step 2: 拉取镜像
# 示例 1：拉取 Alpine 最新版（latest 可省略）
docker pull registry.cn-hangzhou.aliyuncs.com/shrimp-images/alpine

# 示例 2：拉取 Python 指定 tag
docker pull registry.cn-hangzhou.aliyuncs.com/shrimp-images/python:alpine3.19
```

> ⚠️ **注意事项**：如果镜像仓库设置为「公开」，可以跳过 `docker login` 这一步，直接 `docker pull` 即可。但私有仓库必须先登录。

---

#### 拉取验证：三次现场演示

老师在课堂上用一台位于北京的百度云服务器，现场演示了三次镜像拉取，每次都针对不同的场景：

**演示一：拉取 Alpine（验证 latest 标签）**

```bash
# 在北京百度云服务器上执行
docker pull registry.cn-hangzhou.aliyuncs.com/shrimp-images/alpine

# 预期输出（关键行）
# latest: Pulling from shrimp-images/alpine
# Digest: sha256:a856...（具体 hash 值会变化）
# Status: Downloaded newer image for registry.cn-hangzhou.aliyuncs.com/shrimp-images/alpine:latest
# registry.cn-hangzhou.aliyuncs.com/shrimp-images/alpine:latest
```

> 这次演示验证了两个要点：① 阿里云线路下载速度正常；② `latest` 是默认标签，命令中可以省略 `:latest`。

**演示二：拉取 Python Alpine 3.19（验证指定 tag）**

```bash
# 拉取指定版本的 Python 镜像
docker pull registry.cn-hangzhou.aliyuncs.com/shrimp-images/python:alpine3.19

# 预期输出
# alpine3.19: Pulling from shrimp-images/python
# Digest: sha256:...
# Status: Downloaded newer image for registry.cn-hangzhou.aliyuncs.com/shrimp-images/python:alpine3.19
```

> 这次演示验证了：① 具体版本 tag 必须在冒号后面写明；② 多个镜像可以并存于同一个命名空间中，互不冲突。

**演示三：RSS 项目完整改造**（详见 3.8 节）

---

### 3.7 🐛 排错指南

#### 🐛 排错实录一：images.txt 格式错误导致 Action 失败

**❌ 错误写法**

```text
# 错误 1：多个镜像写在同一行
alpine python nginx

# 错误 2：镜像名和 tag 之间用了空格（应该用冒号）
python alpine3.19

# 错误 3：多级 tag 格式错误
python:alpine3.19:extra
```

**🚨 报错信息**

```
Error response from daemon: manifest for python alpine3.19 not found: 
    manifest unknown: manifest unknown
Error: pull access denied for "alpine python nginx", 
    repository does not exist or may require 'docker login'
```

**🔍 原因分析**

Docker 镜像引用（Image Reference）遵循严格的格式规范：`[registry/][namespace/]image[:tag]`。当你在 `images.txt` 中写下 `alpine python nginx` 时，Action 脚本会将整行字符串当作**一个**镜像名去解析和拉取——Docker 当然找不到名为 `alpine python nginx` 的镜像。

**✅ 正确写法**

```text
# 正确：每行一个镜像，tag 用英文冒号连接
alpine
python:alpine3.19
nginx
redis
```

**📝 经验总结**

- `images.txt` 严格遵循**每行一个镜像**的规则，不能将多个镜像写在同一行
- 镜像名和 tag 之间用**英文冒号** `:`（不是空格、不是中文冒号 `：`）
- tag 只能有一级（`name:tag`），不支持 `name:tag1:tag2` 这种多级格式
- 在提交 `images.txt` 之前，逐行检查格式是否正确

---

#### 🐛 排错实录二：Secret 名称不匹配导致登录失败

**❌ 错误配置**

在 GitHub Secrets 页面中，将环境变量的 Name 写错：

```bash
# 错误示例——名称写错
# Name:  ALIYUN_REGISTRY_URL    ← 多写了 _URL
# Name:  ALIYUN_NAMESPACE       ← 少了 _REGISTRY，下划线位置不同
# Name:  ALIYUN_USER            ← 跟工作流文件中的 ALIYUN_REGISTRY_USER 不一致
```

**🚨 报错信息**

在 Action 执行日志中看到：

```
Run docker login ...
Error: Cannot login to registry. Please check your credentials.
Error: ALIYUN_REGISTRY is not set. 
Please add it to your repository secrets.
```

**🔍 原因分析**

GitHub Action 的工作流文件（`.github/workflows/*.yml`）中，通过 `${{ secrets.ALIYUN_REGISTRY }}` 这样的语法来引用 Secret。这个引用名称是**硬编码**在工作流文件中的。如果你的 Secret 名称与工作流文件中的引用不一致（哪怕差一个字母），GitHub 就找不到对应的值，Action 自然失败。

**✅ 正确配置**

以下是四个 Secret 的**精确名称**和常见错误对照：

| Secret Name（必须一致） | 说明 | 常见错误写法 |
|---|---|---|
| `ALIYUN_REGISTRY` | 仓库地址 | `REGISTRY`、`ALIYUN_REGISTRY_URL`、`ALIYUN_REG_ADDR` |
| `ALIYUN_NAME_SPACE` | 命名空间 | `NAMESPACE`、`ALIYUN_NAMESPACE`、`ALIYUN_SPACE` |
| `ALIYUN_REGISTRY_USER` | 用户名 | `USERNAME`、`ALIYUN_USER`、`REGISTRY_USER` |
| `ALIYUN_REGISTRY_PASSWORD` | 密码 | `PASSWORD`、`ALIYUN_PWD`、`REGISTRY_PASS` |

**📝 经验总结**

- 配置 Secrets 时，务必对照项目的 **README 文档**或 `.github/workflows/*.yml` 文件中的真实引用，一字不差地复制 Name
- 建议直接**从项目文档中复制粘贴** Secret Name，避免手动输入时打错
- 如果多次尝试仍失败，打开工作流文件搜索 `secrets.`，确认所有引用的 Secret 名称

---

### 3.8 📋 实际项目应用案例：RSS 项目改造

#### 📋 背景

老师在课堂上分享了一个真实的项目经验：他在前几天演示了一个「微信公众号文章转 RSS 订阅」的开源项目。这个项目的部署依赖 Docker 镜像。但随着国内 Docker Hub 访问问题加剧，原本正常的部署命令已经完全失效了。

#### ⚠️ 问题

```bash
# 原本的部署方式——从 Docker Hub 直接拉取
docker pull some-project/wechat-rss:latest

# 现在的执行结果——拉取失败
# Error response from daemon:
#   Get "https://registry-1.docker.io/v2/...": 
#   dial tcp: connect: connection refused
```

国内服务器无法访问 Docker Hub，镜像拉取命令直接报连接拒绝，整个项目无法部署。

#### 🔍 解决过程

**第一阶段：转存镜像**

```text
# 编辑仓库中的 images.txt
# 在文件末尾追加 RSS 项目的镜像
# 注意格式：镜像名:tag

some-project/wechat-rss:latest
```

点击 **Commit changes** 提交，等待 GitHub Action 执行。

Action 执行完成后，回到阿里云控制台，确认镜像已出现在仓库列表中：

```
阿里云控制台 → 镜像仓库
  └── wechat-rss（新增的仓库！）
        ├── 仓库地址: registry.cn-hangzhou.aliyuncs.com/shrimp-images/wechat-rss
        └── 标签: latest
```

**第二阶段：替换部署命令中的镜像地址**

老师展示了他原本的部署脚本。脚本中最后一行是 `docker pull` 或 `docker run` 命令，引用了 Docker Hub 的原始镜像名：

```bash
# ❌ 原始脚本——镜像来自 Docker Hub，已无法拉取
docker pull some-project/wechat-rss:latest
docker run -d -p 8080:8080 some-project/wechat-rss:latest
```

将其替换为阿里云地址：

```bash
# ✅ 替换为阿里云地址
docker pull registry.cn-hangzhou.aliyuncs.com/shrimp-images/wechat-rss:latest
docker run -d -p 8080:8080 registry.cn-hangzhou.aliyuncs.com/shrimp-images/wechat-rss:latest
```

如果项目使用 `docker-compose.yml`，替换方式如下：

```yaml
# docker-compose.yml —— 修改前后对比
version: '3.8'
services:
  wechat-rss:
    # ❌ 修改前——Docker Hub 地址
    # image: some-project/wechat-rss:latest

    # ✅ 修改后——阿里云地址
    image: registry.cn-hangzhou.aliyuncs.com/shrimp-images/wechat-rss:latest
    ports:
      - "8080:8080"
    restart: unless-stopped
```

#### ✅ 结果

将替换后的命令拿回国内服务器执行：

```bash
$ docker pull registry.cn-hangzhou.aliyuncs.com/shrimp-images/wechat-rss:latest

# latest: Pulling from shrimp-images/wechat-rss
# Digest: sha256:abcdef1234567890...
# Status: Downloaded newer image for 
#   registry.cn-hangzhou.aliyuncs.com/shrimp-images/wechat-rss:latest
# registry.cn-hangzhou.aliyuncs.com/shrimp-images/wechat-rss:latest
```

镜像成功拉取，项目恢复运行。

#### 💡 迁移启示

这个案例揭示了该方案的典型应用模式，可总结为**已有项目改造三步法**：

```
┌──────────────────────────────────────────────────────────┐
│            已有项目接入阿里云转存方案 — 三步法              │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ① 识别：找到项目中所有引用 Docker Hub 镜像的位置          │
│       ├── docker run 命令中的镜像名                       │
│       ├── docker-compose.yml 中的 image 字段              │
│       ├── Shell 脚本中的 docker pull 命令                 │
│       └── Kubernetes YAML 中的 image 字段                 │
│                                                          │
│  ② 转存：将所有镜像名添加到 images.txt，通过 Action 转存   │
│                                                          │
│  ③ 替换：将所有原始镜像名替换为阿里云地址                   │
│      格式：<ALIYUN_REGISTRY>/<NAMESPACE>/<镜像名>:<tag>   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

> ❓ **常见疑问**：以后镜像有更新怎么办？需要重新配置吗？
>
> **回答**：完全不需要重新配置。只需更新 `images.txt` 文件（例如修改 tag 版本号），提交后 GitHub Action 会自动拉取新版本并推送到阿里云。你甚至可以配置 GitHub Action 的定时触发（schedule / cron），让它在每天凌晨自动检查并同步镜像的最新版本，实现**无人值守的持续同步**。

> 🔗 **延伸阅读**：关于 GitHub Action 的定时触发（cron）、手动触发（workflow_dispatch）等高级用法，详见本文 04 章的 GitHub Actions 进阶内容。

---

### 3.9 📊 方案总结

| 维度 | 说明 |
|---|---|
| **适用场景** | 个人开发者、小团队、任何需要在国內服务器稳定拉取 Docker 镜像的用户 |
| **成本** | 完全免费（阿里云 ACR 个人版 + GitHub Actions 公开仓库免费额度 2000 分钟/月） |
| **配置复杂度** | 低，一次性 10 分钟配置，后续只需编辑 `images.txt` 并提交 |
| **镜像来源** | 支持任意 Docker 镜像仓库（Docker Hub、GHCR、Quay.io 等） |
| **自动化程度** | 高，GitHub Action 自动拉取 + 标记 + 推送，全程无需人工干预 |
| **镜像更新** | 手动修改 `images.txt` 提交触发；或配置定时任务自动同步 |
| **单镜像大小上限** | 约 40GB（阿里云个人版限制） |
| **仓库数量上限** | 300 个（阿里云个人版限制） |
| **拉取速度** | 阿里云骨干网，国内服务器通常可达 10-50 MB/s |

> 💡 **核心洞见**：这个方案的本质是利用了「**两个免费资源的组合**」——GitHub Actions 的海外网络（能访问 Docker Hub）+ 阿里云 ACR 的国内网络（国内服务器能高速访问）。中间的 GitHub Action 承担了「搬运工」的角色，把镜像从海外搬到了国内。整套方案零成本运转，对于个人开发者和中小团队来说，这是当前最务实的 Docker 镜像拉取解决方案。

## 四、方案二至五：镜像站、离线下载、一键脚本、Cloudflare Worker

在上一节中，我们详细讲解了方案一（阿里云私有仓库镜像转存），它是五种方案中最推荐个人开发者长期使用的一种。但不同的开发环境、网络条件和使用场景需要不同的解法。本节介绍剩余四种方案，它们各有侧重，灵活组合使用效果更好。

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 在 Linux 和 Windows/Mac 上分别配置 Docker 镜像站
> - [ ] 理解离线镜像下载的完整链路，知道什么时候该用
> - [ ] 使用一键脚本自动测速并拉取镜像
> - [ ] 了解 Cloudflare Worker 自建加速的原理和限制
> - [ ] 根据自身场景，从五种方案中选出最合适的组合

---

### 4.1 方案二：配置镜像站

#### 🧠 直观理解

Docker 默认从 Docker Hub（`docker.io`）拉取镜像，而 Docker Hub 的服务器在境外，国内直接访问经常超时。镜像站相当于在境内设立了一个"Docker Hub 缓存节点"——它定期从 Docker Hub 同步镜像，当你 `docker pull` 时，流量走的是境内镜像站而不是境外 Docker Hub，速度大幅提升。

可以类比为：你要从国外官网下载一个 2GB 的安装包，直连只有 50KB/s。但你发现国内某高校镜像站已经同步了同一个文件，从那里下载能跑满带宽。

#### 📖 详细解释

Docker 的镜像拉取链路默认是这样的：

```
docker pull nginx
       │
       ▼
┌─────────────┐     境外网络      ┌──────────────┐
│  你的机器    │ ──────────────▶  │  Docker Hub   │
│  (中国境内)  │ ◀────慢/超时──── │  (docker.io)  │
└─────────────┘                  └──────────────┘
```

配置 `registry-mirrors` 之后，链路变成：

```
docker pull nginx
       │
       ▼
┌─────────────┐    境内网络       ┌──────────────┐
│  你的机器    │ ──────────────▶  │  国内镜像站   │
│  (中国境内)  │ ◀───快速返回──── │  (如 USTC)   │
└─────────────┘                  └──────┬───────┘
                                        │ 定期同步
                                        ▼
                                  ┌──────────────┐
                                  │  Docker Hub   │
                                  └──────────────┘
```

Docker Daemon 收到 `pull` 请求后，会先尝试配置的 `registry-mirrors` 列表，按顺序逐个尝试，只有当所有镜像源都不可用时才会回退到直连 Docker Hub。

#### 💻 Linux 配置步骤

**Step 1：编辑 Docker 配置文件**

```bash
# Docker 的守护进程配置文件
sudo vim /etc/docker/daemon.json
```

**Step 2：添加镜像源配置**

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
```

> 如果 `daemon.json` 中已有其他配置项（如日志驱动、存储驱动等），将 `"registry-mirrors"` 作为新 key 合并进去，注意上一行末尾需要加逗号。JSON 格式出错会导致 Docker 无法启动。

**Step 3：保存退出 vim**

按 `ESC` 键退出编辑模式，输入 `:wq!` 回车，强制保存并退出。

**Step 4：重启 Docker 服务**

```bash
# 重启 Docker 守护进程使配置生效
sudo systemctl restart docker
```

**Step 5：验证**

```bash
# 拉取一个镜像测试加速效果
sudo docker pull nginx
```

看到镜像快速拉取成功，说明镜像站配置生效。

#### 💻 Windows / Mac 配置步骤

Docker Desktop 提供了图形化的配置入口，不需要手动编辑文件。

**Step 1：打开 Docker Desktop 设置**

右键系统托盘中的 Docker 图标 → 点击 **Settings**。

**Step 2：进入 Docker Engine 配置页**

在左侧菜单栏找到 **Docker Engine**。这个页面展示的就是当前 `daemon.json` 的内容。

**Step 3：修改 JSON 配置**

将 `"registry-mirrors"` 配置添加到大括号内。以下是一个完整示例：

```json
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
```

> 🐞 **常见坑**：Docker Desktop 默认的 `daemon.json` 中 `"experimental": false` 这一行末尾**没有逗号**。如果你直接在它下面新增 `"registry-mirrors"`，JSON 格式会出错导致 Docker Desktop 启动失败。老师特别强调了这一点——务必在 `false` 后面加上一个逗号。

**Step 4：应用并重启**

点击 **Apply & Restart** 按钮，Docker Desktop 会自动重启并加载新配置。

**Step 5：验证**

打开终端，执行 `docker pull nginx`，观察拉取速度是否明显提升。

> 🔗 **关联知识**：镜像站的可用地址不是一成不变的。各个公共镜像源可能因政策调整或维护而停服。建议关注镜像源官网公告，或同时配置多个地址做容错。

---

### 4.2 方案三：GitHub Action 离线镜像下载

#### 🧠 直观理解

有些场景中，目标机器根本就没有互联网连接——内网机房、涉密环境、离线开发机。对于这种情况，配置镜像站或代理都无从谈起。方案三的思路是"搬运"：在**有网的地方**把镜像下载下来并打包成文件，再通过物理介质（U盘、移动硬盘）转移到目标机器上导入。

就像你出差前在有 Wi-Fi 的地方把电影缓存到手机，上了飞机（断网）也能看。

#### 📖 详细解释

方案三的核心项目是由国内开发者「悟空日常」维护的一个开源工具。它利用 GitHub Actions 的运行环境（位于境外，可以无障碍访问 Docker Hub）来拉取镜像，然后通过 `docker save` 命令导出为 `.tar` 文件，最后将这个文件作为 Action 的 Artifact（产物）供你下载。

整个工作流程如下：

```
┌──────────────────────────────────────────────────────────────┐
│                   GitHub Actions 云端环境                     │
│                                                              │
│  Step 1. 你指定镜像名（如 nginx:latest、mysql:8.0）          │
│      │                                                       │
│      ▼                                                       │
│  Step 2. Runner 在境外网络直接 docker pull                   │
│      │                                                       │
│      ▼                                                       │
│  Step 3. docker save -o image.tar nginx:latest               │
│      │                                                       │
│      ▼                                                       │
│  Step 4. 上传 .tar 作为 Action Artifact                      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
        │
        │ 从 GitHub 下载 artifact（.tar 文件）
        ▼
┌──────────────────────────────────────────────────────────────┐
│                     你的离线目标机器                          │
│                                                              │
│  Step 5. docker load -i image.tar                            │
│      │                                                       │
│      ▼                                                       │
│  Step 6. docker images  确认镜像已导入                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

> 💡 **核心洞见**：方案三的精妙之处在于"借道"——GitHub Actions 的 Runner 跑在境外云环境，天然不受国内网络限制。你不用自己翻墙，让 GitHub 的服务器帮你下载，然后你从 GitHub 取结果就行。

#### 💻 使用概述

项目在 GitHub 上开源（搜索「悟空日常 Docker 离线镜像」），README 中有详细的使用说明。大致流程如下：

1. **Fork 项目**：将项目 fork 到自己的 GitHub 账号下
2. **触发下载**：通过项目的 Issue 模板或修改配置文件，指定你需要下载的镜像名称和标签
3. **等待 Action 执行**：GitHub Action 自动触发，拉取镜像并打包
4. **下载产物**：进入 Actions 页面，下载生成的 Artifact（`docker-images.tar`）
5. **导入目标机器**：将 `.tar` 文件拷贝到目标服务器，执行：
   ```bash
   docker load -i docker-images.tar
   ```

| 步骤 | 操作位置 | 是否需网络 |
|---|---|---|
| Fork + 触发 | 任何能访问 GitHub 的设备 | 是 |
| 下载产物 | 任何能访问 GitHub 的设备 | 是 |
| 导入镜像 | 离线目标机器 | 否 |

> ⚠️ **注意事项**：GitHub Action 的 Artifact 有保留期限（默认 90 天），下载产物后建议及时使用或另外备份。另外，单个镜像的 `.tar` 文件可能很大（几百 MB 到几个 GB），下载和拷贝需要预留足够时间和存储空间。

> 🔗 **关联知识**：方案三与方案一都使用了 GitHub Actions 做自动化。方案一用它做镜像的定期同步转存，方案三用它做一次性离线下载。GitHub Actions 在本课程后续章节会有更系统的讲解。

---

### 4.3 方案四：一键脚本自动测速下载

#### 🧠 直观理解

方案二需要你手动去查、去试哪个镜像源当前可用；不同地区、不同网络运营商下，同一个镜像源的表现也完全不同。方案四的一个 Bash 脚本帮你把这份"试错工作"自动化了——它内置了一批常用镜像源地址，逐一测试延迟，自动选出最快的那个来下载你的镜像。

类似于你打开外卖 App，它帮你把附近所有餐厅按距离和评分排好序，你只需要说"我要吃黄焖鸡"，它就自动从最好的那个店下单。

#### 📖 详细解释

一键脚本的工作机制可以拆成三个阶段：

```
┌──────────────────┐     ┌──────────────────────┐     ┌──────────────────┐
│   阶段一：候选池   │────▶│   阶段二：可用性探测   │────▶│  阶段三：择优下载  │
│                  │     │                      │     │                  │
│ 脚本内置了十几个  │     │ 逐个向镜像源发起连接  │     │ 选出延迟最低/     │
│ 常见 Docker 镜像  │     │ 测试（ping/tcp），    │     │ 最先响应的源，    │
│ 源地址列表       │     │ 记录每个源的延迟和    │     │ 用它执行          │
│                  │     │ 超时情况             │     │ docker pull       │
└──────────────────┘     └──────────────────────┘     └──────────────────┘
```

> 💡 **核心洞见**：方案四的差异化优势就在于**自动测速选最优**。方案二是"配置好镜像站，拉取时自动用"，但镜像源哪天挂了你不一定知道；方案一需要手动注册、手动打 tag。方案四把这个过程完全自动化——测速 → 选优 → 下载，一条命令搞定。

#### 💻 代码示例

基本命令格式：

```bash
# 格式：通过 curl 拉取脚本并执行，末尾传入完整镜像名（含标签）
bash <(curl -sSL <脚本地址>) <完整镜像名>:<标签>
```

以拉取小雅的 alist 镜像为例：

```bash
# 一键下载小雅 alist 镜像
bash <(curl -sSL https://raw.githubusercontent.com/xxx/docker-pull/main/docker-pull.sh) xiaoyaliu/alist:latest
```

脚本执行时终端输出示例：

```
========================================
  Docker 镜像一键下载工具
  自动测速 · 择优下载
========================================

[1/3] 加载镜像源列表... 共 12 个候选源
[2/3] 正在测试各镜像源可用性...

  [TEST] docker.mirrors.ustc.edu.cn .......... 38ms   OK
  [TEST] hub-mirror.c.163.com ................ 112ms  OK
  [TEST] mirror.baidubce.com ................. TIMEOUT
  [TEST] dockerhub.azk8s.cn .................. 67ms   OK
  [TEST] registry.docker-cn.com .............. 205ms  OK
  ...

[3/3] 最优镜像源: docker.mirrors.ustc.edu.cn (38ms)
       正在拉取 xiaoyaliu/alist:latest ...

latest: Pulling from xiaoyaliu/alist
Digest: sha256:...
Status: Downloaded newer image

========================================
  下载完成！耗时: 12.3s
========================================
```

> ⚠️ **注意事项**：脚本内置的镜像源列表是硬编码的，如果大量镜像源因政策变化同时失效，脚本可能无法正常工作。建议关注脚本项目的更新，或 fork 后自行维护镜像源列表。

| 维度 | 方案二（配置镜像站） | 方案四（一键脚本） |
|---|---|---|
| 配置方式 | 手动编辑 daemon.json | 无需配置，一行命令 |
| 生效范围 | 全局，所有 docker pull 都走镜像站 | 单次，只对当前拉取生效 |
| 镜像源选择 | 静态，需手动更新 | 动态，自动测速选最优 |
| 适合场景 | 长期使用 Docker 的开发机 | 临时拉取、快速尝试 |

---

### 4.4 方案五：Cloudflare Worker 自建镜像加速

#### 🧠 直观理解

前面四种方案都是使用别人搭建好的服务——公共镜像站、阿里云、GitHub Actions。方案五则是"自己动手，丰衣足食"：利用 Cloudflare 的全球边缘网络，写一个 Worker 脚本充当 Docker Hub 的反向代理，搭建一个**属于你自己的镜像加速服务**。

别人用的是公共卫生间，方案五是你在自己家装了一个专属卫生间——完全由你掌控。

#### 📖 详细解释

Cloudflare Worker 是 Cloudflare 提供的 Serverless（无服务器）计算服务。你的代码会被部署到 Cloudflare 遍布全球的边缘节点上，当请求到达距离用户最近的节点时执行。

方案五的原理是：

```
docker pull nginx
       │
       ▼
┌──────────────────┐     Cloudflare 全球网络     ┌──────────────┐
│   你的机器        │ ──────────────────────────▶ │ Docker Hub   │
│   (中国境内)      │                              │ (docker.io)  │
│                  │     Worker 作为反向代理       │              │
│  配置为拉取你的   │     your-worker.workers.dev  │              │
│  Worker 地址     │ ──────────────────────────▶ │              │
└──────────────────┘                              └──────────────┘
```

具体来说：

1. 你在 Cloudflare 上创建一个 Worker，部署一段 JavaScript 代码
2. 这段代码的功能是：接收 Docker 客户端的 pull 请求，转发到 Docker Hub，再把响应返回
3. 你将 Worker 的域名配置为 Docker 的 `registry-mirror`
4. Docker pull 时，请求经过 Cloudflare 的全球网络到达 Docker Hub，利用 Cloudflare 的优质网络线路规避国内直连的瓶颈

#### 💻 部署概述

项目在 GitHub 上有完整的开源实现（搜索「Cloudflare Worker Docker Mirror」），README 提供了详细的部署步骤。大致流程：

1. 注册 Cloudflare 账号，开通 Workers 服务
2. 进入 Workers 管理面板，创建一个新的 Worker
3. 将项目提供的 JavaScript 代码粘贴到编辑器中
4. 部署 Worker，获得一个 `*.workers.dev` 域名
5. 将这个域名配置到你的 `daemon.json` 的 `registry-mirrors` 中

```json
{
  "registry-mirrors": [
    "https://your-worker-name.your-subdomain.workers.dev"
  ]
}
```

> ⚠️ **注意事项**：Cloudflare Worker 的免费套餐有每日请求次数限制（10 万次/天）。对于个人开发者日常使用绰绰有余，但如果要用于团队共享或高频 CI/CD 流水线，需要考虑付费方案或限流策略。

| 维度 | 方案二（公共镜像站） | 方案五（CF Worker 自建） |
|---|---|---|
| 搭建门槛 | 极低，改一行配置 | 中，需注册 CF + 部署 Worker |
| 稳定性 | 依赖第三方维护 | 自己掌控，配合 CF 的可用性 |
| 成本 | 免费 | 免费套餐够用，大流量需付费 |
| 隐私性 | 拉取记录经过第三方 | 只有你自己和 CF 知道 |
| 灵活性 | 只能使用别人提供的源 | 可以自定义转发逻辑 |

> 💡 **核心洞见**：方案五的本质是"利用 Cloudflare 的网络优势绕过国内网络限制"。Cloudflare 在全球有数百个边缘节点，和国内之间的网络连接质量通常优于国内直连 Docker Hub。这相当于花钱（或免费额度）买了一条优质网络通道。

---

### 4.5 方案对比与选择

学完了全部五种方案，现在把它们放在一起做横向对比，帮助你快速判断在什么情况下该用哪一种。

#### 📊 五种方案横向对比

| 方案 | 原理 | 配置难度 | 稳定性 | 适用场景 | 关键限制 |
|---|---|---|---|---|---|
| 方案一：阿里云 ACR 转存 | 私有仓库中转 | ⭐⭐⭐ 中 | ⭐⭐⭐⭐⭐ 高 | 个人长期使用 | 需注册阿里云；命名空间管理 |
| 方案二：配置镜像站 | daemon.json 配置 | ⭐ 低 | ⭐⭐⭐ 中 | 快速配置，全局加速 | 公共源可能失效 |
| 方案三：GitHub Action 离线 | 云端拉取→打包下载 | ⭐⭐ 较低 | ⭐⭐⭐⭐ 较高 | 完全断网环境 | 需手动搬运；Artifact 有期限 |
| 方案四：一键脚本 | 自动测速→择优下载 | ⭐ 低 | ⭐⭐⭐ 中 | 临时拉取，快速尝试 | 依赖脚本内置源列表 |
| 方案五：CF Worker 自建 | 反向代理加速 | ⭐⭐⭐ 中 | ⭐⭐⭐⭐ 较高 | 自建服务，长期稳定 | 需 CF 账号；免费额有限 |

#### 🤔 如何选择？——决策树

```
你需要在国内拉取 Docker 镜像时：

   ├── 目标机器完全断网（内网/涉密环境）？
   │   └── 是 → 方案三：GitHub Action 离线下载 → 物理搬运 .tar 文件
   │
   ├── 你是个人开发者，希望一劳永逸？
   │   ├── 愿意花十分钟配置一次 → 方案一：阿里云 ACR 转存（最稳定）
   │   └── 想立刻生效 → 方案二：配置镜像站（几分钟搞定）
   │
   ├── 你只是临时拉一个镜像，不想折腾配置？
   │   └── 是 → 方案四：一键脚本（一行命令搞定）
   │
   ├── 你想要完全自主可控的加速服务？
   │   └── 是 → 方案五：Cloudflare Worker 自建
   │
   └── 推荐组合（个人开发者日常）：
       ├── 主力：方案一（稳定可靠，自动同步）
       ├── 备用：方案二（配置 daemon.json 作为全局兜底）
       └── 临时：方案四（遇到冷门镜像时快速拉取）
```

> 💡 **核心洞见**：这些方案不是非此即彼的关系。最成熟的策略是**组合使用**——用方案一作为日常主力（稳定、自动同步），方案二作为全局兜底，方案四处理偶发的临时需求。方案三和方案五分别是应对断网环境和自建服务需求时的补充选项。



## 五、Docker 镜像搜索与第一部分收尾

### 5.1 Docker 镜像搜索网站

#### 🧠 直观理解

你已经装好了 Docker，也掌握了多种镜像拉取方案，但还有一个关键问题没解决：**你想用的那个镜像，在 Docker Hub 上到底叫什么名字？有哪些可用版本？** 镜像搜索网站就像一个"Docker 镜像的黄页"——你输入关键词，它告诉你有哪些镜像、哪些版本、支持哪些硬件架构，然后你就可以配合前面学到的拉取方案，把镜像顺利地弄下来。

#### 📖 详细解释

还记得课程开头老师在 GitHub 上建的那个项目吗？在项目页面的最底部（通常是 README.md 文件的末尾），老师放置了一个镜像搜索网站的入口。这个网站本质上是对 Docker Hub 官方数据的**浏览器可视化呈现**，让国内用户在无法顺畅访问 Docker Hub 的情况下，仍然能够搜索和浏览镜像信息。

> 💡 **核心洞见**：镜像搜索是 Docker 使用链条的"信息入口"。装好 Docker 是基础，拉取镜像靠方案，但**不知道镜像叫什么**，你连搜都搜不到，后续一切无从谈起。这也是为什么老师把"去哪里找镜像名称"列为课程的三大核心问题之一——它排在拉取镜像之前，是先决条件。

搜索网站提供的关键信息包括：

| 信息维度 | 说明 | 为什么要关注 |
|---|---|---|
| **镜像名称** | 镜像在 Docker Hub 上的完整名称，如 `python`、`nginx`、`mysql` | 这是拉取镜像时必须指定的参数，名称错了就无法下载 |
| **可用版本（Tag）** | 镜像的所有标签，如 `python:3.12`、`python:3.12-slim`、`python:latest` | 不同版本的功能和体积差异巨大，选错可能导致兼容性问题 |
| **支持架构** | 镜像支持的 CPU 架构，如 `amd64`、`arm64/v8`、`arm/v7` | 在 ARM 设备（如树莓派、Apple M 系列 Mac）上拉取必须确认架构匹配 |
| **镜像大小** | 镜像各层（Layer）的大小及总压缩体积 | 影响下载时间和存储占用，`-slim` 和 `-alpine` 版本体积通常只有完整版的 1/10 |
| **更新历史** | 镜像最近更新时间 | 判断镜像是否仍在维护，避免使用已废弃的镜像 |

#### 💻 使用示例：搜索 Python 镜像

**Step 1：打开搜索网站**

在老师项目的 README 底部找到搜索入口链接，点击进入。页面通常非常简洁，只有一个搜索框居中放置。

**Step 2：搜索关键词**

在搜索框中输入 `python`，点击搜索或敲回车确认。网站会向 Docker Hub 发起查询，返回与 Python 相关的所有官方和社区镜像。

**Step 3：分析搜索结果**

搜索结果页面会展示以下内容：

```text
┌──────────────────────────────────────────────────────────────┐
│  搜索: python                                                  │
│──────────────────────────────────────────────────────────────│
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ ⭐ python  (Official Image)                              │ │
│  │   描述: Python is an interpreted, high-level...          │ │
│  │   下载量: 1B+    星标: 8.5k                              │ │
│  │                                                         │ │
│  │   可用版本:                                              │ │
│  │   ┌─────────────┬──────────┬────────────────────┐       │ │
│  │   │ Tag         │ 大小     │ 最后推送日期        │       │ │
│  │   ├─────────────┼──────────┼────────────────────┤       │ │
│  │   │ 3.12        │ 370 MB   │ 2024-12-03         │       │ │
│  │   │ 3.12-slim   │ 44 MB    │ 2024-12-03         │       │ │
│  │   │ 3.12-alpine │ 17 MB    │ 2024-12-03         │       │ │
│  │   │ 3.11        │ 360 MB   │ 2024-12-03         │       │ │
│  │   │ latest      │ 370 MB   │ 2024-12-03         │       │ │
│  │   └─────────────┴──────────┴────────────────────┘       │ │
│  │                                                         │ │
│  │   支持架构:                                              │ │
│  │   ┌──────────────────────────────────────────────────┐  │ │
│  │   │ ✅ linux/amd64   ✅ linux/arm64/v8                │  │ │
│  │   │ ✅ linux/arm/v7  ✅ linux/ppc64le                 │  │ │
│  │   │ ✅ linux/s390x                                    │  │ │
│  │   └──────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │   其他相关镜像:  python-django, python-alpine, ...       │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

> 💡 **核心洞见**：注意 `3.12`、`3.12-slim`、`3.12-alpine` 三者体积的差异——完整版 370 MB，`slim` 精简到 44 MB，`alpine` 更是只有 17 MB。如果你只是在容器里跑一个简单的 Python 脚本，完全没有必要拉 370 MB 的完整版。**选择合适的 Tag 能节省大量拉取时间和磁盘空间**，这在网络受限的国内环境下尤为重要。

> 🔗 **关联知识**：搜索得到镜像名称（如 `python:3.12-slim`）后，你可以使用前两章学到的任何拉取方案把它下载到本地——无论是方案一（阿里云私有仓库镜像转存），还是方案二至五（镜像站离线下载、一键脚本、CF-Worker 代理）。搜索和拉取是前后衔接的两个步骤。

#### 🔀 搜索网站 vs Docker Hub 官网

| 维度 | 镜像搜索网站（项目附带） | Docker Hub 官网 |
|---|---|---|
| **国内可访问性** | 可正常访问 | 可能无法访问或被限速 |
| **搜索体验** | 极简，速度极快 | 功能丰富但加载缓慢 |
| **镜像详情** | 版本 + 架构 + 大小 | 完整描述 + Layer 信息 + 使用指南 |
| **适用场景** | **快速查找镜像名称和版本** | 深入研究镜像细节（网络允许时） |
| **设计目的** | 解决"不知道镜像叫什么"的问题 | 官方的镜像托管与分享平台 |

> ❓ **常见疑问**：这个搜索网站会不会信息滞后？网站的搜索结果直接来源于 Docker Hub 的公开 API，信息是实时查询的——它不是静态的数据快照，而是每次搜索都向 Docker Hub 发起实时请求。因此你看到的版本和架构信息与 Docker Hub 官网是一致的。

### 5.2 Docker 第一部分内容回顾

至此，课程 Docker 部分的内容已全部讲解完毕。让我们回到课程开篇（详见 [第一章：课程引入与 Docker Linux 安装](#一课程引入与-docker-linux-安装)）提出的三大核心问题，逐一回顾它们在本章中是如何得到解答的。

#### 📋 三大核心问题解答对照

| 核心问题 | 对应章节 | 核心方案 | 一句话小结 |
|---|---|---|---|
| **1. 如何安装 Docker？** | [第二章：Docker 安装（Windows/Mac）](#二docker-windows-与-mac-安装)及 [第一章：Docker Linux 安装](#一课程引入与-docker-linux-安装) | GitHub Action 定时从官网同步安装脚本，配合 GitHub + Gitee 双地址，国内用户一键安装 | 用 Action 把"下载"这件事搬到境外 Runner 上做，用户只管"执行" |
| **2. 如何拉取镜像？** | [第三章：方案一 阿里云私有仓库镜像转存](#三方案一阿里云私有仓库镜像转存)及 [第四章：方案二至五](#四方案二至五镜像站离线下载一键脚本cloudflare-worker) | 五种拉取方案覆盖从"最稳"到"最快"的各种场景：阿里云转存、镜像站下载、一键脚本、CF-Worker 代理、离线包下载 | 没有银弹——根据网络环境选方案，极速就用代理，稳定就用个人仓库转存 |
| **3. 如何查找镜像名称？** | 本章 5.1 节 | 使用项目附带的镜像搜索网站，输入关键词即可查看所有可用版本和架构信息 | 搜索网站是"信息入口"，配合前五个拉取方案形成完整闭环 |

#### 🔄 Docker 使用完整流程

将三大环节串联起来，一个完整的国内 Docker 使用流程如下：

```
             ┌──────────────────────┐
             │  Step 1: 安装 Docker  │
             │  (GitHub/Gitee 脚本)  │
             └──────────┬───────────┘
                        │
                        ▼
             ┌──────────────────────┐
             │  Step 2: 搜索镜像名称 │
             │  (镜像搜索网站)        │
             └──────────┬───────────┘
                        │
                        ▼
             ┌──────────────────────┐
             │  Step 3: 拉取镜像     │
             │  (五选一方案)          │
             └──────────┬───────────┘
                        │
                        ▼
             ┌──────────────────────┐
             │  Step 4: 运行容器     │
             │  docker run ...       │
             └──────────────────────┘
```

> ⚠️ **注意事项**：这四大步骤是顺序依赖的——没有安装 Docker 就无法拉取镜像，不知道镜像名称就无法搜索和选择版本，拉取不到镜像也就无法运行容器。任何一步卡住，整个链条都会断裂。本课程 Docker 部分的价值正在于**帮你打通全部四个步骤**。

> 💡 **核心洞见**：回头看，整个 Docker 部分的解决方案本质上都围绕着同一个方法论：**用 GitHub Action 充当国内的"境外代理"**。安装脚本是 Action 定时下载的，镜像拉取（方案一）是 Action 帮你转存的，镜像搜索网站也托管在 Action 输出物上。这验证了老师的核心观点——"这又是一个使用 Action 解决问题的完美案例"。当你再遇到"国内网络限制"类问题时，可以优先思考：Action 能不能帮我做这件事？

### 5.3 课程过渡：进入 GitHub Package

Docker 部分的讲解到此结束。但 GitHub 生态中还有一个与容器镜像密切相关的功能——**GitHub Package Registry**，它允许你在 GitHub 上发布、托管和管理软件包（包括 Docker 镜像、npm 包、Maven 包等），并且可以和 GitHub Action 无缝集成。

> 🔗 **延伸阅读**：接下来的章节将带你从零开始使用 GitHub Package——创建项目、发布第一个包、在 Action 工作流中使用自己发布的包。如果说 Docker 部分教你怎么"下载"镜像，那 GitHub Package 部分教你怎么"发布"和"管理"自己的包。（← 合并时替换为对应的章节链接）

课程的第二部分正式开启——**GitHub Package**，即将登场。

---

> 📝 **Docker 部分小结**：本章（第一至第五节）从"国内 Docker 镜像站下架"这一现实问题出发，系统性地讲解了基于 GitHub Action 的 Docker 安装、镜像拉取（五种方案）、镜像搜索三大核心问题的完整解决方案。掌握这些技能后，你将不再受国内网络限制的影响，可以自由地使用 Docker 进行开发和部署。

## 六、GitHub Package 概述与项目初始化

### 6.1 GitHub Package 是什么

#### 🧠 直观理解

GitHub Package 是 GitHub 官方提供的**包托管仓库**。可以把 GitHub 想象成一个"巨型存储中心"——它不仅托管源代码（Git 仓库），还托管构建产物（软件包）。当你开发了一个前端项目，最终的产物是一个 npm 包；开发了一个 Java 项目，产物是一个 JAR 包——这些"包"都可以推送到 GitHub Package，让你的团队成员或社区用户像拉源码一样方便地拉取软件包。

> 💡 **核心洞见**：GitHub Package 让 GitHub 具备了"开发者一站通"的能力。过去代码托管和包托管是割裂的（GitHub + npm registry），现在 GitHub 把两者整合在同一个平台下，源码和产物共用一个权限体系、一套 CI/CD 流水线。

#### 📖 详细解释

在日常开发中，不同技术栈使用不同的包管理器来管理依赖：

| 语言/技术栈 | 包管理器 | 官方注册表 |
|---|---|---|
| JavaScript/Node.js | npm / yarn / pnpm | https://registry.npmjs.org |
| Java | Maven / Gradle | Maven Central |
| .NET | NuGet | https://nuget.org |
| Ruby | RubyGems | https://rubygems.org |
| Docker | Docker | Docker Hub |
| Go | Go Modules | https://proxy.golang.org |

GitHub Package 的定位是这些官方注册表的**替代或补充**。你可以选择把自己的包只推送到 GitHub Package，也可以同时推送到官方仓库和 GitHub Package（双写），取决于你的团队策略。

```
┌─────────────────────────────────────────────────┐
│                 GitHub 生态圈                      │
│                                                   │
│  ┌──────────┐   ┌──────────┐   ┌──────────────┐ │
│  │ Git 源码  │   │ CI/CD    │   │ GitHub       │ │
│  │ 代码仓库  │   │ Actions  │   │ Package      │ │
│  └────┬─────┘   └────┬─────┘   └──────┬───────┘ │
│       │              │                │          │
│       │  push 代码    │  触发构建       │ 发布产物  │
│       └──────────────┴───────────────►│          │
│                                       │          │
│                                ┌──────▼───────┐  │
│                                │  npm / Maven  │  │
│                                │  Docker ...   │  │
│                                └──────────────┘  │
└─────────────────────────────────────────────────┘
```

#### 🔀 对比辨析：npm 官方仓库 vs GitHub Package

| 维度 | npm 官方仓库 | GitHub Package |
|---|---|---|
| 适用范围 | 仅 npm 包 | npm、Maven、NuGet、Docker、RubyGems 等 |
| 权限控制 | 独立的 npm 账号体系 | 复用 GitHub 仓库权限（Teams/GitHub 用户） |
| 与源码关联 | 无直接关联 | 包绑定在 GitHub 仓库下，天然关联 |
| 免费额度 | 公开包免费，私有包付费 | 公开仓库免费；私有仓库 500MB 存储 + 1GB/月带宽 |
| CI/CD 集成 | 需要单独配置 token | 原生集成 GitHub Actions（`GITHUB_TOKEN`） |

### 6.2 免费额度详解

GitHub 对 Package 功能的收费标准区分公开仓库和私有仓库：

| 仓库类型 | 存储空间 | 数据传输 | 费用 |
|---|---|---|---|
| 公开仓库 | 无限制 | 无限制 | 免费 |
| 私有仓库 | 500 MB | 1 GB / 月 | 免费（超出后按量计费） |

> ⚠️ **注意事项**：这里的"存储空间"指所有包的累计大小，非单个包的大小限制。"数据传输"指从 GitHub Package 下载包的流量（出站流量），上传不计。

> ❓ **常见疑问**：为什么私有仓库还有限额？因为私有包是商用场景，GitHub 用免费额度覆盖小团队和试用阶段，超出的收费部分是其商业模式的来源。如果你只是学习或开源，公开仓库完全够用。

### 6.3 项目初始化 Step-by-Step

#### 🎯 目标

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 从一个空 GitHub 仓库开始，在本地初始化一个 npm 包项目
> - [ ] 理解 `npm init` 中 `@scope/name` 包名格式的含义
> - [ ] 区分并解释 `package.json` 与 `package-lock.json` 的作用

#### 🏗️ 前置准备

- 拥有一个 GitHub 账号，并已创建一个名为 `package-example` 的空仓库
- 安装了 GitHub Desktop（或掌握 `git clone` 命令）
- 能够使用命令行（终端/命令提示符/PowerShell）

#### 💻 Step-by-Step

**Step 1: 创建 GitHub 仓库并克隆到本地**

老师以一个全新项目 `package-example` 为例，仓库中只有一个极简的 `index.js` 文件：

```javascript
// 文件名: index.js
// 功能: 最简入口文件，仅输出 Hello World

console.log('Hello World');
```

使用 GitHub Desktop（或命令行）将仓库克隆到本地：

```bash
# 使用命令行克隆（等价于老师视频中的 GitHub Desktop 操作）
git clone https://github.com/你的用户名/package-example.git
cd package-example
```

**Step 2: 配置 Node.js 开发环境**

> 🔗 **关联知识**：Node.js 是 JavaScript 的运行时环境，npm（Node Package Manager）随 Node.js 一起安装。后续使用 GitHub Package 发布 npm 包，必须依赖这套工具链。

2.1 前往 [nodejs.org](https://nodejs.org) 下载并安装 Node.js（推荐 LTS 版本）。

2.2 安装完成后，打开命令行，验证环境：

```bash
# 检查 Node.js 版本
node -v
# 预期输出示例: v20.11.0

# 检查 npm 版本
npm -v
# 预期输出示例: 10.2.4
```

> ⚠️ **注意事项**：如果 `node -v` 或 `npm -v` 提示"command not found"，说明安装未成功或环境变量未配置。可以尝试重新打开终端，或检查安装路径是否被加入了系统的 PATH 环境变量。

**Step 3: 初始化 npm 包 —— `npm init`**

进入项目目录后，执行 `npm init` 将当前目录初始化为一个 npm 包：

```bash
cd package-example
npm init
```

执行后，`npm init` 会以**交互式问答**的形式引导你填写包的元信息。以下是老师演示时的完整填写清单：

| 字段 | 提示文本 | 老师填入的值 | 解释 |
|---|---|---|---|
| `name` | `package name:` | `@你的用户名/package-example` | 包名，使用 scoped 格式 |
| `version` | `version:` | `1.0.0`（默认，一路回车） | 语义化版本号 |
| `description` | `description:` | （留空，回车跳过） | 包描述 |
| `entry point` | `entry point:` | `index.js`（默认） | 入口文件 |
| `test command` | `test command:` | `exit 0` | 测试命令 |
| `git repository` | `git repository:` | （自动识别仓库 URL） | Git 仓库地址 |
| `keywords` | `keywords:` | （留空，回车跳过） | 搜索关键词 |
| `author` | `author:` | （留空，回车跳过） | 作者 |
| `license` | `license:` | `ISC`（默认） | 开源协议 |

> 💡 **核心洞见 —— `@scope/package-name` 格式**：这是 **scoped package**（作用域包）的命名方式。`@` 后面紧跟的是 npm 的 scope，在 GitHub Package 场景下，这个 scope 就是你的 GitHub 用户名或组织名。这样命名有两大好处：
> 1. **命名空间隔离**：`@zhangsan/utils` 和 `@lisi/utils` 是不同的包，避免命名冲突。
> 2. **自动关联 GitHub**：当 scope 与 GitHub 用户名匹配时，GitHub Package 能自动识别包所属的仓库。

> ⚠️ **注意事项 —— `test command: exit 0`**：`npm init` 要求填写测试命令，但项目刚开始还没有测试代码。老师填入 `exit 0`，这是一个**占位技巧**：`exit 0` 在命令行中表示"成功退出"，所以 `npm test` 运行时不会报错。等以后写了真正的测试，再替换为 `jest` 或 `mocha` 等测试框架的命令。

完成后，项目根目录会自动生成 `package.json` 文件，内容如下：

```json
// 文件名: package.json
// 功能: npm 包的核心配置文件，记录包的元信息与依赖

{
  "name": "@你的用户名/package-example",
  "version": "1.0.0",
  "description": "",
  "main": "index.js",
  "scripts": {
    "test": "exit 0"
  },
  "repository": {
    "type": "git",
    "url": "git+https://github.com/你的用户名/package-example.git"
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "bugs": {
    "url": "https://github.com/你的用户名/package-example/issues"
  },
  "homepage": "https://github.com/你的用户名/package-example#readme"
}
```

#### `package.json` 关键字段详解

| 字段 | 类型 | 含义 | 对 GitHub Package 的意义 |
|---|---|---|---|
| `name` | `string` | 包的唯一标识，符合 npm scoped 格式 | 决定包在 GitHub Package 中的 URL 路径 |
| `version` | `string` | 语义化版本号（SemVer） | 每次发布需更新版本，同一版本不可覆盖 |
| `main` | `string` | 包的入口文件 | 其他项目 `require()` 或 `import` 时的默认文件 |
| `scripts.test` | `string` | `npm test` 时执行的命令 | GitHub Actions 构建时会自动运行此命令 |
| `repository` | `object` | 关联的 Git 仓库信息 | GitHub Package 将包与仓库自动关联 |

**Step 4: 安装依赖 —— `npm install`**

```bash
npm install
```

执行后会在项目根目录生成 `package-lock.json` 文件。

> 💡 **核心洞见 —— `package-lock.json` 的作用**：`package.json` 定义的是"想要什么依赖"（版本范围，如 `^2.0.0` 表示 2.x.x 都可），而 `package-lock.json` 锁定的则是"确切装了什么"（精确版本，如 `2.3.1`）。这保证了团队所有成员和 CI/CD 环境安装的依赖版本**完全一致**，消除"在我电脑上能跑啊"的问题。

#### ✅ 验证结果

完成以上步骤后，确认以下检查点：

- [ ] `node -v` 和 `npm -v` 正常输出版本号
- [ ] 项目根目录存在 `package.json`，且 `name` 字段为 `@用户名/package-example`
- [ ] 项目根目录存在 `package-lock.json`
- [ ] `scripts.test` 为 `"exit 0"`，执行 `npm test` 不报错

---

### 6.4 本节知识图谱

```
                           ┌──────────────────────────┐
                           │    GitHub Package         │
                           │    GitHub 的包托管服务      │
                           └────────────┬─────────────┘
                                        │
                  ┌─────────────────────┼─────────────────────┐
                  │                     │                     │
                  ▼                     ▼                     ▼
        ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
        │  支持多种        │   │   免费额度        │   │   与源码深度绑定   │
        │   包管理器        │   │                  │   │                  │
        │  · npm           │   │  公开仓库: 免费    │   │  · 同一权限体系    │
        │  · Maven/Gradle  │   │  私有仓库:        │   │  · 同一 CI/CD     │
        │  · NuGet         │   │    500MB + 1GB/月 │   │  · GITHUB_TOKEN   │
        │  · Docker        │   │                  │   │   自动认证        │
        └─────────────────┘   └─────────────────┘   └─────────────────┘
```

### 💡 一句话总结

> GitHub Package 是 GitHub 生态中的"包管理中枢"，它让开发者可以在同一个平台上管理源码和构建产物。本节通过创建一个极简的 npm 项目，演示了从零搭建可发布到 GitHub Package 的项目环境全过程。

---


## 七、发布包到 GitHub Package

### 7.1 发布流程概述

在 M06 中，我们已经初始化了一个 npm 项目（`package.json` 已就绪）。本节的目标是将这个 npm 包自动发布到 GitHub Package，整个流程可以概括为三步：

```
┌──────────────────────────────────────────────────────────────────────┐
│                         发布三步走                                    │
│                                                                      │
│  Step 1                    Step 2                    Step 3          │
│  ┌────────────────┐       ┌────────────────┐       ┌──────────────┐ │
│  │ 创建 Workflow   │──────▶│ 配置            │──────▶│ 创建 Release  │ │
│  │ release-package │       │ package.json   │       │ 触发发布      │ │
│  │ .yml            │       │ publishConfig  │       │               │ │
│  └────────────────┘       └────────────────┘       └──────────────┘ │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

- **Step 1**：在 `.github/workflows/` 下创建 Action workflow 文件，定义"当 Release 创建时自动执行 npm publish"
- **Step 2**：在 `package.json` 中添加 `publishConfig`，告诉 npm 发布目标是谁
- **Step 3**：提交代码，在 GitHub 上创建 Release，触发 Action 自动发布

> ⚠️ **注意事项**：Workflow 中的 `registry-url` 和 `package.json` 中的 `publishConfig` 是两处配套配置，**缺一不可**。如果只配了一处，发布会失败。

> 🔗 **关联知识**：本模块的 Action workflow 延续了前面章节 Action 的使用经验；发布的包将在 M08 中被其他项目消费。

---

### 7.2 创建 Workflow 文件

#### 🎯 目标

创建一个 GitHub Action workflow，每当仓库中创建了 Release 时，自动将 npm 包发布到 GitHub Package Registry。

#### 🏗️ 前置准备

- 项目根目录下已有 `package.json`（在 M06 中创建）
- 仓库已推送到 GitHub

#### 💻 Step-by-Step

**Step 1: 创建目录结构**

首先在项目根目录下创建 `.github/workflows/` 目录：

```
项目根目录/
├── .github/
│   └── workflows/
│       └── release-package.yml    ← 新建
├── package.json
└── index.js
```

> `release-package.yml` 这个文件名并不固定，只要在 `.github/workflows/` 目录下且以 `.yml` 结尾即可。取一个见名知义的名字是最好的。

**Step 2: 编写 workflow 文件**

创建 `.github/workflows/release-package.yml`，完整内容如下：

```yaml
# 文件名: .github/workflows/release-package.yml
# 功能: 当仓库创建 Release 时，自动发布 npm 包到 GitHub Package

name: Release Package

# 触发器：每当有 Release 被创建时触发
on:
  release:
    types: [created]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      # 步骤 1：检出仓库代码
      - name: Checkout
        uses: actions/checkout@v3

      # 步骤 2：配置 Node.js 环境
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          # 重点：指定 npm 发布的注册表地址为 GitHub Package
          registry-url: https://npm.pkg.github.com

      # 步骤 3：发布包到 GitHub Package
      - name: Publish to GitHub Package
        run: npm publish
        env:
          # GITHUB_TOKEN 由 GitHub Action 自动提供，无需手动创建
          NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

#### 📖 逐行解析

| 行号范围 | 配置项 | 解释 |
|---|---|---|
| `name: Release Package` | workflow 名称 | 将在 GitHub Actions 页面显示的名称，便于识别 |
| `on: release: types: [created]` | 触发器 | 当仓库中有 Release 被创建（`created`）时触发。其他可选的 type 还有 `published`、`prereleased` 等 |
| `jobs: publish:` | Job 定义 | 定义名为 `publish` 的 job，所有步骤在此 job 中执行 |
| `runs-on: ubuntu-latest` | 运行环境 | Job 在最新版 Ubuntu 虚拟机上执行 |
| `actions/checkout@v3` | 检出代码 | 将仓库代码拉到 Action 运行环境中，后续步骤才能操作文件 |
| `actions/setup-node@v3` | 配置 Node 环境 | 安装指定版本的 Node.js，同时配置 npm 的包仓库地址 |
| `registry-url: https://npm.pkg.github.com` | 注册表地址 | **核心配置**。告诉 npm：`npm publish` 时，包发布到这个地址（而非公共 npm registry） |
| `run: npm publish` | 发布命令 | 执行 npm 的发布命令 |
| `NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}` | 认证令牌 | 发布包到 GitHub Package 需要认证。`GITHUB_TOKEN` 由 GitHub Action 在运行时自动注入 |

> 💡 **核心洞见**：`GITHUB_TOKEN` 是 GitHub Action 内置的自动令牌，你不需要去 Settings 里手动创建任何 Token。只要像上面这样在 `env` 中引用 `secrets.GITHUB_TOKEN`，GitHub Action 就会在运行时自动生成一个拥有当前仓库写权限的临时 Token。

> ⚠️ **注意事项**：`registry-url: https://npm.pkg.github.com` 这个地址是 GitHub Package 的 npm 注册表端点。如果没有配这个地址，`npm publish` 会默认发到公共 npm registry（`https://registry.npmjs.org`），导致发布到错误的位置。**这是本模块最重要的配置项。**

---

### 7.3 配置 package.json

Workflow 文件准备好之后，还需要修改项目的 `package.json`，添加 `publishConfig` 字段。

#### 🎯 目标

告诉 npm CLI：这个包的发布目标是 GitHub Package，而非公共 npm registry。

#### 💻 操作步骤

在 `package.json` 的最外层（注意加逗号与前一个字段分隔）添加 `publishConfig`：

```json
{
  "name": "@你的用户名/项目名",
  "version": "1.0.0",
  "description": "一个示例包",
  "main": "index.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "publishConfig": {
    "registry": "https://npm.pkg.github.com"
  }
}
```

#### 📖 关键说明

| 配置项 | 值 | 作用 |
|---|---|---|
| `publishConfig.registry` | `https://npm.pkg.github.com` | 声明该包发布目标为 GitHub Package Registry |

> 💡 **核心洞见**：`publishConfig` 和 workflow 中的 `registry-url` 是一对配套配置。`publishConfig` 写在 `package.json` 中，是包的"身份声明"——"我属于 GitHub Package"；`registry-url` 写在 workflow 中，是 Action 执行环境的运行时配置——"npm publish 命令走这个地址"。两者缺一，发布都会失败。

> ⚠️ **注意事项**：如果你的 `package.json` 中 `name` 字段不是 scoped 格式（即不是 `@scope/package-name` 的形式），GitHub Package 也能支持非 scoped 包名，但建议使用 scoped 格式以明确归属。

---

### 7.4 提交代码并创建 Release

上面三个文件准备就绪（`release-package.yml`、`package.json`、以及项目代码），接下来提交并触发发布。

#### 💻 Step-by-Step

**Step 1: 提交并推送代码**

将所有变更提交到 GitHub：

```bash
# 将所有变更添加到暂存区
git add .

# 提交
git commit -m "feat: 添加自动发布到 GitHub Package 的 workflow"

# 推送到远程仓库
git push origin master
```

**Step 2: 在 GitHub 上创建 Release**

在 GitHub 仓库页面，按以下步骤操作：

```
┌─────────────────────────────────────────────────────────────┐
│                    创建 Release 流程                         │
│                                                             │
│  GitHub 仓库页面                                             │
│       │                                                     │
│       ▼                                                     │
│  ┌───────────────────────┐                                  │
│  │ 点击右侧 "Releases"   │                                  │
│  └───────────┬───────────┘                                  │
│              │                                               │
│              ▼                                               │
│  ┌───────────────────────────┐                              │
│  │ 点击 "Create new release" │                              │
│  └───────────┬───────────────┘                              │
│              │                                               │
│              ▼                                               │
│  ┌─────────────────────────────────────────┐                │
│  │ 1. 创建 Tag：点击 "Create new tag"，    │                │
│  │    输入 v1.0，点击 "Create new tag"     │                │
│  │                                         │                │
│  │ 2. 填写 Release title：release v1.0     │                │
│  │                                         │                │
│  │ 3. 填写版本变化描述（可选）              │                │
│  │                                         │                │
│  │ 4. 点击 "Publish release"              │                │
│  └─────────────────────────────────────────┘                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

| 步骤 | 操作 | 说明 |
|---|---|---|
| 1 | 创建 Tag | 点击 "Choose a tag" 下拉框，输入 `v1.0`，选择 "Create new tag"。Tag 是 Release 的锚点，必须创建 |
| 2 | 填写 Title | 标题用 `release v1.0` 作为版本标识 |
| 3 | 填写描述 | 描述这个版本做了什么改动（新增、修复等） |
| 4 | 点击 Publish | 点击绿色的 "Publish release" 按钮，此时 Release 正式创建，Action workflow 自动触发 |

> ⚠️ **注意事项**：Tag 必须创建——Release 必须关联到一个 Git Tag。如果仓库还没有任何 Tag，需要先点击 "Create new tag" 创建一个（如 `v1.0`），然后再发布。

---

### 7.5 验证发布结果

Release 发布后，Workflow 会自动运行。我们需要确认发布是否成功。

#### 💻 验证步骤

**Step 1: 查看 Action 运行状态**

在 GitHub 仓库页面，点击顶部 **Actions** 选项卡：

```
Actions 页面
    │
    ├── 可以看到名为 "Release Package" 的 workflow 正在运行
    │
    └── 等待所有步骤变为绿色 ✅，表示执行成功
```

如果 workflow 执行失败（出现红色 ❌），点击进入查看具体失败步骤的日志。

**Step 2: 查看 Packages 选项卡**

回到仓库首页（Code 选项卡），在页面右侧可以看到多了一个 **Packages** 选项卡：

```
仓库首页
    │
    ├── 点击 "Packages" 选项卡
    │
    └── 可以看到刚发布的包，包含：
        ├── 包名（如 @用户名/项目名）
        ├── 版本号（如 1.0.0）
        └── 安装使用说明（提示如何使用这个包）
```

#### ✅ 验证结果

如果看到 Packages 选项卡中出现刚发布的包，说明发布完全成功。

#### 🐛 常见排错

| 问题现象 | 可能原因 | 解决方案 |
|---|---|---|
| Action 报错 `401 Unauthorized` | `GITHUB_TOKEN` 未正确配置或权限不足 | 检查 workflow 中 `env.NODE_AUTH_TOKEN` 是否正确引用了 `secrets.GITHUB_TOKEN` |
| Action 报错 `Could not find package.json` | `checkout` 步骤未执行或仓库代码未检出 | 确认 workflow 中 `actions/checkout@v3` 步骤存在且在其他步骤之前 |
| 发布到了公共 npm 而非 GitHub Package | `registry-url` 未配置或 `publishConfig` 缺失 | 检查 workflow 中的 `registry-url` 和 `package.json` 中的 `publishConfig`，两处必须都配 |

> ⚠️ **注意事项**：如果包名在 GitHub 上已被占用（相同的 scope 和包名），`npm publish` 会报错。请确保 `package.json` 中的 `name` 字段在该 scope 下是唯一的。

---

### 📋 本节小结

#### 🗺️ 知识图谱

```
                    ┌────────────────────────────┐
                    │  发布 npm 包到 GitHub       │
                    │       Package               │
                    └────────────┬───────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
    ┌─────────────────┐ ┌───────────────┐ ┌─────────────────┐
    │   Workflow 文件   │ │  package.json │ │  GitHub Release  │
    │ (.github/        │ │  publishConfig│ │  (Tag + Title    │
    │  workflows/      │ │  registry URL │ │   + Publish)     │
    │  release-package │ │               │ │                  │
    │  .yml)           │ │               │ │                  │
    └────────┬────────┘ └───────┬───────┘ └────────┬────────┘
             │                  │                  │
             ▼                  ▼                  ▼
    ┌─────────────────────────────────────────────────────────┐
    │              三者协同：Release 触发 Action               │
    │                → 执行 npm publish                       │
    │                → 包出现在 Packages 选项卡                 │
    └─────────────────────────────────────────────────────────┘
```

#### 💡 一句话总结

> 通过 GitHub Action 的 `on: release` 触发器配合 `registry-url` 和 `GITHUB_TOKEN`，只需创建 Release 就能自动将 npm 包发布到 GitHub Package，零手动操作。

#### 🔗 延伸阅读

> 🔗 **前置知识**：Workflow 文件的编写经验请回顾 [第 X 章：GitHub Action 基础]
>
> 🔗 **下一节**：包发布后，如何在其他项目中使用？详见 [M08：使用 GitHub Package 的包与总结]

---


## 八、使用 GitHub Package 的包与课程总结

### 8.1 使用 GitHub Package 的两步配置概览

> 🎯 **本节目标**
>
> 学完本节后，你将能够：
> - [ ] 在项目的 `dependencies` 中正确声明 GitHub Package 的包
> - [ ] 通过 `.npmrc` 文件配置 GitHub 为 npm 的包管理仓库
> - [ ] 创建 Personal Access Token 并完成认证配置
> - [ ] 使用 `npm install` 成功安装托管在 GitHub 上的包
> - [ ] 理解"发布--使用"的完整闭环流程

在 M07 中，我们通过 GitHub Action 将一个 npm 包成功发布到了 GitHub Package。本节演示如何在另一个项目中使用这个已发布的包，完成"发布--使用"的闭环。

使用 GitHub Package 的包，核心只需要**两步配置**：

1. 在 `package.json` 的 `dependencies` 中声明包名和版本
2. 在 `.npmrc` 文件中声明 GitHub 为 npm 仓库并提供认证 Token

下面逐步拆解每一步的细节。

---

### 8.2 Step 1：配置 package.json 的 dependencies

#### 🎯 目标

在项目的 `package.json` 中添加对 GitHub Package 包的依赖声明。

#### 🏗️ 前置准备

- 已有一个 npm 项目（可以是空项目，通过 `npm init` 初始化）
- 已知目标包的名称和版本（来自 M07 中发布的包：`@texttramp/package-example` `v1.0`）

#### 💻 操作步骤

**Step 1.1: 在 GitHub 网站上找到包的使用说明**

回到 GitHub 网站，点击项目主页右侧的 **Packages** 选项卡，进入包详情页。页面中会提供使用该包的示例代码片段。

**Step 1.2: 将包引用复制到 dependencies 中**

打开项目的 `package.json`，在 `dependencies` 字段中添加包的声明：

```json
{
  "name": "my-consumer-project",
  "version": "1.0.0",
  "dependencies": {
    "@texttramp/package-example": "1.0.0"
  }
}
```

> 这行配置声明了：使用 `@texttramp` 命名空间下名为 `package-example` 的包，版本锁定在 `1.0.0`。

#### 📖 详细解释

```
"@texttramp/package-example": "1.0.0"
  │             │               │
  │             │               └── 版本号：对应 M07 发布时的 v1.0
  │             │
  │             └── 包名：与 package.json 中的 name 字段一致
  │
  └── scope（命名空间）：包发布者的 GitHub 用户名
```

> ⚠️ **注意事项**：`scope` 必须和包发布者的 GitHub 用户名**完全一致**。本例中老师使用的英文名是 `texttramp`。如果你的包发布在另一个用户名下，scope 必须对应。scope 写错是 `npm install` 报 404 的最常见原因。

#### 🔗 推导链：为什么光有 dependencies 不够？

```
起点: 在 dependencies 中声明了 GitHub Package 的包
  │
  ├── 第1步: npm 开始解析依赖
  │   为什么？package.json 是 npm 的"购物清单"
  │   npm 会逐个检查清单中的包，逐一下载
  │
  ├── 第2步: npm 去默认仓库查找
  │   为什么？npm 的默认行为是去 npm 官方仓库（registry.npmjs.org）查找所有包
  │   像 lodash、express 这些普通包不需要额外配置，就是因为它们在官方仓库中
  │
  ├── 第3步: 查找失败
  │   为什么？GitHub Package 托管在 npm.pkg.github.com，不在 npmjs.org 上
  │   如果不额外告知 npm 这个地址，npm 只能搜到 404
  │
  └── 结论: 必须通过 .npmrc 文件告诉 npm："这个 scope 下的包，去 GitHub 找"
```

> 🔗 **关联知识**：这和 M03 中为 Docker 配置镜像加速器的思路相同——告容包管理工具除了默认仓库之外还有哪些可用的仓库地址。Docker 用 `registry-mirrors` 配置，npm 用 `.npmrc` 文件。

---

### 8.3 Step 2：创建 .npmrc 文件 -- 仓库地址声明

#### 🎯 目标

创建 `.npmrc` 文件，声明 GitHub 为特定 scope 下 npm 包的托管仓库。

#### 💻 操作步骤

**Step 2.1: 在项目根目录创建 .npmrc 文件**

```bash
# 在项目根目录下执行
touch .npmrc
```

> ⚠️ **注意事项**：`.npmrc` 必须放在项目的**根目录**下，和 `package.json` 在同一层级。npm 在安装依赖时会自动读取这个文件。如果放错目录，配置不会生效。

**Step 2.2: 添加仓库注册声明**

用编辑器打开 `.npmrc`，写入第一行配置：

```ini
# .npmrc
# 声明 GitHub 为 @texttramp scope 下所有包的仓库地址
@texttramp:registry=https://npm.pkg.github.com
```

#### 📖 详细解释：第一行配置的拆解

```
@texttramp:registry=https://npm.pkg.github.com
  │              │                │
  │              │                └── GitHub Package 的 npm 端点地址
  │              │                    所有 GitHub 上的 npm 包都从这里分发
  │              │
  │              └── registry 指令：声明仓库地址
  │
  └── scope 前缀：作用域/命名空间
      含义：以 @texttramp 开头的包，都从这个地址下载
```

这行的核心含义是：**当 npm 遇到 `@texttramp/xxx` 格式的包名时，不去默认的 npmjs.org，而是去 `npm.pkg.github.com` 查找**。

> 💡 **核心洞见**：`.npmrc` 支持为不同 scope 指定不同仓库。这意味着你可以在同一个项目中同时使用来自官方 npm 的包（如 `lodash`）和来自 GitHub Package 的包（如 `@texttramp/package-example`），互不干扰。npm 会根据 scope 智能路由到正确的仓库。

---

### 8.4 Step 3：创建 Personal Access Token

#### 🎯 目标

在 GitHub 上创建一个 Personal Access Token（Classic），用于在 `.npmrc` 中完成身份认证。

#### 💻 操作步骤

**Step 3.1: 进入 Token 创建页面**

按以下路径导航：

```
GitHub 右上角头像
  → Settings
    → 左侧边栏 Developer settings
      → Personal access tokens
        → Tokens (classic)
          → Generate new token (classic)
```

**Step 3.2: 配置 Token 参数**

在弹出的创建页面中填写：

| 字段 | 填写内容 | 说明 |
|---|---|---|
| **Note** | `package-token` | 起一个辨识度高的名字，方便日后管理 |
| **Expiration** | 按需选择 | 建议设置有效期，到期后重建更安全 |
| **Select scopes** | 勾选 `read:packages` | 只读权限即可（仅使用包）；老师演示时勾选了全部 package 权限 |

> ⚠️ **注意事项**：
>
> - **最小权限原则**：如果你只是**使用**别人发布的包，`read:packages` 就够了。老师勾选全部 package 权限是因为还需要覆盖发布包的场景（M07 中的 `write:packages`）。实际项目中按需赋权。
> - Token 权限敏感度较高，请勿将其提交到 Git 仓库中。`.npmrc` 应加入 `.gitignore`，或使用环境变量替代。

**Step 3.3: 生成并复制 Token**

1. 点击页面底部的 **Generate token**
2. Token 生成后立即**复制**

> ⚠️ **注意事项**：Token **只显示这一次**。离开页面后无法再次查看。如果不慎丢失，只能删除旧 Token，重新生成。务必在生成后立即妥善保存。

**Step 3.4: 将 Token 填入 .npmrc**

回到 `.npmrc` 文件，添加第二行配置：

```ini
# .npmrc -- 完整配置

# 第1行：声明仓库地址（去 GitHub 找包）
@texttramp:registry=https://npm.pkg.github.com

# 第2行：提供认证令牌（证明有权访问）
//npm.pkg.github.com/:_authToken=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 📖 详细解释：第二行配置的拆解

```
//npm.pkg.github.com/:_authToken=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  │                     │             │
  │                     │             └── 刚才生成并复制的 Personal Access Token
  │                     │
  │                     └── _authToken 指令：提供认证令牌
  │
  └── 仓库地址（双斜线开头是 npm 的协议格式）
```

#### 📊 两行配置的职责分工对比

| 行号 | 配置 | 作用 | 类比 |
|---|---|---|---|
| 第1行 | `@scope:registry=URL` | **地址声明**：告诉 npm 去哪找包 | 地图 |
| 第2行 | `//URL/:_authToken=TOKEN` | **身份认证**：证明有权限下载 | 钥匙 |

> 💡 **核心洞见**：第一行解决"去哪找"，第二行解决"凭什么看"。两者缺一不可--有地图没钥匙进不去，有钥匙没地图找不到。这两行配置共同完成了 GitHub Package 使用的完整前置条件。

---

### 8.5 Step 4：npm install 验证

#### 🎯 目标

执行 `npm install`，验证 GitHub Package 的包能否被成功下载到本地。

#### 💻 操作步骤

在项目根目录下执行：

```bash
# 安装项目所有依赖（包括 GitHub Package 的包）
npm install
```

#### ✅ 预期结果

安装成功后，项目目录结构如下：

```
my-consumer-project/
├── node_modules/                 # ← 新生成
│   └── @texttramp/
│       └── package-example/      # ← 从 GitHub Package 下载的包！
├── package.json
├── package-lock.json
└── .npmrc
```

在 `node_modules/@texttramp/package-example/` 目录下，可以看到从 GitHub Package 下载下来的完整包内容。至此，你就可以像使用任何普通 npm 包一样 `require()` 或 `import` 它了。

> 💡 **核心洞见**："发布--使用"闭环完成！M06 初始化了项目，M07 把包发布到 GitHub Package，M08 在另一个项目中使用它。一旦 `.npmrc` 配置好，后续的开发体验和普通 npm 包完全一致。

---

### 8.6 🐛 排错指南

本实操中最常见的三个坑：

#### 🐛 排错实录一：401 Unauthorized

**🚨 报错信息**

```
npm ERR! code E401
npm ERR! 401 Unauthorized - GET https://npm.pkg.github.com/@texttramp/package-example
```

**🔍 原因分析**

Token 未配置、已过期或权限不足。GitHub Package 即使是公开包也需要认证才能下载。

**✅ 修复方法**

1. 检查 `.npmrc` 中 Token 是否正确粘贴
2. 检查 Token 是否已过期（GitHub → Settings → Developer settings 中查看）
3. 确认 Token 最少勾选了 `read:packages` 权限

#### 🐛 排错实录二：404 Not Found

**🚨 报错信息**

```
npm ERR! code E404
npm ERR! 404 Not Found - GET https://npm.pkg.github.com/@wrong-scope/package-example
```

**🔍 原因分析**

scope 和包发布者的 GitHub 用户名不匹配，或者包名写错了。

**✅ 修复方法**

1. 确认 `.npmrc` 中 `@scope` 与包发布者的 GitHub 用户名**完全一致**（大小写敏感）
2. 确认 `package.json` 中 `dependencies` 的包名拼写正确
3. 确认目标包确实已经发布到 GitHub Package

#### 🐛 排错实录三：配置未生效

**🚨 现象**

`.npmrc` 明明写好了配置，但 `npm install` 似乎没有使用它。

**🔍 原因分析**

`.npmrc` 文件不在正确的位置。npm 只读取项目根目录下的 `.npmrc` 文件。

**✅ 修复方法**

1. 确认 `.npmrc` 和 `package.json` 在同一目录下
2. 使用 `ls -la` 确认文件名正确（以点开头，没有额外后缀）

---

### 8.7 两步配置总结

老师将整个使用流程精炼为两步，以下以表格形式突出呈现：

| 步骤 | 操作 | 涉及文件 | 具体内容 | 解决的问题 |
|---|---|---|---|---|
| **Step 1** | 添加依赖声明 | `package.json` → `dependencies` | `"@scope/package-name": "version"` | 告诉 npm"我要用哪个包" |
| **Step 2** | 配置仓库与认证 | `.npmrc`（两行） | ① `@scope:registry=URL`<br>② `//URL/:_authToken=TOKEN` | 告诉 npm"去哪找 + 我有权限" |

#### 🔄 完整流程示意图

```
┌──────────────────────────────────────────────────────────────────┐
│                    两步配置完整流程                                │
└──────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────┐
  │  Step 1: dependencies 声明          │
  │                                     │
  │  package.json:                      │
  │  {                                  │
  │    "dependencies": {                │
  │      "@texttramp/                   │
  │       package-example": "1.0.0"     │  ← "我要用这个包"
  │    }                                │
  │  }                                  │
  └────────────────┬────────────────────┘
                   │
                   ▼
  ┌─────────────────────────────────────┐
  │  Step 2: .npmrc 配置（两行）         │
  │                                     │
  │  # 第1行：地址声明                   │
  │  @texttramp:registry=               │
  │    https://npm.pkg.github.com       │  ← "去哪找这个包"
  │                                     │
  │  # 第2行：身份认证                   │
  │  //npm.pkg.github.com/:_authToken=  │
  │    ghp_xxxxxxxxxxxxxxxxxxxx         │  ← "我有权限访问"
  └────────────────┬────────────────────┘
                   │
                   ▼
          ┌───────────────────┐
          │   npm install     │  ← 一步安装
          │                   │
          │ ✓ package.json    │
          │ ✓ .npmrc          │
          │ → node_modules/   │
          └───────────────────┘
```

> 💡 **核心洞见**：这两步是一次性的项目配置。每个需要使用 GitHub Package 包的项目只需走一遍这个流程。配置完成后，后续的 `npm install`、`require()`、`import` 体验和普通 npm 包没有任何区别。

---

## 📋 全课程回顾总结

### 🗺️ 课程知识图谱

```
                      ┌───────────────────────────────┐
                      │   GitHub 进阶实战课程总览       │
                      └───────────────┬───────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                                               │
              ▼                                               ▼
  ┌───────────────────────┐                   ┌───────────────────────┐
  │   第一部分：Docker     │                   │  第二部分：             │
  │   容器镜像获取方案      │                   │  GitHub Package       │
  └───────────┬───────────┘                   └───────────┬───────────┘
              │                                           │
  ┌───────┼───────┼───────┼───────┐         ┌───────┼───────┐
  ▼       ▼       ▼       ▼       ▼         ▼       ▼       ▼
┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐  ┌──────┐┌──────┐┌──────┐
│安装  ││阿里云││镜像站││CF    ││搜索  │  │概述  ││发布  ││使用  │
│Docker││转存  ││离线  ││Worker││与管理│  │与初  ││包    ││包    │
│M01-02││M03   ││M04   ││M04   ││M05   │  │M06   ││M07   ││M08   │
└──────┘└──────┘└──────┘└──────┘└──────┘  └──────┘└──────┘└──────┘
```

### 📋 第一部分：Docker 镜像获取方案回顾

| 模块 | 主题 | 核心收获 |
|---|---|---|
| M01 | Docker 在 Linux 上的安装 | 掌握 Docker 核心概念及 Linux 环境下的安装配置 |
| M02 | Docker 在 Windows/Mac 上的安装 | 掌握跨平台的 Docker Desktop 安装与配置 |
| M03 | 方案一：阿里云私有仓库镜像转存 | 利用国内云厂商容器镜像服务解决镜像拉取问题 |
| M04 | 方案二至五：镜像站离线下载 / 一键脚本 / Cloudflare Worker | 掌握多种镜像获取方案，灵活应对不同网络环境 |
| M05 | Docker 镜像搜索与第一部分收尾 | 学会搜索和管理 Docker 镜像，第一部分知识体系收尾 |

> 💡 **Part 1 核心价值**：Docker 镜像是容器化部署的基石。面对国内网络访问 Docker Hub 不稳定的问题，这一部分提供了**五种不同的解决方案**——从云服务商镜像加速到自建代理（Cloudflare Worker），覆盖了个人开发者和企业团队的各种场景。

### 📋 第二部分：GitHub Package 回顾

| 模块 | 主题 | 核心收获 |
|---|---|---|
| M06 | GitHub Package 概述与项目初始化 | 理解 GitHub Package 概念、支持的包管理器、免费额度；完成 npm 项目初始化（`npm init`） |
| M07 | 发布包到 GitHub Package | 通过 GitHub Action 自动化发布 npm 包；理解 Workflow 触发机制（`on: release`） |
| M08 | 使用 GitHub Package 的包与总结 | 掌握两步配置法（`dependencies` + `.npmrc`）；理解"发布--使用"闭环 |

> 💡 **Part 2 核心价值**：GitHub Package 将代码托管和包管理统一在 GitHub 平台内，省去了单独维护 npm 官方仓库账号和发布流程的麻烦。对于团队内部**私有包**的管理尤其方便——代码在 GitHub 上，包也在 GitHub 上，权限管理、版本管理全部统一。

### 📊 课程整体回顾

| 维度 | 内容 |
|---|---|
| **课程模块数** | 8 个 |
| **Docker 安装** | Linux + Windows + Mac 三平台覆盖 |
| **Docker 镜像方案** | 5 种方案（阿里云 / 镜像站 / 离线下载 / 一键脚本 / CF Worker） |
| **GitHub Package 实操** | 完整闭环：初始化 → 发布 → 使用 |
| **涉及工具链** | Docker CLI、Node.js / npm、GitHub Action、GitHub Package、Cloudflare Worker |
| **核心技能** | 容器化基础、镜像获取策略、包发布与消费、CI/CD 自动化 |

### 💡 课程一句话总结

> 本课程以**实战驱动**的方式解决了两个实际开发中的核心问题——在国内网络环境下高效获取 Docker 镜像，以及利用 GitHub Package 实现私有包的完整发布与消费闭环。从环境搭建到方案对比，从代码发布到项目消费，每一步都做到了可落地、可复用。

---

## 📝 课后练习

### 练习 1：两步配置实操

**题目**：创建一个新的 npm 项目，配置 `.npmrc` 和 `dependencies`，尝试 `npm install` 你在 M07 中发布的 GitHub Package 包（或任意一个公开的 GitHub Package 包）。

**验收标准**：
- [ ] `package.json` 中包含正确的 `dependencies` 声明
- [ ] `.npmrc` 中正确配置了 scope 注册和 Token 认证
- [ ] `npm install` 成功执行，`node_modules` 中出现目标包
- [ ] 能在项目中通过 `require()` 或 `import` 成功引入该包

### 练习 2：排错训练

**题目**：故意制造以下三种错误场景，观察报错信息并逐一修复：
1. 只配置 `dependencies`，不创建 `.npmrc`，执行 `npm install`
2. 创建 `.npmrc` 但 Token 填写错误，执行 `npm install`
3. `.npmrc` 中 scope 故意写错，执行 `npm install`

**验收标准**：
- [ ] 能识别 401（未授权）和 404（未找到）错误的区别
- [ ] 知道每种错误的原因和对应修复方法
- [ ] 修复后能成功完成 `npm install`

### 练习 3：权限最小化实践

**题目**：创建一个仅含 `read:packages` 权限的 Personal Access Token，用这个最小权限 Token 配置 `.npmrc`，验证能否正常下载包。然后尝试用同一个 Token 去发布包，观察权限不足的报错。

**验收标准**：
- [ ] 理解 `read:packages`（只读）和 `write:packages`（可写）的权限差异
- [ ] 能用最小权限 Token 完成包的消费（下载）
- [ ] 能将"最小权限原则"应用到实际项目配置中

---

> 📅 生成日期: 2026-07-18 | 🎯 级别: M 级 | ⏱️ 录音时长: ~18 分钟 | 📏 文档规模: 2,960+ 行
> 🤖 由 transcript-to-doc v4.2 生成

