from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.core.config import settings
from app.core.exceptions import APIException
from app.api.v1 import auth, videos, public

# Create FastAPI application
app = FastAPI(
    title="ANB Rising Stars API",
    version="1.0.0",
    description="API REST for ANB Rising Stars Showcase Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler for custom API exceptions
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(videos.router, prefix="/api/videos", tags=["Videos"])
app.include_router(public.router, prefix="/api/public", tags=["Public"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "ANB Rising Stars API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

