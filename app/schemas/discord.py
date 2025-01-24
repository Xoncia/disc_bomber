from pydantic import BaseModel, Field
from datetime import datetime

class TokenSchema(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=100)
    token: str = Field(..., min_length=50, max_length=100)
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True 