import ollama
import json
import logging
import time
import os
from typing import Dict, Any, Optional
from db_manager import log_telemetry
from utils import check_ollama_status

# Configure Logging
logger = logging.getLogger(__name__)

# Constants
VISION_MODEL = os.getenv("VISION_MODEL", "llama3.2-vision:latest")
TEXT_MODEL = os.getenv("TEXT_MODEL", "gemma3n:e4b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Initialize Client explicitly to avoid localhost resolution issues
client = ollama.Client(host=OLLAMA_HOST)

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


def analyze_image_content(image_path: str) -> Dict[str, Any]:
    """
    Analyzes an image using Ollama Vision to extract item codes and visual features.
    """
    start_time = time.time()
    
    # 1. Check Service
    status = check_ollama_status(base_url=OLLAMA_HOST)
    if not status["running"]:
        return {"error": f"Ollama service is not running or accessible at {OLLAMA_HOST}."}

    logger.info(f"Analyzing image: {image_path} with {VISION_MODEL}")
    
    # 2. Construct Prompt for Vision Model
    # We ask for a structured JSON response to make parsing easier.
    prompt = """
    Analyze this image of a jade pendant. 
    1. Identify any text labels or item codes (e.g., PA-0425_AF).
    2. Describe the visual features:
       - Color (e.g., Imperial Green, Lavender, White, Oil Green)
       - Motif/Subject (e.g., Guanyin, Bamboo, Dragon, Lotus, Pixiu, Coin, Peach, Gourd)
       - Texture/Translucency (e.g., Icy, Waxy, Fine, Coarse, Transparent, Opaque)
    
    Return the result strictly as a valid JSON object with the following keys. Ensure motif and color match the provided examples or similar common terms.
    {
        "item_code": "detected_code_or_unknown",
        "visual_features": {
            "color": "description",
            "motif": "description",
            "characteristics": "description"
        }
    }
    """

    try:
        # 3. Call Ollama Vision API
        response = client.chat(
            model=VISION_MODEL,
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [image_path]
            }],
            format='json', # Force JSON output
            options={'temperature': 0.1} # Low temp for factual extraction
        )
        
        content = response['message']['content']
        logger.debug(f"Vision Model Raw Output: {content}")
        
        # 4. Parse Result
        try:
            result_json = json.loads(content)
        except json.JSONDecodeError:
            # Fallback: simple text extraction if JSON fails
            logger.warning("Failed to parse JSON from Vision model. Attempting to extract from raw text.")
            # Simple regex/keyword extraction might be needed here for robustness
            result_json = {"item_code": "Unknown", "visual_features": {"color": "Unknown", "motif": "Unknown", "characteristics": content[:200]}} # Truncate for log
            log_telemetry(
                module="ai_engine",
                action="analyze_image",
                execution_data={"duration_ms": duration, "exit_code": 1, "error": "JSON_PARSE_ERROR"},
                context={"raw_output": content},
                args=[image_path]
            )
            return result_json # Return partial result with error

        duration = (time.time() - start_time) * 1000
        
        # 5. Log Telemetry
        log_telemetry(
            module="ai_engine",
            action="analyze_image",
            execution_data={"duration_ms": duration, "exit_code": 0},
            args=[image_path]
        )
        
        return result_json

    except Exception as e:
        duration = (time.time() - start_time) * 1000
        logger.error(f"AI Analysis Failed: {e}")
        
        log_telemetry(
            module="ai_engine",
            action="analyze_image",
            execution_data={"duration_ms": duration, "exit_code": 1, "error": str(e)},
            args=[image_path]
        )
        return {"error": str(e)}

def generate_poetic_description(features: Dict[str, Any]) -> str:
    """
    Generates a Traditional Chinese poetic description based on visual features,
    incorporating symbolism from the glossary.
    """
    start_time = time.time()
    
    motif = features.get('visual_features', {}).get('motif', 'Unknown')
    color = features.get('visual_features', {}).get('color', 'Unknown')
    characteristics = features.get('visual_features', {}).get('characteristics', 'Unknown')
    
    # Get symbolism context
    symbolism_context = _get_symbolism_context(motif, color)
    
    # Construct symbolism section for the prompt
    symbolism_section = ""
    if symbolism_context:
        symbolism_section = (
            "以下是與此翡翠相關的文化寓意，請巧妙地融入描述中：\n"
            f"{symbolism_context}"
        )
    
    # Construct the full prompt using str.format() for robustness
    prompt_template = """
    您是一位經驗豐富的高端翡翠珠寶文案撰寫人。
    請為以下特徵的翡翠吊墜撰寫一篇精緻、富有詩意且優雅的繁體中文描述：
    
    - 圖案: {motif}
    - 顏色: {color}
    - 特性: {characteristics}
    
    {symbolism_section}
    
    要求：
    1. 語氣：沉靜、高端、永恆。
    2. 長度：80-120字。
    3. 如果有相關的文化寓意，請優雅地融入其中。
    4. 請勿提及任何價格或等級保證。
    5. 僅輸出描述文本。
    """
    
    prompt = prompt_template.format(
        motif=motif,
        color=color,
        characteristics=characteristics,
        symbolism_section=symbolism_section
    )
    
    try:
        response = client.chat(
            model=TEXT_MODEL,
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.7} # Higher temp for creativity
        )
        
        description = response['message']['content']
        
        duration = (time.time() - start_time) * 1000
        log_telemetry(
            module="ai_engine",
            action="generate_description",
            execution_data={"duration_ms": duration, "exit_code": 0}
        )
        
        return description.strip()

    except Exception as e:
        duration = (time.time() - start_time) * 1000
        logger.error(f"Description Generation Failed: {e}")
        log_telemetry(
            module="ai_engine",
            action="generate_description",
            execution_data={"duration_ms": duration, "exit_code": 1, "error": str(e)}
        )
        return "（無法生成描述 / Description Generation Failed）"

