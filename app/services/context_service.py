# app/services/context_service.py

class ContextService:

    def __init__(self):
        self.latest_analysis = None

    def set_analysis(self, analysis):
        self.latest_analysis = analysis

    def get_analysis(self):
        return self.latest_analysis


context_service = ContextService()