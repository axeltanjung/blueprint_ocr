# Business Requirements Document (BRD)

## 1. Background & Problem Statement

Manufacturing blueprints (technical drawings) are commonly shared as PDFs or scanned images. These documents contain critical specifications such as dimensions, tolerances, materials, and notes that are essential for downstream processes (manufacturing, quality control, cost estimation).

However:

* Blueprints are **not machine-readable by default**
* OCR outputs are often **noisy, ambiguous, and unstructured**
* Manual interpretation is **time-consuming, error-prone, and does not scale**

There is a need for an automated system that can reliably convert blueprint images into **structured, validated, and machine-consumable specifications**.

---

## 2. Business Objective

To design and implement an automated workflow that:

* Converts blueprint PDFs/images into structured manufacturing specifications
* Reduces manual interpretation effort and turnaround time
* Improves data consistency and traceability
* Enables downstream automation (MES, ERP, costing, analytics)

Success will be measured by:

* Accuracy of extracted specifications
* Reduction in manual processing time
* Adoption by engineering/manufacturing teams

---

## 3. Scope

### In Scope

* Upload of blueprint documents (PDF, PNG, JPG)
* OCR extraction of text from drawings
* LLM-based interpretation and structuring of specifications
* JSON output with confidence scoring
* Workflow orchestration using n8n

### Out of Scope

* CAD-native file parsing (e.g., DWG, STEP)
* Automated validation against manufacturing standards
* Full CAD reconstruction

---

## 4. Stakeholders

| Role                       | Responsibility                 |
| -------------------------- | ------------------------------ |
| Manufacturing Engineer     | Validate extracted specs       |
| Data / Automation Engineer | Build & maintain workflow      |
| QA / QC Team               | Verify tolerances & dimensions |
| IT / Platform Team         | Infrastructure & security      |

---

## 5. High-Level Solution Overview

The solution is an **event-driven n8n workflow** integrating OCR and LLM services.

### Workflow Overview

1. User uploads blueprint via webhook
2. OCR engine extracts raw text
3. LLM interprets OCR output into structured specs
4. System returns validated JSON + confidence score

---

## 6. Functional Requirements

### FR-01: Blueprint Upload

* System shall accept PDF and image formats
* Maximum file size configurable (default: 10 MB)

### FR-02: OCR Processing

* System shall extract text using OCR (Tesseract or Vision API)
* OCR output shall preserve positional hints if available

### FR-03: Specification Extraction via LLM

* System shall extract:

  * Dimensions (length, width, diameter, etc.)
  * Tolerances
  * Material specifications
  * Units of measurement
  * Notes / special instructions

### FR-04: Structured Output

* Output shall conform to a predefined JSON schema
* Each extracted field shall include a confidence score (0–1)

### FR-05: Error Handling & Fallback

* System shall flag low-confidence or ambiguous fields
* System shall return partial results if full extraction fails

---

## 7. Non-Functional Requirements

| Category       | Requirement                                      |
| -------------- | ------------------------------------------------ |
| Performance    | < 30 seconds per blueprint                       |
| Scalability    | Support batch uploads via n8n                    |
| Reliability    | Retry mechanism for OCR/LLM failures             |
| Security       | No persistent storage of files unless configured |
| Explainability | LLM output must reference OCR text snippets      |

---

## 8. JSON Output Schema (High-Level)

```json
{
  "metadata": {
    "file_name": "string",
    "processed_at": "ISO-8601 timestamp"
  },
  "specifications": {
    "dimensions": [
      {
        "type": "length | diameter | width",
        "value": "number",
        "unit": "mm | inch",
        "tolerance": "string",
        "confidence": 0.0
      }
    ],
    "material": {
      "name": "string",
      "standard": "string",
      "confidence": 0.0
    },
    "notes": [
      {
        "text": "string",
        "confidence": 0.0
      }
    ]
  }
}
```

---

## 9. Assumptions & Constraints

### Assumptions

* Blueprints follow common manufacturing drawing conventions
* OCR quality is sufficient for LLM interpretation

### Constraints

* OCR errors may propagate to LLM interpretation
* Highly stylized or handwritten drawings may reduce accuracy

---

## 10. Risks & Mitigations

| Risk                    | Impact           | Mitigation                                 |
| ----------------------- | ---------------- | ------------------------------------------ |
| OCR noise               | Wrong extraction | OCR pre-cleaning + confidence scoring      |
| LLM hallucination       | Incorrect specs  | Strict JSON schema + grounding to OCR text |
| Variability in drawings | Low accuracy     | Iterative prompt tuning                    |

---

## 11. Deliverables

1. n8n workflow export (JSON)
2. OCR + LLM prompt templates
3. JSON schema definition
4. Sample blueprint with extracted output
5. Technical documentation

---

## 12. Acceptance Criteria

* ≥85% accuracy on key dimensions across test blueprints
* Structured JSON output validated against schema
* End-to-end processing time < 30 seconds
* Successful processing of at least 10 sample blueprints

---

## 13. Future Enhancements

* CAD file parsing integration
* Rule-based validation against ISO/ASME standards
* Human-in-the-loop review UI
* Integration with MES / ERP systems
