"""
Fruit Ninja - Hand Tracking Game
Entry Point for Stages 1-4 - Complete with Game Mechanics
Camera feed, fruit physics, hand gesture detection, and game rules
"""

import sys
import os
import time
import cv2
from collections import deque
from game.game_engine import GameEngine
from vision.hand_tracker_new import HandTracker
from ui.hud import HUD
from game.fruit_spawner import FruitSpawner
from game.gesture_detector import GestureDetector
from game.game_manager import GameManager
from config import (
    DISPLAY_NAME, FPS, LANDMARK_COLOR, LANDMARK_RADIUS,
    CONNECTION_COLOR, CONNECTION_THICKNESS, GESTURE_HAND_RADIUS
)


def main():
    """Main game loop for Stage 1"""
    
    print("=" * 60)
    print("Fruit Ninja - Hand Tracking Game")
    print("=" * 60)
    print("\nStage 1-4: Complete Game with Mechanics")
    print("- Camera feed display")
    print("- Hand detection and gesture tracking")
    print("- Fruit spawning with gravity physics")
    print("- Bomb obstacles")
    print("- Hand gesture detection (slicing)")
    print("- Fruit collision and slicing")
    print("- Lives system & game over")
    print("- Score & combo multiplier")
    print("- FPS counter")
    print("\nControls:")
    print("  Q or ESC: Quit")
    print("=" * 60)
    print("\nInitializing...\n")
    
    # Initialize components first
    engine = None
    hand_tracker = None
    hud = None
    spawner = None
    gesture_detector = None
    game_manager = None
    
    try:
        # Initialize components
        print("Initializing Game Engine...")
        sys.stdout.flush()
        engine = GameEngine()
        print("[OK] Game engine initialized")
        sys.stdout.flush()
        
        print("Initializing Hand Tracker...")
        sys.stdout.flush()
        hand_tracker = HandTracker()
        print("[OK] Hand tracker initialized")
        sys.stdout.flush()
        
        print("Initializing HUD...")
        sys.stdout.flush()
        hud = HUD()
        print("[OK] HUD initialized")
        sys.stdout.flush()
        
        print("Initializing Fruit Spawner...")
        sys.stdout.flush()
        spawner = FruitSpawner()
        print("[OK] Fruit spawner initialized")
        sys.stdout.flush()
        
        print("Initializing Gesture Detector...")
        sys.stdout.flush()
        gesture_detector = GestureDetector()
        print("[OK] Gesture detector initialized")
        sys.stdout.flush()
        
        print("Initializing Game Manager...")
        sys.stdout.flush()
        game_manager = GameManager()
        game_manager.set_state(GameManager.STATE_PLAYING)
        print("[OK] Game manager initialized")
        sys.stdout.flush()
        
        print(f"\n[OK] Starting game loop at {FPS} FPS...")
        print("-" * 60)
        sys.stdout.flush()
        
        frame_count = 0
        max_frames = int(os.environ.get('MAX_FRAMES', '0'))  # 0 = infinite, or set limit for testing
        
        visual_trails = {}  # {hand_idx: deque(maxlen=15)}
        
        while True:
            # 1. Get camera frame
            frame = engine.get_camera_frame()
            if frame is None:
                print("Error: Could not read from camera")
                break
            
            if frame_count == 0:
                print(f"[OK] Camera frame captured: {frame.shape}")
                sys.stdout.flush()
            
            # 2. Detect hands and track landmarks
            frame, hands_data = hand_tracker.process_frame(frame)
            
            if frame_count == 0:
                print(f"[OK] Hand detection working (found {len(hands_data)} hands)")
                sys.stdout.flush()
            
            # Update visual trails
            current_hand_indices = []
            for idx, hand_data in enumerate(hands_data):
                if hand_data is not None and not hand_data.get('sliced', False):
                    landmarks = hand_data.get('landmarks', [])
                    if len(landmarks) > 8:
                        idx_finger = landmarks[8]
                        if idx not in visual_trails:
                            visual_trails[idx] = deque(maxlen=15)
                        visual_trails[idx].append(idx_finger)
                        current_hand_indices.append(idx)
            
            # Clean up old trails
            visual_trails = {k: v for k, v in visual_trails.items() if k in current_hand_indices}
            
            # Draw visual trails (meteor effect)
            for idx, trail in visual_trails.items():
                if len(trail) > 1:
                    points = [(int(p[0]), int(p[1])) for p in trail]
                    for i in range(len(points) - 1):
                        factor = i / len(points)
                        thickness = max(1, int(15 * factor))
                        b = 0
                        g = int(255 * factor)
                        r = 255
                        color = (b, g, r)
                        cv2.line(frame, points[i], points[i+1], color, thickness)
                        core_thickness = max(1, int(5 * factor))
                        cv2.line(frame, points[i], points[i+1], (255, 255, 255), core_thickness)
            
            # 3. Draw hand landmarks
            frame = hand_tracker.draw_landmarks(
                frame, hands_data,
                landmark_color=LANDMARK_COLOR,
                landmark_radius=LANDMARK_RADIUS,
                connection_color=CONNECTION_COLOR,
                connection_thickness=CONNECTION_THICKNESS
            )
            
            current_state = game_manager.get_state()
            

            
            if current_state == GameManager.STATE_MENU:
                # Menu HUD
                hud.set_game_mode("Show 'OK' Gesture to Start")
                hud.set_score(0)
                hud.set_lives(3)
                hud.set_combo(0)
                hud.set_fruits_sliced(0)
                fruit_count = 0
                bomb_count = 0
                
            elif current_state == GameManager.STATE_PLAYING:
                # 4. Update and draw fruits with physics
                spawner.update(engine.delta_time)
                frame = spawner.draw(frame)
                fruit_count = spawner.get_active_fruits_count()
                bomb_count = spawner.get_bomb_count()
                
                # Update game manager
                game_manager.update(engine.delta_time)
                
                # 5. Check for missed fruits (penalty)
                for fruit in spawner.get_fruits():
                    if not fruit.sliced and fruit.is_off_screen():
                        if not game_manager.miss_fruit():
                            break
                
                # 6. Detect hand gestures and check collisions
                slices = gesture_detector.update(hands_data, engine.delta_time)
                for slice_data in slices:
                    hand_pos = slice_data['position']
                    old_hand_pos = slice_data.get('old_position', hand_pos)
                    
                    # Check collision with fruits using line intersection
                    nearby_fruits = spawner.get_fruit_intersecting_line(
                        old_hand_pos, hand_pos,
                        radius_padding=GESTURE_HAND_RADIUS
                    )
                    for fruit in nearby_fruits:
                        spawner.slice_fruit(fruit)
                        game_manager.slice_fruit()  # Award points and combo
                    
                    # Check collision with bombs using line intersection
                    nearby_bombs = spawner.get_bomb_intersecting_line(
                        old_hand_pos, hand_pos,
                        radius_padding=GESTURE_HAND_RADIUS
                    )
                    for bomb in nearby_bombs:
                        spawner.hit_bomb(bomb)
                        if not game_manager.hit_bomb():
                            break
                
                # 7. Update HUD with game state
                hud.set_score(game_manager.get_score())
                hud.set_lives(game_manager.get_lives())
                hud.set_combo(game_manager.get_combo())
                hud.set_fruits_sliced(game_manager.fruits_sliced)
                
                if game_manager.is_game_over():
                    hud.set_game_mode(f"GAME OVER - Final Score: {game_manager.get_score()}")
                else:
                    hud.set_game_mode(f"Stage 1-4: {fruit_count}F {bomb_count}B")
            
            elif current_state == GameManager.STATE_PAUSED:
                frame = spawner.draw(frame)
                hud.set_game_mode("PAUSED")
            
            frame = hud.draw(frame)
            
            # 7. Draw FPS counter
            frame = engine.draw_fps(frame)
            
            # 8. Display frame
            engine.display_frame(frame, DISPLAY_NAME)
            
            # 9. Update timing
            engine.update_timing()
            frame_count += 1
            
            if frame_count % 30 == 0:  # Print every 30 frames
                print(f"  Frame {frame_count}, FPS: {engine.current_fps}, Score: {game_manager.get_score()}, Lives: {game_manager.get_lives()}, Combo: {game_manager.get_combo()}x")
                sys.stdout.flush()
            
            # 10. Maintain FPS
            engine.maintain_fps()
            
            # 11. Handle input
            if not engine.handle_input():
                break
            
            # 12. Check game over condition
            if game_manager.is_game_over():
                print(f"\n[OK] GAME OVER!")
                print(f"  Final Score: {game_manager.get_score()}")
                print(f"  Fruits Sliced: {game_manager.fruits_sliced}")
                print(f"  Bombs Hit: {game_manager.bombs_hit}")
                print(f"  Reason: {game_manager.get_game_over_reason()}")
                break
            
            # 13. Test mode limit
            if max_frames > 0 and frame_count >= max_frames:
                print(f"Reached max frames limit ({max_frames}), exiting...")
                break
        
        print("-" * 60)
        print(f"\nTotal frames processed: {frame_count}")
        print("Average FPS: {:.1f}".format(frame_count / engine.clock_time) if engine.clock_time > 0 else "N/A")
        print("\n[OK] Game closed successfully")
        
    except Exception as e:
        print(f"\n[ERROR] Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        # Cleanup
        if hand_tracker:
            hand_tracker.close()
        if engine:
            engine.close()
        if game_manager:
            stats = game_manager.get_stats()
            print("\n" + "=" * 60)
            print("Game Statistics:")
            print(f"Final Score: {stats['score']}")
            print(f"Fruits Sliced: {stats['fruits_sliced']}")
            print(f"Bombs Hit: {stats['bombs_hit']}")
            print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
