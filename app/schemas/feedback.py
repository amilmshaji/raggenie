
from pydantic import BaseModel
from typing import Optional

class ChatFeedbackUpdate(BaseModel):
    chat_id: str
    feedback_status: int  # 1 for like, -1 for dislike
    feedback_json: Optional[dict] = None  # e.g., {"comment": "Helpful", "suggestion": "Add more details"}
