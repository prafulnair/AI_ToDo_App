# api.py
from fastapi import FastAPI, HTTPException, Query, Header
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from services import TaskService

app = FastAPI(title="Smart Todo (Gemini)")

class AddReq(BaseModel):
    text: str

def svc_for(session_id: str) -> TaskService:
    return TaskService(session_id=session_id or "public")

@app.post("/tasks")
def add_task(req: AddReq, x_session_id: str = Header(default="public", alias="X-Session-Id")):
    try:
        task = svc_for(x_session_id).add_task(req.text)
        return task.model_dump()
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/tasks")
def list_tasks(category: Optional[str] = Query(None), x_session_id: str = Header(default="public", alias="X-Session-Id")):
    tasks = svc_for(x_session_id).list_tasks(category=category)
    return [t.model_dump() for t in tasks]

@app.get("/tasks/immediate")
def list_immediate(hours: int = 24, x_session_id: str = Header(default="public", alias="X-Session-Id")):
    cutoff = datetime.now() + timedelta(hours=hours)
    tasks = svc_for(x_session_id).list_immediate(cutoff=cutoff)
    return [t.model_dump() for t in tasks]