# services.py
from datetime import datetime
from typing import List, Optional
from sqlalchemy import and_, or_

from db import SessionLocal, init_db, TaskDB
from models import Task
from ai_client import categorize_and_enrich

init_db()

class TaskService:
    def __init__(self, session_id: str = "local"):
        self.db = SessionLocal()
        self.session_id = session_id  # <— stick to one session per service

    def _to_task(self, obj: TaskDB) -> Task:
        # Pydantic will ignore extra fields like session_id by default (v2)
        return Task.model_validate(obj.__dict__)

    def add_task(self, text: str) -> Task:
        meta = categorize_and_enrich(text)
        db_obj = TaskDB(
            text=text,
            category=meta["category"],
            priority=meta["priority"],
            due_dt=meta["due_dt"],
            created_at=datetime.now(),
            session_id=self.session_id,   # <— bind to session
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return self._to_task(db_obj)

    def list_tasks(self, category: Optional[str] = None) -> List[Task]:
        q = self.db.query(TaskDB).filter(TaskDB.session_id == self.session_id)
        if category:
            q = q.filter(TaskDB.category == category)
        return [self._to_task(o) for o in q.order_by(TaskDB.created_at.desc()).all()]

    def list_immediate(self, cutoff: datetime) -> List[Task]:
        q = self.db.query(TaskDB).filter(
            and_(
                TaskDB.session_id == self.session_id,
                TaskDB.status == "open",
                or_(
                    and_(TaskDB.due_dt.isnot(None), TaskDB.due_dt <= cutoff),
                    TaskDB.priority >= 4,
                ),
            )
        )
        return [self._to_task(o) for o in q.order_by(TaskDB.due_dt.asc().nulls_last()).all()]

    def mark_done(self, task_id: int) -> bool:
        obj = (
            self.db.query(TaskDB)
            .filter(TaskDB.session_id == self.session_id, TaskDB.id == task_id)
            .first()
        )
        if obj and obj.status == "open":
            obj.status = "done"
            self.db.commit()
            return True
        return False

    def delete(self, task_id: int) -> bool:
        obj = (
            self.db.query(TaskDB)
            .filter(TaskDB.session_id == self.session_id, TaskDB.id == task_id)
            .first()
        )
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False