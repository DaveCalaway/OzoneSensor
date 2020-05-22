# I2C Ozone Sensor

# Device: https://is.gd/ai1Qdi & C library: https://github.com/DFRobot/DFRobot_OzoneSensor
# Rpi i2c smbus info:
# https://raspberry-projects.com/pi/programming-in-python/i2c-programming-in-python/using-the-i2c-interface-2
# https://www.electronicwings.com/raspberry-pi/python-based-i2c-functions-for-raspberry-pi
# http://wiki.erazor-zone.de/wiki:linux:python:smbus:doc
# https://embeddedmicro.weebly.com/raspberry-pi.html

import smbus
import time


# I2C channel 1 is connected to the GPIO pins
channel = 1

# Ozone Sensor - 0x70 - 0x71 - 0x72 - 0x73 ( default )
address = 0x73

# Mode
measure_mode_auto = 0x00
measure_mode_passive = 0x01

# register address
auto_read_data = 0x00 
passive_read_data = 0x01 
mode_register = 0x03
read_ozone_data_register = 0x04
AUTO_data_high_eight_bits = 0x09
AUTO_data_low_eight_bits = 0x0A
PASS_data_low_eight_bits = 0x08
PASS_data_high_eight_bits = 0x07

# variables
DEBUG = 1
OCOUNT = 100
m_flag = 0
collect_number = 20 # 1-100
OzoneData = [0x00] * OCOUNT


########################################
            ### FUNCTS ####
########################################

# SetModes
def setModes(mode, address):
    global measure_mode_auto, bus, measure_mode_passive, m_flag, mode_register

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
    global bus, m_flag, auto_read_data, read_ozone_data_register, AUTO_data_high_eight_bits, OzoneData, passive_read_data, PASS_data_high_eight_bits, DEBUG
    
    i = 0
    j = 0

    if CollectNum > 0:
        #for(j = CollectNum - 1;  j > 0; j--):
        for j in range(CollectNum - 1, j > 0, -1):
            OzoneData[j] = OzoneData[j-1]
            print(OzoneData[j])
        if m_flag == 0:
            # read active data in active mode, first request once, then read the data
            bus.write_byte_data(address, read_ozone_data_register, auto_read_data) 
            if DEBUG: 
                sleep(0.01); 
                read = bus.read_byte_data(address, read_ozone_data_register) 
                print("i wrote: {} and i read: {}".format(hex(auto_read_data),hex(read)))
            sleep(0.01);    
            OzoneData[0] = i2cReadOzoneData(address, AUTO_data_high_eight_bits)
            if DEBUG:
                print("Read active data in active mod")
                print("Word Ozone Data: ", OzoneData[0])
        if m_flag == 1:
            # read passive data in passive mode, first request once, then read the data
            bus.write_byte_data(address, read_ozone_data_register, passive_read_data)    
            if DEBUG: 
                sleep(0.01); 
                read = bus.read_byte_data(address, read_ozone_data_register) 
                print("i wrote: {} and i read: {}".format(hex(passive_read_data),hex(read)))
            time.sleep(0.01);    
            OzoneData[0] = i2cReadOzoneData(address, PASS_data_high_eight_bits)
            if DEBUG:
                print("Read passive data in passive mod")
                print("Word Ozone Data: ", OzoneData[0])
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
        bTemp = bTemp + bArray[i]
    return bTemp / iFilterLen



# i2cReadOzoneData
def i2cReadOzoneData(address, reg):
    global bus, DEBUG

    bus.write_byte(address, reg)
    time.sleep(0.01)

    # Wire.requestFrom(address, (uint8_t)2); // request 2 bytes from slave device address
    #     while (Wire.available())
    #         rxbuf[i++] = Wire.read();
    if DEBUG:
        first = bus.read_byte_data(address, 0x00)
        time.sleep(0.01)
        second = bus.read_byte_data(address, 0x01)
        time.sleep(0.01)
        print("first bytes: {}".format(first))
        print("second bytes: {}".format(second))
        result = (first << 8) + second
        print("bit shift: {}".format(result))
    # bus.read_word_data(address,cmd)
    rxbuf = bus.read_word_data(address, 0x00)
    return rxbuf



########################################
            ### MAIN ####
########################################
# Initialize I2C (SMBus)
print("Open i2c bus on channel: {}".format(channel))
bus = smbus.SMBus(channel)

# SetModes
print("Set the mode to: {} for the address: {}".format(measure_mode_passive, hex(address)))
setModes(measure_mode_passive, address)

# ReadOzoneData
while True:
    time.sleep(1.0)
    print("Read data from the sensor")
    ozoneConcentration = ReadOzoneData(collect_number, address)
    print("Ozone concentration is {} PPB.".format(ozoneConcentration))
    print("##########################################################################")


