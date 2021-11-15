import machine 
import utime as time
from machine import Pin
import ssd1306

clock_pin = 5
data_pin = 4
bus = 0

gate_detect_pin = 15
reset_pin_num = 1

i2c = machine.I2C(bus, sda=machine.Pin(data_pin), scl=machine.Pin(clock_pin))
display = ssd1306.SSD1306_I2C(128,64,i2c)
display.fill_rect(0,0,128,64,0)
display.fill_rect(10,40,60,12,0)
display.show()

reset_pin = Pin(reset_pin, Pin.IN, Pin.PULL_UP)
beam_pin = Pin(gate_detect_pin, Pin.IN, Pin.PULL_UP)
old_beam_value = beam_pin.value()
last_time = time.ticks_us()
distance = 0.035
MODE_WAITING = 0
MODE_PASSED_B = 1
MODE_COMPLETE = 2
velocity_1 = 0.0
velocity_2 = 0.0
time_at_a = 0.0
time_at_b = 0.0
time_at_c = 0.0
time_at_d = 0.0
acceleration = 0.0

mode = MODE_WAITING

def beam_change(pin):
    global time_at_a, time_at_b, time_at_c, time_at_d, last_time, distance, velocity_1, velocity_2, acceleration, mode
    broken = pin.value() == 0
    if not broken:
        time_now = time.ticks_us()
        elapsed_time = time.ticks_diff(time_now, last_time)
        elapsed_time = elapsed_time / 1_000_000
 
        print('beam restored', elapsed_time)
        if mode == MODE_WAITING:
            time_at_b = time_now
            velocity_1 = distance / elapsed_time
            mode = MODE_PASSED_B
        elif mode == MODE_PASSED_B:
            time_at_d = time_now
            half_a_to_b = time.ticks_diff(time_at_b, time_at_a)/2
            half_c_to_d = time.ticks_diff(time_at_d, time_at_c)/2
            b_to_d = time.ticks_diff(time_at_d, time_at_b)
            b_to_c = time.ticks_diff(time_at_c, time_at_b)
            # this would work too
            # acceleration_time = b_to_d + half_a_to_b - half_c_to_d
            acceleration_time = half_a_to_b + half_c_to_d + b_to_c
            velocity_2 = distance / elapsed_time
            acceleration_time = acceleration_time / 1_000_000
            mode = MODE_COMPLETE
            print('vel 2: ', velocity_2)
            acceleration = (velocity_2 - velocity_1) / acceleration_time
            print('acc: ', acceleration)
            update_screen()     
    else:
        last_time = time.ticks_us()
        print('beam broken')
        if mode == MODE_WAITING:
            time_at_a = last_time
        elif mode == MODE_PASSED_B:
            time_at_c = last_time
        
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
