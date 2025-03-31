from pydantic import BaseModel, Field
from typing import List, Literal
from enum import Enum

class AlertCode(int, Enum):
    WITHDRAW_OVER_100 = 1100
    THREE_CONSECUTIVE_WITHDRAWS = 30
    THREE_CONSECUTIVE_INCREASING_DEPOSITS = 300
    ACCUMULATIVE_DEPOSIT_OVER_200 = 123

class EventPost(BaseModel):
    type: Literal["deposit", "withdraw"]
    amount: str
    user_id: int
    t: int

class EventResponse(BaseModel):
    alert: bool
    alert_codes: List[AlertCode] = Field(default_factory=list)
    user_id: int