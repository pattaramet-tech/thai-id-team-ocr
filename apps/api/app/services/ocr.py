import re
import cv2
import numpy as np
from datetime import datetime, date
from io import BytesIO
import pytesseract
from typing import Optional, Tuple, Dict, List
from pdf2image import convert_from_bytes

class OCRService:
    @staticmethod
    def pdf_to_image_bytes(pdf_bytes: bytes) -> bytes:
        """
        Convert first page of PDF to image bytes (JPEG).
        Returns bytes of the first page as JPEG image.
        """
        try:
            images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1, dpi=300)
            if not images:
                raise Exception("No pages found in PDF")

            img = images[0]
            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=95)
            img_byte_arr.seek(0)
            return img_byte_arr.getvalue()
        except Exception as e:
            raise Exception(f"PDF conversion failed: {str(e)}")

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
    def _remove_thai_title(text: str) -> str:
        """Remove Thai title from start of text. Order matters: longest first."""
        if not text:
            return text

        # Titles ordered from longest to shortest to avoid partial matches
        titles_ordered = [
            'เด็กหญิง', 'เด็กชาย', 'นางสาว', 'ด.ญ.', 'ด.ช.', 'นาย', 'นาง'
        ]

        text = text.strip()
        for title in titles_ordered:
            if text.startswith(title):
                text = text[len(title):].strip()
                break

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
    def _contains_forbidden_words(name: str) -> bool:
        """Check if extracted name contains forbidden/invalid words."""
        forbidden = {
            'บัตร', 'ประชาชน', 'เลขประจำตัว', 'national', 'id', 'card',
            'เลข', 'ป.ตรว', 'ปตรว', 'passport', 'document'
        }
        name_lower = name.lower()
        return any(word in name_lower for word in forbidden)

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
                    remaining = OCRService._remove_thai_title(remaining)

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
        # Titles ordered from longest to shortest
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
        - เกิดวันที่ 23 ก.ย. 2552 (Thai month with dots)
        - 23 กย 2552 (Thai month without dots)
        - Date of Birth 23 September 2009 (English full month)
        - 23 Sep. 2009 (English abbreviation)
        - 2009-09-23 (ISO format)
        - 23/09/2009 (slash format)
        """
        text = ocr_text.lower()

        # Thai month abbreviations with dots
        thai_months_dotted = {
            'ม.ค.': 1, 'ก.พ.': 2, 'มี.ค.': 3, 'เม.ย.': 4,
            'พ.ค.': 5, 'มิ.ย.': 6, 'ก.ค.': 7, 'ส.ค.': 8,
            'ก.ย.': 9, 'ต.ค.': 10, 'พ.ย.': 11, 'ธ.ค.': 12
        }

        # Thai month abbreviations without dots
        thai_months_nodots = {
            'มค': 1, 'กพ': 2, 'มีค': 3, 'เมย': 4,
            'พค': 5, 'มิย': 6, 'กค': 7, 'สค': 8,
            'กย': 9, 'ตค': 10, 'พย': 11, 'ธค': 12
        }

        # English month full names
        eng_months_full = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }

        # English month abbreviations
        eng_months_abbr = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
            'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
            'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }

        # Pattern 1: English full month names (23 September 2009) - check before other patterns
        for eng_month, month_num in eng_months_full.items():
            pattern = rf'(\d{{1,2}})\s+{eng_month}\s+(\d{{4}})'
            match = re.search(pattern, text)
            if match:
                day = int(match.group(1))
                year = int(match.group(2))
                if 1900 <= year <= 2100:
                    try:
                        return date(year, month_num, day)
                    except ValueError:
                        continue

        # Pattern 2: English abbreviations (23 Sep. 2009)
        for eng_month, month_num in eng_months_abbr.items():
            pattern = rf'(\d{{1,2}})\s+{eng_month}\.?\s+(\d{{4}})'
            match = re.search(pattern, text)
            if match:
                day = int(match.group(1))
                year = int(match.group(2))
                if 1900 <= year <= 2100:
                    try:
                        return date(year, month_num, day)
                    except ValueError:
                        continue

        # Pattern 3: Thai format with dots (23 ก.ย. 2552)
        for thai_month, month_num in thai_months_dotted.items():
            pattern = rf'(\d{{1,2}})\s+{re.escape(thai_month)}\s+(\d{{4}})'
            match = re.search(pattern, text)
            if match:
                day = int(match.group(1))
                year = int(match.group(2))
                if year > 2500:
                    year = year - 543
                if 1900 <= year <= 2100:
                    try:
                        return date(year, month_num, day)
                    except ValueError:
                        continue

        # Pattern 4: Thai format without dots (23 กย 2552)
        for thai_month, month_num in thai_months_nodots.items():
            pattern = rf'(\d{{1,2}})\s+{re.escape(thai_month)}\s+(\d{{4}})'
            match = re.search(pattern, text)
            if match:
                day = int(match.group(1))
                year = int(match.group(2))
                if year > 2500:
                    year = year - 543
                if 1900 <= year <= 2100:
                    try:
                        return date(year, month_num, day)
                    except ValueError:
                        continue

        # Pattern 5: ISO format (2009-09-23) - check after named months to avoid false matches
        pattern = r'(\d{4})-(\d{1,2})-(\d{1,2})'
        match = re.search(pattern, text)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            if year > 2500:
                year = year - 543
            if 1900 <= year <= 2100:
                try:
                    return date(year, month, day)
                except ValueError:
                    pass

        # Pattern 6: Slash format (23/09/2009 or 23/9/2009)
        pattern = r'(\d{1,2})/(\d{1,2})/(\d{4})'
        match = re.search(pattern, text)
        if match:
            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3))
            if year > 2500:
                year = year - 543
            if 1900 <= year <= 2100:
                try:
                    return date(year, month, day)
                except ValueError:
                    pass

        return None
