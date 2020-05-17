# I2C Ozone Sensor

# Device: https://is.gd/ai1Qdi & C library: https://github.com/DFRobot/DFRobot_OzoneSensor
# Rpi i2c smbus info:
# https://raspberry-projects.com/pi/programming-in-python/i2c-programming-in-python/using-the-i2c-interface-2
# https://www.electronicwings.com/raspberry-pi/python-based-i2c-functions-for-raspberry-pi
# http://wiki.erazor-zone.de/wiki:linux:python:smbus:doc

import smbus
from time import sleep

# I2C channel 1 is connected to the GPIO pins
channel = 1

# Ozone Sensor
# 0x70 - 0x71 - 0x72 - 0x73 ( default )
address = 0x73

# Mode
global measure_mode_auto = 0x00
global measure_mode_passive = 0x01

# 
global auto_read_data = 0x00 
global passive_read_data = 0x01 

# 
global mode_register = 0x03
global read_ozone_data_register = 0x04

#
global AUTO_data_high_eight_bits = 0x09
global AUTO_data_low_eight_bits = 0x0A

#
global PASS_data_low_eight_bits = 0x08
global PASS_data_high_eight_bits = 0x07

global OCOUNT = 100
global m_flag = 0
global collect_number = 20 # 1-100
global OzoneData = [0] * OCOUNT



########################################
            ### MAIN ####
########################################
# Initialize I2C (SMBus)
print("Open i2c bus on channel: {}".format(channel))
bus = smbus.SMBus(channel)

# SetModes
# Write out I2C command: address, reg_write_dac, msg[0], msg[1]
print("Set the mode to: {} for the address: {}".format(measure_mode_passive, address))
setModes(measure_mode_passive, address)

# ReadOzoneData
print("Read data from the sensor")
ozoneConcentration = ReadOzoneData(collect_number, address)
print("Ozone concentration is {} PPB.".format(ozoneConcentration))
sleep(1)



########################################
            ### FUNCTS ####
########################################

# SetModes
def setModes(mode, address):
    if mode == measure_mode_auto:
        # Bus.write_byte_data(Device Address, Register Address, Value)
        bus.write_byte_data(address, mode_register, measure_mode_auto)
        m_flag = 0
    if mode == measure_mode_passive:
        # Bus.write_byte_data(Device Address, Register Address, Value)
        bus.write_byte_data(address, mode_register, measure_mode_passive)
        m_flag = 1
    else:
        m_flag = -1



# ReadOzoneData
def ReadOzoneData(CollectNum, address):
    i = 0
    if CollectNum > 0:
        #for(j = CollectNum - 1;  j > 0; j--):
        for j in range(CollectNum - 1, j > 0, -1):
            OzoneData[j] = OzoneData[j-1]
        if m_flag == 0:
            # read active data in active mode
            bus.write_byte_data(address, SET_PASSIVE_REGISTER, auto_read_data)    
            sleep(0.01);    
            OzoneData[0] = i2cReadOzoneData(address, AUTO_data_high_eight_bits)
        if m_flag == 1:
            # read passive data in passive mode, first request once, then read the data
            bus.write_byte_data(address, SET_PASSIVE_REGISTER, passive_read_data)    
            sleep(0.01);    # read active data in active mode
            OzoneData[0] = i2cReadOzoneData(address, PASS_data_high_eight_bits)
        if i < CollectNum:
            i = i + 1
        return getAverageNum(OzoneData, i)
    if CollectNum <= 0 or CollectNum > 100:
        return -1



# getAverageNum
def getAverageNum(bArray, iFilterLen):
    bTemp = 0
    #for(i = 0; i < iFilterLen; i++):
    for i in range(iFilterLen):
        bTemp += bArray[i]
    return bTemp / iFilterLen



# i2cReadOzoneData
def i2cReadOzoneData(address, reg):
    bus.write_byte(address, reg)
    sleep(0.01)

    # Wire.requestFrom(address, (uint8_t)2); // request 2 bytes from slave device address
    #     while (Wire.available())
    #         rxbuf[i++] = Wire.read();
    # bus.read_word_data(address,cmd)
    rxbuf = bus.read_word_data(address, 0x00)

    return (rxbuf[0] << 8) + rxbuf[1]
    