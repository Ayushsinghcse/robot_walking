from sqlalchemy import Column, Integer, String, Float, JSON
from .database import Base

class Trajectory(Base):
    __tablename__ = "trajectories"
    
    id = Column(Integer, primary_key=True, index=True)
    wall_width = Column(Float)
    wall_height = Column(Float)
    obstacles = Column(JSON)  # List of obstacle dicts: {x, y, width, height}
    trajectory = Column(JSON)  # List of points: [{x, y}, ...]
    coverage_time = Column(Float)