# 情感陪伴AI Web API 文档

## 概述
这是小梦情感陪伴AI系统的Web API接口，提供RESTful API来连接前端Web界面与后端对话处理器。

## 快速开始

### 1. 安装依赖
```bash
cd web_api
pip install -r requirements-web.txt
```

### 2. 启动服务器
```bash
# 方法1: 使用启动脚本
python start_web_api.py

# 方法2: 直接运行
python web_api.py

# 方法3: 使用项目根目录的便捷脚本
python start_web_server.py
```

### 3. 访问API
- **API文档**: http://localhost:8000/docs
- **前端界面**: http://localhost:8000/static/index.html
- **健康检查**: http://localhost:8000/api/health

## API 端点

### 聊天接口
**POST** `/api/chat`

发送消息给AI并获取回复。

**请求体:**
```json
{
    "message": "你好，小梦！",
    "enable_timing": false
}
```

**响应:**
```json
{
    "response": "你好呀！很高兴见到你～ 💕",
    "timestamp": "2025-06-05T10:30:00.000Z",
    "emotional_state": {
        "current_emotion": "happy",
        "emotion_intensity": 0.8,
        "relationship_level": 8
    },
    "processing_time": 1.23
}
```

### 情感状态
**GET** `/api/emotional-state`

获取AI当前的情感状态。

**响应:**
```json
{
    "current_emotion": "happy",
    "emotion_intensity": 0.8,
    "relationship_level": 8,
    "last_updated": "2025-06-05T10:30:00.000Z"
}
```

### 聊天历史
**GET** `/api/chat/history`

获取聊天历史记录。

**查询参数:**
- `limit`: 返回记录数量限制 (默认50)
- `offset`: 偏移量 (默认0)  
- `reverse`: 是否倒序返回 (默认true)

**响应:**
```json
{
    "items": [
        {
            "id": "uuid-string",
            "user_message": "你好",
            "ai_response": "你好呀！",
            "timestamp": "2025-06-05T10:30:00.000Z",
            "emotional_state": {...}
        }
    ],
    "total_count": 10,
    "has_more": false
}
```

### 清空历史
**DELETE** `/api/chat/history`

清空聊天历史记录。

**响应:**
```json
{
    "message": "聊天历史已清空",
    "timestamp": "2025-06-05T10:30:00.000Z"
}
```

### 健康检查
**GET** `/api/health`

检查API服务器和相关服务的健康状态。

**响应:**
```json
{
    "status": "healthy",
    "timestamp": "2025-06-05T10:30:00.000Z",
    "version": "1.0.0",
    "uptime": 3600.5,
    "services": {
        "conversation_handler": "healthy",
        "chat_history": "healthy",
        "api_server": "healthy"
    }
}
```

### 系统统计
**GET** `/api/stats`

获取系统运行统计信息。

**响应:**
```json
{
    "uptime_seconds": 3600.5,
    "uptime_formatted": "1:00:00",
    "chat_history_count": 25,
    "max_history_size": 1000,
    "conversation_handler_status": "initialized",
    "timestamp": "2025-06-05T10:30:00.000Z"
}
```

## 错误处理

API使用标准HTTP状态码和统一的错误响应格式：

```json
{
    "error": "Bad Request",
    "message": "具体的错误描述",
    "timestamp": "2025-06-05T10:30:00.000Z",
    "status_code": 400
}
```

常见状态码：
- `200` - 成功
- `400` - 请求参数错误
- `500` - 服务器内部错误
- `503` - 服务不可用（ConversationHandler未初始化）

## CORS配置

API默认允许所有来源的跨域请求，生产环境中应该限制为具体域名。

## 前端集成

前端已配置为自动连接到 `http://localhost:8000` 的API服务器。如果API不可用，前端会自动降级到模拟模式。

## 部署注意事项

1. **配置文件**: 确保 `configs/OAI_CONFIG_LIST.json` 正确配置
2. **虚拟环境**: 建议使用虚拟环境隔离依赖
3. **端口配置**: 默认使用8000端口，可在代码中修改
4. **生产部署**: 使用Gunicorn或其他WSGI服务器部署到生产环境

## 开发调试

启用开发模式：
```bash
uvicorn web_api.web_api:app --reload --log-level debug
```

查看详细日志来调试API问题。
