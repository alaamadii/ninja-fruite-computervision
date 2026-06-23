"""
Bomb class for Fruit Ninja game
Hazard obstacles that cost points if hit
"""

import cv2
import numpy as np
from config import SCREEN_HEIGHT, SCREEN_WIDTH


class Bomb:
    """
    Represents a bomb obstacle in the game
    
    Similar to Fruit but marked as obstacle
    Hitting a bomb costs points and loses a life
    """
    
    def __init__(self, x, y, vx, vy, radius=20):
        """
        Initialize a bomb
        
        Args:
            x, y: Starting position
            vx, vy: Starting velocity (pixels/second)
            radius: Radius in pixels
        """
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.radius = radius
        self.hit = False
        self.creation_time = 0.0
    
    def update(self, delta_time, gravity):
        """
        Update bomb position and velocity with physics
        
        Args:
            delta_time: Time since last frame in seconds
            gravity: Gravity acceleration in pixels/second^2
        """
        if self.hit:
            return
        
        # Apply gravity
        self.vy += gravity * delta_time
        
        # Update position
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
    
    def draw(self, frame):
        """
        Draw bomb on frame
        
        Args:
            frame: OpenCV frame to draw on
            
        Returns:
            Modified frame
        """
        if self.hit:
            return frame
        
        # Convert position to integers
        pos = (int(self.x), int(self.y))
        
        # Draw bomb as dark sphere with spiky top
        # Main body - dark gray
        cv2.circle(frame, pos, self.radius, (50, 50, 50), -1)
        cv2.circle(frame, pos, self.radius, (0, 0, 0), 2)  # Black border
        
        # Draw fuse (small line on top)
        fuse_top = (int(self.x), int(self.y) - self.radius - 8)
        fuse_bottom = (int(self.x), int(self.y) - self.radius + 2)
        cv2.line(frame, fuse_bottom, fuse_top, (100, 0, 0), 2)
        
        # Draw spark at top of fuse
        spark_pos = fuse_top
        cv2.circle(frame, spark_pos, 3, (0, 165, 255), -1)  # Orange spark
        
        # Draw warning indicator (red circle around it)
        cv2.circle(frame, pos, int(self.radius * 1.3), (0, 0, 255), 1)
        
        return frame
    
    def is_off_screen(self):
        """
        Check if bomb has left the screen
        
        Returns:
            True if bomb is off-screen
        """
        # Only remove if falling down, to allow spawning from below
        if self.y > SCREEN_HEIGHT + self.radius and self.vy > 0:
            return True
        if self.x < -self.radius or self.x > SCREEN_WIDTH + self.radius:
            return True
        return False
    
    def mark_hit(self):
        """Mark bomb as hit"""
        self.hit = True
    
    def get_position(self):
        """Return current position as tuple"""
        return (self.x, self.y)
    
    def get_bounds(self):
        """Get bounding box for collision detection"""
        return (
            self.x - self.radius,
            self.y - self.radius,
            self.x + self.radius,
            self.y + self.radius
        )
    
    def is_point_inside(self, px, py):
        """
        Check if point is inside bomb circle
        
        Args:
            px, py: Point coordinates
            
        Returns:
            True if point is inside bomb
        """
        dist = np.sqrt((px - self.x) ** 2 + (py - self.y) ** 2)
        return dist <= self.radius
    
    def __repr__(self):
        """String representation for debugging"""
        hit_str = " (hit)" if self.hit else ""
        return f"Bomb(at ({self.x:.0f},{self.y:.0f}), v=({self.vx:.0f},{self.vy:.0f}){hit_str})"
