# Darkroom Timer

When connected to a potentiometer, standard LCD display, and three buttons to an
RP2040 chip, this embedded program runs a program to operate an enlarger (or,
practically, any powered relay) at precise intervals.

![](fritzing.png)

## Instructions

A time is displayed in the upper left. Pressing blue will add that time to the
sequence. Pressing red will remove the longest time from the sequence. Pressing
black will move into exposure mode. While in exposure mode, the display is not
backlit, so it is safe to take out your paper.

In exposure mode, the remaining exposure time is displayed in the upper left.
Pressing blue will start the next exposure step, which will stop automatically when it
reaches the next exposure interval.

When the total exposure time has elapsed, the device will go into a waiting mode
while you develop the image. Pressing blue and red simultaneously will reset to
the first step, turning on the display backlight.

## Parts

- [I2C 1602 display backpack](https://www.alibaba.com/product-detail/Iicdisplay-Modulelcd-Creen-Module-1-Piece_1601433261587.html?mark=google_shopping&seo=1&gQT=2)
: Converts the standard 16-pin LCD interface to an I2C output that can be
controlled by [pico_i2c_lcd.py](./pico_i2c_lcd.py).
- [16x2 LCD display](https://www.alibaba.com/product-detail/LCD1602-Rohs-module-screen-16x2-Character_1600441231800.html?spm=a2700.galleryofferlist.normal_offer.d_price.50c413a0l1LCfv) 
: A commodity part--anything will do.
- Momentary push-buttons (3)
- Potentiometer (knob recommended)
- [Outlet relay](https://www.adafruit.com/product/2935?gQT=1): For toggling
  power according to 5V output. It really seems like there should be more of
  these out there, but this one works great. I can't recommend an 
  [AC output SSR](https://www.sensata.com/products/relays/solid-state-relays)
  because I'm not too interested in wiring mains myself.

## Next Steps

This isn't a final product. Here are some improvements I'd like to make in the
next iteration on the idea:

### Designed Enclosure

It's currently housed in a cardboard box, which is a little silly. I'd have to
3D print an enclosure with mounting points for 3 buttons, 1 potentiometer, and
the 2x16 display. It should have terminals for the relay outputs, and an opening
for the Pico's micro-usb port. I'll probably design this in two parts, a top and
a bottom piece. Soldering the bits together and fitting them into a compact case
could be difficult. I'll probably design something in Fusion360, FreeCAD, or
SolidWorks.

### Improved Buttons

I've already noticed problems with the arcade-style pushbuttons I'm using. They
use limit switches, and one already has intermittent signal issues. They're also
very high profile, which would increase size constraints.

### Relay Interface

I expect to continue to use a wire-pair style relay output, but I'd like to
divorce the wires from the design. Some kind of terminal block with a quick
attach and detach mechanism would make the device itself a lot cleaner. I could
simply mimic the terminal design on the outlet relay.

### Development Timing

After exposures finish, we do another timed task--developing and fixing the
print. The timer could easily provide input to this task also. I'd add this to
the software, and add an audio output--a buzzer would be very simple to
implement, but voice synthesis would make the UX clearer and perhaps would not
be too hard to include.

### Safelight Compatibility

I'd like to test the display output's light for paper compatibility. I can get a
red display, which might be usable in the dark, or use safelight filter paper to
cover the display. Ilford has information on safelight compatibility 
[here](https://www.ilfordphoto.com/amfile/file/download/file/605/product/613/).

### Integration

It would be nice to eliminate the chunky relay power strip that switches the
enlarger and is the most expensive part of the system. This would probably
require wiring some outlets for mains power, which is probably out of scope.

### Remote control

What if I could control this with RF signals? That would be pretty neat. 
[This guy](https://hblok.net/blog/posts/2012/09/02/home-automation-on-433-92-mhz-with-arduino/)
did some home automation with RF signals.
