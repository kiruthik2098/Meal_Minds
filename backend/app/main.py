from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.api import router

app = FastAPI(
    title="Smart Food Waste Predictor API",
    description="Intelligent meal demand forecasting, buffer recommendation, and waste reduction API for college canteens.",
    version="1.0.0"
)

# CORS middleware for React Vite frontend (port 5173, 3000, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "service": "Smart Food Waste Predictor API",
        "version": "1.0.0",
        "documentation": "/docs"
    }
