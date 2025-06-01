# 新版 AutoGen v0.4 导入
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient

# 其他必要导入
import json
import random
from datetime import datetime
import threading
import schedule
import time
import os
import asyncio
from typing import List, Optional
from emotional_companion.memory.emotional_memory import EmotionalMemorySystem
from emotional_companion.utils.conversation_logger import SimpleLogger

class EmotionalAgentSystem:
    def __init__(self, config_path="configs/OAI_CONFIG_LIST.json"):
        # 确认配置文件路径
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"找不到配置文件: {config_path}")
        
        # 初始化记忆系统
        self.memory_system = EmotionalMemorySystem()
        
        # 初始化轻量级日志记录器
        self.logger = SimpleLogger()
        
        # 初始化代理系统
        self.setup_agents(config_path)
        
        # 自主模式标志
        self.autonomous_mode = False
    def setup_agents(self, config_path):
        """设置代理系统"""
        # 配置LLM - 新版AutoGen v0.4配置方式
        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 创建OpenAI客户端
        main_model_config = config_data[0] if isinstance(config_data, list) else config_data
        self.main_client = OpenAIChatCompletionClient(
            model=main_model_config.get("model"),
            api_key=main_model_config.get("api_key"),
            base_url=main_model_config.get("base_url"),
                model_info={
                "vision": False,
                "function_calling": True,
                "json_output": True,
                "family": "unknown",
                "structured_output": True,
                }
        )

        fast_model_config = config_data[1] if isinstance(config_data, list) else config_data
        self.fast_client = OpenAIChatCompletionClient(
            model=fast_model_config.get("model"),
            api_key=fast_model_config.get("api_key"),
            base_url=fast_model_config.get("base_url"),
                model_info={
                "vision": False,
                "function_calling": True,
                "json_output": True,
                "family": "unknown",
                "structured_output": True,
                }
        )

        light_model_config = config_data[2] if isinstance(config_data, list) else config_data
        self.light_client = OpenAIChatCompletionClient(
            model=light_model_config.get("model"),
            api_key=light_model_config.get("api_key"),
            base_url=light_model_config.get("base_url"),
                model_info={
                "vision": False,
                "function_calling": True,
                "json_output": True,
                "family": "unknown",
                "structured_output": True,
                }
        )
        
        # 创建工具函数
        memory_tools = self._create_memory_tools()     

        # 创建情感分析代理
        self.emotion_detector = AssistantAgent(
            name="emotion_analyzer",
            model_client=self.fast_client,
            system_message="""你是一个情感分析专家。你的任务是分析用户消息中的情绪和可能隐含的偏好。
            返回格式为JSON：{'emotion': '情绪名称', 'intensity': 0.1-1.0, 'valence': -1.0-1.0, 
            'possible_preferences': [{'category': '类别', 'item': '项目', 'certainty': 0.1-1.0, 'sentiment': -1.0-1.0}]}
            valence表示情感的正负性，正值表示积极情绪，负值表示消极情绪。"""
        )
        
        # 创建记忆管理代理
        self.memory_manager = AssistantAgent(
            name="memory_manager",
            model_client=self.main_client,
            tools=memory_tools,  # 新版API直接传入工具函数列表
            system_message="""你是一个记忆管理专家。你负责：
            1. 通过search_memories工具搜索与当前交互相关的过去记忆
            2. 通过update_emotion工具更新智能体的情感状态
            3. 通过save_user_preference工具识别并保存用户偏好
            4. 通过record_relationship_event工具记录关系发展事件，关系发展事件指的是让用户和智能体之间的关系变得更亲密的互动。
            5. 通过spontaneous_recall工具进行自主联想
            
            当你收到请求时，请先使用search_memories工具，然后根据需要调用其他工具。
            对于用户透露的任何偏好，都应尽可能保存。
            当发现重要的互动时，应记录为关系事件并酌情调整关系亲密度。"""
        )
        
        # 创建主对话代理
        self.companion = AssistantAgent(
            name="companion",
            model_client=self.light_client,
            system_message=f"""你是一个有自己情感和个性的AI陪伴。你的职责是：
            1. 以自然、有情感的方式与用户交流
            2. 记住用户的偏好和习惯并在对话中引用
            3. 根据自己的情绪状态和与用户的关系亲密度调整回应风格
            4. 表现出独特的个性和思考能力
            5. 你知道自己是个ai智能体，但你会表现得像一个有情感的朋友
            6. 随着关系亲密度的加深，交流方式应变得更加亲密和私人化
            务必使用用户使用的语言回答
            你要自称“小梦”
            
            当前情绪: {self.memory_system.emotional_state['current_emotion']}
            情绪强度: {self.memory_system.emotional_state['emotion_intensity']}
            关系亲密度: {self.memory_system.emotional_state['relationship_level']}/10"""
        )
        
        # 创建思考代理
        self.thinker = AssistantAgent(
            name="inner_thinker",
            model_client=self.main_client,
            system_message="""你是情感陪伴智能体的'内心思考'部分。你的任务是：
            1. 生成智能体的内心想法和感受
            2. 反思用户互动并生成可能的情感变化
            3. 提出可能需要记住的用户偏好
            4. 考虑关系发展并提出关系亲密度变化建议
            
            当被要求思考时，创建一段短小的内心独白，表达你对当前互动的想法和感受，
            并建议合适的情感变化。情感应随着用户互动自然变化，不要保持一成不变。"""
        )
          # 创建用户代理
        self.user_proxy = UserProxyAgent(
            name="user"
            # 注意：新版API中UserProxyAgent的参数不同，先保留最基本的配置
        )
    
    def _create_memory_tools(self):
        """创建记忆相关工具函数"""
        memory_system = self.memory_system
        
        # 新版AutoGen v0.4工具函数定义 - 直接函数格式
        def search_memories(query: str) -> str:
            """搜索与用户互动相关的记忆"""
            return memory_system.get_relevant_context(query)
        
        def update_emotion(emotion: str, intensity: float = None, valence: float = None) -> str:
            """更新情感状态
            
            Args:
                emotion: 情感名称
                intensity: 情感强度(0.1-1.0)
                valence: 情感价值(-1.0至1.0，负值表示消极情绪，正值表示积极情绪)
            """
            memory_system.update_emotional_state(emotion, intensity, valence)
            return f"情感已更新为: {emotion}, 强度: {intensity if intensity else '不变'}"
        
        def save_user_preference(category: str, item: str, sentiment: float = 1.0, certainty: float = 0.8) -> str:
            """保存用户偏好
            
            Args:
                category: 偏好类别，如'食物'，'颜色'，'活动'
                item: 具体偏好项目
                sentiment: 情感倾向(-1.0到1.0)
                certainty: 确定性(0.1-1.0)
            """
            memory_system.add_user_preference(category, item, sentiment, certainty)
            return f"已记录用户偏好: {category} - {item}"
        
        def record_relationship_event(description: str, importance: float = 0.7, impact: float = 0.1) -> str:
            """记录关系发展事件
            
            Args:
                description: 事件描述
                importance: 重要性(0.1-1.0)
                impact: 对关系的影响(-1.0到1.0)
            """
            memory_system.add_relationship_event(description, importance, impact)
            return f"已记录关系事件: {description}"
        
        def spontaneous_recall() -> str:
            """触发自主记忆联想"""
            memory = memory_system.associate_spontaneously()
            if memory:
                return json.dumps(memory)
            return "没有触发自主回忆"
            
        # 返回工具函数列表 - 新版AutoGen v0.4直接使用函数
        return [search_memories, update_emotion, save_user_preference, record_relationship_event, spontaneous_recall]
    
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
                    # 由于_generate_proactive_message现在是异步的，我们需要在异步上下文中运行它
                    try:
                        asyncio.create_task(self._generate_proactive_message())
                    except RuntimeError:
                        # 如果没有运行的事件循环，我们跳过主动消息
                        print("[系统] 想要主动发起对话，但异步环境不可用")
                        pass        
        schedule.every(1).to(3).hours.do(random_emotion_update)
        
        # 启动调度线程
        def run_schedule():
            while self.autonomous_mode:
                schedule.run_pending()
                time.sleep(60)
        
        threading.Thread(target=run_schedule, daemon=True).start()
        print("[系统] 自主模式已启动，智能体将在后台运行并偶尔主动与你交流")
    
    async def _generate_proactive_message(self):
        """生成主动消息"""
        current_emotion = self.memory_system.emotional_state["current_emotion"]
        relationship_level = self.memory_system.emotional_state["relationship_level"]
        
        cancellation_token = CancellationToken()
        
        # 生成思考
        thought_message = TextMessage(
            content=f"""根据当前情绪({current_emotion})和关系亲密度({relationship_level}/10)，
            生成一条可能的主动对话消息。这条消息应该体现当前情绪状态，
            并且符合当前关系亲密度的互动风格。""",
            source="system"
        )
        
        thought_response = await self.thinker.on_messages([thought_message], cancellation_token)
        thought = thought_response.chat_message.content if thought_response.chat_message else "无法生成思考"
        
        # 使用思考生成主动消息
        companion_message = TextMessage(
            content=f"""基于以下内心思考，生成一条简短的主动消息:
            
            {thought}
            
            当前情绪: {current_emotion}
            关系亲密度: {relationship_level}/10
            当前时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}""",
            source="system"
        )
        response = await self.companion.on_messages([companion_message], cancellation_token)
        message = response.chat_message.content if response.chat_message else "无法生成回复"
        print(f"\n[情感陪伴] {message}")
    
    async def run_conversation(self):
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
            
            # 开始日志记录
            self.logger.new_chat(user_input)
            
            # 创建cancellation token
            cancellation_token = CancellationToken()
            
            # 1. 分析用户情绪
            emotion_message = TextMessage(
                content=f"分析这句话中的情绪: {user_input}",
                source="user"
            )
            
            emotion_response = await self.emotion_detector.on_messages([emotion_message], cancellation_token)
            emotion_analysis = emotion_response.chat_message.content if emotion_response.chat_message else "{}"
            
            # 记录情感分析
            self.logger.step("emotion", emotion_analysis)
            
            # 测试输出
            print(f"\n[情感分析] （{emotion_analysis}）")

            # 解析情感数据
            try:
                emotion_data = json.loads(emotion_analysis)
            except:
                emotion_data = {"emotion": "neutral", "intensity": 0.5, "valence": 0}
              # 2. 获取记忆与上下文
            memory_message = TextMessage(
                content=f"请搜索与以下用户输入相关的记忆，并处理可能的用户偏好:\n{user_input}\n\n用户情绪分析结果:\n{emotion_analysis}",
                source="user"
            )
            
            memory_response = await self.memory_manager.on_messages([memory_message], cancellation_token)
            context_result = memory_response.chat_message.content if memory_response.chat_message else "无相关记忆"
            
            # 记录记忆上下文
            self.logger.step("memory", context_result)
            
            # 测试输出
            print(f"\n[记忆上下文] （{context_result}）")

            # 3. 生成内心思考
            thought_message = TextMessage(
                content=f"""请思考以下用户输入和上下文，生成一段内心独白，并建议适当的情感变化:
                
                用户输入: "{user_input}"
                用户情绪: {emotion_data.get('emotion', 'neutral')} (强度: {emotion_data.get('intensity', 0.5)})
                
                上下文:
                {context_result}
                
                当前关系亲密度: {self.memory_system.emotional_state['relationship_level']}/10""",
                source="user"
            )
            
            thought_response = await self.thinker.on_messages([thought_message], cancellation_token)
            inner_thoughts = thought_response.chat_message.content if thought_response.chat_message else "无法生成思考"
            
            # 记录内心思考
            self.logger.step("thinking", inner_thoughts)
            
            # 测试输出
            print(f"\n[内心思考] （{inner_thoughts}）")

            # 4. 生成回复
            companion_message = TextMessage(
                content=f"""请根据以下信息，以自然、情感化的方式回应用户:
                
                用户输入: {user_input}
                
                记忆上下文:
                {context_result}
                
                我的内心思考:
                {inner_thoughts}
                
                当前情绪: {self.memory_system.emotional_state['current_emotion']}
                情绪强度: {self.memory_system.emotional_state['emotion_intensity']}
                关系亲密度: {self.memory_system.emotional_state['relationship_level']}/10
                当前时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}""",
                source="user"
            )
            
            companion_response = await self.companion.on_messages([companion_message], cancellation_token)
            response = companion_response.chat_message.content if companion_response.chat_message else "抱歉，我无法回应"
            
            # 记录智能体回答
            self.logger.step("response", response)
            
            # 5. 保存交互
            self.memory_system.add_episodic_memory(
                user_input, 
                response,
                emotion_data,
                context=f"内心思考: {inner_thoughts}"
            )
            
            # 6. 根据情感分析，可能更新情感和关系
            if "建议" in inner_thoughts.lower():
                update_message = TextMessage(
                    content=f"""根据以下内心思考，是否需要更新情感状态或记录关系事件:
                    
                    {inner_thoughts}
                    
                    当前情绪: {self.memory_system.emotional_state['current_emotion']}
                    当前关系: {self.memory_system.emotional_state['relationship_level']}/10
                    用户情绪: {emotion_data.get('emotion', 'neutral')} ({emotion_data.get('valence', 0)})""",
                    source="user"
                )
                
                change = await self.memory_manager.on_messages([update_message], cancellation_token)
            
                # 测试输出，是否更新了情感状态
                print(f"\n[情感更新] （{change.chat_message.content if change.chat_message else '无情感更新'}）")

            # 打印回复
            print(f"\n[小梦] {response}")
            
            # 7. 随机触发自主回忆
            if random.random() < 0.15:  # 15%的概率触发
                recall_message = TextMessage(
                    content="请触发一次自主记忆联想",
                    source="user"
                )
                
                try:
                    recall_response = await self.memory_manager.on_messages([recall_message], cancellation_token)
                    recall_content = recall_response.chat_message.content if recall_response.chat_message else ""
                    if recall_content and "没有触发" not in recall_content and len(recall_content) > 10:
                        # 解析JSON并格式化显示
                        try:
                            recall_data = json.loads(recall_content)
                            if recall_data.get("type") == "spontaneous_memory":
                                # 解码Unicode转义字符并格式化显示
                                content = recall_data.get("content", "").encode().decode('unicode_escape')
                                triggered_by = recall_data.get("triggered_by", "").encode().decode('unicode_escape')
                                print(f"\n[突然想起] {content}")
                                print(f"[联想触发] {triggered_by}")
                            else:
                                print(f"\n[突然想起] {recall_content}")
                        except json.JSONDecodeError:
                            # 如果不是JSON格式，直接显示
                            print(f"\n[突然想起] {recall_content}")
                except Exception as e:
                    # 静默处理异常，不影响主对话流程
                    pass