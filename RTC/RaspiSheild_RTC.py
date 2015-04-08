#!/usr/bin/python

import smbus
import time
import os, time

os.system("sudo modprobe i2c:mcp7941x -r")

bus = smbus.SMBus(1)

RTC = 0x6F

#MCP7941x I2C Addresses
RTC_ADDR = 0x6F
EEPROM_ADDR = 0x57

#MCP7941x Register Addresses
TIME_REG = 0x00        #7 registers, Seconds, Minutes, Hours, DOW, Date, Month, Year
DAY_REG = 0x03         #the RTC Day register contains the OSCON, VBAT, and VBATEN bits
YEAR_REG = 0x06        #RTC year register
CTRL_REG = 0x07        #control register
CALIB_REG = 0x08       #calibration register
UNLOCK_ID_REG = 0x09   #unlock ID register
ALM0_REG = 0x0A        #alarm 0, 6 registers, Seconds, Minutes, Hours, DOW, Date, Month
ALM1_REG = 0x11        #alarm 1, 6 registers, Seconds, Minutes, Hours, DOW, Date, Month
ALM0_DAY = 0x0D        #DOW register has alarm config/flag bits
PWRDWN_TS_REG = 0x18   #power-down timestamp, 4 registers, Minutes, Hours, Date, Month
PWRUP_TS_REG = 0x1C    #power-up timestamp, 4 registers, Minutes, Hours, Date, Month
TIMESTAMP_SIZE = 8     #number of bytes in the two timestamp registers
SRAM_START_ADDR = 0x20 #first SRAM address
SRAM_SIZE = 64         #number of bytes of SRAM
EEPROM_SIZE = 128      #number of bytes of EEPROM
EEPROM_PAGE_SIZE = 8   #number of bytes on an EEPROM page
UNIQUE_ID_ADDR = 0xF0  #starting address for unique ID
UNIQUE_ID_SIZE = 8     #number of bytes in unique ID

#Control Register bits
OUT = 7       #sets logic level on MFP when not used as square wave output
SQWE = 6      #set to enable square wave output
ALM1 = 5      #alarm 1 is active
ALM0 = 4      #alarm 0 is active
EXTOSC = 3    #set to drive the RTC registers from an external oscillator instead of a crystal
RS2 = 2       #RS2:0 set square wave output frequency: 0==1Hz, 1==4096Hz, 2==8192Hz, 3=32768Hz
RS1 = 1
RS0 = 0
SQWAVE_1_HZ = 1
SQWAVE_4096_HZ = 2
SQWAVE_8192_HZ = 3
SQWAVE_32768_HZ = 4
SQWAVE_NONE = 5

#Other Control Bits
ST = 7        #Seconds register (TIME_REG) oscillator start/stop bit, 1==Start, 0==Stop
HR1224 = 6    #Hours register (TIME_REG+2) 12 or 24 hour mode (24 hour mode==0)
AMPM = 5      #Hours register (TIME_REG+2) AM/PM bit for 12 hour mode
OSCON = 5     #Day register (TIME_REG+3) oscillator running (set and cleared by hardware)
VBAT = 4      #Day register (TIME_REG+3) set by hardware when Vcc fails and RTC runs on battery.
                    #VBAT is cleared by software, clearing VBAT also clears the timestamp registers
VBATEN = 3    #Day register (TIME_REG+3) VBATEN==1 enables backup battery, VBATEN==0 disconnects the VBAT pin (e.g. to save battery)
LP = 5        #Month register (TIME_REG+5) leap year bit

#Alarm Control Bits
ALMPOL = 7    #Alarm Polarity: Defines the logic level for the MFP when an alarm is triggered.
ALMC2 = 6     #Alarm configuration bits determine how alarms match. See ALM_MATCH defines below.
ALMC1 = 5
ALMC0 = 4
ALMIF = 3     #Alarm Interrupt Flag: Set by hardware when an alarm was triggered, cleared by software.

ALM_MATCH_SECONDS = 0
ALM_MATCH_MINUTES = 1
ALM_MATCH_HOURS = 2
ALM_MATCH_DAY = 3
ALM_MATCH_DATE = 4
ALM_RESERVED_5 = 5
ALM_RESERVED_6 = 6
ALM_MATCH_DATETIME = 7
ALM_DISABLE = 8

#Note ALM_MATCH_DAY triggers alarm at midnight
ALARM_0 = 0   #constants for calling functions
ALARM_1 = 1

def _BV(bit):
	return 1 << (bit)

def i2cRead(add, reg):
	data = bus.read_byte_data(add, reg)
	return data

def i2cWrite(add, reg, data):
	bus.write_byte_data(add, reg, data)
	return true

def dec2bcd(num):
	return num + 6 * (num / 10)

def bcd2dec(num):
	return num - 6 * (num >> 4)

##########################################################################
#Read the RTC
##########################################################################
def RTC_read():
	os.system("sudo modprobe i2c:mcp7941x -r")
	global Second
	global Minute
	global Hour
	global Wday
	global Day
	global Month
	global Year
	#request 7 bytes (secs, min, hr, dow, date, mth, yr)
	Second = bcd2dec(i2cRead(RTC_ADDR,TIME_REG) & ~_BV(ST))
	Minute = bcd2dec(i2cRead(RTC_ADDR,TIME_REG+1))
	Hour = bcd2dec(i2cRead(RTC_ADDR,TIME_REG+2) & ~_BV(HR1224))    #assumes 24hr clock
	Wday = i2cRead(RTC_ADDR,TIME_REG+3) & ~(_BV(OSCON) | _BV(VBAT) | _BV(VBATEN))    #mask off OSCON, VBAT, VBATEN bits
	Day = bcd2dec(i2cRead(RTC_ADDR,TIME_REG+4))
	Month = bcd2dec(i2cRead(RTC_ADDR,TIME_REG+5) & ~_BV(LP))      #mask off the leap year bit
	Year = bcd2dec(i2cRead(RTC_ADDR,TIME_REG+6))
	os.system("sudo modprobe i2c:mcp7941x")
	return

##########################################################################
#Set an alarm time. Sets the alarm registers only, does not enable the
#alarm. See enableAlarm().
##########################################################################
def RTC_setAlarm(alarmNumber, alarmSec, alarmMin, alarmHour, alarmWday, alarmDay, alarmMonth):
	os.system("sudo modprobe i2c:mcp7941x -r")
	alarmNumber &= 0x01     #ensure a valid alarm number
	day = i2cRead(RTC_ADDR, ALM0_DAY + alarmNumber * (ALM1_REG - ALM0_REG)) #need to preserve bits in the day (of week)
	#Wday = i2cRead(RTC_ADDR,TIME_REG+3) & ~(_BV(OSCON) | _BV(VBAT) | _BV(VBATEN))    #mask off OSCON, VBAT, VBATEN bits
	i2cWrite(RTC_ADDR, ALM0_REG + alarmNumber * (ALM1_REG - ALM0_REG), dec2bcd(alarmSec))
	i2cWrite(RTC_ADDR, ALM0_REG + alarmNumber * (ALM1_REG - ALM0_REG)+1, dec2bcd(alarmMin))
	i2cWrite(RTC_ADDR, ALM0_REG + alarmNumber * (ALM1_REG - ALM0_REG)+2, dec2bcd(alarmHour))
	i2cWrite(RTC_ADDR, ALM0_REG + alarmNumber * (ALM1_REG - ALM0_REG)+3, dec2bcd((day & 0xF8) + alarmWday))
	#i2cWrite(RTC_ADDR, ALM0_REG + alarmNumber * (ALM1_REG - ALM0_REG)+3, dec2bcd((day & 0xF8) + Wday))
	i2cWrite(RTC_ADDR, ALM0_REG + alarmNumber * (ALM1_REG - ALM0_REG)+4, dec2bcd(alarmDay))
	i2cWrite(RTC_ADDR, ALM0_REG + alarmNumber * (ALM1_REG - ALM0_REG)+5, dec2bcd(alarmMonth))
	os.system("sudo modprobe i2c:mcp7941x")

##########################################################################
#Enable or disable an alarm, and set the trigger criteria, e.g. match only
#seconds, only minutes, entire time and date, etc.
##########################################################################
def RTC_enableAlarm(alarmNumber, alarmType):
	os.system("sudo modprobe i2c:mcp7941x -r")
	alarmNumber &= 0x01 	#ensure a valid alarm number
	ctrl = i2cRead(RTC_ADDR, CTRL_REG)
	if (alarmType < ALM_DISABLE):
		day = i2cRead(RTC_ADDR, ALM0_DAY + alarmNumber * (ALM1_REG - ALM0_REG))	#need to preserve bits in the day (of week) 
		day = ( day & 0x87 ) | alarmType << 4  #reset interrupt flag, OR in the config bits
		i2cWrite(RTC_ADDR, ALM0_DAY + alarmNumber * (ALM1_REG - ALM0_REG), day)
		ctrl |= _BV(ALM0 + alarmNumber)	#enable the alarm
	else:
		ctrl &= ~(_BV(ALM0 + alarmNumber))	#disable the alarm
	i2cWrite(RTC_ADDR, CTRL_REG, ctrl)
	os.system("sudo modprobe i2c:mcp7941x")


##########################################################################
# Returns true or false depending on whether the given alarm has been
# triggered, and resets the alarm "interrupt" flag. This is not a real
# interrupt, just a bit that's set when an alarm is triggered.
##########################################################################
def RTC_alarm(alarmNumber):
	os.system("sudo modprobe i2c:mcp7941x -r")
	alarmNumber &= 0x01 	#ensure a valid alarm number
	day = i2cRead(RTC_ADDR, ALM0_DAY + alarmNumber * (ALM1_REG - ALM0_REG))	#alarm day register has config & flag bits
	if (day & _BV(ALMIF)):
		day &= ~_BV(ALMIF)	#turn off the alarm "interrupt" flag
		i2cWrite(RTC_ADDR, ALM0_DAY + alarmNumber * (ALM1_REG - ALM0_REG), day)
		os.system("sudo modprobe i2c:mcp7941x")
		return 1
	else:
		os.system("sudo modprobe i2c:mcp7941x")
		return 0

##########################################################################
# Specifies the logic level on the Multi-Function Pin (MFP) when an    *
# alarm is triggered. The default is LOW. When both alarms are         *
# active, the two are ORed together to determine the level of the MFP. *
# With alarm polarity set to LOW (the default), this causes the MFP    *
# to go low only when BOTH alarms are triggered. With alarm polarity   *
# set to HIGH, the MFP will go high when EITHER alarm is triggered.    *
#                                                                      *
# Note that the state of the MFP is independent of the alarm           *
# "interrupt" flags, and the alarm() function will indicate when an    *
# alarm is triggered regardless of the polarity.                       
##########################################################################
def RTC_alarmPolarity(polarity):
	os.system("sudo modprobe i2c:mcp7941x -r")
	alm0Day = i2cRead(RTC_ADDR, ALM0_DAY)
	if (polarity):
		alm0Day |= _BV(OUT)
	else:
		alm0Day &= ~_BV(OUT)
	i2cWrite(RTC_ADDR, ALM0_DAY, alm0Day)
	os.system("sudo modprobe i2c:mcp7941x")

##########################################################################
# Check to see if the RTC's oscillator is started (ST bit in seconds   *
# register). Returns true if started.
##########################################################################
def RTC_isRunning():
	os.system("sudo modprobe i2c:mcp7941x -r")
	st = i2cRead(RTC_ADDR, TIME_REG)
	os.system("sudo modprobe i2c:mcp7941x")
	return st & _BV(ST)

##########################################################################
# Set or clear the VBATEN bit. Setting the bit powers the clock and    *
# SRAM from the backup battery when Vcc falls. Note that setting the   *
# time via set() or write() sets the VBATEN bit.                       
##########################################################################
def RTC_vbaten(enable):
	os.system("sudo modprobe i2c:mcp7941x -r")
	day = i2cRead(RTC_ADDR, ALM0_DAY + alarmNumber * (ALM1_REG - ALM0_REG))	
	if (enable):
		day |= _BV(VBATEN)
	else:
		day &= ~_BV(VBATEN)
	i2cWrite(RTC_ADDR, ALM0_DAY + alarmNumber * (ALM1_REG - ALM0_REG), day)
	os.system("sudo modprobe i2c:mcp7941x")
	return 1
