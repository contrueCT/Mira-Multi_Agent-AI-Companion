@echo off
chcp 65001 > nul
title 小梦桌面客户端安装

echo.
echo 🚀 小梦桌面客户端 v1.0.0
echo.

echo [1/2] 检查 Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 请先安装 Node.js: https://nodejs.org/zh-cn/
    pause
    exit /b 1
)
echo ✅ Node.js 已安装

echo [2/2] 安装依赖...
npm install

if errorlevel 1 (
    echo ❌ 安装失败，请检查网络连接
    pause
    exit /b 1
)

echo.
echo ✅ 安装完成！
echo.
echo 启动应用: npm start
echo 构建应用: npm run build
echo.
pause