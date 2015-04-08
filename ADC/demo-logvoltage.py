#!/usr/bin/python

from RaspiSheild_ADC import ADC
import datetime
import time

# ================================================
# Solution Maker RPi-Sheild 8-Channel ADC data-logger demo
# Version 1.0 Created 17/02/2015
#
# Requires python smbus to be installed
# run with: python demo-readvoltage.py
# ================================================


# Initialise the ADC device using the default addresses and sample rate
# Sample rate can be 12,14, 16 or 18
adc = ADC(0x6a, 0x6b, 18)

def writetofile(texttowrtite):
	f = open('adclog.txt', 'a')
	f.write(str(datetime.datetime.now()) + " " + texttowrtite)
	f.closed

while (True):


  # read from adc channels and write to the log file
  writetofile ("Channel 1: %02f\n" % adc.readVoltage(1))
  writetofile ("Channel 2: %02f\n" % adc.readVoltage(2))
  writetofile ("Channel 3: %02f\n" % adc.readVoltage(3))
  writetofile ("Channel 4: %02f\n" % adc.readVoltage(4))
  writetofile ("Channel 5: %02f\n" % adc.readVoltage(5))
  writetofile ("Channel 6: %02f\n" % adc.readVoltage(6))
  writetofile ("Channel 7: %02f\n" % adc.readVoltage(7))
  writetofile ("Channel 8: %02f\n" % adc.readVoltage(8))

 
  # wait 1 second before reading the pins again
  time.sleep(1)