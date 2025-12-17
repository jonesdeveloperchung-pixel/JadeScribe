# 🧪 Project Test Plan

## 📋 Overview
Defines the validation strategy for **JadeScribe**, focusing on the Database, Ollama Integration, and UI/UX workflows.

---

## 🎯 Test Objectives
- Validate SQLite schema integrity and CRUD operations.
- Confirm Ollama (Vision & Text) connectivity and fallback handling.
- Ensure the Streamlit UI provides immediate feedback and handles errors gracefully.
- Verify Traditional Chinese localization across all outputs.

---

## 🧩 Module Test Coverage

### Module: Database (SQLite)
- **Purpose:** Persistent storage for items, images, and telemetry.
- **Design Reference:** `docs/Design_Specification.md` > Section 12.1
- **Test Owner:** Jones (Gemini Agent)

#### ✅ Test Cases
| Test ID | Description | Input | Expected Output | Status | Notes |
|--------|-------------|-------|------------------|--------|-------|
| DB001  | Schema Initialization | `schema.sql` | Tables `items`, `images`, `telemetry` exist | Pass | Verified via src/verify_db.py |
| DB002  | Telemetry Insert | Sample JSON Log | Record added to `telemetry` table | Pending | |
| DB003  | Item Deduplication | Duplicate `item_code` insert | Constraint violation error | Pending | |

### Module: AI Integration (Ollama)
- **Purpose:** Visual analysis and descriptive text generation.
- **Design Reference:** `src/utils.py`
- **Test Owner:** Jones (Gemini Agent)

#### ✅ Test Cases
| Test ID | Description | Input | Expected Output | Status | Notes |
|--------|-------------|-------|------------------|--------|-------|
| AI001  | Service Status Check | `check_ollama_status()` | Returns `running: True` or clear error | Pending | |
| AI002  | Vision Model Load | Load `llama3.2-vision` | Model loaded success | Pending | |
| AI003  | Offline Fallback | Stop Ollama -> Run App | UI shows "Start Ollama" guide | Pending | |

---

## 🔗 Integration Tests

### Scenario: End-to-End Image Processing
- **Modules Involved:** UI, Database, Ollama Vision, Ollama Text
- **Test Steps:**
  1. Upload `IMG_6070.jpeg` via UI.
  2. System detects `PA-0425_AF`.
  3. System generates "Guanyin" description in Traditional Chinese.
  4. Data saved to `jade_inventory.db`.
- **Expected Outcome:** New row in `items` table, description displayed in UI.
- **Status:** Pending
- **Notes:**

---

## 🗃️ Database Validation

### SQLite Configuration
- [ ] Schema initialized correctly
- [ ] CRUD operations verified
- [ ] Invalid query handling tested

---

## 🧼 Edge Case & Error Handling

| Case ID | Description | Trigger | Expected Behavior | Status | Notes |
|---------|-------------|---------|-------------------|--------|-------|
| EC001   | Unreadable Label | Image with blurry text | Log "OCR Failed", ask user for manual input | Pending | |
| EC002   | Non-Jade Image | Upload random photo | Log "No Jade Detected", warn user | Pending | |

---

## 📈 Test Summary & Reporting
- **Test Lead:** Jones
- **Reporting Frequency:** After each major feature implementation
- **Tools Used:** `pytest`, `sqlite3` CLI
- **Known Issues:** None yet
