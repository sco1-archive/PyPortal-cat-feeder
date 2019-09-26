import time

import board
from CatUtils import calculate_time_remaining, get_next_feeding_cycle
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label
from adafruit_pyportal import PyPortal
from cat_constants import FEEDING_THRESHOLD


FOOD_LOCATION = "America/New_York"

TEXT_COLOR = 0xFFFFFF
EMPHASIS_COLOR = 0x4DFF00
BACKGROUND_COLOR = 0x000000
TEXT_FIELDS = {
    "top": (25, 50, "Time To", TEXT_COLOR),
    "middle": (60, 125, "Noms", TEXT_COLOR),
    "bottom": (65, 200, "69:69", EMPHASIS_COLOR),
}


# Initialize display
board.DISPLAY.auto_brightness = True
pyportal = PyPortal(status_neopixel=board.NEOPIXEL, default_bg=BACKGROUND_COLOR)
big_font = bitmap_font.load_font("./fonts/Nunito-Light-75.bdf")
big_font.load_glyphs(b"0123456789adefikmnorstxBDT: ")  # pre-load glyphs for fast printing

text_areas = {}
for row_name, spec in TEXT_FIELDS.items():
    textarea = Label(big_font, text=spec[2], max_glyphs=9)
    textarea.x = spec[0]
    textarea.y = spec[1]
    textarea.color = spec[3]
    pyportal.splash.append(textarea)
    text_areas[row_name] = textarea

# Core event loop
refresh_time = None
while True:
    # Sync device time with the internet once per hour (or at startup)
    if (not refresh_time) or (time.monotonic() - refresh_time) > 3600:
        try:
            print("Getting time from internet!")
            pyportal.get_local_time(location=FOOD_LOCATION)
            refresh_time = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)
            continue

    current_time = time.localtime()
    print("Current time in", FOOD_LOCATION, ":", current_time)
    target_time, meal_str = get_next_feeding_cycle(current_time)

    total_sec_remaining, hours_remaining, mins_remaining = calculate_time_remaining(
        current_time, target_time
    )
    if total_sec_remaining < FEEDING_THRESHOLD:
        # Activate feeding screen & turn food container
        print("ACTIVATE FOOD!")
        pyportal.set_background(0xFF0000)
        time.sleep(30)  # Simulate food time
        pyportal.set_background(BACKGROUND_COLOR)
    else:
        # Update target meal & x location if it has changed
        if text_areas["middle"].text != meal_str[0]:
            text_areas["middle"].text = meal_str[0]
            text_areas["middle"].x = meal_str[1]

        # Update clock
        text_areas["bottom"].text = "{:>02}:{:>02}".format(hours_remaining, mins_remaining)

    # Update every 30 seconds
    time.sleep(30)
