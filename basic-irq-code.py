import machine 
import utime as time
from machine import Pin

beam_pin = Pin(15, Pin.IN, Pin.PULL_UP)
old_beam_value = beam_pin.value()

def beam_change(pin):
    broken = pin.value() == 0
    if not broken:
        print('TRUE')
    else:
        print("FALSE")

beam_pin.irq(handler = beam_change, trigger = Pin.IRQ_FALLING | Pin.IRQ_RISING)

while True:
    time.sleep(0.1)
