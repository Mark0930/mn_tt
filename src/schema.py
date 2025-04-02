from pydantic import BaseModel, Field, AfterValidator
from typing import List, Literal, Annotated
from enum import IntEnum
from decimal import Decimal

class AlertCode(IntEnum):
    WITHDRAW_OVER_100 = 1100
    THREE_WITHDRAWS = 30
    INCREASING_DEPOSITS = 300
    DEPOSIT_OVER_200 = 123

def validate_event_type(value: str) -> str:
    if value not in ['deposit', 'withdraw']:
        raise ValueError('Event type must be either deposit or withdraw')
    return value

def validate_amount(value: str) -> str:
    amount = Decimal(value)
    if amount <= 0:
        raise ValueError('Amount must be positive')
    return value

class EventPost(BaseModel):
    type: Annotated[str, AfterValidator(validate_event_type)]
    amount: Annotated[str, AfterValidator(validate_amount)]
    user_id: int
    t: int

class EventResponse(BaseModel):
    alert: bool
    alert_codes: List[int] = Field(default_factory=list)
    user_id: int
    