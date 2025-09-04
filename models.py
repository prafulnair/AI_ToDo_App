from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

Category = Literal["work", "personal", "health", "career", "errand"]

class Task(BaseModel):
    id: int
    text: str
    category: Category = "personal"
    priority: int = 3  # 1–5
    due_dt: Optional[datetime] = None
    status: Literal["open", "done"] = "open"
    created_at: datetime