"""
Test suite for Mergington High School Activities API

Tests all API endpoints including:
- GET / (root redirect)
- GET /activities (list all activities)
- POST /activities/{activity_name}/signup (register for activity)
- DELETE /activities/{activity_name}/unregister (unregister from activity)
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def backup_activities():
    """Backup and restore activities data for each test"""
    # Create a deep copy of the original activities data
    original_activities = copy.deepcopy(activities)
    yield
    # Restore the original data after each test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root path redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert "static/index.html" in response.headers["location"]


class TestActivitiesEndpoint:
    """Tests for the activities endpoint"""
    
    def test_get_activities_success(self, client, backup_activities):
        """Test getting all activities returns correct data"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        
        # Check structure of an activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_get_activities_contains_expected_activities(self, client, backup_activities):
        """Test that response contains expected activities"""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", 
            "Soccer Team", "Basketball Club", "Art Club", 
            "Drama Society", "Math Olympiad", "Science Club"
        ]
        
        for activity in expected_activities:
            assert activity in data, f"Activity '{activity}' not found in response"


class TestSignupEndpoint:
    """Tests for the signup endpoint"""
    
    def test_signup_success(self, client, backup_activities):
        """Test successful signup for an activity"""
        activity_name = "Chess Club"
        email = "test@mergington.edu"
        
        # Ensure student is not already registered
        assert email not in activities[activity_name]["participants"]
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify student was added to participants
        assert email in activities[activity_name]["participants"]
    
    def test_signup_nonexistent_activity(self, client, backup_activities):
        """Test signup for non-existent activity returns 404"""
        response = client.post("/activities/Nonexistent Club/signup?email=test@mergington.edu")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_registration(self, client, backup_activities):
        """Test that duplicate registration returns 400 error"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_with_special_characters_in_activity_name(self, client, backup_activities):
        """Test signup works with URL-encoded activity names"""
        activity_name = "Art Club"
        email = "artist@mergington.edu"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify student was added
        assert email in activities[activity_name]["participants"]
    
    def test_signup_missing_email_parameter(self, client, backup_activities):
        """Test signup without email parameter"""
        response = client.post("/activities/Chess Club/signup")
        assert response.status_code == 422  # Unprocessable Entity (missing required parameter)


class TestUnregisterEndpoint:
    """Tests for the unregister endpoint"""
    
    def test_unregister_success(self, client, backup_activities):
        """Test successful unregistration from an activity"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Verify student is registered
        assert email in activities[activity_name]["participants"]
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        assert email in data["message"]
        
        # Verify student was removed
        assert email not in activities[activity_name]["participants"]
    
    def test_unregister_nonexistent_activity(self, client, backup_activities):
        """Test unregister from non-existent activity returns 404"""
        response = client.delete("/activities/Nonexistent Club/unregister?email=test@mergington.edu")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_not_registered_student(self, client, backup_activities):
        """Test unregistering student who is not registered returns 400"""
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "not registered" in data["detail"]
    
    def test_unregister_missing_email_parameter(self, client, backup_activities):
        """Test unregister without email parameter"""
        response = client.delete("/activities/Chess Club/unregister")
        assert response.status_code == 422  # Unprocessable Entity


class TestIntegrationScenarios:
    """Integration tests for complete user workflows"""
    
    def test_signup_then_unregister_workflow(self, client, backup_activities):
        """Test complete workflow: signup then unregister"""
        activity_name = "Science Club"
        email = "workflow@mergington.edu"
        
        # Initial state - student not registered
        initial_participants = activities[activity_name]["participants"].copy()
        assert email not in initial_participants
        
        # Step 1: Sign up
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]
        
        # Step 2: Verify signup via GET activities
        get_response = client.get("/activities")
        assert get_response.status_code == 200
        activities_data = get_response.json()
        assert email in activities_data[activity_name]["participants"]
        
        # Step 3: Unregister
        unregister_response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert unregister_response.status_code == 200
        assert email not in activities[activity_name]["participants"]
        
        # Step 4: Verify unregistration via GET activities
        final_get_response = client.get("/activities")
        assert final_get_response.status_code == 200
        final_activities_data = final_get_response.json()
        assert email not in final_activities_data[activity_name]["participants"]
        
        # Verify we're back to initial state
        assert activities[activity_name]["participants"] == initial_participants
    
    def test_multiple_students_signup_same_activity(self, client, backup_activities):
        """Test multiple students can sign up for the same activity"""
        activity_name = "Math Olympiad"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        initial_count = len(activities[activity_name]["participants"])
        
        # Sign up multiple students
        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all students are registered
        for email in emails:
            assert email in activities[activity_name]["participants"]
        
        # Verify count increased correctly
        assert len(activities[activity_name]["participants"]) == initial_count + len(emails)
    
    def test_activity_capacity_tracking(self, client, backup_activities):
        """Test that activities track participants correctly for capacity"""
        activity_name = "Chess Club"
        initial_count = len(activities[activity_name]["participants"])
        max_participants = activities[activity_name]["max_participants"]
        
        # Get activities and check spots calculation
        response = client.get("/activities")
        data = response.json()
        
        expected_spots_left = max_participants - initial_count
        # Note: The spots calculation is done in frontend, but we can verify the data is correct
        assert len(data[activity_name]["participants"]) == initial_count
        assert data[activity_name]["max_participants"] == max_participants


class TestEdgeCases:
    """Tests for edge cases and error conditions"""
    
    def test_signup_with_special_characters_in_email(self, client, backup_activities):
        """Test signup with special characters in email"""
        activity_name = "Art Club"
        email = "test.special@mergington.edu"  # Using dot instead of plus to avoid URL encoding issues
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]
    
    def test_case_sensitive_activity_names(self, client, backup_activities):
        """Test that activity names are case sensitive"""
        # This should fail because "chess club" != "Chess Club"
        response = client.post("/activities/chess club/signup?email=test@mergington.edu")
        assert response.status_code == 404
    
    def test_empty_email_parameter(self, client, backup_activities):
        """Test signup with empty email parameter"""
        response = client.post("/activities/Chess Club/signup?email=")
        # The API should still process this, but the email will be empty string
        assert response.status_code == 200
        assert "" in activities["Chess Club"]["participants"]