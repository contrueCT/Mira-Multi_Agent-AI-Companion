import chromadb
from sentence_transformers import SentenceTransformer
import json
from datetime import datetime
import os
import random
import numpy as np
from chromadb.utils import embedding_functions

class EmotionalMemorySystem:
    def __init__(self, persist_directory="memory_db"):
        # 创建持久化目录
        os.makedirs(persist_directory, exist_ok=True)
        
        # 初始化ChromaDB
        self.client = chromadb.PersistentClient(path=persist_directory)

        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="BAAI/bge-base-zh-v1.5",
            device="cpu"
        )

        # 定义HNSW索引参数
        self.hnsw_metadata_config = {
            "hnsw:space": "cosine",  # 使用余弦相似度
            "hnsw:M": 32,            # 推荐M值
            "hnsw:construction_ef": 256, # 推荐construction_ef值
            "hnsw:num_threads": 4 # (可选) 如果你的CPU核心多，可以尝试指定构建线程数
        }
    
        
        # 创建不同类型的记忆集合
        self.collections = {
            "episodic": self.client.get_or_create_collection(name = "episodic_memory", 
                                                            embedding_function=self.embedding_function,
                                                            metadata=self.hnsw_metadata_config),
            "semantic": self.client.get_or_create_collection(name = "semantic_memory", 
                                                            embedding_function=self.embedding_function,
                                                            metadata=self.hnsw_metadata_config),
            "emotional": self.client.get_or_create_collection(name = "emotional_memory", 
                                                            embedding_function=self.embedding_function,
                                                            metadata=self.hnsw_metadata_config),
            "relationship": self.client.get_or_create_collection(name = "relationship_memory", 
                                                            embedding_function=self.embedding_function,
                                                            metadata=self.hnsw_metadata_config),
            "preferences": self.client.get_or_create_collection(name = "preferences_memory", 
                                                            embedding_function=self.embedding_function,
                                                            metadata=self.hnsw_metadata_config)
        }

        
        # 记忆衰减参数
        self.decay_rate = 0.05
        self.importance_threshold = 0.3
        
        # 情感状态
        self.emotional_state = {
            "current_emotion": "neutral",
            "emotion_intensity": 0.5,
            "valence": 0.0,
            "relationship_level": 1.0,
            "last_updated": datetime.now().isoformat()
        }
        self.load_emotional_state()

    def load_emotional_state(self):
        """加载最近的情感状态"""
        try:
            results = self.collections["emotional"].query(
                query_texts=["current emotional state"],
                n_results=1
            )
            if results and len(results["metadatas"]) > 0:
                self.emotional_state = json.loads(results["metadatas"][0][0]["state_data"])
        except Exception as e:
            print(f"加载情感状态失败: {e}")
    
    def save_emotional_state(self):
        """保存当前情感状态"""
        self.emotional_state["last_updated"] = datetime.now().isoformat()
        state_id = f"emotional_state_{datetime.now().isoformat()}"
        
        state_text = f"情感: {self.emotional_state['current_emotion']}, " \
                     f"强度: {self.emotional_state['emotion_intensity']}, " \
                     f"关系程度: {self.emotional_state['relationship_level']}"
        
        self.collections["emotional"].add(
            ids=[state_id],
            metadatas=[{"state_data": json.dumps(self.emotional_state)}],
            documents=[state_text]
        )
    
    def add_episodic_memory(self, user_message, agent_response, 
                           user_emotion=None, context=None, importance=0.5):
        """添加情节记忆(对话历史)"""
        timestamp = datetime.now().isoformat()
        memory_id = f"episodic_{timestamp}"
        
        # 创建记忆文本
        memory_text = f"用户: {user_message}\n智能体: {agent_response}"
        if user_emotion:
            emotion_text = f"用户情绪: {user_emotion.get('emotion', 'unknown')}"
            memory_text += f"\n{emotion_text}"
        
        # 创建元数据
        metadata = {
            "timestamp": timestamp,
            "type": "conversation",
            "importance": importance,
            "decay_factor": 1.0,
            "last_accessed": timestamp
        }
        
        if user_emotion:
            metadata["user_emotion"] = json.dumps(user_emotion)
        
        if context:
            metadata["context"] = context
        
        # 保存到ChromaDB
        self.collections["episodic"].add(
            ids=[memory_id],
            metadatas=[metadata],
            documents=[memory_text]
        )
        
        # 如果是积极互动，可能增加关系亲密度
        if user_emotion and user_emotion.get("valence", 0) > 0.6:
            self.update_relationship_level(0.05)
        
        return memory_id
    
    def add_relationship_event(self, event_description, importance=0.7, impact=0.1):
        """添加关系发展里程碑事件"""
        timestamp = datetime.now().isoformat()
        event_id = f"relationship_{timestamp}"
        
        # 更新关系亲密度
        self.update_relationship_level(impact)
        
        # 保存事件
        self.collections["relationship"].add(
            ids=[event_id],
            metadatas=[{
                "timestamp": timestamp,
                "type": "relationship_event",
                "importance": importance,
                "relationship_level": self.emotional_state["relationship_level"],
                "impact": impact
            }],
            documents=[event_description]
        )
    
    def add_user_preference(self, category, item, sentiment=1.0, certainty=0.8):
        """添加用户偏好记忆"""
        timestamp = datetime.now().isoformat()
        preference_id = f"preference_{category}_{timestamp}"
        
        preference_text = f"用户{sentiment>0 and '喜欢' or '不喜欢'}{category}: {item}"
        
        # 查询是否已存在相同偏好
        existing = self.collections["preferences"].query(
            query_texts=[f"{category} {item}"],
            n_results=1,
            where={"category": category}
        )
        
        # 如果存在且确定性较高，则更新
        if existing and len(existing["ids"]) > 0 and len(existing["ids"][0]) > 0 and certainty > 0.7:
            self.collections["preferences"].update(
                ids=[existing["ids"][0][0]],
                metadatas=[{
                    "category": category,
                    "item": item,
                    "sentiment": sentiment, 
                    "certainty": certainty,
                    "timestamp": timestamp,
                    "last_confirmed": timestamp
                }],
                documents=[preference_text]
            )
        else:
            # 否则添加新偏好
            self.collections["preferences"].add(
                ids=[preference_id],
                metadatas=[{
                    "category": category,
                    "item": item,
                    "sentiment": sentiment,
                    "certainty": certainty,
                    "timestamp": timestamp,
                    "last_confirmed": timestamp
                }],
                documents=[preference_text]
            )
    
    def update_relationship_level(self, change):
        """更新关系亲密度"""
        current = self.emotional_state["relationship_level"]
        # 使用非线性变化，随着关系等级提高，变化越来越难
        if change > 0:
            # 随着关系等级提高，正向变化越来越小
            adjusted_change = change * (1 - current/12)
        else:
            # 负向变化总是影响较大
            adjusted_change = change
            
        new_level = max(1.0, min(10.0, current + adjusted_change))
        self.emotional_state["relationship_level"] = new_level
        self.save_emotional_state()
        
        # 记录重要关系变化
        if abs(new_level - current) >= 0.5:  # 关系有较明显变化
            event = f"关系亲密度从 {current:.1f} 变为 {new_level:.1f}"
            self.add_relationship_event(event, importance=0.8, impact=0)
    
    def update_emotional_state(self, emotion, intensity=None, valence=None):
        """更新情感状态"""
        self.emotional_state["current_emotion"] = emotion
        
        if intensity is not None:
            self.emotional_state["emotion_intensity"] = intensity
            
        if valence is not None:
            self.emotional_state["valence"] = valence
            
        self.save_emotional_state()
    #此处的相关性阈值用于测试，后续需要修改
    def semantic_memory_search(self, query, collection_name="episodic", n_results=5, 
                              where_filter=None, threshold=0.6):
        """语义记忆搜索"""
        search_params = {
            "query_texts": [query],
            "n_results": n_results
        }
        
        if where_filter:
            search_params["where"] = where_filter
            
        results = self.collections[collection_name].query(**search_params)
        
        memories = []
        # 检查结果的有效性，并确保所有需要的字段都存在且结构符合预期
        if (results and results["documents"] and results["documents"][0] and
            results["metadatas"] and results["metadatas"][0] and
            results["ids"] and results["ids"][0] and
            results["distances"] and results["distances"][0]):

            # 因为我们只有一个查询文本 (query_texts=[query]), 所以我们只关心结果中的第一个列表
            docs_list = results["documents"][0]
            metadatas_list = results["metadatas"][0]
            ids_list = results["ids"][0]
            distances_list = results["distances"][0]

            for i, doc_content in enumerate(docs_list):
                # 确保索引 i 不会超出其他列表的范围 (尽管ChromaDB通常会返回对齐的列表)
                if i < len(distances_list) and i < len(metadatas_list) and i < len(ids_list):
                    distance = distances_list[i]
                    
                    # ChromaDB返回的距离，值越小表示越相似。
                    # threshold=0.6 意味着我们寻找与查询向量的余弦距离小于等于0.6的文档。
                    if distance <= threshold:
                        memory = {
                            "content": doc_content,  # 这里是单个文档的内容
                            "metadata": metadatas_list[i],
                            "id": ids_list[i],
                            # 相似度通常是 1 - distance (对于归一化的距离，如余弦距离)
                            "similarity": 1 - distance 
                        }
                        memories.append(memory)
        
        # 记录访问，更新衰减因子 (这部分逻辑保持不变)
        for memory in memories:
            if collection_name == "episodic":
                self.update_memory_access(memory["id"])
                
        return memories
    
    def update_memory_access(self, memory_id):
        """更新记忆访问时间和重要性"""
        try:
            # 获取当前记忆数据
            result = self.collections["episodic"].get(ids=[memory_id])
            if result and result["metadatas"]:
                metadata = result["metadatas"][0]
                
                # 更新最后访问时间
                metadata["last_accessed"] = datetime.now().isoformat()
                
                # 增强记忆重要性(被访问的记忆变得更重要)
                metadata["importance"] = min(1.0, metadata.get("importance", 0.5) + 0.05)
                
                # 重置衰减因子
                metadata["decay_factor"] = 1.0
                
                # 更新记忆
                self.collections["episodic"].update(
                    ids=[memory_id],
                    metadatas=[metadata]
                )
        except Exception as e:
            print(f"更新记忆访问失败: {e}")
    
    def apply_memory_decay(self):
        """应用记忆衰减，降低不重要记忆的检索优先级"""
        try:
            # 获取所有情节记忆
            all_memories = self.collections["episodic"].get()
            
            if all_memories and all_memories["ids"]:
                now = datetime.now()
                updated_metadatas = []
                
                for i, memory_id in enumerate(all_memories["ids"]):
                    metadata = all_memories["metadatas"][i]
                    
                    # 计算时间差(以天为单位)
                    last_accessed = datetime.fromisoformat(metadata.get("last_accessed", metadata.get("timestamp")))
                    days_since_access = (now - last_accessed).days
                    
                    # 更新衰减因子
                    importance = metadata.get("importance", 0.5)
                    decay = self.decay_rate * days_since_access * (1 - importance)
                    new_decay_factor = max(0.1, metadata.get("decay_factor", 1.0) - decay)
                    
                    metadata["decay_factor"] = new_decay_factor
                    updated_metadatas.append(metadata)
                
                # 批量更新
                self.collections["episodic"].update(
                    ids=all_memories["ids"],
                    metadatas=updated_metadatas
                )
        except Exception as e:
            print(f"应用记忆衰减失败: {e}")
    
    def get_emotional_summary(self):
        """获取情感状态摘要"""
        current_level = self.emotional_state["relationship_level"]
        
        # 根据关系级别获取不同的描述
        relationship_descriptions = {
            (1, 2): "初期接触阶段，关系较为礼貌但疏远",
            (3, 4): "初步熟悉阶段，开始建立基本信任",
            (5, 6): "熟悉阶段，相互了解并形成稳定互动模式",
            (7, 8): "亲密阶段，交流更加开放和情感化",
            (9, 10): "深度亲密阶段，关系非常紧密和私人化"
        }
        
        # 确定当前关系描述
        relationship_desc = ""
        for range_key, desc in relationship_descriptions.items():
            if range_key[0] <= current_level <= range_key[1]:
                relationship_desc = desc
                break
        
        return {
            "emotion": self.emotional_state["current_emotion"],
            "intensity": self.emotional_state["emotion_intensity"],
            "relationship_level": self.emotional_state["relationship_level"],
            "relationship_description": relationship_desc,
            "last_updated": self.emotional_state["last_updated"]
        }
    
    def get_relevant_context(self, query, full_context=False):
        """获取完整的相关上下文，包括对话记忆、用户偏好和关系状态"""
        # 获取相关对话记忆
        episodic_memories = self.semantic_memory_search(
            query, "episodic", n_results=5
        )
        
        # 获取相关用户偏好
        preference_memories = self.semantic_memory_search(
            query, "preferences", n_results=3
        )
        
        # 获取关系事件
        relationship_memories = []
        if self.emotional_state["relationship_level"] >= 5:
            # 关系较好时，更可能回忆起重要关系事件
            relationship_memories = self.semantic_memory_search(
                query, "relationship", n_results=2
            )
        
        # 情感状态摘要
        emotional_summary = self.get_emotional_summary()
        
        # 格式化输出
        context = "## 相关记忆\n\n"
        
        if episodic_memories:
            context += "### 过去的对话\n"
            for i, memory in enumerate(episodic_memories):
                # 根据衰减因子调整显示优先级
                decay = memory["metadata"].get("decay_factor", 1.0)
                importance = memory["metadata"].get("importance", 0.5)
                if decay * importance > self.importance_threshold or full_context:
                    context += f"{i+1}. {memory['content']}\n"
                    if full_context and "user_emotion" in memory["metadata"]:
                        try:
                            user_emotion = json.loads(memory["metadata"]["user_emotion"])
                            context += f"   用户情绪: {user_emotion.get('emotion', 'unknown')}\n"
                        except:
                            pass
            context += "\n"
        
        if preference_memories:
            context += "### 用户偏好\n"
            for memory in preference_memories:
                certainty = memory["metadata"].get("certainty", 0.8)
                certainty_desc = "确定" if certainty > 0.7 else "可能"
                context += f"- {memory['content']} ({certainty_desc})\n"
            context += "\n"
        
        if relationship_memories:
            context += "### 重要关系事件\n"
            for memory in relationship_memories:
                context += f"- {memory['content']}\n"
            context += "\n"
        
        context += f"### 当前关系状态\n"
        context += f"- 情绪: {emotional_summary['emotion']}\n"
        context += f"- 情绪强度: {emotional_summary['intensity']:.1f}\n"
        context += f"- 关系亲密度: {emotional_summary['relationship_level']:.1f}/10\n"
        context += f"- 关系描述: {emotional_summary['relationship_description']}\n"
        
        return context
    
    def associate_spontaneously(self):
        """自主联想记忆，模拟人类无意识的联想过程"""
        # 获取最近的情感状态
        recent_state = self.emotional_state["current_emotion"]
        
        # 基于当前情绪状态，联想相关记忆
        emotion_query = f"情绪 {recent_state} 相关记忆"
        memories = self.semantic_memory_search(
            emotion_query, "episodic", n_results=1
        )
        
        if memories:
            return {
                "type": "spontaneous_memory",
                "content": memories[0]["content"],
                "triggered_by": f"当前情绪: {recent_state}"
            }
        
        # 如果没有情绪相关记忆，尝试检索一个随机重要记忆
        important_memories = self.collections["episodic"].query(
            query_texts=["important memory"],
            n_results=10,
            where={"importance": {"$gt": 0.7}}
        )
        
        if important_memories and important_memories["documents"] and important_memories["documents"][0]:
            docs_list = important_memories["documents"][0]
            # 检查是否有重要记忆
            if docs_list: 
                idx = random.randint(0, len(docs_list) - 1)
                return {
                    "type": "spontaneous_memory",
                    "content": docs_list[idx],
                    "triggered_by": "重要记忆随机联想"
                }
        return None