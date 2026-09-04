from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.scheduler_service import SchedulerService
from ..utils.helpers import generate_run_id
from datetime import datetime

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])
scheduler_service = SchedulerService()


@router.post("/run")
def run_smart_schedule(payload: dict = None, db: Session = Depends(get_db)):
    date_str = (payload or {}).get("date", datetime.now().strftime("%Y-%m-%d"))
    run_id = generate_run_id()
    result = scheduler_service.run_smart_schedule(db, date_str, run_id)
    return {"run_id": run_id, "date": date_str, **result}


@router.get("/latest")
def get_latest(db: Session = Depends(get_db)):
    return scheduler_service.get_latest_schedule(db, "optimized")
