"""
快速启动Web API服务器的便捷脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # 获取项目根目录
    project_root = Path(__file__).parent
    web_api_dir = project_root / "web_api"
    
    print("🚀 启动情感陪伴AI Web API服务器...")
    
    # 检查虚拟环境
    venv_path = project_root / "venv"
    if venv_path.exists():
        if sys.platform == "win32":
            python_path = venv_path / "Scripts" / "python.exe"
            activate_script = venv_path / "Scripts" / "activate.bat"
        else:
            python_path = venv_path / "bin" / "python"
            activate_script = venv_path / "bin" / "activate"
        
        if python_path.exists():
            print(f"✅ 使用虚拟环境: {venv_path}")
            
            # 在Windows上需要先激活虚拟环境
            if sys.platform == "win32":
                cmd = f'"{activate_script}" && cd "{web_api_dir}" && python start_web_api.py'
                subprocess.run(cmd, shell=True)
            else:
                # Unix/Linux
                cmd = f'source "{activate_script}" && cd "{web_api_dir}" && python start_web_api.py'
                subprocess.run(cmd, shell=True, executable="/bin/bash")
        else:
            print("⚠️  虚拟环境中未找到Python，使用系统Python")
            subprocess.run([sys.executable, str(web_api_dir / "start_web_api.py")])
    else:
        print("⚠️  未找到虚拟环境，使用系统Python")
        subprocess.run([sys.executable, str(web_api_dir / "start_web_api.py")])

if __name__ == "__main__":
    main()
