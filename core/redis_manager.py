import redis
import json
from typing import List, Dict, Optional
from core.configuration import settings

class RedisManager:
    """Manage chat memory using Redis"""

    def __init__(self):
        self.redis_client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
        self.max_history = 20
        self.ttl = 3600

    def save_message(self, session_id: str, role: str, message: str):
        """
        Save a chat message to Redis.
        :param session_id: user's session ID
        :param role: "user" or "assistant"
        :param message: message text
        """
        key = f"chat:{session_id}"
        msg = {"role": role, "message": message}

        # Add message to Redis list
        self.redis_client.rpush(key, json.dumps(msg))

        # Keep only the last N messages
        self.redis_client.ltrim(key, -self.max_history, -1)

        # Set expiration
        self.redis_client.expire(key, self.ttl)

    def get_history(self, session_id: str) -> List[Dict]:
        """Get chat history for a session as a list of messages"""
        key = f"chat:{session_id}"
        messages = self.redis_client.lrange(key, 0, -1)
        return [json.loads(msg) for msg in messages]

    def get_context(self, session_id: str, last_n: int = 5) -> str:
        """Get formatted context for LLM from the last N messages"""
        history = self.get_history(session_id)
        if not history:
            return ""

        recent = history[-last_n:]
        context = "Previous conversation:\n"
        for msg in recent:
            context += f"{msg['role'].capitalize()}: {msg['message']}\n"
        return context

    def clear_session(self, session_id: str):
        """Clear chat history for a session"""
        key = f"chat:{session_id}"
        self.redis_client.delete(key)

redis_manager = RedisManager()
