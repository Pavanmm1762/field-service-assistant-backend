class VisionService:

    def analyze_image(self, image_path: str):
        return {
            "equipment": "Router",
            "issue": "Damaged Ethernet Port",
            "severity": "Medium",
            "confidence": 92
        }