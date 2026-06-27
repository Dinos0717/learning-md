# Session 模块——多用户会话管理实战

> 基于陈泽鹏老师视频课程整理编写 · 2026年6月25日

---

## 目录

- [一、本节概述与学习目标](#一本节概述与学习目标)
- [二、Session 模块要解决的两个核心问题](#二session-模块要解决的两个核心问题)
- [三、Session 模块的架构设计](#三session-模块的架构设计)
- [四、SessionData——每个窗口存什么](#四sessiondata每个窗口存什么)
- [五、SessionManager——会话管理器的完整实现](#五sessionmanager会话管理器的完整实现)
- [六、后台清理线程——自动化过期回收](#六后台清理线程自动化过期回收)
- [七、Session 与 Memory 的绑定关系](#七session-与-memory-的绑定关系)
- [八、完整请求流程——从 HTTP 请求到 Agent 回复](#八完整请求流程从-http-请求到-agent-回复)
- [九、有状态 vs 无状态 Agent](#九有状态-vs-无状态-agent)
- [十、测试 SessionManager](#十测试-sessionmanager)
- [十一、常见问题与排错指南](#十一常见问题与排错指南)
- [十二、课后练习](#十二课后练习)
- [十三、本节小结](#十三本节小结)

---

## 一、本节概述与学习目标

### 1.1 本节定位

> 这是「多 Agent 开发实战」系列的**第六课**。前面我们完成了 Core（配置管理）、Schema（数据格式）、Memory（单用户记忆）三个模块。现在进入**Session 模块**——解决多用户场景下的会话隔离和生命周期管理问题。这是从"单用户可用"走向"多用户可部署"的关键一步。

```
┌─────────────────────────────────────────┐
│           本系列课程体系                   │
├─────────────────────────────────────────┤
│                                         │
│  开篇：课程总览                           │
│  第1课：为什么学 + 范式转变                │
│  第2课：架构总览                          │
│  第3课：Core 模块精讲                     │
│  第4课：Schema 模块                      │
│  第5课：Memory 模块                      │
│  第6课（本节）：Session 模块  ← 你在这里    │
│  后续课程：各 Agent 完整实现 → Service 部署  │
│                                         │
│  Session 是"多用户"能力的基石              │
│                                         │
└─────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────────┐
│                    架构层级（从下往上）                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  入口层 (run_agent.py / run_service.py)                      │
│      ↑ 依赖                                                  │
│  Agent 层 (router / chat / meeting)                          │
│      ↑ 依赖  ← Agent 从 Session 中获取 Memory               │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Session 层（本课）  ← 会话隔离 + 生命周期管理      │       │
│  │  • session_manager.py：SessionManager 管理器      │       │
│  │  • session_data.py：每个窗口的数据结构             │       │
│  │                                                  │       │
│  │  依赖：Memory 层（每个 Session 绑定一个 Memory）   │       │
│  │  特点：独立后台线程做定期清理                       │       │
│  └──────────────────────────────────────────────────┘       │
│      ↑ 依赖                                                  │
│  Memory 层 (记忆存储与检索)                                   │
│      ↑ 依赖                                                  │
│  Schemas 层 → Core 层                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 前情回顾：Memory 模块留下的问题

上节课我们实现了 MemoryManager，让单个 Agent 能记住对话历史。但这引出了一个新问题：

```
上节课的场景（单用户，无隔离）：
┌────────────────────────────────────┐
│  只有一个 MemoryManager 实例        │
│  所有用户共享同一份记忆              │
│                                    │
│  用户A：我叫张三                     │
│  用户B：帮我订机票                   │
│                                    │
│  问题来了：                          │
│  用户A 问"我叫什么名字？"             │
│  → 记忆里混杂了用户B的对话            │
│  → 回答：混乱！                     │
└────────────────────────────────────┘
```

> **本课的核心使命**：让每个用户（每个对话窗口）拥有**独立隔离**的记忆空间，同时自动清理长期不活跃的会话，节约内存资源。

### 1.3 本课要掌握的目标

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  目标一：理解 Session 模块的两大核心职责                    │
│         ├── 职责1：会话隔离——每个窗口独立的记忆空间        │
│         └── 职责2：自动清理——定期回收不活跃会话的内存      │
│                                                         │
│  目标二：掌握 SessionData 的数据结构设计                   │
│         ├── session_id：唯一标识（UUID 生成或外部传入）    │
│         ├── memory：绑定的 MemoryManager 实例             │
│         ├── created_at / last_active：时间追踪           │
│         └── message_count：消息计数                      │
│                                                         │
│  目标三：掌握 SessionManager 的实现与线程管理              │
│         ├── 字典管理：{session_id: SessionData}         │
│         ├── create / get / get_or_create 三种获取方式    │
│         ├── update_activity：活跃时间更新                 │
│         └── 后台清理线程：定期扫描 + 过期回收              │
│                                                         │
│  目标四：理解完整请求流程中 Session 的角色                 │
│         ├── HTTP 请求 → Session 创建/获取 → Agent 处理   │
│         ├── 有状态 Agent vs 无状态 Agent 的区分           │
│         └── session_id 的来回传递机制                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 二、Session 模块要解决的两个核心问题

### 2.1 问题一：记忆混杂——不同用户的对话串台了

```
没有 Session 隔离时，所有用户共用一个 MemoryManager：

┌─────────────────────────────────────────────────────────┐
│              共享的 MemoryManager                        │
│                                                         │
│  User: [用户A] 我叫张三，帮我写一个Python脚本              │
│  AI: 好的张三，请问需要什么功能的脚本？                    │
│  User: [用户B] 今天北京天气怎么样？                        │
│  AI: 今天北京晴，25°C...                                 │
│  User: [用户C] 帮我整理会议纪要                            │
│  AI: 好的，请提供会议内容...                              │
│  User: [用户A] 你刚才不是说帮我写脚本吗？                  │
│  AI: ？？？（记忆里混杂了三个人的对话，完全混乱）           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

```
有 Session 隔离时，每个用户拥有独立的 MemoryManager：

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Session A    │  │ Session B    │  │ Session C    │
│ (用户A)      │  │ (用户B)      │  │ (用户C)      │
│              │  │              │  │              │
│ Memory A     │  │ Memory B     │  │ Memory C     │
│ ├── 张三     │  │ ├── 天气     │  │ ├── 会议纪要 │
│ ├── Python   │  │ ├── 北京     │  │ ├── 本周事项 │
│ └── 脚本     │  │ └── 25°C    │  │ └── 行动项   │
│              │  │              │  │              │
│ 互不干扰 ✅   │  │ 互不干扰 ✅   │  │ 互不干扰 ✅   │
└──────────────┘  └──────────────┘  └──────────────┘
```

### 2.2 问题二：内存泄漏——僵尸会话永不释放

即使解决了隔离问题，还有一个隐患：如果服务长期运行，成千上万个会话一直占用内存，很多甚至连用户都已经不再使用了。

```
时间线：服务运行了 30 天...

Day 1: 用户A 问了 3 句话就走了 → 会话占用内存 ✗ 再也没回来
Day 2: 用户B 聊了 10 分钟 → 会话占用内存 ✗ 再也没回来
Day 3: 用户C 测试了一下 → 会话占用内存 ✗ 再也没回来
...
Day 30: 10000 个会话，9000 个已经 7 天没活跃了
        → 内存被大量僵尸会话占据！
        → 服务越来越慢，最终 OOM（Out of Memory）
```

> **解决方案**：后台线程定期巡检，把超过 N 小时不活跃的会话自动清理掉。

### 2.3 两个问题的解决方案：SessionManager

```
┌─────────────────────────────────────────────────────────┐
│           SessionManager 的两大能力                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  能力一：会话隔离                                         │
│  ├── 每个 session_id → 独立的 SessionData               │
│  ├── 每个 SessionData → 独立的 MemoryManager            │
│  └── 通过 session_id 查找和隔离                          │
│                                                         │
│  能力二：自动清理                                         │
│  ├── 后台线程定期运行（如每 60 分钟一次）                  │
│  ├── 检查每个会话的 last_active 时间                      │
│  ├── 超过过期阈值（如 24 小时）→ 清理                     │
│  └── 释放内存，防止内存泄漏                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 三、Session 模块的架构设计

### 3.1 总体架构

```
┌─────────────────────────────────────────────────────────┐
│                   SessionManager                         │
│                   (总会话管理器)                           │
│                                                         │
│  sessions: Dict[str, SessionData]  ← 字典管理所有会话     │
│                                                         │
│  方法：                                                  │
│  ├── create_session()       创建新会话                    │
│  ├── get_session()          根据 ID 获取会话              │
│  ├── get_or_create()        获取或创建（合并方法）         │
│  ├── update_activity()      更新活跃时间                  │
│  ├── cleanup()              清理过期会话                  │
│  ├── start_cleanup_thread() 启动后台清理线程              │
│  └── stop_cleanup_thread()  停止后台清理线程              │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  SessionData │  │  SessionData │  │  SessionData │  │
│  │  id: "abc"   │  │  id: "xyz"   │  │  id: "123"   │  │
│  │              │  │              │  │              │  │
│  │  ┌────────┐  │  │  ┌────────┐  │  │  ┌────────┐  │  │
│  │  │ Memory │  │  │  │ Memory │  │  │  │ Memory │  │  │
│  │  │Manager │  │  │  │Manager │  │  │  │Manager │  │  │
│  │  └────────┘  │  │  └────────┘  │  │  └────────┘  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  后台清理线程 (Cleanup Thread)                     │    │
│  │  每 60 分钟：遍历所有 Session                      │    │
│  │  → 超过 24 小时不活跃 → 删除                       │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3.2 核心数据结构关系

```
SessionManager
    │
    ├── timeout_hours: int          (过期时间，如 24 小时)
    ├── cleanup_interval_minutes: int (清理间隔，如 60 分钟)
    ├── sessions: dict              {session_id → SessionData}
    └── _cleanup_thread: Thread     (后台清理线程)
            │
            ▼
        SessionData (每个会话窗口的数据)
            │
            ├── session_id: str            (唯一标识)
            ├── memory: MemoryManager      (独立记忆)
            ├── created_at: datetime       (创建时间)
            ├── last_active: datetime      (最后活跃时间)
            └── message_count: int         (消息计数)
```

---

## 四、SessionData——每个窗口存什么

### 4.1 为什么需要 SessionData

> 一个会话窗口不是只有 `session_id` 就够了。我们还需要知道：它的记忆是什么？什么时候创建的？最近有没有人用？聊了多少条消息？这些信息需要一个统一的数据结构来承载。

### 4.2 SessionData 完整定义

```python
# ── src/session/session_data.py ──

from datetime import datetime
from typing import Optional
from src.memory.memory_manager import MemoryManager


class SessionData:
    """
    单个会话窗口的数据结构
    
    每个 SessionData 代表一个独立的对话窗口，
    包含该窗口的唯一标识、记忆实例、时间信息和消息计数。
    
    SessionData 和 MemoryManager 是 1:1 绑定的：
    一个会话窗口 = 一份独立的记忆
    """
    
    def __init__(
        self,
        session_id: str,
        max_token_limit: int = 2000
    ):
        """
        初始化会话窗口数据
        
        Args:
            session_id: 会话的唯一标识符
            max_token_limit: 传给 MemoryManager 的 Token 上限
        """
        # ═══ 唯一标识 ═══
        # 这是区分不同会话的核心字段
        # 可以手动指定（如客户端传入），也可以 UUID 自动生成
        self.session_id: str = session_id
        
        # ═══ 独立记忆 ═══
        # 每个 SessionData 实例化时，创建一个全新的 MemoryManager
        # 这就是"隔离"的物理实现：
        #   不同的 SessionData → 不同的 MemoryManager → 不共享任何记忆
        self.memory: MemoryManager = MemoryManager(
            max_token_limit=max_token_limit
        )
        
        # ═══ 时间追踪 ═══
        # 创建时间：会话窗口是何时建立的
        self.created_at: datetime = datetime.now()
        
        # 最后活跃时间：最近一次有用户交互是什么时候
        # 初始值 = 创建时间（刚创建时肯定也是活跃的）
        # 这个值会被 update_activity() 反复更新
        self.last_active: datetime = datetime.now()
        
        # ═══ 消息计数 ═══
        # 这个会话窗口内一共进行了多少轮对话
        self.message_count: int = 0
    
    def update_activity(self) -> None:
        """
        更新会话的活跃状态
        
        调用时机：每次这个会话窗口收到新的用户请求时
        
        做了什么：
        1. 把 last_active 更新为当前时间
        2. 消息计数 +1
        
        为什么重要：
        后台清理线程就是靠 last_active 来判断
        "这个会话多久没人用了，是否该清理"
        """
        self.last_active = datetime.now()
        self.message_count += 1
    
    def is_expired(self, timeout_hours: int) -> bool:
        """
        判断当前会话是否已过期
        
        Args:
            timeout_hours: 过期阈值（小时），例如 24
        
        Returns:
            True:  超过 timeout_hours 小时没活跃了 → 该清理了
            False: 还在活跃期内 → 保留
        
        计算逻辑：
        (当前时间 - 最后活跃时间) 是否超过 timeout_hours
        """
        now = datetime.now()
        inactive_duration = now - self.last_active
        return inactive_duration.total_seconds() > timeout_hours * 3600
```

### 4.3 SessionData 字段一览

| 字段 | 类型 | 说明 | 更新时机 |
|---|---|---|---|
| `session_id` | `str` | 唯一标识，用于区分不同会话窗口 | 创建时设定，不再变更 |
| `memory` | `MemoryManager` | 独立的记忆管理器，1:1 绑定 | 创建时初始化，随对话持续更新 |
| `created_at` | `datetime` | 会话创建时间 | 创建时设定，不再变更 |
| `last_active` | `datetime` | 最后活跃时间 | 每次收到请求时更新 |
| `message_count` | `int` | 累计消息数 | 每次收到请求时 +1 |

### 4.4 SessionData 的生命周期

```
创建（create_session）
    │
    │  session_id = "abc-123"（用户指定或自动生成）
    │  memory = MemoryManager()（全新的空白记忆）
    │  created_at = 2026-06-25 21:00:00
    │  last_active = 2026-06-25 21:00:00
    │  message_count = 0
    │
    ▼
活跃期（不断有用户交互）
    │
    │  每次用户发消息 →
    │      update_activity()
    │      last_active = 2026-06-25 21:30:00  ← 更新
    │      message_count = 15                  ← 累加
    │
    ▼
不活跃期（用户走了，不再发消息）
    │
    │  last_active = 2026-06-25 21:30:00  ← 不再更新
    │  ... 时间流逝 ...
    │  2026-06-26 21:31:00 → is_expired(24h) = True
    │
    ▼
清理（后台线程发现过期）
    │
    │  cleanup() → 从 sessions 字典中删除
    │  内存被 Python GC 回收
    │
    ▼
💀 会话消亡
```

---

## 五、SessionManager——会话管理器的完整实现

### 5.1 设计思路

SessionManager 是整个 Session 模块的核心。它的设计遵循以下几个原则：

```
┌─────────────────────────────────────────────────────────┐
│          SessionManager 的设计原则                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1️⃣  字典管理：所有会话存在一个 dict 中                   │
│      key = session_id, value = SessionData               │
│      → O(1) 时间复杂度的查找                              │
│                                                         │
│  2️⃣  三种获取方式：                                      │
│      ├── create：确定要新建                                │
│      ├── get：确定已存在，直接取                            │
│      └── get_or_create：不确定，让系统自己判断              │
│                                                         │
│  3️⃣  活跃追踪：每次交互都更新 last_active                  │
│      → 为后台清理提供判断依据                               │
│                                                         │
│  4️⃣  独立线程：清理逻辑跑在后台                            │
│      → 不阻塞主业务流程                                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 5.2 SessionManager 完整代码

```python
# ── src/session/session_manager.py ──

import uuid
import threading
import time
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime

from src.session.session_data import SessionData
from src.memory.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


class SessionManager:
    """
    会话管理器
    
    两大核心职责：
    1. 会话隔离：通过 session_id 管理多个独立的对话窗口
    2. 自动清理：后台线程定期回收不活跃的会话，释放内存
    
    使用示例：
        >>> manager = SessionManager(timeout_hours=24, cleanup_interval_minutes=60)
        >>> sid, memory = manager.get_or_create()             # 创建新会话
        >>> sid, memory = manager.get_or_create(sid)          # 获取已有会话
        >>> manager.update_activity(sid)                      # 标记活跃
        >>> manager.get_session_count()                       # 查看会话数
    """
    
    def __init__(
        self,
        timeout_hours: int = 24,
        cleanup_interval_minutes: int = 60
    ):
        """
        初始化会话管理器
        
        Args:
            timeout_hours: 会话过期时间（小时）。
                          会话超过这个时间没有活跃，就会被清理。
                          默认 24 小时。
            cleanup_interval_minutes: 后台清理线程的巡检间隔（分钟）。
                          每隔这个时间，线程醒来检查一次是否有过期会话。
                          默认 60 分钟。
        """
        # ═══ 配置参数 ═══
        self.timeout_hours = timeout_hours
        self.cleanup_interval_minutes = cleanup_interval_minutes
        
        # ═══ 核心存储：字典管理所有会话 ═══
        # key = session_id (str)
        # value = SessionData
        # 使用字典而不是列表的原因：O(1) 查找效率
        self._sessions: Dict[str, SessionData] = {}
        
        # ═══ 线程安全锁 ═══
        # 因为后台清理线程和主线程都会访问 _sessions，
        # 需要用锁来保证线程安全
        self._lock = threading.Lock()
        
        # ═══ 后台清理线程 ═══
        # 初始为 None，调用 start_cleanup_thread() 时创建
        self._cleanup_thread: Optional[threading.Thread] = None
        self._thread_running = False  # 线程运行标志
        
        # ═══ 自动启动清理线程 ═══
        # 管理器一创建，后台清理线程就自动运行
        self.start_cleanup_thread()
    
    # ══════════════════════════════════════════════════════
    # 会话创建与获取
    # ══════════════════════════════════════════════════════
    
    def create_session(
        self,
        session_id: Optional[str] = None
    ) -> Tuple[str, MemoryManager]:
        """
        创建一个新的会话窗口
        
        这是"确定要新建"时使用的方法。
        如果 session_id 已经存在，不会覆盖，只会计数 +1（同一会话）。
        
        Args:
            session_id: 可选的会话 ID。如果提供，使用这个 ID；
                       如果不提供，自动生成一个 UUID。
        
        Returns:
            Tuple[str, MemoryManager]: 
                - session_id: 创建（或已存在）的会话 ID
                - MemoryManager: 该会话绑定的记忆管理器
        
        流程：
        1. 如果没有传 session_id → UUID 生成唯一 ID
        2. 如果这个 ID 已存在 → 直接返回已有的（不重复创建）
        3. 如果不存在 → 创建新的 SessionData 并存入字典
        """
        # Step 1: 确定 session_id
        if session_id is None:
            session_id = str(uuid.uuid4())  # 自动生成唯一 ID
            # 例如：session_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        
        with self._lock:
            # Step 2: 检查是否已存在（同一个 ID 不重复创建）
            if session_id in self._sessions:
                logger.debug(f"会话 {session_id} 已存在，直接返回")
                return session_id, self._sessions[session_id].memory
            
            # Step 3: 创建新的 SessionData
            session_data = SessionData(session_id=session_id)
            self._sessions[session_id] = session_data
            
            logger.info(f"✅ 创建新会话: {session_id}")
            return session_id, session_data.memory
    
    def get_session(
        self,
        session_id: str
    ) -> Optional[MemoryManager]:
        """
        根据 session_id 获取会话的记忆管理器
        
        这是"确定已存在，直接取"时使用的方法。
        
        Args:
            session_id: 会话 ID
        
        Returns:
            MemoryManager 或 None（如果 ID 不存在）
        """
        with self._lock:
            session_data = self._sessions.get(session_id)
            if session_data is None:
                logger.warning(f"⚠️ 会话 {session_id} 不存在")
                return None
            return session_data.memory
    
    def get_or_create(
        self,
        session_id: Optional[str] = None
    ) -> Tuple[str, MemoryManager]:
        """
        获取已有会话，如果不存在则创建新会话
        
        这是最常用的方法——"有没有？有就取，没有就建"。
        适用于 HTTP 请求入口：客户端可能传了 session_id，也可能没传。
        
        Args:
            session_id: 可选的会话 ID。如果为 None 或不存在于字典中，创建新会话
        
        Returns:
            Tuple[str, MemoryManager]: session_id 和对应的记忆管理器
        
        逻辑流程：
        1. session_id 为 None → 创建新会话（UUID 自动生成）
        2. session_id 有值但在字典中找不到 → 创建新会话（用这个 ID）
        3. session_id 有值且能找到 → 直接返回已有会话
        """
        # 情况1：完全没有传 session_id → 创建新的
        if session_id is None:
            return self.create_session()
        
        # 情况2/3：传了 session_id → 先查字典
        with self._lock:
            if session_id in self._sessions:
                # 情况3：存在 → 直接返回
                logger.debug(f"获取已有会话: {session_id}")
                return session_id, self._sessions[session_id].memory
            else:
                # 情况2：不存在 → 用这个 ID 创建新会话
                logger.info(f"会话 {session_id} 不存在，用此 ID 创建新会话")
                session_data = SessionData(session_id=session_id)
                self._sessions[session_id] = session_data
                return session_id, session_data.memory
    
    # ══════════════════════════════════════════════════════
    # 会话状态管理
    # ══════════════════════════════════════════════════════
    
    def update_activity(self, session_id: str) -> bool:
        """
        更新会话的活跃时间
        
        调用时机：每次该会话收到用户请求时
        
        这非常重要！如果不调用这个方法：
        - last_active 永远不会更新
        - 后台线程会认为这个会话"不活跃"
        - 即使你一直在用，也会被清理掉！
        
        Args:
            session_id: 要更新的会话 ID
        
        Returns:
            True: 更新成功
            False: 会话不存在
        """
        with self._lock:
            session_data = self._sessions.get(session_id)
            if session_data is None:
                logger.warning(f"无法更新活跃时间：会话 {session_id} 不存在")
                return False
            
            session_data.update_activity()
            logger.debug(f"更新会话活跃时间: {session_id}")
            return True
    
    def get_session_count(self) -> int:
        """
        获取当前管理的会话总数
        
        Returns:
            int: 活跃会话的数量
        """
        with self._lock:
            return len(self._sessions)
    
    # ══════════════════════════════════════════════════════
    # 会话清理
    # ══════════════════════════════════════════════════════
    
    def cleanup(self) -> int:
        """
        清理所有过期会话
        
        遍历所有会话，把超过 timeout_hours 小时不活跃的会话删除。
        
        Returns:
            int: 被清理的会话数量
        
        清理逻辑：
        for each session:
            if (now - session.last_active) > timeout_hours:
                删除！
        """
        with self._lock:
            expired_ids = []
            
            # Step 1: 找出所有过期会话的 ID
            for session_id, session_data in self._sessions.items():
                if session_data.is_expired(self.timeout_hours):
                    expired_ids.append(session_id)
            
            # Step 2: 删除过期会话
            for session_id in expired_ids:
                del self._sessions[session_id]
                logger.info(f"🗑️ 清理过期会话: {session_id}")
            
            if expired_ids:
                logger.info(
                    f"清理完成：删除了 {len(expired_ids)} 个过期会话，"
                    f"剩余 {len(self._sessions)} 个活跃会话"
                )
            
            return len(expired_ids)
```

### 5.3 三种获取方式对比

| 方法 | 使用场景 | session_id 不存在时 | session_id 已存在时 |
|---|---|---|---|
| `create_session()` | 确定要新建会话（如用户点击"新对话"按钮） | 创建新的 SessionData | 返回已有的（不重复创建） |
| `get_session()` | 确定会话已存在（如内部调用，已知有 ID） | 返回 `None` | 返回 MemoryManager |
| **`get_or_create()`** | **最常见的 HTTP 请求入口** | 自动创建新会话 | 直接返回已有会话 |

```
客户端请求进来了，你该怎么选？

客户端传了 session_id？
    ├── 是 → 用 get_or_create(session_id)
    │        ├── 这个 ID 之前创建过 → 恢复之前的记忆
    │        └── 这个 ID 是新的（或伪造的）→ 创建新会话
    │
    └── 否 → 用 get_or_create()
             └── 自动生成 UUID → 创建新会话
                 → 把 session_id 返回给客户端
                 → 客户端下次请求带上它
```

### 5.4 线程安全：为什么需要锁

> ⚠️ **关键设计**：`_sessions` 字典同时被**主线程**（处理 HTTP 请求）和**后台清理线程**（定期 cleanup）访问。如果不加锁，可能出现：
> - 主线程正在读某个 session，后台线程同时把它删了 → 数据竞争
> - 两个线程同时修改字典结构 → Python 抛出 RuntimeError

```python
# ── 锁的使用模式 ──

# 所有访问 _sessions 字典的操作都用 with self._lock 保护
with self._lock:
    # 读操作
    data = self._sessions.get(sid)
    
    # 写操作
    self._sessions[sid] = new_data
    
    # 删操作
    del self._sessions[sid]
```

---

## 六、后台清理线程——自动化过期回收

### 6.1 线程的设计思路

```
┌─────────────────────────────────────────────────────────┐
│          后台清理线程的工作模式                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  while 线程正在运行:                                      │
│      │                                                  │
│      ├── sleep(cleanup_interval_minutes * 60) 秒        │
│      │   例如：sleep(3600) → 睡 1 小时                   │
│      │                                                  │
│      ├── 醒来！检查所有会话                               │
│      │                                                  │
│      ├── 遍历 _sessions 字典                             │
│      │   for session_id, session_data in sessions:      │
│      │       if session_data.is_expired(timeout_hours):  │
│      │           标记为待删除                             │
│      │                                                  │
│      ├── 删除所有过期会话                                 │
│      │                                                  │
│      └── 回到循环开头，继续 sleep                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 6.2 线程管理完整代码

```python
    # ── 接前面 SessionManager 类的代码 ──
    
    # ══════════════════════════════════════════════════════
    # 后台清理线程管理
    # ══════════════════════════════════════════════════════
    
    def _cleanup_loop(self):
        """
        后台清理线程的主循环
        
        这个方法是运行在独立线程中的。
        它会一直循环，每隔 cleanup_interval_minutes 分钟醒来一次，
        执行 cleanup() 清理过期会话。
        
        注意：这个方法不应该被外部直接调用。
              它由 start_cleanup_thread() 启动。
        """
        logger.info(
            f"后台清理线程已启动 | "
            f"过期时间: {self.timeout_hours}h | "
            f"检查间隔: {self.cleanup_interval_minutes}min"
        )
        
        while self._thread_running:
            # Step 1: 休眠指定的时间间隔
            # 转换为秒：分钟 × 60
            time.sleep(self.cleanup_interval_minutes * 60)
            
            # Step 2: 醒来后检查线程是否还应该运行
            # （可能在 sleep 期间被外部停止了）
            if not self._thread_running:
                break
            
            # Step 3: 执行清理
            try:
                cleaned_count = self.cleanup()
                if cleaned_count > 0:
                    logger.info(
                        f"后台清理：本次清理 {cleaned_count} 个过期会话 | "
                        f"剩余活跃会话: {self.get_session_count()}"
                    )
                else:
                    logger.debug(
                        f"后台清理：无过期会话 | "
                        f"当前活跃会话: {self.get_session_count()}"
                    )
            except Exception as e:
                logger.error(f"后台清理线程出错: {e}", exc_info=True)
    
    def start_cleanup_thread(self) -> None:
        """
        启动后台清理线程
        
        特性：
        - 如果线程已经在运行，不会重复启动（幂等操作）
        - 线程设置为 daemon=True，主程序退出时自动结束
        - 在 SessionManager 初始化时自动调用
        
        daemon=True 的含义：
        当主程序退出时，daemon 线程会自动被终止。
        如果设为 False，主程序退出后线程可能还在跑，导致程序无法正常退出。
        """
        # 如果已经在运行，不重复启动
        if self._thread_running:
            logger.debug("后台清理线程已在运行，跳过启动")
            return
        
        # 创建线程
        self._thread_running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            name="session-cleanup-thread",
            daemon=True  # 主程序退出时自动结束
        )
        
        # 启动线程
        self._cleanup_thread.start()
        logger.info("🚀 后台清理线程已启动")
    
    def stop_cleanup_thread(self) -> None:
        """
        停止后台清理线程
        
        使用场景：
        - 服务正常关闭时
        - 测试环境中清理资源
        """
        if not self._thread_running:
            return
        
        logger.info("正在停止后台清理线程...")
        self._thread_running = False
        
        if self._cleanup_thread is not None:
            # 等待线程自然结束（最多等 5 秒）
            self._cleanup_thread.join(timeout=5)
        
        logger.info("后台清理线程已停止")
```

### 6.3 线程生命周期

```
SessionManager.__init__()
    │
    ├── self.start_cleanup_thread()   ← 自动启动！
    │
    ▼
┌──────────────────────┐
│  线程开始运行          │
│  _thread_running=True │
│                       │
│  while True:          │
│    sleep(60分钟)       │  ← 大部分时间在休眠
│    cleanup()           │  ← 醒来干活
│    sleep(60分钟)       │
│    cleanup()           │
│    ...                 │
└──────────────────────┘
    │
    │ 外部调用 stop_cleanup_thread()
    │ 或主程序退出（daemon=True 自动终止）
    ▼
线程结束
```

### 6.4 配置参数建议

| 参数 | 推荐值 | 说明 |
|---|---|---|
| `timeout_hours` | **24**（默认） | 1 天不活跃就清理。对于大多数应用足够 |
| `timeout_hours` | **168**（7天） | 想让用户回来后还能接着聊的场景 |
| `timeout_hours` | **1** | 测试环境，快速验证清理逻辑 |
| `cleanup_interval_minutes` | **60**（默认） | 1 小时检查一次，不频繁也不疏忽 |
| `cleanup_interval_minutes` | **30** | 会话量大、内存紧张时，更频繁检查 |
| `cleanup_interval_minutes` | **5** | 测试环境，快速看到清理效果 |

---

## 七、Session 与 Memory 的绑定关系

### 7.1 绑定的物理实现

Session 和 Memory 的绑定不是"逻辑关联"——它是**物理上的创建关系**。每当创建一个 SessionData，它就同步创建一个全新的 MemoryManager。

```python
class SessionData:
    def __init__(self, session_id: str):
        self.session_id = session_id
        # 这里！每个 SessionData 创建时，
        # 都会 new 一个全新的 MemoryManager
        self.memory = MemoryManager(max_token_limit=2000)
```

```
SessionManager
    │
    ├── SessionData(id="abc")
    │   └── MemoryManager()  ← 独立的记忆实例 A
    │       ├── User: 我叫张三
    │       └── AI: 你好张三
    │
    ├── SessionData(id="xyz")
    │   └── MemoryManager()  ← 独立的记忆实例 B
    │       ├── User: 天气怎么样
    │       └── AI: 今天晴天
    │
    └── SessionData(id="123")
        └── MemoryManager()  ← 独立的记忆实例 C
            ├── User: 帮我写代码
            └── AI: 好的，什么语言？
            
    三个 MemoryManager 完全独立，互不干扰！
```

### 7.2 从 Session 到 Memory 的数据流

```
HTTP 请求到达
    │
    ├── session_id = request.session_id  (可能为 None)
    │
    ▼
session_id, memory = session_manager.get_or_create(session_id)
    │
    ├── 如果是新会话：创建 SessionData → 创建 MemoryManager → 返回空记忆
    └── 如果是旧会话：找到 SessionData → 返回已有 MemoryManager（含历史）
    │
    ▼
把 memory 传给 Agent
    agent.invoke(user_input, memory=memory)
    │
    ├── Agent 从 memory.get_content() 获取历史对话
    ├── Agent 拼接 prompt 调用 LLM
    └── Agent 把本轮对话存入 memory
    │
    ▼
session_manager.update_activity(session_id)
    └── last_active 更新为当前时间
    │
    ▼
返回给客户端：{response, session_id}
```

### 7.3 使用示例

```python
# ── Session + Memory 的联合使用 ──

from src.session.session_manager import SessionManager
from src.core.llm_driver import get_llm

# 创建会话管理器
session_manager = SessionManager(timeout_hours=24)

# ── 用户A 的对话 ──
# 第一次请求：没有 session_id → 自动创建
sid_a, memory_a = session_manager.get_or_create()
print(f"用户A 的会话ID: {sid_a}")

# 存入对话
memory_a.add_user_message("我叫张三，喜欢Python")
memory_a.add_ai_message("你好张三！Python是很好的选择")

session_manager.update_activity(sid_a)  # 更新活跃时间

# 用户A 的第二次请求：带上 session_id
sid_a2, memory_a2 = session_manager.get_or_create(sid_a)
print(f"用户A 再次访问: {sid_a2}")  # 同一个 ID！

# 验证记忆还在
print(memory_a2.get_content())
# 输出：
# User: 我叫张三，喜欢Python
# AI: 你好张三！Python是很好的选择

# ── 用户B 的对话（完全独立） ──
sid_b, memory_b = session_manager.get_or_create()
print(f"用户B 的会话ID: {sid_b}")  # 不同的 ID！

# 用户B 看不到用户A 的记忆
print(memory_b.get_content())  # 空白！
# → 验证了隔离性 ✅
```

---

## 八、完整请求流程——从 HTTP 请求到 Agent 回复

### 8.1 端到端流程

```
┌─────────────────────────────────────────────────────────┐
│          一次完整的 HTTP 对话请求                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Step 1: 客户端发送请求                                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ POST /chat                                        │   │
│  │ Body: {                                          │   │
│  │   "message": "帮我写个Python脚本",                  │   │
│  │   "session_id": "abc-123"  // 可选                │   │
│  │ }                                                │   │
│  └──────────────────────────────────────────────────┘   │
│         │                                                │
│         ▼                                                │
│  Step 2: SessionManager 处理会话                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │ sid, memory = session_manager.get_or_create(      │   │
│  │     request.session_id                            │   │
│  │ )                                                │   │
│  │                                                  │   │
│  │ → session_id 不为 None 且在字典中存在              │   │
│  │   → 返回已有的 memory（含历史对话）                │   │
│  │ → session_id 为 None 或不存在                     │   │
│  │   → 创建新的 session + memory                     │   │
│  └──────────────────────────────────────────────────┘   │
│         │                                                │
│         ▼                                                │
│  Step 3: 路由 Agent 判断意图（无状态，不需要 memory）       │
│  ┌──────────────────────────────────────────────────┐   │
│  │ intent = router_agent.invoke(request.message)     │   │
│  │ → intent = "chat" → 分发给对话 Agent              │   │
│  └──────────────────────────────────────────────────┘   │
│         │                                                │
│         ▼                                                │
│  Step 4: 对话 Agent 处理（有状态，需要 memory）            │
│  ┌──────────────────────────────────────────────────┐   │
│  │ # 从 memory 取历史                                 │   │
│  │ history = memory.get_content()                    │   │
│  │                                                   │   │
│  │ # 拼接完整 prompt                                  │   │
│  │ prompt = f"历史：{history}\n当前：{user_input}"     │   │
│  │                                                   │   │
│  │ # 调用 LLM                                        │   │
│  │ response = llm.invoke(prompt)                     │   │
│  │                                                   │   │
│  │ # 存入记忆                                        │   │
│  │ memory.add_user_message(user_input)               │   │
│  │ memory.add_ai_message(response)                   │   │
│  └──────────────────────────────────────────────────┘   │
│         │                                                │
│         ▼                                                │
│  Step 5: 更新会话状态                                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │ session_manager.update_activity(sid)              │   │
│  │ → last_active 更新 → 避免被清理                    │   │
│  └──────────────────────────────────────────────────┘   │
│         │                                                │
│         ▼                                                │
│  Step 6: 返回给客户端                                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Response: {                                       │   │
│  │   "response": "好的，这是你的Python脚本...",        │   │
│  │   "session_id": "abc-123",  // 一定要返回！        │   │
│  │   "intent": "chat"                                │   │
│  │ }                                                │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 8.2 伪代码实现

```python
# ── 服务入口（伪代码，后续课程会完善）──

from src.session.session_manager import SessionManager
from src.schemas.chat_schema import ChatRequest, ChatResponse

# 全局会话管理器（服务启动时创建一次）
session_manager = SessionManager(timeout_hours=24, cleanup_interval_minutes=60)


def handle_chat_request(request: ChatRequest) -> ChatResponse:
    """
    处理一次对话请求
    
    这是 HTTP 服务的核心处理函数
    """
    
    # Step 1: 获取或创建会话
    session_id, memory = session_manager.get_or_create(
        request.session_id
    )
    
    # Step 2: 路由 Agent 判断意图（无状态，直接调用）
    intent = router_agent.invoke(request.message)
    
    # Step 3: 根据意图分发到对应的子 Agent
    if intent == "chat":
        # 对话 Agent —— 需要记忆
        response_text = chat_agent.invoke(
            user_input=request.message,
            memory=memory  # 传入记忆！
        )
    elif intent == "meeting_notes":
        # 会议纪要 Agent —— 不需要记忆（一次性的）
        response_text = meeting_agent.invoke(
            user_input=request.message
        )
    else:
        response_text = "抱歉，我无法理解你的意图。"
    
    # Step 4: 更新会话活跃状态
    session_manager.update_activity(session_id)
    
    # Step 5: 构建并返回响应
    return ChatResponse(
        response=response_text,
        session_id=session_id,  # ⚠️ 一定要返回 session_id！
        intent=intent
    )
```

### 8.3 为什么响应中必须返回 session_id

```
客户端第一次请求（没有 session_id）：
┌──────────────────────────────────────────────────────────┐
│  客户端 → 服务端                                          │
│  {"message": "你好", "session_id": null}                  │
│                                                          │
│  服务端处理：                                             │
│  session_id = UUID → "a1b2c3d4-..."                      │
│                                                          │
│  服务端 → 客户端                                          │
│  {"response": "你好！", "session_id": "a1b2c3d4-..."}     │
│  ← 客户端收到了 session_id！                              │
│                                                          │
│  客户端保存这个 session_id                                 │
└──────────────────────────────────────────────────────────┘

客户端第二次请求（带上 session_id）：
┌──────────────────────────────────────────────────────────┐
│  客户端 → 服务端                                          │
│  {"message": "刚才说到哪了？",                             │
│   "session_id": "a1b2c3d4-..."}                          │
│                                                          │
│  服务端处理：                                             │
│  找到 session_id="a1b2c3d4-..." → 取出之前的记忆          │
│  → Agent 知道上下文 → 正确回答                            │
│                                                          │
│  服务端 → 客户端                                          │
│  {"response": "我们刚才在聊...",                           │
│   "session_id": "a1b2c3d4-..."}                          │
└──────────────────────────────────────────────────────────┘

⚠️ 如果你不返回 session_id，客户端就丢了钥匙，
   下次请求无法找回之前的记忆！
```

---

## 九、有状态 vs 无状态 Agent

### 9.1 概念对比

在 Agent 系统中，不是所有 Agent 都需要记忆。根据是否需要上下文，分为两类：

```
┌─────────────────────────────────────────────────────────┐
│          有状态 Agent vs 无状态 Agent                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  有状态 Agent（Stateful）：需要记忆                        │
│  ├── 每次请求的结果依赖于之前的对话                        │
│  ├── 需要绑定 MemoryManager                              │
│  ├── 典型：对话 Agent（Chat Agent）                       │
│  └── 例子："我叫什么名字？" → 需要记住之前说过             │
│                                                         │
│  无状态 Agent（Stateless）：不需要记忆                     │
│  ├── 每次请求的处理完全独立                                │
│  ├── 不需要绑定 MemoryManager                              │
│  ├── 典型：路由 Agent、会议纪要 Agent                      │
│  └── 例子："这是什么意图？" → 只需要当前这句话             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 9.2 三种 Agent 的状态分析

| Agent 类型 | 有状态/无状态 | 是否需要 Memory | 是否需要 Session | 原因 |
|---|---|---|---|---|
| **路由 Agent** | 无状态 | ❌ | ❌ | 只根据当前输入做意图判断，不依赖历史 |
| **对话 Agent** | **有状态** | ✅ | ✅ | 多轮对话需要上下文，"你刚才说..." |
| **会议纪要 Agent** | 无状态（通常） | ❌ | ❌ | 一次性输入会议内容，提取结构化结果 |

> 💡 **会议纪要 Agent 的例外**：如果你的业务场景是"持续记录一场会议"（比如用户分段输入会议内容），那它也需要记忆。这取决于业务需求，不是技术限制。

### 9.3 在设计中的体现

```python
# ── 路由 Agent：无状态 ──
class RouterAgent:
    def invoke(self, user_input: str) -> Intent:
        # 不需要 memory！直接判断
        result = self.llm.with_structured_output(RouterResponse).invoke(user_input)
        return result.intent


# ── 对话 Agent：有状态 ──
class ChatAgent:
    def invoke(self, user_input: str, memory: MemoryManager) -> str:
        # 需要 memory！从记忆取历史
        history = memory.get_content()
        
        # 拼接 prompt
        full_prompt = f"历史：\n{history}\n\n当前：{user_input}"
        
        response = self.llm.invoke(full_prompt)
        
        # 存入记忆
        memory.add_user_message(user_input)
        memory.add_ai_message(response)
        
        return response


# ── 会议纪要 Agent：无状态（一次性输入） ──
class MeetingAgent:
    def invoke(self, user_input: str) -> MeetingSummary:
        # 不需要 memory！一次性提取
        result = self.llm.with_structured_output(MeetingSummary).invoke(user_input)
        return result
```

---

## 十、测试 SessionManager

### 10.1 完整测试代码

```python
# ── test_session_manager.py ──

import pytest
import time
from src.session.session_manager import SessionManager
from src.session.session_data import SessionData


class TestSessionManager:
    """SessionManager 的单元测试"""
    
    def test_create_session_without_id(self):
        """测试：不传 session_id 时自动生成 UUID"""
        manager = SessionManager(timeout_hours=24)
        
        # 不传 ID
        sid, memory = manager.create_session()
        
        # 验证
        assert sid is not None
        assert len(sid) > 0  # UUID 生成成功
        assert memory is not None
        assert manager.get_session_count() == 1
    
    def test_create_session_with_custom_id(self):
        """测试：传入自定义 session_id"""
        manager = SessionManager(timeout_hours=24)
        
        custom_id = "my-custom-session-001"
        sid, memory = manager.create_session(session_id=custom_id)
        
        # 验证
        assert sid == custom_id
        assert memory is not None
        assert manager.get_session_count() == 1
    
    def test_same_id_does_not_create_duplicate(self):
        """测试：同一个 session_id 不会重复创建"""
        manager = SessionManager(timeout_hours=24)
        
        # 第一次创建
        sid1, _ = manager.create_session(session_id="test-session")
        count1 = manager.get_session_count()
        
        # 第二次用同一个 ID 创建
        sid2, _ = manager.create_session(session_id="test-session")
        count2 = manager.get_session_count()
        
        # 验证：数量应该还是 1（没有重复创建）
        assert sid1 == sid2 == "test-session"
        assert count1 == count2 == 1
    
    def test_get_session_existing(self):
        """测试：获取已存在的会话"""
        manager = SessionManager(timeout_hours=24)
        
        # 先创建
        sid, _ = manager.create_session(session_id="existing-session")
        
        # 再获取
        memory = manager.get_session("existing-session")
        
        assert memory is not None
    
    def test_get_session_nonexistent(self):
        """测试：获取不存在的会话返回 None"""
        manager = SessionManager(timeout_hours=24)
        
        memory = manager.get_session("non-existent-id")
        
        assert memory is None
    
    def test_get_or_create_new(self):
        """测试：get_or_create 在不存在时创建新会话"""
        manager = SessionManager(timeout_hours=24)
        
        # 不传 session_id → 应该创建新的
        sid, memory = manager.get_or_create()
        
        assert sid is not None
        assert memory is not None
        assert manager.get_session_count() == 1
    
    def test_get_or_create_existing(self):
        """测试：get_or_create 在已存在时返回已有会话"""
        manager = SessionManager(timeout_hours=24)
        
        # 先创建一个
        sid1, mem1 = manager.create_session(session_id="my-session")
        mem1.add_user_message("测试消息")
        
        # 用同一个 ID 调用 get_or_create
        sid2, mem2 = manager.get_or_create(session_id="my-session")
        
        # 验证：应该是同一个会话
        assert sid1 == sid2 == "my-session"
        # 验证：记忆还在
        history = mem2.get_content()
        assert "测试消息" in history
        # 验证：没有创建重复的会话
        assert manager.get_session_count() == 1
    
    def test_get_or_create_with_new_id(self):
        """测试：get_or_create 传入不存在的 ID 时创建新会话"""
        manager = SessionManager(timeout_hours=24)
        
        sid, memory = manager.get_or_create(session_id="brand-new-id")
        
        assert sid == "brand-new-id"
        assert memory is not None
        assert manager.get_session_count() == 1
    
    def test_update_activity(self):
        """测试：更新活跃状态"""
        manager = SessionManager(timeout_hours=24)
        
        sid, _ = manager.create_session(session_id="active-session")
        
        # 更新活跃状态
        result = manager.update_activity(sid)
        
        assert result is True  # 更新成功
    
    def test_update_activity_nonexistent(self):
        """测试：更新不存在的会话返回 False"""
        manager = SessionManager(timeout_hours=24)
        
        result = manager.update_activity("ghost-session")
        
        assert result is False
    
    def test_cleanup_expired_sessions(self):
        """测试：清理过期会话"""
        # 设置极短的过期时间（0 小时 = 立即过期）
        # 注意：这里用 0 小时意味着创建出来就已经"过期"了
        manager = SessionManager(timeout_hours=0, cleanup_interval_minutes=60)
        
        # 创建几个会话（立即就"过期"了，因为 timeout_hours=0）
        manager.create_session(session_id="session-1")
        manager.create_session(session_id="session-2")
        manager.create_session(session_id="session-3")
        
        assert manager.get_session_count() == 3
        
        # 清理
        cleaned = manager.cleanup()
        
        assert cleaned == 3  # 3 个都过期了
        assert manager.get_session_count() == 0
    
    def test_cleanup_keeps_active_sessions(self):
        """测试：清理时保留活跃会话"""
        manager = SessionManager(timeout_hours=24)
        
        # 创建一个会话并立即更新活跃时间
        sid, _ = manager.create_session(session_id="active")
        manager.update_activity(sid)
        
        # 24 小时的过期时间，刚创建的会话不会过期
        cleaned = manager.cleanup()
        
        assert cleaned == 0  # 没有过期会话
        assert manager.get_session_count() == 1  # 仍然保留
    
    def test_multiple_sessions_independent_memory(self):
        """测试：多个会话的记忆完全独立"""
        manager = SessionManager(timeout_hours=24)
        
        # 创建两个独立会话
        sid_a, mem_a = manager.create_session(session_id="user-a")
        sid_b, mem_b = manager.create_session(session_id="user-b")
        
        # 分别存入不同的记忆
        mem_a.add_user_message("我是用户A")
        mem_b.add_user_message("我是用户B")
        
        # 验证记忆隔离
        content_a = mem_a.get_content()
        content_b = mem_b.get_content()
        
        assert "用户A" in content_a
        assert "用户B" not in content_a
        assert "用户B" in content_b
        assert "用户A" not in content_b
```

### 10.2 测试要点总结

```
┌─────────────────────────────────────────────────────────┐
│           SessionManager 测试的核心关注点                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1️⃣  会话创建 —— 自动生成 UUID / 自定义 ID               │
│                                                         │
│  2️⃣  重复创建 —— 同一 ID 不产生重复会话                   │
│                                                         │
│  3️⃣  会话获取 —— 存在的能获取，不存在的返回 None          │
│                                                         │
│  4️⃣  get_or_create —— 智能判断创建还是获取                │
│                                                         │
│  5️⃣  活跃更新 —— 存在时更新成功，不存在时返回 False       │
│                                                         │
│  6️⃣  过期清理 —— 过期会话被删除，活跃会话被保留           │
│                                                         │
│  7️⃣  记忆隔离 —— 不同会话的记忆完全独立                   │
│                                                         │
│  8️⃣  线程安全 —— 并发访问时数据一致性                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 十一、常见问题与排错指南

### 11.1 错误速查表

| 错误现象 | 原因 | 解决方法 | 优先级 |
|---|---|---|---|
| **不同用户的对话串台了** | 多个用户共用了同一个 session_id | 确保每个用户/窗口分配独立的 session_id；检查前端是否正确保存和传递 session_id | 🔴 高 |
| **服务重启后所有会话丢失** | 正常——当前方案是内存存储 | 这不是 bug。需要持久化请升级为 Redis/数据库方案 | 🟡 中 |
| **正在聊天的会话被清理了** | 没有调用 `update_activity()` | 检查每次请求是否调用了 `session_manager.update_activity(sid)` | 🔴 高 |
| **后台线程不工作** | 线程可能崩溃了 | 检查日志中是否有线程异常；确认 `start_cleanup_thread()` 被调用 | 🟡 中 |
| **内存持续增长** | timeout_hours 太大或清理间隔太长 | 调小 `timeout_hours`（如 12h）；调小 `cleanup_interval_minutes`（如 30min） | 🟡 中 |
| **同个 ID 创建了多个会话** | `create_session` 被重复调用且 ID 不同 | 检查业务逻辑是否正确使用了 `get_or_create` 而非 `create_session` | 🟢 低 |
| **get_session 返回 None，但会话明明存在** | session_id 大小写、空格不一致 | 确保 session_id 在存储和查询时完全一致 | 🟢 低 |

### 11.2 排查流程

```
用户反馈"不记得之前的对话了"
    │
    ├── Step 1: 检查 session_id 是否正确传递
    │   客户端第一次请求拿到了 session_id 吗？
    │   客户端第二次请求带上了同样的 session_id 吗？
    │   ├── 没带 → 前端问题：没有保存/回传 session_id
    │   └── 带了 → 进入 Step 2
    │
    ├── Step 2: 检查会话是否被意外清理
    │   session_manager.get_session(sid) 返回 None？
    │   ├── 是 → 会话被清理了
    │   │   ├── timeout_hours 太小？→ 调大
    │   │   └── 没有 update_activity？→ 检查代码
    │   └── 否 → 进入 Step 3
    │
    ├── Step 3: 检查 memory 是否正确使用
    │   memory.get_content() 返回空？
    │   ├── 是 → add_user_message/add_ai_message 被调用了吗？
    │   └── 否 → 进入 Step 4
    │
    └── Step 4: 检查 prompt 拼接
        发给 LLM 的 prompt 包含了 history 吗？
        ├── 没有 → 拼接逻辑有问题
        └── 有 → LLM 本身的问题（模型能力、prompt 设计等）
```

### 11.3 关键注意点

> ⚠️ **注意点 1**：`update_activity()` 非常重要！如果忘了调用，即使用户一直在聊天，后台线程也会认为这个会话不活跃，从而把它清理掉。

> ⚠️ **注意点 2**：`create_session` 对同一个 ID 不会重复创建（做了去重检查），但最好在业务逻辑中直接用 `get_or_create`，避免心智负担。

> ⚠️ **注意点 3**：`daemon=True` 的线程在主程序退出时会自动终止。如果你需要保证清理线程优雅退出（如写完日志再退出），可以在服务关闭时调用 `stop_cleanup_thread()`。

---

## 十二、课后练习

### 练习一：基础——SessionManager 基础操作

**题目**：创建一个 SessionManager 实例，完成基本的会话创建、获取、计数操作。

**要求**：
- 创建 SessionManager，过期时间设为 48 小时
- 创建 3 个不同的会话（自定义 ID）
- 验证 `get_session_count()` 返回 3
- 用 `get_session` 获取其中一个，验证不为 None
- 用 `get_session` 获取一个不存在的 ID，验证返回 None

<details>
<summary>参考答案（点击展开）</summary>

```python
from src.session.session_manager import SessionManager

# 创建管理器
manager = SessionManager(timeout_hours=48)

# 创建 3 个会话
ids = []
for i in range(3):
    sid, mem = manager.create_session(session_id=f"user-{i}")
    ids.append(sid)

# 验证
assert manager.get_session_count() == 3, "应该有 3 个会话"
assert manager.get_session("user-0") is not None, "user-0 应该存在"
assert manager.get_session("ghost") is None, "ghost 不应该存在"

print("✅ 所有验证通过！")
```
</details>

### 练习二：进阶——验证记忆隔离

**题目**：创建两个独立会话，分别存入不同的对话，验证它们的记忆完全隔离。

**要求**：
- 创建 session "alice" 和 "bob"
- 分别添加不同的对话内容
- 验证 alice 的记忆中不包含 bob 的内容
- 验证 bob 的记忆中不包含 alice 的内容
- 验证调用 `get_or_create("alice")` 能恢复 alice 的记忆

<details>
<summary>参考答案（点击展开）</summary>

```python
from src.session.session_manager import SessionManager

manager = SessionManager(timeout_hours=24)

# ── Alice 的对话 ──
sid_a, mem_a = manager.create_session(session_id="alice")
mem_a.add_user_message("我是Alice，我需要帮助写一个登录页面")
mem_a.add_ai_message("好的Alice，我来帮你写登录页面。需要React还是Vue？")
mem_a.add_user_message("用React吧")
mem_a.add_ai_message("好的，这是React登录组件的代码...")

# ── Bob 的对话 ──
sid_b, mem_b = manager.create_session(session_id="bob")
mem_b.add_user_message("我是Bob，能帮我分析一下这个数据集吗？")
mem_b.add_ai_message("当然Bob，请把数据发给我")
mem_b.add_user_message("数据是一组用户的购买记录")
mem_b.add_ai_message("好的，我来分析购买记录的规律...")

# ── 验证隔离 ──
content_a = mem_a.get_content()
content_b = mem_b.get_content()

assert "Alice" in content_a
assert "登录" in content_a
assert "React" in content_a
assert "Bob" not in content_a
assert "数据集" not in content_a

assert "Bob" in content_b
assert "数据集" in content_b
assert "购买记录" in content_b
assert "Alice" not in content_b
assert "登录" not in content_b

# ── 验证 get_or_create 恢复记忆 ──
sid_a2, mem_a2 = manager.get_or_create(session_id="alice")
assert sid_a2 == "alice"
assert "Alice" in mem_a2.get_content()
assert "登录" in mem_a2.get_content()

print("✅ 记忆隔离验证通过！")
```
</details>

### 练习三：综合实战——模拟完整请求流程

**题目**：写一个模拟函数，展示从 HTTP 请求到 Agent 回复的完整流程（不真调 LLM，用 mock）。

**要求**：
- 模拟 3 次请求：第一次无 session_id，第二次和第三次带 session_id
- 每次请求后验证记忆是否正确累积
- 模拟 `update_activity` 的调用
- 最后检查会话数量（应该只有 1 个，因为 3 次请求用的是同一个会话）

<details>
<summary>参考答案（点击展开）</summary>

```python
from src.session.session_manager import SessionManager


# 模拟函数
def simulate_request(manager, session_id, message):
    """模拟一次 HTTP 请求"""
    # Step 1: 获取或创建会话
    sid, memory = manager.get_or_create(session_id)
    
    # Step 2: 模拟 Agent 处理（这里用简单的逻辑代替）
    history = memory.get_content()
    # 模拟回复（实际应该是 LLM 生成）
    fake_response = f"[回复] 已收到你的消息: '{message}'，历史对话数: {len(memory.get_history())}"
    
    # Step 3: 存入记忆
    memory.add_user_message(message)
    memory.add_ai_message(fake_response)
    
    # Step 4: 更新活跃时间
    manager.update_activity(sid)
    
    return sid, fake_response


# ── 测试 ──
manager = SessionManager(timeout_hours=24)

# 第一次请求：无 session_id
sid1, resp1 = simulate_request(manager, None, "你好，我叫测试员")
print(f"第1次请求 → session_id: {sid1[:8]}..., 回复: {resp1}")
assert manager.get_session_count() == 1

# 第二次请求：带上 session_id
sid2, resp2 = simulate_request(manager, sid1, "我刚才说我叫什么？")
print(f"第2次请求 → session_id: {sid2[:8]}..., 回复: {resp2}")
assert sid2 == sid1  # 同一个会话

# 第三次请求：带上 session_id
sid3, resp3 = simulate_request(manager, sid1, "帮我写一个函数")
print(f"第3次请求 → session_id: {sid3[:8]}..., 回复: {resp3}")
assert sid3 == sid1  # 还是同一个会话

# 验证
assert manager.get_session_count() == 1  # 只有 1 个会话（3 次请求共用）
_, memory = manager.get_or_create(sid1)
history = memory.get_history()
assert len(history) == 6  # 3 轮 × 2 条 = 6 条消息

print(f"\n✅ 完整流程验证通过！")
print(f"会话总数: {manager.get_session_count()}")
print(f"记忆条数: {len(history)}")
print(f"记忆内容:\n{memory.get_content()}")
```
</details>

---

## 十三、本节小结

### 13.1 核心知识图谱

```
┌────────────────────────────────────────────────────────────┐
│              Session 模块核心知识体系                         │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1️⃣  Session 的两大职责                                      │
│      ├── 会话隔离：每个 session_id → 独立的 MemoryManager    │
│      └── 自动清理：后台线程定期回收不活跃会话的内存           │
│                                                            │
│  2️⃣  SessionData 数据结构                                    │
│      ├── session_id：唯一标识（UUID 或自定义）               │
│      ├── memory：1:1 绑定的 MemoryManager                   │
│      ├── created_at / last_active：时间追踪                 │
│      └── message_count：消息计数                            │
│                                                            │
│  3️⃣  SessionManager 核心方法                                 │
│      ├── create_session()：创建新会话                        │
│      ├── get_session()：获取已有会话                         │
│      ├── get_or_create()：智能创建/获取（最常用）            │
│      ├── update_activity()：更新活跃时间                     │
│      └── cleanup()：清理过期会话                             │
│                                                            │
│  4️⃣  后台清理线程                                            │
│      ├── daemon 线程，主程序退出时自动终止                    │
│      ├── 定时休眠（cleanup_interval_minutes）→ 醒来清理      │
│      └── 判断依据：is_expired(timeout_hours)                │
│                                                            │
│  5️⃣  有状态 vs 无状态 Agent                                  │
│      ├── 路由 Agent：无状态，不需要记忆                       │
│      ├── 对话 Agent：有状态，必须绑定 Memory                 │
│      └── 会议纪要 Agent：视业务场景而定                      │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 13.2 模块依赖全景图

```
┌─────────────────────────────────────────────────────────┐
│              当前已完成的模块依赖关系                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│                       入口层（待实现）                     │
│                           ↑                              │
│                    Agent 层（待实现）                      │
│                     ↑          ↑                         │
│              ┌──────┘          └──────┐                  │
│              │                        │                  │
│         Session 层                Schema 层              │
│         (本课) ✅                 (第4课) ✅              │
│              │                        │                  │
│              ↓                        ↓                  │
│         Memory 层                 Core 层                │
│         (第5课) ✅                (第3课) ✅              │
│              │                        │                  │
│              └────────┬───────────────┘                  │
│                       ↓                                  │
│                   Core 层                                 │
│                   (第3课) ✅                               │
│                                                         │
│  已完成的模块：Core → Schema → Memory → Session           │
│  待实现的模块：Agent（路由/对话/会议）→ Service 入口       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 13.3 一句话总结

> **Session 模块的本质是：用一个字典把不同用户的对话窗口隔离开，每个窗口绑定独立的记忆，再用一个后台线程定期清理"僵尸会话"，从而让 Agent 系统能够安全地服务多个用户而不会记忆串台或内存泄漏。**

### 13.4 系列课程定位

```
┌─────────────────────────────────────────────────────────┐
│              多 Agent 开发实战 · 系列课程                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  开篇：课程总览                                           │
│  第1课：为什么现在必须学 Agent 开发                         │
│  第2课：多 Agent 项目架构总览                              │
│  第3课：Core 模块精讲——配置管理 + 大模型驱动                │
│  第4课：Schema 模块——数据结构决定 Agent 规范               │
│  第5课：Memory 模块——让 Agent 真正记住上下文                │
│  第6课（本课）：Session 模块——多用户会话管理实战             │
│        ← 你在这里                                         │
│  后续课程：各 Agent 完整实现 → Service 入口 → 部署上线       │
│                                                         │
│  本课是基础架构的最后一环！                                  │
│  学完本课后，你已经掌握了：                                  │
│  ✅ Core：配置管理和 LLM 驱动                              │
│  ✅ Schema：结构化数据格式定义                              │
│  ✅ Memory：对话记忆的存储与检索                            │
│  ✅ Session：多用户会话的隔离与生命周期管理                  │
│                                                         │
│  地基已经搭好，下节课开始搭建 Agent 层！                     │
│  → 路由 Agent 怎么和 Session 联动？                        │
│  → 对话 Agent 怎么使用 Memory？                            │
│  → 会议纪要 Agent 的完整实现？                              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

*本教学文档基于陈泽鹏老师视频课程整理编写 · 2026年6月25日*
