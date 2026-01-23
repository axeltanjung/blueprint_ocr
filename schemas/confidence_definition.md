# Confidence Score Definition

Confidence score (0–1) represents the system’s confidence that an extracted field
accurately reflects the blueprint content.

## Confidence is derived from:
1. OCR clarity (numeric symbols, unit consistency)
2. Redundancy (value appears multiple times)
3. Explicit tolerance notation (±, ISO fit, etc.)
4. LLM certainty based on grounded OCR text

## Interpretation Guide
- 0.85 – 1.00 : High confidence, safe for downstream automation
- 0.60 – 0.84 : Medium confidence, human review recommended
- < 0.60 : Low confidence, do not auto-consume

## Important
Confidence score is **not** a probability of correctness.
It is a heuristic ranking to support decision-making.
