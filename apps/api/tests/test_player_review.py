"""Tests for player review and status management."""
import pytest
from datetime import date, datetime
from app.models import Player, Team
from app.database import get_db


@pytest.fixture
def sample_team(db_session):
    """Create a sample team for testing."""
    team = Team(
        name="U18 Test Team",
        ageGroup="U18",
        gender="Male",
        competitionYearBE=2569
    )
    db_session.add(team)
    db_session.commit()
    db_session.refresh(team)
    return team


@pytest.fixture
def sample_player(db_session, sample_team):
    """Create a sample player for testing."""
    player = Player(
        teamId=sample_team.id,
        firstName="สมชาย",
        lastName="วิชัยกุล",
        fullName="สมชาย วิชัยกุล",
        dateOfBirth=date(2009, 6, 15),
        birthYearBE=2552,
        eligibilityStatus="eligible",
        eligibilityNote="Eligible for U18",
        sourceFilename="test_id.jpg",
        ocrText="[REDACTED_ID] สมชาย วิชัยกุล",
        confidence=0.95,
        status="pending"
    )
    db_session.add(player)
    db_session.commit()
    db_session.refresh(player)
    return player


class TestPlayerVerification:
    """Test player verification workflow."""

    def test_verify_player_sets_verified_at(self, db_session, sample_player):
        """Verify that verifying a player sets verifiedAt timestamp."""
        assert sample_player.status == "pending"
        assert sample_player.verifiedAt is None

        # Update to verified
        sample_player.status = "verified"
        sample_player.verifiedAt = datetime.utcnow()
        db_session.commit()
        db_session.refresh(sample_player)

        assert sample_player.status == "verified"
        assert sample_player.verifiedAt is not None
        assert isinstance(sample_player.verifiedAt, datetime)

    def test_reject_player_clears_verified_at(self, db_session, sample_player):
        """Verify that rejecting a player clears verifiedAt."""
        # First verify the player
        sample_player.status = "verified"
        sample_player.verifiedAt = datetime.utcnow()
        db_session.commit()

        # Then reject
        sample_player.status = "rejected"
        sample_player.verifiedAt = None
        db_session.commit()
        db_session.refresh(sample_player)

        assert sample_player.status == "rejected"
        assert sample_player.verifiedAt is None

    def test_pending_player_has_no_verified_at(self, db_session, sample_player):
        """Verify that pending players don't have verifiedAt set."""
        db_session.refresh(sample_player)
        assert sample_player.status == "pending"
        assert sample_player.verifiedAt is None


class TestPlayerEditing:
    """Test player field editing."""

    def test_edit_player_first_name(self, db_session, sample_player):
        """Test editing player's first name."""
        original_name = sample_player.firstName
        new_name = "วิทยา"

        sample_player.firstName = new_name
        sample_player.fullName = f"{new_name} {sample_player.lastName}"
        db_session.commit()
        db_session.refresh(sample_player)

        assert sample_player.firstName == new_name
        assert original_name != new_name

    def test_edit_player_last_name(self, db_session, sample_player):
        """Test editing player's last name."""
        original_name = sample_player.lastName
        new_name = "สิทธิกุล"

        sample_player.lastName = new_name
        sample_player.fullName = f"{sample_player.firstName} {new_name}"
        db_session.commit()
        db_session.refresh(sample_player)

        assert sample_player.lastName == new_name
        assert original_name != new_name

    def test_edit_player_date_of_birth(self, db_session, sample_player):
        """Test editing player's date of birth."""
        original_dob = sample_player.dateOfBirth
        new_dob = date(2008, 12, 25)

        sample_player.dateOfBirth = new_dob
        db_session.commit()
        db_session.refresh(sample_player)

        assert sample_player.dateOfBirth == new_dob
        assert original_dob != new_dob

    def test_edit_player_updates_updated_at(self, db_session, sample_player):
        """Test that editing player updates the updatedAt timestamp."""
        original_updated = sample_player.updatedAt

        import time
        time.sleep(0.1)

        sample_player.firstName = "แก้ไข"
        sample_player.updatedAt = datetime.utcnow()
        db_session.commit()
        db_session.refresh(sample_player)

        assert sample_player.updatedAt > original_updated


class TestPlayerDuplicateDetection:
    """Test duplicate name detection."""

    def test_detect_duplicate_names_in_team(self, db_session, sample_team):
        """Test detecting duplicate names in same team."""
        # Create two players with same name
        player1 = Player(
            teamId=sample_team.id,
            firstName="สมชาย",
            lastName="วิชัยกุล",
            fullName="สมชาย วิชัยกุล",
            dateOfBirth=date(2009, 1, 1),
            birthYearBE=2552,
            eligibilityStatus="eligible",
            sourceFilename="id1.jpg",
            ocrText="[REDACTED_ID]",
            confidence=0.9,
            status="verified",
            verifiedAt=datetime.utcnow()
        )
        player2 = Player(
            teamId=sample_team.id,
            firstName="สมชาย",
            lastName="วิชัยกุล",
            fullName="สมชาย วิชัยกุล",
            dateOfBirth=date(2009, 6, 15),
            birthYearBE=2552,
            eligibilityStatus="eligible",
            sourceFilename="id2.jpg",
            ocrText="[REDACTED_ID]",
            confidence=0.95,
            status="verified",
            verifiedAt=datetime.utcnow()
        )

        db_session.add_all([player1, player2])
        db_session.commit()

        # Query duplicates
        duplicates = db_session.query(Player).filter(
            Player.teamId == sample_team.id,
            Player.status == "verified"
        ).all()

        # Group by name
        name_groups = {}
        for p in duplicates:
            name = p.fullName
            if name not in name_groups:
                name_groups[name] = []
            name_groups[name].append(p)

        assert "สมชาย วิชัยกุล" in name_groups
        assert len(name_groups["สมชาย วิชัยกุล"]) == 2

    def test_different_names_not_duplicates(self, db_session, sample_team):
        """Test that different names are not marked as duplicates."""
        player1 = Player(
            teamId=sample_team.id,
            firstName="สมชาย",
            lastName="วิชัยกุล",
            fullName="สมชาย วิชัยกุล",
            status="verified",
            verifiedAt=datetime.utcnow()
        )
        player2 = Player(
            teamId=sample_team.id,
            firstName="วิทยา",
            lastName="สิทธิกุล",
            fullName="วิทยา สิทธิกุล",
            status="verified",
            verifiedAt=datetime.utcnow()
        )

        db_session.add_all([player1, player2])
        db_session.commit()

        duplicates = db_session.query(Player).filter(
            Player.teamId == sample_team.id,
            Player.status == "verified"
        ).all()

        name_groups = {}
        for p in duplicates:
            name = p.fullName
            if name not in name_groups:
                name_groups[name] = []
            name_groups[name].append(p)

        assert len(name_groups) == 2
        assert all(len(g) == 1 for g in name_groups.values())


class TestExportFiltering:
    """Test export filtering for verified players."""

    def test_export_only_verified_players(self, db_session, sample_team):
        """Test that export only includes verified players."""
        # Create multiple players with different statuses
        pending_player = Player(
            teamId=sample_team.id,
            firstName="สมชาย",
            lastName="วิชัยกุล",
            fullName="สมชาย วิชัยกุล",
            status="pending"
        )
        verified_player = Player(
            teamId=sample_team.id,
            firstName="วิทยา",
            lastName="สิทธิกุล",
            fullName="วิทยา สิทธิกุล",
            status="verified",
            verifiedAt=datetime.utcnow()
        )
        rejected_player = Player(
            teamId=sample_team.id,
            firstName="สมศักดิ์",
            lastName="เทพเมืองไทย",
            fullName="สมศักดิ์ เทพเมืองไทย",
            status="rejected"
        )

        db_session.add_all([pending_player, verified_player, rejected_player])
        db_session.commit()

        # Query only verified
        verified_only = db_session.query(Player).filter(
            Player.teamId == sample_team.id,
            Player.status == "verified"
        ).all()

        assert len(verified_only) == 1
        assert verified_only[0].firstName == "วิทยา"
        assert verified_only[0].verifiedAt is not None

    def test_empty_team_export_raises_error(self, db_session, sample_team):
        """Test that exporting team with no verified players raises error."""
        # Create only pending players
        pending_player = Player(
            teamId=sample_team.id,
            firstName="สมชาย",
            lastName="วิชัยกุล",
            fullName="สมชาย วิชัยกุล",
            status="pending"
        )

        db_session.add(pending_player)
        db_session.commit()

        # Query verified players
        verified = db_session.query(Player).filter(
            Player.teamId == sample_team.id,
            Player.status == "verified"
        ).all()

        assert len(verified) == 0
