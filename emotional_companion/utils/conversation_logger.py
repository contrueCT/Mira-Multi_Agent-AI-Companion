"""
轻量级对话日志记录器
最小化对主要功能代码的影响
"""

import os
from datetime import datetime
from pathlib import Path


class SimpleLogger:
    """极简对话日志记录器 - 支持容器环境"""
    
    def __init__(self, log_dir: str = "logs", enable_console: bool = False):
        # 处理日志目录路径，支持容器环境
        if not os.path.isabs(log_dir):
            if os.getenv('DOCKER_ENV'):
                # Docker环境中使用绝对路径
                self.log_dir = Path(f"/app/{log_dir}")
            else:
                # 本地环境中基于项目根目录
                current_file = Path(__file__)
                project_root = current_file.parent.parent.parent
                self.log_dir = project_root / log_dir
        else:
            self.log_dir = Path(log_dir)
            
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.enable_console = enable_console
        
        # 创建今日日志文件
        today = datetime.now().strftime("%Y-%m-%d")
        self.log_file = self.log_dir / f"chat_{today}.log"
        
        # 对话计数器
        self.count = 0
        
    def log(self, step: str, content: str):
        """统一日志记录方法"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {step}: {content}\n"
        
        # 写入文件
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)
        except:
            pass  # 静默处理文件写入错误
            
        # 可选的控制台输出
        if self.enable_console:
            print(f"📝 {step}")
    
    def new_chat(self, user_input: str):
        """开始新对话"""
        self.count += 1
        self.log("NEW_CHAT", f"#{self.count} | {user_input}")
        
    def step(self, name: str, content: str):
        """记录对话步骤"""
        self.log(name.upper(), content)
