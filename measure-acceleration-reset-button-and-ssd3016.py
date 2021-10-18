import machine 
import utime as time
from machine import Pin
import ssd1306

clockPin = 5
dataPin = 4
bus = 0

i2c = machine.I2C(bus,sda=machine.Pin(dataPin),scl=machine.Pin(clockPin))
display = ssd1306.SSD1306_I2C(128,64,i2c)
display.fill_rect(0,0,128,64,0)
display.fill_rect(10,40,60,12,0)
display.show()

reset_pin = Pin(1, Pin.IN, Pin.PULL_UP)
beam_pin = Pin(15, Pin.IN, Pin.PULL_UP)
old_beam_value = beam_pin.value()
last_time = time.ticks_us()
distance = 0.035
MODE_WAITING = 0
MODE_PASSED_B = 1
MODE_COMPLETE = 2
velocity_1 = 0.0
velocity_2 = 0.0
time_at_b = 0.0
time_at_d = 0.0
acceleration = 0.0

mode = MODE_WAITING

def beam_change(pin):
    global last_time, distance, velocity_1, velocity_2, acceleration, mode, time_at_b, time_at_d
    broken = pin.value() == 0
    if not broken:
        elapsed_time = time.ticks_diff(time.ticks_us(), last_time)
        elapsed_time = elapsed_time / 1_000_000
 
        print('beam restoreded', elapsed_time)
        if mode == MODE_WAITING:
            time_at_b = time.ticks_us()
            velocity_1 = distance / elapsed_time
            mode = MODE_PASSED_B

        elif mode == MODE_PASSED_B:
            time_at_d = time.ticks_us()
            velocity_2 = distance / elapsed_time
            acceleration_time = time.ticks_diff(time_at_d, time_at_b) / 1_000_000
            mode = MODE_COMPLETE
            print('vel 2: ', velocity_2)
            acceleration = (velocity_2 - velocity_1) / acceleration_time
            print('acc: ', acceleration)
            update_screen()
            
    else:
        last_time = time.ticks_us()
        print('beam broken')
        
def reset():
    global last_time, distance, velocity_1, velocity_2, acceleration, mode, time_at_b, time_at_d
    velocity_1 = 0.0
    velocity_2 = 0.0
    time_at_b = 0.0
    time_at_d = 0.0
    acceleration = 0.0
    print('RESET')
    time.sleep(1)
    mode = MODE_WAITING
    display.fill_rect(0,0,128,64,0)
    display.show()
    display.text('RESET :)',30,30)
    display.show()
    time.sleep(1)
    update_screen()
    
def update_screen():
    display.fill_rect(0,0,128,64,0)
    display.text('vel 1: ' + str(velocity_1),0,16)
    display.text('vel 2: ' + str(velocity_2),0,36)
    display.text('acc: ' + str(acceleration),0,54)
    display.show()

beam_pin.irq(handler = beam_change, trigger = Pin.IRQ_FALLING | Pin.IRQ_RISING)

while True:
    if reset_pin.value() == 0:
        reset()
    time.sleep(0.1)
