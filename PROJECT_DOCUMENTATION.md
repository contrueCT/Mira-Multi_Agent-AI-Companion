# 小梦（Mira）- 智能情感陪伴系统 项目技术文档

## 项目概述

小梦（Mira）是一个现代化的AI情感陪伴系统，基于Microsoft AutoGen v0.4和ChromaDB构建。该项目通过多代理协作、长期记忆管理、智能视觉效果和跨平台桌面应用，提供了一个完整的AI情感陪伴解决方案。

### 技术栈
- **后端框架**: AutoGen v0.4 (多代理协作)
- **记忆存储**: ChromaDB (向量数据库)
- **前端界面**: HTML5/CSS3/JavaScript + Electron
- **API服务**: FastAPI + WebSocket
- **依赖管理**: Python 3.10+ / Node.js 16+

## 第一部分：项目整体架构与核心模块

### 1. 项目目录结构

```
emotional-companion/
├── emotional_companion/           # 核心Python包
│   ├── agents/                   # 多代理系统
│   │   ├── agent_system.py       # 主代理系统管理器
│   │   └── conversation_handler.py # 对话处理器
│   ├── memory/                   # 记忆管理模块
│   │   └── emotional_memory.py   # 情感记忆系统
│   ├── effects/                  # 视觉效果控制
│   │   └── visual_effects_controller.py # 视觉效果控制器
│   ├── utils/                    # 工具模块
│   │   ├── conversation_logger.py # 对话日志记录
│   │   ├── memory_viewer.py      # 记忆查看器
│   │   ├── time_utils.py         # 时间工具
│   │   └── disable_telemetry.py  # 禁用遥测
│   └── cli.py                    # 命令行接口
├── web_api/                      # Web API服务
│   ├── web_api.py               # FastAPI主应用
│   ├── websocket_handler.py     # WebSocket处理器
│   ├── config_manager.py        # 配置管理器
│   └── models.py                # 数据模型
├── mira-desktop/                 # Electron桌面客户端
│   ├── main.js                  # Electron主进程
│   ├── preload.js               # 预加载脚本
│   ├── web/                     # 前端资源
│   └── package.json             # Node.js依赖配置
├── web/                         # Web界面资源
│   ├── index.html               # 主界面
│   ├── css/                     # 样式文件
│   └── js/                      # JavaScript脚本
├── configs/                     # 配置文件
│   ├── OAI_CONFIG_LIST.json     # AI模型配置
│   └── user_config.json         # 用户配置
├── memory_db/                   # ChromaDB数据库目录
├── logs/                        # 系统日志
└── scripts/                     # 工具脚本
```

### 2. 核心模块功能说明

#### 2.1 多代理系统 (`emotional_companion/agents/`)

**agent_system.py** - 核心代理管理器
- **功能**: 管理多个专业AI代理的协作，包括情感分析、记忆管理、对话生成和思考代理
- **核心组件**: 
  - `EmotionalAgentSystem`: 主管理类，协调所有代理
  - `emotion_detector`: 快速情感分析代理（基于fast_client）
  - `memory_manager`: 记忆管理代理（基于light_client）
  - `companion`: 主对话代理（基于conversation_client）
  - `thinker`: 内心思考代理（基于main_client）
  - `user_proxy`: 用户代理
- **工具系统**: 实现了记忆工具和视觉效果工具的函数式调用
- **自主模式**: 支持后台自动情感更新和主动对话

**conversation_handler.py** - 对话处理器
- **功能**: 处理用户输入，协调多代理协作，生成最终回复
- **实现逻辑**: 
  1. 接收用户输入
  2. 触发情感分析
  3. 启动记忆搜索和管理
  4. 生成内心思考
  5. 产生最终回复
  6. 处理视觉效果指令

#### 2.2 记忆管理系统 (`emotional_companion/memory/`)

**emotional_memory.py** - 情感记忆核心
- **功能**: 基于ChromaDB实现的长期记忆存储和检索系统
- **核心特性**:
  - **语义检索**: 使用sentence-transformers进行向量化
  - **记忆分类**: 对话记忆、用户偏好、关系事件、用户档案信息
  - **情感状态跟踪**: 动态记录和更新情感状态
  - **记忆衰减**: 模拟真实记忆的时间衰减效果
  - **自主联想**: 基于当前上下文的记忆联想机制
- **数据结构**:
  - 对话记忆：包含内容、时间戳、情感标签、重要性评分
  - 用户偏好：类别、项目、情感倾向、确定性
  - 关系事件：描述、重要性、对关系的影响
  - 情感状态：当前情绪、强度、价值、关系亲密度

#### 2.3 视觉效果系统 (`emotional_companion/effects/`)

**visual_effects_controller.py** - 视觉效果控制器
- **功能**: 根据对话内容和情感状态生成视觉效果指令
- **实现机制**:
  - **关键词映射**: 将对话关键词映射到视觉效果
  - **强度推断**: 自动分析文本情感强度
  - **效果分类**: 支持临时动画和持久主题两类效果
  - **指令生成**: 创建标准化的视觉效果控制指令
- **支持效果**:
  - 临时动画：庆祝、爱心、闪亮、花瓣、气泡等
  - 主题效果：温暖、清凉、夜晚、春日等

#### 2.4 工具模块 (`emotional_companion/utils/`)

**conversation_logger.py** - 轻量级日志系统
- **功能**: 记录对话历史和系统操作日志
- **特性**: 按日期分割、结构化记录、调试信息跟踪

**memory_viewer.py** - 记忆查看工具
- **功能**: 提供记忆数据的查看和分析界面

**time_utils.py** - 时间处理工具
- **功能**: 时间格式化、时区处理等时间相关工具函数

### 3. 技术实现逻辑

#### 3.1 多代理协作流程

```
用户输入 → 情感分析代理(快速) → 记忆管理代理(检索相关记忆) 
    ↓
内心思考代理(深度分析) → 主对话代理(生成回复+视觉效果) → 输出给用户
    ↓
记忆管理代理(保存新记忆) → 视觉效果控制器(处理效果指令)
```

---

## 第二部分：Web API服务与通信架构

### 1. Web API服务 (`web_api/`)

#### 1.1 FastAPI主应用 (`web_api.py`)

**主要接口**:
```python
# 核心API端点
POST /api/chat                    # 发送消息并获取AI回复
GET /api/emotional-state          # 获取当前情感状态
GET /api/memory-stats            # 获取记忆系统统计
POST /api/config/test            # 测试AI模型配置
GET /api/health                  # 健康检查

# WebSocket端点
WS /ws                           # 实时双向通信
```

#### 1.2 WebSocket处理器 (`websocket_handler.py`)

**SimpleWebSocketManager类**:

#### 1.3 配置管理器 (`config_manager.py`)

**功能特性**:
- **多模型支持**: OpenAI、Qwen、自定义API配置
- **配置验证**: 实时测试API连通性
- **备份恢复**: 配置文件的备份和还原机制
- **环境变量集成**: 支持.env文件和系统环境变量

### 2. 桌面客户端架构 (`mira-desktop/`)

#### 2.1 Electron主进程 (`main.js`)

### 3. 前端界面系统 (`web/`)

#### 3.1 主界面 (`index.html`)

**布局结构**:
```html
chat-container
├── chat-header          # 顶部状态栏
│   ├── avatar-container # 头像和在线状态
│   ├── header-info     # 情感状态显示
│   └── header-actions  # 设置和历史按钮
├── chat-messages       # 对话区域
└── chat-input-container # 输入区域
    ├── input-wrapper   # 文本输入框
    └── input-footer    # 字符计数和提示
```

#### 3.2 JavaScript核心 (`js/chat.js`)

**EmotionalChatApp类架构**:
```javascript
class EmotionalChatApp {
    constructor()           # 初始化应用
    init()                 # DOM元素绑定
    bindEvents()           # 事件监听器设置
    sendMessage()          # 发送消息逻辑
    displayMessage()       # 消息显示渲染
    setupAutoResize()      # 输入框自适应
    updateEmotionalState() # 情感状态更新
    handleApiError()       # 错误处理
}
```

**核心功能实现**:
- **消息处理**: 支持文本、表情、多行输入
- **实时通信**: 与WebSocket服务的连接管理
- **状态同步**: 情感状态和关系亲密度的实时更新
- **错误恢复**: 网络异常时的自动重连机制

### 4. 通信协议与数据流

#### 4.2 WebSocket实时通信

**连接建立**:
1. 客户端发起WebSocket连接到 `/ws`
2. 服务器验证连接数限制和频率限制
3. 建立双向通信通道

**消息类型**:
```json
# 用户消息
{
    "type": "user_message",
    "content": "用户输入内容",
    "timestamp": "2025-06-24T10:00:00Z"
}

# AI回复
{
    "type": "ai_response", 
    "content": "AI回复内容",
    "visual_effects": [...],
    "emotional_state": {...}
}

# 主动消息
{
    "type": "proactive_message",
    "content": "AI主动发起的消息"
}
```

#### 4.3 视觉效果指令传递

```
AI代理调用工具 → 效果指令队列 → Web API响应 → 前端渲染
control_visual_effect()  command_queue    JSON格式    JavaScript执行
```

**指令格式**:
```json
{
    "effect_name": "celebration",
    "effect_type": "temporary",
    "duration": 3000,
    "intensity": 0.8,
    "timestamp": "2025-06-24T10:00:00Z"
}
```

### 5. 数据存储与同步

#### 5.1 ChromaDB数据结构

**Collection分类**:
- `conversations`: 对话记忆向量存储
- `user_preferences`: 用户偏好数据
- `relationship_events`: 关系发展事件
- `user_profile`: 用户关键信息档案
- `emotional_states`: 历史情感状态记录

#### 5.2 配置文件管理

**OAI_CONFIG_LIST.json结构**:
```json
[
    {
        "model": "gpt-4o-mini",
        "api_key": "sk-xxx",
        "base_url": "https://api.openai.com/v1",
        "api_type": "openai"
    },
    // ... 其他模型配置
]
```

#### 5.3 日志系统

**日志分类**:
- **对话日志**: `logs/chat_YYYY-MM-DD.log`
- **系统日志**: Web API运行日志
- **错误日志**: 异常和错误记录
- **调试日志**: 开发调试信息

### 6. 部署与运行机制

#### 6.2 容器化部署

**Docker支持**:
- 环境变量适配: `DOCKER_ENV=true`
- 路径映射: `/app` 作为工作目录
- 数据持久化: `memory_db`、`logs` 目录挂载
- 端口暴露: `8000`端口的API服务

