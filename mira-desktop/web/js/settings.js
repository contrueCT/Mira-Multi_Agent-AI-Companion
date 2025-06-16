/**
 * 设置界面JavaScript
 * 管理配置的前端逻辑
 */

class SettingsManager {
    constructor() {
        this.isElectron = typeof window.electronAPI !== 'undefined'
        this.apiBaseUrl = this.isElectron ? 'http://localhost:8000' : 'http://localhost:8000'
        
        // 当前编辑的LLM配置索引
        this.editingLLMIndex = -1
        
        this.init()
    }
      async init() {
        this.bindEvents()
        this.bindTitlebarEvents()
        await this.loadAllConfigs()
        this.initializeTabs()
    }
    
    bindEvents() {
        // 标签页切换
        document.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const tabId = e.currentTarget.dataset.tab
                this.switchTab(tabId)
            })
        })
        
        // LLM配置相关事件
        document.getElementById('addLLMBtn').addEventListener('click', () => {
            this.openLLMModal()
        })
        
        document.getElementById('saveModalBtn').addEventListener('click', () => {
            this.saveLLMConfig()
        })
        
        document.getElementById('cancelModalBtn').addEventListener('click', () => {
            this.closeLLMModal()
        })
        
        document.getElementById('modalCloseBtn').addEventListener('click', () => {
            this.closeLLMModal()
        })
        
        document.getElementById('testConnectionBtn').addEventListener('click', () => {
            this.testLLMConnection()
        })
        
        // 密码显示切换
        document.getElementById('toggleApiKey').addEventListener('click', () => {
            this.togglePasswordVisibility('apiKeyInput')
        })
        
        // 环境配置表单
        document.getElementById('environmentForm').addEventListener('submit', (e) => {
            e.preventDefault()
            this.saveEnvironmentConfig()
        })
        
        document.getElementById('resetEnvironmentBtn').addEventListener('click', () => {
            this.resetEnvironmentConfig()
        })
        
        // 用户偏好表单
        document.getElementById('preferencesForm').addEventListener('submit', (e) => {
            e.preventDefault()
            this.saveUserPreferences()
        })
        
        document.getElementById('resetPreferencesBtn').addEventListener('click', () => {
            this.resetUserPreferences()
        })
        
        // 备份恢复
        document.getElementById('createBackupBtn').addEventListener('click', () => {
            this.createBackup()
        })
        
        document.getElementById('restoreBackupBtn').addEventListener('click', () => {
            document.getElementById('restoreFileInput').click()
        })
        
        document.getElementById('restoreFileInput').addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.restoreBackup(e.target.files[0])
            }
        })        // 模态框外点击关闭
        document.getElementById('llmConfigModal').addEventListener('click', (e) => {
            if (e.target.id === 'llmConfigModal') {
                this.closeLLMModal()
            }
        })
        
        // 返回主界面按钮
        document.getElementById('returnToMainBtn').addEventListener('click', () => {
            this.returnToMain()
        })
    }
    
    /**
     * 绑定标题栏窗口控制按钮事件
     */
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
    }    /**
     * 更新最大化按钮的图标状态
     */
    async updateMaximizeButton() {
        if (this.isElectron) {
            const isMaximized = await window.electronAPI.windowIsMaximized()
            const icon = document.getElementById('maximizeIcon')
            icon.className = isMaximized ? 'fas fa-clone' : 'fas fa-square'
        }
    }
    
    /**
     * 返回主界面
     */
    returnToMain() {
        if (this.isElectron) {
            // 在Electron环境下，导航到主界面
            window.location.href = 'index.html'
        } else {
            // 在浏览器环境下，可以使用不同的导航方式
            window.location.href = 'index.html'
        }
    }
    
    initializeTabs() {
        // 默认显示第一个标签页
        this.switchTab('llm')
    }
    
    switchTab(tabId) {
        // 更新菜单项状态
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active')
        })
        document.querySelector(`[data-tab="${tabId}"]`).classList.add('active')
        
        // 更新标签页内容
        document.querySelectorAll('.settings-tab').forEach(tab => {
            tab.classList.remove('active')
        })
        document.getElementById(`${tabId}-tab`).classList.add('active')
    }
    
    async loadAllConfigs() {
        try {
            this.showLoading('正在加载配置...')
            
            // 并行加载所有配置
            const [llmConfigs, envConfig, preferences] = await Promise.all([
                this.loadLLMConfigs(),
                this.loadEnvironmentConfig(),
                this.loadUserPreferences()
            ])
            
            this.hideLoading()
            this.showToast('配置加载完成', 'success')
        } catch (error) {
            this.hideLoading()
            this.showToast('加载配置失败: ' + error.message, 'error')
        }
    }
    
    async loadLLMConfigs() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/config/llm`)
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`)
            }
            
            const configs = await response.json()
            this.renderLLMConfigs(configs)
            return configs
        } catch (error) {
            console.error('加载LLM配置失败:', error)
            throw error
        }
    }
      renderLLMConfigs(configs) {
        const container = document.getElementById('llmConfigs')
        
        // 保存当前配置数据供其他方法使用
        this.currentLLMConfigs = configs
        
        if (configs.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-robot" style="font-size: 48px; color: #ccc; margin-bottom: 16px;"></i>
                    <p style="color: #666;">还没有配置任何LLM模型</p>
                    <p style="color: #999; font-size: 14px;">点击"添加配置"按钮开始设置</p>
                    <div class="config-requirement-notice">
                        <i class="fas fa-info-circle"></i>
                        <span>智能体系统需要配置4个不同的LLM模型来实现最佳对话效果</span>
                    </div>
                </div>
            `
            return        }
        
        // 添加配置要求说明
        const requirementNotice = configs.length < 4 ? `
            <div class="config-requirement-card">
                <div class="requirement-header">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h4>配置要求</h4>
                </div>
                <div class="requirement-content">
                    <p>智能体系统需要配置<strong>4个不同的LLM模型</strong>来实现最佳对话效果：</p>
                    <ul>
                        <li>主对话模型 - 负责核心对话逻辑</li>
                        <li>情感分析模型 - 分析用户情感状态</li>
                        <li>记忆摘要模型 - 处理对话记忆</li>
                        <li>个性化模型 - 提供个性化回复</li>
                    </ul>
                    <p class="current-status">当前已配置：<span class="config-count">${configs.length}</span>/4</p>
                </div>
            </div>
        ` : `
            <div class="config-requirement-card success">
                <div class="requirement-header">
                    <i class="fas fa-check-circle"></i>
                    <h4>配置完成</h4>
                </div>
                <div class="requirement-content">
                    <p>已配置所需的4个LLM模型，系统可以正常运行。</p>
                </div>
            </div>
        `
        
        container.innerHTML = requirementNotice + configs.map((config, index) => `
            <div class="llm-config-card" data-index="${index}">
                <div class="config-card-header">
                    <h4 class="config-card-title">${config.model}</h4>
                    <div class="config-card-actions">
                        <button class="btn btn-secondary btn-sm" onclick="settingsManager.editLLMConfig(${index})" title="编辑">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-secondary btn-sm" onclick="settingsManager.deleteLLMConfig(${index})" title="删除">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="config-card-body">
                    <div class="config-info">
                        <div class="config-info-label">API密钥</div>
                        <div class="config-info-value masked">${this.maskApiKey(config.api_key)}</div>
                    </div>
                    <div class="config-info">
                        <div class="config-info-label">Base URL</div>
                        <div class="config-info-value">${config.base_url}</div>
                    </div>
                    <div class="config-info">
                        <div class="config-info-label">API类型</div>
                        <div class="config-info-value">${config.api_type}</div>
                    </div>
                </div>
            </div>
        `).join('')
    }
    
    maskApiKey(apiKey) {
        if (!apiKey || apiKey.length < 8) return '••••••••'
        return apiKey.substring(0, 4) + '••••••••' + apiKey.substring(apiKey.length - 4)
    }
    
    async loadEnvironmentConfig() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/config/environment`)
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`)
            }
            
            const config = await response.json()
            this.fillEnvironmentForm(config)
            return config
        } catch (error) {
            console.error('加载环境配置失败:', error)
            throw error
        }
    }
    
    fillEnvironmentForm(config) {
        document.getElementById('userNameInput').value = config.user_name || ''
        document.getElementById('agentNameInput').value = config.agent_name || ''
        document.getElementById('agentDescriptionInput').value = config.agent_description || ''
        document.getElementById('chromaDbDirInput').value = config.chroma_db_dir || './memory_db'
    }
    
    async loadUserPreferences() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/config/preferences`)
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`)
            }
            
            const preferences = await response.json()
            this.fillPreferencesForm(preferences)
            return preferences
        } catch (error) {
            console.error('加载用户偏好失败:', error)
            throw error
        }
    }
    
    fillPreferencesForm(preferences) {        document.getElementById('themeSelect').value = preferences.theme || 'default'
        document.getElementById('languageSelect').value = preferences.language || 'zh-CN'
        document.getElementById('visualEffectsCheckbox').checked = preferences.visual_effects_enabled !== false
        document.getElementById('notificationCheckbox').checked = preferences.notification_enabled !== false
    }
    
    openLLMModal(index = -1) {
        this.editingLLMIndex = index
        
        const modal = document.getElementById('llmConfigModal')
        const title = document.getElementById('modalTitle')
        
        if (index >= 0) {
            // 编辑模式
            title.textContent = '编辑LLM配置'
            this.fillLLMForm(this.currentLLMConfigs[index])
        } else {
            // 添加模式
            title.textContent = '添加LLM配置'
            this.clearLLMForm()
        }
        
        modal.classList.add('show')
    }
    
    closeLLMModal() {
        document.getElementById('llmConfigModal').classList.remove('show')
        this.clearLLMForm()
        this.editingLLMIndex = -1
    }
    
    fillLLMForm(config) {
        document.getElementById('modelInput').value = config.model || ''
        document.getElementById('apiKeyInput').value = config.api_key || ''
        document.getElementById('baseUrlInput').value = config.base_url || ''
        document.getElementById('apiTypeInput').value = config.api_type || 'openai'
    }
    
    clearLLMForm() {
        document.getElementById('llmConfigForm').reset()
    }
    
    async saveLLMConfig() {
        try {
            const form = document.getElementById('llmConfigForm')
            if (!form.checkValidity()) {
                form.reportValidity()
                return
            }
            
            const config = {
                model: document.getElementById('modelInput').value.trim(),
                api_key: document.getElementById('apiKeyInput').value.trim(),
                base_url: document.getElementById('baseUrlInput').value.trim(),
                api_type: document.getElementById('apiTypeInput').value
            }
            
            this.showLoading('正在保存配置...')
            
            // 获取当前配置列表
            let configs = this.currentLLMConfigs || []
            
            if (this.editingLLMIndex >= 0) {
                // 编辑模式
                configs[this.editingLLMIndex] = config
            } else {
                // 添加模式
                configs.push(config)
            }
            
            const response = await fetch(`${this.apiBaseUrl}/api/config/llm`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(configs)
            })
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`)
            }
            
            const result = await response.json()
            
            if (result.success) {
                this.hideLoading()
                this.showToast('LLM配置保存成功', 'success')
                this.closeLLMModal()
                await this.loadLLMConfigs()
            } else {
                throw new Error(result.message)
            }
            
        } catch (error) {
            this.hideLoading()
            this.showToast('保存LLM配置失败: ' + error.message, 'error')
        }
    }
    
    async editLLMConfig(index) {
        this.openLLMModal(index)
    }
    
    async deleteLLMConfig(index) {
        if (!confirm('确定要删除这个LLM配置吗？此操作不可撤销。')) {
            return
        }
        
        try {
            this.showLoading('正在删除配置...')
            
            let configs = this.currentLLMConfigs || []
            configs.splice(index, 1)
            
            const response = await fetch(`${this.apiBaseUrl}/api/config/llm`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(configs)
            })
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`)
            }
            
            const result = await response.json()
            
            if (result.success) {
                this.hideLoading()
                this.showToast('LLM配置删除成功', 'success')
                await this.loadLLMConfigs()
            } else {
                throw new Error(result.message)
            }
            
        } catch (error) {
            this.hideLoading()
            this.showToast('删除LLM配置失败: ' + error.message, 'error')
        }
    }
    
    async testLLMConnection() {
        try {
            const config = {
                model: document.getElementById('modelInput').value.trim(),
                api_key: document.getElementById('apiKeyInput').value.trim(),
                base_url: document.getElementById('baseUrlInput').value.trim(),
                api_type: document.getElementById('apiTypeInput').value
            }
            
            if (!config.model || !config.api_key || !config.base_url) {
                this.showToast('请填写完整的配置信息', 'warning')
                return
            }
            
            this.showLoading('正在测试连接...')
            
            const response = await fetch(`${this.apiBaseUrl}/api/config/llm/test`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            })
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`)
            }
            
            const result = await response.json()
            
            this.hideLoading()
            
            if (result.success) {
                this.showToast('连接测试成功！', 'success')
            } else {
                this.showToast('连接测试失败: ' + result.message, 'error')
            }
            
        } catch (error) {
            this.hideLoading()
            this.showToast('测试连接失败: ' + error.message, 'error')
        }
    }
    
    togglePasswordVisibility(inputId) {
        const input = document.getElementById(inputId)
        const button = document.getElementById('toggleApiKey')
        const icon = button.querySelector('i')
        
        if (input.type === 'password') {
            input.type = 'text'
            icon.className = 'fas fa-eye-slash'
        } else {
            input.type = 'password'
            icon.className = 'fas fa-eye'
        }
    }
    
    async saveEnvironmentConfig() {
        try {
            const config = {
                user_name: document.getElementById('userNameInput').value.trim(),
                agent_name: document.getElementById('agentNameInput').value.trim(),
                agent_description: document.getElementById('agentDescriptionInput').value.trim(),
                chroma_db_dir: document.getElementById('chromaDbDirInput').value.trim()
            }
            
            this.showLoading('正在保存环境配置...')
            
            const response = await fetch(`${this.apiBaseUrl}/api/config/environment`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            })
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`)
            }
            
            const result = await response.json()
            
            if (result.success) {
                this.hideLoading()
                this.showToast('环境配置保存成功', 'success')
            } else {
                throw new Error(result.message)
            }
            
        } catch (error) {
            this.hideLoading()
            this.showToast('保存环境配置失败: ' + error.message, 'error')
        }
    }
    
    async resetEnvironmentConfig() {
        if (!confirm('确定要重置环境配置吗？这将恢复到默认设置。')) {
            return
        }
        
        try {
            await this.loadEnvironmentConfig()
            this.showToast('环境配置已重置', 'success')
        } catch (error) {
            this.showToast('重置环境配置失败: ' + error.message, 'error')
        }
    }
    
    async saveUserPreferences() {
        try {            const preferences = {
                theme: document.getElementById('themeSelect').value,
                language: document.getElementById('languageSelect').value,
                visual_effects_enabled: document.getElementById('visualEffectsCheckbox').checked,
                notification_enabled: document.getElementById('notificationCheckbox').checked
            }
            
            this.showLoading('正在保存用户偏好...')
            
            const response = await fetch(`${this.apiBaseUrl}/api/config/preferences`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(preferences)
            })
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`)
            }
            
            const result = await response.json()
            
            if (result.success) {
                this.hideLoading()
                this.showToast('用户偏好保存成功', 'success')
            } else {
                throw new Error(result.message)
            }
            
        } catch (error) {
            this.hideLoading()
            this.showToast('保存用户偏好失败: ' + error.message, 'error')
        }
    }
    
    async resetUserPreferences() {
        if (!confirm('确定要恢复默认用户偏好吗？')) {
            return
        }
          const defaultPreferences = {
            theme: 'default',
            language: 'zh-CN',
            visual_effects_enabled: true,
            notification_enabled: true
        }
        
        this.fillPreferencesForm(defaultPreferences)
        this.showToast('用户偏好已重置为默认值', 'success')
    }
    
    async createBackup() {
        try {
            this.showLoading('正在创建备份...')
            
            const response = await fetch(`${this.apiBaseUrl}/api/config/backup`, {
                method: 'POST'
            })
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`)
            }
            
            const result = await response.json()
            
            if (result.success) {
                this.hideLoading()
                this.showToast('配置备份创建成功', 'success')
                // 这里可以添加下载备份文件的逻辑
            } else {
                throw new Error(result.message)
            }
            
        } catch (error) {
            this.hideLoading()
            this.showToast('创建备份失败: ' + error.message, 'error')
        }
    }
    
    async restoreBackup(file) {
        try {
            this.showLoading('正在恢复备份...')
            
            // 这里需要实现文件上传和恢复的逻辑
            // 暂时显示提示信息
            this.hideLoading()
            this.showToast('备份恢复功能正在开发中...', 'info')
            
        } catch (error) {
            this.hideLoading()
            this.showToast('恢复备份失败: ' + error.message, 'error')
        }
    }
    
    showLoading(text = '正在加载...') {
        const overlay = document.getElementById('loadingOverlay')
        const textElement = document.getElementById('loadingText')
        textElement.textContent = text
        overlay.classList.add('show')
    }
    
    hideLoading() {
        document.getElementById('loadingOverlay').classList.remove('show')
    }
    
    showToast(message, type = 'info') {
        const toast = document.getElementById('toast')
        const icon = toast.querySelector('.toast-icon')
        const messageElement = toast.querySelector('.toast-message')
        
        // 设置图标
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        }
        
        icon.className = `toast-icon ${icons[type] || icons.info}`
        messageElement.textContent = message
        
        // 移除所有类型类名，然后添加当前类型
        toast.classList.remove('success', 'error', 'warning', 'info')
        toast.classList.add(type)
        toast.classList.add('show')
        
        // 3秒后自动隐藏
        setTimeout(() => {
            toast.classList.remove('show')
        }, 3000)
    }
    
    // 存储当前配置以供其他方法使用
    get currentLLMConfigs() {
        return this._currentLLMConfigs || []
    }
    
    set currentLLMConfigs(configs) {
        this._currentLLMConfigs = configs
    }
}

// 初始化设置管理器
const settingsManager = new SettingsManager()

// 确保在加载LLM配置时存储数据
const originalLoadLLMConfigs = settingsManager.loadLLMConfigs
settingsManager.loadLLMConfigs = async function() {
    const configs = await originalLoadLLMConfigs.call(this)
    this.currentLLMConfigs = configs
    return configs
}
