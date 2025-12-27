import streamlit as st
import logging
import json
import os
import time
from PIL import Image
from utils import check_ollama_status, get_default_model_config
from ai_engine import analyze_image_content, generate_marketing_copy
from db_manager import save_item, get_all_items, check_and_migrate_db, export_items_to_csv
from grading_utils import JadeGrader
from pdf_generator import generate_pdf_catalog
from manual_generator import generate_user_manual

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Initialization ---
# Migrate DB on startup
check_and_migrate_db()
# Initialize Grader
grader = JadeGrader()

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
    # Manual Download
    try:
        manual_pdf = generate_user_manual()
        st.download_button(
            label="📘 下載使用手冊 (User Manual)",
            data=manual_pdf,
            file_name="JadeScribe_User_Manual.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        logger.error(f"Manual generation failed: {e}")

    st.markdown("---")
    st.header("設定 (Settings)")
    # Performance Settings
    st.markdown("#### 效能設定 (Performance)")
    enable_ocr = st.toggle(
        "🚀 啟用增強 OCR (Enable Enhanced OCR)", 
        value=True, 
        help="【建議開啟】能精準讀取標籤上的編號。\n若您的電腦速度較慢，關閉此選項可大幅加速，但編號可能需要手動修正。"
    )
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
    
    # User Guide Block
    with st.expander("ℹ️ 使用說明 (How to use)", expanded=False):
        st.markdown("""
        1. **上傳照片**：點擊下方按鈕或拖曳照片至上傳區。
        2. **輸入提示**（選填）：若照片較模糊，可輸入關鍵字（如「觀音」）幫助 AI。
        3. **開始辨識**：點擊按鈕，AI 將自動分析並生成文案。
        """)

    uploaded_files = st.file_uploader("請選擇影像檔案 (可多選)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    
    if uploaded_files:
        st.info(f"📁 已選取 {len(uploaded_files)} 個檔案。您可以在此視窗批次處理，或開啟新分頁同時處理其他檔案。")
        
        # Action Buttons
        col1, col2 = st.columns(2)
        with col1:
            user_tags = st.text_input("💡 輔助標籤 (選填，將套用於本次上傳的所有圖片)", 
                                    placeholder="例如：觀音, 冰種",
                                    help="輸入關鍵字可提高 AI 辨識準確度。")
            
            analyze_btn = st.button(
                "🔍 開始處理所有檔案", 
                type="primary", 
                disabled=not system_healthy
            )
        
        if analyze_btn:
            for file_idx, uploaded_file in enumerate(uploaded_files):
                # Unique filename per session/file to prevent multi-window collision
                unique_prefix = f"{int(time.time())}_{file_idx}"
                temp_dir = "images"
                os.makedirs(temp_dir, exist_ok=True)
                temp_filename = f"{unique_prefix}_{uploaded_file.name}"
                temp_path = os.path.join(temp_dir, temp_filename)
                
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.markdown(f"---")
                st.subheader(f"🖼️ 正在處理 ({file_idx+1}/{len(uploaded_files)}): {uploaded_file.name}")
                
                with st.spinner(f"⏳ 正在分析 {uploaded_file.name}..."):
                    # 1. Vision Analysis
                    items_found = analyze_image_content(temp_path, enable_ocr=enable_ocr, user_hints=user_tags)
                    
                    if len(items_found) == 1 and "error" in items_found[0]:
                         st.error(f"[{uploaded_file.name}] Analysis Failed: {items_found[0]['error']}")
                    elif not items_found:
                        st.warning(f"⚠️ [{uploaded_file.name}] 未檢測到任何翡翠物件。")
                    else:
                        st.success(f"✅ [{uploaded_file.name}] 成功識別 {len(items_found)} 個物件!")
                        
                        # Iterate through each detected item
                        for idx, item in enumerate(items_found):
                            item_code = item.get("item_code", f"Unknown-{file_idx}-{idx}")
                            features = item.get("visual_features", {})
                            crop_path = item.get("crop_path", None)
                            
                            rank = grader.calculate_grade(features)
                            rank_info = grader.get_tier_info(rank)
                            
                            with st.expander(f"💎 物件 #{idx+1} ({uploaded_file.name}): {item_code}", expanded=True):
                                c1, c2 = st.columns([1, 2])
                                with c1:
                                    if crop_path and os.path.exists(crop_path):
                                        st.image(crop_path, caption="🔍 增強細節")
                                    else:
                                        st.caption("無局部特寫")
                                    
                                    st.metric("識別編號", item_code)
                                    st.markdown(f"**參考評級:** :{rank_info['color']}[{rank}級 - {rank_info['name']}]")
                                    st.json(features)
                                
                                with c2:
                                    with st.spinner(f"✍️ 正在生成文案..."):
                                        copy_deck = generate_marketing_copy(item)
                                        t_hero, t_modern, t_social = st.tabs(["📜 經典", "🛍️ 現代", "📱 社群"])
                                        with t_hero: st.write(copy_deck["hero"])
                                        with t_modern: st.write(copy_deck["modern"])
                                        with t_social: st.write(copy_deck["social"])
                                        
                                        if item_code and "Unknown" not in item_code:
                                            save_item({
                                                "item_code": item_code,
                                                "title": f"Jade Pendant - {features.get('motif', 'Unknown')}",
                                                "description_hero": copy_deck["hero"],
                                                "description_modern": copy_deck["modern"],
                                                "description_social": copy_deck["social"],
                                                "attributes": features,
                                                "rarity_rank": rank
                                            })
                                            st.toast(f"已儲存: {item_code}", icon="💾")
    else:
        st.info("💡 請先上傳照片以開始編目流程。")

with tab2:
    st.header("已編目翡翠 (Cataloged Items)")
    
    with st.expander("ℹ️ 使用說明 (How to filter)", expanded=False):
        st.info("您可以使用下方的工具來篩選庫存。支援依「關鍵字」搜尋（如編號）或依「等級」篩選。")

    # --- Toolbar (Search & Filter) ---
    st.markdown("##### 🔍 搜尋與篩選 (Search & Filter)")
    f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
    with f_col1:
        search_query = st.text_input("關鍵字搜尋 (Search by code or title)", placeholder="PA-0425, Guanyin...")
    with f_col2:
        filter_grade = st.selectbox("等級篩選 (Grade)", ["All", "S", "A", "B"])
    with f_col3:
        if st.button("🔄 重新整理 (Refresh)"):
            st.rerun()
            
    # --- Data Loading & Filtering ---
    all_items = get_all_items()
    filtered_items = []
    
    for item in all_items:
        # 1. Filter by Grade
        rank = item.get('rarity_rank', 'B')
        if filter_grade != "All" and rank != filter_grade:
            continue
            
        # 2. Filter by Search Query
        q = search_query.lower()
        if q:
            text_corpus = (str(item['item_code']) + str(item['title']) + str(item['description_hero'])).lower()
            if q not in text_corpus:
                continue
        
        filtered_items.append(item)
    
    st.caption(f"顯示 {len(filtered_items)} / {len(all_items)} 筆資料")

    # --- Export Tools ---
    with st.expander("📤 匯出工具 (Export Tools)"):
        ec1, ec2 = st.columns(2)
        with ec1:
            # CSV Export
            csv_data = export_items_to_csv()
            st.download_button(
                label="📥 下載 CSV 報表",
                data=csv_data,
                file_name="jade_inventory_export.csv",
                mime="text/csv",
                use_container_width=True
            )
        with ec2:
            # PDF Export
            if st.button("📄 生成 PDF 目錄 (Generate Catalog)", use_container_width=True):
                try:
                    pdf_bytes = generate_pdf_catalog(filtered_items)
                    st.download_button(
                        label="📥 下載 PDF 目錄",
                        data=pdf_bytes,
                        file_name="jade_catalog.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"PDF Generation Failed: {e}")

    # --- Item List ---
    if not filtered_items:
        st.info("沒有符合條件的項目 (No items found).")
    else:
        for item in filtered_items:
            rank = item.get('rarity_rank', 'B')
            rank_info = grader.get_tier_info(rank)
            
            with st.expander(f"[{rank}級] {item['item_code']} - {item['title']}"):
                
                # Preview Toggle
                if st.checkbox(f"👁️ 預覽商品頁面 (Web Preview)", key=f"prev_{item['item_code']}"):
                    st.markdown("---")
                    st.markdown(f"### 🟢 {item['title']}")
                    st.caption(f"Ref: {item['item_code']}")
                    st.markdown(f"**等級評鑑:** :{rank_info['color']}[{rank}級 - {rank_info['name']}]")
                    
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