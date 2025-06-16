/**
 * 性能监控和优化器
 * 监控应用性能并自动应用优化策略
 */

class PerformanceMonitor {    constructor() {
        this.performanceData = {
            frameRate: 0,
            memoryUsage: 0,
            domNodes: 0,
            lastCheck: Date.now(),
            gpuErrors: 0
        }
        
        this.optimizationApplied = false
        this.monitoringInterval = null
        this.gpuFallbackMode = false
        
        this.init()
    }
      init() {
        // 开始性能监控
        this.startMonitoring()
        
        // 监听页面可见性变化
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseNonEssentialAnimations()
            } else {
                this.resumeAnimations()
            }
        })
        
        // 监听潜在的GPU相关错误
        this.setupGPUErrorHandling()
        
        console.log('📊 性能监控器已启动')
    }
    
    /**
     * 设置GPU错误处理
     */
    setupGPUErrorHandling() {
        // 监听WebGL上下文丢失
        window.addEventListener('webglcontextlost', (event) => {
            event.preventDefault()
            this.handleGPUError('WebGL上下文丢失')
        })
        
        // 监听WebGL上下文恢复
        window.addEventListener('webglcontextrestored', () => {
            console.log('🔄 WebGL上下文已恢复')
            this.gpuFallbackMode = false
        })
        
        // 检测CSS滤镜渲染问题
        this.detectFilterRenderingIssues()
    }
    
    /**
     * 处理GPU错误
     */
    handleGPUError(errorType) {
        this.performanceData.gpuErrors++
        console.warn(`⚠️ GPU错误检测: ${errorType}`)
        
        if (!this.gpuFallbackMode) {
            this.enableGPUFallbackMode()
        }
    }
    
    /**
     * 启用GPU回退模式
     */
    enableGPUFallbackMode() {
        this.gpuFallbackMode = true
        document.body.classList.add('gpu-fallback-mode')
        
        // 禁用硬件加速相关的CSS属性
        const style = document.createElement('style')
        style.textContent = `
            .gpu-fallback-mode * {
                transform: none !important;
                filter: none !important;
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
                will-change: auto !important;
            }
            
            .gpu-fallback-mode .app-container {
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
            }
        `
        document.head.appendChild(style)
        
        console.log('🛟 已启用GPU回退模式，减少硬件加速使用')
        
        // 通知用户
        this.showGPUFallbackNotification()
    }
    
    /**
     * 显示GPU回退模式通知
     */
    showGPUFallbackNotification() {
        const notification = document.createElement('div')
        notification.className = 'gpu-fallback-notification'
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-info-circle"></i>
                <span>检测到GPU问题，已启用兼容模式</span>
                <button class="close-notification">×</button>
            </div>
        `
        
        const style = document.createElement('style')
        style.textContent = `
            .gpu-fallback-notification {
                position: fixed;
                top: 50px;
                right: 20px;
                background: rgba(255, 193, 7, 0.95);
                color: #333;
                padding: 12px 16px;
                border-radius: 8px;
                font-size: 14px;
                z-index: 10000;
                animation: slideIn 0.3s ease;
            }
            
            .notification-content {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .close-notification {
                background: none;
                border: none;
                color: #333;
                cursor: pointer;
                font-size: 16px;
                padding: 0;
                margin-left: 8px;
            }
            
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `
        document.head.appendChild(style)
        
        notification.querySelector('.close-notification').addEventListener('click', () => {
            notification.remove()
        })
        
        document.body.appendChild(notification)
        
        // 5秒后自动关闭
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove()
            }
        }, 5000)
    }
    
    /**
     * 检测CSS滤镜渲染问题
     */
    detectFilterRenderingIssues() {
        try {
            const testElement = document.createElement('div')
            testElement.style.cssText = `
                position: absolute;
                top: -9999px;
                width: 100px;
                height: 100px;
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
            `
            document.body.appendChild(testElement)
            
            // 检查是否正确应用了滤镜
            const computedStyle = window.getComputedStyle(testElement)
            const hasBackdropFilter = computedStyle.backdropFilter !== 'none' || 
                                    computedStyle.webkitBackdropFilter !== 'none'
            
            if (!hasBackdropFilter) {
                console.warn('⚠️ 检测到backdrop-filter不支持，启用回退模式')
                this.handleGPUError('backdrop-filter不支持')
            }
            
            document.body.removeChild(testElement)
        } catch (error) {
            console.warn('⚠️ 滤镜检测失败:', error)
            this.handleGPUError('滤镜检测失败')
        }
    }
    
    startMonitoring() {
        this.monitoringInterval = setInterval(() => {
            this.checkPerformance()
        }, 5000) // 每5秒检查一次
    }
    
    checkPerformance() {
        // 检查内存使用情况
        if (window.performance && window.performance.memory) {
            this.performanceData.memoryUsage = window.performance.memory.usedJSHeapSize / 1024 / 1024 // MB
        }
        
        // 检查DOM节点数量
        this.performanceData.domNodes = document.querySelectorAll('*').length
        
        // 检查是否需要优化
        if (this.needsOptimization()) {
            this.applyPerformanceOptimizations()
        }
    }
    
    needsOptimization() {
        const { memoryUsage, domNodes } = this.performanceData
        
        // 如果内存使用超过100MB或DOM节点超过2000个，则需要优化
        return memoryUsage > 100 || domNodes > 2000
    }
    
    applyPerformanceOptimizations() {
        if (this.optimizationApplied) return
        
        console.log('⚡ 检测到性能压力，应用优化策略')
        
        // 1. 减少动画复杂度
        this.reduceAnimationComplexity()
        
        // 2. 清理不必要的DOM元素
        this.cleanupDOMElements()
        
        // 3. 限制并发效果数量
        this.limitConcurrentEffects()
        
        // 4. 启用低性能模式
        this.enableLowPerformanceMode()
        
        this.optimizationApplied = true
        
        // 5分钟后重置优化标志
        setTimeout(() => {
            this.optimizationApplied = false
        }, 300000)
    }
    
    reduceAnimationComplexity() {
        const style = document.createElement('style')
        style.id = 'performance-optimization'
        style.textContent = `
            /* 简化动画 */
            .visual-effects-container * {
                animation-duration: 0.5s !important;
                animation-iteration-count: 1 !important;
            }
            
            /* 减少模糊效果 */
            .app-container,
            .chat-container,
            .settings-container {
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
            }
            
            /* 禁用复杂变换 */
            .celebration-particle,
            .floating-heart-particle,
            .sparkle-particle {
                transform: none !important;
                will-change: auto !important;
            }
        `
        
        // 移除旧的优化样式
        const oldStyle = document.getElementById('performance-optimization')
        if (oldStyle) {
            oldStyle.remove()
        }
        
        document.head.appendChild(style)
    }
    
    cleanupDOMElements() {
        // 清理过期的视觉效果元素
        const effectsContainer = document.querySelector('.visual-effects-container')
        if (effectsContainer) {
            const allEffects = effectsContainer.querySelectorAll('[data-effect-id]')
            if (allEffects.length > 20) {
                // 保留最新的10个效果
                const effectsToRemove = Array.from(allEffects).slice(0, allEffects.length - 10)
                effectsToRemove.forEach(effect => {
                    effect.remove()
                })
                console.log(`🧹 清理了 ${effectsToRemove.length} 个过期的视觉效果元素`)
            }
        }
        
        // 清理过多的聊天消息（保留最新的50条）
        const chatMessages = document.getElementById('chatMessages')
        if (chatMessages) {
            const messages = chatMessages.querySelectorAll('.message')
            if (messages.length > 50) {
                const messagesToRemove = Array.from(messages).slice(0, messages.length - 50)
                messagesToRemove.forEach(message => {
                    message.remove()
                })
                console.log(`🧹 清理了 ${messagesToRemove.length} 条旧聊天记录`)
            }
        }
    }
    
    limitConcurrentEffects() {
        // 通知视觉效果处理器限制效果数量
        if (window.visualEffectsProcessor) {
            window.visualEffectsProcessor.maxConcurrentEffects = 3
            window.visualEffectsProcessor.cleanupExcessiveEffects()
        }
    }
    
    enableLowPerformanceMode() {
        document.body.classList.add('performance-mode-low')
        document.body.classList.remove('performance-mode-medium', 'performance-mode-high')
        console.log('🐌 已启用低性能模式')
    }
    
    pauseNonEssentialAnimations() {
        const style = document.createElement('style')
        style.id = 'pause-animations'
        style.textContent = `
            .visual-effects-container * {
                animation-play-state: paused !important;
            }
        `
        document.head.appendChild(style)
    }
    
    resumeAnimations() {
        const pauseStyle = document.getElementById('pause-animations')
        if (pauseStyle) {
            pauseStyle.remove()
        }
    }
    
    destroy() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval)
        }
        
        // 移除优化样式
        const optimizationStyle = document.getElementById('performance-optimization')
        if (optimizationStyle) {
            optimizationStyle.remove()
        }
    }
}

// 创建全局性能监控器
window.performanceMonitor = new PerformanceMonitor()
