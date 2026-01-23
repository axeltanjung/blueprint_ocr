import sys
import json
from pathlib import Path

from ocr.preprocess import OCRPreprocessor
from llm.llm_client_openrouter import OpenRouterClient
from llm.llm_adapter import adapt_openrouter_output
from llm.confidence_scoring import ConfidenceScorer
from llm.grounding import GroundingEngine
from llm.postprocessor import PostProcessor


def load_prompt(path: str) -> str:
    return Path(path).read_text()


def main(ocr_text_path: str):
    # 1. Load OCR text
    ocr_text = Path(ocr_text_path).read_text()

    # 2. OCR preprocessing
    clean_text = OCRPreprocessor().preprocess(ocr_text)

    # 3. Load prompts
    system_prompt = load_prompt("prompts/system_prompt.md")
    extraction_prompt = load_prompt("prompts/extraction_prompt.md")

    user_prompt = extraction_prompt.replace(
        "{{OCR_TEXT}}", clean_text
    )

    # 4. LLM extraction (OpenRouter)
    client = OpenRouterClient()
    raw_llm_output = client.extract(
        system_prompt=system_prompt,
        user_prompt=user_prompt
    )

    # 5. Adapt to internal schema
    extracted = adapt_openrouter_output(raw_llm_output)

    # 6. Confidence scoring
    scorer = ConfidenceScorer()
    for dim in extracted["specifications"]["dimensions"]:
        dim["confidence"] = scorer.score_dimension(dim, clean_text)

    # 7. Grounding
    grounded_dims = GroundingEngine().ground_dimensions(
        extracted["specifications"]["dimensions"],
        clean_text
    )
    extracted["specifications"]["dimensions"] = grounded_dims

    # 8. Post-processing
    final = PostProcessor().process(extracted)

    print(json.dumps(final, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise RuntimeError(
            "Usage: python -m scripts.run_local_pipeline <ocr_text_path>"
        )

    main(sys.argv[1])
