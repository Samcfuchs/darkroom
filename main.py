from time import sleep
import time
from machine import  Pin, ADC, I2C, Timer
from pico_i2c_lcd import I2cLcd

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

I2C_ADDR = i2c.scan()[0]
LCD = I2cLcd(i2c, I2C_ADDR, 2, 16)

N_SLOTS = 6
PIN_RED = 18
PIN_BLUE = 16
PIN_BLACK = 17
PIN_DIAL = 26
PIN_RELAY = 14

positions = [
    [1,0],
    [6,0],
    [11,0],
    [1,1],
    [6,1],
    [11,1]
]

exposure_values = [
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0
]

pot = ADC(Pin(PIN_DIAL))
#button_red =   Pin(PIN_RED,   Pin.IN, Pin.PULL_UP)
button_blue =  Pin(PIN_BLUE,  Pin.IN, Pin.PULL_DOWN)
button_black = Pin(PIN_BLACK, Pin.IN, Pin.PULL_DOWN)
relay = Pin(PIN_RELAY, Pin.OUT, value=0)

def display_exposure_values(vals):
    LCD.clear()
    exp_vals = sorted(vals)[::-1]

    for pos, val in zip(positions, exp_vals):
        
    #putstr = f""" {exp_vals[0]:.1f} {exp_vals[1]:.1f} {exp_vals[2]:.1f}\n {exp_vals[3]:.1f} {exp_vals[4]:.1f} {exp_vals[5]:.2f}"""
        LCD.move_to(*pos)
        LCD.putstr(f"00{val:.1f}"[-4:])
        print(exp_vals)

def display_single_value(slot, value):
    LCD.move_to(*positions[slot])
    LCD.putstr(f"00{value:.1f}"[-4:])

def transform_dial_value(input):
    return input / 65536.0

def get_exposure_value(input):
    return input * 20.0

def set_indicator(slot, state):
    if state:
        pos = positions[slot]
        LCD.move_to(pos[0]-1, pos[1])
        LCD.putstr(">")
        
        LCD.move_to(pos[0]+4, pos[1])
        LCD.putstr("<")
    else:
        pos = positions[slot]
        LCD.move_to(pos[0]-1, pos[1])
        LCD.putstr(" ")
        
        LCD.move_to(pos[0]+4, pos[1])
        LCD.putstr(" ")

def get_blue():
    return not bool(button_blue.value())

def get_black():
    return not bool(button_black.value())


blue_prev_value = get_blue()
adjust_mode = False
array_slot = 0
display_slot = 0
exposure_value = 0
prev_slot = -1
exposure_mode = False


while True:
    display_exposure_values(exposure_values)
    while not exposure_mode:
        #print("Not in exposure mode")
        sleep(.02)
        dial_value = transform_dial_value(pot.read_u16())
        # If blue button is newly pressed
        if (get_blue() and not blue_prev_value):
            adjust_mode = not adjust_mode
            print(f"Toggles adjust mode to {adjust_mode}")

            # When entering adjustmode
            if (adjust_mode):
                exposure_values[display_slot] = -1
            # When exiting adjustmode
            else:
                exposure_values = sorted(exposure_values)[::-1]
                exposure_values[-1] = exposure_value
                exposure_values = sorted(exposure_values)[::-1]

                display_exposure_values(exposure_values)
            
            print(exposure_values)

        if not adjust_mode:
            # Map display slot to integers
            display_slot = 5 - int(min((1-dial_value) * 6, 5))

            if (display_slot != prev_slot):
                set_indicator(prev_slot, False)
                set_indicator(display_slot, True)

            prev_slot = display_slot
        elif adjust_mode:
            exposure_value = get_exposure_value(transform_dial_value(pot.read_u16()))
            display_single_value(display_slot, exposure_value)

        if get_black():
            if adjust_mode:
                exposure_values = sorted(exposure_values)[::-1]
                exposure_values[-1] = exposure_value
                adjust_mode = False

            exposure_mode = True
            set_indicator(display_slot, False)
        blue_prev_value = get_blue()
        black_prev_value = get_black()

    ##### BEGIN EXPOSURES #####
    # Exposure_values

    exposure_values = sorted(exposure_values)[::-1]
    exposure_step = -1
    
    print("Begin Exposures:")
    print(exposure_values)
    
    set_indicator(0, True)

    while exposure_mode:
        #set_indicator(exposure_step + 1, True)
        if get_blue() and not blue_prev_value:
            exposure_step += 1

            if exposure_values[exposure_step] == 0:
                # Exposures are finished
                exposure_mode = False
                continue
            
            startMs = time.ticks_ms()
            endMs = startMs + 1000.0*(exposure_values[exposure_step] - exposure_values[exposure_step+1])
            
            relay.value(1)

            while time.ticks_ms() < endMs:
                continue
            
            relay.value(0)
            
            set_indicator(exposure_step, False)
            set_indicator(exposure_step+1, True)
            
        blue_prev_value = get_blue()
        black_prev_value = get_black()
