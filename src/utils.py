import requests
import logging
import os
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_ollama_status(base_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Check if the Ollama service is running and accessible.
    
    Args:
        base_url (str, optional): The base URL of the Ollama API. 
                                  Defaults to OLLAMA_HOST env var or http://localhost:11434.

    Returns:
        Dict[str, Any]: A dictionary containing status, message, and details.
            {
                "running": bool,
                "message": str,
                "model_count": int (optional),
                "error_details": str (optional)
            }
    """
    if base_url is None:
        base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    try:
        logger.info(f"Checking Ollama status at: {base_url}")
        
        # Using a longer timeout (5s) to avoid flakes on busy systems
        response = requests.get(f"{base_url}/api/tags", timeout=5.0)
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Handle both old and new Ollama API formats
                if "models" in data:
                    model_count = len(data.get("models", []))
                else:
                    model_count = len(data)
                
                return {
                    "running": True,
                    "message": f"Ollama 服務運作中 (已安裝 {model_count} 個模型)",
                    "model_count": model_count
                }
            except ValueError as json_err:
                return {
                    "running": True,
                    "message": "Ollama 服務運作中，但回傳資料格式錯誤",
                    "error_details": str(json_err)
                }
        else:
            return {
                "running": False,
                "message": f"Ollama 服務回傳錯誤代碼: {response.status_code}",
                "status_code": response.status_code
            }

    except requests.exceptions.ConnectionError:
        return {
            "running": False,
            "message": f"無法連接到 Ollama 服務 ({base_url})。請確認 IP 正確且防火牆已開啟。",
            "error_type": "connection_error"
        }
    except requests.exceptions.Timeout:
        return {
            "running": False,
            "message": "連接 Ollama 服務逾時 (Timeout)。",
            "error_type": "timeout"
        }
    except Exception as e:
        return {
            "running": False,
            "message": f"檢查 Ollama 狀態時發生未預期的錯誤: {str(e)}",
            "error_type": "exception",
            "error_details": str(e)
        }

def get_ollama_models(base_url: Optional[str] = None) -> list:
    """
    Retrieves a list of available model names from Ollama.
    """
    if base_url is None:
        base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            # Return list of model names (e.g., 'llama3.2-vision:latest')
            return [m.get("name") for m in models]
    except Exception as e:
        logger.error(f"Failed to fetch models: {e}")
    return []

def check_model_availability(model_name: str, base_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Checks if a specific model is available in the local Ollama instance.
    """
    available_models = get_ollama_models(base_url)
    
    # Exact match check
    is_available = model_name in available_models
    
    return {
        "available": is_available,
        "message": f"✅ 模型 '{model_name}' 已就緒" if is_available else f"⚠️ 未找到模型 '{model_name}'"
    }

def is_chinese(text: str) -> bool:
    """
    Check if the text contains Chinese characters.
    """
    for char in text:
        if "\u4e00" <= char <= "\u9fff":
            return True
    return False

def get_default_model_config() -> Dict[str, str]:
    """
    Returns the project's safe default model configuration.
    """
    return {
        "vision_model": os.getenv("VISION_MODEL", "llama3.2-vision:latest"),
        "text_model": os.getenv("TEXT_MODEL", "gemma3n:e4b"), 
        "embedding_model": "nomic-embed-text:latest",
        "base_url": os.getenv("OLLAMA_HOST", "http://localhost:11434")
    }
