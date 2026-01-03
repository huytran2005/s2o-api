from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from utils.dependencies import get_current_user
from models.user_point import UserPoint

router = APIRouter(prefix="/points", tags=["Points"])


@router.get("/me")
def my_points(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    record = db.query(UserPoint).filter(
        UserPoint.user_id == current_user.id
    ).first()

    return {
        "total_points": record.total_points if record else 0
    }
