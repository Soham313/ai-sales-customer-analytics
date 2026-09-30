from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api import auth, upload, dashboard, sales, customers, forecasting, anomalies, ai_analyst
from app.database.session import engine, Base
from app.models import database  # registers tables

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Sales & Customer Analytics Platform API",
    description="Backend services for business sales forecasting, RFM customer clustering, anomaly detection, and AI analyst insights.",
    version="1.0.0"
)

# CORS configurations
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
origins = [
    frontend_url,
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(sales.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(forecasting.router, prefix="/api")
app.include_router(anomalies.router, prefix="/api")
app.include_router(ai_analyst.router, prefix="/api")

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "message": "AI Sales & Customer Analytics Platform API is running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
