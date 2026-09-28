from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.forecast_service import ForecastService

router = APIRouter(prefix="/api/forecast", tags=["forecast"])
forecast_service = ForecastService()


@router.get("")
def get_forecast(date: str = Query(None), db: Session = Depends(get_db)):
    return forecast_service.get_forecast(db, date)


@router.post("/train")
def train_model(db: Session = Depends(get_db)):
    result = forecast_service.train_model(db)
    return {"status": "success", "metrics": result}


@router.get("/metrics")
def get_metrics():
    return forecast_service.get_model_metrics()


@router.get("/actual-vs-predicted")
def actual_vs_predicted(days: int = Query(30), db: Session = Depends(get_db)):
    return forecast_service.get_actual_vs_predicted(db, days)


@router.get("/error-analysis")
def error_analysis(db: Session = Depends(get_db)):
    return forecast_service.get_error_analysis(db)


@router.get("/errors")
def get_forecast_errors(db: Session = Depends(get_db)):
    return forecast_service.get_error_distribution(db)
