from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.trips import router as trips_router
from app.db.session import initialize_local_database

app = FastAPI(title="Smart Tourist Mobility API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(trips_router, prefix="/api")

initialize_local_database()
