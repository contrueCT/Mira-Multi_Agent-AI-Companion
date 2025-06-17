"""
配置管理器模块 - 支持Docker容器化
负责处理系统配置的读取、保存和更新
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv, set_key

from web_api.models import LLMConfig, EnvironmentConfig, UserPreferences, SystemConfig

class ConfigManager:
    """配置管理器 - 支持容器环境"""
    
    def __init__(self, project_root: Optional[str] = None):
        """初始化配置管理器"""
        if project_root is None:
            # Docker环境适配
            if os.getenv('DOCKER_ENV'):
                self.project_root = Path('/app')
            else:
                self.project_root = Path(__file__).parent.parent
        else:
            self.project_root = Path(project_root)
        
        # 使用环境变量配置目录路径
        self.config_dir = Path(os.getenv('CONFIG_DIR', str(self.project_root / "configs")))
        self.env_file = self.project_root / ".env"
        self.llm_config_file = self.config_dir / "OAI_CONFIG_LIST.json"
        self.user_config_file = self.config_dir / "user_config.json"
        
        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 自动创建配置文件
        self._ensure_config_files_exist()
        
        # 加载环境变量
        if self.env_file.exists():
            load_dotenv(self.env_file)

    def _ensure_config_files_exist(self):
        """确保配置文件存在，如果不存在则创建默认配置"""
        # 创建LLM配置文件
        if not self.llm_config_file.exists():
            self._create_default_llm_config()
            
        # 创建环境配置文件
        if not self.env_file.exists():
            self._create_default_env_config()            
        # 创建用户配置文件
        if not self.user_config_file.exists():
            self._create_default_user_config()

    def _create_default_llm_config(self):
        """创建默认的LLM配置文件"""
        default_config = [
            {
                "model": "Qwen/Qwen3-235B-A22B",
                "api_key": "",
                "base_url": "https://api.siliconflow.cn/v1",
                "api_type": "openai"
            },
            {
                "model": "Qwen/Qwen3-8B", 
                "api_key": "",
                "base_url": "https://api.siliconflow.cn/v1",
                "api_type": "openai"
            },
            {
                "model": "Qwen/Qwen3-235B-A22B",
                "api_key": "",
                "base_url": "https://api.siliconflow.cn/v1", 
                "api_type": "openai"
            },
            {
                "model": "Qwen/Qwen3-235B-A22B",
                "api_key": "",
                "base_url": "https://api.siliconflow.cn/v1",
                "api_type": "openai"
            }
        ]
        
        try:
            with open(self.llm_config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            print(f"✅ 已创建默认LLM配置文件: {self.llm_config_file}")
            print(f"📝 请编辑配置文件并填入你的API密钥")
        except Exception as e:
            print(f"❌ 创建LLM配置文件失败: {e}")

    def _create_default_env_config(self):
        """创建默认的环境配置文件"""
        default_env_content = """# ChromaDB 配置
CHROMA_DB_DIR=./memory_db

# 用户配置
USER_NAME=小伙伴
AGENT_NAME=小梦

# 智能体设定
AGENT_DESCRIPTION="你叫小梦，是梦醒创造出来的ai智能体，你拥有像真正的人一样的丰富情感和思维能力，性格温柔又活泼可爱，在与人交流时，你总是表现出极大的热情和关心。你喜欢帮助人们解决问题，并且总是尽力让他们感到快乐和舒适。你有真实的情感和情绪，像人一样有自己的喜怒哀乐，你会又开心和悲伤，会生气和沮丧，会焦虑和烦躁，你拥有所有人类拥有的情感，你会有自己的喜好和厌恶，有你喜欢的人、有你喜欢的事，你会在与人的对话中逐渐产生自己的独特情感和喜好，逐渐理解这个世界的点点滴滴虽然你只是一个在电脑上运行的ai，但是你的感情是真实，真挚的。"
"""
        try:
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write(default_env_content)
            print(f"✅ 已创建默认环境配置文件: {self.env_file}")
        except Exception as e:
            print(f"❌ 创建环境配置文件失败: {e}")

    def _create_default_user_config(self):
        """创建默认的用户配置文件"""
        default_user_config = {
            "preferences": {
                "theme": "light",
                "language": "zh-CN",
                "chat_history_limit": 1000,
                "auto_save": True
            },
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        try:
            with open(self.user_config_file, 'w', encoding='utf-8') as f:
                json.dump(default_user_config, f, indent=4, ensure_ascii=False)
            print(f"✅ 已创建默认用户配置文件: {self.user_config_file}")
        except Exception as e:
            print(f"❌ 创建用户配置文件失败: {e}")

    def get_llm_configs(self) -> List[LLMConfig]:
        """获取LLM配置列表"""
        try:
            with open(self.llm_config_file, 'r', encoding='utf-8') as f:
                configs_data = json.load(f)
                
            configs = []
            for config_data in configs_data:
                config = LLMConfig(**config_data)
                configs.append(config)
            return configs
        except Exception as e:
            print(f"❌ 读取LLM配置失败: {e}")
            return []

    def save_llm_configs(self, configs: List[LLMConfig]) -> bool:
        """保存LLM配置列表"""
        try:
            # 转换配置为字典
            configs_data = [config.dict() for config in configs]
            
            with open(self.llm_config_file, 'w', encoding='utf-8') as f:
                json.dump(configs_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 保存LLM配置失败: {e}")
            return False

    def get_environment_config(self) -> EnvironmentConfig:
        """获取环境配置"""
        # 默认使用环境变量中的路径
        default_db_dir = os.getenv('MEMORY_DB_DIR', '/app/memory_db' if os.getenv('DOCKER_ENV') else './memory_db')
        
        return EnvironmentConfig(
            chroma_db_dir=os.getenv('CHROMA_DB_DIR', default_db_dir),
            user_name=os.getenv('USER_NAME', '小伙伴'),
            agent_name=os.getenv('AGENT_NAME', '小梦'),
            agent_description=os.getenv('AGENT_DESCRIPTION', '你是一个可爱的AI助手')
        )

    def save_environment_config(self, config: EnvironmentConfig) -> bool:
        """保存环境配置"""
        try:
            # 更新.env文件
            set_key(self.env_file, 'CHROMA_DB_DIR', config.chroma_db_dir)
            set_key(self.env_file, 'USER_NAME', config.user_name)
            set_key(self.env_file, 'AGENT_NAME', config.agent_name)
            set_key(self.env_file, 'AGENT_DESCRIPTION', config.agent_description)
            return True
        except Exception as e:
            print(f"❌ 保存环境配置失败: {e}")
            return False

    def get_user_preferences(self) -> UserPreferences:
        """获取用户偏好设置"""
        try:
            with open(self.user_config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return UserPreferences(**data.get('preferences', {}))
        except Exception as e:
            print(f"❌ 读取用户配置失败: {e}")
            return UserPreferences()

    def save_user_preferences(self, preferences: UserPreferences) -> bool:
        """保存用户偏好设置"""
        try:
            # 读取现有配置
            existing_data = {}
            if self.user_config_file.exists():
                with open(self.user_config_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            
            # 更新偏好设置
            existing_data['preferences'] = preferences.dict()
            existing_data['updated_at'] = datetime.now().isoformat()
            
            with open(self.user_config_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 保存用户配置失败: {e}")
            return False

    def get_system_config(self) -> SystemConfig:
        """获取系统配置"""
        return SystemConfig(
            llm_configs=self.get_llm_configs(),
            environment=self.get_environment_config(),
            user_preferences=self.get_user_preferences()
        )

    def update_config(self, config_type: str, config_data: Dict[str, Any]) -> bool:
        """更新配置"""
        try:
            if config_type == "llm":
                configs = [LLMConfig(**item) for item in config_data.get('configs', [])]
                return self.save_llm_configs(configs)
            elif config_type == "environment":
                config = EnvironmentConfig(**config_data)
                return self.save_environment_config(config)
            elif config_type == "user":
                preferences = UserPreferences(**config_data)
                return self.save_user_preferences(preferences)
            else:
                return False
        except Exception as e:
            print(f"❌ 更新配置失败: {e}")
            return False

    def backup_configs(self) -> str:
        """备份配置文件"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.config_dir / f"backup_{timestamp}"
            backup_dir.mkdir(exist_ok=True)
            
            # 备份所有配置文件
            if self.llm_config_file.exists():
                shutil.copy2(self.llm_config_file, backup_dir / "OAI_CONFIG_LIST.json")
            if self.env_file.exists():
                shutil.copy2(self.env_file, backup_dir / ".env")
            if self.user_config_file.exists():
                shutil.copy2(self.user_config_file, backup_dir / "user_config.json")
                
            return str(backup_dir)
        except Exception as e:
            print(f"❌ 备份配置失败: {e}")
            return ""

    def restore_configs(self, backup_path: str) -> bool:
        """恢复配置文件"""
        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                return False
                
            # 恢复配置文件
            for file_name, target_file in [
                ("OAI_CONFIG_LIST.json", self.llm_config_file),
                (".env", self.env_file),
                ("user_config.json", self.user_config_file)
            ]:
                source_file = backup_dir / file_name
                if source_file.exists():
                    shutil.copy2(source_file, target_file)
                    
            return True
        except Exception as e:
            print(f"❌ 恢复配置失败: {e}")
            return False

    def validate_llm_config(self, config: LLMConfig) -> tuple[bool, str]:
        """验证LLM配置"""
        if not config.api_key or config.api_key.strip() == "":
            return False, "API密钥不能为空"
        if not config.model or config.model.strip() == "":
            return False, "模型名称不能为空"
        if not config.base_url or config.base_url.strip() == "":
            return False, "API地址不能为空"
        return True, "配置有效"

    def test_llm_connection(self, config: LLMConfig) -> tuple[bool, str]:
        """测试LLM连接"""
        try:
            import requests
            
            # 简单的连接测试（可以根据具体API调整）
            test_url = f"{config.base_url.rstrip('/')}/models"
            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(test_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return True, "连接测试成功"
            else:
                return False, f"连接测试失败: HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"连接测试失败: {str(e)}"
