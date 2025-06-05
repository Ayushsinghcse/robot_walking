from application.models import Trajectory
from application.schemas import TrajectoryCreate, TrajectoryResponse
import logging

logger = logging.getLogger(__name__)

def create_trajectory(db, trajectory: TrajectoryCreate, path_data: dict):
    db_trajectory = Trajectory(
        wall_width=trajectory.wall_width,
        wall_height=trajectory.wall_height,
        obstacles=[obs.model_dump() for obs in trajectory.obstacles],
        trajectory=path_data["path"],
        coverage_time=path_data["time"]
    )
    db.add(db_trajectory)
    db.commit()
    db.refresh(db_trajectory)
    logger.info(f"Created trajectory with ID {db_trajectory.id}")
    return db_trajectory

def get_trajectory(db, trajectory_id: int):
    return db.query(Trajectory).filter(Trajectory.id == trajectory_id).first()

def get_trajectories(db, skip: int = 0, limit: int = 100):
    return db.query(Trajectory).offset(skip).limit(limit).all()