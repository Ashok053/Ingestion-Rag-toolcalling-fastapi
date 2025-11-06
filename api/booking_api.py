from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.booking_schema import BookingRequest, BookingResponse, BookingListResponse
from models.booking import Booking

router = APIRouter(
    prefix="/api/v1/bookings",
    tags=["Interview Booking"]
)

@router.post("/", response_model=BookingResponse)
async def create_booking(
        request: BookingRequest,
        db: Session = Depends(get_db)
):
    """
    Book an interview slot.
    This endpoint can be:
    - Called directly by users
    - Triggered by the RAG chatbot when user wants to schedule

    Parameters:
    - name: Full name of the candidate
    - email: Email address
    - date: Preferred interview date (YYYY-MM-DD)
    - time: Preferred interview time (HH:MM)

    Returns:
    - Booking confirmation with booking ID
    """
    try:
        print(f"  New booking request:")
        print(f"   Name: {request.name}")
        print(f"   Email: {request.email}")
        print(f"   Date: {request.date}, Time: {request.time}")

        # Create booking record in database
        booking = Booking(
            name=request.name,
            email=request.email,
            date=str(request.date),
            time=str(request.time)
        )

        db.add(booking)
        db.commit()
        db.refresh(booking)

        print(f"Booking created with ID: {booking.id}")

        return BookingResponse(
            success=True,
            booking_id=booking.id,
            name=booking.name,
            email=booking.email,
            booking_date=request.date,
            booking_time=request.time,
            message="Interview booking confirmed successfully!"
        )

    except Exception as e:
        db.rollback()
        print(f"   Booking failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create booking: {str(e)}"
        )


@router.get("/", response_model=BookingListResponse)
async def list_all_bookings(db: Session = Depends(get_db)):
    try:
        bookings = db.query(Booking).order_by(
            Booking.created_at.desc()
        ).all()

        from schemas.booking_schema import BookingListItem

        booking_items = [
            BookingListItem(
                id=b.id,
                name=b.name,
                email=b.email,
                booking_date=b.booking_date,
                booking_time=b.booking_time,
                created_at=b.created_at.isoformat() if b.created_at else None
            )
            for b in bookings
        ]

        return BookingListResponse(
            total=len(booking_items),
            bookings=booking_items
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve bookings: {str(e)}"
        )

