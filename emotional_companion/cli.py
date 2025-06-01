import argparse
import os
import sys
import pyfiglet
from emotional_companion.agents.agent_system import EmotionalAgentSystem
from emotional_companion.utils.time_utils import get_formatted_time
def main():
    parser = argparse.ArgumentParser(description="情感陪伴智能体")
    parser.add_argument("--config", type=str, default="configs/OAI_CONFIG_LIST.json", 
                        help="OpenAI配置文件路径")
    parser.add_argument("--memory-db", type=str, default="memory_db",
                        help="记忆数据库存储路径")
    args = parser.parse_args()
    
    # 确认配置文件存在
    if not os.path.exists(args.config):
        print(f"错误: 配置文件不存在: {args.config}")
        print("请创建配置文件或使用--config指定正确的路径")
        return
    
    # 显示欢迎标语
    title = pyfiglet.figlet_format("情感陪伴智能体", font="slant")
    print(title)
    print("=" * 50)
    print("欢迎使用情感陪伴智能体！")
    print("- 输入 '再见' 结束对话")
    print("=" * 50)
    
    # 当前时间
    print(f"当前时间: {get_formatted_time()}")
    print("\n初始化系统中，请稍候...\n")
    
    # 启动对话系统
    try:
        agent_system = EmotionalAgentSystem(config_path=args.config)
        agent_system.run_conversation()
    except KeyboardInterrupt:
        print("\n程序已中断。期待下次与您交流！")
    except Exception as e:
        print(f"\n发生错误: {e}")

if __name__ == "__main__":
    main()