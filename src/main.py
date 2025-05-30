from fastapi import Depends, HTTPException, status
from src.schema import EventPost, EventResponse
from src.models import UserEvent
from sqlalchemy.orm import Session
from fastapi import FastAPI
from src.database import get_db, Base, engine
from contextlib import asynccontextmanager
import time
from sqlalchemy.exc import OperationalError

app = FastAPI()

@app.on_event("startup")
def on_startup():
    retries = 5
    while retries > 0:
        try:
            Base.metadata.create_all(bind=engine)
            break
        except OperationalError:
            retries -= 1
            time.sleep(2)
    else:
        raise Exception("Database connection failed after multiple retries.")
    

@app.post("/event", response_model=EventResponse)
async def handle_event(event: EventPost, db: Session = Depends(get_db)) -> EventResponse:
    user_id = event.user_id
    amount = float(event.amount)
    timestamp = event.t

    try:
        # Save the event to the database
        new_event = UserEvent(user_id=event.user_id, type=event.type, amount=float(event.amount), timestamp=event.t)
        db.add(new_event)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process event"
        )

    alert_codes = []

    rules = [
        (lambda amount, event_type, **kwargs: event_type == "withdraw" and amount > 100, 1100),  # Rule: Code 1100
        (lambda user_id, timestamp, **kwargs: check_three_consecutive_withdraws(db, user_id, timestamp), 30),  # Rule: Code 30
        (lambda user_id, timestamp, **kwargs: check_three_consecutive_increasing_deposits(db, user_id, timestamp), 300),  # Rule: Code 300
        (lambda user_id, timestamp, **kwargs: check_accumulative_deposit_over_200(db, user_id, timestamp), 123),  # Rule: Code 123
    ]

    for rule, code in rules:
        if rule(amount=amount, user_id=user_id, timestamp=timestamp, event_type=event.type):
            alert_codes.append(code)
    
    return EventResponse(alert=bool(alert_codes), alert_codes=alert_codes, user_id=user_id)


def check_three_consecutive_withdraws(session: Session, user_id: int, timestamp: int) -> bool:
    """
    Check if the user has 3 consecutive withdraws.
    """
    last_three_events = (
        session.query(UserEvent)
        .filter(UserEvent.user_id == user_id, UserEvent.timestamp <= timestamp)
        .order_by(UserEvent.timestamp.desc())
        .limit(3)
        .all()
    )
    return len(last_three_events) == 3 and all(event.type == "withdraw" for event in last_three_events)


def check_three_consecutive_increasing_deposits(session: Session, user_id: int, timestamp: int) -> bool:
    """
    Check if the user has 3 consecutive increasing deposits.
    """
    deposits = (
        session.query(UserEvent)
        .filter(UserEvent.user_id == user_id, UserEvent.type == "deposit", UserEvent.timestamp <= timestamp)
        .order_by(UserEvent.timestamp.asc())
        .all()
    )
    if len(deposits) < 3:
        return False

    # Check for 3 consecutive increasing deposits
    for i in range(len(deposits) - 2):
        if (
            deposits[i].amount < deposits[i + 1].amount
            and deposits[i + 1].amount < deposits[i + 2].amount
        ):
            return True
    return False


def check_accumulative_deposit_over_200(session: Session, user_id: int, current_timestamp: int) -> bool:
    """
    Check if the accumulative deposit amount over a window of 30 seconds before the given timestamp is over 200.
    """
    time_window_start = current_timestamp - 30
    deposits = (
        session.query(UserEvent)
        .filter(
            UserEvent.user_id == user_id,
            UserEvent.type == "deposit",
            UserEvent.timestamp >= time_window_start,
            UserEvent.timestamp <= current_timestamp,
        )
        .all()
    )
    total_deposit = sum(event.amount for event in deposits)
    return total_deposit > 200
