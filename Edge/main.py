import time
from machine import Pin, I2C
from micropython import const
from hts221 import HTS221

address = 0x5F

I2C0_SCL = const(26)
I2C0_SDA = const(25)

scl = Pin(I2C0_SCL, Pin.IN)
sda = Pin(I2C0_SDA, Pin.OUT)
i2c = I2C(-1, scl=scl, sda=sda)

sensor = HTS221(i2c=i2c, address=address)

while True:
    humidity = sensor.read_humi()
    print("humidity: " + str(humidity))
    time.sleep(0.5)

    temperature = sensor.read_temp()
    print("temperature: " + str(temperature))
    time.sleep(0.5)
