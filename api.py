# api.py
from fastapi import FastAPI, HTTPException, Query, Header
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from services import TaskService

from services import TaskService
from ai_client import parse_command_nlp, summarize_tasks, filter_tasks_with_ai 
from db import SessionLocal, TaskDB
from ai_client import detect_intent




app = FastAPI(title="Smart Todo (Gemini)")


class AddReq(BaseModel):
    text: str


class UpdateReq(BaseModel):
    status: Optional[str] = None  # currently supports "done"


def svc_for(session_id: str) -> TaskService:
    return TaskService(session_id=session_id or "public")

class NLPCommandReq(BaseModel):
    text: str



class SummaryReq(BaseModel):
    text: Optional[str] = None           # raw "summarize today"
    timeframe: Optional[str] = None      # "today" | "this_week" | "all"
    category: Optional[str] = None       # e.g., "work", "social"



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # or ["http://localhost:5173"] for stricter
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/nlp/intent")
def classify_intent(req: NLPCommandReq):
    try:
        intent = detect_intent(req.text)
        return intent
    except Exception as e:
        raise HTTPException(500, str(e))

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


@app.post("/nlp/command")
def nlp_command(
    req: NLPCommandReq,
    x_session_id: str = Header(default="public", alias="X-Session-Id"),
):
    """
    Accepts a natural language command (e.g. 'show all work tasks today')
    Returns structured intent JSON via AI.
    """
    try:
        db = SessionLocal()
        # collect current categories for this session
        existing = [
            row[0]
            for row in db.query(TaskDB.category)
            .filter(TaskDB.session_id == x_session_id)
            .distinct()
            .all()
        ]
        db.close()

        intent = parse_command_nlp(req.text, existing_categories=existing)
        return intent
    except Exception as e:
        raise HTTPException(500, str(e))
    

@app.post("/summary")
def generate_summary(
    req: SummaryReq,
    x_session_id: str = Header(default="public", alias="X-Session-Id"),
):
    """
    Summarize the tasks for the user. if the 'text' is provided run through NLP Parser
    Else use timeframe/catgeory directly
    """

    try:
        db = SessionLocal()

        # 1. resolve intent
        if req.text:
            # collect catgeories for parser context
            existing = [
                row[0]
                for row in db.query(TaskDB.category)
                .filter(TaskDB.session_id == x_session_id)
                .distinct()
                .all()
            ]
            intent = parse_command_nlp(req.text, existing_categories=existing)

        else:
            intent = {
                "action": "summarize",
                "category": req.category,
                "timeframe": req.timeframe or "all",
                "rationale": "direct summary request"
            }

        # 2. select tasks by session
        q = db.query(TaskDB).filter(TaskDB.session_id == x_session_id)

        if intent.get("timeframe") == "today":
            start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            q = q.filter(TaskDB.due_dt >= start, TaskDB.due_dt < end)
        elif intent.get("timeframe") == "this_week":
            start = datetime.now() - timedelta(days=datetime.now().weekday())
            end = start + timedelta(days=7)
            q = q.filter(TaskDB.due_dt >= start, TaskDB.due_dt < end)

        tasks = [
            {
                "id": t.id,
                "text": t.text,
                "category": t.category,
                "status": t.status,
                "priority": t.priority,
                "due_dt": t.due_dt.isoformat() if t.due_dt else None,
            }
            for t in q.all()
        ]
        db.close()

        # NEW STEP: refine by category_query if it's not an exact match
        category_query = intent.get("category")
        if category_query:
            existing_categories = {t["category"] for t in tasks}
            if category_query not in existing_categories:
                # call AI filter
                tasks = filter_tasks_with_ai(tasks, category_query)

        if not tasks:
            return {
                "headline": "No tasks matched your request",
                "kpis": { "open": 0, "completed": 0, "overdue": 0, "due_today": 0 },
                "highlights": [],
                "by_category": [],
                "urgent_ids": [],
                "overdue_ids": [],
                "markdown": f"No tasks found for '{category_query}' in {intent.get('timeframe')}"
            }

        # 3. Call summarizer
        summary = summarize_tasks(tasks, intent)
        return summary

    except Exception as e:
        raise HTTPException(500, str(e))