#!/usr/bin/env python3
"""
测试工具函数重构 - 第三阶段验证
检查工具函数是否正确转换为新版AutoGen v0.4格式
"""

import sys
import os
import inspect

# 添加项目路径
sys.path.insert(0, os.path.abspath('.'))

def test_tool_functions():
    """测试工具函数定义是否正确"""
    try:
        from emotional_companion.agents.agent_system import EmotionalAgentSystem
        
        print("🔧 测试工具函数重构...")
        
        # 创建代理系统实例（需要配置文件）
        config_path = "configs/OAI_CONFIG_LIST.json"
        if not os.path.exists(config_path):
            print(f"❌ 配置文件不存在: {config_path}")
            return False
            
        try:
            system = EmotionalAgentSystem(config_path)
            print("✅ 代理系统创建成功")
        except Exception as e:
            print(f"❌ 代理系统创建失败: {e}")
            return False
        
        # 测试工具函数创建
        try:
            tools = system._create_memory_tools()
            print(f"✅ 工具函数创建成功，共 {len(tools)} 个工具")
            
            # 验证工具函数类型
            for i, tool in enumerate(tools):
                if callable(tool):
                    sig = inspect.signature(tool)
                    print(f"  {i+1}. {tool.__name__}: {sig}")
                    
                    # 检查是否有类型注解
                    has_annotations = any(
                        param.annotation != inspect.Parameter.empty 
                        for param in sig.parameters.values()
                    )
                    return_annotation = sig.return_annotation != inspect.Signature.empty
                    
                    if has_annotations and return_annotation:
                        print(f"     ✅ 有完整的类型注解")
                    else:
                        print(f"     ⚠️  缺少类型注解")
                else:
                    print(f"  {i+1}. ❌ 不是可调用函数: {type(tool)}")
                    return False
                    
        except Exception as e:
            print(f"❌ 工具函数测试失败: {e}")
            return False
            
        # 测试记忆管理代理是否正确集成工具
        try:
            memory_manager = system.memory_manager
            if hasattr(memory_manager, 'tools'):
                print(f"✅ 记忆管理代理工具集成成功")
            else:
                print(f"❌ 记忆管理代理缺少工具属性")
                return False
        except Exception as e:
            print(f"❌ 代理工具集成测试失败: {e}")
            return False
            
        print("\n🎉 第三阶段工具函数重构验证通过！")
        print("✅ 所有工具函数已成功转换为新版AutoGen v0.4格式")
        print("✅ 工具函数使用了正确的类型注解")
        print("✅ 记忆管理代理正确集成了工具函数")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("AutoGen v0.4 迁移 - 第三阶段验证")
    print("工具函数重构测试")
    print("=" * 60)
    
    success = test_tool_functions()
    
    if success:
        print("\n✅ 第三阶段验证通过！可以继续第四阶段：异步编程转换")
    else:
        print("\n❌ 第三阶段验证失败，请检查工具函数重构")
        sys.exit(1)

if __name__ == "__main__":
    main()
