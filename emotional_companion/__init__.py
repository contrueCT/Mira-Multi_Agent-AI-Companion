"""
情感陪伴智能体系统

基于AutoGen和ChromaDB构建的高级情感陪伴智能体
"""

__version__ = '0.1.0'

# 这里的导入会在用户实际实现完成后更新
# 暂时保留基本导入
from emotional_companion.agents.agent_system import AgentSystem, Agent, EmotionalAgent
from emotional_companion.memory.emotional_memory import EmotionalMemory

__all__ = ['AgentSystem', 'Agent', 'EmotionalAgent', 'EmotionalMemory']