import re
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import pytesseract
from typing import Optional, Tuple

class OCRService:
    @staticmethod
    def preprocess_image(image_bytes: bytes) -> np.ndarray:
        """Preprocess image for better OCR accuracy."""
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray, None, h=10)

        # Apply thresholding
        _, thresh = cv2.threshold(denoised, 150, 255, cv2.THRESH_BINARY)

        # Dilate and erode to improve text clarity
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        return processed

    @staticmethod
    def extract_text_with_confidence(image_bytes: bytes) -> Tuple[str, float]:
        """Extract text from image using Tesseract with confidence score."""
        try:
            processed_img = OCRService.preprocess_image(image_bytes)

            # Extract text using Thai and English language data
            data = pytesseract.image_to_data(
                processed_img,
                lang='tha+eng',
                output_type=pytesseract.Output.DICT,
                config='--psm 6'
            )

            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            avg_confidence = min(avg_confidence / 100, 1.0)  # Normalize to 0-1

            # Extract text
            text = '\n'.join(data['text'])

            return text, avg_confidence
        except Exception as e:
            raise Exception(f"OCR failed: {str(e)}")

    @staticmethod
    def redact_thai_id_numbers(text: str) -> str:
        """Redact 13-digit Thai ID numbers from text."""
        # Thai ID numbers are 13 digits
        pattern = r'\d{13}'
        redacted = re.sub(pattern, '[REDACTED_ID]', text)
        return redacted

    @staticmethod
    def extract_thai_names(ocr_text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract Thai first name and surname from OCR text.
        This is a simplified implementation - can be improved with ML models.
        """
        # Remove ID numbers first
        text = OCRService.redact_thai_id_numbers(ocr_text)

        # Clean up whitespace and special characters
        text = text.strip()
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        first_name = None
        last_name = None

        # Look for Thai text (very simplified heuristic)
        # In real implementation, would use Thai language processing
        thai_words = []
        for line in lines:
            # Filter lines that look like they contain names (Thai characters)
            # Thai characters are in Unicode range 0x0E00-0x0E7F
            if any('฀' <= char <= '๿' for char in line):
                thai_words.append(line)

        # If we have Thai words, assume first is first name, second is last name
        if len(thai_words) >= 2:
            first_name = thai_words[0]
            last_name = thai_words[1]
        elif len(thai_words) == 1:
            first_name = thai_words[0]

        return first_name, last_name
