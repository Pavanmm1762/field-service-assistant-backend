class ContextService:

    def __init__(self):
        self.analysis = None
        self.session_id = None

    def set_analysis(self, analysis):
        self.analysis = analysis

    def get_analysis(self):
        return self.analysis

    def set_session_id(self, session_id):
        self.session_id = session_id

    def get_session_id(self):
        return self.session_id

    def clear(self):
        self.analysis = None
        self.session_id = None

context_service = ContextService()