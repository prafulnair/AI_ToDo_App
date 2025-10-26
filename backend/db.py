# db.py
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, UniqueConstraint
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import json

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


class CategoryMeta(Base):
    """
    Per (session_id, category) metadata used for renaming/splitting.
    Vectors/arrays are stored as JSON text for SQLite simplicity.
    """
    __tablename__ = "category_meta"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(64), index=True, nullable=False, default="public")
    category = Column(String(50), nullable=False)  # canonical, current label

    # Stats
    size = Column(Integer, default=0)
    label_fit = Column(Float, default=0.0)  # mean(label_emb • task_emb)

    # Stored as JSON strings
    centroid_json = Column(Text, nullable=True)       # [float,...]
    sample_texts_json = Column(Text, nullable=True)   # ["task1", "task2", ...] (cap ~5)
    top_keywords_json = Column(Text, nullable=True)   # ["garbage","dishes","kitchen"]
    top_entities_json = Column(Text, nullable=True)   # ["person:wife","place:airport"]

    # Governance
    last_renamed_at = Column(DateTime, nullable=True)
    label_history_json = Column(Text, nullable=True)  # ["Old Label 1","Old Label 2"]

    updated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("session_id", "category", name="uq_meta_session_category"),
    )

    # Helpers (optional): small accessors for json blobs
    def set_centroid(self, vec):
        self.centroid_json = json.dumps(vec) if vec is not None else None

    def get_centroid(self):
        try:
            return json.loads(self.centroid_json) if self.centroid_json else None
        except Exception:
            return None

    def set_sample_texts(self, arr):
        self.sample_texts_json = json.dumps(arr or [])

    def get_sample_texts(self):
        try:
            return json.loads(self.sample_texts_json) if self.sample_texts_json else []
        except Exception:
            return []

    def set_top_keywords(self, arr):
        self.top_keywords_json = json.dumps(arr or [])

    def get_top_keywords(self):
        try:
            return json.loads(self.top_keywords_json) if self.top_keywords_json else []
        except Exception:
            return []

    def set_top_entities(self, arr):
        self.top_entities_json = json.dumps(arr or [])

    def get_top_entities(self):
        try:
            return json.loads(self.top_entities_json) if self.top_entities_json else []
        except Exception:
            return []

    def set_label_history(self, arr):
        self.label_history_json = json.dumps(arr or [])

    def get_label_history(self):
        try:
            return json.loads(self.label_history_json) if self.label_history_json else []
        except Exception:
            return []


class CategoryAlias(Base):
    """
    Maps legacy labels/aliases to the current canonical category per session.
    Used before embeddings/fuzzy to keep snapping stable after renames/splits.
    """
    __tablename__ = "category_aliases"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(64), index=True, nullable=False, default="public")
    alias = Column(String(50), nullable=False)        # e.g., "Household Waste"
    canonical = Column(String(50), nullable=False)    # e.g., "Household chores"

    updated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("session_id", "alias", name="uq_alias_session_alias"),
    )

def init_db():
    Base.metadata.create_all(bind=engine)