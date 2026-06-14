import re


class EquipmentNormalizer:

    MAPPINGS = {

        # Routers
        "router": "router",
        "wireless router": "router",
        "wifi router": "router",
        "wi-fi router": "router",
        "broadband router": "router",
        "edge router": "router",
        "vpn router": "router",
        "cellular router": "router",
        "lte router": "router",
        "5g router": "router",
        "industrial router": "router",

        # Switches
        "switch": "switch",
        "network switch": "switch",
        "ethernet switch": "switch",
        "managed switch": "switch",
        "unmanaged switch": "switch",
        "layer 2 switch": "switch",
        "layer 3 switch": "switch",
        "poe switch": "switch",
        "gigabit switch": "switch",

        # Firewalls
        "firewall": "firewall",
        "network firewall": "firewall",
        "security appliance": "firewall",
        "utm": "firewall",
        "next generation firewall": "firewall",
        "ngfw": "firewall",

        # Access Points
        "access point": "access_point",
        "wireless access point": "access_point",
        "wifi access point": "access_point",
        "wireless ap": "access_point",
        "ap": "access_point",

        # UPS
        "ups": "ups",
        "smart ups": "ups",
        "smart-ups": "ups",
        "online ups": "ups",
        "line interactive ups": "ups",
        "uninterruptible power supply": "ups",
        "battery backup": "ups",
        "power backup": "ups",

        # Servers
        "server": "server",
        "rack server": "server",
        "tower server": "server",
        "application server": "server",
        "database server": "server",
        "file server": "server",
        "web server": "server",

        # Storage
        "nas": "storage",
        "network attached storage": "storage",
        "storage server": "storage",
        "san": "storage",
        "storage array": "storage",
        "disk array": "storage",

        # Modems
        "modem": "modem",
        "dsl modem": "modem",
        "cable modem": "modem",
        "fiber modem": "modem",
        "4g modem": "modem",
        "5g modem": "modem",

        # Industrial Automation
        "plc": "plc",
        "programmable logic controller": "plc",
        "industrial controller": "plc",

        "hmi": "hmi",
        "human machine interface": "hmi",
        "operator panel": "hmi",
        "touch panel": "hmi",

        "vfd": "vfd",
        "variable frequency drive": "vfd",
        "ac drive": "vfd",
        "motor drive": "vfd",

        "servo drive": "servo_drive",
        "servo controller": "servo_drive",

        "servo motor": "servo_motor",

        "industrial pc": "industrial_pc",
        "ipc": "industrial_pc",

        # Power
        "power supply": "power_supply",
        "smps": "power_supply",
        "dc power supply": "power_supply",

        "pdu": "pdu",
        "power distribution unit": "pdu",

        "inverter": "inverter",
        "solar inverter": "inverter",

        # Telecom
        "olt": "olt",
        "optical line terminal": "olt",

        "onu": "onu",
        "ont": "onu",
        "optical network terminal": "onu",
        "optical network unit": "onu",

        # Wireless
        "wireless controller": "wireless_controller",
        "wlan controller": "wireless_controller",

        # Security
        "nvr": "nvr",
        "network video recorder": "nvr",

        "dvr": "dvr",
        "digital video recorder": "dvr",

        "ip camera": "camera",
        "network camera": "camera",
        "cctv camera": "camera",

        # Printers
        "printer": "printer",
        "laser printer": "printer",
        "inkjet printer": "printer",
        "multifunction printer": "printer",
        "mfp": "printer",
        "xerox": "printer",
        "xerox machine": "printer",

        # Scanners
        "scanner": "scanner",
        "document scanner": "scanner",

        # Industrial Networking
        "industrial switch": "industrial_switch",
        "industrial ethernet switch": "industrial_switch",

        "media converter": "media_converter",

        # Cooling
        "cooling unit": "cooling",
        "air conditioner": "cooling",
        "precision cooling": "cooling",

        # Generators
        "generator": "generator",
        "diesel generator": "generator",
        "genset": "generator",

        # Batteries
        "battery": "battery",
        "battery pack": "battery",
        "external battery pack": "battery",

        # Generic
        "network appliance": "network_device",
        "network device": "network_device",
    }

    # Normalize equipment name to a standard form based on common variations
    @classmethod
    def normalize(
        cls,
        equipment: str | None,
    ):

        if not equipment:
            return None

        equipment = (
            equipment
            .strip()
            .lower()
        )

        return cls.MAPPINGS.get(
            equipment,
            equipment,
        )
    
    # To detect equipment type from freeform text
    @classmethod
    def detect_from_text(cls, text: str):

        text = text.lower()

        for key in sorted(
            cls.MAPPINGS.keys(),
            key=len,
            reverse=True,
        ):
            pattern = rf"\b{re.escape(key)}\b"

            if re.search(pattern, text):
                return cls.MAPPINGS[key]

        return None