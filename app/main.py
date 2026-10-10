from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import APP_TITLE, APP_VERSION, BASE_DIR
from app.db.database import init_db
from app.api.jobs import router as jobs_router
from app.api.certificates import router as certs_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="Bulk Certificate Generation System with REST API, Validation, Isolated Failure Handling & Verification",
    lifespan=lifespan
)


# Mount API Routers
app.include_router(jobs_router)
app.include_router(certs_router)

# Static files directory
static_dir = BASE_DIR / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", include_in_schema=False)
def serve_dashboard():
    """Serve the Web UI Dashboard."""
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {
        "app": APP_TITLE,
        "version": APP_VERSION,
        "docs": "/docs",
        "status": "online"
    }
