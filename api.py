# api.py
from fastapi import FastAPI, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
from services import TaskService
from pydantic import BaseModel

app = FastAPI(title="Smart Todo (Gemini)")

svc = TaskService()  # in-memory for now

class AddReq(BaseModel):
    text: str

@app.post("/tasks")
def add_task(req: AddReq):
    try:
        task = svc.add_task(req.text)  # uses ai_client inside
        return task.model_dump()
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/tasks")
def list_tasks(category: Optional[str] = Query(None)):
    tasks = svc.list_tasks(category=category)
    return [t.model_dump() for t in tasks]

@app.get("/tasks/immediate")
def list_immediate(hours: int = 24):
    cutoff = datetime.now() + timedelta(hours=hours)
    tasks = svc.list_immediate(cutoff=cutoff)
    return [t.model_dump() for t in tasks]