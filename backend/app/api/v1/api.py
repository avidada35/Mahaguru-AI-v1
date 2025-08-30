from fastapi import APIRouter

from app.api.v1.endpoints import ai, documents, users, auth

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
