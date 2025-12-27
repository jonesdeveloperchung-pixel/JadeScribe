# 🟢 JadeScribe (翠藝錄)

[English](README_EN.md) | [繁體中文](README.md)

**JadeScribe** 是一個專為高端翡翠珠寶設計的 AI 智能編目助手。它利用本地運行的人工智慧模型，自動分析影像、識別商品編號，並生成具有文化底蘊的行銷文案。

![JadeScribe 主畫面](screenshots/main.png)

## ✨ 主要功能

*   **👁️ 智慧影像分析 (Vision Analysis)**
    *   **高效能辨識**：支援使用 **`moondream:latest`** 模型，以極低資源消耗實現秒級辨識（單件約 30 秒）。
    *   **遠端 AI 引擎**：支援連接高效能遠端 Ollama 伺服器，釋放本地電腦運算壓力。
    *   **批量識別**：能一次掃描整盤翡翠，自動偵測多個吊墜及其對應的商品編號（OCR）。

*   **📤 多檔案與多視窗處理 (Batch & Multi-window)**
    *   **多檔案上傳**：支援一次選取並處理多張照片。
    *   **多視窗並行**：支援同時開啟多個瀏覽器分頁獨立處理不同檔案，互不干擾。
    *   **階段式進度**：詳細的進度追蹤，即時反饋分析狀態。

*   **✍️ 三重風格文案生成 (Marketing Suite)**
    *   **📜 經典敘事 (Hero)**：優雅、詩意，融入文化寓意（如「竹報平安」），適合品牌故事或畫冊。
    *   **🛍️ 現代電商 (Modern)**：直觀、條列式，強調材質與佩戴亮點，適合官網詳情頁。
    *   **📱 社群快訊 (Social)**：短小精悍，帶有 Emoji 與熱門標籤，適合 Instagram 或小紅書推廣。

*   **🏪 商品編目與匯出**
    *   **Web Preview**：內建模擬商品頁面，即時預覽文案在電商網站上的效果。
    *   **CSV 匯出**：一鍵下載完整資料庫，輕鬆匯入 Shopify、WooCommerce 或 ERP 系統。

*   **🛡️ 企業級穩定性**
    *   **資料庫自癒**：遇到損壞自動備份並重建，確保系統不中斷。
    *   **AI 容錯**：具備網路重試機制與智慧 JSON 解析，提升生成成功率。

---

## 🚀 快速開始

### 前置需求
*   **Python 3.10+**
*   **[Ollama](https://ollama.com/)** (需安裝並在背景執行)
*   **必備 AI 模型**：
    請在終端機執行以下指令下載模型：
    ```bash
    ollama pull moondream:latest        # 輕量級視覺模型 (推薦)
    ollama pull llava:latest            # 高精度視覺模型 (可選)
    ollama pull gemma3n:e4b             # 文字模型
    ```

### 安裝步驟

1.  **下載專案**
    ```bash
    git clone https://github.com/yourusername/JadeScribe.git
    cd JadeScribe
    ```

2.  **建立虛擬環境 (推薦)**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```

3.  **安裝依賴套件**
    ```bash
    pip install -r requirements.txt
    ```

### 啟動應用程式
```bash
streamlit run src/app.py
```
啟動後，瀏覽器將自動開啟：`http://localhost:8501`

---

## 📖 使用指南

### 1. 影像上傳 (Upload)
在「📸 影像上傳」分頁，拖曳或選擇您的翡翠照片。系統會自動偵測連線狀態。點擊 **「🔍 開始辨識」**，AI 將掃描所有物件。

### 2. 文案審閱 (Review)
辨識完成後，系統會列出所有偵測到的商品。您可以展開每個項目，切換查看 **經典、現代、社群** 三種風格的文案。

### 3. 編目管理 (Catalog)
切換至「📝 編目列表」分頁：
*   **預覽 (Web Preview)**：勾選商品可查看模擬網頁效果。
*   **匯出 (Export)**：點擊「📥 下載完整報表」取得 CSV 檔。

![編目列表](screenshots/catalog.png)

### 4. 系統重置 (Reset)
若需清空所有測試資料，可至左側邊欄的 **「⚠️ 危險區域」** 執行「重置資料庫」，或在終端機執行：
```bash
python reset.py
```

### 5. 系統日誌 (Logs)
切換至「⚙️ 系統日誌」分頁，可查看後台運行的詳細記錄，包含 API 回應狀態與錯誤訊息。

![系統日誌](screenshots/Log.png)

---

## 🏗️ 技術架構
*   **Frontend**: Streamlit (Python Web UI)
*   **AI Backend**: Ollama (Local LLM)
    *   Vision: `llama3.2-vision`
    *   Text: `gemma3n:e4b` (Localized for Traditional Chinese)
*   **Database**: SQLite (Local file-based, Auto-healing)
*   **Knowledge**: `data/symbolism_glossary.json` (文化象徵資料庫)

## 📄 授權條款
MIT License. 詳見 [LICENSE](LICENSE) 文件。