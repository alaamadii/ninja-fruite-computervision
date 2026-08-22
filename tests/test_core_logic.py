import unittest

from config import INITIAL_LIVES, PENALTY_BOMB, POINTS_PER_COMBO, POINTS_PER_FRUIT
from game.fruit import Fruit
from game.game_manager import GameManager
from game.gesture_detector import GestureDetector


class GameManagerTests(unittest.TestCase):
    def test_initial_state(self):
        manager = GameManager()
        self.assertEqual(manager.get_score(), 0)
        self.assertEqual(manager.get_lives(), INITIAL_LIVES)
        self.assertEqual(manager.get_combo(), 0)
        self.assertFalse(manager.is_game_over())

    def test_combo_scoring(self):
        manager = GameManager()
        manager.slice_fruit()
        manager.slice_fruit()

        expected = POINTS_PER_FRUIT + (POINTS_PER_FRUIT + POINTS_PER_COMBO)
        self.assertEqual(manager.get_score(), expected)
        self.assertEqual(manager.get_combo(), 2)
        self.assertEqual(manager.fruits_sliced, 2)

    def test_combo_expires(self):
        manager = GameManager()
        manager.slice_fruit()
        manager.update(manager.combo_timeout)
        self.assertEqual(manager.get_combo(), 0)

    def test_bombs_consume_lives_and_end_game(self):
        manager = GameManager()
        for _ in range(INITIAL_LIVES):
            manager.hit_bomb()

        self.assertTrue(manager.is_game_over())
        self.assertEqual(manager.get_lives(), 0)
        self.assertEqual(manager.get_score(), PENALTY_BOMB * INITIAL_LIVES)


class GestureDetectorTests(unittest.TestCase):
    @staticmethod
    def _hand_at(x, y):
        landmarks = [(0, 0)] * 21
        landmarks[8] = (x, y)
        return {"landmarks": landmarks}

    def test_fast_motion_triggers_slice(self):
        detector = GestureDetector(history_size=5, velocity_threshold=100)
        self.assertEqual(detector.update([self._hand_at(0, 0)], 0.1), [])
        slices = detector.update([self._hand_at(20, 0)], 0.1)

        self.assertEqual(len(slices), 1)
        self.assertGreaterEqual(slices[0]["velocity"], 100)
        self.assertEqual(slices[0]["position"], (20, 0))

    def test_slow_motion_does_not_trigger_slice(self):
        detector = GestureDetector(history_size=5, velocity_threshold=500)
        detector.update([self._hand_at(0, 0)], 0.1)
        slices = detector.update([self._hand_at(10, 0)], 0.1)
        self.assertEqual(slices, [])

    def test_missing_hand_history_is_removed(self):
        detector = GestureDetector()
        detector.update([self._hand_at(0, 0)], 0.1)
        self.assertIn(0, detector.hand_histories)
        detector.update([], 0.1)
        self.assertNotIn(0, detector.hand_histories)


class FruitPhysicsTests(unittest.TestCase):
    def test_position_and_gravity_update(self):
        fruit = Fruit(x=100, y=100, vx=20, vy=-100, fruit_type="apple")
        fruit.update(0.5)

        self.assertAlmostEqual(fruit.x, 110.0)
        self.assertGreater(fruit.vy, -100.0)

    def test_sliced_fruit_stops_updating(self):
        fruit = Fruit(x=100, y=100, vx=20, vy=-100)
        fruit.slice()
        before = fruit.get_position()
        fruit.update(1.0)
        self.assertEqual(fruit.get_position(), before)

    def test_point_inside_uses_circular_collision(self):
        fruit = Fruit(x=100, y=100, vx=0, vy=0, radius=40)
        self.assertTrue(fruit.is_point_inside(100, 100))
        self.assertFalse(fruit.is_point_inside(150, 100))


if __name__ == "__main__":
    unittest.main()
