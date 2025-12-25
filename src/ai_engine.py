import ollama
import json
import logging
import time
import os
import re
from typing import Dict, Any, Optional, List
from db_manager import log_telemetry
from utils import check_ollama_status
from vision_utils import ImageProcessor

# Configure Logging
logger = logging.getLogger(__name__)

# Constants
VISION_MODEL = os.getenv("VISION_MODEL", "llama3.2-vision:latest")
TEXT_MODEL = os.getenv("TEXT_MODEL", "gemma3n:e4b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Initialize Client explicitly to avoid localhost resolution issues
client = ollama.Client(host=OLLAMA_HOST)

# Initialize Image Processor
processor = ImageProcessor()

# Load Symbolism Glossary
GLOSSARY_PATH = os.path.join("data", "symbolism_glossary.json")
SYMBOLISM_GLOSSARY = {}
try:
    with open(GLOSSARY_PATH, 'r', encoding='utf-8') as f:
        SYMBOLISM_GLOSSARY = json.load(f)
    logger.info("Symbolism glossary loaded successfully.")
except FileNotFoundError:
    logger.error(f"Symbolism glossary not found at {GLOSSARY_PATH}. Descriptions may be generic.")
except json.JSONDecodeError:
    logger.error(f"Error decoding symbolism glossary at {GLOSSARY_PATH}. Descriptions may be generic.")


def _get_symbolism_context(motif: str, color: str) -> str:
    """
    Retrieves symbolism context from the loaded glossary based on detected features.
    """
    context_parts = []

    # Motif symbolism
    if motif and motif.lower() in SYMBOLISM_GLOSSARY.get("motifs", {}):
        motif_entry = SYMBOLISM_GLOSSARY["motifs"][motif.lower()]
        context_parts.append(f"圖案「{motif_entry['name'].split(' ')[0]}」象徵著：{motif_entry['meaning']}")
    
    # Color characteristics
    if color and color.lower() in SYMBOLISM_GLOSSARY.get("colors", {}):
        color_entry = SYMBOLISM_GLOSSARY["colors"][color.lower()]
        context_parts.append(f"此翡翠的顏色為「{color_entry.split(' ')[0]}」，其特色是：{color_entry.split(' - ')[1]}")

    if context_parts:
        return "\n".join(context_parts)
    return ""

def clean_json_output(text: str) -> str:
    """
    Extracts the JSON-like substring from the text, removing Markdown code blocks.
    """
    # 1. Remove markdown code blocks ```json ... ``` or ``` ... ```
    text = re.sub(r'```json\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'```\s*', '', text)
    
    # 2. Find first [ or { and last ] or } to handle extra text around JSON
    # Try finding an Array
    list_match = re.search(r'\[.*\]', text, re.DOTALL)
    if list_match:
        return list_match.group(0)
    
    # Try finding an Object
    obj_match = re.search(r'\{.*\}', text, re.DOTALL)
    if obj_match:
        return obj_match.group(0)
        
    return text.strip()

def safe_chat_call(model, messages, options=None, format=None, retries=2):
    """
    Wraps client.chat with retry logic for network stability.
    """
    attempt = 0
    last_error = None
    
    while attempt <= retries:
        try:
            return client.chat(
                model=model,
                messages=messages,
                options=options,
                format=format
            )
        except Exception as e:
            last_error = e
            logger.warning(f"Ollama Call Failed (Attempt {attempt+1}/{retries+1}): {e}")
            attempt += 1
            time.sleep(1) # Wait 1s before retry
            
    raise last_error

def analyze_single_crop(image_path: str, ocr_code: str = "Unknown") -> Dict[str, Any]:
    """
    Analyzes a single cropped image with "Gemologist" Chain-of-Thought prompting.
    """
    prompt = f"""
    You are a professional Gemologist analyzing a high-resolution close-up of a Jade Pendant.
    
    Detected Item Code from Label: "{ocr_code}" (If "Unknown", try to read it from the image).

    Perform a "Zoom-In" Analysis:
    1. Transparency: Is it Opaque, Translucent (Waxy/Sticky), or Transparent (Icy/Glassy)?
    2. Texture: Describe the grain. Fine, coarse, or oily?
    3. Color: Describe the primary color and any floating flowers (piao hua).
    4. Motif: Identify the carved figure (e.g., Buddha, Leaf, Dragon).
    
    Return a JSON Object:
    {{
        "item_code": "{ocr_code if ocr_code != "Unknown" else "READ_FROM_IMAGE"}",
        "visual_features": {{
            "color": "...",
            "motif": "...",
            "characteristics": "Combine transparency and texture here..."
        }}
    }}
    """
    
    try:
        response = safe_chat_call(
            model=VISION_MODEL,
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [image_path]
            }],
            format='json',
            options={'temperature': 0.1}
        )
        
        content = response['message']['content']
        cleaned = clean_json_output(content)
        result = json.loads(cleaned)
        
        # Merge EasyOCR code if Vision model failed to read it or returned placeholder
        if ocr_code != "Unknown":
            result["item_code"] = ocr_code
            
        return result
    except Exception as e:
        logger.error(f"Crop analysis failed: {e}")
        return {
            "item_code": ocr_code,
            "visual_features": {
                "color": "Analysis Failed", 
                "motif": "Unknown", 
                "characteristics": "Error"
            }
        }

def analyze_image_content(image_path: str, enable_ocr: bool = True) -> List[Dict[str, Any]]:
    """
    Analyzes an image using a Hybrid Pipeline:
    1. Computer Vision Segmentation (Crops) + EasyOCR (Optional)
    2. AI Vision Analysis on Crops
    """
    start_time = time.time()
    
    # 1. Check Service
    status = check_ollama_status(base_url=OLLAMA_HOST)
    if not status["running"]:
        return [{"error": f"Ollama service is not running or accessible at {OLLAMA_HOST}."}]

    logger.info(f"Analyzing image: {image_path} (OCR Enabled: {enable_ocr})")
    
    # 2. Attempt Segmentation & Crop
    try:
        detected_crops = processor.segment_and_crop(image_path, enable_ocr=enable_ocr)
    except Exception as e:
        logger.error(f"Segmentation failed: {e}")
        detected_crops = []

    results = []

    # 3. Process Crops (Zoom-In Analysis)
    if detected_crops:
        logger.info(f"Segmentation found {len(detected_crops)} items. Running Zoom-In Analysis.")
        for item in detected_crops:
            crop_path = item["crop_path"]
            ocr_code = item["ocr_code"]
            
            # Analyze
            crop_result = analyze_single_crop(crop_path, ocr_code)
            
            # Add file path to result so UI can display the crop
            crop_result["crop_path"] = crop_path 
            results.append(crop_result)
            
    else:
        # 4. Fallback: Full Image Analysis (Old Method)
        logger.warning("No items segmented. Falling back to full image analysis.")
        prompt = """
        Analyze this image of jade pendants. Return a JSON ARRAY of items found.
        Extract Item Code and Visual Features (Color, Motif, Texture).
        """
        try:
            response = safe_chat_call(
                model=VISION_MODEL,
                messages=[{'role': 'user', 'content': prompt, 'images': [image_path]}],
                format='json',
                options={'temperature': 0.1}
            )
            content = response['message']['content']
            results = json.loads(clean_json_output(content))
            if isinstance(results, dict): results = [results]
        except Exception as e:
             return [{"error": str(e)}]

    duration = (time.time() - start_time) * 1000
    log_telemetry(
        module="ai_engine",
        action="analyze_image_hybrid",
        execution_data={"duration_ms": duration, "exit_code": 0, "items_found": len(results)},
        args=[image_path]
    )
    
    return results

def generate_marketing_copy(features: Dict[str, Any]) -> Dict[str, str]:
    """
    Generates three styles of Traditional Chinese descriptions:
    1. Hero (Poetic/Classical)
    2. Modern (E-commerce/Benefit-focused)
    3. Social (Short/Hashtags)
    """
    start_time = time.time()
    
    motif = features.get('visual_features', {}).get('motif', 'Unknown')
    color = features.get('visual_features', {}).get('color', 'Unknown')
    characteristics = features.get('visual_features', {}).get('characteristics', 'Unknown')
    
    # Get symbolism context
    symbolism_context = _get_symbolism_context(motif, color)
    symbolism_section = f"文化寓意參考: {symbolism_context}" if symbolism_context else ""
    
    # Construct the Prompt
    prompt = f"""
    您是一位專業的高端翡翠珠寶文案撰寫專家，精通台灣市場的語言習慣。
    物件詳細資料：
    - 主題: {motif}
    - 顏色: {color}
    - 特性: {characteristics}
    {symbolism_section}
    
    任務：請生成三種不同風格的文案，必須使用「繁體中文（台灣）」且「確保完全不使用簡體字」。
    請嚴格遵守 JSON 格式回傳，包含以下三個鍵： "hero", "modern", "social"。
    
    1. "hero" (經典敘事)：優雅、深邃、高端畫冊風格（約 100-150 字）。著重於藝術感、歷史傳承與文化寓意。使用優美的修辭，如「溫潤如玉」、「歷久彌新」。
    2. "modern" (現代電商)：直觀、專業、功能導向。使用清單或短句描述材質、光澤及佩戴感。適合官網商品詳情。
    3. "social" (社群貼文)：活潑、具吸引力的社群媒體風格（如 Instagram 或 Threads）。字數簡潔，包含 3-5 個相關 Emoji 和 Hashtags。
    
    輸出 JSON 格式範例：
    {{
        "hero": "玉色如君子之心...",
        "modern": "材質：天然翡翠...",
        "social": "🐾 超可愛的翡翠小萌物..."
    }}
    """
    
    try:
        # Call with Retry
        response = safe_chat_call(
            model=TEXT_MODEL,
            messages=[{'role': 'user', 'content': prompt}],
            format='json',
            options={'temperature': 0.7}
        )
        
        content = response['message']['content']
        
        try:
            cleaned_content = clean_json_output(content)
            descriptions = json.loads(cleaned_content)
            
            # Defensive check for keys
            for key in ["hero", "modern", "social"]:
                if key not in descriptions:
                    descriptions[key] = "生成不完整 (Generation Incomplete)"
                    
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse Copy JSON. Raw: {content}")
            descriptions = {
                "hero": content,
                "modern": "格式錯誤 (Format Error)",
                "social": "格式錯誤 (Format Error)"
            }

        duration = (time.time() - start_time) * 1000
        log_telemetry(
            module="ai_engine",
            action="generate_marketing_copy",
            execution_data={"duration_ms": duration, "exit_code": 0}
        )
        
        return descriptions

    except Exception as e:
        duration = (time.time() - start_time) * 1000
        logger.error(f"Copy Generation Failed: {e}")
        log_telemetry(
            module="ai_engine",
            action="generate_marketing_copy",
            execution_data={"duration_ms": duration, "exit_code": 1, "error": str(e)}
        )
        return {
            "hero": "生成失敗 (Generation Failed)",
            "modern": "",
            "social": ""
        }

