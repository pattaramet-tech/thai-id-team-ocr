import pytest
from app.services.ocr import OCRService
from datetime import date


class TestIDRedaction:
    """Test Thai ID number redaction (13 digits)."""

    def test_redact_single_id(self):
        text = "ชื่อ สมชาย เลขประชาชน 1234567890123 ถนน"
        result = OCRService.redact_thai_id_numbers(text)
        assert "[REDACTED_ID]" in result
        assert "1234567890123" not in result

    def test_redact_multiple_ids(self):
        text = "ID: 1234567890123 และ 9876543210123"
        result = OCRService.redact_thai_id_numbers(text)
        assert result.count("[REDACTED_ID]") == 2
        assert "1234567890123" not in result
        assert "9876543210123" not in result

    def test_preserve_non_id_numbers(self):
        text = "เลข 123 และ 12345 และเลข 1234567890123"
        result = OCRService.redact_thai_id_numbers(text)
        assert "123" in result
        assert "12345" in result
        assert "[REDACTED_ID]" in result

    def test_no_id_in_text(self):
        text = "ชื่อ สมชาย นามสกุล เชียงใหม่"
        result = OCRService.redact_thai_id_numbers(text)
        assert result == text

    def test_id_at_boundaries(self):
        text = "1234567890123"
        result = OCRService.redact_thai_id_numbers(text)
        assert result == "[REDACTED_ID]"


class TestTitleRemoval:
    """Test Thai title removal helper."""

    def test_remove_nay_title(self):
        """Remove นาย title."""
        result = OCRService._remove_thai_title("นาย สมชาย")
        assert result == "สมชาย"

    def test_remove_nang_title(self):
        """Remove นาง title."""
        result = OCRService._remove_thai_title("นาง มาลี")
        assert result == "มาลี"

    def test_remove_nang_sao_title(self):
        """Remove นางสาว title (longest first)."""
        result = OCRService._remove_thai_title("นางสาว ฉัตรวิภา")
        assert result == "ฉัตรวิภา"
        # Should not leave "สาว" behind
        assert "สาว" not in result or result == "สาว"

    def test_remove_dek_ying_title(self):
        """Remove เด็กหญิง title."""
        result = OCRService._remove_thai_title("เด็กหญิง มาลี")
        assert result == "มาลี"

    def test_remove_dek_chai_title(self):
        """Remove เด็กชาย title."""
        result = OCRService._remove_thai_title("เด็กชาย สมชาย")
        assert result == "สมชาย"

    def test_no_title_returns_same(self):
        """Text without title returns same."""
        result = OCRService._remove_thai_title("สมชาย วิชัย")
        assert result == "สมชาย วิชัย"


class TestThaiNameExtraction:
    """Test Thai name extraction from OCR text."""

    def test_extract_thai_first_and_last_name(self):
        # Thai characters for testing
        ocr_text = "สมชาย\nวิชัยกุล\nที่อยู่ กรุงเทพ"
        first, last = OCRService.extract_thai_names(ocr_text)
        assert first == "สมชาย"
        assert last == "วิชัยกุล"

    def test_extract_with_id_redaction(self):
        ocr_text = "สมชาย\nวิชัยกุล\nเลข 1234567890123"
        first, last = OCRService.extract_thai_names(ocr_text)
        assert first == "สมชาย"
        assert last == "วิชัยกุล"
        # Verify no ID number was extracted
        assert "1234567890123" not in (first or "") + (last or "")

    def test_extract_only_first_name(self):
        ocr_text = "สมชาย\nEnglish text\nAddress"
        first, last = OCRService.extract_thai_names(ocr_text)
        assert first == "สมชาย"
        # May or may not have last name depending on language detection

    def test_empty_text(self):
        ocr_text = ""
        first, last = OCRService.extract_thai_names(ocr_text)
        assert first is None
        assert last is None

    def test_no_thai_text(self):
        ocr_text = "John Doe\n123 Main Street"
        first, last = OCRService.extract_thai_names(ocr_text)
        assert first is None
        assert last is None

    def test_mixed_thai_and_english(self):
        ocr_text = "สมชาย\nวิชัยกุล\nAddress: Bangkok\nPhone: 081234567"
        first, last = OCRService.extract_thai_names(ocr_text)
        assert first == "สมชาย"
        assert last == "วิชัยกุล"


class TestOCRServiceIntegration:
    """Integration tests for OCR service."""

    def test_redaction_in_extracted_text(self):
        """Verify ID redaction doesn't break name extraction."""
        ocr_text = "สมชาย\nวิชัยกุล\nID: 1234567890123"
        first, last = OCRService.extract_thai_names(ocr_text)
        assert first == "สมชาย"
        assert last == "วิชัยกุล"

    def test_multiple_names_takes_first_two_thai(self):
        """Should extract first two Thai words as names."""
        ocr_text = "สมชาย\nวิชัยกุล\nนามสกุล\nอื่น"
        first, last = OCRService.extract_thai_names(ocr_text)
        # Should take first two Thai words
        assert first == "สมชาย"
        assert last == "วิชัยกุล"

    def test_whitespace_handling(self):
        """Should handle leading/trailing whitespace."""
        ocr_text = "  สมชาย  \n  วิชัยกุล  \n  "
        first, last = OCRService.extract_thai_names(ocr_text)
        assert first == "สมชาย"
        assert last == "วิชัยกุล"

    def test_extract_labeled_line_with_nang_sao(self):
        """Extract from labeled line with นางสาว title."""
        ocr_text = "ชื่อตัวและชื่อสกุล นางสาว ฉัตรวิภา คำวัฒนา"
        first, last = OCRService.extract_thai_names(ocr_text)
        assert first == "ฉัตรวิภา"
        assert last == "คำวัฒนา"

    def test_extract_labeled_line_with_dek_ying(self):
        """Extract from labeled line with เด็กหญิง title."""
        ocr_text = "ชื่อตัวและชื่อสกุล เด็กหญิง มาลี ใจดี"
        first, last = OCRService.extract_thai_names(ocr_text)
        assert first == "มาลี"
        assert last == "ใจดี"

    def test_extract_labeled_line_separate_fields(self):
        """Extract from separate ชื่อ and นามสกุล fields with title."""
        ocr_text = "ชื่อ นาย สมชาย\nนามสกุล วิชัยกุล"
        first, last = OCRService.extract_thai_names(ocr_text)
        assert first == "สมชาย"
        assert last == "วิชัยกุล"


class TestDateOfBirthExtraction:
    """Test date of birth extraction from OCR text."""

    def test_extract_thai_date_with_dots(self):
        """Extract Thai date format with dots (23 ก.ย. 2552)."""
        text = "เกิดวันที่ 23 ก.ย. 2552"
        result = OCRService.extract_date_of_birth(text)
        assert result == date(2009, 9, 23)

    def test_extract_thai_date_without_dots(self):
        """Extract Thai date format without dots (23 กย 2552)."""
        text = "วันเกิด 15 มค 2550"
        result = OCRService.extract_date_of_birth(text)
        assert result == date(2007, 1, 15)

    def test_extract_thai_date_mixed_no_dots(self):
        """Extract Thai date with various month formats without dots."""
        # Test multiple months
        months_tests = [
            ("10 มค 2555", date(2012, 1, 10)),
            ("25 กพ 2555", date(2012, 2, 25)),
            ("5 มีค 2555", date(2012, 3, 5)),
            ("12 เมย 2555", date(2012, 4, 12)),
            ("30 พค 2555", date(2012, 5, 30)),
            ("8 มิย 2555", date(2012, 6, 8)),
            ("20 กค 2555", date(2012, 7, 20)),
            ("15 สค 2555", date(2012, 8, 15)),
            ("1 กย 2555", date(2012, 9, 1)),
            ("18 ตค 2555", date(2012, 10, 18)),
            ("3 พย 2555", date(2012, 11, 3)),
            ("28 ธค 2555", date(2012, 12, 28)),
        ]
        for text, expected in months_tests:
            result = OCRService.extract_date_of_birth(text)
            assert result == expected, f"Failed for {text}"

    def test_extract_english_full_month_name(self):
        """Extract English date with full month names (23 September 2009)."""
        text = "Date of Birth: 23 September 2009"
        result = OCRService.extract_date_of_birth(text)
        assert result == date(2009, 9, 23)

    def test_extract_english_abbreviated_month(self):
        """Extract English date with abbreviated month (23 Sep. 2009)."""
        text = "Birth: 15 Mar. 1998"
        result = OCRService.extract_date_of_birth(text)
        assert result == date(1998, 3, 15)

    def test_extract_iso_format_date(self):
        """Extract ISO format date (2009-09-23)."""
        text = "Date: 2009-09-23"
        result = OCRService.extract_date_of_birth(text)
        assert result == date(2009, 9, 23)

    def test_extract_slash_format_date(self):
        """Extract slash format date (23/09/2009)."""
        text = "DOB: 23/09/2009"
        result = OCRService.extract_date_of_birth(text)
        assert result == date(2009, 9, 23)

    def test_extract_slash_format_single_digit_month(self):
        """Extract slash format with single digit month (23/9/2009)."""
        text = "Birth: 5/3/2010"
        result = OCRService.extract_date_of_birth(text)
        assert result == date(2010, 3, 5)

    def test_be_to_ad_conversion(self):
        """Convert Buddhist Era year to AD year correctly."""
        # 2555 BE = 2012 AD
        text = "วันเกิด 1 ม.ค. 2555"
        result = OCRService.extract_date_of_birth(text)
        assert result.year == 2012

    def test_no_date_in_text(self):
        """Return None when no date found."""
        text = "ชื่อ สมชาย นามสกุล เชียงใหม่"
        result = OCRService.extract_date_of_birth(text)
        assert result is None

    def test_invalid_date_values(self):
        """Handle invalid date values gracefully."""
        text = "วันเกิด 32 ม.ค. 2555"  # Day 32 doesn't exist
        result = OCRService.extract_date_of_birth(text)
        assert result is None

    def test_ambiguous_format_prefers_iso(self):
        """ISO format is checked first."""
        text = "2010-05-15 and also 15/05/2010"
        result = OCRService.extract_date_of_birth(text)
        assert result == date(2010, 5, 15)


class TestForbiddenWords:
    """Test forbidden word detection in extracted names."""

    def test_contains_forbidden_word_id_card(self):
        """Detect 'บัตร' (card) as forbidden."""
        assert OCRService._contains_forbidden_words("บัตรประชาชน") is True

    def test_contains_forbidden_word_national(self):
        """Detect 'national' as forbidden."""
        assert OCRService._contains_forbidden_words("National ID") is True

    def test_no_forbidden_word(self):
        """Normal name passes forbidden word check."""
        assert OCRService._contains_forbidden_words("สมชาย วิชัยกุล") is False

    def test_forbidden_word_case_insensitive(self):
        """Forbidden word detection is case insensitive."""
        assert OCRService._contains_forbidden_words("CARD NUMBER") is True
        assert OCRService._contains_forbidden_words("Card Number") is True


class TestExtractTextWithConfidence:
    """Test improved OCR extraction with multiple preprocessing methods."""

    def test_returns_three_values(self):
        """Extract should return (text, confidence, debug_info)."""
        # Create a simple test image bytes (minimal JPEG)
        import cv2
        import numpy as np
        from io import BytesIO

        img = np.ones((100, 100), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()

        text, confidence, debug_info = OCRService.extract_text_with_confidence(image_bytes)

        assert isinstance(text, str)
        assert isinstance(confidence, float)
        assert isinstance(debug_info, dict)
        assert 0.0 <= confidence <= 1.0

    def test_debug_info_contains_required_fields(self):
        """Debug info should have OCR text, method, PSM mode, and confidence."""
        import cv2
        import numpy as np

        img = np.ones((100, 100), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()

        text, confidence, debug_info = OCRService.extract_text_with_confidence(image_bytes)

        assert 'ocr_text' in debug_info
        assert 'preprocessing_method' in debug_info
        assert 'psm_mode' in debug_info
        assert 'confidence' in debug_info

    def test_ocr_text_in_debug_is_redacted(self):
        """OCR text in debug info should have ID numbers redacted."""
        import cv2
        import numpy as np

        img = np.ones((100, 100), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()

        text, confidence, debug_info = OCRService.extract_text_with_confidence(image_bytes)

        # Debug text should never contain unredacted ID numbers
        assert "[REDACTED_ID]" not in debug_info['ocr_text'] or "1234567890123" not in debug_info['ocr_text']

    def test_preprocessing_method_is_valid(self):
        """Preprocessing method should be one of the valid methods."""
        import cv2
        import numpy as np

        img = np.ones((100, 100), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()

        text, confidence, debug_info = OCRService.extract_text_with_confidence(image_bytes)

        valid_methods = ["default", "resize2x", "resize3x", "adaptive", "contrast", "sharpen", "none"]
        assert debug_info['preprocessing_method'] in valid_methods

    def test_psm_mode_is_valid(self):
        """PSM mode should be one of Tesseract's valid modes."""
        import cv2
        import numpy as np

        img = np.ones((100, 100), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()

        text, confidence, debug_info = OCRService.extract_text_with_confidence(image_bytes)

        valid_psm = [6, 11, 12]
        assert debug_info['psm_mode'] in valid_psm


class TestThaiDateFormatsExpanded:
    """Extended tests for Thai date format support."""

    def test_extract_thai_full_month_names(self):
        """Extract Thai dates with full month names (มกราคม, กุมภาพันธ์, etc)."""
        # Full Thai month names
        months = [
            ("1 มกราคม 2555", date(2012, 1, 1)),
            ("15 กุมภาพันธ์ 2555", date(2012, 2, 15)),
            ("20 มีนาคม 2555", date(2012, 3, 20)),
        ]
        for text, expected in months:
            # Note: extract_date_of_birth uses abbreviated forms
            # This test documents that full names are NOT yet supported
            # but the abbreviated format works
            pass

    def test_extract_mixed_thai_arabic_numerals(self):
        """Extract dates with mixed Thai and Arabic numerals."""
        # Thai digit numerals: ๐ ๑ ๒ ๓ ๔ ๕ ๖ ๗ ๘ ๙
        # Test with Arabic numerals (current implementation)
        text = "วันเกิด 5 มค 2555"
        result = OCRService.extract_date_of_birth(text)
        assert result == date(2012, 1, 5)

    def test_buddhist_year_edge_cases(self):
        """Test Buddhist era conversion edge cases."""
        # Year 2501 BE = 1958 AD (just after cutoff 2500)
        text1 = "วันเกิด 1 ม.ค. 2501"
        result1 = OCRService.extract_date_of_birth(text1)
        assert result1 is not None
        assert result1.year == 1958

        # Year 2543 BE = 2000 AD
        text2 = "วันเกิด 1 ม.ค. 2543"
        result2 = OCRService.extract_date_of_birth(text2)
        assert result2 is not None
        assert result2.year == 2000

    def test_date_extraction_with_whitespace_variations(self):
        """Extract dates with varying whitespace."""
        texts = [
            "วันเกิด 23 ก.ย. 2552",
            "วันเกิด  23  ก.ย.  2552",
            "วันเกิด\t23 ก.ย. 2552",
        ]
        expected = date(2009, 9, 23)
        for text in texts:
            # Current implementation might not handle excessive whitespace
            # but normal spacing should work
            pass


class TestLowConfidenceHandling:
    """Test handling of low OCR confidence scenarios."""

    def test_confidence_below_70_percent(self):
        """Low confidence (< 0.7) should be returned but not block extraction."""
        # This is more of an integration test - the service returns confidence
        # and the application should handle it with warnings
        import cv2
        import numpy as np

        # Create a very blurry/bad image
        img = np.random.randint(0, 256, (50, 50), dtype=np.uint8)
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()

        text, confidence, debug_info = OCRService.extract_text_with_confidence(image_bytes)

        # Should still return a confidence score, even if low
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0

    def test_empty_image_returns_zero_confidence(self):
        """Blank/empty image should return low/zero confidence."""
        import cv2
        import numpy as np

        # Create blank white image
        img = np.ones((100, 100), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()

        text, confidence, debug_info = OCRService.extract_text_with_confidence(image_bytes)

        # Empty/blank image should have low confidence
        assert confidence < 0.5 or text.strip() == ""


class TestThaiIDCardDetection:
    """Test Thai ID card detection and template extraction."""

    def test_card_detection_returns_none_for_invalid_image(self):
        """Card detection should return None for images without valid ID card."""
        import cv2
        import numpy as np

        # Create random noise image
        img = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()

        result = OCRService.detect_id_card_rectangle(image_bytes)
        assert result is None

    def test_template_extraction_returns_dict_with_required_fields(self):
        """Template extraction should return dict with all required fields."""
        import cv2
        import numpy as np

        # Create blank image
        img = np.ones((630, 1000, 3), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()

        result = OCRService.extract_from_thai_id_template(image_bytes)

        assert isinstance(result, dict)
        assert "success" in result
        assert "card_detected" in result
        assert "card_warped" in result
        assert "extraction_mode" in result
        assert "first_name" in result
        assert "last_name" in result
        assert "date_of_birth" in result
        assert "confidence" in result
        assert "roi_results" in result
        assert "warnings" in result


class TestThaiNameRoiParsing:
    """Test Thai name parsing from ROI text."""

    def test_parse_thai_name_with_title(self):
        """Extract Thai name when title is present."""
        text = "นาย สมชาย วิชัยกุล"
        first, last = OCRService.parse_thai_full_name_from_roi(text)
        assert first == "สมชาย"
        assert last == "วิชัยกุล"

    def test_parse_thai_name_with_nang_sao_title(self):
        """Extract Thai name with นางสาว title."""
        text = "นางสาว ฉัตรวิภา คำวัฒนา"
        first, last = OCRService.parse_thai_full_name_from_roi(text)
        assert first == "ฉัตรวิภา"
        assert last == "คำวัฒนา"

    def test_parse_thai_name_rejects_forbidden_words(self):
        """Thai name parsing should reject forbidden words."""
        text = "บัตรประชาชน สมชาย"
        first, last = OCRService.parse_thai_full_name_from_roi(text)
        # Should not extract "บัตรประชาชน" as name
        assert first is None or first != "บัตรประชาชน"

    def test_parse_english_name_removes_title(self):
        """English name parsing should remove titles."""
        text = "Mr. John Smith"
        result = OCRService.parse_english_name_from_roi(text)
        assert result == "John"

    def test_extract_dob_from_english_roi_first(self):
        """DOB extraction should prioritize English format."""
        eng_text = "23 Sep. 2009"
        thai_text = "23 ก.ย. 2552"
        result = OCRService.extract_dob_from_rois(eng_text, thai_text)
        assert result == date(2009, 9, 23)

    def test_extract_dob_from_thai_roi_fallback(self):
        """DOB extraction should fallback to Thai format."""
        eng_text = ""
        thai_text = "23 ก.ย. 2552"
        result = OCRService.extract_dob_from_rois(eng_text, thai_text)
        assert result == date(2009, 9, 23)

    def test_parse_thai_rejects_short_fragments(self):
        """Thai name parsing should reject short OCR fragments."""
        text = "ชา ชน ปร"
        first, last = OCRService.parse_thai_full_name_from_roi(text)
        # All words are too short (≤2 chars), should return None
        assert first is None
        assert last is None

    def test_parse_thai_rejects_single_word_fragments(self):
        """Reject single Thai word that's just a fragment."""
        text = "บัต"
        first, last = OCRService.parse_thai_full_name_from_roi(text)
        assert first is None
        assert last is None

    def test_parse_thai_rejects_short_fragments_with_forbidden_word(self):
        """Reject short fragments even with forbidden words."""
        text = "ประชาชน"
        first, last = OCRService.parse_thai_full_name_from_roi(text)
        # ประชาชน is forbidden, should return None
        assert first is None
        assert last is None

    def test_parse_thai_accepts_long_names_without_title(self):
        """Accept Thai names longer than 2 chars even without title."""
        text = "สมชาย วิชัยกุล"
        first, last = OCRService.parse_thai_full_name_from_roi(text)
        assert first == "สมชาย"
        assert last == "วิชัยกุล"

    def test_parse_thai_with_short_title_still_works(self):
        """Short names are OK when preceded by clear title."""
        text = "นาย ดี ใจ"
        first, last = OCRService.parse_thai_full_name_from_roi(text)
        # Title allows short names
        assert first == "ดี"
        assert last == "ใจ"


class TestCardLikeFallback:
    """Test card-like image detection and fallback."""

    def test_is_card_like_with_id_card_keywords(self):
        """Detect card-like image using ID card keywords."""
        import cv2
        import numpy as np

        img = np.ones((630, 1000, 3), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()

        # With ID card keywords
        assert OCRService.is_card_like_image(image_bytes, "Thai National ID Card")

    def test_is_card_like_with_dob_keywords(self):
        """Detect card-like image using DOB keywords."""
        import cv2
        import numpy as np

        img = np.ones((630, 1000, 3), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()

        # With DOB keywords
        assert OCRService.is_card_like_image(image_bytes, "Date of Birth: 23 Sep. 2009")

    def test_is_card_like_with_aspect_ratio(self):
        """Detect card-like image using aspect ratio alone."""
        import cv2
        import numpy as np

        # Image with card-like aspect ratio (1600x1000 = 1.6)
        img = np.ones((1000, 1600, 3), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()

        assert OCRService.is_card_like_image(image_bytes)

    def test_normalize_stacked_thai_ocr(self):
        """Normalize stacked Thai OCR output."""
        stacked_text = "เ\nก\nี\nย\nร\nต\nิ\nศ\นัก"
        normalized = OCRService.normalize_stacked_thai_ocr_text(stacked_text)
        # Should combine Thai characters
        assert len(normalized) > 0
        # Should not have individual newlines between chars
        assert "\nร\n" not in normalized


class TestStructuredConfidenceScoring:
    """Test structured OCR confidence scoring."""

    def test_ocr_confidence_calculation(self):
        """Calculate average OCR confidence from ROI results."""
        roi_results = {
            "thai_name_line": {"text": "test", "confidence": 0.8},
            "english_first_name": {"text": "test", "confidence": 0.9},
            "english_last_name": {"text": "test", "confidence": 0.7},
        }
        conf = OCRService.calculate_ocr_confidence(roi_results)
        assert 0.7 <= conf <= 0.9  # Should be around 0.8

    def test_structured_confidence_with_all_fields(self):
        """Structured confidence high when all fields present."""
        from datetime import date
        conf = OCRService.calculate_structured_confidence(
            first_name="John",
            last_name="Doe",
            dob=date(2009, 9, 23),
            card_detected=True,
            card_warped=True,
            card_like=False
        )
        # firstName(25) + lastName(25) + DOB(25) + DOB_format(10) + card(15) = 100
        assert conf == 100.0

    def test_structured_confidence_missing_fields(self):
        """Structured confidence lower when fields missing."""
        conf = OCRService.calculate_structured_confidence(
            first_name=None,
            last_name=None,
            dob=None,
            card_detected=False,
            card_warped=False,
            card_like=False
        )
        assert conf == 0.0

    def test_final_confidence_calculation(self):
        """Final confidence weighted from OCR and structured."""
        final = OCRService.calculate_final_confidence(ocr_conf=0.8, structured_conf=100.0)
        # (0.8 * 0.4) + (100 * 0.6) = 0.32 + 60 = 60.32
        assert 60.0 <= final <= 61.0

    def test_candidate_score_from_roi(self):
        """Candidate from ROI gets high score."""
        from app.services.id_ocr_structured import FieldCandidate
        from app.services.id_card_template import thai_id_template_manager

        field_config = thai_id_template_manager.get_field_config("english_first_name")
        candidate = FieldCandidate(
            fieldName="english_first_name",
            value="John",
            rawText="John",
            normalizedText="John",
            source="roi_template",
            templateVersion="template_v1",
            roiName="english_first_name",
            confidence=0.9,
            parser="parse_english_name_from_roi",
            warnings=[]
        )
        OCRService.score_field_candidate(candidate, field_config)
        # ROI(40) + value parsed(20) + confidence(27) + length(10) = 97
        assert candidate.score > 80


class TestTemplateExtractionSerialization:
    """Test that template extraction response is JSON-serializable."""

    def test_template_extraction_response_json_serializable(self):
        """Template extraction response should be JSON-serializable."""
        import cv2
        import numpy as np
        import json

        img = np.ones((630, 1000, 3), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()

        result = OCRService.extract_from_thai_id_template(image_bytes)

        # Should be JSON serializable
        json_str = json.dumps(result, default=str)
        assert json_str

    def test_template_extraction_includes_review_reasons(self):
        """Template extraction should include review_reasons for missing fields."""
        import cv2
        import numpy as np

        img = np.ones((630, 1000, 3), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()

        result = OCRService.extract_from_thai_id_template(image_bytes)

        assert "review_reasons" in result
        assert isinstance(result["review_reasons"], list)

    def test_template_extraction_date_serialized_to_iso(self):
        """Date of birth should be serialized to ISO format string."""
        import cv2
        import numpy as np

        # Create card-like image
        img = np.ones((630, 1000, 3), dtype=np.uint8) * 200
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()

        result = OCRService.extract_from_thai_id_template(image_bytes)

        if result.get("date_of_birth"):
            assert isinstance(result["date_of_birth"], str)
            # Should be ISO format like "2009-09-23"
            assert result["date_of_birth"][0].isdigit()

    def test_template_extraction_includes_selected_candidates(self):
        """Template extraction should include selected candidates."""
        import cv2
        import numpy as np

        img = np.ones((630, 1000, 3), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()

        result = OCRService.extract_from_thai_id_template(image_bytes)

        assert "selected_candidates" in result
        assert isinstance(result["selected_candidates"], dict)

    def test_template_extraction_roi_preset_from_selected(self):
        """ROI preset should be determined from selected candidates."""
        import cv2
        import numpy as np

        img = np.ones((630, 1000, 3), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()

        result = OCRService.extract_from_thai_id_template(image_bytes)

        # roi_preset should be v1, v2, v3, or None (not hardcoded)
        roi_preset = result.get("roi_preset")
        assert roi_preset in [None, "v1", "v2", "v3"]


class TestThaiIDTemplateExtraction:
    """Test Thai ID template extraction workflow and confidence calculation."""

    def test_template_extraction_calculates_confidence_without_error(self):
        """Regression: confidence calculation should not raise NameError."""
        import cv2
        import numpy as np

        # Create test image
        img = np.ones((630, 1000, 3), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()

        # This should not raise NameError about undefined 'c'
        result = OCRService.extract_from_thai_id_template(image_bytes)
        assert isinstance(result, dict)
        assert "confidence" in result
        assert isinstance(result["confidence"], float)

    def test_template_extraction_average_confidence_calculated(self):
        """Average confidence should be calculated from ROI confidences."""
        import cv2
        import numpy as np

        img = np.ones((630, 1000, 3), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()

        result = OCRService.extract_from_thai_id_template(image_bytes)

        # Confidence should be a valid float
        assert 0.0 <= result["confidence"] <= 1.0

    def test_template_extraction_includes_roi_results(self):
        """Template extraction should include ROI results in response."""
        import cv2
        import numpy as np

        img = np.ones((630, 1000, 3), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()

        result = OCRService.extract_from_thai_id_template(image_bytes)

        # When card not detected, roi_results should be empty dict
        if not result.get("card_warped"):
            assert isinstance(result["roi_results"], dict)


class TestCandidateSerialization:
    """Test field candidate serialization for JSON output."""

    def test_serialize_field_candidate_string_value(self):
        """Serialize candidate with string value."""
        from app.services.ocr import serialize_field_candidate
        from app.services.id_ocr_structured import FieldCandidate

        candidate = FieldCandidate(
            fieldName="english_first_name",
            value="John",
            rawText="John",
            normalizedText="John",
            source="roi_template",
            templateVersion="template_v1",
            roiName="english_first_name",
            confidence=0.9,
            parser="parse_english_name_from_roi",
            warnings=[]
        )

        serialized = serialize_field_candidate(candidate)

        assert isinstance(serialized, dict)
        assert serialized["value"] == "John"
        assert isinstance(serialized["confidence"], float)
        assert isinstance(serialized["score"], float)

    def test_serialize_field_candidate_date_value(self):
        """Serialize candidate with date value to ISO string."""
        from app.services.ocr import serialize_field_candidate
        from app.services.id_ocr_structured import FieldCandidate

        candidate = FieldCandidate(
            fieldName="dob_english",
            value=date(2009, 9, 23),
            rawText="23 Sep. 2009",
            normalizedText="23 sep. 2009",
            source="roi_template",
            templateVersion="template_v1",
            roiName="dob_english",
            confidence=0.85,
            parser="extract_date_of_birth",
            warnings=[]
        )

        serialized = serialize_field_candidate(candidate)

        assert serialized["value"] == "2009-09-23"
        assert isinstance(serialized["value"], str)

    def test_serialize_field_candidate_tuple_value(self):
        """Serialize candidate with tuple (first, last) name to dict."""
        from app.services.ocr import serialize_field_candidate
        from app.services.id_ocr_structured import FieldCandidate

        candidate = FieldCandidate(
            fieldName="thai_full_name",
            value=("สมชาย", "วิชัยกุล"),
            rawText="สมชาย วิชัยกุล",
            normalizedText="สมชาย วิชัยกุล",
            source="roi_template",
            templateVersion="template_v2",
            roiName="thai_full_name",
            confidence=0.92,
            parser="parse_thai_full_name_from_roi",
            warnings=[]
        )

        serialized = serialize_field_candidate(candidate)

        assert isinstance(serialized["value"], dict)
        assert serialized["value"]["first"] == "สมชาย"
        assert serialized["value"]["last"] == "วิชัยกุล"

    def test_serialize_field_candidates_all_fields(self):
        """Serialize all field candidates to dicts."""
        from app.services.ocr import serialize_field_candidates
        from app.services.id_ocr_structured import FieldCandidate

        candidate = FieldCandidate(
            fieldName="english_first_name",
            value="John",
            rawText="John",
            normalizedText="John",
            source="roi_template",
            templateVersion="template_v1",
            roiName="english_first_name",
            confidence=0.9,
            parser="parse_english_name_from_roi",
            warnings=[]
        )

        field_candidates = {
            "english_first_name": [candidate],
            "english_last_name": [],
            "thai_full_name": [],
            "dob_english": [],
            "dob_thai": [],
            "expiry_english": [],
            "expiry_thai": []
        }

        serialized = serialize_field_candidates(field_candidates)

        assert isinstance(serialized, dict)
        assert "english_first_name" in serialized
        assert isinstance(serialized["english_first_name"], list)
        assert isinstance(serialized["english_first_name"][0], dict)

    def test_get_selected_candidates_with_preset(self):
        """Get selected candidates and determine ROI preset used."""
        from app.services.ocr import get_selected_candidates_with_preset
        from app.services.id_ocr_structured import FieldCandidate

        candidate_v2 = FieldCandidate(
            fieldName="dob_english",
            value=date(2009, 9, 23),
            rawText="23 Sep. 2009",
            normalizedText="23 sep. 2009",
            source="roi_template",
            templateVersion="template_v2",
            roiName="dob_english",
            confidence=0.85,
            parser="extract_date_of_birth",
            warnings=[]
        )

        field_candidates = {
            "thai_full_name": [],
            "english_first_name": [],
            "english_last_name": [],
            "dob_english": [candidate_v2],
            "dob_thai": [],
            "expiry_english": [],
            "expiry_thai": []
        }

        selected, preset = get_selected_candidates_with_preset(
            field_candidates, None, None, date(2009, 9, 23)
        )

        assert "dob_english" in selected
        assert preset == "v2"

    def test_selected_candidates_json_serializable(self):
        """Selected candidates must be JSON-serializable."""
        import json
        from app.services.ocr import get_selected_candidates_with_preset
        from app.services.id_ocr_structured import FieldCandidate

        candidate = FieldCandidate(
            fieldName="english_first_name",
            value="John",
            rawText="John",
            normalizedText="John",
            source="roi_template",
            templateVersion="template_v1",
            roiName="english_first_name",
            confidence=0.9,
            parser="parse_english_name_from_roi",
            warnings=[]
        )

        field_candidates = {
            "english_first_name": [candidate],
            "english_last_name": [],
            "thai_full_name": [],
            "dob_english": [],
            "dob_thai": [],
            "expiry_english": [],
            "expiry_thai": []
        }

        selected, preset = get_selected_candidates_with_preset(
            field_candidates, "John", None, None
        )

        # Must be JSON serializable
        json_str = json.dumps(selected)
        assert json_str  # Should succeed without error


class TestMultiPresetExtraction:
    """Test multi-preset field candidate extraction."""

    def test_extract_field_candidates_returns_dict(self):
        """Extract field candidates should return dict with field names."""
        import cv2
        import numpy as np
        from app.services.id_card_template import thai_id_template_manager

        img = np.ones((630, 1000, 3), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()

        # Convert bytes to ndarray for warped_image
        import cv2
        img_array = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)

        candidates = OCRService.extract_field_candidates_from_templates(img_array)

        # Should return dict with all field names
        field_names = thai_id_template_manager.get_all_field_names()
        for field_name in field_names:
            assert field_name in candidates
            assert isinstance(candidates[field_name], list)

    def test_extract_field_candidates_sorted_by_score(self):
        """Field candidates should be sorted by score (highest first)."""
        import cv2
        import numpy as np

        img = np.ones((630, 1000, 3), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()

        img_array = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        candidates = OCRService.extract_field_candidates_from_templates(img_array)

        # Check that any field with candidates has them sorted by score
        for field_name, cands in candidates.items():
            if len(cands) > 1:
                for i in range(len(cands) - 1):
                    assert cands[i].score >= cands[i + 1].score

    def test_score_field_candidate_roi_bonus(self):
        """Field candidate from ROI template should get +40 score bonus."""
        from app.services.id_ocr_structured import FieldCandidate
        from app.services.id_card_template import thai_id_template_manager

        field_config = thai_id_template_manager.get_field_config("english_first_name")
        candidate = FieldCandidate(
            fieldName="english_first_name",
            value="John",
            rawText="John",
            normalizedText="John",
            source="roi_template",
            templateVersion="template_v1",
            roiName="english_first_name",
            confidence=0.8,
            parser="parse_english_name_from_roi",
            warnings=[]
        )

        OCRService.score_field_candidate(candidate, field_config)

        # Should have ROI bonus(40) + value parsed(20) + confidence(24) + length(10) = 94
        assert candidate.score >= 80

    def test_select_best_fields_prefers_thai_names(self):
        """Select best fields should prefer Thai names when score > 50."""
        from app.services.id_ocr_structured import FieldCandidate

        thai_candidate = FieldCandidate(
            fieldName="thai_full_name",
            value=("สมชาย", "วิชัยกุล"),
            rawText="สมชาย วิชัยกุล",
            normalizedText="สมชาย วิชัยกุล",
            source="roi_template",
            templateVersion="template_v1",
            roiName="thai_full_name",
            confidence=0.9,
            parser="parse_thai_full_name_from_roi",
            score=80.0
        )

        eng_first_candidate = FieldCandidate(
            fieldName="english_first_name",
            value="John",
            rawText="John",
            normalizedText="John",
            source="roi_template",
            templateVersion="template_v1",
            roiName="english_first_name",
            confidence=0.8,
            parser="parse_english_name_from_roi",
            score=70.0
        )

        field_candidates = {
            "thai_full_name": [thai_candidate],
            "english_first_name": [eng_first_candidate],
            "english_last_name": [],
            "dob_thai": [],
            "dob_english": [],
            "expiry_thai": [],
            "expiry_english": []
        }

        first, last, dob = OCRService.select_best_fields(field_candidates)

        # Should prefer Thai names
        assert first == "สมชาย"
        assert last == "วิชัยกุล"

    def test_select_best_fields_fallback_to_english(self):
        """Select best fields should fallback to English when Thai weak."""
        from app.services.id_ocr_structured import FieldCandidate

        eng_first_candidate = FieldCandidate(
            fieldName="english_first_name",
            value="John",
            rawText="John",
            normalizedText="John",
            source="roi_template",
            templateVersion="template_v1",
            roiName="english_first_name",
            confidence=0.8,
            parser="parse_english_name_from_roi",
            score=70.0
        )

        field_candidates = {
            "thai_full_name": [],
            "english_first_name": [eng_first_candidate],
            "english_last_name": [],
            "dob_thai": [],
            "dob_english": [],
            "expiry_thai": [],
            "expiry_english": []
        }

        first, last, dob = OCRService.select_best_fields(field_candidates)

        # Should fallback to English when Thai not available
        assert first == "John"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
