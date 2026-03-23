"""
Comprehensive test suite for Mergington High School Activities API
Uses Arrange-Act-Assert (AAA) testing pattern for clarity and maintainability.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

# Create a test client
client = TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities(self):
        """Test that GET /activities returns all activities with their properties"""
        # Arrange
        expected_fields = {"description", "schedule", "max_participants", "participants"}
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Tennis Club", "Art Studio", "Music Band", "Debate Club", "Science Club"
        ]

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert isinstance(data, dict)
        assert len(data) == len(expected_activities)
        
        for activity_name in expected_activities:
            assert activity_name in data
            assert all(field in data[activity_name] for field in expected_fields)
            assert isinstance(data[activity_name]["participants"], list)
            assert isinstance(data[activity_name]["max_participants"], int)


class TestSignUp:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_valid_activity(self):
        """Test signing up a new student for an activity"""
        # Arrange
        activity_name = "Basketball Team"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]
        
        # Verify the student was added to the activity
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]

    def test_signup_duplicate_email(self):
        """Test that signing up with duplicate email returns 400 error"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already enrolled

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_nonexistent_activity(self):
        """Test that signing up for non-existent activity returns 404 error"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_valid_participant(self):
        """Test removing an existing participant from an activity"""
        # Arrange
        activity_name = "Debate Club"
        email = "lucas@mergington.edu"
        
        # Verify the student is initially enrolled
        initial_response = client.get("/activities")
        assert email in initial_response.json()[activity_name]["participants"]

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]
        
        # Verify the student was removed
        final_response = client.get("/activities")
        assert email not in final_response.json()[activity_name]["participants"]

    def test_unregister_nonexistent_participant(self):
        """Test that removing a non-existent participant returns 404 error"""
        # Arrange
        activity_name = "Science Club"
        email = "nonexistent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_nonexistent_activity(self):
        """Test that unregistering from non-existent activity returns 404 error"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestCompleteFlow:
    """Integration tests for full signup/unregister workflows"""

    def test_signup_then_unregister_flow(self):
        """Test the complete flow of signing up and then unregistering"""
        # Arrange
        activity_name = "Gym Class"
        email = "flowtest@mergington.edu"

        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert - Signup successful
        assert signup_response.status_code == 200
        get_response = client.get("/activities")
        assert email in get_response.json()[activity_name]["participants"]

        # Act - Unregister
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert - Unregister successful
        assert unregister_response.status_code == 200
        final_response = client.get("/activities")
        assert email not in final_response.json()[activity_name]["participants"]

    def test_multiple_participants_same_activity(self):
        """Test that multiple participants can sign up for the same activity"""
        # Arrange
        activity_name = "Art Studio"
        email1 = "participant1@mergington.edu"
        email2 = "participant2@mergington.edu"

        # Act - Sign up first participant
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        
        # Act - Sign up second participant
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )

        # Assert - Both signups successful
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities = client.get("/activities").json()
        assert email1 in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]
