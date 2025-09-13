# api.py
from fastapi import FastAPI, HTTPException, Query, Header
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from services import TaskService

app = FastAPI(title="Smart Todo (Gemini)")


class AddReq(BaseModel):
    text: str


class UpdateReq(BaseModel):
    status: Optional[str] = None  # currently supports "done"


def svc_for(session_id: str) -> TaskService:
    return TaskService(session_id=session_id or "public")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # or ["http://localhost:5173"] for stricter
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/tasks")
def add_task(
    req: AddReq, x_session_id: str = Header(default="public", alias="X-Session-Id")
):
    try:
        task = svc_for(x_session_id).add_task(req.text)
        return task.model_dump()
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/tasks")
def list_tasks(
    category: Optional[str] = Query(None),
    x_session_id: str = Header(default="public", alias="X-Session-Id"),
):
    tasks = svc_for(x_session_id).list_tasks(category=category)
    return [t.model_dump() for t in tasks]


@app.get("/tasks/immediate")
def list_immediate(
    hours: int = 24,
    x_session_id: str = Header(default="public", alias="X-Session-Id"),
):
    cutoff = datetime.now() + timedelta(hours=hours)
    tasks = svc_for(x_session_id).list_immediate(cutoff=cutoff)
    return [t.model_dump() for t in tasks]


@app.patch("/tasks/{task_id}")
def update_task(
    task_id: int,
    req: UpdateReq,
    x_session_id: str = Header(default="public", alias="X-Session-Id"),
):
    svc = svc_for(x_session_id)

    if req.status == "done":
        task = svc.mark_done(task_id)
        if not task:
            raise HTTPException(404, "Task not found or already done")
        return task.model_dump()

    raise HTTPException(400, "Unsupported update request")


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    x_session_id: str = Header(default="public", alias="X-Session-Id"),
):
    svc = svc_for(x_session_id)
    task = svc.delete(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task.model_dump()