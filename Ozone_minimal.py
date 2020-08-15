# I2C Ozone Sensor minimal 
# the function returns the average ppm if it's valid number, or -1 if is not valid
# read mode = measure_mode_auto


import smbus
import time

def read_ppb():
    # mode
    measure_mode_auto = 0x00

    # const
    mode_register = 0x03
    read_ozone_data_register = 0x04
    auto_read_data = 0x00 
    AUTO_data_high_eight_bits = 0x09

    # I2C channel 1 is connected to the GPIO pins
    channel = 1

    # Ozone Sensor - 0x70 - 0x71 - 0x72 - 0x73 ( default )
    address = 0x73

    # variables
    OCOUNT = 100
    collect_number = 20 # numbers of read 1-100
    OzoneData = [0x00] * OCOUNT 

    ########################################
                ### MAIN ####
    ########################################
    # Initialize I2C (SMBus)
    bus = smbus.SMBus(channel)

    # SetModes -> measure_mode_auto
    bus.write_byte_data(address, mode_register, measure_mode_auto)

    # ReadOzoneData
    for j in range(collect_number):
        # read active data in active mode
        bus.write_byte_data(address, read_ozone_data_register, auto_read_data)
        time.sleep(0.1);   
        # first request once
        bus.write_byte(address, AUTO_data_high_eight_bits)
        time.sleep(0.1)
        # then read 2 bytes from the sensor
        rxbuf = bus.read_i2c_block_data(address, AUTO_data_high_eight_bits, 2)
        # convert byte in a word
        O3_ppb = (rxbuf[0] << 8) + rxbuf[1]
        # send back the converted ppb to ppm
        OzoneData[j] = O3_ppb/1000

    # getAverageNum
    Ozone = 0
    for i in range(collect_number):
        Ozone = Ozone + OzoneData[i]
    # average
    Ozone_ppm = Ozone/collect_number

    # check if the result is valid or not
    if Ozone_ppm >= 0 or Ozone_ppm < 60:
        return Ozone_ppm
    else:
        return -1


            



