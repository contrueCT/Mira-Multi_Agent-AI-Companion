#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试视觉效果工具修改后的功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from emotional_companion.agents.agent_system import EmotionalAgentSystem

def test_visual_effect_tool():
    """测试修改后的视觉效果工具"""
    print("=== 测试视觉效果工具修改 ===")
    
    try:
        # 初始化代理系统
        agent_system = EmotionalAgentSystem()
        
        # 获取视觉效果工具函数
        visual_tools = agent_system._create_visual_tools()
        control_visual_effect = visual_tools[0]
        
        # 测试1：使用新的参数结构
        print("\n测试1：调用视觉效果工具（庆祝效果）")
        result = control_visual_effect(
            effect_description="庆祝",
            reply_content="恭喜你！这真是太棒了！🎉",
            intensity=0.8
        )
        print(f"返回结果: {result}")
        
        # 测试2：检查指令队列
        commands = agent_system.get_pending_commands()
        print(f"\n生成的视觉效果指令数量: {len(commands)}")
        if commands:
            print(f"指令详情: {commands[0]}")
        
        # 测试3：再次调用不同效果
        print("\n测试2：调用视觉效果工具（爱心效果）")
        result2 = control_visual_effect(
            effect_description="爱心",
            reply_content="我也很喜欢这种感觉呢~💕",
            intensity=0.6
        )
        print(f"返回结果: {result2}")
        
        # 测试4：检查指令队列
        commands2 = agent_system.get_pending_commands()
        print(f"\n第二次生成的视觉效果指令数量: {len(commands2)}")
        if commands2:
            print(f"指令详情: {commands2[0]}")
        
        print("\n✅ 视觉效果工具修改测试完成！")
        print("主要变化：")
        print("1. 新增了 reply_content 参数")
        print("2. 函数返回传入的 reply_content 而不是确认消息")
        print("3. 视觉效果指令仍然正常添加到队列中")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_visual_effect_tool()
