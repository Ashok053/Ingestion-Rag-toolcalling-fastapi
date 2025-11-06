from dataclasses import field

from pydantic import BaseModel, Field, EmailStr
from datetime import date, time
from typing import Optional

class BookingRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Candidate's full name")
    email: EmailStr = Field(..., description="Candidate's email address")
    booking_date: date = Field(..., description="Preferred date for interview")
    booking_time: time = Field(..., description="Preferred time for interview")

    class Config:
        schema_extra = {
            "example": {
                "name": "Ashok Lamsal",
                "email": "ashoklamsal007@gmail.com",
                "booking_date": "2025-11-04",
                "booking_time": "10:00"
            }
        }


class BookingResponse(BaseModel):
    success: bool = Field(default=True, description="Booking status")
    booking_id: int = Field(..., ge=1, description="Booking ID")
    name: str
    email: EmailStr
    booking_date: date
    booking_time: time
    message: str = Field(default="Interview booking confirmed successfully")

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "success": True,
                "booking_id": 1,
                "name": "John Doe",
                "email": "john.doe@example.com",
                "booking_date": "2025-11-05",
                "booking_time": "12:00",
                "message": "Interview booking confirmed successfully!"
            }
        }


class BookingListItem(BaseModel):
    id: int
    name: str
    email: str
    booking_date: date
    booking_time: time
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class BookingListResponse(BaseModel):
    total: int = Field(...,description="Total number of bookings")
    bookings: list[BookingListItem] = Field(...,description="List of all bookings")