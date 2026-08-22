"""Fruit physics, rendering, and lifecycle for the Fruit Ninja game."""

import platform

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from config import FRUIT_COLORS, FRUIT_RADIUS, GRAVITY, SCREEN_HEIGHT, SCREEN_WIDTH


class EmojiRenderer:
    def __init__(self):
        self.cache = {}
        self.fonts = {}
        self.font_path = (
            "seguiemj.ttf"
            if platform.system() == "Windows"
            else "Apple Color Emoji.ttc"
        )

    def _get_font(self, size):
        if size in self.fonts:
            return self.fonts[size]

        try:
            font = ImageFont.truetype(self.font_path, size)
        except OSError:
            try:
                font = ImageFont.truetype("NotoColorEmoji.ttf", size)
            except OSError:
                font = ImageFont.load_default()

        self.fonts[size] = font
        return font

    def get_emoji_image(self, emoji_char, size=60):
        key = (emoji_char, size)
        if key in self.cache:
            return self.cache[key]

        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        font = self._get_font(size)
        center = (size // 2, size // 2)

        if font != ImageFont.load_default():
            draw.text(
                center,
                emoji_char,
                font=font,
                fill=(255, 255, 255, 255),
                anchor="mm",
                embedded_color=True,
            )
        else:
            draw.text(
                center,
                emoji_char,
                fill=(255, 255, 255, 255),
                anchor="mm",
            )

        emoji_array = np.array(image)
        if emoji_array.shape[2] == 4:
            red, green, blue, alpha = cv2.split(emoji_array)
            emoji_array = cv2.merge((blue, green, red, alpha))

        self.cache[key] = emoji_array
        return emoji_array


emoji_renderer = EmojiRenderer()


class Fruit:
    """Represent one fruit and its physics/rendering state."""

    TYPES = [
        "apple",
        "orange",
        "watermelon",
        "banana",
        "peach",
        "grape",
        "strawberry",
        "lemon",
        "mango",
        "pineapple",
    ]
    FRUIT_EMOJIS = {
        "apple": "🍎",
        "orange": "🍊",
        "watermelon": "🍉",
        "banana": "🍌",
        "peach": "🍑",
        "grape": "🍇",
        "strawberry": "🍓",
        "lemon": "🍋",
        "mango": "🥭",
        "pineapple": "🍍",
    }

    def __init__(self, x, y, vx, vy, fruit_type="apple", radius=FRUIT_RADIUS):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.fruit_type = fruit_type
        self.radius = radius
        self.sliced = False
        self.creation_time = 0.0

    def update(self, delta_time):
        if self.sliced:
            return

        self.vy += GRAVITY * delta_time
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time

    def draw(self, frame):
        if self.sliced:
            return frame

        pos = (int(self.x), int(self.y))
        emoji = self.FRUIT_EMOJIS.get(self.fruit_type, "🍎")
        color = FRUIT_COLORS.get(self.fruit_type, (0, 255, 0))
        cv2.circle(frame, pos, self.radius + 5, color, 1)

        size = int(self.radius * 2.5)
        emoji_img = emoji_renderer.get_emoji_image(emoji, size=size)
        height, width = emoji_img.shape[:2]
        x_min = int(pos[0] - width / 2)
        y_min = int(pos[1] - height / 2)
        x_max = x_min + width
        y_max = y_min + height

        if (
            x_min >= 0
            and y_min >= 0
            and x_max < frame.shape[1]
            and y_max < frame.shape[0]
        ):
            alpha = emoji_img[:, :, 3] / 255.0
            for channel in range(3):
                frame[y_min:y_max, x_min:x_max, channel] = (
                    alpha * emoji_img[:, :, channel]
                    + (1 - alpha) * frame[y_min:y_max, x_min:x_max, channel]
                )

        return frame

    def is_off_screen(self):
        if self.y > SCREEN_HEIGHT + self.radius and self.vy > 0:
            return True
        if self.x < -self.radius or self.x > SCREEN_WIDTH + self.radius:
            return True
        return False

    def slice(self):
        self.sliced = True

    def get_position(self):
        return (self.x, self.y)

    def get_bounds(self):
        return (
            self.x - self.radius,
            self.y - self.radius,
            self.x + self.radius,
            self.y + self.radius,
        )

    def is_point_inside(self, px, py):
        distance = np.sqrt((px - self.x) ** 2 + (py - self.y) ** 2)
        return distance <= self.radius

    def __repr__(self):
        sliced_str = " (sliced)" if self.sliced else ""
        return (
            f"Fruit({self.fruit_type} at ({self.x:.0f},{self.y:.0f}), "
            f"v=({self.vx:.0f},{self.vy:.0f}){sliced_str})"
        )
