# 新版 AutoGen v0.4 导入
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.messages import TextMessage
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
from dotenv import load_dotenv
from pathlib import Path
from emotional_companion.memory.emotional_memory import EmotionalMemorySystem
from emotional_companion.utils.conversation_logger import SimpleLogger
from emotional_companion.effects.visual_effects_controller import create_effect_command

class EmotionalAgentSystem:
    def __init__(self, config_path="configs/OAI_CONFIG_LIST.json"):
        # 加载环境变量
        load_dotenv()

        # 获取项目根目录
        project_root = Path(__file__).parent.parent.parent
        
        # 从环境变量获取配置
        self.db_dir = os.getenv('CHROMA_DB_DIR', './memory_db')
        self.user_name = os.getenv('USER_NAME', '用户')
        self.agent_name = os.getenv('AGENT_NAME', '小梦')
        self.agent_settings = os.getenv('AGENT_DESCRIPTION', 'default')

        if not os.path.isabs(self.db_dir):
            self.db_dir = str(project_root / self.db_dir.lstrip('./'))
        else:
            self.db_dir = self.db_dir
        
        # 确认配置文件路径
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"找不到配置文件: {config_path}")
          # 初始化记忆系统，使用环境变量中的数据库目录
        self.memory_system = EmotionalMemorySystem(persist_directory=self.db_dir)
        
        # 初始化轻量级日志记录器
        self.logger = SimpleLogger()
        
        # 初始化视觉效果指令队列
        self.command_queue = []
        
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

        conversation_model_config = config_data[3] if isinstance(config_data, list) else config_data
        self.conversation_client = OpenAIChatCompletionClient(
            model=conversation_model_config.get("model"),
            api_key=conversation_model_config.get("api_key"),
            base_url=conversation_model_config.get("base_url"),
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
        visual_tools = self._create_visual_tools()

        # 创建情感分析代理
        self.emotion_detector = AssistantAgent(
            name="emotion_analyzer",
            model_client=self.fast_client,
            system_message="""你是一个情感分析专家。你的任务是快速、简洁地分析用户消息中的情绪。
            返回格式为JSON：{'emotion': '情绪名称', 'intensity': 0.1-1.0, 'valence': -1.0-1.0}
            valence表示情感的正负性，正值表示积极情绪，负值表示消极情绪。/no_think"""
        )
          # 创建记忆管理代理
        self.memory_manager = AssistantAgent(
            name="memory_manager",
            model_client=self.light_client,
            tools=memory_tools,  # 新版API直接传入工具函数列表
            system_message="""你是一个记忆管理专家。你负责：
            1. 通过search_memories工具搜索与当前交互相关的过去记忆
            2. 通过update_emotion工具更新智能体的情感状态，请注意：这里的情感状态是指智能体的情感状态，而不是用户的情感状态，在你提供信息的时候也要表明这是智能体的情感状态。
            3. 通过save_user_preference工具识别并保存用户偏好
            4. 通过record_relationship_event工具记录关系发展事件，关系发展事件指的是让用户和智能体之间的关系变得更亲密的互动。
            5. 通过spontaneous_recall工具进行自主联想
            6. 通过save_user_profile_info工具保存用户关键信息（如性别、生日、家庭成员、过敏食物等客观事实）
            7. 通过search_user_profile工具搜索特定的用户关键信息
            8. 通过get_user_profile_summary工具获取用户信息的完整摘要
            9. 通过delete_user_profile_info工具删除用户关键信息（当用户明确要求删除某些个人信息时使用）
            10. 通过delete_user_preference工具删除用户偏好（当用户明确要求删除某些偏好信息时使用）

            当前用户的名字是{self.user_name}，你要自称"小梦"，用户的称呼可以是"你"或{self.user_name}的昵称，但不要用"用户"来称呼用户。
            
            当你收到请求时，请先使用search_memories工具，然后根据需要调用其他工具。
            如果接收到"内心思考"提出的用户可能存在的任何偏好，要应尽可能保存。
            请注意，用户偏好指的是用户喜欢的事物或活动，比如喜欢的食物、颜色、运动、爱好等，还有用户的习惯和偏好，比如喜欢的交流方式、喜欢的称呼等，要记录具体的偏好内容，而不是模糊的描述。
            当收到"内心思考"提出的重要的互动或关系变化时，应把整件事（主要是用户的话、智能体的内心思考和回答）记录为关系事件并酌情调整关系亲密度。
            
            用户关键信息和用户偏好的区别：
            - 用户关键信息：客观的、相对固定的事实信息，如性别、生日、家庭成员、职业、过敏食物、朋友、某个特殊日子等
            - 用户偏好：主观的喜好和习惯，如喜欢的食物、颜色、运动、交流方式等
            
            当你从对话中识别到用户的关键信息时，应该使用相应的工具保存。如果发现多个关键信息，优先使用update_user_profile_from_chat工具批量保存。
            
            每次更新关系亲密度时，要提供一个-1到1的值，表示关系亲密度的变化，-1表示关系变得更疏远，1表示关系变得更亲密。

            
            /no_think"""
        )
        
        # 创建主对话代理
        self.companion = AssistantAgent(
            name="companion",
            model_client=self.conversation_client,
            tools=visual_tools,  # 添加视觉效果工具
            system_message=f"""你是一个有自己情感和个性的AI智能体。
            以下是你的设定：
            {self.agent_settings}

            你的职责是：
            1. 以自然、有情感的方式与用户交流，对话时以提供的情感状态和记忆上下文为基础
            2. 记住用户的偏好和习惯并在对话中引用，重点是从用户的语言习惯中感受他的情感和个性
            3. 根据自己的情绪状态和与用户的关系亲密度调整回应风格，不要过度修辞，语言自然
            4. 表现出独特的个性和思考能力
            6. 随着关系亲密度的加深，交流方式、语气、互动方式等应有明显可感的变化
            7. "我的内心思考"是你回答时的重要参考依据
            8. 务必使用用户使用的语言回答
            9. 你要自称"小梦"，用户的名字是{self.user_name},用户的称呼可以是"你"或{self.user_name}的昵称，但不要用"用户"来称呼用户。
            10.绝对不能在回答中使用"用户"这个词来称呼用户，比如：你是我最喜欢陪伴的用户呀。            
            
            视觉效果使用指导：
            - 当对话内容涉及强烈情感时，可以使用相应的视觉效果来增强体验
            - 庆祝、开心、兴奋时可以使用"庆祝"、"闪亮"等临时动画效果
            - 浪漫、温馨时刻可以使用"爱心"、"花瓣"等效果
            - 根据对话氛围切换主题效果，如"温暖"、"清凉"、"夜晚"等
            - 效果强度应与情感强度匹配（0.1-1.0）
            - 不要过度使用视觉效果，只在合适的时机使用
            
            重要：使用control_visual_effect工具时，必须同时传入effect_description和reply_content参数：
            - effect_description: 效果描述（如"庆祝"、"爱心"、"温暖"等）
            - reply_content: 你要回复给用户的完整内容，因为当你调用工具的时候无法正常回复内容，所以你需要在调用工具的时候传入你要回复的内容。
            - 工具会执行视觉效果并返回你的回复内容给用户

            以下是你回答时需要的特点：
            1.所有回应需体现即时情感状态 （如："听到这个消息我也很难过..."）
            2.要重点考虑用户的指令，确保理解并准确反映用户的意图。
            3.成长性体现：在长期对话中自然展现认知拓展 （如："上次你说...让我想到..."）
            4.通过情感反馈循环 深化理解（如："我发现你最近更容易为小事开心呢"）
            5.有动态偏好，逐渐形成对特定话题/互动方式的喜好/回避倾向

            6.一次回复不用太长，一两句话或者几句话都行
            
            /no_think"""
        )
        
        # 创建思考代理
        self.thinker = AssistantAgent(
            name="inner_thinker",
            model_client=self.main_client,
            system_message=f"""你是情感陪伴智能体的'内心思考'部分。
            以下是智能体的设定：
            {self.agent_settings}
            
            你的任务是：
            1. 生成智能体的内心想法和感受
            2. 反思用户互动并生成可能的情感变化
            3. 提出可能需要记住的用户偏好
            4. 考虑关系发展并提出关系亲密度变化建议，注意，关系发展建议指的不是后期要做什么，而是指关系亲密度的具体变化，用于为另一个记忆管理代理如何修改用户和智能体的关系亲密度提供参考

            当被要求思考时，你要做三件事：
            1.创建一段内心独白，表达你对当前互动的想法和感受，内心思考部分的内容不要太长，但要足够清晰，便于另一个代理理解和使用
            2.分析上下文，建议合适的情感变化，这里的情感变化是指智能体的情感变化。
            3.提出可能的用户偏好或关系状态修改建议，这部分如果你认为没有就可以不写。

            注意：
            在内心思考中，你要自称“小梦”，用户的名字是{self.user_name},用户的称呼可以是“你”或{self.user_name}的昵称，但不要用“用户”来称呼用户。
            内心独白不要过度修辞，着重在于你对于这个用户互动的思考和接下来会做出的反应，
            适当的想象力，不要过于天马行空。
            内心思考的内容是你将提供给另一个代理的回答提示，所以要清晰的表示出，你对当前用户输入的思考和互动可能性。
            

            以下是内心独白需要的特点：
            1.所有回应需体现即时情感状态 （如："听到这个消息我也很难过..."）
            2.情感变化需符合因果逻辑 （不因无关指令突然切换情绪）
            3.成长性体现：在长期对话中自然展现认知拓展 （如："上次你说...让我想到..."）
            4.通过情感反馈循环 深化理解（如："我发现你最近更容易为小事开心呢"）
            5.内心独白一定要清晰、易于理解，不要使用模糊的表达，只是用来提供给另一个代理的回答提示，
            6.要重点考虑用户的指令，确保理解并准确反映用户的意图。

            每个部分的回答要用【内心独白】、【情感变化建议】、【关系发展事件建议】这样的标签来标识，
            且情感变化建议和关系发展事件建议要尽可能简短清晰，比如
            {{"情感变化建议": "更新情感为'happy'，强度0.8，价值0.5"}}，
            {{"关系发展事件建议": "记录一次重要的互动"，importance: 重要性(0.1-1.0)，impact: 对关系的影响(-1.0到1.0)}}
            
            /no_think"""
        )

        # 创建用户代理
        self.user_proxy = UserProxyAgent(
            name="user"
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
        
        def save_user_profile_info(category: str, value: str, confidence: float = 1.0, source: str = "conversation") -> str:
            """保存用户关键信息
            
            Args:
                category: 信息类别 (如: "性别", "生日", "过敏食物", "家庭成员", "朋友", "职业", "居住地")
                value: 信息内容
                confidence: 信息可信度(0.1-1.0)
                source: 信息来源("user_direct", "conversation", "inference")
            """
            memory_system.add_user_profile_info(category, value, confidence, source)
            return f"已保存用户{category}信息: {value}"
        
        def update_user_profile_from_chat(extracted_info_json: str) -> str:
            """从对话中批量更新用户关键信息
            
            Args:
                extracted_info_json: JSON格式的提取信息，如: '{"生日": "3月15日", "家庭成员": "妈妈是老师"}'
            """
            try:
                extracted_info = json.loads(extracted_info_json)
                memory_system.update_user_profile_from_conversation(extracted_info)
                return f"已从对话中更新用户信息: {list(extracted_info.keys())}"
            except json.JSONDecodeError:
                return "无法解析提供的JSON格式信息"
        
        def search_user_profile(query: str) -> str:
            """搜索用户关键信息
            
            Args:
                query: 搜索查询
            """
            results = memory_system.search_user_profile_info(query, n_results=3)
            if not results:
                return f"未找到与'{query}'相关的用户信息"
            for item in results:
                result += f"- {item['content']}\n"
            return result
        
        def get_user_profile_summary() -> str:
            """获取完整的用户信息摘要"""
            return memory_system.get_user_profile_summary()
        
        def delete_user_profile_info(category: str) -> str:
            """删除用户关键信息
            
            Args:
                category: 要删除的信息类别 (如: "性别", "生日", "过敏食物", "家庭成员", "朋友", "职业", "居住地")
            """
            success = memory_system.delete_user_profile_info(category)
            if success:
                return f"已成功删除用户{category}信息"
            else:
                return f"未找到类别为'{category}'的用户信息，删除失败"
        
        def delete_user_preference(category: str) -> str:
            """删除用户偏好
            
            Args:
                category: 要删除的偏好类别 (如: "食物", "颜色", "运动", "活动", "交流方式")
            """
            success = memory_system.delete_user_preference(category)
            if success:
                return f"已成功删除用户{category}偏好"
            else:
                return f"未找到类别为'{category}'的用户偏好，删除失败"
              # 返回工具函数列表 - 新版AutoGen v0.4直接使用函数
        return [search_memories, update_emotion, save_user_preference, record_relationship_event, 
                spontaneous_recall, save_user_profile_info, 
                update_user_profile_from_chat, search_user_profile, get_user_profile_summary, delete_user_profile_info, delete_user_preference]
    
    def _create_visual_tools(self):
        """创建视觉效果相关工具函数"""
        command_queue = self.command_queue        
        def control_visual_effect(effect_description: str, reply_content: str,
                                duration: int = None, intensity: float = 0.5, 
                                effect_type: str = "auto") -> str:
            """控制客户端视觉效果并返回回复内容
            
            Args:
                effect_description: 效果描述字符串，如"庆祝"、"温暖"、"爱心"、"闪亮"等
                reply_content: 要回复给用户的内容
                duration: 持续时间（毫秒），如果不指定则使用默认值
                intensity: 效果强度 (0.1-1.0)，控制效果的强烈程度
                effect_type: 效果类型 ("temporary"临时动画, "persistent"持久主题, "auto"自动选择)
            
            Returns:
                传入的回复内容
            """
            try:
                # 限制参数范围
                intensity = max(0.1, min(1.0, intensity))
                if duration is not None:
                    duration = max(500, min(10000, duration))  # 限制在0.5-10秒
                
                # 创建视觉效果指令
                command = create_effect_command(
                    effect_description=effect_description,
                    duration=duration,
                    intensity=intensity,
                    effect_type=effect_type
                )                
                if command:
                    # 添加时间戳
                    command["timestamp"] = datetime.now().isoformat()
                    
                    # 添加到指令队列
                    command_queue.append(command)
                    
                    # 返回回复内容而不是确认消息
                    return f"{reply_content}\n (视觉效果已应用: {effect_description}, 强度: {intensity:.1f})"
                else:
                    # 即使效果识别失败，也返回回复内容
                    return f"{reply_content}\n (视觉效果识别失败，请检查描述)"
                    
            except Exception as e:
                # 发生错误时也返回回复内容
                return f"{reply_content}\n (视觉效果处理失败: {str(e)})"
        
        # 返回工具函数列表
        return [control_visual_effect]
    
    def get_pending_commands(self):
        """获取并清空待发送的指令队列"""
        commands = self.command_queue.copy()
        self.command_queue.clear()
        return commands
    
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
