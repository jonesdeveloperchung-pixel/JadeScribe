# 🟢 JadeScribe

## 📋 Overview
**JadeScribe** is an AI-powered tool designed to automate the cataloging of high-end jade pendants. It processes images to:
1.  **Identify** items and extract their codes (e.g., `PA-0425_AF`).
2.  **Analyze** visual features (Color, Motif, Texture).
3.  **Generate** elegant, culturally informed descriptions in Traditional Chinese (繁體中文).
4.  **Catalog** all data into a local SQLite database.

## 🏗️ Architecture
*   **Frontend:** [Streamlit](https://streamlit.io/) (Web UI).
*   **AI Engine:** [Ollama](https://ollama.com/) (Local).
    *   **Vision:** `llava:latest` (Image Analysis & OCR).
    *   **Text:** `gemma3n:e4b` (Creative Writing).
*   **Database:** SQLite (`data/jade_inventory.db`).
*   **Knowledge Base:** `data/symbolism_glossary.json` (Cultural symbolism).

## 🚀 Quick Start

### Prerequisites
*   Python 3.10+
*   [Ollama](https://ollama.com/) installed and running.
*   Required Models:
    ```bash
    ollama pull llama3.2-vision:latest
    ollama pull gemma3n:e4b
    ```

### Installation
1.  **Clone/Open the repository.**
2.  **Set up Virtual Environment:**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```
3.  **Navigate to Project Folder:**
    ```bash
    cd JadeScribe
    ```
4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuration
The system uses **Environment Variables** for configuration. 
You can create a `.env` file or set them in your shell.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `OLLAMA_HOST` | URL of the Ollama API | `http://localhost:11434` |
| `VISION_MODEL` | Model for Image Analysis | `llama3.2-vision:latest` |
| `TEXT_MODEL` | Model for Description Generation | `gemma3n:e4b` |

**Example (Windows PowerShell):**
```powershell
$env:OLLAMA_HOST="http://192.168.1.100:11434"
streamlit run src/app.py
```

### Running the Application
```bash
streamlit run src/app.py
```
Access the UI at: `http://localhost:8501`

## 📂 Project Structure
```
JadeScribe/
├── data/
│   ├── jade_inventory.db      # SQLite Database (Local only)
│   ├── schema.sql             # Database Schema
│   └── symbolism_glossary.json # Cultural Knowledge Base
├── docs/                      # Design & Requirement Specs
├── images/                    # Image Analysis Buffer
├── src/
│   ├── ai_engine.py           # Ollama Integration (Vision/Text)
│   ├── app.py                 # Streamlit UI Entry Point
│   ├── db_manager.py          # Database CRUD Operations
│   └── utils.py               # Helper Utilities
├── tests/                     # Automated Tests
└── requirements.txt           # Python Dependencies
```

## 🧪 Testing
Run the verification script to check database integrity:
```bash
python src/verify_db.py
```

## 📝 Features
*   **Image Analysis:** Automatically detects item codes and visual traits.
*   **Symbolism Integration:** Weaves cultural meanings (e.g., Guanyin, Bamboo) into descriptions.
*   **Telemetry:** Logs execution metrics to the database for debugging.
*   **Localization:** Default UI and Content in Traditional Chinese (zh-TW).

## 📦 Release & Deployment
This project uses **GitHub Actions** to automatically build a standalone Windows executable.

### How to Build
1.  **Push a Tag:** The workflow is triggered when you push a tag starting with `v` (e.g., `v1.0.0`).
    ```bash
    git tag v1.0.0
    git push origin v1.0.0
    ```
2.  **Download:** Go to the **Releases** page on GitHub. You will find a `JadeScribe-Windows.zip` file attached to the release.
3.  **Run:** Extract the zip and run `JadeScribe.exe`.

> **Note:** The executable contains the application logic but **still requires Ollama** to be installed and running on the user's machine.

## 📄 License
MIT License. See [LICENSE](LICENSE) for details.
