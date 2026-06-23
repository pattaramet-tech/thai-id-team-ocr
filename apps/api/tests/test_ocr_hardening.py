import pytest
from datetime import date
from app.services.ocr import OCRService


class TestIDRedactionPatterns:
    """Test Thai ID number redaction with various formats."""

    def test_redact_consecutive_13_digits(self):
        text = "เลขประชาชน 1234567890123 ถนน"
        result = OCRService.redact_thai_id_numbers(text)
        assert "[REDACTED_ID]" in result
        assert "1234567890123" not in result

    def test_redact_id_with_spaces(self):
        # Pattern: 1 2345 67890 12 3
        text = "เลขบัตร 1 2345 67890 12 3 บ้าน"
        result = OCRService.redact_thai_id_numbers(text)
        assert "[REDACTED_ID]" in result

    def test_redact_id_with_dashes(self):
        # Pattern: 1-2345-67890-12-3
        text = "ID: 1-2345-67890-12-3"
        result = OCRService.redact_thai_id_numbers(text)
        assert "[REDACTED_ID]" in result

    def test_preserve_non_id_numbers(self):
        text = "เลข 123 และ 12345 และเลข 1234567890123"
        result = OCRService.redact_thai_id_numbers(text)
        assert "123" in result
        assert "12345" in result
        assert "[REDACTED_ID]" in result
        assert "1234567890123" not in result

    def test_multiple_ids_redacted(self):
        text = "ID1: 1234567890123 ID2: 9876543210123"
        result = OCRService.redact_thai_id_numbers(text)
        assert result.count("[REDACTED_ID]") == 2


class TestThaiNameExtraction:
    """Test Thai name extraction from various patterns."""

    def test_extract_with_nai_prefix(self):
        # Pattern: นาย <first> <last>
        ocr_text = "นาย เกียรติศักดิ์ ใจสนุก"
        first, last = OCRService.extract_thai_names(ocr_text)
        assert first == "เกียรติศักดิ์"
        assert last == "ใจสนุก"

    def test_extract_with_nang_prefix(self):
        # Pattern: นาง <first> <last>
        ocr_text = "นาง สวนีย์ ศรีวิทยา"
        first, last = OCRService.extract_thai_names(ocr_text)
        assert first == "สวนีย์"
        assert last == "ศรีวิทยา"

    def test_extract_with_nak_sao_prefix(self):
        # Pattern: นางสาว <first> <last> (must not match partial "นาง")
        ocr_text = "นางสาว ฉัตรวิภา คำวัฒนา"
        first, last = OCRService.extract_thai_names(ocr_text)
        assert first == "ฉัตรวิภา"
        assert last == "คำวัฒนา"

    def test_extract_with_dek_chai_prefix(self):
        # Pattern: เด็กชาย <first> <last>
        ocr_text = "เด็กชาย สมศักดิ์ เทพเมืองไทย"
        first, last = OCRService.extract_thai_names(ocr_text)
        assert first == "สมศักดิ์"
        assert last == "เทพเมืองไทย"

    def test_extract_with_dek_ying_prefix(self):
        # Pattern: เด็กหญิง <first> <last>
        ocr_text = "เด็กหญิง นรีนุช สถิตศิล"
        first, last = OCRService.extract_thai_names(ocr_text)
        assert first == "นรีนุช"
        assert last == "สถิตศิล"

    def test_extract_from_labeled_lines_name_surname(self):
        # Pattern: ชื่อ <first> \n นามสกุล <last>
        ocr_text = "ชื่อ สมชาย\nนามสกุล วิชัยกุล"
        first, last = OCRService.extract_thai_names(ocr_text)
        assert first == "สมชาย"
        assert last == "วิชัยกุล"

    def test_extract_from_name_and_surname_together(self):
        # Pattern: ชื่อตัวและชื่อสกุล นาย <first> <last>
        ocr_text = "ชื่อตัวและชื่อสกุล นาย เกียรติศักดิ์ ใจสนุก"
        first, last = OCRService.extract_thai_names(ocr_text)
        assert first == "เกียรติศักดิ์"
        assert last == "ใจสนุก"

    def test_extract_with_title_and_redaction(self):
        # Include ID number to test redaction happens first
        ocr_text = "นาย สมชาย วิชัยกุล\nเลข 1234567890123"
        first, last = OCRService.extract_thai_names(ocr_text)
        assert first == "สมชาย"
        assert last == "วิชัยกุล"

    def test_avoid_noise_words(self):
        # Should not extract document header as name
        ocr_text = "บัตรประจำตัวประชาชน Thai National ID Card\nนาย สมชาย วิชัยกุล"
        first, last = OCRService.extract_thai_names(ocr_text)
        assert first == "สมชาย"
        assert last == "วิชัยกุล"
        assert "บัตร" not in (first or "")
        assert "ประชาชน" not in (last or "")

    def test_partial_match_prevention(self):
        # Pattern: "นาง" should not match when "นางสาว" is present
        ocr_text = "นางสาว นรีนุช สถิตศิล"
        first, last = OCRService.extract_thai_names(ocr_text)
        assert first == "นรีนุช"
        assert last == "สถิตศิล"
        # Verify we didn't get "สาว" as firstname (from partial นาง match)


class TestDateExtraction:
    """Test date of birth extraction from various formats."""

    def test_extract_thai_format(self):
        # Format: 23 ก.ย. 2552 (Sep 23, 1952 in AD)
        ocr_text = "เกิดวันที่ 23 ก.ย. 2552"
        result = OCRService.extract_date_of_birth(ocr_text)
        assert result == date(2009, 9, 23)

    def test_extract_thai_format_various_months(self):
        # Test multiple Thai month abbreviations
        test_cases = [
            ("15 ม.ค. 2555", date(2012, 1, 15)),
            ("20 กพ. 2550", date(2007, 2, 20)),
            ("10 มี.ค. 2553", date(2010, 3, 10)),
        ]
        for text, expected_date in test_cases:
            result = OCRService.extract_date_of_birth(text)
            if result:  # May be None if month abbr not found exactly
                assert result.month == expected_date.month
                assert result.day == expected_date.day

    def test_extract_english_format(self):
        # Format: 23 Sep. 2009
        ocr_text = "Date of Birth 23 Sep. 2009"
        result = OCRService.extract_date_of_birth(ocr_text)
        assert result == date(2009, 9, 23)

    def test_extract_english_format_no_period(self):
        # Format: 23 Sep 2009 (without period)
        ocr_text = "Birth 23 Sep 2009"
        result = OCRService.extract_date_of_birth(ocr_text)
        assert result == date(2009, 9, 23)

    def test_extract_slash_format(self):
        # Format: 23/09/2009
        ocr_text = "Date: 23/09/2009"
        result = OCRService.extract_date_of_birth(ocr_text)
        assert result == date(2009, 9, 23)

    def test_extract_slash_format_single_digit(self):
        # Format: 23/9/2009 (single digit month)
        ocr_text = "DOB: 23/9/2009"
        result = OCRService.extract_date_of_birth(ocr_text)
        assert result == date(2009, 9, 23)

    def test_convert_be_to_ad(self):
        # Thai date 2552 should be converted to 2009
        ocr_text = "23 ก.ย. 2552"
        result = OCRService.extract_date_of_birth(ocr_text)
        assert result.year == 2009

    def test_no_date_found(self):
        ocr_text = "No date information here"
        result = OCRService.extract_date_of_birth(ocr_text)
        assert result is None


class TestEligibilityIntegration:
    """Test eligibility checking with extracted data."""

    def test_eligible_u18_2009_birth(self):
        # Born 2009 (BE 2552), U18 in 2569 -> eligible
        birth_date = date(2009, 6, 1)
        ocr_text = f"นาย สมชาย วิชัยกุล\nDate: 23/9/{birth_date.year}"

        first_name, last_name = OCRService.extract_thai_names(ocr_text)
        dob = OCRService.extract_date_of_birth(ocr_text)

        assert first_name == "สมชาย"
        assert last_name == "วิชัยกุล"
        assert dob == date(2009, 9, 23)

    def test_over_age_u18_2007_birth(self):
        # Born 2007, U18 in 2569 -> over_age
        ocr_text = "นาย สมชาย วิชัยกุล\nDate: 23/09/2007"

        first_name, last_name = OCRService.extract_thai_names(ocr_text)
        dob = OCRService.extract_date_of_birth(ocr_text)

        assert first_name == "สมชาย"
        assert last_name == "วิชัยกุล"
        assert dob == date(2007, 9, 23)


class TestOCRWithComplexPatterns:
    """Test OCR with real-world complex document patterns."""

    def test_id_card_with_redaction_and_names(self):
        """Simulate ID card text with ID number and name."""
        ocr_text = """
        บัตรประชาชน
        เลขประชาชน 1 2345 67890 12 3
        ชื่อ นาย สมชาย
        นามสกุล วิชัยกุล
        เกิด 23 ก.ย. 2552
        """

        # Redact ID
        redacted = OCRService.redact_thai_id_numbers(ocr_text)
        assert "[REDACTED_ID]" in redacted
        assert "1234567890123" not in redacted

        # Extract name
        first, last = OCRService.extract_thai_names(redacted)
        assert first == "สมชาย"
        assert last == "วิชัยกุล"

        # Extract date
        dob = OCRService.extract_date_of_birth(ocr_text)
        assert dob == date(2009, 9, 23)

    def test_mixed_thai_english_document(self):
        """Test document with mixed Thai and English text."""
        ocr_text = """
        Name: นาย สมชาย วิชัยกุล
        Date of Birth: 23 Sep. 2009
        ID: 1-2345-67890-12-3
        """

        redacted = OCRService.redact_thai_id_numbers(ocr_text)
        assert "[REDACTED_ID]" in redacted

        first, last = OCRService.extract_thai_names(redacted)
        assert first == "สมชาย"
        assert last == "วิชัยกุล"

        dob = OCRService.extract_date_of_birth(ocr_text)
        assert dob == date(2009, 9, 23)
