"""
Database schema for storing line-crossing events.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class Crossing(Base):
    __tablename__ = "crossings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    camera_id = Column(String, nullable=False)
    object_class = Column(String, nullable=False)
    direction = Column(String, nullable=False)  # "in" or "out"
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Crossing {self.object_class} {self.direction} @ {self.timestamp}>"