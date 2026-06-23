"""
Hand Tracking Module
Wrapper for MediaPipe hand detection and landmark tracking
"""

import cv2
import mediapipe as mp
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions, RunningMode
from mediapipe.tasks.python import vision
from typing import List, Tuple, Optional
import numpy as np
from config import (
    HAND_DETECTION_CONFIDENCE,
    HAND_TRACKING_CONFIDENCE,
    MAX_HANDS
)
import os


class HandTracker:
    """Manages hand detection and landmark tracking using MediaPipe"""
    
    def __init__(self):
        """Initialize MediaPipe hand detector"""
        self.frame_count = 0
        self.landmarker = None
        
        # Try to use local model first
        model_path = 'hand_landmarker.task'
        try:
            if not os.path.exists(model_path):
                # Try fallback
                import mediapipe
                mediapipe_path = os.path.dirname(mediapipe.__file__)
                model_path = os.path.join(mediapipe_path, 'tasks', 'hand_landmarker.task')
            
            print(f"Looking for model at: {model_path}")
            print(f"Model exists: {os.path.exists(model_path)}")
            
            if os.path.exists(model_path):
                base_options = mp.tasks.BaseOptions(model_asset_path=model_path)
                options = HandLandmarkerOptions(
                    base_options=base_options,
                    running_mode=RunningMode.VIDEO,
                    num_hands=MAX_HANDS,
                    min_hand_detection_confidence=HAND_DETECTION_CONFIDENCE,
                    min_hand_presence_confidence=HAND_TRACKING_CONFIDENCE,
                    min_tracking_confidence=HAND_TRACKING_CONFIDENCE
                )
                self.landmarker = HandLandmarker.create_from_options(options)
                print("[OK] HandLandmarker initialized successfully")
            else:
                print("[WARNING] Model file not found, hand detection will be disabled")
        except Exception as e:
            print(f"[ERROR] Failed to initialize HandLandmarker: {e}")
    
    def process_frame(self, frame: np.ndarray, timestamp_ms: int = None) -> Tuple[np.ndarray, List[dict]]:
        """
        Process a frame and extract hand landmarks
        
        Args:
            frame: Input frame from webcam (BGR format)
            timestamp_ms: Timestamp in milliseconds (uses frame count if not provided)
            
        Returns:
            Tuple of (frame, hands_data) where hands_data is list of hand info dicts
        """
        hands_data = []
        
        if self.landmarker is None:
            self.frame_count += 1
            return frame, hands_data
        
        try:
            if timestamp_ms is None:
                timestamp_ms = self.frame_count
            
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Create MediaPipe image
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # Detect landmarks
            results = self.landmarker.detect_for_video(mp_image, timestamp_ms)
            
            if results.hand_landmarks:
                for hand_idx, hand_landmarks in enumerate(results.hand_landmarks):
                    handedness_list = results.handedness[hand_idx] if results.handedness else None
                    handedness = handedness_list[0] if handedness_list and len(handedness_list) > 0 else None
                    
                    hand_info = {
                        'landmarks': self._extract_landmarks(hand_landmarks, frame),
                        'handedness': handedness.category_name if handedness else "Unknown",
                        'confidence': handedness.score if handedness else 0.0
                    }
                    hands_data.append(hand_info)
            
            self.frame_count += 1
        except Exception as e:
            print(f"Error processing frame: {e}")
            self.frame_count += 1
        
        return frame, hands_data
    
    def _extract_landmarks(self, hand_landmarks, frame: np.ndarray) -> List[Tuple[int, int]]:
        """
        Extract landmark coordinates from MediaPipe output
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            frame: Frame to get dimensions
            
        Returns:
            List of (x, y) tuples for each landmark
        """
        h, w, _ = frame.shape
        landmarks = []
        
        for landmark in hand_landmarks:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            landmarks.append((x, y))
        
        return landmarks
    
    def draw_landmarks(self, frame: np.ndarray, hands_data: List[dict], 
                       landmark_color: Tuple[int, int, int] = (0, 255, 0),
                       landmark_radius: int = 5,
                       connection_color: Tuple[int, int, int] = (0, 255, 255),
                       connection_thickness: int = 2) -> np.ndarray:
        """
        Draw hand landmarks and connections on frame
        
        Args:
            frame: Input frame
            hands_data: List of hand info dictionaries
            landmark_color: RGB color for landmarks
            landmark_radius: Radius of landmark circles
            connection_color: RGB color for connections
            connection_thickness: Thickness of connection lines
            
        Returns:
            Frame with drawn landmarks
        """
        # Hand landmark connections (from MediaPipe documentation)
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),  # Index finger
            (0, 9), (9, 10), (10, 11), (11, 12),  # Middle finger
            (0, 13), (13, 14), (14, 15), (15, 16),  # Ring finger
            (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
            (5, 9), (9, 13), (13, 17)  # Palm connections
        ]
        
        for hand_info in hands_data:
            landmarks = hand_info['landmarks']
            
            # Draw connections
            for start, end in connections:
                if start < len(landmarks) and end < len(landmarks):
                    x1, y1 = landmarks[start]
                    x2, y2 = landmarks[end]
                    cv2.line(frame, (x1, y1), (x2, y2), connection_color, connection_thickness)
            
            # Draw landmarks (circles)
            for x, y in landmarks:
                cv2.circle(frame, (x, y), landmark_radius, landmark_color, -1)
        
        return frame
    
    def get_index_finger_tip(self, hand_info: dict) -> Optional[Tuple[int, int]]:
        """
        Get the index finger tip position (landmark 8)
        Used for gesture detection
        
        Args:
            hand_info: Hand info dictionary
            
        Returns:
            (x, y) tuple or None if not found
        """
        landmarks = hand_info['landmarks']
        if len(landmarks) > 8:
            return landmarks[8]
        return None
        

    def close(self):
        """Release resources"""
        if self.landmarker:
            self.landmarker.close()
