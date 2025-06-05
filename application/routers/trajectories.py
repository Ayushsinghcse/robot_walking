from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from typing import List

from .. import schemas, crud, coverage
from ..database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.TrajectoryResponse)
def create_trajectory(
    trajectory: schemas.TrajectoryCreate, 
    db: Session = Depends(get_db)
):
    try:
        # Generate coverage path
        planner = coverage.CoveragePlanner(
            wall_width=trajectory.wall_width,
            wall_height=trajectory.wall_height,
            obstacles=trajectory.obstacles
        )
        path_data = planner.generate_path()
        
        # database storage
        db_trajectory = crud.create_trajectory(db, trajectory, path_data)
        return db_trajectory
    except Exception as e:
        logger.error(f"Error creating trajectory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[schemas.TrajectoryResponse])
def read_trajectories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    trajectories = crud.get_trajectories(db, skip=skip, limit=limit)
    return trajectories

@router.get("/{trajectory_id}", response_model=schemas.TrajectoryResponse)
def read_trajectory(trajectory_id: int, db: Session = Depends(get_db)):
    db_trajectory = crud.get_trajectory(db, trajectory_id=trajectory_id)
    if db_trajectory is None:
        raise HTTPException(status_code=404, detail="Trajectory not found")
    return db_trajectory