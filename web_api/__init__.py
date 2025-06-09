"""
Web API模块初始化文件
"""

__version__ = "1.0.0"
__author__ = "Emotional Companion AI"
__description__ = "小梦情感陪伴AI系统的Web API接口"

# 导入主要的FastAPI应用实例
from .web_api import app

__all__ = ["app"]
