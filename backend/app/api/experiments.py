from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import ExperimentResult
from ..services.scheduler_service import SchedulerService
from ..utils.helpers import generate_run_id
from datetime import datetime

router = APIRouter(prefix="/api/experiments", tags=["experiments"])
scheduler_service = SchedulerService()


@router.post("/run")
def run_experiment(payload: dict, db: Session = Depends(get_db)):
    date_str = payload.get("date_str", datetime.now().strftime("%Y-%m-%d"))
    experiment_name = payload.get("experiment_name", f"Experiment {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    run_id = generate_run_id()
    
    # Run both schedulers
    baseline_result = scheduler_service.run_baseline_schedule(db, date_str, run_id + "_baseline")
    smart_result = scheduler_service.run_smart_schedule(db, date_str, run_id + "_smart")
    
    baseline_metrics = baseline_result.get("metrics", {})
    smart_metrics = smart_result.get("metrics", {})
    
    # Calculate improvements
    improvements = {}
    for key in baseline_metrics:
        if isinstance(baseline_metrics[key], (int, float)) and key in smart_metrics:
            bval = baseline_metrics[key]
            sval = smart_metrics[key]
            if key in ["renewable_self_consumption_pct"]:
                improvements[key] = round(sval - bval, 2)  # higher is better
            elif key in ["renewable_export_kwh", "grid_energy_kwh", "deadline_violations", "comfort_violations"]:
                improvements[key] = round(bval - sval, 2)  # lower is better
            else:
                improvements[key] = round(sval - bval, 2)
    
    # Save result
    exp_result = ExperimentResult(
        run_id=run_id,
        experiment_name=experiment_name,
        schedule_type="comparison",
        renewable_self_consumption_pct=smart_metrics.get("renewable_self_consumption_pct", 0),
        renewable_export_kwh=smart_metrics.get("renewable_export_kwh", 0),
        renewable_curtailment_kwh=smart_metrics.get("renewable_curtailment_kwh", 0),
        grid_energy_kwh=smart_metrics.get("grid_energy_kwh", 0),
        battery_charge_kwh=smart_metrics.get("battery_charge_kwh", 0),
        battery_discharge_kwh=smart_metrics.get("battery_discharge_kwh", 0),
        flexible_completion_rate=smart_metrics.get("flexible_completion_rate", 0),
        deadline_violations=int(smart_metrics.get("deadline_violations", 0)),
        comfort_violations=int(smart_metrics.get("comfort_violations", 0)),
        essential_interruptions=0,
        user_disruption_score=smart_metrics.get("user_disruption_score", 0),
        total_renewable_kwh=smart_metrics.get("total_renewable_kwh", 0),
        self_consumed_kwh=smart_metrics.get("self_consumed_kwh", 0),
        created_at=datetime.utcnow(),
        notes=f"Baseline vs Smart comparison for {date_str}",
    )
    db.add(exp_result)
    db.commit()
    db.refresh(exp_result)
    
    return {
        "run_id": run_id,
        "experiment_name": experiment_name,
        "date_str": date_str,
        "baseline": {
            "schedule": baseline_result.get("schedule", []),
            "metrics": baseline_metrics,
        },
        "optimized": {
            "schedule": smart_result.get("schedule", []),
            "metrics": smart_metrics,
        },
        "improvements": improvements,
        "created_at": exp_result.created_at.isoformat(),
    }


@router.get("/results")
def get_results(db: Session = Depends(get_db)):
    results = db.query(ExperimentResult).order_by(ExperimentResult.created_at.desc()).all()
    return [
        {c.name: getattr(r, c.name) for c in r.__table__.columns}
        for r in results
    ]


@router.get("/results/latest")
def get_latest_result(db: Session = Depends(get_db)):
    result = db.query(ExperimentResult).order_by(ExperimentResult.created_at.desc()).first()
    if not result:
        raise HTTPException(status_code=404, detail="No experiment results found")
    return {c.name: getattr(result, c.name) for c in result.__table__.columns}


@router.get("/results/{run_id}")
def get_result_by_id(run_id: str, db: Session = Depends(get_db)):
    result = db.query(ExperimentResult).filter(ExperimentResult.run_id == run_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return {c.name: getattr(result, c.name) for c in result.__table__.columns}
