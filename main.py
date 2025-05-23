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

TEST_MODE = False

positions = [
    [1,0],
    [6,0],
    [11,0],
    [1,1],
    [6,1],
    [11,1]
]

pot = ADC(Pin(PIN_DIAL))
button_red =   Pin(PIN_RED,   Pin.IN, Pin.PULL_DOWN)
button_blue =  Pin(PIN_BLUE,  Pin.IN, Pin.PULL_DOWN)
button_black = Pin(PIN_BLACK, Pin.IN, Pin.PULL_DOWN)
relay = Pin(PIN_RELAY, Pin.OUT, value=0)

"""
 
 ██╗   ██╗████████╗██╗██╗     
 ██║   ██║╚══██╔══╝██║██║     
 ██║   ██║   ██║   ██║██║     
 ██║   ██║   ██║   ██║██║     
 ╚██████╔╝   ██║   ██║███████╗
  ╚═════╝    ╚═╝   ╚═╝╚══════╝
                              
 
"""

def display_exposure_values_new(vals):
    LCD.clear()
    exp_vals = filter(lambda v: v != 0, sorted(vals)[::-1])
    for i,val in enumerate(exp_vals):
        pos = positions[i+1]
        LCD.move_to(*pos)
        LCD.putstr(f"00{val:.1f}"[-4:])

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
        LCD.putstr("(")
        
        LCD.move_to(pos[0]+4, pos[1])
        LCD.putstr(")")
    else:
        pos = positions[slot]
        LCD.move_to(pos[0]-1, pos[1])
        LCD.putstr(" ")
        
        LCD.move_to(pos[0]+4, pos[1])
        LCD.putstr(" ")

def get_blue():
    return not bool(button_blue.value())

def get_red():
    return not bool(button_red.value())

def get_black():
    return not bool(button_black.value())

blue_prev_value = get_blue()
red_prev_value = get_blue()
black_prev_value = get_black()
#display_slot = 0
exposure_value = 0
exposure_mode = False

exposure_values : list[float] = []

"""
 
 ██╗      ██████╗  ██████╗ ██████╗ 
 ██║     ██╔═══██╗██╔═══██╗██╔══██╗
 ██║     ██║   ██║██║   ██║██████╔╝
 ██║     ██║   ██║██║   ██║██╔═══╝ 
 ███████╗╚██████╔╝╚██████╔╝██║     
 ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝     
                                   
 
"""

while True:
    #LCD.blink_cursor_off()
    LCD.backlight_on()
    display_exposure_values_new(exposure_values)
    time.sleep(.5)
    set_indicator(0, True)

    print("Indicator set")
    
    exposure_mode = False

    while not exposure_mode:
        #print("Not in exposure mode")
        sleep(.02)
        dial_value = transform_dial_value(pot.read_u16())

        # If blue button is newly pressed
        if (get_blue() and not blue_prev_value):
            # Commit exposure value
            exposure_values.append(exposure_value)
            exposure_values = sorted(exposure_values)[::-1]

            display_exposure_values_new(exposure_values)
            set_indicator(0, True)

            print(exposure_values)

        exposure_value = get_exposure_value(transform_dial_value(pot.read_u16()))
        display_single_value(0, exposure_value)

        if (get_red() and not red_prev_value):
            if (exposure_values):
                exposure_values.pop(0)
            print(exposure_values)
            display_exposure_values_new(exposure_values)
            set_indicator(0, True)

        if get_black():
            exposure_mode = True


        blue_prev_value = get_blue()
        red_prev_value = get_red()
        black_prev_value = get_black()

    """
    
    ██████╗ ███████╗ ██████╗ ██╗███╗   ██╗    ███████╗██╗  ██╗██████╗  ██████╗ ███████╗██╗   ██╗██████╗ ███████╗███████╗
    ██╔══██╗██╔════╝██╔════╝ ██║████╗  ██║    ██╔════╝╚██╗██╔╝██╔══██╗██╔═══██╗██╔════╝██║   ██║██╔══██╗██╔════╝██╔════╝
    ██████╔╝█████╗  ██║  ███╗██║██╔██╗ ██║    █████╗   ╚███╔╝ ██████╔╝██║   ██║███████╗██║   ██║██████╔╝█████╗  ███████╗
    ██╔══██╗██╔══╝  ██║   ██║██║██║╚██╗██║    ██╔══╝   ██╔██╗ ██╔═══╝ ██║   ██║╚════██║██║   ██║██╔══██╗██╔══╝  ╚════██║
    ██████╔╝███████╗╚██████╔╝██║██║ ╚████║    ███████╗██╔╝ ██╗██║     ╚██████╔╝███████║╚██████╔╝██║  ██║███████╗███████║
    ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝    ╚══════╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝
                                                                                                                        
    
    """

    if len(exposure_values) == 0:
        exposure_values.append(exposure_value)
    display_exposure_values_new(exposure_values)

    exposure_values = sorted(exposure_values)[::-1]
    exposure_values.append(0)
    exposure_step = 0
    
    print("Begin Exposures:")
    print(exposure_values)

    LCD.backlight_off()
    #LCD.blink_cursor_on()
    
    set_indicator(0, True)
    display_single_value(0, exposure_values[0])

    while exposure_mode:
        #set_indicator(exposure_step + 1, True)
        if exposure_step >= len(exposure_values) - 1:
            # Exposures are finished
            exposure_mode = False
            exposure_values.remove(0)

            #LCD.blink_cursor_off()

            continue
            
        if get_blue() and not blue_prev_value:
            print(exposure_step)
            LCD.move_to(*positions[exposure_step+1])

            startMs = time.ticks_ms()
            durationMs = 1000.0*(exposure_values[exposure_step] - exposure_values[exposure_step+1])
            endMs = startMs + 1000.0*(exposure_values[exposure_step] - exposure_values[exposure_step+1])
            
            relay.value(1)
            if TEST_MODE:
                LCD.backlight_on()
            

            while time.ticks_ms() < endMs:
                elapsedMs = time.ticks_ms() - startMs
                if (elapsedMs % 4 == 0):
                    display_single_value(0, exposure_values[exposure_step] - (elapsedMs / 1000.0))
            
            relay.value(0)
            if TEST_MODE:
                LCD.backlight_off()
            
            #set_indicator(exposure_step, False)
            #set_indicator(exposure_step+1, True)
            exposure_step += 1
            
        blue_prev_value = get_blue()
        black_prev_value = get_black()
    
    developing = True

    LCD.move_to(0,0)
    LCD.clear()
    LCD.putstr("Develop")

    while developing:
        if (get_blue() and get_red()):# and not blue_prev_value):
            developing = False
            time.sleep(1)

        blue_prev_value = get_blue()
        black_prev_value = get_red()
    
    #LCD.clear()
