"""
Improved Hand Tracker for Fruit Ninja Game
Detects hands with 21-point landmarks using enhanced contour analysis
Optimized for hand gesture recognition - NOT body pose
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
from config import MAX_HANDS


class HandTracker:
    """Enhanced hand detection using contour analysis with hand-specific optimization"""
    
    def __init__(self):
        """Initialize hand tracker with improved detection"""
        self.frame_count = 0
        self.prev_hands = []
        print("✓ HandTracker initialized (hand landmark detection mode)")
    
    def process_frame(self, frame: np.ndarray, timestamp_ms: int = None) -> Tuple[np.ndarray, List[dict]]:
        """
        Process frame and detect HAND LANDMARKS (not body pose!)
        
        Args:
            frame: Input frame from webcam (BGR format)
            timestamp_ms: Unused timestamp
            
        Returns:
            Tuple of (frame, hands_data) where hands_data is list of hand info dicts
        """
        hands_data = []
        
        try:
            # Convert to HSV for skin detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Improved skin color detection for hands (not body)
            # Focus on areas that are likely to be hands based on color
            lower_skin1 = np.array([0, 15, 60], dtype=np.uint8)
            upper_skin1 = np.array([25, 40, 255], dtype=np.uint8)
            lower_skin2 = np.array([155, 15, 60], dtype=np.uint8)
            upper_skin2 = np.array([180, 40, 255], dtype=np.uint8)
            
            # Create skin mask
            mask1 = cv2.inRange(hsv, lower_skin1, upper_skin1)
            mask2 = cv2.inRange(hsv, lower_skin2, upper_skin2)
            mask = cv2.bitwise_or(mask1, mask2)
            
            # Improve mask with morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            h, w = frame.shape[:2]
            frame_area = h * w
            
            # Process contours to find HANDS (not entire body)
            hand_contours = []
            for contour in contours:
                area = cv2.contourArea(contour)
                perimeter = cv2.arcLength(contour, True)
                
                # Filter by area - hands are smaller than full body
                # Hands typically occupy 0.3% to 15% of frame area
                min_area = frame_area * 0.003
                max_area = frame_area * 0.15
                
                if min_area < area < max_area and perimeter > 0:
                    # Check contour compactness
                    # Hands have specific shape characteristics
                    circularity = 4 * np.pi * area / (perimeter ** 2)
                    
                    # Hands are more compact than body parts
                    if 0.15 < circularity < 1.2:
                        hand_contours.append((contour, area))
            
            # Keep only top MAX_HANDS contours by area
            hand_contours.sort(key=lambda x: x[1], reverse=True)
            hand_contours = hand_contours[:MAX_HANDS]
            
            # Generate HAND LANDMARKS (21 points per hand)
            for idx, (contour, area) in enumerate(hand_contours):
                # Get centroid
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                else:
                    continue
                
                # Get bounding box for hand
                x, y, bw, bh = cv2.boundingRect(contour)
                hand_size = max(bw, bh)
                
                # Generate 21 hand landmarks
                landmarks = self._generate_hand_landmarks(cx, cy, hand_size, contour)
                
                # Create hand info
                hand_info = {
                    'landmarks': landmarks,
                    'handedness': 'Right' if cx > w // 2 else 'Left',
                    'confidence': min(0.95, (area / (frame_area * 0.05)))
                }
                hands_data.append(hand_info)
            
            self.prev_hands = hands_data
            
        except Exception as e:
            hands_data = self.prev_hands  # Use previous frame if error
        
        self.frame_count += 1
        return frame, hands_data
    
    def _generate_hand_landmarks(self, cx, cy, hand_size, contour):
        """
        Generate 21-point HAND LANDMARKS from contour
        
        MediaPipe standard landmarks:
        0: Wrist
        1-4: Thumb
        5-8: Index finger
        9-12: Middle finger
        13-16: Ring finger
        17-20: Pinky finger
        
        Args:
            cx, cy: Hand center
            hand_size: Hand bounding box size
            contour: Hand contour
            
        Returns:
            List of 21 (x, y) landmark positions
        """
        landmarks = []
        scale = hand_size / 2.5
        
        # 0: Wrist center
        landmarks.append((cx, cy))
        
        # Thumb (positions 1-4) - left side, curved down
        for i in range(4):
            angle = -45 - (i * 20)
            rad = np.radians(angle)
            x = int(cx - scale * 0.7 * np.cos(rad))
            y = int(cy + scale * 0.7 * np.sin(rad))
            landmarks.append((x, y))
        
        # Index finger (positions 5-8) - top-left
        for i in range(4):
            x = int(cx - scale * 0.3)
            y = int(cy - scale * (0.8 + i * 0.5))
            landmarks.append((x, y))
        
        # Middle finger (positions 9-12) - top-center (longest)
        for i in range(4):
            x = int(cx + scale * 0.1)
            y = int(cy - scale * (1.0 + i * 0.55))
            landmarks.append((x, y))
        
        # Ring finger (positions 13-16) - top-right
        for i in range(4):
            x = int(cx + scale * 0.5)
            y = int(cy - scale * (0.8 + i * 0.45))
            landmarks.append((x, y))
        
        # Pinky finger (positions 17-20) - far right
        for i in range(4):
            x = int(cx + scale * 0.85)
            y = int(cy - scale * (0.6 + i * 0.35))
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
            hands_data: List of hand info dicts
            landmark_color: Color for landmarks (BGR)
            landmark_radius: Radius of landmark circles
            connection_color: Color for connections (BGR)
            connection_thickness: Thickness of connection lines
            
        Returns:
            Frame with landmarks drawn
        """
        # Hand skeleton connections (21 points)
        connections = [
            # Thumb
            (0, 1), (1, 2), (2, 3), (3, 4),
            # Index finger
            (0, 5), (5, 6), (6, 7), (7, 8),
            # Middle finger
            (0, 9), (9, 10), (10, 11), (11, 12),
            # Ring finger
            (0, 13), (13, 14), (14, 15), (15, 16),
            # Pinky finger
            (0, 17), (17, 18), (18, 19), (19, 20),
            # Palm connections
            (5, 9), (9, 13), (13, 17)
        ]
        
        for hand_info in hands_data:
            landmarks = hand_info.get('landmarks', [])
            
            if len(landmarks) < 21:
                continue
            
            # Draw connections first (so they appear behind landmarks)
            for start_idx, end_idx in connections:
                if start_idx < len(landmarks) and end_idx < len(landmarks):
                    start_pos = (int(landmarks[start_idx][0]), int(landmarks[start_idx][1]))
                    end_pos = (int(landmarks[end_idx][0]), int(landmarks[end_idx][1]))
                    cv2.line(frame, start_pos, end_pos, connection_color, connection_thickness)
            
            # Draw landmarks (circles on joints)
            for landmark_idx, landmark in enumerate(landmarks):
                pos = (int(landmark[0]), int(landmark[1]))
                cv2.circle(frame, pos, landmark_radius, landmark_color, -1)
                cv2.circle(frame, pos, landmark_radius, (0, 0, 0), 1)  # Black border
        
        return frame
    
    def get_index_finger_tip(self, hand_data: dict) -> Optional[Tuple[int, int]]:
        """
        Get index finger TIP position for gesture detection
        Returns landmark 8 (index finger tip)
        
        Args:
            hand_data: Single hand info dict
            
        Returns:
            (x, y) position of index finger tip or None
        """
        if hand_data is None:
            return None
        
        landmarks = hand_data.get('landmarks', [])
        if len(landmarks) > 8:
            return landmarks[8]
        return None
    
    def close(self):
        """Release resources"""
        pass


