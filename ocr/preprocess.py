import re
from typing import List

class OCRPreprocessor:
    """
    Preprocess raw OCR text from manufacturing blueprints
    to reduce noise BEFORE LLM interpretation.
    """

    def __init__(self):
        # common OCR confusions in technical drawings
        self.char_normalization = {
            "Ø": "DIAMETER",
            "ø": "DIAMETER",
            "φ": "DIAMETER",
            "±": "+/-",
            "–": "-",
            "—": "-",
        }

    def normalize_characters(self, text: str) -> str:
        for k, v in self.char_normalization.items():
            text = text.replace(k, f" {v} ")
        return text

    def remove_non_informative_lines(self, lines):
        filtered = []
        for line in lines:
            stripped = line.strip()

            if len(stripped) < 3:
                continue

            # remove drawing index / grid refs like A-12
            if re.fullmatch(r"[A-Z]\s*-\s*\d+", stripped):
                continue

            filtered.append(stripped)
        return filtered

    def fix_common_numeric_noise(self, text: str) -> str:
        """
        Fix OCR numeric patterns without guessing values
        """
        # Example: O instead of 0 in numbers
        text = re.sub(r"(?<=\d)O(?=\d)", "0", text)

        # Remove spaces between number and unit: 10 mm -> 10mm
        text = re.sub(r"(\d)\s+(mm|cm|inch)", r"\1\2", text, flags=re.IGNORECASE)

        return text

    def preprocess(self, raw_ocr_text: str) -> str:
        text = raw_ocr_text

        text = self.normalize_characters(text)
        text = self.fix_common_numeric_noise(text)

        lines = text.splitlines()
        lines = self.remove_non_informative_lines(lines)

        # Normalize excessive whitespace
        cleaned_lines = []
        for line in lines:
            line = re.sub(r"\s+", " ", line)  # collapse multiple spaces
            cleaned_lines.append(line.strip())

        return "\n".join(cleaned_lines)

    def fix_common_numeric_noise(self, text: str) -> str:
        # Case 1: O between digits (1O2 -> 102)
        text = re.sub(r"(?<=\d)O(?=\d)", "0", text)

        # Case 2: digit + O + space/unit (1O mm -> 10mm)
        text = re.sub(
            r"(?<=\d)O(?=\s*(mm|cm|inch))",
            "0",
            text,
            flags=re.IGNORECASE
        )

        # Case 3: O at start of decimal (O.2 -> 0.2)
        text = re.sub(r"\bO\.(\d+)", r"0.\1", text)

        # Normalize spacing: 10 mm -> 10mm
        text = re.sub(
            r"(\d)\s+(mm|cm|inch)",
            r"\1\2",
            text,
            flags=re.IGNORECASE
        )

        return text

