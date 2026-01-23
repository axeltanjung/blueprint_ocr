def adapt_openrouter_output(llm_output: dict) -> dict:
    """
    Normalize OpenRouter / open-source model output
    into internal schema expected by the pipeline.
    """

    dimensions = []

    for dim in llm_output.get("dimensions", []):
        dimensions.append({
            "type": "unknown",
            "value": dim.get("value"),
            "unit": dim.get("unit"),
            "tolerance": None,
            "source_text": dim.get("source_text", ""),
            "confidence": 0.0
        })

    material = None
    if "material" in llm_output:
        material = {
            "name": llm_output["material"].get("name"),
            "standard": llm_output["material"].get("standard")
        }

    return {
        "metadata": {
            "llm_backend": "openrouter",
            "model_output_raw": True
        },
        "specifications": {
            "dimensions": dimensions,
            "material": material,
            "notes": llm_output.get("manufacturing_notes", [])
        }
    }
