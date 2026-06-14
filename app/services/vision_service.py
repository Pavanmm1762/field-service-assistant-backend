import asyncio
import logging

from app.services.ai.factory import get_ai_service

logger = logging.getLogger(__name__)


class VisionService:
    def analyze_image(self, image_path: str):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.analyze_image_async(image_path))
        raise RuntimeError("Use analyze_image_async() inside an async context.")

    async def analyze_image_async(self, image_path: str):
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
            response = await get_ai_service().analyze_image(
                image_path=image_path,
                prompt=prompt,
            )
            return response.model_dump(exclude_none=True)
        except Exception as exc:
            logger.exception("Image analysis failed: %s", exc)
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
