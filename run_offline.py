from main import parse_args
from interaction_logic.mas_interaction import MASInteraction

if __name__ == "__main__":
    args = parse_args()
    args.offline = True  # 强制设置为离线模式
    mas = MASInteraction(debug_mode=args.debug)
    mas.offline_mode()