from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models, orchestrator
import uuid

router = APIRouter(prefix="/runs")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/start")
def start_run_from_brief(title: str = Query(...), description: str = Query(...),
                         background_tasks: BackgroundTasks = None, db: Session = Depends(get_db)):
    
    brief = models.CreativeBrief(title=title, description=description)
    db.add(brief); db.commit(); db.refresh(brief)


    token = uuid.uuid4().hex
    run = models.CreativeRun(state="CREATED", iteration=0, progress=0, client_token=token)
    db.add(run); db.commit(); db.refresh(run)

    
    if background_tasks is not None:
        background_tasks.add_task(orchestrator.run_creative_pipeline, run.id, brief.description)
    else:
        orchestrator.run_creative_pipeline(run.id, brief.description)

    return {"run_id": run.id, "brief_id": brief.id, "token": token, "state": run.state}

def _verify_token(db: Session, run_id: int, token: str):
    run = db.query(models.CreativeRun).filter_by(id=run_id).first()
    if not run or run.client_token != token:
        raise HTTPException(status_code=404, detail="Run not found or invalid token")
    return run

@router.get("/{run_id}/status")
def status(run_id: int, token: str = Query(...), db: Session = Depends(get_db)):
    run = _verify_token(db, run_id, token)
    return {"id": run.id, "state": run.state, "iteration": run.iteration, "progress": run.progress}

@router.get("/{run_id}/agents")
def agent_logs(run_id: int, token: str = Query(...), db: Session = Depends(get_db)):
    _verify_token(db, run_id, token)
    return (
        db.query(models.AgentMessage)
        .join(models.AgentRun)
        .filter(models.AgentRun.creative_run_id == run_id)
        .order_by(models.AgentMessage.timestamp)
        .all()
    )

@router.get("/{run_id}/outputs")
def outputs(run_id: int, token: str = Query(...), db: Session = Depends(get_db)):
    _verify_token(db, run_id, token)
    return db.query(models.Generation).filter_by(creative_run_id=run_id).all()

@router.post("/{run_id}/interrupt")
def interrupt_run(run_id: int, token: str = Query(...), db: Session = Depends(get_db)):
    run = _verify_token(db, run_id, token)
    run.state = "INTERRUPTED"
    db.add(run); db.commit()
    return {"status": "interrupted"}

@router.post("/{run_id}/approve")
def approve_run(run_id: int, token: str = Query(...), db: Session = Depends(get_db)):
    run = _verify_token(db, run_id, token)
    run.state = "APPROVED"
    db.add(run); db.commit()
    return {"status": "approved"}
