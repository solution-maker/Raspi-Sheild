#!/usr/bin/python

from __future__ import division
import RPi.GPIO as GPIO
import os, time
import RPIO

def Init():
        RPIO.setmode(GPIO.BCM)
        RPIO.setup(17, RPIO.IN, pull_up_down=RPIO.PUD_UP)
        RPIO.setup(27, RPIO.OUT, initial=RPIO.LOW)
        print ("[Info] Telling RaspiShield we are running on pin 27")

def off(gpio, value):
        print ("[Info] RaspiShield requesting shutdown on pin 17")
        RPIO.setup(27, RPIO.HIGH)
        os.system("sudo shutdown -h now")
        RPIO.cleanup()
        time.sleep(0.5)

Init()
RPIO.add_interrupt_callback(17, off, edge='falling')
RPIO.wait_for_interrupts()
