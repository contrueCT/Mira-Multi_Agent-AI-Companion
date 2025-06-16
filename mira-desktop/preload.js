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
    
    // 基础配置管理
    getConfig: () => ipcRenderer.invoke('get-config'),
    setConfig: (key, value) => ipcRenderer.invoke('set-config', key, value),
    
    // 窗口控制
    windowMinimize: () => ipcRenderer.invoke('window-minimize'),
    windowMaximize: () => ipcRenderer.invoke('window-maximize'),
    windowClose: () => ipcRenderer.invoke('window-close'),
    windowIsMaximized: () => ipcRenderer.invoke('window-is-maximized'),
    
    // 设置窗口
    openSettings: () => ipcRenderer.invoke('open-settings'),

    // 事件监听
    onConfigChanged: (callback) => {
        ipcRenderer.on('config-changed', (event, data) => callback(data))
    },
    
    // 移除监听器
    removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel)
})

console.log('🚀 Electron桌面客户端已加载')