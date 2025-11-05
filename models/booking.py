from sqlalchemy import Column, Integer, String,DateTime
from core.database import Base
from datetime import datetime

class Booking(Base):
    """store interivew booking information"""
    __tablename__ ="bookingInfo"

    id = Column(Integer,primary_key=True, index = True)
    name = Column(String,nullable=False)
    email = Column(String,nullable=False)
    booking_date = Column(String,nullable=False)
    booking_time = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)