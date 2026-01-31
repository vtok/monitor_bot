from collections import defaultdict

from config import IP_MONITORING


def build_user_ip_map() -> dict[int, list[str]]:
    user_ips = defaultdict(list)

    for ip_name, cfg in IP_MONITORING.items():
        for user_id in cfg["members"]:
            user_ips[user_id].append(ip_name)

    return dict(user_ips)


USER_IP_MAP = build_user_ip_map()
