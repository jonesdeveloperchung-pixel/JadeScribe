import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import logging
import os

# Configure Logging
logger = logging.getLogger(__name__)

# Register a Font that supports Chinese (Microsoft JhengHei usually available on Win, or Noto)
# For portability in this environment, we'll check for a system font or fallback to basic.
# NOTE: In a real deploy, you should ship a .ttf file in /resources.
try:
    # Attempt to load a common Windows Traditional Chinese font
    pdfmetrics.registerFont(TTFont('MsJhengHei', 'msjh.ttc')) # Windows standard
    FONT_NAME = 'MsJhengHei'
except:
    try:
        # Linux/Mac fallback (Noto Sans CJK) - path varies, often not found without config
        # For this prototype, we will warn if we can't find a Chinese font.
        logger.warning("Chinese Font not found. PDF may not render characters correctly.")
        FONT_NAME = 'Helvetica' # Standard built-in (No Chinese support)
    except:
        FONT_NAME = 'Helvetica'

def generate_pdf_catalog(items: list) -> bytes:
    """
    Generates a PDF catalog from the list of items.
    Returns the PDF bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=1*cm, leftMargin=1*cm,
                            topMargin=1*cm, bottomMargin=1*cm)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    style_title = ParagraphStyle(
        'JadeTitle',
        parent=styles['Heading1'],
        fontName=FONT_NAME,
        fontSize=24,
        alignment=1, # Center
        spaceAfter=12
    )
    
    style_item_title = ParagraphStyle(
        'ItemTitle',
        parent=styles['Heading2'],
        fontName=FONT_NAME,
        fontSize=14,
        textColor=colors.darkgreen
    )
    
    style_body = ParagraphStyle(
        'ItemBody',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10,
        leading=14
    )
    
    style_meta = ParagraphStyle(
        'ItemMeta',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=9,
        textColor=colors.gray
    )

    # 1. Cover Page
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("翠藝錄 (JadeScribe)", style_title))
    story.append(Paragraph("典藏目錄 Catalog", style_title))
    story.append(Spacer(1, 1*cm))
    # Add a line
    story.append(Paragraph("_" * 50, style_title))
    story.append(Spacer(1, 2*cm))

    # 2. Item List
    for i, item in enumerate(items):
        # Create a visual block for each item
        # Layout: Image (Left) | Text Info (Right)
        
        # Image Handling (Placeholder for now as we don't track crop paths in DB yet perfectly)
        # We will use a spacer or a generic logo if image path is missing
        # In v1.2, we assume we want to just list text details cleanly.
        
        # Determine Rarity Color
        rank = item.get('rarity_rank', 'B')
        rank_text = f"【{rank}級】"
        if rank == 'S': rank_color = colors.gold
        elif rank == 'A': rank_color = colors.silver
        else: rank_color = colors.brown
        
        # Item Title
        title_text = f"{item['item_code']} - {item['title']}"
        story.append(Paragraph(title_text, style_item_title))
        
        # Rarity Badge (Simulated with text color for now)
        story.append(Paragraph(f"<b>等級 (Grade): {rank}</b>", style_body))
        
        # Description
        story.append(Paragraph(item['description_hero'], style_body))
        story.append(Spacer(1, 0.2*cm))
        
        # Meta
        updated = item.get('updated_at', '')
        story.append(Paragraph(f"Last Updated: {updated}", style_meta))
        
        # Divider
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("_" * 80, style_meta))
        story.append(Spacer(1, 0.5*cm))
        
        # Page break every 4 items
        if (i + 1) % 4 == 0:
            story.append(Spacer(1, 2*cm)) # Or PageBreak()

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
