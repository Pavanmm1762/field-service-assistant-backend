import json
import re
from rapidfuzz import fuzz


class QuickResponseService:

    # Similarity threshold (0–100). Tune this value:
    # Higher = stricter (fewer false positives)
    # Lower  = looser  (catches more typos but risks wrong matches)
    FUZZY_THRESHOLD = 80

    # Only apply fuzzy matching to short messages (word count <= this)
    # Avoids fuzzy matching on long sentences where it's unreliable
    FUZZY_MAX_WORDS = 4

    def __init__(self):
        with open(
            "data/quick_responses.json",
            "r",
            encoding="utf-8"
        ) as file:
            self.responses = json.load(file)

    @staticmethod
    def _normalize(text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[^\w\s]", "", text)  # remove punctuation
        text = re.sub(r"\s+", " ", text)      # collapse spaces
        return text

    @staticmethod
    def _deduplicate_chars(text: str) -> str:
        """
        Collapse runs of 3+ repeated characters down to 2.
        'hiiiii' -> 'hii', 'heyyy' -> 'heyy'
        Keeps 'oo', 'ee' etc. intact (natural doubles).
        """
        return re.sub(r"(.)\1{2,}", r"\1\1", text)

    def _matches_exact_or_startswith(self, msg: str, keyword: str, mode: str) -> bool:
        kw = self._normalize(keyword)

        if mode == "exact":
            return msg == kw
        if mode == "startswith":
            return msg == kw or msg.startswith(kw + " ")
        if mode == "contains":
            return bool(re.search(rf"\b{re.escape(kw)}\b", msg))

        return False

    def _matches_fuzzy(self, msg: str, keyword: str, mode: str) -> bool:
        """
        Fuzzy fallback for short messages.
        Uses token_set_ratio to handle word-order and partial overlaps.
        """
        kw = self._normalize(keyword)
        word_count = len(msg.split())

        if word_count > self.FUZZY_MAX_WORDS:
            return False

        # Deduplicate chars before fuzzy comparison
        msg_deduped = self._deduplicate_chars(msg)
        kw_deduped = self._deduplicate_chars(kw)

        score = fuzz.token_set_ratio(msg_deduped, kw_deduped)
        return score >= self.FUZZY_THRESHOLD

    def get_response(self, message: str) -> str | None:
        msg = self._normalize(message)

        # --- Pass 1: Exact / startswith / contains (fast, no false positives) ---
        for intent in self.responses.values():
            mode = intent.get("match_mode", "exact")
            for keyword in intent["keywords"]:
                if self._matches_exact_or_startswith(msg, keyword, mode):
                    return intent["response"]

        # --- Pass 2: Fuzzy fallback (catches typos and char repetition) ---
        best_score = 0
        best_response = None

        for intent in self.responses.values():
            mode = intent.get("match_mode", "exact")
            for keyword in intent["keywords"]:
                if self._matches_fuzzy(msg, keyword, mode):
                    # Pick the highest-confidence fuzzy match
                    kw = self._deduplicate_chars(self._normalize(keyword))
                    msg_d = self._deduplicate_chars(msg)
                    score = fuzz.token_set_ratio(msg_d, kw)
                    if score > best_score:
                        best_score = score
                        best_response = intent["response"]

        return best_response  # None if nothing matched


quick_response_service = QuickResponseService()