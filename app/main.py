from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import Base, engine, connect_db, disconnect_db
from app.api.characters import router as characters_router
from app.api.films import router as films_router
from app.api.starships import router as starships_router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    await connect_db()
    logger.info("Database connected")
    yield
    # Shutdown
    logger.info("Shutting down...")
    await disconnect_db()
    logger.info("Database disconnected")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A RESTful API that interacts with the Star Wars API (SWAPI) to provide information about Star Wars characters, films, and starships with voting capabilities.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Star Wars API",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


# Include API routers
app.include_router(characters_router, prefix=settings.API_V1_STR)
app.include_router(films_router, prefix=settings.API_V1_STR)
app.include_router(starships_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
