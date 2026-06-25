import re
import cv2
import numpy as np
import logging
from datetime import datetime, date
from io import BytesIO
import pytesseract
from pytesseract import Output
from typing import Optional, Tuple, Dict, List
from pdf2image import convert_from_bytes

logger = logging.getLogger(__name__)

# Thai ID Card template ROI (x, y, width, height) on standard 1000x630 warped card
THAI_ID_CARD_ROIS = {
    "thai_name_line": (250, 205, 520, 75),      # "ชื่อตัวและชื่อสกุล"
    "english_first_name": (360, 265, 360, 55),  # "Name / Mr. ..."
    "english_last_name": (360, 320, 360, 55),   # "Last name ..."
    "dob_thai": (350, 370, 360, 55),            # "เกิดวันที่ ... พ.ศ."
    "dob_english": (385, 420, 360, 55),         # "Date of Birth ..."
}

# Thai ID card aspect ratio (width/height) - typically 1.55-1.65
THAI_ID_ASPECT_RATIO_MIN = 1.50
THAI_ID_ASPECT_RATIO_MAX = 1.70

# Standard warped card size
THAI_ID_STANDARD_WIDTH = 1000
THAI_ID_STANDARD_HEIGHT = 630

# Thai ID card aspect ratio for card-like images (more lenient)
CARD_LIKE_ASPECT_RATIO_MIN = 1.35
CARD_LIKE_ASPECT_RATIO_MAX = 1.85

# Alternative ROI presets for card-like normalized images
THAI_ID_CARD_ROIS_V2 = {
    # Larger ROI for card-like images (more padding)
    "thai_name_line": (190, 180, 600, 95),
    "english_first_name": (310, 250, 430, 70),
    "english_last_name": (310, 310, 430, 70),
    "dob_thai": (300, 365, 430, 65),
    "dob_english": (330, 420, 440, 65),
}

# Noise words to exclude from name extraction
FORBIDDEN_WORDS_EXTENDED = {
    "ประชาชน", "ประจำตัว", "เลขประจำตัว", "บัตรประชาชน", "ไทย",
    "Thai", "National", "ID", "Card", "Identification", "Number",
    "Date", "Birth", "Issue", "Expiry", "ศาสนา", "ที่อยู่",
    "Address", "Sex", "เพศ", "สัญชาติ", "Nationality",
    # Common OCR fragments from ID card text
    "ชา", "ชน", "ปร", "บัต", "ตร", "เลข", "ประ", "บ", "ร", "ก"
}

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
    def preprocess_image(image_bytes: bytes, method: str = "default") -> np.ndarray:
        """Preprocess image with different methods for better OCR accuracy.

        Methods:
        - default: grayscale + denoise + threshold
        - resize2x: resize 2x + default
        - resize3x: resize 3x + default
        - adaptive: grayscale + denoise + adaptive threshold
        - contrast: grayscale + contrast enhancement
        - sharpen: grayscale + sharpening
        """
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        if method in ["resize2x", "resize3x"]:
            scale = 2 if method == "resize2x" else 3
            gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

        if method == "adaptive":
            denoised = cv2.fastNlMeansDenoising(gray, None, h=10)
            return cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
        elif method == "contrast":
            lab = cv2.cvtColor(cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR), cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            return cv2.merge([l, a, b])
        elif method == "sharpen":
            denoised = cv2.fastNlMeansDenoising(gray, None, h=10)
            kernel = np.array([[-1,-1,-1], [-1, 9,-1], [-1,-1,-1]])
            return cv2.filter2D(denoised, -1, kernel)
        else:  # default, resize2x, resize3x
            denoised = cv2.fastNlMeansDenoising(gray, None, h=10)
            _, thresh = cv2.threshold(denoised, 150, 255, cv2.THRESH_BINARY)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            return cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    @staticmethod
    def detect_id_card_rectangle(image_bytes: bytes) -> Optional[np.ndarray]:
        """Detect Thai ID card rectangle and return perspective-warped image.

        Returns warped card image (1000x630) or None if detection fails.
        """
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return None

            height, width = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Preprocess for edge detection
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 50, 150)

            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Look for rectangular contours with card-like aspect ratio
            for contour in sorted(contours, key=cv2.contourArea, reverse=True):
                area = cv2.contourArea(contour)
                if area < (width * height * 0.1):  # Minimum 10% of image
                    continue

                # Approximate polygon
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)

                if len(approx) != 4:
                    continue

                # Get corner points
                pts = approx.reshape(4, 2).astype(np.float32)

                # Calculate aspect ratio
                rect = cv2.minAreaRect(contour)
                card_width, card_height = rect[1]
                if card_height > card_width:
                    card_width, card_height = card_height, card_width

                aspect_ratio = card_width / (card_height + 1e-6)

                # Check if aspect ratio matches Thai ID card
                if not (THAI_ID_ASPECT_RATIO_MIN <= aspect_ratio <= THAI_ID_ASPECT_RATIO_MAX):
                    continue

                # Order points for perspective transform (top-left, top-right, bottom-right, bottom-left)
                def order_points(pts):
                    rect = np.zeros((4, 2), dtype="float32")
                    s = pts.sum(axis=1)
                    rect[0] = pts[np.argmin(s)]
                    rect[2] = pts[np.argmax(s)]
                    diff = np.diff(pts, axis=1)
                    rect[1] = pts[np.argmin(diff)]
                    rect[3] = pts[np.argmax(diff)]
                    return rect

                ordered_pts = order_points(pts)

                # Perspective transform
                dst_pts = np.array([
                    [0, 0],
                    [THAI_ID_STANDARD_WIDTH - 1, 0],
                    [THAI_ID_STANDARD_WIDTH - 1, THAI_ID_STANDARD_HEIGHT - 1],
                    [0, THAI_ID_STANDARD_HEIGHT - 1]
                ], dtype=np.float32)

                matrix = cv2.getPerspectiveTransform(ordered_pts, dst_pts)
                warped = cv2.warpPerspective(img, matrix, (THAI_ID_STANDARD_WIDTH, THAI_ID_STANDARD_HEIGHT))

                return warped

            # No suitable card detected
            return None

        except Exception as e:
            logger.debug(f"Card detection failed: {e}")
            return None

    @staticmethod
    def is_card_like_image(image_bytes: bytes, ocr_text: str = "") -> bool:
        """Check if image appears to be a Thai ID card even without contour detection.

        Returns True if:
        - Aspect ratio is card-like (1.35-1.85)
        - OR OCR text contains ID card keywords
        - OR OCR text contains DOB pattern
        """
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return False

            height, width = img.shape[:2]
            aspect_ratio = width / (height + 1e-6)

            # Check aspect ratio
            if CARD_LIKE_ASPECT_RATIO_MIN <= aspect_ratio <= CARD_LIKE_ASPECT_RATIO_MAX:
                return True

            # Check for ID card keywords in OCR text
            keywords = [
                "Thai National ID Card", "Identification Number",
                "Date of Birth", "บัตรประจำตัวประชาชน",
                "เลขประจำตัวประชาชน", "ชื่อตัวและชื่อสกุล",
                "ชื่อ", "นามสกุล", "Name", "Last name"
            ]
            text_lower = ocr_text.lower()
            if any(kw.lower() in text_lower for kw in keywords):
                return True

            # Check for DOB patterns
            if re.search(r'\d+\s+(Sep|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Oct|Nov|Dec)\.?\s+\d{4}', ocr_text):
                return True
            if re.search(r'\d+\s+(ม\.ค|ก\.พ|มี\.ค|เม\.ย|พ\.ค|มิ\.ย|กค|ส\.ค|ก\.ย|ต\.ค|พ\.ย|ธ\.ค)', ocr_text):
                return True

            return False

        except Exception as e:
            logger.debug(f"Card-like check failed: {e}")
            return False

    @staticmethod
    def crop_card_like_content(image_bytes: bytes) -> Optional[np.ndarray]:
        """Crop content area from card-like image without perfect contour.

        Finds bounding box of non-white content and crops with padding.
        Returns normalized image (1000x630) or None.
        """
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return None

            height, width = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Find pixels that are not white (content area)
            _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

            # Find contours of content
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if not contours:
                return None

            # Get bounding box of all content
            x_min, y_min = width, height
            x_max, y_max = 0, 0

            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                x_min = min(x_min, x)
                y_min = min(y_min, y)
                x_max = max(x_max, x + w)
                y_max = max(y_max, y + h)

            if x_min >= x_max or y_min >= y_max:
                return None

            # Add padding (3-5%)
            padding_x = int((x_max - x_min) * 0.04)
            padding_y = int((y_max - y_min) * 0.04)

            x_min = max(0, x_min - padding_x)
            y_min = max(0, y_min - padding_y)
            x_max = min(width, x_max + padding_x)
            y_max = min(height, y_max + padding_y)

            # Crop content
            cropped = img[y_min:y_max, x_min:x_max]

            # Resize/pad to standard size
            crop_height, crop_width = cropped.shape[:2]
            crop_aspect = crop_width / (crop_height + 1e-6)
            target_aspect = THAI_ID_STANDARD_WIDTH / THAI_ID_STANDARD_HEIGHT

            if crop_aspect > target_aspect:
                # Crop is too wide, resize by height
                new_height = THAI_ID_STANDARD_HEIGHT
                new_width = int(new_height * crop_aspect)
            else:
                # Crop is too tall, resize by width
                new_width = THAI_ID_STANDARD_WIDTH
                new_height = int(new_width / crop_aspect)

            resized = cv2.resize(cropped, (new_width, new_height))

            # Pad to standard size
            if new_width < THAI_ID_STANDARD_WIDTH or new_height < THAI_ID_STANDARD_HEIGHT:
                canvas = np.ones((THAI_ID_STANDARD_HEIGHT, THAI_ID_STANDARD_WIDTH, 3), dtype=np.uint8) * 255
                y_offset = (THAI_ID_STANDARD_HEIGHT - new_height) // 2
                x_offset = (THAI_ID_STANDARD_WIDTH - new_width) // 2
                canvas[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = resized
                return canvas

            return resized[:THAI_ID_STANDARD_HEIGHT, :THAI_ID_STANDARD_WIDTH]

        except Exception as e:
            logger.debug(f"Card-like content crop failed: {e}")
            return None

    @staticmethod
    def normalize_stacked_thai_ocr_text(text: str) -> str:
        """Normalize stacked Thai OCR output where each character is on separate line.

        Example:
        Input:  เ\\nก\\nี\\นย\\nร\\nต\\nิ\\nศ\\นัก → Output: เกีดรติศัก
        """
        # Remove newlines between Thai characters
        lines = text.split('\n')
        thai_chars = []

        for line in lines:
            stripped = line.strip()
            # Keep Thai characters and common symbols
            thai_part = ''.join(c for c in stripped if ('฀' <= c <= '๿') or c in ' .-')
            if thai_part:
                thai_chars.append(thai_part)

        return ' '.join(thai_chars)

    @staticmethod
    def extract_from_roi(image: np.ndarray, roi_name: str, roi_coords: Tuple[int, int, int, int],
                         lang: str = "tha+eng", psm: int = 7) -> Tuple[str, float]:
        """Extract text from specific ROI on image.

        Args:
            image: Image array (warped card)
            roi_name: Name of ROI (for logging)
            roi_coords: (x, y, width, height)
            lang: Tesseract language
            psm: Tesseract PSM mode

        Returns:
            (text, confidence)
        """
        try:
            x, y, w, h = roi_coords
            roi = image[y:y+h, x:x+w]

            if roi.size == 0:
                return "", 0.0

            # Preprocess ROI
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
            denoised = cv2.fastNlMeansDenoising(gray, None, h=10)
            _, thresh = cv2.threshold(denoised, 150, 255, cv2.THRESH_BINARY)

            # OCR
            config = f'--psm {psm}'
            text = pytesseract.image_to_string(thresh, lang=lang, config=config)
            data = pytesseract.image_to_data(thresh, lang=lang, output_type=Output.DICT, config=config)

            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            avg_confidence = min(avg_confidence / 100, 1.0)

            return text.strip(), avg_confidence

        except Exception as e:
            logger.debug(f"ROI extraction failed for {roi_name}: {e}")
            return "", 0.0

    @staticmethod
    def extract_text_with_confidence(image_bytes: bytes, debug: bool = False) -> Tuple[str, float, Dict]:
        """Extract text from image using multiple preprocessing methods and PSM modes.

        Tries multiple preprocessing methods and Tesseract PSM modes, returns the best result.

        Args:
            image_bytes: Raw image data
            debug: If True, returns debug info in the dict

        Returns:
            Tuple of (extracted_text, confidence_score, debug_info)
        """
        preprocessing_methods = ["default", "resize2x", "resize3x", "adaptive", "contrast", "sharpen"]
        psm_modes = [6, 11, 12]
        best_result = None
        best_score = 0.0

        for method in preprocessing_methods:
            try:
                processed = OCRService.preprocess_image(image_bytes, method)

                for psm in psm_modes:
                    try:
                        config = f'--psm {psm}'
                        data = pytesseract.image_to_data(
                            processed,
                            lang='tha+eng',
                            output_type=Output.DICT,
                            config=config
                        )

                        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
                        avg_confidence = min(avg_confidence / 100, 1.0)

                        text = '\n'.join(data['text']).strip()

                        # Calculate score based on confidence and content
                        thai_char_count = sum(1 for c in text if '฀' <= c <= '๿')
                        has_content = len(text) > 0 and thai_char_count > 0
                        score = avg_confidence if has_content else 0

                        if score > best_score:
                            best_score = score
                            best_result = {
                                'text': text,
                                'confidence': avg_confidence,
                                'method': method,
                                'psm': psm
                            }
                    except Exception as e:
                        logger.debug(f"OCR with PSM {psm} failed: {e}")
                        continue
            except Exception as e:
                logger.debug(f"Preprocessing with method {method} failed: {e}")
                continue

        if best_result is None:
            best_result = {
                'text': '',
                'confidence': 0.0,
                'method': 'none',
                'psm': 6
            }

        text = best_result['text']
        confidence = best_result['confidence']

        # Create debug info with redacted text for display
        redacted_text = OCRService.redact_thai_id_numbers(text)
        debug_info = {
            'ocr_text': redacted_text,
            'preprocessing_method': best_result['method'],
            'psm_mode': best_result['psm'],
            'confidence': confidence
        }

        return text, confidence, debug_info

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

    @staticmethod
    def parse_thai_full_name_from_roi(text: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse Thai first name and last name from ROI text.

        Handles Thai title patterns and ensures names are valid.
        Rejects short tokens (≤2 chars) unless they come after a clear title.
        """
        text = OCRService.redact_thai_id_numbers(text.strip().lower())
        if not text:
            return None, None

        lines = [line.strip() for line in text.split('\n') if line.strip()]
        first_name = None
        last_name = None

        # Try title patterns first (titles allow short names)
        titles = ['เด็กหญิง', 'เด็กชาย', 'นางสาว', 'ด.ญ.', 'ด.ช.', 'นาย', 'นาง']
        for line in lines:
            for title in sorted(titles, key=len, reverse=True):  # Longest first
                if title in line:
                    remaining = line.split(title, 1)[1].strip()
                    parts = [
                        p.strip() for p in remaining.split()
                        if p.strip() and not OCRService._is_noise_word(p) and p.lower() not in FORBIDDEN_WORDS_EXTENDED
                    ]
                    if len(parts) >= 2:
                        return parts[0], parts[1]
                    elif len(parts) == 1:
                        return parts[0], None

        # Extract Thai words (without title - reject short tokens)
        thai_words = []
        for line in lines:
            words = [
                w.strip() for w in line.split()
                if w.strip() and not OCRService._is_noise_word(w) and w.lower() not in FORBIDDEN_WORDS_EXTENDED
            ]
            # Only keep Thai words that are longer than 2 characters (reject OCR fragments)
            words = [w for w in words if any('฀' <= c <= '๿' for c in w) and len(w) > 2]
            thai_words.extend(words)

        if len(thai_words) >= 2:
            return thai_words[0], thai_words[1]
        elif len(thai_words) == 1:
            return thai_words[0], None

        return None, None

    @staticmethod
    def parse_english_name_from_roi(text: str) -> Optional[str]:
        """Parse English first or last name from ROI text.

        Removes titles like Mr., Miss, Mrs., etc.
        """
        text = text.strip()
        if not text:
            return None

        # Remove titles
        titles = ['Mr.', 'Mrs.', 'Miss', 'Ms.', 'Dr.', 'Prof.']
        for title in titles:
            if text.lower().startswith(title.lower()):
                text = text[len(title):].strip()

        # Get first word (should be single name)
        words = text.split()
        if words and len(words[0]) > 1:  # Avoid single characters
            return words[0]

        return None

    @staticmethod
    def extract_dob_from_rois(dob_english_text: str, dob_thai_text: str) -> Optional[date]:
        """Extract date of birth from English or Thai ROI text.

        Prioritizes English format, falls back to Thai.
        """
        # Try English first
        if dob_english_text.strip():
            result = OCRService.extract_date_of_birth(dob_english_text)
            if result:
                return result

        # Try Thai
        if dob_thai_text.strip():
            result = OCRService.extract_date_of_birth(dob_thai_text)
            if result:
                return result

        return None

    @staticmethod
    def extract_from_thai_id_template(image_bytes: bytes) -> Dict:
        """Extract data from Thai ID card using template ROI approach.

        Returns dict with:
        - success: bool
        - card_detected: bool
        - card_warped: bool
        - extraction_mode: "thai_id_template" or "full_ocr_fallback"
        - first_name: str or None
        - last_name: str or None
        - date_of_birth: date or None
        - confidence: float (average of all ROIs)
        - roi_results: dict with individual ROI results
        - warnings: list
        """
        warnings = []
        roi_results = {}
        card_detected = False
        card_warped = False

        try:
            # Get full OCR text for fallback checks
            full_ocr_text, _, _ = OCRService.extract_text_with_confidence(image_bytes)

            # Try to detect and warp card
            warped_card = OCRService.detect_id_card_rectangle(image_bytes)
            extraction_mode = "thai_id_template_warped"
            card_like_fallback_used = False

            if warped_card is not None:
                card_detected = True
                card_warped = True
            else:
                # Try card-like fallback if image looks like a Thai ID
                if OCRService.is_card_like_image(image_bytes, full_ocr_text):
                    warped_card = OCRService.crop_card_like_content(image_bytes)
                    if warped_card is not None:
                        card_detected = False
                        card_warped = False
                        card_like_fallback_used = True
                        extraction_mode = "thai_id_template_card_like"
                        warnings.append("ไม่พบกรอบบัตรชัดเจน แต่ใช้โครงบัตรจากภาพแทน กรุณาตรวจสอบข้อมูล")
                    else:
                        warnings.append("ไม่พบกรอบบัตรประชาชน กรุณากรอกชื่อเอง")
                        card_detected = False
                else:
                    warnings.append("ไม่พบกรอบบัตรประชาชน กรุณากรอกชื่อเอง")
                    card_detected = False

            # Extract from ROIs if card was detected, warped, or card-like fallback
            if warped_card is not None:
                # Choose ROI preset based on extraction mode
                roi_preset = THAI_ID_CARD_ROIS if not card_like_fallback_used else THAI_ID_CARD_ROIS_V2

                # Extract Thai name
                thai_name_text, thai_name_conf = OCRService.extract_from_roi(
                    warped_card, "thai_name_line", roi_preset["thai_name_line"], lang="tha+eng", psm=6
                )
                # Normalize stacked Thai characters if needed
                thai_name_text = OCRService.normalize_stacked_thai_ocr_text(thai_name_text)
                thai_first, thai_last = OCRService.parse_thai_full_name_from_roi(thai_name_text)

                # Extract English names
                eng_first_text, eng_first_conf = OCRService.extract_from_roi(
                    warped_card, "english_first_name", roi_preset["english_first_name"], lang="eng", psm=7
                )
                eng_first = OCRService.parse_english_name_from_roi(eng_first_text)

                eng_last_text, eng_last_conf = OCRService.extract_from_roi(
                    warped_card, "english_last_name", roi_preset["english_last_name"], lang="eng", psm=7
                )
                eng_last = OCRService.parse_english_name_from_roi(eng_last_text)

                # Extract DOB
                dob_thai_text, dob_thai_conf = OCRService.extract_from_roi(
                    warped_card, "dob_thai", roi_preset["dob_thai"], lang="tha+eng", psm=7
                )
                dob_eng_text, dob_eng_conf = OCRService.extract_from_roi(
                    warped_card, "dob_english", roi_preset["dob_english"], lang="eng", psm=7
                )
                dob = OCRService.extract_dob_from_rois(dob_eng_text, dob_thai_text)

                # Store ROI results
                roi_results = {
                    "thai_name_line": {"text": OCRService.redact_thai_id_numbers(thai_name_text), "confidence": thai_name_conf},
                    "english_first_name": {"text": OCRService.redact_thai_id_numbers(eng_first_text), "confidence": eng_first_conf},
                    "english_last_name": {"text": OCRService.redact_thai_id_numbers(eng_last_text), "confidence": eng_last_conf},
                    "dob_thai": {"text": OCRService.redact_thai_id_numbers(dob_thai_text), "confidence": dob_thai_conf},
                    "dob_english": {"text": OCRService.redact_thai_id_numbers(dob_eng_text), "confidence": dob_eng_conf},
                }

                # Determine final names (prioritize Thai, fallback to English)
                first_name = thai_first or eng_first
                last_name = thai_last or eng_last

                if not thai_first and eng_first:
                    warnings.append("ไม่พบชื่อภาษาไทยจาก OCR ใช้ชื่อภาษาอังกฤษเป็นข้อมูลอ้างอิง กรุณาตรวจสอบ")

                if not dob:
                    warnings.append("ไม่พบวันเกิดจาก OCR กรุณากรอกเอง")

                # Calculate average confidence
                confidences = [v.get("confidence", 0) for _, v in roi_results.items() if isinstance(v, dict) and v.get("confidence", 0) > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

                return {
                    "success": True,
                    "card_detected": card_detected,
                    "card_warped": True,
                    "extraction_mode": extraction_mode,
                    "card_like_fallback_used": card_like_fallback_used,
                    "roi_preset": "v2" if card_like_fallback_used else "v1",
                    "first_name": first_name,
                    "last_name": last_name,
                    "date_of_birth": dob,
                    "confidence": avg_confidence,
                    "roi_results": roi_results,
                    "warnings": warnings
                }

        except Exception as e:
            logger.warning(f"Thai ID template extraction failed: {e}")

        # Fallback return
        return {
            "success": False,
            "card_detected": card_detected,
            "card_warped": card_warped,
            "extraction_mode": "full_ocr_fallback",
            "card_like_fallback_used": card_like_fallback_used,
            "roi_preset": None,
            "first_name": None,
            "last_name": None,
            "date_of_birth": None,
            "confidence": 0.0,
            "roi_results": roi_results,
            "warnings": warnings
        }
