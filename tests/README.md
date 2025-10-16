# Tests for Mergington High School Activities API

This directory contains comprehensive tests for the FastAPI backend that powers the student activity registration system.

## Test Structure

### `test_api.py`
Comprehensive test suite organized into the following test classes:

#### TestRootEndpoint
- Tests the root redirect functionality (`/` → `/static/index.html`)

#### TestActivitiesEndpoint  
- Tests the `GET /activities` endpoint
- Verifies all activities are returned with correct structure
- Checks for expected activities in the system

#### TestSignupEndpoint
- Tests the `POST /activities/{activity_name}/signup` endpoint
- Covers successful signups, duplicate registrations, nonexistent activities
- Tests edge cases like special characters and missing parameters

#### TestUnregisterEndpoint
- Tests the `DELETE /activities/{activity_name}/unregister` endpoint  
- Covers successful unregistration, nonexistent activities, not-registered users
- Tests edge cases and error conditions

#### TestIntegrationScenarios
- End-to-end workflow tests (signup → verify → unregister → verify)
- Multiple students signing up for same activity
- Activity capacity tracking validation

#### TestEdgeCases
- Special characters in emails and activity names
- Case sensitivity testing
- Empty parameter handling

## Running Tests

### Method 1: Using the test script
```bash
./run_tests.sh
```

### Method 2: Direct pytest command
```bash
# Run all tests with coverage
python -m pytest tests/ --cov=src --cov-report=term-missing -v

# Run just the tests without coverage
python -m pytest tests/ -v

# Run a specific test class
python -m pytest tests/test_api.py::TestSignupEndpoint -v

# Run a specific test
python -m pytest tests/test_api.py::TestSignupEndpoint::test_signup_success -v
```

## Test Coverage

The test suite achieves **100% code coverage** of the main application (`src/app.py`), ensuring all code paths are tested.

## Test Dependencies

- `pytest` - Testing framework
- `pytest-asyncio` - Async test support  
- `pytest-cov` - Coverage reporting
- `httpx` - HTTP client for FastAPI testing

These are automatically installed when you run:
```bash
pip install -r requirements.txt
```

## Test Data Management

The tests use a `backup_activities` fixture that:
- Creates a backup of the original activities data before each test
- Restores the original data after each test completes
- Ensures tests don't interfere with each other

This allows tests to modify the activities data (add/remove participants) without affecting other tests.