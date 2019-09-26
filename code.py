import time

import board
from CatUtils import calculate_time_remaining, feed_the_cats, get_next_feeding_cycle
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label
from adafruit_pyportal import PyPortal
from cat_constants import FEEDING_THRESHOLD, FEED_TIME


FOOD_LOCATION = "America/New_York"
print("Meals Loaded: {0}".format(FEED_TIME))

TEXT_COLOR = 0xFFFFFF
EMPHASIS_COLOR = 0x4DFF00
BACKGROUND_COLOR = 0x000000
TEXT_FIELDS = {
    "top": (25, 50, "Time To", TEXT_COLOR),
    "middle": (60, 125, "Noms", TEXT_COLOR),
    "bottom": (65, 200, "69:69", EMPHASIS_COLOR),
}

# Initialize display
board.DISPLAY.auto_brightness = False
pyportal = PyPortal(status_neopixel=board.NEOPIXEL, default_bg=BACKGROUND_COLOR)
pyportal.set_backlight(0.4)
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
    if not refresh_time or (time.monotonic() - refresh_time) > 3600:
        try:
            pyportal.get_local_time(location=FOOD_LOCATION)
            refresh_time = time.monotonic()
        except RuntimeError as e:
            print("Error fetching local time, retrying! -", e)
            continue

    current_time = time.localtime()
    target_time, meal_str = get_next_feeding_cycle(current_time)
    total_sec_remaining, hours_remaining, mins_remaining = calculate_time_remaining(
        current_time, target_time
    )
    print("Local time: {0:>02}{1:>02}".format(current_time[3], current_time[4]), end=", ")
    print(
        "Next meal: {0} @ {1:>02}{2:>02} ({3}s)".format(
            meal_str[0], target_time[3], target_time[4], total_sec_remaining
        )
    )

    if total_sec_remaining < FEEDING_THRESHOLD:
        # Activate feeding screen & turn food container
        pyportal.set_background(0xFF0000)
        text_areas["middle"].text = "NomNom"
        text_areas["middle"].x = 0
        text_areas["bottom"].text = ""
        feed_the_cats()
        time.sleep(FEEDING_THRESHOLD * 2)  # Add extra sleep to wait out our time buffer
        pyportal.set_background(BACKGROUND_COLOR)
        continue
    else:
        # Update target meal & x location if it has changed
        if text_areas["middle"].text != meal_str[0]:
            text_areas["middle"].text = meal_str[0]
            text_areas["middle"].x = meal_str[1]

        # Update clock
        text_areas["bottom"].text = "{0:>02}:{1:>02}".format(hours_remaining, mins_remaining)

    # Update every 30 seconds
    time.sleep(30)
