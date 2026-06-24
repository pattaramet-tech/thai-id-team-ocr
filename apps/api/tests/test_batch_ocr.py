"""Tests for batch OCR upload functionality."""
import pytest
from datetime import date
from io import BytesIO


class TestBatchUploadEndpoint:
    """Test batch OCR upload endpoint."""

    def test_batch_upload_missing_team(self, client, db_session):
        """Batch upload to non-existent team returns error."""
        response = client.post(
            "/ocr/batch-upload",
            data={"team_id": "999"},
            files=[("files", ("test.jpg", b"x" * 100))]
        )
        assert response.status_code in (404, 500)

    def test_batch_upload_invalid_file_type(self, client, db_session):
        """Invalid file type returns item error, not batch error."""
        from app.models import Team

        team = Team(
            name="Test Team",
            ageGroup="U18",
            gender="Male",
            competitionYearBE=2569
        )
        db_session.add(team)
        db_session.commit()

        response = client.post(
            "/ocr/batch-upload",
            data={"team_id": str(team.id)},
            files=[("files", ("test.txt", b"not an image"))]
        )

        assert response.status_code == 200
        data = response.json()
        assert data["totalFiles"] == 1
        assert data["errorCount"] == 1
        assert data["successCount"] == 0
        assert data["items"][0]["success"] is False
        assert "allowed" in data["items"][0]["error"].lower()

    def test_batch_upload_response_structure(self, client, db_session):
        """Batch upload response has correct structure."""
        from app.models import Team

        team = Team(
            name="Test Team",
            ageGroup="U18",
            gender="Male",
            competitionYearBE=2569
        )
        db_session.add(team)
        db_session.commit()

        # Use invalid files so we don't depend on OCR working
        files = [
            ("files", ("invalid1.txt", b"not image")),
            ("files", ("invalid2.txt", b"not image")),
        ]

        response = client.post(
            "/ocr/batch-upload",
            data={"team_id": str(team.id)},
            files=files
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "totalFiles" in data
        assert "successCount" in data
        assert "errorCount" in data
        assert "items" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) == 2
        assert data["totalFiles"] == 2
        assert data["errorCount"] == 2

    def test_batch_upload_file_too_large(self, client, db_session):
        """File exceeding size limit returns item error."""
        from app.models import Team

        team = Team(
            name="Test Team",
            ageGroup="U18",
            gender="Male",
            competitionYearBE=2569
        )
        db_session.add(team)
        db_session.commit()

        # Create file larger than 10MB limit (11MB)
        large_file = b"x" * (11 * 1024 * 1024)

        response = client.post(
            "/ocr/batch-upload",
            data={"team_id": str(team.id)},
            files=[("files", ("large.jpg", large_file))]
        )

        assert response.status_code == 200
        data = response.json()
        assert data["errorCount"] == 1
        assert "exceeds" in data["items"][0]["error"].lower()

    def test_batch_upload_too_many_files(self, client, db_session):
        """Batch upload exceeding file limit returns error."""
        from app.models import Team

        team = Team(
            name="Test Team",
            ageGroup="U18",
            gender="Male",
            competitionYearBE=2569
        )
        db_session.add(team)
        db_session.commit()

        # Create 31 files (limit is 30)
        files = [
            ("files", (f"test_{i}.txt", b"x" * 100))
            for i in range(31)
        ]

        response = client.post(
            "/ocr/batch-upload",
            data={"team_id": str(team.id)},
            files=files
        )
        assert response.status_code == 400
        assert "Cannot upload more than 30 files" in response.json()["detail"]

    def test_batch_upload_mixed_valid_invalid(self, client, db_session):
        """Batch upload with invalid files still returns batch response."""
        from app.models import Team

        team = Team(
            name="Test Team",
            ageGroup="U18",
            gender="Male",
            competitionYearBE=2569
        )
        db_session.add(team)
        db_session.commit()

        files = [
            ("files", ("invalid1.txt", b"not an image")),
            ("files", ("invalid2.txt", b"not an image")),
            ("files", ("invalid3.txt", b"not an image")),
        ]

        response = client.post(
            "/ocr/batch-upload",
            data={"team_id": str(team.id)},
            files=files
        )

        assert response.status_code == 200
        data = response.json()

        # Should have results for all 3 files
        assert data["totalFiles"] == 3
        # All should fail (invalid types)
        assert data["errorCount"] == 3
        assert data["successCount"] == 0
        # Verify individual item structure for failed items
        for item in data["items"]:
            assert item["success"] is False
            assert item["error"] is not None
            assert item["sourceFilename"] is not None


class TestFuzzyDuplicatesEndpoint:
    """Test fuzzy duplicate detection endpoint."""

    def test_check_fuzzy_duplicates_exact_match(self, client, db_session):
        """Checking exact duplicate returns match."""
        from app.models import Team, Player

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

        response = client.get(
            f"/ocr/teams/{team.id}/fuzzy-duplicates?name=สมชาย วิวัฒน์"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["matches"]) == 1
        assert data["matches"][0]["matchedPlayerId"] == player.id
        assert data["matches"][0]["similarity"] == 100.0

    def test_check_fuzzy_duplicates_no_match(self, client, db_session):
        """Checking different name returns no match."""
        from app.models import Team, Player

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

        response = client.get(
            f"/ocr/teams/{team.id}/fuzzy-duplicates?name=เจษฎา คำสิงห์"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["matches"]) == 0

    def test_check_fuzzy_duplicates_missing_team(self, client):
        """Checking duplicates for non-existent team returns 404 or 500."""
        response = client.get(
            "/ocr/teams/999/fuzzy-duplicates?name=สมชาย วิวัฒน์"
        )
        assert response.status_code in (404, 500)
