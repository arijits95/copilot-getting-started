import copy
import pytest
from fastapi.testclient import TestClient
import src.app as app_module

client = TestClient(app_module.app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: snapshot original state and restore after each test
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = original


def test_get_activities_returns_activity_list():
    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    email = "teststudent@mergington.edu"
    activity = "Chess Club"

    # Act
    resp = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert resp.status_code == 200
    assert resp.json()["message"] == f"Signed up {email} for {activity}"
    assert email in app_module.activities[activity]["participants"]


def test_duplicate_signup_returns_400():
    # Arrange: use an existing participant
    email = app_module.activities["Chess Club"]["participants"][0]
    activity = "Chess Club"

    # Act
    resp = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert resp.status_code == 400


def test_remove_participant_from_activity():
    # Arrange
    email = "remove_me@mergington.edu"
    activity = "Chess Club"
    app_module.activities[activity]["participants"].append(email)

    # Act
    resp = client.delete(f"/activities/{activity}/participants?email={email}")

    # Assert
    assert resp.status_code == 200
    assert resp.json()["message"] == f"Removed {email} from {activity}"
    assert email not in app_module.activities[activity]["participants"]
