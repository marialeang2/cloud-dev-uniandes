from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
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


# Exception handler for Pydantic validation errors (422 -> 400)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert 422 Unprocessable Entity to 400 Bad Request for validation errors"""
    errors = exc.errors()
    
    # Extract first error message for simplicity
    first_error = errors[0] if errors else {}
    field = " -> ".join(str(loc) for loc in first_error.get("loc", []))
    msg = first_error.get("msg", "Validation error")
    
    # Create readable error message
    if field and field != "body":
        detail = f"Validation error in field '{field}': {msg}"
    else:
        detail = msg
    
    return JSONResponse(
        status_code=400,  # Changed from 422 to 400
        content={
            "detail": detail,
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

