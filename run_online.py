from main import online_interaction, parse_args
from interaction_logic.mas_interaction import MASInteraction

if __name__ == "__main__":
    args = parse_args()
    args.online = True  # 强制设置为在线模式
    mas = MASInteraction(debug_mode=args.debug)
    online_interaction(mas)