"""
依赖导入检查脚本
"""
import sys
import importlib
import traceback

def check_import(module_name, package_name=None):
    """
    检查模块是否可以导入
    
    Args:
        module_name (str): 模块名称
        package_name (str, optional): 包名，用于显示
    
    Returns:
        bool: 是否成功导入
    """
    if package_name is None:
        package_name = module_name
        
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, '__version__'):
            print(f"✓ {package_name} 导入成功 (版本: {module.__version__})")
        else:
            print(f"✓ {package_name} 导入成功")
        return True
    except ImportError as e:
        print(f"✗ {package_name} 导入失败: {e}")
        return False
    except Exception as e:
        print(f"✗ {package_name} 导入出现错误: {e}")
        traceback.print_exc()
        return False

def main():
    """检查所有必要的依赖"""
    print("=== 依赖检查 ===")
    
    dependencies = [
        ("autogen", "AutoGen"),
        ("pyautogen", "PyAutoGen"),
        ("chromadb", "ChromaDB"),
        ("sentence_transformers", "Sentence Transformers"),
        ("schedule", "Schedule"),
        ("pyfiglet", "PyFiglet"),
        ("dotenv", "Python-dotenv"),
        ("emotional_companion", "Emotional Companion")
    ]
    
    success_count = 0
    
    for module_name, package_name in dependencies:
        if check_import(module_name, package_name):
            success_count += 1
            
    print(f"\n总结: 成功导入 {success_count}/{len(dependencies)} 个依赖")
    
    # 检查项目特定模块
    print("\n=== 项目模块检查 ===")
    project_modules = [
        "emotional_companion.utils.time_utils",
        "emotional_companion.utils.env_utils",
        "emotional_companion.memory.emotional_memory",
        "emotional_companion.agents.agent_system",
        "emotional_companion.cli"
    ]
    
    project_success = 0
    for module in project_modules:
        if check_import(module):
            project_success += 1
            
    print(f"\n总结: 成功导入 {project_success}/{len(project_modules)} 个项目模块")

if __name__ == "__main__":
    main()
