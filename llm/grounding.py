from typing import List, Dict
import difflib
import re

class GroundingEngine:
    """
    Links extracted fields to OCR text lines for traceability.
    """

    def __init__(self, similarity_threshold: float = 0.6):
        self.similarity_threshold = similarity_threshold

    def _best_match(self, source_text: str, ocr_lines: List[str]) -> Dict:
        """
        Find best matching OCR line for given source_text.
        """
        best_score = 0.0
        best_line = None
        best_index = None

        for idx, line in enumerate(ocr_lines):
            score = difflib.SequenceMatcher(
                None, source_text.lower(), line.lower()
            ).ratio()

            if score > best_score:
                best_score = score
                best_line = line
                best_index = idx

        return {
            "matched": best_score >= self.similarity_threshold,
            "ocr_line": best_line,
            "line_index": best_index,
            "similarity": round(best_score, 2)
        }

    def ground_dimensions(self, dimensions: List[Dict], ocr_text: str) -> List[Dict]:
        ocr_lines = ocr_text.splitlines()

        for dim in dimensions:
            source = dim.get("source_text", "")
            result = self._best_match(source, ocr_lines)

            dim["grounding"] = result

            # penalize confidence if grounding weak
            if not result["matched"]:
                dim["confidence"] = round(dim["confidence"] * 0.7, 2)

        return dimensions
    
    def ground_dimensions(self, dimensions, ocr_text):
        ocr_lines = ocr_text.splitlines()

        for dim in dimensions:
            source = dim.get("source_text", "")
            result = self._best_match(source, ocr_lines)

            ambiguous = self._has_ocr_numeric_ambiguity(
                result["ocr_line"] or ""
            )

            # treat ambiguous numeric match as weak grounding
            if ambiguous:
                result["matched"] = False

            dim["grounding"] = result

            if not result["matched"]:
                dim["confidence"] = round(dim["confidence"] * 0.7, 2)

        return dimensions


    def _has_ocr_numeric_ambiguity(self, text: str) -> bool:
        return bool(re.search(r"\dO|O\d", text))
