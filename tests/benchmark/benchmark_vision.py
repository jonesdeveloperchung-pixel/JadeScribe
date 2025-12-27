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
TEST_IMAGES = [
    "images/IMG_6070.jpeg",  # A tray of jade pendants
    "images/processed/crop_1766657282_0.jpg" # A single cropped jade pendant
]

# Prompt for Benchmarking
PROMPT = """Analyze this image of jade pendants. 
1. Identify the 'item_code' (e.g., PA-XXXX_AF) if visible.
2. Identify the 'motif' (the carved figure, e.g., Buddha, Leaf, Dragon).
3. Describe the 'color' and 'texture'.

Return the result in JSON format:
{
  "items": [
    {
      "item_code": "...",
      "motif": "...",
      "color": "...",
      "texture": "..."
    }
  ]
}
"""

def get_vision_models(models_list_path: str) -> List[str]:
    """Returns a curated list of vision models for benchmarking."""
    # We want to compare these specifically
    return ["moondream:latest", "llama3.2-vision:latest", "llava:latest"]

# Initialize Client with a very long timeout for large vision models
client = ollama.Client(host="http://192.168.16.120:11434", timeout=300)

def unload_model(model: str):
    """Explicitly tells Ollama to unload a model from memory."""
    try:
        logger.info(f"Explicitly unloading model: {model}")
        client.generate(model=model, keep_alive=0)
    except Exception as e:
        logger.warning(f"Unload signal failed (expected): {e}")

def run_benchmark(model: str, image_path: str) -> Dict[str, Any]:
    """Runs a single benchmark test for a model and image."""
    logger.info(f"Testing model: {model} on {image_path}")
    
    start_time = time.time()
    
    try:
        # Use a more descriptive prompt that helps models understand it's a tray/grid
        tray_context = "This is a grid display tray of jade pendants. Please analyze all items visible." if "IMG_6070" in image_path else ""
        
        response = client.chat(
            model=model,
            messages=[{
                'role': 'user',
                'content': f"{tray_context}\n{PROMPT}",
                'images': [image_path]
            }],
            options={'temperature': 0},
            keep_alive=0 # Suggest unload after response
        )
        
        end_time = time.time()
        
        duration = end_time - start_time
        content = response['message']['content']
        
        # After testing, force another unload just to be safe
        unload_model(model)
        
        return {
            "model": model,
            "image": image_path,
            "duration_s": round(duration, 2),
            "response_length": len(content),
            "success": True,
            "output": content[:200] + "..." if len(content) > 200 else content
        }
    except Exception as e:
        logger.error(f"Error testing {model}: {e}")
        return {
            "model": model,
            "image": image_path,
            "success": False,
            "error": str(e)
        }

def main():
    models_file = "resources/my_llms.txt"
    vision_models = get_vision_models(models_file)
    
    logger.info(f"Starting benchmark for models: {vision_models}")
    
    results = []
    for image in TEST_IMAGES:
        if not os.path.exists(image):
            logger.warning(f"Image not found: {image}")
            continue
            
        for model in vision_models:
            res = run_benchmark(model, image)
            results.append(res)
            
            # Substantial delay to allow OS to reclaim VRAM/RAM
            logger.info("Waiting 20 seconds for Ollama server to reclaim memory...")
            time.sleep(20)

    # Save results
    output_file = "tests/benchmark/results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Benchmark complete. Results saved to {output_file}")
    
    # Print Summary Table
    print("\n" + "="*80)
    print(f"{ 'Model':<30} | {'Image':<20} | {'Time (s)':<10} | {'Status'}")
    print("-" * 80)
    for r in results:
        status = "✅" if r["success"] else "❌"
        img_name = os.path.basename(r["image"])
        print(f"{r['model']:<30} | {img_name:<20} | {r.get('duration_s', 'N/A'):<10} | {status}")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
