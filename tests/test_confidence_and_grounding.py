from llm.confidence_scoring import ConfidenceScorer
from llm.grounding import GroundingEngine


def test_confidence_penalized_when_grounding_fails():
    ocr_text = "DIAMETER 1Omm"

    dim = {
        "type": "diameter",
        "value": 10,
        "unit": "mm",
        "source_text": "DIAMETER 10mm",
        "confidence": 0.8
    }

    scorer = ConfidenceScorer()
    engine = GroundingEngine(similarity_threshold=0.9)

    dim["confidence"] = scorer.score_dimension(dim, ocr_text)

    grounded = engine.ground_dimensions([dim], ocr_text)[0]

    assert grounded["grounding"]["matched"] is False
    assert grounded["confidence"] < 0.8
