"""
记忆查看工具模块
用于读取和展示向量数据库中存储的各类记忆数据
"""

import json
import os
import pandas as pd
from typing import List, Dict
import sys

# 添加项目根目录到系统路径，支持容器环境
if os.getenv('DOCKER_ENV'):
    sys.path.append('/app')
else:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from emotional_companion.memory.emotional_memory import EmotionalMemorySystem

class MemoryViewer:
    """
    记忆查看工具 - 用于查询和显示情感陪伴智能体的记忆数据库内容
    """
    
    def __init__(self, memory_system=None, persist_directory="memory_db"):
        """
        初始化记忆查看工具
        
        Args:
            memory_system: 已存在的EmotionalMemorySystem实例，如果为None则创建新实例
            persist_directory: 向量数据库的存储目录
        """
        # 处理持久化目录路径，支持容器环境
        if not os.path.isabs(persist_directory):
            if os.getenv('DOCKER_ENV'):
                persist_directory = f"/app/{persist_directory}"
            else:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(current_dir)
                persist_directory = os.path.join(project_root, persist_directory)
                
        self.memory_system = memory_system or EmotionalMemorySystem(persist_directory)
    
    def get_conversation_history(self, 
                                limit: int = 10, 
                                query: str = None, 
                                sort_by_time: bool = True,
                                include_emotions: bool = True) -> List[Dict]:
        """
        获取历史对话记录
        
        Args:
            limit: 返回的最大记录数
            query: 搜索关键词，如果提供则执行语义搜索
            sort_by_time: 是否按时间排序
            include_emotions: 是否包含情绪数据
            
        Returns:
            List[Dict]: 对话记录列表
        """
        if query:
            # 执行语义搜索
            results = self.memory_system.semantic_memory_search(
                query=query,
                collection_name="episodic",
                n_results=limit,
                threshold=0.9  # 允许更宽松的匹配
            )
            conversations = [self._format_conversation_item(item) for item in results]
        else:
            # 获取全部记录
            all_data = self.memory_system.collections["episodic"].get(limit=limit)
            conversations = []
            
            if all_data and "ids" in all_data and all_data["ids"]:
                for i, memory_id in enumerate(all_data["ids"]):
                    item = {
                        "id": memory_id,
                        "content": all_data["documents"][i],
                        "metadata": all_data["metadatas"][i]
                    }
                    conversations.append(self._format_conversation_item(item))
        
        # 按时间排序
        if sort_by_time:
            conversations.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
        return conversations
    
    def _format_conversation_item(self, item: Dict) -> Dict:
        """格式化对话项目"""
        result = {
            "id": item["id"],
            "content": item["content"]
        }
        
        metadata = item["metadata"]
        if metadata:
            result["timestamp"] = metadata.get("timestamp", "未知时间")
            result["importance"] = metadata.get("importance", 0.0)
            
            # 提取用户情绪信息
            if "user_emotion" in metadata:
                try:
                    result["user_emotion"] = json.loads(metadata["user_emotion"])
                except:
                    result["user_emotion"] = {"emotion": "unknown"}
        
        return result
    
    def get_user_preferences(self, category: str = None, sentiment: float = None) -> List[Dict]:
        """
        获取用户偏好数据
        
        Args:
            category: 可选的类别过滤
            sentiment: 可选的情感倾向过滤(正值表示喜欢，负值表示不喜欢)
            
        Returns:
            List[Dict]: 用户偏好列表
        """
        where_filter = {}
        if category:
            where_filter["category"] = category
            
        if sentiment is not None:
            where_filter["sentiment"] = {"$gte": sentiment} if sentiment >= 0 else {"$lt": 0}
        
        # 查询偏好集合
        preferences_data = self.memory_system.collections["preferences"].get(
            where=where_filter if where_filter else None
        )
        
        preferences = []
        if preferences_data and "ids" in preferences_data and preferences_data["ids"]:
            for i, pref_id in enumerate(preferences_data["ids"]):
                preferences.append({
                    "id": pref_id,
                    "content": preferences_data["documents"][i],
                    "category": preferences_data["metadatas"][i].get("category", "未分类"),
                    "item": preferences_data["metadatas"][i].get("item", ""),
                    "sentiment": preferences_data["metadatas"][i].get("sentiment", 0.0),
                    "certainty": preferences_data["metadatas"][i].get("certainty", 0.0),
                    "timestamp": preferences_data["metadatas"][i].get("timestamp", ""),
                    "last_confirmed": preferences_data["metadatas"][i].get("last_confirmed", "")
                })
                
        return preferences
    
    def get_emotional_state_history(self, limit: int = 10) -> List[Dict]:
        """
        获取情感状态历史记录
        
        Args:
            limit: 返回的最大记录数
            
        Returns:
            List[Dict]: 情感状态历史列表
        """
        emotional_data = self.memory_system.collections["emotional"].get(limit=limit)
        
        states = []
        if emotional_data and "ids" in emotional_data and emotional_data["ids"]:
            for i, state_id in enumerate(emotional_data["ids"]):
                try:
                    state_data = json.loads(emotional_data["metadatas"][i].get("state_data", "{}"))
                    states.append({
                        "id": state_id,
                        "emotion": state_data.get("current_emotion", "neutral"),
                        "intensity": state_data.get("emotion_intensity", 0.5),
                        "relationship_level": state_data.get("relationship_level", 1.0),
                        "timestamp": state_data.get("last_updated", "未知时间"),
                        "valence": state_data.get("valence", 0.0)
                    })
                except:
                    # 跳过无法解析的数据
                    continue
                    
        # 按时间排序
        states.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return states
    
    def get_relationship_events(self, limit: int = 10) -> List[Dict]:
        """
        获取关系事件历史
        
        Args:
            limit: 返回的最大记录数
            
        Returns:
            List[Dict]: 关系事件列表
        """
        relationship_data = self.memory_system.collections["relationship"].get(limit=limit)
        
        events = []
        if relationship_data and "ids" in relationship_data and relationship_data["ids"]:
            for i, event_id in enumerate(relationship_data["ids"]):
                events.append({
                    "id": event_id,
                    "description": relationship_data["documents"][i],
                    "timestamp": relationship_data["metadatas"][i].get("timestamp", "未知时间"),
                    "importance": relationship_data["metadatas"][i].get("importance", 0.0),
                    "relationship_level": relationship_data["metadatas"][i].get("relationship_level", 0.0),
                    "impact": relationship_data["metadatas"][i].get("impact", 0.0)
                })
                
        # 按时间排序
        events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return events
    
    def get_current_emotional_state(self) -> Dict:
        """
        获取当前情感状态
        
        Returns:
            Dict: 当前情感状态
        """
        return self.memory_system.get_emotional_summary()
    
    def export_data(self, collection_name: str, output_file: str, format: str = "json"):
        """
        导出数据到文件
        
        Args:
            collection_name: 集合名称 ("episodic", "preferences", "emotional", "relationship")
            output_file: 输出文件路径
            format: 输出格式 (json或csv)
        """
        if collection_name not in self.memory_system.collections:
            raise ValueError(f"无效的集合名称: {collection_name}")
            
        data = self.memory_system.collections[collection_name].get()
        
        if not data or "ids" not in data or not data["ids"]:
            print(f"集合 {collection_name} 中没有数据")
            return
            
        # 准备导出数据
        export_data = []
        for i, item_id in enumerate(data["ids"]):
            item = {
                "id": item_id,
                "content": data["documents"][i],
                **data["metadatas"][i]  # 展开元数据字段
            }
            export_data.append(item)
            
        # 导出数据
        if format.lower() == "json":
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
        elif format.lower() == "csv":
            df = pd.DataFrame(export_data)
            df.to_csv(output_file, index=False, encoding='utf-8')
        else:
            raise ValueError(f"不支持的格式: {format}")
            
        print(f"数据已导出到 {output_file}")
    
    def print_formatted(self, data: List[Dict], title: str = "查询结果"):
        """
        格式化打印数据
        
        Args:
            data: 要打印的数据列表
            title: 标题
        """
        print(f"\n===== {title} =====")
        
        if not data:
            print("没有找到数据")
            return
            
        for i, item in enumerate(data):
            print(f"\n--- 项目 {i+1} ---")
            for key, value in item.items():
                if key == "content":
                    print(f"\n{value}\n")
                elif key != "id":  # 不打印ID，除非特别需要
                    print(f"{key}: {value}")
            print("-" * 40)


# 命令行接口示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="情感陪伴智能体记忆查看工具")
    parser.add_argument("--type", "-t", choices=["conversations", "preferences", "emotional", "relationship"],
                        default="conversations", help="要查看的记忆类型")
    parser.add_argument("--limit", "-l", type=int, default=10, help="返回的最大记录数")
    parser.add_argument("--query", "-q", type=str, help="搜索关键词")
    parser.add_argument("--category", "-c", type=str, help="偏好类别")
    parser.add_argument("--export", "-e", type=str, help="导出文件路径")
    parser.add_argument("--format", "-f", choices=["json", "csv"], default="json", help="导出格式")
    parser.add_argument("--db-path", "-d", type=str, default="memory_db", help="数据库路径")
    
    args = parser.parse_args()
    
    viewer = MemoryViewer(persist_directory=args.db_path)
    
    if args.export:
        # 导出模式
        collection_map = {
            "conversations": "episodic",
            "preferences": "preferences",
            "emotional": "emotional",
            "relationship": "relationship"
        }
        viewer.export_data(collection_map[args.type], args.export, args.format)
    else:
        # 查看模式
        if args.type == "conversations":
            data = viewer.get_conversation_history(args.limit, args.query)
            viewer.print_formatted(data, "对话历史")
        elif args.type == "preferences":
            data = viewer.get_user_preferences(category=args.category)
            viewer.print_formatted(data, "用户偏好")
        elif args.type == "emotional":
            # 先打印当前状态
            current = viewer.get_current_emotional_state()
            print("\n===== 当前情感状态 =====")
            for key, value in current.items():
                print(f"{key}: {value}")
            print("-" * 40)
            
            # 再打印历史记录
            data = viewer.get_emotional_state_history(args.limit)
            viewer.print_formatted(data, "情感状态历史")
        elif args.type == "relationship":
            data = viewer.get_relationship_events(args.limit)
            viewer.print_formatted(data, "关系事件历史")