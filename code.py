import time
import board
import math
from adafruit_pyportal import PyPortal
from adafruit_button import Button
# from displayio import Group
import terminalio
import neopixel
import displayio
from adafruit_bitmap_font import bitmap_font


class PeriodicTask:
    """Used to run a task every so often without needing to call
    time.sleep() and waste cycles.

    Sub-classes should implement `run`. You should call `update`
    every loop.
    """
    def __init__(self, frequency):
        self.frequency = frequency
        self._last_update_time = 0

    def update(self):
        now = time.monotonic_ns()
        next_update_time = self._last_update_time + int(1.0 / self.frequency * 1000000000)
        if now > next_update_time:
            self.run()
            self._last_update_time = time.monotonic_ns()

    def run(self):
        pass


class PixelPattern(PeriodicTask):
    def __init__(self, frequency, strip):
        super().__init__(frequency)
        self.strip = strip
        self._offset = 0
        self.color = 0

    def run(self):
        # Fetch these first to avoid repeated lookups on properties.
        color = self.color
        strip = self.strip

        # Normalize the color. It can come in as an integer (like 0xFFAABB) but
        # we want a tuple.
        if isinstance(color, int):
            color = color.to_bytes(3, "big")

        multiplier_up = (math.sin((self._offset % 21 / 20) * 2 * 3.14) + 1.0) * 0.5
        multiplier_down = 1.0 - multiplier_up

        for n in range(strip.n):
            if n % 2 == 0:
                multiplier = multiplier_up
            else:
                multiplier = multiplier_down

            strip[n] = (int(color[0] * multiplier), int(color[1] * multiplier), int(color[2] * multiplier))

        strip.show()
        self._offset += 1


color_labels = {
    "red": (255, 0, 0),
    "yellow": (255, 170, 0),
    "green": (0, 255, 0),
}

def create_buttons(size=60, offset=10):
    """Create buttons based on colors and positions

    Based on code from:
        https://learn.adafruit.com/pyportal-neopixel-color-oicker
    """
    buttons = []
    x = offset
    y = offset

    for label, color in color_labels.items():
        button = Button(
            x=x, y=y,
            width=size, height=size,
            style=Button.SHADOWROUNDRECT,
            fill_color=color,
            outline_color=0x222222,
            name=label)
        buttons.append(button)
        x += 80
    return buttons

strip = neopixel.NeoPixel(
    board.D4,
    n=24,
    brightness=0.1,
    auto_write=False,  # Requires calling strip.show() to change neopixel values
)
strip.fill((0, 0, 0))

pixel_pattern = PixelPattern(
    strip=strip,
    frequency=10,  # Update 10 times per second˜˜˜
)

# Initialize the PyPortal
background_color = 0x0  # black
pyportal = PyPortal(default_bg=background_color)

buttons = create_buttons()
button_group = displayio.Group()
for button in buttons:
    button_group.append(button.group)
pyportal.splash.append(button_group)

arial_font = bitmap_font.load_font("/fonts/Arial-ItalicMT-17.bdf")
back_button = Button(
    x=10, y=200,
    width=80, height=40,
    style=Button.SHADOWROUNDRECT,
    fill_color=(0, 0, 0),
    outline_color=0x222222,
    name="back",
    label="back",
    label_font=arial_font,
    label_color=0xFFFFFF,
)

buttons.append(back_button)
back_button_group = displayio.Group()
back_button_group.append(back_button.group)
pyportal.splash.append(back_button_group)
back_button_group.hidden = True

status_backgrounds = {
    "green": "images/full.bmp",
    "yellow": "images/low.bmp",
    "red": "images/empty.bmp",
}

while True:
    touch = pyportal.touchscreen.touch_point
    if touch:
        for button in buttons:
            if button.contains(touch):
                if button.name == "back":
                    back_button_group.hidden = True
                    button_group.hidden = False
                    pyportal.set_background(background_color)
                if button.name in status_backgrounds:
                    back_button_group.hidden = False
                    button_group.hidden = True
                    pyportal.set_background(status_backgrounds[button.name])
                    pixel_pattern.color = button.fill_color
                break

    pixel_pattern.update()
