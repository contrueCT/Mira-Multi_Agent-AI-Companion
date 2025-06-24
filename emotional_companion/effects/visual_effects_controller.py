"""
视觉效果控制器模块
提供智能体控制客户端视觉效果的功能
"""

import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher


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
        self.keyword_mappings = self._init_enhanced_keyword_mappings()
        self.emotional_intensity_keywords = self._init_emotional_intensity_keywords()
        self.debug_enabled = True
        self.logger = logging.getLogger(__name__)
    
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
    
    def _init_enhanced_keyword_mappings(self) -> Dict[str, Dict[str, List[str]]]:
        """初始化增强的关键词映射（包含更多同义词和自然表达）"""
        return {
            "temporary": {
                "celebration": [
                    # 直接表达
                    "庆祝", "祝贺", "恭喜", "开心", "高兴", "兴奋", "烟花", "派对", "成功",
                    # 情感表达
                    "太棒了", "好厉害", "真不错", "很棒", "赞", "amazing", "wonderful", "great",
                    # 成就相关
                    "完成了", "做到了", "实现了", "成功了", "达成", "胜利", "获得",
                    # 感叹词
                    "哇", "耶", "太好了", "fantastic", "excellent", "awesome",
                    # 情绪词
                    "激动", "欢呼", "狂欢", "喜悦", "欣喜", "欢乐", "兴奋不已"
                ],
                "hearts": [
                    # 爱意表达
                    "爱心", "喜欢", "爱", "浪漫", "甜蜜", "温柔", "心动", "爱意",
                    # 情感表达
                    "喜爱", "钟爱", "宠爱", "珍爱", "疼爱", "关爱", "深爱",
                    # 温馨词汇
                    "暖心", "感动", "温暖", "贴心", "用心", "真心", "诚心",
                    # 关系词汇
                    "亲密", "亲近", "亲爱", "宝贝", "darling", "honey", "sweet",
                    # 表白相关
                    "表白", "告白", "心意", "情意", "爱慕", "倾心", "动情"
                ],
                "sparkles": [
                    # 美丽表达
                    "闪亮", "美丽", "漂亮", "灿烂", "光芒", "星星", "梦幻", "魔法",
                    # 赞美词汇
                    "gorgeous", "beautiful", "stunning", "brilliant", "shining", "glowing",
                    # 梦幻词汇
                    "仙女", "公主", "女神", "天使", "精灵", "童话", "梦境",
                    # 光亮词汇
                    "发光", "闪闪", "亮晶晶", "璀璨", "耀眼", "夺目", "炫目",
                    # 魔法词汇
                    "魔法", "魔幻", "奇迹", "神奇", "magical", "miracle", "wonder"
                ],
                "bubbles": [
                    # 轻松表达
                    "轻松", "愉快", "放松", "舒适", "清新", "自由", "飘逸", "梦境",
                    # 心情词汇
                    "心情好", "轻快", "舒服", "comfortable", "peaceful", "calm", "serene",
                    # 自由词汇
                    "解脱", "释放", "自在", "无忧", "快活", "逍遥", "畅快",
                    # 清新词汇
                    "清爽", "新鲜", "pure", "fresh", "clean", "crisp",
                    # 梦幻词汇
                    "飘飘然", "如梦", "如仙", "ethereal", "dreamy", "floating"
                ],
                "flower_petals": [
                    # 优雅表达
                    "优雅", "温馨", "柔美", "诗意", "浪漫", "花朵", "春天", "美好",
                    # 春天词汇
                    "春日", "春光", "春意", "spring", "blossom", "bloom", "garden",
                    # 柔美词汇
                    "柔软", "轻柔", "gentle", "soft", "tender", "delicate",
                    # 花卉词汇
                    "花瓣", "花香", "花海", "樱花", "桃花", "梅花", "玫瑰",
                    # 诗意词汇
                    "诗情画意", "如诗", "如画", "poetic", "artistic", "elegant"
                ]
            },
            "persistent": {
                "warm_theme": [
                    # 温暖表达
                    "温暖", "温馨", "舒适", "温和", "亲切", "友好", "安全", "温柔",
                    # 家的感觉
                    "家的感觉", "像家一样", "归属感", "安全感", "踏实", "安心",
                    # 情感词汇
                    "暖暖的", "暖心", "贴心", "窝心", "cozy", "warm", "comfortable",
                    # 关怀词汇
                    "关怀", "呵护", "照顾", "体贴", "细心", "用心", "caring",
                    # 氛围词汇
                    "温馨的氛围", "暖色调", "橙色", "黄色", "阳光", "sunset"
                ],
                "cool_theme": [
                    # 清凉表达
                    "清凉", "清新", "冷静", "平静", "宁静", "理性", "清爽", "舒缓",
                    # 冷静词汇
                    "淡定", "沉着", "镇静", "冷静思考", "理智", "客观", "rational",
                    # 清新词汇
                    "清香", "清淡", "清雅", "素雅", "淡雅", "fresh", "clean",
                    # 蓝绿色调
                    "蓝色", "绿色", "青色", "薄荷", "海洋", "天空", "blue", "green",
                    # 氛围词汇
                    "宁静致远", "静谧", "安宁", "peaceful", "serene", "tranquil"
                ],
                "sunset_theme": [
                    # 夕阳表达
                    "夕阳", "黄昏", "浪漫", "温暖", "金色", "橙色", "怀旧", "温馨",
                    # 时间词汇
                    "傍晚", "落日", "余晖", "残阳", "sunset", "dusk", "twilight",
                    # 色彩词汇
                    "金黄", "橙红", "玫瑰金", "amber", "golden", "orange", "pink",
                    # 情感词汇
                    "怀念", "回忆", "往昔", "nostalgic", "romantic", "dreamy",
                    # 美景词汇
                    "美景", "如画", "绚烂", "壮观", "magnificent", "gorgeous"
                ],
                "night_theme": [
                    # 夜晚表达
                    "夜晚", "深沉", "安静", "神秘", "思考", "沉思", "冷静", "专注",
                    # 夜色词汇
                    "夜色", "夜幕", "月色", "星空", "night", "midnight", "dark",
                    # 思考词汇
                    "深度思考", "冥想", "反思", "contemplation", "meditation", "focus",
                    # 神秘词汇
                    "神秘感", "深邃", "mysterious", "enigmatic", "profound",
                    # 氛围词汇
                    "静谧", "幽静", "寂静", "quiet", "silent", "peaceful"
                ],
                "spring_theme": [
                    # 春天表达
                    "春天", "生机", "希望", "活力", "新鲜", "成长", "绿色", "自然",
                    # 生命词汇
                    "生命力", "朝气", "青春", "蓬勃", "vitality", "energy", "life",
                    # 成长词汇
                    "萌芽", "发芽", "开花", "绽放", "bloom", "grow", "flourish",
                    # 希望词汇
                    "新开始", "新起点", "充满希望", "hopeful", "optimistic", "bright",
                    # 自然词汇
                    "大自然", "森林", "草地", "nature", "green", "natural", "eco"
                ]
            }
        }
    
    def _init_emotional_intensity_keywords(self) -> Dict[str, float]:
        """初始化情感强度关键词映射"""
        return {
            # 高强度词汇 (0.8-1.0)
            "超级": 0.9, "非常": 0.8, "极其": 0.9, "特别": 0.8, "相当": 0.8,
            "太": 0.9, "最": 1.0, "异常": 0.9, "格外": 0.8, "尤其": 0.8,
            "extraordinarily": 0.9, "extremely": 0.9, "incredibly": 0.9,
            "super": 0.8, "very": 0.8, "really": 0.8, "so": 0.8,
            
            # 中等强度词汇 (0.5-0.7)
            "比较": 0.6, "还是": 0.6, "挺": 0.6, "蛮": 0.6, "颇": 0.6,
            "还算": 0.5, "算是": 0.5, "有点": 0.5, "一些": 0.5, "稍微": 0.4,
            "quite": 0.6, "pretty": 0.6, "fairly": 0.6, "rather": 0.6,
            "somewhat": 0.5, "a bit": 0.4, "slightly": 0.4,
            
            # 强调词汇
            "真的": 0.8, "确实": 0.7, "的确": 0.7, "实在": 0.7, "着实": 0.7,
            "truly": 0.8, "really": 0.8, "indeed": 0.7, "actually": 0.7
        }

    def _log_debug_info(self, message: str):
        """调试信息日志"""
        if self.debug_enabled:
            self.logger.debug(message)
    
    def _fuzzy_match_keyword(self, description: str, keywords: List[str]) -> Tuple[str, float]:
        """
        模糊匹配关键词，返回最佳匹配及其相似度
        
        Args:
            description: 效果描述字符串
            keywords: 关键词列表
        
        Returns:
            最佳匹配的关键词及其相似度（0-1），如果无匹配则返回空串和0
        """
        best_match = ""
        best_score = 0.0
        
        for keyword in keywords:
            # 计算相似度
            score = SequenceMatcher(None, description, keyword).ratio()
            
            if score > best_score:
                best_score = score
                best_match = keyword
        
        return best_match, best_score
    
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
                # 精确匹配
                if description_lower in keywords:
                    return effect_name
                
                # 模糊匹配
                best_match, score = self._fuzzy_match_keyword(description_lower, keywords)
                
                if score > 0.7:  # 相似度阈值
                    self._log_debug_info(f"模糊匹配成功：{description} -> {best_match} (相似度: {score})")
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
        创建视觉效果指令（增强版）
        
        Args:
            effect_description: 效果描述
            duration: 持续时间（毫秒）
            intensity: 效果强度 (0.0-1.0)，如果为None则自动推断
            effect_type: 效果类型
        
        Returns:
            效果指令字典，如果创建失败则返回None
        """
        # 使用增强映射
        mapping_result = self.enhanced_description_mapping(effect_description, effect_type)
        
        if not mapping_result:
            if self.debug_enabled:
                self.logger.warning(f"无法识别效果描述: '{effect_description}' - 尝试使用fallback策略")
            
            # Fallback: 尝试更宽松的匹配
            fallback_result = self._fallback_matching(effect_description, effect_type)
            if fallback_result:
                mapping_result = fallback_result
            else:
                return None
        
        effect_name, estimated_intensity, actual_type = mapping_result
        
        # 使用推断的强度（如果没有明确指定）
        if intensity == 0.5:  # 默认值，使用推断强度
            final_intensity = estimated_intensity
        else:
            final_intensity = intensity
        
        # 获取效果预设
        preset = self.effect_presets[actual_type][effect_name]
        
        # 应用强度调整
        adjusted_params = self.apply_intensity_to_effect(effect_name, actual_type, final_intensity)
        
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
            "intensity": final_intensity,
            "parameters": adjusted_params,
            "timestamp": None,  # 将在发送时添加
            "debug_info": {
                "original_description": effect_description,
                "estimated_intensity": estimated_intensity,
                "final_intensity": final_intensity,
                "selected_type": actual_type
            } if self.debug_enabled else None
        }
        
        if self.debug_enabled:
            self.logger.info(f"创建视觉效果指令: {effect_name} ({actual_type}) 强度:{final_intensity:.2f}")
        
        return command
    
    def _fallback_matching(self, description: str, effect_type: str = "auto") -> Optional[Tuple[str, float, str]]:
        """
        备用匹配策略：更宽松的匹配规则
        """
        description_lower = description.lower()
        
        # 情感词汇到效果的直接映射
        emotion_mappings = {
            "开心": ("celebration", 0.7, "temporary"),
            "高兴": ("celebration", 0.7, "temporary"),
            "兴奋": ("celebration", 0.8, "temporary"),
            "激动": ("celebration", 0.8, "temporary"),
            "喜欢": ("hearts", 0.6, "temporary"),
            "爱": ("hearts", 0.8, "temporary"),
            "美": ("sparkles", 0.6, "temporary"),
            "漂亮": ("sparkles", 0.6, "temporary"),
            "舒服": ("bubbles", 0.5, "temporary"),
            "轻松": ("bubbles", 0.5, "temporary"),
            "温暖": ("warm_theme", 0.6, "persistent"),
            "冷静": ("cool_theme", 0.5, "persistent"),
            "夜": ("night_theme", 0.5, "persistent"),
            "春": ("spring_theme", 0.6, "persistent"),
        }
        
        for emotion, (effect, intensity, etype) in emotion_mappings.items():
            if emotion in description_lower:
                if effect_type == "auto" or effect_type == etype:
                    if self.debug_enabled:
                        self.logger.info(f"Fallback匹配成功: '{emotion}' -> {effect}")
                    return (effect, intensity, etype)
        
        return None
    
    def test_description_matching(self, descriptions: List[str]) -> Dict[str, Any]:
        """
        测试描述匹配效果（调试用）
        """
        results = {}
        
        for desc in descriptions:
            result = self.enhanced_description_mapping(desc)
            if result:
                effect_name, intensity, effect_type = result
                results[desc] = {
                    "effect_name": effect_name,
                    "intensity": intensity,
                    "effect_type": effect_type,
                    "success": True
                }
            else:
                results[desc] = {
                    "effect_name": None,
                    "intensity": 0.5,
                    "effect_type": None,
                    "success": False
                }
        
        return results
    
    def get_debug_info(self) -> Dict[str, Any]:
        """获取调试信息"""
        return {
            "total_effects": {
                "temporary": len(self.effect_presets["temporary"]),
                "persistent": len(self.effect_presets["persistent"])
            },
            "total_keywords": {
                "temporary": sum(len(keywords) for keywords in self.keyword_mappings["temporary"].values()),
                "persistent": sum(len(keywords) for keywords in self.keyword_mappings["persistent"].values())
            },
            "intensity_keywords": len(self.emotional_intensity_keywords),
            "debug_enabled": self.debug_enabled
        }
    
    def set_debug_mode(self, enabled: bool):
        """设置调试模式"""
        self.debug_enabled = enabled
        if enabled:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig(level=logging.WARNING)

    def enhanced_description_mapping(self, description: str, effect_type: str = "auto") -> Optional[Tuple[str, float, str]]:
        """
        增强的效果描述映射，支持语义分析和强度推理
        
        Args:
            description: 效果描述字符串
            effect_type: 效果类型 ("temporary", "persistent", "auto")
        
        Returns:
            (效果名称, 推荐强度, 实际效果类型) 的元组，如果未找到匹配则返回None
        """
        description_lower = description.lower()
        
        # 计算情感强度
        estimated_intensity = self._estimate_intensity_from_text(description_lower)
        
        # 智能选择搜索类型
        if effect_type == "auto":
            search_types = self._smart_effect_type_selection(description_lower)
        elif effect_type in ["temporary", "persistent"]:
            search_types = [effect_type]
        else:
            search_types = ["temporary", "persistent"]
        
        best_match = None
        best_score = 0.0
        best_type = None
        
        for etype in search_types:
            for effect_name, keywords in self.keyword_mappings[etype].items():
                # 计算匹配分数
                match_score = self._calculate_match_score(description_lower, keywords)
                
                if match_score > best_score and match_score > 0.3:  # 最低阈值
                    best_match = effect_name
                    best_score = match_score
                    best_type = etype
        
        if self.debug_enabled and best_match:
            self.logger.info(f"视觉效果匹配: '{description}' -> {best_match} ({best_type}) 分数:{best_score:.2f} 强度:{estimated_intensity:.2f}")
        elif self.debug_enabled:
            self.logger.warning(f"视觉效果未匹配: '{description}' (无合适效果)")
        
        return (best_match, estimated_intensity, best_type) if best_match else None
    
    def _calculate_match_score(self, description: str, keywords: List[str]) -> float:
        """
        计算描述与关键词列表的匹配分数
        使用多种匹配策略来提高准确性
        """
        max_score = 0.0
        
        for keyword in keywords:
            # 1. 精确匹配 (分数: 1.0)
            if keyword in description:
                max_score = max(max_score, 1.0)
                continue
            
            # 2. 模糊匹配 (分数: 0.6-0.9)
            fuzzy_score = SequenceMatcher(None, keyword, description).ratio()
            if fuzzy_score > 0.7:
                max_score = max(max_score, fuzzy_score * 0.9)
                continue
            
            # 3. 部分词匹配 (分数: 0.4-0.8)
            words_in_desc = description.split()
            for word in words_in_desc:
                if len(word) > 1:  # 忽略单字符
                    word_similarity = SequenceMatcher(None, keyword, word).ratio()
                    if word_similarity > 0.8:
                        max_score = max(max_score, word_similarity * 0.8)
                    elif keyword in word or word in keyword:
                        max_score = max(max_score, 0.6)
        
        return max_score
    
    def _estimate_intensity_from_text(self, text: str) -> float:
        """
        从文本中估算情感强度
        """
        base_intensity = 0.5
        intensity_modifiers = []
        
        # 检查强度关键词
        for keyword, intensity_value in self.emotional_intensity_keywords.items():
            if keyword in text:
                intensity_modifiers.append(intensity_value)
        
        # 检查重复词汇（如"好好好"）
        repeated_pattern = re.findall(r'(\w)\1{2,}', text)  # 连续3个或以上相同字符
        if repeated_pattern:
            intensity_modifiers.append(0.8)
        
        # 检查感叹号
        exclamation_count = text.count('!')
        if exclamation_count > 0:
            intensity_modifiers.append(min(0.7 + exclamation_count * 0.1, 1.0))
        
        # 计算最终强度
        if intensity_modifiers:
            # 取最大值，但进行适当调整
            max_modifier = max(intensity_modifiers)
            final_intensity = (base_intensity + max_modifier) / 2
            return min(final_intensity, 1.0)
        
        return base_intensity
    
    def _smart_effect_type_selection(self, description: str) -> List[str]:
        """
        智能选择效果类型优先级
        """
        # 临时效果指示词
        temporary_indicators = [
            "一下", "瞬间", "突然", "刚刚", "马上", "立刻", "现在",
            "moment", "instant", "quick", "now", "sudden"
        ]
        
        # 持久效果指示词
        persistent_indicators = [
            "一直", "始终", "总是", "长期", "持续", "保持", "维持",
            "always", "keep", "maintain", "continue", "stay", "long"
        ]
        
        # 情绪/主题指示词
        theme_indicators = [
            "氛围", "风格", "主题", "调性", "感觉", "环境", "背景",
            "atmosphere", "style", "theme", "mood", "environment"
        ]
        
        # 动作/事件指示词
        action_indicators = [
            "庆祝", "表达", "显示", "展示", "做", "进行", "执行",
            "celebrate", "show", "display", "do", "perform", "action"
        ]
        
        temp_score = sum(1 for indicator in temporary_indicators if indicator in description)
        persist_score = sum(1 for indicator in persistent_indicators if indicator in description)
        theme_score = sum(1 for indicator in theme_indicators if indicator in description)
        action_score = sum(1 for indicator in action_indicators if indicator in description)
        
        # 决策逻辑
        if theme_score > 0 or persist_score > temp_score:
            return ["persistent", "temporary"]
        elif action_score > 0 or temp_score > persist_score:
            return ["temporary", "persistent"]
        else:
            # 默认：优先临时效果
            return ["temporary", "persistent"]

    def map_description_to_effect(self, description: str, effect_type: str = "auto") -> Optional[str]:
        """
        将效果描述映射到具体效果名称（兼容旧接口）
        """
        result = self.enhanced_description_mapping(description, effect_type)
        return result[0] if result else None

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
