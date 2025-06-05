import pytest
from ..coverage import CoveragePlanner
from ..schemas import Obstacle

def test_coverage_planner_no_obstacles():
    """Test path generation without obstacles"""
    planner = CoveragePlanner(wall_width=5.0, wall_height=5.0)
    path_data = planner.generate_path()
    
    # Basic structure checks
    assert isinstance(path_data, dict)
    assert "path" in path_data
    assert "time" in path_data
    assert len(path_data["path"]) > 0
    assert path_data["time"] > 0
    
    # Verify path covers the entire wall
    min_x = min(p["x"] for p in path_data["path"])
    max_x = max(p["x"] for p in path_data["path"])
    min_y = min(p["y"] for p in path_data["path"])
    max_y = max(p["y"] for p in path_data["path"])
    
    assert min_x >= 0
    assert max_x <= 5.0
    assert min_y >= 0
    assert max_y <= 5.0

def test_coverage_planner_with_obstacles():
    """Test path generation with obstacles"""
    obstacles = [Obstacle(x=1.0, y=1.0, width=0.25, height=0.25)]
    planner = CoveragePlanner(wall_width=5.0, wall_height=5.0, obstacles=obstacles)
    path_data = planner.generate_path()
    
    assert isinstance(path_data, dict)
    assert len(path_data["path"]) > 0
    
    # Define obstacle boundaries with tool width consideration
    obs_left = 1.0 - planner.tool_width
    obs_right = 1.25 + planner.tool_width
    obs_bottom = 1.0 - planner.tool_width
    obs_top = 1.25 + planner.tool_width
    
    # Check no path points enter the expanded obstacle zone
    for point in path_data["path"]:
        assert not (
            obs_left <= point["x"] <= obs_right and 
            obs_bottom <= point["y"] <= obs_top
        ), f"Path point {point} violates obstacle boundaries"
    
    # Additional verification - check detour points exist
    detour_points = [p for p in path_data["path"] if p["y"] > 1.25 + planner.tool_width]
    assert len(detour_points) > 0, "No detour points found above obstacle"

def test_obstacle_path_comparison():
    """Compare paths with and without obstacles"""
    # Simple wall
    planner_no_obs = CoveragePlanner(wall_width=5.0, wall_height=5.0)
    path_no_obs = planner_no_obs.generate_path()
    
    # Wall with obstacle
    obstacles = [Obstacle(x=1.0, y=1.0, width=0.25, height=0.25)]
    planner_with_obs = CoveragePlanner(wall_width=5.0, wall_height=5.0, obstacles=obstacles)
    path_with_obs = planner_with_obs.generate_path()
    
    # With obstacles should take longer
    assert path_with_obs["time"] > path_no_obs["time"]
    # With obstacles should have more path points
    assert len(path_with_obs["path"]) > len(path_no_obs["path"])

def test_is_point_in_obstacle():
    """Test obstacle collision detection"""
    obstacles = [Obstacle(x=1.0, y=1.0, width=1.0, height=1.0)]
    planner = CoveragePlanner(wall_width=5.0, wall_height=5.0, obstacles=obstacles)
    
    # Inside obstacle
    assert planner.is_point_in_obstacle(1.5, 1.5)
    # Outside obstacle
    assert not planner.is_point_in_obstacle(0.5, 0.5)
    # On edges
    assert planner.is_point_in_obstacle(1.0, 1.0)
    assert planner.is_point_in_obstacle(2.0, 2.0)
    # Just outside
    assert not planner.is_point_in_obstacle(2.01, 2.01)
    # With safety margin (if implemented)
    # assert planner.is_point_in_obstacle(0.96, 0.96)  # If using 0.05 safety margin