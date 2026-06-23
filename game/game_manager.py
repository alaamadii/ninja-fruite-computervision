"""
Game Manager for Fruit Ninja
Handles game state, lives, scoring, bombs, and game over logic
"""

from config import (
    INITIAL_LIVES, POINTS_PER_FRUIT, POINTS_PER_COMBO,
    PENALTY_BOMB
)


class GameManager:
    """
    Manages game state including lives, scoring, combo, and game over
    
    Attributes:
        score: Current game score
        lives: Remaining lives
        combo: Current combo multiplier
        combo_timer: Time since last fruit sliced
        bombs_hit: Number of bombs hit
        fruits_sliced: Total fruits sliced
        game_over: Whether game is over
        game_over_reason: Why game ended
    """
    
    # Game states
    STATE_PLAYING = "playing"
    STATE_PAUSED = "paused"
    STATE_GAME_OVER = "game_over"
    STATE_MENU = "menu"
    
    def __init__(self):
        """Initialize game manager"""
        self.reset()
    
    def reset(self):
        """Reset game to initial state"""
        self.score = 0
        self.lives = INITIAL_LIVES
        self.combo = 0
        self.combo_timer = 0.0
        self.combo_timeout = 2.0  # seconds before combo resets
        self.bombs_hit = 0
        self.fruits_sliced = 0
        self.game_over = False
        self.game_over_reason = None
        self.state = self.STATE_PLAYING
    
    def update(self, delta_time):
        """
        Update game state (timing, combo decay, etc.)
        
        Args:
            delta_time: Time since last frame in seconds
        """
        if self.game_over or self.state != self.STATE_PLAYING:
            return
        
        # Update combo timer
        if self.combo > 0:
            self.combo_timer += delta_time
            if self.combo_timer >= self.combo_timeout:
                self._reset_combo()
    
    def slice_fruit(self, points=POINTS_PER_FRUIT):
        """
        Award points for slicing a fruit
        
        Args:
            points: Base points for this fruit type
        """
        if self.game_over:
            return
        
        # Increase combo
        self.combo += 1
        self.combo_timer = 0.0
        
        # Calculate points with combo multiplier
        total_points = points + (self.combo - 1) * POINTS_PER_COMBO
        self.score += total_points
        self.fruits_sliced += 1
    
    def hit_bomb(self):
        """
        Penalty for hitting a bomb
        
        Returns:
            True if game continues, False if game over
        """
        if self.game_over:
            return False
        
        self.combo = 0
        self.combo_timer = 0.0
        self.score += PENALTY_BOMB  # Negative points
        self.bombs_hit += 1
        
        # Lose a life
        self.lives -= 1
        
        # Check game over
        if self.lives <= 0:
            self.game_over = True
            self.game_over_reason = "NO_LIVES"
            return False
        
        return True
    
    def miss_fruit(self):
        """
        Penalty for letting a fruit drop off screen
        
        Returns:
            True if game continues, False if game over
        """
        if self.game_over:
            return False
        
        self.combo = 0
        self.combo_timer = 0.0
        
        # Lose a life
        self.lives -= 1
        
        # Check game over
        if self.lives <= 0:
            self.game_over = True
            self.game_over_reason = "OUT_OF_LIVES"
            return False
        
        return True
    
    def get_score(self):
        """Get current score"""
        return self.score
    
    def get_lives(self):
        """Get remaining lives"""
        return self.lives
    
    def get_combo(self):
        """Get current combo multiplier"""
        return self.combo
    
    def is_game_over(self):
        """Check if game is over"""
        return self.game_over
    
    def get_game_over_reason(self):
        """Get reason game ended"""
        return self.game_over_reason
    
    def get_stats(self):
        """Get complete game statistics"""
        return {
            'score': self.score,
            'lives': self.lives,
            'combo': self.combo,
            'bombs_hit': self.bombs_hit,
            'fruits_sliced': self.fruits_sliced,
            'game_over': self.game_over,
            'reason': self.game_over_reason
        }
    
    def _reset_combo(self):
        """Reset combo counter"""
        self.combo = 0
        self.combo_timer = 0.0
    
    def set_state(self, state):
        """Set game state"""
        self.state = state
    
    def get_state(self):
        """Get current game state"""
        return self.state
    
    def __repr__(self):
        """String representation for debugging"""
        return f"GameManager(Score:{self.score}, Lives:{self.lives}, Combo:{self.combo}x, GameOver:{self.game_over})"
