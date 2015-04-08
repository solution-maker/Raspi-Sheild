#!/usr/bin/python

from RaspiSheild_IO import IO
import time

# ================================================
# Solution Maker RPi-Sheild IO 32-Channel Port Expander - Output Write Demo
# Version 1.0 Created 17/02/2015
#
# Requires python smbus to be installed with: sudo apt-get install python-smbus 
# run with: sudo python iopiwrite.py
# ================================================

# This example uses the writePin and writeBank methods to switch the pins on and off on the IO of RPi-Sheild board.

# Initialise the IOPi device using the default addresses
bus1 = IO(0x20)

# We will write to the pins 9 to 16 from bus 1 so set port 1 to be outputs turn off the pins
bus1.setPortDirection(1, 0x00)
bus1.writePort(1, 0x00)

while True:
    
    # count to 255 and display the value on pins 9 to 16 in binary format
    for x in range(0,255):
        time.sleep(0.05)
        bus1.writePort(1, x) 

    #turn off all of the pins on bank 1
    bus1.writePort(1, 0x00)

    #now turn on all of the leds in turn by writing to one pin at a time
    bus1.writePin(9, 1)
    time.sleep(0.1)
    bus1.writePin(10, 1)
    time.sleep(0.1)
    bus1.writePin(11, 1)
    time.sleep(0.1)
    bus1.writePin(12, 1)
    time.sleep(0.1)
    bus1.writePin(13, 1)
    time.sleep(0.1)
    bus1.writePin(14, 1)
    time.sleep(0.1)
    bus1.writePin(15, 1)
    time.sleep(0.1)
    bus1.writePin(16, 1)

    #and turn off all of the leds in turn by writing to one pin at a time
    bus1.writePin(9, 0)
    time.sleep(0.1)
    bus1.writePin(10, 0)
    time.sleep(0.1)
    bus1.writePin(11, 0)
    time.sleep(0.1)
    bus1.writePin(12, 0)
    time.sleep(0.1)
    bus1.writePin(13, 0)
    time.sleep(0.1)
    bus1.writePin(14, 0)
    time.sleep(0.1)
    bus1.writePin(15, 0)
    time.sleep(0.1)
    bus1.writePin(16, 0)

    #repeat until the program ends