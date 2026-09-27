from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, project, workspace

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(workspace.router, prefix="/workspaces", tags=["Workspaces"])
api_router.include_router(project.router, prefix="/projects", tags=["Projects"])
