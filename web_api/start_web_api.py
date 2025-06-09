"""
Web API服务器启动脚本
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_dependencies():
    """检查并安装依赖"""
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
    """检查配置文件"""
    config_file = project_root / "configs" / "OAI_CONFIG_LIST.json"
    
    if not config_file.exists():
        print(f"❌ 配置文件不存在: {config_file}")
        print("请确保已正确配置OpenAI API密钥")
        return False
    
    print(f"✅ 配置文件存在: {config_file}")
    return True


def start_server():
    """启动Web API服务器"""
    try:
        import uvicorn
        from web_api import app
        
        print("\n🚀 启动情感陪伴AI Web API服务器...")
        print("=" * 50)
        print("📖 API文档: http://localhost:8000/docs")
        print("🌐 前端界面: http://localhost:8000/static/index.html")
        print("💡 健康检查: http://localhost:8000/api/health")
        print("=" * 50)
        print("按 Ctrl+C 停止服务器\n")
        
        # 直接传递app对象
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
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
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查配置
    if not check_config():
        return
    
    # 启动服务器
    start_server()


if __name__ == "__main__":
    main()
