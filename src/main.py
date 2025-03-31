from fastapi import HTTPException, Depends
from src.schema import EventPost, EventResponse
from starlette import status
from typing import List
from src.models import UserEvent
from sqlalchemy.orm import Session
from src.models import UserEvent
from fastapi import FastAPI
from database import get_db

app = FastAPI()

@app.post("/event", response_model=EventResponse)
async def handle_event(event: EventPost, db: Session = Depends(get_db)):
    user_id = event.user_id
    amount = float(event.amount)
    timestamp = event.t

    # Save the event to the database
    new_event = UserEvent(user_id=user_id, type=event.type, amount=amount, timestamp=timestamp)
    db.add(new_event)
    db.commit()

    # Initialize alert codes
    alert_codes = []

    # Rule: Code 1100 - A withdraw amount over 100
    if event.type == "withdraw" and amount > 100:
        alert_codes.append(1100)

    # Rule: Code 30 - 3 consecutive withdraws
    if check_three_consecutive_withdraws(db, user_id):
        alert_codes.append(30)

    # Rule: Code 300 - 3 consecutive increasing deposits
    if check_three_consecutive_increasing_deposits(db, user_id):
        alert_codes.append(300)

    # Rule: Code 123 - Accumulative deposit amount over 30 seconds > 200
    if check_accumulative_deposit_over_200(db, user_id, timestamp):
        alert_codes.append(123)

    # Determine if alert is true
    alert = bool(alert_codes)

    # Return the response
    return EventResponse(alert=alert, alert_codes=alert_codes, user_id=user_id)


def check_three_consecutive_withdraws(session: Session, user_id: int) -> bool:
    """
    Check if the user has 3 consecutive withdraws.
    """
    last_three_events = (
        session.query(UserEvent)
        .filter(UserEvent.user_id == user_id)
        .order_by(UserEvent.timestamp.desc())
        .limit(3)
        .all()
    )
    return len(last_three_events) == 3 and all(event.type == "withdraw" for event in last_three_events)

def check_three_consecutive_increasing_deposits(session: Session, user_id: int) -> bool:
    """
    Check if the user has 3 consecutive increasing deposits (ignoring withdraws).
    """
    deposits = (
        session.query(UserEvent)
        .filter(UserEvent.user_id == user_id, UserEvent.type == "deposit")
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
    Check if the accumulative deposit amount over a window of 30 seconds is over 200.
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