from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_get_activities_returns_activity_data():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()

    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert "participants" in payload["Chess Club"]


def test_signup_for_activity_adds_participant():
    activity_name = "Chess Club"
    email = "new.student@example.com"
    original_participants = activities[activity_name]["participants"][:]

    try:
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        assert response.status_code == 200
        assert response.json() == {
            "message": f"Signed up {email} for {activity_name}"
        }
        assert email in activities[activity_name]["participants"]
    finally:
        activities[activity_name]["participants"] = original_participants


def test_signup_for_activity_rejects_duplicate_email():
    response = client.post(
        "/activities/Chess Club/signup?email=michael@mergington.edu"
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_signup_for_unknown_activity_returns_404():
    response = client.post(
        "/activities/Does Not Exist/signup?email=student@example.com"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_from_activity():
    activity_name = "Chess Club"
    email = "temporary.student@example.com"
    original_participants = activities[activity_name]["participants"][:]

    try:
        activities[activity_name]["participants"].append(email)

        response = client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )

        assert response.status_code == 200
        assert response.json() == {
            "message": f"Removed {email} from {activity_name}"
        }
        assert email not in activities[activity_name]["participants"]
    finally:
        activities[activity_name]["participants"] = original_participants


def test_remove_participant_for_unknown_email_returns_404():
    response = client.delete(
        "/activities/Chess Club/participants?email=missing.student@example.com"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found"}
