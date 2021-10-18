import machine 
import utime as time
from machine import Pin

beam_pin = Pin(15, Pin.IN, Pin.PULL_UP)
old_beam_value = beam_pin.value()
last_time = time.ticks_us()

def beam_change(pin):
    global last_time
    broken = pin.value() == 0
    if not broken:
        elapsed_time = time.ticks_diff(time.ticks_us(), last_time)
        elapsed_time = elapsed_time / 1_000_000
        print('beam restored', elapsed_time)
    else:
        print("beam broken")
        last_time = time.ticks_us()

beam_pin.irq(handler = beam_change, trigger = Pin.IRQ_FALLING | Pin.IRQ_RISING)

while True:
    time.sleep(0.1)
