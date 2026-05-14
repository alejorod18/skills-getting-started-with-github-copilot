import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original = {name: list(data["participants"]) for name, data in activities.items()}
    yield
    for name, participants in original.items():
        activities[name]["participants"] = participants


client = TestClient(app)


# --- GET /activities ---

def test_get_activities_returns_all():
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert "Programming Class" in response.json()


def test_get_activities_structure():
    # Act
    response = client.get("/activities")

    # Assert
    for activity in response.json().values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


# --- POST /activities/{activity_name}/signup ---

def test_signup_success():
    # Arrange
    email = "new@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_signup_adds_participant():
    # Arrange
    email = "new@mergington.edu"
    activity_name = "Chess Club"

    # Act
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    participants = client.get("/activities").json()[activity_name]["participants"]
    assert email in participants


def test_signup_duplicate_returns_400():
    # Arrange
    email = "dup@mergington.edu"
    activity_name = "Chess Club"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400


def test_signup_unknown_activity_returns_404():
    # Arrange
    email = "x@mergington.edu"
    activity_name = "Nonexistent Activity"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404


# --- DELETE /activities/{activity_name}/signup ---

def test_unregister_success():
    # Arrange
    email = "temp@mergington.edu"
    activity_name = "Chess Club"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200


def test_unregister_removes_participant():
    # Arrange
    email = "temp@mergington.edu"
    activity_name = "Chess Club"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    participants = client.get("/activities").json()[activity_name]["participants"]
    assert email not in participants


def test_unregister_not_registered_returns_404():
    # Arrange
    email = "nobody@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404


def test_unregister_unknown_activity_returns_404():
    # Arrange
    email = "x@mergington.edu"
    activity_name = "Nonexistent Activity"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
