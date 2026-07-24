from pathlib import Path

from app.models.schemas import UserProfile
from app.repositories.profiles import SQLiteProfileRepository


def test_profile_is_validated_and_upserted(tmp_path: Path):
    repository = SQLiteProfileRepository(str(tmp_path / "profiles.db"))
    profile = UserProfile(name="Sara Ahmed", phone="01012345678", age=25, city="Cairo")

    repository.save(profile)
    repository.save(profile.model_copy(update={"city": "Giza"}))

    assert repository.exists("01012345678")


def test_invalid_egyptian_phone_is_rejected():
    try:
        UserProfile(name="Sara Ahmed", phone="123", age=25, city="Cairo")
    except ValueError as error:
        assert "Phone number" in str(error)
    else:
        raise AssertionError("Invalid phone number should be rejected")
