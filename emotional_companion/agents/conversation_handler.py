"""
对话处理器模块
专门处理对话流程，为外部接口提供简洁的调用方式
"""

import json
import time
import asyncio
from datetime import datetime
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from .agent_system import EmotionalAgentSystem


class ConversationHandler:
    """对话处理器 - 封装对话流程逻辑"""
    
    def __init__(self, config_path="configs/OAI_CONFIG_LIST.json"):
        """初始化对话处理器"""
        self.agent_system = EmotionalAgentSystem(config_path)
        self.is_first_conversation = True  # 跟踪是否是应用启动后的首次对话
        self.last_agent_response = None    # 保存上一次智能体的回复
        
    async def get_response(self, user_message: str, enable_timing=False) -> str:
        """
        获取智能体对用户消息的回复
        
        Args:
            user_message: 用户输入的消息
            enable_timing: 是否启用时间统计
            
        Returns:
            str: 智能体的回复文本
        """
        try:
            # 开始计时（可选）
            if enable_timing:
                total_start = time.perf_counter()
                print(f"\n[处理中] 正在分析用户消息: {user_message[:50]}...")
            
            # 记录日志
            self.agent_system.logger.new_chat(user_message)
            
            # 创建cancellation token
            cancellation_token = CancellationToken()
            
            # 执行完整的对话流程
            response = await self._process_conversation_flow(
                user_message, 
                cancellation_token, 
                enable_timing
            )
            
            # 显示总时间（可选）
            if enable_timing:
                total_time = time.perf_counter() - total_start
                print(f"[完成] 总处理时间: {total_time:.2f}秒")
            
            return response
            
        except Exception as e:
            error_msg = f"抱歉，我遇到了一些问题：{str(e)}"
            print(f"[错误] {error_msg}")            
            return error_msg
    
    async def _process_conversation_flow(self, user_input: str, cancellation_token, enable_timing=False):
        """处理完整的对话流程"""
        
        # 1. 并行执行情绪分析和记忆搜索
        parallel_start = time.perf_counter() if enable_timing else 0
        
        # 使用asyncio.gather并行执行
        emotion_analysis, context_result = await asyncio.gather(
            self._analyze_emotion(user_input, cancellation_token),
            self._search_memory(user_input, cancellation_token)
        )
        
        if enable_timing:
            parallel_time = time.perf_counter() - parallel_start
            print(f"  情感分析&记忆检索(并行): {parallel_time:.2f}秒")
        
        # 记录情感分析和记忆上下文
        self.agent_system.logger.step("emotion", emotion_analysis)
        self.agent_system.logger.step("memory", context_result)
        
        # 解析情感数据
        emotion_data = self._parse_emotion_data(emotion_analysis)
        
        # 2. 生成内心思考
        thought_start = time.perf_counter() if enable_timing else 0
        inner_thoughts = await self._generate_thoughts(user_input, emotion_data, context_result, cancellation_token)
        if enable_timing:
            thought_time = time.perf_counter() - thought_start
            print(f"  内心思考: {thought_time:.2f}秒")
        
        # 记录内心思考
        self.agent_system.logger.step("thinking", inner_thoughts)
        
        # 3. 生成回复
        companion_start = time.perf_counter() if enable_timing else 0
        response = await self._generate_response(user_input, context_result, inner_thoughts, cancellation_token)
        if enable_timing:
            companion_time = time.perf_counter() - companion_start
            print(f"  对话生成: {companion_time:.2f}秒")
        
        # 记录智能体回答
        self.agent_system.logger.step("response", response)
          # 4. 异步保存记忆和更新状态（不等待完成）
        asyncio.create_task(self._save_and_update_async(
            user_input, response, emotion_data, inner_thoughts, cancellation_token
        ))
        
        # 5. 更新对话状态
        self.last_agent_response = response
        self.is_first_conversation = False
        
        return response
    
    async def _analyze_emotion(self, user_input: str, cancellation_token) -> str:
        """分析用户情绪"""
        emotion_message = TextMessage(
            content=f"分析这句话中的情绪: {user_input}",
            source="user"
        )
        
        emotion_response = await self.agent_system.emotion_detector.on_messages([emotion_message], cancellation_token)
        return emotion_response.chat_message.content if emotion_response.chat_message else "{}"
    async def _search_memory(self, user_input: str, cancellation_token) -> str:
        """搜索相关记忆（不处理用户偏好）"""
        # 获取当前时间信息
        current_time = datetime.now()
        time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        weekday = current_time.strftime("%A")  # 星期几
        
        memory_message = TextMessage(
        content=f"""请搜索与以下用户输入相关的记忆，并获取完整的用户信息。

                    用户输入: {user_input}

                    当前时间信息:
                    - 日期时间: {time_str}
                    - 星期: {weekday}

                    请在搜索记忆时考虑时间因素，如果用户提到时间相关的内容（如"昨天"、"上周"、"最近"等），请结合当前时间进行准确的记忆检索。""",
        source="user"
                        )
        memory_response = await self.agent_system.memory_manager.on_messages([memory_message], cancellation_token)
        return memory_response.chat_message.content if memory_response.chat_message else "无相关记忆"
    
    async def _generate_thoughts(self, user_input: str, emotion_data: dict, context_result: str, cancellation_token) -> str:
        """生成内心思考"""
        # 获取思考专用的上下文
        thinking_context = self._get_thinking_context()
        
        thought_message = TextMessage(
            content=f"""请思考以下用户输入和上下文，生成一段内心独白，并建议适当的情感变化:
            
            用户输入: "{user_input}"
            用户情绪: {emotion_data.get('emotion', 'neutral')} (强度: {emotion_data.get('intensity', 0.5)})
            
            记忆上下文:
            {context_result}
            
            对话上下文:
            {thinking_context}
            
            当前关系亲密度: {self.agent_system.memory_system.emotional_state['relationship_level']}/10""",
            source="user"
        )
        
        thought_response = await self.agent_system.thinker.on_messages([thought_message], cancellation_token)
        return thought_response.chat_message.content if thought_response.chat_message else "无法生成思考"
    
    async def _generate_response(self, user_input: str, context_result: str, inner_thoughts: str, cancellation_token) -> str:
        """生成最终回复"""
        companion_message = TextMessage(
            content=f"""请根据以下信息，以自然、情感化的方式回应用户，
            如果用户提到了时间相关的话，请结合当前时间和记忆上下文的时间进行回应，
            提供的记忆上下文可能包含一些无关的内容，请仔细甄别使用，不要混淆。:

            用户输入: {user_input}
            
            记忆上下文:
            {context_result}
            
            我的内心思考:
            {inner_thoughts}
            
            当前情绪: {self.agent_system.memory_system.emotional_state['current_emotion']}
            情绪强度: {self.agent_system.memory_system.emotional_state['emotion_intensity']}
            关系亲密度: {self.agent_system.memory_system.emotional_state['relationship_level']}/10
            当前时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 星期{['一', '二', '三', '四', '五', '六', '日'][datetime.now().weekday()]}""",
            source="user"
        )
        
        companion_response = await self.agent_system.companion.on_messages([companion_message], cancellation_token)
        return companion_response.chat_message.content if companion_response.chat_message else "抱歉，我无法回应"
    async def _save_and_update_async(self, user_input: str, response: str, emotion_data: dict, inner_thoughts: str, cancellation_token):
        """异步保存记忆和更新状态，根据内心思考处理用户偏好"""
        try:
            # 保存交互记忆
            self.agent_system.memory_system.add_episodic_memory(
                user_input, 
                response,
                emotion_data,
                context=f"内心思考: {inner_thoughts}"
            )
            
            # 根据内心思考更新情感状态和处理用户偏好
            update_message = TextMessage(
                content=f"""根据以下内心思考，请：
                1. 判断是否需要更新智能体情感状态（使用update_emotion）
                2. 判断是否记录关系事件（record_relationship_event）
                3. 根据内心思考的建议处理可能的用户偏好（save_user_preference）
                4. 记录可能的用户信息（save_user_profile_info），用户信息也包括上下班时间这些日常时间，假如用户提到时间相关的内容（如"昨天"、"上周"、"最近"等），
                   请结合当前时间记录具体的时间，比如用户说明天下午要考试，当前时间是2025-06-09，星期一，你就要记录用户的考试时间为2025-06-10，星期二下午。

                内心思考内容:
                {inner_thoughts}
                
                当前对话上下文：
                用户输入: {user_input}
                智能体回答: {response}
                用户情绪: {emotion_data.get('emotion', 'neutral')} ({emotion_data.get('valence', 0)})
                
                当前状态:
                当前情绪: {self.agent_system.memory_system.emotional_state['current_emotion']}
                当前关系: {self.agent_system.memory_system.emotional_state['relationship_level']}/10
                
                如果需要记录关系事件或用户偏好，请简要描述事件内容和重要性。""",
                source="user"
            )
            
            change = await self.agent_system.memory_manager.on_messages([update_message], cancellation_token)
            self.agent_system.logger.step("emotionalchange", change.chat_message.content if change.chat_message else "无情感更新")
                
        except Exception as e:
            # 静默处理保存失败，不影响主流程
            print(f"[警告] 记忆保存失败: {e}")
    
    async def _handle_spontaneous_recall(self, cancellation_token):
        """处理自主回忆"""
        try:
            recall_message = TextMessage(
                content="请触发一次自主记忆联想",
                source="user"
            )
            
            recall_response = await self.agent_system.memory_manager.on_messages([recall_message], cancellation_token)
            recall_content = recall_response.chat_message.content if recall_response.chat_message else ""
            
            if recall_content and "没有触发" not in recall_content and len(recall_content) > 10:
                try:
                    recall_data = json.loads(recall_content)
                    if recall_data.get("type") == "spontaneous_memory":
                        content = recall_data.get("content", "").encode().decode('unicode_escape')
                        triggered_by = recall_data.get("triggered_by", "").encode().decode('unicode_escape')
                        print(f"\n[突然想起] {content}")
                        print(f"[联想触发] {triggered_by}")
                    else:
                        print(f"\n[突然想起] {recall_content}")
                except json.JSONDecodeError:
                    print(f"\n[突然想起] {recall_content}")
        except Exception:
            # 静默处理异常
            pass
    
    def _parse_emotion_data(self, emotion_analysis: str) -> dict:
        """解析情感分析数据"""
        try:
            return json.loads(emotion_analysis)
        except:
            return {"emotion": "neutral", "intensity": 0.5, "valence": 0}
    
    def get_current_emotional_state(self) -> dict:
        """获取当前情感状态"""
        return self.agent_system.memory_system.emotional_state
    
    def start_background_tasks(self):
        """启动后台任务（如果需要）"""
        self.agent_system.start_background_tasks()
    
    def stop_background_tasks(self):
        """停止后台任务"""
        self.agent_system.autonomous_mode = False
    def _get_thinking_context(self) -> str:
        """获取内心思考的上下文"""
        try:
            if self.is_first_conversation:
                # 应用刚启动，首次对话
                return "这是应用启动后的第一次对话。"
            else:
                # 已经进行过对话，使用上一次智能体的回复
                if self.last_agent_response:
                    return f"我上一次对用户的回复: {self.last_agent_response}"
                else:
                    return "这是我们本次会话的第一次对话。"
        except Exception as e:
            return f"获取上下文时出错: {str(e)}"
    

# 简化的CLI接口
class ConversationCLI:
    """简化的命令行接口"""
    
    def __init__(self, config_path="configs/OAI_CONFIG_LIST.json"):
        self.handler = ConversationHandler(config_path)
    
    async def run(self):
        """运行命令行对话界面"""
        # 启动后台任务
        self.handler.start_background_tasks()
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        emotional_state = self.handler.get_current_emotional_state()
        
        print(f"[系统] 当前时间: {current_time}")
        print(f"[系统] 情感状态: {emotional_state['current_emotion']}")
        print(f"[系统] 关系亲密度: {emotional_state['relationship_level']}/10")
        
        # 主对话循环
        while True:
            user_input = input("\n[您] ")
            
            if user_input.lower() == "再见":
                print("[小梦] 再见！期待下次与您交流。")
                break
            
            # 获取回复并显示时间统计
            response = await self.handler.get_response(user_input, enable_timing=True)
            print(f"\n[小梦] {response}")