/**
 * 小梦情感陪伴 - 聊天前端脚本
 * 实现基础聊天功能、表情选择、自适应输入等
 */

class EmotionalChatApp {
    constructor() {
        // 检测运行环境
        this.isElectron = typeof window.electronAPI !== 'undefined'
        this.config = null
          console.log(`🌐 运行环境: ${this.isElectron ? 'Electron桌面客户端' : '浏览器'}`)
        
        // 初始化视觉效果处理器
        this.visualEffects = new VisualEffectsProcessor()
        
        // 初始化WebSocket客户端
        this.wsClient = null
        
        this.init()
        this.bindEvents()
        this.setupAutoResize()
        this.setupTypingEffect()
        
        // 根据环境初始化
        if (this.isElectron) {
            this.initElectronMode()
        } else {
            this.initBrowserMode()
        }

        this.bindTitlebarEvents()
    }

    async initElectronMode() {
        try {
            // 获取配置
            this.config = await window.electronAPI.getConfig()
            console.log('✅ 桌面端配置已加载:', this.config)
            
            // 使用配置中的API地址
            this.apiBaseUrl = this.config.apiBaseUrl || 'http://localhost:8000'
            
            // 监听配置变化
            window.electronAPI.onConfigChanged((data) => {
                console.log('配置已更新:', data)
                if (data.key === 'apiBaseUrl') {
                    this.apiBaseUrl = data.value
                    console.log('API地址已更新为:', this.apiBaseUrl)
                }
            })
            
        } catch (error) {
            console.error('❌ 初始化桌面端模式失败:', error)
            this.apiBaseUrl = 'http://localhost:8000'
        }
        
        this.initializeAPI()
    }

    initBrowserMode() {
        // 浏览器环境使用默认配置
        this.apiConfig = window.API_CONFIG || {
            baseUrl: 'http://localhost:8000',
            timeout: 10000
        }
        this.apiBaseUrl = this.apiConfig.baseUrl
        console.log(`📡 API地址: ${this.apiBaseUrl}`)
        
        this.initializeAPI()
    }

    bindTitlebarEvents() {
    if (this.isElectron) {
        // 最小化按钮
        document.getElementById('minimizeBtn').addEventListener('click', () => {
            window.electronAPI.windowMinimize()
        })

        // 最大化/还原按钮
        document.getElementById('maximizeBtn').addEventListener('click', async () => {
            const isMaximized = await window.electronAPI.windowMaximize()
            const icon = document.getElementById('maximizeIcon')
            icon.className = isMaximized ? 'fas fa-clone' : 'fas fa-square'
        })

        // 关闭按钮
        document.getElementById('closeBtn').addEventListener('click', () => {
            window.electronAPI.windowClose()
        })

        // 初始化最大化按钮状态
        this.updateMaximizeButton()
    }
}

async updateMaximizeButton() {
    if (this.isElectron) {
        const isMaximized = await window.electronAPI.windowIsMaximized()
        const icon = document.getElementById('maximizeIcon')
        icon.className = isMaximized ? 'fas fa-clone' : 'fas fa-square'
    }
}    init() {
        // DOM 元素引用
        this.chatMessages = document.getElementById('chatMessages')
        this.messageInput = document.getElementById('messageInput')
        this.sendBtn = document.getElementById('sendBtn')
        this.emojiBtn = document.getElementById('emojiBtn')
        this.emojiPicker = document.getElementById('emojiPicker')
        this.loadingOverlay = document.getElementById('loadingOverlay')
        this.errorToast = document.getElementById('errorToast')
        this.emotionalStatus = document.getElementById('emotionalStatus')
        this.effectsToggleBtn = document.getElementById('effectsToggleBtn')
        
        // 应用状态
        this.isLoading = false
        this.emotionState = {
            emotion: 'happy',
            intensity: 0.8,
            relationshipLevel: 8
        }
        
        // API端点配置
        this.apiEndpoints = {
            chat: '/api/chat',
            emotionalState: '/api/emotional-state',
            health: '/api/health'        }
        
        console.log('✨ 小梦客户端初始化完成')
        
        // 延迟初始化WebSocket，确保其他组件已准备就绪
        setTimeout(() => {
            this.initWebSocket()
        }, 500)
    }

    async updateConfig(key, value) {
        if (this.isElectron) {
            try {
                await window.electronAPI.setConfig(key, value)
                console.log('配置已更新:', key, '=', value)
                return true
            } catch (error) {
                console.error('更新配置失败:', error)
                return false
            }
        }
        return false
    }

    bindEvents() {
        // 发送按钮点击
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        
        // 输入框键盘事件
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // 输入框内容变化
        this.messageInput.addEventListener('input', () => {
            this.updateCharCount();
            this.updateSendButton();
        });
        
        // 表情按钮点击
        this.emojiBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleEmojiPicker();
        });
        
        // 表情选择
        this.emojiPicker.addEventListener('click', (e) => {
            if (e.target.classList.contains('emoji-item')) {
                this.insertEmoji(e.target.textContent);
            }
        });
        
        // 点击其他地方关闭表情选择器
        document.addEventListener('click', (e) => {
            if (!this.emojiPicker.contains(e.target) && e.target !== this.emojiBtn) {
                this.hideEmojiPicker();
            }
        });
          // 头部按钮事件
        document.getElementById('settingsBtn').addEventListener('click', () => {
            if (this.isElectron) {
                this.openSettingsWindow()  // 桌面端打开设置窗口
            } else {
                window.open('settings.html', '_blank')  // 浏览器端打开设置页面
            }
        })
          document.getElementById('historyBtn').addEventListener('click', () => {
            this.showToast('聊天记录功能正在开发中...', 'info');
        });

        // 视觉效果开关按钮
        if (this.effectsToggleBtn) {
            this.effectsToggleBtn.addEventListener('click', () => {
                this.toggleVisualEffects();
            });
            this.updateEffectsToggleButton();
        }    }

    openSettingsWindow() {
        // 在Electron中打开设置窗口
        if (this.isElectron && window.electronAPI) {
            // 可以通过IPC让主进程打开设置窗口
            // 暂时使用当前窗口导航到设置页面
            window.location.href = 'settings.html'
        } else {
            // 备用方案：简单设置提示
            this.showSimpleSettingsPrompt()
        }
    }

    showSimpleSettingsPrompt() {
        const newUrl = prompt('请输入API服务器地址:', this.apiBaseUrl)
        if (newUrl && newUrl !== this.apiBaseUrl) {
            this.updateConfig('apiBaseUrl', newUrl)
            this.showToast('API地址已更新，重启应用后生效', 'success')
        }
    }

    setupAutoResize() {
        // 输入框自适应高度
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
        });
    }    setupTypingEffect() {
        // 为机器人消息添加打字效果的基础设置
        this.typingSpeed = 30; // 毫秒/字符
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isLoading) return;

        // 添加用户消息到界面
        this.addUserMessage(message);
        
        // 清空输入框
        this.messageInput.value = '';
        this.updateCharCount();
        this.updateSendButton();
        this.messageInput.style.height = 'auto';

        // 显示"正在输入"状态
        this.showTypingIndicator();

        try {
            // 优先使用WebSocket发送消息
            const webSocketSent = this.sendMessageViaWebSocket(message);
            
            if (webSocketSent) {
                console.log('📤 通过WebSocket发送消息:', message);
                // WebSocket发送成功，等待服务器回复
                // 回复将通过WebSocket消息处理器处理
                return;
            }
            
            // WebSocket不可用，降级到HTTP API
            console.log('📤 通过HTTP API发送消息:', message);
            const response = await this.callChatAPI(message);
            
            // 隐藏"正在输入"状态
            this.hideTypingIndicator();
            
            // 添加机器人回复
            await this.addBotMessage(response.reply, response.emotionalState);
            
            // 更新情感状态显示
            this.updateEmotionalStatus(response.emotionalState);
            
            // 处理视觉效果指令
            if (response.commands && response.commands.length > 0) {
                await this.processVisualCommands(response.commands);
            }
            
        } catch (error) {
            console.error('发送消息失败:', error);
            this.hideTypingIndicator();
            this.showErrorToast('消息发送失败，请稍后再试～');
            
            // 添加错误回复
            await this.addBotMessage('啊呀，我刚才走神了一下...能再说一遍吗？ 😅');
        }
    }

    addUserMessage(message) {
        const messageElement = this.createMessageElement('user', message);
        this.chatMessages.appendChild(messageElement);
        this.scrollToBottom();
    }

    async addBotMessage(message, emotionalState = null) {
        const messageElement = this.createMessageElement('bot', '');
        this.chatMessages.appendChild(messageElement);
        
        // 找到消息气泡元素
        const bubbleElement = messageElement.querySelector('.message-bubble');
        
        // 打字效果
        await this.typeMessage(bubbleElement, message);
        
        this.scrollToBottom();
    }

    createMessageElement(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
          if (type === 'user') {
            avatarDiv.innerHTML = '<i class="fas fa-user"></i>';
        } else {
            avatarDiv.innerHTML = '<img src="../assets/icon.png" alt="小梦头像" class="avatar-img">';
        }
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        
        // 处理换行
        const formattedContent = content.replace(/\n/g, '<br>');
        bubbleDiv.innerHTML = formattedContent;
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = this.getCurrentTime();
        
        contentDiv.appendChild(bubbleDiv);
        contentDiv.appendChild(timeDiv);
        
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        
        return messageDiv;
    }

    async typeMessage(element, message) {
        element.innerHTML = '';
        let currentText = '';
        
        for (let i = 0; i < message.length; i++) {
            currentText += message[i];
            element.innerHTML = currentText.replace(/\n/g, '<br>');
            this.scrollToBottom();
            
            // 在标点符号后稍作停顿
            const char = message[i];
            const delay = /[。！？.!?]/.test(char) ? this.typingSpeed * 3 : this.typingSpeed;
            
            await this.sleep(delay);
        }
    }    async callChatAPI(message) {
        try {
            // 调用真实的后端API
            const response = await fetch(`${this.apiBaseUrl}${this.apiEndpoints.chat}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    enable_timing: false
                })
            });

            if (!response.ok) {
                throw new Error(`API请求失败: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            
            // 转换API响应格式为前端期望的格式
            const result = {
                reply: data.response,
                emotionalState: {
                    emotion: data.emotional_state?.current_emotion || 'neutral',
                    intensity: data.emotional_state?.emotion_intensity || 0.5,
                    relationshipLevel: data.emotional_state?.relationship_level || 1
                },
                processingTime: data.processing_time,
                commands: data.commands || []  // 添加视觉效果指令
            };

            // 处理视觉效果指令
            if (result.commands && result.commands.length > 0) {
                console.log(`🎨 收到 ${result.commands.length} 个视觉效果指令`)
                this.processVisualCommands(result.commands)
            }

            return result;

        } catch (error) {
            console.error('API调用失败:', error);
            
            // 降级到模拟回复
            return this.getFallbackResponse(message);
        }
    }

    getFallbackResponse(message) {
        // 当API不可用时的降级回复
        const fallbackResponses = [
            {
                reply: "啊呀，我刚才走神了一下...能再说一遍吗？ 😅",
                emotionalState: { emotion: 'apologetic', intensity: 0.6, relationshipLevel: 7 }
            },
            {
                reply: "抱歉，我现在有点反应迟钝，不过我还是很想听你说话呢～ 💕",
                emotionalState: { emotion: 'caring', intensity: 0.7, relationshipLevel: 8 }
            },
            {
                reply: "嗯...让我想想怎么回答你...（小梦正在努力思考中）🤔",
                emotionalState: { emotion: 'thinking', intensity: 0.5, relationshipLevel: 7 }
            }
        ];
        
        return fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)];
    }

    updateEmotionalStatus(emotionalState) {
        if (!emotionalState) return;
        
        this.emotionState = { ...this.emotionState, ...emotionalState };
        
        const emotionMap = {
            'happy': '心情愉悦',
            'joyful': '欣喜若狂',
            'caring': '温柔关怀',
            'curious': '好奇专注',
            'understanding': '理解共情',
            'nostalgic': '怀念温馨',
            'excited': '兴奋期待',
            'neutral': '平静淡然'
        };
        
        const emotionText = emotionMap[this.emotionState.emotion] || '心情不错';
        this.emotionalStatus.textContent = `${emotionText} | 亲密度 ${this.emotionState.relationshipLevel}/10`;
    }

    updateCharCount() {
        const currentLength = this.messageInput.value.length;
        const maxLength = 1000;
        
        const charCountElement = document.querySelector('.char-count');
        charCountElement.textContent = `${currentLength}/${maxLength}`;
        
        // 接近限制时改变颜色
        if (currentLength > maxLength * 0.9) {
            charCountElement.style.color = '#ff6b6b';
        } else {
            charCountElement.style.color = '#666';
        }
    }

    updateSendButton() {
        const hasContent = this.messageInput.value.trim().length > 0;
        this.sendBtn.disabled = !hasContent || this.isLoading;
    }

    toggleEmojiPicker() {
        this.emojiPicker.classList.toggle('show');
    }

    hideEmojiPicker() {
        this.emojiPicker.classList.remove('show');
    }

    insertEmoji(emoji) {
        const currentValue = this.messageInput.value;
        const cursorPos = this.messageInput.selectionStart;
        
        const newValue = currentValue.substring(0, cursorPos) + emoji + currentValue.substring(cursorPos);
        this.messageInput.value = newValue;
        
        // 更新光标位置
        this.messageInput.setSelectionRange(cursorPos + emoji.length, cursorPos + emoji.length);
        this.messageInput.focus();
        
        this.updateCharCount();
        this.updateSendButton();
        this.hideEmojiPicker();
    }    showTypingIndicator() {
        this.isLoading = true;
        this.updateSendButton();
        
        // 创建"正在输入"消息元素
        this.typingMessage = this.createMessageElement('bot', '');
        this.typingMessage.classList.add('typing-indicator');
        
        const bubbleElement = this.typingMessage.querySelector('.message-bubble');
        bubbleElement.innerHTML = `
            <div class="typing-dots">
                <span class="typing-text">小梦正在输入</span>
                <div class="dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(this.typingMessage);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.isLoading = false;
        this.updateSendButton();
        
        // 移除"正在输入"消息
        if (this.typingMessage && this.typingMessage.parentNode) {
            this.typingMessage.parentNode.removeChild(this.typingMessage);
            this.typingMessage = null;
        }
    }

    showErrorToast(message) {
        const errorMessage = this.errorToast.querySelector('.error-message');
        errorMessage.textContent = message;
        this.errorToast.classList.add('show');
        
        // 3秒后自动隐藏
        setTimeout(() => {
            this.errorToast.classList.remove('show');
        }, 3000);
    }

    async checkAPIHealth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}${this.apiEndpoints.health}`, {
                method: 'GET',
                timeout: 5000
            });

            if (response.ok) {
                const healthData = await response.json();
                console.log('✅ API服务器连接正常:', healthData);
                return true;
            } else {
                console.warn('⚠️ API服务器响应异常:', response.status);
                return false;
            }
        } catch (error) {
            console.warn('⚠️ API服务器连接失败:', error.message);
            return false;
        }
    }

    async loadInitialEmotionalState() {
        try {
            const response = await fetch(`${this.apiBaseUrl}${this.apiEndpoints.emotionalState}`, {
                method: 'GET'
            });

            if (response.ok) {
                const stateData = await response.json();
                this.updateEmotionalStatus({
                    emotion: stateData.current_emotion,
                    intensity: stateData.emotional_intensity,
                    relationshipLevel: stateData.relationship_level
                });
                console.log('✅ 初始情感状态加载成功:', stateData);
            }
        } catch (error) {
            console.warn('⚠️ 加载初始情感状态失败:', error);
        }
    }

    async initializeAPI() {        // 检查API健康状态
        const isHealthy = await this.checkAPIHealth();
        
        if (isHealthy) {
            // 加载初始情感状态
            await this.loadInitialEmotionalState();
            
            // 显示连接成功提示
            setTimeout(() => {
                const wsStatus = this.wsClient ? this.wsClient.getConnectionState() : 'disconnected';
                if (wsStatus === 'connected') {
                    this.showToast('💖 小梦已准备好和您聊天啦～ (WebSocket)', 'success');
                } else {
                    this.showToast('💖 小梦已准备好和您聊天啦～ (HTTP)', 'success');
                }
            }, 1500);
        } else {
            // 显示离线模式提示
            setTimeout(() => {
                this.showToast('⚠️ 离线模式：小梦可能反应会慢一些哦', 'warning');
            }, 1500);
        }
    }

    showToast(message, type = 'info') {
        // 创建toast元素
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        // 添加样式
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#4CAF50' : type === 'warning' ? '#ff9800' : '#2196F3'};
            color: white;
            padding: 12px 20px;
            border-radius: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
            font-size: 14px;
            font-weight: 500;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
        `;
        
        document.body.appendChild(toast);
        
        // 显示动画
        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(0)';
        }, 10);
        
        // 自动隐藏
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => document.body.removeChild(toast), 300);
        }, 3000);
    }

    getCurrentTime() {
        const now = new Date();
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
    }

    scrollToBottom() {
        // 使用 setTimeout 确保 DOM 更新完成后再滚动
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 10);
    }    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // ==================== 视觉效果相关方法 ====================

    /**
     * 处理视觉效果指令队列
     */    async processVisualCommands(commands) {
        if (!commands || commands.length === 0) return;

        try {
            // 按时间排序指令（如果有时间戳）
            const sortedCommands = commands.sort((a, b) => {
                if (a.timestamp && b.timestamp) {
                    return new Date(a.timestamp) - new Date(b.timestamp);
                }
                return 0;
            });

            // 分离持久效果和临时效果
            const persistentCommands = sortedCommands.filter(cmd => cmd.effect_type === 'persistent');
            const temporaryCommands = sortedCommands.filter(cmd => cmd.effect_type === 'temporary');

            // 先执行持久效果（只保留最后一个）
            if (persistentCommands.length > 0) {
                const lastPersistentCommand = persistentCommands[persistentCommands.length - 1];
                await this.visualEffects.executeVisualCommand(lastPersistentCommand);
                this.showVisualEffectNotification(lastPersistentCommand);
            }

            // 然后依次执行临时效果
            for (const command of temporaryCommands) {
                await this.visualEffects.executeVisualCommand(command);
                this.showVisualEffectNotification(command);
                // 临时效果之间稍微间隔
                if (temporaryCommands.length > 1) {
                    await this.sleep(200);
                }
            }

        } catch (error) {
            console.error('处理视觉效果指令时发生错误:', error);
            this.showToast('视觉效果执行失败', 'error');
        }
    }

    /**
     * 显示视觉效果触发通知
     */
    showVisualEffectNotification(command) {
        if (!command || !command.effect_description) return;
        
        const { effect_description, intensity, effect_type } = command;
        const intensityText = intensity ? `${(intensity * 100).toFixed(0)}%` : '50%';
        const typeText = effect_type === 'persistent' ? '主题' : '动画';
        
        // 创建更简洁的提示消息
        const message = `✨ ${effect_description} (${typeText}, 强度: ${intensityText})`;
        
        // 显示为轻量级提示，不打断用户
        this.showSubtleNotification(message);
    }    /**
     * 显示轻量级通知（比toast更不显眼）
     */
    showSubtleNotification(message) {
        // 检查是否已有相同类型的通知，避免重复
        const existingNotifications = document.querySelectorAll('.visual-effect-notification');
        
        // 如果已有超过3个通知，移除最旧的
        if (existingNotifications.length >= 3) {
            const oldestNotification = existingNotifications[0];
            if (oldestNotification.parentNode) {
                oldestNotification.style.opacity = '0';
                oldestNotification.style.transform = 'translateY(-10px)';
                setTimeout(() => {
                    if (oldestNotification.parentNode) {
                        document.body.removeChild(oldestNotification);
                    }
                }, 300);
            }
        }
        
        // 创建一个轻量级的通知元素
        const notification = document.createElement('div');
        notification.className = 'visual-effect-notification';
        notification.textContent = message;
        
        // 计算当前通知的位置偏移
        const currentNotifications = document.querySelectorAll('.visual-effect-notification');
        const topOffset = 80 + (currentNotifications.length * 45);
        
        // 添加样式
        notification.style.cssText = `
            position: fixed;
            top: ${topOffset}px;
            right: 20px;
            background: rgba(74, 144, 226, 0.1);
            color: #4a90e2;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            -webkit-backdrop-filter: blur(10px);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(74, 144, 226, 0.3);
            z-index: 1000;
            opacity: 0;
            transition: all 0.3s ease;
            pointer-events: none;
            max-width: 250px;
            word-wrap: break-word;
            transform: translateY(-10px);
        `;
        
        document.body.appendChild(notification);
        
        // 淡入动画
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateY(0)';
        }, 10);
        
        // 3秒后淡出并移除
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                if (notification.parentNode) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    /**
     * 切换视觉效果开关
     */
    toggleVisualEffects() {
        const currentState = this.visualEffects.isEffectsEnabledStatus();
        this.visualEffects.setEffectsEnabled(!currentState);
        this.updateEffectsToggleButton();
        
        const status = this.visualEffects.isEffectsEnabledStatus() ? '已开启' : '已关闭';
        this.showToast(`视觉效果${status}`, 'info');
    }

    /**
     * 更新视觉效果开关按钮状态
     */
    updateEffectsToggleButton() {
        if (!this.effectsToggleBtn) return;

        const isEnabled = this.visualEffects.isEffectsEnabledStatus();
        const icon = this.effectsToggleBtn.querySelector('i');
        
        if (isEnabled) {
            icon.className = 'fas fa-magic';
            this.effectsToggleBtn.style.color = '#ff6b6b';
            this.effectsToggleBtn.title = '关闭视觉效果';
        } else {
            icon.className = 'fas fa-magic';
            this.effectsToggleBtn.style.color = '#999';
            this.effectsToggleBtn.title = '开启视觉效果';
        }
    }

    /**
     * 测试视觉效果（调试用）
     */
    testVisualEffect(effectName, intensity = 0.7) {
        if (this.visualEffects) {
            this.visualEffects.testEffect(effectName, intensity);
            console.log(`🧪 测试视觉效果: ${effectName}, 强度: ${intensity}`);
        }
    }

    // ==================== WebSocket相关方法 ====================

    /**
     * 初始化WebSocket连接
     */
    initWebSocket() {
        try {
            // 创建WebSocket客户端实例
            this.wsClient = new SimpleWebSocketClient()
            
            // 设置消息处理器
            this.wsClient.onMessage = (data) => {
                this.handleWebSocketMessage(data)
            }
            
            // 设置连接状态变化回调
            this.wsClient.onConnectionChange = (newState, oldState) => {
                this.handleConnectionStateChange(newState, oldState)
            }
            
            console.log('✅ WebSocket客户端初始化成功')
            
        } catch (error) {
            console.error('❌ WebSocket客户端初始化失败:', error)
            this.showToast('WebSocket初始化失败，将使用HTTP模式', 'warning')
        }
    }

    /**
     * 处理WebSocket消息
     */
    handleWebSocketMessage(data) {
        const { type } = data
        
        switch (type) {
            case 'chat_response':
                // 处理聊天回复
                this.handleWebSocketChatResponse(data)
                break
                
            case 'proactive_chat':
                // 处理主动消息
                this.handleProactiveMessage(data)
                break
                
            default:
                console.log('收到WebSocket消息:', data)
        }
    }

    /**
     * 处理WebSocket聊天回复
     */
    async handleWebSocketChatResponse(data) {
        const { response, emotional_state, commands } = data
        
        // 隐藏"正在输入"状态
        this.hideTypingIndicator()
        
        // 添加AI回复到界面
        await this.addBotMessage(response, emotional_state)
        
        // 更新情感状态
        if (emotional_state) {
            this.updateEmotionalStatus({
                emotion: emotional_state.current_emotion,
                intensity: emotional_state.emotion_intensity,
                relationshipLevel: emotional_state.relationship_level
            })
        }
        
        // 处理视觉效果指令
        if (commands && commands.length > 0) {
            await this.processVisualCommands(commands)
        }
    }

    /**
     * 处理主动消息
     */
    async handleProactiveMessage(data) {
        const { message, emotional_state } = data
        
        console.log('📢 收到主动消息:', message)
        
        // 添加主动消息到界面
        await this.addBotMessage(message, emotional_state)
        
        // 更新情感状态
        if (emotional_state) {
            this.updateEmotionalStatus({
                emotion: emotional_state.current_emotion,
                intensity: emotional_state.emotion_intensity,
                relationshipLevel: emotional_state.relationship_level
            })
        }
        
        // 显示提示
        this.showToast('收到小梦的主动消息 💕', 'info')
    }

    /**
     * 处理连接状态变化
     */
    handleConnectionStateChange(newState, oldState) {
        console.log(`🔄 连接状态变化: ${oldState} -> ${newState}`)
        
        switch (newState) {
            case 'connected':
                this.showToast('WebSocket连接成功', 'success')
                break
            case 'disconnected':
                if (oldState === 'connected') {
                    this.showToast('连接断开，已切换到HTTP模式', 'warning')
                }
                break
            case 'connecting':
                // 不显示连接中的提示，避免过于频繁
                break
        }
    }

    /**
     * 通过WebSocket发送聊天消息
     */
    sendMessageViaWebSocket(message) {
        if (this.wsClient && this.wsClient.isConnected()) {
            return this.wsClient.sendChatMessage(message)
        }
        return false
    }

    /**
     * 获取WebSocket连接状态
     */
    getWebSocketStatus() {
        if (this.wsClient) {
            return this.wsClient.getStats()
        }
        return null
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    // 添加一些页面加载动画
    document.body.style.opacity = '0'
    document.body.style.transition = 'opacity 0.5s ease-in-out'
    
    setTimeout(() => {
        document.body.style.opacity = '1'
        // 初始化聊天应用
        window.chatApp = new EmotionalChatApp()
    }, 100)
})
