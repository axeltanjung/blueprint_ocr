import json
from jsonschema import validate
from pathlib import Path


def test_output_schema_valid():
    schema = json.loads(
        Path("schemas/output_schema_v1.json").read_text()
    )

    valid_output = {
        "metadata": {
            "file_name": "sample.png",
            "processed_at": "2025-01-01T00:00:00Z"
        },
        "specifications": {
            "dimensions": [
                {
                    "type": "diameter",
                    "value": 10,
                    "unit": "mm",
                    "tolerance": "+/- 0.2",
                    "source_text": "DIAMETER 10mm +/- 0.2",
                    "confidence": 0.9
                }
            ],
            "material": None,
            "notes": []
        }
    }

    validate(instance=valid_output, schema=schema)
