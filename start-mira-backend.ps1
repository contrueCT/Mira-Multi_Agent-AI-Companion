# Mira Backend Docker 启动脚本
# 自动载入Docker镜像并启动容器

param(
    [string]$ImageFile = "miramate-backend-1.0.0.tar",
    [string]$ContainerName = "mira-backend",
    [string]$ImageTag = "miramate-backend:1.0.0"
)

Write-Host "🚀 Mira Backend Docker 启动脚本" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Yellow

# 检查Docker是否运行
Write-Host "🔍 检查Docker服务状态..." -ForegroundColor Cyan
try {
    $dockerInfo = docker info 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker服务未运行，请先启动Docker Desktop" -ForegroundColor Red
        Write-Host "💡 启动Docker Desktop后重新运行此脚本" -ForegroundColor Yellow
        pause
        exit 1
    }
    Write-Host "✅ Docker服务正在运行" -ForegroundColor Green
} catch {
    Write-Host "❌ 无法连接到Docker，请确保Docker已安装并运行" -ForegroundColor Red
    pause
    exit 1
}

# 检查是否存在同名容器，如果存在则停止并删除
Write-Host "🔍 检查现有容器..." -ForegroundColor Cyan
$existingContainer = docker ps -a --filter "name=$ContainerName" --format "{{.Names}}" 2>$null
if ($existingContainer -eq $ContainerName) {
    Write-Host "⚠️  发现同名容器，正在停止并删除..." -ForegroundColor Yellow
    docker stop $ContainerName 2>$null
    docker rm $ContainerName 2>$null
    Write-Host "✅ 已清理同名容器" -ForegroundColor Green
}

# 步骤1: 载入Docker镜像
Write-Host "📦 步骤1: 载入Docker镜像..." -ForegroundColor Cyan
if (Test-Path $ImageFile) {
    Write-Host "📁 找到镜像文件: $ImageFile" -ForegroundColor Green
    Write-Host "⏳ 正在载入镜像，请稍候..." -ForegroundColor Yellow
    
    docker load -i $ImageFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 镜像载入成功!" -ForegroundColor Green
    } else {
        Write-Host "❌ 镜像载入失败!" -ForegroundColor Red
        pause
        exit 1
    }
} else {
    Write-Host "❌ 未找到镜像文件: $ImageFile" -ForegroundColor Red
    Write-Host "💡 请确保镜像文件在当前目录下" -ForegroundColor Yellow
    pause
    exit 1
}

# 创建必要的数据目录
Write-Host "📁 创建数据目录..." -ForegroundColor Cyan
$dataDir = "docker-data"
$subDirs = @("configs", "memory_db", "logs")

if (!(Test-Path $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
    Write-Host "✅ 创建主数据目录: $dataDir" -ForegroundColor Green
}

foreach ($subDir in $subDirs) {
    $fullPath = Join-Path $dataDir $subDir
    if (!(Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "✅ 创建子目录: $fullPath" -ForegroundColor Green
    }
}

# 步骤2: 启动Docker容器
Write-Host "🚀 步骤2: 启动Docker容器..." -ForegroundColor Cyan
Write-Host "📋 容器配置:" -ForegroundColor Yellow
Write-Host "   容器名称: $ContainerName" -ForegroundColor White
Write-Host "   镜像标签: $ImageTag" -ForegroundColor White
Write-Host "   端口映射: 8000:8000" -ForegroundColor White
Write-Host "   数据目录: $dataDir" -ForegroundColor White

$currentPath = Get-Location
Write-Host "⏳ 正在启动容器..." -ForegroundColor Yellow

docker run -d `
    --name $ContainerName `
    -p 8000:8000 `
    -v "${currentPath}\docker-data\configs:/app/configs" `
    -v "${currentPath}\docker-data\memory_db:/app/memory_db" `
    -v "${currentPath}\docker-data\logs:/app/logs" `
    -e DOCKER_ENV=true `
    -e HOST=0.0.0.0 `
    -e PORT=8000 `
    $ImageTag

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 容器启动成功!" -ForegroundColor Green
    
    # 等待容器启动
    Write-Host "⏳ 等待服务启动..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # 检查容器状态
    $containerStatus = docker ps --filter "name=$ContainerName" --format "{{.Status}}" 2>$null
    if ($containerStatus -like "*Up*") {
        Write-Host "✅ 容器运行正常!" -ForegroundColor Green
        
        # 显示容器日志前几行
        Write-Host "`n📋 容器启动日志:" -ForegroundColor Cyan
        docker logs $ContainerName --tail 10
        
        Write-Host "`n🎉 启动完成!" -ForegroundColor Green
        Write-Host "=" * 50 -ForegroundColor Yellow
        Write-Host "🌐 访问地址: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "📊 健康检查: http://localhost:8000/api/health" -ForegroundColor Cyan
        Write-Host "📖 API文档: http://localhost:8000/docs" -ForegroundColor Cyan
        Write-Host "`n💡 常用命令:" -ForegroundColor Yellow
        Write-Host "   查看日志: docker logs -f $ContainerName" -ForegroundColor White
        Write-Host "   停止服务: docker stop $ContainerName" -ForegroundColor White        
        Write-Host "   重启服务: docker restart $ContainerName" -ForegroundColor White
        Write-Host "   删除容器: docker rm $ContainerName" -ForegroundColor White
        } else {
        Write-Host "⚠️  容器可能未正常启动，请检查日志:" -ForegroundColor Yellow
        docker logs $ContainerName
    }
} else {
    Write-Host "❌ 容器启动失败!" -ForegroundColor Red
    Write-Host "💡 请检查镜像标签是否正确: $ImageTag" -ForegroundColor Yellow
    
    # 显示可用的镜像
    Write-Host "`n📋 当前可用的镜像:" -ForegroundColor Cyan
    docker images --format "table {{.Repository}}:{{.Tag}}\t{{.CreatedAt}}\t{{.Size}}"
}

Write-Host "`n按任意键退出..." -ForegroundColor Gray
pause
