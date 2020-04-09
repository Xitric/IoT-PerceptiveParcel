"""
Driver taken from: https://github.com/FaBoPlatform/FaBoHumidity-HTS221-Python

coding: utf-8
@package HTS221
This is a FaBoHumidity_HTS221 library for the FaBo Humidity I2C Brick.
http://fabo.io/208.html

Released under APACHE LICENSE, VERSION 2.0
http://www.apache.org/licenses/

FaBo <info@fabo.io>

This file has been modified by Kasper Schultz Davidsen to remove dependencies
on the smbus library, and instead use the I2C class from the MicroPython
machine library. This mapping has been provided by Geoff Lee at:
    https://github.com/gkluoe/micropython-smbus
The file has also been modified to follow python standards in regards to
comments, method naming, etc. Non-english comments were also removed.
"""

from .usmbus import SMBus

# I2C Slave Address
SLAVE_ADDRESS = 0x5F

# Device Search Reg
DEVICE_REG = 0x0F

# Who am i device identifier
DEVICE_ID = 0xBC

# AV_CONF:AVGH
# Averaged humidity samples configuration
# AVGH_4   : 0b00000000
AVGH_4 = 0x00
# AVGH_8   : 0b00000001
AVGH_8 = 0x01
# AVGH_16  : 0b00000010
AVGH_16 = 0x02
# AVGH_32  : 0b00000011 # defalut
AVGH_32 = 0x03
# AVGH_64  : 0b00000100
AVGH_64 = 0x04
# AVGH_128 : 0b00000101
AVGH_128 = 0x05
# AVGH_256 : 0b00000110
AVGH_256 = 0x06
# AVGH_512 : 0b00000111
AVGH_512 = 0x07

# AV_CONF:AVGT
# Averaged temperature samples configuration
# AVGT_2   : 0b00000000
AVGT_2 = 0x00
# AVGT_4   : 0b00001000
AVGT_4 = 0x08
# AVGT_8   : 0b00010000
AVGT_8 = 0x10
# AVGT_16  : 0b00011000 # defalut
AVGT_16 = 0x18
# AVGT_32  : 0b00100000
AVGT_32 = 0x20
# AVGT_64  : 0b00101000
AVGT_64 = 0x28
# AVGT_128 : 0b00110000
AVGT_128 = 0x30
# AVGT_256 : 0b00111000
AVGT_256 = 0x38

# CTRL_REG1
# Power Down control : 0b10000000
PD = 0x80
# Block Data Update control : 0b00000100
BDU = 0x04
# Output Data Rate : One Shot : 0b00000000
ODR_ONE = 0x00
# Output Data Rate : 1Hz : 0b00000001
ODR_1HZ = 0x01
# Output Data Rate : 7Hz : 0b00000010
ODR_7HZ = 0x02
# Output Data Rate : 12.5Hz : 0b00000011
ODR_125HZ = 0x03

# CTRL_REG2
# Reboot memory content : 0b10000000
BOOT = 0x80
# Heater : 0b00000010
HEATER = 0x02
# One shot enable : 0b00000001
ONE_SHOT = 0x01

# CTRL_REG3
# DRDY pin is no connect in FaBo Brick
CTRL_REG3_DEFAULT = 0x00

# STATUS_REG
# Humidity Data Available
H_DA = 0x02
# Temperature Data Available
T_DA = 0x01

# Register Addresses
AV_CONF = 0x10
CTRL_REG1 = 0x20
CTRL_REG2 = 0x21
CTRL_REG3 = 0x22
STATUS_REG = 0x27
HUMIDITY_OUT_L = 0x28
HUMIDITY_OUT_H = 0x29
TEMP_OUT_L = 0x2A
TEMP_OUT_H = 0x2B
H0_RH_X2 = 0x30
H1_RH_X2 = 0x31
T0_DEGC_X8 = 0x32
T1_DEGC_X8 = 0x33
T1_T0_MSB = 0x35
H0_T0_OUT_L = 0x36
H0_T0_OUT_H = 0x37
H1_T0_OUT_L = 0x3A
H1_T0_OUT_H = 0x3B
T0_OUT_L = 0x3C
T0_OUT_H = 0x3D
T1_OUT_L = 0x3E
T1_OUT_H = 0x3F


# FaBo Humidity I2C Controller class
# noinspection DuplicatedCode,PyAttributeOutsideInit
class HTS221:

    def __init__(self, i2c, address=SLAVE_ADDRESS):
        self.bus = SMBus(i2c)
        self.address = address

        self.power_on()
        self.config_device()
        self.read_coef()

    def search_device(self):
        who_am_i = self.bus.read_byte_data(self.address, DEVICE_REG)

        if who_am_i == DEVICE_ID:
            return True
        else:
            return False

    def power_on(self):
        data = PD | ODR_1HZ
        self.bus.write_byte_data(self.address, CTRL_REG1, data)

    def config_device(self):
        data = AVGH_32 | AVGT_16
        self.bus.write_byte_data(self.address, AV_CONF, data)

    def read_coef(self):

        h0_rh = self.bus.read_byte_data(self.address, H0_RH_X2)
        h1_rh = self.bus.read_byte_data(self.address, H1_RH_X2)

        self.h0_rh_x2 = h0_rh  # uint8
        self.h1_rh_x2 = h1_rh  # uint8

        data = self.bus.read_byte_data(self.address, T1_T0_MSB)

        t0_degc_x8 = self.bus.read_byte_data(self.address, T0_DEGC_X8)
        t1_degc_x8 = self.bus.read_byte_data(self.address, T1_DEGC_X8)
        self.t0_degc_x8 = ((data & 0x3) << 8) | t0_degc_x8  # uint16
        self.t1_degc_x8 = ((data & 0xC) << 6) | t1_degc_x8  # uint16

        h0_t0_l = self.bus.read_byte_data(self.address, H0_T0_OUT_L)
        h0_t0_h = self.bus.read_byte_data(self.address, H0_T0_OUT_H)
        self.h0_t0_out = self.data_conv(h0_t0_l, h0_t0_h)  # int16

        h1_t0_l = self.bus.read_byte_data(self.address, H1_T0_OUT_L)
        h1_t0_h = self.bus.read_byte_data(self.address, H1_T0_OUT_H)
        self.h1_t0_out = self.data_conv(h1_t0_l, h1_t0_h)  # int16

        t0_l = self.bus.read_byte_data(self.address, T0_OUT_L)
        t0_h = self.bus.read_byte_data(self.address, T0_OUT_H)
        self.t0_out = self.data_conv(t0_l, t0_h)  # int16

        t1_l = self.bus.read_byte_data(self.address, T1_OUT_L)
        t1_h = self.bus.read_byte_data(self.address, T1_OUT_H)
        self.t1_out = self.data_conv(t1_l, t1_h)  # int16

    def read_humi(self):
        humidity = 0.0

        data = self.bus.read_byte_data(self.address, STATUS_REG)

        if data & H_DA:
            h_out_l = self.bus.read_byte_data(self.address, HUMIDITY_OUT_L)
            h_out_h = self.bus.read_byte_data(self.address, HUMIDITY_OUT_H)

            h_out = self.data_conv(h_out_l, h_out_h)

            t_h0_rh = self.h0_rh_x2 / 2.0
            t_h1_rh = self.h1_rh_x2 / 2.0
            humidity = t_h0_rh + (t_h1_rh - t_h0_rh) * (h_out - self.h0_t0_out) / (self.h1_t0_out - self.h0_t0_out)

        return humidity

    def read_temp(self):
        temperature = 0.0

        data = self.bus.read_byte_data(self.address, STATUS_REG)

        if data & T_DA:
            temp_out_l = self.bus.read_byte_data(self.address, TEMP_OUT_L)
            temp_out_h = self.bus.read_byte_data(self.address, TEMP_OUT_H)
            t_out = self.data_conv(temp_out_l, temp_out_h)  # int16

            t_t0_degc = self.t0_degc_x8 / 8.0
            t_t1_degc = self.t1_degc_x8 / 8.0
            temperature = t_t0_degc + (t_t1_degc - t_t0_degc) * (t_out - self.t0_out) / (self.t1_out - self.t0_out)

        return temperature

    @staticmethod
    def data_conv(data1, data2):
        value = data1 | (data2 << 8)
        if value & (1 << 16 - 1):
            value -= (1 << 16)
        return value
