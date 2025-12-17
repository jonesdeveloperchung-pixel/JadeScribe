
## Design Specification

**Project Title:** JadeScribe

---

### 1. Design Objectives

* Present jade pendants in a **luxury, culturally respectful, and timeless manner**
* Ensure **clarity, consistency, and visual harmony** across all descriptions
* Support multiple use cases: **catalogs, inventory systems, online retail, and exhibitions**

---

### 2. Content Architecture

Each jade pendant entry shall follow the structure below:

1. **Pendant Title**

   * Format: *Jade Pendant – [Motif/Figure Name]*
   * Example: *Jade Pendant – Guanyin*

2. **Item Code**

   * Displayed prominently under the title
   * Format: `Item Code: PA-0425_AF`

3. **Primary Description (Hero Paragraph)**

   * 80–150 words
   * Poetic, refined language
   * Focus on:

     * Visual beauty
     * Craftsmanship
     * Emotional and cultural resonance

4. **Detail Highlights (Optional Section)**

   * Bullet points for quick reference:

     * Color
     * Carving style
     * Finish
     * Symbolism

---

### 3. Visual & Stylistic Design

#### 3.1 Tone & Voice

* Elegant
* Calm
* Reverent
* Culturally informed
* Avoid commercial exaggeration or spiritual absolutes

#### 3.2 Language Style

* Descriptive, flowing sentences
* Sensory vocabulary (light, texture, form)
* Balanced poetic expression and factual clarity

---

### 4. Typography (Recommended)

#### 4.1 Headings

* Typeface: Serif (e.g., Garamond, Baskerville, Playfair Display)
* Weight: Medium to Semi-bold
* Color: Deep charcoal or jade green

#### 4.2 Body Text

* Typeface: Clean serif or humanist sans-serif
* Size: 10.5–12 pt (print), 14–16 px (digital)
* Line spacing: 1.4–1.6

---

### 5. Layout Design

#### 5.1 Print Catalog

* One pendant per section or page
* Image placed:

  * Above or to the left of text
* White or soft neutral background
* Generous margins to emphasize luxury

#### 5.2 Digital Presentation

* Responsive card-style layout
* Item code placed directly under the title
* Clear separation between entries
* Hover or expandable section for symbolism

---

### 6. Image Presentation Guidelines

* High-resolution images (minimum 300 DPI for print)
* Neutral background (black, gray, or soft cream)
* Soft lighting to highlight jade translucency
* No harsh reflections
* Pendant centered and proportionally scaled

---

### 7. Item Code Design Rules

* Item codes must:

  * Be identical to physical labels
  * Use monospaced or clean sans-serif font
  * Remain non-decorative
* Position:

  * Directly below title
  * Or in a clearly defined metadata section

---

### 8. Symbolism Representation

* Symbolism should be:

  * Informative, not prescriptive
  * Rooted in cultural tradition
* Use phrases such as:

  * “Traditionally associated with…”
  * “Often regarded as a symbol of…”

---

### 9. Accessibility Considerations

* Adequate color contrast
* Readable font sizes
* Avoid overly ornate text blocks
* Clear hierarchy for screen readers (digital use)

---

### 10. Consistency & Quality Control

* All entries must follow the same:

  * Structure
  * Tone
  * Typography
* Descriptions reviewed for:

  * Cultural sensitivity
  * Visual accuracy
  * Language elegance

---

### 11. Future Scalability

This design specification supports:

* Expansion to full collections
* Multilingual versions
* Integration into inventory databases
* Museum or gallery exhibition labeling

---

### 12. Data & System Design

#### 12.1 Database Schema (SQLite)

The system will use a normalized SQLite database structure.

**Table: `items`**
*   `item_code` (TEXT, PK): The unique identifier (e.g., "PA-0425_AF").
*   `title` (TEXT): Generated title (e.g., "Jade Pendant – Guanyin").
*   `description_hero` (TEXT): The main poetic description.
*   `attributes_json` (TEXT): JSON string storing extracted features (Color, Texture, Symbolism).
*   `created_at` (DATETIME): Timestamp of creation.
*   `updated_at` (DATETIME): Timestamp of last edit.

**Table: `images`**
*   `id` (INTEGER, PK, Auto-increment)
*   `file_path` (TEXT, Unique): Relative path to the source image.
*   `processed_status` (TEXT): 'PENDING', 'PROCESSED', 'ERROR'.
*   `scan_date` (DATETIME).

**Table: `item_images` (Junction)**
*   `item_code` (FK -> items.item_code)
*   `image_id` (FK -> images.id)
*   `is_primary` (BOOLEAN): Whether this image is the main display image for the item.

#### 12.2 System Architecture



1.  **Ingestion Layer:**

    *   Scans directories for `*.jpeg`, `*.jpg`, `*.png`.

    *   Checks `images` table to skip already processed files.



2.  **Analysis Layer (Ollama Vision):**

    *   Model: `llava:latest`.

    *   Task: Identify distinct pendants in the image, extract "Item Code" text (OCR), and generate a preliminary visual list of features (Color, Motif).



3.  **Knowledge Retrieval:**

    *   Input: Detected Motif (e.g., "Bamboo").

    *   Process: Query `symbolism_glossary.json` for cultural context.



4.  **Generation Layer (Ollama Text):**

    *   Model: `gemma3n:e4b`.

    *   Input: Visual features + Item Code + Symbolism Context.

    *   Output: Formatted Markdown description.



5.  **Storage Layer:**

    *   Saves final text and relationships to SQLite.





---



### 13. Telemetry Specification



#### 13.1 Core Schema



The system will emit telemetry events matching this JSON structure:



```json

{

  "timestamp": "ISO8601 String",

  "program": "jade-recog-cli",

  "version": "1.0.0",

  "command": "full command string",

  "module": "e.g., image_processor",

  "action": "e.g., scan",

  "args": ["arg1", "arg2"],

  "user": "system_user",

  "host": "hostname",

  "os": "os_name",

  "runtime": "python_version",

  "execution": {

    "duration_ms": 120,

    "cpu_time_ms": 100,

    "gpu_time_ms": 20,

    "memory_mb": 45.5,

    "exit_code": 0,

    "error": null

  },

  "context": {

    "cwd": "/path/to/working/dir",

    "env": { "DEBUG": "true" },

    "tags": ["cli", "vision"]

  }

}

```



#### 13.2 Field Definition



**Identity**

*   `program`: "jade-recog-cli"

*   `version`: Current project version.

*   `command`: The CLI command executed.

*   `module`: The internal module (e.g., `ocr`, `planner`, `db`).

*   `action`: The specific function or step (e.g., `extract_text`, `generate_description`).



**Execution Metrics**

*   `duration_ms`: Wall-clock time in milliseconds.

*   `gpu_time_ms`: Time spent waiting for Ollama/GPU responses.

*   `memory_mb`: Peak memory usage during the operation.



**Context**

*   `tags`: Useful filters (e.g., `["error", "ocr_failure"]`).
