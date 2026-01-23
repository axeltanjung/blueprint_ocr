import json
from datetime import datetime

def build_payload(ocr_text: str, schema: dict, system_prompt: str, extraction_prompt: str):
    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": extraction_prompt.replace("{{OCR_TEXT}}", ocr_text)
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": schema
        }
    }


def postprocess_output(raw_output: dict, file_name: str):
    raw_output["metadata"] = {
        "file_name": file_name,
        "processed_at": datetime.utcnow().isoformat()
    }
    return raw_output
