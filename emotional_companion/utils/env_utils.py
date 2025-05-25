"""
环境变量加载工具。
"""
import os
from dotenv import load_dotenv

def load_env_vars():
    """
    加载环境变量
    
    Returns:
        dict: 包含环境变量的字典
    """
    # 加载.env文件
    load_dotenv()
    
    # 获取环境变量
    env_vars = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "OPENAI_API_BASE": os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-4"),
        "USER_NAME": os.getenv("USER_NAME", "用户"),
        "COMPANION_NAME": os.getenv("COMPANION_NAME", "小伙伴"),
        "CHROMA_DB_DIR": os.getenv("CHROMA_DB_DIR", "./memory_db"),
        "CHROMA_COLLECTION": os.getenv("CHROMA_COLLECTION", "emotional_memories")
    }
    
    return env_vars
