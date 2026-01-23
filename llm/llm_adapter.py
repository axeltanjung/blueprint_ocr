from typing import Optional, Dict, Any, List


# ----------------------------
# Text normalization utilities
# ----------------------------

def normalize_text(text: str) -> str:
    """
    Normalize common OCR / encoding artifacts before any semantic logic.
    This is CRITICAL for deterministic inference.
    """
    if not text:
        return ""

    replacements = {
        "Ã˜": "Ø",
        "Ã¸": "ø",
        "Ø": "Ø",
        "ø": "ø",
        "±": "+/-",
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    return text.strip()


# ----------------------------
# Dimension type inference
# ----------------------------

def infer_dimension_type(source_text: str) -> Optional[str]:
    """
    Infer dimension type strictly.
    Returns None if cannot be inferred safely.
    """
    text = normalize_text(source_text).lower()

    if "ø" in text or "diameter" in text:
        return "diameter"
    if "radius" in text or text.startswith("r "):
        return "radius"
    if "length" in text or text.startswith("l "):
        return "length"
    if "width" in text or text.startswith("w "):
        return "width"
    if "height" in text or text.startswith("h "):
        return "height"

    return None


# ----------------------------
# Adapter (LLM → Internal Schema)
# ----------------------------

def adapt_openrouter_output(llm_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adapt OpenRouter / open-source LLM output into internal schema.

    DESIGN PRINCIPLES:
    - Never guess enum values
    - Drop unsafe dimensions
    - LLM does NOT own metadata
    - Schema hard gate comes AFTER this step
    """

    dimensions: List[Dict[str, Any]] = []

    for dim in llm_output.get("dimensions", []):
        raw_source = dim.get("source_text", "")
        source_text = normalize_text(raw_source)

        inferred_type = infer_dimension_type(source_text)

        # HARD SAFETY RULE:
        # If enum cannot be inferred → DROP dimension
        if inferred_type is None:
            continue

        dimensions.append({
            "type": inferred_type,
            "value": dim.get("value"),
            "unit": dim.get("unit"),
            "tolerance": None,          # tolerance handled later / separately
            "source_text": source_text,
            "confidence": 0.0           # computed later by ConfidenceScorer
        })

    material = None
    if isinstance(llm_output.get("material"), dict):
        material = {
            "name": llm_output["material"].get("name"),
            "standard": llm_output["material"].get("standard")
        }

    return {
        "metadata": {
            # REQUIRED fields injected later by pipeline
            "llm_backend": "openrouter",
            "model_output_raw": True
        },
        "specifications": {
            "dimensions": dimensions,
            "material": material,
            "notes": llm_output.get("manufacturing_notes", [])
        }
    }
