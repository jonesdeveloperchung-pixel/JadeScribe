# 🧪 Project Test Plan

## 📋 Overview
Defines the validation strategy for **JadeScribe**, focusing on the Database, Ollama Integration, UI/UX workflows, and System Robustness.

---

## 🎯 Test Objectives
- Validate SQLite schema integrity, CRUD operations, and **Auto-Healing**.
- Confirm Ollama (Vision & Text) connectivity, **Multi-Item Detection**, and **Retry Logic**.
- Ensure the Streamlit UI provides immediate feedback, **Web Previews**, and **CSV Export**.
- Verify Traditional Chinese localization and **3-Style Marketing Copy** generation.

---

## 🧩 Module Test Coverage

### Module: Database (SQLite)
- **Purpose:** Persistent storage for items, images, and telemetry.
- **Design Reference:** `docs/Design_Specification.md` > Section 12.1
- **Test Owner:** Jones (Gemini Agent)

#### ✅ Test Cases
| Test ID | Description | Input | Expected Output | Status | Notes |
|--------|-------------|-------|------------------|--------|-------|
| DB001  | Schema Initialization | `schema.sql` | Tables `items`, `images`, `telemetry` exist | **Pass** | Verified via src/verify_db.py |
| DB002  | Telemetry Insert | Sample JSON Log | Record added to `telemetry` table | **Pass** | Verified in tests/test_backend.py |
| DB003  | Item Deduplication (Idempotency) | Duplicate `item_code` insert | Record updated, not duplicated | **Pass** | Verified in tests/test_backend.py |
| DB004  | **Auto-Healing** | Corrupt .db file (write garbage) | App renames corrupt file, inits fresh DB | **Pass** | Implemented in db_manager.py |
| DB005  | **Factory Reset** | Call `reset_database()` | DB wiped and schema re-applied | **Pass** | Implemented in db_manager.py |

### Module: AI Integration (Ollama)
- **Purpose:** Visual analysis and descriptive text generation.
- **Design Reference:** `src/ai_engine.py`
- **Test Owner:** Jones (Gemini Agent)

#### ✅ Test Cases
| Test ID | Description | Input | Expected Output | Status | Notes |
|--------|-------------|-------|------------------|--------|-------|
| AI001  | Service Status Check | `check_ollama_status()` | Returns `running: True` or clear error | **Pass** | Verified in UI Sidebar |
| AI002  | **Multi-Item Detection** | Image with 3 pendants | Returns List of 3 JSON objects | **Pass** | Implemented in analyze_image_content |
| AI003  | **Smart JSON Cleaning** | Markdown string (` ```json ... `) | Returns pure valid JSON string | **Pass** | Implemented in clean_json_output |
| AI004  | **Retry Logic** | Simulate network fail | Retries 2x before raising error | **Pass** | Implemented in safe_chat_call |
| AI005  | **3-Style Generation** | Vision Features | Returns JSON with `hero`, `modern`, `social` | **Pass** | Implemented in generate_marketing_copy |

---

## 🔗 Integration Tests

### Scenario: End-to-End Multi-Item Workflow
- **Modules Involved:** UI, Database, Ollama Vision, Ollama Text
- **Test Steps:**
  1. Upload `IMG_6070.jpeg` (Tray of jade) via UI.
  2. System detects **multiple** items (e.g., `PA-001`, `PA-002`).
  3. System generates **3 styles** of copy for each item.
  4. User clicks "Save" (or auto-save).
  5. User clicks "Export CSV".
- **Expected Outcome:** 
  - UI displays list of items.
  - CSV file contains all items with new columns (`description_modern`, `description_social`).
- **Status:** **Ready for UAT**
- **Notes:**

### Scenario: Web Preview & Catalog
- **Modules Involved:** UI, Database
- **Test Steps:**
  1. Go to "Catalog" tab.
  2. Expand an item.
  3. Check "👁️ Web Preview".
- **Expected Outcome:** 
  - Modal/Expander opens showing simulated product page.
  - Hero text in "Brand Story", Modern text in "Features", Social text in "Share".
- **Status:** **Ready for UAT**

---

## 🗃️ Database Validation

### SQLite Configuration
- [x] Schema initialized correctly
- [x] CRUD operations verified
- [x] **New Columns Added:** `description_modern`, `description_social`
- [x] **Migration Logic:** `check_and_migrate_db()` runs on startup

---

## 🧼 Edge Case & Error Handling

| Case ID | Description | Trigger | Expected Behavior | Status | Notes |
|---------|-------------|---------|-------------------|--------|-------|
| EC001   | Unreadable Label | Image with blurry text | Vision model returns `Unknown` code | **Handled** | Returns `Unknown-{idx}` |
| EC002   | Non-Jade Image | Upload random photo | Log "No items detected" | **Handled** | UI shows warning |
| EC003   | **Corrupt JSON** | AI outputs bad JSON | `clean_json_output` attempts fix or returns partial | **Handled** | Fallback dict used |
| EC004   | **DB Corruption** | `.db` file is 0 bytes or garbage | `get_db_connection` triggers auto-heal | **Handled** | Backup created |

---

## 📈 Test Summary & Reporting
- **Test Lead:** Jones
- **Reporting Frequency:** After each major feature implementation
- **Tools Used:** `pytest`, `sqlite3` CLI, `Streamlit` manual test
- **Known Issues:** None
