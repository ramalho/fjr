# fjr
Ferrovia  Jairo Ramalho


```python
from microbit import *
import time

# Threshold value for the inputs
threshold = 500

def read_adc(pin):
    # Read and return the analog value from the specified pin (0 to 1023)
    return pin.read_analog()

def monitor_inputs():
    # Variables to track when each pin goes below the threshold
    time_pin0_below = None
    time_pin1_below = None

    while True:
        # Read the current values from P0 and P1
        value0 = read_adc(pin0)
        value1 = read_adc(pin1)

        # Check if P0 goes below the threshold and time_pin0_below is not yet set
        if value0 < threshold and time_pin0_below is None:
            time_pin0_below = running_time()  # Record the time when P0 goes below 500
            display.show("0")  # Display '0' on the micro:bit to indicate P0 event

        # Check if P1 goes below the threshold and time_pin1_below is not yet set
        if value1 < threshold and time_pin1_below is None:
            time_pin1_below = running_time()  # Record the time when P1 goes below 500
            display.show("1")  # Display '1' on the micro:bit to indicate P1 event

        # If both pins have gone below the threshold, calculate the elapsed time
        if time_pin0_below is not None and time_pin1_below is not None:
            elapsed_time = abs(time_pin1_below - time_pin0_below)  # Time in milliseconds
            display.scroll("Time: {} ms".format(elapsed_time))

            # Reset to monitor for the next event
            time_pin0_below = None
            time_pin1_below = None
            display.clear()  # Clear the display after showing the result

        sleep(10)  # Small delay to prevent spamming the loop

# Start monitoring the inputs
monitor_inputs()
```
