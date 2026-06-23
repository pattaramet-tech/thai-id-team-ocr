import re
import cv2
import numpy as np
from datetime import datetime, date
from io import BytesIO
import pytesseract
from typing import Optional, Tuple, Dict, List

class OCRService:
    @staticmethod
    def preprocess_image(image_bytes: bytes) -> np.ndarray:
        """Preprocess image for better OCR accuracy."""
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray, None, h=10)
        _, thresh = cv2.threshold(denoised, 150, 255, cv2.THRESH_BINARY)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        return processed

    @staticmethod
    def extract_text_with_confidence(image_bytes: bytes) -> Tuple[str, float]:
        """Extract text from image using Tesseract with confidence score."""
        try:
            processed_img = OCRService.preprocess_image(image_bytes)

            data = pytesseract.image_to_data(
                processed_img,
                lang='tha+eng',
                output_type=pytesseract.Output.DICT,
                config='--psm 6'
            )

            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            avg_confidence = min(avg_confidence / 100, 1.0)

            text = '\n'.join(data['text'])
            return text, avg_confidence
        except Exception as e:
            raise Exception(f"OCR failed: {str(e)}")

    @staticmethod
    def redact_thai_id_numbers(text: str) -> str:
        """
        Redact 13-digit Thai ID numbers from text.
        Handles patterns like:
        - 1234567890123
        - 1 2345 67890 12 3
        - 1-2345-67890-12-3
        """
        # Pattern 1: Consecutive 13 digits
        text = re.sub(r'\d{13}', '[REDACTED_ID]', text)

        # Pattern 2: Digits with spaces (1 2345 67890 12 3)
        text = re.sub(r'\d\s+\d\s+\d\s+\d\s+\d', lambda m: '[REDACTED_ID]' if len(re.sub(r'\D', '', m.group())) >= 13 else m.group(), text)

        # Pattern 3: Digits with dashes (1-2345-67890-12-3)
        text = re.sub(r'\d-\d+-\d+-\d+-\d+', lambda m: '[REDACTED_ID]' if len(re.sub(r'\D', '', m.group())) >= 13 else m.group(), text)

        # Pattern 4: Mixed spaces and dashes with exactly 13 digits
        text = re.sub(r'(?:\d[\s-]?){12}\d', lambda m: '[REDACTED_ID]' if len(re.sub(r'\D', '', m.group())) == 13 else m.group(), text)

        return text

    @staticmethod
    def _is_noise_word(word: str) -> bool:
        """Check if word is likely document noise, not a name."""
        noise_keywords = {
            'บัตร', 'ประจำตัว', 'ประชาชน', 'เลข', 'เกิด', 'วันที่', 'ชื่อ',
            'นามสกุล', 'สัญชาติ', 'สถานที่', 'ที่อยู่', 'id', 'card', 'name',
            'birth', 'date', 'thai', 'national', 'copy', 'สำเนา', 'บ้าน',
            'เบอร์', 'หมายเลข', 'ลงชื่อ', 'ผู้', 'องค์', 'การ', 'ระบบ'
        }
        word_lower = word.lower()
        return word_lower in noise_keywords or len(word) < 2

    @staticmethod
    def _extract_from_labeled_lines(lines: List[str]) -> Tuple[Optional[str], Optional[str]]:
        """Extract names from labeled lines like 'ชื่อ <name>' and 'นามสกุล <name>'."""
        first_name = None
        last_name = None

        for line in lines:
            # Pattern: ชื่อ <name> or ชื่อตัวและชื่อสกุล <first> <last>
            if 'ชื่อ' in line:
                remaining = line.replace('ชื่อตัวและชื่อสกุล', '').replace('ชื่อ', '').strip()
                if remaining:
                    # Remove title if present
                    for title in ['นาย', 'นาง', 'นางสาว', 'เด็กชาย', 'เด็กหญิง']:
                        remaining = remaining.replace(title, '').strip()

                    parts = [p.strip() for p in remaining.split() if p.strip() and not OCRService._is_noise_word(p)]
                    if len(parts) >= 2:
                        first_name = parts[0]
                        last_name = parts[1]
                        return first_name, last_name
                    elif len(parts) == 1 and not first_name:
                        first_name = parts[0]

            # Pattern: นามสกุล <name>
            if 'นามสกุล' in line:
                remaining = line.replace('นามสกุล', '').strip()
                if remaining:
                    parts = [p.strip() for p in remaining.split() if p.strip() and not OCRService._is_noise_word(p)]
                    if parts:
                        last_name = parts[0]

        return first_name, last_name

    @staticmethod
    def _extract_from_title_pattern(line: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract names from title patterns like 'นาย <first> <last>'."""
        # Order titles from longest to shortest to avoid partial matches
        titles_ordered = [
            'เด็กหญิง', 'เด็กชาย', 'นางสาว', 'ด.ญ.', 'ด.ช.', 'นาย', 'นาง'
        ]

        for title in titles_ordered:
            if title in line:
                # Find the position after the title
                idx = line.find(title)
                remaining = line[idx + len(title):].strip()

                # Filter out noise words
                parts = [
                    p.strip() for p in remaining.split()
                    if p.strip() and not OCRService._is_noise_word(p)
                ]

                if len(parts) >= 2:
                    return parts[0], parts[1]
                elif len(parts) == 1:
                    return parts[0], None

        return None, None

    @staticmethod
    def extract_thai_names(ocr_text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract Thai first name and surname from OCR text.
        Handles patterns:
        - นาย <first> <last>
        - นางสาว <first> <last>
        - เด็กชาย <first> <last>
        - ชื่อ <first> / นามสกุล <last>
        - ชื่อตัวและชื่อสกุล <first> <last>
        """
        text = OCRService.redact_thai_id_numbers(ocr_text)
        text = text.strip()
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Try labeled lines first (ชื่อ / นามสกุล patterns)
        first_name, last_name = OCRService._extract_from_labeled_lines(lines)
        if first_name or last_name:
            return first_name, last_name

        # Try title patterns
        for line in lines:
            fname, lname = OCRService._extract_from_title_pattern(line)
            if fname or lname:
                return fname, lname

        # Fallback: look for Thai characters only (avoid noise)
        thai_words = []
        for line in lines:
            # Check if line has Thai characters
            has_thai = any('฀' <= char <= '๿' for char in line)
            if has_thai:
                words = [w.strip() for w in line.split() if w.strip()]
                # Filter noise words
                clean_words = [w for w in words if not OCRService._is_noise_word(w)]
                thai_words.extend(clean_words)

        if len(thai_words) >= 2:
            return thai_words[0], thai_words[1]
        elif len(thai_words) == 1:
            return thai_words[0], None

        return None, None

    @staticmethod
    def extract_date_of_birth(ocr_text: str) -> Optional[date]:
        """
        Extract date of birth from OCR text.
        Handles patterns like:
        - เกิดวันที่ 23 ก.ย. 2552
        - Date of Birth 23 Sep. 2009
        - 23 Sep. 2009
        - 23/09/2009
        """
        text = ocr_text.lower()

        # Thai month abbreviations
        thai_months = {
            'ม.ค.': 1, 'ก.พ.': 2, 'มี.ค.': 3, 'เม.ย.': 4,
            'พ.ค.': 5, 'มิ.ย.': 6, 'ก.ค.': 7, 'ส.ค.': 8,
            'ก.ย.': 9, 'ต.ค.': 10, 'พ.ย.': 11, 'ธ.ค.': 12
        }

        # English month abbreviations
        eng_months = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
            'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
            'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }

        # Pattern 1: Thai format (23 ก.ย. 2552)
        for thai_month, month_num in thai_months.items():
            pattern = rf'(\d{{1,2}})\s+{re.escape(thai_month)}\s+(\d{{4}})'
            match = re.search(pattern, text)
            if match:
                day = int(match.group(1))
                year = int(match.group(2))
                # Convert BE to AD if needed
                if year > 2500:
                    year = year - 543
                try:
                    return date(year, month_num, day)
                except ValueError:
                    continue

        # Pattern 2: English format with abbreviations (23 Sep. 2009)
        for eng_month, month_num in eng_months.items():
            pattern = rf'(\d{{1,2}})\s+{eng_month}\.?\s+(\d{{4}})'
            match = re.search(pattern, text)
            if match:
                day = int(match.group(1))
                year = int(match.group(2))
                try:
                    return date(year, month_num, day)
                except ValueError:
                    continue

        # Pattern 3: Slash format (23/09/2009 or 23/9/2009)
        pattern = r'(\d{1,2})/(\d{1,2})/(\d{4})'
        match = re.search(pattern, text)
        if match:
            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3))
            if year > 2500:
                year = year - 543
            try:
                return date(year, month, day)
            except ValueError:
                pass

        return None
