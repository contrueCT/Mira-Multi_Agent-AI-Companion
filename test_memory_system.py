import os
import time
from emotional_companion.memory import EmotionalMemorySystem

def test_memory_system():
    print("===== 情感记忆系统测试 =====")
    
    # 步骤1: 创建测试目录
    test_dir = "test_memory_db"
    if os.path.exists(test_dir):
        print(f"使用已存在的测试数据库：{test_dir}")
    else:
        print(f"创建新的测试数据库：{test_dir}")
    
    # 步骤2: 实例化记忆系统
    try:
        print("\n>> 测试实例化...")
        memory = EmotionalMemorySystem(persist_directory=test_dir)
        print("✓ 实例化成功")
        
        # 输出初始情感状态
        print(f"\n初始情感状态: {memory.emotional_state}")
    except Exception as e:
        print(f"✗ 实例化失败: {e}")
        return
    
    # 步骤3: 测试记忆添加
    try:
        print("\n>> 测试记忆添加...")
        memory_id = memory.add_episodic_memory(
            user_message="今天天气真好！",
            agent_response="是的，阳光明媚，心情舒畅！",
            user_emotion={"emotion": "happy", "valence": 0.8, "intensity": 0.7},
            importance=0.6
        )
        print(f"✓ 添加情节记忆成功: {memory_id}")
        
        # 添加用户偏好
        memory.add_user_preference(
            category="饮料",
            item="咖啡",
            sentiment=0.9,
            certainty=0.8
        )
        print("✓ 添加用户偏好成功")
        
        # 添加关系事件
        memory.add_relationship_event(
            event_description="首次深入交流，分享了个人经历",
            importance=0.8,
            impact=0.2
        )
        print("✓ 添加关系事件成功")
    except Exception as e:
        print(f"✗ 记忆添加失败: {e}")
    
    # 步骤4: 测试情感状态更新
    try:
        print("\n>> 测试情感状态更新...")
        memory.update_emotional_state(
            emotion="joyful",
            intensity=0.8,
            valence=0.9
        )
        print(f"✓ 情感状态更新成功: {memory.emotional_state}")
    except Exception as e:
        print(f"✗ 情感状态更新失败: {e}")
    
    # 步骤5: 测试记忆检索
    try:
        print("\n>> 测试记忆检索...")
        query = "天气 心情"
        results = memory.semantic_memory_search(query, "episodic", n_results=3)
        print(f"✓ 检索成功，找到 {len(results)} 条记忆")
        for i, result in enumerate(results):
            print(f"\n记忆 {i+1}:")
            print(f"内容: {result['content']}")
            print(f"相似度: {result['similarity']:.2f}")
            print(f"元数据: {result['metadata']}")
    except Exception as e:
        print(f"✗ 记忆检索失败: {e}")
    
    # 步骤6: 测试获取上下文
    try:
        print("\n>> 测试获取相关上下文...")
        context = memory.get_relevant_context("天气如何？")
        print("✓ 上下文获取成功:")
        print(context)
    except Exception as e:
        print(f"✗ 上下文获取失败: {e}")
    
    # 步骤7: 测试自主联想
    try:
        print("\n>> 测试自主联想...")
        association = memory.associate_spontaneously()
        if association:
            print("✓ 自主联想成功:")
            print(f"联想内容: {association['content']}")
            print(f"触发因素: {association['triggered_by']}")
        else:
            print("- 无自主联想结果")
    except Exception as e:
        print(f"✗ 自主联想失败: {e}")
    
    print("\n===== 测试完成 =====")

if __name__ == "__main__":
    test_memory_system()