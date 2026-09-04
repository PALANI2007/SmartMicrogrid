from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Load
from ..schemas import LoadResponse, LoadCreate, LoadUpdate
from ..utils.data_validation import validate_load

router = APIRouter(prefix="/api/loads", tags=["loads"])

@router.get("/", response_model=List[LoadResponse])
def get_loads(db: Session = Depends(get_db)):
    return db.query(Load).all()

@router.post("/", response_model=LoadResponse)
def create_load(load_in: LoadCreate, db: Session = Depends(get_db)):
    is_valid, msg = validate_load(load_in.model_dump())
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)
    load = Load(**load_in.model_dump())
    db.add(load)
    db.commit()
    db.refresh(load)
    return load

@router.put("/{load_id}", response_model=LoadResponse)
def update_load(load_id: int, load_in: LoadUpdate, db: Session = Depends(get_db)):
    is_valid, msg = validate_load(load_in.model_dump())
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)
    load = db.query(Load).filter(Load.id == load_id).first()
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")
    for k, v in load_in.model_dump().items():
        setattr(load, k, v)
    db.commit()
    db.refresh(load)
    return load

@router.delete("/{load_id}")
def delete_load(load_id: int, db: Session = Depends(get_db)):
    load = db.query(Load).filter(Load.id == load_id).first()
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")
    db.delete(load)
    db.commit()
    return {"message": "Deleted"}
