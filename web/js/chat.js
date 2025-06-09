/**
 * 小梦情感陪伴 - 聊天前端脚本
 * 实现基础聊天功能、表情选择、自适应输入等
 */

class EmotionalChatApp {
    constructor() {
        this.init();
        this.bindEvents();
        this.setupAutoResize();
        this.setupTypingEffect();
    }

    init() {
        // DOM 元素引用
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.emojiBtn = document.getElementById('emojiBtn');
        this.emojiPicker = document.getElementById('emojiPicker');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.errorToast = document.getElementById('errorToast');
        this.emotionalStatus = document.getElementById('emotionalStatus');
        
        // 应用状态
        this.isLoading = false;
        this.emotionState = {
            emotion: 'happy',
            intensity: 0.8,
            relationshipLevel: 8
        };
          // API 配置
        this.apiBaseUrl = 'http://localhost:8000';
        this.apiEndpoints = {
            chat: '/api/chat',
            emotionalState: '/api/emotional-state',
            health: '/api/health'
        };
        
        console.log('小梦情感陪伴系统初始化完成 ✨');
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
        
        // 头部按钮事件（暂时提示功能待开发）
        document.getElementById('settingsBtn').addEventListener('click', () => {
            this.showToast('设置功能正在开发中...', 'info');
        });
        
        document.getElementById('historyBtn').addEventListener('click', () => {
            this.showToast('聊天记录功能正在开发中...', 'info');
        });
    }

    setupAutoResize() {
        // 输入框自适应高度
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
        });
    }

    setupTypingEffect() {
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

        // 显示加载状态
        this.showLoading();

        try {
            // 调用后端API（暂时模拟）
            const response = await this.callChatAPI(message);
            
            // 隐藏加载状态
            this.hideLoading();
            
            // 添加机器人回复
            await this.addBotMessage(response.reply, response.emotionalState);
            
            // 更新情感状态显示
            this.updateEmotionalStatus(response.emotionalState);
            
        } catch (error) {
            console.error('发送消息失败:', error);
            this.hideLoading();
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
            avatarDiv.innerHTML = '<i class="fas fa-heart"></i>';
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
            return {
                reply: data.response,
                emotionalState: {
                    emotion: data.emotional_state?.current_emotion || 'neutral',
                    intensity: data.emotional_state?.emotion_intensity || 0.5,
                    relationshipLevel: data.emotional_state?.relationship_level || 1
                },
                processingTime: data.processing_time
            };

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
    }

    showLoading() {
        this.isLoading = true;
        this.loadingOverlay.classList.add('show');
        this.updateSendButton();
    }

    hideLoading() {
        this.isLoading = false;
        this.loadingOverlay.classList.remove('show');
        this.updateSendButton();
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

    async initializeAPI() {
        // 检查API健康状态
        const isHealthy = await this.checkAPIHealth();
        
        if (isHealthy) {
            // 加载初始情感状态
            await this.loadInitialEmotionalState();
            
            // 显示连接成功提示
            setTimeout(() => {
                this.showToast('💖 小梦已准备好和您聊天啦～', 'success');
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
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    // 添加一些页面加载动画
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.5s ease-in-out';
    
    setTimeout(() => {
        document.body.style.opacity = '1';
        
        // 初始化聊天应用
        window.chatApp = new EmotionalChatApp();
        
        // 初始化API连接
        window.chatApp.initializeAPI();
        
    }, 100);
});

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EmotionalChatApp;
}
