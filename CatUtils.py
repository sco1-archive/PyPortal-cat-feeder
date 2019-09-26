import time

from cat_constants import FEED_TIME, TRAY_SPIN_SEC


def time_builder(in_time, meal):
    # type: (time.struct_time, str) -> time.struct_time
    """Build a time.struct_time for the specified hour & minute on the current day."""
    tmp = list(in_time)
    tmp[3] = FEED_TIME[meal][0]  # hour
    tmp[4] = FEED_TIME[meal][1]  # minute
    return time.struct_time(tuple(tmp))


def get_next_feeding_cycle(current_time):
    # type: (time.struct_time) -> Tuple[time.struct_time, Tuple[str, int]]  # noqa:F821
    """
    Determine the upcoming food cycle based on the current time.

    Returns a tuple of the `time.struct_time` for the next feeding time as well as its name
    and x-alignment (for centering the label)
    """
    # Use the current day to generate today's feeding times
    morning_feeding = time_builder(current_time, "morning")
    evening_feeding = time_builder(current_time, "evening")

    # Check to see if we're counting down to morning or evening
    if (current_time < morning_feeding) or (current_time > evening_feeding):
        # Counting down to morning
        return morning_feeding, ("Breakfast", 0)
    else:
        # Counting down to evening
        return evening_feeding, ("Dinner", 50)


def calculate_time_remaining(current_time, target_time):
    # type: (time.struct_time, time.struct_time) -> Tuple[int, int, int]  # noqa:F821
    """
    Calculate the total seconds remaining until the target time, as well as the hour/minute split.

    `current_time` and `target_time` will be instances of `time.struct_time`
    """
    # Calculate minute delta
    mins_remaining = target_time[4] - current_time[4]
    if mins_remaining < 0:
        # Faux modulo
        mins_remaining += 60

    # Regenerate the time with the minutes remaining added so we get the correct value for hours
    next_time = time.localtime(time.mktime(current_time) + mins_remaining * 60)

    # Calculate hour delta
    hours_remaining = target_time[3] - next_time[3]
    if hours_remaining < 0:
        # Faux modulo
        hours_remaining += 24

    total_sec_remaining = hours_remaining * 60 * 60
    total_sec_remaining += mins_remaining * 60
    return total_sec_remaining, hours_remaining, mins_remaining


def feed_the_cats():
    # type: (...) -> None
    """Activate the food tray."""
    print("(Mock) Actuating food spinner! Nom nom nom.")
    time.sleep(TRAY_SPIN_SEC)  # Placeholder until we can get wired up
