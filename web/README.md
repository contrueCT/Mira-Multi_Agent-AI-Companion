# 小梦情感陪伴 - Web前端

这是小梦情感陪伴AI的Web前端界面，使用纯HTML+CSS+JavaScript开发。

## 功能特性

### 当前已实现（基础聊天功能）
- ✅ 清新可爱的界面设计，体现小梦的温馨个性
- ✅ 实时聊天界面，支持用户和AI消息展示
- ✅ 打字动效，模拟真实对话体验
- ✅ 表情选择器，丰富表达方式
- ✅ 情感状态显示（心情+亲密度）
- ✅ 响应式设计，适配各种设备
- ✅ 输入框自适应高度
- ✅ 字符计数和发送状态管理
- ✅ 加载状态和错误提示
- ✅ 模拟情感分析和智能回复

### 待开发功能
- ⏳ 聊天记录查看和管理
- ⏳ 系统设置和个性化配置
- ⏳ 与后端Python API的集成
- ⏳ 记忆系统可视化
- ⏳ 情感状态历史图表
- ⏳ 语音交互功能
- ⏳ 主题切换功能

## 文件结构

```
web/
├── index.html          # 主页面
├── css/
│   └── style.css       # 样式文件
├── js/
│   └── chat.js         # 聊天功能脚本
└── README.md           # 说明文档
```

## 部署说明

### 使用 Nginx

1. 将整个 `web` 目录复制到你的 nginx 网站根目录
2. 配置 nginx.conf：

```nginx
server {
    listen 80;
    server_name localhost;
    
    # 前端静态文件
    location / {
        root /path/to/emotional-companion/web;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # 后端API代理（未来集成时使用）
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. 重新加载 nginx 配置
4. 访问 `http://localhost` 即可使用

### 快速预览

也可以使用简单的HTTP服务器快速预览：

```bash
# 使用 Python
cd web
python -m http.server 8080

# 使用 Node.js
cd web
npx serve .

# 使用 Live Server (VS Code扩展)
# 右键 index.html -> Open with Live Server
```

## 设计特色

### 视觉设计
- 🌸 温馨的粉色渐变背景，营造温柔氛围
- 💕 心形图标和浮动动画，体现情感陪伴主题
- ✨ 毛玻璃效果和柔和阴影，现代化视觉体验
- 🎨 精心设计的颜色搭配和字体选择

### 交互体验
- 📝 打字机效果的消息显示
- 🎭 表情选择器和丰富的动画反馈
- 📱 完全响应式设计，移动端友好
- ⚡ 流畅的动画过渡和加载状态

### 技术特点
- 🚀 纯前端实现，无需复杂构建工具
- 🔧 模块化的 JavaScript 代码结构
- 🎯 预留了后端API集成接口
- 🛡️ 错误处理和用户反馈机制

## 当前模拟功能

由于还未与后端集成，前端目前包含以下模拟功能：

1. **智能回复模拟** - 基于关键词的简单情感分析和回复生成
2. **情感状态更新** - 根据对话内容动态更新显示的情感状态
3. **API调用模拟** - 模拟网络请求的延迟和响应格式

## 下一步集成计划

1. 创建 Flask/FastAPI 后端接口
2. 实现前后端通信协议
3. 集成现有的情感记忆系统
4. 添加实时推送功能
5. 完善用户偏好和设置功能

## 浏览器兼容性

- ✅ Chrome 70+
- ✅ Firefox 65+
- ✅ Safari 12+
- ✅ Edge 79+

## 开发说明

如需修改样式或功能，主要文件说明：

- `css/style.css` - 包含所有样式定义，采用CSS Grid和Flexbox布局
- `js/chat.js` - 主要的聊天逻辑，包含 `EmotionalChatApp` 类
- `index.html` - 页面结构和组件定义

代码结构清晰，注释详细，便于后续开发和维护。
