import time
import board
from adafruit_pyportal import PyPortal
from adafruit_button import Button
import neopixel


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


def chase_pattern(color, offset):
    """Single color chase pattern.

    Based on code from:
        https://learn.adafruit.com/gemma-hoop-earrings/circuitpython-code
    """
    for i in range(num_pixels):
        if ((offset + i) & (num_pixels)) < 2:
            strip[i] = current_color
        else:
            strip[i] = 0
    strip.show()
    time.sleep(0.08)
    offset += 1
    if offset >= num_pixels:
        offset = 0
    return offset


# PyPortal Initialization
background_color = 0x0  # black
brightness = 0.1        # turn down the brightness
num_pixels = 5          # 5 pixel strip
auto_write = False      # call strip.show() to change neopixel values

strip = neopixel.NeoPixel(
    board.D4, num_pixels,
    brightness=brightness,
    auto_write=auto_write)
strip.fill(0)

pyportal = PyPortal(default_bg=background_color)

buttons = create_buttons()
# TODO NZ: Do we want to add the buttons to a group before
#  adding them to the pyportal splash screen
for button in buttons:
    pyportal.splash.append(button.group)

current_color = 0
current_offset = 0

while True:
    touch = pyportal.touchscreen.touch_point
    if touch:
        for button in buttons:
            if button.contains(touch):
                if button.name == "green":
                    print("Let's display the full battery image.")
                    pyportal.splash.pop(1)
                    pyportal.splash.pop(1)
                    pyportal.splash.pop(1)
                    pyportal.set_background("images/full.bmp")

                print("Touched", button.name)
                current_color = button.fill_color
                break

    current_offset = chase_pattern(color=current_color, offset=current_offset)
    time.sleep(0.05)