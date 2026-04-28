"""
Test validation and error scenarios using AAA pattern.
"""

import pytest


class TestSignupValidation:
    """Tests for POST /activities/{activity_name}/signup validation"""

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Use a non-existent activity name
        Act: Try to sign up
        Assert: Verify 404 error is returned
        """
        # Arrange
        activity = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_returns_400(self, client):
        """
        Arrange: Use email already signed up for activity
        Act: Try to sign up again
        Assert: Verify 400 error for duplicate signup
        """
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "Student already signed up for this activity"
        )

    def test_signup_same_email_different_activities(self, client):
        """
        Arrange: Student email already signed up for one activity
        Act: Try to sign up for a different activity
        Assert: Verify signup succeeds for different activity
        """
        # Arrange
        activity = "Soccer Team"
        email = "michael@mergington.edu"  # Signed up for Chess Club

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert email in client.get("/activities").json()[activity]["participants"]

    def test_signup_with_special_characters_in_email(self, client):
        """
        Arrange: Use email with special characters
        Act: Sign up with special character email
        Assert: Verify signup succeeds
        """
        # Arrange
        activity = "Drama Club"
        email = "test+tag@example.mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert email in client.get("/activities").json()[activity]["participants"]


class TestUnregisterValidation:
    """Tests for DELETE /activities/{activity_name}/unregister validation"""

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Use a non-existent activity name
        Act: Try to unregister
        Assert: Verify 404 error is returned
        """
        # Arrange
        activity = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity}/unregister?email={email}")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_not_registered_returns_400(self, client):
        """
        Arrange: Use email not registered for the activity
        Act: Try to unregister
        Assert: Verify 400 error for non-registered student
        """
        # Arrange
        activity = "Gym Class"
        email = "notstudent@mergington.edu"  # Not registered

        # Act
        response = client.delete(f"/activities/{activity}/unregister?email={email}")

        # Assert
        assert response.status_code == 400
        assert (
            response.json()["detail"] == "Student is not registered for this activity"
        )

    def test_unregister_case_sensitive_email(self, client):
        """
        Arrange: Try to unregister with different email case
        Act: Unregister with different case
        Assert: Verify it fails (email is case-sensitive in current implementation)
        """
        # Arrange
        activity = "Chess Club"
        original_email = "michael@mergington.edu"
        different_case_email = "MICHAEL@MERGINGTON.EDU"

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister?email={different_case_email}"
        )

        # Assert
        # It should fail because the email doesn't match exactly
        assert response.status_code == 400
        assert (
            response.json()["detail"] == "Student is not registered for this activity"
        )
        # Verify original email is still there
        assert (
            original_email
            in client.get("/activities").json()[activity]["participants"]
        )
