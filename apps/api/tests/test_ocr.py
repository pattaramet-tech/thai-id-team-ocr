import pytest
from app.services.ocr import OCRService


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
