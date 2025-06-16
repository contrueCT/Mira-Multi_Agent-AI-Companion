"""
配置管理器模块
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
    """配置管理器"""
    
    def __init__(self, project_root: Optional[str] = None):
        """初始化配置管理器"""
        if project_root is None:
            self.project_root = Path(__file__).parent.parent
        else:
            self.project_root = Path(project_root)
        
        self.config_dir = self.project_root / "configs"
        self.env_file = self.project_root / ".env"
        self.llm_config_file = self.config_dir / "OAI_CONFIG_LIST.json"
        self.user_config_file = self.config_dir / "user_config.json"
        
        # 确保配置目录存在
        self.config_dir.mkdir(exist_ok=True)
        
        # 加载环境变量
        if self.env_file.exists():
            load_dotenv(self.env_file)
    
    def get_system_config(self) -> SystemConfig:
        """获取完整的系统配置"""
        return SystemConfig(
            llm_configs=self.get_llm_configs(),
            environment=self.get_environment_config(),
            user_preferences=self.get_user_preferences(),
            last_updated=datetime.now()
        )
    
    def get_llm_configs(self) -> List[LLMConfig]:
        """获取LLM配置列表"""
        try:
            if not self.llm_config_file.exists():
                return []
            
            with open(self.llm_config_file, 'r', encoding='utf-8') as f:
                configs_data = json.load(f)
            
            return [LLMConfig(**config) for config in configs_data]
        except Exception as e:
            print(f"读取LLM配置失败: {e}")
            return []
    
    def save_llm_configs(self, configs: List[LLMConfig]) -> bool:
        """保存LLM配置列表"""
        try:
            # 备份原文件
            if self.llm_config_file.exists():
                backup_file = self.llm_config_file.with_suffix('.json.backup')
                shutil.copy2(self.llm_config_file, backup_file)
            
            # 保存新配置
            configs_data = [config.dict() for config in configs]
            with open(self.llm_config_file, 'w', encoding='utf-8') as f:
                json.dump(configs_data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ LLM配置已保存到: {self.llm_config_file}")
            return True
        except Exception as e:
            print(f"❌ 保存LLM配置失败: {e}")
            return False
    
    def get_environment_config(self) -> EnvironmentConfig:
        """获取环境配置"""
        return EnvironmentConfig(
            chroma_db_dir=os.getenv('CHROMA_DB_DIR', './memory_db'),
            user_name=os.getenv('USER_NAME', '梦醒'),
            agent_name=os.getenv('AGENT_NAME', '小梦'),
            agent_description=os.getenv('AGENT_DESCRIPTION', '你是一个可爱的AI助手')
        )
    
    def save_environment_config(self, config: EnvironmentConfig) -> bool:
        """保存环境配置到.env文件"""
        try:
            # 确保.env文件存在
            if not self.env_file.exists():
                self.env_file.touch()
            
            # 更新环境变量
            set_key(str(self.env_file), 'CHROMA_DB_DIR', config.chroma_db_dir)
            set_key(str(self.env_file), 'USER_NAME', config.user_name)
            set_key(str(self.env_file), 'AGENT_NAME', config.agent_name)
            set_key(str(self.env_file), 'AGENT_DESCRIPTION', config.agent_description)
            
            # 重新加载环境变量
            load_dotenv(self.env_file, override=True)
            
            print(f"✅ 环境配置已保存到: {self.env_file}")
            return True
        except Exception as e:
            print(f"❌ 保存环境配置失败: {e}")
            return False
    
    def get_user_preferences(self) -> UserPreferences:
        """获取用户偏好配置"""
        try:
            if not self.user_config_file.exists():
                # 返回默认配置
                return UserPreferences()
            
            with open(self.user_config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            return UserPreferences(**config_data)
        except Exception as e:
            print(f"读取用户配置失败: {e}")
            return UserPreferences()
    
    def save_user_preferences(self, preferences: UserPreferences) -> bool:
        """保存用户偏好配置"""
        try:
            # 备份原文件
            if self.user_config_file.exists():
                backup_file = self.user_config_file.with_suffix('.json.backup')
                shutil.copy2(self.user_config_file, backup_file)
            
            # 保存新配置
            with open(self.user_config_file, 'w', encoding='utf-8') as f:
                json.dump(preferences.dict(), f, indent=4, ensure_ascii=False)
            
            print(f"✅ 用户配置已保存到: {self.user_config_file}")
            return True
        except Exception as e:
            print(f"❌ 保存用户配置失败: {e}")
            return False
    
    def update_config(self, config_type: str, config_data: Dict[str, Any]) -> bool:
        """更新指定类型的配置"""
        try:
            if config_type == "llm":
                configs = [LLMConfig(**config) for config in config_data.get('configs', [])]
                return self.save_llm_configs(configs)
            
            elif config_type == "environment":
                config = EnvironmentConfig(**config_data)
                return self.save_environment_config(config)
            
            elif config_type == "preferences":
                preferences = UserPreferences(**config_data)
                return self.save_user_preferences(preferences)
            
            else:
                print(f"❌ 未知的配置类型: {config_type}")
                return False
                
        except Exception as e:
            print(f"❌ 更新配置失败: {e}")
            return False
    
    def backup_configs(self) -> str:
        """备份所有配置文件"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.config_dir / f"backup_{timestamp}"
            backup_dir.mkdir(exist_ok=True)
            
            # 备份各类配置文件
            files_to_backup = [
                self.llm_config_file,
                self.env_file,
                self.user_config_file
            ]
            
            for file_path in files_to_backup:
                if file_path.exists():
                    backup_path = backup_dir / file_path.name
                    shutil.copy2(file_path, backup_path)
            
            print(f"✅ 配置备份完成: {backup_dir}")
            return str(backup_dir)
        except Exception as e:
            print(f"❌ 配置备份失败: {e}")
            return ""
    
    def restore_configs(self, backup_path: str) -> bool:
        """从备份恢复配置"""
        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                print(f"❌ 备份目录不存在: {backup_path}")
                return False
            
            # 恢复各类配置文件
            files_to_restore = [
                ("OAI_CONFIG_LIST.json", self.llm_config_file),
                (".env", self.env_file),
                ("user_config.json", self.user_config_file)
            ]
            
            for backup_name, target_path in files_to_restore:
                backup_file = backup_dir / backup_name
                if backup_file.exists():
                    shutil.copy2(backup_file, target_path)
            
            # 重新加载环境变量
            if self.env_file.exists():
                load_dotenv(self.env_file, override=True)
            
            print(f"✅ 配置恢复完成: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ 配置恢复失败: {e}")
            return False
    
    def validate_llm_config(self, config: LLMConfig) -> tuple[bool, str]:
        """验证LLM配置"""
        if not config.model:
            return False, "模型名称不能为空"
        
        if not config.api_key:
            return False, "API密钥不能为空"
        
        if not config.base_url:
            return False, "Base URL不能为空"
        
        if not config.base_url.startswith(('http://', 'https://')):
            return False, "Base URL必须以http://或https://开头"
        
        return True, "配置验证通过"
    
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
