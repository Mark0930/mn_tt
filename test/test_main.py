import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from src.main import app, check_three_consecutive_withdraws, check_three_consecutive_increasing_deposits, check_accumulative_deposit_over_200
from src.schema import EventPost
from src.models import UserEvent
from src.database import get_db

client = TestClient(app)

# Mock data for tests
def mock_query_withdraws():
    return [
        UserEvent(user_id=1, type="withdraw", amount=50, timestamp=10),
        UserEvent(user_id=1, type="withdraw", amount=60, timestamp=20),
        UserEvent(user_id=1, type="withdraw", amount=70, timestamp=30),
    ]

def mock_query_deposits():
    return [
        UserEvent(user_id=1, type="deposit", amount=50, timestamp=10),
        UserEvent(user_id=1, type="deposit", amount=100, timestamp=20),
        UserEvent(user_id=1, type="deposit", amount=150, timestamp=30),
    ]

def mock_query_accumulative_deposits():
    return [
        UserEvent(user_id=1, type="deposit", amount=100, timestamp=10),
        UserEvent(user_id=1, type="deposit", amount=150, timestamp=20),
    ]

# Mock the database session dependency
@pytest.fixture
def mock_db_session():
    mock_session = MagicMock()
    yield mock_session

# Override the FastAPI dependency
@pytest.fixture(autouse=True)
def override_get_db(mock_db_session):
    app.dependency_overrides[get_db] = lambda: mock_db_session

# Test Rule: Code 30 - 3 consecutive withdraws
def test_check_three_consecutive_withdraws(mock_db_session):
    mock_db_session.query().filter().order_by().limit().all.return_value = mock_query_withdraws()

    result = check_three_consecutive_withdraws(mock_db_session, user_id=1)
    assert result is True

# Test Rule: Code 300 - 3 consecutive increasing deposits
def test_check_three_consecutive_increasing_deposits(mock_db_session):
    mock_db_session.query().filter().order_by().all.return_value = mock_query_deposits()

    result = check_three_consecutive_increasing_deposits(mock_db_session, user_id=1)
    assert result is True

# Test Rule: Code 123 - Accumulative deposit amount over 30 seconds > 200
def test_check_accumulative_deposit_over_200(mock_db_session):
    mock_db_session.query().filter().all.return_value = mock_query_accumulative_deposits()

    result = check_accumulative_deposit_over_200(mock_db_session, user_id=1, current_timestamp=40)
    assert result is True

# Test Rule: Code 1100 - A withdraw amount over 100
def test_withdraw_over_100(mock_db_session):
    mock_db_session.add = MagicMock()  # Mock the add method
    mock_db_session.commit = MagicMock()  # Mock the commit method

    event = EventPost(type="withdraw", amount="150.00", user_id=1, t=10)
    response = client.post("/event", json=event.model_dump())
    assert response.status_code == 200
    assert 1100 in response.json()["alert_codes"]

# Test Endpoint: /event
def test_event_endpoint(mock_db_session):
    mock_db_session.query().filter().order_by().all.side_effect = [
        mock_query_withdraws(),  # For Rule: Code 30
        mock_query_deposits(),  # For Rule: Code 300
        mock_query_accumulative_deposits(),  # For Rule: Code 123
    ]
    mock_db_session.add = MagicMock()  # Mock the add method
    mock_db_session.commit = MagicMock()  # Mock the commit method

    event = EventPost(type="withdraw", amount="150.00", user_id=1, t=10)
    response = client.post("/event", json=event.model_dump())
    assert response.status_code == 200
    assert response.json() == {
        "alert": True,
        "alert_codes": [1100, 300],
        "user_id": 1,
    }