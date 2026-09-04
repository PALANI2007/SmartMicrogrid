from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.metrics_service import MetricsService

router = APIRouter(prefix="/api", tags=["dashboard"])
metrics_service = MetricsService()


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    return metrics_service.get_dashboard_metrics(db)


@router.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    from ..services.forecast_service import ForecastService
    fs = ForecastService()
    return fs.get_model_metrics()
