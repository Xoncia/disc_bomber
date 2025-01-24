from datetime import datetime
from typing import Any
from sqlalchemy import DateTime
from app.database.session import db

class BaseModel(db.Model):
    """Base model class with common fields and methods"""
    
    __abstract__ = True

    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id: Any) -> Any:
        return cls.query.get(id) 