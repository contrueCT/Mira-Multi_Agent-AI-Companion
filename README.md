# 小梦（Mira）- 智能情感陪伴系统

> **English Version Available** | [English documentation is available at the bottom of this README](#english-version)

一个集成了桌面客户端、智能视觉效果和配置管理的现代化 AI 情感陪伴系统。基于 Microsoft AutoGen v0.4 和 ChromaDB 构建，**拥有数十年级别的准确对话记忆能力和快速检索能力**，提供完整的桌面应用体验，让 AI 陪伴更加生动和个性化。

🎉 **现已正式发布！** 包含完整桌面客户端、Web API和配置管理功能，可以稳定运行。

## ✨ 核心特性

### 🖥️ 桌面客户端体验
- **原生桌面应用** - 基于 Electron 的跨平台桌面客户端，支持 Windows/Mac/Linux
- **美观现代界面** - 自定义标题栏、动态背景装饰、响应式布局设计
- **智能视觉效果** - AI 可控制的动态视觉效果，包括烟花、爱心、星光等多种特效
- **多主题支持** - 温暖、清凉、夕阳、夜晚、春日等多种主题，营造不同氛围

### 🎨 智能视觉效果系统
- **AI 控制特效** - 智能体可根据对话内容和情感状态自动触发相应视觉效果
- **丰富效果库** - 包含庆祝烟花、飘落爱心、闪烁星光、漂浮气泡、花瓣飞舞等多种效果
- **自适应强度** - 效果强度可根据情感程度自动调节
- **关键词触发** - 智能识别对话中的关键词，触发相关视觉效果

### ⚙️ 可视化配置管理
- **图形化配置界面** - 在客户端中直接配置 AI 模型、环境变量和用户偏好
- **多模型支持** - 支持 OpenAI、Qwen、自定义 API 等多种 LLM 配置
- **配置备份恢复** - 一键备份和恢复所有配置，确保数据安全
- **实时连接测试** - 验证 API 配置的有效性

### 🧠 智能记忆与情感系统
- **超长期记忆能力** - 基于 ChromaDB 的语义检索，可准确记忆和快速查询数十年的对话历史
- **智能记忆管理** - 自动提取关键信息，永久保存重要时刻和用户偏好
- **情感状态模型** - 动态情感变化，支持多种情绪和关系亲密度系统（1-10级）
- **多代理协作** - 基于 Microsoft AutoGen v0.4 的专业代理系统
- **主动关怀机制** - 智能体会主动发起关怀对话和回忆分享

## 📦 快速开始

### 系统要求

- **Python 3.10+** - 支持现代异步编程特性
- **Node.js 16+** - 运行桌面客户端所需
- **操作系统** - Windows 10+, macOS 10.14+, Ubuntu 18.04+

### 一键启动（推荐）

1. **克隆项目**
```bash
git clone https://github.com/yourusername/emotional-companion.git
cd emotional-companion
```

2. **安装依赖**
```bash
# 使用 UV 安装（推荐）
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
uv pip install -e .

# 或使用 Pip 安装
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
pip install -e .
```

3. **安装桌面客户端依赖**
```bash
cd mira-desktop
npm install
cd ..
```

4. **配置 API 密钥**

系统需要配置 4 个 API 接口，请编辑 `configs/OAI_CONFIG_LIST.json` 文件：

```json
[
    {
        "model": "Qwen/Qwen3-235B-A22B",
        "api_key": "your-api-key-here",
        "base_url": "https://api.siliconflow.cn/v1",
        "api_type": "openai"
    },
    {
        "model": "Qwen/Qwen3-8B",
        "api_key": "your-api-key-here", 
        "base_url": "https://api.siliconflow.cn/v1",
        "api_type": "openai"
    },
    {
        "model": "Qwen/Qwen3-235B-A22B",
        "api_key": "your-api-key-here",
        "base_url": "https://api.siliconflow.cn/v1", 
        "api_type": "openai"
    },
    {
        "model": "Qwen/Qwen3-235B-A22B",
        "api_key": "your-api-key-here",
        "base_url": "https://api.siliconflow.cn/v1",
        "api_type": "openai"
    }
]
```

> **建议：** 第二个API可以使用较小的模型（如 Qwen/Qwen3-8B）以节省成本，第四个API使用次弱的模型，第三个API使用次次弱的模型，第一个API使用最强的模型，不建议全部使用参数量大的模型，不建议使用不支持非推理模式的模型，本项目代码对qwen3这样支持推理和非推理模型的api进行了特殊配置以让模型保持在非推理状态，使用推理模型/推理模式并不能增强本项目智能体的实际表现

5. **启动系统**
```bash
# 启动 Web API 服务器
python web_api/start_web_api.py

# 在新终端中启动桌面客户端
cd mira-desktop
npm start
```

### 使用体验

启动后您将看到：
- **智能对话** - 支持情感理解和记忆回顾的自然交流
- **视觉效果** - 根据对话内容自动触发的动态特效
- **配置管理** - 点击设置按钮可直接配置系统参数
- **主题切换** - 多种视觉主题营造不同对话氛围

## 🏗️ 系统架构

小梦采用现代化的三层架构设计：

```
桌面客户端 (Electron)  ←→  Web API 服务器 (FastAPI)  ←→  AI 智能体系统 (AutoGen)
     ↓                           ↓                          ↓
 视觉效果渲染              配置管理与API接口           记忆系统 (ChromaDB)
```

### 🧠 AI 智能体核心

**多代理协作系统：**
- **情感分析师** - 分析用户情绪状态和强度
- **记忆管理员** - 管理多种记忆类型的存储和检索
- **内心思考** - 生成智能体的思维过程和策略
- **情感陪伴** - 主对话代理，生成自然回复

**智能视觉效果系统：**
- 庆祝烟花、飘落爱心、闪烁星光等临时效果
- 温暖、清凉、夕阳、夜晚、春日等主题背景
- 基于关键词和情感状态的智能触发

**向量化记忆系统：**
- 基于 BAAI/bge-base-zh-v1.5 的语义理解，支持数十年级别的对话记忆存储  
- ChromaDB 持久化存储和闪电级检索，毫秒内从海量记忆中精准定位
- 智能记忆分层管理：短期记忆、长期记忆、核心记忆永久保存
- 支持记忆衰减、重要性加权和联想机制，确保关键信息永不丢失

### �️ 安全与稳定性

**配置安全：**
- API 密钥加密存储和传输
- 配置文件权限控制
- 敏感信息脱敏显示

**系统稳定性：**
- 异常处理和错误恢复
- 内存泄漏防护
- 优雅降级机制


## 🎯 重点功能

### 🎨 智能视觉效果

**AI 驱动的动态效果：**
- **情感联动** - 根据对话情绪自动触发相应视觉效果
- **关键词识别** - 智能识别"庆祝"、"开心"、"浪漫"等触发词
- **效果丰富** - 包含 12+ 种精美动画效果

**支持的视觉效果：**
- 🎆 **庆祝烟花** - 适用于成功、庆祝、开心时刻
- 💕 **飘落爱心** - 表达爱意、温馨、浪漫情感
- ✨ **闪烁星光** - 营造梦幻、神奇的氛围
- 🫧 **漂浮气泡** - 轻松、愉快的互动场景
- 🌸 **花瓣飞舞** - 优雅、浪漫的对话时刻

### 🎭 多主题界面

**丰富的视觉主题：**
- 🔥 **温暖主题** - 暖色调光斑，营造温馨氛围
- ❄️ **清凉主题** - 冷色调波纹，带来清爽感受
- 🌅 **夕阳主题** - 橙红渐变，模拟夕阳西下
- 🌙 **夜晚主题** - 动态星空，深色护眼模式
- 🌸 **春日主题** - 清新绿调，充满生机活力

### ⚙️ 配置管理

**多模型支持：**
- 使用OPENAI的API接口协议的大模型
- 自定义 API 端点配置
- 实时连接状态检测

**个性化设置：**
- 用户名称和 AI 助手名称
- AI 性格设定和角色描述
- 界面主题和语言偏好
- 功能开关和通知设置

**安全备份：**
- 一键备份所有配置
- 历史版本管理
- 快速恢复功能

### 🧠 智能记忆与学习

**深度记忆能力：**
- **用户档案** - 生日、家庭、职业等基本信息
- **偏好记录** - 兴趣爱好、习惯和喜好
- **情感历程** - 情感状态变化和重要时刻
- **关系发展** - 亲密度变化和关系里程碑

**智能学习机制：**
- 自动提取对话中的关键信息
- 基于时间和重要性的记忆衰减
- 支持记忆联想和主动回忆
- 情感状态影响记忆权重

### 🤖 多代理协作

**专业化分工：**
每个代理都有明确的职责和专业领域，协作完成复杂的情感交互任务

**智能决策：**
多个代理共同分析和决策，确保回复的准确性和情感适当性

**效率优化：**
并行处理和异步执行，确保快速响应用户需求

## 📝 技术栈与架构

## � 技术栈

| 层级 | 技术选型 | 版本要求 | 主要用途 |
|------|----------|----------|----------|
| **桌面客户端** | Electron | v27.0+ | 跨平台桌面应用 |
| **前端界面** | HTML5 + CSS3 + JavaScript | - | 用户界面与交互 |
| **后端API** | FastAPI + Uvicorn | - | 高性能 Web 服务 |
| **AI框架** | Microsoft AutoGen | v0.4+ | 多代理协作系统 |
| **向量数据库** | ChromaDB | >=0.4.17 | 语义记忆存储 |
| **嵌入模型** | BAAI/bge-base-zh-v1.5 | - | 中英文语义理解 |

### 🏗️ 项目结构

```
emotional-companion/
├── 🖥️  mira-desktop/          # 桌面客户端 (Electron)
├── 🌐 web_api/               # Web API 服务 (FastAPI)
├── 🧠 emotional_companion/   # AI 智能体核心 (AutoGen)
├── 📁 configs/              # 配置文件
├── 📊 logs/                 # 日志文件
└── 🗃️  memory_db/           # 记忆数据库
```



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

# Mira (小梦) - Intelligent Emotional Companion System

A modern AI emotional companion system that integrates desktop client, intelligent visual effects, and configuration management. Built with Microsoft AutoGen v0.4 and ChromaDB, **featuring decades-level conversation memory capabilities and millisecond-level retrieval speed**, providing a complete desktop application experience that makes AI companionship more vivid and personalized.

🎉 **Now officially released!** Includes complete desktop client, Web API, and configuration management features, ready for stable operation.

## ✨ Core Features

### 🖥️ Desktop Client Experience
- **Native Desktop App** - Cross-platform desktop client based on Electron, supporting Windows/Mac/Linux
- **Beautiful Modern Interface** - Custom title bar, dynamic background decorations, responsive layout design
- **Intelligent Visual Effects** - AI-controllable dynamic visual effects including fireworks, hearts, starlight, and more
- **Multi-theme Support** - Warm, cool, sunset, night, spring themes to create different atmospheres

### 🎨 Intelligent Visual Effects System
- **AI-Controlled Effects** - AI can automatically trigger appropriate visual effects based on conversation content and emotional state
- **Rich Effect Library** - Includes celebration fireworks, falling hearts, twinkling stars, floating bubbles, flower petals, and more
- **Adaptive Intensity** - Effect intensity automatically adjusts based on emotional degree
- **Keyword Triggers** - Intelligently recognizes keywords in conversation to trigger related visual effects

### ⚙️ Visual Configuration Management
- **Graphical Configuration Interface** - Configure AI models, environment variables, and user preferences directly in the client
- **Multi-model Support** - Supports OpenAI, Qwen, custom APIs, and other LLM configurations
- **Configuration Backup & Restore** - One-click backup and restore of all configurations for data security
- **Real-time Connection Testing** - Verify API configuration validity

### 🧠 Intelligent Memory & Emotional System
- **Ultra-Long-Term Memory** - Accurate memory and lightning-fast retrieval of decades of conversation history based on ChromaDB
- **Intelligent Memory Management** - Automatically extracts key information, permanently stores important moments and user preferences  
- **Emotional State Model** - Dynamic emotional changes, supporting multiple emotions and relationship intimacy system (1-10 levels)
- **Multi-agent Collaboration** - Professional agent system based on Microsoft AutoGen v0.4
- **Proactive Care Mechanism** - AI actively initiates caring conversations and memory sharing

## 📦 Quick Start

### System Requirements

- **Python 3.10+** - Supports modern async programming features
- **Node.js 16+** - Required for running desktop client
- **Operating System** - Windows 10+, macOS 10.14+, Ubuntu 18.04+

### One-Click Launch (Recommended)

1. **Clone the project**
```bash
git clone https://github.com/yourusername/emotional-companion.git
cd emotional-companion
```

2. **Install dependencies**
```bash
# Using UV (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
uv pip install -e .

# Or using Pip
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows
pip install -e .
```

3. **Install desktop client dependencies**
```bash
cd mira-desktop
npm install
cd ..
```

4. **Configure API Keys**

The system requires 4 API interfaces. Please edit the `configs/OAI_CONFIG_LIST.json` file:

```json
[
    {
        "model": "gpt-4",
        "api_key": "your-api-key-here",
        "base_url": "https://api.openai.com/v1",
        "api_type": "openai"
    },
    {
        "model": "gpt-3.5-turbo",
        "api_key": "your-api-key-here", 
        "base_url": "https://api.openai.com/v1",
        "api_type": "openai"
    },
    {
        "model": "gpt-4",
        "api_key": "your-api-key-here",
        "base_url": "https://api.openai.com/v1", 
        "api_type": "openai"
    },
    {
        "model": "gpt-4",
        "api_key": "your-api-key-here",
        "base_url": "https://api.openai.com/v1",
        "api_type": "openai"
    }
]
```

> **Note:** The second API can use a smaller model (like gpt-3.5-turbo) to save costs. The other three are recommended to use gpt-4 for better performance.

5. **Launch System**
```bash
# Start Web API server
python web_api/start_web_api.py

# In a new terminal, start desktop client
cd mira-desktop
npm start
```

### User Experience

After launching, you will see:
- **Welcome Interface** - Mira actively greets and introduces features
- **Intelligent Conversation** - Natural communication supporting emotional understanding and memory recall
- **Visual Effects** - Dynamic effects automatically triggered based on conversation content
- **Configuration Management** - Click settings button to directly configure system parameters
- **Theme Switching** - Multiple visual themes creating different conversation atmospheres

## 🏗️ System Architecture

Mira adopts a modern three-tier architecture:

```
Desktop Client (Electron)  ←→  Web API Server (FastAPI)  ←→  AI Agent System (AutoGen)
        ↓                            ↓                           ↓
Visual Effects Rendering      Configuration & API Interface    Memory System (ChromaDB)
```

### 🧠 AI Agent Core

**Multi-agent Collaboration System:**
- **Emotion Analyzer** - Analyzes user emotional states and intensity
- **Memory Manager** - Manages storage and retrieval of various memory types
- **Inner Thoughts** - Generates AI's thinking processes and strategies
- **Emotional Companion** - Main dialogue agent that generates natural responses

**Intelligent Visual Effects System:**
- Celebration fireworks, falling hearts, twinkling stars and other temporary effects
- Warm, cool, sunset, night, spring themed backgrounds
- Intelligent triggering based on keywords and emotional states

**Vectorized Memory System:**
- Semantic understanding based on BAAI/bge-base-zh-v1.5, supporting decades-level conversation memory storage
- ChromaDB persistent storage and lightning-fast retrieval, precisely locating from massive memories within milliseconds
- Intelligent memory hierarchy management: short-term, long-term, and core memories permanently preserved
- Supports memory decay, importance weighting, and associative mechanisms, ensuring critical information is never lost

## 🎯 Feature Highlights

### 🎨 Intelligent Visual Effects

**Supported Visual Effects:**
- 🎆 **Celebration Fireworks** - For success, celebration, happy moments
- 💕 **Falling Hearts** - Express love, warmth, romantic emotions
- ✨ **Twinkling Starlight** - Create dreamy, magical atmosphere
- 🫧 **Floating Bubbles** - Relaxed, pleasant interactive scenarios
- 🌸 **Flying Petals** - Elegant, romantic conversation moments

### 🎭 Multi-theme Interface

**Rich Visual Themes:**
- 🔥 **Warm Theme** - Warm-toned light spots, creating cozy atmosphere
- ❄️ **Cool Theme** - Cool-toned ripples, bringing refreshing feel
- 🌅 **Sunset Theme** - Orange-red gradient, simulating sunset
- 🌙 **Night Theme** - Dynamic starry sky, dark eye-protection mode
- 🌸 **Spring Theme** - Fresh green tones, full of vitality

## 📝 Technology Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Desktop Client** | Electron | v27.0+ | Cross-platform desktop app |
| **Frontend** | HTML5 + CSS3 + JavaScript | - | User interface & interaction |
| **Backend API** | FastAPI + Uvicorn | - | High-performance web service |
| **AI Framework** | Microsoft AutoGen | v0.4+ | Multi-agent collaboration |
| **Vector Database** | ChromaDB | >=0.4.17 | Semantic memory storage |
| **Embedding Model** | BAAI/bge-base-zh-v1.5 | - | Chinese-English semantic understanding |

### 🏗️ Project Structure

```
emotional-companion/
├── 🖥️  mira-desktop/          # 桌面客户端 (Electron)
├── 🌐 web_api/               # Web API 服务 (FastAPI)
├── 🧠 emotional_companion/   # AI 智能体核心 (AutoGen)
├── 📁 configs/              # 配置文件
├── 📊 logs/                 # 日志文件
└── 🗃️  memory_db/           # 记忆数据库
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Welcome to submit Issues and Pull Requests to help improve Mira!

## 💬 Feedback

If you encounter problems or have suggestions during use, please feel free to create an Issue or contact the developer.

---

**Mira is waiting for your first conversation, let's start a special journey of friendship!** ✨