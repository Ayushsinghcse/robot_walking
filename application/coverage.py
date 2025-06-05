import math
from typing import List, Dict, Tuple
from .schemas import Obstacle
import logging

logger = logging.getLogger(__name__)

class CoveragePlanner:
    def __init__(self, wall_width: float, wall_height: float, obstacles: List[Obstacle] = []):
        self.wall_width = wall_width
        self.wall_height = wall_height
        self.obstacles = obstacles
        self.tool_width = 0.3  # 30cm tool width
        self.robot_speed = 0.5  # 0.5 m/s constant speed
        
    def is_point_in_obstacle(self, x: float, y: float) -> bool:
        """Check if a point is inside any obstacle"""
        for obstacle in self.obstacles:
            if (obstacle.x <= x <= obstacle.x + obstacle.width and
                obstacle.y <= y <= obstacle.y + obstacle.height):
                return True
        return False
    
    def line_intersects_obstacle(self, start: Tuple[float, float], end: Tuple[float, float], 
                               obstacle: Obstacle) -> bool:
        """Check if a line segment intersects with an obstacle"""
        # Simple bounding box intersection check
        rect_left = obstacle.x
        rect_right = obstacle.x + obstacle.width
        rect_top = obstacle.y
        rect_bottom = obstacle.y + obstacle.height
        
        # Check if either point is inside the obstacle
        if self.is_point_in_obstacle(start[0], start[1]) or self.is_point_in_obstacle(end[0], end[1]):
            return True
            
        # Check line segment intersection with rectangle edges
        # (This is a simplified version - a complete implementation would use proper line-rectangle intersection)
        return False
    
    def calculate_detour_distance(self, obstacle: Obstacle, current_y: float) -> float:
        """Calculate additional distance needed to go around an obstacle"""
        # Go up and over the obstacle
        detour_height = self.tool_width * 2  # Go up and back down
        return (obstacle.width + detour_height) * 2  # Extra distance for going around
    
    def generate_path(self) -> Dict:
        """Generate a boustrophedon path for wall coverage with obstacle avoidance"""
        path = []
        current_y = 0
        direction = 1  # 1 for right, -1 for left
        coverage_time = 0
        total_distance = 0
        
        while current_y < self.wall_height:
            if direction == 1:
                start_x = 0
                end_x = self.wall_width
            else:
                start_x = self.wall_width
                end_x = 0
                
            start_point = (start_x, current_y)
            end_point = (end_x, current_y)
            
            # Check for obstacles in this row
            row_obstacles = [
                obs for obs in self.obstacles
                if obs.y <= current_y <= obs.y + obs.height
            ]
            
            if not row_obstacles:
                # No obstacles in this row - straight path
                path.append({"x": start_x, "y": current_y})
                path.append({"x": end_x, "y": current_y})
                distance = abs(end_x - start_x)
                total_distance += distance
            else:
                # Handle obstacles in this row
                path.append({"x": start_x, "y": current_y})
                
                for obstacle in sorted(row_obstacles, key=lambda o: o.x if direction == 1 else -o.x):
                    # Go up and around the obstacle
                    detour_distance = self.calculate_detour_distance(obstacle, current_y)
                    total_distance += detour_distance
                    
                    if direction == 1:
                        # Right-moving pass
                        path.append({"x": obstacle.x, "y": current_y})
                        path.append({"x": obstacle.x, "y": current_y + self.tool_width})
                        path.append({"x": obstacle.x + obstacle.width, "y": current_y + self.tool_width})
                        path.append({"x": obstacle.x + obstacle.width, "y": current_y})
                    else:
                        # Left-moving pass
                        path.append({"x": obstacle.x + obstacle.width, "y": current_y})
                        path.append({"x": obstacle.x + obstacle.width, "y": current_y + self.tool_width})
                        path.append({"x": obstacle.x, "y": current_y + self.tool_width})
                        path.append({"x": obstacle.x, "y": current_y})
                
                path.append({"x": end_x, "y": current_y})
                total_distance += abs(end_x - start_x)
            
            # Move to next row
            current_y += self.tool_width
            direction *= -1
        
        # Calculate coverage time based on total distance
        coverage_time = total_distance / self.robot_speed
        
        logger.info(
            f"Generated path covering {self.wall_width}x{self.wall_height}m wall with "
            f"{len(self.obstacles)} obstacles. Total distance: {total_distance:.2f}m, "
            f"Time: {coverage_time:.2f}s"
        )
        
        return {
            "path": path,
            "time": coverage_time
        }