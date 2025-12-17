import streamlit as st
import logging
import json
import os
import time
from PIL import Image
from utils import check_ollama_status, get_default_model_config
from ai_engine import analyze_image_content, generate_poetic_description
from db_manager import save_item, get_all_items

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- UI Configuration (Traditional Chinese Default) ---
st.set_page_config(
    page_title="JadeScribe - 翡翠辨識與編目系統",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar: System Status & Config ---
with st.sidebar:
    st.header("系統狀態 (System Status)")
    
    # Check Ollama Status
    ollama_status = check_ollama_status()
    if ollama_status["running"]:
        st.success(f"✅ AI 引擎運作中 ({ollama_status.get('message', '')})")
    else:
        st.error("🛑 AI 引擎未連線")
        st.warning("請確保 Ollama 已在背景執行.\n\n(Please ensure Ollama is running in the background.)")
        if st.button("重新檢查連線 (Retry)"):
            st.rerun()

    st.markdown("---")
    st.header("設定 (Settings)")
    st.info("預設使用模型 (Default Models):")
    config = get_default_model_config()
    st.code(json.dumps(config, indent=2), language="json")

# --- Main Content ---
st.title("🟢 JadeScribe")
st.markdown("### 智能翡翠辨識與編目系統 (Intelligent Jade Cataloging)")

# Tabs for Workflow
tab1, tab2, tab3 = st.tabs(["📸 影像上傳 (Upload)", "📝 編目列表 (Catalog)", "⚙️ 系統日誌 (Logs)"])

with tab1:
    st.header("1. 上傳翡翠影像")
    uploaded_file = st.file_uploader("請選擇影像檔案 (Supported: JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        # Display Image
        st.image(uploaded_file, caption="預覽 (Preview)", use_container_width=True)
        
        # Save temp file for Ollama
        temp_dir = "images"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Action Buttons
        col1, col2 = st.columns(2)
        with col1:
            analyze_btn = st.button("🔍 開始辨識 (Start Analysis)", type="primary", disabled=not ollama_status["running"])
        
        if analyze_btn:
            with st.spinner("⏳ 正在分析影像與提取編號... (Analyzing Image & Codes...)"):
                # 1. Vision Analysis
                vision_result = analyze_image_content(temp_path)
                
                if "error" in vision_result:
                    st.error(f"Analysis Failed: {vision_result['error']}")
                else:
                    st.success("影像分析完成！ (Analysis Complete)")
                    
                    # Display Extracted Data
                    item_code = vision_result.get("item_code", "Unknown")
                    features = vision_result.get("visual_features", {})
                    
                    st.markdown("#### 👁️ 視覺識別結果 (Visual Recognition)")
                    c1, c2 = st.columns(2)
                    c1.metric("識別編號 (Item Code)", item_code)
                    c2.json(features)
                    
                    # 2. Text Generation
                    with st.spinner("✍️ 正在生成描述... (Generating Description...)"):
                        description = generate_poetic_description(vision_result)
                    
                    st.markdown("#### 📜 生成描述 (Description)")
                    st.info(description)
                    
                    # 3. Save to DB
                    if item_code != "Unknown":
                        save_success = save_item({
                            "item_code": item_code,
                            "title": f"Jade Pendant - {features.get('motif', 'Unknown')}",
                            "description_hero": description,
                            "attributes": features
                        })
                        
                        if save_success:
                            st.toast("已儲存至資料庫！ (Saved to Database)", icon="💾")
                        else:
                            st.error("儲存失敗 (Save Failed)")

with tab2:
    st.header("已編目翡翠 (Cataloged Items)")
    
    if st.button("🔄 重新整理列表 (Refresh)"):
        st.rerun()
        
    items = get_all_items()
    
    if not items:
        st.info("目前資料庫中沒有項目 (No items in database).")
    else:
        for item in items:
            with st.expander(f"{item['item_code']} - {item['title']}"):
                st.markdown(f"**描述 (Description):**\n{item['description_hero']}")
                st.caption(f"最後更新: {item['updated_at']}")
                st.json(json.loads(item['attributes_json']))

with tab3:
    st.header("系統日誌與遙測 (Telemetry)")
    st.write("目前僅支援後台記錄 (Logs are currently backend-only). Check `telemetry` table in SQLite.")
    
    # Simple query to show last 5 logs
    import sqlite3
    conn = sqlite3.connect(os.path.join("data", "jade_inventory.db"))
    try:
        logs = conn.execute("SELECT timestamp, module, action, duration_ms, error FROM telemetry ORDER BY id DESC LIMIT 10").fetchall()
        if logs:
            st.table(logs)
        else:
            st.info("尚無日誌資料 (No logs yet)")
    except Exception as e:
        st.error(f"Error fetching logs: {e}")
    finally:
        conn.close()