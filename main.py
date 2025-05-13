import argparse
from interaction_logic.mas_interaction import MASInteraction

def parse_args():
    parser = argparse.ArgumentParser(description='MAS 交互系统')
    parser.add_argument('--online', action='store_true', help='启动在线模式')
    parser.add_argument('--offline', action='store_true', help='启动离线模式')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    return parser.parse_args()

def show_menu():
    print("\nMAS 交互系统")
    print("1. 在线模式")
    print("2. 离线模式")
    print("3. 退出")
    choice = input("请选择模式(1/2/3): ")
    return choice

def online_interaction(mas):
    while True:
        query = input("\n请输入您的查询(输入'exit'返回主菜单): ")
        if query.lower() == 'exit':
            break
        response = mas.online_mode(query)
        print("\n系统响应:", response)

if __name__ == "__main__":
    try:
        args = parse_args()
        mas = MASInteraction(debug_mode=args.debug)
        
        # 验证智能体初始化状态
        if not mas.is_initialized():
            raise RuntimeError("智能体初始化失败，请检查配置文件和模型连接")
            
        if args.online:
            online_interaction(mas)
        elif args.offline:
            mas.offline_mode()
        else:
            while True:
                choice = show_menu()
                if choice == '1':
                    online_interaction(mas)
                elif choice == '2':
                    mas.offline_mode()
                elif choice == '3':
                    break
                else:
                    print("无效选择，请重新输入")
    except Exception as e:
        print(f"系统启动失败: {str(e)}")
        if args.debug:
            import traceback
            traceback.print_exc()