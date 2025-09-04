# services.py
from datetime import datetime
from typing import List, Optional

from db import SessionLocal, init_db, TaskDB
from models import Task
from ai_client import categorize_and_enrich

init_db()

class TaskService:
    def __init__(self):
        self.db = SessionLocal()

    def add_task(self, text: str) -> Task:
        meta = categorize_and_enrich(text)
        db_obj = TaskDB(
            text=text,
            category=meta["category"],
            priority=meta["priority"],
            due_dt=meta["due_dt"],
            created_at=datetime.now(),
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return Task.model_validate(db_obj.__dict__)

    def list_tasks(self, category: Optional[str] = None) -> List[Task]:
        q = self.db.query(TaskDB)
        if category:
            q = q.filter(TaskDB.category == category)
        return [Task.model_validate(obj.__dict__) for obj in q.all()]

    def list_immediate(self, cutoff: datetime) -> List[Task]:
        q = self.db.query(TaskDB).filter(
            (TaskDB.status == "open") &
            ((TaskDB.due_dt != None) & (TaskDB.due_dt <= cutoff) | (TaskDB.priority >= 4))
        )
        return [Task.model_validate(obj.__dict__) for obj in q.all()]

    def mark_done(self, task_id: int) -> bool:
        obj = self.db.query(TaskDB).filter(TaskDB.id == task_id).first()
        if obj and obj.status == "open":
            obj.status = "done"
            self.db.commit()
            return True
        return False

    def delete(self, task_id: int) -> bool:
        obj = self.db.query(TaskDB).filter(TaskDB.id == task_id).first()
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False