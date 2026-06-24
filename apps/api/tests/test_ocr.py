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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
