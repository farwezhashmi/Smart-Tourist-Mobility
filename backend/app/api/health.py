from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)) -> dict[str, int | str]:
    try:
        db.execute(text("SELECT 1"))
        location_count = db.execute(text("SELECT COUNT(*) FROM locations WHERE is_active = TRUE")).scalar_one()
        transport_mode_count = db.execute(text("SELECT COUNT(*) FROM transport_modes")).scalar_one()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="PostgreSQL is unavailable. Start Docker Compose or PostgreSQL on port 5432.",
        ) from exc

    return {
        "status": "ok",
        "database": "connected",
        "location_count": location_count,
        "transport_mode_count": transport_mode_count,
    }
