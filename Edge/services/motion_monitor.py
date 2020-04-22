import math

from thread import Thread
from drivers import MPU6050
from machine import Pin, I2C
from connection import MessagingService, Wifi, MqttConnection
import ubinascii
import machine
import utime

TOPIC_DEVICE_PACKAGE = 'hcklI67o/device/{}/package'

class MotionMonitor:
    def __init__(self, wifi: Wifi, mqtt: MqttConnection, messaging: MessagingService, oled):
        self.wifi = wifi
        self.mqtt = mqtt
        self.messaging = messaging
        self.oled = oled
        self.thread = Thread(self.__run, "MontionThread")

        self.last_z = 0
        self.last_y = 0
        self.last_x = 0

        self.motion_sensor = MPU6050(I2C(-1, Pin(26, Pin.IN), Pin(25, Pin.OUT)))

    def start(self):
        self.thread.start()

    def __run(self, thread: Thread):
        device_id = ubinascii.hexlify(machine.unique_id()).decode()
        self.mqtt.subscribe(TOPIC_DEVICE_PACKAGE.format(device_id), self._on_package_id, 1)
        self.messaging.notify()

        while thread.active:
            did_transmit = False

            if self.__check_motion():
                did_transmit = True

            if did_transmit:
                # TODO: Move to budget manager
                print("Notified messaging service of pending data")
                self.messaging.notify()

            utime.sleep_ms(100)  # Reduce energy footprint?

    def _on_package_id(self, topic, msg):
        print('Received package id {}'.format(msg))
        self.oled.push_line("PID: {}".format(msg))
        self.messaging.set_package_id(msg)
        # TODO: Unsubscribe from old id - umqttsimple does not support this!
        self.messaging.notify()

    def __check_motion(self):
        # {'GyZ': -213, 'GyY': 203, 'GyX': -151, 'Tmp': 27.73, 'AcZ': 16312, 'AcY': 620, 'AcX': -1116}
        values = self.motion_sensor.get_values()

        z = values['AcZ']
        y = values['AcY']
        x = values['AcX']

        shake = math.fabs(z + y + x - self.last_z - self.last_y - self.last_x)
        print("The shake: " + str(shake))
        # print(self.last_z)
        self.last_z = z
        self.last_y = y
        self.last_x = x
        # print(values['AcZ'])

        # print(values)