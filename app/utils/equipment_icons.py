ICON_KEYWORDS = {
    "router": "router",
    "switch": "network",
    "access point": "wifi",
    "wifi": "wifi",
    "wireless": "wifi",
    "battery": "battery",
    "ups": "battery",
    "socket": "zap",
    "power": "zap",
    "electrical": "zap",
    "hvac": "wind",
    "fan": "wind",
    "motor": "settings",
    "fiber": "cable",
    "optic": "cable",
    "cable": "cable",
    "patch": "server",
    "panel": "server",
    "server": "server",
}


def get_equipment_icon(equipment: str) -> str:
    equipment_lower = equipment.lower()

    for keyword in sorted(ICON_KEYWORDS, key=len, reverse=True):
        if keyword in equipment_lower:
            return ICON_KEYWORDS[keyword]

    return "cpu"