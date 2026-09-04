from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import get_settings
from .database import init_db

from .api import forecast, loads, battery, scheduler, baseline, experiments, dashboard, validation

settings = get_settings()

app = FastAPI(title="Renewable Microgrid Scheduler API", debug=settings.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(forecast.router)
app.include_router(loads.router)
app.include_router(battery.router)
app.include_router(scheduler.router)
app.include_router(baseline.router)
app.include_router(experiments.router)
app.include_router(dashboard.router)
app.include_router(validation.router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"message": str(exc)})

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
