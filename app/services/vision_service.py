# app/services/vision_service.py

import json
from google import genai
from PIL import Image
from app.core.config import settings


class VisionService:

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    def analyze_image(self, image_path: str):

        image = Image.open(image_path)

        prompt = """
                You are an expert field service engineer.

                Analyze the uploaded image and identify visible faults, risks, and required actions.

                Return ONLY valid JSON.

                {
                "equipment": "",
                "issue": "",
                "severity": "",
                "confidence": 0,
                "fault_detected": false,
                "root_cause": "",
                "recommended_action": "",
                "tools_required": [],
                "safety_warning": ""
                }

                Rules:

                - equipment: device or equipment name
                - issue: primary fault detected
                - severity: Low, Medium, High, or Critical
                - confidence: integer from 0 to 100
                - fault_detected: true if a visible fault/risk/problem exists, otherwise false
                - root_cause: likely reason for issue
                - recommended_action: short actionable fix
                - tools_required: array of tools needed
                - safety_warning: important safety precautions

                Special Rules:

                - If equipment appears normal with no visible issue, set:
                - fault_detected = false
                - severity = "Low"
                - recommended_action = "No visible corrective action required"
                - Only set fault_detected = true when a clear visible defect, damage, safety risk, missing component, corrosion, leak, overheating sign, broken part, or abnormal condition exists.

                Return JSON only.
                Do not include markdown.
                Do not include explanations.
                Do not include notes.
                Do not include any text before or after JSON.
            """
        try:
            response = self.client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=[prompt, image]
            )

        except Exception as e:
            print(f"Gemini Error: {e}")

            return {
                "equipment": "Unknown",
                "issue": "AI service temporarily unavailable",
                "severity": "Low",
                "confidence": 0,
                "fault_detected": False,
                "root_cause": "",
                "recommended_action": "Please retry analysis in a few moments",
                "tools_required": [],
                "safety_warning": ""
            }
         
        text = response.text.strip()

        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()

        try:
            data = json.loads(text)
            return {
                "equipment": data.get("equipment", "Unknown"),
                "issue": data.get("issue", "Unknown"),
                "severity": data.get("severity", "Low"),
                "confidence": data.get("confidence", 0),
                "fault_detected": data.get("fault_detected", False),
                "root_cause": data.get("root_cause", ""),
                "recommended_action": data.get("recommended_action", ""),
                "tools_required": data.get("tools_required", []),
                "safety_warning": data.get("safety_warning", "")
            }
        except Exception:
            return {
                "equipment": "Unknown",
                "issue": "Unable to determine",
                "severity": "Low",
                "confidence": 0,
                "fault_detected": False,
                "root_cause": "",
                "recommended_action": "",
                "tools_required": [],
                "safety_warning": "",
                "raw_response": text
            }