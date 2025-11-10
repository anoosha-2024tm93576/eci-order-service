from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from .api import router
from .db import engine, init_db
from .config import settings

app = FastAPI(title="Order Service", version="1.0.0")

# Add Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

app.include_router(router)

@app.on_event("startup")
def startup():
    # Initialize DB (create tables if they don't exist)
    init_db(engine)

@app.get("/health")
def health():
    return {"status": "ok", "service": "order", "port": settings.SERVICE_PORT}
