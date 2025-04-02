from sqlalchemy import Column, Integer, String, Float, BigInteger, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from src.database import Base

class UserEvent(Base):
    __tablename__ = "user_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(BigInteger, nullable=False)

    def __repr__(self):
        return f"<UserEvent(user_id={self.user_id}, type={self.type}, amount={self.amount}, timestamp={self.timestamp})>"
    