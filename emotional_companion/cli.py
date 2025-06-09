import argparse
import os
import sys
import pyfiglet
import asyncio
from emotional_companion.agents.conversation_handler import ConversationCLI
from emotional_companion.utils.time_utils import get_formatted_time

async def main():
    parser = argparse.ArgumentParser(description="情感陪伴智能体")
    parser.add_argument("--config", type=str, default="configs/OAI_CONFIG_LIST.json", 
                        help="OpenAI配置文件路径")
    parser.add_argument("--memory-db", type=str, default="memory_db",
                        help="记忆数据库存储路径")
    args = parser.parse_args()

        # 获取项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)  # 上一级目录
    
    # 如果配置文件路径是相对路径，则相对于项目根目录
    if not os.path.isabs(args.config):
        config_path = os.path.join(project_root, args.config)
    else:
        config_path = args.config
    
    # 确认配置文件存在
    if not os.path.exists(config_path):
        print(f"错误: 配置文件不存在: {config_path}")
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
        cli = ConversationCLI(config_path=config_path)
        await cli.run()
    except KeyboardInterrupt:
        print("\n程序已中断。期待下次与您交流！")
    except Exception as e:
        print(f"\n发生错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())