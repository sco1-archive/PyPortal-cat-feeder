import time

import board
from adafruit_pyportal import PyPortal
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label


TEXT_COLOR = 0xFFFFFF
EMPHASIS_COLOR = 0x4DFF00
BACKGROUND_COLOR = 0x000000

FOOD_LOCATION = "America/New_York"
FEED_TIME = {
    "morning": (4, 30),
    "evening": (16, 30),
}
FEEDING_THRESHOLD = 300  # Threshold for seconds remaining in order to activate the food spinner

def time_builder(in_time, hour, minute):
    """Build a time.struct_time for the specified hour & minute on the current day."""
    tmp = list(in_time)
    tmp[3] = hour
    tmp[4] = minute
    return time.struct_time(tuple(tmp))

pyportal = PyPortal(status_neopixel=board.NEOPIXEL,
                    default_bg=BACKGROUND_COLOR)
big_font = bitmap_font.load_font("./fonts/Nunito-Light-75.bdf")
big_font.load_glyphs(b'0123456789:') # pre-load glyphs for fast printing

text_labels = [
    (25, 50, "Time To", TEXT_COLOR),      # Top row
    (0, 125, "Breakfast", TEXT_COLOR),    # Middle row
    (65, 200, "xx:xx", EMPHASIS_COLOR),   # Time placeholder
]

text_areas = []
for spec in text_labels:
    textarea = Label(big_font, text=spec[2])
    textarea.x = spec[0]
    textarea.y = spec[1]
    textarea.color = spec[3]
    pyportal.splash.append(textarea)
    text_areas.append(textarea)

refresh_time = None
while True:
    # only query the online time once per hour (and on first run)
    if (not refresh_time) or (time.monotonic() - refresh_time) > 3600:
        try:
            print("Getting time from internet!")
            pyportal.get_local_time(location=FOOD_LOCATION)
            refresh_time = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)
            continue

    current_time = time.localtime()
    morning_feeding = time_builder(current_time, FEED_TIME["morning"][0], FEED_TIME["morning"][1])
    evening_feeding = time_builder(current_time, FEED_TIME["evening"][0], FEED_TIME["evening"][1])
    print("Current time in", FOOD_LOCATION, ":", current_time)

    # Check to see if we're counting down to morning or evening
    current_hour = current_time[3]
    if current_hour > evening_feeding[3] or current_hour <= morning_feeding[3]:
        # Counting down to morning
        target_time = morning_feeding
    else:
        # Counting down to evening
        target_time = evening_feeding

    # Calculate hour and minute deltas
    mins_remaining = target_time[4] - current_time[4]
    if mins_remaining < 0:
        mins_remaining += 60
    # Add minutes to go forward
    current_time = time.localtime(time.mktime(current_time) + mins_remaining * 60)

    hours_remaining = target_time[3] - current_time[3]
    if hours_remaining < 0:
        hours_remaining += 24
    # Add hours to go forward
    the_time = time.localtime(time.mktime(current_time) + hours_remaining * 60 * 60)

    total_sec_remaining = hours_remaining * 60 * 60
    total_sec_remaining += mins_remaining * 60

    print("Remaining: %d hours, %d minutes" % (hours_remaining, mins_remaining))

    if total_sec_remaining < FEEDING_THRESHOLD:
        print("ACTIVATE FOOD!")
        pyportal.set_background(0xFF0000)
    else:
        pyportal.set_background(BACKGROUND_COLOR)
        text_areas[2].text = '{:>02}:{:>02}'.format(hours_remaining, mins_remaining)

    # Update every 30 seconds
    time.sleep(30)
