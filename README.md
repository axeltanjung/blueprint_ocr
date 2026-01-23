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

## ✨ Key Capabilities

* **OCR hygiene**: Deterministic preprocessing to reduce noise (no guessing).
* **Schema-bound LLM extraction**: Strict JSON output with source grounding.
* **Deterministic confidence scoring**: Explainable heuristics (not LLM vibes).
* **Grounding & traceability**: Every field links back to OCR text.
* **Post-processing safety**: Deduplication, normalization, and hard validation.
* **Orchestration-ready**: n8n workflow for production-style execution.

---

## 🧱 Architecture (Conceptual)

```
Image/PDF
  ↓
OCR Engine (Tesseract / Vision API)
  ↓
OCR Preprocess (deterministic)
  ↓
LLM Extraction (schema-bound)
  ↓
Confidence Scoring (heuristic)
  ↓
Grounding (OCR traceability)
  ↓
Post-Processing (dedup, normalize)
  ↓
Schema Validation (hard gate)
  ↓
Final JSON
```

Design principles:

* Separation of concerns
* Fail-safe defaults
* Explainability > raw speed

---

## 📁 Repository Structure

```
blueprint-ocr-structured-spec/
├── docs/                     # BRD, architecture notes
├── schemas/                  # Output contract (JSON Schema)
├── prompts/                  # LLM prompts (system + extraction)
├── ocr/                      # OCR preprocessing
├── llm/                      # Extraction, confidence, grounding, postprocess
├── workflows/n8n/            # n8n workflow export (JSON)
├── tests/                    # Minimal but meaningful tests
└── scripts/                  # Local runners & evaluation helpers
```

---

## 🚀 Quick Start (Local, No n8n)

> Use this path to understand the logic end-to-end without orchestration.

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Prepare sample OCR text

Place a text file in:

```
data/ocr_output/sample.txt
```

### 3) Run local pipeline

```bash
python scripts/run_local_pipeline.py data/ocr_output/sample.txt
```

Output will be written to:

```
data/structured_output/
```

---

## 🔁 Run with n8n (Recommended)

### Import workflow

1. Open n8n UI
2. Import workflow:

```
workflows/n8n/blueprint_ocr_main.json
```

### Trigger

* `POST /webhook/blueprint-upload`
* Form-data:

  * `file`: PDF/PNG/JPG
  * `file_name`: string

### Response

* Validated JSON conforming to `schemas/output_schema_v1.json`

---

## 🧪 Testing

Run all tests:

```bash
pytest tests/
```

What we test (intentionally minimal):

* OCR noise handling (numeric & symbol stability)
* Schema validity (contract enforcement)
* Confidence degradation when grounding fails

---

## Design Decisions & Trade-offs

### Why deterministic confidence scoring (not ML)
Confidence scores are computed using **rule-based heuristics** instead of a learned model.  
This makes the system:
- Explainable to engineers and QA
- Stable across OCR / LLM changes
- Safe for downstream automation decisions

ML-based confidence estimation can be added later once labeled data exists.

---

### Why grounding before post-processing
Grounding is applied **before** deduplication and normalization so that:
- Confidence penalties reflect original OCR evidence
- Post-processing does not hide weak or ambiguous extractions

This preserves traceability and auditability.

---

### Why n8n for orchestration
n8n is used as an orchestration layer to:
- Separate execution flow from business logic
- Enable retries, fallbacks, and human-in-the-loop extensions
- Provide a visual workflow for non-technical stakeholders

Core logic remains framework-agnostic and fully testable in pure Python.


## 📊 Confidence Score Semantics

* **0.85–1.00**: High confidence → safe for automation
* **0.60–0.84**: Medium → human review recommended
* **< 0.60**: Low → do not auto-consume

> Confidence is a **heuristic ranking**, not a probability.

---

## ⚠️ Known Limitations

* Not a CAD parser (DWG/STEP out of scope)
* Handwritten drawings reduce OCR quality
* No standards validation (ISO/ASME) in current scope

---

## 1. High-Level Architecture Diagram

```
┌──────────────┐
│   Blueprint  │
│  PDF / Image │
└──────┬───────┘
       │ Upload (Webhook)
       ▼
┌──────────────┐
│     n8n      │  ← Orchestration Layer
│  (Workflow)  │
└──────┬───────┘
       │
       ▼
┌───────────────────────────┐
│        OCR Engine         │
│  (Tesseract / Vision API) │
└──────────┬────────────────┘
           │ raw OCR text
           ▼
┌───────────────────────────┐
│     OCR Preprocessing     │
│  (Deterministic Cleaning) │
└──────────┬────────────────┘
           │ clean OCR text
           ▼
┌───────────────────────────┐
│     LLM Extraction        │
│ (Schema-bound, grounded) │
└──────────┬────────────────┘
           │ structured JSON
           ▼
┌───────────────────────────┐
│   Confidence Scoring      │
│ (Heuristic, deterministic)│
└──────────┬────────────────┘
           │ scored JSON
           ▼
┌───────────────────────────┐
│       Grounding Engine    │
│ (OCR traceability)        │
└──────────┬────────────────┘
           │ grounded JSON
           ▼
┌───────────────────────────┐
│      Post-Processing      │
│ (Dedup & normalization)   │
└──────────┬────────────────┘
           │ final candidate
           ▼
┌───────────────────────────┐
│     Schema Validation     │
│   (Hard contract gate)    │
└──────────┬────────────────┘
           │ valid JSON
           ▼
┌───────────────────────────┐
│ Response / Persistence    │
│ (Webhook / DB / File)     │
└───────────────────────────┘
```

---

## 2. Architectural Layers & Responsibilities

### 2.1 Orchestration Layer (n8n)

**Responsibility:**

* Event handling (upload, trigger)
* Branching & fallback logic
* Retry & error routing

**Key principle:**

> n8n coordinates *when* things happen, not *how* they are interpreted.

---

### 2.2 OCR Layer

**Components:**

* Tesseract (primary)
* Vision API (fallback)

**Responsibilities:**

* Convert image/PDF to raw text
* Preserve maximum textual signal

**Explicitly NOT responsible for:**

* Semantic interpretation
* Unit inference

---

### 2.3 OCR Preprocessing Layer

**Purpose:** Reduce OCR noise without altering meaning.

Examples:

* Normalize symbols (Ø → DIAMETER)
* Fix numeric confusions (O → 0)
* Remove non-informative lines

**Design choice:** Deterministic, rule-based, testable.

---

### 2.4 LLM Extraction Layer

**Purpose:** Semantic interpretation of blueprint text.

**Key constraints:**

* Strict JSON schema enforcement
* Mandatory `source_text` grounding
* No assumptions or hallucinations

**Why LLM here:**
Blueprints vary widely; rules alone do not scale.

---

### 2.5 Confidence Scoring Layer

**Purpose:** Decide *how safe* the extracted data is for automation.

**Inputs:**

* OCR clarity
* Unit explicitness
* Redundancy
* Tolerance notation

**Important:**

> Confidence is a heuristic ranking, not a probability.

---

### 2.6 Grounding Layer

**Purpose:** Traceability and explainability.

Each extracted field is linked to:

* OCR line
* Line index
* Similarity score

**Effect:**

* Enables auditing
* Penalizes ungrounded extraction

---

### 2.7 Post-Processing Layer

**Purpose:** Final safety enforcement.

Responsibilities:

* Deduplicate equivalent dimensions
* Normalize units
* Cap confidence scores

**Design rule:**

> No new information is introduced at this stage.

---

### 2.8 Validation & Output Layer

**Purpose:** Contract enforcement.

* JSON Schema validation
* Hard failure on invalid output

**Guarantee:**
Downstream systems only receive schema-valid data.

---

## 3. Key Design Decisions & Trade-offs

### Decision: LLM after OCR preprocessing

* ✅ Reduces hallucination
* ❌ Slightly more latency

### Decision: Deterministic confidence scoring

* ✅ Explainable & auditable
* ❌ Less flexible than ML-based scoring

### Decision: Hard schema validation

* ✅ Strong downstream guarantees
* ❌ Partial outputs may be rejected

---

## 4. Failure Modes & Safeguards

| Failure           | Mitigation                     |
| ----------------- | ------------------------------ |
| OCR noise         | Preprocessing + fallback OCR   |
| LLM hallucination | Grounding + schema enforcement |
| Ambiguous specs   | Confidence penalty + flagging  |
| Pipeline error    | n8n retries & branching        |

---

## 5. Why This Architecture Works

This system prioritizes:

* Explainability over black-box automation
* Contract-first design over ad-hoc parsing
* Incremental extensibility (HITL, CAD, standards)

It is suitable for:

* Internal manufacturing tools
* Data ingestion pipelines
* Engineering analytics foundations

---

## 6. Extension Points

* Human-in-the-loop review UI
* CAD-native parsers
* Standards validation (ISO / ASME)
* Batch & queue-based processing

---

## 7. Summary

This architecture demonstrates a **production-minded approach** to combining OCR and LLMs:

* LLMs are powerful but constrained
* Deterministic layers provide safety
* Orchestration enables scalability

Together, they form a robust and defensible system for blueprint digitization.
