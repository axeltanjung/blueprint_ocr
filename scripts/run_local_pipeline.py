import sys
from pathlib import Path
import json

from ocr.preprocess import OCRPreprocessor
from llm.confidence_scoring import ConfidenceScorer
from llm.grounding import GroundingEngine
from llm.postprocessor import PostProcessor

def main(ocr_text_path):
    ocr_text = Path(ocr_text_path).read_text()

    # 1. OCR preprocess
    clean_text = OCRPreprocessor().preprocess(ocr_text)

    # 2. MOCK LLM output (sementara)
    extracted = {
        "metadata": {},
        "specifications": {
            "dimensions": [
                {
                    "type": "diameter",
                    "value": 10,
                    "unit": "mm",
                    "tolerance": "+/- 0.2",
                    "source_text": "DIAMETER 10mm +/- 0.2",
                    "confidence": 0.0
                }
            ],
            "material": None,
            "notes": []
        }
    }

    # 3. Confidence scoring
    scorer = ConfidenceScorer()
    for d in extracted["specifications"]["dimensions"]:
        d["confidence"] = scorer.score_dimension(d, clean_text)

    # 4. Grounding
    grounded = GroundingEngine().ground_dimensions(
        extracted["specifications"]["dimensions"],
        clean_text
    )
    extracted["specifications"]["dimensions"] = grounded

    # 5. Post-processing
    final = PostProcessor().process(extracted)

    print(json.dumps(final, indent=2))

if __name__ == "__main__":
    main(sys.argv[1])
