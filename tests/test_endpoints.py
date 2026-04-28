"""
Test happy path scenarios for API endpoints using AAA pattern.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: Set up expected activities list
        Act: Request all activities
        Assert: Verify all activities are returned with required fields
        """
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Soccer Team",
            "Swimming Club",
            "Art Workshop",
            "Drama Club",
            "Science Club",
            "Debate Team",
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == len(expected_activities)
        for activity_name in expected_activities:
            assert activity_name in activities
            assert "description" in activities[activity_name]
            assert "schedule" in activities[activity_name]
            assert "max_participants" in activities[activity_name]
            assert "participants" in activities[activity_name]

    def test_get_activities_returns_correct_structure(self, client):
        """
        Arrange: None (just get activities)
        Act: Request activities
        Assert: Verify data structure and types
        """
        # Arrange
        # Nothing to arrange

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            assert activity_data["max_participants"] > 0


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_success(self, client):
        """
        Arrange: Prepare new student email and valid activity
        Act: Sign up new student
        Assert: Verify signup succeeds and participant is added
        """
        # Arrange
        activity = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["message"] == f"Signed up {email} for {activity}"

        # Verify participant was added
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity]["participants"]

    def test_signup_increases_participant_count(self, client):
        """
        Arrange: Get initial participant count
        Act: Sign up a new student
        Assert: Verify count increased by 1
        """
        # Arrange
        activity = "Programming Class"
        email = "newemail@mergington.edu"
        initial_activities = client.get("/activities").json()
        initial_count = len(initial_activities[activity]["participants"])

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        updated_activities = client.get("/activities").json()
        updated_count = len(updated_activities[activity]["participants"])
        assert updated_count == initial_count + 1


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_from_activity_success(self, client):
        """
        Arrange: Get a current participant
        Act: Unregister them from the activity
        Assert: Verify unregister succeeds and participant is removed
        """
        # Arrange
        activity = "Programming Class"
        email = "emma@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity}/unregister?email={email}")

        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["message"] == f"Unregistered {email} from {activity}"

        # Verify participant was removed
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity]["participants"]

    def test_unregister_decreases_participant_count(self, client):
        """
        Arrange: Get initial participant count
        Act: Unregister a student
        Assert: Verify count decreased by 1
        """
        # Arrange
        activity = "Gym Class"
        email = "john@mergington.edu"
        initial_activities = client.get("/activities").json()
        initial_count = len(initial_activities[activity]["participants"])

        # Act
        response = client.delete(f"/activities/{activity}/unregister?email={email}")

        # Assert
        assert response.status_code == 200
        updated_activities = client.get("/activities").json()
        updated_count = len(updated_activities[activity]["participants"])
        assert updated_count == initial_count - 1
