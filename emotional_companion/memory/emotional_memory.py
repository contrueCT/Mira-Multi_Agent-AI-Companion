import chromadb
import json
from datetime import datetime, timedelta
import os
import random
from chromadb.utils import embedding_functions

class EmotionalMemorySystem:
    def __init__(self, persist_directory="memory_db"):
        # 创建持久化目录
        os.makedirs(persist_directory, exist_ok=True)
        
        # 初始化ChromaDB
        self.client = chromadb.PersistentClient(path=persist_directory)

        print(f"✅ ChromaDB客户端已初始化，持久化目录: {persist_directory}")

        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="BAAI/bge-base-zh-v1.5",
            device="cpu"
        )

        # 定义HNSW索引参数
        self.hnsw_metadata_config = {
            # 使用余弦相似度
            "hnsw:space": "cosine",  
            # 推荐M值
            "hnsw:M": 32,         
            # construction_ef值   
            "hnsw:construction_ef": 256,
            # (可选) 如果你的CPU核心多，可以尝试指定构建线程数 
            "hnsw:num_threads": 4 
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
                                                            metadata=self.hnsw_metadata_config),
            "user_profile": self.client.get_or_create_collection(name = "user_profile_memory", 
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
        # 格式化时间为中文格式
        dt = datetime.fromisoformat(timestamp)
        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        weekday_name = weekdays[dt.weekday()]
        formatted_time = f"{dt.year}年{dt.month}月{dt.day}日 {weekday_name} {dt.strftime('%H:%M')}"
        
        memory_text = f"时间：{formatted_time}\n用户: {user_message}\n智能体: {agent_response}"
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
                    # 获取时间戳并格式化 - 改进版本
                    timestamp = memory["metadata"].get("timestamp", "")
                    time_str = ""
                    if timestamp:
                        try:
                            # 解析ISO格式的时间戳
                            dt = datetime.fromisoformat(timestamp)
                            # 获取中文星期名称
                            weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
                            weekday_name = weekdays[dt.weekday()]
                            # 格式化为：星期几 月-日 时:分
                            time_str = f"[{weekday_name} {dt.strftime('%m-%d %H:%M')}] "
                        except:
                            # 如果解析失败，使用简化格式
                            time_str = f"[{timestamp[:16]}] "
                    
                    # 将时间放在对话内容前面
                    context += f"{i+1}. {time_str}{memory['content']}\n"
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
    
    def add_user_profile_info(self, category, value, confidence=1.0, source="user_direct"):
        """
        添加用户关键信息
        
        Args:
            category: 信息类别 (如: "性别", "生日", "过敏食物", "家庭成员", "朋友")
            value: 信息内容
            confidence: 信息可信度 (0-1)
            source: 信息来源 ("user_direct", "conversation", "inference")
        """
        timestamp = datetime.now().isoformat()
        profile_id = f"profile_{category}_{timestamp}"
        
        # 创建可搜索的文本描述
        profile_text = f"用户{category}: {value}"
        
        # 查询是否已存在相同类别的信息
        existing = self.collections["user_profile"].query(
            query_texts=[category],
            n_results=5,
            where={"category": category}
        )
        
        # 如果存在相同类别且可信度较高，则更新最新的记录
        if (existing and len(existing["ids"]) > 0 and len(existing["ids"][0]) > 0 
            and confidence >= 0.8 and source in ["user_direct", "conversation"]):
            
            # 更新最近的记录
            latest_id = existing["ids"][0][0]
            self.collections["user_profile"].update(
                ids=[latest_id],
                metadatas=[{
                    "category": category,
                    "value": value,
                    "confidence": confidence,
                    "source": source,
                    "timestamp": timestamp,
                    "last_updated": timestamp
                }],
                documents=[profile_text]
            )
        else:
            # 添加新信息
            self.collections["user_profile"].add(
                ids=[profile_id],
                metadatas=[{
                    "category": category,
                    "value": value,
                    "confidence": confidence,
                    "source": source,
                    "timestamp": timestamp,
                    "last_updated": timestamp
                }],
                documents=[profile_text]
            )
        print(f"✅ 用户信息已添加/更新: {category} - {value} (来源: {source}, 置信度: {confidence})")
    
    def get_user_profile(self, category=None):
        """
        获取用户关键信息
        
        Args:
            category: 可选的信息类别过滤
            
        Returns:
            dict: 用户关键信息字典
        """
        where_filter = {"category": category} if category else None
        
        try:
            results = self.collections["user_profile"].get(
                where=where_filter
            )
            
            profile_data = {}
            if results and "ids" in results and results["ids"]:
                for i, profile_id in enumerate(results["ids"]):
                    metadata = results["metadatas"][i]
                    cat = metadata.get("category", "未知")
                    value = metadata.get("value", "")
                    confidence = metadata.get("confidence", 0.0)
                    source = metadata.get("source", "unknown")
                    timestamp = metadata.get("timestamp", "")
                    
                    # 如果类别已存在，保留置信度更高或更新的信息
                    if cat in profile_data:
                        existing_confidence = profile_data[cat].get("confidence", 0.0)
                        existing_timestamp = profile_data[cat].get("timestamp", "")
                        
                        if confidence > existing_confidence or (confidence == existing_confidence and timestamp > existing_timestamp):
                            profile_data[cat] = {
                                "value": value,
                                "confidence": confidence,
                                "source": source,
                                "timestamp": timestamp
                            }
                    else:
                        profile_data[cat] = {
                            "value": value,
                            "confidence": confidence,
                            "source": source,
                            "timestamp": timestamp
                        }
            
            return profile_data
            
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return {}
    
    def update_user_profile_from_conversation(self, extracted_info):
        """
        从对话中提取的信息更新用户资料
        
        Args:
            extracted_info: 字典格式的提取信息 
                          如: {"生日": "3月15日", "家庭成员": "妈妈是老师"}
        """
        for category, value in extracted_info.items():
            # 从对话中提取的信息置信度相对较低
            self.add_user_profile_info(
                category=category,
                value=value,
                confidence=0.7,
                source="conversation"
            )
    
    def delete_user_profile_info(self, category):
        """
        删除用户关键信息
        
        Args:
            category: 要删除的信息类别 (如: "性别", "生日", "过敏食物")
            
        Returns:
            bool: 删除是否成功
        """
        try:
            # 查询指定类别的所有记录
            results = self.collections["user_profile"].get(
                where={"category": category}
            )
            
            if results and "ids" in results and results["ids"]:
                # 删除所有匹配的记录
                self.collections["user_profile"].delete(
                    ids=results["ids"]
                )
                print(f"✅ 已删除用户信息类别: {category} ({len(results['ids'])}条记录)")
                return True
            else:
                print(f"⚠️ 未找到类别为'{category}'的用户信息")
                return False
                
        except Exception as e:
            print(f"❌ 删除用户信息失败: {e}")
            return False

    def delete_user_preference(self, category):
        """
        删除用户偏好
        
        Args:
            category: 要删除的偏好类别 (如: "食物", "颜色", "运动", "活动")
            
        Returns:
            bool: 删除是否成功
        """
        try:
            # 查询指定类别的所有偏好记录
            results = self.collections["preferences"].get(
                where={"category": category}
            )
            
            if results and "ids" in results and results["ids"]:
                # 删除所有匹配的记录
                self.collections["preferences"].delete(
                    ids=results["ids"]
                )
                print(f"✅ 已删除用户偏好类别: {category} ({len(results['ids'])}条记录)")
                return True
            else:
                print(f"⚠️ 未找到类别为'{category}'的用户偏好")
                return False
                
        except Exception as e:
            print(f"❌ 删除用户偏好失败: {e}")
            return False

    def search_user_profile_info(self, query, n_results=5):
        """
        搜索用户关键信息
        
        Args:
            query: 搜索查询
            n_results: 返回结果数量
            
        Returns:
            list: 匹配的用户信息列表
        """
        try:
            results = self.semantic_memory_search(
                query=query,
                collection_name="user_profile",
                n_results=n_results,
                threshold=0.7
            )
            return results
        except Exception as e:
            print(f"搜索用户信息失败: {e}")
            return []
    
    def get_user_profile_summary(self):
        """
        获取用户信息摘要，用于智能体上下文
        
        Returns:
            str: 格式化的用户信息摘要
        """
        profile_data = self.get_user_profile()
        
        if not profile_data:
            return "暂无用户关键信息记录"
        
        summary = "## 用户关键信息\n\n"
        
        # 按重要性和类别排序显示
        priority_categories = ["性别", "生日", "年龄", "职业", "家庭成员", "朋友", "过敏食物", "疾病", "居住地"]
        
        # 先显示高优先级类别
        for category in priority_categories:
            if category in profile_data:
                info = profile_data[category]
                confidence_desc = "确定" if info["confidence"] >= 0.8 else "可能"
                summary += f"- {category}: {info['value']} ({confidence_desc})\n"
        
        # 再显示其他类别
        for category, info in profile_data.items():
            if category not in priority_categories:
                confidence_desc = "确定" if info["confidence"] >= 0.8 else "可能"
                summary += f"- {category}: {info['value']} ({confidence_desc})\n"
        
        return summary
    
    def get_recent_conversations(self, minutes=30, n_results=3):
        """
        获取最近的对话记录
        
        Args:
            minutes: 限定时间范围，单位为分钟，默认过去30分钟
            n_results: 返回的对话记录条数，默认3条
            
        Returns:
            list: 最近的对话记录列表
        """
        try:
            # 计算时间范围
            time_threshold = datetime.now() - timedelta(minutes=minutes)
            
            # 查询最近的对话记录
            results = self.collections["episodic"].query(
                query_texts=["*"],  # 匹配所有对话
                where={
                    "timestamp": {
                        "$gte": time_threshold.isoformat()  # 过滤条件：时间戳大于等于计算出的阈值
                    }
                }
            )
            
            conversations = []
            if results and "documents" in results and results["documents"]:
                docs_list = results["documents"][0]
                metadatas_list = results["metadatas"][0]
                
                for i, doc_content in enumerate(docs_list):
                    metadata = metadatas_list[i]
                    conversation = {
                        "content": doc_content,
                        "metadata": metadata
                    }
                    conversations.append(conversation)
            
            return conversations
        
        except Exception as e:
            print(f"获取最近对话记录失败: {e}")
            return []
    
    def get_recent_conversations(self, minutes=30, limit=3):
        """获取指定时间范围内最近的对话记录"""
        try:
            # 计算时间阈值
            time_threshold = datetime.now() - timedelta(minutes=minutes)
            # 获取所有情节记忆
            all_memories = self.get_recent_conversations(minutes=minutes, limit=limit)

            if not all_memories or not all_memories["metadatas"]:
                return []
            
            # 筛选指定时间内的记忆并按时间排序
            recent_memories = []
            for i, metadata in enumerate(all_memories["metadatas"]):
                if metadata and metadata.get("timestamp"):
                    memory_time = datetime.fromisoformat(metadata["timestamp"])
                    if memory_time >= time_threshold:
                        recent_memories.append({
                            "content": all_memories["documents"][i],
                            "metadata": metadata,
                            "id": all_memories["ids"][i],
                            "timestamp": memory_time
                        })
            
            # 按时间倒序排序，取最近的N条
            recent_memories.sort(key=lambda x: x["timestamp"], reverse=True)
            return recent_memories[:limit]
            
        except Exception as e:
            print(f"获取最近对话记录失败: {e}")
            return []