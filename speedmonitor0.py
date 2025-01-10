from microbit import *
from micropython import const

DARK_THRESHOLD = const(400)  # ADC range 0:1024
SCROLL_DELAY = const(90)  # ms
SENSOR_DISTANCE = const(67 / 1000)  # meters
H0_SCALE = const(87)  # 1:87

READY_SYMBOL = Image.YES
LEFT_ARROW = Image.ARROW_W
RIGHT_ARROW = Image.ARROW_E


def dark(pin):
    return pin.read_analog() <= DARK_THRESHOLD


def model_speed(dt):
    # return model meters per second
    secs = dt / 1000
    try:
        return SENSOR_DISTANCE / secs
    except ZeroDivisionError:
        return 0


def speed(dt):
    model = model_speed(dt)  # m/s
    scaled = model * H0_SCALE
    return scaled * 3.6  # km/h


def wait_until_ready():
    # wait until lasers illuminate both sensors
    display.show('?')
    while dark(pin0) or dark(pin0):
        sleep(50)


def measure():
    # time when each pin goes dark
    pin0_dark_t = 0
    pin1_dark_t = 0

    while True:

        if pin0_dark_t == 0 and dark(pin0):
            pin0_dark_t = running_time()
            if pin1_dark_t == 0:
                display.show(RIGHT_ARROW)

        if pin1_dark_t == 0 and dark(pin1):
            pin1_dark_t = running_time()
            if pin0_dark_t == 0:
                display.show(LEFT_ARROW)

        if pin0_dark_t and pin1_dark_t:
            dt = abs(pin1_dark_t - pin0_dark_t)  # milliseconds
            v = int(speed(dt))
            if 0 < v < 300:  # avoid invalid readings
                display.scroll('{}km/h'.format(v), delay=SCROLL_DELAY)
            else:
                wait_until_ready()
                sleep(1000)  # wait for train to pass
            # Reset for next events
            pin0_dark_t = 0
            pin1_dark_t = 0
            display.show(READY_SYMBOL)

        if pin0_dark_t or pin0_dark_t:
            continue  # ongoing measurement, skip delay

        sleep(10)  # delay to save battery


def main():
    display.scroll('FJR')
    wait_until_ready()
    display.show(READY_SYMBOL)
    measure()

main()
