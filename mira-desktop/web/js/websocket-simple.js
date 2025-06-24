/**
 * 简单WebSocket客户端
 * 为小梦情感陪伴系统提供WebSocket双向通信功能
 */

class SimpleWebSocketClient {
    constructor() {
        // 配置参数
        this.wsUrl = 'ws://localhost:8000/ws'
        this.maxReconnectAttempts = 5
        this.reconnectInterval = 3000 // 3秒
        this.heartbeatInterval = 30000 // 30秒心跳
        
        // 状态管理
        this.ws = null
        this.connectionState = 'disconnected' // disconnected, connecting, connected
        this.reconnectAttempts = 0
        this.heartbeatTimer = null
        this.reconnectTimer = null
        
        // 事件回调
        this.onMessage = null
        this.onConnectionChange = null
        
        // 自动连接
        this.connect()
        
        console.log('🔌 WebSocket客户端初始化完成')
    }
    
    /**
     * 建立WebSocket连接
     */
    connect() {
        if (this.connectionState === 'connecting' || this.connectionState === 'connected') {
            return
        }
        
        this.setConnectionState('connecting')
        
        try {
            this.ws = new WebSocket(this.wsUrl)
            
            this.ws.onopen = () => {
                console.log('✅ WebSocket连接成功')
                this.setConnectionState('connected')
                this.reconnectAttempts = 0
                this.startHeartbeat()
            }
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data)
                    this.handleMessage(data)
                } catch (error) {
                    console.error('WebSocket消息解析失败:', error)
                }
            }
            
            this.ws.onclose = (event) => {
                console.log('❌ WebSocket连接关闭:', event.code, event.reason)
                this.setConnectionState('disconnected')
                this.stopHeartbeat()
                
                // 如果不是主动关闭，尝试重连
                if (event.code !== 1000) {
                    this.scheduleReconnect()
                }
            }
            
            this.ws.onerror = (error) => {
                console.error('❌ WebSocket连接错误:', error)
                this.setConnectionState('disconnected')
            }
            
        } catch (error) {
            console.error('WebSocket连接失败:', error)
            this.setConnectionState('disconnected')
            this.scheduleReconnect()
        }
    }
    
    /**
     * 关闭WebSocket连接
     */
    disconnect() {
        this.stopHeartbeat()
        this.clearReconnectTimer()
        
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.close(1000, 'Client disconnect')
        }
        
        this.setConnectionState('disconnected')
    }
    
    /**
     * 发送消息
     */
    sendMessage(type, data = null) {
        if (this.connectionState !== 'connected') {
            console.warn('WebSocket未连接，无法发送消息')
            return false
        }
        
        try {
            const message = {
                type: type,
                data: data,
                timestamp: Date.now()
            }
            
            this.ws.send(JSON.stringify(message))
            return true
        } catch (error) {
            console.error('发送WebSocket消息失败:', error)
            return false
        }
    }
    
    /**
     * 发送聊天消息
     */
    sendChatMessage(content) {
        return this.sendMessage('chat', content)
    }
    
    /**
     * 发送心跳
     */
    sendHeartbeat() {
        return this.sendMessage('ping')
    }
    
    /**
     * 处理接收到的消息
     */
    handleMessage(data) {
        const { type, data: messageData, timestamp } = data
        
        switch (type) {
            case 'chat_response':
                // 聊天回复
                if (this.onMessage) {
                    this.onMessage({
                        type: 'chat_response',
                        response: messageData.response,
                        emotional_state: messageData.emotional_state,
                        processing_time: messageData.processing_time,
                        commands: messageData.commands
                    })
                }
                break
                
            case 'proactive_chat':
                // 主动消息
                if (this.onMessage) {
                    this.onMessage({
                        type: 'proactive_chat',
                        message: messageData.message,
                        emotional_state: messageData.emotional_state
                    })
                }
                break
                
            case 'pong':
                // 心跳回复
                console.log('💓 收到心跳回复')
                break
                
            case 'error':
                // 错误消息
                console.error('服务器错误:', messageData)
                break
                
            default:
                console.warn('未知消息类型:', type, messageData)
        }
    }
    
    /**
     * 设置连接状态
     */
    setConnectionState(state) {
        if (this.connectionState !== state) {
            const oldState = this.connectionState
            this.connectionState = state
            
            console.log(`🔄 连接状态变化: ${oldState} -> ${state}`)
            
            // 更新UI显示
            this.updateConnectionUI()
            
            // 触发状态变化回调
            if (this.onConnectionChange) {
                this.onConnectionChange(state, oldState)
            }
        }
    }
    
    /**
     * 更新连接状态UI
     */
    updateConnectionUI() {
        const statusIndicator = document.getElementById('statusIndicator')
        const statusText = document.getElementById('statusText')
        
        if (!statusIndicator || !statusText) return
        
        // 清除所有状态类
        statusIndicator.className = 'status-indicator'
        
        switch (this.connectionState) {
            case 'connected':
                statusIndicator.classList.add('connected')
                statusText.textContent = 'WebSocket已连接'
                break
            case 'connecting':
                statusIndicator.classList.add('connecting')
                statusText.textContent = '连接中...'
                break
            case 'disconnected':
                statusIndicator.classList.add('disconnected')
                statusText.textContent = '使用HTTP模式'
                break
        }
    }
    
    /**
     * 开始心跳
     */
    startHeartbeat() {
        this.stopHeartbeat()
        
        this.heartbeatTimer = setInterval(() => {
            if (this.connectionState === 'connected') {
                this.sendHeartbeat()
            }
        }, this.heartbeatInterval)
    }
    
    /**
     * 停止心跳
     */
    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer)
            this.heartbeatTimer = null
        }
    }
    
    /**
     * 计划重连
     */
    scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.warn(`⚠️ 重连次数已达上限(${this.maxReconnectAttempts})，停止重连`)
            return
        }
        
        this.clearReconnectTimer()
        
        this.reconnectAttempts++
        const delay = this.reconnectInterval * Math.pow(1.5, this.reconnectAttempts - 1) // 指数退避
        
        console.log(`🔄 ${delay}ms后尝试第${this.reconnectAttempts}次重连...`)
        
        this.reconnectTimer = setTimeout(() => {
            this.connect()
        }, delay)
    }
    
    /**
     * 清除重连定时器
     */
    clearReconnectTimer() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer)
            this.reconnectTimer = null
        }
    }
    
    /**
     * 检查是否已连接
     */
    isConnected() {
        return this.connectionState === 'connected'
    }
    
    /**
     * 获取连接状态
     */
    getConnectionState() {
        return this.connectionState
    }
    
    /**
     * 获取连接统计信息
     */
    getStats() {
        return {
            connectionState: this.connectionState,
            reconnectAttempts: this.reconnectAttempts,
            maxReconnectAttempts: this.maxReconnectAttempts,
            heartbeatInterval: this.heartbeatInterval,
            wsUrl: this.wsUrl
        }
    }
}

// 为了调试方便，将类暴露到全局
window.SimpleWebSocketClient = SimpleWebSocketClient

console.log('📡 WebSocket客户端模块加载完成')
