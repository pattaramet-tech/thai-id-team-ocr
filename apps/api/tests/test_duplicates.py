"""Tests for fuzzy duplicate detection."""
import pytest
from app.services.duplicates import DuplicateDetectionService
from app.models import Team, Player
from datetime import date


class TestDuplicateDetection:
    """Test fuzzy duplicate detection service."""

    def test_normalize_name_removes_titles(self):
        """Normalization removes Thai titles."""
        assert DuplicateDetectionService.normalize_name("นาย สมชาย วิวัฒน์") == "สมชาย วิวัฒน์"
        assert DuplicateDetectionService.normalize_name("นางสาว ปรีย์ ใจดี") == "ปรีย์ ใจดี"
        assert DuplicateDetectionService.normalize_name("เด็กชาย ขาว หลี") == "ขาว หลี"

    def test_normalize_name_collapses_spaces(self):
        """Normalization collapses multiple spaces."""
        assert DuplicateDetectionService.normalize_name("สมชาย   วิวัฒน์") == "สมชาย วิวัฒน์"

    def test_normalize_name_lowercases(self):
        """Normalization converts to lowercase."""
        assert DuplicateDetectionService.normalize_name("John Smith") == "john smith"

    def test_calculate_similarity_exact_match(self):
        """Exact match has similarity 1.0."""
        similarity = DuplicateDetectionService.calculate_similarity("สมชาย วิวัฒน์", "สมชาย วิวัฒน์")
        assert similarity == 1.0

    def test_calculate_similarity_with_title_differences(self):
        """Similarity handles title differences well."""
        similarity1 = DuplicateDetectionService.calculate_similarity("นาย สมชาย วิวัฒน์", "สมชาย วิวัฒน์")
        similarity2 = DuplicateDetectionService.calculate_similarity("นางสาว สมชาย วิวัฒน์", "สมชาย วิวัฒน์")
        # Both should be high similarity (after title removal they're nearly identical)
        assert similarity1 > 0.95
        assert similarity2 > 0.85

    def test_calculate_similarity_similar_names(self):
        """Similar names have high similarity."""
        # One character difference
        similarity = DuplicateDetectionService.calculate_similarity("สมชาย วิวัฒน์", "สมชาญ วิวัฒน์")
        assert similarity > 0.85

    def test_calculate_similarity_different_names(self):
        """Different names have low similarity."""
        similarity = DuplicateDetectionService.calculate_similarity("สมชาย วิวัฒน์", "สมหญิง ใจดี")
        assert similarity < 0.7

    def test_find_fuzzy_duplicates_exact_match(self):
        """Finding exact duplicate returns match."""
        existing = [
            {'id': 1, 'fullName': 'สมชาย วิวัฒน์', 'firstName': 'สมชาย', 'lastName': 'วิวัฒน์'}
        ]
        matches = DuplicateDetectionService.find_fuzzy_duplicates(
            "สมชาย วิวัฒน์",
            existing,
            threshold=0.88
        )
        assert len(matches) == 1
        assert matches[0]['matchedPlayerId'] == 1
        assert matches[0]['similarity'] == 100.0

    def test_find_fuzzy_duplicates_above_threshold(self):
        """Finding similar name above threshold returns match."""
        existing = [
            {'id': 1, 'fullName': 'สมชาย วิวัฒน์', 'firstName': 'สมชาย', 'lastName': 'วิวัฒน์'}
        ]
        # Single character difference
        matches = DuplicateDetectionService.find_fuzzy_duplicates(
            "สมชาญ วิวัฒน์",
            existing,
            threshold=0.88
        )
        assert len(matches) == 1

    def test_find_fuzzy_duplicates_below_threshold(self):
        """Finding name below threshold returns no match."""
        existing = [
            {'id': 1, 'fullName': 'สมชาย วิวัฒน์', 'firstName': 'สมชาย', 'lastName': 'วิวัฒน์'}
        ]
        matches = DuplicateDetectionService.find_fuzzy_duplicates(
            "เจษฎา คำสิงห์",
            existing,
            threshold=0.88
        )
        assert len(matches) == 0

    def test_find_fuzzy_duplicates_multiple_candidates(self):
        """Finding duplicates checks all candidates."""
        existing = [
            {'id': 1, 'fullName': 'สมชาย วิวัฒน์', 'firstName': 'สมชาย', 'lastName': 'วิวัฒน์'},
            {'id': 2, 'fullName': 'สมชาญ วิวัฒน์', 'firstName': 'สมชาญ', 'lastName': 'วิวัฒน์'},
            {'id': 3, 'fullName': 'เจษฎา คำสิงห์', 'firstName': 'เจษฎา', 'lastName': 'คำสิงห์'}
        ]
        matches = DuplicateDetectionService.find_fuzzy_duplicates(
            "สมชาย วิวัฒน์",
            existing,
            threshold=0.88
        )
        assert len(matches) >= 1
        assert any(m['matchedPlayerId'] == 1 for m in matches)

    def test_check_team_duplicates(self, db_session):
        """Checking duplicates in a team works."""
        # Create team and players
        team = Team(
            name="Test Team",
            ageGroup="U18",
            gender="Male",
            competitionYearBE=2569
        )
        db_session.add(team)
        db_session.commit()

        player = Player(
            teamId=team.id,
            firstName="สมชาย",
            lastName="วิวัฒน์",
            fullName="สมชาย วิวัฒน์",
            sourceFilename="test.jpg",
            ocrText="test",
            confidence=0.9,
            status="verified"
        )
        db_session.add(player)
        db_session.commit()

        # Check for duplicate
        matches = DuplicateDetectionService.check_team_duplicates(
            team.id,
            "สมชาย วิวัฒน์",
            db_session
        )
        assert len(matches) == 1
        assert matches[0]['matchedPlayerId'] == player.id
