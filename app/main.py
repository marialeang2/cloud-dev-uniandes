from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from app.api.v1 import auth, videos, public
from app.db.base import Base
from app.db.session import engine
from app.core.exceptions import (
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ValidationException,
    DuplicateException
)

app = FastAPI(
    title="ANB Rising Stars API",
    version="1.0.0",
    description="API REST for ANB Rising Stars Showcase Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Endpoints de autenticación y registro"
        },
        {
            "name": "Videos",
            "description": "Gestión de videos personales (requiere JWT)"
        },
        {
            "name": "Public",
            "description": "Endpoints públicos de videos y rankings"
        }
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers
@app.exception_handler(UnauthorizedException)
async def unauthorized_exception_handler(request: Request, exc: UnauthorizedException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)}
    )


@app.exception_handler(ForbiddenException)
async def forbidden_exception_handler(request: Request, exc: ForbiddenException):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": str(exc)}
    )


@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)}
    )


@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )


@app.exception_handler(DuplicateException)
async def duplicate_exception_handler(request: Request, exc: DuplicateException):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)}
    )


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(videos.router, prefix="/api/videos", tags=["Videos"])
app.include_router(public.router, prefix="/api/public", tags=["Public"])


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags
    )
    
    # Agregar esquema de seguridad Bearer JWT
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Ingresa tu token JWT (el sistema agregará 'Bearer' automáticamente)"
        }
    }
    
    # Aplicar seguridad a rutas específicas
    for path, path_item in openapi_schema["paths"].items():
        # Aplicar seguridad solo a rutas que NO son de autenticación ni públicas sin JWT
        if "/auth/" not in path and path not in ["/api/public/videos", "/api/public/rankings", "/", "/health"]:
            for method in path_item.values():
                if isinstance(method, dict) and "parameters" in method:
                    method["security"] = [{"bearerAuth": []}]
                elif isinstance(method, dict):
                    method["security"] = [{"bearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


@app.on_event("startup")
async def startup():
    """Create database tables on startup"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "ANB Rising Stars API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Root"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}