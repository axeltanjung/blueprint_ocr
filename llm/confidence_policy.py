from typing import Dict, Any, List


class ConfidenceDecision:
    AUTO_ACCEPT = "AUTO_ACCEPT"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    REJECT = "REJECT"


class ConfidencePolicy:
    def __init__(
        self,
        accept_threshold: float = 0.85,
        review_threshold: float = 0.6
    ):
        self.accept_threshold = accept_threshold
        self.review_threshold = review_threshold

    def decide_dimension(self, dim: Dict[str, Any]) -> str:
        confidence = dim.get("confidence", 0.0)

        if confidence >= self.accept_threshold:
            return ConfidenceDecision.AUTO_ACCEPT

        if confidence >= self.review_threshold:
            return ConfidenceDecision.REVIEW_REQUIRED

        return ConfidenceDecision.REJECT

    def apply(self, dimensions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Annotate each dimension with a decision.
        """
        for dim in dimensions:
            dim["decision"] = self.decide_dimension(dim)

        return dimensions
