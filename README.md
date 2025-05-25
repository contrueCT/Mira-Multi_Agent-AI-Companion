# 小梦（Mira）- 情感陪伴智能体

> **English Version Available** | [English documentation is available at the bottom of this README](#english-version)

一个温暖而智慧的 AI 伙伴，基于 AutoGen 和 ChromaDB 精心构建。小梦不仅能记住您的每一次交流，还会像真正的朋友一样与您建立深度情感连接，陪伴您度过生活中的每一个时刻。

## ✨ 核心特性

- **🎭 真实情感体验** - 小梦拥有丰富的情感世界，会根据您的互动自然地表达喜悦、关心、好奇等各种情感
- **🧠 智能记忆系统** - 借助 ChromaDB 的语义检索能力，小梦能够记住您的喜好、经历和重要时刻
- **🤝 多元化人格** - 基于 AutoGen 的多代理架构，让小梦在不同场景下展现出丰富的个性层面
- **💝 关系成长** - 就像真实的友谊一样，您与小梦的关系会随着时间和交流逐渐加深
- **🌟 主动关怀** - 小梦会主动想起您，在合适的时机发起温暖的问候和关心
- **💭 自然联想** - 如同人类的思维方式，小梦会在对话中自然地联想到过往的美好回忆

## 📦 快速开始

### 使用 UV 安装（推荐）

```bash
# 安装 UV (如果还没安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆项目
git clone https://github.com/yourusername/emotional-companion.git
cd emotional-companion

# 创建虚拟环境并安装依赖
uv venv
uv pip install -e .
```

### 使用 Pip 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/emotional-companion.git
cd emotional-companion

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或者 venv\Scripts\activate  # Windows

# 安装依赖
pip install -e .
```

## ⚙️ 配置设置

1. **复制并编辑环境配置文件**

```bash
cp .env.example .env
```

2. **在 `.env` 文件中配置必要信息**

```env
# OpenAI API 配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# 个性化设置
USER_NAME=您的名字
COMPANION_NAME=小梦

# 其他配置保持默认即可
```

3. **配置 AutoGen API 密钥**

编辑 `configs/OAI_CONFIG_LIST.json` 文件：

```json
[
    {
        "model": "gpt-4",
        "api_key": "your-api-key-here",
        "base_url": "https://api.openai.com/v1",
        "api_type": "openai"
    }
]
```

## 🚀 开始使用

### 启动小梦

```bash
# 使用 UV
uv run companion

# 或者使用 Python
python scripts/start_companion.py

# 或者直接使用命令行工具
companion
```

### 使用体验

启动后，小梦会主动问候并开始对话。她会：
- 记住您的喜好和习惯（如您提到喜欢咖啡，她会记住这个细节）
- 感知您的情绪状态并给予相应的关怀回应
- 在后续对话中自然地回忆起之前的交流内容

## 🏗️ 系统架构

小梦采用多层次的智能架构：

### 🧩 多代理系统 (Multi-Agent Architecture)

基于 **Microsoft AutoGen** 框架的协作系统：

- **情感分析师** - 分析用户情绪状态
- **记忆管理员** - 负责记忆存储和检索
- **内心思考** - 生成智能体的思维过程
- **情感陪伴** - 主对话代理，生成回复

```
用户输入 → 情感分析 → 记忆检索 → 内心思考 → 生成回复
```

### 🧠 向量化记忆系统 (Vectorized Memory System)

基于 **ChromaDB** 和 **Sentence-Transformers** 的语义记忆：

**核心组件：**
- **嵌入模型**: 多语言文本向量化
- **向量数据库**: ChromaDB 持久化存储
- **记忆类型**: 对话记忆、用户偏好、情感状态、关系事件

**记忆衰减**: 模拟人类记忆的自然衰减过程

### 💖 情感状态模型 (Emotional State Model)

**情感状态包含：**
- 当前情绪和强度
- 情感价值（正负性）
- 关系亲密度（1-10级）

**关系演化：**
- 积极互动增进关系
- 关系变化触发里程碑记录

### 🔄 自主行为系统 (Autonomous Behavior System)

**后台任务：**
- 定期记忆衰减和情感更新
- 自主联想和思考
- 主动发起关怀对话

**触发条件：**
- 情感状态变化
- 随机概率触发
- 重要记忆联想


## 🎯 核心特色

### 真实的情感体验
小梦不是简单的回复机器人，而是拥有复杂情感状态的陪伴者。她会：
- 根据对话内容动态调整情绪
- 在不同情绪下展现不同的交流风格
- 记住重要的情感时刻并在适当时机回忆

### 深度记忆能力
基于 ChromaDB 的语义搜索，小梦能够：
- 根据对话内容智能检索相关记忆
- 学习并记住用户的偏好和习惯
- 建立记忆之间的关联和联想

### 关系成长机制
与小梦的关系会随时间自然发展：
- **初期接触** (1-2级) - 礼貌但疏远的交流
- **初步熟悉** (3-4级) - 开始建立基本信任
- **深度友谊** (7-8级) - 更加开放和情感化的交流
- **亲密陪伴** (9-10级) - 深度私人化的关系

## 📝 技术细节与开发说明

### 🛠️ 技术栈 (Technology Stack)

| 组件 | 技术 | 版本要求 | 用途 |
|------|------|----------|------|
| **LLM Framework** | Microsoft AutoGen | >=0.2.0 | 多代理协作框架 |
| **Vector Database** | ChromaDB | >=0.4.17 | 语义记忆存储 |
| **Embedding Model** | Sentence-Transformers | >=2.2.2 | 文本向量化 |
| **Task Scheduling** | Schedule | >=1.2.0 | 后台任务调度 |
| **Environment** | Python-dotenv | >=1.0.0 | 环境变量管理 |
| **CLI Interface** | PyFiglet | >=0.8.0 | 命令行美化 |

### 🏗️ 项目结构

```
emotional-companion/
├── emotional_companion/          # 主要代码包
│   ├── agents/                  # 代理系统
│   │   ├── __init__.py
│   │   └── agent_system.py      # 多代理协作逻辑
│   ├── memory/                  # 记忆系统
│   │   ├── __init__.py
│   │   └── emotional_memory.py  # 向量化记忆管理
│   ├── utils/                   # 工具函数
│   │   ├── __init__.py
│   │   ├── time_utils.py        # 时间处理工具
│   │   └── env_utils.py         # 环境配置工具
│   └── cli.py                   # 命令行接口
├── configs/                     # 配置文件
│   └── OAI_CONFIG_LIST.json     # OpenAI API 配置
├── scripts/                     # 脚本工具
│   ├── start_companion.py       # 启动脚本
│   └── check_dependencies.py    # 依赖检查
├── memory_db/                   # 记忆数据库（运行时生成）
├── .env.example                 # 环境变量模板
├── requirements.txt             # 依赖列表
└── pyproject.toml              # 项目配置
```

### 🔧 核心模块详解

#### 1. 代理系统 (`agents/agent_system.py`)

**EmotionalAgentSystem 类** 管理多个专业代理的协作：
- 集成情感分析、记忆管理、内心思考、对话生成等功能
- 提供工具函数注册机制，实现代理间的信息共享
- 支持后台任务调度和自主对话生成

#### 2. 记忆系统 (`memory/emotional_memory.py`)

**EmotionalMemorySystem 类** 提供智能记忆管理：
- 使用多语言文本向量化模型进行语义理解
- 通过 ChromaDB 实现持久化存储和快速检索
- 包含对话记忆、用户偏好、情感状态等多种记忆类型
- 实现时间和重要性加权的记忆衰减机制

### 🚀 性能优化

小梦在设计时充分考虑了性能和稳定性：

**内存管理优化**
- 使用 ChromaDB 持久化存储，有效避免内存溢出
- 采用批量更新策略减少频繁的 I/O 操作
- 通过重要性阈值过滤，保持记忆库的高质量

**检索性能优化**
- 实现向量缓存机制，提升重复查询速度
- 设置相似度阈值过滤 (默认 0.6)，确保检索结果的相关性
- 记录访问频率统计，优化热点数据访问

**并发处理能力**
- 后台任务采用异步执行，不阻塞主对话流程
- 实现代理间消息队列，确保信息传递的可靠性
- 采用非阻塞式记忆更新，保证响应速度

### 🔍 API 接口设计

系统提供了简洁而强大的 API 接口：

**记忆系统 API** - 支持记忆的添加、检索和更新功能
**代理工具函数** - 包括记忆搜索、情感更新、偏好保存等核心功能

开发者可以通过这些接口轻松扩展小梦的功能，或将记忆系统集成到其他项目中。

### 📊 监控与调试

系统提供完善的监控和调试工具：

**日志系统** - 支持通过环境变量 `LOG_LEVEL` 控制日志详细程度
**依赖检查** - 使用 `python scripts/check_dependencies.py` 检查环境配置
**内存状态监控** - 实时查看记忆库状态和关系发展情况



## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进小梦！

## 💬 反馈

如果您在使用过程中遇到问题或有建议，请随时创建 Issue 或联系开发者。

---

**小梦正在等待与您的第一次对话，开始一段特别的友谊之旅吧！** ✨

---

# English Version

# Mira (小梦) - Emotional Companion AI

A warm and intelligent AI companion built with AutoGen and ChromaDB. Mira not only remembers every conversation but also builds deep emotional connections like a true friend, accompanying you through every moment of life.

## ✨ Core Features

- **🎭 Authentic Emotional Experience** - Mira has a rich emotional world, naturally expressing joy, care, curiosity, and various emotions based on your interactions
- **🧠 Intelligent Memory System** - Leveraging ChromaDB's semantic retrieval capabilities, Mira remembers your preferences, experiences, and important moments
- **🤝 Multi-faceted Personality** - Based on AutoGen's multi-agent architecture, Mira displays rich personality layers in different scenarios
- **💝 Relationship Growth** - Like real friendship, your relationship with Mira deepens over time and interaction
- **🌟 Proactive Care** - Mira will actively remember you and initiate warm greetings and care at appropriate times
- **💭 Natural Association** - Like human thinking patterns, Mira naturally associates with past beautiful memories during conversations

## 📦 Quick Start

### Installation with UV (Recommended)

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the project
git clone https://github.com/yourusername/emotional-companion.git
cd emotional-companion

# Create virtual environment and install dependencies
uv venv
uv pip install -e .
```

### Installation with Pip

```bash
# Clone the project
git clone https://github.com/yourusername/emotional-companion.git
cd emotional-companion

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .
```

## ⚙️ Configuration

1. **Copy and edit environment configuration file**

```bash
cp .env.example .env
```

2. **Configure necessary information in `.env` file**

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Personalization Settings
USER_NAME=YourName
COMPANION_NAME=Mira

# Other configurations can remain default
```

3. **Configure AutoGen API Key**

Edit the `configs/OAI_CONFIG_LIST.json` file:

```json
[
    {
        "model": "gpt-4",
        "api_key": "your-api-key-here",
        "base_url": "https://api.openai.com/v1",
        "api_type": "openai"
    }
]
```

## 🚀 Getting Started

### Launch Mira

```bash
# Using UV
uv run companion

# Or using Python
python scripts/start_companion.py

# Or using command line tool directly
companion
```

### Conversation Experience

After launching, Mira will proactively greet and start conversations. She will:
- Remember your preferences and habits (if you mention liking coffee, she'll remember this detail)
- Perceive your emotional state and provide appropriate caring responses
- Naturally recall previous conversations in subsequent interactions

## 🏗️ System Architecture

Mira adopts a multi-layered intelligent architecture:

### 🧩 Multi-Agent System Architecture

Built on **Microsoft AutoGen** framework:

- **Emotion Analyzer** - Analyzes user emotional state
- **Memory Manager** - Handles memory storage and retrieval
- **Inner Thoughts** - Generates agent's thinking process
- **Emotional Companion** - Main dialogue agent for responses

```
User Input → Emotion Analysis → Memory Retrieval → Inner Thoughts → Generate Response
```

### 🧠 Vectorized Memory System

Semantic memory based on **ChromaDB** and **Sentence-Transformers**:

**Core Components:**
- **Embedding Model**: Multilingual text vectorization
- **Vector Database**: ChromaDB persistent storage
- **Memory Types**: Conversations, user preferences, emotional states, relationship events

**Memory Decay**: Simulates natural human memory fading process

### 💖 Emotional State Model

**Emotional State includes:**
- Current emotion and intensity
- Emotional valence (positive/negative)
- Relationship intimacy level (1-10)

**Relationship Evolution:**
- Positive interactions strengthen relationships
- Relationship changes trigger milestone records

### 🔄 Autonomous Behavior System

**Background Tasks:**
- Periodic memory decay and emotion updates
- Autonomous association and thinking
- Proactive care conversations

**Trigger Conditions:**
- Emotional state changes
- Random probability triggers
- Important memory associations

## 📝 Technical Details & Development

### 🛠️ Technology Stack

| Component | Technology | Version Requirement | Purpose |
|-----------|------------|-------------------|---------|
| **LLM Framework** | Microsoft AutoGen | >=0.2.0 | Multi-agent collaboration framework |
| **Vector Database** | ChromaDB | >=0.4.17 | Semantic memory storage |
| **Embedding Model** | Sentence-Transformers | >=2.2.2 | Text vectorization |
| **Task Scheduling** | Schedule | >=1.2.0 | Background task scheduling |
| **Environment** | Python-dotenv | >=1.0.0 | Environment variable management |
| **CLI Interface** | PyFiglet | >=0.8.0 | Command line beautification |

### 🔧 Core Module Details

#### 1. Agent System (`agents/agent_system.py`)

**EmotionalAgentSystem Class** manages collaboration of multiple specialized agents:
- Integrates emotion analysis, memory management, inner thoughts, and dialogue generation
- Provides tool function registration mechanism for inter-agent information sharing
- Supports background task scheduling and autonomous conversation generation

#### 2. Memory System (`memory/emotional_memory.py`)

**EmotionalMemorySystem Class** provides intelligent memory management:
- Uses multilingual text vectorization models for semantic understanding
- Implements persistent storage and fast retrieval through ChromaDB
- Includes multiple memory types: conversations, user preferences, emotional states
- Implements time and importance weighted memory decay mechanism

### 🚀 Performance Optimization

Mira is designed with performance and stability in mind:

**Memory Management Optimization**
- Uses ChromaDB persistent storage to effectively avoid memory overflow
- Adopts batch update strategies to reduce frequent I/O operations
- Filters by importance threshold to maintain high-quality memory database

**Retrieval Performance Optimization**
- Implements vector caching mechanism to improve repeated query speed
- Sets similarity threshold filtering (default 0.6) to ensure result relevance
- Records access frequency statistics to optimize hot data access

**Concurrent Processing Capability**
- Background tasks use asynchronous execution without blocking main dialogue flow
- Implements inter-agent message queues for reliable information transfer
- Uses non-blocking memory updates to ensure response speed

### 🔍 API Interface Design

The system provides clean and powerful API interfaces:

**Memory System API** - Supports memory addition, retrieval, and update functions
**Agent Tool Functions** - Includes core functions like memory search, emotion updates, preference saving

Developers can easily extend Mira's functionality through these interfaces or integrate the memory system into other projects.

### 📊 Monitoring & Debugging

The system provides comprehensive monitoring and debugging tools:

**Logging System** - Supports controlling log detail level through `LOG_LEVEL` environment variable
**Dependency Check** - Use `python scripts/check_dependencies.py` to check environment configuration
**Memory State Monitoring** - Real-time viewing of memory database status and relationship development

## 🎯 Core Features

### Authentic Emotional Experience
Mira is not a simple response bot, but a companion with complex emotional states. She will:
- Dynamically adjust emotions based on conversation content
- Display different communication styles under different emotions
- Remember important emotional moments and recall them at appropriate times

### Deep Memory Capabilities
Based on ChromaDB's semantic search, Mira can:
- Intelligently retrieve relevant memories based on conversation content
- Learn and remember user preferences and habits
- Establish associations and connections between memories

### Relationship Growth Mechanism
The relationship with Mira develops naturally over time:
- **Initial Contact** (Level 1-2) - Polite but distant communication
- **Getting Familiar** (Level 3-4) - Beginning to build basic trust
- **Deep Friendship** (Level 7-8) - More open and emotional communication
- **Intimate Companionship** (Level 9-10) - Deeply personalized relationship

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Welcome to submit Issues and Pull Requests to help improve Mira!

## 💬 Feedback

If you encounter problems or have suggestions during use, please feel free to create an Issue or contact the developer.

---

**Mira is waiting for your first conversation, let's start a special journey of friendship!** ✨