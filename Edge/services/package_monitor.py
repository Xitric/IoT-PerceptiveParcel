import math

from thread import Thread
from drivers import MPU6050, HTS221
from machine import Pin, I2C
from connection import MessagingService, Wifi, MqttConnection
import ubinascii
import machine
import utime
import ujson
import sys

TOPIC_DEVICE_PACKAGE = 'hcklI67o/device/{}/package'

TOPIC_TEMPERATURE_SETPOINT = 'hcklI67o/package/{}/setpoint/temperature'
TOPIC_HUMIDITY_SETPOINT = 'hcklI67o/package/{}/setpoint/humidity'
TOPIC_MOTION_SETPOINT = 'hcklI67o/package/{}/setpoint/motion'
TOPIC_TEMPERATURE_PUBLISH = 'hcklI67o/package/{}/temperature'
TOPIC_HUMIDITY_PUBLISH = 'hcklI67o/package/{}/humidity'
TOPIC_MOTION_PUBLISH = 'hcklI67o/package/{}/motion'


class PackageMonitor:
    def __init__(self, wifi: Wifi, mqtt: MqttConnection, messaging: MessagingService, oled):
        self.wifi = wifi
        self.mqtt = mqtt
        self.messaging = messaging
        self.oled = oled

        self.environment_thread = Thread(self.__run_environment, "EnvironmentThread")
        self.motion_thread = Thread(self.__run_motion, "MotionThread")

        self.temperature_setpoint = None
        self.humidity_setpoint = None
        self.motion_setpoint = None

        self.last_z = 0
        self.last_y = 0
        self.last_x = 0

        self.environment_sensor = HTS221(I2C(-1, Pin(26, Pin.IN), Pin(25, Pin.OUT)))
        self.motion_sensor = MPU6050(I2C(-1, Pin(26, Pin.IN), Pin(25, Pin.OUT)))

    def __package_id(self):
        device_id = ubinascii.hexlify(machine.unique_id()).decode()
        self.mqtt.subscribe(TOPIC_DEVICE_PACKAGE.format(device_id), self._on_package_id, 1)
        self.messaging.notify()

    def start(self):
        self.__package_id()
        self.environment_thread.start()
        self.motion_thread.start()

    def __run_environment(self, thread: Thread):
        while thread.active:
            did_transmit = False

            if self.temperature_setpoint:
                if self.__check_temperature():
                    did_transmit = True

            if self.humidity_setpoint:
                if self.__check_humidity():
                    did_transmit = True

            if did_transmit:
                # TODO: Move to budget manager
                print("Notified messaging service of pending data")
                self.messaging.notify()

            utime.sleep(10)  # Reduce energy footprint?

    def __run_motion(self, thread: Thread):
        while thread.active:
            did_transmit = False

            if self.motion_setpoint:
                if self.__check_motion():
                    did_transmit = True

            if did_transmit:
                # TODO: Move to budget manager
                print("Notified messaging service of pending data")
                self.messaging.notify()

            utime.sleep_ms(100)

    def __check_temperature(self) -> bool:
        temperature = self.environment_sensor.read_temp()
        print("Read temperature: {}".format(temperature))

        if temperature > self.temperature_setpoint:
            time = utime.localtime()
            temperature_time = ujson.dumps({"temperature": temperature, "time": time})
            self.mqtt.publish(TOPIC_TEMPERATURE_PUBLISH.format(self.messaging.package_id), temperature_time, qos=1)
            return True
        return False

    def __check_humidity(self) -> bool:
        humidity = self.environment_sensor.read_humi()
        print("Read humidity: {}".format(humidity))

        if humidity > self.humidity_setpoint:
            time = utime.localtime()
            humidity_time = ujson.dumps({"humidity": humidity, "time": time})
            self.mqtt.publish(TOPIC_HUMIDITY_PUBLISH.format(self.messaging.package_id), humidity_time, qos=1)
            return True
        return False

    def __check_motion(self) -> bool:
        # E.g. {'GyZ': -213, 'GyY': 203, 'GyX': -151, 'Tmp': 27.73, 'AcZ': 16312, 'AcY': 620, 'AcX': -1116}
        values = self.motion_sensor.get_values()

        z = values['AcZ']
        y = values['AcY']
        x = values['AcX']

        motion = math.fabs(z + y + x - self.last_z - self.last_y - self.last_x)

        self.last_z = z
        self.last_y = y
        self.last_x = x

        if motion > self.motion_setpoint: #20000
            time = utime.time()
            motion_time = ujson.dumps({"motion": motion, "time": time})
            self.mqtt.publish(TOPIC_MOTION_PUBLISH.format(self.messaging.package_id), motion_time, qos=1)
            return True

        return False

    def _on_package_id(self, topic, msg):
        print('Received package id {}'.format(msg))
        self.messaging.package_id = msg
        # TODO: Unsubscribe from old id - umqttsimple does not support this!
        self.mqtt.subscribe(TOPIC_TEMPERATURE_SETPOINT.format(self.messaging.package_id), self._on_temperature_setpoint, 1)
        self.mqtt.subscribe(TOPIC_HUMIDITY_SETPOINT.format(self.messaging.package_id), self._on_humidity_setpoint, 1)
        self.mqtt.subscribe(TOPIC_MOTION_SETPOINT.format(self.messaging.package_id), self._on_motion_setpoint, 1)
        self.messaging.notify()

    def _on_temperature_setpoint(self, topic, msg):
        self.temperature_setpoint = float(msg)
        print('Received temperature {}'.format(msg))

    def _on_humidity_setpoint(self, topic, msg):
        self.humidity_setpoint = float(msg)
        print('Received humidity {}'.format(msg))

    def _on_motion_setpoint(self, topic, msg):
        self.motion_setpoint = float(msg)
        print('Received motion {}'.format(msg))
