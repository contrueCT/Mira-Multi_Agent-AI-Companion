"""
视觉效果控制器模块
提供智能体控制客户端视觉效果的功能
"""

import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class VisualEffect:
    """视觉效果数据类"""
    effect_type: str  # "temporary" 或 "persistent"
    effect_name: str
    duration: int  # 毫秒
    intensity: float  # 0.0-1.0
    parameters: Dict[str, Any]


class VisualEffectsController:
    """视觉效果控制器"""
    
    def __init__(self):
        """初始化效果预设"""
        self.effect_presets = self._init_effect_presets()
        self.keyword_mappings = self._init_keyword_mappings()
    
    def _init_effect_presets(self) -> Dict[str, Dict[str, Any]]:
        """初始化效果预设字典"""
        return {
            # 临时动画效果
            "temporary": {
                "celebration": {
                    "name": "烟花庆祝",
                    "default_duration": 3000,
                    "parameters": {
                        "particle_count": 50,
                        "colors": ["#ff6b6b", "#4ecdc4", "#45b7d1", "#f9ca24"],
                        "animation_speed": 1.0,
                        "spread_radius": 300,
                        "gravity": 0.5
                    },
                    "intensity_effects": {
                        "particle_count": (20, 100),
                        "animation_speed": (0.5, 2.0),
                        "spread_radius": (150, 500)
                    }
                },
                "hearts": {
                    "name": "飘落爱心",
                    "default_duration": 2500,
                    "parameters": {
                        "heart_count": 15,
                        "colors": ["#ff69b4", "#ff1493", "#dc143c"],
                        "fall_speed": 1.0,
                        "swing_amplitude": 30,
                        "size_range": [20, 40]
                    },
                    "intensity_effects": {
                        "heart_count": (5, 30),
                        "fall_speed": (0.5, 1.8),
                        "swing_amplitude": (15, 60)
                    }
                },
                "sparkles": {
                    "name": "闪烁星光",
                    "default_duration": 2000,
                    "parameters": {
                        "sparkle_count": 25,
                        "colors": ["#ffd700", "#ffff00", "#ffffff", "#87ceeb"],
                        "twinkle_speed": 1.2,
                        "opacity_range": [0.3, 1.0],
                        "size_range": [8, 16]
                    },
                    "intensity_effects": {
                        "sparkle_count": (10, 50),
                        "twinkle_speed": (0.6, 2.0),
                        "opacity_range": ([0.2, 0.8], [0.4, 1.0])
                    }
                },
                "bubbles": {
                    "name": "漂浮气泡",
                    "default_duration": 4000,
                    "parameters": {
                        "bubble_count": 20,
                        "colors": ["rgba(135,206,235,0.6)", "rgba(173,216,230,0.6)", "rgba(240,248,255,0.7)"],
                        "float_speed": 0.8,
                        "size_range": [15, 45],
                        "wobble_intensity": 1.0
                    },
                    "intensity_effects": {
                        "bubble_count": (8, 40),
                        "float_speed": (0.4, 1.5),
                        "wobble_intensity": (0.5, 2.0)
                    }
                },
                "flower_petals": {
                    "name": "花瓣飘落",
                    "default_duration": 3500,
                    "parameters": {
                        "petal_count": 18,
                        "colors": ["#ff69b4", "#ffc0cb", "#ffb6c1", "#f0e68c"],
                        "fall_speed": 0.6,
                        "rotation_speed": 1.0,
                        "wind_effect": 0.3
                    },
                    "intensity_effects": {
                        "petal_count": (8, 35),
                        "fall_speed": (0.3, 1.2),
                        "rotation_speed": (0.5, 2.0)
                    }
                }
            },
            # 持久性效果
            "persistent": {
                "warm_theme": {
                    "name": "温暖主题",
                    "default_duration": 0,  # 持续效果无时间限制
                    "parameters": {
                        "background_gradient": {
                            "start": "#ff9a9e",
                            "middle": "#fecfef",
                            "end": "#fecfef"
                        },
                        "accent_color": "#ff6b6b",
                        "text_color": "#2c3e50",
                        "brightness": 1.0,
                        "saturation": 1.0
                    },
                    "intensity_effects": {
                        "brightness": (0.7, 1.2),
                        "saturation": (0.6, 1.4)
                    }
                },
                "cool_theme": {
                    "name": "清凉主题",
                    "default_duration": 0,
                    "parameters": {
                        "background_gradient": {
                            "start": "#a8e6cf",
                            "middle": "#dcedc1",
                            "end": "#ffd3a5"
                        },
                        "accent_color": "#4ecdc4",
                        "text_color": "#2c3e50",
                        "brightness": 1.0,
                        "saturation": 0.9
                    },
                    "intensity_effects": {
                        "brightness": (0.8, 1.1),
                        "saturation": (0.5, 1.2)
                    }
                },
                "sunset_theme": {
                    "name": "夕阳主题",
                    "default_duration": 0,
                    "parameters": {
                        "background_gradient": {
                            "start": "#ff7e5f",
                            "middle": "#feb47b",
                            "end": "#ff6b6b"
                        },
                        "accent_color": "#ff5722",
                        "text_color": "#ffffff",
                        "brightness": 0.9,
                        "saturation": 1.1
                    },
                    "intensity_effects": {
                        "brightness": (0.7, 1.0),
                        "saturation": (0.8, 1.3)
                    }
                },
                "night_theme": {
                    "name": "夜晚主题",
                    "default_duration": 0,
                    "parameters": {
                        "background_gradient": {
                            "start": "#2c3e50",
                            "middle": "#34495e",
                            "end": "#2c3e50"
                        },
                        "accent_color": "#3498db",
                        "text_color": "#ecf0f1",
                        "brightness": 0.8,
                        "saturation": 0.7
                    },
                    "intensity_effects": {
                        "brightness": (0.6, 0.9),
                        "saturation": (0.5, 1.0)
                    }
                },
                "spring_theme": {
                    "name": "春日主题",
                    "default_duration": 0,
                    "parameters": {
                        "background_gradient": {
                            "start": "#a8e6cf",
                            "middle": "#dcedc8",
                            "end": "#c8e6c9"
                        },
                        "accent_color": "#4caf50",
                        "text_color": "#2e7d32",
                        "brightness": 1.1,
                        "saturation": 1.0
                    },
                    "intensity_effects": {
                        "brightness": (0.9, 1.3),
                        "saturation": (0.7, 1.2)
                    }
                }
            }
        }
    
    def _init_keyword_mappings(self) -> Dict[str, Dict[str, List[str]]]:
        """初始化关键词映射"""
        return {
            "temporary": {
                "celebration": ["庆祝", "祝贺", "恭喜", "开心", "高兴", "兴奋", "烟花", "派对", "成功"],
                "hearts": ["爱心", "喜欢", "爱", "浪漫", "甜蜜", "温柔", "心动", "爱意"],
                "sparkles": ["闪亮", "美丽", "漂亮", "灿烂", "光芒", "星星", "梦幻", "魔法"],
                "bubbles": ["轻松", "愉快", "放松", "舒适", "清新", "自由", "飘逸", "梦境"],
                "flower_petals": ["优雅", "温馨", "柔美", "诗意", "浪漫", "花朵", "春天", "美好"]
            },
            "persistent": {
                "warm_theme": ["温暖", "温馨", "舒适", "温和", "亲切", "友好", "安全", "温柔"],
                "cool_theme": ["清凉", "清新", "冷静", "平静", "宁静", "理性", "清爽", "舒缓"],
                "sunset_theme": ["夕阳", "黄昏", "浪漫", "温暖", "金色", "橙色", "怀旧", "温馨"],
                "night_theme": ["夜晚", "深沉", "安静", "神秘", "思考", "沉思", "冷静", "专注"],
                "spring_theme": ["春天", "生机", "希望", "活力", "新鲜", "成长", "绿色", "自然"]
            }
        }
    
    def map_description_to_effect(self, description: str, effect_type: str = "auto") -> Optional[str]:
        """
        将效果描述映射到具体效果名称
        
        Args:
            description: 效果描述字符串
            effect_type: 效果类型 ("temporary", "persistent", "auto")
        
        Returns:
            效果名称，如果未找到匹配则返回None
        """
        description_lower = description.lower()
        
        # 如果指定了效果类型，只在该类型中搜索
        if effect_type in ["temporary", "persistent"]:
            search_types = [effect_type]
        else:
            # 自动模式：先搜索临时效果，再搜索持久效果
            search_types = ["temporary", "persistent"]
        
        for etype in search_types:
            for effect_name, keywords in self.keyword_mappings[etype].items():
                for keyword in keywords:
                    if keyword in description_lower:
                        return effect_name
        
        return None
    
    def apply_intensity_to_effect(self, effect_name: str, effect_type: str, 
                                 intensity: float) -> Dict[str, Any]:
        """
        根据强度参数调整效果配置
        
        Args:
            effect_name: 效果名称
            effect_type: 效果类型
            intensity: 强度值 (0.0-1.0)
        
        Returns:
            调整后的效果参数字典
        """
        if effect_type not in self.effect_presets:
            return {}
        
        if effect_name not in self.effect_presets[effect_type]:
            return {}
        
        preset = self.effect_presets[effect_type][effect_name]
        result_params = preset["parameters"].copy()
        
        # 应用强度调整
        if "intensity_effects" in preset:
            intensity_config = preset["intensity_effects"]
            
            for param_name, intensity_range in intensity_config.items():
                if param_name in result_params:
                    if isinstance(intensity_range, tuple) and len(intensity_range) == 2:
                        min_val, max_val = intensity_range
                        
                        if isinstance(min_val, (int, float)) and isinstance(max_val, (int, float)):
                            # 数值参数插值
                            result_params[param_name] = min_val + (max_val - min_val) * intensity
                        elif isinstance(min_val, list) and isinstance(max_val, list):
                            # 列表参数插值（如opacity_range）
                            result_list = []
                            for i in range(len(min_val)):
                                if i < len(max_val):
                                    val = min_val[i] + (max_val[i] - min_val[i]) * intensity
                                    result_list.append(val)
                            result_params[param_name] = result_list
        
        return result_params
    
    def create_effect_command(self, effect_description: str, duration: int = None, 
                            intensity: float = 0.5, effect_type: str = "auto") -> Optional[Dict[str, Any]]:
        """
        创建视觉效果指令
        
        Args:
            effect_description: 效果描述
            duration: 持续时间（毫秒）
            intensity: 效果强度 (0.0-1.0)
            effect_type: 效果类型
        
        Returns:
            效果指令字典，如果创建失败则返回None
        """
        # 映射效果描述到具体效果
        effect_name = self.map_description_to_effect(effect_description, effect_type)
        
        if not effect_name:
            return None
        
        # 确定实际的效果类型
        actual_type = None
        for etype in ["temporary", "persistent"]:
            if effect_name in self.effect_presets[etype]:
                actual_type = etype
                break
        
        if not actual_type:
            return None
        
        # 获取效果预设
        preset = self.effect_presets[actual_type][effect_name]
        
        # 应用强度调整
        adjusted_params = self.apply_intensity_to_effect(effect_name, actual_type, intensity)
        
        # 确定持续时间
        if duration is None:
            duration = preset["default_duration"]
        
        # 创建指令
        command = {
            "type": "visual_effect",
            "effect_type": actual_type,
            "effect_name": effect_name,
            "display_name": preset["name"],
            "duration": duration,
            "intensity": intensity,
            "parameters": adjusted_params,
            "timestamp": None  # 将在发送时添加
        }
        
        return command
    
    def get_available_effects(self) -> Dict[str, List[str]]:
        """获取所有可用效果列表"""
        return {
            "temporary": list(self.effect_presets["temporary"].keys()),
            "persistent": list(self.effect_presets["persistent"].keys())
        }
    
    def get_effect_keywords(self, effect_name: str = None) -> Dict[str, Any]:
        """获取效果关键词映射"""
        if effect_name:
            # 查找特定效果的关键词
            for etype in ["temporary", "persistent"]:
                if effect_name in self.keyword_mappings[etype]:
                    return {
                        "effect_type": etype,
                        "keywords": self.keyword_mappings[etype][effect_name]
                    }
            return {}
        else:
            # 返回所有关键词映射
            return self.keyword_mappings


# 创建全局控制器实例
visual_effects_controller = VisualEffectsController()


def map_description_to_effect(description: str, effect_type: str = "auto") -> Optional[str]:
    """便捷函数：映射效果描述到效果名称"""
    return visual_effects_controller.map_description_to_effect(description, effect_type)


def create_effect_command(effect_description: str, duration: int = None, 
                         intensity: float = 0.5, effect_type: str = "auto") -> Optional[Dict[str, Any]]:
    """便捷函数：创建视觉效果指令"""
    return visual_effects_controller.create_effect_command(
        effect_description, duration, intensity, effect_type
    )
