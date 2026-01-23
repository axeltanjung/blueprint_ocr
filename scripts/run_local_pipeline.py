import sys
import json
from pathlib import Path

from ocr.preprocess import OCRPreprocessor
from llm.llm_client_openrouter import OpenRouterClient
from llm.llm_adapter import adapt_openrouter_output
from llm.confidence_scoring import ConfidenceScorer
from llm.grounding import GroundingEngine
from llm.postprocessor import PostProcessor
from schemas.schema_validator import validate_against_schema, SchemaValidationError
from datetime import datetime, timezone
datetime.now(timezone.utc).isoformat()
from llm.confidence_policy import ConfidencePolicy

def aggregate_document_decision(dimensions):
    if any(d["decision"] == "REJECT" for d in dimensions):
        return "REJECTED"

    if any(d["decision"] == "REVIEW_REQUIRED" for d in dimensions):
        return "REVIEW_REQUIRED"

    return "AUTO_ACCEPTED"

def load_prompt(path: str) -> str:
    return Path(path).read_text()

def load_schema(path: str):
    return json.loads(Path(path).read_text())

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

    # 5.1 Enrich metadata (PIPELINE responsibility)
    extracted["metadata"]["file_name"] = Path(ocr_text_path).name
    extracted["metadata"]["processed_at"] = datetime.utcnow().isoformat()

    # 6. HARD SCHEMA VALIDATION
    schema = load_schema("schemas/output_schema_v1.json")

    try:
        validate_against_schema(extracted, schema)
    except SchemaValidationError as e:
        raise RuntimeError(
            f"Pipeline stopped due to schema violation.\n{str(e)}\n"
            f"Raw LLM output:\n{json.dumps(raw_llm_output, indent=2)}"
        )

    if not extracted["specifications"]["dimensions"]:
        raise RuntimeError(
            "No valid dimensions extracted after schema validation."
        )


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

    # 7. Grounding  
    grounded_dims = GroundingEngine().ground_dimensions(
        extracted["specifications"]["dimensions"],
        clean_text
    )
    extracted["specifications"]["dimensions"] = grounded_dims

    # 8. Confidence decision policy
    policy = ConfidencePolicy()
    decided_dims = policy.apply(
        extracted["specifications"]["dimensions"]
    )
    extracted["specifications"]["dimensions"] = decided_dims

    # 8. Post-processing
    final = PostProcessor().process(extracted)

    print(json.dumps(final, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise RuntimeError(
            "Usage: python -m scripts.run_local_pipeline <ocr_text_path>"
        )

    main(sys.argv[1])
