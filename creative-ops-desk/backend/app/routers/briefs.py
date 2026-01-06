from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models, schemas

router = APIRouter(prefix="/briefs")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_brief(b: schemas.BriefCreate, db: Session = Depends(get_db)):
    brief = models.CreativeBrief(
        title=b.title,
        description=b.description
    )
    db.add(brief)
    db.commit()
    db.refresh(brief)
    return brief
