from microbit import *
from micropython import const

DARK_THRESHOLD = const(400)  # ADC range 0:1024
SCROLL_DELAY = const(90)  # ms
SENSOR_DISTANCE = const(64 / 1000)  # meters
H0_SCALE = const(87)  # 1:87

READY_SYMBOL = Image.YES
LEFT_ARROW = Image.ARROW_W
RIGHT_ARROW = Image.ARROW_E

ANALOG_MAX = 1023


class Sensor():
    def __init__(self, pin):
        self.pin = pin
        self.min = ANALOG_MAX
        self.max = 0
        self.threshold = 0
        # last time when pin went dark
        self.dark_time = 0

    def calibrate(self):
        value = self.pin.read_analog()
        if value < self.min:
            self.min = value
        elif value > self.max:
            self.max = value
        self.threshold = round((self.min + self.max) / 2)

    def dark(self):
        if self.pin.read_analog() < self.threshold:
            if self.dark_time == 0:
                self.dark_time = running_time()
            return True
        else:
            return False

    def restart(self):
        self.dark_time = 0


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


def wait_until_ready(sensors):
    # wait until lasers illuminate both sensors
    display.show('?')
    while any(s.dark() for s in sensors):
        sleep(50)


def measure(sensors):

    while True:
        if sensors[0].dark_time == 0 and sensors[0].dark():
            if sensors[1].dark_time == 0:
                display.show(RIGHT_ARROW)

        if sensors[1].dark_time == 0 and sensors[1].dark():
            if sensors[0].dark_time == 0:
                display.show(LEFT_ARROW)

        if sensors[0].dark_time and sensors[1].dark_time:
            dt = abs(sensors[1].dark_time - sensors[0].dark_time)  # milliseconds
            v = int(speed(dt))
            if 0 < v < 300:  # avoid invalid readings
                display.scroll('{}km/h'.format(v), delay=SCROLL_DELAY)
            else:
                wait_until_ready(sensors)
                sleep(1000)  # wait for train to pass
            # Restart timers for next events
            for sensor in sensors:
                sensor.restart()
            display.show(READY_SYMBOL)

        if sensors[0].dark_time or sensors[1].dark_time:
            continue  # ongoing measurement, skip delay

        sleep(10)  # delay to save battery


def show_bar(side, percent):
    x = 0 if side == 0 else 4
    full, partial = divmod(round(percent), 20)
    for i in range(5):
        if i <= full:
            brightness = 9
        elif partial and i <= (full + 1):
            brightness = round(9 * partial / 20)
        else:
            brightness = 0
        display.set_pixel(x, 4-i, brightness)


def calibrate(sensors):
    display.clear()
    while not button_b.was_pressed():
        light0 = pin0.read_analog()
        show_bar(0, light0/1023.0 * 100)
        sensors[0].calibrate()
        light1 = pin1.read_analog()
        show_bar(1, light1/1023.0 * 100)
        sensors[1].calibrate()
        # print((light0, light1))  # data for mu plotter
        sleep(10)


def main():
    sensors = [Sensor(pin0), Sensor(pin1)]
    display.scroll('press B to calibrate', delay=SCROLL_DELAY, wait=False)
    while not button_b.was_pressed():
        sleep(10)
    calibrate(sensors)
    wait_until_ready(sensors)
    display.show(READY_SYMBOL)
    measure(sensors)


main()
