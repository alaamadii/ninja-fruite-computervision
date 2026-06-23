"""
Gesture Detector for Fruit Ninja game
Detects hand slicing gestures from hand movement
"""

import numpy as np
from collections import deque
from config import SCREEN_WIDTH, SCREEN_HEIGHT


class GestureDetector:
    """
    Detects slicing gestures from hand movement
    
    Tracks hand position history and calculates velocity
    to identify rapid "slicing" motions
    """
    
    def __init__(self, history_size=5, velocity_threshold=500):
        """
        Initialize gesture detector
        
        Args:
            history_size: Number of frames to track for velocity
            velocity_threshold: Minimum velocity (pixels/second) to trigger slice
        """
        self.history_size = history_size
        self.velocity_threshold = velocity_threshold
        
        # Track position history per hand (by ID or index)
        self.hand_histories = {}  # {hand_id: deque of (x, y, timestamp)}
        self.last_timestamp = 0.0
        
    def update(self, hands_data, delta_time):
        """
        Update hand position history and detect gestures
        
        Args:
            hands_data: List of hand dicts from hand_tracker
            delta_time: Time since last frame in seconds
            
        Returns:
            List of detected slices with velocity info:
            [{
                'hand_index': int,
                'position': (x, y),
                'velocity': float (pixels/second),
                'direction': (vx, vy)
            }]
        """
        slices = []
        self.last_timestamp += delta_time
        
        # Update history for each hand
        for hand_idx, hand_data in enumerate(hands_data):
            if hand_data is None or hand_data.get('sliced', False):
                continue
            
            # Get index finger tip position (landmark 8)
            landmarks = hand_data.get('landmarks', [])
            if len(landmarks) > 8:
                landmark = landmarks[8]  # Index finger tip
                x = landmark[0]
                y = landmark[1]
                
                # Initialize history for this hand if needed
                if hand_idx not in self.hand_histories:
                    self.hand_histories[hand_idx] = deque(maxlen=self.history_size)
                
                history = self.hand_histories[hand_idx]
                history.append((x, y, self.last_timestamp))
                
                # Check for slicing gesture if we have enough history
                if len(history) >= 2:
                    slice_detected = self._check_for_slice(history, hand_idx)
                    if slice_detected:
                        slices.append(slice_detected)
        
        # Clean up histories for hands that are no longer detected
        detected_indices = set(range(len(hands_data)))
        to_remove = [h_idx for h_idx in self.hand_histories if h_idx not in detected_indices]
        for h_idx in to_remove:
            del self.hand_histories[h_idx]
        
        return slices
    
    def _check_for_slice(self, history, hand_idx):
        """
        Check if hand position history indicates a slicing motion
        
        Args:
            history: Deque of (x, y, timestamp) tuples
            hand_idx: Hand index
            
        Returns:
            Slice dict if gesture detected, None otherwise
        """
        if len(history) < 2:
            return None
        
        # Get recent positions
        oldest = history[0]
        newest = history[-1]
        
        x1, y1, t1 = oldest
        x2, y2, t2 = newest
        
        dt = t2 - t1
        if dt <= 0:
            return None
        
        # Calculate velocity
        dx = x2 - x1
        dy = y2 - y1
        velocity = np.sqrt(dx**2 + dy**2) / dt  # pixels/second
        
        if velocity >= self.velocity_threshold:
            return {
                'hand_index': hand_idx,
                'position': (x2, y2),
                'old_position': (x1, y1),
                'velocity': velocity,
                'direction': (dx / dt, dy / dt)  # pixels/second
            }
        
        return None
    
    def get_hand_position(self, hand_idx):
        """
        Get current hand position
        
        Args:
            hand_idx: Hand index
            
        Returns:
            (x, y) tuple or None if not tracked
        """
        if hand_idx in self.hand_histories and len(self.hand_histories[hand_idx]) > 0:
            x, y, _ = self.hand_histories[hand_idx][-1]
            return (x, y)
        return None
    
    def get_hand_velocity(self, hand_idx):
        """
        Get hand velocity
        
        Args:
            hand_idx: Hand index
            
        Returns:
            (vx, vy) tuple in pixels/second, or None if not enough data
        """
        history = self.hand_histories.get(hand_idx)
        if history is None or len(history) < 2:
            return None
        
        x1, y1, t1 = history[0]
        x2, y2, t2 = history[-1]
        dt = t2 - t1
        
        if dt <= 0:
            return None
        
        return ((x2 - x1) / dt, (y2 - y1) / dt)
    
    def clear(self):
        """Clear all tracking history"""
        self.hand_histories.clear()
        self.last_timestamp = 0.0
    
    def __repr__(self):
        """String representation for debugging"""
        tracked = len(self.hand_histories)
        return f"GestureDetector(tracking {tracked} hands, threshold={self.velocity_threshold}px/s)"
