"""
Test edge cases and complex scenarios using AAA pattern.
"""

import pytest


class TestSignupUnregisterFlow:
    """Tests for signup and unregister flow scenarios"""

    def test_signup_then_unregister_flow(self, client):
        """
        Arrange: Prepare a new student
        Act: Sign up then immediately unregister
        Assert: Verify both operations succeed and state is correct
        """
        # Arrange
        activity = "Art Workshop"
        email = "testuser@mergington.edu"

        # Act - Signup
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert signup
        assert signup_response.status_code == 200
        assert email in client.get("/activities").json()[activity]["participants"]

        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )

        # Assert unregister
        assert unregister_response.status_code == 200
        assert (
            email not in client.get("/activities").json()[activity]["participants"]
        )

    def test_signup_multiple_students_same_activity(self, client):
        """
        Arrange: Prepare multiple new student emails
        Act: Sign them all up for the same activity
        Assert: Verify all are added successfully
        """
        # Arrange
        activity = "Science Club"
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu",
        ]

        # Act
        responses = [
            client.post(f"/activities/{activity}/signup?email={email}")
            for email in emails
        ]

        # Assert
        for response in responses:
            assert response.status_code == 200

        activity_data = client.get("/activities").json()[activity]
        for email in emails:
            assert email in activity_data["participants"]

    def test_unregister_then_signup_same_student(self, client):
        """
        Arrange: Get a current participant
        Act: Unregister them, then sign them up again
        Assert: Verify both operations succeed
        """
        # Arrange
        activity = "Swimming Club"
        email = "noah@mergington.edu"

        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )

        # Assert unregister
        assert unregister_response.status_code == 200
        assert (
            email not in client.get("/activities").json()[activity]["participants"]
        )

        # Act - Signup again
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert signup
        assert signup_response.status_code == 200
        assert email in client.get("/activities").json()[activity]["participants"]


class TestErrorRecovery:
    """Tests for error handling and recovery scenarios"""

    def test_cannot_unregister_twice(self, client):
        """
        Arrange: Get a current participant
        Act: Unregister twice
        Assert: First succeeds, second fails with 400
        """
        # Arrange
        activity = "Soccer Team"
        email = "liam@mergington.edu"

        # Act - First unregister
        response1 = client.delete(f"/activities/{activity}/unregister?email={email}")

        # Assert first unregister succeeds
        assert response1.status_code == 200

        # Act - Second unregister
        response2 = client.delete(f"/activities/{activity}/unregister?email={email}")

        # Assert second unregister fails
        assert response2.status_code == 400
        assert (
            response2.json()["detail"] == "Student is not registered for this activity"
        )

    def test_signup_after_failed_signup(self, client):
        """
        Arrange: Prepare a student to attempt duplicate signup
        Act: Try duplicate signup, then try different activity
        Assert: First fails, second succeeds
        """
        # Arrange
        activity1 = "Debate Team"
        activity2 = "Drama Club"
        email = "olivia@mergington.edu"  # Already in Debate Team

        # Act - Try to signup for same activity
        response1 = client.post(f"/activities/{activity1}/signup?email={email}")

        # Assert first attempt fails
        assert response1.status_code == 400

        # Act - Try to signup for different activity
        response2 = client.post(f"/activities/{activity2}/signup?email={email}")

        # Assert second attempt succeeds
        assert response2.status_code == 200
        assert email in client.get("/activities").json()[activity2]["participants"]


class TestDataIntegrity:
    """Tests for data integrity and consistency"""

    def test_activity_has_valid_participant_count(self, client):
        """
        Arrange: Get all activities
        Act: Check participant counts
        Assert: Verify counts are valid and within limits
        """
        # Arrange
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        for activity_name, activity_data in activities.items():
            participant_count = len(activity_data["participants"])
            max_participants = activity_data["max_participants"]

            # Verify count is within valid range
            assert 0 <= participant_count <= max_participants
            # Verify all participants are unique
            assert len(activity_data["participants"]) == len(
                set(activity_data["participants"])
            )

    def test_participant_not_duplicated_in_activity(self, client):
        """
        Arrange: Get current activity state
        Act: Check participants list
        Assert: Verify no duplicates exist
        """
        # Arrange
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            participants = activity_data["participants"]
            # Check for duplicates by comparing length with set
            assert len(participants) == len(set(participants)), (
                f"Activity {activity_name} has duplicate participants"
            )

    def test_multiple_activities_independent(self, client):
        """
        Arrange: Sign up for multiple activities
        Act: Unregister from one
        Assert: Verify others are not affected
        """
        # Arrange
        email = "testindependent@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"

        # Act - Signup for both
        client.post(f"/activities/{activity1}/signup?email={email}")
        client.post(f"/activities/{activity2}/signup?email={email}")

        # Act - Unregister from first
        client.delete(f"/activities/{activity1}/unregister?email={email}")

        # Assert
        activities = client.get("/activities").json()
        assert email not in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]
