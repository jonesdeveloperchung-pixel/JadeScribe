import ollama
import time
import json
import os
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
REMOTE_HOST = "http://192.168.16.90:11434"
TEST_IMAGES = [
    "images/processed/crop_1766657282_0.jpg"
]

# Prompt
PROMPT = "Analyze this jade pendant. Identify the motif and color. Return JSON: {'motif': '...', 'color': '...'}"

def main():
    logger.info(f"Checking remote host: {REMOTE_HOST}")
    client = ollama.Client(host=REMOTE_HOST)
    
    try:
        # Check connectivity and models
        models_resp = client.list()
        
        # Handle different response formats (model vs name)
        models = []
        for m in models_resp.get('models', []):
            name = m.get('model') or m.get('name')
            if name:
                models.append(name)
                
        logger.info(f"Connected! Remote models: {models}")
        
        vision_models = [m for m in models if "vision" in m or "llava" in m or "moondream" in m]
        if not vision_models:
            logger.warning("No vision models found on remote server.")
            return

        results = []
        for model in vision_models[:3]: # Test up to 3 models
            for img in TEST_IMAGES:
                logger.info(f"Benchmarking {model} on {img}...")
                start = time.time()
                try:
                    res = client.chat(model=model, messages=[{'role': 'user', 'content': PROMPT, 'images': [img]}])
                    duration = time.time() - start
                    results.append({
                        "model": model,
                        "duration_s": round(duration, 2),
                        "success": True,
                        "output": res['message']['content'][:100]
                    })
                except Exception as e:
                    results.append({"model": model, "success": False, "error": str(e)})

        print("\n=== Remote Benchmark Results ===")
        for r in results:
            status = "✅" if r["success"] else "❌"
            print(f"{r['model']:<30} | {r.get('duration_s', 'N/A'):<10} | {status}")
            
    except Exception as e:
        logger.error(f"Could not connect to remote host: {e}")

if __name__ == "__main__":
    main()
