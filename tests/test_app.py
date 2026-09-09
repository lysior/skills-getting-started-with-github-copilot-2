from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    assert set(response.json()) == set(activities)
    assert response.json()["Chess Club"]["participants"]


def test_signup_adds_student_to_activity():
    email = "test-signup@mergington.edu"
    activity_name = "Chess Club"

    try:
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        assert response.status_code == 200
        assert response.json() == {
            "message": f"Signed up {email} for {activity_name}"
        }
        assert email in activities[activity_name]["participants"]
    finally:
        if email in activities[activity_name]["participants"]:
            activities[activity_name]["participants"].remove(email)


def test_signup_rejects_unknown_activity():
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "unknown-activity@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_duplicate_student():
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_removes_student_from_activity():
    activity_name = "Chess Club"
    email = "test-unregister@mergington.edu"
    activities[activity_name]["participants"].append(email)

    try:
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        assert response.status_code == 200
        assert response.json() == {
            "message": f"Unregistered {email} from {activity_name}"
        }
        assert email not in activities[activity_name]["participants"]
    finally:
        if email in activities[activity_name]["participants"]:
            activities[activity_name]["participants"].remove(email)


def test_unregister_rejects_unknown_activity():
    response = client.delete(
        "/activities/Unknown Club/signup",
        params={"email": "unknown-activity@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_student_not_signed_up():
    activity_name = "Chess Club"
    email = "not-signed-up@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"