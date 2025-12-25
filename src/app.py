import streamlit as st
import logging
import json
import os
import time
from PIL import Image
from utils import check_ollama_status, get_default_model_config
from ai_engine import analyze_image_content, generate_marketing_copy
from db_manager import save_item, get_all_items, check_and_migrate_db, export_items_to_csv

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Initialization ---
# Migrate DB on startup to ensure new columns exist
check_and_migrate_db()

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
    
    # 1. Check Connection
    ollama_status = check_ollama_status()
    system_healthy = False
    
    if ollama_status["running"]:
        st.success(f"✅ AI 引擎運作中 ({ollama_status.get('message', '')})")
        
        # 2. Check Models
        config = get_default_model_config()
        vision_model = config["vision_model"]
        text_model = config["text_model"]
        
        from utils import check_model_availability
        vision_check = check_model_availability(vision_model)
        text_check = check_model_availability(text_model)
        
        # Vision Model Status
        if vision_check["available"]:
            st.caption(f"👁️ 視覺模型: {vision_model} (Ready)")
        else:
            st.error(f"❌ 缺少視覺模型: {vision_model}")
            st.code(f"ollama pull {vision_model}", language="bash")
            
        # Text Model Status
        if text_check["available"]:
            st.caption(f"✍️ 文字模型: {text_model} (Ready)")
        else:
            st.error(f"❌ 缺少文字模型: {text_model}")
            st.code(f"ollama pull {text_model}", language="bash")
            
        # Global Health Flag
        if vision_check["available"] and text_check["available"]:
            system_healthy = True
            st.info("🟢 系統準備就緒 (System Ready)")
        else:
            st.warning("⚠️ 請先安裝缺少的模型 (Please install missing models)")
            
    else:
        st.error("🛑 AI 引擎未連線")
        st.warning("請確保 Ollama 已在背景執行.\n\n(Please ensure Ollama is running in the background.)")
        if st.button("重新檢查連線 (Retry)"):
            st.rerun()

    st.markdown("---")
    st.header("設定 (Settings)")
    st.info("目前配置 (Current Config):")
    st.code(json.dumps(get_default_model_config(), indent=2), language="json")

    # Performance Settings
    st.markdown("#### 效能設定 (Performance)")
    enable_ocr = st.toggle("🚀 啟用增強 OCR (Enable Enhanced OCR)", value=True, help="關閉此選項可加快舊電腦的處理速度 (Disable for faster performance on old PCs)")
    if not enable_ocr:
        st.caption("⚠️ 快速模式：將跳過文字識別，僅進行影像分析。")
    
    st.markdown("---")
    st.header("危險區域 (Danger Zone)")
    with st.expander("⚠️ 重置系統 (Reset System)"):
        st.warning("這將刪除所有已儲存的資料！\n(This will delete all saved data!)")
        confirm_reset = st.checkbox("我確定要重置資料庫 (I confirm)")
        
        if st.button("🗑️ 重置資料庫 (Reset DB)", type="primary", disabled=not confirm_reset):
            from db_manager import reset_database
            if reset_database():
                st.toast("資料庫已重置！ (Database Reset)", icon="🧹")
                time.sleep(1)
                st.rerun()
            else:
                st.error("重置失敗 (Reset Failed)")

# --- Main Content ---
st.title("🟢 JadeScribe")
st.markdown("### 智能翡翠辨識與編目系統 (Intelligent Jade Cataloging)")

# Tabs for Workflow
tab1, tab2, tab3 = st.tabs(["📸 影像上傳 (Upload)", "📝 編目列表 (Catalog)", "⚙️ 系統日誌 (Logs)"])

with tab1:
    st.header("1. 上傳翡翠影像")
    st.caption("支援多物件識別 (Supports multi-item detection)")
    uploaded_file = st.file_uploader("請選擇影像檔案 (Supported: JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        # Display Image
        st.image(uploaded_file, caption="預覽 (Preview)")
        
        # Save temp file for Ollama
        temp_dir = "images"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Action Buttons
        col1, col2 = st.columns(2)
        with col1:
            # User Hints Input
            user_tags = st.text_input("💡 輔助標籤 (Optional Hints)", 
                                    placeholder="例如：觀音, 滿綠, 冰種 (e.g., Guanyin, Imperial Green)",
                                    help="輸入關鍵字可幫助 AI 更準確識別圖案與特徵 (Keywords help AI identify motifs accurately)")
            
            # Only enable button if system is healthy
            analyze_btn = st.button(
                "🔍 開始辨識 (Start Analysis)", 
                type="primary", 
                disabled=not system_healthy,
                help="請先解決左側邊欄的系統問題 (Please resolve system issues in sidebar)" if not system_healthy else "開始分析影像"
            )
        
        if analyze_btn:
            with st.spinner("⏳ 正在分析影像與提取物件... (Scanning Image...)"):
                # 1. Vision Analysis (Returns a List)
                items_found = analyze_image_content(temp_path, enable_ocr=enable_ocr, user_hints=user_tags)
                
                # Check for global errors (single error dict in list)
                if len(items_found) == 1 and "error" in items_found[0]:
                     st.error(f"Analysis Failed: {items_found[0]['error']}")
                elif not items_found:
                    st.warning("⚠️ 未檢測到任何翡翠物件 (No items detected).")
                else:
                    st.success(f"✅ 成功識別 {len(items_found)} 個物件 (Found {len(items_found)} items)!")
                    
                    # Iterate through each detected item
                    for idx, item in enumerate(items_found):
                        item_code = item.get("item_code", f"Unknown-{idx}")
                        features = item.get("visual_features", {})
                        crop_path = item.get("crop_path", None)
                        
                        with st.expander(f"💎 物件 #{idx+1}: {item_code}", expanded=True):
                            c1, c2 = st.columns([1, 2])
                            with c1:
                                # Show Enhanced Crop if available (The "Gemologist View")
                                if crop_path and os.path.exists(crop_path):
                                    st.image(crop_path, caption="🔍 增強細節 (Enhanced Detail)")
                                else:
                                    st.caption("無局部特寫 (No Crop Available)")
                                
                                st.metric("識別編號", item_code, delta="OCR Verified" if crop_path else "AI Vision")
                                st.json(features)
                            
                            with c2:
                                with st.spinner(f"✍️ 正在為 {item_code} 生成文案..."):
                                    # 2. Generate Marketing Copy (3 Styles)
                                    copy_deck = generate_marketing_copy(item)
                                    
                                    # Display Tabs for Styles
                                    t_hero, t_modern, t_social = st.tabs(["📜 經典 (Classical)", "🛍️ 現代 (Modern)", "📱 社群 (Social)"])
                                    with t_hero:
                                        st.write(copy_deck["hero"])
                                    with t_modern:
                                        st.write(copy_deck["modern"])
                                    with t_social:
                                        st.write(copy_deck["social"])
                                    
                                    # 3. Save to DB automatically
                                    if item_code and item_code != "Unknown":
                                        save_item({
                                            "item_code": item_code,
                                            "title": f"Jade Pendant - {features.get('motif', 'Unknown')}",
                                            "description_hero": copy_deck["hero"],
                                            "description_modern": copy_deck["modern"],
                                            "description_social": copy_deck["social"],
                                            "attributes": features
                                        })
                                        st.toast(f"已儲存: {item_code}", icon="💾")

with tab2:
    st.header("已編目翡翠 (Cataloged Items)")
    
    col_tools_1, col_tools_2 = st.columns([1, 3])
    with col_tools_1:
        if st.button("🔄 重新整理 (Refresh)"):
            st.rerun()
    with col_tools_2:
        # CSV Export
        csv_data = export_items_to_csv()
        st.download_button(
            label="📥 下載完整報表 (Export CSV)",
            data=csv_data,
            file_name="jade_inventory_export.csv",
            mime="text/csv"
        )
        
    items = get_all_items()
    
    if not items:
        st.info("目前資料庫中沒有項目 (No items in database).")
    else:
        for item in items:
            with st.expander(f"{item['item_code']} - {item['title']}"):
                
                # Preview Toggle
                if st.checkbox(f"👁️ 預覽商品頁面 (Web Preview)", key=f"prev_{item['item_code']}"):
                    st.markdown("---")
                    st.markdown(f"### 🟢 {item['title']}")
                    st.caption(f"Ref: {item['item_code']}")
                    
                    # Simulate Web Layout
                    wc1, wc2 = st.columns([1, 1])
                    with wc1:
                        st.markdown("**產品特色**")
                        st.markdown(item.get('description_modern', 'N/A'))
                    with wc2:
                        st.markdown("**品牌故事**")
                        st.markdown(f"_{item['description_hero']}_")
                    
                    st.markdown("#### 社群分享")
                    st.info(item.get('description_social', 'N/A'))
                    st.button("加入購物車 (Simulated)", key=f"cart_{item['item_code']}")
                    st.markdown("---")

                # Raw Data View
                st.caption(f"最後更新: {item['updated_at']}")
                st.text("原始資料:")
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