import pytest
from ..coverage import CoveragePlanner
from ..schemas import Obstacle

def test_coverage_planner_no_obstacles():
    planner = CoveragePlanner(wall_width=5.0, wall_height=5.0)
    path_data = planner.generate_path()
    
    assert isinstance(path_data, dict)
    assert "path" in path_data
    assert "time" in path_data
    assert len(path_data["path"]) > 0
    assert path_data["time"] > 0
    
    # Check path covers the wall
    min_x = min(p["x"] for p in path_data["path"])
    max_x = max(p["x"] for p in path_data["path"])
    min_y = min(p["y"] for p in path_data["path"])
    max_y = max(p["y"] for p in path_data["path"])
    
    assert min_x >= 0
    assert max_x <= 5.0
    assert min_y >= 0
    assert max_y <= 5.0

def test_coverage_planner_with_obstacles():
    obstacles = [Obstacle(x=1.0, y=1.0, width=0.25, height=0.25)]
    planner = CoveragePlanner(wall_width=5.0, wall_height=5.0, obstacles=obstacles)
    path_data = planner.generate_path()
    
    assert isinstance(path_data, dict)
    assert len(path_data["path"]) > 0
    
    # Check path avoids obstacles (simplified check)
    for point in path_data["path"]:
        assert not (1.0 <= point["x"] <= 1.25 and 1.0 <= point["y"] <= 1.25)

def test_is_point_in_obstacle():
    obstacles = [Obstacle(x=1.0, y=1.0, width=1.0, height=1.0)]
    planner = CoveragePlanner(wall_width=5.0, wall_height=5.0, obstacles=obstacles)
    
    assert planner.is_point_in_obstacle(1.5, 1.5)  # Inside obstacle
    assert not planner.is_point_in_obstacle(0.5, 0.5)  # Outside obstacle
    assert planner.is_point_in_obstacle(1.0, 1.0)  # On edge
    assert planner.is_point_in_obstacle(2.0, 2.0)  # On opposite edge
    assert not planner.is_point_in_obstacle(2.01, 2.01)  # Just outside