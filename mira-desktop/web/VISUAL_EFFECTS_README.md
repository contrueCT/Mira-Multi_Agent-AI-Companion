# 视觉效果功能使用指南

## 功能概述

小梦情感陪伴AI现已支持智能视觉效果功能，能够根据对话内容和情绪变化自动显示相应的视觉效果，让聊天体验更加生动有趣。

## 支持的效果类型

### 临时动画效果
- **庆祝烟花** (`celebration`) - 适用于祝贺、成功、开心等场景
- **飘落爱心** (`hearts`) - 适用于表达爱意、浪漫、甜蜜等场景
- **闪烁星光** (`sparkles`) - 适用于美丽、漂亮、梦幻等场景
- **漂浮气泡** (`bubbles`) - 适用于轻松、愉快、放松等场景
- **花瓣飘落** (`flower_petals`) - 适用于优雅、温馨、诗意等场景

### 持久主题效果
- **温暖主题** (`warm_theme`) - 粉色系，营造温馨氛围
- **清凉主题** (`cool_theme`) - 蓝绿色系，营造清新氛围
- **夕阳主题** (`sunset_theme`) - 橙红色系，营造浪漫氛围
- **夜晚主题** (`night_theme`) - 深色系，营造静谧氛围
- **春日主题** (`spring_theme`) - 绿色系，营造生机氛围

## 使用方法

### 1. 智能体自动触发
当与小梦聊天时，智能体会根据对话内容和情绪自动选择合适的视觉效果。例如：
- 说"今天考试通过了，好开心！" → 可能触发庆祝烟花效果
- 说"我爱你" → 可能触发飘落爱心效果
- 说"感觉很累，想放松一下" → 可能切换到清凉主题

### 2. 手动控制
- 点击聊天界面右上角的魔法棒图标 (🪄) 可以开启/关闭视觉效果
- 效果开启时，按钮呈红色并有绿色指示点
- 效果关闭时，按钮呈灰色

### 3. 测试页面
访问 `test-effects.html` 可以手动测试所有视觉效果：
```bash
# 在浏览器中打开
file:///path/to/mira-desktop/web/test-effects.html
```

## 技术实现

### 文件结构
```
web/
├── js/
│   ├── visual-effects.js    # 视觉效果处理器
│   └── chat.js             # 修改后的聊天逻辑
├── css/
│   ├── visual-effects.css  # 视觉效果样式
│   └── style.css          # 主样式（已更新）
├── index.html             # 主页面（已更新）
└── test-effects.html      # 测试页面
```

### 核心组件

#### VisualEffectsProcessor 类
负责处理所有视觉效果的执行和管理：
- `executeVisualCommand(command)` - 执行视觉效果指令
- `setEffectsEnabled(enabled)` - 启用/禁用效果
- `testEffect(effectName, intensity)` - 测试特定效果

#### 效果指令格式
```javascript
{
    "type": "visual_effect",
    "effect_type": "temporary|persistent", 
    "effect_name": "celebration",
    "display_name": "庆祝烟花",
    "duration": 3000,
    "intensity": 0.8,
    "parameters": {
        "particle_count": 50,
        "colors": ["#ff6b6b", "#4ecdc4"],
        // ...其他参数
    },
    "timestamp": "2025-06-13T10:30:00.000Z"
}
```

## 配置选项

### 用户偏好设置
视觉效果的开关状态会自动保存到 localStorage：
```javascript
// 手动设置偏好
visualEffects.setEffectsEnabled(false) // 禁用效果
visualEffects.setEffectsEnabled(true)  // 启用效果
```

### 强度参数
所有效果都支持 0.1-1.0 的强度调节：
- 0.1-0.3: 轻微效果
- 0.4-0.6: 中等效果  
- 0.7-1.0: 强烈效果

## 性能优化

### CSS 动画优化
- 使用 `will-change` 属性优化动画性能
- 使用 `transform` 和 `opacity` 属性实现硬件加速
- 支持 `prefers-reduced-motion` 媒体查询

### 内存管理
- 临时效果会在指定时间后自动清理
- 持久效果会在切换时平滑过渡
- 禁用效果时会立即清理所有活动效果

## 浏览器兼容性

### 支持的浏览器
- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

### 降级处理
- 不支持的浏览器会自动禁用视觉效果
- 所有功能都有适当的错误处理

## 开发调试

### 调试模式
在浏览器控制台中启用调试：
```javascript
// 添加调试类
document.body.classList.add('debug-mode')

// 测试特定效果
visualEffects.testEffect('celebration', 0.8)

// 查看当前状态
console.log(visualEffects.isEffectsEnabledStatus())
```

### 常见问题
1. **效果不显示** - 检查是否已启用视觉效果
2. **性能问题** - 降低效果强度或禁用部分效果
3. **样式冲突** - 确保 CSS 加载顺序正确

## 更新日志

### v1.0.0 (2025-06-13)
- ✅ 实现基础视觉效果系统
- ✅ 支持 5 种临时动画效果
- ✅ 支持 5 种持久主题效果  
- ✅ 集成到聊天系统
- ✅ 提供测试页面
- ✅ 支持用户偏好设置

## 后续计划

- 🔄 添加更多效果类型
- 🔄 支持自定义效果参数
- 🔄 优化移动端体验
- 🔄 添加音效支持
