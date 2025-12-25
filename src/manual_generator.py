from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import logging

logger = logging.getLogger(__name__)

# Font Registration (Using same logic as pdf_generator)
try:
    pdfmetrics.registerFont(TTFont('MsJhengHei', 'msjh.ttc'))
    FONT_NAME = 'MsJhengHei'
except:
    FONT_NAME = 'Helvetica'

def generate_user_manual() -> bytes:
    """
    Generates a User Manual PDF for JadeScribe.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontName=FONT_NAME, fontSize=24, alignment=1, spaceAfter=20)
    h1_style = ParagraphStyle('H1', parent=styles['Heading2'], fontName=FONT_NAME, fontSize=16, spaceBefore=15, spaceAfter=10, textColor=colors.darkgreen)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontName=FONT_NAME, fontSize=11, leading=16)
    
    # Content
    story.append(Paragraph("JadeScribe 使用手冊", title_style))
    story.append(Paragraph("智能翡翠編目系統", ParagraphStyle('Sub', parent=body_style, alignment=1)))
    story.append(Spacer(1, 1*cm))
    
    # 1. Quick Start
    story.append(Paragraph("1. 快速開始 (Quick Start)", h1_style))
    story.append(Paragraph("歡迎使用 JadeScribe！本系統能協助您快速將翡翠拍照、辨識並建立數位檔案。", body_style))
    story.append(Paragraph("• 步驟一：將翡翠照片拖曳至「📸 影像上傳」區塊。", body_style))
    story.append(Paragraph("• 步驟二：點擊「🔍 開始辨識」按鈕。", body_style))
    story.append(Paragraph("• 步驟三：等待 AI 分析完成，查看生成的文案與評級。", body_style))
    
    # 2. Features
    story.append(Paragraph("2. 主要功能介紹", h1_style))
    story.append(Paragraph("<b>👁️ 智能視覺 (Vision):</b> 系統會自動找出圖片中的翡翠，並分析其顏色、種水與圖案。", body_style))
    story.append(Paragraph("<b>✍️ 文案生成 (Copywriting):</b> 自動產生三種風格（經典、現代、社群）的行銷文案。", body_style))
    story.append(Paragraph("<b>🏆 等級評鑑 (Grading):</b> 根據特徵自動給予參考評級（S級收藏、A級高貨、B級商業）。", body_style))
    
    # 3. Catalog & Export
    story.append(Paragraph("3. 編目與匯出", h1_style))
    story.append(Paragraph("在「📝 編目列表」分頁中，您可以：", body_style))
    story.append(Paragraph("• <b>搜尋：</b> 輸入關鍵字（如「觀音」）快速查找商品。", body_style))
    story.append(Paragraph("• <b>篩選：</b> 依照等級 (S/A/B) 過濾清單。", body_style))
    story.append(Paragraph("• <b>匯出：</b> 點擊「下載 CSV」或「生成 PDF 目錄」將資料存檔。", body_style))
    
    # 4. Troubleshooting
    story.append(Paragraph("4. 常見問題 (Q&A)", h1_style))
    story.append(Paragraph("<b>Q: 辨識速度很慢？</b><br/>A: 請在左側設定中關閉「🚀 啟用增強 OCR」。這會稍微降低文字讀取準確度，但大幅提升速度。", body_style))
    story.append(Paragraph("<b>Q: 找不到 AI 模型？</b><br/>A: 請確認 Ollama 程式已在背景執行，且網路連線正常。", body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
