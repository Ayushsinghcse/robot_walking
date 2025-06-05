import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..main import app
from ..database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_trajectory():
    response = client.post(
        "/api/trajectories/",
        json={
            "wall_width": 5.0,
            "wall_height": 5.0,
            "obstacles": [{"x": 1.0, "y": 1.0, "width": 0.25, "height": 0.25}]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["wall_width"] == 5.0
    assert data["wall_height"] == 5.0
    assert len(data["obstacles"]) == 1
    assert len(data["trajectory"]) > 0
    assert data["coverage_time"] > 0

def test_get_trajectories():
    response = client.get("/api/trajectories/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "trajectory" in data[0]

def test_get_trajectory():
    # First create a trajectory
    create_response = client.post(
        "/api/trajectories/",
        json={
            "wall_width": 3.0,
            "wall_height": 3.0,
            "obstacles": []
        }
    )
    trajectory_id = create_response.json()["id"]
    
    # Then get it
    response = client.get(f"/api/trajectories/{trajectory_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == trajectory_id
    assert data["wall_width"] == 3.0
    assert data["wall_height"] == 3.0

def test_get_nonexistent_trajectory():
    response = client.get("/api/trajectories/999999")
    assert response.status_code == 404