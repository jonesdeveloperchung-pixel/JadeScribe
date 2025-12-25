import cv2
import numpy as np
import re
import os
import logging
import time
from PIL import Image

# Configure Logging
logger = logging.getLogger(__name__)

# Global variable for lazy loading
_reader = None

def get_reader():
    """Lazy loads EasyOCR reader only when requested."""
    global _reader
    if _reader is None:
        try:
            import easyocr
            logger.info("Initializing EasyOCR (Lazy Load)...")
            _reader = easyocr.Reader(['en'], gpu=False)
            logger.info("EasyOCR initialized successfully.")
        except ImportError:
            logger.error("EasyOCR module not found.")
            _reader = False # Sentinel for failure
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            _reader = False
    return _reader

class ImageProcessor:
    def __init__(self, output_dir="images/processed"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def apply_white_balance(self, img):
        """
        Applies Gray World White Balance to correct lighting color casts.
        """
        result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        avg_a = np.average(result[:, :, 1])
        avg_b = np.average(result[:, :, 2])
        result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
        result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)
        result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
        return result

    def apply_clahe(self, img):
        """
        Applies CLAHE (Contrast Limited Adaptive Histogram Equalization)
        to bring out texture details in jade.
        """
        # Convert to LAB to only enhance Luminance channel
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L-channel
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        
        # Merge back
        limg = cv2.merge((cl, a, b))
        final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        return final

    def clean_item_code(self, raw_text):
        """
        Cleans OCR output using Regex to match strict pattern.
        Target Format: PA-0425_AF (Example)
        Common Fixes: O->0, I->1, S->5
        """
        if not raw_text:
            return None
            
        text = raw_text.upper().replace(" ", "").strip()
        
        # 1. Simple replacements for common OCR errors
        # (This is heuristic and might need tuning based on specific label fonts)
        text = text.replace("O", "0").replace("I", "1")
        
        # 2. Strict Pattern Matching
        # Looking for Pattern: 2 Letters - 4 Digits [Optional Suffix]
        # Example: PA-0425, PA0425, PA-0425_AF
        
        # Try finding the core ID first (XX-DDDD)
        match = re.search(r'([A-Z]{2})[-_]?(\d{3,4})', text)
        if match:
            # Reconstruct standardized format
            prefix = match.group(1)
            number = match.group(2)
            
            # Look for suffix (e.g., _AF)
            suffix_match = re.search(r'[A-Z]{2}$', text)
            suffix = f"_{suffix_match.group(0)}" if suffix_match and suffix_match.group(0) != prefix else ""
            
            return f"{prefix}-{number}{suffix}"
            
        return None # Return None if no valid code pattern found

    def segment_and_crop(self, image_path, enable_ocr=True):
        """
        Detects individual pendants in a tray, crops them, enhances them,
        and saves them for analysis.
        
        Args:
            image_path: Path to source image.
            enable_ocr: If True, runs EasyOCR on crops. If False, skips OCR (Faster).
        
        Returns: List of dicts {'path': str, 'code': str}
        """
        original_img = cv2.imread(image_path)
        if original_img is None:
            logger.error(f"Could not read image: {image_path}")
            return []

        # 1. Pre-processing for Contours
        gray = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # Adaptive thresholding to handle uneven lighting on the tray
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY_INV, 19, 3)

        # 2. Find Contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detected_items = []
        item_count = 0
        
        img_h, img_w = original_img.shape[:2]
        min_area = (img_w * img_h) * 0.02 # Filter out noise (< 2% of image)

        # Lazy load reader only if needed
        ocr_reader = None
        if enable_ocr:
            ocr_reader = get_reader()

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < min_area:
                continue

            # Get Bounding Box
            x, y, w, h = cv2.boundingRect(cnt)
            
            # Add padding
            padding = 20
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(img_w - x, w + 2*padding)
            h = min(img_h - y, h + 2*padding)
            
            # Crop
            crop = original_img[y:y+h, x:x+w]
            
            if crop.size == 0:
                continue

            # 3. Enhance Crop (Zoom-In Analysis Prep)
            # Apply WB then CLAHE
            enhanced_crop = self.apply_white_balance(crop)
            enhanced_crop = self.apply_clahe(enhanced_crop)
            
            # Save Crop
            item_filename = f"crop_{int(time.time())}_{item_count}.jpg"
            save_path = os.path.join(self.output_dir, item_filename)
            cv2.imwrite(save_path, enhanced_crop)
            
            # 4. Run Specialized OCR on this specific crop
            detected_code = "Unknown"
            if enable_ocr and ocr_reader:
                try:
                    ocr_results = ocr_reader.readtext(crop, detail=0) # Use unenhanced crop for OCR sometimes better?
                    # Concatenate all found text and try to find code
                    full_text = "".join(ocr_results)
                    cleaned = self.clean_item_code(full_text)
                    if cleaned:
                        detected_code = cleaned
                    else:
                        # Fallback: Try OCR on enhanced crop
                        ocr_results_enh = ocr_reader.readtext(enhanced_crop, detail=0)
                        full_text_enh = "".join(ocr_results_enh)
                        cleaned_enh = self.clean_item_code(full_text_enh)
                        if cleaned_enh:
                            detected_code = cleaned_enh
                except Exception as e:
                    logger.warning(f"OCR failed for crop {item_count}: {e}")

            detected_items.append({
                "crop_path": save_path,
                "ocr_code": detected_code
            })
            item_count += 1
            
        return detected_items

import time
