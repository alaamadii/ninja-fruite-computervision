"""
Fruit class for Fruit Ninja game
Handles fruit physics, rendering, and lifecycle
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import platform

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GRAVITY,
    FRUIT_RADIUS, FRUIT_COLORS, FRUIT_SPAWN_HEIGHT
)

class EmojiRenderer:
    def __init__(self):
        self.cache = {}
        self.fonts = {}
        self.font_path = "seguiemj.ttf" if platform.system() == "Windows" else "Apple Color Emoji.ttc"
        
    def _get_font(self, size):
        if size in self.fonts:
            return self.fonts[size]
        try:
            font = ImageFont.truetype(self.font_path, size)
        except:
            try:
                font = ImageFont.truetype("NotoColorEmoji.ttf", size)
            except:
                font = ImageFont.load_default()
        self.fonts[size] = font
        return font

    def get_emoji_image(self, emoji_char, size=60):
        key = (emoji_char, size)
        if key in self.cache:
            return self.cache[key]
        
        # Create a blank transparent image
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        font = self._get_font(size)
        
        # Draw the text
        if font != ImageFont.load_default():
            draw.text((size//2, size//2), emoji_char, font=font, fill=(255, 255, 255, 255), anchor="mm", embedded_color=True)
        else:
            draw.text((size//2, size//2), emoji_char, fill=(255, 255, 255, 255), anchor="mm")
            
        # Convert to numpy array
        # PIL puts RGBA, we need to handle it. The color is BGR in OpenCV, but emojis have their own colors.
        # Image is RGBA.
        emoji_array = np.array(img)
        # Convert RGB to BGR for OpenCV
        if emoji_array.shape[2] == 4:
            r, g, b, a = cv2.split(emoji_array)
            emoji_array = cv2.merge((b, g, r, a))
            
        self.cache[key] = emoji_array
        return emoji_array

# Global renderer
emoji_renderer = EmojiRenderer()


class Fruit:
    """
    Represents a single fruit in the game
    
    Attributes:
        x, y: Position in pixels
        vx, vy: Velocity in pixels/second
        fruit_type: Type of fruit (affects color and points)
        radius: Radius in pixels
        sliced: Whether fruit has been sliced
        creation_time: When fruit was created
    """
    
    # Fruit types with emoji representations
    TYPES = ['apple', 'orange', 'watermelon', 'banana', 'peach', 'grape', 'strawberry', 'lemon', 'mango', 'pineapple']
    FRUIT_EMOJIS = {
        'apple': '🍎',
        'orange': '🍊',
        'watermelon': '🍉',
        'banana': '🍌',
        'peach': '🍑',
        'grape': '🍇',
        'strawberry': '🍓',
        'lemon': '🍋',
        'mango': '🥭',
        'pineapple': '🍍'
    }
    
    def __init__(self, x, y, vx, vy, fruit_type='apple', radius=FRUIT_RADIUS):
        """
        Initialize a fruit
        
        Args:
            x, y: Starting position
            vx, vy: Starting velocity (pixels/second)
            fruit_type: Type of fruit (determines color)
            radius: Radius in pixels
        """
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.fruit_type = fruit_type
        self.radius = radius
        self.sliced = False
        self.creation_time = 0.0  # Set by spawner
        
    def update(self, delta_time):
        """
        Update fruit position and velocity with physics
        
        Args:
            delta_time: Time since last frame in seconds
        """
        if self.sliced:
            return  # Don't update sliced fruits
            
        # Apply gravity (pixels/second^2)
        self.vy += GRAVITY * delta_time
        
        # Update position
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        
    def draw(self, frame):
        """
        Draw fruit on frame using emoji characters
        
        Args:
            frame: OpenCV frame to draw on
            
        Returns:
            Modified frame
        """
        if self.sliced:
            return frame  # Don't draw sliced fruits
            
        # Convert position to integers
        pos = (int(self.x), int(self.y))
        
        # Get emoji for this fruit type
        emoji = self.FRUIT_EMOJIS.get(self.fruit_type, '🍎')
        
        # Add glow effect - draw circle around emoji for visibility
        color = FRUIT_COLORS.get(self.fruit_type, (0, 255, 0))
        cv2.circle(frame, pos, self.radius + 5, color, 1)  # Thin glow circle
        
        # Get emoji image
        size = int(self.radius * 2.5)
        emoji_img = emoji_renderer.get_emoji_image(emoji, size=size)
        
        # Overlay emoji on frame
        h, w = emoji_img.shape[:2]
        x_min = int(pos[0] - w/2)
        y_min = int(pos[1] - h/2)
        x_max = x_min + w
        y_max = y_min + h
        
        # Check bounds
        if x_min >= 0 and y_min >= 0 and x_max < frame.shape[1] and y_max < frame.shape[0]:
            # Alpha blending
            alpha = emoji_img[:, :, 3] / 255.0
            for c in range(3):
                frame[y_min:y_max, x_min:x_max, c] = (
                    alpha * emoji_img[:, :, c] +
                    (1 - alpha) * frame[y_min:y_max, x_min:x_max, c]
                )
        
        return frame
        
    def is_off_screen(self):
        """
        Check if fruit has left the screen
        
        Returns:
            True if fruit is off-screen
        """
        # Off screen if below, left, or right of screen
        # Only remove if falling down, to allow spawning from below
        if self.y > SCREEN_HEIGHT + self.radius and self.vy > 0:
            return True
        if self.x < -self.radius or self.x > SCREEN_WIDTH + self.radius:
            return True
        return False
        
    def slice(self):
        """Mark fruit as sliced"""
        self.sliced = True
        
    def get_position(self):
        """Return current position as tuple"""
        return (self.x, self.y)
        
    def get_bounds(self):
        """
        Get bounding box for collision detection
        
        Returns:
            Tuple of (x_min, y_min, x_max, y_max)
        """
        return (
            self.x - self.radius,
            self.y - self.radius,
            self.x + self.radius,
            self.y + self.radius
        )
        
    def is_point_inside(self, px, py):
        """
        Check if point is inside fruit circle
        
        Args:
            px, py: Point coordinates
            
        Returns:
            True if point is inside fruit
        """
        dist = np.sqrt((px - self.x) ** 2 + (py - self.y) ** 2)
        return dist <= self.radius
        
    def __repr__(self):
        """String representation for debugging"""
        sliced_str = " (sliced)" if self.sliced else ""
        return f"Fruit({self.fruit_type} at ({self.x:.0f},{self.y:.0f}), v=({self.vx:.0f},{self.vy:.0f}){sliced_str})"
