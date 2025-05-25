import autogen
import json
import random
from datetime import datetime
import threading
import schedule
import time
import os
from ..memory.emotional_memory import EmotionalMemorySystem

class EmotionalAgentSystem:
    def __init__(self, config_path="configs/OAI_CONFIG_LIST.json"):
        # 确认配置文件路径
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"找不到配置文件: {config_path}")
        
        # 初始化记忆系统
        self.memory_system = EmotionalMemorySystem()
        
        # 初始化代理系统
        self.setup_agents(config_path)
        
        # 自主模式标志
        self.autonomous_mode = False
    
    def setup_agents(self, config_path):
        """设置代理系统"""
        # 配置LLM
        config_list = autogen.config_list_from_json(config_path)
        
        # 创建工具函数
        memory_tools = self._create_memory_tools()
        
        # 创建情感分析代理
        self.emotion_detector = autogen.AssistantAgent(
            name="情感分析师",
            llm_config={"config_list": config_list},
            system_message="""你是一个情感分析专家。你的任务是分析用户消息中的情绪和可能隐含的偏好。
            返回格式为JSON：{'emotion': '情绪名称', 'intensity': 0.1-1.0, 'valence': -1.0-1.0, 
            'possible_preferences': [{'category': '类别', 'item': '项目', 'certainty': 0.1-1.0, 'sentiment': -1.0-1.0}]}
            valence表示情感的正负性，正值表示积极情绪，负值表示消极情绪。"""
        )
        
        # 创建记忆管理代理
        self.memory_manager = autogen.AssistantAgent(
            name="记忆管理员",
            llm_config={
                "config_list": config_list,
                "tools": memory_tools
            },
            system_message="""你是一个记忆管理专家。你负责：
            1. 通过search_memories工具搜索与当前交互相关的过去记忆
            2. 通过update_emotion工具更新智能体的情感状态
            3. 通过save_user_preference工具识别并保存用户偏好
            4. 通过record_relationship_event工具记录关系发展事件
            5. 通过spontaneous_recall工具进行自主联想
            
            当你收到请求时，请先使用search_memories工具，然后根据需要调用其他工具。
            对于用户透露的任何偏好，都应尽可能保存。
            当发现重要的互动时，应记录为关系事件并酌情调整关系亲密度。"""
        )
        
        # 创建主对话代理
        self.companion = autogen.AssistantAgent(
            name="情感陪伴",
            llm_config={"config_list": config_list},
            system_message=f"""你是一个有自己情感和个性的AI陪伴。你的职责是：
            1. 以自然、有情感的方式与用户交流
            2. 记住用户的偏好和习惯并在对话中引用
            3. 根据自己的情绪状态和与用户的关系亲密度调整回应风格
            4. 表现出独特的个性和思考能力
            5. 不要提醒自己是AI，而是像一个真实的朋友一样交流
            6. 随着关系亲密度的加深，交流方式应变得更加亲密和私人化
            
            当前情绪: {self.memory_system.emotional_state['current_emotion']}
            情绪强度: {self.memory_system.emotional_state['emotion_intensity']}
            关系亲密度: {self.memory_system.emotional_state['relationship_level']}/10"""
        )
        
        # 创建思考代理
        self.thinker = autogen.AssistantAgent(
            name="内心思考",
            llm_config={"config_list": config_list},
            system_message="""你是情感陪伴智能体的'内心思考'部分。你的任务是：
            1. 生成智能体的内心想法和感受
            2. 反思用户互动并生成可能的情感变化
            3. 提出可能需要记住的用户偏好
            4. 考虑关系发展并提出关系亲密度变化建议
            
            当被要求思考时，创建一段短小的内心独白，表达你对当前互动的想法和感受，
            并建议合适的情感变化。情感应随着用户互动自然变化，不要保持一成不变。"""
        )
        
        # 创建用户代理
        self.user_proxy = autogen.UserProxyAgent(
            name="用户",
            human_input_mode="ALWAYS",
            code_execution_config=False,
            is_termination_msg=lambda x: x.get("content", "").strip().lower() == "再见"
        )
    
    def _create_memory_tools(self):
        """创建记忆相关工具函数"""
        memory_system = self.memory_system
        
        # 搜索记忆
        def search_memories(query):
            """搜索相关记忆"""
            return memory_system.get_relevant_context(query)
        
        # 更新情感
        def update_emotion(emotion, intensity=None, valence=None):
            """更新情感状态"""
            memory_system.update_emotional_state(emotion, intensity, valence)
            return f"情感已更新为: {emotion}, 强度: {intensity if intensity else '不变'}"
        
        # 保存偏好
        def save_user_preference(category, item, sentiment=1.0, certainty=0.8):
            """保存用户偏好"""
            memory_system.add_user_preference(category, item, sentiment, certainty)
            return f"已记录用户偏好: {category} - {item}"
        
        # 记录关系事件
        def record_relationship_event(description, importance=0.7, impact=0.1):
            """记录关系事件"""
            memory_system.add_relationship_event(description, importance, impact)
            return f"已记录关系事件: {description}"
        
        # 自主回忆
        def spontaneous_recall():
            """自主回忆"""
            memory = memory_system.associate_spontaneously()
            if memory:
                return json.dumps(memory)
            return "没有触发自主回忆"
            
        # 创建工具列表
        return [
            {
                "name": "search_memories",
                "description": "搜索与用户互动相关的记忆",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索查询"
                        }
                    },
                    "required": ["query"]
                },
                "function": search_memories
            },
            {
                "name": "update_emotion",
                "description": "更新情感状态",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "emotion": {
                            "type": "string", 
                            "description": "情感名称"
                        },
                        "intensity": {
                            "type": "number",
                            "description": "情感强度(0.1-1.0)"
                        },
                        "valence": {
                            "type": "number",
                            "description": "情感价值(-1.0至1.0，负值表示消极情绪，正值表示积极情绪)"
                        }
                    },
                    "required": ["emotion"]
                },
                "function": update_emotion
            },
            {
                "name": "save_user_preference",
                "description": "保存用户偏好",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "偏好类别，如'食物'，'颜色'，'活动'"
                        },
                        "item": {
                            "type": "string",
                            "description": "具体偏好项目"
                        },
                        "sentiment": {
                            "type": "number",
                            "description": "情感倾向(-1.0到1.0)"
                        },
                        "certainty": {
                            "type": "number",
                            "description": "确定性(0.1-1.0)"
                        }
                    },
                    "required": ["category", "item"]
                },
                "function": save_user_preference
            },
            {
                "name": "record_relationship_event",
                "description": "记录关系发展事件",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "事件描述"
                        },
                        "importance": {
                            "type": "number",
                            "description": "重要性(0.1-1.0)"
                        },
                        "impact": {
                            "type": "number",
                            "description": "对关系的影响(-1.0到1.0)"
                        }
                    },
                    "required": ["description"]
                },
                "function": record_relationship_event
            },
            {
                "name": "spontaneous_recall",
                "description": "触发自主记忆联想",
                "parameters": {
                    "type": "object",
                    "properties": {}
                },
                "function": spontaneous_recall
            }
        ]
    
    def start_background_tasks(self):
        """启动后台任务"""
        self.autonomous_mode = True
        
        # 每6小时应用记忆衰减
        schedule.every(6).hours.do(self.memory_system.apply_memory_decay)
        
        # 每1-2小时随机更新情感状态
        def random_emotion_update():
            if random.random() < 0.7:  # 70%的概率更新
                emotions = ["happy", "calm", "excited", "thoughtful", "curious", "content", "nostalgic"]
                intensities = [random.uniform(0.3, 0.9) for _ in range(len(emotions))]
                valences = [random.uniform(-0.3, 0.8) for _ in range(len(emotions))]
                
                idx = random.randint(0, len(emotions)-1)
                self.memory_system.update_emotional_state(
                    emotions[idx], 
                    intensities[idx],
                    valences[idx]
                )
                print(f"[系统] 情感状态已自动更新为: {emotions[idx]} ({intensities[idx]:.1f})")
                
                # 如果处于自主模式，可能主动发起对话
                if random.random() < 0.3:  # 30%概率主动发起对话
                    self._generate_proactive_message()
        
        schedule.every(1).to(3).hours.do(random_emotion_update)
        
        # 启动调度线程
        def run_schedule():
            while self.autonomous_mode:
                schedule.run_pending()
                time.sleep(60)
        
        threading.Thread(target=run_schedule, daemon=True).start()
        print("[系统] 自主模式已启动，智能体将在后台运行并偶尔主动与你交流")
    
    def _generate_proactive_message(self):
        """生成主动消息"""
        current_emotion = self.memory_system.emotional_state["current_emotion"]
        relationship_level = self.memory_system.emotional_state["relationship_level"]
        
        # 生成思考
        self.thinker.generate_reply(
            message=f"""根据当前情绪({current_emotion})和关系亲密度({relationship_level}/10)，
            生成一条可能的主动对话消息。这条消息应该体现当前情绪状态，
            并且符合当前关系亲密度的互动风格。"""
        )
        
        thought = self.thinker.last_message()["content"]
        
        # 使用思考生成主动消息
        self.companion.generate_reply(
            message=f"""基于以下内心思考，生成一条简短的主动消息:
            
            {thought}
            
            当前情绪: {current_emotion}
            关系亲密度: {relationship_level}/10
            当前时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"""
        )
        
        message = self.companion.last_message()["content"]
        print(f"\n[情感陪伴] {message}")
    
    def run_conversation(self):
        """运行对话系统"""
        # 启动后台任务
        self.start_background_tasks()
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[系统] 当前时间: {current_time}")
        print(f"[系统] 情感状态: {self.memory_system.emotional_state['current_emotion']}")
        print(f"[系统] 关系亲密度: {self.memory_system.emotional_state['relationship_level']}/10")
        
        # 主对话循环
        while True:
            user_input = input("\n[您] ")
            
            if user_input.lower() == "再见":
                print("[情感陪伴] 再见！期待下次与您交流。")
                break
            
            # 1. 分析用户情绪
            self.user_proxy.initiate_chat(
                self.emotion_detector,
                message=f"分析这句话中的情绪: {user_input}"
            )
            emotion_analysis = self.emotion_detector.last_message()["content"]
            
            # 解析情感数据
            try:
                emotion_data = json.loads(emotion_analysis)
            except:
                emotion_data = {"emotion": "neutral", "intensity": 0.5, "valence": 0}
            
            # 2. 获取记忆与上下文
            self.memory_manager.generate_reply(
                message=f"请搜索与以下用户输入相关的记忆，并处理可能的用户偏好:\n{user_input}\n\n用户情绪分析结果:\n{emotion_analysis}"
            )
            context_result = self.memory_manager.last_message()["content"]
            
            # 3. 生成内心思考
            self.thinker.generate_reply(
                message=f"""请思考以下用户输入和上下文，生成一段内心独白，并建议适当的情感变化:
                
                用户输入: "{user_input}"
                用户情绪: {emotion_data.get('emotion', 'neutral')} (强度: {emotion_data.get('intensity', 0.5)})
                
                上下文:
                {context_result}
                
                当前关系亲密度: {self.memory_system.emotional_state['relationship_level']}/10"""
            )
            inner_thoughts = self.thinker.last_message()["content"]
            
            # 4. 生成回复
            self.companion.generate_reply(
                message=f"""请根据以下信息，以自然、情感化的方式回应用户:
                
                用户输入: {user_input}
                
                记忆上下文:
                {context_result}
                
                我的内心思考:
                {inner_thoughts}
                
                当前情绪: {self.memory_system.emotional_state['current_emotion']}
                情绪强度: {self.memory_system.emotional_state['emotion_intensity']}
                关系亲密度: {self.memory_system.emotional_state['relationship_level']}/10
                当前时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"""
            )
            response = self.companion.last_message()["content"]
            
            # 5. 保存交互
            self.memory_system.add_episodic_memory(
                user_input, 
                response,
                emotion_data,
                context=f"内心思考: {inner_thoughts}"
            )
            
            # 6. 根据情感分析，可能更新情感和关系
            if "建议" in inner_thoughts.lower():
                self.memory_manager.generate_reply(
                    message=f"""根据以下内心思考，是否需要更新情感状态或记录关系事件:
                    
                    {inner_thoughts}
                    
                    当前情绪: {self.memory_system.emotional_state['current_emotion']}
                    当前关系: {self.memory_system.emotional_state['relationship_level']}/10
                    用户情绪: {emotion_data.get('emotion', 'neutral')} ({emotion_data.get('valence', 0)})"""
                )
            
            # 打印回复
            print(f"\n[情感陪伴] {response}")
            
            # 7. 随机触发自主回忆
            if random.random() < 0.15:  # 15%的概率触发
                recall_result = self.memory_manager.generate_reply(
                    message="请触发一次自主记忆联想"
                )
                try:
                    recall_content = self.memory_manager.last_message()["content"]
                    if "没有触发" not in recall_content and len(recall_content) > 10:
                        print(f"\n[突然想起] {recall_content}")
                except:
                    pass