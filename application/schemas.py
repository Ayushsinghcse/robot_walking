from pydantic import BaseModel
from typing import List, Optional

class Obstacle(BaseModel):
    x: float
    y: float
    width: float
    height: float

class TrajectoryCreate(BaseModel):
    wall_width: float
    wall_height: float
    obstacles: List[Obstacle] = []

class TrajectoryResponse(TrajectoryCreate):
    id: int
    trajectory: List[dict]
    coverage_time: float
    
    class Config:
        from_attributes = True