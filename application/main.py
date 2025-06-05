from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from .database import engine, Base
from .routers import trajectories

app = FastAPI(title="Autonomous Wall-Finishing Robot API")

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(trajectories.router, prefix="/api/trajectories")

# Mount static files
app.mount("/static", StaticFiles(directory="application/static"), name="static")

# Serve index.html at root
@app.get("/")
async def read_index():
    return FileResponse(Path("application/static/index.html"))