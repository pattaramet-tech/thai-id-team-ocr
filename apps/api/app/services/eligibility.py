from datetime import date
from typing import Dict, Literal

EligibilityStatus = Literal["eligible", "over_age", "unknown"]


def get_age_limit(age_group: str) -> int:
    """Extract age limit from age group string (e.g., 'U18' -> 18)."""
    try:
        return int(age_group.replace("U", "").replace("u", ""))
    except (ValueError, AttributeError):
        return 0


def get_min_birth_year_be(age_group: str, competition_year_be: int) -> int:
    """
    Calculate minimum birth year in Buddhist Era.

    Formula: competitionYearBE - ageLimit
    Example: U18 in 2569 BE -> 2569 - 18 = 2551 BE (minimum birth year)
    """
    age_limit = get_age_limit(age_group)
    return competition_year_be - age_limit


def gregorian_to_be(gregorian_year: int) -> int:
    """Convert Gregorian year to Buddhist Era year."""
    return gregorian_year + 543


def date_to_birth_year_be(date_of_birth: date) -> int:
    """Convert date of birth to Buddhist Era birth year."""
    if not date_of_birth:
        return None
    gregorian_year = date_of_birth.year
    return gregorian_to_be(gregorian_year)


def check_player_eligibility(
    age_group: str,
    competition_year_be: int,
    birth_year_be: int = None
) -> Dict[str, str]:
    """
    Check player eligibility based on age group and birth year.

    Args:
        age_group: Age group (e.g., 'U18', 'U16')
        competition_year_be: Competition year in Buddhist Era (e.g., 2569)
        birth_year_be: Player's birth year in Buddhist Era (optional)

    Returns:
        Dictionary with 'status' and 'note' keys
        status: 'eligible', 'over_age', or 'unknown'
    """
    if not birth_year_be:
        return {
            "status": "unknown",
            "note": "ยังไม่ได้กรอกวันเกิด"
        }

    min_birth_year_be = get_min_birth_year_be(age_group, competition_year_be)

    if birth_year_be >= min_birth_year_be:
        return {
            "status": "eligible",
            "note": f"ผ่านเกณฑ์ {age_group} ต้องเกิด พ.ศ. {min_birth_year_be} ขึ้นไป"
        }

    return {
        "status": "over_age",
        "note": f"อายุเกินรุ่น {age_group} ต้องเกิด พ.ศ. {min_birth_year_be} ขึ้นไป"
    }


def check_eligibility_for_player(
    age_group: str,
    competition_year_be: int,
    date_of_birth: date = None
) -> Dict[str, str]:
    """
    Check player eligibility from date of birth.

    Args:
        age_group: Age group
        competition_year_be: Competition year in BE
        date_of_birth: Player's date of birth (optional)

    Returns:
        Dictionary with 'status' and 'note' keys
    """
    if not date_of_birth:
        return {
            "status": "unknown",
            "note": "ยังไม่ได้กรอกวันเกิด"
        }

    birth_year_be = date_to_birth_year_be(date_of_birth)
    return check_player_eligibility(age_group, competition_year_be, birth_year_be)
