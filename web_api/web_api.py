"""
情感陪伴AI系统 Web API 服务器
使用FastAPI提供RESTful API接口，连接前端Web界面与后端ConversationHandler
"""

import os
import sys
import time
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from emotional_companion.agents.conversation_handler import ConversationHandler
from web_api.models import (
    ChatRequest, ChatResponse, EmotionalState, 
    ChatHistory, ChatHistoryItem, HealthStatus, ErrorResponse
)


class WebAPIServer:
    """Web API 服务器类"""
    
    def __init__(self):
        self.conversation_handler: Optional[ConversationHandler] = None
        self.start_time = time.time()
        self.chat_history: List[ChatHistoryItem] = []
        self.max_history_size = 1000  # 最大历史记录数量
        
    async def initialize(self):
        """初始化ConversationHandler"""
        try:
            config_path = os.path.join(project_root, "configs", "OAI_CONFIG_LIST.json")
            self.conversation_handler = ConversationHandler(config_path)
            
            # 启动后台任务
            self.conversation_handler.start_background_tasks()
            
            print(f"✅ ConversationHandler初始化成功")
            print(f"✅ 配置文件: {config_path}")
            
        except Exception as e:
            print(f"❌ ConversationHandler初始化失败: {e}")
            raise
    
    async def cleanup(self):
        """清理资源"""
        if self.conversation_handler:
            self.conversation_handler.stop_background_tasks()
            print("✅ 后台任务已停止")


# 创建全局服务器实例
server = WebAPIServer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    await server.initialize()
    yield
    # 关闭时清理
    await server.cleanup()


# 创建FastAPI应用
app = FastAPI(
    title="情感陪伴AI Web API",
    description="小梦情感陪伴AI系统的Web API接口",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件服务
web_static_path = os.path.join(project_root, "web")
if os.path.exists(web_static_path):
    app.mount("/static", StaticFiles(directory=web_static_path), name="static")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            message=str(exc),
            timestamp=datetime.now(),
            status_code=500
        ).dict()
    )


@app.get("/", response_model=dict)
async def root():
    """根路径 - 返回API信息"""
    return {
        "name": "情感陪伴AI Web API",
        "version": "1.0.0",
        "description": "小梦情感陪伴AI系统的Web API接口",
        "docs_url": "/docs",
        "endpoints": {
            "chat": "/api/chat",
            "emotional_state": "/api/emotional-state",
            "chat_history": "/api/chat/history",
            "health": "/api/health"
        }
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    聊天接口 - 处理用户消息并返回AI回复
    """
    if not server.conversation_handler:
        raise HTTPException(
            status_code=503, 
            detail="ConversationHandler未初始化"
        )
    
    try:
        start_time = time.time()
        
        # 获取AI回复
        ai_response = await server.conversation_handler.get_response(
            request.message, 
            enable_timing=request.enable_timing
        )
        
        processing_time = time.time() - start_time
        
        # 获取当前情感状态
        emotional_state = server.conversation_handler.get_current_emotional_state()
        
        # 生成聊天记录ID
        chat_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # 添加到聊天历史
        chat_item = ChatHistoryItem(
            id=chat_id,
            user_message=request.message,
            ai_response=ai_response,
            timestamp=timestamp,
            emotional_state=emotional_state
        )
        
        server.chat_history.append(chat_item)
        
        # 限制历史记录大小
        if len(server.chat_history) > server.max_history_size:
            server.chat_history = server.chat_history[-server.max_history_size:]
        
        return ChatResponse(
            response=ai_response,
            timestamp=timestamp,
            emotional_state=emotional_state,
            processing_time=processing_time if request.enable_timing else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"处理聊天消息时发生错误: {str(e)}"
        )


@app.get("/api/emotional-state", response_model=EmotionalState)
async def get_emotional_state():
    """
    获取当前情感状态
    """
    if not server.conversation_handler:
        raise HTTPException(
            status_code=503, 
            detail="ConversationHandler未初始化"
        )
    
    try:
        state = server.conversation_handler.get_current_emotional_state()
        
        return EmotionalState(
            current_emotion=state.get('current_emotion', 'neutral'),
            emotion_intensity=state.get('emotion_intensity', 0.5),
            relationship_level=state.get('relationship_level', 1),
            last_updated=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取情感状态时发生错误: {str(e)}"
        )


@app.get("/api/chat/history", response_model=ChatHistory)
async def get_chat_history(
    limit: int = 50,
    offset: int = 0,
    reverse: bool = True
):
    """
    获取聊天历史记录
    
    Args:
        limit: 返回记录数量限制 (默认50)
        offset: 偏移量 (默认0)
        reverse: 是否倒序返回 (默认True，最新的在前)
    """
    try:
        total_count = len(server.chat_history)
        
        # 处理倒序
        history = list(reversed(server.chat_history)) if reverse else server.chat_history
        
        # 应用分页
        start_idx = offset
        end_idx = offset + limit
        
        items = history[start_idx:end_idx]
        has_more = end_idx < total_count
        
        return ChatHistory(
            items=items,
            total_count=total_count,
            has_more=has_more
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取聊天历史时发生错误: {str(e)}"
        )


@app.delete("/api/chat/history")
async def clear_chat_history():
    """
    清空聊天历史记录
    """
    try:
        server.chat_history.clear()
        return {"message": "聊天历史已清空", "timestamp": datetime.now()}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"清空聊天历史时发生错误: {str(e)}"
        )


@app.get("/api/health", response_model=HealthStatus)
async def health_check():
    """
    健康检查接口
    """
    uptime = time.time() - server.start_time
    
    services = {
        "conversation_handler": "healthy" if server.conversation_handler else "unhealthy",
        "chat_history": "healthy",
        "api_server": "healthy"
    }
    
    overall_status = "healthy" if all(status == "healthy" for status in services.values()) else "unhealthy"
    
    return HealthStatus(
        status=overall_status,
        timestamp=datetime.now(),
        version="1.0.0",
        uptime=uptime,
        services=services
    )


@app.get("/api/stats")
async def get_stats():
    """
    获取系统统计信息
    """
    try:
        uptime = time.time() - server.start_time
        
        return {
            "uptime_seconds": uptime,
            "uptime_formatted": str(timedelta(seconds=int(uptime))),
            "chat_history_count": len(server.chat_history),
            "max_history_size": server.max_history_size,
            "conversation_handler_status": "initialized" if server.conversation_handler else "not_initialized",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取统计信息时发生错误: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动情感陪伴AI Web API服务器...")
    print("📖 API文档: http://localhost:8000/docs")
    print("🌐 前端界面: http://localhost:8000/static/index.html")
    print("💡 健康检查: http://localhost:8000/api/health")
    
    uvicorn.run(
        "web_api.web_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
