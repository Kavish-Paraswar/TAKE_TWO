from pydantic import BaseModel
from typing import Any
from datetime import datetime

class BriefCreate(BaseModel):
    title: str
    description: str

class AgentMessageOut(BaseModel):
    id: int
    role: str
    content: str
    timestamp: datetime
    class Config:
        orm_mode = True

class GenerationOut(BaseModel):
    id: int
    asset_url: str
    meta: Any
    created_at: datetime
    class Config:
        orm_mode = True
