#!/usr/bin/python

import smbus
import re


# ================================================
# SolutionMaker RaspiSheild DAC 8-Channel DAC
# Version 1.0 Created 07/04/2015
#
# Requires python smbus to be installed
#
# ================================================

class DAC :
  # internal variables

  __address = 0x60 # default address for dac 1 on RaspiSheild
  __address2 = 0x61 # default address for dac 2 on RaspiSheild


  __RAM_WriteSeq = 0x00 # sequential write to [RAM] (repeat the command!) 	
			#[00 + pd1 + pd0 + D11-8 --- D7-0]

  __RAM_WriteMulti = 0x40 # sequential write to [RAM] (repeat the command!) 	
			#[01000 + StartCH=00 + 0 --- vref + pd0 + pd1 + Gx + D11-8 --- D7-0]

  __WriteAll = 0x50 # sequential write to multiple channel	
			#[01010 + StartCH=00 + 0 --- vref + pd0 + pd1 + Gx + D11-8 --- D7-0]

  __WriteOne = 0x58 # write one channel
			#[01011 + CH=00 + 0 --- vref + pd0 + pd1 + Gx + D11-8 --- D7-0]

  __WriteVref = 0x80 # write Vref for all 4 channel
			#[100x + Vref A-D = 0000]

  __WritePD = 0xA0 # write Power Down bits (require another byte)
			#[101x + PD1=00 + PD2=00 (+ PD3=00 + PD4=00 + xxxx)]

  __WriteGain = 0xC0 # write Gain Bits
			#[110x + GainBits=1111]

#Control Bits

  

  # detect i2C port number and assign to i2c_bus
  for line in open('/proc/cpuinfo').readlines():
    m = re.match('(.*?)\s*:\s*(.*)', line)
    if m:
      (name, value) = (m.group(1), m.group(2))
      if name == "Revision":
        if value [-4:] in ('0002', '0003'):
          i2c_bus = 0
        else:
          i2c_bus = 1
        break
  
  # Define I2C bus and init        
  global bus
  bus = smbus.SMBus(i2c_bus); 

  #local methods    

  def _BV(bit):
    return 1 << (bit)

  def __updatebyte(self, byte, bit, value): 
      # internal method for setting the value of a single bit within a byte
    if value == 0:
        return byte & ~(1 << bit)
    elif value == 1:
        return byte | (1 << bit)


  def __checkbit(self, byte, bit): 
      # internal method for reading the value of a single bit within a byte
    if byte & (1 << bit):
        return 1
    else:
        return 0
  
  def __twos_comp(self, val, bits):
    if( (val&(1<<(bits-1))) != 0 ):
        val = val - (1<<bits)
    return val
 
  #init object with i2caddress, default is 0x60 0x61for RPi-Sheild
  def __init__(self, address=0x60, address2=0x61): 
    self.__address = address
    self.__address2 = address2
    

  def setVoltage(self, voltage=0, channel=0, chip=0):
    "Sets the output voltage to the specified value on the specified channel"
    if (voltage > 4095):
      voltage = 4095
    if (voltage < 0):
      voltage = 0
    if chip > 1:
      chip = 1
    if channel > 7:
      channel = 7
    if channel > 3:
      channel = channel-4
      chip=1
    if channel < 0:
      channel = 0
    print "Setting voltage to %04d on the channel %d, chip %d" % (voltage, channel, chip)
    # Value needs to be right-shifted
    bytes = [((voltage >> 8) & 0x0F), (voltage) & 0xFF]
    bus.write_i2c_block_data(self.__address +chip, self.__WriteOne + (channel << 1), bytes)  


  def setAllVoltage(self, volt0=0, volt1=0, volt2=0, volt3=0, volt4=0, volt5=0, volt6=0, volt7=0):
    "Sets the output voltage to the specified value"
    if (volt0 > 4095):
      volt0 = 4095
    if (volt0 < 0):
          volt0 = 0
    if (volt1 > 4095):
      volt1 = 4095
    if (volt1 < 0):
          volt1 = 0
    if (volt2 > 4095):
      volt2 = 4095
    if (volt2 < 0):
           volt2 = 0
    if (volt3 > 4095):
      volt3 = 4095
    if (volt3 < 0):
           volt3 = 0  
    if (volt4 > 4095):
      volt4 = 4095
    if (volt4 < 0):
           volt4 = 0  
    if (volt5 > 4095):
      volt5 = 4095
    if (volt5 < 0):
           volt5 = 0  
    if (volt6 > 4095):
      volt6 = 4095
    if (volt6 < 0):
           volt6 = 0  
    if (volt7 > 4095):
      volt7 = 4095
    if (volt7 < 0):
           volt7 = 0  
    print 'Setting voltage to {0:8.3f}{1:8.3f}{2:8.3f}{3:8.3f} '.format(volt0, volt1, volt2, volt3)
    # Break integers into 2 bytes for sending to MCP4728
    bytes = [(volt0 >> 8) & 0x0F, (volt0) & 0xFF, (volt1 >> 8) & 0x0F, (volt1) & 0xFF, (volt2 >> 8) & 0x0F, (volt2) & 0xFF, (volt3 >> 8) & 0x0F, (volt3) & 0xFF] 
    bytes2 = [(volt4 >> 8) & 0x0F, (volt4) & 0xFF, (volt5 >> 8) & 0x0F, (volt5) & 0xFF, (volt6 >> 8) & 0x0F, (volt6) & 0xFF, (volt7 >> 8) & 0x0F, (volt7) & 0xFF]
    bus.write_i2c_block_data(self.__address, self.__WriteAll, bytes)
    bus.write_i2c_block_data(self.__address2, self.__WriteAll, bytes2)

  def setVref(self, vref0=0, vref1=0, vref2=0, vref3=0, vref4=0, vref5=0, vref6=0, vref7=0):
    byte0 = 0+(vref0 << 3) + (vref1 << 2) + (vref2 << 1) + vref3
    byte1 = 0+(vref4 << 3) + (vref5 << 2) + (vref6 << 1) + vref7
    bus.write_byte(self.__address, self.__WriteVref + byte0)
    bus.write_byte(self.__address +1, self.__WriteVref + byte1)

  def setPD(self, pd0=0, pd1=0, pd2=0, pd3=0, pd4=0, pd5=0, pd6=0, pd7=0):
    byte0 = 0+(pd0 << 6) + (pd1 << 4) + (pd2 << 2) + pd3
    byte1 = 0+(pd4 << 6) + (pd5 << 4) + (pd6 << 2) + pd7
    bus.write_byte_data(self.__address, self.__WritePD + (byte0 >> 4), (byte0 & 0x0F))
    bus.write_byte_data(self.__address +1, self.__WritePD + (byte1 >> 4), (byte1 & 0x0F))

  def setGain(self, gain0=0, gain1=0, gain2=0, gain3=0, gain4=0, gain5=0, gain6=0, gain7=0):
    byte0 = 0+(gain0 << 3) + (gain1 << 2) + (gain2 << 1) + gain3
    byte1 = 0+(gain4 << 3) + (gain5 << 2) + (gain6 << 1) + gain7
    bus.write_byte(self.__address, self.__WriteGain + byte0)
    bus.write_byte(self.__address +1, self.__WriteGain + byte1)
