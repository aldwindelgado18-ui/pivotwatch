from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api import companies, changes, auth, users
import os

# Create upload directories
os.makedirs(settings.SCREENSHOT_PATH, exist_ok=True)
os.makedirs(settings.UPLOAD_PATH, exist_ok=True)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(companies.router, prefix="/api/companies", tags=["companies"])
app.include_router(changes.router, prefix="/api/changes", tags=["changes"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to PivotWatch API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}