const { contextBridge, ipcRenderer } = require('electron')

// 暴露安全的API给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
    // 基础信息
    platform: process.platform,
    isElectron: true,
    
    // 版本信息
    versions: {
        node: process.versions.node,
        chrome: process.versions.chrome,
        electron: process.versions.electron
    },
    
    // 基础配置管理（为后续扩展预留）
    getConfig: () => ipcRenderer.invoke('get-config'),
    setConfig: (key, value) => ipcRenderer.invoke('set-config', key, value),
    
    // 事件监听（为后续扩展预留）
    onConfigChanged: (callback) => {
        ipcRenderer.on('config-changed', (event, data) => callback(data))
    },
    
    // 移除监听器
    removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel)
})

console.log('🚀 Electron桌面客户端已加载')