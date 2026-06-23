"""
HUD Module
On-screen display for score, lives, and game information
"""

import cv2
import numpy as np
from config import COLOR_WHITE, COLOR_RED, COLOR_GREEN, COLOR_YELLOW


class HUD:
    """Heads-Up Display for game information"""
    
    def __init__(self):
        """Initialize HUD"""
        self.score = 0
        self.lives = 3
        self.combo = 0
        self.fruits_sliced = 0
        self.game_mode = "Playing"  # Playing, GameOver, Menu, etc.
        
    def set_score(self, score: int):
        """Set current score"""
        self.score = score
    
    def set_lives(self, lives: int):
        """Set remaining lives"""
        self.lives = lives
    
    def set_combo(self, combo: int):
        """Set combo counter"""
        self.combo = combo
    
    def set_game_mode(self, mode: str):
        """Set current game mode"""
        self.game_mode = mode
    
    def set_fruits_sliced(self, count: int):
        """Set fruits sliced counter"""
        self.fruits_sliced = count
    
    def draw(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw HUD elements on frame
        
        Args:
            frame: Input frame
            
        Returns:
            Frame with HUD drawn
        """
        frame = self._draw_score(frame)
        frame = self._draw_lives(frame)
        frame = self._draw_combo(frame)
        frame = self._draw_game_mode(frame)
        frame = self._draw_fruits_sliced(frame)
        
        return frame
    
    def _draw_score(self, frame: np.ndarray, position: tuple = (10, 60),
                    font_scale: float = 1.2) -> np.ndarray:
        """Draw score on frame"""
        score_text = f"Score: {self.score}"
        cv2.putText(frame, score_text, position, cv2.FONT_HERSHEY_SIMPLEX,
                   font_scale, COLOR_YELLOW, 2)
        return frame
    
    def _draw_lives(self, frame: np.ndarray, position: tuple = (10, 100),
                    font_scale: float = 1.2) -> np.ndarray:
        """Draw lives on frame"""
        lives_text = f"Lives: {self.lives}"
        color = COLOR_RED if self.lives <= 1 else COLOR_GREEN
        cv2.putText(frame, lives_text, position, cv2.FONT_HERSHEY_SIMPLEX,
                   font_scale, color, 2)
        return frame
    
    def _draw_combo(self, frame: np.ndarray, position: tuple = (10, 140),
                    font_scale: float = 1.0) -> np.ndarray:
        """Draw combo counter on frame"""
        if self.combo > 0:
            combo_text = f"Combo: {self.combo}x"
            cv2.putText(frame, combo_text, position, cv2.FONT_HERSHEY_SIMPLEX,
                       font_scale, COLOR_YELLOW, 2)
        return frame
    
    def _draw_game_mode(self, frame: np.ndarray, position: tuple = (10, 180),
                        font_scale: float = 1.0) -> np.ndarray:
        """Draw game mode on frame"""
        mode_text = f"Mode: {self.game_mode}"
        cv2.putText(frame, mode_text, position, cv2.FONT_HERSHEY_SIMPLEX,
                   font_scale, COLOR_WHITE, 2)
        return frame
    
    def _draw_fruits_sliced(self, frame: np.ndarray, position: tuple = (10, 220),
                            font_scale: float = 1.0) -> np.ndarray:
        """Draw fruits sliced counter on frame"""
        text = f"Fruits Sliced: {self.fruits_sliced}"
        cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX,
                   font_scale, COLOR_WHITE, 2)
        return frame
    
    def reset(self):
        """Reset HUD for new game"""
        self.score = 0
        self.lives = 3
        self.combo = 0
        self.game_mode = "Playing"
