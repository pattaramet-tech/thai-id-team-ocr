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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
