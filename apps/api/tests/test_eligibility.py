import pytest
from datetime import date
from app.services.eligibility import (
    get_age_limit,
    get_min_birth_year_be,
    gregorian_to_be,
    date_to_birth_year_be,
    check_player_eligibility,
    check_eligibility_for_player
)


class TestAgeLimit:
    """Test age limit extraction from age group strings."""

    def test_extract_u18(self):
        assert get_age_limit("U18") == 18

    def test_extract_u16(self):
        assert get_age_limit("U16") == 16

    def test_extract_u14(self):
        assert get_age_limit("U14") == 14

    def test_lowercase_u18(self):
        assert get_age_limit("u18") == 18

    def test_invalid_age_group(self):
        assert get_age_limit("Invalid") == 0


class TestMinBirthYear:
    """Test minimum birth year calculation."""

    def test_u18_2569_min_birth_year(self):
        # U18 in 2569 BE -> min birth year = 2569 - 18 = 2551
        result = get_min_birth_year_be("U18", 2569)
        assert result == 2551

    def test_u16_2569_min_birth_year(self):
        # U16 in 2569 BE -> min birth year = 2569 - 16 = 2553
        result = get_min_birth_year_be("U16", 2569)
        assert result == 2553

    def test_u14_2569_min_birth_year(self):
        # U14 in 2569 BE -> min birth year = 2569 - 14 = 2555
        result = get_min_birth_year_be("U14", 2569)
        assert result == 2555


class TestGregorianToBE:
    """Test Gregorian to Buddhist Era conversion."""

    def test_2005_gregorian_to_be(self):
        # 2005 + 543 = 2548 BE
        assert gregorian_to_be(2005) == 2548

    def test_2004_gregorian_to_be(self):
        # 2004 + 543 = 2547 BE
        assert gregorian_to_be(2004) == 2547

    def test_2026_gregorian_to_be(self):
        # 2026 + 543 = 2569 BE
        assert gregorian_to_be(2026) == 2569


class TestDateToBirthYear:
    """Test date to Buddhist Era birth year conversion."""

    def test_date_2005_01_15(self):
        # Born 2005-01-15 -> birth year 2548 BE
        birth_date = date(2005, 1, 15)
        assert date_to_birth_year_be(birth_date) == 2548

    def test_date_2004_12_31(self):
        # Born 2004-12-31 -> birth year 2547 BE
        birth_date = date(2004, 12, 31)
        assert date_to_birth_year_be(birth_date) == 2547

    def test_date_2000_06_01(self):
        # Born 2000-06-01 -> birth year 2543 BE
        birth_date = date(2000, 6, 1)
        assert date_to_birth_year_be(birth_date) == 2543


class TestCheckPlayerEligibility:
    """Test player eligibility checking."""

    def test_u18_2569_eligible_birth_2552(self):
        # U18 in 2569: min birth year = 2551
        # Birth 2552 >= 2551 = eligible
        result = check_player_eligibility("U18", 2569, 2552)
        assert result["status"] == "eligible"
        assert "2551" in result["note"]

    def test_u18_2569_eligible_birth_2551(self):
        # U18 in 2569: min birth year = 2551
        # Birth 2551 >= 2551 = eligible
        result = check_player_eligibility("U18", 2569, 2551)
        assert result["status"] == "eligible"

    def test_u18_2569_over_age_birth_2550(self):
        # U18 in 2569: min birth year = 2551
        # Birth 2550 < 2551 = over_age
        result = check_player_eligibility("U18", 2569, 2550)
        assert result["status"] == "over_age"
        assert "อายุเกินรุ่น" in result["note"]

    def test_u18_2569_over_age_birth_2540(self):
        # U18 in 2569: min birth year = 2551
        # Birth 2540 < 2551 = over_age
        result = check_player_eligibility("U18", 2569, 2540)
        assert result["status"] == "over_age"

    def test_u16_2569_eligible_birth_2554(self):
        # U16 in 2569: min birth year = 2553
        # Birth 2554 >= 2553 = eligible
        result = check_player_eligibility("U16", 2569, 2554)
        assert result["status"] == "eligible"

    def test_u16_2569_over_age_birth_2552(self):
        # U16 in 2569: min birth year = 2553
        # Birth 2552 < 2553 = over_age
        result = check_player_eligibility("U16", 2569, 2552)
        assert result["status"] == "over_age"

    def test_unknown_no_birth_year(self):
        # No birth year = unknown
        result = check_player_eligibility("U18", 2569, None)
        assert result["status"] == "unknown"
        assert "ยังไม่ได้กรอก" in result["note"]


class TestCheckEligibilityForPlayer:
    """Test eligibility checking from date of birth."""

    def test_eligible_with_date(self):
        # U18 in 2569, born 2005-01-15 (BE 2548)
        # 2548 < 2551 (min for U18) = over_age
        birth_date = date(2005, 1, 15)
        result = check_eligibility_for_player("U18", 2569, birth_date)
        assert result["status"] == "over_age"

    def test_eligible_with_recent_date(self):
        # U18 in 2569, born 2008-06-01 (BE 2551)
        # 2551 >= 2551 (min for U18) = eligible
        birth_date = date(2008, 6, 1)
        result = check_eligibility_for_player("U18", 2569, birth_date)
        assert result["status"] == "eligible"

    def test_unknown_no_date(self):
        # No birth date = unknown
        result = check_eligibility_for_player("U18", 2569, None)
        assert result["status"] == "unknown"


class TestEligibilityEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_multiple_years_same_month(self):
        # Test birth year changes within same month
        birth_2551 = date(2008, 6, 1)  # BE 2551
        birth_2550 = date(2007, 6, 1)  # BE 2550

        result_2551 = check_eligibility_for_player("U18", 2569, birth_2551)
        result_2550 = check_eligibility_for_player("U18", 2569, birth_2550)

        assert result_2551["status"] == "eligible"
        assert result_2550["status"] == "over_age"

    def test_different_competition_years(self):
        # Same birth year, different competition years
        birth_year = 2550

        result_2568 = check_player_eligibility("U18", 2568, birth_year)
        result_2569 = check_player_eligibility("U18", 2569, birth_year)
        result_2570 = check_player_eligibility("U18", 2570, birth_year)

        # 2550 < 2550 (2568-18) = eligible
        assert result_2568["status"] == "eligible"
        # 2550 < 2551 (2569-18) = over_age
        assert result_2569["status"] == "over_age"
        # 2550 < 2552 (2570-18) = over_age
        assert result_2570["status"] == "over_age"
