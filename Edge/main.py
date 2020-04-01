from drivers import HTS221
from time import sleep
from machine import I2C, Pin
from micropython import const

print("Hello")
sleep(5)
print("World")

I2C0_SCL = const(26)
I2C0_SDA = const(25)

scl = Pin(I2C0_SCL, Pin.IN)
sda = Pin(I2C0_SDA, Pin.OUT)
i2c = I2C(-1, scl=scl, sda=sda)
sensor = HTS221(i2c)

while True:
    # data = sensor.get_values()
    #
    # print("Accelerometer data")
    # print("x: " + str(data['AcX']))
    # print("y: " + str(data['AcY']))
    # print("z: " + str(data['AcZ']))
    #
    # print("Gyroscope data")
    # print("x: " + str(data['GyX']))
    # print("y: " + str(data['GyY']))
    # print("z: " + str(data['GyZ']))
    #
    # print("Temp: " + str(data['Tmp']) + " C")
    # sleep(0.5)

    data = sensor.read_temp()
    print(data)
    sleep(1)
