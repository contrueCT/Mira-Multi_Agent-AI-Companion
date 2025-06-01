#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试异步代理系统
验证第四阶段的异步编程转换是否成功
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from emotional_companion.agents.agent_system import EmotionalAgentSystem

async def test_async_agents():
    """测试异步代理系统"""
    print("=== 测试异步代理系统 ===")
    
    try:
        # 创建代理系统
        agent_system = EmotionalAgentSystem()
        print("✅ 代理系统初始化成功")
        
        # 测试异步主动消息生成
        print("\n测试异步主动消息生成...")
        await agent_system._generate_proactive_message()
        print("✅ 异步主动消息生成成功")
        
        # 测试简单的对话流程（不运行完整的对话循环）
        print("\n测试异步对话处理...")
        
        # 我们创建一个简化的测试来验证异步流程
        from autogen_core import CancellationToken
        from autogen_agentchat.messages import TextMessage
        
        cancellation_token = CancellationToken()
        test_message = TextMessage(
            content="你好，今天心情如何？",
            source="user"
        )
        
        # 测试情感分析代理
        emotion_response = await agent_system.emotion_detector.on_messages([test_message], cancellation_token)
        print(f"✅ 情感分析代理响应: {emotion_response.chat_message.content[:100] if emotion_response.chat_message else 'None'}...")
        
        # 测试记忆管理代理
        memory_response = await agent_system.memory_manager.on_messages([test_message], cancellation_token)
        print(f"✅ 记忆管理代理响应: {memory_response.chat_message.content[:100] if memory_response.chat_message else 'None'}...")
        
        # 测试陪伴代理
        companion_response = await agent_system.companion.on_messages([test_message], cancellation_token)
        print(f"✅ 陪伴代理响应: {companion_response.chat_message.content[:100] if companion_response.chat_message else 'None'}...")
        
        print("\n=== 所有异步测试通过！ ===")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_imports():
    """测试导入是否正确"""
    print("=== 测试导入 ===")
    
    try:
        from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
        from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
        from autogen_agentchat.messages import TextMessage, SystemMessage
        from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
        from autogen_core import CancellationToken
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        print("✅ 所有AutoGen v0.4模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("开始测试AutoGen v0.4异步代理系统...")
    
    # 测试导入
    if not test_imports():
        return
    
    # 测试异步代理
    await test_async_agents()
    
    print("\n测试完成！")

if __name__ == "__main__":
    asyncio.run(main())
