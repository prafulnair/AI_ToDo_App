from datetime import datetime, timedelta
from typing import List, Optional
from itertools import count

from models import Task
from ai_client import categorize_and_enrich

import json
from datetime import datetime

def _task_to_dict(t):
    d = t.model_dump()
    if d.get("due_dt"):
        d["due_dt"] = t.due_dt.isoformat()
    d["created_at"] = t.created_at.isoformat()
    return d

def _task_from_dict(d):
    d = d.copy()
    if d.get("due_dt"):
        d["due_dt"] = datetime.fromisoformat(d["due_dt"])
    d["created_at"] = datetime.fromisoformat(d["created_at"])
    from models import Task
    return Task(**d)

class TaskService:
    def __init__(self):
        self._id = count(1)
        self._tasks: List[Task] = []

    def add_task(self, text: str) -> Task:
        meta = categorize_and_enrich(text)
        task = Task(
            id=next(self._id),
            text=text,
            category=meta["category"],
            priority=meta["priority"],
            due_dt=meta["due_dt"],
            created_at=datetime.now(),
        )
        self._tasks.append(task)
        return task

    def list_tasks(self, category: Optional[str] = None) -> List[Task]:
        if not category:
            return list(self._tasks)
        cat = category.lower()
        return [t for t in self._tasks if t.category == cat]

    def list_immediate(self, cutoff: datetime) -> List[Task]:
        return [
            t for t in self._tasks
            if t.status == "open" and (
                (t.due_dt and t.due_dt <= cutoff) or t.priority >= 4
            )
        ]
    def mark_done(self, task_id: int) -> bool:
        for t in self._tasks:
            if t.id == task_id and t.status == "open":
                t.status = "done"
                return True
        return False

    def delete(self, task_id: int) -> bool:
        before = len(self._tasks)
        self._tasks = [t for t in self._tasks if t.id != task_id]
        return len(self._tasks) < before

    def save(self, path: str = "tasks.json") -> None:
        data = [_task_to_dict(t) for t in self._tasks]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self, path: str = "tasks.json") -> int:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return 0
        self._tasks = [_task_from_dict(d) for d in data]
        # reset id counter to max+1
        if self._tasks:
            from itertools import count
            self._id = count(max(t.id for t in self._tasks) + 1)
        return len(self._tasks)