"""
Web API服务器启动脚本 - 支持Docker容器化
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

# Docker环境适配
def get_project_root():
    """获取项目根目录，支持容器环境"""
    if os.getenv('DOCKER_ENV'):
        return Path('/app')
    return Path(__file__).parent.parent

project_root = get_project_root()
sys.path.insert(0, str(project_root))

def check_dependencies():
    """检查并安装依赖"""
    # Docker环境中跳过依赖检查
    if os.getenv('DOCKER_ENV'):
        print("📦 Docker环境，跳过依赖检查...")
        return True
        
    requirements_file = project_root / "web_api" / "requirements-web.txt"
    
    print("📦 检查Web API依赖...")
    try:
        # 检查是否在虚拟环境中
        venv_path = project_root / "venv"
        if venv_path.exists():
            if sys.platform == "win32":
                pip_path = venv_path / "Scripts" / "pip.exe"
                python_path = venv_path / "Scripts" / "python.exe"
            else:
                pip_path = venv_path / "bin" / "pip"
                python_path = venv_path / "bin" / "python"
            
            if pip_path.exists():
                print(f"✅ 使用虚拟环境: {venv_path}")
                subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], check=True)
            else:
                print("⚠️  虚拟环境中未找到pip，使用系统pip")
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], check=True)
        else:
            print("⚠️  未找到虚拟环境，使用系统pip")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], check=True)
            
        print("✅ 依赖安装完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 检查依赖时发生错误: {e}")
        return False
    
    return True

def check_config():
    """检查配置文件状态"""
    print("🔍 检查配置文件...")
    
    # 导入配置管理器
    from web_api.config_manager import ConfigManager
    
    try:
        config_manager = ConfigManager(str(project_root))
        
        # 检查LLM配置
        llm_configs = config_manager.get_llm_configs()
        
        if not llm_configs:
            print("⚠️  未找到LLM配置，但服务仍将启动以便通过客户端配置")
            return True
            
        # 检查是否有空的API密钥
        empty_keys = 0
        for i, config in enumerate(llm_configs, 1):
            if not config.api_key or config.api_key.strip() == "":
                empty_keys += 1
                
        if empty_keys > 0:
            print(f"⚠️  发现 {empty_keys} 个API配置缺少密钥")
            print("📝 可以通过以下方式配置API密钥:")
            print(f"   1. 直接编辑配置文件: {config_manager.llm_config_file}")
            print(f"   2. 通过Web界面配置: http://localhost:8000/static/settings.html")
            print("💡 服务将正常启动，配置完成后功能即可使用")
            return True
        else:
            print(f"✅ 找到 {len(llm_configs)} 个有效的API配置")
            return True
            
    except Exception as e:
        print(f"⚠️  检查配置时发生错误: {e}")
        print("💡 服务仍将启动以便通过客户端配置")
        return True

def start_server():
    """启动Web API服务器"""
    try:
        import uvicorn
        from web_api.web_api import app
        
        # 从环境变量获取配置
        host = os.getenv('HOST', '0.0.0.0')  # Docker中使用0.0.0.0
        port = int(os.getenv('PORT', '8000'))
        
        print(f"\n🚀 启动情感陪伴AI Web API服务器...")
        print("=" * 50)
        print(f"📡 服务地址: http://{host}:{port}")
        print(f"📖 API文档: http://{host}:{port}/docs")
        print(f"🌐 前端界面: http://{host}:{port}/static/index.html")
        print(f"💡 健康检查: http://{host}:{port}/api/health")
        print("=" * 50)
        print("按 Ctrl+C 停止服务器\n")
        
        # 直接传递app对象
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("🎯 情感陪伴AI Web API 启动器")
    print("=" * 40)
    
    # Docker环境检查
    if os.getenv('DOCKER_ENV'):
        print("🐳 Docker环境检测到")
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查配置（但不阻止启动）
    check_config()
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()
