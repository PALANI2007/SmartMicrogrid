from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import EdgeCaseResult, Load, BatteryConfig
import json
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

router = APIRouter(prefix='/api/edge-cases', tags=['edge-cases'])


@router.get('')
def get_edge_case_results(db: Session = Depends(get_db)):
    results = db.query(EdgeCaseResult).order_by(EdgeCaseResult.run_at.desc()).all()
    return [
        {
            'id': r.id, 'scenario_id': r.scenario_id, 'name': r.name,
            'status': r.status, 'smart_metrics': json.loads(r.smart_metrics or '{}'),
            'baseline_metrics': json.loads(r.baseline_metrics or 'null'),
            'violations': json.loads(r.violations or '{}'),
            'explanation': r.explanation, 'run_at': r.run_at.isoformat()
        } for r in results
    ]


@router.post('/run')
def run_edge_case(payload: dict, db: Session = Depends(get_db)):
    scenario_id = payload.get('scenario_id', 'all')

    loads = [
        {'id': l.id, 'name': l.name, 'load_type': l.load_type, 'power_kw': l.power_kw,
         'duration_hours': l.duration_hours, 'earliest_start': l.earliest_start,
         'latest_finish': l.latest_finish, 'priority': l.priority}
        for l in db.query(Load).filter(Load.is_active == True).all()
    ]
    battery_db = db.query(BatteryConfig).first()
    battery_config = {
        'capacity_kwh': battery_db.capacity_kwh if battery_db else 10.0,
        'initial_soc': battery_db.initial_soc if battery_db else 0.5,
        'minimum_soc': battery_db.minimum_soc if battery_db else 0.2,
        'maximum_soc': battery_db.maximum_soc if battery_db else 0.95,
        'max_charge_kw': battery_db.max_charge_kw if battery_db else 3.0,
        'max_discharge_kw': battery_db.max_discharge_kw if battery_db else 3.0,
        'charging_efficiency': battery_db.charging_efficiency if battery_db else 0.95,
        'discharging_efficiency': battery_db.discharging_efficiency if battery_db else 0.95,
    } if battery_db else {
        'capacity_kwh': 10.0, 'initial_soc': 0.5, 'minimum_soc': 0.2,
        'maximum_soc': 0.95, 'max_charge_kw': 3.0, 'max_discharge_kw': 3.0,
        'charging_efficiency': 0.95, 'discharging_efficiency': 0.95
    }

    from scheduler.edge_cases import EdgeCaseSimulator
    simulator = EdgeCaseSimulator()

    scenarios = ['monsoon_cloud_cover', 'low_battery', 'essential_load_surge', 'deadline_conflict']
    if scenario_id != 'all' and scenario_id in scenarios:
        scenarios = [scenario_id]

    results = []
    for sid in scenarios:
        result = simulator.run_scenario(sid, loads, battery_config)
        # Save to DB
        record = EdgeCaseResult(
            scenario_id=result['scenario_id'],
            name=result['name'],
            status=result['status'],
            smart_metrics=json.dumps(result['smart_metrics']),
            baseline_metrics=json.dumps(result.get('baseline_metrics')),
            schedule_summary=json.dumps(result.get('schedule', [])[:5]),
            violations=json.dumps(result['violations']),
            explanation=result['explanation'],
            run_at=datetime.utcnow()
        )
        db.add(record)
        results.append(result)

    db.commit()
    return {'scenarios_run': len(results), 'results': results}
