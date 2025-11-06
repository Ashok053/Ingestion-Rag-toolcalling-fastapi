from sqlalchemy.orm import Session
from models.booking import Booking

class BookingService:
    @staticmethod
    def create_booking(db :Session,name:str, email:str, date:str, time:str) -> Booking:
        booking = Booking(
            name = name,
            email = email,
            booking_date = date,
            booking_time = time
        )

        db.add(booking)
        db.commit()
        db.refresh(booking)

        return booking

    @staticmethod
    def get_all_bookings(db:Session):
        return db.query(Booking).order_by(Booking.created_at.desc()).all()

    @staticmethod
    def get_booking_by_email(db:Session, email: str):
        return db.query(Booking).filter(email == Booking.email).all()