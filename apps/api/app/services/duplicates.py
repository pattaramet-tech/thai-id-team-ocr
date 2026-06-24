from difflib import SequenceMatcher
from typing import Optional, List, Dict
import re


class DuplicateDetectionService:
    """Service for detecting fuzzy duplicate names."""

    @staticmethod
    def normalize_name(name: str) -> str:
        """
        Normalize name for comparison.
        - Trim whitespace
        - Collapse multiple spaces
        - Remove Thai titles
        - Lowercase for comparison
        """
        if not name:
            return ""

        normalized = name.strip()

        # Remove Thai titles (longest first to avoid partial matches)
        titles = ['นางสาว', 'เด็กหญิง', 'เด็กชาย', 'นาย', 'นาง', 'ด.ช.', 'ด.ญ.']
        for title in titles:
            # Remove title at the beginning with word boundary
            if normalized.startswith(title):
                normalized = normalized[len(title):]
                break

        # Collapse spaces
        normalized = ' '.join(normalized.split())

        # Lowercase for comparison
        normalized = normalized.lower()

        return normalized

    @staticmethod
    def calculate_similarity(name1: str, name2: str) -> float:
        """Calculate similarity ratio between two names (0.0 to 1.0)."""
        norm1 = DuplicateDetectionService.normalize_name(name1)
        norm2 = DuplicateDetectionService.normalize_name(name2)

        if not norm1 or not norm2:
            return 0.0

        matcher = SequenceMatcher(None, norm1, norm2)
        return matcher.ratio()

    @staticmethod
    def find_fuzzy_duplicates(
        candidate_name: str,
        existing_names: List[Dict],
        threshold: float = 0.88
    ) -> List[Dict]:
        """
        Find fuzzy duplicates of a candidate name in existing names list.

        Args:
            candidate_name: Name to check
            existing_names: List of dicts with 'id', 'fullName', 'firstName', 'lastName'
            threshold: Similarity threshold (default 0.88)

        Returns:
            List of matches with structure:
            {
                'candidateName': str,
                'matchedPlayerId': int,
                'matchedFullName': str,
                'similarity': float,
                'reason': str
            }
        """
        matches = []

        for existing in existing_names:
            full_name = existing.get('fullName') or ''
            similarity = DuplicateDetectionService.calculate_similarity(
                candidate_name, full_name
            )

            if similarity >= threshold:
                matches.append({
                    'candidateName': candidate_name,
                    'matchedPlayerId': existing.get('id'),
                    'matchedFullName': full_name,
                    'similarity': round(similarity * 100, 1),
                    'reason': f"Similar name (match: {round(similarity * 100, 0):.0f}%)"
                })

        return matches

    @staticmethod
    def check_team_duplicates(
        team_id: int,
        new_full_name: str,
        db_session,
        threshold: float = 0.88
    ) -> List[Dict]:
        """
        Check if a new name has duplicates in a team.

        Args:
            team_id: Team ID to check
            new_full_name: New name to check
            db_session: SQLAlchemy session
            threshold: Similarity threshold

        Returns:
            List of matching players in that team
        """
        from app.models import Player, Team

        team = db_session.query(Team).filter(Team.id == team_id).first()
        if not team:
            return []

        # Get all players in team
        players = db_session.query(Player).filter(Player.teamId == team_id).all()

        existing_names = [
            {
                'id': p.id,
                'fullName': p.fullName or '',
                'firstName': p.firstName or '',
                'lastName': p.lastName or ''
            }
            for p in players
        ]

        return DuplicateDetectionService.find_fuzzy_duplicates(
            new_full_name,
            existing_names,
            threshold
        )
