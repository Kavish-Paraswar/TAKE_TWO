from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from .database import Base

class CreativeBrief(Base):
    __tablename__ = "creative_briefs"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(Text)

class CreativeRun(Base):
    __tablename__ = "creative_runs"
    id = Column(Integer, primary_key=True)
    state = Column(String, default="CREATED")  # CREATED, RUNNING, COMPLETED, FAILED, INTERRUPTED, APPROVED
    iteration = Column(Integer, default=0)
    progress = Column(Integer, default=0)
    client_token = Column(String, unique=True, nullable=True)  

class AgentRun(Base):
    __tablename__ = "agent_runs"
    id = Column(Integer, primary_key=True)
    creative_run_id = Column(Integer, ForeignKey("creative_runs.id"))
    agent_name = Column(String)
    iteration = Column(Integer, default=0)

class AgentMessage(Base):
    __tablename__ = "agent_messages"
    id = Column(Integer, primary_key=True)
    agent_run_id = Column(Integer, ForeignKey("agent_runs.id"))
    role = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Generation(Base):
    __tablename__ = "generations"
    id = Column(Integer, primary_key=True)
    creative_run_id = Column(Integer, ForeignKey("creative_runs.id"))
    asset_url = Column(String)
    meta = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
