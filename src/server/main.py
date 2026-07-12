from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.server.core.config import settings
from src.server.core.database import client
from src.server.core.security_hardening import RateLimiterMiddleware
from src.server.api.v1.auth import router as auth_router
from src.server.api.v1.collaboration import router as collaboration_router
from src.server.api.v1.meetings import router as meetings_router
from src.server.api.v1.video import websocket_router as video_router
from src.server.api.v1.documents import router as documents_router
from src.server.api.v1.payments import router as payments_router
from src.server.api.v1.security import router as security_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0"
)

# Add Rate Limiting Middleware
app.add_middleware(RateLimiterMiddleware)

# Conditional CORS Configuration
if settings.ENVIRONMENT == "production":
    allow_origins = ["https://nexus-khaki-phi.vercel.app"] # Replace with actual domain
else:
    allow_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=f"{settings.API_STR}/auth", tags=["Authentication"])
app.include_router(collaboration_router, prefix=f"{settings.API_STR}/collaboration", tags=["Collaboration"])
app.include_router(meetings_router, prefix=f"{settings.API_STR}/meetings", tags=["Meetings"])
app.include_router(video_router, prefix=f"{settings.API_STR}/video", tags=["Video"])
app.include_router(documents_router, prefix=f"{settings.API_STR}/documents", tags=["Documents"])
app.include_router(payments_router, prefix=f"{settings.API_STR}/payments", tags=["Payments"])
app.include_router(security_router, prefix=f"{settings.API_STR}/security", tags=["Security"])

# Global Exception Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail
            }
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred."
            }
        },
    )

# Health Check Endpoint
@app.get("/health")
async def health_check():
    try:
        await client.admin.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error": {
                    "code": "DATABASE_UNAVAILABLE",
                    "message": "Database connection failed."
                }
            }
        )
