"""Game state, scoring, lives, combo, bombs, and game-over logic."""

from config import INITIAL_LIVES, PENALTY_BOMB, POINTS_PER_COMBO, POINTS_PER_FRUIT


class GameManager:
    """Manage the core Fruit Ninja game state."""

    STATE_PLAYING = "playing"
    STATE_PAUSED = "paused"
    STATE_GAME_OVER = "game_over"
    STATE_MENU = "menu"

    def __init__(self):
        self.reset()

    def reset(self):
        self.score = 0
        self.lives = INITIAL_LIVES
        self.combo = 0
        self.combo_timer = 0.0
        self.combo_timeout = 2.0
        self.bombs_hit = 0
        self.fruits_sliced = 0
        self.game_over = False
        self.game_over_reason = None
        self.state = self.STATE_PLAYING

    def update(self, delta_time):
        if self.game_over or self.state != self.STATE_PLAYING:
            return

        if self.combo > 0:
            self.combo_timer += delta_time
            if self.combo_timer >= self.combo_timeout:
                self._reset_combo()

    def slice_fruit(self, points=POINTS_PER_FRUIT):
        if self.game_over:
            return

        self.combo += 1
        self.combo_timer = 0.0
        total_points = points + (self.combo - 1) * POINTS_PER_COMBO
        self.score += total_points
        self.fruits_sliced += 1

    def hit_bomb(self):
        if self.game_over:
            return False

        self._reset_combo()
        self.score += PENALTY_BOMB
        self.bombs_hit += 1
        self.lives -= 1

        if self.lives <= 0:
            self.game_over = True
            self.game_over_reason = "NO_LIVES"
            return False

        return True

    def miss_fruit(self):
        if self.game_over:
            return False

        self._reset_combo()
        self.lives -= 1

        if self.lives <= 0:
            self.game_over = True
            self.game_over_reason = "OUT_OF_LIVES"
            return False

        return True

    def get_score(self):
        return self.score

    def get_lives(self):
        return self.lives

    def get_combo(self):
        return self.combo

    def is_game_over(self):
        return self.game_over

    def get_game_over_reason(self):
        return self.game_over_reason

    def get_stats(self):
        return {
            "score": self.score,
            "lives": self.lives,
            "combo": self.combo,
            "bombs_hit": self.bombs_hit,
            "fruits_sliced": self.fruits_sliced,
            "game_over": self.game_over,
            "reason": self.game_over_reason,
        }

    def _reset_combo(self):
        self.combo = 0
        self.combo_timer = 0.0

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def __repr__(self):
        return (
            f"GameManager(Score:{self.score}, Lives:{self.lives}, "
            f"Combo:{self.combo}x, GameOver:{self.game_over})"
        )
