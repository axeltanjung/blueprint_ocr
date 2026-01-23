Given the OCR text from a manufacturing blueprint:

Tasks:
1. Extract all explicit dimensions with units.
2. Extract tolerances if specified.
3. Extract material name and standard if present.
4. Extract relevant manufacturing notes.

Constraints:
- Do not normalize units unless explicitly written.
- Do not guess missing tolerances.
- Each extracted item must include:
  - value
  - unit
  - source_text
  - confidence score (0–1)

OCR Text:
{{OCR_TEXT}}

Return output strictly as JSON following the provided schema.

IMPORTANT:
- Output MUST be raw JSON only
- Do NOT use markdown or code fences
- Do NOT add explanations
