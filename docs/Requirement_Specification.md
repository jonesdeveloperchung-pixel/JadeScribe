
## Requirement Specification

**Project Title:** JadeScribe (Jade Pendant Recognition & Documentation)

### 1. Purpose

To create **accurate, elegant, and market-ready descriptions** of jade pendants, each clearly associated with its **unique item code**, suitable for use in catalogs, inventories, online stores, or exhibitions.

---

### 2. Scope

This specification applies to:

* Individual **jade pendant selection**
* **Descriptive writing** emphasizing aesthetics and symbolism
* **Item code identification and listing**
* Presentation in a **luxury, cultural, and informative tone**

---

### 3. Functional Requirements

#### 3.1 Pendant Selection

* Select **one specific jade pendant** from the provided image.
* Clearly state:

  * **Item code**
  * **Location in the tray** (e.g., bottom row, center)

#### 3.2 Visual Description

The description must include:

* Jade **color and tone** (e.g., pale green, moss green, translucent white)
* **Material characteristics** (translucency, texture, polish)
* **Carving details** (figure, shape, motifs)
* **Metal attachment** or clasp details (if visible)

#### 3.3 Symbolism & Meaning

* Identify **traditional or cultural symbolism** (e.g., Guanyin, protection, compassion).
* Express meaning in a **respectful and culturally aware manner**.
* Avoid claims of supernatural guarantees.

#### 3.4 Aesthetic Language

* Use **refined, poetic, and elegant language**.
* Tone should be:

  * Calm
  * Premium
  * Timeless
* Suitable for **high-end jewelry presentation**.

#### 3.5 Item Code Documentation

* Provide a **list of all visible item codes** in the image.
* Codes must:

  * Match labels exactly as seen
  * Be formatted consistently (e.g., PA-0425_AF)

---

### 4. Non-Functional Requirements

#### 4.1 Accuracy

* Descriptions must be **faithful to what is visible** in the image.
* No identification of real people.
* No assumptions about jade grade or origin unless specified.

#### 4.2 Consistency

* Writing style must remain consistent across all pendant descriptions.
* Item code format must not vary.

#### 4.3 Readability

* Content should be:

  * Clear
  * Well-structured
  * Easy to adapt for marketing or documentation use

---

### 5. Deliverables

* One **feature jade pendant description** (per request)
* One **complete item code list**
* Text delivered in **ready-to-use format**

---

### 6. Optional Extensions (Future Use)

* Full catalog descriptions for each pendant
* Symbolism reference guide
* Pricing or grading placeholders
* Multilingual descriptions

---

### 7. Technical Requirements

#### 7.1 Technology Stack
*   **Language:** Python 3.10+
*   **Database:** SQLite (local file-based storage)
*   **AI/LLM Engine:** Ollama (Local/Network)
    *   **Vision/OCR:** `llava:latest`
    *   **Text Generation:** `gemma3n:e4b`
    *   **Embeddings:** `nomic-embed-text:latest` (for symbolism retrieval)
*   **UI:** UI-driven interface (Streamlit or similar Python web-UI framework preferred over pure CLI for final delivery, per project memory).

#### 7.2 Data Persistence
*   All item data (codes, descriptions, image paths) must be persisted in a SQLite database (`jade_inventory.db`).
*   System must support idempotent processing (re-scanning an image shouldn't create duplicate DB entries for the same item code).

#### 7.3 Telemetry & Logging
*   **Standard:** Strict adherence to the "General Telemetry Specification".
*   **Schema:** Logs must use the standardized JSON structure:
    *   `identity`: program, version, command, module, action, args.
    *   `environment`: user, host, os, runtime.
    *   `execution`: duration_ms, cpu_time_ms, gpu_time_ms, memory_mb, exit_code, error.
    *   `context`: cwd, env, tags.
*   **Storage:**
    *   Primary: `telemetry.jsonl` (JSON Lines) for local auditing.
    *   Secondary: `telemetry` table in `jade_inventory.db` for structured querying.

#### 7.4 Security & Privacy

*   Local processing only (no data sent to external cloud APIs).

*   Respect `.gitignore` and `.geminiignore`.



---



### 8. Usability & Localization



#### 8.1 Language Preferences

*   **Default Language:** Traditional Chinese (zh-TW) for all UI elements, logs, and generated descriptions.

*   **Secondary Language:** English (en-US) available as a fallback or toggle.

*   **Content Tone:** Elegant, culturally resonant Chinese (e.g., using idioms like "溫潤如玉", "節節高升").



#### 8.2 User Experience (UX) Principles

*   **Zero Configuration:** The application must start with sensible defaults (Local Ollama, standard ports) without requiring config file editing.

*   **UI-First:** Interaction must be through a visual interface (Web UI), not CLI commands.

*   **Feedback:** Operations must provide immediate visual feedback (Spinners for "Analyzing...", Toasts for "Success").

*   **Resilience:** If Ollama is offline, the UI must clearly guide the user to start it, rather than crashing with a stack trace.
