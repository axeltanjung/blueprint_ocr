import re
from typing import Dict


class ConfidenceScorer:
    """
    Deterministic confidence scoring for extracted blueprint fields.
    """

    def score_dimension(self, item: Dict, full_ocr_text: str) -> float:
        score = 0.0

        value = str(item.get("value", ""))
        unit = item.get("unit", "")
        source = item.get("source_text", "")

        # 1. Numeric clarity
        if re.fullmatch(r"\d+(\.\d+)?", value):
            score += 0.30
        else:
            score += 0.10  # partially readable

        # 2. Explicit unit
        if unit:
            score += 0.20

        # 3. Redundancy in OCR
        occurrences = full_ocr_text.count(source)
        if occurrences >= 2:
            score += 0.20
        elif occurrences == 1:
            score += 0.10

        # 4. Tolerance explicitly stated
        if re.search(r"\+/-|±|H\d+|f\d+", source):
            score += 0.20

        # 5. OCR noise penalty
        if re.search(r"[OIl]", source):
            score -= 0.10

        return round(min(max(score, 0.0), 1.0), 2)

    def score_material(self, item: Dict) -> float:
        score = 0.0
        source = item.get("source_text", "")

        if re.search(r"SS\d+|ASTM|AISI|ISO", source):
            score += 0.50

        if len(source) > 5:
            score += 0.20

        if re.search(r"[OIl]", source):
            score -= 0.10

        return round(min(max(score, 0.0), 1.0), 2)
