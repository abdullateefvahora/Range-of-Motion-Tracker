# Timer logic
def process_hold_timer(flexion, target_flexion, target_hold_secs, hold_start_time):
    import utime

    holding = False
    target_reached = False
    hold_elapsed = 0

    if flexion >= target_flexion:
        if hold_start_time is None:
            hold_start_time = utime.ticks_ms()
        else:
            hold_elapsed = utime.ticks_diff(utime.ticks_ms(), hold_start_time) / 1000
            if hold_elapsed >= target_hold_secs:
                target_reached = True
            else:
                holding = True
    else:
        hold_start_time = None

    return holding, target_reached, hold_elapsed, hold_start_time
