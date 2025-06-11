/**
 * 客户端配置文件
 * 管理API地址和其他配置
 */

// API配置
const API_CONFIG = {
    // 开发环境 - 本地后端
    development: {
        baseUrl: 'http://localhost:8000',
        timeout: 10000
    },
    
    // 生产环境 - 云端后端
    production: {
        baseUrl: 'https://your-cloud-api.com',  // 替换为您的云端API地址
        timeout: 15000
    }
}

// 自动检测环境
function getApiConfig() {
    // 可以通过URL参数或其他方式判断环境
    const isProduction = window.location.hostname !== 'localhost' && 
                         !window.location.hostname.includes('127.0.0.1')
    
    const env = isProduction ? 'production' : 'development'
    console.log(`🌐 运行环境: ${env}`)
    console.log(`📡 API地址: ${API_CONFIG[env].baseUrl}`)
    
    return API_CONFIG[env]
}

// 导出配置
window.API_CONFIG = getApiConfig()