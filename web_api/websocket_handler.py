"""
WebSocket处理器模块
简化的WebSocket连接管理和消息处理
"""

import json
import asyncio
import time
import random
from datetime import datetime, timedelta
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Optional
import logging

# 配置日志
logger = logging.getLogger(__name__)


class SimpleWebSocketManager:
    """简单的WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.max_connections = 10  # 最大连接数限制
        self.message_rate_limit: Dict[str, List[float]] = {}  # 消息频率限制
        
    async def connect(self, websocket: WebSocket) -> bool:
        """建立WebSocket连接"""
        try:
            # 检查连接数限制
            if len(self.active_connections) >= self.max_connections:
                await websocket.close(code=1008, reason="Too many connections")
                logger.warning(f"连接被拒绝：超过最大连接数限制 ({self.max_connections})")
                return False
                
            await websocket.accept()
            self.active_connections.append(websocket)
            logger.info(f"WebSocket连接建立，当前连接数: {len(self.active_connections)}")
            return True
            
        except Exception as e:
            logger.error(f"WebSocket连接失败: {e}")
            return False
    
    def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket连接断开，当前连接数: {len(self.active_connections)}")
    
    async def send_message(self, websocket: WebSocket, message: dict) -> bool:
        """向指定WebSocket发送消息"""
        try:
            await websocket.send_text(json.dumps(message, ensure_ascii=False))
            return True
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            # 如果发送失败，从连接列表中移除
            self.disconnect(websocket)
            return False
    
    async def broadcast(self, message: dict) -> int:
        """向所有连接广播消息"""
        if not self.active_connections:
            logger.debug("没有活跃连接，跳过广播")
            return 0
            
        success_count = 0
        # 复制连接列表，避免在迭代过程中修改
        connections_copy = self.active_connections.copy()
        
        for connection in connections_copy:
            if await self.send_message(connection, message):
                success_count += 1
                
        logger.info(f"广播消息完成，成功发送到 {success_count}/{len(connections_copy)} 个连接")
        return success_count
    
    def validate_message(self, message_text: str) -> Optional[dict]:
        """验证消息格式"""
        try:
            # 检查消息大小
            if len(message_text) > 10000:  # 10KB限制
                logger.warning("消息过大，拒绝处理")
                return None
                
            message = json.loads(message_text)
            
            # 检查必需字段
            if not isinstance(message.get("type"), str):
                logger.warning("消息格式错误：缺少type字段")
                return None
            
            return message
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return None
        except Exception as e:
            logger.error(f"消息验证失败: {e}")
            return None
    
    def get_connection_count(self) -> int:
        """获取当前连接数"""
        return len(self.active_connections)


class ProactiveMessageService:
    """主动消息服务"""
    
    def __init__(self, ws_manager: SimpleWebSocketManager):
        self.ws_manager = ws_manager
        self.is_running = False
        self.last_message_time = datetime.now()
        self.check_interval = 300  # 每5分钟检查一次
        self.idle_threshold = 30  # 30分钟无消息后发送主动关怀
        
        # 预定义的主动关怀消息
        self.proactive_messages = [
            "你在忙什么呢？记得休息一下哦～ 💕",
            "好久没有聊天了，想你了呢 🥺",
            "喝水了吗？要注意保持水分哦～ 💧",
            "最近感觉怎么样？有什么想分享的吗？ ✨",
            "在做什么有趣的事情吗？分享给我听听吧 😊",
            "记得按时吃饭哦，身体健康最重要 🍚",
            "今天心情怎么样？我一直都在这里陪着你 💖",
            "累了的话就休息一下，我会在这里等你 😴"
        ]
    
    async def start(self):
        """启动主动消息服务"""
        if self.is_running:
            logger.warning("主动消息服务已经在运行")
            return
            
        self.is_running = True
        logger.info("主动消息服务启动")
        
        # 创建后台任务
        asyncio.create_task(self._proactive_loop())
    
    async def stop(self):
        """停止主动消息服务"""
        self.is_running = False
        logger.info("主动消息服务停止")
    
    async def _proactive_loop(self):
        """主动消息检查循环"""
        while self.is_running:
            try:
                await asyncio.sleep(self.check_interval)
                
                # 检查是否需要发送主动消息
                if (self.ws_manager.get_connection_count() > 0 and 
                    self._should_send_proactive_message()):
                    
                    await self._send_proactive_message()
                    
            except Exception as e:
                logger.error(f"主动消息循环异常: {e}")
                await asyncio.sleep(60)  # 发生错误时等待1分钟再继续
    
    def _should_send_proactive_message(self) -> bool:
        """判断是否应该发送主动消息"""
        time_since_last = datetime.now() - self.last_message_time
        return time_since_last > timedelta(minutes=self.idle_threshold)
    
    async def _send_proactive_message(self):
        """发送主动关怀消息"""
        try:
            message = random.choice(self.proactive_messages)
            
            proactive_data = {
                "type": "proactive_chat",
                "data": message,
                "timestamp": time.time()
            }
            
            success_count = await self.ws_manager.broadcast(proactive_data)
            
            if success_count > 0:
                logger.info(f"发送主动关怀消息: {message}")
                self.update_last_message_time()
            else:
                logger.warning("主动消息发送失败，没有活跃连接")
                
        except Exception as e:
            logger.error(f"发送主动消息失败: {e}")
    
    def update_last_message_time(self):
        """更新最后消息时间"""
        self.last_message_time = datetime.now()
        logger.debug(f"更新最后消息时间: {self.last_message_time}")


# 创建全局实例
ws_manager = SimpleWebSocketManager()
proactive_service = ProactiveMessageService(ws_manager)


# 启动主动消息服务的函数
async def start_proactive_service():
    """启动主动消息服务"""
    await proactive_service.start()


async def stop_proactive_service():
    """停止主动消息服务"""
    await proactive_service.stop()
