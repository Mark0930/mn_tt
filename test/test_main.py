import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from src.main import app, check_three_consecutive_withdraws, check_three_consecutive_increasing_deposits, check_accumulative_deposit_over_200
from src.schema import EventPost
from src.models import UserEvent
from src.database import get_db
from unittest.mock import patch

client = TestClient(app)

def mock_query_withdraws():
    return [
        UserEvent(user_id=1, type="withdraw", amount=50, timestamp=10),
        UserEvent(user_id=1, type="withdraw", amount=60, timestamp=20),
        UserEvent(user_id=1, type="withdraw", amount=70, timestamp=30),
    ]

def mock_query_deposits():
    return [
        UserEvent(user_id=1, type="deposit", amount=50, timestamp=40),
        UserEvent(user_id=1, type="deposit", amount=100, timestamp=50),
        UserEvent(user_id=1, type="deposit", amount=150, timestamp=60),
    ]

def mock_query_accumulative_deposits():
    return [
        UserEvent(user_id=1, type="deposit", amount=100, timestamp=70),
        UserEvent(user_id=1, type="deposit", amount=150, timestamp=80),
    ]

@pytest.fixture
def mock_db_session():
    mock_session = MagicMock()
    yield mock_session

@pytest.fixture(autouse=True)
def override_get_db(mock_db_session):
    app.dependency_overrides[get_db] = lambda: mock_db_session

def test_check_three_consecutive_withdraws(mock_db_session):
    mock_db_session.query().filter().order_by().limit().all.return_value = mock_query_withdraws()
    result = check_three_consecutive_withdraws(mock_db_session, user_id=1, timestamp=40)
    assert result is True

def test_check_three_consecutive_increasing_deposits(mock_db_session):
    mock_db_session.query().filter().order_by().all.return_value = mock_query_deposits()
    result = check_three_consecutive_increasing_deposits(mock_db_session, user_id=1, timestamp=70)
    assert result is True

def test_check_accumulative_deposit_over_200(mock_db_session):
    mock_db_session.query().filter().all.return_value = mock_query_accumulative_deposits()
    result = check_accumulative_deposit_over_200(mock_db_session, user_id=1, current_timestamp=40)
    assert result is True

def test_event_endpoint_1100(mock_db_session):
    with patch("src.main.check_three_consecutive_withdraws", return_value=False):
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()
        event = EventPost(type="withdraw", amount="150.00", user_id=1, t=100)
        response = client.post("/event", json=event.model_dump())
        assert response.status_code == 200
        assert response.json() == {
            "alert": True,
            "alert_codes": [1100],
            "user_id": 1,
        }

def test_event_endpoint_30(mock_db_session):
    with patch("src.main.check_three_consecutive_withdraws", return_value=True):
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()
        event = EventPost(type="withdraw", amount="150.00", user_id=1, t=100)
        response = client.post("/event", json=event.model_dump())
        assert response.status_code == 200
        assert response.json() == {
            "alert": True,
            "alert_codes": [1100, 30],
            "user_id": 1,
        }

def test_event_endpoint_300(mock_db_session):
    with patch("src.main.check_three_consecutive_increasing_deposits", return_value=True):
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()
        event = EventPost(type="deposit", amount="150.00", user_id=1, t=100)
        response = client.post("/event", json=event.model_dump())
        assert response.status_code == 200
        assert response.json() == {
            "alert": True,
            "alert_codes": [300],
            "user_id": 1,
        }

def test_event_endpoint_123(mock_db_session):
    with patch("src.main.check_three_consecutive_increasing_deposits", return_value=True), \
         patch("src.main.check_accumulative_deposit_over_200", return_value=True):
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()
        event = EventPost(type="deposit", amount="150.00", user_id=1, t=100)
        response = client.post("/event", json=event.model_dump())
        assert response.status_code == 200
        assert response.json() == {
            "alert": True,
            "alert_codes": [300, 123],
            "user_id": 1,
        }

def test_event_endpoint_no_alerts(mock_db_session):
    with patch("src.main.check_three_consecutive_withdraws", return_value=False):
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()
        event = EventPost(type="withdraw", amount="50.00", user_id=1, t=10)
        response = client.post("/event", json=event.model_dump())
        assert response.status_code == 200
        assert response.json() == {
            "alert": False,
            "alert_codes": [],
            "user_id": 1,
        }