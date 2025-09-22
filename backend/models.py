from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class Task(BaseModel):
    id: int
    text: str
    category: str  # dynamic, AI can generate or reuse existing
    priority: int = 3  # 1–5
    due_dt: Optional[datetime] = None
    status: Literal["open", "done"] = "open"
    created_at: datetime