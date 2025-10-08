# db.py
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

DB_PATH = os.getenv("TODO_DB_PATH", "sqlite:///tasks.db")
engine = create_engine(DB_PATH, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

Base = declarative_base()

class TaskDB(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    category = Column(String(50), default="personal")
    priority = Column(Integer, default=3)
    due_dt = Column(DateTime, nullable=True)
    status = Column(String(20), default="open")
    created_at = Column(DateTime, default=datetime.utcnow)

    # NEW: per-visitor isolation without login
    session_id = Column(String(64), index=True, nullable=False, default="public")

def init_db():
    Base.metadata.create_all(bind=engine)