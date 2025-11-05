from typing import Dict, Tuple, Optional
import json, re
from services.llm_service import llm_service
from services.rag_service import CustomRAG
from sqlalchemy.orm import Session

class ToolService:
    """Service to detect intent, handle bookings or answer questions."""

    @staticmethod
    def detect_intent(query: str) -> Dict:
        """Detect if user wants to book or ask a question using LLM"""
        prompt = f"""
        
        Analyze this message and return ONLY JSON:
        {{
        "intent": "book_interview" or "ask_question",
        "name": "full name or null",
        "email": "email or null",
        "date": "YYYY-MM-DD or null",
        "time": "HH:MM or null"
        }}
        Message: "{query}"
        """
        try:
            response = llm_service.generate(prompt, max_tokens=200, temperature=0.3)
            match = re.search(r'\{.*}', response, re.DOTALL)
            return json.loads(match.group()) if match else {"intent": "ask_question", "name": None, "email": None,
                                                            "date": None, "time": None}
        except:
            return {"intent": "ask_question", "name": None, "email": None, "date": None, "time": None}

    @staticmethod
    def extract_booking_info(query: str, intent_data: Dict) -> Optional[Dict]:
        """Return booking info if complete, else None"""
        if all(intent_data.get(k) for k in ["name", "email", "date", "time"]):
            return {k: intent_data[k] for k in ["name", "email", "date", "time"]}

        if intent_data["intent"] == "book_interview":
            prompt = f"""Extract JSON with name, email, date (YYYY-MM-DD), time (HH:MM) from: "{query}" """
            try:
                response = llm_service.generate(prompt, max_tokens=150, temperature=0.1)
                match = re.search(r'\{.*}', response, re.DOTALL)
                data = json.loads(match.group()) if match else {}
                if all(data.get(k) for k in ["name", "email", "date", "time"]):
                    return data
            except:
                return None
        return None

    @staticmethod
    def create_booking(booking_info: Dict, db: Session) -> Tuple[bool, str]:
        """Save booking in DB and return success message"""
        from models.booking import Booking
        from datetime import datetime

        # Map input keys to match DB model
        booking_data = {
            "name": booking_info["name"],
            "email": booking_info["email"],
            "booking_date": booking_info["date"],  # map 'date' -> 'booking_date'
            "booking_time": booking_info["time"]  # map 'time' -> 'booking_time'
        }

        # Validate date/time
        try:
            datetime.strptime(str(booking_data["booking_date"]), "%Y-%m-%d")
        except:
            return False, "Invalid date format. Use YYYY-MM-DD."

        try:
            datetime.strptime(str(booking_data["booking_time"]), "%H:%M")
        except:
            return False, "Invalid time format. Use HH:MM."

        try:
            booking = Booking(**booking_data)
            db.add(booking)
            db.commit()
            db.refresh(booking)
            msg = (
                f"Interview booked!\n"
                f"Name: {booking.name}\n"
                f"Email: {booking.email}\n"
                f"Date: {booking.booking_date}\n"
                f"Time: {booking.booking_time}\n"
                f"ID: {booking.id}"
            )
            return True, msg
        except Exception as e:
            db.rollback()
            return False, f"Failed to book: {e}"

    @staticmethod
    def process_query(query: str, chat_history: str, db: Session) -> Tuple[str, bool]:
        """Main entry: handle query"""
        intent_data = ToolService.detect_intent(query)

        if intent_data["intent"] == "book_interview":
            booking_info = ToolService.extract_booking_info(query, intent_data)
            if booking_info:
                # Fix: unpack correctly
                success, msg = ToolService.create_booking(booking_info, db)
                return msg, success  #  msg is string, success is bool
            else:
                missing = [k for k in ["name", "email", "date", "time"] if not intent_data.get(k)]
                msg = "Provide the following info to book interview:\n" + "\n".join(f"• {m}" for m in missing)
                return msg, False
        else:
            # Make sure answer is always string
            answer, _ = CustomRAG.answer_query(query, chat_history)
            if not isinstance(answer, str):
                answer = str(answer)
            return answer, False

