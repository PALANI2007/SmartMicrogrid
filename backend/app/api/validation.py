from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import ValidationResponse
from datetime import datetime

router = APIRouter(prefix="/api/validation", tags=["validation"])


@router.post("")
def submit_validation(payload: dict, db: Session = Depends(get_db)):
    resp = ValidationResponse(
        respondent_name=payload.get("respondent_name"),
        q1_understandable=int(payload.get("q1_understandable", 3)),
        q2_explanation_clear=int(payload.get("q2_explanation_clear", 3)),
        q3_disruption=int(payload.get("q3_disruption", 3)),
        q4_easy_to_read=int(payload.get("q4_easy_to_read", 3)),
        q5_language_useful=int(payload.get("q5_language_useful", 3)),
        q6_confidence_clear=int(payload.get("q6_confidence_clear", 3)),
        overall_satisfaction=float(payload.get("overall_satisfaction", 3.0)),
        created_at=datetime.utcnow(),
        notes=payload.get("notes"),
    )
    db.add(resp)
    db.commit()
    db.refresh(resp)
    return {"status": "success", "id": resp.id}


@router.get("")
def get_validations(db: Session = Depends(get_db)):
    responses = db.query(ValidationResponse).all()
    result = []
    for r in responses:
        d = {c.name: getattr(r, c.name) for c in r.__table__.columns}
        if d.get("created_at"):
            d["created_at"] = d["created_at"].isoformat()
        result.append(d)
    
    if result:
        avg_scores = {
            "q1_avg": sum(r["q1_understandable"] for r in result) / len(result),
            "q2_avg": sum(r["q2_explanation_clear"] for r in result) / len(result),
            "q3_avg": sum(r["q3_disruption"] for r in result) / len(result),
            "q4_avg": sum(r["q4_easy_to_read"] for r in result) / len(result),
            "q5_avg": sum(r["q5_language_useful"] for r in result) / len(result),
            "q6_avg": sum(r["q6_confidence_clear"] for r in result) / len(result),
            "overall_avg": sum(r.get("overall_satisfaction", 3) for r in result) / len(result),
        }
    else:
        avg_scores = {}
    
    return {"responses": result, "averages": avg_scores, "count": len(result)}
