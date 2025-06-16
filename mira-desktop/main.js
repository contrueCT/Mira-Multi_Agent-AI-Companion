const { app, BrowserWindow, ipcMain } = require('electron')
const path = require('path')
const fs = require('fs')

// 立即禁用硬件加速以避免持续的GPU错误
app.disableHardwareAcceleration()

// 添加更严格的GPU禁用参数
app.commandLine.appendSwitch('--disable-gpu')
app.commandLine.appendSwitch('--disable-gpu-compositing')
app.commandLine.appendSwitch('--disable-gpu-rasterization')
app.commandLine.appendSwitch('--disable-gpu-sandbox')
app.commandLine.appendSwitch('--disable-software-rasterizer')
app.commandLine.appendSwitch('--disable-background-timer-throttling')
app.commandLine.appendSwitch('--disable-backgrounding-occluded-windows')
app.commandLine.appendSwitch('--disable-renderer-backgrounding')
app.commandLine.appendSwitch('--disable-features=VizDisplayCompositor')

// 使用新的child-process-gone事件代替已弃用的gpu-process-crashed
app.on('child-process-gone', (event, details) => {
    if (details.type === 'GPU') {
        console.log('⚠️ GPU子进程异常退出，已预先禁用硬件加速')
    }
})

let mainWindow

// 基础配置
let config = {
    apiBaseUrl: 'http://localhost:8000',
    windowBounds: {
        width: 1000,
        height: 700
    }
}

// 配置文件路径
const configPath = path.join(app.getPath('userData'), 'config.json')

function loadConfig() {
    try {
        if (fs.existsSync(configPath)) {
            const data = fs.readFileSync(configPath, 'utf8')
            config = { ...config, ...JSON.parse(data) }
            console.log('✅ 配置已加载')
        }
    } catch (error) {
        console.error('加载配置失败:', error)
    }
}

function saveConfig() {
    try {
        const userDataDir = app.getPath('userData')
        if (!fs.existsSync(userDataDir)) {
            fs.mkdirSync(userDataDir, { recursive: true })
        }
        fs.writeFileSync(configPath, JSON.stringify(config, null, 2))
        console.log('✅ 配置已保存')
    } catch (error) {
        console.error('保存配置失败:', error)
    }
}

function createWindow() {
    // 加载配置
    loadConfig()

    // 构建图标路径
    let iconPath;
    if (process.platform === 'win32') {
        iconPath = path.join(__dirname, 'assets/icon.ico');
    } else if (process.platform === 'darwin') {
        iconPath = path.join(__dirname, 'assets/icon.icns');
    } else {
        iconPath = path.join(__dirname, 'assets/icon.png');
    }
    
    // 检查图标文件是否存在
    if (!fs.existsSync(iconPath)) {
        iconPath = path.join(__dirname, 'assets/icon.png');
        if (!fs.existsSync(iconPath)) {
            console.warn('⚠️ 图标文件不存在:', iconPath);
            iconPath = undefined;
        }
    }    mainWindow = new BrowserWindow({
        width: config.windowBounds.width,
        height: config.windowBounds.height,
        minWidth: 800,
        minHeight: 600,
        frame: false, // 无边框窗口
        backgroundColor: '#f5f5f5', // 使用浅色背景代替透明
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js'),
            // 强制使用软件渲染
            enableRemoteModule: false,
            backgroundThrottling: false,
            offscreen: false,
            experimentalFeatures: false,
            // 禁用硬件加速相关功能
            hardwareAcceleration: false
        },
        icon: iconPath,
        titleBarStyle: 'hidden', // 隐藏标题栏
        show: false // 先不显示，等加载完成后再显示
    })

    // 加载前端页面
    mainWindow.loadFile('web/index.html')

    // 页面加载完成后显示窗口
    mainWindow.once('ready-to-show', () => {
        mainWindow.show()
    })

    // 开发时打开调试工具
    if (process.argv.includes('--dev')) {
        mainWindow.webContents.openDevTools()
    }
    
    // 窗口关闭时保存配置
    mainWindow.on('close', () => {
        const bounds = mainWindow.getBounds()
        config.windowBounds = bounds
        saveConfig()
    })
}

// 基础IPC处理
ipcMain.handle('get-config', () => {
    return config
})

ipcMain.handle('set-config', (event, key, value) => {
    const keys = key.split('.')
    let target = config
    for (let i = 0; i < keys.length - 1; i++) {
        if (!target[keys[i]]) target[keys[i]] = {}
        target = target[keys[i]]
    }
    target[keys[keys.length - 1]] = value
    saveConfig()
    
    // 通知渲染进程配置已更改
    mainWindow.webContents.send('config-changed', { key, value })
    return true
})

// 窗口控制IPC处理
ipcMain.handle('window-minimize', () => {
    mainWindow.minimize()
})

ipcMain.handle('window-maximize', () => {
    if (mainWindow.isMaximized()) {
        mainWindow.unmaximize()
    } else {
        mainWindow.maximize()
    }
    return mainWindow.isMaximized()
})

ipcMain.handle('window-close', () => {
    mainWindow.close()
})

ipcMain.handle('window-is-maximized', () => {
    return mainWindow.isMaximized()
})

// 应用准备就绪
app.whenReady().then(createWindow)

// 所有窗口关闭时退出 (macOS除外)
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit()
    }
})

// macOS重新激活
app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow()
    }
})

// 防止多实例运行
if (!app.requestSingleInstanceLock()) {
    app.quit()
} else {
    app.on('second-instance', () => {
        if (mainWindow) {
            if (mainWindow.isMinimized()) mainWindow.restore()
            mainWindow.focus()
        }
    })
}