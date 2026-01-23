from typing import Dict, List, Tuple


class PostProcessor:
    """
    Final cleanup and consistency enforcement
    before structured output is returned.
    """

    UNIT_MAP = {
        "millimeter": "mm",
        "millimeters": "mm",
        "mm": "mm",
        "cm": "cm",
        "inch": "inch",
        "in": "inch"
    }

    def normalize_unit(self, unit: str) -> str:
        if not unit:
            return unit
        return self.UNIT_MAP.get(unit.lower(), unit)

    def cap_confidence(self, confidence: float) -> float:
        return round(min(max(confidence, 0.0), 1.0), 2)

    def deduplicate_dimensions(self, dimensions: List[Dict]) -> List[Dict]:
        seen: Dict[Tuple, Dict] = {}

        for dim in dimensions:
            key = (
                dim.get("type"),
                dim.get("value"),
                self.normalize_unit(dim.get("unit"))
            )

            if key not in seen:
                seen[key] = dim
            else:
                # keep the one with higher confidence
                if dim.get("confidence", 0) > seen[key].get("confidence", 0):
                    seen[key] = dim

        return list(seen.values())

    def process_dimensions(self, dimensions: List[Dict]) -> List[Dict]:
        processed = []

        for dim in dimensions:
            dim["unit"] = self.normalize_unit(dim.get("unit"))
            dim["confidence"] = self.cap_confidence(dim.get("confidence", 0))

            processed.append(dim)

        return self.deduplicate_dimensions(processed)

    def process_material(self, material: Dict) -> Dict:
        if not material:
            return material

        material["confidence"] = self.cap_confidence(
            material.get("confidence", 0)
        )

        return material

    def process(self, output_json: Dict) -> Dict:
        specs = output_json.get("specifications", {})

        specs["dimensions"] = self.process_dimensions(
            specs.get("dimensions", [])
        )

        specs["material"] = self.process_material(
            specs.get("material")
        )

        output_json["specifications"] = specs
        return output_json
