from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import clients, policies, conversations, documents, agent
from app.core.config import settings
from app.core.logger import setup_logger
from app.core.exceptions import register_exception_handlers
from app.db.init_db import init_db

# Setup logger
logger = setup_logger()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API for Beacon AI Insurance Advisor Platform",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
register_exception_handlers(app)

# Include API routes
app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(policies.router, prefix="/api/policies", tags=["policies"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully")

@app.get("/", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 